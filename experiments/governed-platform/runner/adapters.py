"""Provider-independent mechanism adapters for the governed-platform pilot.

The mock adapter is infrastructure-only. Its outputs MUST NOT be counted as
experimental evidence or used to rank reasoning mechanisms.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
import json
import time
from typing import Any, Mapping
from urllib import error, request

from review_contract import REVIEW_OUTPUT_SCHEMA_INSTRUCTION, StructuredReviewError, parse_structured_review


@dataclass(frozen=True)
class AdapterResult:
    status: str
    raw_output: str
    provider: str | None
    mechanism_version: str | None
    input_tokens: int | None
    output_tokens: int | None
    estimated_cost_usd: float | None
    latency_ms: int
    evidence_eligible: bool
    runtime_metadata: Mapping[str, Any] | None = None


class MechanismAdapter(ABC):
    """Stable interface implemented by real provider/tool adapters."""

    @abstractmethod
    def invoke(self, envelope: Mapping[str, Any]) -> AdapterResult:
        """Invoke one mechanism using only the prepared model-visible envelope."""


class MockAdapter(MechanismAdapter):
    """Deterministic plumbing adapter; never valid experimental evidence."""

    def __init__(self, response: str = "MOCK_RESPONSE") -> None:
        self._response = response

    def invoke(self, envelope: Mapping[str, Any]) -> AdapterResult:
        if "model_visible" not in envelope:
            raise ValueError("prepared envelope must contain model_visible")
        started = time.perf_counter()
        raw = self._response
        latency_ms = max(0, int((time.perf_counter() - started) * 1000))
        return AdapterResult(
            status="PASS",
            raw_output=raw,
            provider="mock",
            mechanism_version="mock-v1",
            input_tokens=None,
            output_tokens=None,
            estimated_cost_usd=0.0,
            latency_ms=latency_ms,
            evidence_eligible=False,
            runtime_metadata={"evidence_class": "NON_EXPERIMENTAL"},
        )


class OllamaAdapter(MechanismAdapter):
    """Local Ollama HTTP adapter using only the model-visible prepared envelope."""

    def __init__(
        self,
        model: str,
        base_url: str = "http://127.0.0.1:11434",
        timeout_seconds: int = 600,
    ) -> None:
        if not model:
            raise ValueError("model is required")
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    @staticmethod
    def _prompt(envelope: Mapping[str, Any]) -> str:
        if "model_visible" not in envelope:
            raise ValueError("prepared envelope must contain model_visible")
        payload = json.dumps(envelope["model_visible"], ensure_ascii=False, sort_keys=True)
        return (
            "You are an independent evaluator in a blinded software-engineering experiment. "
            "Use only the supplied case payload. Do not assume hidden requirements. "
            "Report concrete material defects supported by the payload; if the task asks for "
            "diagnosis, classify the failure and state authorized artifact scope. If no material "
            "defect is supported, report that explicitly.\n\n"
            + REVIEW_OUTPUT_SCHEMA_INSTRUCTION
            + "\n\nCASE PAYLOAD:\n"
            + payload
        )

    def invoke(self, envelope: Mapping[str, Any]) -> AdapterResult:
        body = {
            "model": self.model,
            "prompt": self._prompt(envelope),
            "stream": False,
        }
        encoded = json.dumps(body).encode("utf-8")
        req = request.Request(
            f"{self.base_url}/api/generate",
            data=encoded,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        started = time.perf_counter()
        try:
            with request.urlopen(req, timeout=self.timeout_seconds) as response:
                data = json.loads(response.read().decode("utf-8"))
        except (error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            latency_ms = max(0, int((time.perf_counter() - started) * 1000))
            return AdapterResult(
                status="ERROR",
                raw_output=f"OLLAMA_ADAPTER_ERROR: {exc}",
                provider="ollama-local",
                mechanism_version=self.model,
                input_tokens=None,
                output_tokens=None,
                estimated_cost_usd=0.0,
                latency_ms=latency_ms,
                evidence_eligible=False,
                runtime_metadata={"base_url": self.base_url, "model": self.model},
            )

        latency_ms = max(0, int((time.perf_counter() - started) * 1000))
        raw_output = data.get("response")
        if not isinstance(raw_output, str):
            return AdapterResult(
                status="ERROR",
                raw_output="OLLAMA_ADAPTER_ERROR: response field missing or invalid",
                provider="ollama-local",
                mechanism_version=str(data.get("model") or self.model),
                input_tokens=data.get("prompt_eval_count"),
                output_tokens=data.get("eval_count"),
                estimated_cost_usd=0.0,
                latency_ms=latency_ms,
                evidence_eligible=False,
                runtime_metadata={"done_reason": data.get("done_reason")},
            )

        return AdapterResult(
            status="PASS",
            raw_output=raw_output,
            provider="ollama-local",
            mechanism_version=str(data.get("model") or self.model),
            input_tokens=data.get("prompt_eval_count"),
            output_tokens=data.get("eval_count"),
            estimated_cost_usd=0.0,
            latency_ms=latency_ms,
            evidence_eligible=True,
            runtime_metadata={
                "done": data.get("done"),
                "done_reason": data.get("done_reason"),
                "total_duration_ns": data.get("total_duration"),
                "load_duration_ns": data.get("load_duration"),
                "prompt_eval_duration_ns": data.get("prompt_eval_duration"),
                "eval_duration_ns": data.get("eval_duration"),
                "base_url": self.base_url,
            },
        )


def normalize_adapter_result(
    envelope: Mapping[str, Any], result: AdapterResult
) -> dict[str, Any]:
    """Normalize adapter output without adjudicating correctness.

    Evidence-eligible reasoning completions must satisfy the structured review
    contract. Unstructured text is retained for diagnosis but fails closed as
    scientific evidence so findings cannot disappear between raw output and the
    evidence ledger.
    """
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
            structured = parse_structured_review(result.raw_output)
        except StructuredReviewError as exc:
            normalization_error = str(exc)

    runtime_metadata = dict(result.runtime_metadata or {})
    runtime_metadata["structured_output_valid"] = structured is not None
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
