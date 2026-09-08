from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

MODULE = Path("governance-runtime/review-trust-kernel/integrated_review_path_v1.py")


def load(repo):
    spec=importlib.util.spec_from_file_location("integrated_review_path_v1", repo/MODULE)
    m=importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(m)
    return m


class IQR1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo=Path(__file__).resolve().parents[2]
        cls.m=load(cls.repo)

    def source(self, **extra):
        x={
          "review_id":"REV-GOV-PR11-IQR1-R2",
          "candidate_sha":"b3abfed189504721b30c9ed647b2ffe79f27f85c",
          "base_sha":"f0bb95a5b4902b76efceca2f36e27d3512e0bbc7",
          "decision_target":"Determine whether PR11 is promotable under the qualified review path.",
          "evidence":[{"evidence_id":"e1","content":"frozen governed evidence"}],
          "blind_review_required":True,
        }
        x.update(extra); return x

    def policy(self):
        return {"risk_class":"PROMOTION_AUTHORITY","promotion_authoritative":True,"policy_requires_dual_review":True}

    def frozen(self):
        return {"candidate_sha":"b3abfed189504721b30c9ed647b2ffe79f27f85c","base_sha":"f0bb95a5b4902b76efceca2f36e27d3512e0bbc7","evidence_manifest_hash":"sha256:m","corpus_hash":"sha256:c"}

    def r2(self, disposition="PASS"):
        return {"review_id":"REV-GOV-PR11-IQR1-R2","disposition":disposition,"findings":[],"evidence_ids":["e1"],"uncertainties":[]}

    def test_01_blind_anchor_fields_removed(self):
        r=self.m.construct_r2_packet(source_packet=self.source(proposer_identity="CTO",proposer_conclusion="PASS"),mandatory_evidence_ids=["e1"],memory_items=[])
        self.assertNotIn("proposer_identity",r["reviewer_packet"]); self.assertNotIn("proposer_conclusion",r["reviewer_packet"])

    def test_02_unknown_source_field_fails_closed(self):
        with self.assertRaises(ValueError): self.m.construct_r2_packet(source_packet=self.source(unregistered="x"),mandatory_evidence_ids=["e1"],memory_items=[])

    def test_03_missing_mandatory_evidence_blocks_before_review(self):
        with self.assertRaises(ValueError): self.m.construct_r2_packet(source_packet=self.source(),mandatory_evidence_ids=["e1","e2"],memory_items=[])

    def test_04_context_memory_cannot_fill_evidence_gap(self):
        mem=[{"memory_id":"m1","authority_class":"CONTEXT_ONLY","claim":"e2 exists"}]
        with self.assertRaises(ValueError): self.m.construct_r2_packet(source_packet=self.source(),mandatory_evidence_ids=["e1","e2"],memory_items=mem)

    def test_05_evidence_isolation_enabled(self):
        r=self.m.construct_r2_packet(source_packet=self.source(),mandatory_evidence_ids=["e1"],memory_items=[])
        self.assertTrue(r["isolated_evidence_packet"]["evidence_is_untrusted_data"])

    def test_06_promotion_policy_always_requires_r3(self):
        h=self.m.construct_r3_handoff(review_request={"id":"x"},frozen_packet=self.frozen(),policy=self.policy(),r2_result=self.r2("PASS"))
        self.assertTrue(h["r3_required"])

    def test_07_r2_block_does_not_skip_r3(self):
        h=self.m.construct_r3_handoff(review_request={"id":"x"},frozen_packet=self.frozen(),policy=self.policy(),r2_result=self.r2("BLOCK"))
        self.assertTrue(h["r3_required"])

    def test_08_r1_middle_opinion_rejected(self):
        bad=self.r2(); bad["r1_opinion"]="approve"
        with self.assertRaises(ValueError): self.m.construct_r3_handoff(review_request={"id":"x"},frozen_packet=self.frozen(),policy=self.policy(),r2_result=bad)

    def test_09_unknown_r2_field_rejected(self):
        bad=self.r2(); bad["new_material_field"]="x"
        with self.assertRaises(ValueError): self.m.construct_r3_handoff(review_request={"id":"x"},frozen_packet=self.frozen(),policy=self.policy(),r2_result=bad)

    def test_10_final_requires_both_pass(self):
        h=self.m.construct_r3_handoff(review_request={"id":"x"},frozen_packet=self.frozen(),policy=self.policy(),r2_result=self.r2())
        out=self.m.final_adjudication(r2_result=self.r2(),r3_result={"review_id":"R3","disposition":"BLOCK"},handoff=h,mandatory_evidence_ids=["e1"],frozen_evidence=self.source()["evidence"],memory_items=[])
        self.assertFalse(out["promotable"])

    def test_11_final_pass_requires_complete_evidence(self):
        h=self.m.construct_r3_handoff(review_request={"id":"x"},frozen_packet=self.frozen(),policy=self.policy(),r2_result=self.r2())
        out=self.m.final_adjudication(r2_result=self.r2(),r3_result={"review_id":"R3","disposition":"PASS"},handoff=h,mandatory_evidence_ids=["e1"],frozen_evidence=self.source()["evidence"],memory_items=[])
        self.assertTrue(out["promotable"])

    def test_12_final_memory_never_independent_authority(self):
        h=self.m.construct_r3_handoff(review_request={"id":"x"},frozen_packet=self.frozen(),policy=self.policy(),r2_result=self.r2())
        out=self.m.final_adjudication(r2_result=self.r2(),r3_result={"review_id":"R3","disposition":"PASS"},handoff=h,mandatory_evidence_ids=["e1"],frozen_evidence=self.source()["evidence"],memory_items=[{"memory_id":"m1","authority_class":"CONTEXT_ONLY"}])
        self.assertFalse(out["memory_independent_authority"])

if __name__ == "__main__": unittest.main(verbosity=2)
