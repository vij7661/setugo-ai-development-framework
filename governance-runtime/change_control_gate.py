#!/usr/bin/env python3
"""Deterministic gate for review-finding remediation and change impact.

The gate does not decide whether a reviewer is correct. It verifies that an
already-adjudicated finding set has been handled coherently before a successor
candidate is sent for another review.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any, Mapping, Sequence

SHA40 = re.compile(r"^[0-9a-f]{40}$")
ALLOWED_DISPOSITIONS = {
    "ACCEPT", "PARTIAL_ACCEPT", "REJECT", "INSUFFICIENT_EVIDENCE", "PACKET_PROCESS_DEFECT"
}
ALLOWED_CHANGE_CLASSES = {
    "PACKET_PROCESS_DEFECT", "DESIGN_DEFECT", "IMPLEMENTATION_DEFECT",
    "TEST_FIXTURE_DEFECT", "DOCUMENTATION_ONLY", "MIXED",
}
ALLOWED_PATH_CLASSES = {
    "INTENDED_REMEDIATION", "REQUIRED_TRANSITIVE_CHANGE", "TEST_OR_EVIDENCE_CHANGE",
    "CLEANUP_WITH_PROVEN_NO_SEMANTIC_CHANGE",
}
READY = "CHANGE_READY_FOR_REVIEW"
NOT_READY = "CHANGE_NOT_READY"
PACKET_REPAIR = "NO_DESIGN_CHANGE_PACKET_REPAIR"


def _is_sha(value: Any) -> bool:
    return isinstance(value, str) and bool(SHA40.fullmatch(value))


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def git_changed_paths(repo: Path, base: str, head: str) -> list[str]:
    cp = subprocess.run(
        ["git", "diff", "--name-only", base, head, "--"], cwd=repo,
        text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8",
    )
    if cp.returncode:
        raise RuntimeError(cp.stderr.strip() or "git diff failed")
    return sorted({line.strip() for line in cp.stdout.splitlines() if line.strip()})


def validate_change_control(manifest: Mapping[str, Any], actual_changed_paths: Sequence[str]) -> dict[str, Any]:
    errors: list[str] = []
    notes: list[str] = []

    if manifest.get("schema_version") != 1:
        errors.append("CHANGE_SCHEMA_INVALID")
    base = manifest.get("reviewed_candidate_commit")
    head = manifest.get("successor_commit")
    if not _is_sha(base):
        errors.append("CHANGE_BASE_COMMIT_INVALID")
    if not _is_sha(head):
        errors.append("CHANGE_SUCCESSOR_COMMIT_INVALID")

    change_class = manifest.get("change_class")
    if change_class not in ALLOWED_CHANGE_CLASSES:
        errors.append("CHANGE_CLASS_INVALID")

    findings = manifest.get("findings")
    if not isinstance(findings, list) or not findings:
        errors.append("CHANGE_FINDINGS_REQUIRED")
        findings = []

    unresolved_blocking = False
    accepted_change_required = False
    same_family_requires_generalization = False
    seen_ids: set[str] = set()
    for idx, finding in enumerate(findings):
        if not isinstance(finding, Mapping):
            errors.append(f"CHANGE_FINDING_MALFORMED:{idx}")
            continue
        fid = finding.get("id")
        if not _nonempty(fid) or fid in seen_ids:
            errors.append(f"CHANGE_FINDING_ID_INVALID:{idx}")
            continue
        seen_ids.add(str(fid))
        disp = finding.get("disposition")
        if disp not in ALLOWED_DISPOSITIONS:
            errors.append(f"CHANGE_FINDING_DISPOSITION_INVALID:{fid}")
        sev = str(finding.get("severity", "")).upper()
        if sev in {"CRITICAL", "HIGH"} and disp in {"INSUFFICIENT_EVIDENCE"}:
            unresolved_blocking = True
        if disp in {"ACCEPT", "PARTIAL_ACCEPT"}:
            if not _nonempty(finding.get("affected_invariant")):
                errors.append(f"CHANGE_FINDING_INVARIANT_REQUIRED:{fid}")
            if not _nonempty(finding.get("root_cause_class")):
                errors.append(f"CHANGE_FINDING_ROOT_CAUSE_REQUIRED:{fid}")
            if finding.get("requires_change", True):
                accepted_change_required = True
            repeats = finding.get("same_family_consecutive_reviews", 0)
            if not isinstance(repeats, int) or repeats < 0:
                errors.append(f"CHANGE_FINDING_REPEAT_COUNT_INVALID:{fid}")
            elif repeats >= 2:
                same_family_requires_generalization = True
                if finding.get("remediation_scope") != "GENERALIZED_INVARIANT":
                    errors.append(f"CHANGE_REPEATED_FAMILY_REQUIRES_GENERALIZATION:{fid}")

    if unresolved_blocking:
        errors.append("CHANGE_BLOCKING_FINDING_UNRESOLVED")

    if manifest.get("all_findings_adjudicated") is not True:
        errors.append("CHANGE_FINDINGS_NOT_FULLY_ADJUDICATED")
    if manifest.get("intermediate_partial_repair") is True:
        errors.append("CHANGE_PARTIAL_REPAIR_NOT_REVIEW_READY")

    impact = manifest.get("impact_manifest")
    if not isinstance(impact, Mapping):
        errors.append("CHANGE_IMPACT_MANIFEST_REQUIRED")
        impact = {}
    direct = set(x for x in _list(impact.get("direct_paths")) if isinstance(x, str) and x)
    transitive = set(x for x in _list(impact.get("transitive_paths")) if isinstance(x, str) and x)
    no_change = set(x for x in _list(impact.get("no_change_required_paths")) if isinstance(x, str) and x)
    if accepted_change_required and not direct:
        errors.append("CHANGE_DIRECT_IMPACT_REQUIRED")
    if impact.get("unknown_impact") is True:
        errors.append("CHANGE_IMPACT_INSUFFICIENT_EVIDENCE")

    compatibility = impact.get("compatibility_strategy")
    contract_changed = bool(impact.get("contract_or_state_changed"))
    allowed_compat = {
        "NOT_APPLICABLE", "BACKWARD_COMPATIBLE_ADDITIVE", "VERSIONED_DUAL_READ_WRITE",
        "EXPLICIT_MIGRATION_WITH_ROLLBACK", "GOVERNED_BREAKING_CHANGE",
    }
    if contract_changed and compatibility not in allowed_compat - {"NOT_APPLICABLE"}:
        errors.append("CHANGE_COMPATIBILITY_STRATEGY_REQUIRED")
    elif not contract_changed and compatibility not in allowed_compat:
        errors.append("CHANGE_COMPATIBILITY_STRATEGY_INVALID")

    classifications = manifest.get("changed_path_classification")
    if not isinstance(classifications, Mapping):
        errors.append("CHANGE_PATH_CLASSIFICATION_REQUIRED")
        classifications = {}

    actual = set(actual_changed_paths)
    classified = set()
    for path, cls in classifications.items():
        if not isinstance(path, str) or not path:
            errors.append("CHANGE_PATH_INVALID")
            continue
        if cls not in ALLOWED_PATH_CLASSES:
            errors.append(f"CHANGE_PATH_CLASS_INVALID:{path}")
        classified.add(path)

    for path in sorted(actual - classified):
        errors.append(f"UNACCOUNTED_CHANGE:{path}")
    for path in sorted(classified - actual):
        errors.append(f"CLASSIFIED_PATH_NOT_CHANGED:{path}")

    required_impacted = direct | transitive
    for path in sorted(required_impacted - actual - no_change):
        errors.append(f"IMPACT_PATH_NOT_RECONCILED:{path}")

    cleanup = [p for p, cls in classifications.items() if cls == "CLEANUP_WITH_PROVEN_NO_SEMANTIC_CHANGE"]
    cleanup_evidence = impact.get("cleanup_no_semantic_change_evidence", {})
    for path in cleanup:
        if not isinstance(cleanup_evidence, Mapping) or not _nonempty(cleanup_evidence.get(path)):
            errors.append(f"CLEANUP_SEMANTIC_EVIDENCE_REQUIRED:{path}")

    tests = manifest.get("validation_obligations")
    if not isinstance(tests, list) or not tests:
        errors.append("CHANGE_VALIDATION_OBLIGATIONS_REQUIRED")
        tests = []
    for idx, item in enumerate(tests):
        if not isinstance(item, Mapping):
            errors.append(f"CHANGE_VALIDATION_MALFORMED:{idx}")
            continue
        oid = item.get("id")
        status = item.get("status")
        required = item.get("required", True)
        if not _nonempty(oid):
            errors.append(f"CHANGE_VALIDATION_ID_INVALID:{idx}")
        if status not in {"PASS", "FAIL", "NOT_APPLICABLE", "NOT_VERIFIED"}:
            errors.append(f"CHANGE_VALIDATION_STATUS_INVALID:{oid}")
        if required is True and status != "PASS":
            errors.append(f"CHANGE_REQUIRED_VALIDATION_NOT_PASS:{oid}:{status}")
        if status == "PASS" and not _nonempty(item.get("evidence")):
            errors.append(f"CHANGE_VALIDATION_EVIDENCE_REQUIRED:{oid}")

    cleanliness = manifest.get("cleanliness_checks")
    if not isinstance(cleanliness, Mapping):
        errors.append("CHANGE_CLEANLINESS_CHECKS_REQUIRED")
        cleanliness = {}
    for check in manifest.get("required_cleanliness_checks", []):
        result = cleanliness.get(check)
        if not isinstance(result, Mapping) or result.get("status") != "PASS" or not _nonempty(result.get("evidence")):
            errors.append(f"CHANGE_CLEANLINESS_REQUIRED_NOT_PASS:{check}")

    if manifest.get("previous_green_reachable_surface_regressed") is True:
        errors.append("CHANGE_NEW_REGRESSION_DETECTED")
    if manifest.get("test_removed_or_weakened_without_disposition") is True:
        errors.append("CHANGE_TEST_OBLIGATION_SILENTLY_WEAKENED")
    if manifest.get("production_test_only_branch_added") is True:
        errors.append("CHANGE_TEST_ONLY_PRODUCTION_BRANCH_REJECTED")
    if manifest.get("duplicate_authoritative_logic_added") is True:
        errors.append("CHANGE_DUPLICATE_AUTHORITY_LOGIC_REJECTED")

    design_changed = manifest.get("design_candidate_changed")
    if change_class == "PACKET_PROCESS_DEFECT" and design_changed is False and not errors:
        result = PACKET_REPAIR
    else:
        if change_class in {"DESIGN_DEFECT", "MIXED"} and design_changed is not True:
            errors.append("CHANGE_DESIGN_CLASS_REQUIRES_NEW_DESIGN_CANDIDATE")
        result = NOT_READY if errors else READY

    if same_family_requires_generalization:
        notes.append("repeated defect family: generalized invariant remediation required")

    return {
        "schema_version": 1,
        "result": NOT_READY if errors else result,
        "reviewed_candidate_commit": base,
        "successor_commit": head,
        "actual_changed_paths": sorted(actual),
        "error_count": len(errors),
        "errors": errors,
        "notes": notes,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--repo", default=".")
    ap.add_argument("--report")
    args = ap.parse_args()
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    base = str(manifest.get("reviewed_candidate_commit", ""))
    head = str(manifest.get("successor_commit", ""))
    try:
        paths = git_changed_paths(Path(args.repo), base, head)
    except Exception as exc:
        report = {"schema_version": 1, "result": NOT_READY, "errors": [f"CHANGE_DIFF_UNAVAILABLE:{exc}"]}
    else:
        report = validate_change_control(manifest, paths)
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.report:
        Path(args.report).write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if report.get("result") in {READY, PACKET_REPAIR} else 2


if __name__ == "__main__":
    raise SystemExit(main())
