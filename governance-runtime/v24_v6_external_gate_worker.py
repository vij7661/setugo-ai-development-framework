"""Successor-5 external authority gate worker.

This process is a construction diagnostic child of the native authority gate.
It never grants authority by itself. The native parent pins this file and the
load-bearing Python sources by SHA-256, independently validates the exact
context/scope/root attestation, launches this worker in a clean interpreter, and
alone emits the final construction allow/deny decision.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import v24_v6_proof_reference_closure as prc

AUTHORITY_EFFECT = "NONE_EVIDENCE_ONLY"


def _load(path: str) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main(argv: list[str]) -> int:
    if len(argv) != 7:
        raise SystemExit("worker requires operation, context, boundary, reference, expected id, expected digest")

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
        raise SystemExit("unsupported gate worker operation")

    scope = context.get("genesis_trusted_scope")
    output = {
        "authority_effect": result.get("authority_effect"),
        "construction_diagnostic_only": True,
        "input_binding": {
            "context_digest": context.get("context_digest"),
            "expected_digest": expected_digest,
            "expected_id": expected_id,
            "genesis_trusted_scope_digest": (
                scope.get("scope_digest") if isinstance(scope, dict) else None
            ),
            "governance_generation_id": context.get("governance_generation_id"),
        },
        "problems": result.get("problems", []),
        "qualified": bool(result.get("qualified")),
        "reference_digest": result.get("reference_digest", reference),
        "resolved_digests": result.get("resolved_digests", []),
        "state": result.get("state"),
    }
    print(json.dumps(output, sort_keys=True, separators=(",", ":"), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
