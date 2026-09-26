from __future__ import annotations
import unittest, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from r8_release_qualification_gate import evaluate

class ReleaseGateTests(unittest.TestCase):
    def base(self):
        return {"schema": "release/v1", "candidate_commit": "a" * 40, "candidate_tree": "b" * 40,
                "artifact_sha256": "c" * 64, "sbom_sha256": "d" * 64, "test_evidence_sha256": "e" * 64,
                "runtime_evidence_sha256": "f" * 64, "unresolved_findings": [], "independent_review": True,
                "release_authorized": False}
    def test_qualified_is_not_authorized(self):
        self.assertFalse(evaluate(self.base(), expected_commit="a"*40, expected_tree="b"*40)["release_authorized"])
    def test_stale_build_rejected(self):
        x=self.base(); x["artifact_sha256"]="short"
        with self.assertRaises(ValueError): evaluate(x, expected_commit="a"*40, expected_tree="b"*40)
    def test_skipped_review_rejected(self):
        x=self.base(); x["independent_review"]=False
        with self.assertRaises(ValueError): evaluate(x, expected_commit="a"*40, expected_tree="b"*40)
    def test_self_approval_rejected(self):
        x=self.base(); x["release_authorized"]=True
        with self.assertRaises(ValueError): evaluate(x, expected_commit="a"*40, expected_tree="b"*40)

if __name__ == "__main__": unittest.main()
