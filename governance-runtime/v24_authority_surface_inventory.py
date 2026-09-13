from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

CANONICAL_SOURCE_REL = Path("governance-runtime/v24-authority-surface-source.json")


def git_blob_sha(raw: bytes) -> str:
    header = f"blob {len(raw)}\0".encode("utf-8")
    return hashlib.sha1(header + raw).hexdigest()


def _run_git(repo_root: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", "-C", str(repo_root), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def _commit_exists(repo_root: Path, commit: str) -> bool:
    if not isinstance(commit, str) or len(commit) != 40:
        return False
    proc = _run_git(repo_root, "cat-file", "-e", f"{commit}^{{commit}}")
    return proc.returncode == 0


def _bytes_at_commit(repo_root: Path, commit: str, path: str) -> bytes | None:
    proc = _run_git(repo_root, "show", f"{commit}:{path}")
    return proc.stdout if proc.returncode == 0 else None


def _canonical_source(repo_root: Path) -> dict[str, Any] | None:
    path = repo_root / CANONICAL_SOURCE_REL
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def _canonical_json_digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def build_inventory(repo_root: Path, source: dict[str, Any]) -> dict[str, Any]:
    problems: list[str] = []
    records: list[dict[str, Any]] = []
    canonical = _canonical_source(repo_root)
    if canonical is None:
        canonical = {}
        problems.append("AUTHORITY_SURFACE_CANONICAL_SOURCE_MISSING")
    elif _canonical_json_digest(source) != _canonical_json_digest(canonical):
        problems.append("AUTHORITY_SURFACE_SOURCE_NOT_CANONICAL")

    governed_source = canonical
    base_commit = governed_source.get("base_commit")
    if not _commit_exists(repo_root, str(base_commit or "")):
        problems.append("AUTHORITY_SURFACE_BASE_COMMIT_NOT_GOVERNED_GIT_OBJECT")

    surfaces = governed_source.get("surfaces")
    if not isinstance(surfaces, list) or not surfaces:
        surfaces = []
        problems.append("AUTHORITY_SURFACE_CANONICAL_UNIVERSE_REQUIRED")

    seen_ids: set[str] = set()
    seen_paths: set[str] = set()
    for surface in surfaces:
        if not isinstance(surface, dict):
            problems.append("SURFACE_DESCRIPTOR_MALFORMED")
            continue
        component_id = surface.get("component_id")
        path = surface.get("path")
        classes = surface.get("functional_classes")
        if not isinstance(component_id, str) or not component_id:
            problems.append("SURFACE_COMPONENT_ID_INVALID")
            continue
        if component_id in seen_ids:
            problems.append(f"SURFACE_COMPONENT_ID_DUPLICATE:{component_id}")
        seen_ids.add(component_id)
        if not isinstance(path, str) or not path or path.startswith("/") or ".." in Path(path).parts:
            problems.append(f"SURFACE_PATH_INVALID:{component_id}")
            continue
        if path in seen_paths:
            problems.append(f"SURFACE_PATH_DUPLICATE:{path}")
        seen_paths.add(path)
        if not isinstance(classes, list) or not classes or not all(isinstance(x, str) and x for x in classes):
            problems.append(f"SURFACE_FUNCTIONAL_CLASS_INVALID:{component_id}")

        raw = _bytes_at_commit(repo_root, str(base_commit), path) if _commit_exists(repo_root, str(base_commit or "")) else None
        if raw is None:
            problems.append(f"SURFACE_FILE_NOT_BOUND_AT_BASE_COMMIT:{component_id}:{path}")
            continue
        records.append(
            {
                "component_id": component_id,
                "path": path,
                "git_blob_sha": git_blob_sha(raw),
                "sha256": hashlib.sha256(raw).hexdigest(),
                "functional_classes": classes,
                "production_control_plane_evidence": governed_source.get("production_control_plane_evidence", "NOT_VERIFIED"),
                "bound_commit": base_commit,
            }
        )

    if len(records) != 14:
        problems.append(f"SURFACE_COUNT_MISMATCH:{len(records)}:14")
    problems = sorted(set(problems))
    return {
        "state": "AUTHORITY_SURFACE_INVENTORY_CONSTRUCTION_COMPLETE" if not problems else "AUTHORITY_SURFACE_INVENTORY_INVALID",
        "qualified": False,
        "base_commit": base_commit,
        "canonical_source_path": str(CANONICAL_SOURCE_REL),
        "canonical_source_digest": _canonical_json_digest(governed_source),
        "surface_count": len(records),
        "records": records,
        "problems": problems,
        "unresolved_production_evidence": [
            "CLOUD_OR_ORGANIZATION_ROOT_CONTROL",
            "DEPLOYMENT_AND_CI_CD_CONTROL",
            "SECRET_STORE_AND_KMS_HSM_CONTROL",
            "CREDENTIAL_RECOVERY_RESET_CONTROL",
            "DIRECT_DATABASE_STORE_OR_OFFLINE_ACCESS",
            "CACHE_REPLICA_AUTHORITY_INFLUENCE",
            "INDEPENDENT_RUNTIME_EFFECT_PATH_PROJECTION",
        ],
        "authority_effect": "NONE_EVIDENCE_ONLY",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default="..")
    parser.add_argument("--source", default="v24-authority-surface-source.json")
    parser.add_argument("--report")
    parser.add_argument("--expect-construction-complete", action="store_true")
    args = parser.parse_args()
    repo_root = Path(args.repo_root).resolve()
    source_path = Path(args.source)
    if not source_path.is_absolute():
        source_path = Path(__file__).resolve().parent / source_path
    source = json.loads(source_path.read_text())
    result = build_inventory(repo_root, source)
    rendered = json.dumps(result, sort_keys=True, indent=2)
    if args.report:
        Path(args.report).write_text(rendered + "\n")
    else:
        print(rendered)
    if args.expect_construction_complete:
        return 0 if result["state"] == "AUTHORITY_SURFACE_INVENTORY_CONSTRUCTION_COMPLETE" and result["surface_count"] == 14 and not result["problems"] and len(result["unresolved_production_evidence"]) == 7 else 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
