from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import time
import uuid
from hashlib import sha256
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

import platform_candidate_review as legacy
from api_call_gate import (
    build_request_hash,
    decision as api_gate_decision,
)

DIGITS = re.compile(r"^[0-9]+$")


def _canon(value):
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _sha_bytes(data: bytes) -> str:
    return sha256(data).hexdigest()


def _repo_name() -> str:
    repo = os.environ.get("GITHUB_REPOSITORY", "").strip()
    if not repo or "/" not in repo:
        raise RuntimeError("GITHUB_REPOSITORY required for ci_run evidence materialization")
    return repo


def _fetch_ci_run(run_id: str) -> dict:
    if not isinstance(run_id, str) or not DIGITS.fullmatch(run_id):
        raise ValueError("ci_run ref must be numeric string")
    repo = _repo_name()
    url = f"https://api.github.com/repos/{repo}/actions/runs/{run_id}"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "setugo-governance-evidence-materializer/2.0",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = Request(url, headers=headers, method="GET")
    try:
        with urlopen(req, timeout=60) as response:
            data = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        raise RuntimeError(f"ci_run evidence fetch failed HTTP {exc.code}") from exc
    except URLError as exc:
        raise RuntimeError(f"ci_run evidence fetch failed: {exc.reason}") from exc
    if str(data.get("id")) != run_id:
        raise RuntimeError("ci_run response id mismatch")
    return data


def _materialize_file(root: Path, candidate: str, ref_value: str) -> dict:
    if not isinstance(ref_value, str) or not ref_value.strip():
        raise ValueError("file evidence ref required")
    path = ref_value.strip()
    cp = subprocess.run(
        ["git", "show", f"{candidate}:{path}"],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if cp.returncode:
        raise RuntimeError(f"candidate evidence file unavailable: {path}")
    text = cp.stdout.decode("utf-8")
    return {
        "type": "file",
        "ref": path,
        "candidate_sha": candidate,
        "bytes_utf8": len(cp.stdout),
        "sha256": _sha_bytes(cp.stdout),
        "content": text,
    }


def _materialize_history(ref_value: str) -> dict:
    if not isinstance(ref_value, str) or not ref_value.strip():
        raise ValueError("history evidence ref required")
    text = ref_value.strip()
    raw = text.encode("utf-8")
    return {
        "type": "history",
        "ref": text,
        "authority_class": "FROZEN_REQUEST_TEXT_NON_AUTHORITATIVE",
        "bytes_utf8": len(raw),
        "sha256": _sha_bytes(raw),
        "content": text,
    }


def _materialize_ci_run(candidate: str, ref_value: str) -> dict:
    data = _fetch_ci_run(ref_value)
    if data.get("head_sha") != candidate:
        raise RuntimeError("ci_run head_sha does not match reviewed candidate")
    materialized = {
        "id": data.get("id"),
        "name": data.get("name"),
        "workflow_id": data.get("workflow_id"),
        "event": data.get("event"),
        "status": data.get("status"),
        "conclusion": data.get("conclusion"),
        "head_branch": data.get("head_branch"),
        "head_sha": data.get("head_sha"),
        "run_attempt": data.get("run_attempt"),
        "created_at": data.get("created_at"),
        "updated_at": data.get("updated_at"),
    }
    raw = _canon(materialized)
    return {
        "type": "ci_run",
        "ref": ref_value,
        "candidate_sha": candidate,
        "authority_class": "EXECUTION_EVIDENCE_NOT_SEMANTIC_AUTHORITY",
        "sha256": _sha_bytes(raw),
        "content": materialized,
    }


def materialize_evidence_ref(root: Path, candidate: str, ref: dict) -> dict:
    if not isinstance(ref, dict):
        raise ValueError("evidence ref must be object")
    ref_type = ref.get("type")
    ref_value = ref.get("ref")
    if ref_type == "file":
        return _materialize_file(root, candidate, ref_value)
    if ref_type == "history":
        return _materialize_history(ref_value)
    if ref_type == "ci_run":
        return _materialize_ci_run(candidate, ref_value)
    raise ValueError(f"unsupported evidence ref type: {ref_type!r}")


def build_corpus(root: Path, request: dict) -> dict:
    candidate = request["artifact"]["commit"]
    legacy.require_commit(root, candidate, "candidate")
    refs = request.get("evidence_refs", [])
    if not isinstance(refs, list):
        raise ValueError("evidence_refs must be list")
    evidence = [materialize_evidence_ref(root, candidate, ref) for ref in refs]
    if len(evidence) != len(refs):
        raise RuntimeError("evidence materialization count mismatch")
    base = legacy.git(root, "merge-base", "origin/main", candidate).strip()
    diff = legacy.git(
        root,
        "diff",
        "--no-ext-diff",
        base,
        candidate,
        "--",
        "governance-runtime",
        ".github/workflows/live-conversation-governance.yml",
        ".github/workflows/governance-candidate-platform-review.yml",
    )
    corpus = {
        "schema_version": 2,
        "materialization_version": "GOV-EVIDENCE-MATERIALIZATION-001",
        "review_request": request,
        "base_commit": base,
        "candidate_commit": candidate,
        "candidate_diff": diff,
        "evidence_artifacts": evidence,
        "evidence_ref_count": len(refs),
        "materialized_evidence_count": len(evidence),
        "posture": (
            "Assume false-green. Treat green CI, memory, prior PASS labels, consensus, "
            "and history text as non-semantic authority unless independently supported "
            "by governed evidence."
        ),
    }
    corpus["corpus_sha256"] = sha256(_canon(corpus)).hexdigest()
    return corpus


def _gemini_payload(prompt: str) -> dict:
    return {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.0,
            "maxOutputTokens": 16384,
            "responseMimeType": "application/json",
        },
    }


def _provider_request_id(headers) -> str | None:
    for name in (
        "x-request-id",
        "x-goog-request-id",
        "request-id",
        "x-cloud-trace-context",
    ):
        value = headers.get(name)
        if value:
            return str(value)
    return None


def _invoke_gemini(key: str, model: str, payload: dict) -> dict:
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{quote(model, safe='')}:generateContent"
    )
    body = _canon(payload)
    req = Request(
        url,
        data=body,
        headers={
            "x-goog-api-key": key,
            "content-type": "application/json",
            "user-agent": "setugo-governance-platform-review/2.1",
        },
        method="POST",
    )
    started = time.monotonic()
    try:
        with urlopen(req, timeout=180) as response:
            raw = response.read()
            status = int(response.status)
            headers = response.headers
    except HTTPError as exc:
        raw = exc.read()
        return {
            "dispatch_state": "FAILED_AFTER_DISPATCH",
            "http_status": int(exc.code),
            "raw_body": raw,
            "provider_request_id": _provider_request_id(exc.headers),
            "latency_ms": int((time.monotonic() - started) * 1000),
            "error": f"Gemini HTTP {exc.code}",
        }
    except URLError as exc:
        return {
            "dispatch_state": "OUTCOME_UNKNOWN",
            "http_status": None,
            "raw_body": b"",
            "provider_request_id": None,
            "latency_ms": int((time.monotonic() - started) * 1000),
            "error": f"Gemini connection failed: {exc.reason}",
        }

    try:
        parsed = json.loads(raw.decode("utf-8"))
    except Exception:
        parsed = None
    return {
        "dispatch_state": "SUCCEEDED",
        "http_status": status,
        "raw_body": raw,
        "parsed_body": parsed,
        "provider_request_id": _provider_request_id(headers),
        "latency_ms": int((time.monotonic() - started) * 1000),
        "error": None,
    }


def _extract_review(provider_body: dict) -> tuple[dict | None, bool, bool]:
    if not isinstance(provider_body, dict):
        return None, False, False
    candidate = (provider_body.get("candidates") or [{}])[0]
    if candidate.get("finishReason") != "STOP":
        return None, False, False
    text = "".join(
        str(part.get("text", ""))
        for part in ((candidate.get("content") or {}).get("parts") or [])
        if isinstance(part, dict)
    )
    if not text.strip():
        return None, False, True
    try:
        review = json.loads(text)
    except Exception:
        return None, True, False
    return (review if isinstance(review, dict) else None), True, isinstance(review, dict)


def _load_json(path: str | None, default):
    if not path:
        return default
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--request", required=True)
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--phase", required=True)
    ap.add_argument(
        "--api-policy",
        default="governance-runtime/api-call-policy-v1.json",
    )
    ap.add_argument("--api-history")
    ap.add_argument("--attempt-no", type=int, default=1)
    args = ap.parse_args()

    request = json.loads(Path(args.request).read_text(encoding="utf-8"))
    legacy.verify_request_integrity(request)
    root = Path(".")
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    corpus = build_corpus(root, request)
    prompt = legacy.build_prompt(request, corpus, args.model)
    payload = _gemini_payload(prompt)
    payload_bytes = _canon(payload)
    policy = _load_json(args.api_policy, {})
    history = _load_json(args.api_history, [])

    call_id = f"{request['review_request_id']}:attempt:{args.attempt_no}:{uuid.uuid4().hex[:12]}"
    api_envelope = {
        "schema_version": 1,
        "call_id": call_id,
        "intent_id": request["review_request_id"],
        "attempt_no": args.attempt_no,
        "transport": "AUTOMATIC_API",
        "call_class": "REVIEW_API",
        "authority_effect": "EVIDENCE_ONLY",
        "phase": args.phase,
        "governance_policy_id": policy.get("policy_id"),
        "governance_policy_hash": policy.get("policy_hash"),
        "provider": "gemini",
        "model": args.model,
        "endpoint_origin": "https://generativelanguage.googleapis.com",
        "credential_ref": "env:GEMINI_API_KEY",
        "request_payload_sha256": _sha_bytes(payload_bytes),
        "context_bundle_sha256": corpus["corpus_sha256"],
        "secrets_in_payload": False,
        "request_metadata": {
            "purpose": "independent-platform-candidate-review",
            "review_request_id": request["review_request_id"],
        },
        "retry_policy": {
            "max_attempts": 3,
            "reuse_intent_id": True,
            "blind_retry_after_outcome_unknown": False,
            "retryable_http_statuses": [429, 500, 502, 503, 504],
        },
        "fallback_policy": {
            "allowed_targets": [{"provider": "gemini", "model": args.model}],
            "silent_provider_or_model_substitution": False,
            "stop_on_first_qualified_success": True,
        },
        "candidate_commit": request["artifact"]["commit"],
        "review_request_id": request["review_request_id"],
        "expected_response_contract": {
            "required_fields": [
                "review_request_id",
                "reviewed_artifact_commit",
                "reviewer",
                "disposition",
                "findings",
                "evidence_assessment",
                "independence_attestation",
                "review_coverage",
            ],
        },
    }
    api_envelope["envelope_hash"] = build_request_hash(api_envelope)
    preflight = api_gate_decision(api_envelope, policy, history=history)
    (out / "api-preflight.json").write_text(
        json.dumps(preflight, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (out / "api-request-envelope.json").write_text(
        json.dumps(api_envelope, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    if preflight["result"] != "API_CALL_READY":
        raise SystemExit(4)

    key = os.environ.get("GEMINI_API_KEY", "")
    if not key:
        raise RuntimeError("GEMINI_API_KEY repository secret required")

    provider_call = _invoke_gemini(key, args.model, payload)
    provider_body = provider_call.get("parsed_body")
    review, assistant_content_present, response_schema_valid = _extract_review(provider_body)
    observed_fields = sorted(review.keys()) if isinstance(review, dict) else []

    receipt = {
        "schema_version": 1,
        "call_id": api_envelope["call_id"],
        "intent_id": api_envelope["intent_id"],
        "attempt_no": api_envelope["attempt_no"],
        "request_envelope_hash": api_envelope["envelope_hash"],
        "adapter_identity_assurance": "PROVIDER_ADAPTER_AUTHENTICATED",
        "actual_provider": "gemini",
        "actual_model": args.model,
        "dispatch_state": provider_call["dispatch_state"],
        "http_status": provider_call["http_status"],
        "response_payload_sha256": (
            _sha_bytes(provider_call["raw_body"])
            if provider_call["raw_body"]
            else None
        ),
        "response_schema_valid": response_schema_valid,
        "assistant_content_present": assistant_content_present,
        "observed_response_fields": observed_fields,
        "review_request_id": (
            review.get("review_request_id") if isinstance(review, dict) else None
        ),
        "candidate_commit": (
            review.get("reviewed_artifact_commit") if isinstance(review, dict) else None
        ),
        "secrets_redacted": True,
        "provider_request_id": provider_call["provider_request_id"],
        "adapter_dispatch_id": api_envelope["call_id"],
        "latency_ms": provider_call["latency_ms"],
    }
    gate_receipt = api_gate_decision(
        api_envelope,
        policy,
        receipt=receipt,
        history=history,
    )
    (out / "api-receipt.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (out / "api-receipt-validation.json").write_text(
        json.dumps(gate_receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    provider_output = provider_body if isinstance(provider_body, dict) else {
        "raw_response_sha256": receipt["response_payload_sha256"],
        "parseable_json": False,
    }
    if gate_receipt["result"] != "API_RESULT_QUALIFIED" or not isinstance(review, dict):
        (out / "provider-response.json").write_text(
            json.dumps(provider_output, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        raise SystemExit(5)

    validation = legacy.validate(review, request, args.model)
    execution_envelope = {
        "schema_version": 3,
        "review_request_id": request["review_request_id"],
        "reviewed_artifact_commit": request["artifact"]["commit"],
        "review_class": "PLATFORM_AUTO_API_REVIEW",
        "transport": "AUTOMATIC_API",
        "provider": "gemini",
        "model": args.model,
        "provider_api_authenticated": True,
        "adapter_identity_assurance": "PROVIDER_ADAPTER_AUTHENTICATED",
        "remote_model_identity_cryptographically_proven": False,
        "request_hash": request.get("request_hash"),
        "corpus_sha256": corpus["corpus_sha256"],
        "api_request_envelope_hash": api_envelope["envelope_hash"],
        "api_receipt_gate_result": gate_receipt["result"],
        "materialization_version": "GOV-EVIDENCE-MATERIALIZATION-001",
        "evidence_ref_count": corpus["evidence_ref_count"],
        "materialized_evidence_count": corpus["materialized_evidence_count"],
        "authority_effect": "NONE_PENDING_DETERMINISTIC_INGESTION",
    }

    for name, obj in [
        ("corpus.json", corpus),
        ("provider-response.json", provider_output),
        ("review.json", review),
        ("validation.json", validation),
        ("execution-envelope.json", execution_envelope),
    ]:
        (out / name).write_text(
            json.dumps(obj, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    if not validation["valid"]:
        raise SystemExit(3)


if __name__ == "__main__":
    main()
