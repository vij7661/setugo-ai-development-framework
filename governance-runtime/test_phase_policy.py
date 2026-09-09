from __future__ import annotations

import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import phase_policy


class PhasePolicyTests(unittest.TestCase):
    def test_testing_defaults_manual_and_no_api(self):
        p = phase_policy.review_transport_policy("TESTING")
        self.assertEqual("MANUAL", p["default_transport"])
        self.assertFalse(p["external_api_allowed"])
        self.assertFalse(p["automatic_api_dispatch"])
        self.assertTrue(p["ask_user_before_review"])
        self.assertTrue(p["manual_review_can_satisfy_phase_review_gate"])
        self.assertFalse(p["manual_review_can_establish_production_qualification"])

    def test_testing_api_requires_explicit_boundary_or_user_approval(self):
        self.assertTrue(phase_policy.review_transport_policy("TESTING", api_boundary_under_test=True)["external_api_allowed"])
        self.assertTrue(phase_policy.review_transport_policy("TESTING", user_approved_api=True)["external_api_allowed"])

    def test_testing_review_instruction_rejects_production_scope_creep(self):
        b = phase_policy.build_phase_review_boundary(
            phase="TESTING",
            review_scope=["bounded falsification"],
            required_dimensions=["d1"],
            explicit_nonclaims=["production readiness"],
            out_of_scope_dimensions=["production IAM"],
            allowed_evidence=["embedded source"],
        )
        self.assertIn("not a production-readiness review", b["reviewer_instruction"])
        self.assertEqual("RELEASE", b["promotion_target"])
        self.assertFalse(b["raw_finding_becomes_governance_rule_automatically"])

    def test_future_phase_findings_are_deferred_unless_current_contract_violated(self):
        self.assertEqual(
            "DEFERRED_TO_PRODUCTION",
            phase_policy.classify_finding_for_phase(
                phase="TESTING", finding_phase="PRODUCTION", violates_current_contract=False
            ),
        )
        self.assertEqual(
            "BLOCK_CURRENT_PHASE_PENDING_ADJUDICATION",
            phase_policy.classify_finding_for_phase(
                phase="TESTING", finding_phase="PRODUCTION", violates_current_contract=True
            ),
        )

    def test_promotion_must_advance_one_phase_and_preserve_exact_sha(self):
        sha = "a" * 40
        ok = phase_policy.validate_promotion(
            source_phase="TESTING",
            destination_phase="RELEASE",
            source_branch="phase/testing",
            destination_branch="phase/release",
            source_sha=sha,
            qualified_sha=sha,
        )
        self.assertTrue(ok["promotion_direction_valid"])
        with self.assertRaises(phase_policy.PhasePolicyError):
            phase_policy.validate_promotion(
                source_phase="TESTING",
                destination_phase="PRODUCTION",
                source_branch="phase/testing",
                destination_branch="phase/production",
                source_sha=sha,
                qualified_sha=sha,
            )
        with self.assertRaises(phase_policy.PhasePolicyError):
            phase_policy.validate_promotion(
                source_phase="TESTING",
                destination_phase="RELEASE",
                source_branch="phase/testing",
                destination_branch="phase/release",
                source_sha=sha,
                qualified_sha="b" * 40,
            )

    def test_testing_pass_means_release_qualification_not_production(self):
        r = phase_policy.testing_phase_pass_requirements()
        self.assertEqual("READY_TO_BEGIN_RELEASE_QUALIFICATION", r["means"])
        self.assertEqual("PRODUCTION_READY", r["does_not_mean"])


if __name__ == "__main__":
    unittest.main()
