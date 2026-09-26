"""Production-readiness evidence checks with an explicit non-authority boundary."""
from __future__ import annotations

REQUIRED = {"schema", "release_evidence_sha256", "deployment_evidence_sha256", "observability", "audit_history", "backup_recovery", "incident_rollback", "capacity_health", "secret_config", "dependency_failure", "production_authorized"}

def evaluate(record: dict) -> dict:
    if set(record) != REQUIRED: raise ValueError("production readiness schema mismatch")
    for key in ("release_evidence_sha256", "deployment_evidence_sha256"):
        if not isinstance(record[key], str) or len(record[key]) != 64: raise ValueError("evidence lineage missing")
    for key in ("observability", "audit_history", "backup_recovery", "incident_rollback", "capacity_health", "secret_config", "dependency_failure"):
        if record[key] is not True: raise ValueError(f"readiness check failed: {key}")
    if record["production_authorized"] is not False: raise ValueError("readiness cannot authorize production")
    return {"status": "PRODUCTION_READY_EVIDENCE", "production_authorized": False}
