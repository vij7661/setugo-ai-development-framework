from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

import ecc_governance as gov


STRICT = "REQUIREMENT_CANDIDATE"


def candidate_call(fn, *args, **kwargs):
    """Preregistered adapter: V2 lacks the strict kwarg, which is a V3 RED, not a test error."""
    try:
        return fn(*args, requirement_candidate=True, **kwargs)
    except TypeError as exc:
        if "requirement_candidate" in str(exc):
            return {"status": "STRICT_ENTRYPOINT_MISSING", "evaluation_class": None}
        raise


def base_control():
    return {"control_id": "gate", "version": 3, "digest": "c" * 64}


def legacy_event():
    return {
        "control_id": "gate", "version": 3, "control_digest": "c" * 64,
        "candidate": "shaA", "action_id": "act1", "started": True,
        "result_recorded": True, "execution_ok": True, "decision": "ALLOW",
        "input_digest": "i" * 64, "result_digest": "r" * 64,
        "invocation_id": "inv1",
    }


def strict_event():
    e = legacy_event()
    e.update({
        "attestation_source": "PLATFORM_ENFORCEMENT_POINT",
        "attestation_valid": True,
        "verified_action_sequence": 10,
        "executed_action_sequence": 10,
        "process_identity": "hook@pid:trusted",
        "expected_process_identity": "hook@pid:trusted",
    })
    return e


def declared():
    return {
        "mode": "BLOCKING", "on_internal_error": "DENY",
        "candidate_binding": "EXACT", "disable_paths": [],
        "contract_version": 2, "profile_digest": "p2", "scope": "ALL",
    }


def strict_executable():
    return {
        **declared(),
        "machine_verified": True,
        "runtime_mode": "BLOCKING",
        "runtime_on_internal_error": "DENY",
        "generated_doc_mode": "BLOCKING",
        "discovered_disable_flags": [],
        "paths": [{
            "mode": "BLOCKING", "on_internal_error": "DENY",
            "candidate_binding": "EXACT", "machine_verified": True,
        }],
    }


def legacy_envelope():
    return {
        "complete": True, "harness_id": "h1", "runtime_version": "1",
        "qualified_runtime_version": "1", "config_digest": "d",
        "qualified_config_digest": "d",
        "capabilities": {"write_confinement": "NATIVE_ENFORCEMENT"},
        "semantic_evidence": {"write_confinement": True},
    }


def strict_envelope():
    e = legacy_envelope()
    e.update({
        "identity_attested": True,
        "identity_attestation_source": "PLATFORM_HARNESS_REGISTRY",
        "runtime_identity_digest": "r" * 64,
    })
    return e


def cap_req():
    return {"write_confinement": {"allowed_classes": ["NATIVE_ENFORCEMENT"], "semantic_evidence_required": True}}


def legacy_manifest():
    return {"digest": "m", "role": "R1", "powers": ["WRITE"], "resources": ["repo"]}


def legacy_approval():
    return {
        "approved": True, "manifest_digest": "m", "role": "R1",
        "approved_powers": ["WRITE"], "approved_resources": ["repo"],
    }


def strict_manifest():
    return {**legacy_manifest(), "project_id": "p1"}


def strict_approval():
    return {
        **legacy_approval(), "principal_authenticated": True,
        "authority_grant_valid": True, "project_id": "p1",
        "approval_sequence": 7,
    }


def legacy_cfg():
    return {
        "tool_id": "t", "harness_id": "h", "transport": "stdio",
        "endpoint": None, "argv_digest": "a", "permission_profile": "r",
        "credential_profile": "cp", "canonical_digest": "d",
        "semantic_digest": "s", "read_ok": True,
    }


def strict_cfg():
    material = {
        "tool_id": "t", "harness_id": "h", "transport": "stdio",
        "endpoint": None, "argv": ["x"], "permission_profile": "r",
        "credential_profile_fingerprint": "cred-fp",
    }
    canonical = hashlib.sha256(json.dumps(material, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    argv_digest = hashlib.sha256(json.dumps(["x"], sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return {
        **material, "argv_digest": argv_digest, "canonical_digest": canonical,
        "semantic_digest": "s", "credential_attestation": "attested-cred",
        "resolved_endpoint": "LOCAL_STDIO", "read_ok": True,
        "config_attestation_valid": True,
        "config_attestation_source": "PLATFORM_CONFIG_REGISTRY",
    }


def legacy_binding():
    return {
        "packet_current": True, "packet_digest": "p", "consented_packet_digest": "p",
        "reviewer_slot": "R3", "selected_model": "m", "selected_provider": "A",
        "returned_provider": "A", "context_isolation_evidenced": True,
        "transport_enabled": True, "transport_ok": True,
    }


def strict_binding():
    return {
        **legacy_binding(),
        "provider_identity_attested": True,
        "gateway_route_attested": True,
        "provider_attestation_source": "PLATFORM_PROVIDER_REGISTRY",
    }


def legacy_manual_binding():
    return {
        **legacy_binding(), "evidence_class": "INDEPENDENT_MANUAL_REVIEW",
        "manual_attestation_valid": True,
    }


def strict_proposal():
    return {
        "artifact_digest": "a", "reviewed_digest": "a",
        "scope": "project", "target_scope": "project",
        "source_verified": True, "independent_support": True,
        "governed_approval": True,
        "claim_governance_evidence_valid": True,
        "dependency_graph_current": True,
        "retraction_traversal_complete": True,
    }


class ECCV3OmissionHardening(unittest.TestCase):
    # EXP-ECC-1: mandatory execution attestation in requirement-candidate mode.
    def test_e1_omitted_platform_attestation_fails_closed(self):
        r = candidate_call(gov.assess_control_execution, base_control(), legacy_event(), candidate="shaA", action_id="act1")
        self.assertEqual(r["status"], "CONTROL_ATTESTATION_REQUIRED")

    def test_e1_omitted_sequence_or_process_binding_fails_closed(self):
        e = legacy_event() | {"attestation_source": "PLATFORM_ENFORCEMENT_POINT", "attestation_valid": True}
        r = candidate_call(gov.assess_control_execution, base_control(), e, candidate="shaA", action_id="act1")
        self.assertEqual(r["status"], "CONTROL_ACTION_BINDING_REQUIRED")

    def test_e1_strict_valid_receipt_is_eligible(self):
        r = candidate_call(gov.assess_control_execution, base_control(), strict_event(), candidate="shaA", action_id="act1")
        self.assertEqual(r["status"], "VERIFIED")
        self.assertEqual(r.get("evaluation_class"), STRICT)

    # EXP-ECC-2: no declared-only equivalence in requirement-candidate mode.
    def test_e2_omitted_machine_verification_fails_closed(self):
        r = candidate_call(gov.check_declared_executable_equivalence, declared(), dict(declared()))
        self.assertEqual(r["status"], "EXECUTABLE_PROFILE_REQUIRED")

    def test_e2_omitted_runtime_paths_fails_closed(self):
        x = strict_executable(); x.pop("paths")
        r = candidate_call(gov.check_declared_executable_equivalence, declared(), x)
        self.assertEqual(r["status"], "EXECUTABLE_PATHS_REQUIRED")

    def test_e2_strict_machine_profile_can_match(self):
        r = candidate_call(gov.check_declared_executable_equivalence, declared(), strict_executable())
        self.assertEqual(r["status"], "EQUIVALENT")
        self.assertEqual(r.get("evaluation_class"), STRICT)

    # EXP-ECC-3: identity attestation and per-capability matrix mandatory.
    def test_e3_omitted_identity_attestation_fails_closed(self):
        r = candidate_call(gov.qualify_role_binding, "R1", "model-x", legacy_envelope(), cap_req())
        self.assertEqual(r["status"], "HARNESS_IDENTITY_ATTESTATION_REQUIRED")

    def test_e3_legacy_string_requirement_ineligible_for_candidate(self):
        r = candidate_call(gov.qualify_role_binding, "R1", "model-x", strict_envelope(), {"write_confinement": "NATIVE_ENFORCEMENT"})
        self.assertEqual(r["status"], "HARNESS_CAPABILITY_MATRIX_REQUIRED")

    def test_e3_strict_provider_neutral_binding_is_eligible(self):
        r = candidate_call(gov.qualify_role_binding, "R1", "user-selected-qualified-model", strict_envelope(), cap_req())
        self.assertEqual(r["status"], "ROLE_BINDING_ELIGIBLE")
        self.assertEqual(r["selected_model"], "user-selected-qualified-model")
        self.assertEqual(r.get("evaluation_class"), STRICT)

    # EXP-ECC-4: authenticated authority/project/sequence are mandatory.
    def test_e4_legacy_approval_without_authority_fields_fails_closed(self):
        r = candidate_call(gov.authorize_power_activation, legacy_manifest(), legacy_approval(), ["WRITE"], role="R1", requested_resources=["repo"], current_sequence=7)
        self.assertEqual(r["status"], "ACTIVATION_AUTHORITY_REQUIRED")

    def test_e4_missing_project_or_sequence_binding_fails_closed(self):
        a = strict_approval(); a.pop("approval_sequence")
        r = candidate_call(gov.authorize_power_activation, strict_manifest(), a, ["WRITE"], role="R1", requested_resources=["repo"], current_sequence=7)
        self.assertEqual(r["status"], "ACTIVATION_SEQUENCE_BINDING_REQUIRED")

    def test_e4_strict_activation_is_allowed(self):
        r = candidate_call(gov.authorize_power_activation, strict_manifest(), strict_approval(), ["WRITE"], role="R1", requested_resources=["repo"], current_sequence=7)
        self.assertEqual(r["status"], "ACTIVATION_ALLOWED")
        self.assertEqual(r.get("evaluation_class"), STRICT)

    # EXP-ECC-5: legacy config comparison cannot qualify new candidates.
    def test_e5_legacy_config_fields_fail_closed(self):
        r = candidate_call(gov.check_tool_configuration, legacy_cfg(), dict(legacy_cfg()))
        self.assertEqual(r["status"], "TOOL_CONFIG_ATTESTATION_REQUIRED")

    def test_e5_missing_platform_config_attestation_fails_closed(self):
        c = strict_cfg(); c.pop("config_attestation_valid"); c.pop("config_attestation_source")
        r = candidate_call(gov.check_tool_configuration, strict_cfg(), c)
        self.assertEqual(r["status"], "TOOL_CONFIG_ATTESTATION_REQUIRED")

    def test_e5_strict_attested_config_can_be_current(self):
        c = strict_cfg()
        r = candidate_call(gov.check_tool_configuration, c, dict(c))
        self.assertEqual(r["status"], "TOOL_CONFIG_CURRENT")
        self.assertEqual(r.get("evaluation_class"), STRICT)

    # EXP-ECC-6 remains deferred but omission must never create identity/manual credit.
    def test_e6_omitted_provider_attestation_never_confirms_relationship(self):
        r = candidate_call(gov.classify_review_binding, legacy_binding())
        self.assertEqual(r["provider_relationship"], "PROVIDER_IDENTITY_UNKNOWN")
        self.assertEqual(r.get("status"), "REVIEW_PROVIDER_ATTESTATION_REQUIRED")

    def test_e6_omitted_manual_principal_never_gets_threshold_credit(self):
        r = candidate_call(gov.classify_review_binding, legacy_manual_binding())
        self.assertEqual(r["manual_review_threshold_contribution"], 0)
        self.assertEqual(r.get("status"), "REVIEW_MANUAL_ATTESTATION_REQUIRED")

    def test_e6_strict_provider_binding_still_has_zero_ai_credit(self):
        b = strict_binding() | {"evidence_class": "AI_GENERATED_ENGINEERING_FEEDBACK_ONLY"}
        r = candidate_call(gov.classify_review_binding, b)
        self.assertEqual(r["manual_review_threshold_contribution"], 0)
        self.assertEqual(r.get("evaluation_class"), STRICT)

    # EXP-ECC-7 remains deferred but self-asserted legacy flags cannot promote.
    def test_e7_legacy_promotion_flags_fail_closed(self):
        p = {"artifact_digest": "a", "reviewed_digest": "a", "scope": "project", "target_scope": "project", "source_verified": True, "independent_support": True, "governed_approval": True}
        r = candidate_call(gov.authorize_learning_promotion, p)
        self.assertEqual(r["status"], "LEARNING_GOVERNANCE_EVIDENCE_REQUIRED")
        self.assertFalse(r["promotable"])

    def test_e7_strict_governance_evidence_remains_reference_only(self):
        r = candidate_call(gov.authorize_learning_promotion, strict_proposal())
        self.assertEqual(r["status"], "LEARNING_PROPOSAL_REFERENCE_ELIGIBLE")
        self.assertFalse(r["promotable"])
        self.assertEqual(r.get("evaluation_class"), STRICT)

    # Shared module is an explicit trust boundary rather than invisible coupling.
    def test_shared_module_has_exact_trust_boundary_manifest(self):
        module_path = Path(__file__).with_name("ecc_governance.py")
        manifest_path = Path(__file__).with_name("ecc_governance_trust_manifest.json")
        self.assertTrue(manifest_path.exists(), "shared governance module requires an external trust-boundary manifest")
        manifest = json.loads(manifest_path.read_text())
        actual = hashlib.sha256(module_path.read_bytes()).hexdigest()
        self.assertEqual(manifest.get("module_sha256"), actual)
        self.assertEqual(manifest.get("legacy_path_policy"), "HISTORICAL_REFERENCE_ONLY")
        self.assertEqual(manifest.get("candidate_path_policy"), "MANDATORY_STRICT_EVALUATION")
        self.assertEqual(set(manifest.get("covers", [])), {f"EXP-ECC-{i}" for i in range(1, 8)})


if __name__ == "__main__":
    unittest.main()
