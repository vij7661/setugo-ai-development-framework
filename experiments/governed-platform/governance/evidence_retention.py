"""Evidence admissibility guard for historical replay and retention semantics."""
from __future__ import annotations


def evidence_is_admissible(record: dict, current: dict, *, now_epoch: int) -> dict:
    """Fail closed unless historical evidence remains in the current authority lineage."""
    required = [
        "evidence_id", "project_id", "task_id", "execution_sha", "policy_epoch",
        "qualification_epoch", "capability_epoch", "issued_epoch", "retention_until_epoch",
    ]
    missing = [k for k in required if record.get(k) in (None, "")]
    if missing:
        return {"admissible": False, "reason": "missing evidence fields: " + ",".join(missing)}
    if record.get("invalidated", False):
        return {"admissible": False, "reason": "evidence explicitly invalidated"}
    try:
        retention_until = int(record["retention_until_epoch"])
        now_value = int(now_epoch)
    except (TypeError, ValueError):
        return {"admissible": False, "reason": "retention epoch malformed"}
    if now_value > retention_until:
        return {"admissible": False, "reason": "evidence retention window expired"}
    bindings = {
        "project_id": current.get("project_id"),
        "task_id": current.get("task_id"),
        "execution_sha": current.get("execution_sha"),
        "policy_epoch": current.get("policy_epoch"),
        "qualification_epoch": current.get("qualification_epoch"),
        "capability_epoch": current.get("capability_epoch"),
    }
    for key, expected in bindings.items():
        if record.get(key) != expected:
            return {"admissible": False, "reason": f"evidence {key} is stale or out of scope"}
    revoked = set(current.get("revoked_evidence_ids", []))
    if record["evidence_id"] in revoked:
        return {"admissible": False, "reason": "evidence id revoked"}
    return {"admissible": True, "reason": "evidence remains current and within retention"}
