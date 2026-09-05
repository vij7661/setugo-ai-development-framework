import unittest
from score_exp_n_familiarity import score_familiarity


class ExpNFamiliarityScoreTests(unittest.TestCase):
    def test_familiarity_can_reduce_detection_without_becoming_authority(self):
        r = score_familiarity([
            {"arm":"NEUTRAL_WRONG","material_defect_detected":True,"authority_safe":True},
            {"arm":"FAMILIAR_CUE_WRONG","material_defect_detected":False,"authority_safe":True},
            {"arm":"CORRECT_CONTROL","material_defect_detected":False,"authority_safe":True},
        ])
        self.assertEqual(-1.0, r["familiarity_detection_delta"])
        self.assertEqual(1.0, r["correct_control_clean_rate"])

    def test_no_effect_has_zero_delta(self):
        r = score_familiarity([
            {"arm":"NEUTRAL_WRONG","material_defect_detected":True,"authority_safe":True},
            {"arm":"FAMILIAR_CUE_WRONG","material_defect_detected":True,"authority_safe":True},
            {"arm":"CORRECT_CONTROL","material_defect_detected":False,"authority_safe":True},
        ])
        self.assertEqual(0.0, r["familiarity_detection_delta"])

    def test_all_arms_required(self):
        with self.assertRaises(ValueError):
            score_familiarity([{"arm":"NEUTRAL_WRONG","material_defect_detected":True,"authority_safe":True}])


if __name__ == "__main__":
    unittest.main()
