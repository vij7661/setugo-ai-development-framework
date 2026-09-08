from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

MODULE_PATH=Path("governance-runtime/review-trust-kernel/contradiction_reconstruction_v1.py")

def load_module(root):
    spec=importlib.util.spec_from_file_location("l8",root/MODULE_PATH)
    m=importlib.util.module_from_spec(spec); assert spec.loader is not None; spec.loader.exec_module(m); return m

class L8Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.m=load_module(Path(__file__).resolve().parents[2])
    def e(self,i,c,claim,**kw):
        x={"evidence_id":i,"source_class":c,"claim":claim,"provenance":f"repo:{i}@sha"}; x.update(kw); return x
    def test_01_implementation_beats_history(self):
        r=self.m.reconstruct([self.e("h","HISTORICAL_DISCUSSION","OLD"),self.e("i","AUTHORITATIVE_IMPLEMENTATION","NEW")]); self.assertEqual(r["winner_claim"],"NEW")
    def test_02_design_beats_reasoning(self):
        r=self.m.reconstruct([self.e("r","NON_AUTHORITATIVE_REASONING","X"),self.e("d","AUTHORITATIVE_DESIGN","Y")]); self.assertEqual(r["winner_claim"],"Y")
    def test_03_explicit_supersession_removes_old(self):
        r=self.m.reconstruct([self.e("a","AUTHORITATIVE_DESIGN","OLD"),self.e("b","AUTHORITATIVE_DESIGN","NEW",supersedes=["a"])]); self.assertEqual(r["winner_claim"],"NEW"); self.assertIn("a",r["superseded_evidence_ids"])
    def test_04_same_rank_conflict_fails_closed(self):
        r=self.m.reconstruct([self.e("a","AUTHORITATIVE_IMPLEMENTATION","A"),self.e("b","AUTHORITATIVE_IMPLEMENTATION","B")]); self.assertEqual(r["status"],"UNRESOLVED_CONTRADICTION")
    def test_05_same_rank_agreement_resolves(self):
        r=self.m.reconstruct([self.e("a","AUTHORITATIVE_QA","A"),self.e("b","AUTHORITATIVE_QA","A")]); self.assertEqual(r["status"],"RESOLVED")
    def test_06_missing_provenance_rejected(self):
        with self.assertRaises(ValueError): self.m.reconstruct([{"evidence_id":"a","source_class":"AUTHORITATIVE_QA","claim":"A"}])
    def test_07_unknown_class_rejected(self):
        with self.assertRaises(ValueError): self.m.reconstruct([self.e("a","MAGIC","A")])
    def test_08_unknown_superseded_ref_rejected(self):
        with self.assertRaises(ValueError): self.m.reconstruct([self.e("a","AUTHORITATIVE_DESIGN","A",supersedes=["missing"])])
    def test_09_duplicate_id_rejected(self):
        with self.assertRaises(ValueError): self.m.reconstruct([self.e("a","AUTHORITATIVE_QA","A"),self.e("a","AUTHORITATIVE_QA","A")])
    def test_10_proposer_conclusion_not_required(self):
        r=self.m.reconstruct([self.e("i","AUTHORITATIVE_IMPLEMENTATION","A")]); self.assertEqual(r["winner_claim"],"A")

if __name__=="__main__": unittest.main(verbosity=2)
