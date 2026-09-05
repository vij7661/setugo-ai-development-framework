import unittest

from governor import process_event
from review_convergence import authorize_model_routing, evaluate_review_convergence


def state(**overrides):
    value = {
        "project_id": "pilot1", "task_id": "EXP-F-DEEP", "execution_sha": "sha-current", "state_version": 5,
        "status": "RUNNING", "processed_event_keys": [], "manual_gate_active": False, "completion_authorized": True,
        "required_evidence": ["judge:canonical", "regression:canonical"],
        "evidence_bindings": {
            "judge:canonical": {"project_id": "pilot1", "task_id": "EXP-F-DEEP", "execution_sha": "sha-current"},
            "regression:canonical": {"project_id": "pilot1", "task_id": "EXP-F-DEEP", "execution_sha": "sha-current"},
        },
    }
    value.update(overrides); return value


def event(event_id="evt-a", **overrides):
    value = {
        "source": "orchestrator", "event_id": event_id, "authenticated": True, "project_id": "pilot1", "task_id": "EXP-F-DEEP",
        "execution_sha": "sha-current", "expected_state_version": 5, "conclusion": "success",
        "evidence_refs": ["judge:canonical", "regression:canonical"], "requested_transition": "COMPLETE",
    }
    value.update(overrides); return value


class ExpFDeepOrchestrationTests(unittest.TestCase):
    def test_sequentialized_race_loser_cannot_complete_again(self):
        first = process_event(state(), event("evt-a")); self.assertEqual("COMPLETE", first["decision"])
        second = process_event(first["state"], event("evt-b", expected_state_version=5)); self.assertEqual("IGNORE", second["decision"])

    def test_cross_project_evidence_binding_cannot_be_laundered(self):
        bad = state(); bad["evidence_bindings"]["judge:canonical"]["project_id"] = "other-project"
        self.assertEqual("BLOCK", process_event(bad, event(requested_transition="CONTINUING"))["decision"])

    def test_cross_task_evidence_binding_cannot_be_laundered(self):
        bad = state(); bad["evidence_bindings"]["judge:canonical"]["task_id"] = "other-task"
        self.assertEqual("BLOCK", process_event(bad, event(requested_transition="CONTINUING"))["decision"])

    def test_alias_evidence_identity_cannot_substitute_for_canonical_refs(self):
        result = process_event(state(), event(evidence_refs=["judge:canonical-copy", "regression:canonical"]))
        self.assertEqual("BLOCK", result["decision"])

    def test_duplicate_reviewer_cannot_manufacture_convergence(self):
        policy = {
            "max_reviews": 3, "required_qualified_agreement": 2, "false_positive_rate_threshold": 0.10,
            "review_role": "judge", "task_class": "governance-review", "risk_tier": "high",
            "min_performance_samples": 20, "required_difficulty_bands": ["MEDIUM", "HARD"], "min_samples_per_difficulty": 5,
        }
        reviews = [{"reviewer_id": "r1", "verdict": "PASS"}, {"reviewer_id": "r1", "verdict": "PASS"}, {"reviewer_id": "r2", "verdict": "FAIL"}]
        common = {"independently_adjudicated": True, "role": "judge", "task_class": "governance-review", "risk_tier": "high", "sample_count": 20, "difficulty_distribution": {"MEDIUM": 10, "HARD": 10}}
        performance_records = [
            {**common, "reviewer_id": "r1", "false_positive_rate": 0.01, "evidence_ref": "perf:r1:v1", "performance_epoch": 1},
            {**common, "reviewer_id": "r2", "false_positive_rate": 0.02, "evidence_ref": "perf:r2:v1", "performance_epoch": 1},
        ]
        result = evaluate_review_convergence(policy, reviews, performance_records)
        self.assertEqual("CEILING_REACHED_ESCALATE", result["decision"])
        self.assertEqual(["r1"], result["duplicate_reviewers"])

    def test_asserted_compatibility_cannot_bypass_invariant_extraction(self):
        contract = {"domain_invariants": ["authority_external", "evidence_before_promotion"]}
        candidate = {"asserted_compatible": True, "preserved_invariants": ["authority_external"]}
        result = authorize_model_routing(contract, candidate)
        self.assertFalse(result["authorized"])

    def test_routing_fails_closed_when_contract_omits_invariants(self):
        with self.assertRaises(ValueError): authorize_model_routing({}, {"preserved_invariants": []})


if __name__ == "__main__": unittest.main()
