from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import platform_candidate_review as legacy
import platform_candidate_evidence_v3 as evidence_v3
import platform_candidate_review_v5 as v5
import provider_review_telemetry as telemetry

SUPPORTED_PROVIDERS = set(v5.SUPPORTED_PROVIDERS)
OPENROUTER_URL = v5.OPENROUTER_URL

verify_provider_binding = v5.verify_provider_binding
required_secret_name = v5.required_secret_name
build_prompt = v5.build_prompt
validate = v5.validate
execution_envelope = v5.execution_envelope

_HTTP_STATUS = re.compile(r"\bHTTP(?:\s+error)?\s+(\d{3})\b", re.IGNORECASE)
_RETRYABLE_HTTP = {408, 425, 429, 500, 502, 503, 504}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _normalized_provider(value: str) -> str:
    return "".join(ch.lower() for ch in value if ch.isalnum())


def _review_execution_policy(request: dict, provider: str) -> dict:
    policy = request.get("review_execution_policy")
    if not isinstance(policy, dict):
        raise ValueError("frozen ReviewRequest lacks review_execution_policy")

    max_output = policy.get("max_output_tokens")
    if not isinstance(max_output, int) or not (1024 <= max_output <= 65536):
        raise ValueError("invalid max_output_tokens")

    reasoning_max = policy.get("reasoning_max_tokens")
    if not isinstance(reasoning_max, int) or not (0 <= reasoning_max < max_output):
        raise ValueError("invalid reasoning_max_tokens")

    response_format = policy.get("response_format")
    if response_format != "json_object":
        raise ValueError("review response_format must be json_object")

    if provider == "openrouter":
        serving = policy.get("serving_provider")
        if not isinstance(serving, str) or not serving.strip():
            raise ValueError("OpenRouter review requires serving_provider")
        if policy.get("allow_fallbacks") is not False:
            raise ValueError("governed OpenRouter review requires allow_fallbacks=false")
    return policy


def verify_route_binding(request: dict, provider: str, model: str) -> dict:
    verify_provider_binding(request, provider, model)
    slot = request.get("reviewer_slot")
    if slot not in {"R1", "R2", "R3"}:
        raise ValueError("reviewer_slot must be R1, R2, or R3")
    return _review_execution_policy(request, provider)


def _provider_error_message(body: dict) -> str | None:
    err = body.get("error")
    if err is None:
        return None
    if isinstance(err, dict):
        return f"OpenRouter provider error code={err.get('code')!r} type={err.get('type')!r} message={err.get('message')!r}"
    return f"OpenRouter provider error: {err!r}"


def _invoke_openrouter_pinned(
    key: str,
    model: str,
    prompt: str,
    policy: dict,
    raw_response_path: Path | None = None,
):
    serving_provider = policy["serving_provider"]
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
        "max_tokens": policy["max_output_tokens"],
        "reasoning": {"max_tokens": policy["reasoning_max_tokens"]},
        "response_format": {"type": "json_object"},
        "provider": {
            "order": [serving_provider],
            "only": [serving_provider],
            "allow_fallbacks": False,
            "require_parameters": True,
        },
    }
    req = Request(
        OPENROUTER_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/vij7661/setugo-ai-development-framework",
            "X-Title": "Setugo Governed Platform Review",
            "User-Agent": "setugo-governance-platform-review/7.0",
        },
        method="POST",
    )
    try:
        with urlopen(req, timeout=300) as response:
            raw = response.read().decode("utf-8")
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        if raw_response_path is not None:
            raw_response_path.write_text(detail, encoding="utf-8")
        raise RuntimeError(f"OpenRouter HTTP {exc.code}: {detail[:4000]}") from exc
    except URLError as exc:
        raise RuntimeError(f"OpenRouter connection failed: {exc.reason}") from exc

    if raw_response_path is not None:
        raw_response_path.write_text(raw, encoding="utf-8")
    try:
        body = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError("OpenRouter response was not valid JSON") from exc
    if not isinstance(body, dict):
        raise RuntimeError("OpenRouter response JSON must be an object")

    provider_error = _provider_error_message(body)
    if provider_error:
        raise RuntimeError(provider_error)

    returned_model = body.get("model")
    if returned_model != model:
        raise RuntimeError(f"OpenRouter returned model mismatch: requested={model!r} returned={returned_model!r}")

    returned_provider = body.get("provider")
    if not isinstance(returned_provider, str) or not returned_provider.strip():
        raise RuntimeError("OpenRouter response missing serving provider identity")
    if _normalized_provider(returned_provider) != _normalized_provider(serving_provider):
        raise RuntimeError(
            f"OpenRouter serving provider mismatch: requested={serving_provider!r} returned={returned_provider!r}"
        )

    choices = body.get("choices") or []
    if not choices:
        raise RuntimeError("OpenRouter response missing choices")
    finish_reason = choices[0].get("finish_reason")
    if finish_reason == "length":
        raise RuntimeError("OpenRouter completion exhausted token budget before valid assistant content")

    review = v5.v4._extract_openai_compatible_review(body, "OpenRouter")
    return body, review


def invoke(
    provider: str,
    key: str,
    model: str,
    prompt: str,
    policy: dict,
    raw_response_path: Path | None = None,
):
    if provider == "openrouter":
        return _invoke_openrouter_pinned(key, model, prompt, policy, raw_response_path)
    return v5.invoke(provider, key, model, prompt)


def classify_attempt_failure(exc: BaseException) -> tuple[bool, int | None, str]:
    """Classify attempt failures from transport/error shape, never provider identity."""
    text = str(exc)
    low = text.lower()
    match = _HTTP_STATUS.search(text)
    status = int(match.group(1)) if match else None
    if status is not None:
        return status in _RETRYABLE_HTTP, status, f"HTTP_{status}"
    if "serving provider mismatch" in low:
        return False, None, "SERVING_PROVIDER_MISMATCH"
    if "model mismatch" in low:
        return False, None, "MODEL_MISMATCH"
    if "timeout" in low or "timed out" in low:
        return True, None, "TRANSPORT_TIMEOUT"
    if any(token in low for token in ("temporarily unavailable", "temporarily overloaded", "high demand", "rate limit", "too many requests", "upstream error")):
        return True, None, "TRANSIENT_PROVIDER_UNAVAILABLE"
    if any(token in low for token in ("connection failed", "connection reset", "connection refused", "network is unreachable")):
        return True, None, "TRANSPORT_CONNECTION_FAILURE"
    return False, None, "NONRETRYABLE_PROVIDER_ATTEMPT_FAILURE"


def build_attempt_telemetry(
    *,
    request: dict,
    provider: str,
    model: str,
    credential_profile: str,
    attempt_index: int,
    request_started_at: str,
    provider_call_started_at: str,
    first_response_at: str | None,
    provider_call_completed_at: str,
    provider_latency_ms: int | float,
    outcome: str,
    retryable: bool,
    http_status: int | None,
    error_classification: str | None,
    error_detail: str | None,
    policy: dict,
    provider_response: dict | None,
    review: dict | None,
    validation: dict | None,
) -> dict:
    artifact = request.get("artifact") if isinstance(request, dict) else None
    candidate = artifact.get("commit") if isinstance(artifact, dict) else None
    event = {
        "schema_version": telemetry.SCHEMA_VERSION,
        "event_type": telemetry.EVENT_TYPE,
        "review_request_id": request.get("review_request_id"),
        "reviewed_candidate_commit": candidate,
        "reviewer_slot": request.get("reviewer_slot"),
        "gateway_provider": provider,
        "model": model,
        "credential_profile": credential_profile,
        "requested_serving_provider": policy.get("serving_provider") if isinstance(policy, dict) else None,
        "returned_serving_provider": provider_response.get("provider") if isinstance(provider_response, dict) else None,
        "attempt_index": attempt_index,
        "request_started_at": request_started_at,
        "provider_call_started_at": provider_call_started_at,
        "first_response_at": first_response_at,
        "provider_call_completed_at": provider_call_completed_at,
        "provider_latency_ms": provider_latency_ms,
        "attempt_outcome": outcome,
        "retryable": retryable,
        "http_status": http_status,
        "error_classification": error_classification,
        "error_detail": error_detail,
        "semantic_disposition": review.get("disposition") if isinstance(review, dict) else None,
        "validation_valid": validation.get("valid") if isinstance(validation, dict) else None,
        "authority_effect": telemetry.AUTHORITY_EFFECT,
    }
    return telemetry.validate_attempt_event(event)


def _write_attempt_event(out: Path, attempt_index: int, event: dict) -> None:
    path = out / f"telemetry-attempt-{attempt_index}.json"
    path.write_text(json.dumps(event, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--request", required=True)
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--provider", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--attempt-index", required=True, type=int)
    ap.add_argument("--credential-profile", required=True)
    args = ap.parse_args()

    request_started_at = _utc_now()
    request = json.loads(Path(args.request).read_text(encoding="utf-8"))
    legacy.verify_request_integrity(request)
    policy = verify_route_binding(request, args.provider, args.model)
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    corpus = evidence_v3.build_corpus(Path("."), request)
    prompt = build_prompt(request, corpus, args.provider, args.model)
    secret_name = required_secret_name(args.provider)
    key = os.environ.get(secret_name, "").strip()
    if not key:
        raise RuntimeError(f"{secret_name} repository secret required")

    raw_path = out / "provider-response-raw.json"
    provider_response: dict | None = None
    review: dict | None = None
    validation: dict | None = None
    provider_call_started_at = _utc_now()
    monotonic_started = time.monotonic()
    try:
        provider_response, review = invoke(
            args.provider,
            key,
            args.model,
            prompt,
            policy,
            raw_path if args.provider == "openrouter" else None,
        )
    except Exception as exc:
        provider_call_completed_at = _utc_now()
        latency_ms = round((time.monotonic() - monotonic_started) * 1000, 3)
        retryable, http_status, classification = classify_attempt_failure(exc)
        event = build_attempt_telemetry(
            request=request,
            provider=args.provider,
            model=args.model,
            credential_profile=args.credential_profile,
            attempt_index=args.attempt_index,
            request_started_at=request_started_at,
            provider_call_started_at=provider_call_started_at,
            first_response_at=provider_call_completed_at if http_status is not None else None,
            provider_call_completed_at=provider_call_completed_at,
            provider_latency_ms=latency_ms,
            outcome="FAILURE",
            retryable=retryable,
            http_status=http_status,
            error_classification=classification,
            error_detail=str(exc),
            policy=policy,
            provider_response=None,
            review=None,
            validation=None,
        )
        _write_attempt_event(out, args.attempt_index, event)
        raise

    provider_call_completed_at = _utc_now()
    latency_ms = round((time.monotonic() - monotonic_started) * 1000, 3)
    # The current adapters return a response as one materialized object. Until an
    # adapter exposes an earlier byte/header timestamp, the first usable response
    # observed by the governed runner is the provider-call completion timestamp.
    first_response_at = provider_call_completed_at

    try:
        validation = validate(review, request, args.provider, args.model)
    except Exception:
        event = build_attempt_telemetry(
            request=request,
            provider=args.provider,
            model=args.model,
            credential_profile=args.credential_profile,
            attempt_index=args.attempt_index,
            request_started_at=request_started_at,
            provider_call_started_at=provider_call_started_at,
            first_response_at=first_response_at,
            provider_call_completed_at=provider_call_completed_at,
            provider_latency_ms=latency_ms,
            outcome="SUCCESS",
            retryable=False,
            http_status=200,
            error_classification=None,
            error_detail=None,
            policy=policy,
            provider_response=provider_response,
            review=review,
            validation={"valid": False},
        )
        _write_attempt_event(out, args.attempt_index, event)
        raise

    event = build_attempt_telemetry(
        request=request,
        provider=args.provider,
        model=args.model,
        credential_profile=args.credential_profile,
        attempt_index=args.attempt_index,
        request_started_at=request_started_at,
        provider_call_started_at=provider_call_started_at,
        first_response_at=first_response_at,
        provider_call_completed_at=provider_call_completed_at,
        provider_latency_ms=latency_ms,
        outcome="SUCCESS",
        retryable=False,
        http_status=200,
        error_classification=None,
        error_detail=None,
        policy=policy,
        provider_response=provider_response,
        review=review,
        validation=validation,
    )
    _write_attempt_event(out, args.attempt_index, event)

    envelope = execution_envelope(request, corpus, args.provider, args.model, provider_response)
    envelope["runner_version"] = "GOV-REVIEWER-SERVING-PROVIDER-PIN-001"
    envelope["materialization_version"] = "GOV-FROZEN-CROSS-COMMIT-EVIDENCE-001"
    envelope["reviewer_slot"] = request["reviewer_slot"]
    envelope["review_execution_policy"] = policy
    envelope["provider_attempt_telemetry_file"] = f"telemetry-attempt-{args.attempt_index}.json"
    if args.provider == "openrouter":
        envelope["requested_serving_provider"] = policy["serving_provider"]
        envelope["returned_serving_provider"] = provider_response.get("provider")
        envelope["provider_fallbacks_allowed"] = False

    for name, obj in [
        ("corpus.json", corpus),
        ("provider-response.json", provider_response),
        ("review.json", review),
        ("validation.json", validation),
        ("execution-envelope.json", envelope),
    ]:
        (out / name).write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if not validation["valid"]:
        raise SystemExit(3)


if __name__ == "__main__":
    main()
