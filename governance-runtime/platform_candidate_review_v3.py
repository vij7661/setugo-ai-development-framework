#!/usr/bin/env python3
"""Governed API review wrapper requiring deliberate change/impact assessment output."""
from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any, Mapping

import platform_candidate_review as legacy
import platform_candidate_review_v2 as v2
from review_change_impact_gate import (
    CHANGE_REQUIRED_VALUES,
    MANDATORY_RECOMMENDATION_FIELDS,
    mandatory_reviewer_instructions,
    validate_review_change_impact_contract,
)


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_change_assessment_output(review: Mapping[str, Any], contract: Mapping[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    assessment = review.get("change_assessment")
    if not isinstance(assessment, Mapping):
        errors.append("REVIEW_CHANGE_ASSESSMENT_OUTPUT_REQUIRED")
        assessment = {}

    changes_required = assessment.get("changes_required")
    if changes_required not in CHANGE_REQUIRED_VALUES:
        errors.append("REVIEW_CHANGE_ASSESSMENT_VALUE_INVALID")

    recs = assessment.get("change_recommendations")
    if not isinstance(recs, list):
        errors.append("REVIEW_CHANGE_RECOMMENDATIONS_REQUIRED")
        recs = []
    if changes_required == "YES" and not recs:
        errors.append("REVIEW_CHANGE_RECOMMENDATION_REQUIRED_WHEN_YES")

    required_fields = set(contract.get("required_recommendation_fields", []))
    required_fields |= MANDATORY_RECOMMENDATION_FIELDS
    for idx, rec in enumerate(recs):
        if not isinstance(rec, Mapping):
            errors.append(f"REVIEW_CHANGE_RECOMMENDATION_MALFORMED:{idx}")
            continue
        for field in sorted(required_fields):
            value = rec.get(field)
            if field in {"affected_existing_surfaces", "regression_risks"}:
                if not isinstance(value, list):
                    errors.append(f"REVIEW_CHANGE_RECOMMENDATION_FIELD_REQUIRED:{idx}:{field}")
            elif not _nonempty(value):
                errors.append(f"REVIEW_CHANGE_RECOMMENDATION_FIELD_REQUIRED:{idx}:{field}")

    if "existing_system_impact" not in assessment:
        errors.append("REVIEW_EXISTING_SYSTEM_IMPACT_REQUIRED")
    if not isinstance(assessment.get("verification_requirements"), list):
        errors.append("REVIEW_VERIFICATION_REQUIREMENTS_REQUIRED")
    missing = assessment.get("missing_evidence")
    if not isinstance(missing, list):
        errors.append("REVIEW_MISSING_EVIDENCE_LIST_REQUIRED")
    if changes_required == "INSUFFICIENT_EVIDENCE" and not missing:
        errors.append("REVIEW_MISSING_EVIDENCE_REQUIRED_WHEN_INSUFFICIENT")

    return {
        "schema_version": 1,
        "valid": not errors,
        "errors": errors,
        "effective_change_assessment": changes_required if not errors else "INVALID_CHANGE_ASSESSMENT",
    }


def _augment_prompt(original):
    def wrapped(request, corpus, model):
        base = original(request, corpus, model)
        contract = request.get("review_change_impact_contract", {})
        shape = {
            "change_assessment": {
                "changes_required": "YES | NO | INSUFFICIENT_EVIDENCE",
                "change_recommendations": [{
                    "finding_id": "F1",
                    "minimum_required_change": "semantic requirement, not blind patch",
                    "why_required": "why this change closes the failure",
                    "affected_existing_surfaces": ["exact code/component/interface/state/test surfaces supported by evidence"],
                    "regression_risks": ["specific risks"],
                    "evidence_to_verify_fix": "tests/evidence required to verify closure",
                }],
                "existing_system_impact": {
                    "direct_code": [],
                    "callers_dependents": [],
                    "apis_schemas_state": [],
                    "providers_external_effects": [],
                    "retry_recovery_cache": [],
                    "tests_telemetry": [],
                    "compatibility_rollback": [],
                },
                "verification_requirements": [],
                "missing_evidence": [],
            }
        }
        return (
            base
            + "\n\nMANDATORY ADDITIONAL TOP-LEVEL OUTPUT FIELD:\n"
            + json.dumps(shape, sort_keys=True)
            + "\n"
            + mandatory_reviewer_instructions(contract)
            + "\nThe additional `change_assessment` top-level field is mandatory even though the legacy output shape above predates this contract."
        )
    return wrapped


def main() -> None:
    request_path = None
    for idx, arg in enumerate(sys.argv):
        if arg == "--request" and idx + 1 < len(sys.argv):
            request_path = sys.argv[idx + 1]
            break
    if not request_path:
        raise SystemExit("--request required")

    request = json.loads(Path(request_path).read_text(encoding="utf-8"))
    candidate = str(request.get("artifact", {}).get("commit", ""))
    pre = validate_review_change_impact_contract(request, candidate_commit=candidate)
    if pre["result"] != "REVIEW_CHANGE_IMPACT_READY":
        raise SystemExit("REVIEW_CHANGE_IMPACT_NOT_READY:" + ";".join(pre["errors"]))

    original = legacy.build_prompt
    legacy.build_prompt = _augment_prompt(original)
    try:
        v2.main()
    finally:
        legacy.build_prompt = original

    output_dir = None
    for idx, arg in enumerate(sys.argv):
        if arg == "--output-dir" and idx + 1 < len(sys.argv):
            output_dir = sys.argv[idx + 1]
            break
    if not output_dir:
        raise SystemExit("--output-dir required")

    review_path = Path(output_dir) / "review.json"
    if not review_path.exists():
        raise SystemExit("review.json missing after provider execution")
    review = json.loads(review_path.read_text(encoding="utf-8"))
    validation = validate_change_assessment_output(review, request["review_change_impact_contract"])
    (Path(output_dir) / "review-change-impact-output-validation.json").write_text(
        json.dumps(validation, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    if not validation["valid"]:
        raise SystemExit(5)


if __name__ == "__main__":
    main()
