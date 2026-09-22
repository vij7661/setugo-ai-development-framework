"""Build EXP-M prior-failure preservation index from pinned Git objects."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments" / "governed-platform" / "PRIOR-EVIDENCE-INDEX.md"

ENTRIES = (
    {
        "id": "HIST-22-TEST",
        "path": "governance-runtime/test_exp_m_deterministic.py",
        "commit": "1e954c7c584c01086456af6434cde05e3336df63",
        "claim": "22 test methods in original deterministic suite",
        "disposition": "SUPERSEDED_FALSE_GREEN",
        "kind": "test_count",
        "expected": 22,
    },
    {
        "id": "HIST-29-MUTATION",
        "path": "experiments/governed-platform/EXP-M-MUTATION-RESULTS.json",
        "commit": "1e954c7c584c01086456af6434cde05e3336df63",
        "claim": "29/29 mutations reported rejected",
        "disposition": "SUPERSEDED_FALSE_GREEN",
        "kind": "mutation_count",
        "expected": 29,
    },
    {
        "id": "R1-34-TEST",
        "path": "governance-runtime/test_exp_m_deterministic.py",
        "commit": "66129025f9b5211a551f191c4367713e78ef14c4",
        "claim": "34 test methods in R1 remediation suite",
        "disposition": "SUPERSEDED_BY_R1_CHANGES_REQUIRED",
        "kind": "test_count",
        "expected": 34,
    },
    {
        "id": "R1-46-MUTATION",
        "path": "experiments/governed-platform/EXP-M-MUTATION-RESULTS.json",
        "commit": "66129025f9b5211a551f191c4367713e78ef14c4",
        "claim": "46/46 mutations reported rejected",
        "disposition": "SUPERSEDED_BY_R1_CHANGES_REQUIRED",
        "kind": "mutation_count",
        "expected": 46,
    },
    {
        "id": "R1-REVIEW",
        "path": "experiments/governed-platform/EXP-M-DETERMINISTIC-EXTERNAL-REVIEW-R1.md",
        "commit": "8e23ba2b9359c1f3040b6260e23c91b46309cf2e",
        "claim": "Independent R1 implementation review",
        "disposition": "CHANGES_REQUIRED",
        "kind": "text",
    },
    {
        "id": "R2-REVIEW",
        "path": "experiments/governed-platform/EXP-M-R2-EXTERNAL-REVIEW.md",
        "commit": "f0df30118d37b5bcbbdd5cb61380b7e3c7c429f1",
        "claim": "Independent R2 review",
        "disposition": "CHANGES_REQUIRED",
        "kind": "text",
    },
    {
        "id": "R2E-STATIC-REVIEW-R1",
        "path": "experiments/governed-platform/EXP-M-R2E-EXTERNAL-STATIC-REVIEW-R1.md",
        "commit": "2d01e38a5e7b2bb3e181cc3fdd7b46d7bf261bd6",
        "claim": "Independent R2E static review after first clarified handoff",
        "disposition": "CLARIFICATIONS_REQUIRED",
        "kind": "text",
    },
    {
        "id": "R2A-REMEDIATION",
        "path": "experiments/governed-platform/EXP-M-DETERMINISTIC-SELF-ADJUDICATION-R2A-REMEDIATION.md",
        "commit": "e40fa99043cfba081b71e430e4e981c410314bf8",
        "claim": "R2A internal remediation/adjudication record",
        "disposition": "SUPERSEDED_INTERNAL_EVIDENCE",
        "kind": "text",
    },
    {
        "id": "R2B-REMEDIATION",
        "path": "experiments/governed-platform/EXP-M-DETERMINISTIC-SELF-ADJUDICATION-R2B-REMEDIATION.md",
        "commit": "0bb7bc6bcde7d36c89fd017b6d05d0c99529108b",
        "claim": "R2B internal remediation/adjudication record",
        "disposition": "SUPERSEDED_INTERNAL_EVIDENCE",
        "kind": "text",
    },
    {
        "id": "R2C-REMEDIATION",
        "path": "experiments/governed-platform/EXP-M-DETERMINISTIC-SELF-ADJUDICATION-R2C-REMEDIATION.md",
        "commit": "b873291ee6ecb982c2fac213ab819c89f34e7890",
        "claim": "R2C internal remediation/adjudication record",
        "disposition": "SUPERSEDED_INTERNAL_EVIDENCE",
        "kind": "text",
    },
)


def git_bytes(commit: str, path: str) -> bytes:
    return subprocess.check_output(("git", "show", f"{commit}:{path}"), cwd=ROOT)


def validate_claim(entry: dict, raw: bytes) -> None:
    if entry["kind"] == "test_count":
        count = raw.decode("utf-8", errors="replace").count("def test_")
        if count != entry["expected"]:
            raise SystemExit(f"{entry['id']}: expected {entry['expected']} tests, got {count}")
    elif entry["kind"] == "mutation_count":
        data = json.loads(raw)
        if data.get("total_mutations") != entry["expected"] or data.get("rejected_mutations") != entry["expected"]:
            raise SystemExit(f"{entry['id']}: mutation-count claim mismatch")


def build() -> str:
    rows = []
    for entry in ENTRIES:
        raw = git_bytes(entry["commit"], entry["path"])
        validate_claim(entry, raw)
        rows.append(
            (
                entry["id"],
                entry["path"],
                entry["commit"],
                hashlib.sha256(raw).hexdigest(),
                entry["claim"],
                entry["disposition"],
            )
        )
    lines = [
        "# EXP-M Prior Evidence Index",
        "",
        "This index preserves superseded and failed EXP-M deterministic evidence. "
        "It is historical evidence only; it grants no qualification or runtime authority.",
        "",
        "| ID | Artifact | Pinned commit | SHA-256 at pinned commit | Historical claim | Disposition |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    lines += [
        "",
        "All hashes are recomputed from the pinned Git object by governance-runtime/build_prior_evidence_index.py.",
        "",
        "Authority effect: NONE.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    OUT.write_text(build(), encoding="utf-8")
    print(OUT.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
