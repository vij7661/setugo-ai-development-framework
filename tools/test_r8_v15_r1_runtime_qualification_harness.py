from __future__ import annotations
import copy, unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from r8_v15_r1_runtime_qualification_harness import load_matrix, validate_evidence


class HarnessTests(unittest.TestCase):
    def base(self):
        matrix = load_matrix()
        return {"schema": "r8/v1", "candidate_commit": matrix["candidate_commit"], "run_id": "run-1",
                "toolchain": {"python": "test"}, "environment": {"platform": "offline"},
                "arms": [{"id": "candidate_immutability", "fault_proof": {"kind": "git"}}],
                "independent_review": False}

    def test_valid_shape_is_still_non_authoritative(self):
        validate_evidence(self.base(), expected_candidate=load_matrix()["candidate_commit"])

    def test_stale_candidate_rejected(self):
        data = self.base(); data["candidate_commit"] = "stale"
        with self.assertRaises(ValueError): validate_evidence(data, expected_candidate=load_matrix()["candidate_commit"])

    def test_missing_fault_proof_rejected(self):
        data = self.base(); data["arms"] = [{"id": "candidate_immutability"}]
        with self.assertRaises(ValueError): validate_evidence(data, expected_candidate=load_matrix()["candidate_commit"])

    def test_independent_review_cannot_be_preclaimed(self):
        data = self.base(); data["independent_review"] = True
        with self.assertRaises(ValueError): validate_evidence(data, expected_candidate=load_matrix()["candidate_commit"])


if __name__ == "__main__": unittest.main()
