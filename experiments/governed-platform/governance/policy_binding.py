"""Policy binding guard for preventing TOCTOU authority drift."""
from __future__ import annotations


def authorize_policy_bound_execution(authority: dict, current: dict, request: dict) -> dict:
    required = ["policy_epoch", "policy_hash", "artifact_hash", "capability_id"]
    for key in required:
        if not authority.get(key):
            return {"authorized": False, "reason": f"authority missing {key}"}
    if authority.get("revoked"):
        return {"authorized": False, "reason": "authority revoked"}
    if authority["policy_epoch"] != current.get("policy_epoch"):
        return {"authorized": False, "reason": "policy epoch changed"}
    if authority["policy_hash"] != current.get("policy_hash"):
        return {"authorized": False, "reason": "policy hash changed"}
    if authority["artifact_hash"] != request.get("artifact_hash"):
        return {"authorized": False, "reason": "artifact changed after authorization"}
    if authority["capability_id"] != request.get("capability_id"):
        return {"authorized": False, "reason": "capability substitution"}
    if request.get("policy_epoch") != current.get("policy_epoch"):
        return {"authorized": False, "reason": "request bound to stale policy epoch"}
    if request.get("policy_hash") != current.get("policy_hash"):
        return {"authorized": False, "reason": "request bound to stale policy hash"}
    return {"authorized": True, "reason": "authority, policy, artifact and capability remain exactly bound"}


def evidence_policy_admissible(evidence: dict, current: dict) -> bool:
    return bool(
        evidence.get("valid", True)
        and evidence.get("policy_epoch") == current.get("policy_epoch")
        and evidence.get("policy_hash") == current.get("policy_hash")
        and evidence.get("artifact_hash") == current.get("artifact_hash")
    )
