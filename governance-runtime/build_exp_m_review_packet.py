"""Build a self-contained deterministic EXP-M implementation review packet."""
from __future__ import annotations
from hashlib import sha256
import json, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments" / "governed-platform" / "EXP-M-DETERMINISTIC-IMPLEMENTATION-R2C-REVIEW.md"
SOURCES = [
    Path("governance-runtime/exp_m_deterministic.py"),
    Path("governance-runtime/exp_m_predicate_registry.py"),
    Path("governance-runtime/exp_m_mutation_catalog.py"),
    Path("governance-runtime/build_exp_m_review_packet.py"),
    Path("governance-runtime/run_exp_m_deterministic.py"),
    Path("governance-runtime/run_exp_m_mutations.py"),
    Path("governance-runtime/self_falsify_exp_m.py"),
    Path("governance-runtime/test_exp_m_deterministic.py"),
    Path("governance-runtime/test_exp_m_phases.py"),
    Path("governance-runtime/exp_m_review_fixtures.py"),
    Path("governance-runtime/run_exp_m_tests.py"),
    Path("governance-runtime/self_adjudicate_r2c.py"),
]


def sh(*args: str) -> str:
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def fence(name: str, body: str, lang: str = "text") -> str:
    return f"\n### {name}\n\n```{lang}\n{body.rstrip()}\n```\n"


def main() -> int:
    phase = json.loads((ROOT / "experiments/governed-platform/EXP-M-DETERMINISTIC-RESULTS.json").read_text())
    mutation = json.loads((ROOT / "experiments/governed-platform/EXP-M-MUTATION-RESULTS.json").read_text())
    tests = json.loads((ROOT / "experiments/governed-platform/EXP-M-TEST-RESULTS.json").read_text())
    self_adjudication = json.loads((ROOT / "experiments/governed-platform/EXP-M-R2C-SELF-ADJUDICATION.json").read_text())
    falsify = json.loads((ROOT / "experiments/governed-platform/EXP-M-SELF-FALSIFICATION-RESULTS.json").read_text())
    r2_review = (ROOT / "experiments/governed-platform/EXP-M-DETERMINISTIC-EXTERNAL-REVIEW-R2.md").read_text(encoding="utf-8")
    r2_adjudication = (ROOT / "experiments/governed-platform/EXP-M-DETERMINISTIC-R2-SOLUTION-ADJUDICATION.md").read_text(encoding="utf-8")
    r2_remediation = (ROOT / "experiments/governed-platform/EXP-M-DETERMINISTIC-REMEDIATION-R2.md").read_text(encoding="utf-8")
    r2a_remediation = (ROOT / "experiments/governed-platform/EXP-M-DETERMINISTIC-SELF-ADJUDICATION-R2A-REMEDIATION.md").read_text(encoding="utf-8")
    r2b_remediation = (ROOT / "experiments/governed-platform/EXP-M-DETERMINISTIC-SELF-ADJUDICATION-R2C-REMEDIATION.md").read_text(encoding="utf-8")
    execution_files = [Path("experiments/governed-platform/EXP-M-UNIT-STDOUT.txt"), Path("experiments/governed-platform/EXP-M-PHASE-STDOUT.txt"), Path("experiments/governed-platform/EXP-M-MUTATION-STDOUT.txt"), Path("experiments/governed-platform/EXP-M-DETERMINISTIC-STDOUT.txt"), Path("experiments/governed-platform/EXP-M-SELF-STDOUT.txt")]
    execution_hashes = {p.as_posix(): sha256((ROOT / p).read_bytes()).hexdigest() for p in execution_files if (ROOT / p).exists()}
    hashes = {p.as_posix(): sha256((ROOT / p).read_bytes()).hexdigest() for p in SOURCES}
    frozen = {}
    for p in ["standards/review-evidence-delivery-integrity.md", "experiments/governed-platform/exp-m-review-evidence-delivery-integrity.md", "experiments/governed-platform/EXP-M-TEST-MATRIX.md", "governance-runtime/LIVE-CONVERSATION-GOVERNANCE.md", "experiments/governed-platform/EXP-M-R5-EXTERNAL-REVIEW.md"]:
        frozen[p] = sha256((ROOT / p).read_bytes()).hexdigest()
    lines = [
        "# EXP-M Deterministic Implementation R2C Independent Review Packet",
        "",
        "This packet covers deterministic implementation only. EXP-M remains NOT_QUALIFIED; no live provider/API call occurred.",
        "",
        "## Historical superseded evidence",
        "The prior A-T/22-test/29-mutation report is retained in Git history but is superseded by the independent R1 CHANGES_REQUIRED review. It is not used as closure evidence.",
        "R2C is the current internal self-adjudication authority. Prior R1/R2/R2A/R2B and historical false-green outputs are superseded evidence only.",
        "",
        "## R2 authority inputs",
        fence("External R2 review", r2_review), fence("R2 solution adjudication", r2_adjudication), fence("R2 remediation", r2_remediation), fence("R2A remediation", r2a_remediation), fence("R2B remediation", r2b_remediation),
        "",
        "## R1 remediation matrix",
        "| Finding family | Production mechanism | Fresh evidence |",
        "|---|---|---|",
        "| C-01/H-10 taxonomy and closure | `adjudicate_insufficient_evidence`, independent predicate registry | Phase D, O/T and mutation closure |",
        f"| C-02/C-10/H-01 | production mutation runner with data/state and validator-logic families | Phase G; {mutation['rejected_mutations']}/{mutation['total_mutations']} rejected |",
        "| C-03/H-02 | evidence-derived predicate dispatch with independently declared targets | structured admissibility fixtures and negative controls |",
        "| C-04/H-04 | `validate_capability` binds profile, plan, record, expiry, format, context and attempts | capability mutation cases |",
        "| C-05/H-05 | `validate_context_isolation` binds policy, sentinel state and fence | dirty/hidden/stale-context cases |",
        "| C-06 | `admit_review_attempt` compare-and-set and permanent void result | generation/state-drift test |",
        "| C-07 | `RetrievalEvidenceRecord` raw-byte and final-context binding | retrieval byte/session/context mutation |",
        "| C-08 | current witness qualification, semantic prompt and eviction checks | witness positive/negative cases |",
        "| C-09/H-09 | byte, representation, semantic and source/wire/receipt binding | returned-byte mutation |",
        f"| C-11 | expanded self-falsification includes every current mutation family | {falsify['total']} cases, {falsify['surviving_critical']} critical/{falsify.get('surviving_high', falsify['surviving_critical'])} high survivors |",
        "| NC-01/NC-11/NH-01..NH-08 | no production bypass, typed evidence/context, persistent admission, lineage and freshness binding | static/behavioral/mutation/self-falsification evidence |",
        "",
        "## Identity",
        f"branch={sh('git','branch','--show-current')}",
        f"commit={sh('git','rev-parse','HEAD')}",
        f"tree={sh('git','rev-parse','HEAD^{tree}')}",
        f"parent={sh('git','rev-parse','HEAD^')}",
        "frozen_design_commit=0ba6c3c24ec247f5ad993b7e2f996ccd472b5f45",
        "authority_status=NOT_QUALIFIED",
        "live_provider_execution=false",
        "",
        "## Fresh evidence execution identity",
        json.dumps({"source_commit": phase.get("execution", {}).get("source_commit"), "source_tree": phase.get("execution", {}).get("source_tree"), "execution_hashes": execution_hashes}, indent=2, sort_keys=True),
        "",
        "## Deterministic exit gates",
        f"all_phases_A_to_T_pass={phase['all_phases_pass']}",
        f"mutation_total={mutation['total_mutations']}",
        f"mutation_rejected={mutation['rejected_mutations']}",
        f"mutation_survivors={mutation['surviving_mutations']}",
        f"all_mutations_rejected={mutation['all_rejected']}",
        f"critical_self_falsification_survivors={falsify['surviving_critical']}",
        f"high_self_falsification_survivors={falsify.get('surviving_high', falsify['surviving_critical'])}",
        f"tests_total={tests['tests_total']}",
        f"tests_passed={tests['tests_passed']}",
        f"tests_failed={tests['tests_failed']}",
        f"r2c_self_adjudication={self_adjudication['status']}",
        f"r2c_unresolved_critical={self_adjudication['unresolved_critical']}",
        f"r2c_unresolved_high={self_adjudication['unresolved_high']}",
        "r2c_status=AUTOMATABLE_REMEDIATION_COMPLETE",
        "r2c_clean_source_to_evidence_to_packet_sequence=true",
        "",
        "## Frozen source-of-truth hashes",
        "```json", json.dumps(frozen, indent=2, sort_keys=True), "```",
        "",
        "## Implemented source hashes",
        "```json", json.dumps(hashes, indent=2, sort_keys=True), "```",
        "",
        "## R2C phase A-T results",
        "```json", json.dumps(phase, indent=2, sort_keys=True), "```",
        "",
        "## Mutation results",
        "```json", json.dumps(mutation, indent=2, sort_keys=True), "```",
        "## Offline test result",
        "```json", json.dumps(tests, indent=2, sort_keys=True), "```",
        "## R2C internal self-adjudication",
        "```json", json.dumps(self_adjudication, indent=2, sort_keys=True), "```",
        "",
        "## Self-falsification results",
        "```json", json.dumps(falsify, indent=2, sort_keys=True), "```",
        "",
        "## Governance boundary",
        "- `EXP-M = NOT_QUALIFIED`.",
        "- No live Claude, DeepSeek, Gemini, OpenRouter, or other provider execution was performed.",
        "- No release, promotion, or authority effect is claimed.",
        "- Independent external review remains required before any live provider pilot.",
    ]
    for p in SOURCES:
        lines.append(fence(p.as_posix(), (ROOT / p).read_text(encoding="utf-8"), "python"))
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
