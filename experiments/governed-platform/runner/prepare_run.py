#!/usr/bin/env python3
"""Prepare a blinded experiment-run envelope from a model-visible case.

This module performs deterministic preparation only. It never calls an LLM and never
loads protected ground truth.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def select_mechanism(config: dict[str, Any], mechanism_id: str) -> dict[str, Any]:
    mechanisms = config.get("mechanisms", [])
    matches = [m for m in mechanisms if m.get("mechanism_id") == mechanism_id]
    if len(matches) != 1:
        raise ValueError(f"mechanism_id must resolve exactly once: {mechanism_id}")
    mechanism = matches[0]
    if not mechanism.get("enabled", False):
        raise ValueError(f"mechanism is not enabled: {mechanism_id}")
    return mechanism


def validate_case(case: dict[str, Any]) -> None:
    required = {"case_id", "experiment_id", "version", "risk", "artifact_ref", "model_visible"}
    missing = sorted(required - case.keys())
    if missing:
        raise ValueError(f"case missing required fields: {', '.join(missing)}")
    if not isinstance(case["model_visible"], dict):
        raise ValueError("model_visible must be an object")


def prepare(case: dict[str, Any], mechanism: dict[str, Any], instruction_version: str) -> dict[str, Any]:
    validate_case(case)
    model_visible = case["model_visible"]
    case_binding = {
        "case_id": case["case_id"],
        "case_version": case["version"],
        "experiment_id": case["experiment_id"],
        "model_visible_sha256": sha256_json(model_visible),
    }
    run_seed = {
        **case_binding,
        "mechanism_id": mechanism["mechanism_id"],
        "instruction_version": instruction_version,
    }
    run_id = f"pilot1-{sha256_json(run_seed)[:20]}"
    return {
        "schema_version": "1.0",
        "run_id": run_id,
        "prepared_at": datetime.now(timezone.utc).isoformat(),
        "case_binding": case_binding,
        "instruction_version": instruction_version,
        "mechanism": {
            "mechanism_id": mechanism["mechanism_id"],
            "kind": mechanism.get("kind"),
            "adapter": mechanism.get("adapter"),
            "provider": mechanism.get("provider"),
            "model": mechanism.get("model"),
            "role": mechanism.get("role"),
            "qualification_ref": mechanism.get("qualification_ref"),
            "privacy_class": mechanism.get("privacy_class"),
        },
        "model_visible": model_visible,
        "prohibited_fields_confirmed_absent": ["ground_truth_ref", "authoritative_intent_ref", "invariant_refs"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", required=True, type=Path)
    parser.add_argument("--mechanisms", required=True, type=Path)
    parser.add_argument("--mechanism-id", required=True)
    parser.add_argument("--instruction-version", required=True)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    case = load_json(args.case)
    config = load_json(args.mechanisms)
    mechanism = select_mechanism(config, args.mechanism_id)
    envelope = prepare(case, mechanism, args.instruction_version)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(envelope, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
