from __future__ import annotations

import unittest

from review_engine.models import ReviewerConfig
from review_engine.qualification import QualificationRecord, QualificationRegistry


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


if __name__ == "__main__":
    unittest.main()
