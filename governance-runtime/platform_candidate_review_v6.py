from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import platform_candidate_review as legacy
import platform_candidate_evidence_v3 as evidence_v3
import platform_candidate_review_v5 as v5

SUPPORTED_PROVIDERS = set(v5.SUPPORTED_PROVIDERS)
verify_provider_binding = v5.verify_provider_binding
required_secret_name = v5.required_secret_name
build_prompt = v5.build_prompt
validate = v5.validate
execution_envelope = v5.execution_envelope
invoke = v5.invoke


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

    corpus = evidence_v3.build_corpus(Path("."), request)
    prompt = build_prompt(request, corpus, args.provider, args.model)
    secret_name = required_secret_name(args.provider)
    key = os.environ.get(secret_name, "").strip()
    if not key:
        raise RuntimeError(f"{secret_name} repository secret required")

    raw_path = out / "provider-response-raw.json"
    provider_response, review = invoke(
        args.provider,
        key,
        args.model,
        prompt,
        raw_path if args.provider == "openrouter" else None,
    )
    validation = validate(review, request, args.provider, args.model)
    envelope = execution_envelope(request, corpus, args.provider, args.model, provider_response)
    envelope["runner_version"] = "GOV-FROZEN-CROSS-COMMIT-EVIDENCE-001"
    envelope["materialization_version"] = "GOV-FROZEN-CROSS-COMMIT-EVIDENCE-001"

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
