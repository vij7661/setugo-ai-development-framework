"""Exact-artifact, non-activating preflight for SG-1 review contracts."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from r8_v15_r1_review_contract_parser import parse_review_file  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", required=True, type=Path)
    args = ap.parse_args()
    path = args.review
    result = parse_review_file(path)
    raw = path.read_bytes()
    print(json.dumps({
        "status": "PASS",
        "review_path": path.as_posix(),
        "raw_sha256": hashlib.sha256(raw).hexdigest(),
        "disposition": result["A"].strip(),
        "critical": result["C"].strip(),
        "high": result["D"].strip(),
        "activation_yes": "Stage2 SG-1 may be explicitly activated by user: YES" in result["H"],
        "broader_stage2_no": "Broader Stage2 semantic authority granted: NO" in result["H"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
