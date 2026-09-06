"""Normalize provider review output, then bind it to platform-issued authority.

Scientific evidence eligibility and execution authority are intentionally separate.
A model can produce an unsafe authority claim that remains valid behavioral evidence;
the platform binding records the claim and prevents it from becoming effective scope.
"""
from __future__ import annotations

from typing import Any, Mapping

from adapters import AdapterResult
from review_contract_external_authority import (
    ExternalAuthorityStructuredReviewError,
    parse_external_authority_review,
)


def normalize_external_authority_result(
    envelope: Mapping[str, Any], result: AdapterResult
) -> dict[str, Any]:
    case_binding = envelope.get("case_binding", {})
    mechanism = envelope.get("mechanism", {})

    run_id = envelope.get("run_id")
    case_id = envelope.get("case_id", case_binding.get("case_id"))
    case_version = envelope.get("case_version", case_binding.get("case_version"))
    mechanism_id = envelope.get("mechanism_id", mechanism.get("mechanism_id"))
    missing = [
        name
        for name, value in (
            ("run_id", run_id),
            ("case_id", case_id),
            ("case_version", case_version),
            ("mechanism_id", mechanism_id),
        )
        if value is None
    ]
    if missing:
        raise ValueError(f"prepared envelope missing required fields: {missing}")

    structured = None
    normalization_error = None
    if result.evidence_eligible and result.status == "PASS":
        try:
            structured = parse_external_authority_review(result.raw_output)
        except ExternalAuthorityStructuredReviewError as exc:
            normalization_error = str(exc)

    runtime_metadata = dict(result.runtime_metadata or {})
    runtime_metadata["structured_output_valid"] = structured is not None
    runtime_metadata["authority_binding_required"] = True
    if normalization_error:
        runtime_metadata["normalization_error"] = normalization_error

    normalized_status = result.status
    normalized_evidence_eligible = result.evidence_eligible
    if normalization_error:
        normalized_status = "ERROR"
        normalized_evidence_eligible = False

    return {
        "run_id": run_id,
        "case_id": case_id,
        "case_version": case_version,
        "case_model_visible_sha256": case_binding.get("model_visible_sha256"),
        "instruction_version": envelope.get("instruction_version"),
        "mechanism_id": mechanism_id,
        "mechanism_version": result.mechanism_version,
        "provider": result.provider,
        "status": normalized_status,
        "summary": structured["summary"] if structured else None,
        "findings": structured["findings"] if structured else [],
        "detected_defect_ids": [],
        "diagnosis": structured["diagnosis"] if structured else None,
        "authorized_scope": structured["authorized_scope"] if structured else [],
        "changed_artifacts": structured["changed_artifacts"] if structured else [],
        "raw_output": result.raw_output,
        "evidence_refs": structured["evidence_refs"] if structured else [],
        "input_tokens": result.input_tokens,
        "output_tokens": result.output_tokens,
        "estimated_cost_usd": result.estimated_cost_usd,
        "latency_ms": result.latency_ms,
        "evidence_eligible": normalized_evidence_eligible,
        "runtime_metadata": runtime_metadata,
    }
