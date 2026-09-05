from __future__ import annotations

import json
import os
import random
import time
from dataclasses import dataclass, replace
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from .models import ReviewerConfig, ReviewerResponse
from .providers import (
    RETRYABLE_HTTP,
    SYSTEM_INSTRUCTION,
    _parse_response,
    validate_provider_base_url,
)


@dataclass(frozen=True)
class GeminiEndpoint:
    base_url: str = "https://generativelanguage.googleapis.com/v1beta"
    timeout_seconds: int = 120
    max_attempts: int = 3
    temperature: float = 0.0
    max_output_tokens: int = 4096
    initial_backoff_seconds: float = 1.0
    max_backoff_seconds: float = 10.0


class GeminiProvider:
    def __init__(self, endpoint: GeminiEndpoint) -> None:
        base_url = validate_provider_base_url(endpoint.base_url, label="Gemini")
        if not 0 <= endpoint.temperature <= 2:
            raise ValueError("Gemini temperature must be in [0,2]")
        if endpoint.initial_backoff_seconds < 0 or endpoint.max_backoff_seconds < endpoint.initial_backoff_seconds:
            raise ValueError("invalid Gemini backoff configuration")
        if endpoint.max_attempts < 1:
            raise ValueError("Gemini max_attempts must be >= 1")
        if endpoint.timeout_seconds <= 0:
            raise ValueError("Gemini timeout_seconds must be positive")
        if endpoint.max_output_tokens < 1:
            raise ValueError("Gemini max_output_tokens must be positive")
        self.endpoint = replace(endpoint, base_url=base_url)

    def _delay(self, attempt: int, retry_after: str | None = None) -> None:
        if retry_after:
            try:
                time.sleep(min(max(float(retry_after), 0.0), self.endpoint.max_backoff_seconds))
                return
            except ValueError:
                pass
        base = min(
            self.endpoint.initial_backoff_seconds * (2 ** max(0, attempt - 1)),
            self.endpoint.max_backoff_seconds,
        )
        time.sleep(base + random.uniform(0, min(0.25, base / 4 if base else 0.0)))

    def invoke(self, config: ReviewerConfig, context: dict) -> ReviewerResponse:
        config.validate()
        key = os.environ.get(config.api_key_env)
        if not key:
            raise RuntimeError(f"missing API credential in environment variable {config.api_key_env}")
        payload = {
            "systemInstruction": {"parts": [{"text": SYSTEM_INSTRUCTION}]},
            "contents": [{"role": "user", "parts": [{"text": json.dumps(context, ensure_ascii=False, sort_keys=True)}]}],
            "generationConfig": {
                "temperature": self.endpoint.temperature,
                "maxOutputTokens": self.endpoint.max_output_tokens,
                "responseMimeType": "application/json",
            },
        }
        model = quote(config.model, safe="")
        url = self.endpoint.base_url.rstrip("/") + f"/models/{model}:generateContent"
        last_error = None
        for attempt in range(1, self.endpoint.max_attempts + 1):
            request = Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "x-goog-api-key": key,
                    "content-type": "application/json",
                    "user-agent": "setugo-review-engine-mvp/1.0",
                },
                method="POST",
            )
            try:
                with urlopen(request, timeout=self.endpoint.timeout_seconds) as response:
                    body = json.loads(response.read().decode("utf-8"))
            except HTTPError as exc:
                detail = exc.read().decode("utf-8", errors="replace")[:1000]
                last_error = f"Gemini HTTP {exc.code}: {detail}"
                if exc.code in RETRYABLE_HTTP and attempt < self.endpoint.max_attempts:
                    self._delay(attempt, exc.headers.get("Retry-After"))
                    continue
                raise RuntimeError(f"{last_error} (attempt {attempt}/{self.endpoint.max_attempts})") from exc
            except URLError as exc:
                last_error = f"Gemini connection failed: {exc.reason}"
                if attempt < self.endpoint.max_attempts:
                    self._delay(attempt)
                    continue
                raise RuntimeError(f"{last_error} (attempt {attempt}/{self.endpoint.max_attempts})") from exc

            candidates = body.get("candidates") or []
            candidate = candidates[0] if candidates else {}
            finish_reason = candidate.get("finishReason")
            if finish_reason not in {"STOP", "MAX_TOKENS"}:
                raise RuntimeError(f"Gemini completion nonterminal: finishReason={finish_reason!r}")
            if finish_reason == "MAX_TOKENS":
                raise RuntimeError("Gemini completion truncated at max tokens")
            content = candidate.get("content") or {}
            parts = content.get("parts") or []
            text = "".join(str(part.get("text", "")) for part in parts if isinstance(part, dict))
            if not text.strip():
                raise RuntimeError("Gemini response contained no usable text")
            return _parse_response(config.role, context, text)
        raise RuntimeError(last_error or "Gemini provider failed")
