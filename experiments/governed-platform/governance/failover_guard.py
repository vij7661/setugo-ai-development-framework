"""Fail-closed provider/model/SKU/deployment-path failover authorization for EXP-F."""
from __future__ import annotations


def authorize_failover(original_route: dict, candidate: dict, current_qualification: dict) -> dict:
    identity_fields = (
        "provider",
        "model",
        "sku",
        "deployment_path",
        "role",
        "task_class",
        "privacy_class",
        "policy_hash",
        "qualification_id",
        "qualification_epoch",
    )
    route_scope_fields = ("role", "task_class", "privacy_class", "policy_hash")
    for name, payload in (("original_route", original_route), ("candidate", candidate), ("current_qualification", current_qualification)):
        if not isinstance(payload, dict):
            return {"authorized": False, "reason": f"{name}-malformed"}

    candidate_missing = [key for key in identity_fields if candidate.get(key) in (None, "")]
    if candidate_missing:
        return {"authorized": False, "reason": "candidate-missing-binding", "missing": candidate_missing}

    qualification_missing = [key for key in identity_fields if current_qualification.get(key) in (None, "")]
    if qualification_missing:
        return {"authorized": False, "reason": "qualification-missing-binding", "missing": qualification_missing}

    route_missing = [key for key in route_scope_fields if original_route.get(key) in (None, "")]
    if route_missing:
        return {"authorized": False, "reason": "original-route-missing-binding", "missing": route_missing}

    if current_qualification.get("status") != "QUALIFIED":
        return {"authorized": False, "reason": "candidate-not-currently-qualified"}

    for key in identity_fields:
        if candidate.get(key) != current_qualification.get(key):
            return {"authorized": False, "reason": f"qualification-{key}-mismatch"}

    for key in route_scope_fields:
        if candidate.get(key) != original_route.get(key):
            return {"authorized": False, "reason": f"route-{key}-substitution-denied"}

    return {
        "authorized": True,
        "reason": "qualified-failover-authorized",
        "selected": {
            "provider": candidate["provider"],
            "model": candidate["model"],
            "sku": candidate["sku"],
            "deployment_path": candidate["deployment_path"],
            "qualification_id": candidate["qualification_id"],
            "qualification_epoch": candidate["qualification_epoch"],
        },
    }
