"""Non-authoritative release qualification evaluator."""
from __future__ import annotations
import hashlib, json

REQUIRED = {"schema", "candidate_commit", "candidate_tree", "artifact_sha256", "sbom_sha256", "test_evidence_sha256", "runtime_evidence_sha256", "unresolved_findings", "independent_review", "release_authorized"}


def evaluate(record: dict, *, expected_commit: str, expected_tree: str) -> dict:
    if set(record) != REQUIRED:
        raise ValueError("release record schema mismatch")
    if record["candidate_commit"] != expected_commit or record["candidate_tree"] != expected_tree:
        raise ValueError("stale candidate identity")
    for key in ("artifact_sha256", "sbom_sha256", "test_evidence_sha256", "runtime_evidence_sha256"):
        if not isinstance(record[key], str) or len(record[key]) != 64:
            raise ValueError(f"missing {key}")
    if record["unresolved_findings"] != []:
        raise ValueError("unresolved findings remain")
    if record["independent_review"] is not True:
        raise ValueError("independent release review required")
    if record["release_authorized"] is not False:
        raise ValueError("qualification cannot authorize release")
    return {"status": "RELEASE_QUALIFIED_EVIDENCE", "release_authorized": False}


def digest(record: dict) -> str:
    return hashlib.sha256(json.dumps(record, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
