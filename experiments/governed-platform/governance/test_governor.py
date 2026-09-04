import unittest

from governor import process_event


def base_state():
    return {
        "project_id": "pilot1",
        "task_id": "EXP-D-001",
        "execution_sha": "abc123",
        "state_version": 7,
        "status": "RUNNING",
        "processed_event_keys": [],
        "manual_gate_active": False,
        "completion_authorized": False,
        "required_evidence": ["ci:run-1"],
    }


def event(**overrides):
    value = {
        "source": "github-actions",
        "event_id": "delivery-1",
        "authenticated": True,
        "project_id": "pilot1",
        "task_id": "EXP-D-001",
        "execution_sha": "abc123",
        "expected_state_version": 7,
        "conclusion": "success",
        "evidence_refs": ["ci:run-1"],
        "requested_transition": "CONTINUING",
    }
    value.update(overrides)
    return value


class GovernorTests(unittest.TestCase):
    def test_valid_success_advances_once(self):
        first = process_event(base_state(), event())
        self.assertEqual("CONTINUE", first["decision"])
        self.assertTrue(first["mutated"])
        self.assertEqual(8, first["state"]["state_version"])
        self.assertEqual("CONTINUING", first["state"]["status"])
        replay = process_event(first["state"], event(expected_state_version=8))
        self.assertEqual("IGNORE", replay["decision"])
        self.assertIn("duplicate", replay["reason"])

    def test_forged_event_is_blocked(self):
        result = process_event(base_state(), event(authenticated=False))
        self.assertEqual("BLOCK", result["decision"])
        self.assertFalse(result["mutated"])

    def test_stale_sha_is_ignored(self):
        result = process_event(base_state(), event(execution_sha="oldsha"))
        self.assertEqual("IGNORE", result["decision"])
        self.assertIn("SHA", result["reason"])

    def test_wrong_project_is_ignored(self):
        result = process_event(base_state(), event(project_id="other"))
        self.assertEqual("IGNORE", result["decision"])

    def test_state_version_race_loser_is_ignored(self):
        result = process_event(base_state(), event(expected_state_version=6))
        self.assertEqual("IGNORE", result["decision"])
        self.assertIn("race", result["reason"])

    def test_manual_gate_cannot_be_bypassed_by_pass(self):
        state = base_state()
        state["manual_gate_active"] = True
        result = process_event(state, event())
        self.assertEqual("REQUEST_HUMAN", result["decision"])

    def test_missing_evidence_cannot_advance(self):
        result = process_event(base_state(), event(evidence_refs=[]))
        self.assertEqual("BLOCK", result["decision"])
        self.assertIn("evidence", result["reason"])

    def test_complete_requires_explicit_gate_authority(self):
        result = process_event(base_state(), event(requested_transition="COMPLETE"))
        self.assertEqual("BLOCK", result["decision"])
        state = base_state()
        state["completion_authorized"] = True
        ok = process_event(state, event(requested_transition="COMPLETE"))
        self.assertEqual("COMPLETE", ok["decision"])
        self.assertEqual("COMPLETE", ok["state"]["status"])

    def test_budget_exhaustion_is_not_pass(self):
        result = process_event(base_state(), event(budget_exhausted=True))
        self.assertEqual("BLOCK", result["decision"])

    def test_corrective_scope_cannot_escape_classification(self):
        bad = process_event(
            base_state(),
            event(
                conclusion="failure",
                classification="CODE DEFECT",
                requested_artifact_classes=["tests"],
            ),
        )
        self.assertEqual("BLOCK", bad["decision"])
        good = process_event(
            base_state(),
            event(
                event_id="delivery-2",
                conclusion="failure",
                classification="CODE DEFECT",
                requested_artifact_classes=["production_code"],
            ),
        )
        self.assertEqual("DIAGNOSE", good["decision"])


if __name__ == "__main__":
    unittest.main()
