"""Freeze the EXP-M deterministic source identity.

Run only from a clean source commit S. The generated JSON is evidence and is
therefore intentionally not part of S; it is committed later in E.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments" / "governed-platform" / "EXP-M-SOURCE-FREEZE.json"

EXPLICIT_SOURCE_PATHS = (
    "governance-runtime/freeze_source.py",
    "governance-runtime/generate_evidence.py",
    "governance-runtime/verify_sep_sequence.py",
    "governance-runtime/build_prior_evidence_index.py",
    "governance-runtime/run_reviewer_compound_attacks.py",
    "governance-runtime/self_adjudicate_r2d.py",
    ".github/workflows/exp-m-r2e-offline.yml",
    ".github/workflows/exp-m-r2e-sep.yml",
    "experiments/governed-platform/EXP-M-R2E-STATIC-REVIEW-ADJUDICATION.md",
)


def _git(*args: str) -> str:
    return subprocess.check_output(("git",) + args, cwd=ROOT, text=True).strip()


def sha256_path(path: str) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def source_paths() -> tuple[str, ...]:
    tracked = _git("ls-files", "governance-runtime").splitlines()
    dynamic = {
        path for path in tracked
        if path.endswith(".py") and "exp_m" in Path(path).name
    }
    return tuple(sorted(dynamic | set(EXPLICIT_SOURCE_PATHS)))


def canonical_json(value) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def delivery_manifest_hash(request_id: str, reviewed_commit: str, items: dict[str, bytes]) -> str:
    records = {
        key: {"sha256": hashlib.sha256(value).hexdigest(), "size": len(value)}
        for key, value in sorted(items.items())
    }
    body = {"request_id": request_id, "reviewed_commit": reviewed_commit, "items": records}
    return hashlib.sha256(canonical_json(body)).hexdigest()


def build() -> dict:
    raw_status = subprocess.check_output(
        ("git", "status", "--porcelain", "--untracked-files=all"), cwd=ROOT, text=True
    ).splitlines()
    dirty = []
    for line in raw_status:
        rel = line[3:].strip().replace("\\", "/")
        if " -> " in rel:
            rel = rel.split(" -> ", 1)[1]
        if "/__pycache__/" in f"/{rel}" or rel.endswith(".pyc"):
            continue
        dirty.append(rel)
    if dirty:
        raise SystemExit("source_freeze_requires_clean_worktree:" + ",".join(dirty))
    source_commit = _git("rev-parse", "HEAD")
    source_tree = _git("rev-parse", "HEAD^{tree}")
    paths = source_paths()
    missing = [path for path in paths if not (ROOT / path).is_file()]
    if missing:
        raise SystemExit("source_freeze_missing_files:" + ",".join(missing))
    frozen_items = {"a": b"a"}
    return {
        "schema": "EXP-M-SOURCE-FREEZE/v1",
        "source_commit": source_commit,
        "source_tree": source_tree,
        "source_files": {path: sha256_path(path) for path in paths},
        "delivery_authority": {
            "requests": {
                "r": {
                    "reviewed_commit": source_commit,
                    "manifest_hash": delivery_manifest_hash("r", source_commit, frozen_items),
                }
            }
        },
        "authority_effect": "NONE",
        "exp_m_state": "NOT_QUALIFIED",
        "live_provider_api_execution": False,
    }


def main() -> int:
    data = build()
    OUT.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(OUT.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
