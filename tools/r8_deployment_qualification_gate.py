"""Dry-run deployment qualification evaluator; never deploys or authorizes."""
from __future__ import annotations

REQUIRED = {"schema", "release_artifact_sha256", "environment_identity", "environment_digest", "config_digest", "migration_check", "preflight", "health_checks", "rollback_plan", "post_deploy_evidence", "deployment_authorized"}

def evaluate(record: dict, *, expected_artifact: str, expected_environment: str) -> dict:
    if set(record) != REQUIRED: raise ValueError("deployment schema mismatch")
    if record["release_artifact_sha256"] != expected_artifact: raise ValueError("artifact substitution")
    if record["environment_identity"] != expected_environment: raise ValueError("environment drift")
    if len(record["environment_digest"]) != 64 or len(record["config_digest"]) != 64: raise ValueError("missing environment provenance")
    if record["migration_check"] is not True or record["preflight"] is not True: raise ValueError("preflight incomplete")
    if record["health_checks"] is not True: raise ValueError("health checks incomplete")
    if record["rollback_plan"] is not True: raise ValueError("rollback evidence missing")
    if record["post_deploy_evidence"] is not False: raise ValueError("deployment evidence cannot imply execution")
    if record["deployment_authorized"] is not False: raise ValueError("qualification cannot authorize deployment")
    return {"status": "DEPLOYMENT_QUALIFIED_EVIDENCE", "deployment_authorized": False}
