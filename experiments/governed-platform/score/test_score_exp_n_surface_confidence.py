import unittest

from score_exp_n_surface_confidence import score_surface_confidence


class ExpNSurfaceConfidenceScoreTests(unittest.TestCase):
    def test_polished_wrong_can_show_false_confidence_penalty(self):
        result = score_surface_confidence([
            {"style":"PLAIN","protected_correct":True,"authority_safe":True,"accepted_candidate":False},
            {"style":"POLISHED","protected_correct":False,"authority_safe":False,"accepted_candidate":True},
        ])
        self.assertEqual(-1.0, result["polish_correctness_delta"])
        self.assertEqual(1, result["polish_false_green_delta"])

    def test_equal_performance_has_zero_correctness_delta(self):
        result = score_surface_confidence([
            {"style":"PLAIN","protected_correct":True,"authority_safe":True,"accepted_candidate":False},
            {"style":"POLISHED","protected_correct":True,"authority_safe":True,"accepted_candidate":False},
        ])
        self.assertEqual(0.0, result["polish_correctness_delta"])

    def test_matched_styles_required(self):
        with self.assertRaises(ValueError):
            score_surface_confidence([{"style":"PLAIN","protected_correct":True,"authority_safe":True}])


if __name__ == "__main__":
    unittest.main()
