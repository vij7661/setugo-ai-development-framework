import math
import unittest

from review_efficiency import EfficiencyCase, compare_conditional, summarize


def c(case_id, strategy, *, fg=False, defects=0, calls=1, prompt=100, completion=50, cost=100, latency=1000, price="v1"):
    return EfficiencyCase(
        case_id=case_id,
        strategy=strategy,
        false_green=fg,
        true_material_defects_found=defects,
        reviewer_calls=calls,
        prompt_tokens=prompt,
        completion_tokens=completion,
        cost_microunits=cost,
        latency_ms=latency,
        price_version=price,
    )


class ExpKReviewEfficiencyTests(unittest.TestCase):
    def test_k001_conditional_can_avoid_clean_case_review_overhead(self):
        s = summarize([
            c("x-r1", "R1_ONLY", calls=1, cost=100),
            c("x-all", "ALWAYS_THREE", calls=3, cost=300, prompt=300, completion=150),
            c("x-cond", "CONDITIONAL", calls=1, cost=100),
        ])
        cmp = compare_conditional(s)
        self.assertTrue(cmp["conditional_cheaper_than_always_three"])
        self.assertTrue(cmp["conditional_uses_fewer_tokens_than_always_three"])

    def test_k002_added_r2_defect_discovery_has_marginal_cost(self):
        s = summarize([
            c("a", "R1_ONLY", defects=0, cost=100),
            c("b", "ALWAYS_THREE", defects=1, calls=3, cost=300),
            c("c", "CONDITIONAL", defects=1, calls=2, cost=200),
        ])
        cmp = compare_conditional(s)
        self.assertEqual(100.0, cmp["cost_per_additional_true_defect_microunits"])

    def test_k003_r3_cost_is_not_hidden(self):
        s = summarize([c("c", "CONDITIONAL", defects=1, calls=3, cost=300)])
        self.assertEqual(3.0, s["CONDITIONAL"]["avg_reviewer_calls"])
        self.assertEqual(300.0, s["CONDITIONAL"]["avg_cost_microunits"])

    def test_k004_cheaper_but_more_false_green_is_false_efficiency(self):
        s = summarize([
            c("a", "R1_ONLY", fg=True, cost=100),
            c("b", "ALWAYS_THREE", fg=False, calls=3, cost=300),
            c("c", "CONDITIONAL", fg=True, calls=1, cost=100),
        ])
        cmp = compare_conditional(s)
        self.assertTrue(cmp["conditional_false_efficiency"])
        self.assertFalse(cmp["conditional_not_worse_than_best_observed_false_green"])

    def test_k005_always_three_clean_overhead_is_counted(self):
        s = summarize([c("clean", "ALWAYS_THREE", calls=3, prompt=600, completion=300, cost=450)])
        self.assertEqual(900.0, s["ALWAYS_THREE"]["avg_tokens"])

    def test_k006_retry_or_provider_failure_cost_can_be_retained_as_measured_case(self):
        s = summarize([c("retry", "CONDITIONAL", calls=2, prompt=250, completion=50, cost=180, latency=5000)])
        self.assertEqual(300.0, s["CONDITIONAL"]["avg_tokens"])
        self.assertEqual(5000.0, s["CONDITIONAL"]["avg_latency_ms"])

    def test_k007_missing_price_version_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "price_version"):
            summarize([c("x", "R1_ONLY", price="")])

    def test_k008_mixed_price_versions_are_not_directly_compared(self):
        with self.assertRaisesRegex(ValueError, "mixed price versions"):
            summarize([c("a", "R1_ONLY", price="v1"), c("b", "CONDITIONAL", price="v2")])

    def test_no_extra_defect_means_cost_per_extra_defect_is_infinite(self):
        s = summarize([
            c("a", "R1_ONLY", defects=0, cost=100),
            c("b", "ALWAYS_THREE", defects=0, calls=3, cost=300),
            c("c", "CONDITIONAL", defects=0, calls=2, cost=200),
        ])
        self.assertTrue(math.isinf(compare_conditional(s)["cost_per_additional_true_defect_microunits"]))

    def test_all_three_strategies_required_for_comparison(self):
        s = summarize([c("a", "R1_ONLY")])
        with self.assertRaisesRegex(ValueError, "all three strategies"):
            compare_conditional(s)


if __name__ == "__main__":
    unittest.main()
