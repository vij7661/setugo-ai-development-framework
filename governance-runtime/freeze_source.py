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

SOURCE_PATHS = (
    "governance-runtime/exp_m_deterministic.py",
    "governance-runtime/exp_m_expectation_authority.py",
    "governance-runtime/exp_m_predicate_registry.py",
    "governance-runtime/exp_m_mutation_catalog.py",
    "governance-runtime/exp_m_review_fixtures.py",
    "governance-runtime/exp_m_test_fixtures.py",
    "governance-runtime/run_exp_m_deterministic.py",
    "governance-runtime/run_exp_m_mutations.py",
    "governance-runtime/run_exp_m_tests.py",
    "governance-runtime/self_falsify_exp_m.py",
    "governance-runtime/self_adjudicate_r2d.py",
    "governance-runtime/test_exp_m_deterministic.py",
    "governance-runtime/test_exp_m_phases.py",
    "governance-runtime/reviewer_exp_m_r2e_suite.py",
    "governance-runtime/reviewer_exp_m_r2e_authority_suite.py",
    "governance-runtime/reviewer_exp_m_r2e_compound_suite.py",
    "governance-runtime/run_reviewer_compound_attacks.py",
    "governance-runtime/build_prior_evidence_index.py",
    "governance-runtime/verify_exp_m_prior_evidence.py",
    "governance-runtime/verify_exp_m_sep_sequence.py",
    "governance-runtime/verify_sep_sequence.py",
    "governance-runtime/generate_evidence.py",
    "governance-runtime/build_exp_m_r2e_packet.py",
    ".github/workflows/exp-m-r2e-offline.yml",
    ".github/workflows/exp-m-r2e-sep.yml",
)


def _git(*args: str) -> str:
    return subprocess.check_output(("git",) + args, cwd=ROOT, text=True).strip()


def sha256_path(path: str) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def build() -> dict:
    dirty = _git("status", "--porcelain")
    if dirty:
        raise SystemExit("source_freeze_requires_clean_worktree")
    source_commit = _git("rev-parse", "HEAD")
    source_tree = _git("rev-parse", "HEAD^{tree}")
    missing = [path for path in SOURCE_PATHS if not (ROOT / path).is_file()]
    if missing:
        raise SystemExit("source_freeze_missing_files:" + ",".join(missing))
    return {
        "schema": "EXP-M-SOURCE-FREEZE/v1",
        "source_commit": source_commit,
        "source_tree": source_tree,
        "source_files": {path: sha256_path(path) for path in SOURCE_PATHS},
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
