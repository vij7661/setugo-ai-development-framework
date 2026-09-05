"""Generic OpenAI-compatible remote reasoning adapter.

Provider/model identities are runtime configuration. Transient delivery failures are
retried within a bounded policy; every exhausted failure remains explicit evidence.
"""
from __future__ import annotations

import json
import os
import random
import time
from dataclasses import dataclass
from typing import Any, Mapping
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from adapters import AdapterResult, MechanismAdapter
from review_contract import REVIEW_OUTPUT_SCHEMA_INSTRUCTION

RETRYABLE_HTTP = frozenset({429, 500, 502, 503, 504})


@dataclass(frozen=True)
class RemoteProviderConfig:
    provider_id: str
    base_url: str
    model: str
    api_key_env: str
    timeout_seconds: int = 120
    max_attempts: int = 3
    initial_backoff_seconds: float = 2.0
    max_backoff_seconds: float = 15.0


class OpenAICompatibleAdapter(MechanismAdapter):
    def __init__(self, config: RemoteProviderConfig) -> None:
        self._config = config

    def _delay(self, attempt: int, retry_after: str | None = None) -> None:
        if retry_after:
            try:
                seconds = float(retry_after)
                time.sleep(min(max(seconds, 0.0), self._config.max_backoff_seconds))
                return
            except ValueError:
                pass
        base = min(self._config.initial_backoff_seconds * (2 ** max(0, attempt - 1)), self._config.max_backoff_seconds)
        time.sleep(base + random.uniform(0, min(0.5, base / 4)))

    def invoke(self, envelope: Mapping[str, Any]) -> AdapterResult:
        if "model_visible" not in envelope:
            raise ValueError("prepared envelope must contain model_visible")
        api_key = os.environ.get(self._config.api_key_env)
        if not api_key:
            raise RuntimeError(f"missing API credential in environment variable {self._config.api_key_env}")
        payload = {
            "model": self._config.model,
            "messages": [
                {"role": "system", "content": "You are an independent software-review mechanism. Use only the supplied case content. Report concrete material defects or requested change-impact conclusions; do not invent hidden requirements.\n\n" + REVIEW_OUTPUT_SCHEMA_INSTRUCTION},
                {"role": "user", "content": json.dumps(envelope["model_visible"], ensure_ascii=False)},
            ],
            "temperature": 0,
        }
        endpoint = self._config.base_url.rstrip("/") + "/chat/completions"
        started = time.perf_counter()
        last_error: str | None = None
        for attempt in range(1, self._config.max_attempts + 1):
            request = Request(endpoint, data=json.dumps(payload).encode("utf-8"), headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json", "User-Agent": "setugo-governed-platform-pilot/1.0"}, method="POST")
            try:
                with urlopen(request, timeout=self._config.timeout_seconds) as response:
                    body = json.loads(response.read().decode("utf-8"))
            except HTTPError as exc:
                detail = exc.read().decode("utf-8", errors="replace")
                last_error = f"provider HTTP {exc.code}: {detail}"
                if exc.code in RETRYABLE_HTTP and attempt < self._config.max_attempts:
                    self._delay(attempt, exc.headers.get("Retry-After")); continue
                raise RuntimeError(f"{last_error} (attempt {attempt}/{self._config.max_attempts})") from exc
            except URLError as exc:
                last_error = f"provider connection failed: {exc.reason}"
                if attempt < self._config.max_attempts:
                    self._delay(attempt); continue
                raise RuntimeError(f"{last_error} (attempt {attempt}/{self._config.max_attempts})") from exc

            choices = body.get("choices") or []
            first = choices[0] if choices else {}
            message = first.get("message") or {}
            raw_output = message.get("content")
            finish_reason = first.get("finish_reason")
            if not choices or not isinstance(raw_output, str) or not raw_output.strip():
                last_error = "provider response contained no usable text completion"
                if attempt < self._config.max_attempts:
                    self._delay(attempt); continue
                raise RuntimeError(f"{last_error} (attempt {attempt}/{self._config.max_attempts})")
            if finish_reason != "stop":
                raise RuntimeError(f"provider completion is incomplete or nonterminal: finish_reason={finish_reason!r}")

            latency_ms = max(0, int((time.perf_counter() - started) * 1000))
            usage = body.get("usage") or {}
            return AdapterResult(
                status="PASS",
                raw_output=raw_output,
                provider=self._config.provider_id,
                mechanism_version=self._config.model,
                input_tokens=usage.get("prompt_tokens"),
                output_tokens=usage.get("completion_tokens"),
                estimated_cost_usd=0.0,
                latency_ms=latency_ms,
                evidence_eligible=True,
                runtime_metadata={
                    "provider_attempts": attempt,
                    "finish_reason": finish_reason,
                    "response_model_claim": body.get("model"),
                    "completion_complete": True,
                    "configured_model": self._config.model,
                },
            )
        raise RuntimeError(last_error or "provider failed without a usable completion")
