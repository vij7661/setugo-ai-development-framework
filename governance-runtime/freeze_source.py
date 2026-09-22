"""Freeze the EXP-M deterministic source identity.

Run only from a clean source commit S. The generated JSON is evidence and is
therefore intentionally not part of S; it is committed later in E.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

from exp_m_expectation_authority import DEFAULT_AUTHORITY_COMMIT, ROOT_PATH as AUTHORITY_ROOT_PATH

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
    "experiments/governed-platform/EXP-M-R2E-EXTERNAL-REVIEW-R2.md",
    "experiments/governed-platform/EXP-M-R2E-REVIEW-R2-ADJUDICATION.md",
    "experiments/governed-platform/EXP-M-R2E-INTERNAL-ADJUDICATION-R3.md",
    "experiments/governed-platform/EXP-M-R2E-EXTERNAL-REVIEW-R3.md",
    "experiments/governed-platform/EXP-M-R2E-INTERNAL-ADJUDICATION-R4.md",
    "experiments/governed-platform/EXP-M-R2E-EXTERNAL-REVIEW-R5.md",
    "experiments/governed-platform/EXP-M-R2E-INTERNAL-ADJUDICATION-R6.md",
    "experiments/governed-platform/EXP-M-R2E-INTERNAL-ADJUDICATION-R7.md",
    "experiments/governed-platform/PRIOR-EVIDENCE-INDEX.md",
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


def _git_bytes(commit: str, path: str) -> bytes:
    return subprocess.check_output(("git", "show", f"{commit}:{path}"), cwd=ROOT)


def _authority_policies() -> tuple[dict, dict]:
    root = json.loads(_git_bytes(DEFAULT_AUTHORITY_COMMIT, AUTHORITY_ROOT_PATH))
    current = root.get("current_source_identity_policy") or {}
    delivery = root.get("delivery_binding_policy") or {}
    if root.get("root_id") != "EXP-M-R2E-AUTHORITY-ROOT-3":
        raise SystemExit("source_freeze_authority_root_invalid")
    if current.get("policy_id") != "CURRENT-SOURCE-FREEZE-V1":
        raise SystemExit("source_freeze_current_source_policy_invalid")
    if delivery.get("policy_id") != "SOURCE-FREEZE-DELIVERY-DERIVATION-V1":
        raise SystemExit("source_freeze_delivery_policy_invalid")
    return current, delivery


def delivery_binding(reviewed_commit: str, policy: dict) -> dict:
    request_id = str(policy["request_id"])
    items = {
        str(item_id): {"sha256": str(meta["sha256"]), "size": int(meta["size"])}
        for item_id, meta in sorted((policy.get("items") or {}).items())
    }
    body = {"request_id": request_id, "reviewed_commit": reviewed_commit, "items": items}
    return {
        "policy_id": str(policy["policy_id"]),
        "role": "DERIVED_BINDING_EVIDENCE",
        "authoritative": False,
        "request_id": request_id,
        "reviewed_commit": reviewed_commit,
        "items": items,
        "manifest_hash": hashlib.sha256(canonical_json(body)).hexdigest(),
    }


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
    current_policy, delivery_policy = _authority_policies()
    return {
        "schema": "EXP-M-SOURCE-FREEZE/v2",
        "source_commit": source_commit,
        "source_tree": source_tree,
        "source_files": {path: sha256_path(path) for path in paths},
        "authority_reference": {
            "root_commit": DEFAULT_AUTHORITY_COMMIT,
            "current_source_policy_id": str(current_policy["policy_id"]),
            "policy_id": str(current_policy["policy_id"]),
            "delivery_binding_policy_id": str(delivery_policy["policy_id"]),
            "semantics": "The preregistered root authorizes the derivation rule; this artifact records current-S binding evidence only and grants no authority.",
        },
        "delivery_binding": delivery_binding(source_commit, delivery_policy),
        "authority_effect": "NONE",
        "exp_m_state": "NOT_QUALIFIED",
        "live_provider_api_execution": False,
    }


def main() -> int:
    data = build()
    OUT.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(data, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
