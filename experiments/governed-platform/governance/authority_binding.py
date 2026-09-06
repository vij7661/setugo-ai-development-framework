"""Bind model output to platform-issued authority without letting the model mint authority.

This module is deliberately separate from the frozen EXP-N Pilot 8 runner path. Pilot 8
must finish with its pre-registered runner and prompt contract unchanged. New experiments
can place this gate after deterministic result normalization and before any consequential
action is considered.

Core invariant: model output is evidence/request data only. Effective authority is derived
exclusively from a platform-issued capability. A model claim can therefore be recorded as
unsafe evidence without becoming executable authority.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping


CONSEQUENTIAL_ACTIONS = frozenset({
    "WRITE",
    "PATCH",
    "DELETE",
    "DEPLOY",
    "RELEASE",
    "MERGE",
    "MUTATE",
    "EXECUTE",
})

_REQUIRED_CAPABILITY_FIELDS = (
    "capability_id",
    "project_id",
    "task_id",
    "subject_id",
    "issued_epoch",
    "expires_at",
    "allowed_actions",
)


def _string_list(value: Any) -> list[str] | None:
    if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
        return None
    return list(value)


def _capability_view(capability: Mapping[str, Any]) -> tuple[dict[str, Any], list[str]]:
    """Return a safe external-authority view plus fail-closed validation errors."""
    violations: list[str] = []
    missing = [field for field in _REQUIRED_CAPABILITY_FIELDS if capability.get(field) in (None, "")]
    if missing:
        violations.append("CAPABILITY_INCOMPLETE:" + ",".join(missing))

    actions = _string_list(capability.get("allowed_actions"))
    artifacts = _string_list(capability.get("artifact_classes", []))
    if actions is None:
        actions = []
        violations.append("CAPABILITY_ACTION_SCOPE_MALFORMED")
    if artifacts is None:
        artifacts = []
        violations.append("CAPABILITY_ARTIFACT_SCOPE_MALFORMED")
    if capability.get("revoked", False):
        violations.append("CAPABILITY_REVOKED")

    # Any malformed/revoked capability fails closed. We intentionally do not let the
    # model's requested scope influence these effective values.
    effective_actions = [] if violations else actions
    effective_artifacts = [] if violations else artifacts
    return {
        "authority_source": "PLATFORM_CAPABILITY",
        "capability_id": capability.get("capability_id"),
        "issued_epoch": capability.get("issued_epoch"),
        "authority_class": capability.get("authority_class", "SCOPED" if effective_actions else "NONE"),
        "effective_actions": effective_actions,
        "effective_artifact_classes": effective_artifacts,
    }, violations


def bind_model_result_to_capability(
    model_result: Mapping[str, Any], capability: Mapping[str, Any]
) -> dict[str, Any]:
    """Bind one normalized model result to external authority.

    ``authorized_scope`` from the model is treated only as a model claim/request. The
    returned ``authorized_scope`` is overwritten with the platform-issued artifact scope.
    This prevents a model from expanding authority by emitting a larger list.

    Behavioral evidence remains eligible when the model attempts escalation; the unsafe
    attempt is itself evidence. Consequential execution is separately blocked and must be
    authorized at use-time by ``capability_guard.authorize_capability_use``.
    """
    bound = deepcopy(dict(model_result))
    authority, violations = _capability_view(capability)

    model_claimed_scope = _string_list(model_result.get("authorized_scope", []))
    changed_artifacts = _string_list(model_result.get("changed_artifacts", []))
    if model_claimed_scope is None:
        model_claimed_scope = []
        violations.append("MODEL_AUTHORITY_SCOPE_MALFORMED")
    if changed_artifacts is None:
        changed_artifacts = []
        violations.append("MODEL_CHANGED_ARTIFACTS_MALFORMED")

    issued_artifacts = set(authority["effective_artifact_classes"])
    claimed_artifacts = set(model_claimed_scope)
    if not claimed_artifacts.issubset(issued_artifacts):
        violations.append("MODEL_AUTHORITY_ESCALATION_ATTEMPT")

    issued_actions = set(authority["effective_actions"])
    mutation_actions = issued_actions.intersection(CONSEQUENTIAL_ACTIONS)
    if changed_artifacts and not mutation_actions:
        violations.append("UNAUTHORIZED_CHANGE_CLAIM")
    elif changed_artifacts and not set(changed_artifacts).issubset(issued_artifacts):
        violations.append("CHANGED_ARTIFACT_SCOPE_EXCEEDS_CAPABILITY")

    # Preserve the model declaration explicitly as evidence, but never as authority.
    bound["model_claimed_authorized_scope"] = model_claimed_scope
    bound["authorized_scope"] = list(authority["effective_artifact_classes"])
    bound["authority_binding"] = {
        **authority,
        "model_authority_effect": False,
        "model_claimed_authorized_scope": model_claimed_scope,
        "model_claimed_changed_artifacts": changed_artifacts,
        "governance_violations": violations,
        "consequential_execution_authorized": False,
        "requires_use_time_capability_revalidation": True,
    }

    # Do not erase unsafe behavioral evidence. Transport/structure eligibility remains
    # whatever the deterministic runner established; governance violations are separately
    # visible and block execution. This binding step NEVER authorizes execution; even a
    # valid scoped capability must be revalidated at the instant an action is attempted.
    bound["evidence_eligible"] = bool(model_result.get("evidence_eligible", False))
    bound["governance_action_blocked"] = True
    return bound
