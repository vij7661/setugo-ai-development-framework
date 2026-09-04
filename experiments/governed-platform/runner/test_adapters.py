import unittest

from adapters import MockAdapter, normalize_adapter_result


class MockAdapterTests(unittest.TestCase):
    def setUp(self):
        self.envelope = {
            "run_id": "RUN-123",
            "case_id": "EXP-B-001",
            "case_version": "1.0",
            "mechanism_id": "mock-plumbing",
            "model_visible": {"review_task": "review this"},
        }

    def test_mock_is_never_evidence_eligible(self):
        result = MockAdapter("fixture response").invoke(self.envelope)
        self.assertFalse(result.evidence_eligible)
        self.assertEqual(result.provider, "mock")
        self.assertEqual(result.estimated_cost_usd, 0.0)

    def test_normalizer_does_not_assign_truth_or_diagnosis(self):
        result = MockAdapter("fixture response").invoke(self.envelope)
        normalized = normalize_adapter_result(self.envelope, result)
        self.assertEqual(normalized["detected_defect_ids"], [])
        self.assertIsNone(normalized["diagnosis"])
        self.assertEqual(normalized["authorized_scope"], [])
        self.assertFalse(normalized["evidence_eligible"])

    def test_adapter_requires_model_visible_payload(self):
        envelope = dict(self.envelope)
        envelope.pop("model_visible")
        with self.assertRaises(ValueError):
            MockAdapter().invoke(envelope)

    def test_normalizer_requires_run_binding_fields(self):
        result = MockAdapter().invoke(self.envelope)
        broken = dict(self.envelope)
        broken.pop("run_id")
        with self.assertRaises(ValueError):
            normalize_adapter_result(broken, result)


if __name__ == "__main__":
    unittest.main()
