from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import inspect
import json
import unittest

from provider_review_telemetry import (
    aggregate_attempts,
    build_dashboard_data,
    render_provider_table,
    sanitize_error_detail,
    validate_attempt_event,
)


def event(
    *,
    provider: str = "future-provider-x",
    model: str = "future-model-1",
    profile: str = "future-profile",
    attempt: int = 1,
    outcome: str = "SUCCESS",
    retryable: bool = False,
    http_status: int | None = 200,
    error_classification: str | None = None,
    error_detail: str | None = None,
    started: str = "2026-09-09T08:00:00Z",
    first: str | None = "2026-09-09T08:00:01Z",
    completed: str = "2026-09-09T08:00:02Z",
    latency_ms: int = 2000,
    disposition: str | None = "PASS",
    validation_valid: bool | None = True,
    request_id: str = "REV-FUTURE-001",
    candidate: str = "a" * 40,
    slot: str = "R3",
    requested_serving_provider: str | None = None,
    returned_serving_provider: str | None = None,
) -> dict:
    return {
        "schema_version": 1,
        "event_type": "REVIEW_PROVIDER_ATTEMPT",
        "review_request_id": request_id,
        "reviewed_candidate_commit": candidate,
        "reviewer_slot": slot,
        "gateway_provider": provider,
        "model": model,
        "credential_profile": profile,
        "requested_serving_provider": requested_serving_provider,
        "returned_serving_provider": returned_serving_provider,
        "attempt_index": attempt,
        "request_started_at": started,
        "provider_call_started_at": started,
        "first_response_at": first,
        "provider_call_completed_at": completed,
        "provider_latency_ms": latency_ms,
        "attempt_outcome": outcome,
        "retryable": retryable,
        "http_status": http_status,
        "error_classification": error_classification,
        "error_detail": error_detail,
        "semantic_disposition": disposition,
        "validation_valid": validation_valid,
        "authority_effect": "NONE_PENDING_DETERMINISTIC_INGESTION",
    }


class ProviderReviewTelemetryTests(unittest.TestCase):
    def test_tel_01_arbitrary_provider_event_validates(self):
        self.assertEqual("future-provider-x", validate_attempt_event(event())["gateway_provider"])

    def test_tel_02_future_provider_appears_automatically(self):
        data = aggregate_attempts([event()])
        self.assertEqual(["future-provider-x"], [x["provider"] for x in data["providers"]])

    def test_tel_03_two_unknown_providers_not_collapsed(self):
        data = aggregate_attempts([event(provider="alpha-new"), event(provider="beta-new", request_id="REV-B")])
        self.assertEqual({"alpha-new", "beta-new"}, {x["provider"] for x in data["providers"]})

    def test_tel_04_provider_model_profile_are_data_not_renderer_enums(self):
        source = inspect.getsource(render_provider_table)
        for forbidden in ("openrouter", "gemini", "groq", "future-provider-x"):
            self.assertNotIn(forbidden, source.lower())

    def test_tel_05_429_then_success_preserves_retry(self):
        first = event(outcome="FAILURE", retryable=True, http_status=429, error_classification="HTTP_429", disposition=None, validation_valid=None, first="2026-09-09T08:00:00.500000Z", completed="2026-09-09T08:00:01Z", latency_ms=1000)
        second = event(attempt=2, started="2026-09-09T08:00:21Z", first="2026-09-09T08:00:22Z", completed="2026-09-09T08:00:23Z", latency_ms=2000)
        data = aggregate_attempts([first, second])
        review = data["reviews"][0]
        self.assertEqual(2, review["attempt_count"])
        self.assertEqual(1, review["retry_count"])
        self.assertEqual("SUCCESS", review["final_outcome"])
        self.assertEqual([429, 200], [a["http_status"] for a in review["attempts"]])

    def test_tel_06_503_sequence_remains_failed(self):
        rows = [event(attempt=i, outcome="FAILURE", retryable=True, http_status=503, error_classification="HTTP_503", disposition=None, validation_valid=None, first=None, request_id="REV-503") for i in (1, 2, 3)]
        review = aggregate_attempts(rows)["reviews"][0]
        self.assertEqual("FAILURE", review["final_outcome"])
        self.assertEqual(3, review["attempt_count"])

    def test_tel_07_failure_before_response_allows_null_first_response(self):
        row = event(outcome="FAILURE", retryable=False, http_status=None, error_classification="CONNECTION_FAILURE", first=None, disposition=None, validation_valid=None)
        normalized = validate_attempt_event(row)
        self.assertIsNone(normalized["first_response_at"])
        self.assertGreaterEqual(normalized["provider_latency_ms"], 0)

    def test_tel_08_success_requires_first_response_and_nonnegative_latency(self):
        normalized = validate_attempt_event(event())
        self.assertIsNotNone(normalized["first_response_at"])
        self.assertGreaterEqual(normalized["provider_latency_ms"], 0)

    def test_tel_09_attempt_indices_unique_per_review(self):
        with self.assertRaises(ValueError):
            aggregate_attempts([event(), event(model="other")])

    def test_tel_10_secret_like_material_is_sanitized(self):
        text = "Authorization: Bearer sk-super-secret-token"
        clean = sanitize_error_detail(text)
        self.assertNotIn("sk-super-secret-token", clean)
        self.assertNotIn("Bearer sk-", clean)

    def test_tel_11_aggregation_never_keeps_authorization_header(self):
        row = event(outcome="FAILURE", retryable=False, http_status=401, error_classification="HTTP_401", error_detail="Authorization: Bearer abcdef1234567890", disposition=None, validation_valid=None)
        blob = json.dumps(aggregate_attempts([row]))
        self.assertNotIn("abcdef1234567890", blob)

    def test_tel_12_semantics_are_preserved_not_derived_from_latency(self):
        row = event(latency_ms=999999, disposition="CHANGES_REQUIRED", validation_valid=False)
        review = aggregate_attempts([row])["reviews"][0]
        self.assertEqual("CHANGES_REQUIRED", review["semantic_disposition"])
        self.assertFalse(review["validation_valid"])

    def test_tel_13_r1_r2_r3_aggregate_generically(self):
        rows = [event(slot=slot, request_id=f"REV-{slot}") for slot in ("R1", "R2", "R3")]
        data = aggregate_attempts(rows)
        self.assertEqual({"R1", "R2", "R3"}, {x["reviewer_slot"] for x in data["reviews"]})

    def test_tel_14_credential_profiles_remain_distinct(self):
        rows = [event(profile="primary", request_id="REV-A"), event(profile="r3", request_id="REV-B")]
        provider = aggregate_attempts(rows)["providers"][0]
        self.assertEqual(["primary", "r3"], provider["credential_profiles"])

    def test_tel_15_requested_returned_serving_provider_separate(self):
        row = event(requested_serving_provider="deepinfra", returned_serving_provider="DeepInfra")
        normalized = validate_attempt_event(row)
        self.assertEqual("deepinfra", normalized["requested_serving_provider"])
        self.assertEqual("DeepInfra", normalized["returned_serving_provider"])

    def test_tel_16_route_failure_cannot_be_semantic_success(self):
        row = event(outcome="FAILURE", http_status=None, error_classification="SERVING_PROVIDER_MISMATCH", disposition="PASS", validation_valid=True)
        with self.assertRaises(ValueError):
            validate_attempt_event(row)

    def test_tel_17_failed_attempt_stays_visible_after_success(self):
        rows = [event(attempt=1, outcome="FAILURE", retryable=True, http_status=429, error_classification="HTTP_429", disposition=None, validation_valid=None), event(attempt=2)]
        review = aggregate_attempts(rows)["reviews"][0]
        self.assertEqual("FAILURE", review["attempts"][0]["attempt_outcome"])
        self.assertEqual("SUCCESS", review["attempts"][1]["attempt_outcome"])

    def test_tel_18_aggregation_deterministic_under_input_order(self):
        rows = [event(provider="z-provider", request_id="REV-Z"), event(provider="a-provider", request_id="REV-A")]
        self.assertEqual(aggregate_attempts(rows), aggregate_attempts(list(reversed(rows))))

    def test_tel_19_dashboard_builder_includes_arbitrary_provider(self):
        dashboard = build_dashboard_data([event(provider="provider-never-seen-before")])
        self.assertIn("provider-never-seen-before", json.dumps(dashboard))

    def test_tel_20_renderer_does_not_name_future_provider_in_source(self):
        self.assertNotIn("future-provider-x", inspect.getsource(render_provider_table).lower())
        html = render_provider_table(build_dashboard_data([event()]))
        self.assertIn("future-provider-x", html)

    def test_tel_21_telemetry_does_not_modify_semantic_values(self):
        row = event(disposition="BOUNDED_PASS", validation_valid=True)
        before = deepcopy(row)
        aggregate_attempts([row])
        self.assertEqual(before, row)

    def test_tel_22_telemetry_failure_has_no_authority_upgrade(self):
        row = event(outcome="FAILURE", retryable=False, http_status=None, error_classification="TELEMETRY_IO_FAILURE", disposition=None, validation_valid=None)
        review = aggregate_attempts([row])["reviews"][0]
        self.assertEqual("NONE_PENDING_DETERMINISTIC_INGESTION", review["authority_effect"])
        self.assertEqual("FAILURE", review["final_outcome"])

    def test_tel_23_profile_visible_secret_absent(self):
        row = event(profile="openrouter-r3", error_detail="Bearer secret-value-123456")
        data = build_dashboard_data([row])
        html = render_provider_table(data)
        self.assertIn("openrouter-r3", html)
        self.assertNotIn("secret-value-123456", json.dumps(data) + html)

    def test_tel_24_current_openrouter_route_needs_no_aggregator_special_case(self):
        row = event(provider="openrouter", model="nvidia/nemotron-3-ultra-550b-a55b", profile="r3", requested_serving_provider="deepinfra", returned_serving_provider="DeepInfra")
        data = aggregate_attempts([row])
        self.assertEqual("openrouter", data["providers"][0]["provider"])
        source = inspect.getsource(aggregate_attempts).lower()
        self.assertNotIn("openrouter", source)
        self.assertNotIn("deepinfra", source)


if __name__ == "__main__":
    unittest.main()
