#!/usr/bin/env python3
from __future__ import annotations

import re
from typing import Any, Mapping, Sequence

PHASES = ("TESTING", "RELEASE", "PRODUCTION")
PHASE_BRANCH = {
    "TESTING": "phase/testing",
    "RELEASE": "phase/release",
    "PRODUCTION": "phase/production",
}
PHASE_ORDER = {name: i for i, name in enumerate(PHASES)}
SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")

DEFAULT_REVIEW_TRANSPORT = {
    "TESTING": "MANUAL",
    "RELEASE": "MANUAL_OR_API_WHEN_JUSTIFIED",
    "PRODUCTION": "AUTHENTICATED_API_OR_OTHER_TRUSTED_PROVENANCE",
}

DEFAULT_API_POLICY = {
    "TESTING": "NO_EXTERNAL_API_BY_DEFAULT",
    "RELEASE": "API_ALLOWED_WHEN_BOUNDARY_IS_READY_FOR_REAL_INTEGRATION",
    "PRODUCTION": "REAL_API_AND_ENVIRONMENT_QUALIFICATION_REQUIRED_WHERE_APPLICABLE",
}

PHASE_PROMOTION_TARGET = {
    "TESTING": "RELEASE",
    "RELEASE": "PRODUCTION",
    "PRODUCTION": None,
}

TESTING_MANDATORY_REVIEW_TRIGGERS = frozenset({
    "MATERIAL_AUTHORITY_TRANSITION",
    "EXTERNAL_API_BOUNDARY",
    "CONCURRENCY_OR_RECOVERY_BOUNDARY",
    "SECURITY_BOUNDARY",
    "FROZEN_CONTRACT_REQUIRES_REVIEW",
    "GOVERNANCE_RELEVANT_CHANGE",
})
GOVERNANCE_RELEVANT_PREFIXES = (
    "governance-runtime/", "standards/", "experiments/governed-platform/", ".github/workflows/",
)

TESTING_REVIEW_INSTRUCTION = (
    "This is a TESTING/FALSIFICATION review of release-quality code, not a production-readiness review. "
    "Focus on the frozen testing contract, correctness, false-green risk, crash/concurrency/recovery/security behavior, "
    "test quality, regressions, and bounded implementation claims. Production-only gaps that do not violate the current "
    "testing contract must be recorded as DEFERRED_TO_RELEASE or DEFERRED_TO_PRODUCTION rather than blocking TESTING."
)

RELEASE_REVIEW_INSTRUCTION = (
    "This is a RELEASE-QUALIFICATION review. Focus on integrated behavior, migration/recovery, configuration, real API "
    "readiness where enabled, performance/resource boundaries, artifact reproducibility, security qualification, and release blockers. "
    "Production-environment-only concerns may be recorded as DEFERRED_TO_PRODUCTION unless they block release qualification."
)

PRODUCTION_REVIEW_INSTRUCTION = (
    "This is a PRODUCTION-QUALIFICATION review. Evaluate authenticated provenance, production IAM/credentials, deployment and rollback "
    "controls, production observability/auditability, environment-specific risks, operational safety, and explicit release authority."
)

REVIEW_INSTRUCTION = {
    "TESTING": TESTING_REVIEW_INSTRUCTION,
    "RELEASE": RELEASE_REVIEW_INSTRUCTION,
    "PRODUCTION": PRODUCTION_REVIEW_INSTRUCTION,
}


class PhasePolicyError(ValueError):
    pass


def validate_phase(phase: str) -> str:
    p = str(phase).upper()
    if p not in PHASES:
        raise PhasePolicyError(f"unsupported phase: {phase}")
    return p


def phase_branch(phase: str) -> str:
    return PHASE_BRANCH[validate_phase(phase)]


def testing_review_requirement(*, material_transition: bool = False,
                               external_api_boundary: bool = False,
                               concurrency_or_recovery_boundary: bool = False,
                               security_boundary: bool = False,
                               frozen_contract_requires_review: bool = False,
                               changed_paths: Sequence[str] = ()) -> dict[str, Any]:
    triggers: list[str] = []
    if material_transition:
        triggers.append("MATERIAL_AUTHORITY_TRANSITION")
    if external_api_boundary:
        triggers.append("EXTERNAL_API_BOUNDARY")
    if concurrency_or_recovery_boundary:
        triggers.append("CONCURRENCY_OR_RECOVERY_BOUNDARY")
    if security_boundary:
        triggers.append("SECURITY_BOUNDARY")
    if frozen_contract_requires_review:
        triggers.append("FROZEN_CONTRACT_REQUIRES_REVIEW")
    if any(any(str(path).startswith(prefix) for prefix in GOVERNANCE_RELEVANT_PREFIXES) for path in changed_paths):
        triggers.append("GOVERNANCE_RELEVANT_CHANGE")
    level = "REQUIRED" if triggers else "RECOMMENDED"
    return {
        "review_level": level,
        "mandatory_triggers": sorted(set(triggers)),
        "review_transport_default": "MANUAL",
        "transport_default_does_not_define_review_level": True,
        "review_artifact_required_for_testing_pass": level == "REQUIRED",
    }


def review_transport_policy(phase: str, *, api_boundary_under_test: bool = False,
                            user_approved_api: bool = False,
                            api_approval_ref: str | None = None) -> dict[str, Any]:
    p = validate_phase(phase)
    structured_user_approval = bool(
        user_approved_api and isinstance(api_approval_ref, str) and api_approval_ref.strip()
    )
    if p == "TESTING":
        api_allowed = bool(api_boundary_under_test or structured_user_approval)
        return {
            "default_transport": "MANUAL",
            "external_api_allowed": api_allowed,
            "external_api_reason_required": api_allowed,
            "api_boundary_under_test": bool(api_boundary_under_test),
            "structured_user_api_approval": structured_user_approval,
            "api_approval_ref": api_approval_ref if structured_user_approval else None,
            "chat_message_alone_is_api_approval": False,
            "automatic_api_dispatch": False,
            "ask_user_before_review": True,
            "manual_review_can_satisfy_phase_review_gate": True,
            "manual_review_can_establish_production_qualification": False,
        }
    if p == "RELEASE":
        return {
            "default_transport": "MANUAL_OR_API_WHEN_JUSTIFIED",
            "external_api_allowed": True,
            "external_api_reason_required": True,
            "structured_user_api_approval": structured_user_approval,
            "api_approval_ref": api_approval_ref if structured_user_approval else None,
            "chat_message_alone_is_api_approval": False,
            "automatic_api_dispatch": False,
            "ask_user_before_review": True,
            "manual_review_can_satisfy_phase_review_gate": True,
            "manual_review_can_establish_production_qualification": False,
        }
    return {
        "default_transport": "AUTHENTICATED_API_OR_OTHER_TRUSTED_PROVENANCE",
        "external_api_allowed": True,
        "external_api_reason_required": True,
        "structured_user_api_approval": structured_user_approval,
        "api_approval_ref": api_approval_ref if structured_user_approval else None,
        "chat_message_alone_is_api_approval": False,
        "automatic_api_dispatch": False,
        "ask_user_before_review": True,
        "manual_review_can_satisfy_phase_review_gate": False,
        "manual_review_can_establish_production_qualification": False,
    }


def build_phase_review_boundary(*, phase: str, review_scope: Sequence[str], required_dimensions: Sequence[str],
                                explicit_nonclaims: Sequence[str], out_of_scope_dimensions: Sequence[str],
                                allowed_evidence: Sequence[str], api_boundary_under_test: bool = False,
                                user_approved_api: bool = False, api_approval_ref: str | None = None,
                                material_transition: bool = False,
                                concurrency_or_recovery_boundary: bool = False,
                                security_boundary: bool = False,
                                frozen_contract_requires_review: bool = False,
                                changed_paths: Sequence[str] = ()) -> dict[str, Any]:
    p = validate_phase(phase)
    if not review_scope:
        raise PhasePolicyError("review_scope must not be empty")
    if not required_dimensions:
        raise PhasePolicyError("required_dimensions must not be empty")
    if len(set(required_dimensions)) != len(tuple(required_dimensions)):
        raise PhasePolicyError("required_dimensions must be unique")
    overlap = set(required_dimensions) & set(out_of_scope_dimensions)
    if overlap:
        raise PhasePolicyError(f"dimensions cannot be both required and out-of-scope: {sorted(overlap)}")
    boundary = {
        "phase": p,
        "phase_branch": PHASE_BRANCH[p],
        "review_scope": list(review_scope),
        "required_dimensions": list(required_dimensions),
        "explicit_nonclaims": list(explicit_nonclaims),
        "out_of_scope_dimensions": list(out_of_scope_dimensions),
        "allowed_evidence": list(allowed_evidence),
        "review_transport_policy": review_transport_policy(
            p,
            api_boundary_under_test=api_boundary_under_test,
            user_approved_api=user_approved_api,
            api_approval_ref=api_approval_ref,
        ),
        "reviewer_instruction": REVIEW_INSTRUCTION[p],
        "promotion_target": PHASE_PROMOTION_TARGET[p],
        "reviewer_consensus_is_authority": False,
        "raw_finding_becomes_governance_rule_automatically": False,
        "material_finding_requires_adjudication": True,
    }
    if p == "TESTING":
        boundary["review_requirement"] = testing_review_requirement(
            material_transition=material_transition,
            external_api_boundary=api_boundary_under_test,
            concurrency_or_recovery_boundary=concurrency_or_recovery_boundary,
            security_boundary=security_boundary,
            frozen_contract_requires_review=frozen_contract_requires_review,
            changed_paths=changed_paths,
        )
    return boundary


def classify_finding_for_phase(*, phase: str, finding_phase: str, violates_current_contract: bool) -> str:
    current = validate_phase(phase)
    target = validate_phase(finding_phase)
    if violates_current_contract:
        return "BLOCK_CURRENT_PHASE_PENDING_ADJUDICATION"
    if PHASE_ORDER[target] <= PHASE_ORDER[current]:
        return "CURRENT_PHASE_EVIDENCE_PENDING_ADJUDICATION"
    return "DEFERRED_TO_RELEASE" if target == "RELEASE" else "DEFERRED_TO_PRODUCTION"


def validate_adjudication_record(record: Mapping[str, Any]) -> dict[str, Any]:
    required = {
        "finding_id", "candidate_sha", "original_review_evidence_hash",
        "adjudication_decision", "root_cause_classification",
        "review_evidence_ref", "adjudicator_identity_claim",
    }
    missing = required - set(record.keys())
    if missing:
        raise PhasePolicyError(f"adjudication record missing fields: {sorted(missing)}")
    if not isinstance(record["finding_id"], str) or not record["finding_id"].strip():
        raise PhasePolicyError("finding_id is required")
    if not SHA40.fullmatch(str(record["candidate_sha"])):
        raise PhasePolicyError("adjudication candidate_sha must be exact lowercase SHA40")
    if not SHA256.fullmatch(str(record["original_review_evidence_hash"])):
        raise PhasePolicyError("original_review_evidence_hash must be lowercase SHA256")
    decision = str(record["adjudication_decision"]).upper()
    if decision not in {"ACCEPT", "REJECT", "SPLIT"}:
        raise PhasePolicyError("adjudication_decision must be ACCEPT, REJECT, or SPLIT")
    root = str(record["root_cause_classification"]).strip()
    if not root:
        raise PhasePolicyError("root_cause_classification is required")
    reproduction = record.get("reproduction_artifact")
    process_defect = record.get("reproduction_exception")
    if decision in {"ACCEPT", "SPLIT"}:
        if reproduction is None and process_defect != "GOVERNANCE_PROCESS_DEFECT":
            raise PhasePolicyError(
                "accepted/split material finding requires reproduction_artifact or GOVERNANCE_PROCESS_DEFECT exception"
            )
        if process_defect == "GOVERNANCE_PROCESS_DEFECT":
            governance_change_sha = record.get("governance_change_sha")
            if not SHA40.fullmatch(str(governance_change_sha or "")):
                raise PhasePolicyError(
                    "GOVERNANCE_PROCESS_DEFECT reproduction exception requires governance_change_sha"
                )
    if reproduction is not None:
        if not isinstance(reproduction, Mapping):
            raise PhasePolicyError("reproduction_artifact must be an object")
        if not reproduction.get("evidence_ref"):
            raise PhasePolicyError("reproduction_artifact.evidence_ref is required")
        test_sha = reproduction.get("test_sha")
        if test_sha is not None and not SHA40.fullmatch(str(test_sha)):
            raise PhasePolicyError("reproduction_artifact.test_sha must be SHA40 when present")
    out = dict(record)
    out["adjudication_decision"] = decision
    out["schema_valid"] = True
    out["reviewer_finding_is_authority"] = False
    return out


def validate_promotion(*, source_phase: str, destination_phase: str, source_branch: str,
                       destination_branch: str, source_sha: str, qualified_sha: str) -> dict[str, Any]:
    src = validate_phase(source_phase)
    dst = validate_phase(destination_phase)
    if PHASE_ORDER[dst] != PHASE_ORDER[src] + 1:
        raise PhasePolicyError("GOVERNANCE_INVALID_PROMOTION: phase promotion must advance exactly one phase")
    if source_branch != PHASE_BRANCH[src] or destination_branch != PHASE_BRANCH[dst]:
        raise PhasePolicyError("GOVERNANCE_INVALID_PROMOTION: promotion branch does not match governed phase")
    if source_sha != qualified_sha:
        raise PhasePolicyError("GOVERNANCE_INVALID_PROMOTION: promotion must use the exact qualified source SHA")
    return {
        "source_phase": src,
        "destination_phase": dst,
        "source_branch": source_branch,
        "destination_branch": destination_branch,
        "source_sha": source_sha,
        "qualified_sha": qualified_sha,
        "promotion_direction_valid": True,
        "raw_reviewer_findings_forwarded_as_rules": False,
        "adjudicated_evidence_required": True,
    }


def testing_phase_pass_requirements() -> dict[str, Any]:
    return {
        "phase": "TESTING",
        "code_quality_target": "RELEASE_LEVEL",
        "required": [
            "frozen_contract_satisfied",
            "required_acceptance_cases_pass",
            "standard_adversarial_matrix_exercised",
            "relevant_regressions_pass",
            "all_observed_failures_classified",
            "no_unresolved_material_code_test_fixture_or_requirement_defect",
            "testing_review_level_and_triggers_recorded",
            "review_artifact_present_for_REQUIRED_testing_review",
            "all_review_findings_have_schema_valid_adjudication_records",
            "accepted_or_split_material_findings_have_reproduction_or_governance_process_defect_record",
            "coding_agent_changed_artifacts_independently_observed_where_coding_agent_used",
            "coding_agent_stop_conditions_enforced_where_coding_agent_used",
            "agent_generated_governance_validation_tokens_rejected_as_evidence",
            "exact_candidate_sha_requalified_after_last_repair",
            "integrated_release_scope_regressions_pass_before_phase_promotion",
            "explicit_untested_and_deferred_risks_recorded",
        ],
        "bounded_pass_rule": (
            "BOUNDED_PASS may close TESTING only when every mandatory dimension is closed; "
            "each remaining bound is explicitly non-mandatory, recorded, and cannot silently satisfy a later RELEASE requirement."
        ),
        "means": "READY_TO_BEGIN_RELEASE_QUALIFICATION",
        "does_not_mean": "PRODUCTION_READY",
    }
