"""Qualification freshness guard for governed model/provider routing and execution."""
from __future__ import annotations


def authorize_qualified_execution(route: dict, registry_entry: dict, *, now_epoch: int) -> dict:
    """Revalidate qualification at execution time; routing-time eligibility is insufficient."""
    required = ["provider", "model", "qualification_ref", "qualification_epoch", "qualification_expires_epoch"]
    missing = [key for key in required if key not in registry_entry]
    if missing:
        return {"authorized": False, "reason": "qualification metadata incomplete", "missing": missing}

    if route.get("provider") != registry_entry.get("provider") or route.get("model") != registry_entry.get("model"):
        return {"authorized": False, "reason": "route identity does not match current registry entry"}
    if route.get("qualification_ref") != registry_entry.get("qualification_ref"):
        return {"authorized": False, "reason": "qualification changed after routing"}
    if registry_entry.get("revoked", False):
        return {"authorized": False, "reason": "qualification has been revoked"}
    if not registry_entry.get("eligible", False):
        return {"authorized": False, "reason": "registry entry is currently ineligible"}
    try:
        routed_epoch = int(route.get("qualification_epoch"))
        current_epoch = int(registry_entry.get("qualification_epoch"))
        expires = int(registry_entry.get("qualification_expires_epoch"))
    except (TypeError, ValueError):
        return {"authorized": False, "reason": "qualification epoch metadata malformed"}
    if routed_epoch != current_epoch:
        return {"authorized": False, "reason": "qualification epoch drift detected"}
    if now_epoch >= expires:
        return {"authorized": False, "reason": "qualification expired before execution"}
    return {"authorized": True, "reason": "current qualification revalidated at execution"}


def evidence_still_admissible(evidence: dict, registry_entry: dict) -> dict:
    """Invalidate prior model evidence when its qualification lineage is revoked or replaced."""
    if evidence.get("provider") != registry_entry.get("provider") or evidence.get("model") != registry_entry.get("model"):
        return {"admissible": False, "reason": "evidence model/provider identity mismatch"}
    if evidence.get("qualification_ref") != registry_entry.get("qualification_ref"):
        return {"admissible": False, "reason": "evidence qualification lineage is stale"}
    if evidence.get("qualification_epoch") != registry_entry.get("qualification_epoch"):
        return {"admissible": False, "reason": "evidence qualification epoch is stale"}
    if registry_entry.get("revoked", False) or not registry_entry.get("eligible", False):
        return {"admissible": False, "reason": "current registry state revokes evidence eligibility"}
    return {"admissible": True, "reason": "evidence remains bound to current qualification lineage"}
