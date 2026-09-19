"""Build a self-contained deterministic EXP-M implementation review packet."""
from __future__ import annotations
from hashlib import sha256
import json, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments" / "governed-platform" / "EXP-M-DETERMINISTIC-IMPLEMENTATION-REVIEW.md"
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
