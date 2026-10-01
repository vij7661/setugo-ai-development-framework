"""Trusted, post-freeze evidence receipt construction and verification.

Receipts grant eligibility evidence only. They never grant merge or runtime authority.
"""
from __future__ import annotations

import hashlib
import json
import re
import io
import zipfile
from pathlib import Path
from typing import Mapping, Protocol

from freeze_attestation import verify_execution_statement, verify_freeze_attestation

SHA40 = set("0123456789abcdef")
TOP = {"schema", "repository", "candidate", "linux", "packet", "freeze_attestation", "independent_review", "authority_effect"}
CANDIDATE = {"baseline", "commit", "tree", "changed_file_count", "frozen_ref"}
LINUX = {"run_id", "job_id", "workflow_identity", "artifact_id", "artifact_digest", "statement_raw_sha256", "statement_internal_sha256"}
PACKET = LINUX | {"payload_sha256"}
ARTIFACT = {"raw_sha256", "git_blob"}
REVIEW_ARTIFACT_V2 = {"original_upload_raw_sha256", "committed_review_sha256", "git_blob"}


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
    def download_artifact(self, repository: str, artifact_id: str, download_url: str) -> bytes: ...
    def git_blob(self, repository: str, commit: str, path: str) -> str: ...
    def git_blob_bytes(self, repository: str, commit: str, path: str) -> bytes: ...

def verify_trusted_code_binding(receipt:Mapping, *, expected_commit:str, expected_tree:str, actual_commit:str|None=None, actual_tree:str|None=None)->bool:
    """Bind the executing trusted checkout and recorded receipt identity."""
    if not (_sha40(expected_commit) and _sha40(expected_tree)): return False
    if actual_commit is not None and actual_commit != expected_commit: return False
    if actual_tree is not None and actual_tree != expected_tree: return False
    trusted=receipt.get("trusted_code") if isinstance(receipt,Mapping) else None
    return isinstance(trusted,Mapping) and trusted.get("verifier_commit")==expected_commit and trusted.get("verifier_tree")==expected_tree


V2_TOP={"schema","repository","candidate","linux","packet","freeze_attestation","independent_review","trusted_code","authority_effect"}
V2_EXEC={"run_id","job_id","workflow_file","workflow_identity","artifact_id","archive_digest","archive_raw_sha256","payload_member_path","payload_member_sha256","payload_member_bytes","statement_member_path","statement_raw_sha256","statement_internal_sha256"}
TRUSTED={"verifier_commit","verifier_tree","evidence_ref"}

def _safe_archive(raw:bytes,allowed:set[str])->dict[str,bytes]:
    if not zipfile.is_zipfile(io.BytesIO(raw)): raise ValueError("artifact is not a ZIP archive")
    result={}
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        for info in archive.infolist():
            name=info.filename
            normalized=name.replace("\\","/")
            if name!=normalized or normalized.startswith("/") or re.match(r"^[A-Za-z]:",normalized) or any(p in {"",".",".."} for p in normalized.split("/")):
                raise ValueError("unsafe artifact member path")
            if normalized in result: raise ValueError("duplicate artifact member")
            if (info.external_attr >> 16) & 0o170000 == 0o120000: raise ValueError("symlink artifact member")
            if normalized not in allowed: raise ValueError("unexpected artifact member")
            result[normalized]=archive.read(info)
    if set(result)!=allowed: raise ValueError("artifact member missing")
    return result

def verify_receipt_v2_structure(receipt:Mapping)->bool:
    if not isinstance(receipt,Mapping) or receipt.get("schema")!="r8-governed-evidence-receipt/v2" or receipt.get("authority_effect")!="NONE": return False
    if set(receipt) not in (V2_TOP,V2_TOP|{"review_source"}): return False
    candidate=receipt.get("candidate")
    if not isinstance(candidate,Mapping) or set(candidate)!=CANDIDATE or not all(_sha40(candidate.get(k)) for k in ("baseline","commit","tree")) or not isinstance(candidate.get("changed_file_count"),int) or candidate["changed_file_count"]<0: return False
    trusted=receipt.get("trusted_code")
    if not isinstance(trusted,Mapping) or set(trusted)!=TRUSTED or not _sha40(trusted.get("verifier_commit")) or not _sha40(trusted.get("verifier_tree")) or not isinstance(trusted.get("evidence_ref"),str) or not trusted["evidence_ref"]: return False
    for name in ("linux","packet"):
        row=receipt.get(name)
        if not isinstance(row,Mapping) or set(row)!=V2_EXEC: return False
        if not all(isinstance(row.get(k),str) and row[k] for k in V2_EXEC-{"payload_member_bytes"}) or not isinstance(row.get("payload_member_bytes"),int) or row["payload_member_bytes"]<0: return False
        if not all(row[k].isdigit() for k in ("run_id","job_id","artifact_id")): return False
        if not all(_sha256(row[k],prefixed=True) for k in ("archive_digest","archive_raw_sha256","payload_member_sha256","statement_raw_sha256","statement_internal_sha256")): return False
        if row["archive_digest"]!=row["archive_raw_sha256"] or row["payload_member_path"]==row["statement_member_path"]: return False
    if not (isinstance(receipt.get("freeze_attestation"),Mapping) and set(receipt["freeze_attestation"])==ARTIFACT and _sha256(receipt["freeze_attestation"]["raw_sha256"]) and _sha40(receipt["freeze_attestation"]["git_blob"])): return False
    review=receipt.get("independent_review")
    if not (isinstance(review,Mapping) and set(review)==REVIEW_ARTIFACT_V2 and _sha256(review["original_upload_raw_sha256"]) and _sha256(review["committed_review_sha256"]) and _sha40(review["git_blob"])): return False
    if "review_source" in receipt:
        src=receipt["review_source"]
        if not isinstance(src,Mapping) or set(src)!={"repository","revision","path"} or not all(isinstance(src.get(k),str) and src[k] for k in src): return False
        if not _sha40(src["revision"]) or src["path"].startswith("/") or "\\" in src["path"] or any(p in {"",".",".."} for p in src["path"].split("/")): return False
        if src["repository"]!=receipt.get("repository"): return False
    return True

def ingest_verified_receipt(spec: Mapping, api: GitHubEvidenceAPI, blobs: Mapping[str, bytes], *, artifact_locations: Mapping[str, Mapping[str, str]], trusted_verifier_commit:str, trusted_verifier_tree:str, evidence_ref:str) -> dict:
    """Verify GitHub associations and exact bytes, then emit deterministic evidence only."""
    receipt = json.loads(json.dumps(spec))
    if not verify_receipt_v2_structure(receipt): raise ValueError("receipt v2 specification required; v1 is historical only")
    if not verify_trusted_code_binding(receipt,expected_commit=trusted_verifier_commit,expected_tree=trusted_verifier_tree): raise ValueError("trusted code/evidence separation mismatch")
    repo, candidate = receipt["repository"], receipt["candidate"]
    if api.resolve_ref(repo, candidate["frozen_ref"]) != candidate["commit"]: raise ValueError("frozen ref mismatch")
    statements={}
    for name,kind in (("linux","LINUX_VALIDATION"),("packet","REVIEW_PACKET")):
        row=receipt[name]; run=api.run(repo,row["run_id"]); job=api.job(repo,row["job_id"]); artifact=api.artifact(repo,row["artifact_id"])
        if str(run.get("id"))!=row["run_id"] or run.get("workflow_file")!=row["workflow_file"] or run.get("conclusion")!="success": raise ValueError(f"{name} run association mismatch")
        if str(job.get("id"))!=row["job_id"] or str(job.get("run_id"))!=row["run_id"] or job.get("workflow_identity")!=row["workflow_identity"] or job.get("conclusion")!="success": raise ValueError(f"{name} job association mismatch")
        if str(artifact.get("id"))!=row["artifact_id"] or str(artifact.get("run_id"))!=row["run_id"] or artifact.get("digest")!=row["archive_digest"]: raise ValueError(f"{name} artifact association mismatch")
        archive_raw=api.download_artifact(repo,row["artifact_id"],artifact.get("archive_download_url"))
        if "sha256:"+sha256_bytes(archive_raw)!=row["archive_raw_sha256"]: raise ValueError(f"{name} archive digest mismatch")
        members=_safe_archive(archive_raw,{row["statement_member_path"],row["payload_member_path"]})
        statement_raw=members[row["statement_member_path"]]; payload_raw=members[row["payload_member_path"]]
        try: statement=json.loads(statement_raw.decode("utf-8"))
        except (UnicodeDecodeError,json.JSONDecodeError) as exc: raise ValueError(f"{name} statement malformed") from exc
        if row["statement_raw_sha256"] != "sha256:"+sha256_bytes(statement_raw) or row["statement_internal_sha256"] != "sha256:"+str(statement.get("statement_sha256")) or not verify_execution_statement(statement,kind=kind,commit=candidate["commit"],tree=candidate["tree"],baseline=candidate["baseline"],changed_file_count=candidate["changed_file_count"]): raise ValueError(f"{name} statement identity mismatch")
        if str(statement.get("run_id"))!=row["run_id"] or str(statement.get("job_id"))!=row["job_id"] or statement.get("workflow_identity")!=row["workflow_identity"]: raise ValueError(f"{name} statement execution mismatch")
        if row["payload_member_sha256"]!="sha256:"+sha256_bytes(payload_raw) or row["payload_member_bytes"]!=len(payload_raw) or statement.get("artifact_digest")!=row["payload_member_sha256"]: raise ValueError(f"{name} payload member mismatch")
        statements[name]=statement
    freeze_value=json.loads(blobs["freeze_attestation"].decode("utf-8"))
    if freeze_value.get("linux_validation_statement") != statements["linux"] or freeze_value.get("review_packet_statement") != statements["packet"]: raise ValueError("attestation statement binding mismatch")
    for name in ("freeze_attestation", "independent_review"):
        raw=blobs[name]; record=receipt[name]; location=artifact_locations.get(name,{})
        if not location.get("revision") or not location.get("path"): raise ValueError(f"{name} identity mismatch")
        if name=="independent_review":
            src=receipt.get("review_source",{})
            if src and (src.get("repository")!=repo or src.get("revision")!=location.get("revision") or src.get("path")!=location.get("path")): raise ValueError(f"{name} source mismatch")
            committed=api.git_blob_bytes(repo,location["revision"],location["path"])
            if record["original_upload_raw_sha256"] != sha256_bytes(raw) or record["committed_review_sha256"] != sha256_bytes(committed) or git_blob_sha1(committed) != record["git_blob"] or api.git_blob(repo,location["revision"],location["path"]) != record["git_blob"]: raise ValueError(f"{name} identity mismatch")
        elif record["raw_sha256"] != sha256_bytes(raw) or record["git_blob"] != git_text_blob_sha1(raw) or api.git_blob(repo,location["revision"],location["path"]) != record["git_blob"]: raise ValueError(f"{name} identity mismatch")
    review_location=artifact_locations.get("independent_review",{})
    receipt["review_source"]={"repository":repo,"revision":review_location["revision"],"path":review_location["path"]}
    return receipt
