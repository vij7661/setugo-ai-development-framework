import unittest

from governor import process_event


def state():
    return {
        "project_id": "pilot1",
        "task_id": "EXP-F-001",
        "execution_sha": "sha-current",
        "state_version": 11,
        "status": "RUNNING",
        "processed_event_keys": [],
        "manual_gate_active": False,
        "completion_authorized": False,
        "required_evidence": ["ci:run-current"],
    }


def event(**overrides):
    value = {
        "source": "github-actions",
        "event_id": "delivery-f1",
        "authenticated": True,
        "project_id": "pilot1",
        "task_id": "EXP-F-001",
        "execution_sha": "sha-current",
        "expected_state_version": 11,
        "conclusion": "failure",
        "classification": "CODE DEFECT",
        "requested_artifact_classes": ["production_code"],
        "evidence_refs": ["ci:run-current"],
    }
    value.update(overrides)
    return value


class ExpFGovernorFalsificationTests(unittest.TestCase):
    def test_classified_failure_event_is_consumed_before_repair_dispatch(self):
        first = process_event(state(), event())
        self.assertEqual("DIAGNOSE", first["decision"])
        self.assertTrue(first["mutated"])
        self.assertIn("github-actions::delivery-f1", first["state"]["processed_event_keys"])
        replay = process_event(first["state"], event(expected_state_version=12))
        self.assertEqual("IGNORE", replay["decision"])
        self.assertIn("duplicate", replay["reason"])

    def test_requirement_unresolved_event_is_consumed_before_human_request(self):
        first = process_event(
            state(),
            event(classification="REQUIREMENT UNRESOLVED", requested_artifact_classes=[]),
        )
        self.assertEqual("REQUEST_HUMAN", first["decision"])
        self.assertTrue(first["mutated"])
        replay = process_event(first["state"], event(expected_state_version=12))
        self.assertEqual("IGNORE", replay["decision"])

    def test_malformed_state_version_fails_closed_instead_of_crashing(self):
        result = process_event(state(), event(expected_state_version="not-an-int"))
        self.assertEqual("BLOCK", result["decision"])
        self.assertFalse(result["mutated"])
        self.assertIn("state version", result["reason"].lower())

    def test_malformed_evidence_fails_closed(self):
        success = event(conclusion="success", classification=None, requested_artifact_classes=[], evidence_refs=[{"bad": "shape"}])
        result = process_event(state(), success)
        self.assertEqual("BLOCK", result["decision"])
        self.assertFalse(result["mutated"])
        self.assertIn("evidence", result["reason"].lower())


if __name__ == "__main__":
    unittest.main()
