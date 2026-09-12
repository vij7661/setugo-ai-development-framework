#!/usr/bin/env python3
"""Deterministic governance gate for outbound API calls and returned receipts.

This module never performs a network request. It validates:
1) the exact call envelope against a separately supplied governance policy;
2) dispatch sequencing/retry/fallback history; and
3) the trusted-adapter receipt after dispatch.

A network 2xx or model/provider string inside a response is never sufficient by
itself to create governed evidence.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Mapping, Sequence
from urllib.parse import urlparse

SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
SAFE_TRANSPORTS = {"AUTOMATIC_API", "USER_INITIATED_API"}
CALL_CLASSES = {
    "REVIEW_API",
    "RESEARCH_API",
    "READ_ONLY_API",
    "MUTATING_API",
    "EXTERNAL_EFFECT_API",
}
AUTHORITY_EFFECTS = {"NONE_EVIDENCE_ONLY", "EVIDENCE_ONLY", "AUTHORITY_AFFECTING"}
RECEIPT_STATES = {
    "SUCCEEDED",
    "FAILED_BEFORE_DISPATCH",
    "FAILED_AFTER_DISPATCH",
    "OUTCOME_UNKNOWN",
}
SECRET_KEY_PATTERN = re.compile(
    r"(api[_-]?key|authorization|access[_-]?token|refresh[_-]?token|password|client[_-]?secret|secret)",
    re.I,
)
PLACEHOLDER_VALUES = {"<redacted>", "REDACTED", "***", "<secret-ref>"}
NON_MUTATING_CLASSES = {"REVIEW_API", "RESEARCH_API", "READ_ONLY_API"}

def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def canonical_hash(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()

def hash_without_field(value: Mapping[str, Any], field: str) -> str:
    material = deepcopy(dict(value))
    material.pop(field, None)
    return canonical_hash(material)

def _has_literal_secret(value: Any, path: str = "") -> list[str]:
    bad: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else str(key)
            if SECRET_KEY_PATTERN.search(str(key)):
                if isinstance(child, str) and child and child not in PLACEHOLDER_VALUES:
                    bad.append(child_path)
                elif child not in (None, "", False) and not isinstance(child, str):
                    bad.append(child_path)
            bad.extend(_has_literal_secret(child, child_path))
    elif isinstance(value, list):
        for idx, child in enumerate(value):
            bad.extend(_has_literal_secret(child, f"{path}[{idx}]"))
    return bad

def _https_origin(value: str) -> bool:
    try:
        parsed = urlparse(value)
        return parsed.scheme == "https" and bool(parsed.netloc) and not parsed.username and not parsed.password
    except ValueError:
        return False

def build_policy_hash(policy: Mapping[str, Any]) -> str:
    return hash_without_field(policy, "policy_hash")

def verify_policy(policy: Mapping[str, Any]) -> tuple[bool, list[str]]:
    errors: list[str] = []
    if policy.get("schema_version") != 1:
        errors.append("API_POLICY_SCHEMA_INVALID")
    if not isinstance(policy.get("policy_id"), str) or not policy.get("policy_id"):
        errors.append("API_POLICY_ID_MISSING")
    supplied = policy.get("policy_hash")
    if not isinstance(supplied, str) or not SHA256.fullmatch(supplied):
        errors.append("API_POLICY_HASH_MISSING")
    elif supplied != build_policy_hash(policy):
        errors.append("API_POLICY_HASH_MISMATCH")
    phase_rules = policy.get("phase_rules")
    if not isinstance(phase_rules, Mapping) or not phase_rules:
        errors.append("API_POLICY_PHASE_RULES_MISSING")
    return not errors, errors

def _valid_retry_policy(policy: Mapping[str, Any]) -> tuple[bool, str]:
    max_attempts = policy.get("max_attempts")
    if not isinstance(max_attempts, int) or max_attempts < 1 or max_attempts > 8:
        return False, "retry max_attempts must be 1..8"
    if policy.get("reuse_intent_id") is not True:
        return False, "retry policy must reuse intent_id"
    if policy.get("blind_retry_after_outcome_unknown") is not False:
        return False, "blind retry after outcome-unknown must be disabled"
    statuses = policy.get("retryable_http_statuses", [])
    if not isinstance(statuses, list) or any(not isinstance(x, int) for x in statuses):
        return False, "retryable_http_statuses invalid"
    return True, "retry policy valid"

def build_request_hash(envelope: Mapping[str, Any]) -> str:
    return hash_without_field(envelope, "envelope_hash")

def _validate_phase_policy(envelope: Mapping[str, Any], policy: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if envelope.get("governance_policy_id") != policy.get("policy_id"):
        errors.append("API_POLICY_ID_BINDING_MISMATCH")
    if envelope.get("governance_policy_hash") != policy.get("policy_hash"):
        errors.append("API_POLICY_HASH_BINDING_MISMATCH")
    phase = envelope.get("phase")
    rules = policy.get("phase_rules", {})
    rule = rules.get(phase) if isinstance(rules, Mapping) else None
    if not isinstance(phase, str) or not isinstance(rule, Mapping):
        errors.append("API_PHASE_POLICY_MISSING")
        return errors
    allowed_classes = rule.get("allowed_call_classes")
    if not isinstance(allowed_classes, list) or envelope.get("call_class") not in allowed_classes:
        errors.append("API_PHASE_POLICY_PROHIBITS_CALL")
    allowed_transports = rule.get("allowed_transports", sorted(SAFE_TRANSPORTS))
    if not isinstance(allowed_transports, list) or envelope.get("transport") not in allowed_transports:
        errors.append("API_PHASE_POLICY_PROHIBITS_TRANSPORT")
    if rule.get("manual_review_only") is True and envelope.get("call_class") == "REVIEW_API":
        errors.append("API_PHASE_POLICY_MANUAL_REVIEW_ONLY")
    return errors

def validate_preflight(envelope: Mapping[str, Any], policy: Mapping[str, Any]) -> tuple[bool, list[str]]:
    errors: list[str] = []
    policy_ok, policy_errors = verify_policy(policy)
    errors.extend(policy_errors)
    if envelope.get("schema_version") != 1:
        errors.append("API_ENVELOPE_SCHEMA_INVALID")
    for key in ("call_id", "intent_id", "provider", "model", "credential_ref", "phase"):
        if not isinstance(envelope.get(key), str) or not envelope.get(key):
            errors.append(f"API_ENVELOPE_FIELD_MISSING:{key}")
    if envelope.get("transport") not in SAFE_TRANSPORTS:
        errors.append("API_TRANSPORT_INVALID")
    if envelope.get("call_class") not in CALL_CLASSES:
        errors.append("API_CALL_CLASS_INVALID")
    if envelope.get("authority_effect") not in AUTHORITY_EFFECTS:
        errors.append("API_AUTHORITY_EFFECT_INVALID")
    origin = envelope.get("endpoint_origin")
    if not isinstance(origin, str) or not _https_origin(origin):
        errors.append("API_ENDPOINT_ORIGIN_INVALID")
    payload_hash = envelope.get("request_payload_sha256")
    if not isinstance(payload_hash, str) or not SHA256.fullmatch(payload_hash):
        errors.append("API_REQUEST_PAYLOAD_HASH_INVALID")
    context_hash = envelope.get("context_bundle_sha256")
    if not isinstance(context_hash, str) or not SHA256.fullmatch(context_hash):
        errors.append("API_CONTEXT_BUNDLE_HASH_INVALID")
    if envelope.get("secrets_in_payload") is not False:
        errors.append("API_SECRET_PAYLOAD_DECLARATION_INVALID")
    literal_secrets = _has_literal_secret(envelope.get("request_metadata", {}))
    if literal_secrets:
        errors.append("API_SECRET_LITERAL_PRESENT:" + ",".join(sorted(literal_secrets)))

    if policy_ok:
        errors.extend(_validate_phase_policy(envelope, policy))

    retry = envelope.get("retry_policy")
    if not isinstance(retry, Mapping):
        errors.append("API_RETRY_POLICY_MISSING")
    else:
        ok, reason = _valid_retry_policy(retry)
        if not ok:
            errors.append("API_RETRY_POLICY_INVALID:" + reason)

    attempt = envelope.get("attempt_no")
    if not isinstance(attempt, int) or attempt < 1:
        errors.append("API_ATTEMPT_INVALID")
    elif isinstance(retry, Mapping) and isinstance(retry.get("max_attempts"), int) and attempt > retry["max_attempts"]:
        errors.append("API_ATTEMPT_EXCEEDS_POLICY")

    fallback = envelope.get("fallback_policy")
    if not isinstance(fallback, Mapping):
        errors.append("API_FALLBACK_POLICY_MISSING")
    else:
        allowed = fallback.get("allowed_targets")
        if not isinstance(allowed, list) or not allowed:
            errors.append("API_FALLBACK_TARGETS_INVALID")
        else:
            current = {"provider": envelope.get("provider"), "model": envelope.get("model")}
            if current not in allowed:
                errors.append("API_TARGET_NOT_IN_FALLBACK_POLICY")
        if fallback.get("silent_provider_or_model_substitution") is not False:
            errors.append("API_SILENT_FALLBACK_MUST_BE_DISABLED")
        if fallback.get("stop_on_first_qualified_success") is not True:
            errors.append("API_FALLBACK_STOP_RULE_INVALID")

    if envelope.get("call_class") == "REVIEW_API":
        commit = envelope.get("candidate_commit")
        if not isinstance(commit, str) or not SHA40.fullmatch(commit):
            errors.append("API_REVIEW_CANDIDATE_BINDING_INVALID")
        if not isinstance(envelope.get("review_request_id"), str) or not envelope.get("review_request_id"):
            errors.append("API_REVIEW_REQUEST_ID_MISSING")
        if envelope.get("authority_effect") == "AUTHORITY_AFFECTING":
            errors.append("API_REVIEW_CALL_CANNOT_SELF_DECLARE_AUTHORITY")

    if envelope.get("call_class") in {"MUTATING_API", "EXTERNAL_EFFECT_API"}:
        idem = envelope.get("idempotency_key")
        if not isinstance(idem, str) or not idem:
            errors.append("API_IDEMPOTENCY_KEY_REQUIRED")

    expected = envelope.get("expected_response_contract")
    if not isinstance(expected, Mapping):
        errors.append("API_RESPONSE_CONTRACT_MISSING")
    else:
        fields = expected.get("required_fields")
        if not isinstance(fields, list) or not all(isinstance(x, str) and x for x in fields):
            errors.append("API_RESPONSE_CONTRACT_FIELDS_INVALID")

    supplied_hash = envelope.get("envelope_hash")
    if not isinstance(supplied_hash, str) or not SHA256.fullmatch(supplied_hash):
        errors.append("API_ENVELOPE_HASH_MISSING")
    elif supplied_hash != build_request_hash(envelope):
        errors.append("API_ENVELOPE_HASH_MISMATCH")

    return not errors, errors

def validate_dispatch_history(
    envelope: Mapping[str, Any],
    history: Sequence[Mapping[str, Any]],
) -> tuple[bool, list[str]]:
    errors: list[str] = []
    relevant = [x for x in history if x.get("intent_id") == envelope.get("intent_id")]
    if any(
        x.get("gate_result") == "API_RESULT_QUALIFIED"
        and x.get("dispatch_state") == "SUCCEEDED"
        for x in relevant
    ):
        errors.append("API_FALLBACK_AFTER_QUALIFIED_SUCCESS")
    if relevant:
        attempts = [x.get("attempt_no") for x in relevant if isinstance(x.get("attempt_no"), int)]
        if attempts:
            expected = max(attempts) + 1
            if envelope.get("attempt_no") != expected:
                errors.append(f"API_ATTEMPT_SEQUENCE_INVALID:expected={expected}")
        last = max(
            (x for x in relevant if isinstance(x.get("attempt_no"), int)),
            key=lambda x: x["attempt_no"],
            default=None,
        )
        if last and last.get("dispatch_state") == "OUTCOME_UNKNOWN":
            resolution = envelope.get("previous_outcome_resolution")
            if envelope.get("call_class") in {"MUTATING_API", "EXTERNAL_EFFECT_API"}:
                if resolution != "PROVIDER_CONFIRMED_NOT_APPLIED":
                    errors.append("API_OUTCOME_UNKNOWN_REQUIRES_RECONCILIATION")
            elif resolution not in {
                "PROVIDER_CONFIRMED_NOT_APPLIED",
                "SAFE_DUPLICATE_ALLOWED_BY_CALL_CLASS",
            }:
                errors.append("API_OUTCOME_UNKNOWN_RETRY_NOT_JUSTIFIED")
    elif envelope.get("attempt_no") != 1:
        errors.append("API_FIRST_ATTEMPT_MUST_BE_ONE")
    return not errors, errors

def validate_receipt(
    envelope: Mapping[str, Any],
    receipt: Mapping[str, Any],
    policy: Mapping[str, Any],
) -> tuple[bool, list[str]]:
    _, pre_errors = validate_preflight(envelope, policy)
    errors = list(pre_errors)
    if receipt.get("schema_version") != 1:
        errors.append("API_RECEIPT_SCHEMA_INVALID")
    if receipt.get("call_id") != envelope.get("call_id"):
        errors.append("API_RECEIPT_CALL_ID_MISMATCH")
    if receipt.get("intent_id") != envelope.get("intent_id"):
        errors.append("API_RECEIPT_INTENT_ID_MISMATCH")
    if receipt.get("attempt_no") != envelope.get("attempt_no"):
        errors.append("API_RECEIPT_ATTEMPT_MISMATCH")
    if receipt.get("request_envelope_hash") != envelope.get("envelope_hash"):
        errors.append("API_RECEIPT_REQUEST_HASH_MISMATCH")
    if receipt.get("adapter_identity_assurance") != "PROVIDER_ADAPTER_AUTHENTICATED":
        errors.append("API_PROVIDER_IDENTITY_UNAUTHENTICATED")
    if receipt.get("actual_provider") != envelope.get("provider"):
        errors.append("API_PROVIDER_IDENTITY_MISMATCH")
    if receipt.get("actual_model") != envelope.get("model"):
        errors.append("API_MODEL_IDENTITY_MISMATCH")
    state = receipt.get("dispatch_state")
    if state not in RECEIPT_STATES:
        errors.append("API_DISPATCH_STATE_INVALID")
    if state == "OUTCOME_UNKNOWN":
        errors.append("API_OUTCOME_UNKNOWN_CANNOT_QUALIFY")
    elif state in {"FAILED_BEFORE_DISPATCH", "FAILED_AFTER_DISPATCH"}:
        errors.append("API_FAILED_CALL_CANNOT_QUALIFY")

    if state == "SUCCEEDED":
        status = receipt.get("http_status")
        if not isinstance(status, int) or not (200 <= status < 300):
            errors.append("API_HTTP_STATUS_NOT_SUCCESS")
        response_hash = receipt.get("response_payload_sha256")
        if not isinstance(response_hash, str) or not SHA256.fullmatch(response_hash):
            errors.append("API_RESPONSE_HASH_INVALID")
        if receipt.get("response_schema_valid") is not True:
            errors.append("API_RESPONSE_SCHEMA_INVALID")
        if receipt.get("assistant_content_present") is not True:
            errors.append("API_RESPONSE_CONTENT_MISSING")
        expected = envelope.get("expected_response_contract", {})
        required_fields = expected.get("required_fields", []) if isinstance(expected, Mapping) else []
        observed = receipt.get("observed_response_fields")
        if not isinstance(observed, list):
            errors.append("API_RESPONSE_FIELDS_MISSING")
        else:
            missing = sorted(set(required_fields) - set(observed))
            if missing:
                errors.append("API_RESPONSE_REQUIRED_FIELDS_MISSING:" + ",".join(missing))

    if envelope.get("call_class") == "REVIEW_API":
        if receipt.get("review_request_id") != envelope.get("review_request_id"):
            errors.append("API_REVIEW_REQUEST_BINDING_MISMATCH")
        if receipt.get("candidate_commit") != envelope.get("candidate_commit"):
            errors.append("API_REVIEW_CANDIDATE_BINDING_MISMATCH")

    if receipt.get("secrets_redacted") is not True:
        errors.append("API_RECEIPT_SECRET_REDACTION_INVALID")
    provider_request_id = receipt.get("provider_request_id")
    adapter_dispatch_id = receipt.get("adapter_dispatch_id")
    if not (
        (isinstance(provider_request_id, str) and provider_request_id)
        or (isinstance(adapter_dispatch_id, str) and adapter_dispatch_id)
    ):
        errors.append("API_DISPATCH_CORRELATION_ID_MISSING")
    if not isinstance(receipt.get("latency_ms"), int) or receipt.get("latency_ms") < 0:
        errors.append("API_LATENCY_INVALID")

    return not errors, errors

def decision(
    envelope: Mapping[str, Any],
    policy: Mapping[str, Any],
    receipt: Mapping[str, Any] | None = None,
    history: Sequence[Mapping[str, Any]] = (),
) -> dict[str, Any]:
    pre_ok, pre_errors = validate_preflight(envelope, policy)
    hist_ok, hist_errors = validate_dispatch_history(envelope, history)
    if receipt is None:
        errors = pre_errors + hist_errors
        return {
            "schema_version": 1,
            "phase": "PREFLIGHT",
            "result": "API_CALL_READY" if pre_ok and hist_ok else "API_CALL_BLOCKED",
            "errors": errors,
        }
    receipt_ok, receipt_errors = validate_receipt(envelope, receipt, policy)
    errors = receipt_errors + hist_errors
    return {
        "schema_version": 1,
        "phase": "RECEIPT",
        "result": "API_RESULT_QUALIFIED" if receipt_ok and hist_ok else "API_RESULT_REJECTED",
        "errors": errors,
    }

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--envelope", required=True)
    parser.add_argument("--policy", required=True)
    parser.add_argument("--receipt")
    parser.add_argument("--history")
    parser.add_argument("--report")
    args = parser.parse_args()
    envelope = json.loads(Path(args.envelope).read_text(encoding="utf-8"))
    policy = json.loads(Path(args.policy).read_text(encoding="utf-8"))
    receipt = json.loads(Path(args.receipt).read_text(encoding="utf-8")) if args.receipt else None
    history = json.loads(Path(args.history).read_text(encoding="utf-8")) if args.history else []
    result = decision(envelope, policy, receipt, history)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.report:
        Path(args.report).write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if result["result"] in {"API_CALL_READY", "API_RESULT_QUALIFIED"} else 2

if __name__ == "__main__":
    raise SystemExit(main())
