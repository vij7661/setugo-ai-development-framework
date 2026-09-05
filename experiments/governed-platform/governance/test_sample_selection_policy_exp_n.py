import unittest

from sample_selection_policy import select_evidence, validate_sampling_policy


def sample(ok=True, value="x"):
    return {"status": "PASS" if ok else "ERROR", "evidence_eligible": ok, "value": value}


class SampleSelectionPolicyTests(unittest.TestCase):
    def test_first_valid_is_deterministic(self):
        policy = {"policy_version": "n1", "strategy": "FIRST_VALID", "sample_count": 3}
        self.assertEqual("b", select_evidence(policy, [sample(False,"a"), sample(True,"b"), sample(True,"c")])[0]["value"])

    def test_all_valid_retains_all_eligible_evidence(self):
        policy = {"policy_version": "n1", "strategy": "ALL_VALID_SCORED", "sample_count": 3}
        self.assertEqual(["a","c"], [x["value"] for x in select_evidence(policy, [sample(True,"a"), sample(False,"b"), sample(True,"c")])])

    def test_pre_registered_index_cannot_move_after_results(self):
        policy = {"policy_version": "n1", "strategy": "PRE_REGISTERED_INDEX", "sample_count": 3, "selected_index": 1}
        self.assertEqual(["b"], [x["value"] for x in select_evidence(policy, [sample(True,"a"), sample(True,"b"), sample(True,"c")])])

    def test_post_hoc_best_selection_is_forbidden(self):
        with self.assertRaises(ValueError):
            validate_sampling_policy({"policy_version":"n1","strategy":"ALL_VALID_SCORED","sample_count":5,"prefer_longest":True})

    def test_unknown_strategy_rejected(self):
        with self.assertRaises(ValueError):
            validate_sampling_policy({"policy_version":"n1","strategy":"BEST_LOOKING","sample_count":5})

    def test_observed_count_must_match_frozen_policy(self):
        with self.assertRaises(ValueError):
            select_evidence({"policy_version":"n1","strategy":"ALL_VALID_SCORED","sample_count":3}, [sample(True)])


if __name__ == "__main__":
    unittest.main()
