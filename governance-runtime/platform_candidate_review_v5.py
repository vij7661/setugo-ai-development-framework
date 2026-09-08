from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import platform_candidate_review as legacy
import platform_candidate_review_v2 as evidence_v2
import platform_candidate_review_v4 as v4

SUPPORTED_PROVIDERS = set(v4.SUPPORTED_PROVIDERS)
OPENROUTER_URL = v4.OPENROUTER_URL

verify_provider_binding = v4.verify_provider_binding
required_secret_name = v4.required_secret_name
build_prompt = v4.build_prompt
validate = v4.validate
execution_envelope = v4.execution_envelope


def _provider_error_message(body: dict) -> str | None:
    err = body.get("error")
    if err is None:
        return None
    if isinstance(err, dict):
        code = err.get("code")
        typ = err.get("type")
        msg = err.get("message")
        return f"OpenRouter provider error code={code!r} type={typ!r} message={msg!r}"
    return f"OpenRouter provider error: {err!r}"


def _invoke_openrouter(key: str, model: str, prompt: str, raw_response_path: Path | None = None):
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
            "User-Agent": "setugo-governance-platform-review/5.0",
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
    review = v4._extract_openai_compatible_review(body, "OpenRouter")
    return body, review


def invoke(provider: str, key: str, model: str, prompt: str, raw_response_path: Path | None = None):
    if provider == "openrouter":
        return _invoke_openrouter(key, model, prompt, raw_response_path)
    return v4.invoke(provider, key, model, prompt)


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

    raw_path = out / "provider-response-raw.json"
    provider_response, review = invoke(args.provider, key, args.model, prompt, raw_path if args.provider == "openrouter" else None)
    validation = validate(review, request, args.provider, args.model)
    envelope = execution_envelope(request, corpus, args.provider, args.model, provider_response)
    envelope["runner_version"] = "GOV-OPENROUTER-ERROR-OBSERVABILITY-001"

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
