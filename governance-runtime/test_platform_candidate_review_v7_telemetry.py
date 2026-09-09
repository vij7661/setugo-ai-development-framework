from __future__ import annotations

from pathlib import Path
import inspect
import unittest

import platform_candidate_review_v7 as v7


class V7TelemetryIntegrationTests(unittest.TestCase):
    def test_v7_builds_success_attempt_event_without_secret(self):
        request = {
            "review_request_id": "REV-TEL-001",
            "reviewer_slot": "R3",
            "artifact": {"commit": "a" * 40},
        }
        event = v7.build_attempt_telemetry(
            request=request,
            provider="future-provider-x",
            model="future-model",
            credential_profile="r3",
            attempt_index=2,
            request_started_at="2026-09-09T08:00:00Z",
            provider_call_started_at="2026-09-09T08:00:01Z",
            first_response_at="2026-09-09T08:00:02Z",
            provider_call_completed_at="2026-09-09T08:00:03Z",
            provider_latency_ms=2000,
            outcome="SUCCESS",
            retryable=False,
            http_status=200,
            error_classification=None,
            error_detail=None,
            policy={"serving_provider": "future-serving"},
            provider_response={"provider": "Future Serving"},
            review={"disposition": "PASS"},
            validation={"valid": True},
        )
        self.assertEqual("future-provider-x", event["gateway_provider"])
        self.assertEqual("r3", event["credential_profile"])
        self.assertEqual("future-serving", event["requested_serving_provider"])
        self.assertEqual("Future Serving", event["returned_serving_provider"])
        self.assertNotIn("api_key", str(event).lower())

    def test_v7_failure_classifier_is_provider_neutral(self):
        retryable, status, classification = v7.classify_attempt_failure(RuntimeError("HTTP 429: overloaded"))
        self.assertTrue(retryable)
        self.assertEqual(429, status)
        self.assertEqual("HTTP_429", classification)
        source = inspect.getsource(v7.classify_attempt_failure).lower()
        for provider in ("openrouter", "gemini", "groq"):
            self.assertNotIn(provider, source)

    def test_v7_route_mismatch_classified_without_semantic_success(self):
        retryable, status, classification = v7.classify_attempt_failure(RuntimeError("serving provider mismatch"))
        self.assertFalse(retryable)
        self.assertIsNone(status)
        self.assertEqual("SERVING_PROVIDER_MISMATCH", classification)

    def test_review_workflow_passes_attempt_and_credential_profile(self):
        workflow = Path("../.github/workflows/governance-candidate-platform-review.yml").read_text(encoding="utf-8")
        self.assertIn('--attempt-index "$attempt"', workflow)
        self.assertIn('--credential-profile "$REVIEW_CREDENTIAL_PROFILE"', workflow)
        self.assertIn("telemetry-attempt-", workflow)
        self.assertIn("provider-review-telemetry.json", workflow)

    def test_v7_cli_declares_attempt_and_profile(self):
        source = Path("platform_candidate_review_v7.py").read_text(encoding="utf-8")
        self.assertIn('ap.add_argument("--attempt-index"', source)
        self.assertIn('ap.add_argument("--credential-profile"', source)
        self.assertIn("telemetry-attempt-", source)


if __name__ == "__main__":
    unittest.main()
