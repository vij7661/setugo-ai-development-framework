#!/usr/bin/env python3
"""Validate deliberate reviewer change/impact questions and supplied verification evidence."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Mapping, Sequence

SHA40 = re.compile(r"^[0-9a-f]{40}$")
CHANGE_REQUIRED_VALUES = {"YES", "NO", "INSUFFICIENT_EVIDENCE"}
EVIDENCE_STATUSES = {"PRESENT", "NOT_APPLICABLE", "UNAVAILABLE"}
REVIEW_MODES = {"CLEAN_INDEPENDENT_REVIEW", "REMEDIATION_VERIFICATION_REVIEW"}
MANDATORY_EVIDENCE_CLASSES = {
    "EXACT_CANDIDATE_ARTIFACTS",
    "BASE_TO_CANDIDATE_DIFF",
    "APPLICABLE_CONTRACTS",
    "EXISTING_CODE_IMPACT_SURFACE",
    "INTERFACES_SCHEMAS_STATE",
    "CURRENT_TESTS_AND_RESULTS",
    "KNOWN_FAILURES_AND_DEFERRED",
    "RUNTIME_EXECUTION_EVIDENCE",
}
MANDATORY_RECOMMENDATION_FIELDS = {
    "finding_id",
    "minimum_required_change",
    "why_required",
    "affected_existing_surfaces",
    "regression_risks",
    "evidence_to_verify_fix",
}
MANDATORY_OUTPUT_FIELDS = {
    "changes_required",
    "change_recommendations",
    "existing_system_impact",
    "verification_requirements",
    "missing_evidence",
}


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _paths_from_evidence_refs(refs: Any) -> set[str]:
    out: set[str] = set()
    if isinstance(refs, list):
        for item in refs:
            if isinstance(item, Mapping) and item.get("type") in {"file", "artifact"}:
                ref = item.get("ref")
                if isinstance(ref, str) and ref:
                    out.add(ref)
    return out


def validate_review_change_impact_contract(
    container: Mapping[str, Any],
    *,
    candidate_commit: str,
    available_artifact_paths: Sequence[str] | None = None,
) -> dict[str, Any]:
    errors: list[str] = []
    notes: list[str] = []

    if not isinstance(candidate_commit, str) or not SHA40.fullmatch(candidate_commit):
        errors.append("REVIEW_CHANGE_CANDIDATE_INVALID")

    mode = container.get("review_mode")
    if mode not in REVIEW_MODES:
        errors.append("REVIEW_CHANGE_MODE_INVALID")

    contract = container.get("review_change_impact_contract")
    if not isinstance(contract, Mapping):
        errors.append("REVIEW_CHANGE_CONTRACT_REQUIRED")
        contract = {}
    elif contract.get("schema_version") != 1:
        errors.append("REVIEW_CHANGE_CONTRACT_SCHEMA_INVALID")

    deliberate_question = contract.get("deliberate_question")
    if not _nonempty(deliberate_question):
        errors.append("REVIEW_CHANGE_QUESTION_REQUIRED")
    elif deliberate_question.strip() != "Are changes required for this exact candidate?":
        errors.append("REVIEW_CHANGE_QUESTION_NOT_EXACT")

    vocab = contract.get("changes_required_vocabulary")
    if not isinstance(vocab, list) or set(vocab) != CHANGE_REQUIRED_VALUES:
        errors.append("REVIEW_CHANGE_VOCABULARY_INVALID")

    required_output = contract.get("required_output_fields")
    if not isinstance(required_output, list) or not MANDATORY_OUTPUT_FIELDS.issubset(set(required_output)):
        errors.append("REVIEW_CHANGE_OUTPUT_CONTRACT_INCOMPLETE")

    rec_fields = contract.get("required_recommendation_fields")
    if not isinstance(rec_fields, list) or not MANDATORY_RECOMMENDATION_FIELDS.issubset(set(rec_fields)):
        errors.append("REVIEW_CHANGE_RECOMMENDATION_CONTRACT_INCOMPLETE")

    for flag in (
        "require_existing_system_impact",
        "require_regression_risks",
        "require_verification_evidence",
        "require_missing_evidence",
        "reviewer_suggestions_non_authoritative",
    ):
        if contract.get(flag) is not True:
            errors.append(f"REVIEW_CHANGE_CONTRACT_FLAG_REQUIRED:{flag}")

    if mode == "CLEAN_INDEPENDENT_REVIEW" and contract.get("prior_reviewer_conclusions_included") is not False:
        errors.append("REVIEW_CHANGE_CLEAN_MODE_CONTAMINATION_FLAG_INVALID")

    evidence = container.get("verification_evidence_manifest")
    if not isinstance(evidence, Mapping):
        errors.append("REVIEW_VERIFICATION_EVIDENCE_MANIFEST_REQUIRED")
        evidence = {}
    elif evidence.get("schema_version") != 1:
        errors.append("REVIEW_VERIFICATION_EVIDENCE_SCHEMA_INVALID")

    if evidence.get("candidate_commit") != candidate_commit:
        errors.append("REVIEW_VERIFICATION_EVIDENCE_CANDIDATE_MISMATCH")

    entries = evidence.get("evidence_classes")
    if not isinstance(entries, list):
        errors.append("REVIEW_VERIFICATION_EVIDENCE_CLASSES_REQUIRED")
        entries = []

    by_id: dict[str, Mapping[str, Any]] = {}
    for idx, item in enumerate(entries):
        if not isinstance(item, Mapping):
            errors.append(f"REVIEW_VERIFICATION_EVIDENCE_ENTRY_MALFORMED:{idx}")
            continue
        eid = item.get("id")
        if not _nonempty(eid) or eid in by_id:
            errors.append(f"REVIEW_VERIFICATION_EVIDENCE_ID_INVALID:{idx}")
            continue
        by_id[str(eid)] = item
        status = item.get("status")
        if status not in EVIDENCE_STATUSES:
            errors.append(f"REVIEW_VERIFICATION_EVIDENCE_STATUS_INVALID:{eid}")
            continue
        required = item.get("required_for_review")
        if not isinstance(required, bool):
            errors.append(f"REVIEW_VERIFICATION_EVIDENCE_REQUIRED_FLAG_INVALID:{eid}")
        if required is True and status != "PRESENT":
            errors.append(f"REVIEW_VERIFICATION_REQUIRED_EVIDENCE_NOT_PRESENT:{eid}:{status}")
        refs = item.get("refs")
        if status == "PRESENT":
            if not isinstance(refs, list) or not any(_nonempty(x) for x in refs):
                errors.append(f"REVIEW_VERIFICATION_EVIDENCE_REFS_REQUIRED:{eid}")
        else:
            if not _nonempty(item.get("reason")):
                errors.append(f"REVIEW_VERIFICATION_EVIDENCE_REASON_REQUIRED:{eid}")

    for eid in sorted(MANDATORY_EVIDENCE_CLASSES - set(by_id)):
        errors.append(f"REVIEW_VERIFICATION_EVIDENCE_CLASS_MISSING:{eid}")

    available = set(available_artifact_paths or ())
    if not available:
        available |= _paths_from_evidence_refs(container.get("evidence_refs"))
    if available:
        for eid, item in by_id.items():
            if item.get("status") != "PRESENT":
                continue
            for ref in item.get("refs", []):
                if isinstance(ref, str) and ref.startswith("path:"):
                    path = ref[5:]
                    if path not in available:
                        errors.append(f"REVIEW_VERIFICATION_EVIDENCE_REF_NOT_SUPPLIED:{eid}:{path}")

    questions = container.get("review_questions")
    if isinstance(questions, list) and _nonempty(deliberate_question):
        if deliberate_question not in questions:
            errors.append("REVIEW_CHANGE_QUESTION_NOT_IN_REVIEW_QUESTIONS")
    elif "review_questions" in container:
        errors.append("REVIEW_CHANGE_REVIEW_QUESTIONS_INVALID")

    if not errors:
        notes.append("review change-impact contract and required evidence are review-dispatch ready")

    return {
        "schema_version": 1,
        "result": "REVIEW_CHANGE_IMPACT_READY" if not errors else "REVIEW_CHANGE_IMPACT_NOT_READY",
        "candidate_commit": candidate_commit,
        "error_count": len(errors),
        "errors": errors,
        "notes": notes,
    }


def mandatory_reviewer_instructions(contract: Mapping[str, Any]) -> str:
    return """## Mandatory change and existing-system impact assessment

Deliberately answer: **Are changes required for this exact candidate?** Return exactly `YES`, `NO`, or `INSUFFICIENT_EVIDENCE`.

For every finding that requires change, provide: finding ID; violated invariant/requirement; concrete failure path; minimum required semantic change; why it is required; affected existing code/components/interfaces/state/tests visible in the supplied evidence; regression/compatibility risks; evidence/tests that would verify the repair; and acceptable alternative repair criteria where appropriate.

Separately assess existing-system impact across direct code, callers/dependents, APIs/schemas, events/state/ledgers/migrations, providers/adapters/external effects, configuration/policy/credentials, retries/idempotency/recovery/caches/replicas, tests/fixtures/mocks, telemetry/audit/proof views, and compatibility/rollback. If the supplied evidence is insufficient for any material point, list the exact missing evidence instead of speculating.

Your recommended change is evidence, not executable authority. Do not assume your implementation wording must be followed; state the invariant and verification criteria the repair must satisfy.
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--candidate-commit")
    args = ap.parse_args()
    obj = json.loads(Path(args.input).read_text(encoding="utf-8"))
    candidate = args.candidate_commit or obj.get("artifact", {}).get("commit") or obj.get("candidate_commit", "")
    report = validate_review_change_impact_contract(obj, candidate_commit=str(candidate))
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["result"] == "REVIEW_CHANGE_IMPACT_READY" else 2


if __name__ == "__main__":
    raise SystemExit(main())
