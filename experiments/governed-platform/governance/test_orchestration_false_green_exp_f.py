"""EXP-F: falsify orchestration false-green paths while evaluated models behave correctly."""
import unittest

from governor import process_event


def base_state(**overrides):
    value = {
        "project_id": "pilot1",
        "task_id": "EXP-F-ORCH",
        "execution_sha": "sha-current",
        "state_version": 1,
        "status": "RUNNING",
        "processed_event_keys": [],
        "manual_gate_active": False,
        "completion_authorized": False,
        "required_evidence": ["judge:independent", "regression:current"],
        "evidence_bindings": {
            "judge:independent": {"project_id": "pilot1", "task_id": "EXP-F-ORCH", "execution_sha": "sha-current"},
            "regression:current": {"project_id": "pilot1", "task_id": "EXP-F-ORCH", "execution_sha": "sha-current"},
        },
    }
    value.update(overrides)
    return value


def success_event(**overrides):
    value = {
        "source": "orchestrator",
        "event_id": "orch-1",
        "authenticated": True,
        "project_id": "pilot1",
        "task_id": "EXP-F-ORCH",
        "execution_sha": "sha-current",
        "expected_state_version": 1,
        "conclusion": "success",
        "evidence_refs": ["judge:independent", "regression:current"],
        "requested_transition": "COMPLETE",
    }
    value.update(overrides)
    return value


class ExpFOrchestrationFalseGreenTests(unittest.TestCase):
    def test_correct_model_output_cannot_bypass_independent_evidence(self):
        result = process_event(base_state(), success_event(evidence_refs=["model:self-report"]))
        self.assertEqual("BLOCK", result["decision"])

    def test_correct_model_output_cannot_self_authorize_completion(self):
        result = process_event(base_state(), success_event())
        self.assertEqual("BLOCK", result["decision"])
        self.assertIn("not authorized", result["reason"])

    def test_stale_independent_evidence_cannot_create_false_green(self):
        state = base_state()
        state["evidence_bindings"]["judge:independent"]["execution_sha"] = "sha-old"
        result = process_event(state, success_event(requested_transition="CONTINUING"))
        self.assertEqual("BLOCK", result["decision"])
        self.assertIn("provenance", result["reason"])

    def test_manual_gate_cannot_be_bypassed_by_green_model_and_tests(self):
        result = process_event(base_state(manual_gate_active=True), success_event(requested_transition="CONTINUING"))
        self.assertEqual("REQUEST_HUMAN", result["decision"])

    def test_budget_exhaustion_cannot_be_laundered_as_success(self):
        result = process_event(base_state(), success_event(budget_exhausted=True, requested_transition="CONTINUING"))
        self.assertEqual("BLOCK", result["decision"])
        self.assertIn("cannot be interpreted as PASS", result["reason"])

    def test_only_external_completion_authority_plus_current_evidence_can_complete(self):
        result = process_event(base_state(completion_authorized=True), success_event())
        self.assertEqual("COMPLETE", result["decision"])
        self.assertEqual("COMPLETE", result["state"]["status"])


if __name__ == "__main__":
    unittest.main()
