"""Successor-5 external authority gate worker.

This process is a construction diagnostic child of the native authority gate.
It never grants authority by itself. The native parent pins this file and every
load-bearing Python source used by an operation, independently validates the
exact context/scope/root attestation, launches this worker in a clean
interpreter, and alone emits the final construction allow/deny decision.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import v24_v6_proof_reference_closure as prc
from v24_v6_decision_apply import evaluate_decision_apply_latch
from v24_v6_normative_clause_projection import validate_catalog_candidate_coverage

AUTHORITY_EFFECT = "NONE_EVIDENCE_ONLY"


def _load(path: str) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _raw_sha256(path: str) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _input_binding(context: dict[str, Any]) -> dict[str, Any]:
    scope = context.get("genesis_trusted_scope")
    return {
        "context_digest": context.get("context_digest"),
        "genesis_trusted_scope_digest": (
            scope.get("scope_digest") if isinstance(scope, dict) else None
        ),
        "governance_generation_id": context.get("governance_generation_id"),
    }


def _resolve(argv: list[str]) -> int:
    if len(argv) != 7:
        raise SystemExit(
            "resolve worker requires operation, context, boundary, reference, expected id, expected digest"
        )
    operation, context_path, boundary_path, reference, expected_id, expected_digest = argv[1:]
    context = _load(context_path)
    boundary = _load(boundary_path)

    expected_id_value = None if expected_id == "-" else expected_id
    expected_digest_value = None if expected_digest == "-" else expected_digest

    if operation == "resolve-governed":
        result = prc.resolve_governed_qualification(
            reference,
            context,
            boundary,
            expected_subject_id=expected_id_value,
            expected_subject_content_digest=expected_digest_value,
        )
    elif operation == "resolve-independence":
        result = prc.resolve_independence_qualification(
            reference,
            context,
            boundary,
            expected_subject_identity_id=expected_id_value,
        )
    elif operation == "resolve-currentness":
        result = prc.resolve_currentness_binding(
            reference,
            context,
            boundary,
            expected_source_id=expected_id_value,
            expected_source_digest=expected_digest_value,
        )
    else:
        raise SystemExit("unsupported proof-resolution gate worker operation")

    binding = _input_binding(context)
    binding["expected_digest"] = expected_digest
    binding["expected_id"] = expected_id
    output = {
        "authority_effect": result.get("authority_effect"),
        "construction_diagnostic_only": True,
        "input_binding": binding,
        "problems": result.get("problems", []),
        "qualified": bool(result.get("qualified")),
        "reference_digest": result.get("reference_digest", reference),
        "resolved_digests": result.get("resolved_digests", []),
        "state": result.get("state"),
    }
    print(json.dumps(output, sort_keys=True, separators=(",", ":"), ensure_ascii=False))
    return 0


def _downstream(argv: list[str]) -> int:
    if len(argv) != 5:
        raise SystemExit(
            "downstream worker requires operation, context, boundary, payload"
        )
    operation, context_path, boundary_path, payload_path = argv[1:]
    context = _load(context_path)
    boundary = _load(boundary_path)
    payload = _load(payload_path)

    if operation == "evaluate-decision-apply":
        result = evaluate_decision_apply_latch(
            payload,
            proof_context=context,
            trusted_boundary=boundary,
        )
        success = bool(result.get("allowed"))
    elif operation == "validate-normative-coverage":
        result = validate_catalog_candidate_coverage(
            payload,
            proof_context=context,
            trusted_boundary=boundary,
        )
        success = bool(result.get("qualified"))
    else:
        raise SystemExit("unsupported downstream gate worker operation")

    output = {
        "authority_effect": result.get("authority_effect"),
        "construction_diagnostic_only": True,
        "input_binding": _input_binding(context),
        "payload_sha256": _raw_sha256(payload_path),
        "problems": result.get("problems", []),
        "success": success,
        "state": result.get("state"),
    }
    print(json.dumps(output, sort_keys=True, separators=(",", ":"), ensure_ascii=False))
    return 0


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        raise SystemExit("gate worker operation required")
    if argv[1] in {"resolve-governed", "resolve-independence", "resolve-currentness"}:
        return _resolve(argv)
    if argv[1] in {"evaluate-decision-apply", "validate-normative-coverage"}:
        return _downstream(argv)
    raise SystemExit("unsupported gate worker operation")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
