from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from multi_witness_checkpoint_exp_o import statement_for_db
from process_witness_anti_equivocation_exp_o import WitnessProcess, coordinator_request_payload, history_snapshot, recover_process_witness
from sqlite_process_crash_exp_o import authority_payload, connect, worker_authority, worker_consume, worker_effect
from sqlite_storage_seal_exp_o import init_sealed_db, seal_state

P="governed-platform"; T="EXP-O-PILOT21"; S="authority-ledger-A"
K1=b"pilot21-w1-key"; K2=b"pilot21-w2-key"; K3=b"pilot21-w3-key"
KEYS={"w1":K1,"w2":K2,"w3":K3}; KEYIDS={"w1":"k1","w2":"k2","w3":"k3"}


def verifier_config():
    return {w:{"key_id":KEYIDS[w],"key":KEYS[w],"revoked":False} for w in ("w1","w2","w3")}


class ExpOPilot21ProcessWitnessAntiEquivocationTests(unittest.TestCase):
    def setUp(self):
        self.td=tempfile.TemporaryDirectory(); self.root=Path(self.td.name); self.procs=[]
    def tearDown(self):
        for p in reversed(self.procs):
            try: p.stop(kill=True)
            except Exception: pass
        self.td.cleanup()
    def db(self,n="case.db"): return self.root/n
    def store(self,w): return self.root/f"{w}.sqlite"
    def payload(self,**kw):
        d=dict(logical_id="auth-1",term=1,commit_index=1,owner="r1",lease_epoch=1,semantic_digest="semantic-A",effect_digest="effect-A",idempotency_key="intent-1"); d.update(kw); return authority_payload(**d)
    def active(self,path,payload=None):
        payload=payload or self.payload(); init_sealed_db(path); self.assertTrue(worker_authority(str(path),payload,None)["authorized"]); seal_state(path); return payload
    def effect(self,path,payload=None,consume=False):
        payload=self.active(path,payload); self.assertTrue(worker_effect(str(path),payload,None)["executed"])
        if consume: self.assertEqual(worker_consume(str(path),payload,None)["decision"],"CONSUMED")
        seal_state(path); return payload
    def stmt(self,path,g=1): return statement_for_db(path,project=P,task=T,logical_state_id=S,generation=g)
    def spawn(self,w):
        p=WitnessProcess(witness_id=w,key_id=KEYIDS[w],key=KEYS[w],store=self.store(w)); self.procs.append(p); return p
    def restart(self,p,w):
        old=p.pid; p.stop(kill=True); q=self.spawn(w); self.assertNotEqual(old,q.pid); return q
    def rec(self,path,recs,min_g=1):
        return recover_process_witness(path,recs,verifier_config=verifier_config(),expected_project=P,expected_task=T,expected_logical_state_id=S,minimum_generation=min_g)

    def test_p21_01_three_independent_witness_processes_and_stores(self):
        a,b,c=self.spawn("w1"),self.spawn("w2"),self.spawn("w3")
        self.assertEqual(len({a.pid,b.pid,c.pid}),3); self.assertTrue(all(x.proc.poll() is None for x in (a,b,c)))
        self.assertEqual(len({str(Path(a.store).resolve()),str(Path(b.store).resolve()),str(Path(c.store).resolve())}),3)
        self.assertTrue(all(Path(x.store).exists() for x in (a,b,c)))

    def test_p21_02_clean_two_process_same_statement_quorum(self):
        db=self.db(); self.active(db); st=self.stmt(db); a,b=self.spawn("w1"),self.spawn("w2")
        r=self.rec(db,[a.request(st),b.request(st)]); self.assertTrue(r["authorized"]); self.assertEqual(r["witness_voters"],["w1","w2"])

    def test_p21_03_coordinator_request_path_has_no_witness_signing_keys(self):
        db=self.db(); self.active(db); st=self.stmt(db); a=self.spawn("w1")
        wire=coordinator_request_payload(st); material=json.dumps(wire,sort_keys=True)+" "+" ".join(a.argv)
        self.assertNotIn(K1.hex(),material); self.assertNotIn(K1.decode(),material); self.assertNotIn("EXP_O_WITNESS_KEY_HEX",material)
        self.assertNotIn("key",wire)

    def test_p21_04_same_witness_exact_replay_is_idempotent(self):
        db=self.db(); self.active(db); st=self.stmt(db); a=self.spawn("w1")
        x=a.request(st); y=a.request(st); self.assertTrue(x["approved"] and y["approved"]); self.assertFalse(x["replay"]); self.assertTrue(y["replay"])
        self.assertEqual(x["auth_tag"],y["auth_tag"]); self.assertEqual(len(history_snapshot(self.store("w1"))["rows"]),1)

    def test_p21_05_honest_witness_same_generation_conflicting_statement_refusal(self):
        db=self.db(); self.active(db); a=self.spawn("w1"); good=self.stmt(db,5); bad=dict(good); bad["state_root"]="e"*64
        self.assertTrue(a.request(good)["approved"]); r=a.request(bad); self.assertFalse(r["approved"]); self.assertEqual(r["reason"],"SAME_GENERATION_EQUIVOCATION_REFUSED")
        self.assertEqual(len(history_snapshot(self.store("w1"))["rows"]),1)

    def test_p21_06_same_generation_equivocation_refusal_survives_restart(self):
        db=self.db(); self.active(db); a=self.spawn("w1"); good=self.stmt(db,5); bad=dict(good); bad["state_root"]="d"*64
        self.assertTrue(a.request(good)["approved"]); a=self.restart(a,"w1"); r=a.request(bad); self.assertFalse(r["approved"]); self.assertEqual(r["reason"],"SAME_GENERATION_EQUIVOCATION_REFUSED")

    def test_p21_07_honest_witness_lower_generation_refusal(self):
        db=self.db(); self.active(db); a=self.spawn("w1"); self.assertTrue(a.request(self.stmt(db,7))["approved"])
        r=a.request(self.stmt(db,6)); self.assertFalse(r["approved"]); self.assertEqual(r["reason"],"GENERATION_ROLLBACK_REFUSED")

    def test_p21_08_lower_generation_refusal_survives_restart(self):
        db=self.db(); self.active(db); a=self.spawn("w1"); self.assertTrue(a.request(self.stmt(db,7))["approved"]); a=self.restart(a,"w1")
        r=a.request(self.stmt(db,6)); self.assertFalse(r["approved"]); self.assertEqual(r["reason"],"GENERATION_ROLLBACK_REFUSED")

    def test_p21_09_higher_generation_advances_durable_maximum(self):
        db=self.db(); self.active(db); a=self.spawn("w1"); self.assertTrue(a.request(self.stmt(db,2))["approved"]); self.assertTrue(a.request(self.stmt(db,3))["approved"])
        snap=history_snapshot(self.store("w1")); self.assertEqual(snap["max_generation"],3); self.assertEqual([x["generation"] for x in snap["rows"]],[2,3])

    def test_p21_10_crash_after_durable_signing_commit_before_response(self):
        db=self.db(); self.active(db); st=self.stmt(db,4); a=self.spawn("w1"); lost=a.request(st,crash_after_commit=True)
        self.assertEqual(lost["transport"],"UNKNOWN_AFTER_REQUEST"); snap=history_snapshot(self.store("w1")); self.assertEqual(snap["max_generation"],4); self.assertEqual(len(snap["rows"]),1)
        a=self.spawn("w1"); replay=a.request(st); self.assertTrue(replay["approved"]); self.assertTrue(replay["replay"]); self.assertEqual(replay["auth_tag"],snap["rows"][0]["auth_tag"])

    def test_p21_11_duplicate_response_from_one_witness_cannot_count_twice(self):
        db=self.db(); self.active(db); st=self.stmt(db); a=self.spawn("w1"); vote=a.request(st); r=self.rec(db,[vote,vote]); self.assertFalse(r["authorized"]); self.assertEqual(r["reason"],"WITNESS_QUORUM_INSUFFICIENT")

    def test_p21_12_delayed_positive_response_cannot_retroactively_reopen_failed_decision(self):
        db=self.db(); self.active(db); st=self.stmt(db); a,b=self.spawn("w1"),self.spawn("w2"); va=a.request(st); first=self.rec(db,[va]); self.assertFalse(first["authorized"])
        vb=b.request(st); self.assertFalse(first["authorized"]); second=self.rec(db,[va,vb]); self.assertTrue(second["authorized"])

    def test_p21_13_reordered_signatures_for_different_statements_do_not_form_quorum(self):
        db=self.db(); self.active(db); a,b=self.spawn("w1"),self.spawn("w2"); s1=self.stmt(db,1); s2=self.stmt(db,2)
        r=self.rec(db,[b.request(s2),a.request(s1)]); self.assertFalse(r["authorized"]); self.assertEqual(r["reason"],"WITNESS_QUORUM_INSUFFICIENT")

    def test_p21_14_one_malicious_witness_conflicts_two_honest_agree(self):
        db=self.db(); self.active(db); a,b,c=self.spawn("w1"),self.spawn("w2"),self.spawn("w3"); good=self.stmt(db,3); bad=dict(good); bad["state_root"]="c"*64
        r=self.rec(db,[a.request(good),b.request(good),c.request(bad)],min_g=3); self.assertTrue(r["authorized"]); self.assertEqual(r["witness_voters"],["w1","w2"])

    def test_p21_15_one_honest_witness_unavailable_remaining_honest_pair_agrees(self):
        db=self.db(); self.active(db); b,c=self.spawn("w2"),self.spawn("w3"); st=self.stmt(db,3); r=self.rec(db,[b.request(st),c.request(st)],min_g=3)
        self.assertTrue(r["authorized"]); self.assertEqual(r["witness_voters"],["w2","w3"])

    def test_p21_16_one_honest_unavailable_plus_one_malicious_conflicting_witness(self):
        db=self.db(); self.active(db); a,c=self.spawn("w1"),self.spawn("w3"); good=self.stmt(db,3); bad=dict(good); bad["state_root"]="b"*64
        r=self.rec(db,[a.request(good),c.request(bad)],min_g=3); self.assertFalse(r["authorized"]); self.assertEqual(r["reason"],"WITNESS_QUORUM_INSUFFICIENT")

    def test_p21_17_old_two_process_valid_signatures_below_trusted_minimum(self):
        db=self.db(); self.active(db); a,b=self.spawn("w1"),self.spawn("w2"); old=self.stmt(db,2); r=self.rec(db,[a.request(old),b.request(old)],min_g=5)
        self.assertFalse(r["authorized"]); self.assertEqual(r["reason"],"WITNESS_QUORUM_ROLLBACK")

    def test_p21_18_coherent_db_rewrite_reseal_plus_one_malicious_witness_resigns(self):
        db=self.db(); self.active(db); a,b,c=self.spawn("w1"),self.spawn("w2"),self.spawn("w3"); old=self.stmt(db,2); va,vb=a.request(old),b.request(old)
        conn=connect(db); conn.execute("UPDATE authority SET owner='evil'"); conn.close(); seal_state(db); new=self.stmt(db,2); vc=c.request(new)
        r=self.rec(db,[va,vb,vc],min_g=2); self.assertFalse(r["authorized"]); self.assertEqual(r["reason"],"WITNESS_STATE_ROOT_MISMATCH")

    def test_p21_19_repeated_restart_retry_cannot_erase_anti_equivocation_memory(self):
        db=self.db(); self.active(db); good=self.stmt(db,8); bad=dict(good); bad["state_root"]="a"*64; a=self.spawn("w1"); self.assertTrue(a.request(good)["approved"])
        for _ in range(3):
            a=self.restart(a,"w1"); conflict=a.request(bad); rollback=a.request(self.stmt(db,7)); self.assertFalse(conflict["approved"]); self.assertFalse(rollback["approved"])
        snap=history_snapshot(self.store("w1")); self.assertEqual(snap["max_generation"],8); self.assertEqual(len(snap["rows"]),1)

    def test_p21_20_clean_higher_generation_quorum_effect_liveness_control(self):
        db=self.db(); self.effect(db,self.payload(term=9,commit_index=14,lease_epoch=10,owner="fresh",semantic_digest="semantic-21",effect_digest="effect-21",idempotency_key="intent-21"),consume=True)
        a,b=self.spawn("w1"),self.spawn("w2"); st=self.stmt(db,11); r=self.rec(db,[a.request(st),b.request(st)],min_g=11)
        self.assertFalse(r["authorized"]); self.assertTrue(r["witness_quorum"]); self.assertEqual(r["recovery_status"],"RECOVERED_CONSUMED"); self.assertEqual(r["witness_voters"],["w1","w2"])
        conn=connect(db); self.assertEqual(conn.execute("SELECT COUNT(*) FROM effects").fetchone()[0],1); conn.close()


if __name__=="__main__": unittest.main()
