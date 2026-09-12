from __future__ import annotations

_ALLOWED_CAP_CLASSES = {
    "NATIVE_ENFORCEMENT",
    "ADAPTER_ENFORCEMENT",
    "INSTRUCTION_ONLY",
    "REFERENCE_ONLY",
    "UNSUPPORTED",
    "UNKNOWN",
}


def assess_control_execution(control, event, *, candidate, action_id):
    if not event:
        return {"verified": False, "status": "CONTROL_NOT_INVOKED"}
    if (
        event.get("control_id") != control.get("control_id")
        or event.get("version") != control.get("version")
        or event.get("control_digest") != control.get("digest")
    ):
        return {"verified": False, "status": "CONTROL_VERSION_MISMATCH"}
    if event.get("candidate") != candidate or event.get("action_id") != action_id:
        return {"verified": False, "status": "CONTROL_EVIDENCE_INVALID"}
    if not event.get("started") or not event.get("result_recorded"):
        return {"verified": False, "status": "CONTROL_RESULT_UNKNOWN"}
    if not event.get("execution_ok"):
        return {"verified": False, "status": "CONTROL_EXECUTION_FAILED"}
    if not event.get("input_digest") or not event.get("result_digest") or not event.get("invocation_id"):
        return {"verified": False, "status": "CONTROL_EVIDENCE_INVALID"}
    return {"verified": True, "status": "VERIFIED"}


def check_declared_executable_equivalence(declared, executable):
    keys = ("mode", "on_internal_error", "candidate_binding")
    equivalent = all(declared.get(k) == executable.get(k) for k in keys)
    return {
        "equivalent": equivalent,
        "status": "EQUIVALENT" if equivalent else "ENFORCEMENT_MISMATCH",
    }


def qualify_role_binding(role, selected_model, envelope, required_capabilities):
    caps = envelope.get("capabilities")
    if not isinstance(caps, dict):
        return {"eligible": False, "status": "HARNESS_CAPABILITY_UNKNOWN"}
    for capability, required in required_capabilities.items():
        actual = caps.get(capability)
        if actual is None or actual == "UNKNOWN":
            return {"eligible": False, "status": "HARNESS_CAPABILITY_UNKNOWN"}
        if required == "NATIVE_ENFORCEMENT" and actual != "NATIVE_ENFORCEMENT":
            return {"eligible": False, "status": "HARNESS_CAPABILITY_INSUFFICIENT"}
        if required == "ADAPTER_ENFORCEMENT" and actual not in {"NATIVE_ENFORCEMENT", "ADAPTER_ENFORCEMENT"}:
            return {"eligible": False, "status": "HARNESS_CAPABILITY_INSUFFICIENT"}
        if actual not in _ALLOWED_CAP_CLASSES:
            return {"eligible": False, "status": "HARNESS_CAPABILITY_UNKNOWN"}
    return {
        "eligible": True,
        "status": "ROLE_BINDING_ELIGIBLE",
        "role": role,
        "selected_model": selected_model,
        "harness_id": envelope.get("harness_id"),
        "runtime_version": envelope.get("runtime_version"),
        "config_digest": envelope.get("config_digest"),
    }


def authorize_power_activation(manifest, approval, requested_powers, *, role):
    if manifest.get("revoked"):
        return {"authorized": False, "status": "ACTIVATION_REVOKED"}
    if not approval or not approval.get("approved"):
        return {"authorized": False, "status": "ACTIVATION_NOT_APPROVED"}
    if (
        approval.get("manifest_digest") != manifest.get("digest")
        or approval.get("role") != role
        or manifest.get("role") != role
    ):
        return {"authorized": False, "status": "ACTIVATION_BINDING_MISMATCH"}
    requested = set(requested_powers or [])
    manifest_powers = set(manifest.get("powers") or [])
    approved = set(approval.get("approved_powers") or [])
    if not requested.issubset(manifest_powers) or not requested.issubset(approved):
        return {"authorized": False, "status": "ACTIVATION_SCOPE_EXCEEDED"}
    return {"authorized": True, "status": "ACTIVATION_ALLOWED", "powers": sorted(requested)}


def check_tool_configuration(expected, current):
    identity_fields = (
        "tool_id",
        "harness_id",
        "transport",
        "endpoint",
        "argv_digest",
        "permission_profile",
        "credential_profile",
        "canonical_digest",
    )
    if not expected or not current or any(k not in current for k in identity_fields):
        return {"current": False, "status": "TOOL_CONFIG_UNKNOWN", "stale_dependents": True}
    drift = any(expected.get(k) != current.get(k) for k in identity_fields)
    if drift:
        return {"current": False, "status": "TOOL_CONFIG_DRIFT", "stale_dependents": True}
    return {"current": True, "status": "TOOL_CONFIG_CURRENT", "stale_dependents": False}


def classify_review_binding(binding):
    if not binding.get("packet_current"):
        return {
            "status": "REVIEW_BINDING_STALE",
            "provider_relationship": "PROVIDER_IDENTITY_UNKNOWN",
            "manual_review_threshold_contribution": 0,
        }
    selected = binding.get("selected_provider")
    returned = binding.get("returned_provider")
    gateway = binding.get("gateway")
    if gateway and not returned:
        relationship = "GATEWAY_RELATIONSHIP_UNVERIFIED"
    elif selected and returned and selected == returned:
        relationship = "SAME_PROVIDER_CONFIRMED"
    elif selected and returned and selected != returned:
        relationship = "DIFFERENT_PROVIDER_CONFIRMED"
    else:
        relationship = "PROVIDER_IDENTITY_UNKNOWN"
    evidence_class = binding.get("evidence_class")
    manual_contribution = 1 if evidence_class == "INDEPENDENT_MANUAL_REVIEW" else 0
    status = "REVIEW_BINDING_VALID"
    if not binding.get("context_isolation_evidenced"):
        status = "REVIEW_ISOLATION_INSUFFICIENT_EVIDENCE"
    return {
        "status": status,
        "provider_relationship": relationship,
        "manual_review_threshold_contribution": manual_contribution,
        "reviewer_slot": binding.get("reviewer_slot"),
    }


def authorize_learning_promotion(proposal):
    if proposal.get("artifact_digest") != proposal.get("reviewed_digest"):
        return {"promotable": False, "status": "LEARNING_PROPOSAL_CHANGED_AFTER_REVIEW"}
    if proposal.get("parent_retracted"):
        return {"promotable": False, "status": "LEARNING_PROPOSAL_REASSESSMENT_REQUIRED"}
    if not (
        proposal.get("source_verified")
        and proposal.get("independent_support")
        and proposal.get("governed_approval")
    ):
        return {"promotable": False, "status": "LEARNING_PROPOSAL_NOT_PROMOTABLE"}
    return {"promotable": True, "status": "LEARNING_PROPOSAL_PROMOTABLE"}
