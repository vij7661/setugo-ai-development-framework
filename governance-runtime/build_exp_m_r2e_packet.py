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
    if root.get("root_id") != "EXP-M-R2E-AUTHORITY-ROOT-3":
        raise SystemExit("authority_root_v3_required")
    if (root.get("delivery_binding_policy") or {}).get("policy_id") != "SOURCE-FREEZE-DELIVERY-DERIVATION-V1":
        raise SystemExit("authority_delivery_binding_policy_missing")
    specs = (
        ("authority_root", root_path, None),
        ("test_expectations", str(root["test_expectation_manifest_path"]), "test_expectation_manifest_sha256"),
        ("test_expectations_signature", str(root["test_expectation_signature_path"]), None),
        ("r5_protocol", str(root["r5_protocol_path"]), "r5_protocol_sha256"),
        ("retrieval_ledger", str(root["retrieval_source_ledger_path"]), "retrieval_source_ledger_sha256"),
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
    test_integrity = _json(EXP / "EXP-M-R2E-TEST-INTEGRITY-RESULTS.json")
    clarification_probes = _json(EXP / "EXP-M-R2E-CLARIFICATION-PROBES.json")
    tests = _json(EXP / "EXP-M-TEST-RESULTS.json")
    mutations = _json(EXP / "EXP-M-MUTATION-RESULTS.json")
    self_fals = _json(EXP / "EXP-M-SELF-FALSIFICATION-RESULTS.json")
    prior = _read(EXP / "PRIOR-EVIDENCE-INDEX.md")
    static_review_adjudication = _read(EXP / "EXP-M-R2E-STATIC-REVIEW-ADJUDICATION.md")
    external_review_r2 = _read(EXP / "EXP-M-R2E-EXTERNAL-REVIEW-R2.md")
    review_r2_adjudication = _read(EXP / "EXP-M-R2E-REVIEW-R2-ADJUDICATION.md")
    internal_adjudication_r3 = _read(EXP / "EXP-M-R2E-INTERNAL-ADJUDICATION-R3.md")
    authority_bundle = _authority_bundle(source)
    pinned_by_label = {row["label"]: row for row in authority_bundle["files"]}
    authority_root = str(pinned_by_label["authority_root"]["content"])
    protocol = str(pinned_by_label["r5_protocol"]["content"])
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
    if test_integrity.get("all_passed") is not True:
        raise SystemExit("packet_test_integrity_failure")
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
        f"- Falsification-test integrity gate: all_passed={test_integrity.get('all_passed')}, findings={len(test_integrity.get('findings') or [])}",
        "",
        "## Compound attack results",
        "",
        "~~~json",
        json.dumps(compound, indent=2, sort_keys=True),
        "~~~",
        "",
        "## Falsification-test integrity results",
        "",
        "~~~json",
        json.dumps(test_integrity, indent=2, sort_keys=True),
        "~~~",
        "",
        "## Full mutation results",
        "",
        "~~~json",
        json.dumps(mutations, indent=2, sort_keys=True),
        "~~~",
        "",
        "## Full self-falsification results",
        "",
        "~~~json",
        json.dumps(self_fals, indent=2, sort_keys=True),
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
        "## Static-review clarification probes",
        "",
        "~~~json",
        json.dumps(clarification_probes, indent=2, sort_keys=True),
        "~~~",
        "",
        "## Independent external review R2 (CHANGES_REQUIRED)",
        "",
        external_review_r2.rstrip(),
        "",
        "## Internal adversarial adjudication R3",
        "",
        internal_adjudication_r3.rstrip(),
        "",
        "## External review R2 remediation adjudication",
        "",
        review_r2_adjudication.rstrip(),
        "",
        "## Static-review clarification adjudication",
        "",
        static_review_adjudication.rstrip(),
        "",
        "## Static-review clarifications",
        "",
        "- CA-9: disposition_promotable is a blocking predicate identifier, not a positive status. In this attack the underlying predicates fail, the governor derives CHANGES_REQUIRED, and a caller-supplied PASS cannot override it; therefore disposition_promotable evaluates false.",
        "- CA-10: the authoritative mechanism suite instantiates a real AuthorityHandle input with protocol_available=false and passes it through production validate_capability; no test-only rejection shortcut is used. The frozen R5 protocol remains present and hash-bound in authority-root-v3.",
        "- Every result-producing governed command now emits the exact final result JSON on stdout. The v2 command capture separately records stdout/stderr, command-source SHA-256, result SHA-256/size at command exit, and S commit/tree; any stdout/result byte mismatch fails evidence generation. No later result post-processing is permitted.",
        "- Delivery authority is no longer substituted by the source freeze. Preregistered authority-root v2 freezes the current-S identity rule and delivery derivation policy; EXP-M-SOURCE-FREEZE.json records only non-authoritative derived binding evidence, which the authority loader and S-E-P verifier independently recompute.",
        "- Reproducibility evidence records Python, Git, runner image metadata, exact checkout guidance, and an import audit. The governed Python surface has no third-party Python dependencies; test commands are offline.",
        "- CA-7 and CA-8 are now exercised by the preregistered mechanism-integrity suite using synthetic Git commits that delete an indexed artifact or mutate a reviewer suite, then invoke the unmodified production verifier path. Legacy simulate_* cases are retained only as historical source and are not authoritative compound evidence.",
        "- A dedicated falsification-test integrity gate rejects simulate_/force_/mock_ shortcuts in the authoritative suite, requires each CA case to call its claimed production mechanism, and audits the self-falsification and mutation harness for shortcut patterns.",
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
        *[str(row.get("portable_command") or row.get("command")) for row in evidence_manifest.get("commands") or []],
        "~~~",
        "",
        "## Portable static-review bundle",
        "",
        "After Q is created and explicit S-E-P-Q verification succeeds, the governed workflow builds and uploads EXP-M-R2E-PORTABLE-REVIEW-BUNDLE.zip. The ZIP contains frozen source, all E artifacts, full mutation/self-falsification results, P, Q, the S-E-P-Q verification capture, pinned authority inputs, prior-history artifacts, an offline verifier, exact fetch/replay instructions, and a nested Git bundle carrying the referenced commit objects. BUNDLE-MANIFEST.json attests every other archive entry; only the manifest itself is excluded to avoid recursive self-hashing. The ZIP grants no authority.",
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
        "## Q identity publication",
        "",
        "Q cannot contain its own final commit SHA/tree without Git self-reference. After Q exists, "
        "the governed portable-bundle step independently verifies S->E->P->Q and creates "
        "FINAL-REVIEW-HANDOFF.md carrying the exact Q commit/tree plus the verification-capture hash. "
        "Reviewers should treat that post-Q file inside the portable bundle as the exact Q identity carrier.",
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
