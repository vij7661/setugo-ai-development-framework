from __future__ import annotations

import tempfile
import threading
import unittest
from pathlib import Path

from review_engine.app import ReviewEngineApp
from review_engine.configuration import ReviewEngineConfiguration
from review_engine.judge_health import JudgeIdentityBinding, JudgeObservation
from review_engine.models import ReviewerConfig, ReviewerResponse


class FakeProviders:
    def __init__(self):
        self.calls = []

    def invoke(self, config, context):
        self.calls.append(config.role)
        if config.role == "R1":
            return ReviewerResponse("R1", None, "hello from R1")
        raise AssertionError("low-risk test should not invoke external reviewers")


class BlockingProviders(FakeProviders):
    """Hold the winning R1 call open so a duplicate can race while in progress."""

    def __init__(self):
        super().__init__()
        self.entered = threading.Event()
        self.release = threading.Event()

    def invoke(self, config, context):
        self.calls.append(config.role)
        if config.role != "R1":
            raise AssertionError("low-risk test should not invoke external reviewers")
        self.entered.set()
        if not self.release.wait(timeout=10):
            raise TimeoutError("test did not release provider")
        return ReviewerResponse("R1", None, "hello from R1")


def r1_config():
    return ReviewerConfig("R1", "fake", "model", "default", "api", "R1_API_KEY", "lineage", None)


def health_identity(name: str) -> JudgeIdentityBinding:
    return JudgeIdentityBinding(
        provider=f"provider-{name}", model=f"model-{name}", sku="default",
        deployment_path=f"api/{name}", role="R2", foundation_lineage=f"lineage-{name}",
        qualification_ref=f"q-{name}", qualification_epoch=1,
    )


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
            self.assertEqual(health["truth_contract_version"], "TVC-1")
            self.assertEqual(health["evidence_correspondence_validator"], "UNCONFIGURED")
            self.assertEqual(health["judge_health_monitor"], "PAIRWISE_LOGICAL_DISAGREEMENT_BOUND_V1")

            result = app.review({"request_id": "s1", "user_input": "brainstorm", "operation_class": "CHAT"})
            self.assertEqual(result["state"], "CONVERGED_PASS")
            self.assertEqual(result["final_output"], "hello from R1")
            self.assertFalse(result["action_authorized"])
            self.assertTrue(result["session_chain_valid"])
            self.assertEqual(result["truth_contract_version"], "TVC-1")
            self.assertFalse(result["evidence_correspondence_validator_configured"])
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
            self.assertEqual(fake.calls, ["R1"])

    def test_duplicate_request_id_is_rejected_after_application_restart_without_provider_replay(self):
        with tempfile.TemporaryDirectory() as td:
            first_provider = FakeProviders()
            first_app = self.build_app(td, first_provider)
            first = first_app.review({"request_id": "restart-dup", "user_input": "first"})
            self.assertEqual(first["state"], "CONVERGED_PASS")
            self.assertEqual(first_provider.calls, ["R1"])

            restarted_provider = FakeProviders()
            restarted_app = self.build_app(td, restarted_provider)
            with self.assertRaisesRegex(ValueError, "already exists"):
                restarted_app.review({"request_id": "restart-dup", "user_input": "retry after restart"})

            self.assertEqual(restarted_provider.calls, [])
            events = restarted_app.session_events("restart-dup")
            self.assertEqual(len([e for e in events if e["event_type"] == "REQUEST_RECEIVED"]), 1)
            self.assertEqual(len([e for e in events if e["event_type"] == "FINAL_DECISION"]), 1)
            self.assertTrue(restarted_app.sessions.validate_chain("restart-dup"))

    def test_concurrent_duplicate_request_is_rejected_before_second_provider_invocation(self):
        with tempfile.TemporaryDirectory() as td:
            provider = BlockingProviders()
            app = self.build_app(td, provider)
            first_result: list[dict] = []
            first_error: list[Exception] = []

            def first_request() -> None:
                try:
                    first_result.append(app.review({"request_id": "race-dup", "user_input": "first"}))
                except Exception as exc:  # pragma: no cover - asserted below
                    first_error.append(exc)

            thread = threading.Thread(target=first_request)
            thread.start()
            self.assertTrue(provider.entered.wait(timeout=5), "winning request never reached provider")

            try:
                with self.assertRaisesRegex(ValueError, "already exists"):
                    app.review({"request_id": "race-dup", "user_input": "concurrent duplicate"})
                # The first request is still blocked inside R1. A second provider
                # call here would prove that request admission happened too late.
                self.assertEqual(provider.calls, ["R1"])
                events_while_open = app.session_events("race-dup")
                self.assertEqual(
                    [e["event_type"] for e in events_while_open],
                    ["REQUEST_RECEIVED"],
                )
            finally:
                provider.release.set()
                thread.join(timeout=10)

            self.assertFalse(first_error, first_error)
            self.assertEqual(len(first_result), 1)
            self.assertEqual(first_result[0]["state"], "CONVERGED_PASS")
            self.assertEqual(provider.calls, ["R1"])
            events = app.session_events("race-dup")
            self.assertEqual(len([e for e in events if e["event_type"] == "REQUEST_RECEIVED"]), 1)
            self.assertEqual(len([e for e in events if e["event_type"] == "FINAL_DECISION"]), 1)
            self.assertTrue(app.sessions.validate_chain("race-dup"))

    def test_judge_health_is_internal_monitoring_evidence_not_correctness_certificate(self):
        with tempfile.TemporaryDirectory() as td:
            app = self.build_app(td, FakeProviders())
            a, b = health_identity("a"), health_identity("b")
            observations = []
            for i in range(10):
                observations.append(JudgeObservation.bound(f"t{i}", a, "A"))
                observations.append(JudgeObservation.bound(f"t{i}", b, "B" if i < 3 else "A"))
            report = app.judge_health(
                observations,
                minimum_accuracy_target=0.9,
                minimum_shared_tasks=10,
            )
            self.assertEqual(report["status"], "LOGICALLY_INCONSISTENT_WITH_QUALIFICATION_TARGET")
            self.assertTrue(report["bound_identity_required"])
            self.assertFalse(report["no_alarm_establishes_correctness"])
            self.assertFalse(report["can_identify_faulty_judge"])


if __name__ == "__main__":
    unittest.main()
