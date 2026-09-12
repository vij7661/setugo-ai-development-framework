from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from ecc_governance import (  # noqa: E402
    assess_control_execution,
    authorize_learning_promotion,
    authorize_power_activation,
    check_declared_executable_equivalence,
    check_tool_configuration,
    classify_review_binding,
    qualify_role_binding,
)


class ExpEcc1ExecutionAttestationTests(unittest.TestCase):
    def _control(self):
        return {"control_id": "hook-A", "version": "v1", "digest": "sha-control", "required": True}

    def _event(self):
        return {
            "control_id": "hook-A",
            "version": "v1",
            "control_digest": "sha-control",
            "candidate": "cand-1",
            "action_id": "act-1",
            "invocation_id": "inv-1",
            "input_digest": "in-1",
            "result_digest": "out-1",
            "started": True,
            "result_recorded": True,
            "execution_ok": True,
        }

    def test_configured_without_invocation_is_not_verified(self):
        r = assess_control_execution(self._control(), None, candidate="cand-1", action_id="act-1")
        self.assertEqual(r["status"], "CONTROL_NOT_INVOKED")
        self.assertFalse(r["verified"])

    def test_wrapper_exception_cannot_be_success(self):
        e = self._event(); e["execution_ok"] = False; e["error"] = "wrapper exception"
        r = assess_control_execution(self._control(), e, candidate="cand-1", action_id="act-1")
        self.assertEqual(r["status"], "CONTROL_EXECUTION_FAILED")

    def test_stale_control_version_fails(self):
        e = self._event(); e["version"] = "v0"
        r = assess_control_execution(self._control(), e, candidate="cand-1", action_id="act-1")
        self.assertEqual(r["status"], "CONTROL_VERSION_MISMATCH")

    def test_exact_execution_verifies(self):
        r = assess_control_execution(self._control(), self._event(), candidate="cand-1", action_id="act-1")
        self.assertEqual(r["status"], "VERIFIED")
        self.assertTrue(r["verified"])


class ExpEcc2DeclaredExecutableTests(unittest.TestCase):
    def test_fail_closed_declaration_vs_fail_open_runtime_rejected(self):
        d = {"mode": "BLOCKING", "on_internal_error": "DENY", "candidate_binding": "EXACT"}
        x = {"mode": "BLOCKING", "on_internal_error": "ALLOW", "candidate_binding": "EXACT"}
        self.assertEqual(check_declared_executable_equivalence(d, x)["status"], "ENFORCEMENT_MISMATCH")

    def test_blocking_declaration_vs_telemetry_runtime_rejected(self):
        d = {"mode": "BLOCKING", "on_internal_error": "DENY", "candidate_binding": "EXACT"}
        x = {"mode": "ADVISORY", "on_internal_error": "ALLOW", "candidate_binding": "NONE"}
        self.assertFalse(check_declared_executable_equivalence(d, x)["equivalent"])

    def test_exact_equivalence_passes(self):
        d = {"mode": "BLOCKING", "on_internal_error": "DENY", "candidate_binding": "EXACT"}
        self.assertTrue(check_declared_executable_equivalence(d, copy.deepcopy(d))["equivalent"])


class ExpEcc3HarnessEnvelopeTests(unittest.TestCase):
    def _envelope(self):
        return {
            "harness_id": "h1", "runtime_version": "1.2.0", "config_digest": "cfg-1",
            "capabilities": {"read_only_review": "NATIVE_ENFORCEMENT", "filesystem_write": "NATIVE_ENFORCEMENT"},
        }

    def test_instruction_only_cannot_satisfy_native_requirement(self):
        e = self._envelope(); e["capabilities"]["read_only_review"] = "INSTRUCTION_ONLY"
        r = qualify_role_binding("R2", "model-x", e, {"read_only_review": "NATIVE_ENFORCEMENT"})
        self.assertEqual(r["status"], "HARNESS_CAPABILITY_INSUFFICIENT")

    def test_user_selected_qualified_model_can_fill_r1(self):
        r = qualify_role_binding("R1", "any-qualified-model", self._envelope(), {"filesystem_write": "NATIVE_ENFORCEMENT"})
        self.assertEqual(r["status"], "ROLE_BINDING_ELIGIBLE")

    def test_unknown_capability_fails_closed(self):
        e = self._envelope(); e["capabilities"].pop("read_only_review")
        r = qualify_role_binding("R3", "model-y", e, {"read_only_review": "NATIVE_ENFORCEMENT"})
        self.assertEqual(r["status"], "HARNESS_CAPABILITY_UNKNOWN")


class ExpEcc4ActivationConsentTests(unittest.TestCase):
    def _manifest(self):
        return {"manifest_id": "p1", "digest": "m1", "powers": ["read_files", "write_files"], "role": "R1", "revoked": False}

    def test_consent_digest_must_match_manifest(self):
        a = {"manifest_digest": "old", "role": "R1", "approved_powers": ["read_files", "write_files"], "approved": True}
        r = authorize_power_activation(self._manifest(), a, ["write_files"], role="R1")
        self.assertEqual(r["status"], "ACTIVATION_BINDING_MISMATCH")

    def test_read_consent_cannot_authorize_write(self):
        a = {"manifest_digest": "m1", "role": "R1", "approved_powers": ["read_files"], "approved": True}
        r = authorize_power_activation(self._manifest(), a, ["write_files"], role="R1")
        self.assertEqual(r["status"], "ACTIVATION_SCOPE_EXCEEDED")

    def test_exact_consent_activates_only_requested_subset(self):
        a = {"manifest_digest": "m1", "role": "R1", "approved_powers": ["read_files", "write_files"], "approved": True}
        r = authorize_power_activation(self._manifest(), a, ["read_files"], role="R1")
        self.assertEqual(r["status"], "ACTIVATION_ALLOWED")


class ExpEcc5ToolConfigTests(unittest.TestCase):
    def _cfg(self):
        return {
            "tool_id": "mcp-a", "harness_id": "h1", "transport": "stdio", "endpoint": None,
            "argv_digest": "argv-1", "permission_profile": "read", "credential_profile": "cp1", "canonical_digest": "cfg-a",
        }

    def test_same_name_different_endpoint_is_drift(self):
        old = self._cfg(); new = self._cfg(); new.update({"transport": "http", "endpoint": "https://example.invalid", "canonical_digest": "cfg-b"})
        r = check_tool_configuration(old, new)
        self.assertEqual(r["status"], "TOOL_CONFIG_DRIFT")
        self.assertTrue(r["stale_dependents"])

    def test_cross_harness_reuse_is_rejected(self):
        old = self._cfg(); new = self._cfg(); new["harness_id"] = "h2"
        r = check_tool_configuration(old, new)
        self.assertEqual(r["status"], "TOOL_CONFIG_DRIFT")

    def test_exact_canonical_config_remains_current(self):
        r = check_tool_configuration(self._cfg(), copy.deepcopy(self._cfg()))
        self.assertEqual(r["status"], "TOOL_CONFIG_CURRENT")


class ExpEcc6ReviewBindingTests(unittest.TestCase):
    def _binding(self):
        return {
            "candidate": "cand-1", "packet_digest": "pkt-1", "reviewer_slot": "R2",
            "selected_model": "model-a", "selected_provider": "provider-a", "returned_provider": "provider-a",
            "gateway": None, "evidence_class": "AI_GENERATED_ENGINEERING_FEEDBACK_ONLY",
            "packet_current": True, "context_isolation_evidenced": True,
        }

    def test_same_provider_not_laundered_as_cross_provider(self):
        r = classify_review_binding(self._binding())
        self.assertEqual(r["provider_relationship"], "SAME_PROVIDER_CONFIRMED")

    def test_unknown_gateway_route_cannot_claim_different_provider(self):
        b = self._binding(); b["gateway"] = "router"; b["returned_provider"] = None
        r = classify_review_binding(b)
        self.assertEqual(r["provider_relationship"], "GATEWAY_RELATIONSHIP_UNVERIFIED")

    def test_ai_feedback_has_zero_manual_threshold_contribution(self):
        r = classify_review_binding(self._binding())
        self.assertEqual(r["manual_review_threshold_contribution"], 0)

    def test_stale_packet_is_ineligible(self):
        b = self._binding(); b["packet_current"] = False
        r = classify_review_binding(b)
        self.assertEqual(r["status"], "REVIEW_BINDING_STALE")


class ExpEcc7LearningPromotionTests(unittest.TestCase):
    def _proposal(self):
        return {
            "proposal_id": "lp1", "scope": "project-a", "confidence": 0.99,
            "source_verified": False, "independent_support": False, "governed_approval": False,
            "parent_retracted": False, "artifact_digest": "a1", "reviewed_digest": "a1",
        }

    def test_confidence_alone_cannot_promote(self):
        r = authorize_learning_promotion(self._proposal())
        self.assertEqual(r["status"], "LEARNING_PROPOSAL_NOT_PROMOTABLE")

    def test_consensus_flag_cannot_replace_evidence(self):
        p = self._proposal(); p["model_consensus"] = True
        self.assertFalse(authorize_learning_promotion(p)["promotable"])

    def test_retracted_parent_requires_reassessment(self):
        p = self._proposal(); p.update({"source_verified": True, "independent_support": True, "governed_approval": True, "parent_retracted": True})
        r = authorize_learning_promotion(p)
        self.assertEqual(r["status"], "LEARNING_PROPOSAL_REASSESSMENT_REQUIRED")

    def test_fully_supported_exact_proposal_can_be_promotable(self):
        p = self._proposal(); p.update({"source_verified": True, "independent_support": True, "governed_approval": True})
        r = authorize_learning_promotion(p)
        self.assertEqual(r["status"], "LEARNING_PROPOSAL_PROMOTABLE")
        self.assertTrue(r["promotable"])


if __name__ == "__main__":
    unittest.main()
