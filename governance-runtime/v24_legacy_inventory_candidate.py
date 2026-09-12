from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

from normative_control_catalog import _extract_clause

H2 = re.compile(r"^## (.+)$", re.MULTILINE)
BASE_COMMIT = "a0c780b516b83ff8a1d0cdfd3724545d7dd6668b"
BASE_TREE = "fafc42dcf7d2b234ef0219ccfbd9edc4d4541567"


def _run(repo_root: Path, *args: str) -> str:
    cp = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if cp.returncode != 0:
        raise RuntimeError(cp.stderr.strip() or cp.stdout.strip() or "git command failed")
    return cp.stdout


def _locator_id(path: str, heading: str) -> str:
    digest = hashlib.sha256(f"{path}\0{heading}".encode("utf-8")).hexdigest()[:24]
    return f"LEGACY-{digest}"


def derive_candidate_inventory(repo_root: Path) -> dict[str, Any]:
    actual_tree = _run(repo_root, "show", "-s", "--format=%T", BASE_COMMIT).strip()
    problems: list[str] = []
    if actual_tree != BASE_TREE:
        problems.append("V23_BASE_TREE_MISMATCH")

    raw = _run(repo_root, "ls-tree", "-r", "--full-tree", BASE_COMMIT, "standards")
    artifacts: list[dict[str, Any]] = []
    clauses: list[dict[str, Any]] = []
    current_drift: list[str] = []

    for line in raw.splitlines():
        if not line.strip():
            continue
        meta, path = line.split("\t", 1)
        mode, obj_type, blob_sha = meta.split(" ", 2)
        if obj_type != "blob" or not path.endswith(".md"):
            continue
        content = _run(repo_root, "show", f"{BASE_COMMIT}:{path}")
        headings = H2.findall(content)
        artifact = {
            "path": path,
            "blob_sha": blob_sha,
            "candidate_clause_count": len(headings),
            "classification_state": "PENDING_CLASSIFICATION",
        }
        if not headings:
            artifact["note"] = "NO_LEVEL2_HEADING_REQUIRES_MANUAL_CLASSIFICATION"
        artifacts.append(artifact)

        current_path = repo_root / path
        if current_path.is_file():
            current_blob = _run(repo_root, "hash-object", path).strip()
            if current_blob != blob_sha:
                current_drift.append(path)

        for heading_text in headings:
            heading = "## " + heading_text
            clause = _extract_clause(content, heading)
            if clause is None:
                problems.append(f"LEGACY_CLAUSE_UNREADABLE:{path}:{heading_text}")
                continue
            clauses.append(
                {
                    "artifact_path": path,
                    "artifact_blob_sha": blob_sha,
                    "locator_id": _locator_id(path, heading),
                    "heading": heading,
                    "clause_sha256": hashlib.sha256(clause.encode("utf-8")).hexdigest(),
                    "classification_state": "PENDING_CLASSIFICATION",
                    "target_control_id": None,
                }
            )

    if current_drift:
        problems.extend(f"LEGACY_ARTIFACT_CHANGED_AFTER_V23:{path}" for path in sorted(current_drift))
    if not artifacts:
        problems.append("LEGACY_ARTIFACT_INVENTORY_EMPTY")
    if not clauses:
        problems.append("LEGACY_CLAUSE_CANDIDATE_INVENTORY_EMPTY")

    return {
        "schema_version": 1,
        "artifact": "V24_LEGACY_NORMATIVE_CONTROL_CANDIDATE_INVENTORY",
        "state": "LEGACY_CLASSIFICATION_PENDING" if not problems else "LEGACY_INVENTORY_SOURCE_INVALID",
        "qualified": False,
        "v23_base_commit": BASE_COMMIT,
        "v23_base_tree": BASE_TREE,
        "artifact_count": len(artifacts),
        "candidate_clause_count": len(clauses),
        "artifacts_without_level2_headings": [x["path"] for x in artifacts if x.get("candidate_clause_count") == 0],
        "current_drift_paths": sorted(current_drift),
        "problems": sorted(set(problems)),
        "artifacts": artifacts,
        "legacy_clause_inventory": clauses,
        "authority_effect": "NONE_EVIDENCE_ONLY",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default="..")
    parser.add_argument("--report")
    parser.add_argument("--expect-pending", action="store_true")
    args = parser.parse_args()

    result = derive_candidate_inventory(Path(args.repo_root).resolve())
    rendered = json.dumps(result, sort_keys=True, indent=2, ensure_ascii=False)
    if args.report:
        Path(args.report).write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)

    if args.expect_pending:
        ok = (
            result["state"] == "LEGACY_CLASSIFICATION_PENDING"
            and result["qualified"] is False
            and result["artifact_count"] > 0
            and result["candidate_clause_count"] > 0
            and not result["problems"]
            and not result["current_drift_paths"]
        )
        return 0 if ok else 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
