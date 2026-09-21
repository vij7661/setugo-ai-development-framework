"""Build the bounded EXP-M R2E external-review packet.

Stage content creates the packet payload committed as P.
Stage handoff runs after P and reports exact S/E/P without requiring a Git
commit to contain its own SHA.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
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


def _git_bytes(commit: str, path: str) -> bytes:
    return subprocess.check_output(("git", "show", f"{commit}:{path}"), cwd=ROOT)


def _blob(commit: str, path: str) -> str:
    return _git("rev-parse", f"{commit}:{path}")


def _sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _authority_bundle(source: str) -> dict:
    authority_source = _git_text(source, "governance-runtime/exp_m_expectation_authority.py")
    match = re.search(r'DEFAULT_AUTHORITY_COMMIT\s*=\s*"([0-9a-f]{40})"', authority_source)
    if not match:
        raise SystemExit("authority_commit_not_resolved_from_source")
    authority_commit = match.group(1)
    root_path = "experiments/governed-platform/EXP-M-R2E-AUTHORITY-ROOT.json"
    root_raw = _git_bytes(authority_commit, root_path)
    root = json.loads(root_raw)
    specs = (
        ("authority_root", root_path, None),
        ("test_expectations", str(root["test_expectation_manifest_path"]), "test_expectation_manifest_sha256"),
        ("test_expectations_signature", str(root["test_expectation_signature_path"]), None),
        ("r5_protocol", str(root["r5_protocol_path"]), "r5_protocol_sha256"),
        ("retrieval_ledger", str(root["retrieval_source_ledger_path"]), "retrieval_source_ledger_sha256"),
        ("delivery_ledger", str(root["delivery_ledger_path"]), "delivery_ledger_sha256"),
        ("qualification_ledger", str(root["qualification_ledger_path"]), "qualification_ledger_sha256"),
    )
    files = []
    for label, file_path, declared_key in specs:
        raw = _git_bytes(authority_commit, file_path)
        actual = _sha256_bytes(raw)
        declared = root.get(declared_key) if declared_key else None
        if declared is not None and actual != declared:
            raise SystemExit(f"authority_input_hash_mismatch:{label}")
        files.append({
            "label": label,
            "path": file_path,
            "git_blob": _blob(authority_commit, file_path),
            "sha256": actual,
            "declared_sha256": declared,
            "content": raw.decode("utf-8", errors="replace"),
        })
    retrieval_ledger = json.loads(next(x["content"] for x in files if x["label"] == "retrieval_ledger"))
    backing = []
    for source_id, entry in sorted((retrieval_ledger.get("sources") or {}).items()):
        raw = _git_bytes(authority_commit, str(entry["path"]))
        actual = _sha256_bytes(raw)
        if actual != str(entry["sha256"]) or len(raw) != int(entry["length"]):
            raise SystemExit(f"authority_retrieval_backing_mismatch:{source_id}")
        backing.append({
            "source_id": source_id,
            "path": str(entry["path"]),
            "sha256": actual,
            "size": len(raw),
            "content_hex": raw.hex(),
        })
    return {
        "authority_commit": authority_commit,
        "authority_tree": _tree(authority_commit),
        "root_sha256": _sha256_bytes(root_raw),
        "files": files,
        "retrieval_backing_sources": backing,
        "note": "Authority inputs are pinned by the preregistered authority commit and consumed by source S. They are not generated E evidence.",
    }


def _manifest_attestation(evidence: str) -> dict:
    path = "experiments/governed-platform/EXP-M-R2E-EVIDENCE-MANIFEST.json"
    raw = _git_bytes(evidence, path)
    return {
        "path": path,
        "git_blob": _blob(evidence, path),
        "sha256": _sha256_bytes(raw),
        "size": len(raw),
        "attestation_stage": "P",
        "reason_not_self_listed": "The manifest cannot safely contain its own final cryptographic hash without self-reference. P independently attests the exact manifest bytes stored at E.",
    }


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
    authority_bundle = _authority_bundle(source)
    manifest_attestation = _manifest_attestation(evidence)

    ca9 = next((row for row in compound.get("cases") or [] if row.get("id") == "CA-9"), {})
    ca10 = next((row for row in compound.get("cases") or [] if row.get("id") == "CA-10"), {})
    if "guard_semantics" not in ca9:
        raise SystemExit("packet_ca9_semantics_missing")
    if "fault_injection" not in ca10:
        raise SystemExit("packet_ca10_fault_injection_missing")

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
        f"- Evidence manifest SHA-256 at E: {manifest_attestation['sha256']}",
        f"- Evidence manifest Git blob at E: {manifest_attestation['git_blob']}",
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
        "The evidence manifest intentionally does not list itself as an artifact because that would create self-hash recursion. The immutable P packet independently attests the exact manifest bytes stored at E.",
        "",
        "~~~json",
        json.dumps(evidence_manifest, indent=2, sort_keys=True),
        "~~~",
        "",
        "## Evidence manifest post-generation attestation",
        "",
        "~~~json",
        json.dumps(manifest_attestation, indent=2, sort_keys=True),
        "~~~",
        "",
        "## Static-review clarifications",
        "",
        "- CA-9: disposition_promotable is a blocking predicate identifier, not a positive status. In this attack the underlying predicates fail, the governor derives CHANGES_REQUIRED, and a caller-supplied PASS cannot override it; therefore disposition_promotable evaluates false.",
        "- CA-10: r5_protocol_unavailable is deliberately fault-injected by AuthorityHandle.with_missing_r5_protocol_for_test() for that negative case only. The frozen R5 protocol remains present and hash-bound in the real authority root.",
        "- Duplicate JSON/STDOUT hashes are expected when a runner prints the same serialized JSON it writes to its result file. Such STDOUT is retained as command-console capture and is explicitly not independent evidence; the manifest records this relationship.",
        "- Authority inputs are not generated E artifacts. They are pinned by the preregistered authority commit used by source S and are embedded below with recomputed hashes and Git blob identities for static inspection.",
        "- Reproducibility evidence records Python, Git, runner image metadata, exact checkout guidance, and an import audit. The governed Python surface has no third-party Python dependencies; test commands are offline.",
        "- Prior-failure preservation is checked by a dedicated evidence command in E and the full index remains embedded below. Independent historical recomputation still requires the pinned Git objects; that is an inherent limit of static-only review, not an authority grant.",
        "",
        "## Reproducibility environment and checkout",
        "",
        "~~~json",
        json.dumps(evidence_manifest.get("reproducibility") or {}, indent=2, sort_keys=True),
        "~~~",
        "",
        "Exact re-execution sequence from a repository clone:",
        "",
        "~~~text",
        "git fetch --all --tags --prune",
        f"git checkout --detach {source}",
        "git status --porcelain",
        *[str(row.get("command")) for row in evidence_manifest.get("commands") or []],
        "~~~",
        "",
        "## Pinned authority input bundle",
        "",
        "~~~json",
        json.dumps(authority_bundle, indent=2, sort_keys=True),
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
