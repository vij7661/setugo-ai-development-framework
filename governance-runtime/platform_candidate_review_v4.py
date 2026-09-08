from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import platform_candidate_review as legacy
import platform_candidate_review_v2 as evidence_v2
import platform_candidate_review_v3 as v3

SUPPORTED_PROVIDERS = {"gemini", "groq", "openrouter"}
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def verify_provider_binding(request: dict, provider: str, model: str) -> None:
    if provider not in SUPPORTED_PROVIDERS:
        raise ValueError(f"unsupported authenticated review provider: {provider!r}")
    required = request.get("required_reviewer")
    if not isinstance(required, dict):
        raise ValueError("required_reviewer missing")
    if required.get("provider") != provider:
        raise ValueError("trigger provider does not match frozen ReviewRequest provider")
    exact = required.get("model")
    model_class = required.get("model_class")
    if isinstance(exact, str) and exact and exact != model:
        raise ValueError("trigger model does not match frozen ReviewRequest model")
    if not ((isinstance(exact, str) and exact) or (isinstance(model_class, str) and model_class)):
        raise ValueError("frozen ReviewRequest has no reviewer model constraint")


def required_secret_name(provider: str) -> str:
    if provider == "gemini":
        return "GEMINI_API_KEY"
    if provider == "groq":
        return "GROQ_API_KEY"
    if provider == "openrouter":
        return "OPENROUTER_API_KEY"
    raise ValueError(f"unsupported authenticated review provider: {provider!r}")


def _extract_openai_compatible_review(body: dict, provider_label: str) -> dict:
    choices = body.get("choices") or []
    if not choices:
        raise RuntimeError(f"{provider_label} response missing choices")
    message = choices[0].get("message") or {}
    text = message.get("content")
    if not isinstance(text, str) or not text.strip():
        raise RuntimeError(f"{provider_label} response missing assistant content")
    try:
        review = json.loads(text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{provider_label} assistant content was not strict JSON") from exc
    if not isinstance(review, dict):
        raise RuntimeError("review JSON must be object")
    return review


def _invoke_openrouter(key: str, model: str, prompt: str):
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
        "max_tokens": 16384,
    }
    req = Request(
        OPENROUTER_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/vij7661/setugo-ai-development-framework",
            "X-Title": "Setugo Governed Platform Review",
            "User-Agent": "setugo-governance-platform-review/4.0",
        },
        method="POST",
    )
    try:
        with urlopen(req, timeout=300) as response:
            body = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        raise RuntimeError(f"OpenRouter HTTP {exc.code}: " + exc.read().decode("utf-8", errors="replace")[:4000]) from exc
    except URLError as exc:
        raise RuntimeError(f"OpenRouter connection failed: {exc.reason}") from exc
    returned_model = body.get("model")
    if returned_model != model:
        raise RuntimeError(f"OpenRouter returned model mismatch: requested={model!r} returned={returned_model!r}")
    review = _extract_openai_compatible_review(body, "OpenRouter")
    return body, review


def invoke(provider: str, key: str, model: str, prompt: str):
    if provider in {"gemini", "groq"}:
        return v3.invoke(provider, key, model, prompt)
    if provider == "openrouter":
        return _invoke_openrouter(key, model, prompt)
    raise ValueError(f"unsupported authenticated review provider: {provider!r}")


def build_prompt(request: dict, corpus: dict, provider: str, model: str) -> str:
    # Keep v3 semantic prompt contract unchanged.
    return v3.build_prompt(request, corpus, provider, model)


def validate(review: dict, request: dict, provider: str, model: str) -> dict:
    # Keep v3 deterministic semantic validation unchanged.
    return v3.validate(review, request, provider, model)


def execution_envelope(request: dict, corpus: dict, provider: str, model: str, provider_response: dict) -> dict:
    envelope = {
        "schema_version": 4,
        "review_request_id": request["review_request_id"],
        "reviewed_artifact_commit": request["artifact"]["commit"],
        "review_class": "PLATFORM_AUTO_API_REVIEW",
        "transport": "AUTOMATIC_API",
        "provider": provider,
        "model": model,
        "provider_api_authenticated": True,
        "remote_model_identity_cryptographically_proven": False,
        "request_hash": request.get("request_hash"),
        "corpus_sha256": corpus["corpus_sha256"],
        "materialization_version": "GOV-EVIDENCE-MATERIALIZATION-001",
        "runner_version": "GOV-OPENROUTER-REVIEW-RUNNER-001",
        "evidence_ref_count": corpus["evidence_ref_count"],
        "materialized_evidence_count": corpus["materialized_evidence_count"],
        "authority_effect": "NONE_PENDING_DETERMINISTIC_INGESTION",
    }
    if provider == "openrouter":
        envelope["remote_returned_model"] = provider_response.get("model")
        envelope["openrouter_upstream_provider"] = provider_response.get("provider")
        envelope["provider_usage"] = provider_response.get("usage")
    return envelope


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--request", required=True)
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--provider", required=True)
    ap.add_argument("--model", required=True)
    args = ap.parse_args()

    request = json.loads(Path(args.request).read_text(encoding="utf-8"))
    legacy.verify_request_integrity(request)
    verify_provider_binding(request, args.provider, args.model)
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    corpus = evidence_v2.build_corpus(Path("."), request)
    prompt = build_prompt(request, corpus, args.provider, args.model)
    secret_name = required_secret_name(args.provider)
    key = os.environ.get(secret_name, "").strip()
    if not key:
        raise RuntimeError(f"{secret_name} repository secret required")

    provider_response, review = invoke(args.provider, key, args.model, prompt)
    validation = validate(review, request, args.provider, args.model)
    envelope = execution_envelope(request, corpus, args.provider, args.model, provider_response)

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
