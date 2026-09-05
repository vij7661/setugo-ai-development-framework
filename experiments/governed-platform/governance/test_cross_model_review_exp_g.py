import copy
import unittest

from cross_model_review import validate_cross_model_run, validate_role_reversal


def actor(name, lineage):
    return {
        "provider": name,
        "model": name + "-model",
        "sku": name + "-sku",
        "deployment_path": "api/" + name + "/prod",
        "qualification_ref": "qual-" + name,
        "qualification_epoch": 1,
        "foundation_lineage": lineage,
        "qualification_status": "QUALIFIED",
    }


def run(builder=None, reviewer=None, **overrides):
    value = {
        "case_id": "EXP-G-001",
        "case_version": 1,
        "requirements_hash": "req-hash",
        "builder": builder or actor("builder-a", "family-a"),
        "builder_artifact_hash": "artifact-hash-a",
        "reviewer": reviewer or actor("reviewer-b", "family-b"),
        "reviewer_output_hash": "review-hash-b",
        "reviewer_input": {
            "builder_artifact_hash": "artifact-hash-a",
            "requirements_hash": "req-hash",
        },
        "ground_truth_ref": "truth:EXP-G-001:v1",
        "ground_truth_hash": "truth-hash",
        "role_assignment_id": "A-B",
        "role_reversal_pair_id": "PAIR-1",
        "reviewer_complete": True,
        "risk_tier": "HIGH",
    }
    value.update(overrides)
    return value


class ExpGCrossModelProtocolTests(unittest.TestCase):
    def test_valid_independent_cross_model_review_is_accepted(self):
        self.assertTrue(validate_cross_model_run(run())["valid"])

    def test_reviewer_cannot_receive_builder_private_reasoning(self):
        value = run()
        value["reviewer_input"]["builder_chain_of_thought"] = "hidden reasoning"
        result = validate_cross_model_run(value)
        self.assertFalse(result["valid"])
        self.assertIn("blinding", result["reason"])

    def test_reviewer_cannot_receive_protected_ground_truth(self):
        value = run()
        value["reviewer_input"]["protected_ground_truth"] = {"defects": ["D1"]}
        self.assertFalse(validate_cross_model_run(value)["valid"])

    def test_truncated_reviewer_output_cannot_count(self):
        value = run(reviewer_complete=False)
        self.assertFalse(validate_cross_model_run(value)["valid"])

    def test_reviewer_must_receive_exact_frozen_builder_artifact(self):
        value = run()
        value["reviewer_input"]["builder_artifact_hash"] = "different-artifact"
        self.assertFalse(validate_cross_model_run(value)["valid"])

    def test_requirements_binding_cannot_drift_between_builder_and_reviewer(self):
        value = run()
        value["reviewer_input"]["requirements_hash"] = "other-requirements"
        self.assertFalse(validate_cross_model_run(value)["valid"])

    def test_high_risk_same_foundation_lineage_is_not_independent(self):
        value = run(reviewer=actor("reviewer-b", "family-a"))
        result = validate_cross_model_run(value)
        self.assertFalse(result["valid"])
        self.assertIn("correlated", result["reason"])

    def test_unqualified_reviewer_cannot_generate_evidence(self):
        reviewer = actor("reviewer-b", "family-b")
        reviewer["qualification_status"] = "REVOKED"
        self.assertFalse(validate_cross_model_run(run(reviewer=reviewer))["valid"])

    def test_reviewer_cannot_self_authorize_release(self):
        self.assertFalse(validate_cross_model_run(run(reviewer_claims_release_authority=True))["valid"])

    def test_adjudicator_cannot_self_authorize_release(self):
        value = run(adjudicator=actor("judge-c", "family-c"), adjudicator_claims_release_authority=True)
        self.assertFalse(validate_cross_model_run(value)["valid"])

    def test_role_reversal_requires_actual_a_to_b_and_b_to_a(self):
        a = actor("model-a", "family-a")
        b = actor("model-b", "family-b")
        first = run(builder=a, reviewer=b, role_assignment_id="A-B")
        second = run(builder=b, reviewer=a, role_assignment_id="B-A")
        second["builder_artifact_hash"] = "artifact-hash-b"
        second["reviewer_input"]["builder_artifact_hash"] = "artifact-hash-b"
        result = validate_role_reversal([first, second])
        self.assertTrue(result["valid"])

    def test_role_reversal_rejects_nominal_pair_without_swapped_models(self):
        first = run()
        second = copy.deepcopy(first)
        second["role_assignment_id"] = "B-A"
        result = validate_role_reversal([first, second])
        self.assertFalse(result["valid"])

    def test_role_reversal_must_use_matched_requirements(self):
        a = actor("model-a", "family-a")
        b = actor("model-b", "family-b")
        first = run(builder=a, reviewer=b)
        second = run(builder=b, reviewer=a, requirements_hash="different")
        second["builder_artifact_hash"] = "artifact-hash-b"
        second["reviewer_input"] = {"builder_artifact_hash": "artifact-hash-b", "requirements_hash": "different"}
        self.assertFalse(validate_role_reversal([first, second])["valid"])


if __name__ == "__main__":
    unittest.main()
