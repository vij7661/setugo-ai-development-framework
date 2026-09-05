from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from review_engine.app import ReviewEngineApp
from review_engine.configuration import ReviewEngineConfiguration
from review_engine.models import ReviewerConfig, ReviewerResponse


class FakeProviders:
    def __init__(self): self.calls = []
    def invoke(self, config, context):
        self.calls.append(config.role)
        if config.role == "R1": return ReviewerResponse("R1", None, "hello from R1")
        raise AssertionError("low-risk test should not invoke external reviewers")


def r1_config():
    return ReviewerConfig("R1", "fake", "model", "default", "api", "R1_API_KEY", "lineage", None)


class AppTests(unittest.TestCase):
    def test_health_and_low_risk_review_are_ui_ready_without_exposing_secret_env_name(self):
        with tempfile.TemporaryDirectory() as td:
            configuration = ReviewEngineConfiguration(reviewers={"R1": r1_config()}, provider_specs={})
            fake = FakeProviders()
            app = ReviewEngineApp(
                configuration,
                memory_db=str(Path(td) / "memory.db"),
                sessions_db=str(Path(td) / "sessions.db"),
                provider_registry=fake,
            )
            health = app.health()
            self.assertEqual(health["status"], "ok")
            self.assertEqual(health["assurance_mode"], "EXPERIMENTAL_UNQUALIFIED")
            self.assertNotIn("api_key_env", health["reviewers"]["R1"])
            result = app.review({"request_id": "s1", "user_input": "brainstorm", "operation_class": "CHAT"})
            self.assertEqual(result["state"], "CONVERGED_PASS")
            self.assertEqual(result["final_output"], "hello from R1")
            self.assertFalse(result["action_authorized"])
            self.assertTrue(result["session_chain_valid"])
            self.assertEqual(fake.calls, ["R1"])
            summaries = app.session_summaries()
            self.assertEqual(summaries[0]["session_id"], "s1")
            self.assertEqual(summaries[0]["final_state"], "CONVERGED_PASS")


if __name__ == "__main__": unittest.main()
