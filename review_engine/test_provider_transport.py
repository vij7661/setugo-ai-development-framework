from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from review_engine.anthropic_provider import AnthropicEndpoint, AnthropicProvider
from review_engine.configuration import build_provider_registry, load_configuration
from review_engine.gemini_provider import GeminiEndpoint, GeminiProvider
from review_engine.providers import (
    OpenAICompatibleEndpoint,
    OpenAICompatibleProvider,
    validate_provider_base_url,
)


class ProviderTransportTests(unittest.TestCase):
    def test_remote_plain_http_is_rejected_for_every_provider_adapter(self):
        constructors = (
            lambda: OpenAICompatibleProvider(OpenAICompatibleEndpoint(base_url="http://api.example.test/v1")),
            lambda: AnthropicProvider(AnthropicEndpoint(base_url="http://api.example.test/v1")),
            lambda: GeminiProvider(GeminiEndpoint(base_url="http://api.example.test/v1beta")),
        )
        for construct in constructors:
            with self.subTest(construct=construct):
                with self.assertRaisesRegex(ValueError, "must use https"):
                    construct()

    def test_private_network_plain_http_is_not_mistaken_for_loopback(self):
        for url in (
            "http://10.0.0.5:8080/v1",
            "http://172.16.0.9/v1",
            "http://192.168.1.20/v1",
            "http://example.test/v1",
        ):
            with self.subTest(url=url):
                with self.assertRaisesRegex(ValueError, "must use https"):
                    validate_provider_base_url(url)

    def test_explicit_loopback_http_is_allowed_for_local_development(self):
        urls = (
            "http://localhost:8080/v1",
            "http://127.0.0.1:8080/v1",
            "http://127.0.0.2:8080/v1",
            "http://[::1]:8080/v1",
        )
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(validate_provider_base_url(url), url)

        self.assertEqual(
            OpenAICompatibleProvider(OpenAICompatibleEndpoint(base_url=urls[0])).endpoint.base_url,
            urls[0],
        )
        self.assertEqual(AnthropicProvider(AnthropicEndpoint(base_url=urls[1])).endpoint.base_url, urls[1])
        self.assertEqual(GeminiProvider(GeminiEndpoint(base_url=urls[3])).endpoint.base_url, urls[3])

    def test_https_remote_endpoints_remain_allowed(self):
        urls = (
            "https://openrouter.example/v1",
            "https://anthropic.example/v1",
            "https://gemini.example/v1beta",
        )
        self.assertEqual(
            OpenAICompatibleProvider(OpenAICompatibleEndpoint(base_url=urls[0])).endpoint.base_url,
            urls[0],
        )
        self.assertEqual(AnthropicProvider(AnthropicEndpoint(base_url=urls[1])).endpoint.base_url, urls[1])
        self.assertEqual(GeminiProvider(GeminiEndpoint(base_url=urls[2])).endpoint.base_url, urls[2])

    def test_base_url_cannot_embed_credentials_query_or_fragment(self):
        invalid = (
            "https://user:password@api.example.test/v1",
            "https://api.example.test/v1?api_key=secret",
            "https://api.example.test/v1#fragment",
            "https://api.example.test/v1\nInjected: header",
        )
        for url in invalid:
            with self.subTest(url=url):
                with self.assertRaises(ValueError):
                    validate_provider_base_url(url)

    def test_configuration_registry_build_fails_closed_for_remote_http(self):
        data = {
            "providers": {
                "p": {
                    "adapter": "openai_compatible",
                    "base_url": "http://remote.example.test/v1",
                }
            },
            "reviewers": {
                "R1": {
                    "provider": "p",
                    "model": "model-a",
                    "api_key_env": "KEY_A",
                    "foundation_lineage": "lineage-a",
                }
            },
        }
        tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
        with tmp:
            json.dump(data, tmp)
        config = load_configuration(Path(tmp.name))
        with self.assertRaisesRegex(ValueError, "must use https"):
            build_provider_registry(config)


if __name__ == "__main__":
    unittest.main()
