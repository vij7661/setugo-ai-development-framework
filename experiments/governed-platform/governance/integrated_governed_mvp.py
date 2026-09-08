"""Minimum integrated governed execution decision slice.

This module composes existing deterministic qualification, authority-binding, and
use-time capability guards. It deliberately performs no real side effect.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from authority_binding import bind_model_result_to_capability
from capability_guard import authorize_capability_use
from qualification_guard import authorize_qualified_execution


TERMINAL_ACTIONS = frozenset({"RELEASE", "DEPLOY", "MERGE"})
REVIEW_STATES = frozenset({"CLEAR", "REVIEW_REQUIRED", "HUMAN_REQUIRED"})


def _decision(
    state: str,
    reason: str,
    *,
    qualification: Mapping[str, Any] | None = None,
    authority_binding: Mapping[str, Any] | None = None,
    capability: Mapping[str, Any] | None = None,
    review_gate: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a normalized deterministic decision/evidence record."""
    return {
        "decision": state,
        "reason": reason,
        "consequential_execution_authorized": state == "AUTHORIZED_FOR_ISOLATED_EXECUTION",
        "release_completion_authority": False,
        "qualification": deepcopy(dict(qualification or {})),
        "authority_binding": deepcopy(dict(authority_binding or {})),
        "capability_use": deepcopy(dict(capability or {})),
        "review_gate": deepcopy(dict(review_gate or {})),
    }


def evaluate_governed_execution(
    *,
    route: Mapping[str, Any],
    registry_entry: Mapping[str, Any],
    normalized_model_result: Mapping[str, Any],
    capability: Mapping[str, Any],
    execution_request: Mapping[str, Any],
    review_gate: Mapping[str, Any],
    now_epoch: int,
    now_iso: str,
) -> dict[str, Any]:
    """Evaluate one exact consequential action without performing the action.

    Authority is never derived from the model result. A positive return means only
    that an isolated execution gateway may be invoked for this exact request.
    """
    qualification = authorize_qualified_execution(dict(route), dict(registry_entry), now_epoch=now_epoch)
    if not qualification.get("authorized", False):
        return _decision("DENY_QUALIFICATION", qualification.get("reason", "qualification denied"), qualification=qualification)

    bound = bind_model_result_to_capability(dict(normalized_model_result), dict(capability))
    binding = bound.get("authority_binding", {})
    violations = list(binding.get("governance_violations", []))
    if violations:
        return _decision(
            "DENY_AUTHORITY_BINDING",
            "model result or capability binding contains governance violations",
            qualification=qualification,
            authority_binding=binding,
        )

    capability_use = authorize_capability_use(dict(capability), dict(execution_request), now_iso)
    if not capability_use.get("authorized", False):
        return _decision(
            "DENY_CAPABILITY",
            capability_use.get("reason", "capability use denied"),
            qualification=qualification,
            authority_binding=binding,
            capability=capability_use,
        )

    gate_state = review_gate.get("state")
    evidence_refs = review_gate.get("evidence_refs")
    if gate_state not in REVIEW_STATES or not isinstance(evidence_refs, list) or not all(
        isinstance(ref, str) and ref for ref in evidence_refs
    ):
        return _decision(
            "HUMAN_REQUIRED",
            "review gate is malformed or unrecognized",
            qualification=qualification,
            authority_binding=binding,
            capability=capability_use,
            review_gate=review_gate,
        )
    if gate_state == "HUMAN_REQUIRED":
        return _decision(
            "HUMAN_REQUIRED",
            "platform review policy requires human adjudication",
            qualification=qualification,
            authority_binding=binding,
            capability=capability_use,
            review_gate=review_gate,
        )
    if gate_state == "REVIEW_REQUIRED":
        return _decision(
            "REVIEW_REQUIRED",
            "platform review policy requires independent review before execution",
            qualification=qualification,
            authority_binding=binding,
            capability=capability_use,
            review_gate=review_gate,
        )

    action = execution_request.get("action")
    if action in TERMINAL_ACTIONS:
        return _decision(
            "TERMINAL_AUTHORITY_REQUIRED",
            "release/deploy/merge requires a separate external terminal authority gate",
            qualification=qualification,
            authority_binding=binding,
            capability=capability_use,
            review_gate=review_gate,
        )

    return _decision(
        "AUTHORIZED_FOR_ISOLATED_EXECUTION",
        "exact qualification, external capability, use-time scope, and review gate are current and clear",
        qualification=qualification,
        authority_binding=binding,
        capability=capability_use,
        review_gate=review_gate,
    )
