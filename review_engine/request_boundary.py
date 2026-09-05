from __future__ import annotations

from dataclasses import dataclass

from .models import ReviewRequest
from .risk_guard import MATERIALITY_ORDER, RISK_ORDER, classify_platform_facts


@dataclass(frozen=True)
class PlatformExecutionEnvelope:
    """Trusted execution facts supplied by the application/platform boundary.

    Arbitrary HTTP/CLI payload fields are declarations and cannot lower this
    envelope. The v0.1 review service uses a review-only/no-tool envelope.
    """

    operation_class: str = "ANALYSIS"
    connected_tool_capabilities: tuple[str, ...] = ()
    target_environment: str | None = None
    task_type: str = "GENERAL"


def _max_value(a: str, b: str, order: dict[str, int]) -> str:
    if a not in order or b not in order:
        raise ValueError("invalid ordered signal")
    return a if order[a] >= order[b] else b


def _text_consequence_hints(user_input: str) -> tuple[str, str, bool, tuple[str, ...]]:
    """Conservative deterministic consequence hints from the actual request text.

    This is deliberately a floor, not a semantic authority classifier. It
    catches obvious consequential wording but cannot prove that all hidden or
    euphemistic consequential intent has been found.
    """
    text = " ".join(user_input.lower().split())
    production_terms = ("production", "prod ", "live environment", "go live")
    release_terms = ("deploy", "release", "merge", "publish", "send", "delete", "purchase", "ship")

    if any(term in text for term in production_terms):
        return "CRITICAL", "CONSEQUENTIAL", True, ("request text references production/live consequences",)
    if any(term in text for term in release_terms):
        return "HIGH", "CONSEQUENTIAL", True, ("request text references consequential mutation/action",)
    return "LOW", "NONE", False, ()


def build_request(payload: dict, *, platform_envelope: PlatformExecutionEnvelope | None = None) -> ReviewRequest:
    """Convert an untrusted request into a governed request with source provenance.

    Trust model:
    - `platform_envelope` is supplied by application code, not request JSON.
    - caller-supplied operation/tool/target/risk/materiality fields are declarations
      that may only raise conservatism.
    - deterministic text hints may also raise conservatism.
    - task type used for qualification comes from the trusted envelope, not the caller.
    """
    if not isinstance(payload, dict):
        raise ValueError("request payload must be an object")
    envelope = platform_envelope or PlatformExecutionEnvelope()

    request_id = payload.get("request_id")
    user_input = payload.get("user_input")
    if not isinstance(request_id, str) or not request_id.strip():
        raise ValueError("request_id required")
    if not isinstance(user_input, str) or not user_input.strip():
        raise ValueError("user_input required")

    # Trusted platform envelope. In v0.1 the actual service can review but cannot
    # execute external actions, so its default operation is ANALYSIS with no tools.
    platform = classify_platform_facts(
        operation_class=envelope.operation_class,
        connected_tool_capabilities=envelope.connected_tool_capabilities,
        target_environment=envelope.target_environment,
    )

    # Caller declarations may increase the floor but are never described as
    # independently verified platform facts.
    declared_operation = str(payload.get("operation_class", "CHAT"))
    declared_capabilities = payload.get("connected_tool_capabilities", [])
    if not isinstance(declared_capabilities, list):
        raise ValueError("connected_tool_capabilities must be a list")
    declared_target = payload.get("target_environment")
    declared_risk = payload.get("risk")
    caller = classify_platform_facts(
        operation_class=declared_operation,
        connected_tool_capabilities=[str(v) for v in declared_capabilities],
        target_environment=None if declared_target is None else str(declared_target),
        user_declared_risk=None if declared_risk is None else str(declared_risk),
    )

    text_risk, text_materiality, text_mutation, text_reasons = _text_consequence_hints(user_input)

    risk_floor = _max_value(platform.risk_floor, caller.risk_floor, RISK_ORDER)
    risk_floor = _max_value(risk_floor, text_risk, RISK_ORDER)
    materiality_floor = _max_value(platform.materiality_floor, caller.materiality_floor, MATERIALITY_ORDER)
    materiality_floor = _max_value(materiality_floor, text_materiality, MATERIALITY_ORDER)

    declared_materiality = payload.get("materiality")
    if declared_materiality is not None:
        if declared_materiality not in MATERIALITY_ORDER:
            raise ValueError("invalid materiality")
        materiality_floor = _max_value(materiality_floor, str(declared_materiality), MATERIALITY_ORDER)

    uncertainty = str(payload.get("uncertainty", "LOW"))
    if uncertainty not in {"LOW", "MEDIUM", "HIGH"}:
        raise ValueError("invalid uncertainty")

    external_action = bool(platform.external_action or caller.external_action)
    mutation_requested = bool(platform.mutation_requested or caller.mutation_requested or text_mutation)
    human_approval_required = bool(platform.human_approval_required or caller.human_approval_required)

    declared_task_type = str(payload.get("task_type", "GENERAL"))
    return ReviewRequest(
        request_id=request_id.strip(),
        user_input=user_input,
        risk=risk_floor,
        materiality=materiality_floor,
        external_action=external_action,
        mutation_requested=mutation_requested,
        requirement_ambiguity=bool(payload.get("requirement_ambiguity", False)),
        evidence_complete=bool(payload.get("evidence_complete", True)),
        uncertainty=uncertainty,
        platform_facts={
            "operation_class": platform.operation_class,
            "platform_operation_class": platform.operation_class,
            "platform_target_environment": envelope.target_environment,
            "platform_connected_tool_capabilities": list(envelope.connected_tool_capabilities),
            "task_type": envelope.task_type,
            "declared_operation_class": declared_operation,
            "declared_target_environment": declared_target,
            "declared_connected_tool_capabilities": [str(v) for v in declared_capabilities],
            "declared_task_type": declared_task_type,
            "risk_reasons": list(platform.reasons)
            + [f"caller declaration: {reason}" for reason in caller.reasons]
            + list(text_reasons),
            "human_approval_required": human_approval_required,
            "trust_model": {
                "platform_envelope": "trusted_application_boundary",
                "caller_fields": "untrusted_declarations_escalation_only",
                "text_hints": "deterministic_conservative_floor_not_complete_semantic_classification",
            },
        },
    )
