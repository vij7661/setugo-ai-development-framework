from __future__ import annotations

from copy import deepcopy
import unittest

from review_protocol import (
    AutomaticAPITransport,
    ManualRelayTransport,
    ReviewOrchestrator,
    UserInitiatedAPITransport,
    build_portable_review_bundle,
    build_review_request,
    can_promote_material_transition,
    canonical_hash,
    evaluate_review_level,
    plan_review_interaction,
    validate_review_evidence,
    verify_portable_review_bundle,
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
        self.bundle = build_portable_review_bundle(
            request=self.request,
            artifacts=[
                {"path": "governance-runtime/review_protocol.py", "content": "exact candidate content"},
                {"path": "governance-runtime/session-state.json", "content": "{}"},
            ],
            evidence_summary={"ci": "green", "repository_access_required": False},
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

    def test_policy_can_force_required_even_when_r1_does_not_recommend(self) -> None:
        self.assertEqual(
            evaluate_review_level(
                trigger="MATERIAL_GOVERNANCE_CHANGE",
                r1_recommends_review=False,
            ),
            "REQUIRED",
        )

    def test_r1_can_recommend_review_for_nonmandatory_work(self) -> None:
        self.assertEqual(
            evaluate_review_level(
                trigger="NON_AUTHORITATIVE_ARCHITECTURE_PROPOSAL",
                r1_recommends_review=True,
            ),
            "RECOMMENDED",
        )
        self.assertEqual(
            evaluate_review_level(
                trigger="ROUTINE_FORMATTING",
                r1_recommends_review=False,
            ),
            "NONE",
        )

    def test_auto_mode_dispatches_review_without_user_button(self) -> None:
        plan = plan_review_interaction(platform_mode="AUTO_MODE", review_level="RECOMMENDED")
        self.assertEqual(plan["action"], "AUTOMATIC_API")
        self.assertTrue(plan["automatic_dispatch"])
        self.assertFalse(plan["show_review_controls"])

    def test_manual_mode_shows_buttons_and_does_not_auto_dispatch(self) -> None:
        plan = plan_review_interaction(platform_mode="MANUAL_MODE", review_level="RECOMMENDED")
        self.assertEqual(plan["action"], "SHOW_REVIEW_CONTROLS")
        self.assertTrue(plan["show_review_controls"])
        self.assertFalse(plan["automatic_dispatch"])
        self.assertEqual(plan["recommended_buttons"], ["ASK_REVIEWER_SLOT_1", "ASK_REVIEWER_SLOT_2"])

    def test_manual_required_review_can_be_skipped_but_authority_stays_blocked(self) -> None:
        plan = plan_review_interaction(platform_mode="MANUAL_MODE", review_level="REQUIRED")
        self.assertTrue(plan["authoritative_transition_blocked"])
        self.assertFalse(
            can_promote_material_transition(
                trigger="MATERIAL_GOVERNANCE_CHANGE",
                deterministic_gate_passed=True,
                valid_independent_review_present=False,
            )
        )

    def test_auto_and_user_initiated_api_receive_identical_request_semantics(self) -> None:
        captured = []

        def provider_call(payload):
            captured.append(deepcopy(dict(payload)))
            return self._valid_evidence()

        automatic = ReviewOrchestrator().dispatch(self.request, AutomaticAPITransport(provider_call))
        user_initiated = ReviewOrchestrator().dispatch(self.request, UserInitiatedAPITransport(provider_call))

        self.assertEqual(automatic.payload_hash, user_initiated.payload_hash)
        self.assertEqual(automatic.payload_hash, canonical_hash(self.request))
        self.assertEqual(captured, [self.request, self.request])
        self.assertEqual(automatic.state, "REVIEW_RECEIVED")
        self.assertEqual(user_initiated.state, "REVIEW_RECEIVED")

    def test_manual_relay_requires_self_contained_verified_bundle(self) -> None:
        ok, reason = verify_portable_review_bundle(request=self.request, bundle=self.bundle)
        self.assertTrue(ok, reason)
        self.assertFalse(self.bundle["repository_access_required"])
        result = ReviewOrchestrator().dispatch(self.request, ManualRelayTransport(self.bundle))
        self.assertEqual(result.state, "PENDING_EXTERNAL_REVIEW")
        self.assertIsNone(result.response)
        self.assertEqual(result.portable_bundle_hash, self.bundle["bundle_hash"])

    def test_corrupted_manual_bundle_fails_closed(self) -> None:
        bundle = deepcopy(self.bundle)
        bundle["artifacts"][0]["content"] = "tampered"
        result = ReviewOrchestrator().dispatch(self.request, ManualRelayTransport(bundle))
        self.assertEqual(result.state, "PENDING_EXTERNAL_REVIEW")
        self.assertIsNotNone(result.error_class)
        self.assertIsNone(result.response)

    def test_api_failure_fails_closed_and_does_not_change_policy(self) -> None:
        def provider_call(_payload):
            raise TimeoutError("provider unavailable")

        result = ReviewOrchestrator().dispatch(self.request, AutomaticAPITransport(provider_call))
        self.assertEqual(result.state, "PENDING_EXTERNAL_REVIEW")
        self.assertEqual(result.error_class, "TimeoutError")
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

    def test_transport_and_platform_mode_are_not_inputs_to_promotion(self) -> None:
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
