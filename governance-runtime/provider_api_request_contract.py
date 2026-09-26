"""Provider-facing API request contract preservation helpers.

This module defines a provider-neutral semantic fingerprint. It does not perform
network I/O and does not grant execution authority.
"""
from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any, Mapping

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
    "x-api-key",
    "api-key",
    "proxy-authorization",
})


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
    forbidden = keys & FORBIDDEN_PROVIDER_KEYS
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
    if not isinstance(out["timeout_ms"], int) or out["timeout_ms"] <= 0:
        raise ValueError("timeout_ms must be a positive integer")
    if not isinstance(out["retry_policy"], Mapping):
        raise ValueError("retry_policy must be an object")
    return out


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
    """Optional helper for adapter tests: never fingerprint secret header values."""
    out: dict[str, str] = {}
    for name, value in headers.items():
        low = str(name).lower()
        if low in SECRET_HEADER_NAMES:
            continue
        out[str(name)] = str(value)
    return out
