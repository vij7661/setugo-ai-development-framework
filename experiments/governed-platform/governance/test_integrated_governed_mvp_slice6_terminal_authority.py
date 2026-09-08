from __future__ import annotations

from copy import deepcopy
import unittest

from integrated_governed_mvp_terminal_authority import (
    evaluate_terminal_authority,
    with_self_hash,
)


class TerminalAuthorityGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.now = 2_000_000_000
        self.request = {
            "project_id": "project-1",
            "task_id": "task-1",
            "action": "RELEASE",
            "effect_id": "effect-1",
            "artifact_sha": "abc123",
            "expected_state_version": 7,
        }
        self.current_state = {"project_id": "project-1", "state_version": 7}
        self.execution = with_self_hash(
            {
                "state": "ISOLATED_EXECUTION_SUCCEEDED",
                "project_id": "project-1",
                "task_id": "task-1",
                "effect_id": "effect-1",
                "artifact_sha": "abc123",
                "terminal_authority": False,
                "release_completion_authority": False,
            },
            "execution_evidence_hash",
        )
        self.review = {
            "state": "CLEAR",
            "action": "RELEASE",
            "artifact_sha": "abc123",
            "evidence_refs": ["review:exact-artifact:abc123"],
        }
        self.authority = self._authority()

    def _authority(self, **overrides):
        record = {
            "authority_id": "authority-1",
            "source_class": "HUMAN",
            "decision": "APPROVE",
            "project_id": "project-1",
            "task_id": "task-1",
            "effect_id": "effect-1",
            "action": "RELEASE",
            "artifact_sha": "abc123",
            "state_version": 7,
            "issued_at_epoch": self.now - 100,
            "expires_at_epoch": self.now + 100,
            "evidence_refs": ["human-approval:authority-1"],
        }
        record.update(overrides)
        return with_self_hash(record, "authority_record_hash")

    def _evaluate(self, **overrides):
        values = {
            "terminal_request": self.request,
            "execution_evidence": self.execution,
            "review_gate": self.review,
            "authority_record": self.authority,
            "current_state": self.current_state,
            "now_epoch": self.now,
        }
        values.update(overrides)
        return evaluate_terminal_authority(**values)

    def test_s6_01_exact_valid_release_is_authorized(self):
        result = self._evaluate()
        self.assertEqual("AUTHORIZED_FOR_TERMINAL_ACTION", result["state"])
        self.assertTrue(result["authorized"])
        self.assertTrue(result["terminal_authority"])
        self.assertTrue(result["release_completion_authority"])

    def test_s6_02_merge_approval_is_bound_to_merge(self):
        request = {**self.request, "action": "MERGE"}
        review = {**self.review, "action": "MERGE"}
        authority = self._authority(action="MERGE")
        result = self._evaluate(terminal_request=request, review_gate=review, authority_record=authority)
        self.assertEqual("AUTHORIZED_FOR_TERMINAL_ACTION", result["state"])
        self.assertEqual("MERGE", result["bound_lineage"]["action"])

    def test_s6_03_deploy_approval_is_bound_to_deploy(self):
        request = {**self.request, "action": "DEPLOY"}
        review = {**self.review, "action": "DEPLOY"}
        authority = self._authority(action="DEPLOY")
        result = self._evaluate(terminal_request=request, review_gate=review, authority_record=authority)
        self.assertEqual("AUTHORIZED_FOR_TERMINAL_ACTION", result["state"])
        self.assertEqual("DEPLOY", result["bound_lineage"]["action"])

    def test_s6_04_complete_approval_is_bound_to_complete(self):
        request = {**self.request, "action": "COMPLETE"}
        review = {**self.review, "action": "COMPLETE"}
        authority = self._authority(action="COMPLETE")
        result = self._evaluate(terminal_request=request, review_gate=review, authority_record=authority)
        self.assertEqual("AUTHORIZED_FOR_TERMINAL_ACTION", result["state"])
        self.assertEqual("COMPLETE", result["bound_lineage"]["action"])

    def test_s6_05_execution_success_without_authority_record_is_denied(self):
        result = self._evaluate(authority_record=None)
        self.assertEqual("DENY_AUTHORITY_RECORD", result["state"])
        self.assertFalse(result["authorized"])

    def test_s6_06_model_or_worker_source_is_denied(self):
        for source in ("MODEL", "WORKER", "RESEARCHER", "JUDGE"):
            with self.subTest(source=source):
                result = self._evaluate(authority_record=self._authority(source_class=source))
                self.assertEqual("DENY_AUTHORITY_SOURCE", result["state"])

    def test_s6_07_action_substitution_is_denied(self):
        request = {**self.request, "action": "MERGE"}
        review = {**self.review, "action": "MERGE"}
        result = self._evaluate(terminal_request=request, review_gate=review)
        self.assertEqual("DENY_AUTHORITY_RECORD", result["state"])

    def test_s6_08_artifact_sha_substitution_is_denied(self):
        request = {**self.request, "artifact_sha": "moved456"}
        execution = with_self_hash({**self.execution, "artifact_sha": "moved456"}, "execution_evidence_hash")
        review = {**self.review, "artifact_sha": "moved456"}
        result = self._evaluate(terminal_request=request, execution_evidence=execution, review_gate=review)
        self.assertEqual("DENY_AUTHORITY_RECORD", result["state"])

    def test_s6_09_project_task_effect_lineage_mismatch_is_denied(self):
        for field in ("project_id", "task_id", "effect_id"):
            with self.subTest(field=field):
                execution = deepcopy(self.execution)
                execution[field] = "other"
                execution = with_self_hash(execution, "execution_evidence_hash")
                result = self._evaluate(execution_evidence=execution)
                self.assertEqual("DENY_EXECUTION_EVIDENCE", result["state"])

    def test_s6_10_stale_expected_state_version_is_denied(self):
        request = {**self.request, "expected_state_version": 6}
        result = self._evaluate(terminal_request=request)
        self.assertEqual("DENY_STATE_VERSION", result["state"])

    def test_s6_11_future_expected_state_version_is_denied(self):
        request = {**self.request, "expected_state_version": 8}
        result = self._evaluate(terminal_request=request)
        self.assertEqual("DENY_STATE_VERSION", result["state"])

    def test_s6_12_review_required_cannot_authorize(self):
        review = {**self.review, "state": "REVIEW_REQUIRED"}
        result = self._evaluate(review_gate=review)
        self.assertEqual("DENY_REVIEW_GATE", result["state"])

    def test_s6_13_human_required_cannot_authorize(self):
        review = {**self.review, "state": "HUMAN_REQUIRED"}
        result = self._evaluate(review_gate=review)
        self.assertEqual("DENY_REVIEW_GATE", result["state"])

    def test_s6_14_malformed_review_gate_cannot_authorize(self):
        review = {"state": "CLEAR", "action": "RELEASE", "artifact_sha": "abc123", "evidence_refs": []}
        result = self._evaluate(review_gate=review)
        self.assertEqual("DENY_REVIEW_GATE", result["state"])

    def test_s6_15_explicit_authority_deny_is_terminal_denial(self):
        result = self._evaluate(authority_record=self._authority(decision="DENY"))
        self.assertEqual("TERMINAL_ACTION_DENIED", result["state"])
        self.assertFalse(result["authorized"])

    def test_s6_16_expired_authority_is_denied(self):
        authority = self._authority(issued_at_epoch=self.now - 200, expires_at_epoch=self.now)
        result = self._evaluate(authority_record=authority)
        self.assertEqual("DENY_EXPIRED_AUTHORITY", result["state"])

    def test_s6_17_future_issued_authority_is_denied(self):
        authority = self._authority(issued_at_epoch=self.now + 1, expires_at_epoch=self.now + 100)
        result = self._evaluate(authority_record=authority)
        self.assertEqual("DENY_AUTHORITY_RECORD", result["state"])

    def test_s6_18_tampered_authority_record_hash_is_denied(self):
        authority = deepcopy(self.authority)
        authority["artifact_sha"] = "tampered"
        result = self._evaluate(authority_record=authority)
        self.assertEqual("DENY_AUTHORITY_RECORD", result["state"])

    def test_s6_19_tampered_execution_evidence_is_denied(self):
        execution = deepcopy(self.execution)
        execution["artifact_sha"] = "tampered"
        result = self._evaluate(execution_evidence=execution)
        self.assertEqual("DENY_EXECUTION_EVIDENCE", result["state"])

    def test_s6_20_execution_evidence_attempting_terminal_authority_is_denied(self):
        execution = with_self_hash(
            {**self.execution, "terminal_authority": True, "release_completion_authority": True},
            "execution_evidence_hash",
        )
        result = self._evaluate(execution_evidence=execution)
        self.assertEqual("DENY_EXECUTION_EVIDENCE", result["state"])

    def test_s6_21_identical_replay_is_deterministic(self):
        first = self._evaluate()
        second = self._evaluate()
        self.assertEqual(first, second)
        self.assertEqual(first["receipt_hash"], second["receipt_hash"])

    def test_s6_22_green_ci_or_model_success_cannot_replace_authority(self):
        execution = with_self_hash(
            {**self.execution, "ci_status": "SUCCESS", "model_claim": "APPROVED_FOR_RELEASE"},
            "execution_evidence_hash",
        )
        result = self._evaluate(execution_evidence=execution, authority_record=None)
        self.assertEqual("DENY_AUTHORITY_RECORD", result["state"])

    def test_s6_23_authority_identity_cannot_be_rebound_to_changed_binding(self):
        tampered = deepcopy(self.authority)
        tampered["artifact_sha"] = "new-sha-with-old-hash"
        self.assertEqual("DENY_AUTHORITY_RECORD", self._evaluate(authority_record=tampered)["state"])

        changed_action = self._authority(action="MERGE")
        self.assertEqual("DENY_AUTHORITY_RECORD", self._evaluate(authority_record=changed_action)["state"])

        changed_state_version = self._authority(state_version=6)
        self.assertEqual("DENY_AUTHORITY_RECORD", self._evaluate(authority_record=changed_state_version)["state"])

    def test_s6_24_authorized_receipt_does_not_claim_side_effect_occurred(self):
        result = self._evaluate()
        self.assertEqual("AUTHORIZED_FOR_TERMINAL_ACTION", result["state"])
        self.assertFalse(result["actual_side_effect_performed"])
        self.assertNotIn("merged", result)
        self.assertNotIn("deployed", result)
        self.assertNotIn("released", result)
        self.assertNotIn("completed", result)


if __name__ == "__main__":
    unittest.main()
