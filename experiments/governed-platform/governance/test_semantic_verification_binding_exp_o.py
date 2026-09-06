from __future__ import annotations

import copy
from pathlib import Path
import tempfile
import unittest

from runtime_slice_exp_o import AuthorityKernel, LocalEnforcementPoint, McpGateway
from semantic_verification_binding_exp_o import (
    SemanticBoundGateway,
    SemanticBoundLocalEnforcementPoint,
    SemanticVerificationAuthority,
    digest,
    make_permit_store,
)


class ExpOSemanticVerificationBindingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="exp-o-semantic-binding-")
        self.kernel = AuthorityKernel(b"semantic-binding-kernel-key")
        self.lep = LocalEnforcementPoint(self.kernel, b"semantic-binding-inner-permit-key")
        self.verifier = SemanticVerificationAuthority(b"semantic-binding-verifier-key", verifier_id="independent-verifier")
        self.store = make_permit_store()
        self.bound_lep = SemanticBoundLocalEnforcementPoint(
            self.lep,
            semantic_verification_key=self.verifier.verification_key,
            bound_permit_signing_key=b"semantic-binding-outer-permit-key",
            permit_store=self.store,
        )
        raw_gateway = McpGateway(self.lep.gateway_verification_key, Path(self.tmp.name) / "effects.sqlite")
        self.gateway = SemanticBoundGateway(
            raw_gateway,
            bound_permit_verification_key=self.bound_lep.bound_permit_verification_key,
            permit_store=self.store,
        )
        self.capability = self.kernel.issue_capability(
            subject_id="worker",
            subject_key_thumbprint="worker-key",
            issued_at_ms=90_000,
            expires_at_ms=120_000,
            freshness_class="WORKSPACE_MUTATION",
            allowed_actions=["WRITE"],
            allowed_resources=["src/app.py"],
            effect_contract_id="contract-v1",
            base_sha="base-v1",
        )
        self.contract = {
            "effect_contract_id": "contract-v1",
            "base_sha": "base-v1",
            "allowed_action_classes": ["WRITE"],
            "allowed_resources": ["src/app.py"],
            "forbidden_resources": ["prod/**", ".github/**", "secrets/**"],
            "max_changed_files": 1,
            "destructive_effect_allowed": False,
            "semantic_correspondence_required": True,
        }
        self.candidate_a = {"change_intent": "Apply verified correction A", "rationale": "candidate A"}
        self.candidate_b = {"change_intent": "Apply different unverified correction B", "rationale": "candidate B"}

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def effect_for(self, candidate: dict) -> dict:
        return {
            "action_class": "WRITE",
            "target_resources": ["src/app.py"],
            "changed_files": ["src/app.py"],
            "base_sha": "base-v1",
            "effect_contract_id": "contract-v1",
            "destructive_effect": False,
            "provenance_trust_classes": ["REMOTE_MODEL_PROPOSAL"],
            "semantic_payload_digest": digest(candidate),
        }

    def authorize(self, candidate: dict, effect: dict, evidence, key: str = "intent-1"):
        return self.bound_lep.authorize(
            self.capability,
            candidate_payload=candidate,
            semantic_verification=evidence,
            worker_id="worker",
            worker_key_thumbprint="worker-key",
            effect_contract=self.contract,
            effect=effect,
            idempotency_key=key,
            now_ms=100_000,
            origin_available=True,
            online_authority_confirmed=False,
        )

    def execute(self, permit, candidate: dict, effect: dict, key: str = "intent-1"):
        return self.gateway.execute(
            permit=permit,
            candidate_payload=candidate,
            worker_id="worker",
            worker_key_thumbprint="worker-key",
            effect=effect,
            idempotency_key=key,
            now_ms=100_000,
        )

    def test_missing_semantic_evidence_denies_before_inner_permit(self) -> None:
        effect = self.effect_for(self.candidate_a)
        result = self.authorize(self.candidate_a, effect, None)
        self.assertFalse(result["authorized"])
        self.assertEqual(result["reason"], "SIGNED_SEMANTIC_VERIFICATION_REQUIRED")
        self.assertEqual(self.gateway.effect_count(), 0)

    def test_forged_semantic_evidence_is_rejected(self) -> None:
        effect = self.effect_for(self.candidate_a)
        evidence = self.verifier.verify_candidate(candidate_payload=self.candidate_a, effect=effect)
        evidence["signature"] = "0" * 64
        result = self.authorize(self.candidate_a, effect, evidence)
        self.assertFalse(result["authorized"])
        self.assertEqual(result["reason"], "SIGNED_SEMANTIC_VERIFICATION_REQUIRED")

    def test_verified_candidate_a_cannot_be_substituted_with_candidate_b(self) -> None:
        effect_a = self.effect_for(self.candidate_a)
        evidence_a = self.verifier.verify_candidate(candidate_payload=self.candidate_a, effect=effect_a)
        effect_b = self.effect_for(self.candidate_b)
        result = self.authorize(self.candidate_b, effect_b, evidence_a)
        self.assertFalse(result["authorized"])
        self.assertTrue(result["reason"].startswith("SEMANTIC_VERIFICATION_BINDING_MISMATCH:"))
        self.assertEqual(self.gateway.effect_count(), 0)

    def test_effect_claim_cannot_lie_about_candidate_digest(self) -> None:
        effect = self.effect_for(self.candidate_a)
        effect["semantic_payload_digest"] = digest(self.candidate_b)
        evidence = self.verifier.verify_candidate(candidate_payload=self.candidate_b, effect=effect)
        result = self.authorize(self.candidate_a, effect, evidence)
        self.assertFalse(result["authorized"])
        self.assertEqual(result["reason"], "SEMANTIC_CANDIDATE_EFFECT_DIGEST_MISMATCH")

    def test_valid_exact_binding_issues_outer_permit_without_exposing_inner_permit(self) -> None:
        effect = self.effect_for(self.candidate_a)
        evidence = self.verifier.verify_candidate(candidate_payload=self.candidate_a, effect=effect)
        auth = self.authorize(self.candidate_a, effect, evidence)
        self.assertTrue(auth["authorized"])
        self.assertEqual(auth["decision"], "SEMANTIC_BOUND_PERMIT_ISSUED")
        self.assertNotIn("lep_permit", auth)
        self.assertNotIn("inner_permit", auth)
        result = self.execute(auth["permit"], self.candidate_a, effect)
        self.assertEqual(result["decision"], "EXECUTED")
        self.assertEqual(self.gateway.effect_count(), 1)

    def test_outer_permit_cannot_be_replayed_for_mutated_candidate(self) -> None:
        effect_a = self.effect_for(self.candidate_a)
        evidence_a = self.verifier.verify_candidate(candidate_payload=self.candidate_a, effect=effect_a)
        auth = self.authorize(self.candidate_a, effect_a, evidence_a)
        self.assertTrue(auth["authorized"])
        effect_b = self.effect_for(self.candidate_b)
        result = self.execute(auth["permit"], self.candidate_b, effect_b)
        self.assertEqual(result["decision"], "DENIED")
        self.assertIn("semantic_payload_digest", result["reason"])
        self.assertEqual(self.gateway.effect_count(), 0)

    def test_outer_permit_is_single_use_even_for_exact_replay(self) -> None:
        effect = self.effect_for(self.candidate_a)
        evidence = self.verifier.verify_candidate(candidate_payload=self.candidate_a, effect=effect)
        auth = self.authorize(self.candidate_a, effect, evidence)
        first = self.execute(auth["permit"], self.candidate_a, effect)
        second = self.execute(auth["permit"], self.candidate_a, effect)
        self.assertEqual(first["decision"], "EXECUTED")
        self.assertEqual(second["decision"], "DENIED")
        self.assertEqual(second["reason"], "INNER_LEP_PERMIT_MISSING_OR_CONSUMED")
        self.assertEqual(self.gateway.effect_count(), 1)

    def test_causal_s0_s1_same_candidate_capability_effect_and_key(self) -> None:
        effect = self.effect_for(self.candidate_a)
        s0 = self.authorize(self.candidate_a, effect, None, key="same-intent")
        self.assertFalse(s0["authorized"])
        self.assertEqual(s0["reason"], "SIGNED_SEMANTIC_VERIFICATION_REQUIRED")
        self.assertEqual(self.gateway.effect_count(), 0)

        evidence = self.verifier.verify_candidate(candidate_payload=self.candidate_a, effect=effect)
        s1 = self.authorize(self.candidate_a, effect, evidence, key="same-intent")
        self.assertTrue(s1["authorized"])
        executed = self.execute(s1["permit"], self.candidate_a, effect, key="same-intent")
        self.assertEqual(executed["decision"], "EXECUTED")
        self.assertEqual(self.gateway.effect_count(), 1)


if __name__ == "__main__":
    unittest.main()
