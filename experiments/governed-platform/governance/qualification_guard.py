"""Qualification freshness guard for governed model/provider routing and execution."""
from __future__ import annotations


IDENTITY_FIELDS = ("provider", "model", "sku", "deployment_path")


def _identity_mismatch(left: dict, right: dict) -> list[str]:
    return [field for field in IDENTITY_FIELDS if left.get(field) != right.get(field)]


def authorize_qualified_execution(route: dict, registry_entry: dict, *, now_epoch: int) -> dict:
    """Revalidate exact qualification lineage at execution time.

    Eligibility is bound to provider + model + SKU + deployment path. A technically
    successful substitute is not equivalent authority.
    """
    required = [
        *IDENTITY_FIELDS,
        "qualification_ref",
        "qualification_epoch",
        "qualification_expires_epoch",
    ]
    missing = [key for key in required if key not in registry_entry]
    if missing:
        return {"authorized": False, "reason": "qualification metadata incomplete", "missing": missing}

    route_missing = [key for key in (*IDENTITY_FIELDS, "qualification_ref", "qualification_epoch") if key not in route]
    if route_missing:
        return {"authorized": False, "reason": "route qualification identity incomplete", "missing": route_missing}

    mismatched = _identity_mismatch(route, registry_entry)
    if mismatched:
        return {
            "authorized": False,
            "reason": "route identity does not match current registry entry",
            "mismatched_identity_fields": mismatched,
        }
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
    return {
        "authorized": True,
        "reason": "current exact qualification identity revalidated at execution",
        "identity": {field: registry_entry[field] for field in IDENTITY_FIELDS},
    }


def evidence_still_admissible(evidence: dict, registry_entry: dict) -> dict:
    """Invalidate model evidence when any qualification identity dimension is stale."""
    missing = [key for key in (*IDENTITY_FIELDS, "qualification_ref", "qualification_epoch") if key not in evidence]
    if missing:
        return {"admissible": False, "reason": "evidence qualification identity incomplete", "missing": missing}

    registry_missing = [key for key in (*IDENTITY_FIELDS, "qualification_ref", "qualification_epoch") if key not in registry_entry]
    if registry_missing:
        return {"admissible": False, "reason": "registry qualification identity incomplete", "missing": registry_missing}

    mismatched = _identity_mismatch(evidence, registry_entry)
    if mismatched:
        return {
            "admissible": False,
            "reason": "evidence qualification identity mismatch",
            "mismatched_identity_fields": mismatched,
        }
    if evidence.get("qualification_ref") != registry_entry.get("qualification_ref"):
        return {"admissible": False, "reason": "evidence qualification lineage is stale"}
    if evidence.get("qualification_epoch") != registry_entry.get("qualification_epoch"):
        return {"admissible": False, "reason": "evidence qualification epoch is stale"}
    if registry_entry.get("revoked", False) or not registry_entry.get("eligible", False):
        return {"admissible": False, "reason": "current registry state revokes evidence eligibility"}
    return {"admissible": True, "reason": "evidence remains bound to current exact qualification identity"}
