from __future__ import annotations
import hashlib,hmac,json,sqlite3,tempfile,unittest
from pathlib import Path

from checkpoint_authority_process_exp_o import CheckpointAuthorityProcess, checkpoint_digest, checkpoint_statement
from checkpoint_oracle_witness_exp_o import OracleWitnessProcess
from multi_witness_checkpoint_exp_o import recover_multi_witness, statement_for_db
from process_witness_store_integrity_exp_o import make_history_checkpoint, verify_store, _row_seal, _meta_seal
from sqlite_process_crash_exp_o import authority_payload,connect,worker_authority,worker_consume,worker_effect
from sqlite_storage_seal_exp_o import init_sealed_db,seal_state

P="governed-platform";T="EXP-O-PILOT23";L="authority-ledger-A";CK=b"p23-checkpoint-authority-key";VK=b"p23-oracle-decision-key"
WK={"w1":b"p23-w1","w2":b"p23-w2","w3":b"p23-w3"};KID={"w1":"k1","w2":"k2","w3":"k3"}

def canon(v):return json.dumps(v,sort_keys=True,separators=(",",":")).encode()
class ExpOPilot23CheckpointAuthorityIsolationTests(unittest.TestCase):
 def setUp(self):self.td=tempfile.TemporaryDirectory();self.root=Path(self.td.name);self.ps=[]
 def tearDown(self):
  for p in self.ps:
   try:p.stop(True) if isinstance(p,CheckpointAuthorityProcess) else p.stop(kill=True)
   except Exception:pass
  self.td.cleanup()
 def ap(self):
  a=CheckpointAuthorityProcess(store=self.root/"checkpoint-authority.sqlite",checkpoint_key=CK,verification_key=VK);self.ps.append(a);return a
 def wp(self,w):
  q=OracleWitnessProcess(witness_id=w,key_id=KID[w],signing_key=WK[w],store=self.root/f"{w}.sqlite",store_identity=f"store-{w}");self.ps.append(q);return q
 def localcpstmt(self,w,cg):
  v=verify_store(self.root/f"{w}.sqlite",expected_store_identity=f"store-{w}");self.assertTrue(v["ok"],v);return checkpoint_statement(witness_id=w,key_id=KID[w],store_identity=f"store-{w}",history_root=v["history_root"],max_generation=v["max_generation"],checkpoint_generation=cg)
 def issueverify(self,a,w,cg,min_g=None):
  s=self.localcpstmt(w,cg);r=a.issue(s);self.assertTrue(r.get("ok"),r);v=a.verify(r,minimum_generation=cg if min_g is None else min_g,expected_witness_id=w,expected_store_identity=f"store-{w}",expected_key_id=KID[w]);self.assertTrue(v.get("ok"),v);return r,v
 def stmt(self,g,root="a"*64):return {"version":"exp-o-pilot20-v1","project":P,"task":T,"logical_state_id":L,"generation":g,"state_root":root,"fence":{"term":g,"commit_index":g,"lease_epoch":g}}
 def sign(self,a,w,p,g,cg=0,min_g=0,stmt=None):
  r,v=self.issueverify(a,w,cg,min_g);out=p.sign(stmt or self.stmt(g),checkpoint_record=r,verification_decision=v,minimum_checkpoint_generation=min_g);return out,r,v
 def authdb(self,consumed=False):
  p=self.root/"authority.db";init_sealed_db(p);x=authority_payload(logical_id="auth",term=9,commit_index=9,owner="r",lease_epoch=9,semantic_digest="s",effect_digest="e",idempotency_key="i");self.assertTrue(worker_authority(str(p),x,None)["authorized"])
  if consumed:self.assertTrue(worker_effect(str(p),x,None)["executed"]);self.assertEqual(worker_consume(str(p),x,None)["decision"],"CONSUMED")
  seal_state(p);return p
 def cfg(self):return {w:{"key_id":KID[w],"key":WK[w],"revoked":False} for w in WK}

 def test_p23_01_checkpoint_authority_distinct_process_and_store(self):
  a=self.ap();w=self.wp("w1");self.assertNotEqual(a.pid,w.pid);self.assertNotEqual(Path(a.store).resolve(),Path(w.store).resolve())
 def test_p23_02_witness_has_no_checkpoint_signing_key(self):
  w=self.wp("w1");self.assertEqual(w.env_keys,[]);self.assertNotIn(CK.hex()," ".join(w.argv))
 def test_p23_03_clean_issue_verify_and_witness_sign(self):
  a=self.ap();w=self.wp("w1");o,_,_=self.sign(a,"w1",w,1);self.assertTrue(o["approved"])
 def test_p23_04_witness_key_cannot_forge_checkpoint(self):
  a=self.ap();w=self.wp("w1");s=self.localcpstmt("w1",0);d=checkpoint_digest(s);fake={"ok":True,"statement":s,"checkpoint_digest":d,"auth_tag":hmac.new(WK["w1"],canon(s),hashlib.sha256).hexdigest()};v=a.verify(fake,minimum_generation=0,expected_witness_id="w1",expected_store_identity="store-w1",expected_key_id="k1");self.assertFalse(v["ok"])
 def test_p23_05_unrelated_key_cannot_forge_checkpoint(self):
  a=self.ap();self.wp("w1");s=self.localcpstmt("w1",0);fake={"statement":s,"checkpoint_digest":checkpoint_digest(s),"auth_tag":hmac.new(b"bad",canon(s),hashlib.sha256).hexdigest()};self.assertFalse(a.verify(fake,minimum_generation=0,expected_witness_id="w1",expected_store_identity="store-w1",expected_key_id="k1")["ok"])
 def test_p23_06_lower_generation_issuance_refused(self):
  a=self.ap();self.wp("w1");s2=self.localcpstmt("w1",2);self.assertTrue(a.issue(s2)["ok"]);s1=dict(s2);s1["checkpoint_generation"]=1;self.assertEqual(a.issue(s1)["reason"],"CHECKPOINT_GENERATION_ROLLBACK")
 def test_p23_07_same_generation_conflicting_root_refused(self):
  a=self.ap();self.wp("w1");s=self.localcpstmt("w1",2);self.assertTrue(a.issue(s)["ok"]);b=dict(s);b["history_root"]="f"*64;self.assertEqual(a.issue(b)["reason"],"CHECKPOINT_SAME_GENERATION_EQUIVOCATION")
 def test_p23_08_monotonicity_survives_authority_restart(self):
  a=self.ap();self.wp("w1");s=self.localcpstmt("w1",3);self.assertTrue(a.issue(s)["ok"]);old=a.pid;a.stop(True);b=self.ap();self.assertNotEqual(old,b.pid);lo=dict(s);lo["checkpoint_generation"]=2;self.assertFalse(b.issue(lo)["ok"]);cf=dict(s);cf["history_root"]="e"*64;self.assertFalse(b.issue(cf)["ok"])
 def test_p23_09_exact_issue_replay_idempotent(self):
  a=self.ap();self.wp("w1");s=self.localcpstmt("w1",1);x=a.issue(s);y=a.issue(s);self.assertTrue(y["ok"]);self.assertTrue(y["replay"]);self.assertEqual(x["auth_tag"],y["auth_tag"])
 def test_p23_10_checkpoint_tag_mutation_rejected(self):
  a=self.ap();self.wp("w1");r=a.issue(self.localcpstmt("w1",0));r["auth_tag"]="0"+r["auth_tag"][1:];self.assertFalse(a.verify(r,minimum_generation=0,expected_witness_id="w1",expected_store_identity="store-w1",expected_key_id="k1")["ok"])
 def test_p23_11_checkpoint_scope_substitution_rejected(self):
  a=self.ap();self.wp("w1");r=a.issue(self.localcpstmt("w1",0));self.assertFalse(a.verify(r,minimum_generation=0,expected_witness_id="w2",expected_store_identity="store-w1",expected_key_id="k1")["ok"])
 def test_p23_12_old_valid_checkpoint_below_trusted_minimum(self):
  a=self.ap();self.wp("w1");r=a.issue(self.localcpstmt("w1",1));self.assertFalse(a.verify(r,minimum_generation=2,expected_witness_id="w1",expected_store_identity="store-w1",expected_key_id="k1")["ok"])
 def test_p23_13_authority_unavailable_fails_closed(self):
  a=self.ap();w=self.wp("w1");r,v=self.issueverify(a,"w1",0);a.stop(True);bad=a.verify(r,minimum_generation=0,expected_witness_id="w1",expected_store_identity="store-w1",expected_key_id="k1");self.assertFalse(bad["ok"]);self.assertFalse(w.sign(self.stmt(1),checkpoint_record=r,verification_decision=bad,minimum_checkpoint_generation=0)["approved"])
 def test_p23_14_old_positive_verify_not_rebound_to_changed_checkpoint(self):
  a=self.ap();w=self.wp("w1");r,v=self.issueverify(a,"w1",0);changed=dict(r);changed["statement"]=dict(r["statement"]);changed["statement"]["history_root"]="c"*64;changed["checkpoint_digest"]=checkpoint_digest(changed["statement"]);self.assertFalse(w.sign(self.stmt(1),checkpoint_record=changed,verification_decision=v,minimum_checkpoint_generation=0)["approved"])
 def test_p23_15_old_positive_verify_not_rebound_to_changed_history(self):
  a=self.ap();w=self.wp("w1");r,v=self.issueverify(a,"w1",0);first=w.sign(self.stmt(1),checkpoint_record=r,verification_decision=v,minimum_checkpoint_generation=0);self.assertTrue(first["approved"]);self.assertFalse(w.sign(self.stmt(2),checkpoint_record=r,verification_decision=v,minimum_checkpoint_generation=0)["approved"])
 def test_p23_16_posthistory_precheckpoint_ambiguity_blocked_until_reconcile(self):
  a=self.ap();w=self.wp("w1");o,r,v=self.sign(a,"w1",w,1);self.assertTrue(o["approved"]);self.assertFalse(w.sign(self.stmt(2),checkpoint_record=r,verification_decision=v,minimum_checkpoint_generation=0)["approved"]);r2,v2=self.issueverify(a,"w1",1);self.assertTrue(w.sign(self.stmt(2),checkpoint_record=r2,verification_decision=v2,minimum_checkpoint_generation=1)["approved"])
 def test_p23_17_authority_crash_after_issue_commit_replays_same_checkpoint(self):
  a=self.ap();self.wp("w1");s=self.localcpstmt("w1",4);lost=a.issue(s,crash_after_commit=True);self.assertFalse(lost.get("ok",False));b=self.ap();r=b.issue(s);self.assertTrue(r["ok"]);self.assertTrue(r["replay"])
 def test_p23_18_tampered_resealed_store_old_checkpoint_blocked(self):
  a=self.ap();w=self.wp("w1");o,r,v=self.sign(a,"w1",w,1);self.assertTrue(o["approved"]);w.stop();c=sqlite3.connect(w.store,isolation_level=None);row=c.execute("SELECT auth_tag FROM signed_statements WHERE generation=1").fetchone();nd="d"*64;c.execute("UPDATE signed_statements SET statement_digest=?,row_seal=? WHERE generation=1",(nd,_row_seal(1,nd,row[0])));c.execute("PRAGMA wal_checkpoint(TRUNCATE)");c.close();q=self.wp("w1");self.assertFalse(q.sign(self.stmt(2),checkpoint_record=r,verification_decision=v,minimum_checkpoint_generation=0)["approved"])
 def test_p23_19_one_authority_two_witness_quorum_liveness(self):
  a=self.ap();w1=self.wp("w1");w2=self.wp("w2");db=self.authdb();st=statement_for_db(db,project=P,task=T,logical_state_id=L,generation=1);x,_,_=self.sign(a,"w1",w1,1,stmt=st);y,_,_=self.sign(a,"w2",w2,1,stmt=st);rr=recover_multi_witness(db,[x,y],witness_config=self.cfg(),expected_project=P,expected_task=T,expected_logical_state_id=L,minimum_generation=1);self.assertTrue(rr["authorized"])
 def test_p23_20_clean_higher_generation_consumed_liveness_after_restarts(self):
  a=self.ap();w1=self.wp("w1");w2=self.wp("w2");db=self.authdb(True);st=statement_for_db(db,project=P,task=T,logical_state_id=L,generation=9);x,_,_=self.sign(a,"w1",w1,9,stmt=st);y,_,_=self.sign(a,"w2",w2,9,stmt=st);a.stop(True);w1.stop(kill=True);w2.stop(kill=True);b=self.ap();q1=self.wp("w1");q2=self.wp("w2");r1,v1=self.issueverify(b,"w1",9);r2,v2=self.issueverify(b,"w2",9);x2=q1.sign(st,checkpoint_record=r1,verification_decision=v1,minimum_checkpoint_generation=9);y2=q2.sign(st,checkpoint_record=r2,verification_decision=v2,minimum_checkpoint_generation=9);rr=recover_multi_witness(db,[x2,y2],witness_config=self.cfg(),expected_project=P,expected_task=T,expected_logical_state_id=L,minimum_generation=9);self.assertFalse(rr["authorized"]);self.assertEqual(rr["recovery_status"],"RECOVERED_CONSUMED");c=connect(db);self.assertEqual(c.execute("SELECT COUNT(*) FROM effects").fetchone()[0],1);c.close()
if __name__=="__main__":unittest.main()
