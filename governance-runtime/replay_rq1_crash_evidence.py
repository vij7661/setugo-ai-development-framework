#!/usr/bin/env python3
"""Offline replay of preserved RQ-13/14/15 result structures.

This command only reads files and invokes pure predicates; it never imports
the service client and never contacts the runtime.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from v24_v6_rq1_crash_predicates import evaluate_crash_case


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("evidence_dir", type=Path)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    files = sorted(p for p in args.evidence_dir.rglob("*") if p.is_file())
    result = {"operation": "OFFLINE_EVIDENCE_REPLAY_NO_RUNTIME_EXECUTION", "input_files": {str(p.relative_to(args.evidence_dir)): digest(p) for p in files}, "cases": {}}
    exit_code = 0
    for case in ("RQ-13", "RQ-14", "RQ-15"):
        path = args.evidence_dir / f"{case}.result.json"
        if not path.is_file():
            result["cases"][case] = {"status": "INSUFFICIENT_EVIDENCE", "reason": "result_file_missing"}
            exit_code = 2
            continue
        raw = json.loads(path.read_text(encoding="utf-8"))
        evidence = raw.get("detail") if isinstance(raw, dict) else None
        if not isinstance(evidence, dict):
            result["cases"][case] = {"status": "INSUFFICIENT_EVIDENCE", "reason": "result_detail_missing"}
            exit_code = 2
            continue
        ok, reasons = evaluate_crash_case(case, evidence)
        result["cases"][case] = {"status": "PASS" if ok else "NOT_PASS", "reasons": reasons, "result_sha256": digest(path)}
        if not ok:
            exit_code = 2
    text = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
