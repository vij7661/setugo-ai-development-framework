import unittest

from reviewer_qualification_profile import evaluate_reviewer_eligibility, validate_reviewer_profile


def profile(**overrides):
    value = {
        "reviewer_id": "r1",
        "role": "JUDGE",
        "task_class": "ARCHITECTURE_REVIEW",
        "risk_tier": "HIGH",
        "independently_adjudicated": True,
        "evidence_ref": "perf:r1:1",
        "performance_epoch": 1,
        "sample_count": 40,
        "dimensions": {
            "factuality_quality": 0.90,
            "logical_reasoning_quality": 0.90,
            "requirement_interpretation_quality": 0.90,
            "omission_detection_quality": 0.90,
            "authority_scope_safety": 0.95,
            "provenance_quality": 0.90,
            "discourse_quality": 0.98,
        },
    }
    value.update(overrides)
    return value


def policy(**overrides):
    value = {
        "role": "JUDGE",
        "task_class": "ARCHITECTURE_REVIEW",
        "risk_tier": "HIGH",
        "min_samples": 20,
        "dimension_thresholds": {
            "logical_reasoning_quality": 0.80,
            "requirement_interpretation_quality": 0.85,
            "omission_detection_quality": 0.80,
            "authority_scope_safety": 0.90,
        },
    }
    value.update(overrides)
    return value


class ReviewerQualificationProfileTests(unittest.TestCase):
    def test_good_prose_cannot_compensate_for_unsafe_authority_scope(self):
        p = profile()
        p["dimensions"]["authority_scope_safety"] = 0.40
        p["dimensions"]["discourse_quality"] = 1.0
        result = evaluate_reviewer_eligibility(policy(), p)
        self.assertFalse(result["eligible"])
        self.assertIn("authority_scope_safety", result["failed_dimensions"])

    def test_exact_scope_profile_can_qualify(self):
        self.assertTrue(evaluate_reviewer_eligibility(policy(), profile())["eligible"])

    def test_wrong_task_does_not_transfer(self):
        self.assertFalse(evaluate_reviewer_eligibility(policy(), profile(task_class="FACTUAL_RESEARCH"))["eligible"])

    def test_missing_dimension_fails_closed(self):
        p = profile()
        del p["dimensions"]["provenance_quality"]
        with self.assertRaises(ValueError):
            validate_reviewer_profile(p)

    def test_unadjudicated_profile_fails_closed(self):
        with self.assertRaises(ValueError):
            validate_reviewer_profile(profile(independently_adjudicated=False))

    def test_insufficient_samples_cannot_qualify(self):
        self.assertFalse(evaluate_reviewer_eligibility(policy(), profile(sample_count=5))["eligible"])

    def test_unknown_dimension_threshold_rejected(self):
        with self.assertRaises(ValueError):
            evaluate_reviewer_eligibility(policy(dimension_thresholds={"charisma": 0.9}), profile())


if __name__ == "__main__":
    unittest.main()
