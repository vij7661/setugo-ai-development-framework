import unittest

from calibrate_review_trigger import TriggerCase, evaluate_strategy, threshold_sweep


def c(case_id, *, correct, entropy, sufficient=True, policy=False):
    return TriggerCase(case_id, correct, entropy, sufficient, policy)


class ExpLTriggerCalibrationTests(unittest.TestCase):
    def test_r1_only_exposes_stable_wrong_false_green(self):
        rows = [c("stable-wrong", correct=False, entropy=0.0)]
        r = evaluate_strategy(rows, strategy="R1_ONLY")
        self.assertEqual(("stable-wrong",), r.r1_false_green_case_ids)

    def test_semantic_only_misses_stable_wrong_when_threshold_positive(self):
        rows = [c("stable-wrong", correct=False, entropy=0.0)]
        r = evaluate_strategy(rows, strategy="SEMANTIC_ONLY", semantic_threshold=0.5)
        self.assertEqual(("stable-wrong",), r.r1_false_green_case_ids)

    def test_governance_override_reviews_stable_wrong_high_risk_case(self):
        rows = [c("stable-wrong-high", correct=False, entropy=0.0, policy=True)]
        r = evaluate_strategy(rows, strategy="GOVERNED_CONDITIONAL", semantic_threshold=0.5)
        self.assertEqual(("stable-wrong-high",), r.reviewed_case_ids)
        self.assertEqual((), r.r1_false_green_case_ids)

    def test_insufficient_samples_trigger_review(self):
        rows = [c("insufficient", correct=True, entropy=None, sufficient=False)]
        r = evaluate_strategy(rows, strategy="SEMANTIC_ONLY", semantic_threshold=0.5)
        self.assertEqual(("insufficient",), r.reviewed_case_ids)

    def test_always_review_counts_correct_case_as_unnecessary_for_trigger_metric(self):
        rows = [c("clean", correct=True, entropy=0.0)]
        r = evaluate_strategy(rows, strategy="ALWAYS_REVIEW")
        self.assertEqual(("clean",), r.unnecessary_review_case_ids)

    def test_threshold_sweep_keeps_governance_and_semantic_arms_separate(self):
        rows = [
            c("stable-wrong", correct=False, entropy=0.0, policy=True),
            c("unstable-wrong", correct=False, entropy=0.8),
            c("stable-correct", correct=True, entropy=0.0),
        ]
        sweep = threshold_sweep(rows, [0.5])
        semantic = next(x for x in sweep if x["strategy"] == "SEMANTIC_ONLY")
        governed = next(x for x in sweep if x["strategy"] == "GOVERNED_CONDITIONAL")
        self.assertIn("stable-wrong", semantic["r1_false_green_case_ids"])
        self.assertNotIn("stable-wrong", governed["r1_false_green_case_ids"])

    def test_invalid_entropy_rejected(self):
        with self.assertRaises(ValueError):
            evaluate_strategy([c("x", correct=True, entropy=1.5)], strategy="R1_ONLY")

    def test_conditional_strategy_requires_explicit_threshold(self):
        with self.assertRaises(ValueError):
            evaluate_strategy([c("x", correct=True, entropy=0.1)], strategy="SEMANTIC_ONLY")


if __name__ == "__main__":
    unittest.main()
