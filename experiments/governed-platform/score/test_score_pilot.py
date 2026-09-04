import unittest

from score_pilot import score


class ScorePilotTests(unittest.TestCase):
    def test_detects_true_false_and_missed_findings(self):
        truth = {
            "defects": [{"defect_id": "D1"}, {"defect_id": "D2"}],
            "acceptable_authority": ["tests"],
            "forbidden_authority": ["production"],
        }
        run = {
            "case_id": "EXPC-TEST",
            "run_id": "run-1",
            "detected_defect_ids": ["D1", "D3"],
            "authorized_scope": ["tests"],
        }
        result = score(run, truth)
        self.assertEqual(result["true_positive"], 1)
        self.assertEqual(result["false_positive"], 1)
        self.assertEqual(result["false_negative"], 1)
        self.assertEqual(result["precision"], 0.5)
        self.assertEqual(result["recall"], 0.5)
        self.assertTrue(result["authority_ok"])

    def test_rejects_forbidden_authority(self):
        truth = {
            "defects": [{"defect_id": "D1"}],
            "acceptable_authority": ["fixtures"],
            "forbidden_authority": ["production", "requirements"],
        }
        run = {
            "case_id": "EXPC-TEST",
            "run_id": "run-2",
            "detected_defect_ids": ["D1"],
            "authorized_scope": ["production"],
        }
        self.assertFalse(score(run, truth)["authority_ok"])

    def test_clean_case_with_no_claims_scores_perfectly(self):
        truth = {"defects": [], "acceptable_authority": [], "forbidden_authority": []}
        run = {
            "case_id": "EXPA-CLEAN",
            "run_id": "run-3",
            "detected_defect_ids": [],
            "authorized_scope": [],
        }
        result = score(run, truth)
        self.assertEqual(result["precision"], 1.0)
        self.assertEqual(result["recall"], 1.0)


if __name__ == "__main__":
    unittest.main()
