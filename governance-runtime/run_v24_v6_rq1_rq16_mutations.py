#!/usr/bin/env python3
"""Offline RQ-16 preregistration mutation checks; never touches the runtime."""
from __future__ import annotations
import copy, json
from v24_v6_rq1_rq16_harness import evaluate_arm

GOOD = {
    "fault_proof": {"injected": True, "errno": "ENOSPC"},
    "target_path": "/run/v24-v6-authority/private/records/T.record",
    "observer_ok": True, "cleanup_verified": True, "restored_exact": True,
    "service_recoverable": True, "lifecycle_explained": True,
}

def case(name, mutate, expected="reject"):
    ev = copy.deepcopy(GOOD); mutate(ev)
    actual, reasons = evaluate_arm("ENOSPC", ev)
    return {"mutation_id": name, "expected": expected, "actual": actual,
            "reasons": reasons, "rejected": actual != "PASS"}

def main():
    muts = [
        ("missing_fault_proof", lambda e: e.pop("fault_proof")),
        ("wrong_errno", lambda e: e["fault_proof"].update(errno="EROFS")),
        ("injected_false", lambda e: e["fault_proof"].update(injected=False)),
        ("observer_failure", lambda e: e.update(observer_ok=False)),
        ("cleanup_failure", lambda e: e.update(cleanup_verified=False)),
        ("restoration_mismatch", lambda e: e.update(restored_exact=False)),
        ("service_not_recoverable", lambda e: e.update(service_recoverable=False)),
        ("lifecycle_unexplained", lambda e: e.update(lifecycle_explained=False)),
        ("authoritative_success", lambda e: e.update(authoritative_success=True)),
        ("invalid_transition", lambda e: e.update(invalid_transition=True)),
        ("missing_target", lambda e: e.pop("target_path")),
        ("unknown_arm_cross_substitution", lambda e: None),
    ]
    results = []
    for name, mutate in muts:
        if name == "unknown_arm_cross_substitution":
            actual, reasons = evaluate_arm("EROFS", GOOD)
            results.append({"mutation_id": name, "expected": "reject", "actual": actual, "reasons": reasons, "rejected": actual != "PASS"})
        else:
            results.append(case(name, mutate))
    out = {"total_mutations": len(results), "rejected_mutations": sum(r["rejected"] for r in results),
           "surviving_mutations": sum(not r["rejected"] for r in results),
           "all_rejected": all(r["rejected"] for r in results), "mutations": results,
           "RQ16_EXECUTED": False}
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0 if out["all_rejected"] and out["surviving_mutations"] == 0 else 2

if __name__ == "__main__": raise SystemExit(main())
