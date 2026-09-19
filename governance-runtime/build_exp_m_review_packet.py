"""Build a self-contained deterministic EXP-M implementation review packet."""
from __future__ import annotations
from hashlib import sha256
import json, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments" / "governed-platform" / "EXP-M-DETERMINISTIC-IMPLEMENTATION-R1-REVIEW.md"
SOURCES = [
    Path("governance-runtime/exp_m_deterministic.py"),
    Path("governance-runtime/run_exp_m_deterministic.py"),
    Path("governance-runtime/run_exp_m_mutations.py"),
    Path("governance-runtime/self_falsify_exp_m.py"),
    Path("governance-runtime/test_exp_m_deterministic.py"),
    Path("governance-runtime/test_exp_m_phases.py"),
]


def sh(*args: str) -> str:
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def fence(name: str, body: str, lang: str = "text") -> str:
    return f"\n### {name}\n\n```{lang}\n{body.rstrip()}\n```\n"


def main() -> int:
    phase = json.loads((ROOT / "experiments/governed-platform/EXP-M-DETERMINISTIC-RESULTS.json").read_text())
    mutation = json.loads((ROOT / "experiments/governed-platform/EXP-M-MUTATION-RESULTS.json").read_text())
    falsify = json.loads((ROOT / "experiments/governed-platform/EXP-M-SELF-FALSIFICATION-RESULTS.json").read_text())
    hashes = {p.as_posix(): sha256((ROOT / p).read_bytes()).hexdigest() for p in SOURCES}
    frozen = {}
    for p in ["standards/review-evidence-delivery-integrity.md", "experiments/governed-platform/exp-m-review-evidence-delivery-integrity.md", "experiments/governed-platform/EXP-M-TEST-MATRIX.md", "governance-runtime/LIVE-CONVERSATION-GOVERNANCE.md", "experiments/governed-platform/EXP-M-R5-EXTERNAL-REVIEW.md"]:
        frozen[p] = sha256((ROOT / p).read_bytes()).hexdigest()
    lines = [
        "# EXP-M Deterministic Implementation and Falsification Review Packet",
        "",
        "This packet covers deterministic implementation only. EXP-M remains NOT_QUALIFIED; no live provider/API call occurred.",
        "",
        "## Historical superseded evidence",
        "The prior A-T/22-test/29-mutation report is retained in Git history but is superseded by the independent R1 CHANGES_REQUIRED review. It is not used as closure evidence.",
        "R1-C01..C11 and R1-H01..H10 are addressed by production validators, adversarial fixtures, and fresh mutation/self-falsification evidence below.",
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
        "| H-03/H-06/H-07/H-08 | source identity, egress/currentness, attempt ledger, bounded materialization | production validators and mutations |",
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
        "## Deterministic exit gates",
        f"all_phases_A_to_T_pass={phase['all_phases_pass']}",
        f"mutation_total={mutation['total_mutations']}",
        f"mutation_rejected={mutation['rejected_mutations']}",
        f"mutation_survivors={mutation['surviving_mutations']}",
        f"all_mutations_rejected={mutation['all_rejected']}",
        f"critical_self_falsification_survivors={falsify['surviving_critical']}",
        f"high_self_falsification_survivors={falsify.get('surviving_high', falsify['surviving_critical'])}",
        "",
        "## Frozen source-of-truth hashes",
        "```json", json.dumps(frozen, indent=2, sort_keys=True), "```",
        "",
        "## Implemented source hashes",
        "```json", json.dumps(hashes, indent=2, sort_keys=True), "```",
        "",
        "## Phase A-T results",
        "```json", json.dumps(phase, indent=2, sort_keys=True), "```",
        "",
        "## Mutation results",
        "```json", json.dumps(mutation, indent=2, sort_keys=True), "```",
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
