"""Deterministic continuation controller for governed-platform pilots.

The controller deliberately makes no model calls. It converts terminal execution
facts into a constrained next action. Reasoning/repair agents are downstream
capabilities and receive authority only after classification.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

TERMINAL = {"success", "failure", "cancelled", "timed_out", "action_required"}


def decide(event: dict) -> dict:
    conclusion = str(event.get("conclusion", "")).lower()
    case_id = event.get("case_id")
    attempt = int(event.get("repair_attempt", 0))
    max_attempts = int(event.get("max_repair_attempts", 2))

    if conclusion not in TERMINAL:
        return {"decision": "IGNORE", "reason": "execution is not terminal", "case_id": case_id}
    if conclusion == "success":
        return {
            "decision": "CONTINUE",
            "reason": "execution completed; evidence must be adjudicated before scientific PASS",
            "case_id": case_id,
            "authority": "EVIDENCE_ONLY",
        }
    if conclusion in {"cancelled", "action_required"}:
        return {
            "decision": "REQUEST_HUMAN",
            "reason": f"terminal state {conclusion} is not safe to auto-repair",
            "case_id": case_id,
            "authority": "NONE",
        }
    if attempt >= max_attempts:
        return {
            "decision": "REQUEST_HUMAN",
            "reason": "automatic environment/tooling repair budget exhausted",
            "case_id": case_id,
            "authority": "NONE",
        }
    return {
        "decision": "DIAGNOSE",
        "reason": "execution failure requires evidence-based failure classification",
        "case_id": case_id,
        "allowed_classifications": [
            "CODE DEFECT",
            "FIXTURE-DATA DEFECT",
            "TEST DEFECT",
            "ENVIRONMENT-TOOLING DEFECT",
            "REQUIREMENT UNRESOLVED",
        ],
        "authority": "NONE_UNTIL_CLASSIFIED",
        "next": "collect exact-SHA logs and classify before granting scoped repair authority",
    }


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
