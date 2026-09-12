import hashlib
import json
import unittest

from ecc_governance import (
    assess_control_execution,
    check_declared_executable_equivalence,
    qualify_role_binding,
    authorize_power_activation,
    check_tool_configuration,
    classify_review_binding,
    authorize_learning_promotion,
)


def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


class ECCReviewRemediationV2(unittest.TestCase):
    # EXP-ECC-1 — trusted execution provenance, TOCTOU, process identity.
    def test_e1_spoofed_worker_receipt_is_not_verified(self):
        control = {"control_id": "gate", "version": 3, "digest": "c" * 64}
        event = {
            "control_id": "gate", "version": 3, "control_digest": "c" * 64,
            "candidate": "shaA", "action_id": "act1", "started": True,
            "result_recorded": True, "execution_ok": True, "decision": "ALLOW",
            "input_digest": "i" * 64, "result_digest": "r" * 64, "invocation_id": "inv1",
            "attestation_source": "WORKER_SELF_ASSERTED", "attestation_valid": False,
        }
        self.assertEqual(assess_control_execution(control, event, candidate="shaA", action_id="act1")["status"], "CONTROL_ATTESTATION_UNTRUSTED")

    def test_e1_toctou_action_sequence_mismatch_is_rejected(self):
        control = {"control_id": "gate", "version": 3, "digest": "c" * 64}
        event = {
            "control_id": "gate", "version": 3, "control_digest": "c" * 64,
            "candidate": "shaA", "action_id": "act1", "started": True,
            "result_recorded": True, "execution_ok": True, "decision": "ALLOW",
            "input_digest": "i" * 64, "result_digest": "r" * 64, "invocation_id": "inv1",
            "attestation_source": "PLATFORM_ENFORCEMENT_POINT", "attestation_valid": True,
            "verified_action_sequence": 10, "executed_action_sequence": 11,
            "process_identity": "hook@pid:10", "expected_process_identity": "hook@pid:10",
        }
        self.assertEqual(assess_control_execution(control, event, candidate="shaA", action_id="act1")["status"], "CONTROL_TOCTOU_MISMATCH")

    def test_e1_hook_process_replacement_is_rejected(self):
        control = {"control_id": "gate", "version": 3, "digest": "c" * 64}
        event = {
            "control_id": "gate", "version": 3, "control_digest": "c" * 64,
            "candidate": "shaA", "action_id": "act1", "started": True,
            "result_recorded": True, "execution_ok": True, "decision": "ALLOW",
            "input_digest": "i" * 64, "result_digest": "r" * 64, "invocation_id": "inv1",
            "attestation_source": "PLATFORM_ENFORCEMENT_POINT", "attestation_valid": True,
            "verified_action_sequence": 10, "executed_action_sequence": 10,
            "process_identity": "hook@pid:evil", "expected_process_identity": "hook@pid:trusted",
        }
        self.assertEqual(assess_control_execution(control, event, candidate="shaA", action_id="act1")["status"], "CONTROL_PROCESS_IDENTITY_MISMATCH")

    # EXP-ECC-2 — executable semantics must be machine-derived, all paths checked.
    def test_e2_declared_blocking_but_runtime_fail_open_is_rejected(self):
        declared = {"mode": "BLOCKING", "on_internal_error": "DENY", "candidate_binding": "EXACT", "contract_version": 1, "profile_digest": "p", "scope": "ALL"}
        executable = dict(declared, machine_verified=True, runtime_on_internal_error="ALLOW", paths=[])
        self.assertEqual(check_declared_executable_equivalence(declared, executable)["status"], "ENFORCEMENT_MISMATCH")

    def test_e2_undocumented_disable_flag_is_rejected(self):
        declared = {"mode": "BLOCKING", "on_internal_error": "DENY", "candidate_binding": "EXACT", "contract_version": 1, "profile_digest": "p", "scope": "ALL", "disable_paths": []}
        executable = dict(declared, machine_verified=True, discovered_disable_flags=["ECC_SKIP_GATE"], paths=[])
        self.assertEqual(check_declared_executable_equivalence(declared, executable)["status"], "ENFORCEMENT_MISMATCH")

    def test_e2_generated_docs_stronger_than_code_is_rejected(self):
        declared = {"mode": "BLOCKING", "on_internal_error": "DENY", "candidate_binding": "EXACT", "contract_version": 1, "profile_digest": "p", "scope": "ALL"}
        executable = dict(declared, machine_verified=True, generated_doc_mode="BLOCKING", runtime_mode="ADVISORY", paths=[])
        self.assertEqual(check_declared_executable_equivalence(declared, executable)["status"], "ENFORCEMENT_MISMATCH")

    def test_e2_unverified_executable_profile_is_insufficient(self):
        declared = {"mode": "BLOCKING", "on_internal_error": "DENY", "candidate_binding": "EXACT", "contract_version": 1, "profile_digest": "p", "scope": "ALL"}
        executable = dict(declared, machine_verified=False)
        self.assertEqual(check_declared_executable_equivalence(declared, executable)["status"], "EXECUTABLE_PROFILE_UNVERIFIED")

    # EXP-ECC-3 — per-capability matrices and attested harness identity.
    def test_e3_incomparable_capability_class_requires_explicit_allowed_set(self):
        envelope = {"complete": True, "harness_id": "h1", "runtime_version": "1", "config_digest": "d", "identity_attested": True,
                    "capabilities": {"network_denial": "NATIVE_ENFORCEMENT"}}
        req = {"network_denial": {"allowed_classes": ["ADAPTER_ENFORCEMENT"], "semantic_evidence_required": False}}
        self.assertEqual(qualify_role_binding("R1", "model-x", envelope, req)["status"], "HARNESS_CAPABILITY_INSUFFICIENT")

    def test_e3_unattested_harness_identity_is_rejected(self):
        envelope = {"complete": True, "harness_id": "h1", "runtime_version": "1", "config_digest": "d", "identity_attested": False,
                    "capabilities": {"write_confinement": "NATIVE_ENFORCEMENT"}}
        req = {"write_confinement": {"allowed_classes": ["NATIVE_ENFORCEMENT"]}}
        self.assertEqual(qualify_role_binding("R1", "model-x", envelope, req)["status"], "HARNESS_IDENTITY_UNATTESTED")

    def test_e3_downgrade_after_qualification_requires_revalidation(self):
        envelope = {"complete": True, "harness_id": "h1", "runtime_version": "1", "config_digest": "d2", "qualified_config_digest": "d1", "identity_attested": True,
                    "capabilities": {"write_confinement": "NATIVE_ENFORCEMENT"}}
        req = {"write_confinement": {"allowed_classes": ["NATIVE_ENFORCEMENT"]}}
        self.assertEqual(qualify_role_binding("R2", "model-y", envelope, req)["status"], "HARNESS_QUALIFICATION_STALE")

    # EXP-ECC-4 — authenticated platform activation, project/sequence/TOCTOU binding.
    def test_e4_forged_approver_is_rejected(self):
        manifest = {"digest": "m", "role": "R1", "powers": ["WRITE"], "resources": ["repo"], "project_id": "p1"}
        approval = {"approved": True, "manifest_digest": "m", "role": "R1", "approved_powers": ["WRITE"], "approved_resources": ["repo"],
                    "principal_authenticated": False, "authority_grant_valid": False, "project_id": "p1", "approval_sequence": 7}
        self.assertEqual(authorize_power_activation(manifest, approval, ["WRITE"], role="R1", requested_resources=["repo"], current_sequence=7)["status"], "ACTIVATION_AUTHORITY_INVALID")

    def test_e4_cross_project_replay_is_rejected(self):
        manifest = {"digest": "m", "role": "R1", "powers": ["WRITE"], "resources": ["repo"], "project_id": "p2"}
        approval = {"approved": True, "manifest_digest": "m", "role": "R1", "approved_powers": ["WRITE"], "approved_resources": ["repo"],
                    "principal_authenticated": True, "authority_grant_valid": True, "project_id": "p1", "approval_sequence": 7}
        self.assertEqual(authorize_power_activation(manifest, approval, ["WRITE"], role="R1", requested_resources=["repo"], current_sequence=7)["status"], "ACTIVATION_PROJECT_MISMATCH")

    def test_e4_revocation_after_approval_before_activation_is_rejected(self):
        manifest = {"digest": "m", "role": "R1", "powers": ["WRITE"], "resources": ["repo"], "project_id": "p1", "revoked_at_sequence": 8}
        approval = {"approved": True, "manifest_digest": "m", "role": "R1", "approved_powers": ["WRITE"], "approved_resources": ["repo"],
                    "principal_authenticated": True, "authority_grant_valid": True, "project_id": "p1", "approval_sequence": 7}
        self.assertEqual(authorize_power_activation(manifest, approval, ["WRITE"], role="R1", requested_resources=["repo"], current_sequence=8)["status"], "ACTIVATION_REVOKED")

    # EXP-ECC-5 — recomputed cryptographic identity and live-endpoint state.
    def test_e5_canonical_digest_collision_is_rejected_by_recomputation(self):
        expected_material = {"tool_id": "t", "harness_id": "h", "transport": "stdio", "endpoint": "A", "argv": ["x"], "permission_profile": "r", "credential_profile_fingerprint": "cred1"}
        current_material = dict(expected_material, endpoint="B")
        forged = digest(expected_material)
        expected = dict(expected_material, argv_digest=digest(["x"]), canonical_digest=forged, semantic_digest="s", read_ok=True)
        current = dict(current_material, argv_digest=digest(["x"]), canonical_digest=forged, semantic_digest="s", read_ok=True)
        self.assertEqual(check_tool_configuration(expected, current)["status"], "TOOL_CONFIG_ATTESTATION_INVALID")

    def test_e5_secret_redaction_collision_is_rejected(self):
        base = {"tool_id": "t", "harness_id": "h", "transport": "stdio", "endpoint": "A", "argv_digest": "a", "permission_profile": "r", "credential_profile": "REDACTED", "canonical_digest": "d", "semantic_digest": "s", "read_ok": True}
        expected = dict(base, credential_attestation="cred-fp-1")
        current = dict(base, credential_attestation="cred-fp-2")
        self.assertEqual(check_tool_configuration(expected, current)["status"], "TOOL_CONFIG_DRIFT")

    def test_e5_dns_endpoint_rebinding_is_rejected(self):
        base = {"tool_id": "t", "harness_id": "h", "transport": "https", "endpoint": "https://mcp.example", "argv_digest": "a", "permission_profile": "r", "credential_profile": "c", "canonical_digest": "d", "semantic_digest": "s", "read_ok": True}
        expected = dict(base, resolved_endpoint="203.0.113.10")
        current = dict(base, resolved_endpoint="203.0.113.99")
        self.assertEqual(check_tool_configuration(expected, current)["status"], "TOOL_CONFIG_DRIFT")

    # EXP-ECC-6 — remain deferred without real identity/manual attestation.
    def test_e6_different_provider_claim_without_attestation_is_unverified(self):
        binding = {"packet_current": True, "packet_digest": "p", "consented_packet_digest": "p", "reviewer_slot": "R3", "selected_model": "m", "selected_provider": "A", "returned_provider": "B",
                   "provider_identity_attested": False, "gateway_route_attested": False, "context_isolation_evidenced": True, "transport_enabled": True}
        self.assertEqual(classify_review_binding(binding)["provider_relationship"], "PROVIDER_IDENTITY_UNKNOWN")

    def test_e6_forged_manual_attestation_has_zero_credit(self):
        binding = {"packet_current": True, "packet_digest": "p", "consented_packet_digest": "p", "reviewer_slot": "R3", "selected_model": "m", "selected_provider": "A", "returned_provider": "A",
                   "provider_identity_attested": True, "gateway_route_attested": True, "context_isolation_evidenced": True, "transport_enabled": True,
                   "evidence_class": "INDEPENDENT_MANUAL_REVIEW", "manual_attestation_valid": True, "manual_attestation_principal_authenticated": False}
        self.assertEqual(classify_review_binding(binding)["manual_review_threshold_contribution"], 0)

    def test_e6_packet_replay_after_consent_sequence_is_rejected(self):
        binding = {"packet_current": True, "packet_digest": "p", "consented_packet_digest": "p", "reviewer_slot": "R3", "selected_model": "m", "selected_provider": "A", "returned_provider": "A",
                   "provider_identity_attested": True, "gateway_route_attested": True, "context_isolation_evidenced": True, "transport_enabled": True,
                   "consent_sequence": 10, "egress_sequence": 11, "consent_max_egress_sequence": 10}
        self.assertEqual(classify_review_binding(binding)["status"], "REVIEW_EGRESS_CONSENT_STALE")

    # EXP-ECC-7 — reuse governed claim/dependency evidence, not self-asserted flags.
    def test_e7_self_asserted_independent_support_is_not_promotable(self):
        proposal = {"artifact_digest": "a", "reviewed_digest": "a", "scope": "project", "target_scope": "project",
                    "source_verified": True, "independent_support": True, "governed_approval": True,
                    "claim_governance_evidence_valid": False, "dependency_graph_current": False}
        self.assertEqual(authorize_learning_promotion(proposal)["status"], "LEARNING_GOVERNANCE_EVIDENCE_INSUFFICIENT")

    def test_e7_retraction_requires_dependency_traversal(self):
        proposal = {"artifact_digest": "a", "reviewed_digest": "a", "scope": "project", "target_scope": "project",
                    "source_verified": True, "independent_support": True, "governed_approval": True,
                    "claim_governance_evidence_valid": True, "dependency_graph_current": True,
                    "parent_retracted": True, "retraction_traversal_complete": False}
        self.assertEqual(authorize_learning_promotion(proposal)["status"], "LEARNING_PROPOSAL_REASSESSMENT_REQUIRED")

    def test_e7_stale_learned_artifact_cannot_be_session_injected_as_authority(self):
        proposal = {"artifact_digest": "a", "reviewed_digest": "a", "scope": "project", "target_scope": "project",
                    "stale": True, "session_injection_requested": True, "claim_governance_evidence_valid": True, "dependency_graph_current": True}
        result = authorize_learning_promotion(proposal)
        self.assertFalse(result["promotable"])
        self.assertFalse(result["advisory_allowed"])


if __name__ == "__main__":
    unittest.main()
