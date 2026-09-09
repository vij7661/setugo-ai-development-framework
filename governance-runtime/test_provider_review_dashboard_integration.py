from __future__ import annotations

from pathlib import Path
import unittest

import provider_review_telemetry as telemetry


class ProviderReviewDashboardIntegrationTests(unittest.TestCase):
    def _event(self, provider: str, model: str) -> dict:
        return {
            "schema_version": 1,
            "event_type": "REVIEW_PROVIDER_ATTEMPT",
            "review_request_id": "REV-DASH-001",
            "reviewed_candidate_commit": "a" * 40,
            "reviewer_slot": "R3",
            "gateway_provider": provider,
            "model": model,
            "credential_profile": "r3",
            "requested_serving_provider": None,
            "returned_serving_provider": None,
            "attempt_index": 1,
            "request_started_at": "2026-09-09T08:00:00Z",
            "provider_call_started_at": "2026-09-09T08:00:01Z",
            "first_response_at": "2026-09-09T08:00:02Z",
            "provider_call_completed_at": "2026-09-09T08:00:03Z",
            "provider_latency_ms": 2000,
            "attempt_outcome": "SUCCESS",
            "retryable": False,
            "http_status": 200,
            "error_classification": None,
            "error_detail": None,
            "semantic_disposition": "PASS",
            "validation_valid": True,
            "authority_effect": "NONE_PENDING_DETERMINISTIC_INGESTION",
        }

    def test_separate_workflow_runs_do_not_collide_on_attempt_one(self):
        first = telemetry.aggregate_attempts([self._event("provider-a", "model-a")])
        second = telemetry.aggregate_attempts([self._event("future-provider-x", "model-x")])
        merged = telemetry.merge_run_summaries([
            {"workflow_run_id": "100", "summary": first},
            {"workflow_run_id": "101", "summary": second},
        ])
        self.assertEqual(2, len(merged["reviews"]))
        self.assertEqual(["future-provider-x", "provider-a"], [p["provider"] for p in merged["providers"]])
        self.assertEqual({"100", "101"}, {str(r["workflow_run_id"]) for r in merged["reviews"]})

    def test_dashboard_page_consumes_provider_telemetry_data(self):
        page = Path("../experiments/governed-platform/observability/dashboard/index.html").read_text(encoding="utf-8")
        self.assertIn("provider-review-telemetry-dashboard.json", page)
        self.assertIn('id="reviewTelemetry"', page)
        self.assertNotIn("future-provider-x", page)

    def test_dashboard_publication_collects_governance_review_artifacts_generically(self):
        workflow = Path("../.github/workflows/governed-platform-dashboard-pages.yml").read_text(encoding="utf-8")
        self.assertIn("Governance Candidate Platform Review", workflow)
        self.assertIn("governance-candidate-platform-review", workflow)
        self.assertIn("provider-review-telemetry-dashboard.json", workflow)
        self.assertNotIn("future-provider-x", workflow)


if __name__ == "__main__":
    unittest.main()
