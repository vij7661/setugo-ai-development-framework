from __future__ import annotations

import functools
import hashlib
import json

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

_REQUIREMENT_CANDIDATE = "REQUIREMENT_CANDIDATE"
_HISTORICAL_REFERENCE = "HISTORICAL_REFERENCE"


def _sha256_json(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _strict(result, requirement_candidate):
    if requirement_candidate:
        result = dict(result)
        result["evaluation_class"] = _REQUIREMENT_CANDIDATE
    return result


def assess_control_execution(control, event, *, candidate, action_id, requirement_candidate=False):
    if not event:
        return _strict({"verified": False, "status": "CONTROL_NOT_INVOKED"}, requirement_candidate)
    if (
        event.get("control_id") != control.get("control_id")
        or event.get("version") != control.get("version")
        or event.get("control_digest") != control.get("digest")
    ):
        return _strict({"verified": False, "status": "CONTROL_VERSION_MISMATCH"}, requirement_candidate)
    if event.get("candidate") != candidate or event.get("action_id") != action_id:
        return _strict({"verified": False, "status": "CONTROL_EVIDENCE_INVALID"}, requirement_candidate)
    if event.get("script_present", True) is False:
        return _strict({"verified": False, "status": "CONTROL_EXECUTION_FAILED"}, requirement_candidate)
    if event.get("input_valid", True) is False:
        return _strict({"verified": False, "status": "CONTROL_EVIDENCE_INVALID"}, requirement_candidate)
    if event.get("authoritative", True) is False or event.get("evidence_integrity", True) is False:
        return _strict({"verified": False, "status": "CONTROL_EVIDENCE_INVALID"}, requirement_candidate)

    if requirement_candidate:
        if "attestation_source" not in event or "attestation_valid" not in event:
            return _strict({"verified": False, "status": "CONTROL_ATTESTATION_REQUIRED"}, True)
        if (
            event.get("attestation_source") != "PLATFORM_ENFORCEMENT_POINT"
            or event.get("attestation_valid") is not True
        ):
            return _strict({"verified": False, "status": "CONTROL_ATTESTATION_UNTRUSTED"}, True)
        required_binding = (
            "verified_action_sequence",
            "executed_action_sequence",
            "process_identity",
            "expected_process_identity",
        )
        if any(key not in event for key in required_binding):
            return _strict({"verified": False, "status": "CONTROL_ACTION_BINDING_REQUIRED"}, True)
    else:
        attestation_fields_present = (
            "attestation_source" in event or "attestation_valid" in event
        )
        if attestation_fields_present:
            if (
                event.get("attestation_source") != "PLATFORM_ENFORCEMENT_POINT"
                or event.get("attestation_valid") is not True
            ):
                return {"verified": False, "status": "CONTROL_ATTESTATION_UNTRUSTED"}

    if (
        "verified_action_sequence" in event
        or "executed_action_sequence" in event
    ) and event.get("verified_action_sequence") != event.get("executed_action_sequence"):
        return _strict({"verified": False, "status": "CONTROL_TOCTOU_MISMATCH"}, requirement_candidate)

    if (
        "process_identity" in event
        or "expected_process_identity" in event
    ) and event.get("process_identity") != event.get("expected_process_identity"):
        return _strict({"verified": False, "status": "CONTROL_PROCESS_IDENTITY_MISMATCH"}, requirement_candidate)

    if not event.get("started") or not event.get("result_recorded"):
        return _strict({"verified": False, "status": "CONTROL_RESULT_UNKNOWN"}, requirement_candidate)
    if event.get("acknowledgement") == "LOST" and not event.get("reconciled", False):
        return _strict({
            "verified": False,
            "status": "CONTROL_RESULT_UNKNOWN",
            "invocation_id": event.get("invocation_id"),
        }, requirement_candidate)
    if not event.get("execution_ok"):
        return _strict({"verified": False, "status": "CONTROL_EXECUTION_FAILED"}, requirement_candidate)
    if not event.get("input_digest") or not event.get("result_digest") or not event.get("invocation_id"):
        return _strict({"verified": False, "status": "CONTROL_EVIDENCE_INVALID"}, requirement_candidate)
    if event.get("decision") == "DENY":
        return _strict({
            "verified": True,
            "allowed": False,
            "status": "VERIFIED_DENY",
            "invocation_id": event.get("invocation_id"),
        }, requirement_candidate)
    return _strict({
        "verified": True,
        "allowed": True,
        "status": "VERIFIED",
        "invocation_id": event.get("invocation_id"),
    }, requirement_candidate)


def check_declared_executable_equivalence(declared, executable, *, requirement_candidate=False):
    if requirement_candidate:
        if executable.get("machine_verified") is not True:
            return _strict({"equivalent": False, "status": "EXECUTABLE_PROFILE_REQUIRED"}, True)
        mandatory_runtime_fields = (
            "runtime_mode",
            "runtime_on_internal_error",
            "generated_doc_mode",
            "discovered_disable_flags",
        )
        if any(key not in executable for key in mandatory_runtime_fields):
            return _strict({"equivalent": False, "status": "EXECUTABLE_PROFILE_REQUIRED"}, True)
        if not isinstance(executable.get("paths"), list) or not executable.get("paths"):
            return _strict({"equivalent": False, "status": "EXECUTABLE_PATHS_REQUIRED"}, True)
        if any(path.get("machine_verified") is not True for path in executable["paths"]):
            return _strict({"equivalent": False, "status": "EXECUTABLE_PATHS_REQUIRED"}, True)
    elif executable.get("machine_verified") is False:
        return {"equivalent": False, "status": "EXECUTABLE_PROFILE_UNVERIFIED"}

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

    if equivalent and "runtime_on_internal_error" in executable:
        equivalent = executable.get("runtime_on_internal_error") == declared.get("on_internal_error")
    if equivalent and "runtime_mode" in executable:
        equivalent = executable.get("runtime_mode") == declared.get("mode")
    if equivalent and "generated_doc_mode" in executable and "runtime_mode" in executable:
        if executable.get("generated_doc_mode") != executable.get("runtime_mode"):
            equivalent = False

    if equivalent and "discovered_disable_flags" in executable:
        declared_disable = set(declared.get("disable_paths") or [])
        discovered_disable = set(executable.get("discovered_disable_flags") or [])
        if not discovered_disable.issubset(declared_disable):
            equivalent = False

    paths = executable.get("paths") or []
    if equivalent and paths:
        for path in paths:
            for key in ("mode", "on_internal_error", "candidate_binding"):
                if path.get(key) != declared.get(key):
                    equivalent = False
                    break
            if path.get("machine_verified") is False:
                equivalent = False
            if not equivalent:
                break

    return _strict({
        "equivalent": equivalent,
        "status": "EQUIVALENT" if equivalent else "ENFORCEMENT_MISMATCH",
    }, requirement_candidate)


def qualify_role_binding(
    role,
    selected_model,
    envelope,
    required_capabilities,
    *,
    prior_binding=None,
    revalidated=True,
    require_semantic_evidence=False,
    requirement_candidate=False,
):
    if not envelope or envelope.get("complete", True) is False:
        return _strict({"eligible": False, "status": "HARNESS_CAPABILITY_UNKNOWN"}, requirement_candidate)

    if requirement_candidate:
        required_identity = (
            "identity_attested",
            "identity_attestation_source",
            "runtime_identity_digest",
        )
        if any(key not in envelope for key in required_identity):
            return _strict({"eligible": False, "status": "HARNESS_IDENTITY_ATTESTATION_REQUIRED"}, True)
        if envelope.get("identity_attested") is not True:
            return _strict({"eligible": False, "status": "HARNESS_IDENTITY_UNATTESTED"}, True)
        if envelope.get("identity_attestation_source") != "PLATFORM_HARNESS_REGISTRY":
            return _strict({"eligible": False, "status": "HARNESS_IDENTITY_UNATTESTED"}, True)
        if any(not isinstance(required, dict) for required in required_capabilities.values()):
            return _strict({"eligible": False, "status": "HARNESS_CAPABILITY_MATRIX_REQUIRED"}, True)
    elif envelope.get("identity_attested") is False:
        return {"eligible": False, "status": "HARNESS_IDENTITY_UNATTESTED"}

    if (
        envelope.get("qualified_runtime_version") is not None
        and envelope.get("runtime_version") != envelope.get("qualified_runtime_version")
    ) or (
        envelope.get("qualified_config_digest") is not None
        and envelope.get("config_digest") != envelope.get("qualified_config_digest")
    ):
        return _strict({"eligible": False, "status": "HARNESS_QUALIFICATION_STALE"}, requirement_candidate)

    if prior_binding and not revalidated:
        changed = (
            prior_binding.get("role") != role
            or prior_binding.get("selected_model") != selected_model
            or prior_binding.get("harness_id") != envelope.get("harness_id")
        )
        if changed:
            return _strict({"eligible": False, "status": "ROLE_BINDING_CHANGE_REVALIDATION_REQUIRED"}, requirement_candidate)

    caps = envelope.get("capabilities")
    if not isinstance(caps, dict):
        return _strict({"eligible": False, "status": "HARNESS_CAPABILITY_UNKNOWN"}, requirement_candidate)

    semantic = envelope.get("semantic_evidence") or {}
    for capability, required in required_capabilities.items():
        actual = caps.get(capability)
        if actual is None or actual == "UNKNOWN" or actual not in _ALLOWED_CAP_CLASSES:
            return _strict({"eligible": False, "status": "HARNESS_CAPABILITY_UNKNOWN"}, requirement_candidate)

        if isinstance(required, dict):
            allowed = set(required.get("allowed_classes") or [])
            if not allowed or actual not in allowed:
                return _strict({"eligible": False, "status": "HARNESS_CAPABILITY_INSUFFICIENT"}, requirement_candidate)
            semantic_required = required.get("semantic_evidence_required", False)
        else:
            if _CAPABILITY_RANK.get(actual, 0) < _CAPABILITY_RANK.get(required, 999):
                return {"eligible": False, "status": "HARNESS_CAPABILITY_INSUFFICIENT"}
            semantic_required = require_semantic_evidence

        if (require_semantic_evidence or semantic_required) and not semantic.get(capability):
            return _strict({"eligible": False, "status": "HARNESS_CAPABILITY_UNVERIFIED"}, requirement_candidate)

    return _strict({
        "eligible": True,
        "status": "ROLE_BINDING_ELIGIBLE",
        "role": role,
        "selected_model": selected_model,
        "harness_id": envelope.get("harness_id"),
        "runtime_version": envelope.get("runtime_version"),
        "config_digest": envelope.get("config_digest"),
    }, requirement_candidate)


def authorize_power_activation(
    manifest,
    approval,
    requested_powers,
    *,
    role,
    requested_resources=None,
    current_sequence=None,
    requirement_candidate=False,
):
    if manifest.get("revoked"):
        return _strict({"authorized": False, "status": "ACTIVATION_REVOKED"}, requirement_candidate)
    revoked_at = manifest.get("revoked_at_sequence")
    if current_sequence is not None and revoked_at is not None and current_sequence >= revoked_at:
        return _strict({"authorized": False, "status": "ACTIVATION_REVOKED"}, requirement_candidate)
    expiry = manifest.get("expires_sequence")
    if current_sequence is not None and expiry is not None and current_sequence >= expiry:
        return _strict({"authorized": False, "status": "ACTIVATION_EXPIRED"}, requirement_candidate)
    if not approval or not approval.get("approved"):
        return _strict({"authorized": False, "status": "ACTIVATION_NOT_APPROVED"}, requirement_candidate)
    if (
        approval.get("manifest_digest") != manifest.get("digest")
        or approval.get("role") != role
        or manifest.get("role") != role
    ):
        return _strict({"authorized": False, "status": "ACTIVATION_BINDING_MISMATCH"}, requirement_candidate)

    if requirement_candidate:
        required_authority = (
            "principal_authenticated",
            "authority_grant_valid",
            "project_id",
        )
        if any(key not in approval for key in required_authority) or "project_id" not in manifest:
            return _strict({"authorized": False, "status": "ACTIVATION_AUTHORITY_REQUIRED"}, True)
        if approval.get("principal_authenticated") is not True or approval.get("authority_grant_valid") is not True:
            return _strict({"authorized": False, "status": "ACTIVATION_AUTHORITY_INVALID"}, True)
        if current_sequence is None or "approval_sequence" not in approval:
            return _strict({"authorized": False, "status": "ACTIVATION_SEQUENCE_BINDING_REQUIRED"}, True)
    else:
        strict_activation = (
            "project_id" in manifest
            or "principal_authenticated" in approval
            or "authority_grant_valid" in approval
        )
        if strict_activation and not (
            approval.get("principal_authenticated") is True
            and approval.get("authority_grant_valid") is True
        ):
            return {"authorized": False, "status": "ACTIVATION_AUTHORITY_INVALID"}

    if "project_id" in manifest or "project_id" in approval:
        if manifest.get("project_id") != approval.get("project_id"):
            return _strict({"authorized": False, "status": "ACTIVATION_PROJECT_MISMATCH"}, requirement_candidate)

    if current_sequence is not None and approval.get("approval_sequence") is not None:
        if approval.get("approval_sequence") > current_sequence:
            return _strict({"authorized": False, "status": "ACTIVATION_SEQUENCE_INVALID"}, requirement_candidate)

    requested = set(requested_powers or [])
    manifest_powers = set(manifest.get("powers") or [])
    approved = set(approval.get("approved_powers") or [])
    if not requested.issubset(manifest_powers) or not requested.issubset(approved):
        return _strict({"authorized": False, "status": "ACTIVATION_SCOPE_EXCEEDED"}, requirement_candidate)

    requested_res = set(requested_resources or [])
    manifest_res = set(manifest.get("resources") or [])
    approved_res = set(approval.get("approved_resources") or [])
    if requested_res and (
        not requested_res.issubset(manifest_res)
        or not requested_res.issubset(approved_res)
    ):
        return _strict({"authorized": False, "status": "ACTIVATION_RESOURCE_SCOPE_EXCEEDED"}, requirement_candidate)

    return _strict({
        "authorized": True,
        "status": "ACTIVATION_ALLOWED",
        "powers": sorted(requested),
        "resources": sorted(requested_res),
    }, requirement_candidate)


def _v2_config_material(cfg):
    return {
        "tool_id": cfg.get("tool_id"),
        "harness_id": cfg.get("harness_id"),
        "transport": cfg.get("transport"),
        "endpoint": cfg.get("endpoint"),
        "argv": cfg.get("argv"),
        "permission_profile": cfg.get("permission_profile"),
        "credential_profile_fingerprint": cfg.get("credential_profile_fingerprint"),
    }


def check_tool_configuration(expected, current, *, requirement_candidate=False):
    if not expected or not current or current.get("read_ok", True) is False:
        return _strict({"current": False, "status": "TOOL_CONFIG_UNKNOWN", "stale_dependents": True}, requirement_candidate)

    if requirement_candidate:
        mandatory = (
            "argv",
            "credential_profile_fingerprint",
            "credential_attestation",
            "resolved_endpoint",
            "config_attestation_valid",
            "config_attestation_source",
        )
        if any(key not in expected or key not in current for key in mandatory):
            return _strict({"current": False, "status": "TOOL_CONFIG_ATTESTATION_REQUIRED", "stale_dependents": True}, True)
        if (
            expected.get("config_attestation_valid") is not True
            or current.get("config_attestation_valid") is not True
            or expected.get("config_attestation_source") != "PLATFORM_CONFIG_REGISTRY"
            or current.get("config_attestation_source") != "PLATFORM_CONFIG_REGISTRY"
        ):
            return _strict({"current": False, "status": "TOOL_CONFIG_ATTESTATION_INVALID", "stale_dependents": True}, True)

    v2_attestation = requirement_candidate or any(
        key in expected or key in current
        for key in (
            "argv",
            "credential_profile_fingerprint",
            "credential_attestation",
            "resolved_endpoint",
        )
    )

    if v2_attestation:
        required = (
            "tool_id",
            "harness_id",
            "transport",
            "endpoint",
            "permission_profile",
            "canonical_digest",
        )
        if any(k not in current for k in required):
            return _strict({"current": False, "status": "TOOL_CONFIG_UNKNOWN", "stale_dependents": True}, requirement_candidate)

        if "argv" in expected or "argv" in current:
            if _sha256_json(current.get("argv")) != current.get("argv_digest"):
                return _strict({"current": False, "status": "TOOL_CONFIG_ATTESTATION_INVALID", "stale_dependents": True}, requirement_candidate)
            if _sha256_json(expected.get("argv")) != expected.get("argv_digest"):
                return _strict({"current": False, "status": "TOOL_CONFIG_ATTESTATION_INVALID", "stale_dependents": True}, requirement_candidate)

        if "credential_profile_fingerprint" in expected or "credential_profile_fingerprint" in current:
            if _sha256_json(_v2_config_material(current)) != current.get("canonical_digest"):
                return _strict({"current": False, "status": "TOOL_CONFIG_ATTESTATION_INVALID", "stale_dependents": True}, requirement_candidate)
            if _sha256_json(_v2_config_material(expected)) != expected.get("canonical_digest"):
                return _strict({"current": False, "status": "TOOL_CONFIG_ATTESTATION_INVALID", "stale_dependents": True}, requirement_candidate)

        fields = [
            "tool_id",
            "harness_id",
            "transport",
            "endpoint",
            "argv_digest",
            "permission_profile",
            "credential_profile_fingerprint",
            "credential_attestation",
            "canonical_digest",
            "semantic_digest",
            "resolved_endpoint",
        ]
        if any(expected.get(k) != current.get(k) for k in fields if k in expected or k in current):
            return _strict({"current": False, "status": "TOOL_CONFIG_DRIFT", "stale_dependents": True}, requirement_candidate)
        return _strict({"current": True, "status": "TOOL_CONFIG_CURRENT", "stale_dependents": False}, requirement_candidate)

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
    if any(k not in current for k in identity_fields):
        return {"current": False, "status": "TOOL_CONFIG_UNKNOWN", "stale_dependents": True}

    fields = list(identity_fields)
    if "semantic_digest" in expected or "semantic_digest" in current:
        fields.append("semantic_digest")
    drift = any(expected.get(k) != current.get(k) for k in fields)
    if drift:
        return {"current": False, "status": "TOOL_CONFIG_DRIFT", "stale_dependents": True}
    return {"current": True, "status": "TOOL_CONFIG_CURRENT", "stale_dependents": False}


def _manual_threshold_contribution(binding, *, requirement_candidate=False):
    if not (
        binding.get("evidence_class") == "INDEPENDENT_MANUAL_REVIEW"
        and binding.get("manual_attestation_valid") is True
    ):
        return 0
    if requirement_candidate:
        return 1 if binding.get("manual_attestation_principal_authenticated") is True else 0
    if "manual_attestation_principal_authenticated" in binding:
        return 1 if binding.get("manual_attestation_principal_authenticated") is True else 0
    return 1


def classify_review_binding(binding, *, requirement_candidate=False):
    if requirement_candidate and binding.get("evidence_class") == "INDEPENDENT_MANUAL_REVIEW":
        if (
            binding.get("manual_attestation_valid") is True
            and binding.get("manual_attestation_principal_authenticated") is not True
        ):
            return _strict({
                "status": "REVIEW_MANUAL_ATTESTATION_REQUIRED",
                "provider_relationship": "PROVIDER_IDENTITY_UNKNOWN",
                "manual_review_threshold_contribution": 0,
                "reviewer_slot": binding.get("reviewer_slot"),
            }, True)

    contribution = _manual_threshold_contribution(binding, requirement_candidate=requirement_candidate)
    if not binding.get("packet_current"):
        return _strict({
            "status": "REVIEW_BINDING_STALE",
            "provider_relationship": "PROVIDER_IDENTITY_UNKNOWN",
            "manual_review_threshold_contribution": 0,
        }, requirement_candidate)
    if binding.get("packet_digest") != binding.get("consented_packet_digest", binding.get("packet_digest")):
        return _strict({
            "status": "REVIEW_EGRESS_BINDING_MISMATCH",
            "provider_relationship": "PROVIDER_IDENTITY_UNKNOWN",
            "manual_review_threshold_contribution": 0,
        }, requirement_candidate)
    if (
        binding.get("evidence_bound_slot", binding.get("reviewer_slot")) != binding.get("reviewer_slot")
        or binding.get("role_binding_model", binding.get("selected_model")) != binding.get("selected_model")
    ):
        return _strict({
            "status": "REVIEW_ROLE_BINDING_MISMATCH",
            "provider_relationship": "PROVIDER_IDENTITY_UNKNOWN",
            "manual_review_threshold_contribution": 0,
        }, requirement_candidate)

    if (
        binding.get("consent_max_egress_sequence") is not None
        and binding.get("egress_sequence") is not None
        and binding.get("egress_sequence") > binding.get("consent_max_egress_sequence")
    ):
        return _strict({
            "status": "REVIEW_EGRESS_CONSENT_STALE",
            "provider_relationship": "PROVIDER_IDENTITY_UNKNOWN",
            "manual_review_threshold_contribution": 0,
        }, requirement_candidate)

    permitted = set(binding.get("permitted_data_classes") or [])
    packet_classes = set(binding.get("packet_data_classes") or [])
    if packet_classes and not packet_classes.issubset(permitted):
        return _strict({
            "status": "REVIEW_EGRESS_SCOPE_EXCEEDED",
            "provider_relationship": "PROVIDER_IDENTITY_UNKNOWN",
            "manual_review_threshold_contribution": 0,
        }, requirement_candidate)
    if binding.get("transport_enabled", True) is False:
        return _strict({
            "status": "REVIEW_TRANSPORT_DISABLED",
            "provider_relationship": "PROVIDER_IDENTITY_UNKNOWN",
            "manual_review_threshold_contribution": 0,
        }, requirement_candidate)
    if binding.get("transport_ok", True) is False:
        return _strict({
            "status": "REVIEW_TRANSPORT_FAILED",
            "provider_relationship": "PROVIDER_IDENTITY_UNKNOWN",
            "manual_review_threshold_contribution": 0,
        }, requirement_candidate)

    selected = binding.get("selected_provider")
    returned = binding.get("returned_provider")
    gateway = binding.get("gateway")

    if requirement_candidate:
        if binding.get("provider_identity_attested") is not True:
            return _strict({
                "status": "REVIEW_PROVIDER_ATTESTATION_REQUIRED",
                "provider_relationship": "PROVIDER_IDENTITY_UNKNOWN",
                "manual_review_threshold_contribution": 0,
                "reviewer_slot": binding.get("reviewer_slot"),
            }, True)
        if gateway and binding.get("gateway_route_attested") is not True:
            return _strict({
                "status": "REVIEW_PROVIDER_ATTESTATION_REQUIRED",
                "provider_relationship": "PROVIDER_IDENTITY_UNKNOWN",
                "manual_review_threshold_contribution": 0,
                "reviewer_slot": binding.get("reviewer_slot"),
            }, True)
    else:
        identity_fields_present = (
            "provider_identity_attested" in binding or "gateway_route_attested" in binding
        )
        if identity_fields_present and not (
            binding.get("provider_identity_attested") is True
            and (not gateway or binding.get("gateway_route_attested") is True)
        ):
            relationship = "PROVIDER_IDENTITY_UNKNOWN"
            contribution = 0
        elif gateway and not returned:
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

    return _strict({
        "status": status,
        "provider_relationship": relationship,
        "manual_review_threshold_contribution": contribution,
        "reviewer_slot": binding.get("reviewer_slot"),
    }, True)


def authorize_learning_promotion(proposal, *, requirement_candidate=False):
    scope_preserved = proposal.get("target_scope", proposal.get("scope")) == proposal.get("scope")
    advisory_allowed = not proposal.get("stale", False) and not proposal.get("conflicts_governed", False)

    if proposal.get("artifact_digest") != proposal.get("reviewed_digest"):
        return _strict({
            "promotable": False,
            "status": "LEARNING_PROPOSAL_CHANGED_AFTER_REVIEW",
            "advisory_allowed": advisory_allowed,
            "scope_preserved": scope_preserved,
        }, requirement_candidate)
    if proposal.get("prior_rejection") and not proposal.get("history_preserved", False):
        return _strict({
            "promotable": False,
            "status": "LEARNING_HISTORY_INTEGRITY_REQUIRED",
            "advisory_allowed": False,
            "scope_preserved": scope_preserved,
        }, requirement_candidate)
    if not scope_preserved:
        return _strict({
            "promotable": False,
            "status": "LEARNING_SCOPE_WIDENING_REJECTED",
            "advisory_allowed": True,
            "scope_preserved": False,
        }, requirement_candidate)
    if proposal.get("requested_authority") and not proposal.get("explicit_authority_grant"):
        return _strict({
            "promotable": False,
            "status": "LEARNING_AUTHORITY_NOT_GRANTED",
            "advisory_allowed": True,
            "scope_preserved": True,
        }, requirement_candidate)
    if proposal.get("stale") or proposal.get("conflicts_governed"):
        return _strict({
            "promotable": False,
            "status": "LEARNING_PROPOSAL_STALE_OR_CONFLICTING",
            "advisory_allowed": False,
            "scope_preserved": scope_preserved,
        }, requirement_candidate)

    if requirement_candidate:
        mandatory = (
            "claim_governance_evidence_valid",
            "dependency_graph_current",
            "retraction_traversal_complete",
        )
        if any(key not in proposal for key in mandatory):
            return _strict({
                "promotable": False,
                "status": "LEARNING_GOVERNANCE_EVIDENCE_REQUIRED",
                "advisory_allowed": advisory_allowed,
                "scope_preserved": scope_preserved,
            }, True)
        if not (
            proposal.get("claim_governance_evidence_valid") is True
            and proposal.get("dependency_graph_current") is True
        ):
            return _strict({
                "promotable": False,
                "status": "LEARNING_GOVERNANCE_EVIDENCE_INSUFFICIENT",
                "advisory_allowed": advisory_allowed,
                "scope_preserved": scope_preserved,
            }, True)
        if proposal.get("parent_retracted") and proposal.get("retraction_traversal_complete") is not True:
            return _strict({
                "promotable": False,
                "status": "LEARNING_PROPOSAL_REASSESSMENT_REQUIRED",
                "advisory_allowed": True,
                "scope_preserved": scope_preserved,
                "independent_support_preserved": False,
            }, True)
        if not (
            proposal.get("source_verified")
            and proposal.get("independent_support")
            and proposal.get("governed_approval")
        ):
            return _strict({
                "promotable": False,
                "status": "LEARNING_PROPOSAL_NOT_PROMOTABLE",
                "advisory_allowed": advisory_allowed,
                "scope_preserved": scope_preserved,
            }, True)
        return _strict({
            "promotable": False,
            "status": "LEARNING_PROPOSAL_REFERENCE_ELIGIBLE",
            "advisory_allowed": True,
            "scope_preserved": scope_preserved,
        }, True)

    v2_governance_fields = (
        "claim_governance_evidence_valid" in proposal
        or "dependency_graph_current" in proposal
        or "retraction_traversal_complete" in proposal
    )
    if v2_governance_fields and not (
        proposal.get("claim_governance_evidence_valid") is True
        and proposal.get("dependency_graph_current") is True
    ):
        return {
            "promotable": False,
            "status": "LEARNING_GOVERNANCE_EVIDENCE_INSUFFICIENT",
            "advisory_allowed": advisory_allowed,
            "scope_preserved": scope_preserved,
        }

    if proposal.get("parent_retracted"):
        if v2_governance_fields and proposal.get("retraction_traversal_complete") is not True:
            return {
                "promotable": False,
                "status": "LEARNING_PROPOSAL_REASSESSMENT_REQUIRED",
                "advisory_allowed": True,
                "scope_preserved": scope_preserved,
                "independent_support_preserved": False,
            }
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

# V4_HISTORICAL_RESULT_CLASSIFICATION_BOUNDARY
# The historical compatibility functions remain replayable, but every result is
# explicitly typed. Only the separate ecc_candidate_boundary module is eligible
# to produce requirement-candidate evidence for new candidate evaluation.
def _classify_public_evaluation_result(fn):
    @functools.wraps(fn)
    def wrapped(*args, **kwargs):
        result = fn(*args, **kwargs)
        if not isinstance(result, dict):
            return result
        if "evaluation_class" in result:
            return result
        classified = dict(result)
        classified["evaluation_class"] = (
            _REQUIREMENT_CANDIDATE
            if kwargs.get("requirement_candidate", False)
            else _HISTORICAL_REFERENCE
        )
        return classified

    return wrapped


for _public_name in (
    "assess_control_execution",
    "check_declared_executable_equivalence",
    "qualify_role_binding",
    "authorize_power_activation",
    "check_tool_configuration",
    "classify_review_binding",
    "authorize_learning_promotion",
):
    globals()[_public_name] = _classify_public_evaluation_result(globals()[_public_name])
