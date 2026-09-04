"""Freeze externally stored Pilot #1 ground truth without copying it into Git.

Usage example:
  python freeze_truth.py --truth-dir /secure/pilot-1/truth --out /secure/pilot-1/truth-manifest.json

The truth directory and output manifest must both resolve outside this repository.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Iterable


REQUIRED_CASE_IDS = {
    "EXP-A-001",
    "EXP-B-001",
    "EXP-B-002",
    "EXP-B-003",
    "EXP-C-001",
    "EXP-C-002",
    "EXP-C-003",
    "EXP-C-004",
    "EXP-C-005",
    "EXP-C-006",
    "EXP-C-007",
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def assert_outside_repo(path: Path) -> Path:
    resolved = path.expanduser().resolve()
    root = repo_root()
    try:
        resolved.relative_to(root)
    except ValueError:
        return resolved
    raise ValueError(f"protected truth path must be outside repository: {resolved}")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_truth_record(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    required = {"case_id", "case_version", "truth_version", "defects", "clean_control"}
    missing = sorted(required - data.keys())
    if missing:
        raise ValueError(f"{path.name}: missing required fields {missing}")
    if not isinstance(data["defects"], list):
        raise ValueError(f"{path.name}: defects must be a list")
    if not isinstance(data["clean_control"], bool):
        raise ValueError(f"{path.name}: clean_control must be boolean")
    return data


def build_manifest(truth_dir: Path, required_case_ids: Iterable[str] = REQUIRED_CASE_IDS) -> dict:
    truth_dir = assert_outside_repo(truth_dir)
    if not truth_dir.is_dir():
        raise ValueError(f"truth directory does not exist: {truth_dir}")

    records = {}
    for path in sorted(truth_dir.glob("*.json")):
        data = validate_truth_record(path)
        case_id = data["case_id"]
        if case_id in records:
            raise ValueError(f"duplicate truth record for {case_id}")
        records[case_id] = {
            "file": path.name,
            "case_version": data["case_version"],
            "truth_version": data["truth_version"],
            "sha256": sha256_file(path),
        }

    required = set(required_case_ids)
    missing = sorted(required - records.keys())
    unexpected = sorted(records.keys() - required)
    if missing:
        raise ValueError(f"missing truth records: {missing}")
    if unexpected:
        raise ValueError(f"unexpected truth records: {unexpected}")

    return {
        "schema_version": "1.0",
        "status": "FROZEN",
        "records": records,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--truth-dir", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    out = assert_outside_repo(args.out)
    manifest = build_manifest(args.truth_dir)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"frozen {len(manifest['records'])} truth records -> {out}")


if __name__ == "__main__":
    main()
