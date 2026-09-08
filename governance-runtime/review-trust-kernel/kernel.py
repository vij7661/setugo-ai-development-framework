from __future__ import annotations

import json
import re
import subprocess
from hashlib import sha256
from pathlib import Path

HEX40 = re.compile(r"^[0-9a-f]{40}$")
ALLOWED_STATUSES = {
    "CONTRADICTED", "INACCESSIBLE", "INSUFFICIENT", "NOT_TESTED",
    "TESTED_DEFECT_FOUND", "TESTED_SUPPORTED", "UNAVAILABLE",
}
ALLOWED_DISPOSITIONS = {
    "PASS", "BOUNDED_PASS", "FAIL", "NOT_TESTED",
    "INSUFFICIENT_EVIDENCE", "CHANGES_REQUIRED",
}
BLOCKING = {"MEDIUM", "HIGH", "CRITICAL"}


def canon(value):
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    ).encode("utf-8")


def digest(value):
    return sha256(canon(value)).hexdigest()


def file_sha256(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def git(root, *args):
    cp = subprocess.run(
        ["git", *args], cwd=root, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        encoding="utf-8", errors="strict",
    )
    if cp.returncode:
        raise RuntimeError(cp.stderr.strip() or "git failed")
    return cp.stdout


def require_commit(root, commit, label="candidate"):
    if not isinstance(commit, str) or not HEX40.fullmatch(commit):
        raise ValueError(f"{label} invalid")
    resolved = git(root, "rev-parse", f"{commit}^{{commit}}").strip()
    if resolved != commit:
        raise ValueError(f"{label} not exact")


def collect_candidate_files(root, candidate_commit, evidence_refs):
    """Collect candidate files without importing or executing candidate Python code."""
    require_commit(root, candidate_commit)
    artifacts = []
    for ref in evidence_refs:
        if not isinstance(ref, dict) or ref.get("type") != "file":
            continue
        path = ref.get("ref")
        if not isinstance(path, str) or not path:
            raise ValueError("file evidence ref requires ref path")
        cp = subprocess.run(
            ["git", "show", f"{candidate_commit}:{path}"],
            cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        if cp.returncode:
            raise RuntimeError(f"candidate evidence file unavailable: {path}")
        artifacts.append({
            "path": path,
            "bytes": len(cp.stdout),
            "sha256": sha256(cp.stdout).hexdigest(),
            "content": cp.stdout.decode("utf-8"),
        })
    return artifacts


def validate_review(review, request, provider, model):
    """Deterministic validator owned by the trust kernel, not candidate code."""
    errors = []
    reqid = request["review_request_id"]
    candidate = request["artifact"]["commit"]
    mandatory = [
        d["id"] for d in request["required_review_dimensions"] if d.get("mandatory")
    ]

    if review.get("review_request_id") != reqid:
        errors.append("review_request_id mismatch")
    if review.get("reviewed_artifact_commit") != candidate:
        errors.append("reviewed_artifact_commit mismatch")
    disposition = review.get("disposition")
    if disposition not in ALLOWED_DISPOSITIONS:
        errors.append("invalid disposition")

    reviewer = review.get("reviewer")
    if (
        not isinstance(reviewer, dict)
        or reviewer.get("provider") != provider
        or reviewer.get("model") != model
    ):
        errors.append("reviewer content identity disagrees with execution envelope")

    findings = review.get("findings")
    if not isinstance(findings, list):
        errors.append("findings must be list")
        findings = []
    blocking = False
    for finding in findings:
        if not isinstance(finding, dict):
            errors.append("finding must be object")
            continue
        severity = finding.get("severity")
        if severity not in {"LOW", "MEDIUM", "HIGH", "CRITICAL"}:
            errors.append("invalid finding severity")
        if severity in BLOCKING:
            blocking = True
        if not str(finding.get("evidence", "")).strip():
            errors.append("finding evidence required")

    coverage = review.get("review_coverage")
    if not isinstance(coverage, list):
        errors.append("review_coverage must be list")
        coverage = []
    by_dimension = {}
    for row in coverage:
        if not isinstance(row, dict):
            errors.append("coverage row must be object")
            continue
        dimension_id = row.get("dimension_id")
        if dimension_id in by_dimension:
            errors.append(f"duplicate dimension {dimension_id}")
            continue
        by_dimension[dimension_id] = row
        status = row.get("status")
        if status not in ALLOWED_STATUSES:
            errors.append(f"invalid coverage status {dimension_id}")
        if status in {"TESTED_SUPPORTED", "TESTED_DEFECT_FOUND", "CONTRADICTED"}:
            evidence = row.get("evidence")
            if not isinstance(evidence, list) or not any(str(x).strip() for x in evidence):
                errors.append(f"tested dimension evidence required {dimension_id}")

    missing = [d for d in mandatory if d not in by_dimension]
    extras = [d for d in by_dimension if d not in mandatory]
    if missing:
        errors.append("missing mandatory dimensions: " + ",".join(missing))
    if extras:
        errors.append("unexpected dimensions: " + ",".join(extras))

    statuses = {d: by_dimension[d].get("status") for d in mandatory if d in by_dimension}
    all_supported = (
        len(statuses) == len(mandatory)
        and all(v == "TESTED_SUPPORTED" for v in statuses.values())
    )
    incomplete = any(
        v in {"NOT_TESTED", "UNAVAILABLE", "INACCESSIBLE", "INSUFFICIENT"}
        for v in statuses.values()
    )
    defective = any(
        v in {"TESTED_DEFECT_FOUND", "CONTRADICTED"}
        for v in statuses.values()
    )

    if disposition == "PASS" and (not all_supported or blocking):
        errors.append("PASS contradicts coverage/findings")
    if disposition == "BOUNDED_PASS" and (blocking or defective or incomplete):
        errors.append("BOUNDED_PASS contradicts mandatory coverage/findings")
    if disposition in {"FAIL", "CHANGES_REQUIRED"} and not (defective or blocking):
        errors.append("negative disposition lacks defect evidence")
    if disposition in {"NOT_TESTED", "INSUFFICIENT_EVIDENCE"} and not incomplete:
        errors.append("insufficient disposition lacks incomplete coverage")

    return {
        "valid": not errors,
        "errors": errors,
        "effective_disposition": disposition if not errors else "INVALID_REVIEW_EVIDENCE",
        "all_mandatory_dimensions_supported": all_supported if not errors else False,
    }


def verify_kernel_provenance(actual_kernel_sha256, expected_kernel_sha256):
    if not actual_kernel_sha256 or actual_kernel_sha256 != expected_kernel_sha256:
        return {
            "valid": False,
            "authority_effect": "NONE",
            "reason": "TRUST_KERNEL_PROVENANCE_MISMATCH",
        }
    return {
        "valid": True,
        "authority_effect": "NONE_PENDING_DETERMINISTIC_INGESTION",
        "reason": None,
    }


def classify_candidate_side_execution():
    """Candidate-side workflows can generate evidence but never promotion authority."""
    return {
        "trusted": False,
        "authority_effect": "NONE",
        "reason": "CANDIDATE_CONTROLLED_EXECUTION_PATH",
    }
