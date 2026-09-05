from __future__ import annotations

import ipaddress
import json
import os
import random
import time
from copy import deepcopy
from dataclasses import dataclass
from typing import Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

from .models import ReviewFinding, ReviewerConfig, ReviewerResponse
from .qualification import reviewer_context_hash
from .truth_contract import TVC_VERSION, validate_epistemic_review

RETRYABLE_HTTP = frozenset({429, 500, 502, 503, 504})
LOOPBACK_HOSTNAMES = frozenset({"localhost"})


class ProviderAdapter(Protocol):
    def invoke(self, config: ReviewerConfig, context: dict) -> ReviewerResponse: ...


def validate_provider_base_url(base_url: str, *, label: str = "provider") -> str:
    """Require encrypted transport for remote credential-bearing provider calls."""
    if not isinstance(base_url, str) or not base_url.strip():
        raise ValueError(f"{label} base_url required")
    value = base_url.strip()
    if any(ch.isspace() for ch in value):
        raise ValueError(f"{label} base_url cannot contain whitespace")

    parsed = urlparse(value)
    if parsed.scheme not in {"https", "http"} or not parsed.hostname:
        raise ValueError(f"{label} base_url must be an absolute http(s) URL")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError(f"{label} base_url must not contain embedded credentials")
    if parsed.query or parsed.fragment:
        raise ValueError(f"{label} base_url must not contain query or fragment components")

    if parsed.scheme == "http":
        host = parsed.hostname.lower()
        loopback = host in LOOPBACK_HOSTNAMES
        if not loopback:
            try:
                loopback = ipaddress.ip_address(host).is_loopback
            except ValueError:
                loopback = False
        if not loopback:
            raise ValueError(f"{label} remote base_url must use https")
    return value


class _RejectProviderRedirectHandler(HTTPRedirectHandler):
    """Fail closed instead of forwarding credential-bearing headers on redirect."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        raise HTTPError(
            req.full_url,
            code,
            "provider HTTP redirects are forbidden",
            headers,
            fp,
        )


_PROVIDER_OPENER = build_opener(_RejectProviderRedirectHandler())


def urlopen(request: Request, timeout: int | float):
    """Provider transport opener with redirects disabled."""
    return _PROVIDER_OPENER.open(request, timeout=timeout)


@dataclass(frozen=True)
class OpenAICompatibleEndpoint:
    base_url: str
    timeout_seconds: int = 120
    max_attempts: int = 3
    initial_backoff_seconds: float = 1.0
    max_backoff_seconds: float = 10.0
    temperature: float = 0.0


SYSTEM_INSTRUCTION = f"""You are a governed review-engine role. Return STRICT JSON only.
Never claim release, production, write, deployment, approval, or authorization authority.
Do not reveal private chain-of-thought. Give concise evidence-based conclusions only.
Agreement with another model is not proof of correctness.

Schema:
{{
  "output": "user-facing artifact or concise review conclusion",
  "proposed_signals": {{
    "risk": "LOW|MEDIUM|HIGH|CRITICAL",
    "materiality": "NONE|REVERSIBLE|MATERIAL|CONSEQUENTIAL",
    "uncertainty": "LOW|MEDIUM|HIGH",
    "external_action": false,
    "mutation_requested": false,
    "requirement_ambiguity": false,
    "evidence_complete": true
  }},
  "epistemic_review": {{
    "version": "{TVC_VERSION}",
    "correspondence": "SUPPORTED|UNSUPPORTED|UNVERIFIED|NOT_APPLICABLE",
    "coherence": "CONSISTENT|CONTRADICTED|UNRESOLVED",
    "pragmatic": "VIABLE|LIMITED|NOT_VIABLE|NOT_APPLICABLE",
    "semantic": "PRECISE|AMBIGUOUS|MISLEADING",
    "contradiction_refs": [],
    "claims": [
      {{
        "claim_id": "c1",
        "text": "specific truth-bearer",
        "claim_type": "EMPIRICAL_FACT|LOGICAL_CLAIM|DEFINITION|INFERENCE|ASSUMPTION|HYPOTHESIS|OPINION|RECOMMENDATION",
        "correspondence": "SUPPORTED|UNSUPPORTED|UNVERIFIED|NOT_APPLICABLE",
        "evidence_refs": [],
        "material": false
      }}
    ]
  }},
  "findings": [
    {{
      "finding_id": "stable local id",
      "severity": "NONE|LOW|MEDIUM|HIGH|CRITICAL",
      "material": false,
      "summary": "concise finding",
      "violated_invariant": null,
      "evidence_refs": [],
      "affected_scope": [],
      "first_invalid_claim": null
    }}
  ],
  "resolved_finding_ids": []
}}
The epistemic_review object is mandatory. Empirical claims marked SUPPORTED must include evidence_refs.
Correspondence, coherence, pragmatic utility and semantic precision are separate dimensions.
Pragmatic usefulness never overrides factual, logical or governance defects.
For R1 generation, findings may be empty. For R2/R3 review, localize the first material failure when possible and do not rewrite unrelated scope.
resolved_finding_ids is only for R3 ADJUDICATION. It must contain exact frozen Phase-A material finding IDs that the adjudicator explicitly resolves. Never use omission as resolution and never invent IDs.
"""


def _context_artifact_hash(context: dict) -> str | None:
    artifact = context.get("artifact")
    if isinstance(artifact, dict):
        value = artifact.get("artifact_hash")
        if isinstance(value, str):
            return value
    value = context.get("artifact_hash")
    return value if isinstance(value, str) else None


def _parse_response(role: str, context: dict, raw: str) -> ReviewerResponse:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError("reviewer returned non-JSON output") from exc
    if not isinstance(data, dict) or not isinstance(data.get("output"), str) or not data["output"].strip():
        raise RuntimeError("reviewer JSON must contain non-empty output")

    findings: list[ReviewFinding] = []
    raw_findings = data.get("findings", [])
    if not isinstance(raw_findings, list):
        raise RuntimeError("reviewer findings must be a list")
    for index, item in enumerate(raw_findings):
        if not isinstance(item, dict):
            raise RuntimeError("reviewer finding must be an object")
        finding = ReviewFinding(
            finding_id=str(item.get("finding_id") or f"{role.lower()}-{index+1}"),
            reviewer_role=role,
            severity=str(item.get("severity", "NONE")),
            material=bool(item.get("material", False)),
            summary=str(item.get("summary", "")).strip(),
            violated_invariant=item.get("violated_invariant"),
            evidence_refs=tuple(str(v) for v in item.get("evidence_refs", []) if v is not None),
            affected_scope=tuple(str(v) for v in item.get("affected_scope", []) if v is not None),
            first_invalid_claim=item.get("first_invalid_claim"),
        )
        finding.validate()
        findings.append(finding)

    proposed = data.get("proposed_signals", {})
    if proposed is None:
        proposed = {}
    if not isinstance(proposed, dict):
        raise RuntimeError("proposed_signals must be an object")

    raw_resolved = data.get("resolved_finding_ids", [])
    if raw_resolved is None:
        raw_resolved = []
    if not isinstance(raw_resolved, list):
        raise RuntimeError("resolved_finding_ids must be a list")
    if any(not isinstance(value, str) or not value.strip() for value in raw_resolved):
        raise RuntimeError("resolved_finding_ids must contain non-empty strings")

    epistemic_review = validate_epistemic_review(data.get("epistemic_review"))

    response = ReviewerResponse(
        role=role,
        artifact_hash=_context_artifact_hash(context),
        output=data["output"].strip(),
        findings=tuple(findings),
        complete=True,
        proposed_signals=proposed,
        epistemic_review=epistemic_review,
        resolved_finding_ids=tuple(raw_resolved),
    )
    response.validate()
    return response


class OpenAICompatibleProvider:
    def __init__(self, endpoint: OpenAICompatibleEndpoint) -> None:
        base_url = validate_provider_base_url(endpoint.base_url, label="provider")
        if not 0 <= endpoint.temperature <= 2:
            raise ValueError("temperature must be in [0,2]")
        if endpoint.initial_backoff_seconds < 0 or endpoint.max_backoff_seconds < endpoint.initial_backoff_seconds:
            raise ValueError("invalid provider backoff configuration")
        if endpoint.max_attempts < 1:
            raise ValueError("provider max_attempts must be >= 1")
        if endpoint.timeout_seconds <= 0:
            raise ValueError("provider timeout_seconds must be positive")
        self.endpoint = OpenAICompatibleEndpoint(
            base_url=base_url,
            timeout_seconds=endpoint.timeout_seconds,
            max_attempts=endpoint.max_attempts,
            initial_backoff_seconds=endpoint.initial_backoff_seconds,
            max_backoff_seconds=endpoint.max_backoff_seconds,
            temperature=endpoint.temperature,
        )

    def _delay(self, attempt: int, retry_after: str | None = None) -> None:
        if retry_after:
            try:
                time.sleep(min(max(float(retry_after), 0.0), self.endpoint.max_backoff_seconds))
                return
            except ValueError:
                pass
        base = min(self.endpoint.initial_backoff_seconds * (2 ** max(0, attempt - 1)), self.endpoint.max_backoff_seconds)
        time.sleep(base + random.uniform(0, min(0.25, base / 4)))

    def invoke(self, config: ReviewerConfig, context: dict) -> ReviewerResponse:
        config.validate()
        key = os.environ.get(config.api_key_env)
        if not key:
            raise RuntimeError(f"missing API credential in environment variable {config.api_key_env}")

        payload = {
            "model": config.model,
            "messages": [
                {"role": "system", "content": SYSTEM_INSTRUCTION},
                {"role": "user", "content": json.dumps(context, ensure_ascii=False, sort_keys=True)},
            ],
            "temperature": self.endpoint.temperature,
            "response_format": {"type": "json_object"},
        }
        endpoint = self.endpoint.base_url.rstrip("/") + "/chat/completions"
        last_error: str | None = None
        for attempt in range(1, self.endpoint.max_attempts + 1):
            request = Request(
                endpoint,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json",
                    "User-Agent": "setugo-review-engine-mvp/1.0",
                },
                method="POST",
            )
            try:
                with urlopen(request, timeout=self.endpoint.timeout_seconds) as response:
                    body = json.loads(response.read().decode("utf-8"))
            except HTTPError as exc:
                detail = exc.read().decode("utf-8", errors="replace")[:1000]
                last_error = f"provider HTTP {exc.code}: {detail}"
                if exc.code in RETRYABLE_HTTP and attempt < self.endpoint.max_attempts:
                    self._delay(attempt, exc.headers.get("Retry-After"))
                    continue
                raise RuntimeError(f"{last_error} (attempt {attempt}/{self.endpoint.max_attempts})") from exc
            except URLError as exc:
                last_error = f"provider connection failed: {exc.reason}"
                if attempt < self.endpoint.max_attempts:
                    self._delay(attempt)
                    continue
                raise RuntimeError(f"{last_error} (attempt {attempt}/{self.endpoint.max_attempts})") from exc

            choices = body.get("choices") or []
            first = choices[0] if choices else {}
            finish_reason = first.get("finish_reason")
            content = (first.get("message") or {}).get("content")
            if finish_reason != "stop":
                raise RuntimeError(f"provider completion incomplete: finish_reason={finish_reason!r}")
            if not isinstance(content, str) or not content.strip():
                last_error = "provider response contained no usable text"
                if attempt < self.endpoint.max_attempts:
                    self._delay(attempt)
                    continue
                raise RuntimeError(last_error)
            return _parse_response(config.role, context, content)

        raise RuntimeError(last_error or "provider failed without usable completion")


class ProviderRegistry:
    """Dispatch provider adapters while preserving capability-bound context integrity.

    The registry snapshots the model-visible context before giving it to an
    adapter and rejects any response if that adapter mutates the dispatch copy.
    This prevents mutated adapter state from being accepted as governed review
    evidence. It is an in-process integrity control, not cryptographic proof of
    what a remote provider ultimately received.
    """

    provider_context_integrity_enforced = True

    def __init__(self) -> None:
        self._providers: dict[str, ProviderAdapter] = {}

    def register(self, provider_id: str, adapter: ProviderAdapter) -> None:
        if not provider_id:
            raise ValueError("provider_id required")
        self._providers[provider_id] = adapter

    def invoke(self, config: ReviewerConfig, context: dict) -> ReviewerResponse:
        adapter = self._providers.get(config.provider)
        if adapter is None:
            raise RuntimeError(f"provider adapter not registered: {config.provider}")

        try:
            dispatch_context = deepcopy(context)
            before_hash = reviewer_context_hash(dispatch_context)
        except (TypeError, ValueError):
            raise RuntimeError("provider dispatch context is not admissible") from None

        response = adapter.invoke(config, dispatch_context)

        try:
            after_hash = reviewer_context_hash(dispatch_context)
        except (TypeError, ValueError):
            raise RuntimeError("provider dispatch context changed during adapter invocation") from None
        if after_hash != before_hash:
            raise RuntimeError("provider dispatch context changed during adapter invocation")

        if not isinstance(response, ReviewerResponse):
            raise RuntimeError("provider adapter returned invalid response type")
        response.validate()
        if not response.epistemic_review:
            raise RuntimeError("provider response missing mandatory epistemic_review")
        validate_epistemic_review(response.epistemic_review)
        return response
