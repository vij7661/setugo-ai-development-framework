"""Build a self-contained static-review bundle from frozen EXP-M Git objects.

The ZIP is a review-convenience artifact only. It does not modify S, E, P, or Q
and grants no authority. Every included repository object is identified by its
origin commit/path and independently SHA-256 hashed inside BUNDLE-MANIFEST.json.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import subprocess
import zipfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FREEZE_PATH = "experiments/governed-platform/EXP-M-SOURCE-FREEZE.json"
EVIDENCE_MANIFEST_PATH = "experiments/governed-platform/EXP-M-R2E-EVIDENCE-MANIFEST.json"
PACKET_PATH = "experiments/governed-platform/EXP-M-R2E-PACKET-CONTENT.md"
HANDOFF_PATH = "experiments/governed-platform/EXP-M-DETERMINISTIC-IMPLEMENTATION-R2E-REVIEW.md"
PRIOR_INDEX_PATH = "experiments/governed-platform/PRIOR-EVIDENCE-INDEX.md"
AUTHORITY_ROOT_PATH = "experiments/governed-platform/EXP-M-R2E-AUTHORITY-ROOT.json"


def _git(*args: str) -> str:
    return subprocess.check_output(("git",) + args, cwd=ROOT, text=True).strip()


def _git_bytes(commit: str, path: str) -> bytes:
    return subprocess.check_output(("git", "show", f"{commit}:{path}"), cwd=ROOT)


def _blob(commit: str, path: str) -> str:
    return _git("rev-parse", f"{commit}:{path}")


def _tree(commit: str) -> str:
    return _git("rev-parse", f"{commit}^{{tree}}")


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _parent(commit: str) -> str:
    return _git("rev-parse", f"{commit}^")


def _zip_name(prefix: str, repo_path: str) -> str:
    return f"{prefix}/{repo_path}".replace("//", "/")


def _parse_prior_index(raw: bytes) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for line in raw.decode("utf-8").splitlines():
        if not line.startswith("| ") or line.startswith("| ID ") or line.startswith("|---"):
            continue
        cells = [x.strip() for x in line.strip("|").split("|")]
        if len(cells) != 6:
            continue
        rows.append({
            "id": cells[0],
            "path": cells[1],
            "commit": cells[2],
            "sha256": cells[3],
            "claim": cells[4],
            "disposition": cells[5],
        })
    return rows


def build(source: str, evidence: str, packet: str, handoff: str, output: Path) -> dict[str, Any]:
    if _parent(evidence) != source:
        raise SystemExit("portable_bundle_evidence_not_direct_child_of_source")
    if _parent(packet) != evidence:
        raise SystemExit("portable_bundle_packet_not_direct_child_of_evidence")
    if _parent(handoff) != packet:
        raise SystemExit("portable_bundle_handoff_not_direct_child_of_packet")

    freeze_raw = _git_bytes(evidence, FREEZE_PATH)
    freeze = json.loads(freeze_raw)
    if freeze.get("source_commit") != source or freeze.get("source_tree") != _tree(source):
        raise SystemExit("portable_bundle_source_freeze_identity_mismatch")

    evidence_manifest_raw = _git_bytes(evidence, EVIDENCE_MANIFEST_PATH)
    evidence_manifest = json.loads(evidence_manifest_raw)
    if evidence_manifest.get("source_commit") != source or evidence_manifest.get("source_tree") != _tree(source):
        raise SystemExit("portable_bundle_evidence_manifest_identity_mismatch")

    entries: list[dict[str, Any]] = []
    payloads: dict[str, bytes] = {}

    def add(
        bundle_path: str,
        raw: bytes,
        role: str,
        *,
        origin_commit: str | None = None,
        origin_path: str | None = None,
        expected_sha256: str | None = None,
        expected_size: int | None = None,
    ) -> None:
        if bundle_path in payloads:
            raise SystemExit(f"portable_bundle_duplicate_path:{bundle_path}")
        actual_sha = _sha256(raw)
        if expected_sha256 is not None and actual_sha != expected_sha256:
            raise SystemExit(f"portable_bundle_hash_mismatch:{bundle_path}")
        if expected_size is not None and len(raw) != expected_size:
            raise SystemExit(f"portable_bundle_size_mismatch:{bundle_path}")
        entry: dict[str, Any] = {
            "bundle_path": bundle_path,
            "role": role,
            "sha256": actual_sha,
            "size": len(raw),
        }
        if origin_commit is not None:
            entry["origin_commit"] = origin_commit
        if origin_path is not None:
            entry["origin_path"] = origin_path
        if origin_commit is not None and origin_path is not None:
            entry["git_blob"] = _blob(origin_commit, origin_path)
        entries.append(entry)
        payloads[bundle_path] = raw

    add(
        _zip_name("evidence", FREEZE_PATH),
        freeze_raw,
        "source-freeze evidence",
        origin_commit=evidence,
        origin_path=FREEZE_PATH,
    )

    for repo_path, expected_hash in sorted((freeze.get("source_files") or {}).items()):
        raw = _git_bytes(source, repo_path)
        add(
            _zip_name("source", repo_path),
            raw,
            "frozen source",
            origin_commit=source,
            origin_path=repo_path,
            expected_sha256=str(expected_hash),
        )

    add(
        _zip_name("evidence", EVIDENCE_MANIFEST_PATH),
        evidence_manifest_raw,
        "evidence manifest",
        origin_commit=evidence,
        origin_path=EVIDENCE_MANIFEST_PATH,
    )
    for item in evidence_manifest.get("artifacts") or []:
        repo_path = str(item["path"])
        raw = _git_bytes(evidence, repo_path)
        bundle_path = _zip_name("evidence", repo_path)
        if bundle_path in payloads:
            continue
        add(
            bundle_path,
            raw,
            "fresh E evidence artifact",
            origin_commit=evidence,
            origin_path=repo_path,
            expected_sha256=str(item["sha256"]),
            expected_size=int(item["size"]),
        )

    add(
        _zip_name("packet", PACKET_PATH),
        _git_bytes(packet, PACKET_PATH),
        "immutable packet P",
        origin_commit=packet,
        origin_path=PACKET_PATH,
    )
    add(
        _zip_name("handoff", HANDOFF_PATH),
        _git_bytes(handoff, HANDOFF_PATH),
        "post-P exact identity handoff Q",
        origin_commit=handoff,
        origin_path=HANDOFF_PATH,
    )

    authority_source = _git_bytes(source, "governance-runtime/exp_m_expectation_authority.py").decode("utf-8")
    match = re.search(r'DEFAULT_AUTHORITY_COMMIT\s*=\s*"([0-9a-f]{40})"', authority_source)
    if not match:
        raise SystemExit("portable_bundle_authority_commit_unresolved")
    authority_commit = match.group(1)
    authority_root_raw = _git_bytes(authority_commit, AUTHORITY_ROOT_PATH)
    authority_root = json.loads(authority_root_raw)
    add(
        _zip_name("authority", AUTHORITY_ROOT_PATH),
        authority_root_raw,
        "preregistered authority root",
        origin_commit=authority_commit,
        origin_path=AUTHORITY_ROOT_PATH,
    )
    authority_specs = (
        (str(authority_root["test_expectation_manifest_path"]), authority_root.get("test_expectation_manifest_sha256"), "test expectations"),
        (str(authority_root["test_expectation_signature_path"]), None, "test expectation signature"),
        (str(authority_root["r5_protocol_path"]), authority_root.get("r5_protocol_sha256"), "R5 protocol"),
        (str(authority_root["retrieval_source_ledger_path"]), authority_root.get("retrieval_source_ledger_sha256"), "retrieval authority ledger"),
        (str(authority_root["delivery_ledger_path"]), authority_root.get("delivery_ledger_sha256"), "delivery authority ledger"),
        (str(authority_root["qualification_ledger_path"]), authority_root.get("qualification_ledger_sha256"), "qualification authority ledger"),
    )
    for repo_path, expected_hash, role in authority_specs:
        raw = _git_bytes(authority_commit, repo_path)
        add(
            _zip_name("authority", repo_path),
            raw,
            role,
            origin_commit=authority_commit,
            origin_path=repo_path,
            expected_sha256=str(expected_hash) if expected_hash else None,
        )

    retrieval_ledger = json.loads(_git_bytes(authority_commit, str(authority_root["retrieval_source_ledger_path"])))
    for source_id, entry in sorted((retrieval_ledger.get("sources") or {}).items()):
        repo_path = str(entry["path"])
        raw = _git_bytes(authority_commit, repo_path)
        add(
            _zip_name("authority", repo_path),
            raw,
            f"retrieval backing source {source_id}",
            origin_commit=authority_commit,
            origin_path=repo_path,
            expected_sha256=str(entry["sha256"]),
            expected_size=int(entry["length"]),
        )

    prior_index_raw = _git_bytes(source, PRIOR_INDEX_PATH)
    add(
        _zip_name("prior-history", PRIOR_INDEX_PATH),
        prior_index_raw,
        "prior evidence index",
        origin_commit=source,
        origin_path=PRIOR_INDEX_PATH,
    )
    for row in _parse_prior_index(prior_index_raw):
        raw = _git_bytes(row["commit"], row["path"])
        safe_id = re.sub(r"[^A-Za-z0-9_.-]+", "_", row["id"])
        add(
            _zip_name(f"prior-history/{safe_id}", row["path"]),
            raw,
            f"historical evidence: {row['claim']} [{row['disposition']}]",
            origin_commit=row["commit"],
            origin_path=row["path"],
            expected_sha256=row["sha256"],
        )

    identity = {
        "schema": "EXP-M-R2E-PORTABLE-REVIEW-BUNDLE/v2",
        "S": source,
        "S_tree": _tree(source),
        "E": evidence,
        "E_tree": _tree(evidence),
        "P": packet,
        "P_tree": _tree(packet),
        "Q": handoff,
        "Q_tree": _tree(handoff),
        "authority_commit": authority_commit,
        "authority_tree": _tree(authority_commit),
        "authority_effect": "NONE",
        "exp_m_state": "NOT_QUALIFIED",
        "live_provider_api_execution": False,
        "static_review_limit": "This bundle permits local/static inspection and hash recomputation of included bytes. It does not independently prove remote Git hosting authenticity without an external Git/repository trust source.",
    }
    identity_raw = (json.dumps(identity, indent=2, sort_keys=True) + "\n").encode()
    add("IDENTITY.json", identity_raw, "bundle identity")

    readme = f"""# EXP-M R2E Portable Static Review Bundle

This ZIP is derived from immutable Git objects after the governed S -> E -> P -> Q chain.

S: {source}
E: {evidence}
P: {packet}
Q: {handoff}
Authority commit: {authority_commit}

Contents:
- source/: every source file enumerated by the source-freeze manifest at S.
- evidence/: the source freeze, evidence manifest, and every E artifact.
- packet/: the immutable P packet content.
- handoff/: the exact Q review handoff.
- authority/: the preregistered authority inputs and retrieval backing source.
- prior-history/: the prior-evidence index plus each pinned historical artifact.
- IDENTITY.json: bundle identities and authority boundary.
- README.md: this review guide.
- BUNDLE-MANIFEST.json: hash/size/origin attestation for every other archive entry. It intentionally does not hash itself.

The bundle is for static/independent review convenience only.
It grants no EXP-M qualification and no live provider/API authority.
A reviewer can recompute SHA-256 values for the included bytes without repository access.
Authenticating that the stated commit/blob identifiers are the repository's true remote objects still requires an external Git/repository trust source.
"""
    add("README.md", readme.encode(), "bundle review guide")

    attested_entries = sorted(entries, key=lambda row: row["bundle_path"])
    manifest = {
        **identity,
        "manifest_schema": "EXP-M-R2E-BUNDLE-MANIFEST/v2",
        "entries": attested_entries,
        "entry_count": len(attested_entries),
        "attested_entry_count": len(attested_entries),
        "archive_entry_count": len(attested_entries) + 1,
        "self_attestation": {
            "path": "BUNDLE-MANIFEST.json",
            "included_in_entries": False,
            "reason": "A file cannot contain a stable cryptographic hash of its own final bytes without self-reference.",
        },
    }
    manifest_raw = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    payloads["BUNDLE-MANIFEST.json"] = manifest_raw

    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in sorted(payloads):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, payloads[name])

    # Self-verify the review convenience artifact before publishing it.
    with zipfile.ZipFile(output, "r") as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise SystemExit("portable_bundle_duplicate_archive_entry")
        if set(names) != set(payloads):
            raise SystemExit("portable_bundle_archive_entry_set_mismatch")
        persisted_manifest = json.loads(archive.read("BUNDLE-MANIFEST.json"))
        persisted_entries = persisted_manifest.get("entries") or []
        if persisted_manifest.get("entry_count") != len(persisted_entries):
            raise SystemExit("portable_bundle_manifest_entry_count_mismatch")
        if persisted_manifest.get("attested_entry_count") != len(persisted_entries):
            raise SystemExit("portable_bundle_attested_entry_count_mismatch")
        if persisted_manifest.get("archive_entry_count") != len(names):
            raise SystemExit("portable_bundle_archive_entry_count_mismatch")
        expected_attested_paths = set(names) - {"BUNDLE-MANIFEST.json"}
        observed_attested_paths = {str(row.get("bundle_path", "")) for row in persisted_entries}
        if observed_attested_paths != expected_attested_paths:
            raise SystemExit("portable_bundle_manifest_coverage_mismatch")
        for row in persisted_entries:
            name = str(row["bundle_path"])
            raw = archive.read(name)
            if len(raw) != int(row["size"]) or _sha256(raw) != str(row["sha256"]):
                raise SystemExit(f"portable_bundle_manifest_integrity_mismatch:{name}")

    return {
        "path": str(output),
        "sha256": _sha256(output.read_bytes()),
        "size": output.stat().st_size,
        "entry_count": len(attested_entries),
        "attested_entry_count": len(attested_entries),
        "archive_entry_count": len(payloads),
        "S": source,
        "E": evidence,
        "P": packet,
        "Q": handoff,
        "authority_effect": "NONE",
        "exp_m_state": "NOT_QUALIFIED",
        "live_provider_api_execution": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--evidence", required=True)
    parser.add_argument("--packet", required=True)
    parser.add_argument("--handoff", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = build(args.source, args.evidence, args.packet, args.handoff, Path(args.output))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
