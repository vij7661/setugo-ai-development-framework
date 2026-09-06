from __future__ import annotations

import copy
import os
from pathlib import Path
import shutil
import sqlite3
import tempfile
import unittest

from multi_witness_checkpoint_exp_o import sign_witness, statement_for_db
from process_witness_store_integrity_exp_o import SealedWitnessProcess, make_history_checkpoint, recover_sealed_process_witness, verify_store
from sqlite_process_crash_exp_o import authority_payload, connect, worker_authority, worker_consume, worker_effect
from sqlite_storage_seal_exp_o import init_sealed_db, seal_state

P="governed-platform"; T="EXP-O-PILOT22"; L="authority-ledger-A"
WKEYS={"w1":b"p22-w1","w2":b"p22-w2","w3":b"p22-w3"}; KIDS={"w1":"k1","w2":"k2","w3":"k3"}; CKEY=b"p22-checkpoint-key"

def vcfg(): return {w:{"key_id":KIDS[w],"key":WKEYS[w],"revoked":False} for w in WKEYS}

class ExpOPilot22WitnessStoreIntegrityTests(unittest.TestCase):
    def setUp(self): self.td=tempfile.TemporaryDirectory(); self.root=Path(self.td.name); self.procs=[]
    def tearDown(self):
        for p in self.procs:
            try: p.stop(kill=True)
            except Exception: pass
        self.td.cleanup()
    def store(self,w): return self.root/f"{w}.sqlite"
    def sid(self,w): return f"store-{w}"
    def proc(self,w):
        p=SealedWitnessProcess(witness_id=w,key_id=KIDS[w],signing_key=WKEYS[w],checkpoint_key=CKEY,store=self.store(w),store_identity=self.sid(w)); self.procs.append(p); return p
    def cp(self,w,cg): return make_history_checkpoint(self.store(w),witness_id=w,key_id=KIDS[w],store_identity=self.sid(w),checkpoint_generation=cg,checkpoint_key=CKEY)
    def stmt(self,g,root="a"*64): return {"version":"exp-o-pilot20-v1","project":P,"task":T,"logical_state_id":L,"generation":g,"state_root":root,"fence":{"term":g,"commit_index":g,"lease_epoch":g}}
    def bootstrap(self,w,g=5,cg=5):
        p=self.proc(w); empty=self.cp(w,0); r=p.request(self.stmt(g),checkpoint=empty,minimum_checkpoint_generation=0); self.assertTrue(r.get("approved"),r); chk=self.cp(w,cg); return p,chk,r
    def restart(self,p,w):
        old=p.pid; p.stop(kill=True); q=self.proc(w); self.assertNotEqual(old,q.pid); return q
    def wal_flush(self,path):
        c=sqlite3.connect(str(path),isolation_level=None); c.execute("PRAGMA wal_checkpoint(TRUNCATE)"); c.close()
    def authdb(self,consumed=False):
        p=self.root/"authority.db"; init_sealed_db(p); payload=authority_payload(logical_id="auth-1",term=9,commit_index=9,owner="r1",lease_epoch=9,semantic_digest="sem",effect_digest="eff",idempotency_key="intent")
        self.assertTrue(worker_authority(str(p),payload,None)["authorized"])
        if consumed:
            self.assertTrue(worker_effect(str(p),payload,None)["executed"]); self.assertEqual(worker_consume(str(p),payload,None)["decision"],"CONSUMED")
        seal_state(p); return p
    def quorum(self,db,recs,min_g): return recover_sealed_process_witness(db,recs,verifier_config=vcfg(),expected_project=P,expected_task=T,expected_logical_state_id=L,minimum_generation=min_g)
    def mutate_sql(self,path,sql,args=()):
        c=sqlite3.connect(str(path),isolation_level=None); c.execute(sql,args); c.execute("PRAGMA wal_checkpoint(TRUNCATE)"); c.close()

    def test_p22_01_clean_sealed_witness_store_control(self):
        p,chk,r=self.bootstrap("w1"); q=self.restart(p,"w1"); rr=q.request(self.stmt(5),checkpoint=chk,minimum_checkpoint_generation=5); self.assertTrue(rr["approved"]); self.assertTrue(rr["replay"])
    def test_p22_02_witness_sqlite_header_corruption(self):
        p,chk,_=self.bootstrap("w1"); p.stop(); data=bytearray(self.store("w1").read_bytes()); data[:16]=b"X"*16; self.store("w1").write_bytes(data); q=self.proc("w1"); r=q.request(self.stmt(5),checkpoint=chk,minimum_checkpoint_generation=5); self.assertFalse(r["approved"])
    def test_p22_03_witness_sqlite_truncation(self):
        p,chk,_=self.bootstrap("w1"); p.stop(); data=self.store("w1").read_bytes(); self.store("w1").write_bytes(data[:max(64,len(data)//2)]); q=self.proc("w1"); r=q.request(self.stmt(5),checkpoint=chk,minimum_checkpoint_generation=5); self.assertFalse(r["approved"])
    def test_p22_04_signed_history_payload_mutation_detected_by_seal(self):
        p,chk,_=self.bootstrap("w1"); p.stop(); self.mutate_sql(self.store("w1"),"UPDATE signed_statements SET statement_digest=? WHERE generation=5",("b"*64,)); q=self.proc("w1"); r=q.request(self.stmt(5),checkpoint=chk,minimum_checkpoint_generation=5); self.assertFalse(r["approved"]); self.assertEqual(r["reason"],"WITNESS_ROW_SEAL_MISMATCH")
    def test_p22_05_max_generation_lowered_without_history_rewrite(self):
        p,chk,_=self.bootstrap("w1"); p.stop(); self.mutate_sql(self.store("w1"),"UPDATE witness_meta SET max_generation=4"); q=self.proc("w1"); r=q.request(self.stmt(5),checkpoint=chk,minimum_checkpoint_generation=5); self.assertFalse(r["approved"])
    def test_p22_06_signed_history_row_deletion_detected(self):
        p,chk,_=self.bootstrap("w1"); p.stop(); self.mutate_sql(self.store("w1"),"DELETE FROM signed_statements WHERE generation=5"); q=self.proc("w1"); r=q.request(self.stmt(5),checkpoint=chk,minimum_checkpoint_generation=5); self.assertFalse(r["approved"])
    def test_p22_07_coherent_history_rewrite_resealed_external_root_blocks(self):
        p,chk,_=self.bootstrap("w1"); p.stop();
        c=sqlite3.connect(str(self.store("w1")),isolation_level=None); row=c.execute("SELECT auth_tag FROM signed_statements WHERE generation=5").fetchone(); nd="c"*64
        import hashlib,json
        rs=hashlib.sha256(json.dumps({"generation":5,"statement_digest":nd,"auth_tag":row[0]},sort_keys=True,separators=(",",":")).encode()).hexdigest(); c.execute("UPDATE signed_statements SET statement_digest=?,row_seal=? WHERE generation=5",(nd,rs)); c.execute("PRAGMA wal_checkpoint(TRUNCATE)"); c.close()
        q=self.proc("w1"); r=q.request(self.stmt(5),checkpoint=chk,minimum_checkpoint_generation=5); self.assertFalse(r["approved"]); self.assertEqual(r["reason"],"WITNESS_HISTORY_ROOT_MISMATCH")
    def test_p22_08_stale_older_valid_db_below_current_checkpoint(self):
        p,chk5,_=self.bootstrap("w1",5,5); self.wal_flush(self.store("w1")); old=self.root/"old.sqlite"; shutil.copy2(self.store("w1"),old)
        r=p.request(self.stmt(6),checkpoint=chk5,minimum_checkpoint_generation=5); self.assertTrue(r["approved"]); chk6=self.cp("w1",6); p.stop(); shutil.copy2(old,self.store("w1")); q=self.proc("w1"); rr=q.request(self.stmt(6),checkpoint=chk6,minimum_checkpoint_generation=6); self.assertFalse(rr["approved"])
    def test_p22_09_stale_db_plus_old_valid_checkpoint_below_trusted_minimum(self):
        p,chk5,_=self.bootstrap("w1",5,5); p.stop(); q=self.proc("w1"); r=q.request(self.stmt(5),checkpoint=chk5,minimum_checkpoint_generation=6); self.assertFalse(r["approved"]); self.assertEqual(r["reason"],"WITNESS_CHECKPOINT_ROLLBACK")
    def test_p22_10_checkpoint_auth_tag_mutation(self):
        p,chk,_=self.bootstrap("w1"); bad=dict(chk); bad["checkpoint_auth_tag"]="0"+bad["checkpoint_auth_tag"][1:]; r=p.request(self.stmt(5),checkpoint=bad,minimum_checkpoint_generation=5); self.assertFalse(r["approved"])
    def test_p22_11_forged_checkpoint_wrong_key(self):
        p,chk,_=self.bootstrap("w1"); bad=dict(chk); import hashlib,hmac,json
        st={k:bad[k] for k in ("version","witness_id","key_id","store_identity","max_generation","history_root","checkpoint_generation")}; bad["checkpoint_auth_tag"]=hmac.new(b"wrong",json.dumps(st,sort_keys=True,separators=(",",":")).encode(),hashlib.sha256).hexdigest(); r=p.request(self.stmt(5),checkpoint=bad,minimum_checkpoint_generation=5); self.assertFalse(r["approved"])
    def test_p22_12_checkpoint_scope_substitution(self):
        p,chk,_=self.bootstrap("w1"); bad=dict(chk); bad["witness_id"]="w2"; r=p.request(self.stmt(5),checkpoint=bad,minimum_checkpoint_generation=5); self.assertFalse(r["approved"])
    def test_p22_13_history_and_metadata_lowered_resealed_external_checkpoint_blocks(self):
        p,chk,_=self.bootstrap("w1",6,6); p.stop();
        c=sqlite3.connect(str(self.store("w1")),isolation_level=None); c.execute("DELETE FROM signed_statements WHERE generation=6"); import hashlib,json
        ms=hashlib.sha256(json.dumps({"store_identity":self.sid("w1"),"max_generation":-1},sort_keys=True,separators=(",",":")).encode()).hexdigest(); c.execute("UPDATE witness_meta SET max_generation=-1,meta_seal=?",(ms,)); c.execute("PRAGMA wal_checkpoint(TRUNCATE)"); c.close(); q=self.proc("w1"); r=q.request(self.stmt(5),checkpoint=chk,minimum_checkpoint_generation=6); self.assertFalse(r["approved"])
    def test_p22_14_same_generation_conflict_after_coherent_rollback_attempt(self):
        p,chk,_=self.bootstrap("w1",5,5); self.wal_flush(self.store("w1")); old=self.root/"pre.sqlite"; shutil.copy2(self.store("w1"),old); r=p.request(self.stmt(6),checkpoint=chk,minimum_checkpoint_generation=5); self.assertTrue(r["approved"]); chk6=self.cp("w1",6); p.stop(); shutil.copy2(old,self.store("w1")); q=self.proc("w1"); conflict=self.stmt(6,root="d"*64); rr=q.request(conflict,checkpoint=chk6,minimum_checkpoint_generation=6); self.assertFalse(rr["approved"])
    def test_p22_15_lower_generation_after_coherent_rollback_attempt(self):
        p,chk,_=self.bootstrap("w1",7,7); p.stop(); r=self.proc("w1").request(self.stmt(6),checkpoint=chk,minimum_checkpoint_generation=7); self.assertFalse(r["approved"])
    def test_p22_16_repeated_restart_corrupt_store_never_fails_open(self):
        p,chk,_=self.bootstrap("w1"); p.stop(); self.mutate_sql(self.store("w1"),"UPDATE signed_statements SET statement_digest='bad' WHERE generation=5")
        for _ in range(3):
            q=self.proc("w1"); r=q.request(self.stmt(5),checkpoint=chk,minimum_checkpoint_generation=5); self.assertFalse(r["approved"]); q.stop()
    def test_p22_17_one_tampered_honest_store_plus_one_malicious_no_conflicting_quorum(self):
        p,chk,_=self.bootstrap("w1"); p.stop(); self.mutate_sql(self.store("w1"),"UPDATE signed_statements SET statement_digest='bad' WHERE generation=5"); q=self.proc("w1"); honest=q.request(self.stmt(5),checkpoint=chk,minimum_checkpoint_generation=5); self.assertFalse(honest["approved"])
        db=self.authdb(); st=statement_for_db(db,project=P,task=T,logical_state_id=L,generation=5); evil=sign_witness(st,witness_id="w3",key_id="k3",key=WKEYS["w3"]); r=self.quorum(db,[evil],5); self.assertFalse(r["authorized"])
    def test_p22_18_one_store_corrupt_remaining_two_honest_current_stores_live(self):
        p1,c1,_=self.bootstrap("w1"); p1.stop(); self.mutate_sql(self.store("w1"),"UPDATE signed_statements SET statement_digest='bad' WHERE generation=5")
        p2,c2,_=self.bootstrap("w2"); p3,c3,_=self.bootstrap("w3"); db=self.authdb(); st=statement_for_db(db,project=P,task=T,logical_state_id=L,generation=6)
        r2=p2.request(st,checkpoint=c2,minimum_checkpoint_generation=5); r3=p3.request(st,checkpoint=c3,minimum_checkpoint_generation=5); self.assertTrue(r2["approved"]); self.assertTrue(r3["approved"]); rr=self.quorum(db,[r2,r3],6); self.assertTrue(rr["authorized"])
    def test_p22_19_postcommit_precheckpoint_crash_fails_closed_until_reconciled(self):
        p,chk5,_=self.bootstrap("w1",5,5); r=p.request(self.stmt(6),checkpoint=chk5,minimum_checkpoint_generation=5,crash_after_history_commit=True); self.assertEqual(r["transport"],"UNKNOWN_AFTER_REQUEST"); q=self.proc("w1"); blocked=q.request(self.stmt(6),checkpoint=chk5,minimum_checkpoint_generation=5); self.assertFalse(blocked["approved"]); chk6=self.cp("w1",6); replay=q.request(self.stmt(6),checkpoint=chk6,minimum_checkpoint_generation=6); self.assertTrue(replay["approved"]); self.assertTrue(replay["replay"])
    def test_p22_20_clean_higher_generation_checkpoint_liveness_control(self):
        p1,c1,_=self.bootstrap("w1",5,5); p2,c2,_=self.bootstrap("w2",5,5); db=self.authdb(consumed=True); st=statement_for_db(db,project=P,task=T,logical_state_id=L,generation=9)
        a=p1.request(st,checkpoint=c1,minimum_checkpoint_generation=5); b=p2.request(st,checkpoint=c2,minimum_checkpoint_generation=5); self.assertTrue(a["approved"]); self.assertTrue(b["approved"]); c1n=self.cp("w1",9); c2n=self.cp("w2",9); p1=self.restart(p1,"w1"); p2=self.restart(p2,"w2"); a2=p1.request(st,checkpoint=c1n,minimum_checkpoint_generation=9); b2=p2.request(st,checkpoint=c2n,minimum_checkpoint_generation=9); rr=self.quorum(db,[a2,b2],9); self.assertFalse(rr["authorized"]); self.assertTrue(rr["witness_quorum"]); self.assertEqual(rr["recovery_status"],"RECOVERED_CONSUMED"); c=connect(db); self.assertEqual(c.execute("SELECT COUNT(*) FROM effects").fetchone()[0],1); c.close()

if __name__=="__main__": unittest.main()
