from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

import platform_candidate_review as legacy
import platform_candidate_review_v2 as evidence_v2

SUPPORTED_PROVIDERS = {"gemini", "groq"}


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
    raise ValueError(f"unsupported authenticated review provider: {provider!r}")


def build_prompt(request: dict, corpus: dict, provider: str, model: str) -> str:
    dims = [d["id"] for d in request["required_review_dimensions"] if d.get("mandatory")]
    attestation = legacy.expected_attestation(request)
    shape = {
        "review_request_id": request["review_request_id"],
        "reviewed_artifact_commit": request["artifact"]["commit"],
        "reviewer": {"provider": provider, "model": model},
        "disposition": "PASS|BOUNDED_PASS|FAIL|NOT_TESTED|INSUFFICIENT_EVIDENCE|CHANGES_REQUIRED",
        "findings": [{
            "id": "F1", "severity": "LOW|MEDIUM|HIGH|CRITICAL", "title": "title",
            "evidence": "specific file/function evidence", "impact": "impact", "required_change": "change or null"
        }],
        "evidence_assessment": "assessment",
        "independence_attestation": attestation,
        "review_coverage": [{
            "dimension_id": dims[0] if dims else "dimension",
            "status": "TESTED_SUPPORTED|TESTED_DEFECT_FOUND|CONTRADICTED|NOT_TESTED|UNAVAILABLE|INACCESSIBLE|INSUFFICIENT",
            "evidence": ["specific refs"], "assessment": "assessment"
        }],
    }
    if request.get("blind_review_required") is True:
        role = "You are the independent adversarial R2 reviewer. You are blind to proposer conclusions and must independently reconstruct the evidence."
    else:
        role = "You are the R3 adversarial review-of-review critic. The prior R2 review is intentionally visible. You are NOT independent of R2: challenge it, search for anchoring or missed defects, and do not defer to its PASS/FAIL label."
    return (
        role
        + " Assume false-green. Inspect the exact candidate and supplied evidence. Return strict JSON only; no markdown and no private chain-of-thought. "
        + "Every mandatory dimension must be present exactly once. PASS requires every mandatory dimension TESTED_SUPPORTED and no MEDIUM/HIGH/CRITICAL finding. "
        + "Reviewer content cannot establish API provenance; the platform execution envelope does.\nREQUEST:\n"
        + json.dumps(request, sort_keys=True)
        + "\nOUTPUT SHAPE:\n"
        + json.dumps(shape, sort_keys=True)
        + "\nCORPUS:\n"
        + json.dumps(corpus, sort_keys=True)
    )


def _invoke_gemini(key: str, model: str, prompt: str):
    return legacy.invoke(key, model, prompt)


def _invoke_groq(key: str, model: str, prompt: str):
    url = "https://api.groq.com/openai/v1/chat/completions"
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
        "max_completion_tokens": 16384,
        "response_format": {"type": "json_object"},
    }
    req = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "User-Agent": "setugo-governance-platform-review/3.0",
        },
        method="POST",
    )
    try:
        with urlopen(req, timeout=180) as response:
            body = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        raise RuntimeError(f"Groq HTTP {exc.code}: " + exc.read().decode("utf-8", errors="replace")[:1000]) from exc
    except URLError as exc:
        raise RuntimeError(f"Groq connection failed: {exc.reason}") from exc
    choices = body.get("choices") or []
    if not choices:
        raise RuntimeError("Groq response missing choices")
    message = choices[0].get("message") or {}
    text = message.get("content")
    if not isinstance(text, str) or not text.strip():
        raise RuntimeError("Groq response missing assistant content")
    review = json.loads(text)
    if not isinstance(review, dict):
        raise RuntimeError("review JSON must be object")
    return body, review


def invoke(provider: str, key: str, model: str, prompt: str):
    if provider == "gemini":
        return _invoke_gemini(key, model, prompt)
    if provider == "groq":
        return _invoke_groq(key, model, prompt)
    raise ValueError(f"unsupported authenticated review provider: {provider!r}")


def validate(review: dict, request: dict, provider: str, model: str) -> dict:
    errors = []
    reqid = request["review_request_id"]
    candidate = request["artifact"]["commit"]
    mandatory = [d["id"] for d in request["required_review_dimensions"] if d.get("mandatory")]
    if review.get("review_request_id") != reqid:
        errors.append("review_request_id mismatch")
    if review.get("reviewed_artifact_commit") != candidate:
        errors.append("reviewed_artifact_commit mismatch")
    disp = review.get("disposition")
    if disp not in legacy.ALLOWED_DISPOSITIONS:
        errors.append("invalid disposition")
    rv = review.get("reviewer")
    if not isinstance(rv, dict) or rv.get("provider") != provider or rv.get("model") != model:
        errors.append("reviewer content identity disagrees with execution envelope")
    if review.get("independence_attestation") != legacy.expected_attestation(request):
        errors.append("review independence/review-of-review attestation mismatch")
    findings = review.get("findings")
    if not isinstance(findings, list):
        errors.append("findings must be list")
        findings = []
    blocking = False
    for finding in findings:
        if not isinstance(finding, dict):
            errors.append("finding must be object")
            continue
        severity = finding.get("severity")
        if severity not in {"LOW", "MEDIUM", "HIGH", "CRITICAL"}:
            errors.append("invalid finding severity")
        if severity in legacy.BLOCKING:
            blocking = True
        if not str(finding.get("evidence", "")).strip():
            errors.append("finding evidence required")
    coverage = review.get("review_coverage")
    if not isinstance(coverage, list):
        errors.append("review_coverage must be list")
        coverage = []
    by = {}
    for row in coverage:
        if not isinstance(row, dict):
            errors.append("coverage row must be object")
            continue
        did = row.get("dimension_id")
        if did in by:
            errors.append(f"duplicate dimension {did}")
            continue
        by[did] = row
        if row.get("status") not in legacy.ALLOWED_STATUSES:
            errors.append(f"invalid coverage status {did}")
        if row.get("status") in {"TESTED_SUPPORTED", "TESTED_DEFECT_FOUND", "CONTRADICTED"}:
            ev = row.get("evidence")
            if not isinstance(ev, list) or not any(str(x).strip() for x in ev):
                errors.append(f"tested dimension evidence required {did}")
    missing = [d for d in mandatory if d not in by]
    extras = [d for d in by if d not in mandatory]
    if missing:
        errors.append("missing mandatory dimensions: " + ",".join(missing))
    if extras:
        errors.append("unexpected dimensions: " + ",".join(extras))
    statuses = {d: by[d].get("status") for d in mandatory if d in by}
    all_supported = len(statuses) == len(mandatory) and all(v == "TESTED_SUPPORTED" for v in statuses.values())
    incomplete = any(v in {"NOT_TESTED", "UNAVAILABLE", "INACCESSIBLE", "INSUFFICIENT"} for v in statuses.values())
    defective = any(v in {"TESTED_DEFECT_FOUND", "CONTRADICTED"} for v in statuses.values())
    if disp == "PASS" and (not all_supported or blocking):
        errors.append("PASS contradicts coverage/findings")
    if disp == "BOUNDED_PASS" and (blocking or defective or incomplete):
        errors.append("BOUNDED_PASS contradicts mandatory coverage/findings")
    if disp in {"FAIL", "CHANGES_REQUIRED"} and not (defective or blocking):
        errors.append("negative disposition lacks defect evidence")
    if disp in {"NOT_TESTED", "INSUFFICIENT_EVIDENCE"} and not incomplete:
        errors.append("insufficient disposition lacks incomplete coverage")
    return {
        "valid": not errors,
        "errors": errors,
        "effective_disposition": disp if not errors else "INVALID_REVIEW_EVIDENCE",
        "all_mandatory_dimensions_supported": all_supported if not errors else False,
    }


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
    root = Path(".")
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    corpus = evidence_v2.build_corpus(root, request)
    prompt = build_prompt(request, corpus, args.provider, args.model)
    secret_name = required_secret_name(args.provider)
    key = os.environ.get(secret_name, "").strip()
    if not key:
        raise RuntimeError(f"{secret_name} repository secret required")
    provider_response, review = invoke(args.provider, key, args.model, prompt)
    validation = validate(review, request, args.provider, args.model)
    envelope = {
        "schema_version": 3,
        "review_request_id": request["review_request_id"],
        "reviewed_artifact_commit": request["artifact"]["commit"],
        "review_class": "PLATFORM_AUTO_API_REVIEW",
        "transport": "AUTOMATIC_API",
        "provider": args.provider,
        "model": args.model,
        "provider_api_authenticated": True,
        "remote_model_identity_cryptographically_proven": False,
        "request_hash": request.get("request_hash"),
        "corpus_sha256": corpus["corpus_sha256"],
        "materialization_version": "GOV-EVIDENCE-MATERIALIZATION-001",
        "evidence_ref_count": corpus["evidence_ref_count"],
        "materialized_evidence_count": corpus["materialized_evidence_count"],
        "authority_effect": "NONE_PENDING_DETERMINISTIC_INGESTION",
    }
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
