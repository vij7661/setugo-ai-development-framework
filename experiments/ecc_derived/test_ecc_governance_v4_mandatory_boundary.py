from __future__ import annotations

import inspect
import unittest
from unittest.mock import patch

import ecc_governance as gov
from test_ecc_governance_v3_omission_hardening import (
    base_control,
    legacy_event,
    strict_event,
    declared,
    strict_executable,
    legacy_envelope,
    strict_envelope,
    cap_req,
    legacy_manifest,
    legacy_approval,
    strict_manifest,
    strict_approval,
    legacy_cfg,
    strict_cfg,
    legacy_binding,
    legacy_manual_binding,
    strict_binding,
    strict_proposal,
)

try:
    import ecc_candidate_boundary as boundary
except ImportError:
    boundary = None


STRICT = "REQUIREMENT_CANDIDATE"
HISTORICAL = "HISTORICAL_REFERENCE"


class ECCV4MandatoryCandidateBoundary(unittest.TestCase):
    def require_boundary(self):
        self.assertIsNotNone(boundary, "mandatory candidate-boundary module is missing")
        return boundary

    # Every legacy result must identify itself as historical evidence only.
    def test_e1_default_legacy_result_is_explicitly_historical(self):
        r = gov.assess_control_execution(base_control(), legacy_event(), candidate="shaA", action_id="act1")
        self.assertEqual(r["status"], "VERIFIED")
        self.assertEqual(r.get("evaluation_class"), HISTORICAL)

    def test_e2_default_legacy_result_is_explicitly_historical(self):
        r = gov.check_declared_executable_equivalence(declared(), dict(declared()))
        self.assertEqual(r["status"], "EQUIVALENT")
        self.assertEqual(r.get("evaluation_class"), HISTORICAL)

    def test_e3_default_legacy_result_is_explicitly_historical(self):
        r = gov.qualify_role_binding(
            "R1", "legacy-model", legacy_envelope(), {"write_confinement": "NATIVE_ENFORCEMENT"}
        )
        self.assertEqual(r["status"], "ROLE_BINDING_ELIGIBLE")
        self.assertEqual(r.get("evaluation_class"), HISTORICAL)

    def test_e4_default_legacy_result_is_explicitly_historical(self):
        r = gov.authorize_power_activation(
            legacy_manifest(), legacy_approval(), ["WRITE"], role="R1", requested_resources=["repo"]
        )
        self.assertEqual(r["status"], "ACTIVATION_ALLOWED")
        self.assertEqual(r.get("evaluation_class"), HISTORICAL)

    def test_e5_default_legacy_result_is_explicitly_historical(self):
        c = legacy_cfg()
        r = gov.check_tool_configuration(c, dict(c))
        self.assertEqual(r["status"], "TOOL_CONFIG_CURRENT")
        self.assertEqual(r.get("evaluation_class"), HISTORICAL)

    def test_e6_default_legacy_result_is_explicitly_historical(self):
        r = gov.classify_review_binding(legacy_manual_binding())
        self.assertEqual(r["manual_review_threshold_contribution"], 1)
        self.assertEqual(r.get("evaluation_class"), HISTORICAL)

    def test_e7_default_legacy_result_is_explicitly_historical(self):
        p = {
            "artifact_digest": "a", "reviewed_digest": "a",
            "scope": "project", "target_scope": "project",
            "source_verified": True, "independent_support": True,
            "governed_approval": True,
        }
        r = gov.authorize_learning_promotion(p)
        self.assertEqual(r["status"], "LEARNING_PROPOSAL_PROMOTABLE")
        self.assertTrue(r["promotable"])
        self.assertEqual(r.get("evaluation_class"), HISTORICAL)

    def test_candidate_boundary_exports_seven_strict_only_entrypoints(self):
        b = self.require_boundary()
        names = {
            "assess_control_execution_candidate",
            "check_declared_executable_equivalence_candidate",
            "qualify_role_binding_candidate",
            "authorize_power_activation_candidate",
            "check_tool_configuration_candidate",
            "classify_review_binding_candidate",
            "authorize_learning_promotion_candidate",
        }
        self.assertEqual({name for name in names if hasattr(b, name)}, names)

    def test_candidate_entrypoints_have_no_caller_selectable_mode_flag(self):
        b = self.require_boundary()
        for name in (
            "assess_control_execution_candidate",
            "check_declared_executable_equivalence_candidate",
            "qualify_role_binding_candidate",
            "authorize_power_activation_candidate",
            "check_tool_configuration_candidate",
            "classify_review_binding_candidate",
            "authorize_learning_promotion_candidate",
        ):
            with self.subTest(entrypoint=name):
                self.assertNotIn("requirement_candidate", inspect.signature(getattr(b, name)).parameters)

    def test_candidate_gate_rejects_historical_and_unclassified_results(self):
        b = self.require_boundary()
        self.assertFalse(b.candidate_result_eligible({"evaluation_class": HISTORICAL, "status": "VERIFIED"}))
        self.assertFalse(b.candidate_result_eligible({"status": "VERIFIED"}))

    def test_candidate_gate_accepts_only_strict_candidate_class(self):
        b = self.require_boundary()
        self.assertTrue(b.candidate_result_eligible({"evaluation_class": STRICT, "status": "VERIFIED"}))

    def test_runtime_trust_manifest_is_enforced_by_candidate_boundary(self):
        b = self.require_boundary()
        self.assertTrue(b.verify_runtime_policy())
        with patch.object(b, "verify_runtime_policy", return_value=False):
            r = b.assess_control_execution_candidate(
                base_control(), strict_event(), candidate="shaA", action_id="act1"
            )
        self.assertEqual(r["status"], "CANDIDATE_BOUNDARY_POLICY_INVALID")
        self.assertFalse(r.get("verified", True))

    # Positive controls prove the new boundary is not a block-all wrapper.
    def test_strict_candidate_boundary_positive_controls(self):
        b = self.require_boundary()
        r1 = b.assess_control_execution_candidate(base_control(), strict_event(), candidate="shaA", action_id="act1")
        self.assertEqual(r1["status"], "VERIFIED")
        self.assertEqual(r1.get("evaluation_class"), STRICT)

        r2 = b.check_declared_executable_equivalence_candidate(declared(), strict_executable())
        self.assertEqual(r2["status"], "EQUIVALENT")
        self.assertEqual(r2.get("evaluation_class"), STRICT)

        r3 = b.qualify_role_binding_candidate("R1", "user-selected-qualified-model", strict_envelope(), cap_req())
        self.assertEqual(r3["status"], "ROLE_BINDING_ELIGIBLE")
        self.assertEqual(r3.get("evaluation_class"), STRICT)

        r4 = b.authorize_power_activation_candidate(
            strict_manifest(), strict_approval(), ["WRITE"], role="R1",
            requested_resources=["repo"], current_sequence=7,
        )
        self.assertEqual(r4["status"], "ACTIVATION_ALLOWED")
        self.assertEqual(r4.get("evaluation_class"), STRICT)

        c = strict_cfg()
        r5 = b.check_tool_configuration_candidate(c, dict(c))
        self.assertEqual(r5["status"], "TOOL_CONFIG_CURRENT")
        self.assertEqual(r5.get("evaluation_class"), STRICT)

        r6 = b.classify_review_binding_candidate(
            strict_binding() | {"evidence_class": "AI_GENERATED_ENGINEERING_FEEDBACK_ONLY"}
        )
        self.assertEqual(r6["manual_review_threshold_contribution"], 0)
        self.assertEqual(r6.get("evaluation_class"), STRICT)

        r7 = b.authorize_learning_promotion_candidate(strict_proposal())
        self.assertEqual(r7["status"], "LEARNING_PROPOSAL_REFERENCE_ELIGIBLE")
        self.assertFalse(r7["promotable"])
        self.assertEqual(r7.get("evaluation_class"), STRICT)

    # Independent cross-checks must catch a favorable result forged by/shared through the common core.
    def test_e1_shared_core_false_green_is_independently_rejected(self):
        b = self.require_boundary()
        forged = {"verified": True, "allowed": True, "status": "VERIFIED", "evaluation_class": STRICT}
        with patch.object(b.gov, "assess_control_execution", return_value=forged):
            r = b.assess_control_execution_candidate(base_control(), legacy_event(), candidate="shaA", action_id="act1")
        self.assertEqual(r["status"], "CANDIDATE_INDEPENDENT_CROSSCHECK_FAILED")
        self.assertFalse(r.get("verified", True))

    def test_e2_shared_core_false_green_is_independently_rejected(self):
        b = self.require_boundary()
        forged = {"equivalent": True, "status": "EQUIVALENT", "evaluation_class": STRICT}
        with patch.object(b.gov, "check_declared_executable_equivalence", return_value=forged):
            r = b.check_declared_executable_equivalence_candidate(declared(), dict(declared()))
        self.assertEqual(r["status"], "CANDIDATE_INDEPENDENT_CROSSCHECK_FAILED")
        self.assertFalse(r.get("equivalent", True))

    def test_e3_shared_core_false_green_is_independently_rejected(self):
        b = self.require_boundary()
        forged = {"eligible": True, "status": "ROLE_BINDING_ELIGIBLE", "evaluation_class": STRICT}
        with patch.object(b.gov, "qualify_role_binding", return_value=forged):
            r = b.qualify_role_binding_candidate("R1", "model-x", legacy_envelope(), cap_req())
        self.assertEqual(r["status"], "CANDIDATE_INDEPENDENT_CROSSCHECK_FAILED")
        self.assertFalse(r.get("eligible", True))

    def test_e4_shared_core_false_green_is_independently_rejected(self):
        b = self.require_boundary()
        forged = {"authorized": True, "status": "ACTIVATION_ALLOWED", "evaluation_class": STRICT}
        with patch.object(b.gov, "authorize_power_activation", return_value=forged):
            r = b.authorize_power_activation_candidate(
                legacy_manifest(), legacy_approval(), ["WRITE"], role="R1",
                requested_resources=["repo"], current_sequence=7,
            )
        self.assertEqual(r["status"], "CANDIDATE_INDEPENDENT_CROSSCHECK_FAILED")
        self.assertFalse(r.get("authorized", True))

    def test_e5_shared_core_false_green_is_independently_rejected(self):
        b = self.require_boundary()
        forged = {"current": True, "status": "TOOL_CONFIG_CURRENT", "stale_dependents": False, "evaluation_class": STRICT}
        c = legacy_cfg()
        with patch.object(b.gov, "check_tool_configuration", return_value=forged):
            r = b.check_tool_configuration_candidate(c, dict(c))
        self.assertEqual(r["status"], "CANDIDATE_INDEPENDENT_CROSSCHECK_FAILED")
        self.assertFalse(r.get("current", True))


if __name__ == "__main__":
    unittest.main()
