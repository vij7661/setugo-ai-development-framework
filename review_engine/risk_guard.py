from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

RISK_ORDER = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}
MATERIALITY_ORDER = {"NONE": 0, "REVERSIBLE": 1, "MATERIAL": 2, "CONSEQUENTIAL": 3}
OPERATION_CLASSES = {
    "CHAT",
    "ANALYSIS",
    "ARTIFACT_CREATE",
    "ARTIFACT_MODIFY",
    "EXTERNAL_ACTION",
    "PRODUCTION_CHANGE",
    "RELEASE",
}


@dataclass(frozen=True)
class PlatformRiskFacts:
    operation_class: str
    risk_floor: str
    materiality_floor: str
    external_action: bool
    mutation_requested: bool
    human_approval_required: bool
    reasons: tuple[str, ...]


_OPERATION_FLOORS = {
    "CHAT": ("LOW", "NONE", False, False, False),
    "ANALYSIS": ("LOW", "REVERSIBLE", False, False, False),
    "ARTIFACT_CREATE": ("MEDIUM", "MATERIAL", False, True, False),
    "ARTIFACT_MODIFY": ("MEDIUM", "MATERIAL", False, True, False),
    "EXTERNAL_ACTION": ("HIGH", "CONSEQUENTIAL", True, True, True),
    "PRODUCTION_CHANGE": ("CRITICAL", "CONSEQUENTIAL", True, True, True),
    "RELEASE": ("CRITICAL", "CONSEQUENTIAL", True, True, True),
}


def classify_platform_facts(
    *,
    operation_class: str,
    connected_tool_capabilities: Iterable[str] = (),
    target_environment: str | None = None,
    user_declared_risk: str | None = None,
) -> PlatformRiskFacts:
    """Derive a deterministic minimum risk from platform-known consequences.

    Natural-language interpretation may propose stricter values later, but it
    cannot lower this floor. This function intentionally does not infer
    consequential authority from the model's prose.
    """
    if operation_class not in OPERATION_CLASSES:
        raise ValueError("invalid operation_class")
    base_risk, materiality, external, mutation, approval = _OPERATION_FLOORS[operation_class]
    reasons = [f"operation_class={operation_class}"]

    capabilities = {str(v).upper() for v in connected_tool_capabilities}
    consequential_caps = {"WRITE", "SEND", "DEPLOY", "MERGE", "PUBLISH", "DELETE", "PURCHASE"}
    if capabilities & consequential_caps:
        external = True
        mutation = True
        approval = True
        if RISK_ORDER[base_risk] < RISK_ORDER["HIGH"]:
            base_risk = "HIGH"
        materiality = "CONSEQUENTIAL"
        reasons.append("connected consequential tool capability")

    if target_environment is not None and target_environment.lower() in {"production", "prod", "live"}:
        base_risk = "CRITICAL"
        materiality = "CONSEQUENTIAL"
        external = True
        mutation = True
        approval = True
        reasons.append("production/live target")

    if user_declared_risk is not None:
        if user_declared_risk not in RISK_ORDER:
            raise ValueError("invalid user_declared_risk")
        if RISK_ORDER[user_declared_risk] > RISK_ORDER[base_risk]:
            base_risk = user_declared_risk
            reasons.append("user-declared higher risk")

    return PlatformRiskFacts(
        operation_class=operation_class,
        risk_floor=base_risk,
        materiality_floor=materiality,
        external_action=external,
        mutation_requested=mutation,
        human_approval_required=approval,
        reasons=tuple(reasons),
    )
