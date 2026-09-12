from __future__ import annotations

import types
import unittest
from unittest.mock import patch

import ecc_candidate_boundary as boundary
from test_ecc_governance_v3_omission_hardening import base_control, strict_event


STRICT = "REQUIREMENT_CANDIDATE"


def positive_execution_event(evidence_id="ECC-V5-E1-POS"):
    return strict_event() | {"reference_evidence_id": evidence_id}


def matching_execution_record(control, event, candidate="shaA", action_id="act1"):
    return {
        "kind": "execution",
        "candidate": candidate,
        "action_id": action_id,
        "control_id": control["control_id"],
        "control_version": control["version"],
        "control_digest": control["digest"],
        "process_identity": event["process_identity"],
        "action_sequence": event["verified_action_sequence"],
        "invocation_id": event["invocation_id"],
    }


def favorable_execution_result():
    return {
        "status": "VERIFIED",
        "verified": True,
        "allowed": True,
        "evaluation_class": STRICT,
    }


class ECCV8VerifierSubstitution(unittest.TestCase):
    def genuine_result(self):
        return boundary.assess_control_execution_candidate(
            base_control(), positive_execution_event(), candidate="shaA", action_id="act1"
        )

    def test_public_verifier_is_diagnostic_not_candidate_authority_for_issuance(self):
        with patch.object(boundary, "verify_runtime_policy", return_value=False):
            result = self.genuine_result()
        self.assertEqual(result["status"], "VERIFIED")
        self.assertTrue(boundary.candidate_result_eligible(result))

    def test_public_verifier_is_diagnostic_not_candidate_authority_for_consumption(self):
        result = self.genuine_result()
        self.assertTrue(boundary.candidate_result_eligible(result))
        with patch.object(boundary, "verify_runtime_policy", return_value=False):
            self.assertTrue(boundary.candidate_result_eligible(result))

    def test_always_true_public_verifier_plus_reference_function_tamper_cannot_mint(self):
        control = base_control()
        event = positive_execution_event("FORGED-V8-EVIDENCE")
        forged_record = matching_execution_record(control, event)
        with patch.object(boundary, "verify_runtime_policy", return_value=True), patch.object(
            boundary.reference_evidence,
            "lookup_reference_evidence",
            return_value=forged_record,
        ):
            result = boundary.assess_control_execution_candidate(
                control, event, candidate="shaA", action_id="act1"
            )
            self.assertFalse(boundary.candidate_result_eligible(result))
        self.assertNotEqual(result["status"], "VERIFIED")

    def test_always_true_public_verifier_plus_strict_and_reference_tamper_cannot_mint(self):
        control = base_control()
        event = positive_execution_event("FORGED-V8-EVIDENCE")
        forged_record = matching_execution_record(control, event)
        with patch.object(boundary, "verify_runtime_policy", return_value=True), patch.object(
            boundary.strict_core,
            "assess_control_execution_candidate",
            return_value=favorable_execution_result(),
        ), patch.object(
            boundary.reference_evidence,
            "lookup_reference_evidence",
            return_value=forged_record,
        ):
            result = boundary.assess_control_execution_candidate(
                control, event, candidate="shaA", action_id="act1"
            )
            self.assertFalse(boundary.candidate_result_eligible(result))
        self.assertNotEqual(result["status"], "VERIFIED")

    def test_module_alias_substitution_plus_public_verifier_substitution_cannot_mint(self):
        control = base_control()
        event = positive_execution_event("FORGED-V8-EVIDENCE")
        forged_record = matching_execution_record(control, event)
        fake_strict = types.SimpleNamespace(
            assess_control_execution_candidate=lambda *a, **k: favorable_execution_result(),
        )
        fake_evidence = types.SimpleNamespace(
            lookup_reference_evidence=lambda *a, **k: dict(forged_record),
        )
        with patch.object(boundary, "verify_runtime_policy", return_value=True), patch.object(
            boundary, "strict_core", fake_strict
        ), patch.object(boundary, "reference_evidence", fake_evidence):
            result = boundary.assess_control_execution_candidate(
                control, event, candidate="shaA", action_id="act1"
            )
            self.assertFalse(boundary.candidate_result_eligible(result))
        self.assertNotEqual(result["status"], "VERIFIED")

    def test_actual_reference_dependency_tamper_is_detected_by_internal_recheck(self):
        with patch.object(
            boundary.reference_evidence,
            "lookup_reference_evidence",
            lambda *a, **k: None,
        ):
            result = self.genuine_result()
        self.assertEqual(result["status"], "CANDIDATE_BOUNDARY_POLICY_INVALID")
        self.assertFalse(boundary.candidate_result_eligible(result))

    def test_actual_strict_dependency_tamper_is_detected_by_internal_recheck(self):
        with patch.object(
            boundary.strict_core,
            "assess_control_execution_candidate",
            lambda *a, **k: favorable_execution_result(),
        ):
            result = self.genuine_result()
        self.assertEqual(result["status"], "CANDIDATE_BOUNDARY_POLICY_INVALID")
        self.assertFalse(boundary.candidate_result_eligible(result))

    def test_dependency_tamper_after_issuance_invalidates_consumption(self):
        result = self.genuine_result()
        self.assertTrue(boundary.candidate_result_eligible(result))
        with patch.object(
            boundary.reference_evidence,
            "lookup_reference_evidence",
            lambda *a, **k: None,
        ):
            self.assertFalse(boundary.candidate_result_eligible(result))

    def test_legitimate_candidate_path_remains_positive(self):
        result = self.genuine_result()
        self.assertEqual(result["status"], "VERIFIED")
        self.assertTrue(boundary.candidate_result_eligible(result))

    def test_public_runtime_verifier_still_reports_current_policy(self):
        self.assertTrue(boundary.verify_runtime_policy())

    def test_internal_runtime_verifier_capability_is_not_module_exported(self):
        for name in (
            "_runtime_policy_verifier",
            "_internal_runtime_verifier",
            "_candidate_runtime_verifier",
        ):
            with self.subTest(name=name):
                self.assertFalse(hasattr(boundary, name))


if __name__ == "__main__":
    unittest.main()
