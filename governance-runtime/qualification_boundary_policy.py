#!/usr/bin/env python3
"""Platform-owned qualification-boundary policy.

This module owns qualification floors that an evaluated actor must not be able to
weaken: review triggers, mandatory review dimensions, TESTING adversarial cases,
and terminal-authority issuer/action scope.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from typing import Any, Mapping, Sequence

POLICY_ID = "QUALIFICATION_BOUNDARY_OWNERSHIP"
POLICY_VERSION = 1

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
)

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
    """Return the platform-owned review floor.

    Inputs may report facts, but no input provides a waiver. Unknown materiality
    at a consequential boundary escalates to review rather than lowering it.
    """
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


def review_dimensions(profile_id: str) -> list[dict[str, Any]]:
    try:
        return [deepcopy(item) for item in REVIEW_PROFILES[profile_id]]
    except KeyError as exc:
        raise ValueError(f"unknown platform review profile: {profile_id}") from exc


def merge_review_dimensions(profile_id: str, requested: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Resolve a request to the immutable platform floor plus caller-added scope.

    When a caller reuses a platform-owned dimension id, the platform definition
    wins. Extra dimensions may only increase review scope; they cannot replace,
    delete, downgrade, or narrow the platform floor.
    """
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
    """Verify supplied request dimensions preserve the complete platform floor.

    Extra dimensions are allowed. Platform dimensions must be present exactly;
    in particular a caller cannot downgrade `mandatory` or narrow description.
    """
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
        "matrix_version": 1,
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
