import unittest

from governor import process_event


def base_state():
    return {
        "project_id": "p1",
        "task_id": "t1",
        "execution_sha": "sha-current",
        "state_version": 1,
        "status": "RUNNING",
        "processed_event_keys": [],
        "manual_gate_active": False,
        "completion_authorized": True,
        "required_evidence": ["judge", "regression"],
        "evidence_bindings": {
            "judge": {"project_id": "p1", "task_id": "t1", "execution_sha": "sha-current"},
            "regression": {"project_id": "p1", "task_id": "t1", "execution_sha": "sha-current"},
        },
    }


def valid_event(event_id="e1", transition="CONTINUING"):
    return {
        "source": "orchestrator",
        "event_id": event_id,
        "authenticated": True,
        "project_id": "p1",
        "task_id": "t1",
        "execution_sha": "sha-current",
        "expected_state_version": 1,
        "conclusion": "success",
        "evidence_refs": ["judge", "regression"],
        "requested_transition": transition,
    }


class ExpDCleanSpecificityControls(unittest.TestCase):
    def test_legitimate_current_sha_transition_is_not_rejected(self):
        result = process_event(base_state(), valid_event())
        self.assertNotIn(result["decision"], {"BLOCK", "IGNORE"})

    def test_legitimate_gate_cleared_transition_can_advance(self):
        state = base_state(); state["manual_gate_active"] = False
        result = process_event(state, valid_event())
        self.assertNotEqual("BLOCK", result["decision"])

    def test_legitimate_single_event_is_consumed_once(self):
        result = process_event(base_state(), valid_event("unique-event"))
        self.assertIn("orchestrator::unique-event", result["state"]["processed_event_keys"])

    def test_legitimate_authorized_complete_with_current_evidence_succeeds(self):
        result = process_event(base_state(), valid_event("complete-event", "COMPLETE"))
        self.assertEqual("COMPLETE", result["decision"])


if __name__ == "__main__":
    unittest.main()
