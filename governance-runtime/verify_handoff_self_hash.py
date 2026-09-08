#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def canonical_self_hash(record: dict[str, Any], field: str = "handoff_hash") -> str:
    material = dict(record)
    material.pop(field, None)
    return "sha256:" + hashlib.sha256(canonical_bytes(material)).hexdigest()


def whole_file_hash(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--expected", required=True)
    args = ap.parse_args()

    path = Path(args.path)
    record = json.loads(path.read_text(encoding="utf-8"))
    stored = record.get("handoff_hash")
    computed = canonical_self_hash(record)
    raw = whole_file_hash(path)

    result = {
        "path": str(path),
        "stored_handoff_hash": stored,
        "computed_canonical_self_hash": computed,
        "whole_file_byte_hash": raw,
        "expected": args.expected,
        "self_hash_matches_stored": stored == computed,
        "self_hash_matches_expected": computed == args.expected,
        "whole_file_hash_is_not_protocol_self_hash": raw != computed,
    }
    print(json.dumps(result, sort_keys=True))

    if stored != computed:
        raise SystemExit("stored handoff_hash does not equal canonical self-hash excluding handoff_hash")
    if computed != args.expected:
        raise SystemExit("canonical self-hash does not equal preregistered expected hash")


if __name__ == "__main__":
    main()
