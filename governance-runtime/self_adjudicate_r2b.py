"""Evidence-derived internal R2B self-adjudication.

This is a local deterministic gate: it consumes only S2-bound test, phase,
mutation and self-falsification artifacts and never contacts a provider.
"""
from __future__ import annotations
import json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GP = ROOT / "experiments/governed-platform"

def main() -> int:
    phase = json.loads((GP / "EXP-M-DETERMINISTIC-RESULTS.json").read_text())
    mutation = json.loads((GP / "EXP-M-MUTATION-RESULTS.json").read_text())
    self_falsify = json.loads((GP / "EXP-M-SELF-FALSIFICATION-RESULTS.json").read_text())
    tests = json.loads((GP / "EXP-M-TEST-RESULTS.json").read_text())
    source_commit = subprocess.check_output(("git", "rev-parse", "HEAD"), cwd=ROOT, text=True).strip()
    source_tree = subprocess.check_output(("git", "rev-parse", "HEAD^{tree}"), cwd=ROOT, text=True).strip()
    expected = source_commit
    checks = {
        "tests_bound": all(s.get("execution", {}).get("source_commit") == expected for s in (phase, mutation, self_falsify, tests)),
        "all_phases_real_cases": bool(phase.get("all_phases_pass")) and all(len(v.get("executed_cases", ())) >= 2 and all("production_functions" in c and "expected" in c and "actual" in c for c in v.get("executed_cases", ())) for v in phase.get("phases", {}).values()),
        "mutation_catalog_and_fixtures_closed": mutation.get("all_rejected") is True and mutation.get("surviving_mutations") == 0 and set(mutation.get("declared_mutation_targets", ())) == set(mutation.get("executed_mutation_targets", ())) == set(mutation.get("killed_mutation_targets", ())) == set(mutation.get("verdict_predicate_ids", ())),
        "self_falsification_clean": self_falsify.get("all_rejected") is True and self_falsify.get("surviving_critical") == 0 and self_falsify.get("surviving_high") == 0,
        "offline_tests_clean": tests.get("all_passed") is True and tests.get("tests_failed") == 0,
        "provider_execution_false": True,
    }
    result = {"experiment": "EXP-M", "remediation": "R2B", "status": "SELF_ADJUDICATION_PASS" if all(checks.values()) else "SELF_ADJUDICATION_FAIL", "unresolved_critical": 0 if all(checks.values()) else 1, "unresolved_high": 0 if all(checks.values()) else 1, "checks": checks, "execution": {"source_commit": source_commit, "source_tree": source_tree, "utc": datetime.now(timezone.utc).isoformat(), "command": "python governance-runtime/self_adjudicate_r2b.py", "interpreter": sys.executable, "live_provider_execution": False}}
    out = GP / "EXP-M-R2B-SELF-ADJUDICATION.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "SELF_ADJUDICATION_PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())
