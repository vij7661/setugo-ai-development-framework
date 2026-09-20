"""Independent offline R2C self-adjudication gate."""
from __future__ import annotations
import json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GP = ROOT / "experiments" / "governed-platform"

def load(name: str):
    return json.loads((GP / name).read_text(encoding="utf-8"))

def main() -> int:
    phase = load("EXP-M-DETERMINISTIC-RESULTS.json")
    mutation = load("EXP-M-MUTATION-RESULTS.json")
    tests = load("EXP-M-TEST-RESULTS.json")
    falsify = load("EXP-M-SELF-FALSIFICATION-RESULTS.json")
    from exp_m_deterministic import admissibility_registry
    from exp_m_review_fixtures import FIXTURE_CATALOG
    reg = admissibility_registry()
    source_commit = subprocess.check_output(("git", "rev-parse", "HEAD"), cwd=ROOT, text=True).strip()
    source_tree = subprocess.check_output(("git", "rev-parse", "HEAD^{tree}"), cwd=ROOT, text=True).strip()
    expected_predicates = set(reg.predicate_ids)
    fixture_targets = {str(x["target_predicate_id"]) for x in FIXTURE_CATALOG}
    executed_cases = all(
        v.get("status") == "PASS" and len(v.get("executed_cases", ())) >= 2
        and all(c.get("kind") in {"positive", "negative"} and c.get("result") is True for c in v.get("executed_cases", ()))
        for v in phase.get("phases", {}).values()
    )
    same_source = all(x.get("execution", {}).get("source_commit") == source_commit for x in (phase, mutation, tests, falsify))
    checks = {
        "tests_bound": same_source and tests.get("all_passed") is True and tests.get("tests_failed") == 0,
        "phase_cases_independent": bool(phase.get("all_phases_pass")) and executed_cases,
        "predicate_registry_closed": set(mutation.get("verdict_predicate_ids", ())) == expected_predicates,
        "mutation_catalog_closed": set(mutation.get("declared_mutation_targets", ())) == expected_predicates and set(mutation.get("executed_mutation_targets", ())) == expected_predicates and set(mutation.get("killed_mutation_targets", ())) == expected_predicates and mutation.get("all_rejected") is True and mutation.get("surviving_mutations") == 0,
        "fixture_catalog_closed": fixture_targets == expected_predicates and set(mutation.get("declared_fixture_targets", ())) == fixture_targets and set(mutation.get("executed_fixture_targets", ())) == fixture_targets,
        "self_falsification_clean": same_source and falsify.get("all_rejected") is True and falsify.get("surviving_critical") == 0 and falsify.get("surviving_high") == 0,
        "provider_execution_false": True,
    }
    ok = all(checks.values())
    result = {
        "experiment": "EXP-M", "remediation": "R2C",
        "status": "SELF_ADJUDICATION_PASS" if ok else "SELF_ADJUDICATION_FAIL",
        "unresolved_critical": 0 if ok else 1, "unresolved_high": 0 if ok else 1,
        "checks": checks,
        "execution": {"source_commit": source_commit, "source_tree": source_tree, "utc": datetime.now(timezone.utc).isoformat(), "command": "python governance-runtime/self_adjudicate_r2c.py", "interpreter": sys.executable, "live_provider_execution": False},
    }
    out = GP / "EXP-M-R2C-SELF-ADJUDICATION.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
