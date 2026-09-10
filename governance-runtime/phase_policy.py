#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
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


def _canon(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def validate_phase(phase: str) -> str:
    p = str(phase).upper()
    if p not in PHASES:
        raise PhasePolicyError(f"unsupported phase: {phase}")
    return p


def phase_branch(phase: str) -> str:
    return PHASE_BRANCH[validate_phase(phase)]


def testing_review_requirement(*, touches_governance: bool, touches_security_boundary: bool,
                               touches_external_side_effect: bool, alters_frozen_artifact_after_exposure: bool,
                               testing_phase_exit: bool, touches_external_api_boundary: bool = False) -> str:
    flags = (
        touches_governance,
        touches_security_boundary,
        touches_external_side_effect,
        alters_frozen_artifact_after_exposure,
        testing_phase_exit,
        touches_external_api_boundary,
    )
    if any(not isinstance(x, bool) for x in flags):
        raise PhasePolicyError("testing review trigger flags must be booleans")
    if any(flags):
        return "REQUIRED"
    return "RECOMMENDED"


def validate_testing_review_evidence(*, review_requirement: str, review_performed: bool,
                                     adjudication_complete: bool) -> dict[str, Any]:
    requirement = str(review_requirement).upper()
    if requirement not in {"NONE", "RECOMMENDED", "REQUIRED"}:
        raise PhasePolicyError("invalid testing review requirement")
    if not isinstance(review_performed, bool) or not isinstance(adjudication_complete, bool):
        raise PhasePolicyError("review evidence flags must be booleans")
    if requirement == "REQUIRED" and not review_performed:
        raise PhasePolicyError("required TESTING review cannot be skipped")
    if review_performed and not adjudication_complete:
        raise PhasePolicyError("performed review does not satisfy a gate until adjudication is complete")
    if not review_performed:
        return {
            "review_requirement": requirement,
            "review_status": "REVIEW_NOT_PERFORMED",
            "adjudication_status": "NOT_APPLICABLE",
            "testing_gate_satisfied": requirement != "REQUIRED",
            "authority_effect": "NONE",
        }
    return {
        "review_requirement": requirement,
        "review_status": "REVIEW_PERFORMED",
        "adjudication_status": "COMPLETE",
        "testing_gate_satisfied": True,
        "authority_effect": "NONE",
    }


def build_api_approval(*, approval_id: str, candidate_sha: str, endpoint: str, purpose: str,
                       scope: str, approved_by: str) -> dict[str, Any]:
    for name, value in (("approval_id", approval_id), ("endpoint", endpoint), ("purpose", purpose), ("scope", scope)):
        if not isinstance(value, str) or not value.strip():
            raise PhasePolicyError(f"{name} is required")
    if not SHA40.fullmatch(str(candidate_sha)):
        raise PhasePolicyError("candidate_sha must be exact lowercase SHA40")
    if approved_by != "USER_EXPLICIT_ACTION":
        raise PhasePolicyError("API approval must come from explicit user action")
    material = {
        "schema_version": 1,
        "approval_id": approval_id,
        "candidate_sha": candidate_sha,
        "endpoint": endpoint,
        "purpose": purpose,
        "scope": scope,
        "approved_by": approved_by,
        "phase": "TESTING",
        "authority_effect": "API_CALL_SCOPE_ONLY",
        "reusable": False,
    }
    material["approval_hash"] = hashlib.sha256(_canon(material)).hexdigest()
    return material


def validate_api_approval(approval: Mapping[str, Any], *, candidate_sha: str, endpoint: str) -> bool:
    if not isinstance(approval, Mapping):
        raise PhasePolicyError("approval must be a mapping")
    if approval.get("phase") != "TESTING" or approval.get("approved_by") != "USER_EXPLICIT_ACTION":
        raise PhasePolicyError("approval is not a valid TESTING user approval")
    if approval.get("candidate_sha") != candidate_sha:
        raise PhasePolicyError("API approval candidate SHA mismatch")
    if approval.get("endpoint") != endpoint:
        raise PhasePolicyError("API approval endpoint mismatch")
    if approval.get("reusable") is not False:
        raise PhasePolicyError("TESTING API approval must be single-use/non-reusable")
    material = dict(approval)
    supplied = material.pop("approval_hash", None)
    if supplied != hashlib.sha256(_canon(material)).hexdigest():
        raise PhasePolicyError("API approval hash mismatch")
    return True


def review_transport_policy(phase: str, *, api_boundary_under_test: bool = False, user_approved_api: bool = False) -> dict[str, Any]:
    p = validate_phase(phase)
    if p == "TESTING":
        api_allowed = bool(api_boundary_under_test or user_approved_api)
        return {
            "default_transport": "MANUAL",
            "external_api_allowed": api_allowed,
            "external_api_reason_required": api_allowed,
            "automatic_api_dispatch": False,
            "ask_user_before_review": True,
            "manual_review_can_satisfy_phase_review_gate": True,
            "manual_review_can_establish_production_qualification": False,
            "user_approval_must_be_structured_if_used_for_api_exception": bool(user_approved_api),
        }
    if p == "RELEASE":
        return {
            "default_transport": "MANUAL_OR_API_WHEN_JUSTIFIED",
            "external_api_allowed": True,
            "external_api_reason_required": True,
            "automatic_api_dispatch": False,
            "ask_user_before_review": True,
            "manual_review_can_satisfy_phase_review_gate": True,
            "manual_review_can_establish_production_qualification": False,
        }
    return {
        "default_transport": "AUTHENTICATED_API_OR_OTHER_TRUSTED_PROVENANCE",
        "external_api_allowed": True,
        "external_api_reason_required": True,
        "automatic_api_dispatch": False,
        "ask_user_before_review": True,
        "manual_review_can_satisfy_phase_review_gate": False,
        "manual_review_can_establish_production_qualification": False,
    }


def build_phase_review_boundary(*, phase: str, review_scope: Sequence[str], required_dimensions: Sequence[str],
                                explicit_nonclaims: Sequence[str], out_of_scope_dimensions: Sequence[str],
                                allowed_evidence: Sequence[str], api_boundary_under_test: bool = False,
                                user_approved_api: bool = False) -> dict[str, Any]:
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
    return {
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
        ),
        "reviewer_instruction": REVIEW_INSTRUCTION[p],
        "promotion_target": PHASE_PROMOTION_TARGET[p],
        "reviewer_consensus_is_authority": False,
        "raw_finding_becomes_governance_rule_automatically": False,
        "material_finding_requires_adjudication": True,
    }


def classify_finding_for_phase(*, phase: str, finding_phase: str, violates_current_contract: bool) -> str:
    current = validate_phase(phase)
    target = validate_phase(finding_phase)
    if violates_current_contract:
        return "BLOCK_CURRENT_PHASE_PENDING_ADJUDICATION"
    if PHASE_ORDER[target] <= PHASE_ORDER[current]:
        return "CURRENT_PHASE_EVIDENCE_PENDING_ADJUDICATION"
    return "DEFERRED_TO_RELEASE" if target == "RELEASE" else "DEFERRED_TO_PRODUCTION"


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
            "no_unresolved_material_defect_in_any_governed_failure_class",
            "deterministic_testing_review_requirement_recorded",
            "review_performed_if_required_or_review_not_performed_explicitly_recorded_if_optional",
            "performed_review_not_gate_satisfying_until_adjudication_complete",
            "review_findings_adjudicated",
            "accepted_material_findings_reproduced_or_supported_by_explicit_alternative_deterministic_evidence",
            "exact_candidate_sha_requalified_after_last_repair",
            "integrated_release_scope_regressions_pass_before_phase_promotion",
            "bounded_and_deferred_dimensions_explicitly_recorded",
            "explicit_untested_and_deferred_risks_recorded",
        ],
        "means": "READY_TO_BEGIN_RELEASE_QUALIFICATION",
        "does_not_mean": "PRODUCTION_READY",
    }
