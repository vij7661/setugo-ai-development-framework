from __future__ import annotations

import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import phase_policy
import coding_agent_adapter as caa
import review_adjudication_policy as rap

SHA = "a" * 40


class GovernanceReviewAdjudicationTests(unittest.TestCase):
    def test_t001_testing_review_requirement_is_deterministic(self):
        self.assertEqual("REQUIRED", phase_policy.testing_review_requirement(
            touches_governance=True,
            touches_security_boundary=False,
            touches_external_side_effect=False,
            alters_frozen_artifact_after_exposure=False,
            testing_phase_exit=False,
        ))
        self.assertEqual("RECOMMENDED", phase_policy.testing_review_requirement(
            touches_governance=False,
            touches_security_boundary=False,
            touches_external_side_effect=False,
            alters_frozen_artifact_after_exposure=False,
            testing_phase_exit=False,
        ))

    def test_t001_testing_pass_records_review_not_performed_when_optional(self):
        evidence = phase_policy.validate_testing_review_evidence(
            review_requirement="RECOMMENDED",
            review_performed=False,
            adjudication_complete=False,
        )
        self.assertEqual("REVIEW_NOT_PERFORMED", evidence["review_status"])
        self.assertTrue(evidence["testing_gate_satisfied"])

    def test_t001_required_review_cannot_be_skipped(self):
        with self.assertRaises(phase_policy.PhasePolicyError):
            phase_policy.validate_testing_review_evidence(
                review_requirement="REQUIRED",
                review_performed=False,
                adjudication_complete=False,
            )

    def test_t002_adjudication_record_binds_original_finding_and_candidate(self):
        record = rap.build_adjudication_record(
            finding_id="F-1",
            candidate_sha=SHA,
            original_review_evidence_hash="b" * 64,
            decision="ACCEPT",
            root_cause_classification="CODE DEFECT",
            reproduction_status="REPRODUCED",
            reproduction_evidence_refs=["run:123"],
            regression_test_sha="c" * 40,
            governance_change_sha=None,
            adjudicator_identity_claim="manual-governor",
        )
        self.assertEqual(SHA, record["candidate_sha"])
        self.assertEqual("b" * 64, record["original_review_evidence_hash"])
        self.assertEqual("ACCEPT", record["decision"])

    def test_t005_accept_requires_reproduction_or_explicit_alternative_evidence(self):
        with self.assertRaises(rap.AdjudicationPolicyError):
            rap.build_adjudication_record(
                finding_id="F-2",
                candidate_sha=SHA,
                original_review_evidence_hash="d" * 64,
                decision="ACCEPT",
                root_cause_classification="CODE DEFECT",
                reproduction_status="IMPRACTICAL",
                reproduction_evidence_refs=[],
                regression_test_sha=None,
                governance_change_sha=None,
                adjudicator_identity_claim="manual-governor",
            )
        ok = rap.build_adjudication_record(
            finding_id="F-3",
            candidate_sha=SHA,
            original_review_evidence_hash="e" * 64,
            decision="ACCEPT",
            root_cause_classification="GOVERNANCE-PROCESS DEFECT",
            reproduction_status="IMPRACTICAL",
            reproduction_evidence_refs=[],
            alternative_evidence_refs=["artifact:formal-proof-1"],
            reproduction_impractical_reason="Cannot safely trigger irreversible external effect in TESTING",
            regression_test_sha=None,
            governance_change_sha="f" * 40,
            adjudicator_identity_claim="manual-governor",
        )
        self.assertEqual("IMPRACTICAL", ok["reproduction_status"])

    def test_t006_user_approval_must_be_structured_and_candidate_scoped(self):
        approval = phase_policy.build_api_approval(
            approval_id="API-APPROVAL-1",
            candidate_sha=SHA,
            endpoint="https://example.test/v1/check",
            purpose="test provider retry boundary",
            scope="single-call",
            approved_by="USER_EXPLICIT_ACTION",
        )
        self.assertTrue(phase_policy.validate_api_approval(approval, candidate_sha=SHA, endpoint="https://example.test/v1/check"))
        with self.assertRaises(phase_policy.PhasePolicyError):
            phase_policy.validate_api_approval(approval, candidate_sha="b" * 40, endpoint="https://example.test/v1/check")

    def test_t007_rejected_reviewer_finding_is_preserved(self):
        record = rap.build_adjudication_record(
            finding_id="F-4",
            candidate_sha=SHA,
            original_review_evidence_hash="1" * 64,
            decision="REJECT",
            root_cause_classification="REVIEWER EVIDENCE ERROR",
            reproduction_status="NOT_REPRODUCED",
            reproduction_evidence_refs=["test:existing-regression"],
            regression_test_sha=None,
            governance_change_sha=None,
            adjudicator_identity_claim="manual-governor",
        )
        self.assertTrue(record["preserve_original_finding"])
        self.assertEqual("REVIEWER EVIDENCE ERROR", record["root_cause_classification"])

    def test_t004_agent_claimed_governance_validation_is_rejected_evidence(self):
        result = {
            "execution_id": "E1",
            "task_id": "T1",
            "candidate_sha": SHA,
            "adapter_id": "a",
            "agent_id": "agent",
            "agent_family": "fake",
            "agent_version": "1",
            "task_contract_hash": "2" * 64,
            "authority_effect": "NONE",
            "review_effect": "MANUAL_REVIEW_IF_REQUESTED",
            "phase": "TESTING",
            "completion_state": "COMPLETED",
            "changed_artifacts": [],
            "commands_run": ["python governance-runtime/validate_runtime.py"],
            "test_results": [{"name": "governance validation", "status": "PASS"}],
            "failure_classification": "NONE",
            "execution_events": [],
            "material_test_change_requires_adjudication": False,
            "agent_claimed_governance_validation": "PASS",
        }
        gateway = caa.CodingAgentExecutionGateway.from_adapters([])
        with self.assertRaises(caa.AuthorityViolation):
            gateway.ingest_result(result)

    def test_t003_skip_phase_is_already_rejected(self):
        with self.assertRaises(phase_policy.PhasePolicyError):
            phase_policy.validate_promotion(
                source_phase="TESTING",
                destination_phase="PRODUCTION",
                source_branch="phase/testing",
                destination_branch="phase/production",
                source_sha=SHA,
                qualified_sha=SHA,
            )

    def test_t008_shared_memory_never_mints_authoritative_rule(self):
        self.assertEqual("UNVERIFIED_RULE", rap.classify_memory_only_rule(
            present_in_shared_memory=True,
            present_in_authoritative_git=False,
        ))
        self.assertEqual("AUTHORITATIVE_RULE", rap.classify_memory_only_rule(
            present_in_shared_memory=True,
            present_in_authoritative_git=True,
        ))


if __name__ == "__main__":
    unittest.main()
