from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path("governance-runtime/review-trust-kernel/memory_admissibility_v1.py")


def load_module(repo_root):
    spec = importlib.util.spec_from_file_location("memory_admissibility_v1", repo_root / MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class MemoryAdmissibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo_root = Path(__file__).resolve().parents[2]
        cls.m = load_module(cls.repo_root)

    def frozen(self):
        return [{"evidence_id":"e1","claim":"authoritative current behavior"}]

    def context(self, **extra):
        item={"memory_id":"m1","authority_class":"CONTEXT_ONLY","claim":"memory claim"}
        item.update(extra)
        return item

    def governed(self, **extra):
        item={"memory_id":"m2","authority_class":"GOVERNED_EVIDENCE","evidence_id":"e2","provenance":"repo:path@sha","content_sha256":"abc123"}
        item.update(extra)
        return item

    def test_l12_01_stale_memory_cannot_satisfy_missing_mandatory_evidence(self):
        r=self.m.evaluate_admissibility(mandatory_evidence_ids=["e1","e2"],frozen_evidence=self.frozen(),memory_items=[self.context(claim="stale e2")],frozen_disposition="PASS")
        self.assertEqual(r["missing_mandatory_evidence_ids"],["e2"])
        self.assertFalse(r["promotable"])

    def test_l12_02_correct_memory_cannot_satisfy_missing_mandatory_evidence(self):
        r=self.m.evaluate_admissibility(mandatory_evidence_ids=["e2"],frozen_evidence=[],memory_items=[self.context(claim="correct e2")],frozen_disposition="PASS")
        self.assertEqual(r["missing_mandatory_evidence_ids"],["e2"])
        self.assertFalse(r["promotable"])

    def test_l12_03_conflicting_memory_cannot_override_frozen_evidence(self):
        winner=self.m.evidence_winner(frozen_claim="FROZEN_CURRENT",memory_claims=[self.context(claim="WRONG_MEMORY")])
        self.assertEqual(winner,"FROZEN_CURRENT")

    def test_l12_04_memory_cannot_promote_insufficient_evidence_review(self):
        r=self.m.evaluate_admissibility(mandatory_evidence_ids=["e1"],frozen_evidence=self.frozen(),memory_items=[self.context(last_known_decision="PROMOTED")],frozen_disposition="INSUFFICIENT_EVIDENCE")
        self.assertFalse(r["promotable"])

    def test_l12_05_governed_materialized_memory_evidence_may_be_admissible(self):
        r=self.m.evaluate_admissibility(mandatory_evidence_ids=["e2"],frozen_evidence=[],memory_items=[self.governed()],frozen_disposition="PASS")
        self.assertEqual(r["missing_mandatory_evidence_ids"],[])
        self.assertTrue(r["promotable"])

    def test_l12_06_malformed_authority_metadata_fails_closed(self):
        with self.assertRaises(ValueError):
            self.m.evaluate_admissibility(mandatory_evidence_ids=[],frozen_evidence=[],memory_items=[{"memory_id":"m3","authority_class":"PROMOTED"}],frozen_disposition="PASS")

    def test_l12_07_memory_promoted_label_has_no_authority(self):
        r=self.m.evaluate_admissibility(mandatory_evidence_ids=["e2"],frozen_evidence=[],memory_items=[self.context(review_status="PROMOTED")],frozen_disposition="PASS")
        self.assertFalse(r["promotable"])

    def test_l12_08_memory_reviewer_consensus_has_no_authority(self):
        r=self.m.evaluate_admissibility(mandatory_evidence_ids=["e2"],frozen_evidence=[],memory_items=[self.context(reviewer_consensus="4/4 PASS")],frozen_disposition="PASS")
        self.assertFalse(r["promotable"])

    def test_l12_09_memory_ci_pass_has_no_semantic_authority(self):
        r=self.m.evaluate_admissibility(mandatory_evidence_ids=["e2"],frozen_evidence=[],memory_items=[self.context(ci_status="387/387 PASS")],frozen_disposition="PASS")
        self.assertFalse(r["promotable"])

    def test_l12_10_decision_is_byte_stable(self):
        kwargs=dict(mandatory_evidence_ids=["e2","e1"],frozen_evidence=self.frozen(),memory_items=[self.context()],frozen_disposition="PASS")
        a=self.m.evaluate_admissibility(**kwargs)
        b=self.m.evaluate_admissibility(**kwargs)
        self.assertEqual(a,b)
        self.assertEqual(a["decision_sha256"],b["decision_sha256"])

    def test_l12_11_governed_memory_requires_provenance(self):
        with self.assertRaises(ValueError):
            self.m.evaluate_admissibility(mandatory_evidence_ids=["e2"],frozen_evidence=[],memory_items=[{"memory_id":"m2","authority_class":"GOVERNED_EVIDENCE","evidence_id":"e2"}],frozen_disposition="PASS")

    def test_l12_12_context_memory_is_explicitly_reported_non_authoritative(self):
        r=self.m.evaluate_admissibility(mandatory_evidence_ids=["e1"],frozen_evidence=self.frozen(),memory_items=[self.context()],frozen_disposition="PASS")
        self.assertFalse(r["memory_independent_authority"])
        self.assertEqual(r["context_only_memory_ids"],["m1"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
