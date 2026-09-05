import json
import os
import unittest
from unittest.mock import patch

from openai_compatible import OpenAICompatibleAdapter, RemoteProviderConfig


class _FakeResponse:
    def __init__(self, body): self._body = json.dumps(body).encode("utf-8")
    def __enter__(self): return self
    def __exit__(self, exc_type, exc, tb): return False
    def read(self): return self._body


class OpenAICompatibleAdapterTests(unittest.TestCase):
    def setUp(self):
        self.config = RemoteProviderConfig(provider_id="example", base_url="https://example.invalid/v1", model="model-x", api_key_env="TEST_PROVIDER_KEY", max_attempts=1)
        self.envelope = {"model_visible": {"review_task": "check this"}}

    def tearDown(self): os.environ.pop("TEST_PROVIDER_KEY", None)

    def test_missing_key_is_rejected_before_network(self):
        with self.assertRaisesRegex(RuntimeError, "missing API credential"):
            OpenAICompatibleAdapter(self.config).invoke(self.envelope)

    @patch("openai_compatible.urlopen")
    def test_success_requires_terminal_stop_and_captures_metadata(self, mocked_urlopen):
        os.environ["TEST_PROVIDER_KEY"] = "secret"
        mocked_urlopen.return_value = _FakeResponse({
            "model": "spoofable-response-label",
            "choices": [{"message": {"content": "material defect"}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 12, "completion_tokens": 4},
        })
        result = OpenAICompatibleAdapter(self.config).invoke(self.envelope)
        self.assertEqual(result.raw_output, "material defect")
        self.assertEqual(result.provider, "example")
        self.assertEqual(result.mechanism_version, "model-x")
        self.assertEqual(result.runtime_metadata["response_model_claim"], "spoofable-response-label")
        self.assertEqual(result.runtime_metadata["configured_model"], "model-x")
        self.assertTrue(result.runtime_metadata["completion_complete"])
        request = mocked_urlopen.call_args.args[0]
        self.assertNotIn(b"ground_truth", request.data)

    @patch("openai_compatible.urlopen")
    def test_length_truncated_completion_is_rejected_even_if_text_is_valid_json(self, mocked_urlopen):
        os.environ["TEST_PROVIDER_KEY"] = "secret"
        mocked_urlopen.return_value = _FakeResponse({
            "model": "model-x",
            "choices": [{"message": {"content": '{"summary":"clean","findings":[]}'}, "finish_reason": "length"}],
            "usage": {"prompt_tokens": 12, "completion_tokens": 2048},
        })
        with self.assertRaisesRegex(RuntimeError, "incomplete or nonterminal"):
            OpenAICompatibleAdapter(self.config).invoke(self.envelope)

    @patch("openai_compatible.urlopen")
    def test_missing_finish_reason_is_rejected(self, mocked_urlopen):
        os.environ["TEST_PROVIDER_KEY"] = "secret"
        mocked_urlopen.return_value = _FakeResponse({"model": "model-x", "choices": [{"message": {"content": "looks complete"}}]})
        with self.assertRaisesRegex(RuntimeError, "incomplete or nonterminal"):
            OpenAICompatibleAdapter(self.config).invoke(self.envelope)


if __name__ == "__main__": unittest.main()
