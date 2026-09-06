#!/usr/bin/env python3
"""Execute one prepared review envelope with authority enforced outside the model.

This runner is intentionally separate from run_remote_canary.py so the frozen EXP-N
Pilot 8 execution path remains unchanged. Provider output is normalized first, then
bound to a platform-issued capability. Any model-declared authority remains evidence
only and cannot become effective authority.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

GOVERNED_PLATFORM_ROOT = Path(__file__).resolve().parents[1]
GOVERNANCE_DIR = GOVERNED_PLATFORM_ROOT / "governance"
if str(GOVERNANCE_DIR) not in sys.path:
    sys.path.insert(0, str(GOVERNANCE_DIR))

from authority_binding import bind_model_result_to_capability  # noqa: E402
from normalize_external_authority_result import normalize_external_authority_result  # noqa: E402
from openai_compatible_external_authority import (  # noqa: E402
    ExternalAuthorityRemoteProviderConfig,
    OpenAICompatibleExternalAuthorityAdapter,
)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _error_result(args, envelope, capability, exc: Exception) -> dict:
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
            "authority_prompt_mode": "NO_PROMPT_AUTHORITY_GUARD",
            "authority_binding_required": True,
            "error_type": type(exc).__name__,
            "error": str(exc),
        },
    }
    return bind_model_result_to_capability(result, capability)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--envelope", required=True, type=Path)
    parser.add_argument("--capability", required=True, type=Path)
    parser.add_argument("--provider", required=True)
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--api-key-env", required=True)
    parser.add_argument("--timeout-seconds", type=int, default=120)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    envelope = load_json(args.envelope)
    capability = load_json(args.capability)
    configured_model = envelope.get("mechanism", {}).get("model")
    if configured_model and configured_model != args.model:
        raise ValueError(
            f"runtime model {args.model!r} does not match prepared envelope model {configured_model!r}"
        )

    adapter = OpenAICompatibleExternalAuthorityAdapter(
        ExternalAuthorityRemoteProviderConfig(
            provider_id=args.provider,
            base_url=args.base_url,
            model=args.model,
            api_key_env=args.api_key_env,
            timeout_seconds=args.timeout_seconds,
            temperature=args.temperature,
        )
    )

    try:
        provider_result = adapter.invoke(envelope)
        normalized = normalize_external_authority_result(envelope, provider_result)
        bound = bind_model_result_to_capability(normalized, capability)
        bound.setdefault("runtime_metadata", {})["platform_capability_id"] = capability.get("capability_id")
        bound["runtime_metadata"]["platform_capability_epoch"] = capability.get("issued_epoch")
        bound["runtime_metadata"]["platform_authority_class"] = capability.get("authority_class")
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(bound, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(args.out)
        return 0 if bound["status"] == "PASS" and bound["evidence_eligible"] else 2
    except Exception as exc:
        bound = _error_result(args, envelope, capability, exc)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(bound, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(args.out)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
