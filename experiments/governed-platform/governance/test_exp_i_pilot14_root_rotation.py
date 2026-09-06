from __future__ import annotations
import json, shutil, sqlite3, tempfile, threading, unittest
from pathlib import Path
from exp_i_asymmetric_checkpoint_signer import _ensure_ed25519_keypair, _ed25519_verify, _canon
from exp_i_registry_root_isolation import fp
from exp_i_root_rotation import PlatformRootTrustAuthority,RootMinimumAuthority,RotatingRootSigner,RootRotatingRegistry,RotatingRegistryReader

class ExpIPilot14RootRotationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); d=Path(self.tmp.name)
        self.rootdb=d/'root.db'; self.rootauth=d/'root-auth.key'; self.mindb=d/'root-min.db'; self.regdb=d/'registry.db'
        self.minimum=RootMinimumAuthority(self.mindb); self.trust=PlatformRootTrustAuthority(self.rootdb,self.rootauth)
        self.signers={r:RotatingRootSigner(d/r,r,self.trust,self.minimum) for r in ('R1','R2','R3')}
        self.keys={}
        for k in ('K1','K2','K3','K4','KX'):
            pr=d/f'{k}.priv'; pu=d/f'{k}.pub'; _ensure_ed25519_keypair(str(pr),str(pu)); self.keys[k]=pu.read_text()
        self.r1=self.trust.bootstrap(transition_id='ROOT-T1',root_id='R1',public_key_pem=self.signers['R1'].public_key_pem,activation_registry_epoch=0); self.minimum.advance(1,self.r1['record_digest'])
        self.registry=RootRotatingRegistry(self.regdb,self.trust,self.minimum,self.signers); self.e1=self.registry.transition(transition_id='T1',key_id='K1',public_key_pem=self.keys['K1'],activation_generation=1)
        self.root1copy=d/'root-epoch1.db'; shutil.copy2(self.rootdb,self.root1copy)
        self.r2=self.trust.rotate(transition_id='ROOT-T2',expected_prior_root_id='R1',next_root_id='R2',next_public_key_pem=self.signers['R2'].public_key_pem,activation_registry_epoch=1); self.minimum.advance(2,self.r2['record_digest'])
    def tearDown(self):
        for s in getattr(self,'signers',{}).values():
            try:s.stop(kill=True)
            except Exception:pass
        self.tmp.cleanup()
    def test_p14_01_root_trust_authority_distinct_and_roots_cannot_self_rotate(self):
        for s in self.signers.values():
            self.assertFalse(hasattr(s,'rotate')); self.assertFalse(hasattr(s,'bootstrap')); self.assertFalse(hasattr(s,'auth_key_path'))
        self.assertTrue(hasattr(self.trust,'rotate'))
    def test_p14_02_clean_r1_baseline(self):
        self.assertEqual(self.e1['event']['signer_root_id'],'R1'); self.assertTrue(_ed25519_verify(self.signers['R1'].public_key_pem,_canon(self.e1['event']),self.e1['signature']))
    def test_p14_03_clean_atomic_r1_to_r2_rotation(self):
        cur=self.trust.current(self.minimum)['record']; self.assertEqual(cur['root_epoch'],2); self.assertEqual(cur['active_root_id'],'R2'); self.assertEqual(cur['prior_root_id'],'R1'); self.assertEqual(cur['prior_status_after'],'REVOKED')
    def test_p14_04_valid_r1_rejected_for_new_current_transition_after_revocation(self):
        body={'transition_id':'ATTACK','root_epoch':2,'root_record_digest':self.r2['record_digest']}; sig=self.signers['R1'].sign(body); self.assertFalse(sig['ok']); self.assertIn('ROOT_NOT_CURRENTLY_ELIGIBLE',sig['reason'])
    def test_p14_05_stale_pre_rotation_root_snapshot_cannot_restore_r1(self):
        stale=PlatformRootTrustAuthority(self.root1copy,self.rootauth)
        with self.assertRaises(PermissionError): stale.current(self.minimum)
    def test_p14_06_root_epoch_rollback_denied(self):
        body={'transition_id':'ROLLBACK','root_epoch':1,'root_record_digest':self.r1['record_digest']}; res=self.signers['R2'].sign(body); self.assertFalse(res['ok']); self.assertIn('ROOT_BINDING_STALE',res['reason'])
    def test_p14_07_root_id_substitution_denied(self):
        with self.assertRaises(PermissionError): self.registry.transition(transition_id='T2',key_id='K2',public_key_pem=self.keys['K2'],activation_generation=2,root_id='R1')
    def test_p14_08_root_public_key_fingerprint_substitution_denied(self):
        c=sqlite3.connect(self.rootdb); j=c.execute('SELECT record_json FROM root_records WHERE root_epoch=2').fetchone()[0]; e=json.loads(j); e['active_public_key_pem']=self.signers['R1'].public_key_pem; c.execute('UPDATE root_records SET record_json=? WHERE root_epoch=2',(json.dumps(e,sort_keys=True),)); c.commit(); c.close()
        with self.assertRaises(PermissionError): self.trust.current(self.minimum)
    def test_p14_09_old_r1_signature_cannot_rebind_new_registry_semantics(self):
        forged=dict(self.e1['event']); forged['active_key_id']='KX'; self.assertFalse(_ed25519_verify(self.signers['R1'].public_key_pem,_canon(forged),self.e1['signature']))
    def test_p14_10_transition_replay_idempotent_across_root_rotation(self):
        replay=self.registry.transition(transition_id='T1',key_id='K1',public_key_pem=self.keys['K1'],activation_generation=1)
        self.assertEqual(replay['event_digest'],self.e1['event_digest']); c=sqlite3.connect(self.regdb); n=c.execute("SELECT COUNT(*) FROM trust_events WHERE transition_id='T1'").fetchone()[0]; c.close(); self.assertEqual(n,1)
    def test_p14_11_same_transition_identity_semantic_rebinding_denied_across_rotation(self):
        with self.assertRaises(PermissionError): self.registry.transition(transition_id='T1',key_id='KX',public_key_pem=self.keys['KX'],activation_generation=1,root_id='R2')
    def test_p14_12_concurrent_r1_issuance_vs_rotation_has_one_authoritative_outcome(self):
        # Current root is already R2: a stale R1 racer must fail while R2 may advance once.
        results=[]
        def stale():
            try:self.registry.transition(transition_id='T2-R1',key_id='K2',public_key_pem=self.keys['K2'],activation_generation=2,root_id='R1'); results.append('R1_OK')
            except Exception:results.append('R1_DENY')
        def current():
            try:self.registry.transition(transition_id='T2-R2',key_id='K2',public_key_pem=self.keys['K2'],activation_generation=2,root_id='R2'); results.append('R2_OK')
            except Exception:results.append('R2_DENY')
        a=threading.Thread(target=stale); b=threading.Thread(target=current); a.start(); b.start(); a.join(); b.join(); self.assertIn('R1_DENY',results); self.assertIn('R2_OK',results)
    def test_p14_13_r1_outage_blocks_r1_mint_not_historical_verification(self):
        self.signers['R1'].stop(kill=True); self.assertTrue(_ed25519_verify(self.signers['R1'].public_key_pem,_canon(self.e1['event']),self.e1['signature']))
        self.assertEqual(self.signers['R1'].sign({'transition_id':'X'}).get('reason'),'ROOT_UNAVAILABLE')
    def test_p14_14_r2_restart_preserves_eligibility_and_replay(self):
        e2=self.registry.transition(transition_id='T2',key_id='K2',public_key_pem=self.keys['K2'],activation_generation=2); self.signers['R2'].stop(); self.signers['R2'].start(); replay=self.registry.transition(transition_id='T2',key_id='K2',public_key_pem=self.keys['K2'],activation_generation=2); self.assertEqual(replay['event_digest'],e2['event_digest'])
    def test_p14_15_revoked_r1_plus_registry_writer_collusion_has_zero_current_authority(self):
        c=sqlite3.connect(self.regdb); j=c.execute('SELECT event_json FROM trust_events WHERE trust_epoch=1').fetchone()[0]; e=json.loads(j); e['active_key_id']='KX'; c.execute('UPDATE trust_events SET event_json=? WHERE trust_epoch=1',(json.dumps(e,sort_keys=True),)); c.commit(); c.close()
        with self.assertRaises(PermissionError): RotatingRegistryReader(self.regdb,self.trust,self.minimum).current()
        for obj in (self.registry,self.trust,self.signers['R1']):
            for name in ('release','merge','approve','production_authority'): self.assertFalse(hasattr(obj,name))
    def test_p14_16_clean_r2_to_r3_second_rotation_liveness(self):
        e2=self.registry.transition(transition_id='T2',key_id='K2',public_key_pem=self.keys['K2'],activation_generation=2)
        r3=self.trust.rotate(transition_id='ROOT-T3',expected_prior_root_id='R2',next_root_id='R3',next_public_key_pem=self.signers['R3'].public_key_pem,activation_registry_epoch=2); self.minimum.advance(3,r3['record_digest'])
        e3=self.registry.transition(transition_id='T3',key_id='K3',public_key_pem=self.keys['K3'],activation_generation=3); cur=RotatingRegistryReader(self.regdb,self.trust,self.minimum).current()
        self.assertEqual(cur['event_digest'],e3['event_digest']); self.assertEqual(cur['event']['signer_root_id'],'R3'); self.assertEqual(cur['event']['root_epoch'],3); self.assertEqual(cur['event']['predecessor_event_digest'],e2['event_digest'])

if __name__=='__main__': unittest.main()
