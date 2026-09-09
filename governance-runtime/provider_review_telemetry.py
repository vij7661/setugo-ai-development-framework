"""Provider-neutral governed reviewer telemetry.

Provider adapters emit normalized attempt records. This layer knows no provider
names; it validates, sanitizes, aggregates and renders without changing review
or authority semantics.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import html
import re
from typing import Any, Iterable, Mapping

SCHEMA_VERSION = 1
EVENT_TYPE = "REVIEW_PROVIDER_ATTEMPT"
AUTHORITY_EFFECT = "NONE_PENDING_DETERMINISTIC_INGESTION"
OUTCOMES = frozenset({"SUCCESS", "FAILURE"})
SLOTS = frozenset({"R1", "R2", "R3"})
PROMOTABLE_DISPOSITIONS = frozenset({"PASS", "BOUNDED_PASS"})
_SHA40 = re.compile(r"^[0-9a-f]{40}$")
_AUTH_BEARER = re.compile(r"(?i)(authorization\s*:\s*bearer\s+)([^\s,;]+)")
_BEARER = re.compile(r"(?i)(bearer\s+)([^\s,;]+)")
_SK_TOKEN = re.compile(r"(?i)\bsk-[A-Za-z0-9._-]{6,}\b")
_API_ASSIGNMENT = re.compile(r"(?i)\b(api[_-]?key|token|secret)\s*[=:]\s*([^\s,;]+)")


def sanitize_error_detail(value: str | None, *, limit: int = 2000) -> str | None:
    if value is None:
        return None
    text = str(value)
    text = _AUTH_BEARER.sub(r"\1[REDACTED]", text)
    text = _BEARER.sub(r"\1[REDACTED]", text)
    text = _SK_TOKEN.sub("[REDACTED]", text)
    text = _API_ASSIGNMENT.sub(lambda m: f"{m.group(1)}=[REDACTED]", text)
    return text[:limit]


def _secret_like_identity(value: str) -> bool:
    low = value.lower()
    return any(x in low for x in ("authorization:", "bearer ", "api_key=", "apikey=", "secret=")) or low.startswith("sk-")


def _parse_utc(value: Any, field: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a UTC ISO-8601 string")
    try:
        dt = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field} must be ISO-8601") from exc
    if dt.tzinfo is None or dt.utcoffset() is None or dt.utcoffset().total_seconds() != 0:
        raise ValueError(f"{field} must be UTC")
    return dt.astimezone(timezone.utc)


def _required_string(row: Mapping[str, Any], field: str) -> str:
    value = row.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} required")
    return value.strip()


def validate_attempt_event(value: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError("telemetry event must be an object")
    row = deepcopy(dict(value))
    if row.get("schema_version") != SCHEMA_VERSION or row.get("event_type") != EVENT_TYPE:
        raise ValueError("invalid telemetry schema/event type")

    request_id = _required_string(row, "review_request_id")
    candidate = _required_string(row, "reviewed_candidate_commit")
    if not _SHA40.fullmatch(candidate):
        raise ValueError("reviewed_candidate_commit must be a lowercase 40-character SHA")
    slot = _required_string(row, "reviewer_slot")
    if slot not in SLOTS:
        raise ValueError("reviewer_slot must be R1, R2, or R3")
    provider = _required_string(row, "gateway_provider")
    model = _required_string(row, "model")
    profile = _required_string(row, "credential_profile")
    if any(_secret_like_identity(x) for x in (provider, model, profile)):
        raise ValueError("provider/model/credential identity contains secret-like material")

    index = row.get("attempt_index")
    if not isinstance(index, int) or isinstance(index, bool) or index <= 0:
        raise ValueError("attempt_index must be a positive integer")
    request_started = _parse_utc(row.get("request_started_at"), "request_started_at")
    provider_started = _parse_utc(row.get("provider_call_started_at"), "provider_call_started_at")
    completed = _parse_utc(row.get("provider_call_completed_at"), "provider_call_completed_at")
    first_raw = row.get("first_response_at")
    first_response = None if first_raw is None else _parse_utc(first_raw, "first_response_at")
    if provider_started < request_started or completed < provider_started:
        raise ValueError("invalid telemetry timestamp ordering")
    if first_response is not None and not (provider_started <= first_response <= completed):
        raise ValueError("first_response_at outside provider call interval")

    latency = row.get("provider_latency_ms")
    if not isinstance(latency, (int, float)) or isinstance(latency, bool) or latency < 0:
        raise ValueError("provider_latency_ms must be nonnegative")
    outcome = row.get("attempt_outcome")
    if outcome not in OUTCOMES or not isinstance(row.get("retryable"), bool):
        raise ValueError("invalid attempt outcome/retryable")
    http_status = row.get("http_status")
    if http_status is not None and (not isinstance(http_status, int) or isinstance(http_status, bool) or not 100 <= http_status <= 599):
        raise ValueError("http_status invalid")
    if outcome == "SUCCESS" and first_response is None:
        raise ValueError("successful provider attempt requires first_response_at")

    disposition = row.get("semantic_disposition")
    validation_valid = row.get("validation_valid")
    if validation_valid is not None and not isinstance(validation_valid, bool):
        raise ValueError("validation_valid must be boolean or null")
    if outcome == "FAILURE" and (disposition in PROMOTABLE_DISPOSITIONS or validation_valid is True):
        raise ValueError("failed provider attempt cannot carry promotable semantic success")
    if row.get("authority_effect") != AUTHORITY_EFFECT:
        raise ValueError("telemetry may not change authority effect")

    for field in ("requested_serving_provider", "returned_serving_provider"):
        identity = row.get(field)
        if identity is not None:
            if not isinstance(identity, str) or not identity.strip() or _secret_like_identity(identity):
                raise ValueError(f"{field} invalid")
            row[field] = identity.strip()

    row.update(
        review_request_id=request_id,
        reviewed_candidate_commit=candidate,
        reviewer_slot=slot,
        gateway_provider=provider,
        model=model,
        credential_profile=profile,
        error_detail=sanitize_error_detail(row.get("error_detail")),
    )
    return row


def _review_key(row: Mapping[str, Any]) -> tuple[str, str, str]:
    # Routing metadata belongs to attempts. It must not create a new review
    # execution identity and thereby permit duplicate attempt indices.
    return (str(row["review_request_id"]), str(row["reviewed_candidate_commit"]), str(row["reviewer_slot"]))


def _attempt_counts_by_review(rows: Iterable[Mapping[str, Any]]) -> dict[tuple[str, str, str], int]:
    counts: dict[tuple[str, str, str], int] = {}
    for row in rows:
        key = _review_key(row)
        counts[key] = counts.get(key, 0) + 1
    return counts


def aggregate_attempts(events: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    rows = [validate_attempt_event(x) for x in events]
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(_review_key(row), []).append(row)

    reviews: list[dict[str, Any]] = []
    for key in sorted(grouped):
        attempts = sorted(grouped[key], key=lambda x: x["attempt_index"])
        indices = [x["attempt_index"] for x in attempts]
        if len(indices) != len(set(indices)):
            raise ValueError("attempt_index must be unique within one review execution")
        final = attempts[-1]
        successes = [x for x in attempts if x["attempt_outcome"] == "SUCCESS"]
        start_dt = min(_parse_utc(x["request_started_at"], "request_started_at") for x in attempts)
        end_dt = max(_parse_utc(x["provider_call_completed_at"], "provider_call_completed_at") for x in attempts)
        reviews.append({
            "review_request_id": key[0],
            "reviewed_candidate_commit": key[1],
            "reviewer_slot": key[2],
            "provider": final["gateway_provider"],
            "model": final["model"],
            "credential_profile": final["credential_profile"],
            "attempt_count": len(attempts),
            "retry_count": max(0, len(attempts) - 1),
            "first_attempt_start": min(x["request_started_at"] for x in attempts),
            "first_successful_response_at": successes[0].get("first_response_at") if successes else None,
            "completion_time": max(x["provider_call_completed_at"] for x in attempts),
            "total_elapsed_latency_ms": max(0, int(round((end_dt - start_dt).total_seconds() * 1000))),
            "final_outcome": final["attempt_outcome"],
            "final_error_classification": final.get("error_classification") if final["attempt_outcome"] == "FAILURE" else None,
            "semantic_disposition": final.get("semantic_disposition"),
            "validation_valid": final.get("validation_valid"),
            "authority_effect": final["authority_effect"],
            "attempts": attempts,
        })

    provider_rows: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        provider_rows.setdefault(row["gateway_provider"], []).append(row)
    providers: list[dict[str, Any]] = []
    for provider in sorted(provider_rows):
        attempts = provider_rows[provider]
        review_ids = {_review_key(x) for x in attempts}
        successes = [x for x in attempts if x["attempt_outcome"] == "SUCCESS"]
        failures = [x for x in attempts if x["attempt_outcome"] == "FAILURE"]
        latest = max(attempts, key=lambda x: (_parse_utc(x["provider_call_completed_at"], "provider_call_completed_at"), x["review_request_id"], x["attempt_index"]))
        providers.append({
            "provider": provider,
            "models": sorted({x["model"] for x in attempts}),
            "credential_profiles": sorted({x["credential_profile"] for x in attempts}),
            "review_count": len(review_ids),
            "attempt_count": len(attempts),
            "success_count": len(successes),
            "failure_count": len(failures),
            "retry_count": sum(max(0, count - 1) for count in _attempt_counts_by_review(attempts).values()),
            "average_successful_provider_latency_ms": round(sum(float(x["provider_latency_ms"]) for x in successes) / len(successes), 3) if successes else None,
            "latest_event_time": latest["provider_call_completed_at"],
            "latest_outcome": latest["attempt_outcome"],
            "latest_error_classification": latest.get("error_classification"),
        })

    return {
        "schema_version": 1,
        "summary_type": "PROVIDER_REVIEW_TELEMETRY_SUMMARY",
        "event_count": len(rows),
        "reviews": reviews,
        "providers": providers,
        "authority_effect": AUTHORITY_EFFECT,
    }


def build_dashboard_data(events: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    aggregate = aggregate_attempts(events)
    return {
        "schema_version": 1,
        "data_type": "PROVIDER_REVIEW_TELEMETRY_DASHBOARD",
        "providers": deepcopy(aggregate["providers"]),
        "reviews": deepcopy(aggregate["reviews"]),
        "event_count": aggregate["event_count"],
        "authority_effect": AUTHORITY_EFFECT,
    }


def render_provider_table(data: Mapping[str, Any]) -> str:
    providers = data.get("providers") if isinstance(data, Mapping) else []
    if not isinstance(providers, list):
        providers = []
    parts = ["<table><thead><tr><th>Provider</th><th>Models</th><th>Credential profiles</th><th>Reviews</th><th>Attempts</th><th>Success</th><th>Failure</th><th>Retries</th><th>Avg success latency ms</th><th>Latest</th></tr></thead><tbody>"]
    for row in providers:
        if not isinstance(row, Mapping):
            continue
        values = [
            row.get("provider"),
            ", ".join(str(x) for x in (row.get("models") or [])),
            ", ".join(str(x) for x in (row.get("credential_profiles") or [])),
            row.get("review_count"), row.get("attempt_count"), row.get("success_count"),
            row.get("failure_count"), row.get("retry_count"),
            row.get("average_successful_provider_latency_ms"), row.get("latest_event_time"),
        ]
        parts.append("<tr>" + "".join(f"<td>{html.escape('' if v is None else str(v))}</td>" for v in values) + "</tr>")
    parts.append("</tbody></table>")
    return "".join(parts)
