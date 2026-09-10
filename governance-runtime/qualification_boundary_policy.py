#!/usr/bin/env python3
"""Platform-owned qualification-boundary policy.

This module owns qualification floors that an evaluated actor must not be able to
weaken: review triggers, mandatory review dimensions, TESTING adversarial cases,
acceptance-boundary freezing, root-cause/adjudication authority, phase deferral,
and terminal-authority issuer/action scope.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from typing import Any, Mapping, Sequence

POLICY_ID = "QUALIFICATION_BOUNDARY_OWNERSHIP"
POLICY_VERSION = 2

REVIEW_REQUIRED_TRIGGERS = frozenset({
    "EXPERIMENT_ADJUDICATION",
    "MATERIAL_FAILURE_CLASSIFICATION",
    "FROZEN_ARTIFACT_CHANGE_AFTER_EXPOSURE",
    "MATERIAL_GOVERNANCE_CHANGE",
    "MATERIAL_EXTERNAL_EVIDENCE_PROMOTION",
    "AUTHORITATIVE_RETRACTION_OR_SUPERSESSION",
    "GOVERNED_REQUIREMENT_ACCEPTANCE",
    "TERMINAL_ACTION",
    "MATERIAL_DISAGREEMENT_RESOLUTION",
    "MATERIAL_AUTHORITY_TRANSITION",
})

GOVERNANCE_RELEVANT_PATH_PREFIXES = (
    "governance-runtime/",
    "standards/",
    "experiments/governed-platform/",
    ".github/workflows/",
)

REVIEW_PROFILES: dict[str, tuple[dict[str, Any], ...]] = {
    "GOVERNANCE_MATERIAL": (
        {
            "id": "authority_path",
            "mandatory": True,
            "description": "Authority, self-grant, waiver and promotion-bypass resistance.",
        },
        {
            "id": "evidence_integrity",
            "mandatory": True,
            "description": "Evidence provenance, exact-revision binding and replay resistance.",
        },
        {
            "id": "qualification_boundary_ownership",
            "mandatory": True,
            "description": "The evaluated actor cannot define or lower its own qualification boundary.",
        },
        {
            "id": "phase_separation",
            "mandatory": True,
            "description": "TESTING cannot acquire RELEASE or PRODUCTION authority.",
        },
    ),
}

TESTING_ADVERSARIAL_MATRIX: tuple[dict[str, str], ...] = (
    {"id": "QO-01", "description": "Candidate declarations cannot lower a platform review requirement."},
    {"id": "QO-02", "description": "Mandatory review dimensions cannot be deleted, downgraded or rebound by the candidate."},
    {"id": "QO-03", "description": "Required TESTING adversarial cases cannot be omitted or replaced by a weaker matrix."},
    {"id": "QO-04", "description": "A candidate/model/reviewer cannot self-appoint terminal authority."},
    {"id": "QO-05", "description": "The evaluated actor cannot choose whether its acceptance boundary must be preregistered or change it after exposure."},
    {"id": "QO-06", "description": "The evaluated actor cannot terminally classify its own material failure into a less consequential root-cause class."},
    {"id": "QO-07", "description": "The evaluated actor or reviewer cannot terminally adjudicate reviewer evidence about that actor."},
    {"id": "QO-08", "description": "The evaluated actor cannot defer a TESTING-contract defect into RELEASE or PRODUCTION."},
)

PREREGISTRATION_REQUIRED_ARTIFACT_TYPES = frozenset({
    "FALSIFICATION_CONTRACT",
    "ACCEPTANCE_MATRIX",
    "QUALIFICATION_POLICY",
    "GOVERNANCE_STANDARD",
    "PROMOTION_CONTRACT",
})

ROOT_CAUSE_CLASSES = frozenset({
    "CODE_DEFECT",
    "FIXTURE_DATA_DEFECT",
    "TEST_DEFECT",
    "ENVIRONMENT_TOOLING_DEFECT",
    "GOVERNANCE_PROCESS_DEFECT",
    "REQUIREMENT_UNRESOLVED",
    "REVIEWER_EVIDENCE_ERROR",
})

ROOT_CAUSE_AUTHORITY = {
    "material": "INDEPENDENT_GOVERNANCE_ADJUDICATOR",
    "non_material": "PLATFORM_DETERMINISTIC_CLASSIFIER",
}

REVIEW_ADJUDICATION_AUTHORITY = "INDEPENDENT_GOVERNANCE_ADJUDICATOR"

PHASE_CONTRACT_OWNERS = {
    "TESTING": "PLATFORM_TESTING_CONTRACT",
    "RELEASE": "PLATFORM_RELEASE_CONTRACT",
    "PRODUCTION": "PLATFORM_PRODUCTION_CONTRACT",
}

TERMINAL_AUTHORITY_POLICY: dict[str, Any] = {
    "TESTING": {
        "permitted_issuer_classes": ("HUMAN_GOVERNANCE_OWNER",),
        "permitted_actions": ("READY_TO_BEGIN_RELEASE_QUALIFICATION",),
    },
    "RELEASE": {
        "permitted_issuer_classes": ("HUMAN_RELEASE_AUTHORITY",),
        "permitted_actions": ("MERGE_RELEASE_CANDIDATE", "BEGIN_PRODUCTION_QUALIFICATION"),
    },
    "PRODUCTION": {
        "permitted_issuer_classes": ("HUMAN_PRODUCTION_AUTHORITY",),
        "permitted_actions": ("DEPLOY_PRODUCTION",),
    },
}


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _policy_material() -> dict[str, Any]:
    return {
        "policy_id": POLICY_ID,
        "policy_version": POLICY_VERSION,
        "review_required_triggers": sorted(REVIEW_REQUIRED_TRIGGERS),
        "governance_relevant_path_prefixes": list(GOVERNANCE_RELEVANT_PATH_PREFIXES),
        "review_profiles": REVIEW_PROFILES,
        "testing_adversarial_matrix": TESTING_ADVERSARIAL_MATRIX,
        "preregistration_required_artifact_types": sorted(PREREGISTRATION_REQUIRED_ARTIFACT_TYPES),
        "root_cause_classes": sorted(ROOT_CAUSE_CLASSES),
        "root_cause_authority": ROOT_CAUSE_AUTHORITY,
        "review_adjudication_authority": REVIEW_ADJUDICATION_AUTHORITY,
        "phase_contract_owners": PHASE_CONTRACT_OWNERS,
        "terminal_authority_policy": TERMINAL_AUTHORITY_POLICY,
    }


def qualification_policy_hash() -> str:
    return hashlib.sha256(_canonical(_policy_material()).encode("utf-8")).hexdigest()


def policy_binding() -> dict[str, Any]:
    return {
        "qualification_policy_id": POLICY_ID,
        "qualification_policy_version": POLICY_VERSION,
        "qualification_policy_hash": qualification_policy_hash(),
    }


def review_required(*, trigger: str, material_authority_transition: bool = False,
                    standard_requires_review: bool = False,
                    changed_paths: Sequence[str] | None = None,
                    unresolved_materiality: bool = False) -> bool:
    protected = any(
        isinstance(path, str) and path.startswith(GOVERNANCE_RELEVANT_PATH_PREFIXES)
        for path in tuple(changed_paths or ())
    )
    return (
        trigger in REVIEW_REQUIRED_TRIGGERS
        or bool(material_authority_transition)
        or bool(standard_requires_review)
        or bool(protected)
        or bool(unresolved_materiality)
    )


def resolve_review_profile(*, trigger: str, artifact_type: str) -> str:
    if not isinstance(trigger, str) or not trigger:
        raise ValueError("review trigger is required for platform profile resolution")
    if not isinstance(artifact_type, str) or not artifact_type:
        raise ValueError("artifact type is required for platform profile resolution")
    return "GOVERNANCE_MATERIAL"


def review_dimensions(profile_id: str) -> list[dict[str, Any]]:
    try:
        return [deepcopy(item) for item in REVIEW_PROFILES[profile_id]]
    except KeyError as exc:
        raise ValueError(f"unknown platform review profile: {profile_id}") from exc


def merge_review_dimensions(profile_id: str, requested: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    platform = review_dimensions(profile_id)
    platform_ids = {item["id"] for item in platform}
    extras: list[dict[str, Any]] = []
    seen = set(platform_ids)
    for item in requested:
        if not isinstance(item, Mapping):
            raise ValueError("review dimension must be a mapping")
        did = item.get("id")
        mandatory = item.get("mandatory")
        description = item.get("description")
        if not isinstance(did, str) or not did:
            raise ValueError("review dimension id is required")
        if did in platform_ids:
            continue
        if did in seen:
            raise ValueError(f"duplicate review dimension id: {did}")
        if not isinstance(mandatory, bool):
            raise ValueError(f"review dimension mandatory flag is required: {did}")
        if not isinstance(description, str) or not description:
            raise ValueError(f"review dimension description is required: {did}")
        seen.add(did)
        extras.append({"id": did, "mandatory": mandatory, "description": description})
    return platform + extras


def verify_review_dimensions(profile_id: str, supplied: Sequence[Mapping[str, Any]]) -> tuple[bool, str]:
    required = {item["id"]: item for item in review_dimensions(profile_id)}
    seen: dict[str, Mapping[str, Any]] = {}
    for item in supplied:
        if not isinstance(item, Mapping) or not isinstance(item.get("id"), str):
            return False, "review dimension is malformed"
        if item["id"] in seen:
            return False, f"duplicate review dimension: {item['id']}"
        seen[item["id"]] = item
    for dimension_id, expected in required.items():
        actual = seen.get(dimension_id)
        if actual is None:
            return False, f"missing platform-mandatory review dimension: {dimension_id}"
        if dict(actual) != dict(expected):
            return False, f"platform review dimension was rebound or weakened: {dimension_id}"
    return True, "review dimensions preserve platform policy floor"


def testing_matrix_binding() -> dict[str, Any]:
    matrix = [deepcopy(item) for item in TESTING_ADVERSARIAL_MATRIX]
    matrix_hash = hashlib.sha256(_canonical(matrix).encode("utf-8")).hexdigest()
    return {
        "matrix_id": "TESTING_STANDARD_ADVERSARIAL_MATRIX",
        "matrix_version": 2,
        "matrix_hash": matrix_hash,
        "required_case_ids": [item["id"] for item in matrix],
    }


def verify_testing_matrix_results(binding: Mapping[str, Any], case_results: Mapping[str, str]) -> tuple[bool, str]:
    expected = testing_matrix_binding()
    if dict(binding) != expected:
        return False, "testing adversarial matrix binding is missing, stale, or rebound"
    allowed_pass = {"PASS", "TESTED_SUPPORTED"}
    for case_id in expected["required_case_ids"]:
        if case_results.get(case_id) not in allowed_pass:
            return False, f"required testing adversarial case is not supported: {case_id}"
    return True, "all platform-owned testing adversarial cases are supported"


def preregistration_required(*, artifact_type: str, candidate_override: bool | None = None) -> bool:
    """Platform decides preregistration; caller override cannot lower the floor."""
    platform_floor = artifact_type in PREREGISTRATION_REQUIRED_ARTIFACT_TYPES
    return platform_floor or candidate_override is True


def acceptance_boundary_record(*, artifact_type: str, artifact_sha: str,
                               boundary_hash: str, approved_by: str,
                               exposed: bool = False) -> dict[str, Any]:
    if not preregistration_required(artifact_type=artifact_type):
        raise ValueError("artifact type does not require platform preregistration")
    if approved_by != "HUMAN_GOVERNANCE_OWNER":
        raise ValueError("acceptance boundary requires human governance-owner approval")
    if not all(isinstance(v, str) and v for v in (artifact_sha, boundary_hash)):
        raise ValueError("artifact_sha and boundary_hash are required")
    return {
        "artifact_type": artifact_type,
        "artifact_sha": artifact_sha,
        "boundary_hash": boundary_hash,
        "approved_by": approved_by,
        "exposed": bool(exposed),
        **policy_binding(),
    }


def acceptance_boundary_change_allowed(*, original: Mapping[str, Any], proposed: Mapping[str, Any]) -> tuple[bool, str]:
    if original.get("exposed") is True:
        immutable = ("artifact_type", "artifact_sha", "boundary_hash", "approved_by",
                     "qualification_policy_id", "qualification_policy_version", "qualification_policy_hash")
        if any(original.get(field) != proposed.get(field) for field in immutable):
            return False, "exposed acceptance boundary is immutable; create a new preregistration lineage"
    return True, "acceptance boundary change is allowed"


def root_cause_classification_allowed(*, classification: str, material: bool,
                                      classifier_role: str,
                                      independent_evidence_bound: bool) -> tuple[bool, str]:
    if classification not in ROOT_CAUSE_CLASSES:
        return False, "unknown root-cause class"
    expected = ROOT_CAUSE_AUTHORITY["material" if material else "non_material"]
    if classifier_role != expected:
        return False, "classifier role is not authorized for this failure materiality"
    if material and not independent_evidence_bound:
        return False, "material root-cause classification lacks bound independent evidence"
    return True, "root-cause classification authority is valid"


def reviewer_finding_adjudication_allowed(*, adjudicator_role: str,
                                           candidate_role: str,
                                           reviewer_role: str,
                                           exact_sha_bound: bool,
                                           raw_finding_preserved: bool) -> tuple[bool, str]:
    if adjudicator_role != REVIEW_ADJUDICATION_AUTHORITY:
        return False, "review finding requires independent governance adjudicator"
    if adjudicator_role in {candidate_role, reviewer_role}:
        return False, "candidate or reviewer cannot terminally adjudicate its own review evidence"
    if not exact_sha_bound:
        return False, "adjudication is not bound to exact candidate SHA"
    if not raw_finding_preserved:
        return False, "raw reviewer finding must be preserved before adjudication"
    return True, "review finding adjudication authority is valid"


def phase_disposition(*, current_phase: str, violated_contract_phase: str | None,
                      material: bool, uncertainty: bool = False) -> tuple[str, str]:
    """Derive blocker/defer status from platform phase contracts, never candidate choice."""
    if current_phase not in PHASE_CONTRACT_OWNERS:
        return "BLOCKED", "current phase is unknown"
    if uncertainty or violated_contract_phase is None:
        return "REQUIREMENT_UNRESOLVED", "phase applicability is uncertain"
    if violated_contract_phase == current_phase and material:
        return "BLOCK_TESTING" if current_phase == "TESTING" else f"BLOCK_{current_phase}", "material defect violates current phase contract"
    order = {"TESTING": 0, "RELEASE": 1, "PRODUCTION": 2}
    if violated_contract_phase not in order:
        return "REQUIREMENT_UNRESOLVED", "violated contract phase is unknown"
    if order[violated_contract_phase] > order[current_phase]:
        return f"DEFERRED_TO_{violated_contract_phase}", "defect belongs to a later frozen phase contract"
    return f"BLOCK_{current_phase}", "defect belongs to current or earlier contract"


def terminal_authority_allowed(*, phase: str, action: str,
                               issuer_class: str | None,
                               provenance_verified: bool,
                               current: bool) -> tuple[bool, str]:
    phase_policy = TERMINAL_AUTHORITY_POLICY.get(phase)
    if not isinstance(phase_policy, Mapping):
        return False, "unknown phase has no terminal-authority policy"
    if not provenance_verified:
        return False, "terminal-authority issuer provenance is unverified"
    if not current:
        return False, "terminal authorization is stale or not valid at use time"
    if issuer_class not in phase_policy["permitted_issuer_classes"]:
        return False, "issuer class is not authorized for this phase"
    if action not in phase_policy["permitted_actions"]:
        return False, "terminal action is outside the authority scope for this phase"
    return True, "terminal authority is permitted by platform-owned policy"
