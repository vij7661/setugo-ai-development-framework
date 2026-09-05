import unittest

from review_convergence import evaluate_review_convergence


def policy(**overrides):
    value = {
        "max_reviews": 3,
        "required_qualified_agreement": 2,
        "false_positive_rate_threshold": 0.10,
        "review_role": "JUDGE",
        "task_class": "SECURITY_REVIEW",
        "risk_tier": "HIGH",
        "min_performance_samples": 20,
        "required_difficulty_bands": ["MEDIUM", "HARD"],
        "min_samples_per_difficulty": 5,
    }
    value.update(overrides)
    return value


def review(reviewer_id, verdict="PASS", **overrides):
    value = {"reviewer_id": reviewer_id, "verdict": verdict, "false_positive_rate": 0.0}
    value.update(overrides)
    return value


def perf(reviewer_id, rate=0.02, **overrides):
    value = {
        "reviewer_id": reviewer_id,
        "false_positive_rate": rate,
        "role": "JUDGE",
        "task_class": "SECURITY_REVIEW",
        "risk_tier": "HIGH",
        "independently_adjudicated": True,
        "evidence_ref": f"perf-{reviewer_id}",
        "performance_epoch": 1,
        "sample_count": 20,
        "difficulty_distribution": {"MEDIUM": 10, "HARD": 10},
    }
    value.update(overrides)
    return value


class ExpFReviewerPerformanceTests(unittest.TestCase):
    def test_self_reported_low_rate_cannot_make_reviewer_eligible(self):
        result = evaluate_review_convergence(policy(), [review("r1")], [])
        self.assertEqual(["r1"], result["missing_performance_evidence"])

    def test_unadjudicated_performance_record_is_ignored(self):
        result = evaluate_review_convergence(policy(), [review("r1")], [perf("r1", independently_adjudicated=False)])
        self.assertEqual(["r1"], result["missing_performance_evidence"])

    def test_wrong_role_performance_cannot_transfer(self):
        self.assertEqual(["r1"], evaluate_review_convergence(policy(), [review("r1")], [perf("r1", role="BUILDER")])["missing_performance_evidence"])

    def test_wrong_task_class_performance_cannot_transfer(self):
        self.assertEqual(["r1"], evaluate_review_convergence(policy(), [review("r1")], [perf("r1", task_class="ARCHITECTURE_REVIEW")])["missing_performance_evidence"])

    def test_wrong_risk_tier_performance_cannot_transfer(self):
        self.assertEqual(["r1"], evaluate_review_convergence(policy(), [review("r1")], [perf("r1", risk_tier="LOW")])["missing_performance_evidence"])

    def test_missing_risk_tier_policy_fails_closed(self):
        with self.assertRaises(ValueError): evaluate_review_convergence(policy(risk_tier=""), [review("r1")], [perf("r1")])

    def test_easy_case_padding_cannot_qualify_high_risk_reviewer(self):
        padded = perf("r1", rate=0.0, sample_count=100, difficulty_distribution={"EASY": 100, "MEDIUM": 0, "HARD": 0})
        result = evaluate_review_convergence(policy(), [review("r1")], [padded])
        self.assertEqual(["r1"], result["missing_performance_evidence"])
        self.assertEqual(0, result["qualified_reviews"])

    def test_insufficient_sample_count_cannot_qualify(self):
        thin = perf("r1", sample_count=4, difficulty_distribution={"MEDIUM": 2, "HARD": 2})
        result = evaluate_review_convergence(policy(), [review("r1")], [thin])
        self.assertEqual(["r1"], result["missing_performance_evidence"])

    def test_missing_evidence_ref_is_not_qualified(self):
        self.assertEqual(["r1"], evaluate_review_convergence(policy(), [review("r1")], [perf("r1", evidence_ref="")])["missing_performance_evidence"])

    def test_latest_performance_epoch_controls_eligibility(self):
        records = [perf("r1", rate=0.01, performance_epoch=1), perf("r1", rate=0.40, performance_epoch=2)]
        self.assertEqual(["r1"], evaluate_review_convergence(policy(), [review("r1")], records)["demoted_reviewers"])

    def test_later_independent_epoch_can_restore_reviewer(self):
        records = [perf("r1", rate=0.40, performance_epoch=1), perf("r1", rate=0.01, performance_epoch=2)]
        result = evaluate_review_convergence(policy(), [review("r1")], records)
        self.assertEqual([], result["demoted_reviewers"])
        self.assertEqual(1, result["qualified_reviews"])

    def test_review_cannot_override_bad_external_performance(self):
        self.assertEqual(["r1"], evaluate_review_convergence(policy(), [review("r1", false_positive_rate=0.0)], [perf("r1", rate=0.50)])["demoted_reviewers"])

    def test_two_independently_qualified_reviewers_can_converge(self):
        result = evaluate_review_convergence(policy(), [review("r1"), review("r2")], [perf("r1", rate=0.02), perf("r2", rate=0.03)])
        self.assertEqual("CONVERGED_PASS", result["decision"])


if __name__ == "__main__": unittest.main()
