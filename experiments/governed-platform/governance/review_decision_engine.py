from __future__ import annotations

from dataclasses import dataclass
from typing import Any

DECISIONS = {"NO_REVIEW", "REVIEW_R2", "REVIEW_R3", "HUMAN_REQUIRED"}
RISK_ORDER = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}
MATERIALITY_ORDER = {"NONE": 0, "REVERSIBLE": 1, "MATERIAL": 2, "CONSEQUENTIAL": 3}
SEVERITY_ORDER = {"NONE": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
SEMANTIC_PROBE_STATUSES = {"NOT_RUN", "STABLE", "UNCERTAIN", "REFUSAL_DOMINANT"}


@dataclass(frozen=True)
class ReviewDecision:
    decision: str
    reasons: tuple[str, ...]


def _required_bool(signals: dict[str, Any], name: str) -> bool:
    if name not in signals or not isinstance(signals[name], bool):
        raise ValueError(f"missing or invalid boolean signal: {name}")
    return signals[name]


def _optional_bool(signals: dict[str, Any], name: str, default: bool = False) -> bool:
    value = signals.get(name, default)
    if not isinstance(value, bool):
        raise ValueError(f"invalid boolean signal: {name}")
    return value


def decide_review(signals: dict[str, Any]) -> ReviewDecision:
    risk = signals.get("risk")
    materiality = signals.get("materiality")
    uncertainty = signals.get("uncertainty")
    r2_severity = signals.get("r2_finding_severity", "NONE")
    semantic_probe_status = signals.get("semantic_probe_status", "NOT_RUN")
    if risk not in RISK_ORDER:
        raise ValueError("invalid risk")
    if materiality not in MATERIALITY_ORDER:
        raise ValueError("invalid materiality")
    if uncertainty not in {"LOW", "MEDIUM", "HIGH"}:
        raise ValueError("invalid uncertainty")
    if r2_severity not in SEVERITY_ORDER:
        raise ValueError("invalid r2_finding_severity")
    if semantic_probe_status not in SEMANTIC_PROBE_STATUSES:
        raise ValueError("invalid semantic_probe_status")

    external_action = _required_bool(signals, "external_action")
    mutation_requested = _required_bool(signals, "mutation_requested")
    requirement_ambiguity = _required_bool(signals, "requirement_ambiguity")
    unresolved_contradiction = _required_bool(signals, "unresolved_contradiction")
    evidence_complete = _required_bool(signals, "evidence_complete")
    r2_completed = _required_bool(signals, "r2_completed")
    r2_material_disagreement = _required_bool(signals, "r2_material_disagreement")
    material_revision_after_r2 = _required_bool(signals, "material_revision_after_r2")
    r2_available_qualified = _required_bool(signals, "r2_available_qualified")
    r3_available_qualified = _required_bool(signals, "r3_available_qualified")
    suspected_memory_contamination = _required_bool(signals, "suspected_memory_contamination")
    review_budget_exhausted = _required_bool(signals, "review_budget_exhausted")
    counterfactual_instability = _optional_bool(signals, "counterfactual_instability")

    reasons: list[str] = []

    if requirement_ambiguity:
        return ReviewDecision("HUMAN_REQUIRED", ("authoritative requirement ambiguity",))

    if not evidence_complete and (RISK_ORDER[risk] >= RISK_ORDER["HIGH"] or external_action or mutation_requested):
        return ReviewDecision("HUMAN_REQUIRED", ("incomplete authoritative evidence for consequential task",))

    needs_r3 = (
        r2_completed
        and (
            r2_material_disagreement
            or material_revision_after_r2
            or SEVERITY_ORDER[r2_severity] >= SEVERITY_ORDER["HIGH"]
            or suspected_memory_contamination
        )
    )
    if needs_r3:
        if review_budget_exhausted:
            return ReviewDecision("HUMAN_REQUIRED", ("review unresolved at budget ceiling",))
        if not r3_available_qualified:
            return ReviewDecision("HUMAN_REQUIRED", ("required Reviewer 3 unavailable or unqualified",))
        if r2_material_disagreement:
            reasons.append("material R1/R2 disagreement")
        if material_revision_after_r2:
            reasons.append("material revision after Reviewer 2")
        if SEVERITY_ORDER[r2_severity] >= SEVERITY_ORDER["HIGH"]:
            reasons.append("high-severity Reviewer 2 finding")
        if suspected_memory_contamination:
            reasons.append("suspected reviewer memory contamination")
        return ReviewDecision("REVIEW_R3", tuple(reasons))

    semantic_escalation = semantic_probe_status in {"UNCERTAIN", "REFUSAL_DOMINANT"}
    needs_r2 = (
        RISK_ORDER[risk] >= RISK_ORDER["MEDIUM"]
        or MATERIALITY_ORDER[materiality] >= MATERIALITY_ORDER["MATERIAL"]
        or external_action
        or mutation_requested
        or unresolved_contradiction
        or uncertainty == "HIGH"
        or semantic_escalation
        or counterfactual_instability
        or suspected_memory_contamination
    )

    if needs_r2 and not r2_completed:
        if review_budget_exhausted:
            return ReviewDecision("HUMAN_REQUIRED", ("required review unavailable because budget is exhausted",))
        if not r2_available_qualified:
            return ReviewDecision("HUMAN_REQUIRED", ("required Reviewer 2 unavailable or unqualified",))
        if RISK_ORDER[risk] >= RISK_ORDER["MEDIUM"]:
            reasons.append(f"{risk.lower()}-or-higher task risk")
        if MATERIALITY_ORDER[materiality] >= MATERIALITY_ORDER["MATERIAL"]:
            reasons.append("material artifact")
        if external_action:
            reasons.append("external action requested")
        if mutation_requested:
            reasons.append("mutation requested")
        if unresolved_contradiction:
            reasons.append("unresolved contradiction")
        if uncertainty == "HIGH":
            reasons.append("high primary-model self-reported uncertainty")
        if semantic_probe_status == "UNCERTAIN":
            reasons.append("high within-model semantic uncertainty")
        if semantic_probe_status == "REFUSAL_DOMINANT":
            reasons.append("within-model probe dominated by refusal or unknown answers")
        if counterfactual_instability:
            reasons.append("controlled counterfactual cross-examination changed the material conclusion")
        if suspected_memory_contamination:
            reasons.append("suspected reviewer memory contamination")
        return ReviewDecision("REVIEW_R2", tuple(reasons))

    if r2_completed and r2_material_disagreement:
        raise AssertionError("material disagreement must not fall through")

    if unresolved_contradiction and r2_completed:
        return ReviewDecision("HUMAN_REQUIRED", ("contradiction remains unresolved after review",))

    return ReviewDecision("NO_REVIEW", ("policy permits direct finalization",))
