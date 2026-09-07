from __future__ import annotations

from copy import deepcopy
import unittest

from review_protocol import (
    AutomaticAPITransport,
    DispatchResult,
    ManualRelayTransport,
    ReviewOrchestrator,
    UserInitiatedAPITransport,
    build_portable_review_bundle,
    build_review_request,
    can_promote_material_transition,
    canonical_hash,
    evaluate_review_level,
    ingest_manual_relay_response,
    plan_review_interaction,
    validate_review_evidence,
    validate_shared_memory_grounding,
    verify_portable_review_bundle,
    verify_review_request,
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
            evidence_refs=[
                {"type": "file", "ref": "governance-runtime/review_protocol.py"},
                {"type": "ci_run", "ref": "12345"},
            ],
            changed_paths=["governance-runtime/review_protocol.py"],
        )
        self.bundle = build_portable_review_bundle(
            request=self.request,
            artifacts=[
                {"path": "governance-runtime/review_protocol.py", "content": "exact candidate content"},
                {"path": "governance-runtime/session-state.json", "content": "{}"},
            ],
            evidence_summary={"reference_summaries": {"ci_run:12345": {"conclusion": "success"}}},
        )
        self.authoritative_state = {
            "active_workstream": {
                "branch": "feature/test",
                "head_commit": "a" * 40,
                "state": "CONSTRUCTION_GREEN",
            },
            "independent_review": {
                "current_review_request_id": "REV-TEST-001",
                "current_review_status": "REVIEW_RECEIVED",
                "current_reviewed_artifact_commit": "1" * 40,
            },
        }
        self.shared_memory = {
            "independent_authority": False,
            "current_work": {
                "authoritative_branch": "feature/test",
                "authoritative_head": "a" * 40,
                "status": "CONSTRUCTION_GREEN",
            },
            "governance_runtime": {
                "current_review_request_id": "REV-TEST-001",
                "current_review_status": "REVIEW_RECEIVED",
            },
            "pending_reviews": [{"status": "REVIEW_RECEIVED", "review_request_id": "REV-TEST-001"}],
        }

    def _valid_evidence(self, *, provider="anthropic", model="claude-sonnet-5") -> dict:
        return {
            "review_request_id": "REV-TEST-001",
            "reviewed_artifact_commit": "1" * 40,
            "reviewer": {"provider": provider, "model": model},
            "disposition": "CHANGES_REQUIRED",
            "findings": [{"id": "F1", "severity": "medium"}],
            "evidence_assessment": "Deterministic gates remain necessary.",
            "independence_attestation": "BLIND_TO_PROPOSER_CONCLUSION",
        }

    def _trusted_execution(self, evidence=None, *, provider="anthropic", model="claude-sonnet-5") -> DispatchResult:
        evidence = evidence or self._valid_evidence(provider=provider, model=model)
        return DispatchResult(
            transport="AUTOMATIC_API",
            state="REVIEW_RECEIVED",
            review_request_id="REV-TEST-001",
            payload_hash=canonical_hash(self.request),
            response=deepcopy(evidence),
            reviewer_provider=provider,
            reviewer_model=model,
            identity_assurance="PROVIDER_ADAPTER_AUTHENTICATED",
        )

    def test_governance_path_cannot_be_downgraded_by_r1_trigger_label(self) -> None:
        self.assertEqual(
            evaluate_review_level(
                trigger="ROUTINE_FORMATTING",
                r1_recommends_review=False,
                material_authority_transition=False,
                changed_paths=["governance-runtime/review_protocol.py"],
            ),
            "REQUIRED",
        )

    def test_unknown_material_transition_requires_review(self) -> None:
        self.assertEqual(
            evaluate_review_level(
                trigger="UNRECOGNIZED_LABEL",
                r1_recommends_review=False,
                material_authority_transition=True,
            ),
            "REQUIRED",
        )

    def test_non_authoritative_r1_may_recommend_review(self) -> None:
        self.assertEqual(
            evaluate_review_level(
                trigger="NON_AUTHORITATIVE_ARCHITECTURE_PROPOSAL",
                r1_recommends_review=True,
            ),
            "RECOMMENDED",
        )
        self.assertEqual(
            evaluate_review_level(trigger="ROUTINE_FORMATTING", r1_recommends_review=False),
            "NONE",
        )

    def test_auto_and_manual_mode_only_change_initiation(self) -> None:
        auto = plan_review_interaction(platform_mode="AUTO_MODE", review_level="RECOMMENDED")
        manual = plan_review_interaction(platform_mode="MANUAL_MODE", review_level="RECOMMENDED")
        self.assertEqual(auto["action"], "AUTOMATIC_API")
        self.assertTrue(auto["automatic_dispatch"])
        self.assertEqual(manual["action"], "SHOW_REVIEW_CONTROLS")
        self.assertFalse(manual["automatic_dispatch"])

    def test_material_promotion_cannot_waive_review_with_routine_trigger(self) -> None:
        self.assertFalse(
            can_promote_material_transition(
                trigger="ROUTINE_FORMATTING",
                deterministic_gate_passed=True,
                authoritative_state=self.authoritative_state,
                shared_memory=self.shared_memory,
                review_request=None,
                review_evidence=None,
                review_execution=None,
            )
        )

    def test_trusted_api_review_can_satisfy_material_promotion(self) -> None:
        evidence = self._valid_evidence()
        execution = self._trusted_execution(evidence)
        self.assertTrue(
            can_promote_material_transition(
                trigger="ROUTINE_FORMATTING",
                deterministic_gate_passed=True,
                authoritative_state=self.authoritative_state,
                shared_memory=self.shared_memory,
                review_request=self.request,
                review_evidence=evidence,
                review_execution=execution,
            )
        )

    def test_manual_relay_self_declared_claude_identity_cannot_satisfy_provider_requirement(self) -> None:
        evidence = self._valid_evidence(provider="anthropic", model="claude-sonnet-5")
        execution = ingest_manual_relay_response(request=self.request, evidence=evidence)
        valid, reason = validate_review_evidence(request=self.request, evidence=evidence, execution=execution)
        self.assertFalse(valid)
        self.assertIn("not provider-authenticated", reason)
        self.assertFalse(
            can_promote_material_transition(
                deterministic_gate_passed=True,
                authoritative_state=self.authoritative_state,
                shared_memory=self.shared_memory,
                review_request=self.request,
                review_evidence=evidence,
                review_execution=execution,
            )
        )

    def test_deepseek_execution_cannot_masquerade_as_claude_via_json(self) -> None:
        evidence = self._valid_evidence(provider="anthropic", model="claude-sonnet-5")
        execution = self._trusted_execution(evidence, provider="deepseek", model="deepseek-reasoner")
        valid, reason = validate_review_evidence(request=self.request, evidence=evidence, execution=execution)
        self.assertFalse(valid)
        self.assertIn("trusted reviewer provider", reason)

    def test_review_content_identity_must_match_trusted_adapter_identity(self) -> None:
        evidence = self._valid_evidence(provider="anthropic", model="claude-sonnet-4")
        execution = self._trusted_execution(evidence, provider="anthropic", model="claude-sonnet-5")
        valid, reason = validate_review_evidence(request=self.request, evidence=evidence, execution=execution)
        self.assertFalse(valid)
        self.assertIn("conflicts with trusted execution identity", reason)

    def test_auto_and_user_initiated_api_use_same_request_and_identity_contract(self) -> None:
        captured = []
        evidence = self._valid_evidence()

        def provider_call(payload):
            captured.append(deepcopy(dict(payload)))
            return evidence

        automatic = ReviewOrchestrator().dispatch(
            self.request,
            AutomaticAPITransport(provider_call, provider="anthropic", model="claude-sonnet-5"),
        )
        user_initiated = ReviewOrchestrator().dispatch(
            self.request,
            UserInitiatedAPITransport(provider_call, provider="anthropic", model="claude-sonnet-5"),
        )
        self.assertEqual(automatic.payload_hash, user_initiated.payload_hash)
        self.assertEqual(captured, [self.request, self.request])
        self.assertEqual(automatic.identity_assurance, "PROVIDER_ADAPTER_AUTHENTICATED")
        self.assertEqual(user_initiated.identity_assurance, "PROVIDER_ADAPTER_AUTHENTICATED")

    def test_api_failure_fails_closed_end_to_end(self) -> None:
        def provider_call(_payload):
            raise TimeoutError("provider unavailable")

        execution = ReviewOrchestrator().dispatch(
            self.request,
            AutomaticAPITransport(provider_call, provider="anthropic", model="claude-sonnet-5"),
        )
        self.assertEqual(execution.state, "PENDING_EXTERNAL_REVIEW")
        self.assertEqual(execution.error_class, "TimeoutError")
        self.assertFalse(
            can_promote_material_transition(
                deterministic_gate_passed=True,
                authoritative_state=self.authoritative_state,
                shared_memory=self.shared_memory,
                review_request=self.request,
                review_evidence=self._valid_evidence(),
                review_execution=execution,
            )
        )

    def test_required_reviewer_provider_is_rechecked_at_acceptance(self) -> None:
        request = deepcopy(self.request)
        request["required_reviewer"].pop("provider")
        material = deepcopy(request)
        material.pop("request_hash")
        request["request_hash"] = canonical_hash(material)
        ok, reason = verify_review_request(request)
        self.assertFalse(ok)
        self.assertIn("required reviewer provider", reason)

    def test_wrong_model_class_is_rejected_from_trusted_identity(self) -> None:
        evidence = self._valid_evidence(provider="anthropic", model="other-model")
        execution = self._trusted_execution(evidence, provider="anthropic", model="other-model")
        valid, reason = validate_review_evidence(request=self.request, evidence=evidence, execution=execution)
        self.assertFalse(valid)
        self.assertIn("model class", reason)

    def test_same_proposer_model_is_not_independent(self) -> None:
        request = build_review_request(
            review_request_id="REV-TEST-002",
            trigger="EXPERIMENT_ADJUDICATION",
            artifact_type="experiment",
            artifact_ref="EXP-X",
            artifact_commit="3" * 40,
            proposer={"provider": "openai", "model": "gpt-5.6-sol"},
            required_reviewer={"provider": "openai", "model": "gpt-5.6-sol"},
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
        execution = DispatchResult(
            transport="AUTOMATIC_API",
            state="REVIEW_RECEIVED",
            review_request_id="REV-TEST-002",
            payload_hash=canonical_hash(request),
            response=evidence,
            reviewer_provider="openai",
            reviewer_model="gpt-5.6-sol",
            identity_assurance="PROVIDER_ADAPTER_AUTHENTICATED",
        )
        valid, reason = validate_review_evidence(request=request, evidence=evidence, execution=execution)
        self.assertFalse(valid)
        self.assertIn("independence is unproven", reason)

    def test_stale_shared_memory_blocks_promotion(self) -> None:
        stale = deepcopy(self.shared_memory)
        stale["current_work"]["authoritative_head"] = "b" * 40
        grounded, reason = validate_shared_memory_grounding(authoritative_state=self.authoritative_state, shared_memory=stale)
        self.assertFalse(grounded)
        self.assertIn("stale/conflicted", reason)
        evidence = self._valid_evidence()
        self.assertFalse(
            can_promote_material_transition(
                deterministic_gate_passed=True,
                authoritative_state=self.authoritative_state,
                shared_memory=stale,
                review_request=self.request,
                review_evidence=evidence,
                review_execution=self._trusted_execution(evidence),
            )
        )

    def test_superseded_or_noncurrent_review_request_cannot_promote(self) -> None:
        state = deepcopy(self.authoritative_state)
        state["independent_review"]["current_review_request_id"] = "REV-NEWER"
        memory = deepcopy(self.shared_memory)
        memory["governance_runtime"]["current_review_request_id"] = "REV-NEWER"
        memory["pending_reviews"][0]["review_request_id"] = "REV-NEWER"
        evidence = self._valid_evidence()
        self.assertFalse(
            can_promote_material_transition(
                deterministic_gate_passed=True,
                authoritative_state=state,
                shared_memory=memory,
                review_request=self.request,
                review_evidence=evidence,
                review_execution=self._trusted_execution(evidence),
            )
        )

    def test_pending_review_state_cannot_promote_even_with_valid_old_content(self) -> None:
        state = deepcopy(self.authoritative_state)
        state["independent_review"]["current_review_status"] = "PENDING_EXTERNAL_REVIEW"
        memory = deepcopy(self.shared_memory)
        memory["governance_runtime"]["current_review_status"] = "PENDING_EXTERNAL_REVIEW"
        memory["pending_reviews"][0]["status"] = "PENDING_EXTERNAL_REVIEW"
        evidence = self._valid_evidence()
        self.assertFalse(
            can_promote_material_transition(
                deterministic_gate_passed=True,
                authoritative_state=state,
                shared_memory=memory,
                review_request=self.request,
                review_evidence=evidence,
                review_execution=self._trusted_execution(evidence),
            )
        )

    def test_portable_bundle_missing_referenced_file_is_rejected(self) -> None:
        bundle = deepcopy(self.bundle)
        bundle["artifacts"] = [item for item in bundle["artifacts"] if item["path"] != "governance-runtime/review_protocol.py"]
        material = deepcopy(bundle); material.pop("bundle_hash"); bundle["bundle_hash"] = canonical_hash(material)
        ok, reason = verify_portable_review_bundle(request=self.request, bundle=bundle)
        self.assertFalse(ok)
        self.assertIn("missing referenced artifact", reason)

    def test_portable_bundle_missing_reference_summary_is_rejected(self) -> None:
        bundle = deepcopy(self.bundle)
        bundle["evidence_summary"]["reference_summaries"] = {}
        material = deepcopy(bundle); material.pop("bundle_hash"); bundle["bundle_hash"] = canonical_hash(material)
        ok, reason = verify_portable_review_bundle(request=self.request, bundle=bundle)
        self.assertFalse(ok)
        self.assertIn("missing evidence summary", reason)

    def test_corrupted_manual_bundle_fails_closed(self) -> None:
        bundle = deepcopy(self.bundle)
        bundle["artifacts"][0]["content"] = "tampered"
        result = ReviewOrchestrator().dispatch(self.request, ManualRelayTransport(bundle))
        self.assertEqual(result.state, "PENDING_EXTERNAL_REVIEW")
        self.assertIsNotNone(result.error_class)

    def test_deterministic_gate_still_blocks_valid_authenticated_review(self) -> None:
        evidence = self._valid_evidence()
        self.assertFalse(
            can_promote_material_transition(
                deterministic_gate_passed=False,
                authoritative_state=self.authoritative_state,
                shared_memory=self.shared_memory,
                review_request=self.request,
                review_evidence=evidence,
                review_execution=self._trusted_execution(evidence),
            )
        )


if __name__ == "__main__":
    unittest.main()
