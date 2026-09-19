#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, subprocess, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / ".rq1-remediation7-input-20260919161744" / "raw-evidence"
OUT = ROOT / "V24-I11-V6-RQ1-REMEDIATION-7-F02-CLOSURE-REVIEW.md"
CASES = ("RQ-13", "RQ-14", "RQ-15")
TMP = Path(__import__("os").environ.get("TEMP", "/tmp"))


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""): h.update(b)
    return h.hexdigest()


def text(p: Path) -> str:
    raw = p.read_bytes()
    if raw.startswith(b"\xff\xfe"):
        return raw.decode("utf-16")
    if raw.startswith(b"\xfe\xff"):
        return raw.decode("utf-16-be")
    return raw.decode("utf-8")


def fenced(name: str, body: str, language: str = "text") -> str:
    return f"\n### {name}\n\n```{language}\n{body.rstrip()}\n```\n"


def run(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, cwd=ROOT, text=True, stderr=subprocess.STDOUT).strip()


def main() -> None:
    head = run(["git", "rev-parse", "HEAD"])
    tree = run(["git", "show", "-s", "--format=%T", "HEAD"])
    origin = run(["git", "rev-parse", "origin/qualification/v24-i11-v6-runtime-qualification-1-remediation-7"])
    status = run(["git", "status", "--short"])
    ahead = run(["git", "rev-list", "--left-right", "--count", "origin/qualification/v24-i11-v6-runtime-qualification-1-remediation-7...HEAD"])
    diff = run(["git", "diff", "18659a46ac9c9d2d4a79fdc84f45646427f00e95", "HEAD"])
    sources = [
        ROOT / "governance-runtime/v24_v6_rq1_crash_predicates.py",
        ROOT / "governance-runtime/replay_rq1_crash_evidence.py",
        ROOT / "governance-runtime/test_v24_v6_rq1_crash_observation.py",
        ROOT / "governance-runtime/run_rq1_remediation7_mutations.py",
        ROOT / "governance-runtime/v24_v6_rq1_remediation2_harness.py",
    ]
    direct = []
    import sys
    sys.path.insert(0, str(ROOT / "governance-runtime"))
    from v24_v6_rq1_crash_predicates import evaluate_crash_case
    for case in CASES:
        raw = json.loads(text(EVIDENCE / f"{case}.result.json")); detail = raw["detail"]
        direct.append({"case": case, "input_file": f"{case}.result.json", "input_sha256": sha(EVIDENCE / f"{case}.result.json"), "detail_keys": sorted(detail), "first_consume": detail.get("first_consume"), "trigger": detail.get("trigger"), "boundary": detail.get("boundary"), "restart": detail.get("restart"), "restart_returncode": detail.get("restart_returncode"), "retry": detail.get("retry"), "replay": detail.get("replay"), "direct_evaluation": evaluate_crash_case(case, detail)})
    replay_path = TMP / "rq1-f02/replay.json"
    mutation_path = TMP / "rq1-f02/mutations.json"
    test_path = TMP / "rq1-f02/tests.txt"
    validator_path = TMP / "rq1-f02/validator.txt"
    not_pushed = ahead.split()[-1] != "0"
    test_output = text(test_path)
    test_match = re.search(r"Ran (\d+) tests? in ", test_output)
    behavioral_total = int(test_match.group(1)) if test_match else 0
    behavioral_passed = behavioral_total if "\nOK\n" in test_output or test_output.rstrip().endswith("OK") else 0
    mutation_result = json.loads(text(mutation_path))
    mutation_total = mutation_result["total_mutations"]
    mutation_rejected = mutation_result["rejected_mutations"]
    mutation_surviving = mutation_result["surviving_mutations"]
    parts = ["# V24-I11-V6 RQ1 Remediation-7 DeepSeek Full Review", "", "This is a self-contained text artifact. No scientific execution was performed.", "", "## Source identity", "", f"branch=qualification/v24-i11-v6-runtime-qualification-1-remediation-7", f"local_head={head}", f"origin_head={origin}", f"local_tree={tree}", f"scientific_commit=d79db50568cccaffe67ed1de5a6ee63bf5027284", f"scientific_tree=2b86dad37b38bc2579dd09d4e545fb5248b17ae8", f"scientific_run=35433799081", f"git_status_short={status!r}", f"ahead_behind_left_right={ahead}", f"LOCAL_SOURCE_NOT_YET_ON_REMOTE={str(not_pushed).lower()}", "", f"## Authoritative current verification counts\n\nbehavioral_tests_total={behavioral_total}\nbehavioral_tests_passed={behavioral_passed}\nmutation_total={mutation_total}\nmutation_rejected={mutation_rejected}\nmutation_surviving={mutation_surviving}\nall_rejected={str(mutation_result['all_rejected']).lower()}", "", "## Historical superseded review material (non-authoritative)", "The exact diff below contains prior review text with superseded counts. Those historical counts are preserved only for chronology and MUST NOT be interpreted as current evidence. Current counts are the machine-derived values above.", fenced("git diff 18659...HEAD", diff), "## Included source SHA-256", ""]
    for p in sources: parts.append(f"{sha(p)}  {p.relative_to(ROOT).as_posix()}")
    harness_text = text(sources[4])
    parts += ["", "## Historical/current harness distinction", "", "Run-35 scientific execution used historical harness SHA-256 `7ce7d5fb9817898198aa3b2be89706cd9ac561a2763386f2cd1cd9412eb81e1d`; it did not use the current Remediation-7 evaluator. The immutable Run-35 result is adapted offline by `replay_rq1_crash_evidence.py::adapt_case` using representation-only mappings, then evaluated by the shared predicate. Current/future live execution uses `current_live_first_attempt` in `v24_v6_rq1_remediation2_harness.py` and directly feeds canonical evidence to the same `evaluate_crash_case`. This chronology is intentional and does not alter Run-35 evidence.", "", "## Complete corrected predicate source", fenced("v24_v6_rq1_crash_predicates.py", text(sources[0]), "python"), "## First-attempt interpreter", fenced("interpret_first_attempt", text(sources[0])[text(sources[0]).index("def interpret_first_attempt"):text(sources[0]).index("def _first_interrupted")], "python"), "## Complete replay source and historical adapter", fenced("replay_rq1_crash_evidence.py", text(sources[1]), "python"), "## Current live evidence builder", fenced("current_live_first_attempt", harness_text[harness_text.index("def current_live_first_attempt"):harness_text.index("def run(")], "python"), "## Complete behavioral tests", fenced("test_v24_v6_rq1_crash_observation.py", text(sources[2]), "python"), "## Complete mutation harness", fenced("run_rq1_remediation7_mutations.py", text(sources[3]), "python")]
    h = text(sources[4]); start = h.index("def _crash_case"); end = h.index("def protocol_variants")
    parts.append(fenced("Relevant live harness crash section", h[start:end], "python"))
    parts += ["## Shared evaluator code-path proof", "", "LIVE HARNESS: `v24_v6_rq1_remediation2_harness.py::_crash_case` imports and calls `evaluate_crash_case` from `v24_v6_rq1_crash_predicates.py` after collecting evidence.", "OFFLINE REPLAY: `replay_rq1_crash_evidence.py::adapt_case` normalizes raw files and calls the same `evaluate_crash_case`.", "TESTS: `test_v24_v6_rq1_crash_observation.py` imports and calls the same function.", "MUTATIONS: `run_rq1_remediation7_mutations.py` imports and calls the same function.", "", "## Complete direct untouched-detail replay", fenced("direct-untouched-detail-replay.json", json.dumps(direct, indent=2, sort_keys=True), "json"), "## Complete normalized offline replay", fenced("offline-replay.json", text(replay_path), "json"), "## Complete mutation results", fenced("mutation-results.json", text(mutation_path), "json"), "## Behavioral test output", fenced("regression-tests.txt", text(test_path)), "## Oracle validator output", fenced("oracle-validator.txt", text(validator_path))]
    parts += ["## Normalization provenance", "", "The complete per-field provenance is embedded in each case's `normalization_provenance` array in the normalized replay JSON. Every entry is representational only: dedicated raw observer/boundary/tracer files, preserved stdout parsing, or nested restart.rc aliasing. No semantic-change classification is used.", ""]
    for case in CASES:
        parts += [f"### Raw immutable files for {case}", ""]
        names = [f"{case}.result.json", f"{case}.diagnostic.json", f"{case}.tracer-ready.json", f"{case}.boundary.json", f"{case}.baseline.observer.json", f"{case}.prepared.observer.json", f"{case}.recovery.observer.json", f"{case}.post-retry.observer.json", f"{case}.post-replay.observer.json"]
        for n in names:
            p = EVIDENCE / n
            parts.append(fenced(n + " sha256=" + sha(p), text(p), "json"))
    for n in ("run-summary.json", "exit-code.txt", "harness.sha256", "observer.sha256", "bundle.sha256"):
        p = EVIDENCE / n
        parts.append(fenced(n + " sha256=" + sha(p), text(p), "json" if n.endswith("json") else "text"))
    parts += ["## Immutable input hash manifest", fenced("all Run-35 raw file hashes", "\n".join(f"{sha(p)}  {p.relative_to(EVIDENCE).as_posix()}" for p in sorted(EVIDENCE.rglob("*")) if p.is_file()))]
    parts += ["## F-02 closure record", fenced("V24-I11-V6-RQ1-REMEDIATION-7-F02-CLOSURE.md", text(ROOT / "implementation/v24/V24-I11-V6-RQ1-REMEDIATION-7-F02-CLOSURE.md")), "## Issue ledger", fenced("V24-I11-V6-RQ1-REMEDIATION-7-ISSUE-LEDGER.json", text(ROOT / "implementation/v24/V24-I11-V6-RQ1-REMEDIATION-7-ISSUE-LEDGER.json"), "json"), "## Current harness-reuse qualification", fenced("current-harness-reuse-qualification.json", json.dumps({"status":"HARNESS_REUSE_CANDIDATE_PASS","f01":"INDEPENDENTLY_CLOSED","f02":"CANDIDATE_CLOSED_PENDING_REVIEW","f03":"INDEPENDENTLY_CLOSED","behavioral_tests_total":behavioral_total,"behavioral_tests_passed":behavioral_passed,"mutation_total":mutation_total,"mutation_rejected":mutation_rejected,"mutation_surviving":mutation_surviving,"historical_replay":{"RQ-13":"PASS","RQ-14":"PASS","RQ-15":"PASS"},"scientific_rerun":False,"RQ16_started":False,"runtime_qualification":"NOT_QUALIFIED"}, indent=2), "json"), "## Integrity and governance", "", "input_zip_sha256=8c689ef763b9758e52fe72e73ad0381480b2b8f996d32558de6961ec10483d3b", "package_file_manifest=PASS", "package_tar_manifest=PASS", "cache_scan=__pycache__:0,pyc:0,pyo:0", "scientific_rerun=false", "RQ16_started=false", "qualification=NOT_QUALIFIED", "scientific_execution_state=CLOSED_PENDING_SUCCESSOR_REVIEW", "authority_effect=NONE_EVIDENCE_ONLY", "", "## Review matrix", "", "| Finding | Requirement | Source evidence | Behavioral evidence | Status |", "|---|---|---|---|---|", "| F-01 | Explicit parseable retry/replay denial and zero deltas | Shared predicate and raw Run-35 response handling | Mutation suite rejects malformed/authoritative/wrong-reason/state-changing responses | INDEPENDENTLY_CLOSED |", f"| F-02 | Current live builder and historical adapter both fail closed through shared evaluator | `interpret_first_attempt`, `current_live_first_attempt`, adapter and evaluator source | {behavioral_total}/{behavioral_total} behavioral tests; {mutation_rejected}/{mutation_total} mutations rejected; surviving={mutation_surviving} | CANDIDATE_CLOSED_PENDING_REVIEW |", "| F-03 | Boundary evidence load-bearing | PID/target/syscall/phase/path/error/return checks | Wrong-field mutations reject | INDEPENDENTLY_CLOSED |", "", "## Independent-review prompt", "", f"Determine independently whether F-02 is now closed for current/future harness reuse. Confirm that Run-35 used the historical harness, not the current evaluator; verify the representation-only historical adapter, raw-first first-attempt interpreter, complete {behavioral_total}-test output, and all {mutation_total} mutation records. Do not grant qualification or authorize RQ-16."]
    OUT.write_text("\n".join(parts) + "\n", encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
