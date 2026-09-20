"""Build the bounded EXP-M R2E external-review packet.

Stage content creates the packet payload committed as P.
Stage handoff runs after P and reports exact S/E/P without requiring a Git
commit to contain its own SHA.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / "experiments" / "governed-platform"
CONTENT_OUT = EXP / "EXP-M-R2E-PACKET-CONTENT.md"
HANDOFF_OUT = EXP / "EXP-M-DETERMINISTIC-IMPLEMENTATION-R2E-REVIEW.md"


def _git(*args: str) -> str:
    return subprocess.check_output(("git",) + args, cwd=ROOT, text=True).strip()


def _git_text(commit: str, path: str) -> str:
    return subprocess.check_output(("git", "show", f"{commit}:{path}"), cwd=ROOT, text=True)


def _tree(commit: str) -> str:
    return _git("rev-parse", f"{commit}^{{tree}}")


def _diff(a: str, b: str) -> list[str]:
    out = _git("diff", "--name-only", a, b)
    return [x for x in out.splitlines() if x]


def _read(path: Path) -> str:
    if not path.exists():
        raise SystemExit(f"packet_required_artifact_missing:{path.name}")
    return path.read_text(encoding="utf-8")


def _json(path: Path) -> dict:
    return json.loads(_read(path))


def build_content(source: str, evidence: str) -> str:
    freeze = _json(EXP / "EXP-M-SOURCE-FREEZE.json")
    evidence_manifest = _json(EXP / "EXP-M-R2E-EVIDENCE-MANIFEST.json")
    compound = _json(EXP / "EXP-M-R2E-COMPOUND-RESULTS.json")
    tests = _json(EXP / "EXP-M-TEST-RESULTS.json")
    mutations = _json(EXP / "EXP-M-MUTATION-RESULTS.json")
    self_fals = _json(EXP / "EXP-M-SELF-FALSIFICATION-RESULTS.json")
    prior = _read(EXP / "PRIOR-EVIDENCE-INDEX.md")
    protocol = _read(EXP / "EXP-M-R5-QUALIFICATION-PROTOCOL.json")
    authority_root = _read(EXP / "EXP-M-R2E-AUTHORITY-ROOT.json")

    if freeze.get("source_commit") != source or evidence_manifest.get("source_commit") != source:
        raise SystemExit("packet_source_identity_mismatch")
    if freeze.get("source_tree") != _tree(source) or evidence_manifest.get("source_tree") != _tree(source):
        raise SystemExit("packet_source_tree_mismatch")
    if not compound.get("all_rejected") or compound.get("survivor_count") != 0:
        raise SystemExit("packet_compound_survivor")
    if not self_fals.get("all_rejected"):
        raise SystemExit("packet_self_falsification_survivor")

    source_to_evidence = _diff(source, evidence)
    lines = [
        "# EXP-M Deterministic Implementation R2E — Packet Content",
        "",
        "## Bounded authority statement",
        "",
        "- EXP-M: NOT_QUALIFIED",
        "- Authority effect: NONE",
        "- Live provider/API execution: false",
        "- This packet covers deterministic/offline falsification only.",
        "",
        "## Identity",
        "",
        f"- S source commit: {source}",
        f"- S source tree: {_tree(source)}",
        f"- E evidence commit: {evidence}",
        f"- E evidence tree: {_tree(evidence)}",
        "- P packet-content commit: established by the first commit containing this file; "
        "the exact P SHA is reported in the post-P handoff document to avoid Git commit-hash self-reference.",
        "",
        "## S -> E changed paths",
        "",
        "~~~text",
        *source_to_evidence,
        "~~~",
        "",
        "## Fresh evidence summary",
        "",
        f"- Core tests: {tests.get('tests_passed')}/{tests.get('tests_total')} with all_passed={tests.get('all_passed')}",
        f"- Mutation closure: validator logic all killed={mutations.get('validator_logic_all_killed')}, "
        f"data/state all rejected={mutations.get('data_state_all_rejected')}, survivors={mutations.get('surviving_mutations')}",
        f"- Self-falsification total: {self_fals.get('total')}, all rejected={self_fals.get('all_rejected')}",
        f"- Reviewer compound attacks CA-1..CA-10: {compound.get('case_count')} executed, survivors={compound.get('survivor_count')}",
        "",
        "## Compound attack results",
        "",
        "~~~json",
        json.dumps(compound, indent=2, sort_keys=True),
        "~~~",
        "",
        "## Source freeze",
        "",
        "~~~json",
        json.dumps(freeze, indent=2, sort_keys=True),
        "~~~",
        "",
        "## Evidence manifest",
        "",
        "~~~json",
        json.dumps(evidence_manifest, indent=2, sort_keys=True),
        "~~~",
        "",
        "## Prior failure preservation index",
        "",
        prior.rstrip(),
        "",
        "## Frozen R5 protocol",
        "",
        "~~~json",
        protocol.rstrip(),
        "~~~",
        "",
        "## Authority root",
        "",
        "~~~json",
        authority_root.rstrip(),
        "~~~",
        "",
        "## Evidence artifact hashes",
        "",
    ]
    for item in evidence_manifest.get("artifacts") or []:
        lines.append(f"- {item.get('path')} — {item.get('sha256')}")
    lines += [
        "",
        "## External-review scope",
        "",
        "Treat all self-reported PASS values as claims. Attack the authority/source/evidence "
        "boundaries, verify S->E->P changed-path restrictions, verify prior-failure "
        "preservation, and independently confirm CA-1..CA-10.",
        "",
        "A PASS here cannot qualify EXP-M and cannot authorize live provider/API execution.",
        "",
    ]
    return "\n".join(lines)


def build_handoff(source: str, evidence: str, packet: str) -> str:
    content_path = "experiments/governed-platform/EXP-M-R2E-PACKET-CONTENT.md"
    embedded = _git_text(packet, content_path)
    e_to_p = _diff(evidence, packet)
    lines = [
        "# EXP-M Deterministic Implementation R2E — Independent Review Handoff",
        "",
        "## Exact S -> E -> P identity",
        "",
        f"- S: {source}",
        f"- S tree: {_tree(source)}",
        f"- E: {evidence}",
        f"- E tree: {_tree(evidence)}",
        f"- P: {packet}",
        f"- P tree: {_tree(packet)}",
        "",
        "The current handoff commit is a docs-only post-P identity attestation. P is "
        "the immutable packet-content commit; this avoids the impossible requirement "
        "for a Git commit to contain its own SHA.",
        "",
        "## E -> P changed paths",
        "",
        "~~~text",
        *e_to_p,
        "~~~",
        "",
        "## Authority boundary",
        "",
        "- EXP-M remains NOT_QUALIFIED.",
        "- Authority effect remains NONE.",
        "- No live provider/API execution occurred or is authorized.",
        "",
        "## Packet content frozen at P",
        "",
        embedded.rstrip(),
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=("content", "handoff"), required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--evidence", required=True)
    parser.add_argument("--packet")
    args = parser.parse_args()

    if args.stage == "content":
        CONTENT_OUT.write_text(build_content(args.source, args.evidence), encoding="utf-8")
        print(CONTENT_OUT.relative_to(ROOT))
    else:
        if not args.packet:
            raise SystemExit("--packet required for handoff")
        HANDOFF_OUT.write_text(build_handoff(args.source, args.evidence, args.packet), encoding="utf-8")
        print(HANDOFF_OUT.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
