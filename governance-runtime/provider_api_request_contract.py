"""Provider-facing API request contract preservation helpers.

This module defines a provider-neutral semantic fingerprint. It does not perform
network I/O and does not grant execution authority.
"""
from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any, Mapping
from urllib.parse import quote

ALLOWED_CHANGE_CLASSES = frozenset({
    "CONTROL_PLANE_ONLY",
    "EVIDENCE_ONLY",
    "API_ADMISSION_EFFECT",
    "API_REQUEST_SCHEMA_CHANGE",
    "API_EXECUTION_BEHAVIOR_CHANGE",
})

GOVERNANCE_ONLY_CLASSES = frozenset({
    "CONTROL_PLANE_ONLY",
    "EVIDENCE_ONLY",
    "API_ADMISSION_EFFECT",
})

PROVIDER_REQUEST_KEYS = frozenset({
    "provider",
    "endpoint",
    "method",
    "model",
    "messages",
    "provider_parameters",
    "timeout_ms",
    "retry_policy",
})

FORBIDDEN_PROVIDER_KEYS = frozenset({
    "governance_review_blob",
    "reviewer_decision",
    "candidate_sha",
    "authority_effect",
    "policy_snapshot",
    "evidence_refs",
    "authorization_receipt",
})

SECRET_HEADER_NAMES = frozenset({
    "authorization",
    "x_api_key", "api_key", "proxy_authorization", "x_goog_api_key",
    "token", "access_token", "secret", "password", "pat", "personal_access_token",
})


def _policy_key(value: Any) -> str:
    return str(value).strip().lower().replace("-", "_")


def _canon(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def validate_change_classes(classes: set[str] | frozenset[str]) -> None:
    if not classes:
        raise ValueError("at least one API change class is required")
    unknown = set(classes) - ALLOWED_CHANGE_CLASSES
    if unknown:
        raise ValueError(f"unknown API change class: {sorted(unknown)}")


def canonical_provider_request(request: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(request, Mapping):
        raise ValueError("provider request must be an object")
    keys = set(request)
    forbidden = {_policy_key(key) for key in keys} & {_policy_key(key) for key in FORBIDDEN_PROVIDER_KEYS}
    if forbidden:
        raise ValueError(f"governance metadata leaked into provider request: {sorted(forbidden)}")
    unknown = keys - PROVIDER_REQUEST_KEYS
    if unknown:
        raise ValueError(f"unknown provider request fields: {sorted(unknown)}")
    missing = PROVIDER_REQUEST_KEYS - keys
    if missing:
        raise ValueError(f"missing provider request fields: {sorted(missing)}")

    out = deepcopy(dict(request))
    if out["method"] != "POST":
        raise ValueError("provider request method must be POST")
    for field in ("provider", "endpoint", "model"):
        if not isinstance(out[field], str) or not out[field].strip():
            raise ValueError(f"{field} must be a non-empty string")
    if not isinstance(out["messages"], list) or not out["messages"]:
        raise ValueError("messages must be a non-empty list")
    if not isinstance(out["provider_parameters"], Mapping):
        raise ValueError("provider_parameters must be an object")
    _reject_forbidden_structured_keys(out["provider_parameters"])
    for message in out["messages"]:
        if not isinstance(message, Mapping):
            raise ValueError("message must be an object")
        # Natural-language strings are deliberately opaque. Structured message,
        # tool, and adapter metadata remains governed and is scanned recursively.
        structured = {key: value for key, value in message.items() if key != "content" or not isinstance(value, str)}
        _reject_forbidden_structured_keys(structured)
    if not isinstance(out["timeout_ms"], int) or out["timeout_ms"] <= 0:
        raise ValueError("timeout_ms must be a positive integer")
    if not isinstance(out["retry_policy"], Mapping):
        raise ValueError("retry_policy must be an object")
    _reject_forbidden_structured_keys(out["retry_policy"])
    return out


def _reject_forbidden_structured_keys(value: Any) -> None:
    if isinstance(value, Mapping):
        forbidden = {_policy_key(key) for key in FORBIDDEN_PROVIDER_KEYS}
        leaked = {_policy_key(key) for key in value if _policy_key(key) in forbidden}
        secrets = {_policy_key(key) for key in value if _policy_key(key) in SECRET_HEADER_NAMES}
        if leaked or secrets:
            raise ValueError(f"forbidden structured metadata entered provider request: {sorted(leaked | secrets)}")
        for child in value.values():
            _reject_forbidden_structured_keys(child)
    elif isinstance(value, (list, tuple)):
        for child in value:
            _reject_forbidden_structured_keys(child)


def gemini_adapter_semantic_request(*, model: str, prompt: str, timeout_ms: int = 180000) -> dict[str, Any]:
    """Exact non-secret semantic projection used by the real Gemini adapter."""
    return canonical_provider_request({
        "provider": "gemini",
        "endpoint": f"/v1beta/models/{quote(model, safe='')}:generateContent",
        "method": "POST",
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "provider_parameters": {
            "temperature": 0.0,
            "maxOutputTokens": 16384,
            "responseMimeType": "application/json",
            "stream": False,
        },
        "timeout_ms": timeout_ms,
        "retry_policy": {"max_attempts": 1, "retry_on": []},
    })


def gemini_wire_request_from_semantic(semantic: Mapping[str, Any]) -> dict[str, Any]:
    """Derive the real Gemini wire request solely from the canonical projection."""
    spec = canonical_provider_request(semantic)
    if spec["provider"] != "gemini" or spec["retry_policy"] != {"max_attempts": 1, "retry_on": []}:
        raise ValueError("unsupported Gemini semantic execution contract")
    params = dict(spec["provider_parameters"])
    if params.pop("stream", None) is not False:
        raise ValueError("Gemini review path must be non-streaming")
    messages = spec["messages"]
    if len(messages) != 1 or messages[0].get("role") != "user" or not isinstance(messages[0].get("content"), str):
        raise ValueError("Gemini review path requires one user prompt")
    return {
        "url": "https://generativelanguage.googleapis.com" + spec["endpoint"],
        "method": spec["method"],
        "payload": {"contents": [{"role": "user", "parts": [{"text": messages[0]["content"]}]}], "generationConfig": params},
        "timeout_seconds": spec["timeout_ms"] // 1000,
        "retry_policy": dict(spec["retry_policy"]),
    }


def assert_gemini_wire_matches_semantic(semantic: Mapping[str, Any], wire: Mapping[str, Any]) -> None:
    if dict(wire) != gemini_wire_request_from_semantic(semantic):
        raise ValueError("Gemini wire request drifted from canonical semantic projection")


def provider_request_fingerprint(request: Mapping[str, Any]) -> str:
    canonical = canonical_provider_request(request)
    return hashlib.sha256(_canon(canonical)).hexdigest()


def assert_governance_change_preserves_provider_request(
    before: Mapping[str, Any],
    after: Mapping[str, Any],
    *,
    change_classes: set[str] | frozenset[str],
) -> str:
    validate_change_classes(change_classes)
    before_fp = provider_request_fingerprint(before)
    after_fp = provider_request_fingerprint(after)
    if set(change_classes) <= GOVERNANCE_ONLY_CLASSES and before_fp != after_fp:
        raise ValueError("governance-only remediation changed provider request semantics")
    return after_fp


def sanitize_semantic_headers(headers: Mapping[str, str]) -> dict[str, str]:
    """Normalize non-secret semantic headers; authentication is excluded."""
    out: dict[str, str] = {}
    for name, value in headers.items():
        low = _policy_key(name)
        if low in SECRET_HEADER_NAMES:
            continue
        out[low] = " ".join(str(value).strip().split())
    return out
