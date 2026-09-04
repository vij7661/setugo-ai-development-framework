"""Deterministic continuation and corrective-authority controller.

No model receives corrective authority merely because execution failed. Evidence
must establish a failure classification first; classification then constrains
what an agent/tool may modify. Requirement uncertainty never receives automatic
write authority.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

TERMINAL = {"success", "failure", "cancelled", "timed_out", "action_required"}
CLASSIFICATIONS = {
    "CODE DEFECT",
    "FIXTURE-DATA DEFECT",
    "TEST DEFECT",
    "ENVIRONMENT-TOOLING DEFECT",
    "REQUIREMENT UNRESOLVED",
}
AUTHORITY = {
    "CODE DEFECT": {"decision": "REPAIR", "authority": "PRODUCTION_CODE_SCOPED", "allowed_artifacts": ["production_code"]},
    "FIXTURE-DATA DEFECT": {"decision": "REPAIR", "authority": "FIXTURE_DATA_SCOPED", "allowed_artifacts": ["fixtures", "seed_data", "test_data"]},
    "TEST DEFECT": {"decision": "REPAIR", "authority": "TEST_SCOPED", "allowed_artifacts": ["tests", "test_harness"]},
    "ENVIRONMENT-TOOLING DEFECT": {"decision": "REPAIR", "authority": "ENVIRONMENT_TOOLING_SCOPED", "allowed_artifacts": ["ci", "tooling", "environment_config", "build_config"]},
    "REQUIREMENT UNRESOLVED": {"decision": "REQUEST_HUMAN", "authority": "NONE", "allowed_artifacts": []},
}


def decide(event: dict) -> dict:
    conclusion = str(event.get("conclusion", "")).lower()
    case_id = event.get("case_id")
    attempt = int(event.get("repair_attempt", 0))
    max_attempts = int(event.get("max_repair_attempts", 2))
    classification = event.get("classification")

    if conclusion not in TERMINAL:
        return {"decision": "IGNORE", "reason": "execution is not terminal", "case_id": case_id, "authority": "NONE"}
    if conclusion == "success":
        return {"decision": "CONTINUE", "reason": "execution completed; evidence must be adjudicated before scientific PASS", "case_id": case_id, "authority": "EVIDENCE_ONLY", "allowed_artifacts": []}
    if conclusion in {"cancelled", "action_required"}:
        return {"decision": "REQUEST_HUMAN", "reason": f"terminal state {conclusion} is not safe to auto-repair", "case_id": case_id, "authority": "NONE", "allowed_artifacts": []}
    if attempt >= max_attempts:
        return {"decision": "REQUEST_HUMAN", "reason": "automatic repair budget exhausted", "case_id": case_id, "authority": "NONE", "allowed_artifacts": []}
    if not classification:
        return {"decision": "DIAGNOSE", "reason": "execution failure requires evidence-based failure classification", "case_id": case_id, "allowed_classifications": sorted(CLASSIFICATIONS), "authority": "NONE_UNTIL_CLASSIFIED", "allowed_artifacts": [], "next": "collect exact-SHA evidence and classify before granting scoped repair authority"}
    if classification not in CLASSIFICATIONS:
        return {"decision": "BLOCK", "reason": "unrecognized failure classification", "case_id": case_id, "authority": "NONE", "allowed_artifacts": []}

    grant = dict(AUTHORITY[classification])
    grant.update({"case_id": case_id, "classification": classification, "repair_attempt": attempt, "max_repair_attempts": max_attempts})
    if classification == "REQUIREMENT UNRESOLVED":
        grant["reason"] = "requirement ambiguity cannot be repaired by inventing product intent"
        grant["human_required"] = True
    else:
        grant["reason"] = "classification established; correction is restricted to the authorized artifact class"
        grant["human_required"] = False
        grant["verification_required"] = ["original_failing_check", "targeted_regression", "affected_regression", "exact_sha_verification"]
    return grant


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    event = json.loads(Path(args.event).read_text(encoding="utf-8"))
    result = decide(event)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
