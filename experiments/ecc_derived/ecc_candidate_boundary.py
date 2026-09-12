from __future__ import annotations

import hashlib
import json
from pathlib import Path

import ecc_governance as gov

STRICT = "REQUIREMENT_CANDIDATE"
HISTORICAL = "HISTORICAL_REFERENCE"
_COVERS = {f"EXP-ECC-{i}" for i in range(1, 8)}


def _sha256_json(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def verify_runtime_policy():
    """Verify the exact shared core and V4 candidate boundary are the manifest-bound runtime pair."""
    here = Path(__file__).resolve().parent
    manifest_path = here / "ecc_governance_trust_manifest.json"
    core_path = here / "ecc_governance.py"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        return False

    if manifest.get("candidate_path_policy") != "MANDATORY_STRICT_EVALUATION":
        return False
    if manifest.get("legacy_path_policy") != "HISTORICAL_REFERENCE_ONLY":
        return False
    if set(manifest.get("covers") or []) != _COVERS:
        return False
    if manifest.get("module_sha256") != hashlib.sha256(core_path.read_bytes()).hexdigest():
        return False

    # V4 adds these fields. Their absence intentionally keeps Stage A RED.
    if manifest.get("candidate_boundary_policy") != "STRICT_ONLY_NO_CALLER_MODE_SWITCH":
        return False
    if manifest.get("historical_result_class") != HISTORICAL:
        return False
    if set(manifest.get("independent_crosscheck_covers") or []) != {
        "EXP-ECC-1", "EXP-ECC-2", "EXP-ECC-3", "EXP-ECC-4", "EXP-ECC-5"
    }:
        return False
    if manifest.get("candidate_boundary_module_sha256") != hashlib.sha256(Path(__file__).read_bytes()).hexdigest():
        return False
    return True


def candidate_result_eligible(result):
    """Classification gate only: historical/unclassified results can never be candidate evidence."""
    return isinstance(result, dict) and result.get("evaluation_class") == STRICT


def _policy_failure(kind):
    base = {"status": "CANDIDATE_BOUNDARY_POLICY_INVALID", "evaluation_class": STRICT}
    if kind == "execution":
        return base | {"verified": False, "allowed": False}
    if kind == "equivalence":
        return base | {"equivalent": False}
    if kind == "role":
        return base | {"eligible": False}
    if kind == "activation":
        return base | {"authorized": False}
    if kind == "config":
        return base | {"current": False, "stale_dependents": True}
    if kind == "review":
        return base | {
            "provider_relationship": "PROVIDER_IDENTITY_UNKNOWN",
            "manual_review_threshold_contribution": 0,
        }
    if kind == "learning":
        return base | {"promotable": False, "advisory_allowed": False}
    return base


def _crosscheck_failure(kind):
    base = {"status": "CANDIDATE_INDEPENDENT_CROSSCHECK_FAILED", "evaluation_class": STRICT}
    if kind == "execution":
        return base | {"verified": False, "allowed": False}
    if kind == "equivalence":
        return base | {"equivalent": False}
    if kind == "role":
        return base | {"eligible": False}
    if kind == "activation":
        return base | {"authorized": False}
    if kind == "config":
        return base | {"current": False, "stale_dependents": True}
    return base


def _execution_crosscheck(control, event, candidate, action_id):
    if not isinstance(event, dict):
        return False
    if event.get("control_id") != control.get("control_id"):
        return False
    if event.get("version") != control.get("version") or event.get("control_digest") != control.get("digest"):
        return False
    if event.get("candidate") != candidate or event.get("action_id") != action_id:
        return False
    if event.get("attestation_source") != "PLATFORM_ENFORCEMENT_POINT" or event.get("attestation_valid") is not True:
        return False
    if event.get("verified_action_sequence") != event.get("executed_action_sequence"):
        return False
    if event.get("verified_action_sequence") is None:
        return False
    if event.get("process_identity") != event.get("expected_process_identity") or not event.get("process_identity"):
        return False
    return bool(
        event.get("started")
        and event.get("result_recorded")
        and event.get("execution_ok")
        and event.get("input_digest")
        and event.get("result_digest")
        and event.get("invocation_id")
    )


def _equivalence_crosscheck(declared, executable):
    if executable.get("machine_verified") is not True:
        return False
    required_runtime = (
        "runtime_mode", "runtime_on_internal_error", "generated_doc_mode", "discovered_disable_flags"
    )
    if any(key not in executable for key in required_runtime):
        return False
    paths = executable.get("paths")
    if not isinstance(paths, list) or not paths:
        return False
    if executable.get("runtime_mode") != declared.get("mode"):
        return False
    if executable.get("runtime_on_internal_error") != declared.get("on_internal_error"):
        return False
    if executable.get("generated_doc_mode") != executable.get("runtime_mode"):
        return False
    if not set(executable.get("discovered_disable_flags") or []).issubset(set(declared.get("disable_paths") or [])):
        return False
    for path in paths:
        if path.get("machine_verified") is not True:
            return False
        for key in ("mode", "on_internal_error", "candidate_binding"):
            if path.get(key) != declared.get(key):
                return False
    for key in (
        "mode", "on_internal_error", "candidate_binding", "disable_paths",
        "contract_version", "profile_digest", "scope",
    ):
        if declared.get(key) != executable.get(key):
            return False
    return True


def _role_crosscheck(envelope, required_capabilities, require_semantic_evidence=False):
    if envelope.get("identity_attested") is not True:
        return False
    if envelope.get("identity_attestation_source") != "PLATFORM_HARNESS_REGISTRY":
        return False
    if not envelope.get("runtime_identity_digest"):
        return False
    if any(not isinstance(required, dict) for required in required_capabilities.values()):
        return False
    if envelope.get("qualified_runtime_version") is not None and envelope.get("runtime_version") != envelope.get("qualified_runtime_version"):
        return False
    if envelope.get("qualified_config_digest") is not None and envelope.get("config_digest") != envelope.get("qualified_config_digest"):
        return False
    caps = envelope.get("capabilities")
    if not isinstance(caps, dict):
        return False
    semantic = envelope.get("semantic_evidence") or {}
    for capability, required in required_capabilities.items():
        allowed = set(required.get("allowed_classes") or [])
        actual = caps.get(capability)
        if not allowed or actual not in allowed:
            return False
        if (require_semantic_evidence or required.get("semantic_evidence_required")) and not semantic.get(capability):
            return False
    return True


def _activation_crosscheck(manifest, approval, requested_powers, role, requested_resources, current_sequence):
    if manifest.get("revoked"):
        return False
    if not approval or approval.get("approved") is not True:
        return False
    if approval.get("manifest_digest") != manifest.get("digest"):
        return False
    if approval.get("role") != role or manifest.get("role") != role:
        return False
    if approval.get("principal_authenticated") is not True or approval.get("authority_grant_valid") is not True:
        return False
    if not manifest.get("project_id") or manifest.get("project_id") != approval.get("project_id"):
        return False
    if current_sequence is None or approval.get("approval_sequence") is None:
        return False
    if approval.get("approval_sequence") > current_sequence:
        return False
    revoked_at = manifest.get("revoked_at_sequence")
    if revoked_at is not None and current_sequence >= revoked_at:
        return False
    expiry = manifest.get("expires_sequence")
    if expiry is not None and current_sequence >= expiry:
        return False
    requested = set(requested_powers or [])
    if not requested.issubset(set(manifest.get("powers") or [])):
        return False
    if not requested.issubset(set(approval.get("approved_powers") or [])):
        return False
    resources = set(requested_resources or [])
    if resources and not resources.issubset(set(manifest.get("resources") or [])):
        return False
    if resources and not resources.issubset(set(approval.get("approved_resources") or [])):
        return False
    return True


def _config_material(cfg):
    return {
        "tool_id": cfg.get("tool_id"),
        "harness_id": cfg.get("harness_id"),
        "transport": cfg.get("transport"),
        "endpoint": cfg.get("endpoint"),
        "argv": cfg.get("argv"),
        "permission_profile": cfg.get("permission_profile"),
        "credential_profile_fingerprint": cfg.get("credential_profile_fingerprint"),
    }


def _config_crosscheck(expected, current):
    required = (
        "tool_id", "harness_id", "transport", "endpoint", "argv",
        "argv_digest", "permission_profile", "credential_profile_fingerprint",
        "credential_attestation", "canonical_digest", "semantic_digest",
        "resolved_endpoint", "config_attestation_valid", "config_attestation_source",
    )
    if any(key not in expected or key not in current for key in required):
        return False
    if expected.get("read_ok", True) is False or current.get("read_ok", True) is False:
        return False
    if expected.get("config_attestation_valid") is not True or current.get("config_attestation_valid") is not True:
        return False
    if expected.get("config_attestation_source") != "PLATFORM_CONFIG_REGISTRY" or current.get("config_attestation_source") != "PLATFORM_CONFIG_REGISTRY":
        return False
    if not expected.get("credential_attestation") or not current.get("credential_attestation"):
        return False
    if _sha256_json(expected.get("argv")) != expected.get("argv_digest"):
        return False
    if _sha256_json(current.get("argv")) != current.get("argv_digest"):
        return False
    if _sha256_json(_config_material(expected)) != expected.get("canonical_digest"):
        return False
    if _sha256_json(_config_material(current)) != current.get("canonical_digest"):
        return False
    compared = (
        "tool_id", "harness_id", "transport", "endpoint", "argv_digest",
        "permission_profile", "credential_profile_fingerprint", "credential_attestation",
        "canonical_digest", "semantic_digest", "resolved_endpoint",
    )
    return all(expected.get(key) == current.get(key) for key in compared)


def assess_control_execution_candidate(control, event, *, candidate, action_id):
    if not verify_runtime_policy():
        return _policy_failure("execution")
    result = gov.assess_control_execution(
        control, event, candidate=candidate, action_id=action_id, requirement_candidate=True
    )
    if result.get("verified") and not _execution_crosscheck(control, event, candidate, action_id):
        return _crosscheck_failure("execution")
    return result


def check_declared_executable_equivalence_candidate(declared, executable):
    if not verify_runtime_policy():
        return _policy_failure("equivalence")
    result = gov.check_declared_executable_equivalence(declared, executable, requirement_candidate=True)
    if result.get("equivalent") and not _equivalence_crosscheck(declared, executable):
        return _crosscheck_failure("equivalence")
    return result


def qualify_role_binding_candidate(
    role,
    selected_model,
    envelope,
    required_capabilities,
    *,
    prior_binding=None,
    revalidated=True,
    require_semantic_evidence=False,
):
    if not verify_runtime_policy():
        return _policy_failure("role")
    result = gov.qualify_role_binding(
        role,
        selected_model,
        envelope,
        required_capabilities,
        prior_binding=prior_binding,
        revalidated=revalidated,
        require_semantic_evidence=require_semantic_evidence,
        requirement_candidate=True,
    )
    if result.get("eligible") and not _role_crosscheck(
        envelope, required_capabilities, require_semantic_evidence
    ):
        return _crosscheck_failure("role")
    return result


def authorize_power_activation_candidate(
    manifest,
    approval,
    requested_powers,
    *,
    role,
    requested_resources=None,
    current_sequence=None,
):
    if not verify_runtime_policy():
        return _policy_failure("activation")
    result = gov.authorize_power_activation(
        manifest,
        approval,
        requested_powers,
        role=role,
        requested_resources=requested_resources,
        current_sequence=current_sequence,
        requirement_candidate=True,
    )
    if result.get("authorized") and not _activation_crosscheck(
        manifest, approval, requested_powers, role, requested_resources, current_sequence
    ):
        return _crosscheck_failure("activation")
    return result


def check_tool_configuration_candidate(expected, current):
    if not verify_runtime_policy():
        return _policy_failure("config")
    result = gov.check_tool_configuration(expected, current, requirement_candidate=True)
    if result.get("current") and not _config_crosscheck(expected, current):
        return _crosscheck_failure("config")
    return result


def classify_review_binding_candidate(binding):
    if not verify_runtime_policy():
        return _policy_failure("review")
    return gov.classify_review_binding(binding, requirement_candidate=True)


def authorize_learning_promotion_candidate(proposal):
    if not verify_runtime_policy():
        return _policy_failure("learning")
    return gov.authorize_learning_promotion(proposal, requirement_candidate=True)
