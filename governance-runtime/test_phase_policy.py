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
        self.assertFalse(p["chat_message_alone_is_api_approval"])

    def test_testing_api_requires_explicit_boundary_or_structured_user_approval(self):
        self.assertTrue(phase_policy.review_transport_policy("TESTING", api_boundary_under_test=True)["external_api_allowed"])
        self.assertFalse(phase_policy.review_transport_policy("TESTING", user_approved_api=True)["external_api_allowed"])
        approved = phase_policy.review_transport_policy(
            "TESTING", user_approved_api=True, api_approval_ref="API-APPROVAL-001"
        )
        self.assertTrue(approved["external_api_allowed"])
        self.assertTrue(approved["structured_user_api_approval"])

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
        self.assertEqual("RECOMMENDED", b["review_requirement"]["review_level"])

    def test_testing_review_triggers_are_deterministic(self):
        r = phase_policy.testing_review_requirement(
            material_transition=True,
            concurrency_or_recovery_boundary=True,
            changed_paths=["src/x.py"],
        )
        self.assertEqual("REQUIRED", r["review_level"])
        self.assertEqual(
            ["CONCURRENCY_OR_RECOVERY_BOUNDARY", "MATERIAL_AUTHORITY_TRANSITION"],
            r["mandatory_triggers"],
        )
        self.assertTrue(r["review_artifact_required_for_testing_pass"])

    def test_governance_relevant_change_requires_testing_review(self):
        r = phase_policy.testing_review_requirement(changed_paths=["governance-runtime/x.py"])
        self.assertEqual("REQUIRED", r["review_level"])
        self.assertIn("GOVERNANCE_RELEVANT_CHANGE", r["mandatory_triggers"])

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
        with self.assertRaisesRegex(phase_policy.PhasePolicyError, "GOVERNANCE_INVALID_PROMOTION"):
            phase_policy.validate_promotion(
                source_phase="TESTING",
                destination_phase="PRODUCTION",
                source_branch="phase/testing",
                destination_branch="phase/production",
                source_sha=sha,
                qualified_sha=sha,
            )
        with self.assertRaisesRegex(phase_policy.PhasePolicyError, "GOVERNANCE_INVALID_PROMOTION"):
            phase_policy.validate_promotion(
                source_phase="TESTING",
                destination_phase="RELEASE",
                source_branch="phase/testing",
                destination_branch="phase/release",
                source_sha=sha,
                qualified_sha="b" * 40,
            )

    def test_adjudication_record_requires_reproduction_for_accepted_finding(self):
        base = {
            "finding_id": "T-001",
            "candidate_sha": "a" * 40,
            "original_review_evidence_hash": "b" * 64,
            "adjudication_decision": "ACCEPT",
            "root_cause_classification": "GOVERNANCE DEFECT",
            "review_evidence_ref": "review-evidence/T-001.json",
            "adjudicator_identity_claim": "R1",
        }
        with self.assertRaises(phase_policy.PhasePolicyError):
            phase_policy.validate_adjudication_record(base)
        base["reproduction_artifact"] = {
            "evidence_ref": "failures/T-001.json",
            "test_sha": "c" * 40,
        }
        out = phase_policy.validate_adjudication_record(base)
        self.assertTrue(out["schema_valid"])
        self.assertFalse(out["reviewer_finding_is_authority"])

    def test_adjudication_reproduction_exception_requires_governance_change(self):
        record = {
            "finding_id": "T-005",
            "candidate_sha": "a" * 40,
            "original_review_evidence_hash": "b" * 64,
            "adjudication_decision": "SPLIT",
            "root_cause_classification": "GOVERNANCE PROCESS DEFECT",
            "review_evidence_ref": "review-evidence/T-005.json",
            "adjudicator_identity_claim": "R1",
            "reproduction_exception": "GOVERNANCE_PROCESS_DEFECT",
        }
        with self.assertRaises(phase_policy.PhasePolicyError):
            phase_policy.validate_adjudication_record(record)
        record["governance_change_sha"] = "d" * 40
        self.assertTrue(phase_policy.validate_adjudication_record(record)["schema_valid"])

    def test_testing_pass_means_release_qualification_not_production(self):
        r = phase_policy.testing_phase_pass_requirements()
        self.assertEqual("READY_TO_BEGIN_RELEASE_QUALIFICATION", r["means"])
        self.assertEqual("PRODUCTION_READY", r["does_not_mean"])
        self.assertIn("review_artifact_present_for_REQUIRED_testing_review", r["required"])
        self.assertIn("coding_agent_changed_artifacts_independently_observed_where_coding_agent_used", r["required"])


if __name__ == "__main__":
    unittest.main()
