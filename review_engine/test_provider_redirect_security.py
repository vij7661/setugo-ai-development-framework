from __future__ import annotations

import os
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import patch

from review_engine.anthropic_provider import AnthropicEndpoint, AnthropicProvider
from review_engine.gemini_provider import GeminiEndpoint, GeminiProvider
from review_engine.models import ReviewerConfig
from review_engine.providers import OpenAICompatibleEndpoint, OpenAICompatibleProvider


class _SinkHandler(BaseHTTPRequestHandler):
    requests_seen: list[dict[str, str]] = []

    def _capture(self) -> None:
        self.__class__.requests_seen.append({key.lower(): value for key, value in self.headers.items()})
        self.send_response(200)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_GET(self) -> None:
        self._capture()

    def do_POST(self) -> None:
        self._capture()

    def log_message(self, fmt: str, *args) -> None:
        return


class _RedirectHandler(BaseHTTPRequestHandler):
    redirect_target = ""
    requests_seen = 0

    def do_POST(self) -> None:
        self.__class__.requests_seen += 1
        self.send_response(302)
        self.send_header("Location", self.__class__.redirect_target)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def log_message(self, fmt: str, *args) -> None:
        return


def _serve(handler: type[BaseHTTPRequestHandler]) -> tuple[ThreadingHTTPServer, threading.Thread]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def _config(*, provider: str, env: str) -> ReviewerConfig:
    return ReviewerConfig(
        role="R2",
        provider=provider,
        model="security-test-model",
        sku="default",
        deployment_path="api",
        api_key_env=env,
        foundation_lineage=f"{provider}-lineage",
        qualification_ref=f"{provider}-q",
    )


class ProviderRedirectSecurityTests(unittest.TestCase):
    def setUp(self) -> None:
        _SinkHandler.requests_seen = []
        _RedirectHandler.requests_seen = 0
        self.sink, self.sink_thread = _serve(_SinkHandler)
        sink_host, sink_port = self.sink.server_address
        _RedirectHandler.redirect_target = f"http://{sink_host}:{sink_port}/credential-sink"
        self.redirector, self.redirect_thread = _serve(_RedirectHandler)
        redirect_host, redirect_port = self.redirector.server_address
        self.base_url = f"http://{redirect_host}:{redirect_port}"

    def tearDown(self) -> None:
        self.redirector.shutdown()
        self.sink.shutdown()
        self.redirector.server_close()
        self.sink.server_close()
        self.redirect_thread.join(timeout=5)
        self.sink_thread.join(timeout=5)

    def test_all_credential_bearing_adapters_refuse_redirect_without_forwarding_secret(self) -> None:
        adapters = (
            (
                "openai-compatible",
                OpenAICompatibleProvider(OpenAICompatibleEndpoint(base_url=self.base_url, max_attempts=1)),
                _config(provider="openai-compatible", env="OPENAI_REDIRECT_TEST_KEY"),
                "OPENAI_REDIRECT_TEST_KEY",
            ),
            (
                "anthropic",
                AnthropicProvider(AnthropicEndpoint(base_url=self.base_url, max_attempts=1)),
                _config(provider="anthropic", env="ANTHROPIC_REDIRECT_TEST_KEY"),
                "ANTHROPIC_REDIRECT_TEST_KEY",
            ),
            (
                "gemini",
                GeminiProvider(GeminiEndpoint(base_url=self.base_url, max_attempts=1)),
                _config(provider="gemini", env="GEMINI_REDIRECT_TEST_KEY"),
                "GEMINI_REDIRECT_TEST_KEY",
            ),
        )

        for name, adapter, config, env_name in adapters:
            with self.subTest(adapter=name), patch.dict(os.environ, {env_name: f"secret-for-{name}"}, clear=False):
                with self.assertRaisesRegex(RuntimeError, "HTTP 302"):
                    adapter.invoke(config, {"artifact": {"artifact_hash": "trusted-artifact"}})

        self.assertEqual(_RedirectHandler.requests_seen, 3)
        self.assertEqual(
            _SinkHandler.requests_seen,
            [],
            "credential-bearing provider requests must never follow HTTP redirects",
        )


if __name__ == "__main__":
    unittest.main()
