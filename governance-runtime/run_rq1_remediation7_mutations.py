#!/usr/bin/env python3
"""Apply adversarial mutations to copied evidence and require NOT_PASS."""
from __future__ import annotations
import argparse, copy, json
from pathlib import Path
from replay_rq1_crash_evidence import adapt_case
from v24_v6_rq1_crash_predicates import evaluate_crash_case


def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("evidence", type=Path); ap.add_argument("--output", type=Path, required=True); args = ap.parse_args()
    checks = []
    for case in ("RQ-13", "RQ-14", "RQ-15"):
        base = adapt_case(args.evidence, case)
        mutations = {
            "retry_empty": lambda e: e["retry"].update(parsed={}),
            "retry_malformed": lambda e: e["retry"].update(parsed="not-json"),
            "retry_authoritative": lambda e: e["retry"].update(parsed={"service_authoritative": True}),
            "wrong_replay_reason": lambda e: e["replay"].update(parsed={"trusted_record_id": e["target_id"], "service_authoritative": False, "reason": "WRONG"}),
            "replay_parse_failure": lambda e: e["replay"].update(parsed="not-json"),
            "nonzero_retry_delta": lambda e: e.update(records_delta_retry={"added": ["other.record"], "removed": []}),
            "replay_state_mutation": lambda e: e.update(records_delta_post_replay={"added": ["other.record"], "removed": []}),
            "wrong_pid": lambda e: e["boundary_evidence"].update(pid=999),
            "wrong_syscall": lambda e: e["boundary_evidence"].update(syscall=1),
            "trace_error": lambda e: e["boundary_evidence"].update(error="injected"),
            "wrong_boundary": lambda e: e["boundary_evidence"].update(boundary="wrong"),
            "wrong_path": lambda e: e["boundary_evidence"].update(paths=["/wrong/path"]),
            "first_authoritative": lambda e: e["first_consume"].update(parsed={"service_authoritative": True}),
            "tracer_not_armed": lambda e: e["tracer_ready"].update(armed=False),
            "launch_before_ready": lambda e: e.update(control_launch_timestamp=0),
        }
        if case == "RQ-15":
            mutations["failed_rename"] = lambda e: e["boundary_evidence"].update(return_value=1)
        for name, mutate in mutations.items():
            evidence = copy.deepcopy(base); mutate(evidence); ok, reasons = evaluate_crash_case(case, evidence)
            checks.append({"case": case, "mutation": name, "pass": ok, "reasons": reasons})
    args.output.write_text(json.dumps({"operation": "OFFLINE_MUTATION_FALSIFICATION", "checks": checks, "all_rejected": all(not c["pass"] for c in checks)}, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return 0 if all(not c["pass"] for c in checks) else 2


if __name__ == "__main__":
    raise SystemExit(main())
