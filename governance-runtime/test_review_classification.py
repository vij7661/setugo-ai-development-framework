from __future__ import annotations

from copy import deepcopy
import unittest

from review_protocol import (
    AutomaticAPITransport,
    DispatchResult,
    ManualRelayTransport,
    ReviewOrchestrator,
    UserInitiatedAPITransport,
    attest_external_llm_review,
    build_portable_review_bundle,
    build_review_request,
    can_promote_material_transition,
    canonical_hash,
    classify_user_provided_external_content,
    validate_review_evidence,
)


class ReviewClassificationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.request = build_review_request(
            review_request_id="REV-CLASS-001",
            trigger="MATERIAL_GOVERNANCE_CHANGE",
            artifact_type="governance_candidate",
            artifact_ref="PR-5",
            artifact_commit="6" * 40,
            proposer={"provider": "openai", "model": "gpt-5.6-sol"},
            required_reviewer={"provider": "deepseek", "model_class": "deepseek"},
            blind_review_required=True,
            review_questions=["Review independently."],
            evidence_refs=[],
            material_authority_transition=True,
            required_review_dimensions=[
                {"id": "authority", "mandatory": True, "description": "Authority boundary."}
            ],
        )
        self.evidence = {
            "review_request_id": "REV-CLASS-001",
            "reviewed_artifact_commit": "6" * 40,
            "reviewer": {"provider": "deepseek", "model": "deepseek-reasoner"},
            "disposition": "PASS",
            "findings": [],
            "evidence_assessment": "The mandatory authority dimension was directly tested and supported.",
            "independence_attestation": "BLIND_TO_PROPOSER_CONCLUSION",
            "review_coverage": [
                {
                    "dimension_id": "authority",
                    "status": "TESTED_SUPPORTED",
                    "evidence": ["review_protocol.py authority gate"],
                    "assessment": "Authority boundary directly tested.",
                }
            ],
        }
        self.authoritative_state = {
            "active_workstream": {"branch": "feature/test", "head_commit": "a" * 40, "state": "CONSTRUCTION_GREEN"},
            "independent_review": {
                "current_review_request_id": "REV-CLASS-001",
                "current_review_status": "REVIEW_RECEIVED",
                "current_reviewed_artifact_commit": "6" * 40,
            },
        }
        self.shared_memory = {
            "independent_authority": False,
            "current_work": {"authoritative_branch": "feature/test", "authoritative_head": "a" * 40, "status": "CONSTRUCTION_GREEN"},
            "governance_runtime": {"current_review_request_id": "REV-CLASS-001", "current_review_status": "REVIEW_RECEIVED"},
            "pending_reviews": [{"review_request_id": "REV-CLASS-001", "status": "REVIEW_RECEIVED"}],
        }

    def provider_call(self, _payload):
        return deepcopy(self.evidence)

    def test_rc01_auto_api_is_platform_auto_review(self):
        result = ReviewOrchestrator().dispatch(
            self.request,
            AutomaticAPITransport(self.provider_call, provider="deepseek", model="deepseek-reasoner"),
        )
        self.assertEqual(result.review_class, "PLATFORM_AUTO_API_REVIEW")
        self.assertEqual(result.transport, "AUTOMATIC_API")

    def test_rc02_manual_mode_api_is_platform_user_initiated_review(self):
        result = ReviewOrchestrator().dispatch(
            self.request,
            UserInitiatedAPITransport(self.provider_call, provider="deepseek", model="deepseek-reasoner"),
        )
        self.assertEqual(result.review_class, "PLATFORM_USER_INITIATED_API_REVIEW")
        self.assertEqual(result.transport, "USER_INITIATED_API")
        valid, reason = validate_review_evidence(request=self.request, evidence=self.evidence, execution=result)
        self.assertTrue(valid, reason)

    def test_rc03_paste_without_attestation_is_external_content(self):
        pasted = classify_user_provided_external_content(content=self.evidence)
        self.assertEqual(pasted["evidence_class"], "USER_PROVIDED_EXTERNAL_CONTENT")
        self.assertIsNone(pasted["user_attested_source"])
        self.assertFalse(pasted["provider_api_authenticated"])
        self.assertEqual(pasted["self_declared_reviewer"]["provider"], "deepseek")

    def test_rc04_explicit_user_attestation_creates_user_attested_external_review(self):
        pasted = classify_user_provided_external_content(content=self.evidence)
        attested = attest_external_llm_review(external_content=pasted, provider="deepseek", model="deepseek")
        self.assertEqual(attested["evidence_class"], "USER_ATTESTED_EXTERNAL_LLM_REVIEW")
        self.assertEqual(attested["user_attested_source"], {"provider": "deepseek", "model": "deepseek"})
        self.assertFalse(attested["provider_api_authenticated"])

    def test_rc05_self_declared_reviewer_cannot_self_attest_provenance(self):
        content = deepcopy(self.evidence)
        content["reviewer"] = {"provider": "moonshot", "model": "kimi"}
        pasted = classify_user_provided_external_content(content=content)
        self.assertEqual(pasted["evidence_class"], "USER_PROVIDED_EXTERNAL_CONTENT")
        self.assertIsNone(pasted["user_attested_source"])
        self.assertEqual(pasted["self_declared_reviewer"], {"provider": "moonshot", "model": "kimi"})

    def test_rc06_external_content_cannot_satisfy_material_promotion(self):
        pasted = classify_user_provided_external_content(content=self.evidence)
        attested = attest_external_llm_review(external_content=pasted, provider="deepseek", model="deepseek")
        self.assertFalse(attested["provider_api_authenticated"])
        self.assertFalse(
            can_promote_material_transition(
                deterministic_gate_passed=True,
                authoritative_state=self.authoritative_state,
                shared_memory=self.shared_memory,
                review_request=self.request,
                review_evidence=self.evidence,
                review_execution=None,
            )
        )

    def test_rc07_api_identity_still_rejects_content_identity_substitution(self):
        content = deepcopy(self.evidence)
        content["reviewer"] = {"provider": "moonshot", "model": "kimi"}
        result = DispatchResult(
            transport="USER_INITIATED_API",
            state="REVIEW_RECEIVED",
            review_request_id="REV-CLASS-001",
            payload_hash=canonical_hash(self.request),
            response=content,
            reviewer_provider="deepseek",
            reviewer_model="deepseek-reasoner",
            identity_assurance="PROVIDER_ADAPTER_AUTHENTICATED",
            review_class="PLATFORM_USER_INITIATED_API_REVIEW",
        )
        valid, reason = validate_review_evidence(request=self.request, evidence=content, execution=result)
        self.assertFalse(valid)
        self.assertIn("conflicts with trusted execution identity", reason)

    def test_rc08_api_failure_preserves_platform_class_and_fails_closed(self):
        def fail(_payload):
            raise TimeoutError("down")
        for transport, expected_class in (
            (AutomaticAPITransport(fail, provider="deepseek", model="deepseek-reasoner"), "PLATFORM_AUTO_API_REVIEW"),
            (UserInitiatedAPITransport(fail, provider="deepseek", model="deepseek-reasoner"), "PLATFORM_USER_INITIATED_API_REVIEW"),
        ):
            result = ReviewOrchestrator().dispatch(self.request, transport)
            self.assertEqual(result.review_class, expected_class)
            self.assertEqual(result.state, "PENDING_EXTERNAL_REVIEW")
            self.assertNotEqual(result.identity_assurance, "PROVIDER_ADAPTER_AUTHENTICATED")

    def test_rc09_manual_relay_is_rejected_as_platform_review_transport(self):
        bundle = build_portable_review_bundle(
            request=self.request,
            artifacts=[{"path": "dummy.txt", "content": "x"}],
            evidence_summary={"reference_summaries": {}},
        )
        with self.assertRaisesRegex(ValueError, "unsupported review transport"):
            ReviewOrchestrator().dispatch(self.request, ManualRelayTransport(bundle))

    def test_rc10_legacy_manual_relay_remains_nonpromotable_external_history(self):
        pasted = classify_user_provided_external_content(
            content=self.evidence,
            related_review_request_id=self.request["review_request_id"],
            related_artifact_commit=self.request["artifact"]["commit"],
        )
        self.assertEqual(pasted["evidence_class"], "USER_PROVIDED_EXTERNAL_CONTENT")
        self.assertFalse(pasted["provider_api_authenticated"])
        self.assertEqual(pasted["related_review_request_id"], "REV-CLASS-001")


if __name__ == "__main__":
    unittest.main()
