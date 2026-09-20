"""Independent, source-bound R2D self-adjudication (offline only)."""
from __future__ import annotations
import json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GP = ROOT / "experiments" / "governed-platform"

def load(name: str):
    return json.loads((GP / name).read_text(encoding="utf-8"))

def main() -> int:
    phase, mutation, tests, falsify = (load(n) for n in (
        "EXP-M-DETERMINISTIC-RESULTS.json", "EXP-M-MUTATION-RESULTS.json",
        "EXP-M-TEST-RESULTS.json", "EXP-M-SELF-FALSIFICATION-RESULTS.json"))
    from exp_m_deterministic import admissibility_registry
    from exp_m_review_fixtures import FIXTURE_CATALOG
    reg = admissibility_registry()
    commit = subprocess.check_output(("git", "rev-parse", "HEAD"), cwd=ROOT, text=True).strip()
    tree = subprocess.check_output(("git", "rev-parse", "HEAD^{tree}"), cwd=ROOT, text=True).strip()
    artifacts = (phase, mutation, tests, falsify)
    bound = all(a.get("execution", {}).get("source_commit") == commit and a.get("execution", {}).get("source_tree") == tree for a in artifacts)
    phase_cases = all(
        v.get("status") == "PASS" and len(v.get("executed_cases", ())) >= 2 and
        any(c.get("kind") == "positive" and c.get("result") is True and c.get("production_functions") for c in v.get("executed_cases", ())) and
        any(c.get("kind") == "negative" and c.get("result") is True and c.get("actual") == "REJECT" and c.get("production_functions") for c in v.get("executed_cases", ()))
        for v in phase.get("phases", {}).values())
    predicates = set(reg.predicate_ids)
    fixtures = {str(x["target_predicate_id"]) for x in FIXTURE_CATALOG}
    mutation_closed = (mutation.get("all_rejected") is True and mutation.get("surviving_mutations") == 0 and
        set(mutation.get("verdict_predicate_ids", ())) == predicates and
        set(mutation.get("declared_mutation_targets", ())) == predicates and
        set(mutation.get("executed_mutation_targets", ())) == predicates and
        set(mutation.get("killed_mutation_targets", ())) == predicates and
        set(mutation.get("declared_fixture_targets", ())) == fixtures and
        set(mutation.get("executed_fixture_targets", ())) == fixtures and
        all(m.get("negative_control") in (None, "REJECT") for m in mutation.get("mutations", ())))
    checks = {
        "source_bound": bound,
        "tests_pass": tests.get("all_passed") is True and tests.get("tests_failed") == 0 and tests.get("tests_total", 0) > 0,
        "phases_pass": phase.get("all_phases_pass") is True and phase_cases,
        "mutation_catalog_closed": mutation_closed,
        "self_falsification_clean": falsify.get("all_rejected") is True and falsify.get("surviving_critical") == 0 and falsify.get("surviving_high") == 0,
        "live_provider_execution_false": all(a.get("execution", {}).get("live_provider_execution", False) is False for a in artifacts if "live_provider_execution" in a.get("execution", {})),
        "r2d_attacks_present": falsify.get("total", 0) >= 50,
    }
    ok = all(checks.values())
    result = {"experiment":"EXP-M", "remediation":"R2D", "status":"SELF_ADJUDICATION_PASS" if ok else "SELF_ADJUDICATION_FAIL", "unresolved_critical":0 if ok else 1, "unresolved_high":0 if ok else 1, "checks":checks, "execution":{"source_commit":commit,"source_tree":tree,"utc":datetime.now(timezone.utc).isoformat(),"command":"python governance-runtime/self_adjudicate_r2d.py","interpreter":sys.executable,"live_provider_execution":False}}
    (GP / "EXP-M-R2D-SELF-ADJUDICATION.json").write_text(json.dumps(result, indent=2, sort_keys=True)+"\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
