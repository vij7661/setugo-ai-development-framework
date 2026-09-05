from __future__ import annotations

import unittest

from review_engine.models import ReviewerConfig
from review_engine.qualification import QualificationRecord, QualificationRegistry, reviewer_context_hash


def cfg(ref="q1", *, model="m", role="R2", lineage="lineage"):
    return ReviewerConfig(
        role=role, provider="p", model=model, sku="s", deployment_path="api",
        api_key_env="KEY", foundation_lineage=lineage, qualification_ref=ref,
    )


def record(**overrides):
    values = dict(
        qualification_ref="q1", provider="p", model="m", sku="s", deployment_path="api",
        role="R2", status="QUALIFIED", qualification_epoch=1,
        foundation_lineage="lineage", max_risk="HIGH", task_types=("GENERAL",),
    )
    values.update(overrides)
    return QualificationRecord(**values)


def context_hash(request_id: str, *, phase: str = "R2_INDEPENDENT", content: str = "artifact text") -> str:
    return reviewer_context_hash(
        {
            "role": "R2",
            "request_id": request_id,
            "phase": phase,
            "artifact": {"artifact_hash": "artifact-a", "content": content},
        }
    )


class QualificationTests(unittest.TestCase):
    def test_exact_qualified_binding_is_eligible(self):
        registry = QualificationRegistry((record(),))
        decision = registry.evaluate(cfg(), risk="HIGH", task_type="GENERAL")
        self.assertTrue(decision.eligible)

    def test_model_substitution_is_not_eligible(self):
        registry = QualificationRegistry((record(),))
        decision = registry.evaluate(cfg(model="different"), risk="HIGH", task_type="GENERAL")
        self.assertFalse(decision.eligible)
        self.assertIn("model", decision.reason)

    def test_pending_or_revoked_record_is_not_eligible(self):
        pending = QualificationRegistry((record(status="PENDING"),))
        self.assertFalse(pending.evaluate(cfg(), risk="LOW").eligible)
        revoked = QualificationRegistry((record(status="REVOKED"),))
        self.assertFalse(revoked.evaluate(cfg(), risk="LOW").eligible)

    def test_qualification_is_task_and_risk_specific(self):
        registry = QualificationRegistry((record(max_risk="MEDIUM", task_types=("CODE_REVIEW",)),))
        self.assertFalse(registry.evaluate(cfg(), risk="HIGH", task_type="CODE_REVIEW").eligible)
        self.assertFalse(registry.evaluate(cfg(), risk="MEDIUM", task_type="ARCHITECTURE").eligible)
        self.assertTrue(registry.evaluate(cfg(), risk="MEDIUM", task_type="CODE_REVIEW").eligible)

    def test_missing_qualification_fails_closed(self):
        registry = QualificationRegistry()
        decision = registry.evaluate(cfg(ref=None), risk="LOW")
        self.assertFalse(decision.eligible)

    def test_new_epoch_can_replace_same_qualification_reference(self):
        registry = QualificationRegistry((record(),))
        registry.add(record(qualification_epoch=2, status="REVOKED"))
        self.assertEqual(registry.get("q1").qualification_epoch, 2)
        self.assertFalse(registry.evaluate(cfg(), risk="LOW").eligible)

    def test_capability_binds_exact_epoch_identity_risk_task_request_phase_artifact_and_context(self):
        registry = QualificationRegistry((record(),))
        ctx_hash = context_hash("req-1")
        decision, capability = registry.issue_capability(
            cfg(),
            risk="HIGH",
            task_type="GENERAL",
            request_id="req-1",
            phase="R2_INDEPENDENT",
            context_hash=ctx_hash,
            artifact_hash="artifact-a",
        )
        self.assertTrue(decision.eligible)
        self.assertIsNotNone(capability)
        assert capability is not None
        self.assertEqual(capability.qualification_epoch, 1)
        self.assertEqual(capability.model, "m")
        self.assertEqual(capability.risk, "HIGH")
        self.assertEqual(capability.task_type, "GENERAL")
        self.assertEqual(capability.request_id, "req-1")
        self.assertEqual(capability.phase, "R2_INDEPENDENT")
        self.assertEqual(capability.artifact_hash, "artifact-a")
        self.assertEqual(capability.context_hash, ctx_hash)

    def test_revoked_qualification_cannot_issue_capability(self):
        registry = QualificationRegistry((record(status="REVOKED"),))
        decision, capability = registry.issue_capability(
            cfg(),
            risk="LOW",
            request_id="req-2",
            phase="R2_INDEPENDENT",
            context_hash=context_hash("req-2"),
            artifact_hash="artifact-a",
        )
        self.assertFalse(decision.eligible)
        self.assertIsNone(capability)
        self.assertIn("REVOKED", decision.reason)

    def test_capability_is_single_use_and_cannot_change_scope_or_context(self):
        registry = QualificationRegistry((record(),))
        original_hash = context_hash("req-3")
        _, capability = registry.issue_capability(
            cfg(),
            risk="HIGH",
            task_type="GENERAL",
            request_id="req-3",
            phase="R2_INDEPENDENT",
            context_hash=original_hash,
            artifact_hash="artifact-a",
        )
        assert capability is not None

        with self.assertRaisesRegex(ValueError, "phase binding mismatch"):
            registry.consume_capability(
                capability.capability_id,
                cfg(),
                risk="HIGH",
                task_type="GENERAL",
                request_id="req-3",
                phase="R3_INDEPENDENT",
                context_hash=original_hash,
                artifact_hash="artifact-a",
            )
        self.assertFalse(registry.capability_consumed(capability.capability_id))

        with self.assertRaisesRegex(ValueError, "context_hash binding mismatch"):
            registry.consume_capability(
                capability.capability_id,
                cfg(),
                risk="HIGH",
                task_type="GENERAL",
                request_id="req-3",
                phase="R2_INDEPENDENT",
                context_hash=context_hash("req-3", content="substituted text"),
                artifact_hash="artifact-a",
            )
        self.assertFalse(registry.capability_consumed(capability.capability_id))

        consumed = registry.consume_capability(
            capability.capability_id,
            cfg(),
            risk="HIGH",
            task_type="GENERAL",
            request_id="req-3",
            phase="R2_INDEPENDENT",
            context_hash=original_hash,
            artifact_hash="artifact-a",
        )
        self.assertEqual(consumed.capability_id, capability.capability_id)
        self.assertTrue(registry.capability_consumed(capability.capability_id))

        with self.assertRaisesRegex(ValueError, "already consumed"):
            registry.consume_capability(
                capability.capability_id,
                cfg(),
                risk="HIGH",
                task_type="GENERAL",
                request_id="req-3",
                phase="R2_INDEPENDENT",
                context_hash=original_hash,
                artifact_hash="artifact-a",
            )

    def test_revocation_after_issue_does_not_retroactively_rewrite_one_shot_grant(self):
        registry = QualificationRegistry((record(),))
        ctx_hash = context_hash("req-4")
        _, capability = registry.issue_capability(
            cfg(),
            risk="HIGH",
            request_id="req-4",
            phase="R2_INDEPENDENT",
            context_hash=ctx_hash,
            artifact_hash="artifact-a",
        )
        assert capability is not None
        registry.add(record(qualification_epoch=2, status="REVOKED"))

        consumed = registry.consume_capability(
            capability.capability_id,
            cfg(),
            risk="HIGH",
            request_id="req-4",
            phase="R2_INDEPENDENT",
            context_hash=ctx_hash,
            artifact_hash="artifact-a",
        )
        self.assertEqual(consumed.qualification_epoch, 1)

        next_decision, next_capability = registry.issue_capability(
            cfg(),
            risk="HIGH",
            request_id="req-4",
            phase="R2_INDEPENDENT",
            context_hash=ctx_hash,
            artifact_hash="artifact-a",
        )
        self.assertFalse(next_decision.eligible)
        self.assertIsNone(next_capability)

    def test_context_hash_is_canonical_for_equivalent_json_objects(self):
        left = reviewer_context_hash({"b": [2, 3], "a": {"x": True}})
        right = reviewer_context_hash({"a": {"x": True}, "b": [2, 3]})
        self.assertEqual(left, right)


if __name__ == "__main__":
    unittest.main()
