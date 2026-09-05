import unittest

from governor import process_event


def state():
    return {
        "project_id": "pilot1",
        "task_id": "EXP-F-PROV-001",
        "execution_sha": "sha-current",
        "state_version": 21,
        "status": "RUNNING",
        "processed_event_keys": [],
        "manual_gate_active": False,
        "completion_authorized": False,
        "required_evidence": ["ci:run-current"],
        "evidence_bindings": {
            "ci:run-current": {
                "project_id": "pilot1",
                "task_id": "EXP-F-PROV-001",
                "execution_sha": "sha-current",
            }
        },
    }


def event(**overrides):
    value = {
        "source": "github-actions",
        "event_id": "delivery-prov-1",
        "authenticated": True,
        "project_id": "pilot1",
        "task_id": "EXP-F-PROV-001",
        "execution_sha": "sha-current",
        "expected_state_version": 21,
        "conclusion": "success",
        "evidence_refs": ["ci:run-current"],
        "requested_transition": "CONTINUING",
    }
    value.update(overrides)
    return value


class ExpFProvenanceTests(unittest.TestCase):
    def test_required_evidence_must_be_bound_to_current_project_task_and_sha(self):
        bad = state()
        bad["evidence_bindings"]["ci:run-current"]["execution_sha"] = "sha-old"
        result = process_event(bad, event())
        self.assertEqual("BLOCK", result["decision"])
        self.assertFalse(result["mutated"])
        self.assertIn("provenance", result["reason"].lower())

    def test_matching_evidence_binding_can_advance(self):
        result = process_event(state(), event())
        self.assertEqual("CONTINUE", result["decision"])
        self.assertTrue(result["mutated"])


if __name__ == "__main__":
    unittest.main()
