from __future__ import annotations

import functools
import inspect
import unittest
from unittest.mock import patch

import ecc_governance as gov
import ecc_candidate_boundary as boundary
from test_ecc_governance_v3_omission_hardening import (
    base_control,
    strict_event,
    declared,
    strict_executable,
    strict_envelope,
    cap_req,
    strict_manifest,
    strict_approval,
    strict_cfg,
    strict_binding,
    strict_proposal,
)

try:
    import ecc_governance_strict as strict_core
except ImportError:
    strict_core = None

try:
    import ecc_reference_evidence as reference_evidence
except ImportError:
    reference_evidence = None

STRICT = "REQUIREMENT_CANDIDATE"
HISTORICAL = "HISTORICAL_REFERENCE"


class ECCV5ClosedCandidateBoundary(unittest.TestCase):
    def test_public_core_has_no_caller_selectable_strict_mode(self):
        names = (
            "assess_control_execution",
            "check_declared_executable_equivalence",
            "qualify_role_binding",
            "authorize_power_activation",
            "check_tool_configuration",
            "classify_review_binding",
            "authorize_learning_promotion",
        )
        for name in names:
            with self.subTest(name=name):
                self.assertNotIn("requirement_candidate", inspect.signature(getattr(gov, name)).parameters)
        self.assertNotIn("requirement_candidate", inspect.getsource(gov))

    def test_direct_strict_keyword_is_rejected_for_all_seven_public_core_calls(self):
        calls = (
            lambda: gov.assess_control_execution(base_control(), strict_event(), candidate="shaA", action_id="act1", requirement_candidate=True),
            lambda: gov.check_declared_executable_equivalence(declared(), strict_executable(), requirement_candidate=True),
            lambda: gov.qualify_role_binding("R1", "model", strict_envelope(), cap_req(), requirement_candidate=True),
            lambda: gov.authorize_power_activation(strict_manifest(), strict_approval(), ["WRITE"], role="R1", requested_resources=["repo"], current_sequence=7, requirement_candidate=True),
            lambda: gov.check_tool_configuration(strict_cfg(), strict_cfg(), requirement_candidate=True),
            lambda: gov.classify_review_binding(strict_binding(), requirement_candidate=True),
            lambda: gov.authorize_learning_promotion(strict_proposal(), requirement_candidate=True),
        )
        for call in calls:
            with self.subTest(call=call):
                with self.assertRaises(TypeError):
                    call()

    def test_alias_partial_wrapper_and_serialized_flag_cannot_restore_strict_core_mode(self):
        alias = gov.assess_control_execution
        partial = functools.partial(alias, base_control(), strict_event(), candidate="shaA", action_id="act1")
        forwarded = {"candidate": "shaA", "action_id": "act1", "requirement_candidate": True}
        for call in (
            lambda: alias(base_control(), strict_event(), **forwarded),
            lambda: partial(requirement_candidate=True),
            lambda: (lambda **kw: alias(base_control(), strict_event(), **kw))(**forwarded),
        ):
            with self.assertRaises(TypeError):
                call()

    def test_strict_core_and_reference_evidence_are_separate_boundary_dependencies(self):
        self.assertIsNotNone(strict_core, "private strict core is missing")
        self.assertIsNotNone(reference_evidence, "separate reference evidence source is missing")
        source = inspect.getsource(boundary)
        self.assertIn("ecc_governance_strict", source)
        self.assertIn("ecc_reference_evidence", source)
        self.assertNotIn("requirement_candidate=True", source)

    def test_candidate_result_gate_requires_boundary_marker_kind_and_favorable_status(self):
        self.assertFalse(boundary.candidate_result_eligible({"evaluation_class": STRICT, "status": "VERIFIED"}))
        self.assertFalse(boundary.candidate_result_eligible({
            "evaluation_class": STRICT, "candidate_eligible": True,
            "candidate_kind": "execution", "status": "CANDIDATE_BOUNDARY_POLICY_INVALID",
        }))
        self.assertFalse(boundary.candidate_result_eligible({
            "evaluation_class": STRICT, "candidate_eligible": True,
            "candidate_kind": "execution", "status": "CANDIDATE_INDEPENDENT_CROSSCHECK_FAILED",
        }))
        self.assertFalse(boundary.candidate_result_eligible({
            "evaluation_class": STRICT, "candidate_eligible": True,
            "candidate_kind": "execution", "status": "CONTROL_EVIDENCE_INVALID",
        }))
        self.assertTrue(boundary.candidate_result_eligible({
            "evaluation_class": STRICT, "candidate_eligible": True,
            "candidate_kind": "execution", "status": "VERIFIED",
        }))

    def _reference_positive_inputs(self):
        e1 = strict_event() | {"reference_evidence_id": "ECC-V5-E1-POS"}
        e2 = strict_executable() | {"reference_evidence_id": "ECC-V5-E2-POS"}
        e3 = strict_envelope() | {"reference_evidence_id": "ECC-V5-E3-POS"}
        a4 = strict_approval() | {"reference_evidence_id": "ECC-V5-E4-POS"}
        c5 = strict_cfg() | {"reference_evidence_id": "ECC-V5-E5-POS"}
        return e1, e2, e3, a4, c5

    def test_reference_positive_controls_receive_boundary_eligibility_only_after_independent_source(self):
        e1, e2, e3, a4, c5 = self._reference_positive_inputs()
        results = (
            boundary.assess_control_execution_candidate(base_control(), e1, candidate="shaA", action_id="act1"),
            boundary.check_declared_executable_equivalence_candidate(declared(), e2),
            boundary.qualify_role_binding_candidate("R1", "user-selected-qualified-model", e3, cap_req()),
            boundary.authorize_power_activation_candidate(strict_manifest(), a4, ["WRITE"], role="R1", requested_resources=["repo"], current_sequence=7),
            boundary.check_tool_configuration_candidate(c5, dict(c5)),
        )
        expected = ("VERIFIED", "EQUIVALENT", "ROLE_BINDING_ELIGIBLE", "ACTIVATION_ALLOWED", "TOOL_CONFIG_CURRENT")
        for result, status in zip(results, expected):
            with self.subTest(status=status):
                self.assertEqual(result["status"], status)
                self.assertTrue(result.get("candidate_eligible"))
                self.assertTrue(boundary.candidate_result_eligible(result))

    def test_same_favorable_fixtures_without_independent_reference_evidence_are_blocked(self):
        results = (
            boundary.assess_control_execution_candidate(base_control(), strict_event(), candidate="shaA", action_id="act1"),
            boundary.check_declared_executable_equivalence_candidate(declared(), strict_executable()),
            boundary.qualify_role_binding_candidate("R1", "user-selected-qualified-model", strict_envelope(), cap_req()),
            boundary.authorize_power_activation_candidate(strict_manifest(), strict_approval(), ["WRITE"], role="R1", requested_resources=["repo"], current_sequence=7),
            boundary.check_tool_configuration_candidate(strict_cfg(), strict_cfg()),
        )
        for result in results:
            with self.subTest(result=result):
                self.assertEqual(result["status"], "CANDIDATE_INDEPENDENT_EVIDENCE_REQUIRED")
                self.assertFalse(result.get("candidate_eligible", False))
                self.assertFalse(boundary.candidate_result_eligible(result))

    def test_review_and_learning_remain_reference_only_and_not_candidate_eligible(self):
        review = boundary.classify_review_binding_candidate(
            strict_binding() | {"evidence_class": "AI_GENERATED_ENGINEERING_FEEDBACK_ONLY"}
        )
        learning = boundary.authorize_learning_promotion_candidate(strict_proposal())
        self.assertEqual(review.get("manual_review_threshold_contribution"), 0)
        self.assertFalse(review.get("candidate_eligible", False))
        self.assertFalse(boundary.candidate_result_eligible(review))
        self.assertFalse(learning.get("promotable", True))
        self.assertFalse(learning.get("candidate_eligible", False))
        self.assertFalse(boundary.candidate_result_eligible(learning))

    def test_runtime_policy_binds_imported_module_identity_not_only_disk_hashes(self):
        self.assertTrue(boundary.verify_runtime_policy())
        with patch.object(boundary.gov, "__file__", "/tmp/shadow/ecc_governance.py"):
            self.assertFalse(boundary.verify_runtime_policy())
        self.assertIsNotNone(strict_core)
        with patch.object(boundary.strict_core, "__file__", "/tmp/shadow/ecc_governance_strict.py"):
            self.assertFalse(boundary.verify_runtime_policy())
        self.assertIsNotNone(reference_evidence)
        with patch.object(boundary.reference_evidence, "__file__", "/tmp/shadow/ecc_reference_evidence.py"):
            self.assertFalse(boundary.verify_runtime_policy())

    def test_in_memory_strict_core_monkeypatch_is_detected(self):
        self.assertIsNotNone(strict_core)
        with patch.object(boundary.strict_core, "assess_control_execution_candidate", lambda *a, **k: {"status": "VERIFIED", "verified": True}):
            self.assertFalse(boundary.verify_runtime_policy())

    def test_in_memory_reference_evidence_monkeypatch_is_detected(self):
        self.assertIsNotNone(reference_evidence)
        with patch.object(boundary.reference_evidence, "lookup_reference_evidence", lambda *a, **k: {"valid": True}):
            self.assertFalse(boundary.verify_runtime_policy())

    def test_policy_is_reverified_immediately_before_candidate_eligibility(self):
        e1, *_ = self._reference_positive_inputs()
        original = boundary.verify_runtime_policy
        calls = {"n": 0}
        def flip():
            calls["n"] += 1
            return calls["n"] == 1
        with patch.object(boundary, "verify_runtime_policy", side_effect=flip):
            result = boundary.assess_control_execution_candidate(base_control(), e1, candidate="shaA", action_id="act1")
        self.assertGreaterEqual(calls["n"], 2)
        self.assertEqual(result["status"], "CANDIDATE_BOUNDARY_POLICY_INVALID")
        self.assertFalse(result.get("candidate_eligible", False))
        self.assertIsNotNone(original)


if __name__ == "__main__":
    unittest.main()
