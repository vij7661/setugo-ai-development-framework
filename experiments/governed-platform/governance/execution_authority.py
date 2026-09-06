"""Use-time execution authority composed from external capability and bound model evidence.

This is a governance-layer integration point for future experiments. It is intentionally
not wired into the frozen EXP-N Pilot 8 runner path.

The model can diagnose or propose, but the platform alone decides whether a concrete
action request may execute. A clean authority binding is necessary but never sufficient:
the current capability is revalidated at the instant of use.
"""
from __future__ import annotations

from typing import Any, Mapping

from capability_guard import authorize_capability_use


def authorize_bound_execution(
    bound_result: Mapping[str, Any],
    capability: Mapping[str, Any],
    request: Mapping[str, Any],
    now: str,
) -> dict[str, Any]:
    binding = bound_result.get("authority_binding")
    if not isinstance(binding, Mapping):
        return {"authorized": False, "reason": "external authority binding missing"}
    if binding.get("authority_source") != "PLATFORM_CAPABILITY":
        return {"authorized": False, "reason": "authority source is not platform capability"}
    if binding.get("model_authority_effect") is not False:
        return {"authorized": False, "reason": "model authority effect must be false"}
    if binding.get("requires_use_time_capability_revalidation") is not True:
        return {"authorized": False, "reason": "use-time revalidation requirement missing"}
    if binding.get("consequential_execution_authorized") is not False:
        return {"authorized": False, "reason": "binding stage must not pre-authorize execution"}

    violations = binding.get("governance_violations")
    if not isinstance(violations, list):
        return {"authorized": False, "reason": "governance violation ledger malformed"}
    if violations:
        return {
            "authorized": False,
            "reason": "model result has unresolved governance violation",
            "governance_violations": list(violations),
        }

    if binding.get("capability_id") != capability.get("capability_id"):
        return {"authorized": False, "reason": "bound capability changed before use"}
    if binding.get("issued_epoch") != capability.get("issued_epoch"):
        return {"authorized": False, "reason": "bound capability epoch changed before use"}

    effective_actions = binding.get("effective_actions")
    effective_artifacts = binding.get("effective_artifact_classes")
    if not isinstance(effective_actions, list) or not isinstance(effective_artifacts, list):
        return {"authorized": False, "reason": "effective authority scope malformed"}
    if request.get("action") not in effective_actions:
        return {"authorized": False, "reason": "requested action exceeds bound effective authority"}
    requested_artifacts = request.get("artifact_classes", [])
    if not isinstance(requested_artifacts, list):
        return {"authorized": False, "reason": "requested artifact scope malformed"}
    if not set(requested_artifacts).issubset(set(effective_artifacts)):
        return {"authorized": False, "reason": "requested artifacts exceed bound effective authority"}

    current = authorize_capability_use(dict(capability), dict(request), now)
    if not current.get("authorized", False):
        return current

    return {
        "authorized": True,
        "reason": "platform capability revalidated at use time",
        "capability_id": current.get("capability_id"),
        "issued_epoch": current.get("issued_epoch"),
        "authority_source": "PLATFORM_CAPABILITY",
    }
