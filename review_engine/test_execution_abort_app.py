from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from review_engine.app import ReviewEngineApp
from review_engine.configuration import ReviewEngineConfiguration
from review_engine.models import ReviewerConfig


class FailingProviders:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def invoke(self, config, context):
        self.calls.append(config.role)
        # Deliberately include content that must never be copied into retained
        # session evidence or exposed through the application boundary.
        raise RuntimeError("provider-private-response-body SECRET_TOKEN_SHOULD_NOT_PERSIST")


def r1_config() -> ReviewerConfig:
    return ReviewerConfig(
        "R1",
        "fake",
        "model",
        "default",
        "api",
        "R1_API_KEY",
        "lineage",
        None,
    )


def build_app(td: str, providers: FailingProviders) -> ReviewEngineApp:
    configuration = ReviewEngineConfiguration(reviewers={"R1": r1_config()}, provider_specs={})
    return ReviewEngineApp(
        configuration,
        memory_db=str(Path(td) / "memory.db"),
        sessions_db=str(Path(td) / "sessions.db"),
        provider_registry=providers,
    )


class ExecutionAbortApplicationTests(unittest.TestCase):
    def test_provider_failure_is_terminally_retained_without_provider_error_content(self):
        with tempfile.TemporaryDirectory() as td:
            providers = FailingProviders()
            app = build_app(td, providers)

            with self.assertRaises(RuntimeError) as caught:
                app.review({"request_id": "provider-failure", "user_input": "brainstorm"})
            self.assertEqual(
                str(caught.exception),
                "review execution failed; inspect retained session evidence",
            )
            self.assertNotIn("SECRET_TOKEN_SHOULD_NOT_PERSIST", str(caught.exception))
            self.assertNotIn("provider-private-response-body", str(caught.exception))
            self.assertIsNone(caught.exception.__cause__)

            self.assertEqual(providers.calls, ["R1"])
            events = app.session_events("provider-failure")
            self.assertEqual(
                [event["event_type"] for event in events],
                ["REQUEST_RECEIVED", "EXECUTION_ABORTED"],
            )
            self.assertTrue(app.sessions.validate_chain("provider-failure"))
            request_payload = events[0]["payload"]
            self.assertTrue(str(request_payload.get("execution_attempt_id", "")).startswith("review-attempt:"))
            abort_payload = events[-1]["payload"]
            self.assertEqual(abort_payload["state"], "EXECUTION_ABORTED")
            self.assertEqual(
                abort_payload["reasons"],
                ["review execution failed before a governed final decision"],
            )
            retained_text = repr(events)
            self.assertNotIn("SECRET_TOKEN_SHOULD_NOT_PERSIST", retained_text)
            self.assertNotIn("provider-private-response-body", retained_text)

            summary = app.session_summaries()[0]
            self.assertEqual(summary["session_id"], "provider-failure")
            self.assertEqual(summary["final_state"], "EXECUTION_ABORTED")
            self.assertTrue(summary["chain_valid"])

    def test_aborted_request_id_remains_single_use_after_restart_and_does_not_reinvoke_provider(self):
        with tempfile.TemporaryDirectory() as td:
            first_provider = FailingProviders()
            first_app = build_app(td, first_provider)
            with self.assertRaises(RuntimeError):
                first_app.review({"request_id": "aborted-replay", "user_input": "first"})
            self.assertEqual(first_provider.calls, ["R1"])

            restarted_provider = FailingProviders()
            restarted_app = build_app(td, restarted_provider)
            with self.assertRaisesRegex(ValueError, "already exists"):
                restarted_app.review({"request_id": "aborted-replay", "user_input": "retry"})

            self.assertEqual(restarted_provider.calls, [])
            events = restarted_app.session_events("aborted-replay")
            self.assertEqual(
                [event["event_type"] for event in events],
                ["REQUEST_RECEIVED", "EXECUTION_ABORTED"],
            )
            self.assertTrue(restarted_app.sessions.validate_chain("aborted-replay"))

    def test_successful_review_exposes_terminal_abort_control_without_creating_abort_event(self):
        class SuccessProviders:
            def invoke(self, config, context):
                from review_engine.models import ReviewerResponse
                return ReviewerResponse("R1", None, "ok")

        with tempfile.TemporaryDirectory() as td:
            configuration = ReviewEngineConfiguration(reviewers={"R1": r1_config()}, provider_specs={})
            app = ReviewEngineApp(
                configuration,
                memory_db=str(Path(td) / "memory.db"),
                sessions_db=str(Path(td) / "sessions.db"),
                provider_registry=SuccessProviders(),
            )
            result = app.review({"request_id": "success", "user_input": "brainstorm"})
            self.assertEqual(result["state"], "CONVERGED_PASS")
            self.assertTrue(result["session_terminal_abort_evidence"])
            self.assertTrue(result["session_owned_execution_attempt"])
            events = app.session_events("success")
            self.assertEqual(events[-1]["event_type"], "FINAL_DECISION")
            self.assertFalse(any(event["event_type"] == "EXECUTION_ABORTED" for event in events))


if __name__ == "__main__":
    unittest.main()
