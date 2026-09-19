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


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _stdout_obj(item):
    if not isinstance(item, dict):
        return None
    if isinstance(item.get("parsed"), dict):
        return item["parsed"]
    text = item.get("stdout", "")
    if not isinstance(text, str) or not text.strip():
        return None
    try:
        value = json.loads(text)
    except (TypeError, ValueError):
        return None
    return value if isinstance(value, dict) else None


def adapt_case(directory: Path, case: str) -> dict:
    raw = _json(directory / f"{case}.result.json")
    detail = raw.get("detail") if isinstance(raw, dict) else None
    if not isinstance(detail, dict):
        raise ValueError("result detail missing")
    tracer = _json(directory / f"{case}.tracer-ready.json")
    boundary = _json(directory / f"{case}.boundary.json")
    target_id = detail.get("target_id")
    target = detail.get("target_name")
    out = dict(detail)
    out.update({"target_id": target_id, "target_name": target, "service_pid": tracer.get("pid"), "boundary": tracer.get("boundary"), "tracer_ready": tracer, "boundary_evidence": boundary})
    for phase in ("baseline", "prepared", "recovery", "post-retry", "post-replay"):
        path = directory / f"{case}.{phase}.observer.json"
        if not path.is_file():
            raise ValueError(f"missing {path.name}")
        out["prepared" if phase == "prepared" else phase.replace("-", "_")] = _json(path)
    for key in ("retry", "replay"):
        if isinstance(out.get(key), dict):
            parsed = _stdout_obj(out[key])
            out[key] = dict(out[key], parsed=parsed)
    if isinstance(out.get("first_consume"), dict):
        out["first_consume"] = dict(out["first_consume"], parsed=_stdout_obj(out["first_consume"]))
    out["restart_returncode"] = out.get("restart_returncode", (out.get("restart") or {}).get("rc"))
    return out


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
        try:
            evidence = adapt_case(args.evidence_dir, case)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            result["cases"][case] = {"status": "INSUFFICIENT_EVIDENCE", "reason": str(exc)}
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
