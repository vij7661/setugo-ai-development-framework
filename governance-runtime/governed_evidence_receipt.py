"""Trusted, post-freeze evidence receipt construction and verification.

Receipts grant eligibility evidence only. They never grant merge or runtime authority.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Mapping, Protocol

from freeze_attestation import verify_execution_statement, verify_freeze_attestation

SHA40 = set("0123456789abcdef")
TOP = {"schema", "repository", "candidate", "linux", "packet", "freeze_attestation", "independent_review", "authority_effect"}
CANDIDATE = {"baseline", "commit", "tree", "changed_file_count", "frozen_ref"}
LINUX = {"run_id", "job_id", "workflow_identity", "artifact_id", "artifact_digest", "statement_raw_sha256", "statement_internal_sha256"}
PACKET = LINUX | {"payload_sha256"}
ARTIFACT = {"raw_sha256", "git_blob"}


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def git_blob_sha1(raw: bytes) -> str:
    return hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()

def git_text_blob_sha1(raw: bytes) -> str:
    """Git identity of the LF-normalized committed text, separate from upload bytes."""
    return git_blob_sha1(raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n"))


def canonical_bytes(value: Mapping) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def raw_json(path: Path) -> tuple[bytes, dict]:
    raw = path.read_bytes()
    return raw, json.loads(raw.decode("utf-8"))


def _sha40(value) -> bool:
    return isinstance(value, str) and len(value) == 40 and set(value) <= SHA40

def _sha256(value, *, prefixed=False) -> bool:
    prefix=r"sha256:" if prefixed else ""
    return isinstance(value,str) and re.fullmatch(prefix+r"[0-9a-f]{64}",value) is not None


def verify_receipt_structure(receipt: Mapping) -> bool:
    if not isinstance(receipt, Mapping) or set(receipt) != TOP or receipt.get("schema") != "r8-governed-evidence-receipt/v1" or receipt.get("authority_effect") != "NONE":
        return False
    candidate = receipt.get("candidate")
    if not isinstance(candidate, Mapping) or set(candidate) != CANDIDATE or not all(_sha40(candidate.get(k)) for k in ("baseline", "commit", "tree")) or not isinstance(candidate.get("changed_file_count"), int) or candidate["changed_file_count"] < 0 or not str(candidate.get("frozen_ref", "")).startswith("frozen/"):
        return False
    for name, fields in (("linux", LINUX), ("packet", PACKET)):
        row = receipt.get(name)
        if not isinstance(row, Mapping) or set(row) != fields or not all(isinstance(row.get(k), str) and row[k].strip() for k in fields):
            return False
        if not row["run_id"].isdigit() or not row["job_id"].isdigit() or not row["artifact_id"].isdigit():
            return False
        for key in ("artifact_digest", "statement_raw_sha256", "statement_internal_sha256"):
            if not _sha256(row[key],prefixed=True):
                return False
        if name == "packet" and not _sha256(row["payload_sha256"],prefixed=True):
            return False
    return all(isinstance(receipt.get(name), Mapping) and set(receipt[name]) == ARTIFACT and _sha256(receipt[name]["raw_sha256"]) and _sha40(receipt[name]["git_blob"]) for name in ("freeze_attestation", "independent_review"))


def verify_receipt_files(receipt: Mapping, *, linux_statement_path: Path, packet_statement_path: Path, freeze_attestation_path: Path, review_path: Path, packet_payload_path: Path) -> bool:
    if not verify_receipt_structure(receipt):
        return False
    c = receipt["candidate"]
    linux_raw, linux = raw_json(linux_statement_path); packet_raw, packet = raw_json(packet_statement_path); freeze_raw, freeze = raw_json(freeze_attestation_path); review_raw = review_path.read_bytes(); payload_raw = packet_payload_path.read_bytes()
    if not verify_execution_statement(linux, kind="LINUX_VALIDATION", commit=c["commit"], tree=c["tree"], baseline=c["baseline"], changed_file_count=c["changed_file_count"]): return False
    if not verify_execution_statement(packet, kind="REVIEW_PACKET", commit=c["commit"], tree=c["tree"], baseline=c["baseline"], changed_file_count=c["changed_file_count"]): return False
    if freeze.get("linux_validation_statement") != linux or freeze.get("review_packet_statement") != packet or freeze.get("frozen_ref") != c["frozen_ref"] or not verify_freeze_attestation(freeze, resolver=lambda _r, rev: c["commit"] if rev == c["frozen_ref"] else c["tree"]): return False
    checks = (
        receipt["linux"]["statement_raw_sha256"].removeprefix("sha256:") == sha256_bytes(linux_raw),
        receipt["linux"]["statement_internal_sha256"].removeprefix("sha256:") == linux["statement_sha256"],
        receipt["packet"]["statement_raw_sha256"].removeprefix("sha256:") == sha256_bytes(packet_raw),
        receipt["packet"]["statement_internal_sha256"].removeprefix("sha256:") == packet["statement_sha256"],
        receipt["packet"]["payload_sha256"].removeprefix("sha256:") == sha256_bytes(payload_raw),
        receipt["freeze_attestation"]["raw_sha256"] == sha256_bytes(freeze_raw),
        receipt["freeze_attestation"]["git_blob"] == git_text_blob_sha1(freeze_raw),
        receipt["independent_review"]["raw_sha256"] == sha256_bytes(review_raw),
        receipt["independent_review"]["git_blob"] == git_text_blob_sha1(review_raw),
    )
    return all(checks)


class GitHubEvidenceAPI(Protocol):
    def resolve_ref(self, repository: str, ref: str) -> str: ...
    def run(self, repository: str, run_id: str) -> Mapping: ...
    def job(self, repository: str, job_id: str) -> Mapping: ...
    def artifact(self, repository: str, artifact_id: str) -> Mapping: ...
    def git_blob(self, repository: str, commit: str, path: str) -> str: ...


def ingest_verified_receipt(spec: Mapping, api: GitHubEvidenceAPI, blobs: Mapping[str, bytes], *, artifact_locations: Mapping[str, Mapping[str, str]]) -> dict:
    """Verify GitHub associations and exact bytes, then emit deterministic evidence only."""
    receipt = json.loads(json.dumps(spec))
    if not verify_receipt_structure(receipt): raise ValueError("receipt specification malformed")
    repo, candidate = receipt["repository"], receipt["candidate"]
    if api.resolve_ref(repo, candidate["frozen_ref"]) != candidate["commit"]: raise ValueError("frozen ref mismatch")
    statements={}
    for name,kind in (("linux","LINUX_VALIDATION"),("packet","REVIEW_PACKET")):
        statement_raw=blobs[f"{name}_statement"]
        try: statement=json.loads(statement_raw.decode("utf-8"))
        except (UnicodeDecodeError,json.JSONDecodeError) as exc: raise ValueError(f"{name} statement malformed") from exc
        row=receipt[name]
        if row["statement_raw_sha256"].removeprefix("sha256:") != sha256_bytes(statement_raw) or row["statement_internal_sha256"].removeprefix("sha256:") != statement.get("statement_sha256") or not verify_execution_statement(statement,kind=kind,commit=candidate["commit"],tree=candidate["tree"],baseline=candidate["baseline"],changed_file_count=candidate["changed_file_count"]): raise ValueError(f"{name} statement identity mismatch")
        statements[name]=statement
    if receipt["packet"]["payload_sha256"].removeprefix("sha256:") != sha256_bytes(blobs["packet_payload"]): raise ValueError("packet payload mismatch")
    freeze_value=json.loads(blobs["freeze_attestation"].decode("utf-8"))
    if freeze_value.get("linux_validation_statement") != statements["linux"] or freeze_value.get("review_packet_statement") != statements["packet"]: raise ValueError("attestation statement binding mismatch")
    for name in ("linux", "packet"):
        row=receipt[name]; run=api.run(repo,row["run_id"]); job=api.job(repo,row["job_id"]); artifact=api.artifact(repo,row["artifact_id"])
        if str(run.get("id")) != row["run_id"] or run.get("workflow_identity") != row["workflow_identity"] or run.get("conclusion") != "success": raise ValueError(f"{name} run association mismatch")
        if str(job.get("id")) != row["job_id"] or str(job.get("run_id")) != row["run_id"] or job.get("workflow_identity") not in (None,row["workflow_identity"]) or job.get("conclusion") != "success": raise ValueError(f"{name} job association mismatch")
        if str(artifact.get("id")) != row["artifact_id"] or str(artifact.get("run_id")) != row["run_id"] or artifact.get("digest") != row["artifact_digest"] or row["artifact_digest"].removeprefix("sha256:") != sha256_bytes(blobs[f"{name}_artifact"]): raise ValueError(f"{name} artifact association mismatch")
    for name in ("freeze_attestation", "independent_review"):
        raw=blobs[name]; record=receipt[name]; location=artifact_locations.get(name,{})
        if not location.get("revision") or not location.get("path") or record["raw_sha256"] != sha256_bytes(raw) or record["git_blob"] != git_text_blob_sha1(raw) or api.git_blob(repo,location["revision"],location["path"]) != record["git_blob"]: raise ValueError(f"{name} identity mismatch")
    return receipt
