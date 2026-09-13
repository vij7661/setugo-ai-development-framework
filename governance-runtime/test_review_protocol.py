from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import subprocess
import tempfile
import unittest

from review_protocol import (
    AutomaticAPITransport,
    DispatchResult,
    ManualRelayTransport,
    attest_external_llm_review,
    classify_user_provided_external_content,
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
        self._git_tmp = tempfile.TemporaryDirectory()
        self.repo_root = Path(self._git_tmp.name)
        subprocess.run(["git","init","-q",str(self.repo_root)],check=True)
        subprocess.run(["git","-C",str(self.repo_root),"config","user.email","test@example.com"],check=True)
        subprocess.run(["git","-C",str(self.repo_root),"config","user.name","Test"],check=True)
        subprocess.run(["git","-C",str(self.repo_root),"remote","add","origin","https://github.com/vij7661/setugo-ai-development-framework.git"],check=True)
        (self.repo_root/"candidate.txt").write_text("candidate",encoding="utf-8")
        subprocess.run(["git","-C",str(self.repo_root),"add","candidate.txt"],check=True)
        subprocess.run(["git","-C",str(self.repo_root),"commit","-q","-m","candidate"],check=True)
        self.artifact_commit = subprocess.run(["git","-C",str(self.repo_root),"rev-parse","HEAD"],check=True,capture_output=True,text=True).stdout.strip()
        self.dimensions = [
            {
                "id": "authority_path",
                "mandatory": True,
                "description": "Review authority and promotion bypass resistance.",
            },
            {
                "id": "evidence_integrity",
                "mandatory": True,
                "description": "Review evidence and packet integrity enforcement.",
            },
        ]
        self.request = build_review_request(
            review_request_id="REV-TEST-001",
            trigger="MATERIAL_GOVERNANCE_CHANGE",
            artifact_type="pull_request_candidate",
            artifact_ref="PR-5",
            artifact_commit=self.artifact_commit,
            proposer={"provider": "openai", "model": "gpt-5.6-sol"},
            required_reviewer={"provider": "anthropic", "model_class": "claude"},
            blind_review_required=True,
            review_questions=["Independently assess the governance design."],
            evidence_refs=[
                {"type": "file", "ref": "governance-runtime/review_protocol.py"},
                {"type": "ci_run", "ref": "12345"},
            ],
            changed_paths=["governance-runtime/review_protocol.py"],
            required_review_dimensions=self.dimensions,
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
            "authority": {"repository": "vij7661/setugo-ai-development-framework"},
            "active_workstream": {
                "branch": "feature/test",
                "head_commit": self.artifact_commit,
                "state": "CONSTRUCTION_GREEN",
            },
            "independent_review": {
                "current_review_request_id": "REV-TEST-001",
                "current_review_status": "REVIEW_RECEIVED",
                "current_reviewed_artifact_commit": self.artifact_commit,
                "current_review_trigger": "MATERIAL_GOVERNANCE_CHANGE",
            },
        }
        self.shared_memory = {
            "independent_authority": False,
            "current_work": {
                "authoritative_branch": "feature/test",
                "authoritative_head": self.artifact_commit,
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
            "reviewed_artifact_commit": self.artifact_commit,
            "reviewer": {"provider": provider, "model": model},
            "disposition": "PASS",
            "findings": [],
            "evidence_assessment": "All mandatory review dimensions were directly tested and supported.",
            "review_coverage": [
                {
                    "dimension_id": "authority_path",
                    "status": "TESTED_SUPPORTED",
                    "evidence": ["evidence:authority_path"],
                    "assessment": "Authority path tested and supported.",
                },
                {
                    "dimension_id": "evidence_integrity",
                    "status": "TESTED_SUPPORTED",
                    "evidence": ["evidence:evidence_integrity"],
                    "assessment": "Evidence integrity tested and supported.",
                },
            ],
            "independence_attestation": "BLIND_TO_PROPOSER_CONCLUSION",
        }

    def _trusted_execution(self, evidence=None, *, provider="anthropic", model="claude-sonnet-5") -> DispatchResult:
        evidence = evidence or self._valid_evidence(provider=provider, model=model)
        return ReviewOrchestrator().dispatch(
            self.request,
            AutomaticAPITransport(lambda _payload: deepcopy(evidence), provider=provider, model=model),
        )

    def tearDown(self) -> None:
        self._git_tmp.cleanup()

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

    def test_trusted_api_positive_review_can_satisfy_material_promotion(self) -> None:
        evidence = self._valid_evidence()
        execution = self._trusted_execution(evidence)
        self.assertTrue(
            can_promote_material_transition(
                trigger="MATERIAL_GOVERNANCE_CHANGE",
                deterministic_gate_passed=True,
                authoritative_state=self.authoritative_state,
                shared_memory=self.shared_memory,
                review_request=self.request,
                review_evidence=evidence,
                review_execution=execution,
                governed_repo_root=self.repo_root,
            )
        )

    def test_manual_relay_content_is_external_evidence_not_review_execution(self) -> None:
        evidence = self._valid_evidence(provider="anthropic", model="claude-sonnet-5")
        record = ingest_manual_relay_response(request=self.request, evidence=evidence)
        self.assertEqual(record["evidence_class"], "USER_PROVIDED_EXTERNAL_CONTENT")
        self.assertFalse(record["provider_api_authenticated"])
        self.assertIsNone(record["user_attested_source"])
        self.assertEqual(record["self_declared_reviewer"]["provider"], "anthropic")
        self.assertFalse(
            can_promote_material_transition(
                deterministic_gate_passed=True,
                authoritative_state=self.authoritative_state,
                shared_memory=self.shared_memory,
                review_request=self.request,
                review_evidence=evidence,
                review_execution=None,
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
            required_review_dimensions=[{"id":"independence","mandatory":True,"description":"Review independence."}],
        )
        evidence = {
            "review_request_id": "REV-TEST-002",
            "reviewed_artifact_commit": "3" * 40,
            "reviewer": {"provider": "openai", "model": "gpt-5.6-sol"},
            "disposition": "PASS",
            "findings": [],
            "evidence_assessment": "No defects found.",
            "review_coverage": [{"dimension_id":"independence","status":"TESTED_SUPPORTED","evidence":["ev"],"assessment":"Independence reviewed."}],
            "independence_attestation": "NOT_BLIND",
        }
        execution = ReviewOrchestrator().dispatch(
            request,
            AutomaticAPITransport(lambda _payload: deepcopy(evidence), provider="openai", model="gpt-5.6-sol"),
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
        bundle["artifacts"] = [
            item for item in bundle["artifacts"]
            if item["path"] != "governance-runtime/review_protocol.py"
        ]
        material = deepcopy(bundle)
        material.pop("bundle_hash")
        bundle["bundle_hash"] = canonical_hash(material)
        ok, reason = verify_portable_review_bundle(request=self.request, bundle=bundle)
        self.assertFalse(ok)
        self.assertIn("missing referenced artifact", reason)

    def test_portable_bundle_missing_reference_summary_is_rejected(self) -> None:
        bundle = deepcopy(self.bundle)
        bundle["evidence_summary"]["reference_summaries"] = {}
        material = deepcopy(bundle)
        material.pop("bundle_hash")
        bundle["bundle_hash"] = canonical_hash(material)
        ok, reason = verify_portable_review_bundle(request=self.request, bundle=bundle)
        self.assertFalse(ok)
        self.assertIn("missing evidence summary", reason)

    def test_manual_relay_is_not_a_platform_review_transport(self) -> None:
        with self.assertRaisesRegex(ValueError, "registered concrete platform adapter"):
            ReviewOrchestrator().dispatch(self.request, ManualRelayTransport(self.bundle))

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

    def test_directly_fabricated_dispatch_result_is_not_authenticated(self) -> None:
        evidence=self._valid_evidence()
        forged=DispatchResult(transport="AUTOMATIC_API",state="REVIEW_RECEIVED",review_request_id="REV-TEST-001",
                              payload_hash=canonical_hash(self.request),response=evidence,reviewer_provider="anthropic",
                              reviewer_model="claude-sonnet-5",identity_assurance="PROVIDER_ADAPTER_AUTHENTICATED",
                              review_class="PLATFORM_AUTO_API_REVIEW")
        valid,reason=validate_review_evidence(request=self.request,evidence=evidence,execution=forged)
        self.assertFalse(valid);self.assertIn("trusted-adapter receipt",reason)

    def test_all_optional_semantic_dimensions_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError,"at least one mandatory"):
            build_review_request(review_request_id="REV-OPTIONAL",trigger="MATERIAL_GOVERNANCE_CHANGE",
                artifact_type="candidate",artifact_ref="X",artifact_commit=self.artifact_commit,
                proposer={"provider":"openai","model":"gpt-5.6-sol"},
                required_reviewer={"provider":"anthropic","model_class":"claude"},blind_review_required=True,
                review_questions=["review"],evidence_refs=[],
                required_review_dimensions=[{"id":"optional","mandatory":False,"description":"optional"}])

    def test_extra_pending_review_entry_breaks_grounding(self) -> None:
        memory=deepcopy(self.shared_memory)
        memory["pending_reviews"].append({"status":"REVIEW_RECEIVED","review_request_id":"STALE"})
        ok,reason=validate_shared_memory_grounding(authoritative_state=self.authoritative_state,shared_memory=memory)
        self.assertFalse(ok);self.assertIn("exactly one",reason)

    def test_rejected_request_state_cannot_promote(self) -> None:
        request=deepcopy(self.request);request["state"]="REVIEW_REJECTED"
        material=deepcopy(request);material.pop("request_hash");request["request_hash"]=canonical_hash(material)
        evidence=self._valid_evidence();execution=ReviewOrchestrator().dispatch(
            request,AutomaticAPITransport(lambda _payload: deepcopy(evidence),provider="anthropic",model="claude-sonnet-5"))
        self.assertFalse(can_promote_material_transition(trigger="MATERIAL_GOVERNANCE_CHANGE",deterministic_gate_passed=True,
            authoritative_state=self.authoritative_state,shared_memory=self.shared_memory,review_request=request,
            review_evidence=evidence,review_execution=execution,governed_repo_root=self.repo_root))

    def test_trigger_mismatch_cannot_promote(self) -> None:
        evidence=self._valid_evidence();execution=self._trusted_execution(evidence)
        self.assertFalse(can_promote_material_transition(trigger="TERMINAL_ACTION",deterministic_gate_passed=True,
            authoritative_state=self.authoritative_state,shared_memory=self.shared_memory,review_request=self.request,
            review_evidence=evidence,review_execution=execution,governed_repo_root=self.repo_root))

    def test_sha_shaped_nonobject_cannot_promote(self) -> None:
        state=deepcopy(self.authoritative_state);state["active_workstream"]["head_commit"]="f"*40
        state["independent_review"]["current_reviewed_artifact_commit"]="f"*40
        memory=deepcopy(self.shared_memory);memory["current_work"]["authoritative_head"]="f"*40
        request=deepcopy(self.request);request["artifact"]["commit"]="f"*40
        material=deepcopy(request);material.pop("request_hash");request["request_hash"]=canonical_hash(material)
        evidence=self._valid_evidence();evidence["reviewed_artifact_commit"]="f"*40
        execution=ReviewOrchestrator().dispatch(request,AutomaticAPITransport(lambda _payload: deepcopy(evidence),provider="anthropic",model="claude-sonnet-5"))
        self.assertFalse(can_promote_material_transition(trigger="MATERIAL_GOVERNANCE_CHANGE",deterministic_gate_passed=True,
            authoritative_state=state,shared_memory=memory,review_request=request,review_evidence=evidence,
            review_execution=execution,governed_repo_root=self.repo_root))



if __name__ == "__main__":
    unittest.main()
