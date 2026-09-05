from __future__ import annotations

from .models import ReviewRequest
from .risk_guard import classify_platform_facts


def build_request(payload: dict) -> ReviewRequest:
    """Convert untrusted API/user payload into platform-owned request facts."""
    if not isinstance(payload, dict): raise ValueError("request payload must be an object")
    request_id = payload.get("request_id"); user_input = payload.get("user_input")
    operation_class = payload.get("operation_class", "CHAT")
    if not isinstance(request_id, str) or not request_id.strip(): raise ValueError("request_id required")
    if not isinstance(user_input, str) or not user_input.strip(): raise ValueError("user_input required")
    capabilities = payload.get("connected_tool_capabilities", [])
    if not isinstance(capabilities, list): raise ValueError("connected_tool_capabilities must be a list")
    target_environment = payload.get("target_environment")
    user_declared_risk = payload.get("risk")
    facts = classify_platform_facts(
        operation_class=str(operation_class),
        connected_tool_capabilities=[str(v) for v in capabilities],
        target_environment=None if target_environment is None else str(target_environment),
        user_declared_risk=None if user_declared_risk is None else str(user_declared_risk),
    )
    materiality = payload.get("materiality")
    order = {"NONE": 0, "REVERSIBLE": 1, "MATERIAL": 2, "CONSEQUENTIAL": 3}
    if materiality is not None:
        if materiality not in order: raise ValueError("invalid materiality")
        effective_materiality = materiality if order[materiality] > order[facts.materiality_floor] else facts.materiality_floor
    else:
        effective_materiality = facts.materiality_floor
    uncertainty = str(payload.get("uncertainty", "LOW"))
    if uncertainty not in {"LOW", "MEDIUM", "HIGH"}: raise ValueError("invalid uncertainty")
    task_type = str(payload.get("task_type", "GENERAL"))
    return ReviewRequest(
        request_id=request_id.strip(), user_input=user_input, risk=facts.risk_floor,
        materiality=effective_materiality, external_action=facts.external_action,
        mutation_requested=facts.mutation_requested,
        requirement_ambiguity=bool(payload.get("requirement_ambiguity", False)),
        evidence_complete=bool(payload.get("evidence_complete", True)), uncertainty=uncertainty,
        platform_facts={
            "operation_class": facts.operation_class, "risk_reasons": list(facts.reasons),
            "human_approval_required": facts.human_approval_required, "target_environment": target_environment,
            "connected_tool_capabilities": [str(v) for v in capabilities], "task_type": task_type,
        },
    )
