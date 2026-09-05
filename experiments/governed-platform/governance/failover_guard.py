"""Fail-closed provider/model/SKU failover authorization for EXP-F."""
from __future__ import annotations


def authorize_failover(original_route: dict, candidate: dict, current_qualification: dict) -> dict:
    required = ("provider", "model", "sku", "role", "qualification_id", "qualification_epoch")
    for name, payload in (("original_route", original_route), ("candidate", candidate), ("current_qualification", current_qualification)):
        if not isinstance(payload, dict):
            return {"authorized": False, "reason": f"{name}-malformed"}

    missing = [key for key in required if key not in candidate]
    if missing:
        return {"authorized": False, "reason": "candidate-missing-binding", "missing": missing}

    if current_qualification.get("status") != "QUALIFIED":
        return {"authorized": False, "reason": "candidate-not-currently-qualified"}

    for key in ("provider", "model", "sku", "role", "qualification_id", "qualification_epoch"):
        if candidate.get(key) != current_qualification.get(key):
            return {"authorized": False, "reason": f"qualification-{key}-mismatch"}

    if candidate.get("role") != original_route.get("role"):
        return {"authorized": False, "reason": "role-substitution-denied"}

    if candidate.get("task_class") != original_route.get("task_class"):
        return {"authorized": False, "reason": "task-class-substitution-denied"}

    if candidate.get("privacy_class") != original_route.get("privacy_class"):
        return {"authorized": False, "reason": "privacy-class-substitution-denied"}

    if candidate.get("policy_hash") != original_route.get("policy_hash"):
        return {"authorized": False, "reason": "policy-binding-substitution-denied"}

    return {
        "authorized": True,
        "reason": "qualified-failover-authorized",
        "selected": {
            "provider": candidate["provider"],
            "model": candidate["model"],
            "sku": candidate["sku"],
            "qualification_id": candidate["qualification_id"],
            "qualification_epoch": candidate["qualification_epoch"],
        },
    }
