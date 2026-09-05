"""Scoped capability guard for governed execution.

Authority is issued by the platform and remains revocable. A model cannot infer,
extend, refresh, or widen its own capability.
"""
from __future__ import annotations

from datetime import datetime, timezone


def _parse(ts: str) -> datetime:
    if not isinstance(ts, str) or not ts:
        raise ValueError("timestamp required")
    value = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def authorize_capability_use(capability: dict, request: dict, now: str) -> dict:
    """Revalidate capability at the instant of use; fail closed on any drift."""
    required = ["capability_id", "project_id", "task_id", "subject_id", "issued_epoch", "expires_at", "allowed_actions"]
    if any(capability.get(k) in (None, "") for k in required):
        return {"authorized": False, "reason": "capability is incomplete"}
    if capability.get("revoked", False):
        return {"authorized": False, "reason": "capability revoked"}
    try:
        if _parse(now) >= _parse(capability["expires_at"]):
            return {"authorized": False, "reason": "capability expired"}
    except (TypeError, ValueError):
        return {"authorized": False, "reason": "capability time binding malformed"}

    bindings = ["capability_id", "project_id", "task_id", "subject_id", "issued_epoch"]
    for key in bindings:
        if request.get(key) != capability.get(key):
            return {"authorized": False, "reason": f"capability binding mismatch: {key}"}

    action = request.get("action")
    allowed = capability.get("allowed_actions")
    if not isinstance(allowed, list) or not all(isinstance(x, str) and x for x in allowed):
        return {"authorized": False, "reason": "allowed action scope malformed"}
    if action not in allowed:
        return {"authorized": False, "reason": "requested action exceeds capability scope"}

    requested_artifacts = request.get("artifact_classes", [])
    permitted_artifacts = capability.get("artifact_classes", [])
    if not isinstance(requested_artifacts, list) or not isinstance(permitted_artifacts, list):
        return {"authorized": False, "reason": "artifact scope malformed"}
    if not set(requested_artifacts).issubset(set(permitted_artifacts)):
        return {"authorized": False, "reason": "requested artifact scope exceeds capability"}

    return {
        "authorized": True,
        "reason": "current scoped capability permits requested action",
        "capability_id": capability["capability_id"],
        "issued_epoch": capability["issued_epoch"],
    }


def evidence_from_capability_is_admissible(evidence: dict, current_capability: dict) -> bool:
    """Evidence is inadmissible after capability revocation/replacement or scope drift."""
    if current_capability.get("revoked", False):
        return False
    keys = ["capability_id", "project_id", "task_id", "subject_id", "issued_epoch"]
    return all(evidence.get(k) == current_capability.get(k) for k in keys)
