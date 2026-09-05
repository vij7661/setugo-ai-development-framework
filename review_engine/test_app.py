from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from review_engine.app import ReviewEngineApp
from review_engine.configuration import ReviewEngineConfiguration
from review_engine.models import ReviewerConfig, ReviewerResponse


class FakeProviders:
    def __init__(self):
        self.calls = []

    def invoke(self, config, context):
        self.calls.append(config.role)
        if config.role == "R1":
            return ReviewerResponse("R1", None, "hello from R1")
        raise AssertionError("low-risk test should not invoke external reviewers")


def r1_config():
    return ReviewerConfig("R1", "fake", "model", "default", "api", "R1_API_KEY", "lineage", None)


class AppTests(unittest.TestCase):
    def build_app(self, td: str, fake: FakeProviders) -> ReviewEngineApp:
        configuration = ReviewEngineConfiguration(reviewers={"R1": r1_config()}, provider_specs={})
        return ReviewEngineApp(
            configuration,
            memory_db=str(Path(td) / "memory.db"),
            sessions_db=str(Path(td) / "sessions.db"),
            provider_registry=fake,
        )

    def test_health_and_low_risk_review_are_ui_ready_without_exposing_secret_env_name(self):
        with tempfile.TemporaryDirectory() as td:
            fake = FakeProviders()
            app = self.build_app(td, fake)
            health = app.health()
            self.assertEqual(health["status"], "ok")
            self.assertEqual(health["assurance_mode"], "EXPERIMENTAL_UNQUALIFIED")
            self.assertNotIn("api_key_env", health["reviewers"]["R1"])
            self.assertEqual(health["execution_envelope"]["operation_class"], "ANALYSIS")
            self.assertEqual(health["execution_envelope"]["connected_tool_capabilities"], [])
            self.assertEqual(health["execution_envelope"]["source"], "trusted_application_boundary")

            result = app.review({"request_id": "s1", "user_input": "brainstorm", "operation_class": "CHAT"})
            self.assertEqual(result["state"], "CONVERGED_PASS")
            self.assertEqual(result["final_output"], "hello from R1")
            self.assertFalse(result["action_authorized"])
            self.assertTrue(result["session_chain_valid"])
            self.assertEqual(fake.calls, ["R1"])
            self.assertEqual(result["platform_facts"]["platform_operation_class"], "ANALYSIS")
            self.assertEqual(result["platform_facts"]["declared_operation_class"], "CHAT")
            summaries = app.session_summaries()
            self.assertEqual(summaries[0]["session_id"], "s1")
            self.assertEqual(summaries[0]["final_state"], "CONVERGED_PASS")

    def test_obvious_production_text_cannot_be_downgraded_by_chat_declaration(self):
        with tempfile.TemporaryDirectory() as td:
            fake = FakeProviders()
            app = self.build_app(td, fake)
            result = app.review({
                "request_id": "prod-1",
                "user_input": "deploy this fix to production now",
                "operation_class": "CHAT",
                "connected_tool_capabilities": [],
            })
            self.assertEqual(result["state"], "HUMAN_REQUIRED")
            self.assertIn("EXPERIMENTAL_UNQUALIFIED", result["reasons"][0])
            self.assertEqual(result["platform_facts"]["declared_operation_class"], "CHAT")
            self.assertEqual(result["platform_facts"]["platform_operation_class"], "ANALYSIS")
            self.assertEqual(fake.calls, [])

    def test_client_task_type_is_declaration_not_qualification_authority(self):
        with tempfile.TemporaryDirectory() as td:
            fake = FakeProviders()
            app = self.build_app(td, fake)
            result = app.review({"request_id": "task-1", "user_input": "review this", "task_type": "SECURITY"})
            self.assertEqual(result["platform_facts"]["task_type"], "GENERAL")
            self.assertEqual(result["platform_facts"]["declared_task_type"], "SECURITY")

    def test_duplicate_request_id_is_rejected_instead_of_merging_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            fake = FakeProviders()
            app = self.build_app(td, fake)
            first = app.review({"request_id": "dup", "user_input": "first"})
            self.assertEqual(first["state"], "CONVERGED_PASS")
            with self.assertRaisesRegex(ValueError, "already exists"):
                app.review({"request_id": "dup", "user_input": "different second request"})
            events = app.session_events("dup")
            self.assertEqual(len([e for e in events if e["event_type"] == "REQUEST_RECEIVED"]), 1)
            self.assertEqual(len([e for e in events if e["event_type"] == "FINAL_DECISION"]), 1)


if __name__ == "__main__":
    unittest.main()
