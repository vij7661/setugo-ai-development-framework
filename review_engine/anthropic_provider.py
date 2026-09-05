from __future__ import annotations

import json
import os
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .models import ReviewerConfig, ReviewerResponse
from .providers import SYSTEM_INSTRUCTION, _parse_response


@dataclass(frozen=True)
class AnthropicEndpoint:
    base_url: str = "https://api.anthropic.com/v1"
    anthropic_version: str = "2023-06-01"
    timeout_seconds: int = 120
    max_attempts: int = 3
    max_tokens: int = 4096
    temperature: float = 0.0


class AnthropicProvider:
    def __init__(self, endpoint: AnthropicEndpoint) -> None:
        if not endpoint.base_url.startswith(("https://", "http://")):
            raise ValueError("Anthropic base_url must be http(s)")
        if not 0 <= endpoint.temperature <= 1:
            raise ValueError("Anthropic temperature must be in [0,1]")
        self.endpoint = endpoint

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
                if exc.code in {429, 500, 502, 503, 504} and attempt < self.endpoint.max_attempts:
                    continue
                raise RuntimeError(f"{last_error} (attempt {attempt}/{self.endpoint.max_attempts})") from exc
            except URLError as exc:
                last_error = f"Anthropic connection failed: {exc.reason}"
                if attempt < self.endpoint.max_attempts:
                    continue
                raise RuntimeError(f"{last_error} (attempt {attempt}/{self.endpoint.max_attempts})") from exc

            if body.get("stop_reason") not in {"end_turn", "stop_sequence"}:
                raise RuntimeError(f"Anthropic completion incomplete: stop_reason={body.get('stop_reason')!r}")
            blocks = body.get("content") or []
            text = "".join(str(block.get("text", "")) for block in blocks if isinstance(block, dict) and block.get("type") == "text")
            if not text.strip():
                raise RuntimeError("Anthropic response contained no usable text")
            return _parse_response(config.role, context, text)
        raise RuntimeError(last_error or "Anthropic provider failed")
