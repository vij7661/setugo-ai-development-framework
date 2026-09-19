#!/usr/bin/env python3
"""Build a self-contained Remediation-7 package from supplied run-35 evidence.

The command is intentionally fail-closed: it refuses to build a package when
the immutable RQ-13/14/15 raw evidence directory is absent or incomplete.
It performs no runtime operation.
"""
from __future__ import annotations
import argparse, hashlib, json, shutil, subprocess
from pathlib import Path

CASES = ("RQ-13", "RQ-14", "RQ-15")


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""): h.update(b)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("evidence", type=Path)
    ap.add_argument("output", type=Path)
    args = ap.parse_args()
    required = [f"{case}.result.json" for case in CASES]
    required += [f"{case}.boundary.json" for case in CASES]
    required += [f"{case}.tracer-ready.json" for case in CASES]
    missing = [name for name in required if not (args.evidence / name).is_file()]
    if missing:
        raise SystemExit("INSUFFICIENT_EVIDENCE: missing immutable raw files: " + ", ".join(missing))
    args.output.mkdir(parents=True, exist_ok=False)
    shutil.copytree(args.evidence, args.output / "raw-evidence")
    manifest = {
        "operation": "OFFLINE_REVIEW_PACKAGE_NO_SCIENTIFIC_REEXECUTION",
        "scientific_commit": "d79db50568cccaffe67ed1de5a6ee63bf5027284",
        "scientific_run": "35433799081",
        "raw_input_sha256": {p.name: sha(p) for p in sorted(args.evidence.iterdir()) if p.is_file()},
        "governance": ["NOT_QUALIFIED", "CLOSED_PENDING_SUCCESSOR_REVIEW", "NONE_EVIDENCE_ONLY"],
    }
    (args.output / "manifest.json").write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"package": str(args.output), "files": len(list(args.output.rglob("*")))}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
