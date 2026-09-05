from __future__ import annotations

import io
import json
import os
import unittest
from email.message import Message
from unittest.mock import patch
from urllib.error import HTTPError

from review_engine.anthropic_provider import AnthropicEndpoint, AnthropicProvider
from review_engine.models import ReviewerConfig


class _Response:
    def __init__(self, body: dict):
        self._body = json.dumps(body).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return self._body


def cfg() -> ReviewerConfig:
    return ReviewerConfig(
        role="R2",
        provider="anthropic",
        model="claude-test",
        sku="default",
        deployment_path="anthropic-api",
        api_key_env="ANTHROPIC_TEST_KEY",
        foundation_lineage="anthropic-lineage",
        qualification_ref="q-r2",
    )


class AnthropicProviderTests(unittest.TestCase):
    def test_retryable_http_error_waits_before_retry(self):
        endpoint = AnthropicEndpoint(max_attempts=2, initial_backoff_seconds=0.1, max_backoff_seconds=1.0)
        provider = AnthropicProvider(endpoint)
        headers = Message()
        headers["Retry-After"] = "0.2"
        error = HTTPError(
            url="https://api.anthropic.com/v1/messages",
            code=429,
            msg="rate limited",
            hdrs=headers,
            fp=io.BytesIO(b"busy"),
        )
        body = {
            "stop_reason": "end_turn",
            "content": [{
                "type": "text",
                "text": json.dumps({"output": "clean", "findings": []}),
            }],
        }
        context = {"artifact": {"artifact_hash": "artifact-hash"}}

        with patch.dict(os.environ, {"ANTHROPIC_TEST_KEY": "test-value"}, clear=False), \
             patch("review_engine.anthropic_provider.urlopen", side_effect=[error, _Response(body)]), \
             patch("review_engine.anthropic_provider.time.sleep") as sleep:
            result = provider.invoke(cfg(), context)

        self.assertEqual(result.output, "clean")
        self.assertEqual(result.artifact_hash, "artifact-hash")
        sleep.assert_called_once_with(0.2)

    def test_invalid_backoff_configuration_is_rejected(self):
        with self.assertRaises(ValueError):
            AnthropicProvider(AnthropicEndpoint(initial_backoff_seconds=2.0, max_backoff_seconds=1.0))


if __name__ == "__main__":
    unittest.main()
