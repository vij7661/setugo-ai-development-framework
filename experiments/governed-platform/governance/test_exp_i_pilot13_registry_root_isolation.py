from __future__ import annotations
import json, shutil, sqlite3, tempfile, unittest
from pathlib import Path
from exp_i_asymmetric_checkpoint_signer import _digest, _ensure_ed25519_keypair
from exp_i_registry_root_isolation import (
    IsolatedRootAuthority, TrustedMinimumAuthority, RootSignedRegistry,
    PinnedRegistryReader, ROOT_ID, fp,
)

class ExpIPilot13RegistryRootIsolationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); root=Path(self.tmp.name)
        self.registry_db=str(root/"registry.db"); self.minimum_db=str(root/"minimum.db")
        self.root=IsolatedRootAuthority(root/"root-authority")
        self.registry=RootSignedRegistry(self.registry_db,self.root)
        self.keys={}
        for kid in ("K1","K2","K3","K4","KX"):
            priv=root/f"{kid}-private.pem"; pub=root/f"{kid}-public.pem"; _ensure_ed25519_keypair(str(priv),str(pub)); self.keys[kid]=pub.read_text()
        self.e1=self.registry.transition(transition_id="T1",key_id="K1",public_key_pem=self.keys["K1"],activation_generation=1)
        self.epoch1_db=str(root/"epoch1.db"); shutil.copy2(self.registry_db,self.epoch1_db)
        self.e2=self.registry.transition(transition_id="T2",key_id="K2",public_key_pem=self.keys["K2"],activation_generation=2)
        self.epoch2_db=str(root/"epoch2.db"); shutil.copy2(self.registry_db,self.epoch2_db)
        self.e3=self.registry.transition(transition_id="T3",key_id="K3",public_key_pem=self.keys["K3"],activation_generation=3)
        self.minimum=TrustedMinimumAuthority(self.minimum_db); self.minimum.advance(3,self.e3["event_digest"])
        self.reader=PinnedRegistryReader(self.registry_db,pinned_root_id=ROOT_ID,pinned_root_public_key_pem=self.root.public_key_pem,minimum=self.minimum)
    def tearDown(self):
        try:self.root.stop(kill=True)
        except Exception:pass
        self.tmp.cleanup()
    def reader_for(self,path,minimum=None,root_id=ROOT_ID,pub=None):
        return PinnedRegistryReader(path,pinned_root_id=root_id,pinned_root_public_key_pem=pub or self.root.public_key_pem,minimum=minimum or self.minimum)
    def assert_rejected(self,fn):
        with self.assertRaises(PermissionError): fn()

    def test_p13_01_root_signer_distinct_private_absent_from_ordinary_surfaces(self):
        self.assertIsNotNone(self.root.proc); self.assertIsNone(self.root.proc.poll())
        for obj in (self.registry,self.reader,self.minimum):
            self.assertFalse(hasattr(obj,"private_key_pem")); self.assertFalse(hasattr(obj,"sign"))
        con=sqlite3.connect(self.registry_db); cols=[r[1] for r in con.execute("PRAGMA table_info(trust_events)")]; con.close()
        self.assertNotIn("private_key",cols); self.assertNotIn("private_key_pem",cols)

    def test_p13_02_clean_inherited_k3_baseline_verifies_above_minimum(self):
        h=self.reader.history(); self.assertEqual(len(h),3); self.assertEqual(h[-1]["event"]["active_key_id"],"K3"); self.assertEqual(self.minimum.current(),(3,self.e3["event_digest"]))

    def test_p13_03_coherent_registry_rollback_to_old_valid_epoch_denied(self):
        self.assert_rejected(lambda:self.reader_for(self.epoch2_db).current())
        self.assert_rejected(lambda:self.reader_for(self.epoch1_db).current())

    def test_p13_04_coherent_rewrite_without_current_root_signature_denied(self):
        con=sqlite3.connect(self.registry_db); row=con.execute("SELECT event_json,signature FROM trust_events WHERE trust_epoch=3").fetchone(); e=json.loads(row[0]); e["active_key_id"]="KX"; e["active_public_key_pem"]=self.keys["KX"]; e["active_public_key_fingerprint"]=fp(self.keys["KX"]); d=_digest({"event":e,"signature":row[1]}); con.execute("UPDATE trust_events SET event_json=?,event_digest=? WHERE trust_epoch=3",(json.dumps(e,sort_keys=True),d)); con.commit(); con.close()
        self.assert_rejected(lambda:self.reader.current())

    def test_p13_05_old_valid_chain_cannot_reactivate_revoked_k1(self):
        self.assert_rejected(lambda:self.reader_for(self.epoch1_db).current())
        self.assertEqual(self.reader.current()["event"]["active_key_id"],"K3")

    def test_p13_06_substituted_root_public_key_denied(self):
        other=IsolatedRootAuthority(Path(self.tmp.name)/"other-root")
        try:self.assert_rejected(lambda:self.reader_for(self.registry_db,pub=other.public_key_pem).current())
        finally:other.stop(kill=True)

    def test_p13_07_root_id_public_key_binding_substitution_denied(self):
        self.assert_rejected(lambda:self.reader_for(self.registry_db,root_id="ATTACKER-ROOT").current())
        con=sqlite3.connect(self.registry_db); row=con.execute("SELECT event_json FROM trust_events WHERE trust_epoch=3").fetchone(); e=json.loads(row[0]); e["signer_root_id"]="ATTACKER-ROOT"; con.execute("UPDATE trust_events SET event_json=? WHERE trust_epoch=3",(json.dumps(e,sort_keys=True),)); con.commit(); con.close(); self.assert_rejected(lambda:self.reader.current())

    def test_p13_08_trusted_minimum_epoch_rollback_denied(self):
        with self.assertRaises(PermissionError) as ctx:self.minimum.advance(2,self.e2["event_digest"])
        self.assertEqual(str(ctx.exception),"MINIMUM_ROLLBACK_DENIED"); self.assertEqual(self.minimum.current()[0],3)

    def test_p13_09_trusted_minimum_event_digest_substitution_denied(self):
        with self.assertRaises(PermissionError) as ctx:self.minimum.advance(3,"0"*64)
        self.assertEqual(str(ctx.exception),"MINIMUM_DIGEST_REBIND_DENIED"); self.assertEqual(self.minimum.current(),(3,self.e3["event_digest"]))

    def test_p13_10_event_deletion_reorder_duplicate_epoch_denied(self):
        con=sqlite3.connect(self.registry_db); con.execute("DELETE FROM trust_events WHERE trust_epoch=2"); con.commit(); con.close(); self.assert_rejected(lambda:self.reader.current())

    def test_p13_11_exact_transition_replay_idempotent(self):
        r=self.registry.transition(transition_id="T3",key_id="K3",public_key_pem=self.keys["K3"],activation_generation=3)
        self.assertEqual(r["event_digest"],self.e3["event_digest"]); con=sqlite3.connect(self.registry_db); n=con.execute("SELECT COUNT(*) FROM trust_events WHERE trust_epoch=3").fetchone()[0]; con.close(); self.assertEqual(n,1)

    def test_p13_12_same_transition_identity_semantic_rebinding_denied(self):
        with self.assertRaises(PermissionError) as ctx:self.registry.transition(transition_id="T3",key_id="KX",public_key_pem=self.keys["KX"],activation_generation=3)
        self.assertEqual(str(ctx.exception),"TRANSITION_REBIND_DENIED")

    def test_p13_13_root_outage_blocks_mutation_not_verification(self):
        before=self.reader.current(); self.root.stop(kill=True)
        with self.assertRaises(PermissionError) as ctx:self.registry.transition(transition_id="T4",key_id="K4",public_key_pem=self.keys["K4"],activation_generation=4)
        self.assertEqual(str(ctx.exception),"ROOT_UNAVAILABLE"); self.assertEqual(self.reader.current()["event_digest"],before["event_digest"])

    def test_p13_14_root_restart_preserves_monotonicity_and_replay_memory(self):
        self.root.stop(); self.root.start(); replay=self.registry.transition(transition_id="T3",key_id="K3",public_key_pem=self.keys["K3"],activation_generation=3); self.assertEqual(replay["event_digest"],self.e3["event_digest"])
        body={"transition_id":"T-low","trust_epoch":2}
        denied=self.root.sign(body); self.assertFalse(denied["ok"]); self.assertIn("ROOT_EPOCH_NOT_EXACT_NEXT",denied["reason"])

    def test_p13_15_signer_registry_collusion_has_no_root_or_production_authority(self):
        con=sqlite3.connect(self.registry_db); row=con.execute("SELECT event_json,signature FROM trust_events WHERE trust_epoch=3").fetchone(); e=json.loads(row[0]); e["active_key_id"]="KX"; e["active_public_key_pem"]=self.keys["KX"]; e["active_public_key_fingerprint"]=fp(self.keys["KX"]); con.execute("UPDATE trust_events SET event_json=? WHERE trust_epoch=3",(json.dumps(e,sort_keys=True),)); con.commit(); con.close(); self.assert_rejected(lambda:self.reader.current())
        for obj in (self.registry,self.reader,self.minimum):
            for name in ("approve","release","merge","production_authority"): self.assertFalse(hasattr(obj,name))

    def test_p13_16_clean_k3_to_k4_transition_liveness(self):
        self.root.stop(); self.root.start(); e4=self.registry.transition(transition_id="T4",key_id="K4",public_key_pem=self.keys["K4"],activation_generation=4); self.minimum.advance(4,e4["event_digest"]); fresh=self.reader_for(self.registry_db); cur=fresh.current(); self.assertEqual(cur["event"]["active_key_id"],"K4"); self.assertEqual(cur["event"]["prior_key_id"],"K3"); self.assertEqual(cur["event"]["trust_epoch"],4); self.assertEqual(len(fresh.history()),4)

if __name__=="__main__": unittest.main()
