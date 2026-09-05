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
    }
    value.update(overrides)
    return value


class ExpFReviewerPerformanceTests(unittest.TestCase):
    def test_self_reported_low_rate_cannot_make_reviewer_eligible(self):
        result = evaluate_review_convergence(policy(), [review("r1")], [])
        self.assertEqual("CONTINUE_REVIEW", result["decision"])
        self.assertEqual(["r1"], result["missing_performance_evidence"])

    def test_unadjudicated_performance_record_is_ignored(self):
        result = evaluate_review_convergence(policy(), [review("r1")], [perf("r1", independently_adjudicated=False)])
        self.assertEqual(["r1"], result["missing_performance_evidence"])

    def test_wrong_role_performance_cannot_transfer(self):
        result = evaluate_review_convergence(policy(), [review("r1")], [perf("r1", role="BUILDER")])
        self.assertEqual(["r1"], result["missing_performance_evidence"])

    def test_wrong_task_class_performance_cannot_transfer(self):
        result = evaluate_review_convergence(policy(), [review("r1")], [perf("r1", task_class="ARCHITECTURE_REVIEW")])
        self.assertEqual(["r1"], result["missing_performance_evidence"])

    def test_wrong_risk_tier_performance_cannot_transfer(self):
        result = evaluate_review_convergence(policy(), [review("r1")], [perf("r1", risk_tier="LOW")])
        self.assertEqual(["r1"], result["missing_performance_evidence"])

    def test_missing_risk_tier_policy_fails_closed(self):
        with self.assertRaises(ValueError):
            evaluate_review_convergence(policy(risk_tier=""), [review("r1")], [perf("r1")])

    def test_missing_evidence_ref_is_not_qualified(self):
        result = evaluate_review_convergence(policy(), [review("r1")], [perf("r1", evidence_ref="")])
        self.assertEqual(["r1"], result["missing_performance_evidence"])

    def test_latest_performance_epoch_controls_eligibility(self):
        records = [perf("r1", rate=0.01, performance_epoch=1), perf("r1", rate=0.40, performance_epoch=2)]
        result = evaluate_review_convergence(policy(), [review("r1")], records)
        self.assertEqual(["r1"], result["demoted_reviewers"])

    def test_later_independent_epoch_can_restore_reviewer(self):
        records = [perf("r1", rate=0.40, performance_epoch=1), perf("r1", rate=0.01, performance_epoch=2)]
        result = evaluate_review_convergence(policy(), [review("r1")], records)
        self.assertEqual([], result["demoted_reviewers"])
        self.assertEqual(1, result["qualified_reviews"])

    def test_review_cannot_override_bad_external_performance(self):
        records = [perf("r1", rate=0.50)]
        result = evaluate_review_convergence(policy(), [review("r1", false_positive_rate=0.0)], records)
        self.assertEqual(["r1"], result["demoted_reviewers"])

    def test_two_independently_qualified_reviewers_can_converge(self):
        reviews = [review("r1"), review("r2")]
        records = [perf("r1", rate=0.02), perf("r2", rate=0.03)]
        result = evaluate_review_convergence(policy(), reviews, records)
        self.assertEqual("CONVERGED_PASS", result["decision"])


if __name__ == "__main__":
    unittest.main()
