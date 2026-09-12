from __future__ import annotations

# V5 public compatibility surface: historical evidence only.
# New candidate evaluation is intentionally absent from this module.
import ecc_governance_strict as _engine

HISTORICAL_REFERENCE = "HISTORICAL_REFERENCE"


def _historical(result):
    if not isinstance(result, dict):
        return result
    out = dict(result)
    out["evaluation_class"] = HISTORICAL_REFERENCE
    out.pop("candidate_eligible", None)
    out.pop("candidate_kind", None)
    return out


def assess_control_execution(control, event, *, candidate, action_id):
    return _historical(_engine.assess_control_execution(
        control, event, candidate=candidate, action_id=action_id
    ))


def check_declared_executable_equivalence(declared, executable):
    return _historical(_engine.check_declared_executable_equivalence(declared, executable))


def qualify_role_binding(
    role,
    selected_model,
    envelope,
    required_capabilities,
    *,
    prior_binding=None,
    revalidated=True,
    require_semantic_evidence=False,
):
    return _historical(_engine.qualify_role_binding(
        role,
        selected_model,
        envelope,
        required_capabilities,
        prior_binding=prior_binding,
        revalidated=revalidated,
        require_semantic_evidence=require_semantic_evidence,
    ))


def authorize_power_activation(
    manifest,
    approval,
    requested_powers,
    *,
    role,
    requested_resources=None,
    current_sequence=None,
):
    return _historical(_engine.authorize_power_activation(
        manifest,
        approval,
        requested_powers,
        role=role,
        requested_resources=requested_resources,
        current_sequence=current_sequence,
    ))


def check_tool_configuration(expected, current):
    return _historical(_engine.check_tool_configuration(expected, current))


def classify_review_binding(binding):
    return _historical(_engine.classify_review_binding(binding))


def authorize_learning_promotion(proposal):
    return _historical(_engine.authorize_learning_promotion(proposal))
