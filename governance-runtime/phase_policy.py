#!/usr/bin/env python3
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

PHASES = ("TESTING", "RELEASE", "PRODUCTION")
PHASE_BRANCH = {
    "TESTING": "phase/testing",
    "RELEASE": "phase/release",
    "PRODUCTION": "phase/production",
}
PHASE_ORDER = {name: i for i, name in enumerate(PHASES)}

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


def validate_phase(phase: str) -> str:
    p = str(phase).upper()
    if p not in PHASES:
        raise PhasePolicyError(f"unsupported phase: {phase}")
    return p


def phase_branch(phase: str) -> str:
    return PHASE_BRANCH[validate_phase(phase)]


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
        raise PhasePolicyError("phase promotion must advance exactly one phase")
    if source_branch != PHASE_BRANCH[src] or destination_branch != PHASE_BRANCH[dst]:
        raise PhasePolicyError("promotion branch does not match governed phase")
    if source_sha != qualified_sha:
        raise PhasePolicyError("promotion must use the exact qualified source SHA")
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
            "review_performed_when_requested_or_required_by_testing_policy",
            "review_findings_adjudicated",
            "material_valid_findings_falsified_where_practical",
            "exact_candidate_sha_requalified_after_last_repair",
            "integrated_release_scope_regressions_pass_before phase promotion",
            "explicit_untested_and_deferred_risks_recorded",
        ],
        "means": "READY_TO_BEGIN_RELEASE_QUALIFICATION",
        "does_not_mean": "PRODUCTION_READY",
    }
