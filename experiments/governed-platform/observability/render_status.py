#!/usr/bin/env python3
"""Render a human-readable execution dashboard from normalized authoritative state."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def render(state: dict) -> str:
    jobs = state.get("jobs", [])
    lines = [
        "# Governed Platform — Live Execution",
        "",
        f"- **Campaign:** {state.get('campaign', 'UNKNOWN')}",
        f"- **Experiment:** {state.get('experiment', 'UNKNOWN')}",
        f"- **Case:** {state.get('case_id', 'UNKNOWN')}",
        f"- **Execution:** {state.get('execution_status', state.get('state', 'UNKNOWN'))}",
        f"- **Scientific:** {state.get('scientific_status', 'AWAITING_ADJUDICATION')}",
        f"- **Human action:** {'REQUIRED' if state.get('human_required') else 'NOT REQUIRED'}",
        "",
        "## Jobs",
        "",
    ]
    if jobs:
        for job in jobs:
            lines.append(f"- **{job.get('name', 'unknown')}** — {job.get('status', 'UNKNOWN')}")
    else:
        lines.append("- No normalized job evidence recorded yet.")
    lines += [
        "",
        "## Execution identity",
        "",
        f"- **Branch:** `{state.get('branch', 'UNKNOWN')}`",
        f"- **Exact SHA:** `{state.get('execution_sha', state.get('last_verified_sha', 'UNKNOWN'))}`",
        f"- **Run ID:** `{state.get('run_id', 'UNKNOWN')}`",
        f"- **Repair attempts:** {state.get('repair_attempt', 0)} / {state.get('max_repair_attempts', 0)}",
        f"- **Failure classification:** {state.get('failure_classification', 'NONE')}",
        f"- **Controller decision:** {state.get('controller_decision', 'UNKNOWN')}",
        f"- **Next:** {state.get('next_case', 'AWAITING_CONTROLLER')}",
        "",
        "> Execution success is not scientific PASS. Scientific status changes only after evidence adjudication.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    state = json.loads(Path(args.state).read_text(encoding="utf-8"))
    Path(args.out).write_text(render(state), encoding="utf-8")
    print(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
