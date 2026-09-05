from __future__ import annotations

import json
import os
import random
import time
from dataclasses import dataclass, replace
from urllib.error import HTTPError, URLError
from urllib.request import Request

from .models import ReviewerConfig, ReviewerResponse
from .providers import (
    RETRYABLE_HTTP,
    SYSTEM_INSTRUCTION,
    _parse_response,
    urlopen,
    validate_provider_base_url,
)


@dataclass(frozen=True)
class AnthropicEndpoint:
    base_url: str = "https://api.anthropic.com/v1"
    anthropic_version: str = "2023-06-01"
    timeout_seconds: int = 120
    max_attempts: int = 3
    max_tokens: int = 4096
    temperature: float = 0.0
    initial_backoff_seconds: float = 1.0
    max_backoff_seconds: float = 10.0


class AnthropicProvider:
    def __init__(self, endpoint: AnthropicEndpoint) -> None:
        base_url = validate_provider_base_url(endpoint.base_url, label="Anthropic")
        if not 0 <= endpoint.temperature <= 1:
            raise ValueError("Anthropic temperature must be in [0,1]")
        if endpoint.initial_backoff_seconds < 0 or endpoint.max_backoff_seconds < endpoint.initial_backoff_seconds:
            raise ValueError("invalid Anthropic backoff configuration")
        if endpoint.max_attempts < 1:
            raise ValueError("Anthropic max_attempts must be >= 1")
        if endpoint.timeout_seconds <= 0:
            raise ValueError("Anthropic timeout_seconds must be positive")
        if endpoint.max_tokens < 1:
            raise ValueError("Anthropic max_tokens must be positive")
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
            "model": config.model,
            "max_tokens": self.endpoint.max_tokens,
            "temperature": self.endpoint.temperature,
            "system": SYSTEM_INSTRUCTION,
            "messages": [{"role": "user", "content": json.dumps(context, ensure_ascii=False, sort_keys=True)}],
        }
        url = self.endpoint.base_url.rstrip("/") + "/messages"
        last_error = None
        for attempt in range(1, self.endpoint.max_attempts + 1):
            request = Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "x-api-key": key,
                    "anthropic-version": self.endpoint.anthropic_version,
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
                last_error = f"Anthropic HTTP {exc.code}: {detail}"
                if exc.code in RETRYABLE_HTTP and attempt < self.endpoint.max_attempts:
                    self._delay(attempt, exc.headers.get("Retry-After"))
                    continue
                raise RuntimeError(f"{last_error} (attempt {attempt}/{self.endpoint.max_attempts})") from exc
            except URLError as exc:
                last_error = f"Anthropic connection failed: {exc.reason}"
                if attempt < self.endpoint.max_attempts:
                    self._delay(attempt)
                    continue
                raise RuntimeError(f"{last_error} (attempt {attempt}/{self.endpoint.max_attempts})") from exc

            if body.get("stop_reason") not in {"end_turn", "stop_sequence"}:
                raise RuntimeError(f"Anthropic completion incomplete: stop_reason={body.get('stop_reason')!r}")
            blocks = body.get("content") or []
            text = "".join(
                str(block.get("text", ""))
                for block in blocks
                if isinstance(block, dict) and block.get("type") == "text"
            )
            if not text.strip():
                raise RuntimeError("Anthropic response contained no usable text")
            return _parse_response(config.role, context, text)
        raise RuntimeError(last_error or "Anthropic provider failed")
