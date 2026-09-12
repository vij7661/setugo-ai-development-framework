from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def git_blob_sha(raw: bytes) -> str:
    header = f"blob {len(raw)}\0".encode("utf-8")
    return hashlib.sha1(header + raw).hexdigest()


def build_inventory(repo_root: Path, source: dict[str, Any]) -> dict[str, Any]:
    problems: list[str] = []
    records: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    seen_paths: set[str] = set()
    for surface in source.get("surfaces", []):
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
        full = repo_root / path
        if not full.is_file():
            problems.append(f"SURFACE_FILE_MISSING:{component_id}:{path}")
            continue
        raw = full.read_bytes()
        records.append(
            {
                "component_id": component_id,
                "path": path,
                "git_blob_sha": git_blob_sha(raw),
                "sha256": hashlib.sha256(raw).hexdigest(),
                "functional_classes": classes,
                "production_control_plane_evidence": source.get("production_control_plane_evidence", "NOT_VERIFIED"),
            }
        )
    if len(records) != 14:
        problems.append(f"SURFACE_COUNT_MISMATCH:{len(records)}:14")
    problems = sorted(set(problems))
    return {
        "state": "AUTHORITY_SURFACE_INVENTORY_CONSTRUCTION_COMPLETE" if not problems else "AUTHORITY_SURFACE_INVENTORY_INVALID",
        "qualified": False,
        "base_commit": source.get("base_commit"),
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
    source_path = Path(args.source)
    if not source_path.is_absolute():
        source_path = Path(__file__).resolve().parent / source_path
    result = build_inventory(Path(args.repo_root).resolve(), json.loads(source_path.read_text()))
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
