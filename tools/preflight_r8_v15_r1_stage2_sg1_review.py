"""Exact-artifact, non-activating preflight for SG-1 review contracts."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import subprocess
import re

sys.path.insert(0, str(Path(__file__).parent))
from r8_v15_r1_review_contract_parser import parse_review_file  # noqa: E402


def validate_artifact(path: Path, *, expected_sha256: str | None = None, expected_blob: str | None = None, git_rev: str = "HEAD") -> dict:
    result = parse_review_file(path)
    raw = path.read_bytes()
    raw_sha = hashlib.sha256(raw).hexdigest()
    if expected_sha256 and raw_sha != expected_sha256:
        raise ValueError("review raw SHA-256 mismatch")
    if expected_blob:
        blob = subprocess.check_output(["git", "rev-parse", f"{git_rev}:{path.as_posix()}"], text=True).strip()
        if blob != expected_blob:
            raise ValueError("review Git blob mismatch")
    activation_yes = len(re.findall(r"(?mi)^\s*(?:-\s*)?Stage2 SG-1 may be explicitly activated by user:\s*YES\.?\s*$", result["H"])) == 1
    broader_no = len(re.findall(r"(?mi)^\s*(?:-\s*)?Broader Stage2 semantic authority granted:\s*NO\.?\s*$", result["H"])) == 1
    return {"status": "PASS", "review_path": path.as_posix(), "raw_sha256": raw_sha, "disposition": result["A"].strip(), "critical": result["C"].strip(), "high": result["D"].strip(), "activation_yes": activation_yes, "broader_stage2_no": broader_no}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", required=True, type=Path)
    ap.add_argument("--expected-sha256")
    ap.add_argument("--expected-blob")
    ap.add_argument("--git-rev", default="HEAD")
    args = ap.parse_args()
    if (str(__import__("os").environ.get("CI", "")).lower() == "true" or args.expected_sha256 or args.expected_blob) and not (args.expected_sha256 and args.expected_blob):
        raise SystemExit("exact expected SHA-256 and Git blob are required in CI/exact mode")
    path = args.review
    try:
        result = validate_artifact(path, expected_sha256=args.expected_sha256, expected_blob=args.expected_blob, git_rev=args.git_rev)
    except ValueError as exc:
        raise SystemExit(str(exc))
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
