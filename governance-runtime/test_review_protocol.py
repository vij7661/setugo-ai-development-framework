from __future__ import annotations

from copy import deepcopy
import unittest

from review_protocol import (
    AutomaticAPITransport,
    ManualRelayTransport,
    build_review_request,
    can_promote_material_transition,
    canonical_hash,
    validate_review_evidence,
)


class ReviewProtocolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.request = build_review_request(
            review_request_id="REV-TEST-001",
            trigger="MATERIAL_GOVERNANCE_CHANGE",
            artifact_type="pull_request_candidate",
            artifact_ref="PR-5",
            artifact_commit="1" * 40,
            proposer={"provider": "openai", "model": "gpt-5.6-sol"},
            required_reviewer={"provider": "anthropic", "model_class": "claude"},
            blind_review_required=True,
            review_questions=["Independently assess the governance design."],
            evidence_refs=[{"type": "git", "ref": "PR-5"}],
        )

    def _valid_evidence(self) -> dict:
        return {
            "review_request_id": "REV-TEST-001",
            "reviewed_artifact_commit": "1" * 40,
            "reviewer": {"provider": "anthropic", "model": "claude-sonnet"},
            "disposition": "CHANGES_REQUIRED",
            "findings": [{"id": "F1", "severity": "medium"}],
            "evidence_assessment": "Deterministic gates remain necessary.",
            "independence_attestation": "BLIND_TO_PROPOSER_CONCLUSION",
        }

    def test_manual_and_api_receive_identical_review_request_semantics(self) -> None:
        captured = []

        def provider_call(payload):
            captured.append(deepcopy(dict(payload)))
            return self._valid_evidence()

        manual = ManualRelayTransport().dispatch(self.request)
        automatic = AutomaticAPITransport(provider_call).dispatch(self.request)

        self.assertEqual(manual.payload_hash, automatic.payload_hash)
        self.assertEqual(manual.payload_hash, canonical_hash(self.request))
        self.assertEqual(captured, [self.request])
        self.assertEqual(manual.state, "PENDING_EXTERNAL_REVIEW")
        self.assertEqual(automatic.state, "REVIEW_RECEIVED")

    def test_manual_relay_cannot_self_complete_review(self) -> None:
        result = ManualRelayTransport().dispatch(self.request)
        self.assertIsNone(result.response)
        self.assertEqual(result.state, "PENDING_EXTERNAL_REVIEW")
        self.assertFalse(
            can_promote_material_transition(
                trigger="MATERIAL_GOVERNANCE_CHANGE",
                deterministic_gate_passed=True,
                valid_independent_review_present=False,
            )
        )

    def test_api_failure_or_absence_cannot_change_policy(self) -> None:
        manual = ManualRelayTransport().dispatch(self.request)
        self.assertEqual(manual.state, "PENDING_EXTERNAL_REVIEW")
        self.assertFalse(
            can_promote_material_transition(
                trigger="MATERIAL_GOVERNANCE_CHANGE",
                deterministic_gate_passed=True,
                valid_independent_review_present=False,
            )
        )

    def test_deterministic_gate_still_blocks_even_with_valid_review(self) -> None:
        evidence = self._valid_evidence()
        valid, _ = validate_review_evidence(request=self.request, evidence=evidence)
        self.assertTrue(valid)
        self.assertFalse(
            can_promote_material_transition(
                trigger="MATERIAL_GOVERNANCE_CHANGE",
                deterministic_gate_passed=False,
                valid_independent_review_present=True,
            )
        )

    def test_wrong_commit_review_is_rejected(self) -> None:
        evidence = self._valid_evidence()
        evidence["reviewed_artifact_commit"] = "2" * 40
        valid, reason = validate_review_evidence(request=self.request, evidence=evidence)
        self.assertFalse(valid)
        self.assertIn("different artifact commit", reason)

    def test_same_proposer_model_is_not_independent(self) -> None:
        request = build_review_request(
            review_request_id="REV-TEST-002",
            trigger="EXPERIMENT_ADJUDICATION",
            artifact_type="experiment",
            artifact_ref="EXP-X",
            artifact_commit="3" * 40,
            proposer={"provider": "openai", "model": "gpt-5.6-sol"},
            required_reviewer={"provider": "openai"},
            blind_review_required=False,
            review_questions=["Adjudicate independently."],
            evidence_refs=[],
        )
        evidence = {
            "review_request_id": "REV-TEST-002",
            "reviewed_artifact_commit": "3" * 40,
            "reviewer": {"provider": "openai", "model": "gpt-5.6-sol"},
            "disposition": "PASS",
            "findings": [],
            "evidence_assessment": "No defects found.",
            "independence_attestation": "NOT_BLIND",
        }
        valid, reason = validate_review_evidence(request=request, evidence=evidence)
        self.assertFalse(valid)
        self.assertIn("independence is unproven", reason)

    def test_blind_review_attestation_is_required_when_requested(self) -> None:
        evidence = self._valid_evidence()
        evidence["independence_attestation"] = "SAW_PROPOSER_CONCLUSION"
        valid, reason = validate_review_evidence(request=self.request, evidence=evidence)
        self.assertFalse(valid)
        self.assertIn("blind-review", reason)

    def test_transport_is_not_an_input_to_promotion_decision(self) -> None:
        self.assertTrue(
            can_promote_material_transition(
                trigger="MATERIAL_GOVERNANCE_CHANGE",
                deterministic_gate_passed=True,
                valid_independent_review_present=True,
            )
        )
        self.assertFalse(
            can_promote_material_transition(
                trigger="MATERIAL_GOVERNANCE_CHANGE",
                deterministic_gate_passed=True,
                valid_independent_review_present=False,
            )
        )


if __name__ == "__main__":
    unittest.main()
