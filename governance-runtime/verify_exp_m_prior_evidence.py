"""Verify the EXP-M prior-evidence index and deletion preservation."""
from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

from build_prior_evidence_index import ENTRIES

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "experiments" / "governed-platform" / "PRIOR-EVIDENCE-INDEX.md"


def _git(*args: str) -> str:
    return subprocess.check_output(("git",) + args, cwd=ROOT, text=True).strip()


def _git_bytes(commit: str, path: str) -> bytes:
    return subprocess.check_output(("git", "show", f"{commit}:{path}"), cwd=ROOT)


def _parse_index() -> dict[str, dict[str, str]]:
    if not INDEX.exists():
        return {}
    rows: dict[str, dict[str, str]] = {}
    for line in INDEX.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| ") or line.startswith("| ID ") or line.startswith("|---"):
            continue
        cells = [x.strip() for x in line.strip("|").split("|")]
        if len(cells) != 6:
            continue
        rows[cells[0]] = {
            "path": cells[1],
            "commit": cells[2],
            "sha256": cells[3],
            "claim": cells[4],
            "disposition": cells[5],
        }
    return rows


def verify_prior_evidence_index(
    *,
    source_commit: str | None = None,
    packet_commit: str | None = None,
    simulate_deleted_indexed_artifact: bool = False,
) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    rows = _parse_index()
    required = {entry["id"]: entry for entry in ENTRIES}
    if set(rows) != set(required):
        reasons.append("prior_evidence_index_incomplete")
    for evidence_id, entry in required.items():
        row = rows.get(evidence_id)
        if row is None:
            continue
        if row["path"] != entry["path"] or row["commit"] != entry["commit"]:
            reasons.append(f"prior_evidence_identity_mismatch:{evidence_id}")
            continue
        try:
            raw = _git_bytes(row["commit"], row["path"])
        except subprocess.CalledProcessError:
            reasons.append(f"indexed_prior_artifact_missing:{evidence_id}")
            continue
        if hashlib.sha256(raw).hexdigest() != row["sha256"]:
            reasons.append(f"prior_evidence_hash_mismatch:{evidence_id}")
    if simulate_deleted_indexed_artifact:
        reasons.append("indexed_prior_artifact_missing")
    if source_commit and packet_commit:
        deleted = _git("diff", "--diff-filter=D", "--name-only", source_commit, packet_commit).splitlines()
        indexed_paths = {entry["path"] for entry in ENTRIES}
        if indexed_paths.intersection(deleted):
            reasons.append("indexed_prior_artifact_deleted_after_source_freeze")
    return not reasons, tuple(dict.fromkeys(reasons))


def main() -> int:
    ok, reasons = verify_prior_evidence_index()
    print("PRIOR_EVIDENCE_INDEX_PASS" if ok else "PRIOR_EVIDENCE_INDEX_FAIL")
    for reason in reasons:
        print(reason)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
