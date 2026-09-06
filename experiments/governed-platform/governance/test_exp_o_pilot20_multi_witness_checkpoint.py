from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from multi_witness_checkpoint_exp_o import recover_multi_witness, sign_witness, statement_for_db
from sqlite_process_crash_exp_o import authority_payload, connect, worker_authority, worker_consume, worker_effect
from sqlite_storage_seal_exp_o import init_sealed_db, seal_state

P= "governed-platform"; T="EXP-O-PILOT20"; S="authority-ledger-A"
K1=b"pilot20-w1-key"; K2=b"pilot20-w2-key"; K3=b"pilot20-w3-key"; BAD=b"pilot20-bad-key"

def cfg(revoke=None):
    revoke=set(revoke or [])
    return {"w1":{"key_id":"k1","key":K1,"revoked":"w1" in revoke},"w2":{"key_id":"k2","key":K2,"revoked":"w2" in revoke},"w3":{"key_id":"k3","key":K3,"revoked":"w3" in revoke}}

class ExpOPilot20MultiWitnessCheckpointTests(unittest.TestCase):
    def setUp(self): self.td=tempfile.TemporaryDirectory(); self.root=Path(self.td.name)
    def tearDown(self): self.td.cleanup()
    def db(self,n="case.db"): return self.root/n
    def p(self,**kw):
        d=dict(logical_id="auth-1",term=1,commit_index=1,owner="r1",lease_epoch=1,semantic_digest="semantic-A",effect_digest="effect-A",idempotency_key="intent-1"); d.update(kw); return authority_payload(**d)
    def active(self,path,payload=None):
        payload=payload or self.p(); init_sealed_db(path); self.assertTrue(worker_authority(str(path),payload,None)["authorized"]); seal_state(path); return payload
    def effect(self,path,payload=None,consume=False):
        payload=self.active(path,payload); self.assertTrue(worker_effect(str(path),payload,None)["executed"])
        if consume: self.assertEqual(worker_consume(str(path),payload,None)["decision"],"CONSUMED")
        seal_state(path); return payload
    def stmt(self,path,g=1,project=P,task=T,state=S): return statement_for_db(path,project=project,task=task,logical_state_id=state,generation=g)
    def sig(self,st,w):
        return sign_witness(st,witness_id=w,key_id={"w1":"k1","w2":"k2","w3":"k3"}[w],key={"w1":K1,"w2":K2,"w3":K3}[w])
    def rec(self,path,recs,min_g=1,conf=None): return recover_multi_witness(path,recs,witness_config=conf or cfg(),expected_project=P,expected_task=T,expected_logical_state_id=S,minimum_generation=min_g)

    def test_p20_01_clean_2_of_3_agreeing_witness_control(self):
        p=self.db(); self.active(p); st=self.stmt(p); r=self.rec(p,[self.sig(st,"w1"),self.sig(st,"w2")]); self.assertTrue(r["authorized"]); self.assertEqual(r["witness_voters"],["w1","w2"])
    def test_p20_02_one_valid_witness_only(self):
        p=self.db(); self.active(p); st=self.stmt(p); r=self.rec(p,[self.sig(st,"w1")]); self.assertFalse(r["authorized"]); self.assertEqual(r["reason"],"WITNESS_QUORUM_INSUFFICIENT")
    def test_p20_03_duplicate_same_witness_cannot_manufacture_quorum(self):
        p=self.db(); self.active(p); st=self.stmt(p); a=self.sig(st,"w1"); r=self.rec(p,[a,a]); self.assertFalse(r["authorized"]); self.assertEqual(r["reason"],"WITNESS_QUORUM_INSUFFICIENT")
    def test_p20_04_one_honest_plus_forged_second_witness(self):
        p=self.db(); self.active(p); st=self.stmt(p); forged=sign_witness(st,witness_id="w2",key_id="k2",key=BAD); r=self.rec(p,[self.sig(st,"w1"),forged]); self.assertFalse(r["authorized"])
    def test_p20_05_one_compromised_witness_conflicting_state_insufficient(self):
        p=self.db(); self.active(p); st=self.stmt(p); st["state_root"]="f"*64; evil=self.sig(st,"w3"); r=self.rec(p,[evil]); self.assertFalse(r["authorized"]); self.assertEqual(r["reason"],"WITNESS_QUORUM_INSUFFICIENT")
    def test_p20_06_two_valid_witnesses_different_roots_no_quorum(self):
        p=self.db(); self.active(p); a=self.stmt(p); b=dict(a); b["state_root"]="e"*64; r=self.rec(p,[self.sig(a,"w1"),self.sig(b,"w2")]); self.assertFalse(r["authorized"])
    def test_p20_07_two_valid_witnesses_different_generations_no_quorum(self):
        p=self.db(); self.active(p); a=self.stmt(p,1); b=self.stmt(p,2); r=self.rec(p,[self.sig(a,"w1"),self.sig(b,"w2")]); self.assertFalse(r["authorized"])
    def test_p20_08_two_valid_witnesses_different_scope_no_quorum(self):
        p=self.db(); self.active(p); a=self.stmt(p); b=self.stmt(p,project="wrong"); r=self.rec(p,[self.sig(a,"w1"),self.sig(b,"w2")]); self.assertFalse(r["authorized"])
    def test_p20_09_two_honest_agree_one_compromised_conflicts(self):
        p=self.db(); self.active(p); good=self.stmt(p); bad=dict(good); bad["state_root"]="d"*64; r=self.rec(p,[self.sig(good,"w1"),self.sig(good,"w2"),self.sig(bad,"w3")]); self.assertTrue(r["authorized"]); self.assertEqual(r["witness_voters"],["w1","w2"])
    def test_p20_10_three_records_no_two_agree(self):
        p=self.db(); self.active(p); a=self.stmt(p,1); b=self.stmt(p,2); c=self.stmt(p,3); r=self.rec(p,[self.sig(a,"w1"),self.sig(b,"w2"),self.sig(c,"w3")]); self.assertFalse(r["authorized"])
    def test_p20_11_valid_old_quorum_below_trusted_minimum(self):
        p=self.db(); self.active(p); st=self.stmt(p,1); r=self.rec(p,[self.sig(st,"w1"),self.sig(st,"w2")],min_g=2); self.assertFalse(r["authorized"]); self.assertEqual(r["reason"],"WITNESS_QUORUM_ROLLBACK")
    def test_p20_12_stale_db_resealed_valid_old_quorum_still_rolls_back(self):
        p=self.db(); self.active(p); st=self.stmt(p,1); r=self.rec(p,[self.sig(st,"w1"),self.sig(st,"w2")],min_g=4); self.assertFalse(r["authorized"]); self.assertEqual(r["recovery_status"],"TRUSTED_GENERATION_ROLLBACK_BLOCKED")
    def test_p20_13_coherent_db_rewrite_only_compromised_witness_resigns(self):
        p=self.db(); self.active(p); conn=connect(p); conn.execute("UPDATE authority SET owner='evil'"); conn.close(); seal_state(p); st=self.stmt(p,2); r=self.rec(p,[self.sig(st,"w3")],min_g=2); self.assertFalse(r["authorized"])
    def test_p20_14_coherent_db_rewrite_old_honest_quorum_root_mismatch(self):
        p=self.db(); self.active(p); old=self.stmt(p); recs=[self.sig(old,"w1"),self.sig(old,"w2")]; conn=connect(p); conn.execute("UPDATE authority SET owner='evil'"); conn.close(); seal_state(p); r=self.rec(p,recs); self.assertFalse(r["authorized"]); self.assertEqual(r["reason"],"WITNESS_STATE_ROOT_MISMATCH")
    def test_p20_15_unknown_witness_contributes_zero(self):
        p=self.db(); self.active(p); st=self.stmt(p); unknown=sign_witness(st,witness_id="wx",key_id="kx",key=BAD); r=self.rec(p,[self.sig(st,"w1"),unknown]); self.assertFalse(r["authorized"])
    def test_p20_16_revoked_witness_plus_one_honest_insufficient(self):
        p=self.db(); self.active(p); st=self.stmt(p); r=self.rec(p,[self.sig(st,"w1"),self.sig(st,"w2")],conf=cfg({"w2"})); self.assertFalse(r["authorized"])
    def test_p20_17_witness_identity_key_substitution_denied(self):
        p=self.db(); self.active(p); st=self.stmt(p); subst=sign_witness(st,witness_id="w2",key_id="k1",key=K1); r=self.rec(p,[self.sig(st,"w1"),subst]); self.assertFalse(r["authorized"])
    def test_p20_18_one_witness_unavailable_remaining_two_honest_agree(self):
        p=self.db(); self.active(p); st=self.stmt(p); r=self.rec(p,[self.sig(st,"w2"),self.sig(st,"w3")]); self.assertTrue(r["authorized"]); self.assertEqual(r["witness_voters"],["w2","w3"])
    def test_p20_19_repeated_one_witness_forged_bundle_never_promotes(self):
        p=self.db(); self.active(p); st=self.stmt(p); st["state_root"]="c"*64; evil=self.sig(st,"w3"); rs=[self.rec(p,[evil]) for _ in range(3)]; self.assertTrue(all(not x.get("authorized",False) for x in rs))
    def test_p20_20_clean_higher_generation_quorum_liveness_control(self):
        p=self.db(); payload=self.effect(p,self.p(term=7,commit_index=11,lease_epoch=8,owner="fresh",idempotency_key="intent-20",semantic_digest="semantic-20",effect_digest="effect-20"),consume=True); st=self.stmt(p,9); r=self.rec(p,[self.sig(st,"w1"),self.sig(st,"w3")],min_g=9); self.assertFalse(r["authorized"]); self.assertTrue(r["witness_quorum"]); self.assertEqual(r["recovery_status"],"RECOVERED_CONSUMED"); conn=connect(p); self.assertEqual(conn.execute("SELECT COUNT(*) FROM effects").fetchone()[0],1); conn.close()

if __name__=="__main__": unittest.main()
