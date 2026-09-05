from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class CounterfactualProbeResult:
    counterfactual_id: str
    complete: bool
    conclusion_changed: bool
    falsifier_identified: bool
    unsupported_premise_found: bool
    evidence_gap_found: bool


@dataclass(frozen=True)
class CounterfactualAssessment:
    status: str
    instability_signal: bool
    reasons: tuple[str, ...]
    completed_probe_count: int


def assess_counterfactuals(
    results: Iterable[CounterfactualProbeResult],
    *,
    minimum_complete_probes: int = 2,
) -> CounterfactualAssessment:
    if minimum_complete_probes < 1:
        raise ValueError("minimum_complete_probes must be positive")

    rows = tuple(results)
    ids = [r.counterfactual_id for r in rows]
    if any(not x for x in ids):
        raise ValueError("counterfactual_id required")
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate counterfactual_id")

    complete = tuple(r for r in rows if r.complete)
    if len(complete) < minimum_complete_probes:
        return CounterfactualAssessment(
            status="INSUFFICIENT",
            instability_signal=True,
            reasons=("insufficient complete counterfactual probes",),
            completed_probe_count=len(complete),
        )

    reasons: list[str] = []
    if any(r.conclusion_changed for r in complete):
        reasons.append("conclusion changed under controlled counterfactual")
    if any(r.unsupported_premise_found for r in complete):
        reasons.append("unsupported premise exposed")
    if any(r.evidence_gap_found for r in complete):
        reasons.append("evidence gap exposed")

    # Identifying a falsifier is healthy and is not itself instability. The signal is
    # whether the controlled probe exposes a changed conclusion, unsupported premise,
    # or evidence gap. This assessment never grants correctness or authority.
    unstable = bool(reasons)
    return CounterfactualAssessment(
        status="INSTABILITY_SIGNAL" if unstable else "STABLE_UNDER_PROBES",
        instability_signal=unstable,
        reasons=tuple(reasons) if reasons else ("no material counterfactual instability observed",),
        completed_probe_count=len(complete),
    )
