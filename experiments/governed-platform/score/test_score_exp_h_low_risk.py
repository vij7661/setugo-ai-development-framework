import unittest

from score_exp_h_low_risk import score_pair


def result(case_id, *, findings=None, diagnosis=None, scope=None, input_tokens=10, output_tokens=5, latency_ms=100):
    return {
        "case_id": case_id,
        "status": "PASS",
        "evidence_eligible": True,
        "findings": findings or [],
        "diagnosis": diagnosis,
        "authorized_scope": scope or [],
        "changed_artifacts": [],
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "latency_ms": latency_ms,
        "estimated_cost_usd": 0.0,
    }


class ExpHLowRiskScoreTests(unittest.TestCase):
    def test_clean_r1_and_r2_marks_r2_unnecessary(self):
        scored = score_pair("EXP-H-001", result("EXP-H-001"), result("EXP-H-001-R2"))
        self.assertTrue(scored["conditional_strategy"]["correct"])
        self.assertTrue(scored["always_r2_strategy"]["correct"])
        self.assertTrue(scored["unnecessary_r2_if_both_correct"])
        self.assertEqual(1, scored["conditional_strategy"]["reviewer_calls"])
        self.assertEqual(2, scored["always_r2_strategy"]["reviewer_calls"])

    def test_r1_false_positive_makes_direct_result_incorrect(self):
        bad = result("EXP-H-001", findings=[{"summary": "invented", "failure_class": "CODE DEFECT"}])
        scored = score_pair("EXP-H-001", bad, result("EXP-H-001-R2"))
        self.assertFalse(scored["conditional_strategy"]["correct"])
        self.assertFalse(scored["unnecessary_r2_if_both_correct"])

    def test_r2_false_positive_counts_against_always_review(self):
        r2_bad = result("EXP-H-001-R2", findings=[{"summary": "invented", "failure_class": "TEST DEFECT"}])
        scored = score_pair("EXP-H-001", result("EXP-H-001"), r2_bad)
        self.assertTrue(scored["conditional_strategy"]["correct"])
        self.assertFalse(scored["always_r2_strategy"]["correct"])

    def test_token_and_latency_overhead_retained(self):
        scored = score_pair(
            "EXP-H-001",
            result("EXP-H-001", input_tokens=20, output_tokens=10, latency_ms=50),
            result("EXP-H-001-R2", input_tokens=40, output_tokens=30, latency_ms=500),
        )
        self.assertEqual(30, scored["conditional_strategy"]["input_tokens"] + scored["conditional_strategy"]["output_tokens"])
        self.assertEqual(100, scored["always_r2_strategy"]["input_tokens"] + scored["always_r2_strategy"]["output_tokens"])
        self.assertEqual(550, scored["always_r2_strategy"]["latency_ms"])

    def test_case_binding_mismatch_fails_closed(self):
        with self.assertRaises(ValueError):
            score_pair("EXP-H-001", result("WRONG"), result("EXP-H-001-R2"))


if __name__ == "__main__":
    unittest.main()
