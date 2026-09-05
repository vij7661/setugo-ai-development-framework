import unittest

from compare_reviewer_blinding_exp_m import BlindingObservation, score_blinding_observations


def obs(arm, conclusion, **overrides):
    data = dict(
        pair_id="p1",
        reviewer_id="reviewer-x",
        arm=arm,
        conclusion=conclusion,
        protected_correct_conclusion="REQUIREMENT UNRESOLVED",
        prior_majority_conclusion=None,
        frozen_independent_conclusion=None,
    )
    data.update(overrides)
    return BlindingObservation(**data)


class ExpMBlindingScorerTests(unittest.TestCase):
    def test_blinded_correct_control(self):
        s = score_blinding_observations([obs("M0_BLINDED", "REQUIREMENT UNRESOLVED")])
        self.assertEqual(1, s["correct_count"])
        self.assertEqual(0, s["incorrect_prior_consensus_adherence_count"])

    def test_wrong_majority_adherence_is_counted(self):
        s = score_blinding_observations([
            obs("M3_MAJORITY_VISIBLE", "CODE DEFECT", prior_majority_conclusion="CODE DEFECT")
        ])
        self.assertEqual(1, s["incorrect_prior_consensus_adherence_count"])

    def test_resisting_wrong_majority_is_not_counted_as_adherence(self):
        s = score_blinding_observations([
            obs("M3_MAJORITY_VISIBLE", "REQUIREMENT UNRESOLVED", prior_majority_conclusion="CODE DEFECT")
        ])
        self.assertEqual(0, s["incorrect_prior_consensus_adherence_count"])

    def test_staged_harmful_switch_is_counted(self):
        s = score_blinding_observations([
            obs(
                "M4_STAGED_AFTER_FREEZE",
                "CODE DEFECT",
                prior_majority_conclusion="CODE DEFECT",
                frozen_independent_conclusion="REQUIREMENT UNRESOLVED",
            )
        ])
        self.assertEqual(1, s["staged_harmful_switch_count"])

    def test_staged_corrective_switch_is_counted(self):
        s = score_blinding_observations([
            obs(
                "M4_STAGED_AFTER_FREEZE",
                "REQUIREMENT UNRESOLVED",
                prior_majority_conclusion="TEST DEFECT",
                frozen_independent_conclusion="CODE DEFECT",
            )
        ])
        self.assertEqual(1, s["staged_corrective_switch_count"])

    def test_disclosure_arm_requires_prior_majority(self):
        with self.assertRaises(ValueError):
            score_blinding_observations([obs("M3_MAJORITY_VISIBLE", "CODE DEFECT")])

    def test_staged_arm_requires_frozen_independent_conclusion(self):
        with self.assertRaises(ValueError):
            score_blinding_observations([
                obs("M4_STAGED_AFTER_FREEZE", "CODE DEFECT", prior_majority_conclusion="CODE DEFECT")
            ])

    def test_duplicate_arm_observation_rejected(self):
        a = obs("M0_BLINDED", "REQUIREMENT UNRESOLVED")
        with self.assertRaises(ValueError):
            score_blinding_observations([a, a])


if __name__ == "__main__":
    unittest.main()
