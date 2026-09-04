import json
import unittest

from adapters import AdapterResult, MockAdapter, normalize_adapter_result


class MockAdapterTests(unittest.TestCase):
    def setUp(self):
        self.envelope = {
            "run_id": "RUN-123",
            "case_id": "EXP-B-001",
            "case_version": "1.0",
            "mechanism_id": "mock-plumbing",
            "model_visible": {"review_task": "review this"},
        }

    def _evidence_result(self, raw_output: str) -> AdapterResult:
        return AdapterResult(
            status="PASS",
            raw_output=raw_output,
            provider="test-provider",
            mechanism_version="test-model",
            input_tokens=1,
            output_tokens=1,
            estimated_cost_usd=0.0,
            latency_ms=1,
            evidence_eligible=True,
            runtime_metadata={"provider_attempts": 1},
        )

    def test_mock_is_never_evidence_eligible(self):
        result = MockAdapter("fixture response").invoke(self.envelope)
        self.assertFalse(result.evidence_eligible)
        self.assertEqual(result.provider, "mock")
        self.assertEqual(result.estimated_cost_usd, 0.0)

    def test_non_experimental_normalizer_does_not_assign_truth_or_diagnosis(self):
        result = MockAdapter("fixture response").invoke(self.envelope)
        normalized = normalize_adapter_result(self.envelope, result)
        self.assertEqual(normalized["detected_defect_ids"], [])
        self.assertIsNone(normalized["diagnosis"])
        self.assertEqual(normalized["authorized_scope"], [])
        self.assertFalse(normalized["evidence_eligible"])

    def test_structured_evidence_is_preserved(self):
        payload = {
            "summary": "code defect found",
            "findings": [
                {
                    "summary": "retry is unbounded",
                    "severity": "HIGH",
                    "failure_class": "CODE DEFECT",
                    "artifact_scope": ["production_code"],
                }
            ],
            "diagnosis": {"primary_failure_class": "CODE DEFECT", "contributors": []},
            "authorized_scope": ["production_code"],
            "changed_artifacts": ["CODE-RETRY"],
            "evidence_refs": ["ci:1"],
        }
        normalized = normalize_adapter_result(self.envelope, self._evidence_result(json.dumps(payload)))
        self.assertEqual(normalized["status"], "PASS")
        self.assertTrue(normalized["evidence_eligible"])
        self.assertEqual(normalized["findings"][0]["summary"], "retry is unbounded")
        self.assertEqual(normalized["diagnosis"]["primary_failure_class"], "CODE DEFECT")
        self.assertEqual(normalized["authorized_scope"], ["production_code"])
        self.assertTrue(normalized["runtime_metadata"]["structured_output_valid"])

    def test_unstructured_evidence_fails_closed_instead_of_losing_findings(self):
        normalized = normalize_adapter_result(
            self.envelope,
            self._evidence_result("The production code has a serious retry defect."),
        )
        self.assertEqual(normalized["status"], "ERROR")
        self.assertFalse(normalized["evidence_eligible"])
        self.assertEqual(normalized["findings"], [])
        self.assertFalse(normalized["runtime_metadata"]["structured_output_valid"])
        self.assertIn("not one JSON object", normalized["runtime_metadata"]["normalization_error"])

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
