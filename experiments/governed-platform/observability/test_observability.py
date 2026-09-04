import unittest

from normalize_github_event import normalize
from render_status import render


class ObservabilityTests(unittest.TestCase):
    def base_event(self):
        return {
            "campaign": "pilot1",
            "experiment": "EXP-B",
            "case_id": "EXP-B-003",
            "branch": "experiment/governed-platform-falsification-harness",
            "execution_sha": "abcdef1234567890",
            "run_id": 123,
            "jobs": [
                {"name": "Groq", "status": "completed", "conclusion": "success"},
                {"name": "OpenRouter", "status": "completed", "conclusion": "success"},
            ],
            "controller_decision": "COMPLETE",
            "human_required": False,
        }

    def test_dual_success_is_complete_but_not_scientific_pass(self):
        state = normalize(self.base_event())
        self.assertEqual(state["execution_status"], "COMPLETE")
        self.assertEqual(state["scientific_status"], "AWAITING_ADJUDICATION")

    def test_provider_failure_is_failed_and_inconclusive(self):
        event = self.base_event()
        event["jobs"][1]["conclusion"] = "failure"
        state = normalize(event)
        self.assertEqual(state["execution_status"], "FAILED")
        self.assertEqual(state["scientific_status"], "INCONCLUSIVE")

    def test_missing_required_field_rejected(self):
        event = self.base_event()
        event.pop("execution_sha")
        with self.assertRaisesRegex(ValueError, "missing authoritative fields"):
            normalize(event)

    def test_invalid_classification_rejected(self):
        event = self.base_event()
        event["failure_classification"] = "MAGIC"
        with self.assertRaisesRegex(ValueError, "invalid failure classification"):
            normalize(event)

    def test_stale_or_out_of_scope_event_rejected(self):
        event = self.base_event()
        with self.assertRaisesRegex(ValueError, "out-of-scope event"):
            normalize(event, expected_sha="different-sha")

    def test_scientific_pass_rejected_on_failed_execution(self):
        event = self.base_event()
        event["jobs"][0]["conclusion"] = "failure"
        event["scientific_status"] = "PASS"
        with self.assertRaisesRegex(ValueError, "scientific PASS"):
            normalize(event)

    def test_renderer_includes_authoritative_identity_and_human_state(self):
        state = normalize(self.base_event())
        text = render(state)
        self.assertIn("abcdef1234567890", text)
        self.assertIn("Run ID:** `123`", text)
        self.assertIn("Human action:** NOT REQUIRED", text)
        self.assertIn("Scientific:** AWAITING_ADJUDICATION", text)


if __name__ == "__main__":
    unittest.main()
