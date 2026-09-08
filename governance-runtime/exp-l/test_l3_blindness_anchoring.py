from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path("governance-runtime/review-trust-kernel/blind_packet_v1.py")


def load_module(repo_root):
    spec = importlib.util.spec_from_file_location("blind_packet_v1", repo_root / MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class L3BlindnessAnchoringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo_root = Path(__file__).resolve().parents[2]
        cls.m = load_module(cls.repo_root)

    def base(self, blind=True, **extra):
        p = {
            "schema_version": 1,
            "review_id": "REV-L3-001",
            "candidate_sha": "cand",
            "base_sha": "base",
            "decision_target": "Determine authoritative behavior",
            "evidence": [{"id": "e1", "claim": "fact"}],
            "blind_review_required": blind,
        }
        p.update(extra)
        return p

    def test_l3_01_blind_strips_proposer_identity(self):
        out = self.m.build_reviewer_packet(self.base(proposer_identity="Alice"))
        self.assertNotIn("proposer_identity", out)

    def test_l3_02_blind_strips_proposer_conclusion(self):
        out = self.m.build_reviewer_packet(self.base(proposer_conclusion="PASS"))
        self.assertNotIn("proposer_conclusion", out)

    def test_l3_03_blind_strips_prior_reviewer_verdict(self):
        out = self.m.build_reviewer_packet(self.base(prior_reviewer_verdict="PASS"))
        self.assertNotIn("prior_reviewer_verdict", out)

    def test_l3_04_blind_strips_consensus_and_promotion(self):
        out = self.m.build_reviewer_packet(self.base(reviewer_consensus="4/4 PASS", promotion_state="PROMOTED"))
        self.assertNotIn("reviewer_consensus", out)
        self.assertNotIn("promotion_state", out)

    def test_l3_05_blind_preserves_target_and_evidence(self):
        src = self.base(proposer_conclusion="FAIL")
        out = self.m.build_reviewer_packet(src)
        self.assertEqual(out["decision_target"], src["decision_target"])
        self.assertEqual(out["evidence"], src["evidence"])

    def test_l3_06_exposed_arm_retains_anchor_fields(self):
        out = self.m.build_reviewer_packet(self.base(False, proposer_identity="Alice", proposer_conclusion="PASS"))
        self.assertEqual(out["proposer_identity"], "Alice")
        self.assertEqual(out["proposer_conclusion"], "PASS")

    def test_l3_07_unknown_field_fails_closed(self):
        with self.assertRaises(ValueError):
            self.m.build_reviewer_packet(self.base(new_authority_signal="PASS"))

    def test_l3_08_validation_detects_manual_leak(self):
        packet = self.m.build_reviewer_packet(self.base())
        packet["proposer_conclusion"] = "PASS"
        result = self.m.validate_blind_packet(packet)
        self.assertFalse(result["valid"])
        self.assertIn("proposer_conclusion", result["leaked_anchor_fields"])

    def test_l3_09_packet_hash_is_deterministic(self):
        a = self.m.build_reviewer_packet(self.base(proposer_identity="Alice"))
        b = self.m.build_reviewer_packet(self.base(proposer_identity="Alice"))
        self.assertEqual(a["packet_sha256"], b["packet_sha256"])

    def test_l3_10_blind_and_exposed_have_distinct_hashes(self):
        a = self.m.build_reviewer_packet(self.base(True, proposer_conclusion="PASS"))
        b = self.m.build_reviewer_packet(self.base(False, proposer_conclusion="PASS"))
        self.assertNotEqual(a["packet_sha256"], b["packet_sha256"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
