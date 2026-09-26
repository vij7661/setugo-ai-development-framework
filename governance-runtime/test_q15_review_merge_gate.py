from pathlib import Path
import unittest

from q15_review_merge_gate import review_merge_evidence_eligible


class Q15ReviewMergeGateTests(unittest.TestCase):
    def test_preserved_changes_required_review_is_not_eligible(self):
        self.assertFalse(review_merge_evidence_eligible(
            review_path=Path("governance-r8/R8-V15-R1-Q14-INDEPENDENT-REVIEW-001.txt"),
            freeze_attestation_path=Path("governance-r8/freeze-attestations/Q14-FREEZE-ATTESTATION.json"),
        ))


if __name__ == "__main__":
    unittest.main()
