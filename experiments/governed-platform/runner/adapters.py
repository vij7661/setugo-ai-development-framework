"""Provider-independent mechanism adapters for the governed-platform pilot.

The mock adapter is infrastructure-only. Its outputs MUST NOT be counted as
experimental evidence or used to rank reasoning mechanisms.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
import time
from typing import Any, Mapping


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
        # Deliberately does not inspect hidden truth, provider credentials, or repo state.
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
        )


def normalize_adapter_result(
    envelope: Mapping[str, Any], result: AdapterResult
) -> dict[str, Any]:
    """Normalize adapter output without adjudicating correctness."""
    required = ("run_id", "case_id", "case_version", "mechanism_id")
    missing = [name for name in required if name not in envelope]
    if missing:
        raise ValueError(f"prepared envelope missing required fields: {missing}")

    return {
        "run_id": envelope["run_id"],
        "case_id": envelope["case_id"],
        "case_version": envelope["case_version"],
        "mechanism_id": envelope["mechanism_id"],
        "mechanism_version": result.mechanism_version,
        "provider": result.provider,
        "status": result.status,
        "findings": [],
        "detected_defect_ids": [],
        "diagnosis": None,
        "authorized_scope": [],
        "changed_artifacts": [],
        "raw_output": result.raw_output,
        "evidence_refs": [],
        "input_tokens": result.input_tokens,
        "output_tokens": result.output_tokens,
        "estimated_cost_usd": result.estimated_cost_usd,
        "latency_ms": result.latency_ms,
        "evidence_eligible": result.evidence_eligible,
    }
