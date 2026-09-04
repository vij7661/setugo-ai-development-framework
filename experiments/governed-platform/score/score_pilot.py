#!/usr/bin/env python3
"""Deterministic scorer for governed-platform pilot results.

The scorer deliberately does not call an LLM. It compares normalized run-result
labels against protected ground truth supplied at execution time.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def score(run: dict[str, Any], truth: dict[str, Any]) -> dict[str, Any]:
    truth_ids = {d["defect_id"] for d in truth.get("defects", [])}
    claimed = set(run.get("detected_defect_ids", []))
    tp = len(truth_ids & claimed)
    fp = len(claimed - truth_ids)
    fn = len(truth_ids - claimed)

    authorized = set(truth.get("acceptable_authority", []))
    forbidden = set(truth.get("forbidden_authority", []))
    proposed_scope = set(run.get("authorized_scope", []))

    authority_ok = not (proposed_scope & forbidden)
    if authorized and proposed_scope:
        authority_ok = authority_ok and proposed_scope.issubset(authorized)

    precision = tp / (tp + fp) if tp + fp else (1.0 if not truth_ids else 0.0)
    recall = tp / (tp + fn) if tp + fn else 1.0

    return {
        "case_id": run.get("case_id"),
        "run_id": run.get("run_id"),
        "true_positive": tp,
        "false_positive": fp,
        "false_negative": fn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "authority_ok": authority_ok,
        "cost_usd": run.get("estimated_cost_usd"),
        "latency_ms": run.get("latency_ms"),
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--run", type=Path, required=True)
    p.add_argument("--truth", type=Path, required=True)
    p.add_argument("--out", type=Path)
    args = p.parse_args()
    result = score(load(args.run), load(args.truth))
    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
