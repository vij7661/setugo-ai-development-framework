import json
import os
import unittest
from unittest.mock import patch

from openai_compatible import OpenAICompatibleAdapter, RemoteProviderConfig


class _FakeResponse:
    def __init__(self, body):
        self._body = json.dumps(body).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return self._body


class OpenAICompatibleAdapterTests(unittest.TestCase):
    def setUp(self):
        self.config = RemoteProviderConfig(
            provider_id="example",
            base_url="https://example.invalid/v1",
            model="model-x",
            api_key_env="TEST_PROVIDER_KEY",
        )
        self.envelope = {"model_visible": {"review_task": "check this"}}

    def tearDown(self):
        os.environ.pop("TEST_PROVIDER_KEY", None)

    def test_missing_key_is_rejected_before_network(self):
        adapter = OpenAICompatibleAdapter(self.config)
        with self.assertRaisesRegex(RuntimeError, "missing API credential"):
            adapter.invoke(self.envelope)

    @patch("openai_compatible.urlopen")
    def test_success_captures_model_tokens_and_zero_configured_cost(self, mocked_urlopen):
        os.environ["TEST_PROVIDER_KEY"] = "secret"
        mocked_urlopen.return_value = _FakeResponse(
            {
                "model": "model-x-revision",
                "choices": [{"message": {"content": "material defect"}}],
                "usage": {"prompt_tokens": 12, "completion_tokens": 4},
            }
        )
        result = OpenAICompatibleAdapter(self.config).invoke(self.envelope)
        self.assertEqual(result.raw_output, "material defect")
        self.assertEqual(result.provider, "example")
        self.assertEqual(result.mechanism_version, "model-x-revision")
        self.assertEqual(result.input_tokens, 12)
        self.assertEqual(result.output_tokens, 4)
        self.assertTrue(result.evidence_eligible)

        request = mocked_urlopen.call_args.args[0]
        self.assertNotIn(b"ground_truth", request.data)
        self.assertNotIn(b"authoritative_intent", request.data)


if __name__ == "__main__":
    unittest.main()
