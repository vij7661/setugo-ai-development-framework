#!/usr/bin/env python3
"""Normalize a GitHub Actions execution snapshot into dashboard state.

Input is deliberately provider-neutral JSON produced by the workflow. Protected truth
is never accepted by this adapter. Optional expected-scope arguments reject stale or
out-of-scope events before they can become authoritative state.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ALLOWED = {
    "CODE DEFECT",
    "FIXTURE-DATA DEFECT",
    "TEST DEFECT",
    "ENVIRONMENT-TOOLING DEFECT",
    "REQUIREMENT UNRESOLVED",
    "NONE",
}


def normalize(e: dict, *, expected_branch: str | None = None, expected_sha: str | None = None,
              expected_case: str | None = None, expected_run_id: str | None = None) -> dict:
    required = ("campaign", "experiment", "case_id", "branch", "execution_sha", "run_id", "jobs")
    missing = [k for k in required if k not in e]
    if missing:
        raise ValueError("missing authoritative fields: " + ",".join(missing))

    scope_checks = {
        "branch": expected_branch,
        "execution_sha": expected_sha,
        "case_id": expected_case,
        "run_id": expected_run_id,
    }
    for field, expected in scope_checks.items():
        if expected is not None and str(e[field]) != str(expected):
            raise ValueError(f"out-of-scope event: expected {field}={expected}, got {e[field]}")

    conclusions = [j.get("conclusion") for j in e["jobs"]]
    if any(x in {"failure", "timed_out"} for x in conclusions):
        status = "FAILED"
    elif any(x in {"queued", "in_progress", None} for x in conclusions):
        status = "EXECUTING"
    elif conclusions and all(x in {"success", "skipped"} for x in conclusions):
        status = "COMPLETE"
    else:
        status = "BLOCKED"

    classification = e.get("failure_classification", "NONE")
    if classification not in ALLOWED:
        raise ValueError("invalid failure classification")

    scientific_status = e.get("scientific_status")
    if scientific_status is None:
        scientific_status = "AWAITING_ADJUDICATION" if status == "COMPLETE" else "INCONCLUSIVE"
    elif status != "COMPLETE" and scientific_status == "PASS":
        raise ValueError("scientific PASS cannot be emitted from incomplete/failed execution")

    return {
        "schema_version": "1.0",
        "campaign": e["campaign"],
        "experiment": e["experiment"],
        "case_id": e["case_id"],
        "execution_status": status,
        "scientific_status": scientific_status,
        "branch": e["branch"],
        "execution_sha": e["execution_sha"],
        "run_id": e["run_id"],
        "jobs": e["jobs"],
        "failure_classification": classification,
        "controller_decision": e.get("controller_decision", "UNKNOWN"),
        "repair_attempt": e.get("repair_attempt", 0),
        "max_repair_attempts": e.get("max_repair_attempts", 2),
        "next_case": e.get("next_case"),
        "human_required": bool(e.get("human_required", False)),
        "human_reason": e.get("human_reason"),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--event", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--expected-branch")
    p.add_argument("--expected-sha")
    p.add_argument("--expected-case")
    p.add_argument("--expected-run-id")
    a = p.parse_args()
    e = json.loads(Path(a.event).read_text(encoding="utf-8"))
    try:
        state = normalize(
            e,
            expected_branch=a.expected_branch,
            expected_sha=a.expected_sha,
            expected_case=a.expected_case,
            expected_run_id=a.expected_run_id,
        )
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    Path(a.out).write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
