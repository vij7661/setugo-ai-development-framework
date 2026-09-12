from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any

from v24_legacy_inventory_candidate import derive_candidate_inventory

BASE_COMMIT = "a0c780b516b83ff8a1d0cdfd3724545d7dd6668b"
V7_MAP_PATH = "standards/conversation-drift-parent-child-v7-active-clause-map.md"
V7_MAP_BLOB = "7800ce565b87f77efe736bf58e8e184d3d4dd88d"
V5_PATH = "standards/conversation-drift-parent-child-impact-control.md"
V6_PATH = "standards/conversation-drift-parent-child-impact-control-v6-hardening.md"
V7_PATH = "standards/conversation-drift-parent-child-impact-control-v7-hardening.md"

SECTION_HEADING = re.compile(r"^## (\d+)\.\s")
MAP_ROW = re.compile(r"^\| §(\d+)(?: [^|]*)? \| ([A-Z0-9_]+) \|", re.MULTILINE)


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


def _git_blob(repo_root: Path, commit: str, path: str) -> str:
    line = _run(repo_root, "ls-tree", commit, path).strip()
    if not line:
        raise RuntimeError(f"path not found at commit: {path}")
    meta, returned = line.split("\t", 1)
    if returned != path:
        raise RuntimeError(f"unexpected ls-tree path: {returned}")
    _, obj_type, sha = meta.split(" ", 2)
    if obj_type != "blob":
        raise RuntimeError(f"not a blob: {path}")
    return sha


def _section_number(heading: str) -> int | None:
    match = SECTION_HEADING.match(heading)
    return int(match.group(1)) if match else None


def _target(locator_id: str) -> str:
    return "INHERITED-" + locator_id


def classify_v5_v7(repo_root: Path) -> dict[str, Any]:
    candidate = derive_candidate_inventory(repo_root)
    problems = list(candidate.get("problems", []))

    actual_map_blob = _git_blob(repo_root, BASE_COMMIT, V7_MAP_PATH)
    if actual_map_blob != V7_MAP_BLOB:
        problems.append("V7_MAP_BLOB_MISMATCH")
    map_text = _run(repo_root, "show", f"{BASE_COMMIT}:{V7_MAP_PATH}")

    # The V7 map has two explicit tables. Split around the H2 markers so rows cannot
    # accidentally bleed from one source artifact into the other.
    try:
        v5_block = map_text.split("## V5 standard mapping", 1)[1].split("## V6 hardening mapping", 1)[0]
        v6_block = map_text.split("## V6 hardening mapping", 1)[1].split("## V7 hardening mapping", 1)[0]
    except IndexError:
        v5_block = v6_block = ""
        problems.append("V7_MAP_REQUIRED_SECTIONS_MISSING")

    v5_status = {int(num): status for num, status in MAP_ROW.findall(v5_block)}
    v6_status = {int(num): status for num, status in MAP_ROW.findall(v6_block)}
    if set(v5_status) != set(range(1, 25)):
        problems.append("V7_MAP_V5_SECTION_SET_MISMATCH")
    if set(v6_status) != set(range(1, 22)):
        problems.append("V7_MAP_V6_SECTION_SET_MISMATCH")

    records: list[dict[str, Any]] = []
    classified_keys: set[tuple[str, str]] = set()

    for item in candidate.get("legacy_clause_inventory", []):
        path = item["artifact_path"]
        locator_id = item["locator_id"]
        key = (path, locator_id)
        heading = item["heading"]
        classification: str | None = None
        source_status: str | None = None
        evidence = None

        if path == V5_PATH:
            number = _section_number(heading)
            if number in v5_status:
                source_status = v5_status[number]
                evidence = {"artifact_path": V7_MAP_PATH, "blob_sha": V7_MAP_BLOB, "section": "V5 standard mapping", "source_section": number}
        elif path == V6_PATH:
            number = _section_number(heading)
            if number in v6_status:
                source_status = v6_status[number]
                evidence = {"artifact_path": V7_MAP_PATH, "blob_sha": V7_MAP_BLOB, "section": "V6 hardening mapping", "source_section": number}
        elif path == V7_PATH:
            number = _section_number(heading)
            if number is not None and 1 <= number <= 20:
                source_status = "ACTIVE_UNCHANGED"
                evidence = {"artifact_path": V7_MAP_PATH, "blob_sha": V7_MAP_BLOB, "section": "V7 hardening mapping", "statement": "All normative V7 sections §1–§20 are ACTIVE_UNCHANGED"}
        elif path == V7_MAP_PATH:
            # V8-M02 includes the exact V7 active-clause map in the composite source
            # set and says it resolves V5/V6/V7 precedence. Treat its four H2 clauses
            # as still-active composite interpretation controls at the V7->V8 boundary.
            source_status = "ACTIVE_UNCHANGED"
            evidence = {"artifact_path": "standards/conversation-drift-parent-child-v8-precedence-and-evidence-map.md", "blob_sha": "188ae90b3ace17ef4293c5408d46065e127d3c51", "section": "V8-M02", "statement": "V7 active-clause map resolves V5/V6/V7 precedence"}

        if source_status is not None:
            if source_status.startswith("ACTIVE_"):
                classification = "ACTIVE_MAPPED"
            elif source_status == "SUPERSEDED":
                classification = "SUPERSEDED"
            elif source_status == "REFERENCE_ONLY":
                classification = "REFERENCE_ONLY"
            else:
                problems.append(f"UNSUPPORTED_V7_MAP_STATUS:{path}:{locator_id}:{source_status}")
                continue

            record = {
                "artifact_path": path,
                "locator_id": locator_id,
                "status": classification,
                "target_control_id": _target(locator_id) if classification == "ACTIVE_MAPPED" else None,
                "source_status": source_status,
                "classification_evidence": evidence,
            }
            records.append(record)
            classified_keys.add(key)

    expected_by_path = {V5_PATH: 24, V6_PATH: 21, V7_PATH: 20, V7_MAP_PATH: 4}
    counts_by_path = {path: 0 for path in expected_by_path}
    for record in records:
        if record["artifact_path"] in counts_by_path:
            counts_by_path[record["artifact_path"]] += 1
    for path, expected in expected_by_path.items():
        if counts_by_path[path] != expected:
            problems.append(f"V7_CLASSIFIED_COUNT_MISMATCH:{path}:{counts_by_path[path]}:{expected}")

    active = [r for r in records if r["status"] == "ACTIVE_MAPPED"]
    superseded = [r for r in records if r["status"] == "SUPERSEDED"]
    reference = [r for r in records if r["status"] == "REFERENCE_ONLY"]
    unresolved = [
        item for item in candidate.get("legacy_clause_inventory", [])
        if (item["artifact_path"], item["locator_id"]) not in classified_keys
    ]

    if len(records) != 69:
        problems.append(f"V7_TOTAL_CLASSIFIED_COUNT_MISMATCH:{len(records)}:69")
    if len(active) != 67:
        problems.append(f"V7_ACTIVE_COUNT_MISMATCH:{len(active)}:67")
    if len(superseded) != 1:
        problems.append(f"V7_SUPERSEDED_COUNT_MISMATCH:{len(superseded)}:1")
    if len(reference) != 1:
        problems.append(f"V7_REFERENCE_COUNT_MISMATCH:{len(reference)}:1")

    return {
        "schema_version": 1,
        "artifact": "V24_LEGACY_V5_V7_CLASSIFICATION",
        "state": "V5_V7_CLASSIFICATION_BOUNDED_PASS" if not problems else "V5_V7_CLASSIFICATION_INVALID",
        "qualified": False,
        "base_commit": BASE_COMMIT,
        "evidence_map": {"path": V7_MAP_PATH, "blob_sha": V7_MAP_BLOB},
        "classified_count": len(records),
        "active_mapped_count": len(active),
        "superseded_count": len(superseded),
        "reference_only_count": len(reference),
        "unresolved_legacy_count": len(unresolved),
        "records": records,
        "problems": sorted(set(problems)),
        "authority_effect": "NONE_EVIDENCE_ONLY",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default="..")
    parser.add_argument("--report")
    parser.add_argument("--expect-bounded-pass", action="store_true")
    args = parser.parse_args()
    result = classify_v5_v7(Path(args.repo_root).resolve())
    rendered = json.dumps(result, sort_keys=True, indent=2, ensure_ascii=False)
    if args.report:
        Path(args.report).write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    if args.expect_bounded_pass:
        ok = (
            result["state"] == "V5_V7_CLASSIFICATION_BOUNDED_PASS"
            and result["classified_count"] == 69
            and result["active_mapped_count"] == 67
            and result["superseded_count"] == 1
            and result["reference_only_count"] == 1
            and result["unresolved_legacy_count"] == 466
            and not result["problems"]
        )
        return 0 if ok else 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
