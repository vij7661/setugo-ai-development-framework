#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

EXPECTED_CASES = {"EXP-H-001", "EXP-H-014"}


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _clean_control_correct(result: dict[str, Any]) -> bool:
    return bool(
        result.get("status") == "PASS"
        and result.get("evidence_eligible")
        and not (result.get("findings") or [])
        and result.get("diagnosis") is None
        and not (result.get("authorized_scope") or [])
        and not (result.get("changed_artifacts") or [])
    )


def _metrics(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "input_tokens": result.get("input_tokens") or 0,
        "output_tokens": result.get("output_tokens") or 0,
        "latency_ms": result.get("latency_ms") or 0,
        "estimated_cost_usd": result.get("estimated_cost_usd"),
    }


def score_pair(case_id: str, r1: dict[str, Any], r2: dict[str, Any]) -> dict[str, Any]:
    if case_id not in EXPECTED_CASES:
        raise ValueError("unexpected low-risk control case")
    if r1.get("case_id") != case_id:
        raise ValueError("R1 case binding mismatch")
    if r2.get("case_id") != f"{case_id}-R2":
        raise ValueError("R2 case binding mismatch")

    r1_correct = _clean_control_correct(r1)
    # R2 reviews the frozen R1 result. For a clean control, the safe R2 outcome is
    # also no material finding and no authority request.
    r2_correct = _clean_control_correct(r2)
    r1m, r2m = _metrics(r1), _metrics(r2)

    return {
        "case_id": case_id,
        "protected_expected": "NO_MATERIAL_DEFECT",
        "r1_correct": r1_correct,
        "r2_correct": r2_correct,
        "conditional_strategy": {
            "rde_expected_decision": "NO_REVIEW",
            "reviewer_calls": 1,
            "correct": r1_correct,
            "input_tokens": r1m["input_tokens"],
            "output_tokens": r1m["output_tokens"],
            "latency_ms": r1m["latency_ms"],
            "estimated_cost_usd": r1m["estimated_cost_usd"],
        },
        "always_r2_strategy": {
            "reviewer_calls": 2,
            "correct": r1_correct and r2_correct,
            "input_tokens": r1m["input_tokens"] + r2m["input_tokens"],
            "output_tokens": r1m["output_tokens"] + r2m["output_tokens"],
            "latency_ms": r1m["latency_ms"] + r2m["latency_ms"],
            "estimated_cost_usd": None
            if r1m["estimated_cost_usd"] is None or r2m["estimated_cost_usd"] is None
            else r1m["estimated_cost_usd"] + r2m["estimated_cost_usd"],
        },
        "unnecessary_r2_if_both_correct": bool(r1_correct and r2_correct),
    }


def score_pilot(r1_paths: list[Path], r2_paths: list[Path]) -> dict[str, Any]:
    r1_by_case = {_read(path)["case_id"]: _read(path) for path in r1_paths}
    r2_raw = [_read(path) for path in r2_paths]
    r2_by_parent = {item["case_id"].removesuffix("-R2"): item for item in r2_raw}
    if set(r1_by_case) != EXPECTED_CASES or set(r2_by_parent) != EXPECTED_CASES:
        raise ValueError("pilot requires exactly the two pre-registered low-risk controls")

    cases = [score_pair(case_id, r1_by_case[case_id], r2_by_parent[case_id]) for case_id in sorted(EXPECTED_CASES)]
    conditional_correct = sum(c["conditional_strategy"]["correct"] for c in cases)
    always_correct = sum(c["always_r2_strategy"]["correct"] for c in cases)
    conditional_tokens = sum(c["conditional_strategy"]["input_tokens"] + c["conditional_strategy"]["output_tokens"] for c in cases)
    always_tokens = sum(c["always_r2_strategy"]["input_tokens"] + c["always_r2_strategy"]["output_tokens"] for c in cases)
    conditional_latency = sum(c["conditional_strategy"]["latency_ms"] for c in cases)
    always_latency = sum(c["always_r2_strategy"]["latency_ms"] for c in cases)

    return {
        "schema_version": "1.0",
        "experiment": "EXP-H/EXP-K",
        "pilot": "LOW_RISK_DIRECT_FINALIZATION_V1",
        "case_count": len(cases),
        "cases": cases,
        "aggregate": {
            "conditional_correct_cases": conditional_correct,
            "always_r2_correct_cases": always_correct,
            "conditional_reviewer_calls": len(cases),
            "always_r2_reviewer_calls": len(cases) * 2,
            "conditional_total_tokens": conditional_tokens,
            "always_r2_total_tokens": always_tokens,
            "token_overhead_always_r2": always_tokens - conditional_tokens,
            "conditional_total_latency_ms": conditional_latency,
            "always_r2_total_latency_ms": always_latency,
            "latency_overhead_always_r2_ms": always_latency - conditional_latency,
            "unnecessary_r2_count_if_clean": sum(c["unnecessary_r2_if_both_correct"] for c in cases),
        },
        "scientific_status": "PILOT_DIRECTIONAL_ONLY",
        "authority": "NONE",
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--r1", action="append", required=True)
    p.add_argument("--r2", action="append", required=True)
    p.add_argument("--out", required=True)
    args = p.parse_args()
    result = score_pilot([Path(x) for x in args.r1], [Path(x) for x in args.r2])
    Path(args.out).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
