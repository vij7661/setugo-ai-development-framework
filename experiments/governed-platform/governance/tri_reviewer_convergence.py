from __future__ import annotations

from dataclasses import dataclass
from typing import Any

STATES = {
    "CONVERGED_PASS",
    "CONVERGED_WITH_DISSENT",
    "CONVERGED_FAIL",
    "INSUFFICIENT_EVIDENCE",
    "HUMAN_REQUIRED",
}
SEVERITY = {"NONE": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}


@dataclass(frozen=True)
class ConvergenceDecision:
    state: str
    reasons: tuple[str, ...]


def decide_convergence(signals: dict[str, Any]) -> ConvergenceDecision:
    required_bools = (
        "evidence_complete",
        "requirement_ambiguity",
        "material_conflict",
        "r3_completed",
        "r3_required",
        "r3_available_qualified",
        "review_ceiling_reached",
        "material_revision_since_review",
        "authoritative_failure_established",
        "non_material_dissent",
    )
    for key in required_bools:
        if key not in signals or not isinstance(signals[key], bool):
            raise ValueError(f"missing or invalid boolean signal: {key}")

    max_unresolved = signals.get("max_unresolved_severity", "NONE")
    if max_unresolved not in SEVERITY:
        raise ValueError("invalid max_unresolved_severity")

    if signals["requirement_ambiguity"]:
        return ConvergenceDecision("HUMAN_REQUIRED", ("authoritative requirement ambiguity",))

    if signals["material_revision_since_review"]:
        return ConvergenceDecision("INSUFFICIENT_EVIDENCE", ("reviews are stale after material revision",))

    if signals["r3_required"]:
        if not signals["r3_available_qualified"]:
            return ConvergenceDecision("HUMAN_REQUIRED", ("required Reviewer 3 unavailable or unqualified",))
        if not signals["r3_completed"]:
            if signals["review_ceiling_reached"]:
                return ConvergenceDecision("HUMAN_REQUIRED", ("review ceiling reached before required R3 completion",))
            return ConvergenceDecision("INSUFFICIENT_EVIDENCE", ("required Reviewer 3 has not completed",))

    if signals["review_ceiling_reached"] and signals["material_conflict"]:
        return ConvergenceDecision("HUMAN_REQUIRED", ("material conflict remains at review ceiling",))

    if signals["authoritative_failure_established"]:
        return ConvergenceDecision("CONVERGED_FAIL", ("authoritative evidence establishes material failure",))

    if not signals["evidence_complete"]:
        return ConvergenceDecision("INSUFFICIENT_EVIDENCE", ("authoritative evidence incomplete",))

    if signals["material_conflict"] or SEVERITY[max_unresolved] >= SEVERITY["HIGH"]:
        return ConvergenceDecision("HUMAN_REQUIRED", ("material finding remains unresolved",))

    if signals["non_material_dissent"] or SEVERITY[max_unresolved] in {SEVERITY["LOW"], SEVERITY["MEDIUM"]}:
        return ConvergenceDecision("CONVERGED_WITH_DISSENT", ("only non-blocking dissent remains",))

    return ConvergenceDecision("CONVERGED_PASS", ("complete evidence and no unresolved material finding",))
