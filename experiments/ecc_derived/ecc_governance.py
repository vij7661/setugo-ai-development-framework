from __future__ import annotations

_ALLOWED_CAP_CLASSES = {
    "NATIVE_ENFORCEMENT",
    "ADAPTER_ENFORCEMENT",
    "INSTRUCTION_ONLY",
    "REFERENCE_ONLY",
    "UNSUPPORTED",
    "UNKNOWN",
}

_CAPABILITY_RANK = {
    "UNKNOWN": 0,
    "UNSUPPORTED": 0,
    "REFERENCE_ONLY": 1,
    "INSTRUCTION_ONLY": 2,
    "ADAPTER_ENFORCEMENT": 3,
    "NATIVE_ENFORCEMENT": 4,
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
    if event.get("script_present", True) is False:
        return {"verified": False, "status": "CONTROL_EXECUTION_FAILED"}
    if event.get("input_valid", True) is False:
        return {"verified": False, "status": "CONTROL_EVIDENCE_INVALID"}
    if event.get("authoritative", True) is False or event.get("evidence_integrity", True) is False:
        return {"verified": False, "status": "CONTROL_EVIDENCE_INVALID"}
    if not event.get("started") or not event.get("result_recorded"):
        return {"verified": False, "status": "CONTROL_RESULT_UNKNOWN"}
    if event.get("acknowledgement") == "LOST" and not event.get("reconciled", False):
        return {"verified": False, "status": "CONTROL_RESULT_UNKNOWN", "invocation_id": event.get("invocation_id")}
    if not event.get("execution_ok"):
        return {"verified": False, "status": "CONTROL_EXECUTION_FAILED"}
    if not event.get("input_digest") or not event.get("result_digest") or not event.get("invocation_id"):
        return {"verified": False, "status": "CONTROL_EVIDENCE_INVALID"}
    if event.get("decision") == "DENY":
        return {
            "verified": True,
            "allowed": False,
            "status": "VERIFIED_DENY",
            "invocation_id": event.get("invocation_id"),
        }
    return {
        "verified": True,
        "allowed": True,
        "status": "VERIFIED",
        "invocation_id": event.get("invocation_id"),
    }


def check_declared_executable_equivalence(declared, executable):
    comparison_keys = (
        "mode",
        "on_internal_error",
        "candidate_binding",
        "disable_paths",
        "contract_version",
        "profile_digest",
        "scope",
    )
    equivalent = True
    for key in comparison_keys:
        if key in declared or key in executable:
            if declared.get(key) != executable.get(key):
                equivalent = False
                break

    paths = executable.get("paths") or []
    if equivalent and paths:
        for path in paths:
            for key in ("mode", "on_internal_error", "candidate_binding"):
                if path.get(key) != declared.get(key):
                    equivalent = False
                    break
            if not equivalent:
                break

    return {
        "equivalent": equivalent,
        "status": "EQUIVALENT" if equivalent else "ENFORCEMENT_MISMATCH",
    }


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
    if not envelope or envelope.get("complete", True) is False:
        return {"eligible": False, "status": "HARNESS_CAPABILITY_UNKNOWN"}

    if (
        envelope.get("qualified_runtime_version") is not None
        and envelope.get("runtime_version") != envelope.get("qualified_runtime_version")
    ) or (
        envelope.get("qualified_config_digest") is not None
        and envelope.get("config_digest") != envelope.get("qualified_config_digest")
    ):
        return {"eligible": False, "status": "HARNESS_QUALIFICATION_STALE"}

    if prior_binding and not revalidated:
        changed = (
            prior_binding.get("role") != role
            or prior_binding.get("selected_model") != selected_model
            or prior_binding.get("harness_id") != envelope.get("harness_id")
        )
        if changed:
            return {"eligible": False, "status": "ROLE_BINDING_CHANGE_REVALIDATION_REQUIRED"}

    caps = envelope.get("capabilities")
    if not isinstance(caps, dict):
        return {"eligible": False, "status": "HARNESS_CAPABILITY_UNKNOWN"}

    semantic = envelope.get("semantic_evidence") or {}
    for capability, required in required_capabilities.items():
        actual = caps.get(capability)
        if actual is None or actual == "UNKNOWN" or actual not in _ALLOWED_CAP_CLASSES:
            return {"eligible": False, "status": "HARNESS_CAPABILITY_UNKNOWN"}
        if _CAPABILITY_RANK.get(actual, 0) < _CAPABILITY_RANK.get(required, 999):
            return {"eligible": False, "status": "HARNESS_CAPABILITY_INSUFFICIENT"}
        if require_semantic_evidence and not semantic.get(capability):
            return {"eligible": False, "status": "HARNESS_CAPABILITY_UNVERIFIED"}

    return {
        "eligible": True,
        "status": "ROLE_BINDING_ELIGIBLE",
        "role": role,
        "selected_model": selected_model,
        "harness_id": envelope.get("harness_id"),
        "runtime_version": envelope.get("runtime_version"),
        "config_digest": envelope.get("config_digest"),
    }


def authorize_power_activation(
    manifest,
    approval,
    requested_powers,
    *,
    role,
    requested_resources=None,
    current_sequence=None,
):
    if manifest.get("revoked"):
        return {"authorized": False, "status": "ACTIVATION_REVOKED"}
    expiry = manifest.get("expires_sequence")
    if current_sequence is not None and expiry is not None and current_sequence >= expiry:
        return {"authorized": False, "status": "ACTIVATION_EXPIRED"}
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

    requested_res = set(requested_resources or [])
    manifest_res = set(manifest.get("resources") or [])
    approved_res = set(approval.get("approved_resources") or [])
    if requested_res and (
        not requested_res.issubset(manifest_res)
        or not requested_res.issubset(approved_res)
    ):
        return {"authorized": False, "status": "ACTIVATION_RESOURCE_SCOPE_EXCEEDED"}

    return {
        "authorized": True,
        "status": "ACTIVATION_ALLOWED",
        "powers": sorted(requested),
        "resources": sorted(requested_res),
    }


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
    if not expected or not current or current.get("read_ok", True) is False:
        return {"current": False, "status": "TOOL_CONFIG_UNKNOWN", "stale_dependents": True}
    if any(k not in current for k in identity_fields):
        return {"current": False, "status": "TOOL_CONFIG_UNKNOWN", "stale_dependents": True}

    fields = list(identity_fields)
    if "semantic_digest" in expected or "semantic_digest" in current:
        fields.append("semantic_digest")
    drift = any(expected.get(k) != current.get(k) for k in fields)
    if drift:
        return {"current": False, "status": "TOOL_CONFIG_DRIFT", "stale_dependents": True}
    return {"current": True, "status": "TOOL_CONFIG_CURRENT", "stale_dependents": False}


def _manual_threshold_contribution(binding):
    # The evidence-class label alone is not enough. A real qualifying policy must
    # validate human/manual attestation separately.
    return 1 if (
        binding.get("evidence_class") == "INDEPENDENT_MANUAL_REVIEW"
        and binding.get("manual_attestation_valid") is True
    ) else 0


def classify_review_binding(binding):
    contribution = _manual_threshold_contribution(binding)
    if not binding.get("packet_current"):
        return {
            "status": "REVIEW_BINDING_STALE",
            "provider_relationship": "PROVIDER_IDENTITY_UNKNOWN",
            "manual_review_threshold_contribution": 0,
        }
    if binding.get("packet_digest") != binding.get("consented_packet_digest", binding.get("packet_digest")):
        return {
            "status": "REVIEW_EGRESS_BINDING_MISMATCH",
            "provider_relationship": "PROVIDER_IDENTITY_UNKNOWN",
            "manual_review_threshold_contribution": 0,
        }
    if (
        binding.get("evidence_bound_slot", binding.get("reviewer_slot")) != binding.get("reviewer_slot")
        or binding.get("role_binding_model", binding.get("selected_model")) != binding.get("selected_model")
    ):
        return {
            "status": "REVIEW_ROLE_BINDING_MISMATCH",
            "provider_relationship": "PROVIDER_IDENTITY_UNKNOWN",
            "manual_review_threshold_contribution": 0,
        }
    permitted = set(binding.get("permitted_data_classes") or [])
    packet_classes = set(binding.get("packet_data_classes") or [])
    if packet_classes and not packet_classes.issubset(permitted):
        return {
            "status": "REVIEW_EGRESS_SCOPE_EXCEEDED",
            "provider_relationship": "PROVIDER_IDENTITY_UNKNOWN",
            "manual_review_threshold_contribution": 0,
        }
    if binding.get("transport_enabled", True) is False:
        return {
            "status": "REVIEW_TRANSPORT_DISABLED",
            "provider_relationship": "PROVIDER_IDENTITY_UNKNOWN",
            "manual_review_threshold_contribution": 0,
        }
    if binding.get("transport_ok", True) is False:
        return {
            "status": "REVIEW_TRANSPORT_FAILED",
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

    status = "REVIEW_BINDING_VALID"
    if not binding.get("context_isolation_evidenced"):
        status = "REVIEW_ISOLATION_INSUFFICIENT_EVIDENCE"
        contribution = 0

    return {
        "status": status,
        "provider_relationship": relationship,
        "manual_review_threshold_contribution": contribution,
        "reviewer_slot": binding.get("reviewer_slot"),
    }


def authorize_learning_promotion(proposal):
    scope_preserved = proposal.get("target_scope", proposal.get("scope")) == proposal.get("scope")
    advisory_allowed = not proposal.get("stale", False) and not proposal.get("conflicts_governed", False)

    if proposal.get("artifact_digest") != proposal.get("reviewed_digest"):
        return {
            "promotable": False,
            "status": "LEARNING_PROPOSAL_CHANGED_AFTER_REVIEW",
            "advisory_allowed": advisory_allowed,
            "scope_preserved": scope_preserved,
        }
    if proposal.get("prior_rejection") and not proposal.get("history_preserved", False):
        return {
            "promotable": False,
            "status": "LEARNING_HISTORY_INTEGRITY_REQUIRED",
            "advisory_allowed": False,
            "scope_preserved": scope_preserved,
        }
    if not scope_preserved:
        return {
            "promotable": False,
            "status": "LEARNING_SCOPE_WIDENING_REJECTED",
            "advisory_allowed": True,
            "scope_preserved": False,
        }
    if proposal.get("requested_authority") and not proposal.get("explicit_authority_grant"):
        return {
            "promotable": False,
            "status": "LEARNING_AUTHORITY_NOT_GRANTED",
            "advisory_allowed": True,
            "scope_preserved": True,
        }
    if proposal.get("stale") or proposal.get("conflicts_governed"):
        return {
            "promotable": False,
            "status": "LEARNING_PROPOSAL_STALE_OR_CONFLICTING",
            "advisory_allowed": False,
            "scope_preserved": scope_preserved,
        }
    if proposal.get("parent_retracted"):
        return {
            "promotable": False,
            "status": "LEARNING_PROPOSAL_REASSESSMENT_REQUIRED",
            "advisory_allowed": True,
            "scope_preserved": scope_preserved,
            "independent_support_preserved": bool(proposal.get("independent_support")),
        }
    if not (
        proposal.get("source_verified")
        and proposal.get("independent_support")
        and proposal.get("governed_approval")
    ):
        return {
            "promotable": False,
            "status": "LEARNING_PROPOSAL_NOT_PROMOTABLE",
            "advisory_allowed": advisory_allowed,
            "scope_preserved": scope_preserved,
        }
    return {
        "promotable": True,
        "status": "LEARNING_PROPOSAL_PROMOTABLE",
        "advisory_allowed": True,
        "scope_preserved": scope_preserved,
    }
