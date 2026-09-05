#!/usr/bin/env python3
"""Execute one prepared blinded envelope through an OpenAI-compatible remote provider.

This runner never reads protected ground truth. Provider/model/credential locations are runtime inputs.
Every attempted invocation writes an explicit result record, including transport/provider failures,
so experimental candidate collection cannot silently drop a failed mechanism.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from adapters import normalize_adapter_result
from openai_compatible import OpenAICompatibleAdapter, RemoteProviderConfig


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _write_error_result(args, envelope, exc: Exception) -> None:
    case_binding = envelope.get("case_binding", {})
    mechanism = envelope.get("mechanism", {})
    result = {
        "run_id": envelope.get("run_id"),
        "case_id": envelope.get("case_id", case_binding.get("case_id")),
        "case_version": envelope.get("case_version", case_binding.get("case_version")),
        "case_model_visible_sha256": case_binding.get("model_visible_sha256"),
        "instruction_version": envelope.get("instruction_version"),
        "mechanism_id": envelope.get("mechanism_id", mechanism.get("mechanism_id")),
        "mechanism_version": args.model,
        "provider": args.provider,
        "status": "ERROR",
        "summary": None,
        "findings": [],
        "detected_defect_ids": [],
        "diagnosis": None,
        "authorized_scope": [],
        "changed_artifacts": [],
        "raw_output": None,
        "evidence_refs": [],
        "input_tokens": None,
        "output_tokens": None,
        "estimated_cost_usd": None,
        "latency_ms": None,
        "evidence_eligible": False,
        "runtime_metadata": {
            "configured_model": args.model,
            "completion_complete": False,
            "structured_output_valid": False,
            "sampling_temperature": args.temperature,
            "error_type": type(exc).__name__,
            "error": str(exc),
        },
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(args.out)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--envelope", required=True, type=Path)
    parser.add_argument("--provider", required=True)
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--api-key-env", required=True)
    parser.add_argument("--timeout-seconds", type=int, default=120)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    envelope = load_json(args.envelope)
    configured_model = envelope.get("mechanism", {}).get("model")
    if configured_model and configured_model != args.model:
        raise ValueError(
            f"runtime model {args.model!r} does not match prepared envelope model {configured_model!r}"
        )

    adapter = OpenAICompatibleAdapter(
        RemoteProviderConfig(
            provider_id=args.provider,
            base_url=args.base_url,
            model=args.model,
            api_key_env=args.api_key_env,
            timeout_seconds=args.timeout_seconds,
            temperature=args.temperature,
        )
    )
    try:
        result = adapter.invoke(envelope)
        normalized = normalize_adapter_result(envelope, result)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(normalized, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(args.out)
        return 0 if normalized["status"] == "PASS" and normalized["evidence_eligible"] else 2
    except Exception as exc:
        _write_error_result(args, envelope, exc)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
