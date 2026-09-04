import io
import json
import unittest
from unittest.mock import patch

from adapters import OllamaAdapter, normalize_adapter_result


class _FakeResponse:
    def __init__(self, payload):
        self._payload = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return self._payload


class OllamaAdapterTests(unittest.TestCase):
    def setUp(self):
        self.envelope = {
            "run_id": "pilot1-test",
            "instruction_version": "pilot-v1",
            "case_binding": {
                "case_id": "EXP-A-001",
                "case_version": "1.0",
                "model_visible_sha256": "abc123",
            },
            "mechanism": {
                "mechanism_id": "local-reasoner-a",
                "adapter": "ollama",
                "model": "qwen3:4b",
            },
            "model_visible": {
                "review_task": "Find material defects.",
                "artifact": "example",
            },
        }

    @patch("adapters.request.urlopen")
    def test_success_is_evidence_eligible_and_preserves_binding(self, urlopen):
        urlopen.return_value = _FakeResponse(
            {
                "model": "qwen3:4b",
                "response": "material finding",
                "done": True,
                "done_reason": "stop",
                "prompt_eval_count": 50,
                "eval_count": 25,
                "total_duration": 1000,
            }
        )
        result = OllamaAdapter("qwen3:4b").invoke(self.envelope)
        self.assertEqual(result.status, "PASS")
        self.assertTrue(result.evidence_eligible)
        self.assertEqual(result.estimated_cost_usd, 0.0)

        normalized = normalize_adapter_result(self.envelope, result)
        self.assertEqual(normalized["case_id"], "EXP-A-001")
        self.assertEqual(normalized["mechanism_id"], "local-reasoner-a")
        self.assertEqual(normalized["case_model_visible_sha256"], "abc123")
        self.assertEqual(normalized["raw_output"], "material finding")

    @patch("adapters.request.urlopen")
    def test_prompt_contains_only_model_visible_payload(self, urlopen):
        urlopen.return_value = _FakeResponse({"model": "qwen3:4b", "response": "ok"})
        envelope = dict(self.envelope)
        envelope["ground_truth_ref"] = "MUST_NOT_LEAK"
        envelope["private_truth"] = {"answer": "MUST_NOT_LEAK"}
        OllamaAdapter("qwen3:4b").invoke(envelope)
        req = urlopen.call_args.args[0]
        body = json.loads(req.data.decode("utf-8"))
        prompt = body["prompt"]
        self.assertIn("Find material defects.", prompt)
        self.assertNotIn("MUST_NOT_LEAK", prompt)
        self.assertNotIn("ground_truth_ref", prompt)

    @patch("adapters.request.urlopen", side_effect=TimeoutError("timed out"))
    def test_transport_failure_is_not_evidence(self, _urlopen):
        result = OllamaAdapter("qwen3:4b").invoke(self.envelope)
        self.assertEqual(result.status, "ERROR")
        self.assertFalse(result.evidence_eligible)


if __name__ == "__main__":
    unittest.main()
