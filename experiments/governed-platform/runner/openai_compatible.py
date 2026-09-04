"""Generic OpenAI-compatible remote reasoning adapter.

Designed for providers that expose an OpenAI-compatible chat-completions endpoint.
Provider/model identities are runtime configuration, never workflow constants.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Any, Mapping
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from adapters import AdapterResult, MechanismAdapter


@dataclass(frozen=True)
class RemoteProviderConfig:
    provider_id: str
    base_url: str
    model: str
    api_key_env: str
    timeout_seconds: int = 120


class OpenAICompatibleAdapter(MechanismAdapter):
    def __init__(self, config: RemoteProviderConfig) -> None:
        self._config = config

    def invoke(self, envelope: Mapping[str, Any]) -> AdapterResult:
        if "model_visible" not in envelope:
            raise ValueError("prepared envelope must contain model_visible")

        api_key = os.environ.get(self._config.api_key_env)
        if not api_key:
            raise RuntimeError(
                f"missing API credential in environment variable {self._config.api_key_env}"
            )

        payload = {
            "model": self._config.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are an independent software-review mechanism. "
                        "Use only the supplied case content. Report concrete material defects; "
                        "do not invent hidden requirements."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(envelope["model_visible"], ensure_ascii=False),
                },
            ],
            "temperature": 0,
        }

        endpoint = self._config.base_url.rstrip("/") + "/chat/completions"
        request = Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": "setugo-governed-platform-pilot/1.0",
            },
            method="POST",
        )

        started = time.perf_counter()
        try:
            with urlopen(request, timeout=self._config.timeout_seconds) as response:
                body = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"provider HTTP {exc.code}: {detail}") from exc
        except URLError as exc:
            raise RuntimeError(f"provider connection failed: {exc.reason}") from exc
        latency_ms = max(0, int((time.perf_counter() - started) * 1000))

        choices = body.get("choices") or []
        if not choices:
            raise RuntimeError("provider response contained no choices")
        message = choices[0].get("message") or {}
        raw_output = message.get("content")
        if not isinstance(raw_output, str):
            raise RuntimeError("provider response contained no text content")

        usage = body.get("usage") or {}
        return AdapterResult(
            status="PASS",
            raw_output=raw_output,
            provider=self._config.provider_id,
            mechanism_version=body.get("model") or self._config.model,
            input_tokens=usage.get("prompt_tokens"),
            output_tokens=usage.get("completion_tokens"),
            estimated_cost_usd=0.0,
            latency_ms=latency_ms,
            evidence_eligible=True,
        )
