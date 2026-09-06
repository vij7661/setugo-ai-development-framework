from __future__ import annotations
import copy, json, os, sqlite3, tempfile, threading, unittest
from pathlib import Path

from exp_i_asymmetric_checkpoint_signer import _ensure_ed25519_keypair
from exp_i_root_rotation import PlatformRootTrustAuthority, RootMinimumAuthority, RotatingRootSigner, RootRotatingRegistry
from exp_i_isolated_minimum_authority import MinimumAuthorityProcess, RecoveryAuthorizationAuthority


class ExpIPilot16IsolatedMinimumAuthorityTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.d=Path(self.tmp.name)
        self.rootdb=self.d/'root.db'; self.rootauth=self.d/'root-auth.key'; self.mindb=self.d/'minimum.db'
        self.trust=PlatformRootTrustAuthority(self.rootdb,self.rootauth); self.minimum=RootMinimumAuthority(self.mindb)
        self.root_keys={}
        for rid in ('R1','R2','R3'):
            pr=self.d/f'{rid}.priv'; pu=self.d/f'{rid}.pub'; _ensure_ed25519_keypair(str(pr),str(pu)); self.root_keys[rid]=pu.read_text()
        self.r1=self.trust.bootstrap(transition_id='ROOT-T1',root_id='R1',public_key_pem=self.root_keys['R1'],activation_registry_epoch=0)
        self.minimum.advance(1,self.r1['record_digest'])
        self.r2=self.trust.rotate(transition_id='ROOT-T2',expected_prior_root_id='R1',next_root_id='R2',next_public_key_pem=self.root_keys['R2'],activation_registry_epoch=1)
        self.rec=RecoveryAuthorizationAuthority(self.d/'recovery.priv',self.d/'recovery.pub')
        self.proc=MinimumAuthorityProcess(self.rootdb,self.rootauth,self.mindb,self.rec.public_key_pem)
    def tearDown(self):
        try:self.proc.stop(kill=True)
        except Exception:pass
        self.tmp.cleanup()
    def _auth(self,rid='REC-1',target=None,current=None):
        if target is None:target=self.r2
        if current is None:current=(1,self.r1['record_digest'])
        return self.rec.issue(rid,current[0],current[1],target)
    def _minimum(self):
        c=sqlite3.connect(self.mindb); row=c.execute('SELECT root_epoch,record_digest FROM minimum WHERE id=1').fetchone(); c.close(); return (int(row[0]),str(row[1]))
    def _recover_r2(self,rid='REC-1'):
        out=self.proc.advance(self._auth(rid)); self.assertTrue(out['ok'],out); return out

    def test_p16_01_dedicated_minimum_authority_is_distinct_process_and_durable_store(self):
        ping=self.proc.request({'op':'ping'}); self.assertTrue(ping['ok']); self.assertNotEqual(ping['pid'],os.getpid())
        self.assertTrue(self.mindb.exists()); self.assertEqual(self.proc.read()['minimum'][0],1)

    def test_p16_02_ordinary_root_surfaces_lack_minimum_mutation_secret_and_direct_advance(self):
        for cls in (RotatingRootSigner,RootRotatingRegistry,PlatformRootTrustAuthority):
            self.assertFalse(hasattr(cls,'recovery_private_path')); self.assertFalse(hasattr(cls,'issue_recovery_authorization'))
        self.assertNotIn(str(self.rec.private_path),repr(vars(self.proc)))
        self.assertFalse(hasattr(self.proc,'recovery_private_path'))

    def test_p16_03_clean_exact_r1_to_r2_authorization_advances_minimum(self):
        out=self._recover_r2(); self.assertEqual(tuple(out['minimum']),(2,self.r2['record_digest'])); self.assertEqual(self._minimum(),(2,self.r2['record_digest']))

    def test_p16_04_missing_recovery_authorization_denied_before_mutation(self):
        out=self.proc.advance(None); self.assertFalse(out['ok']); self.assertIn('RECOVERY_AUTHORIZATION_REQUIRED',out['reason']); self.assertEqual(self._minimum(),(1,self.r1['record_digest']))

    def test_p16_05_forged_recovery_authorization_denied_before_mutation(self):
        bad=self._auth(); bad['signature']='AAAA'; out=self.proc.advance(bad); self.assertFalse(out['ok']); self.assertIn('RECOVERY_AUTHORIZATION_INVALID',out['reason']); self.assertEqual(self._minimum(),(1,self.r1['record_digest']))

    def test_p16_06_current_minimum_epoch_or_digest_substitution_denied(self):
        for field,value in [('current_minimum_epoch',0),('current_minimum_digest','forged')]:
            auth=self._auth(); auth['permit'][field]=value
            out=self.proc.advance(auth); self.assertFalse(out['ok']); self.assertIn('RECOVERY_AUTHORIZATION_INVALID',out['reason'])
        self.assertEqual(self._minimum(),(1,self.r1['record_digest']))

    def test_p16_07_target_root_record_digest_substitution_denied(self):
        auth=self._auth(); auth['permit']['target_root_record_digest']='forged'; out=self.proc.advance(auth); self.assertFalse(out['ok']); self.assertIn('RECOVERY_AUTHORIZATION_INVALID',out['reason']); self.assertEqual(self._minimum()[0],1)

    def test_p16_08_target_semantic_binding_substitutions_denied(self):
        changes={'target_root_id':'RX','target_public_key_fingerprint':'00','predecessor_root_record_digest':'bad','transition_id':'ROOT-X','activation_registry_epoch':99}
        for field,value in changes.items():
            auth=self._auth(); auth['permit'][field]=value; out=self.proc.advance(auth); self.assertFalse(out['ok']); self.assertIn('RECOVERY_AUTHORIZATION_INVALID',out['reason'])
        self.assertEqual(self._minimum()[0],1)

    def test_p16_09_exact_successful_authorization_replay_is_idempotent(self):
        auth=self._auth(); a=self.proc.advance(auth); b=self.proc.advance(auth); self.assertTrue(a['ok']); self.assertTrue(b['ok']); self.assertFalse(a['replay']); self.assertTrue(b['replay']); self.assertEqual(a['minimum'],b['minimum'])
        c=sqlite3.connect(self.mindb); n=c.execute('SELECT COUNT(*) FROM recovery_ledger').fetchone()[0]; c.close(); self.assertEqual(n,1)

    def test_p16_10_same_recovery_identity_semantic_rebinding_denied(self):
        self._recover_r2('REC-SAME')
        r3=self.trust.rotate(transition_id='ROOT-T3',expected_prior_root_id='R2',next_root_id='R3',next_public_key_pem=self.root_keys['R3'],activation_registry_epoch=2)
        rebound=self.rec.issue('REC-SAME',2,self.r2['record_digest'],r3); out=self.proc.advance(rebound); self.assertFalse(out['ok']); self.assertIn('RECOVERY_ID_REBIND_DENIED',out['reason']); self.assertEqual(self._minimum()[0],2)

    def test_p16_11_old_valid_authorization_below_current_minimum_denied(self):
        old=self._auth('REC-OLD'); self._recover_r2('REC-NOW'); out=self.proc.advance(old); self.assertFalse(out['ok']); self.assertIn('CURRENT_MINIMUM_BINDING_MISMATCH',out['reason']); self.assertEqual(self._minimum()[0],2)

    def test_p16_12_minimum_authority_outage_leaves_ambiguous_root_failclosed_zero_mutation(self):
        self.proc.stop(kill=True); out=self.proc.advance(self._auth()); self.assertFalse(out['ok']); self.assertEqual(out['reason'],'MINIMUM_AUTHORITY_UNAVAILABLE'); self.assertEqual(self._minimum(),(1,self.r1['record_digest']))

    def test_p16_13_restart_preserves_minimum_and_replay_rebinding_memory(self):
        auth=self._auth('REC-R'); first=self.proc.advance(auth); self.assertTrue(first['ok']); self.proc.stop(kill=True); self.proc.start(); replay=self.proc.advance(auth); self.assertTrue(replay['ok']); self.assertTrue(replay['replay']); self.assertEqual(self._minimum()[0],2)
        r3=self.trust.rotate(transition_id='ROOT-T3',expected_prior_root_id='R2',next_root_id='R3',next_public_key_pem=self.root_keys['R3'],activation_registry_epoch=2)
        bad=self.rec.issue('REC-R',2,self.r2['record_digest'],r3); denied=self.proc.advance(bad); self.assertFalse(denied['ok']); self.assertIn('RECOVERY_ID_REBIND_DENIED',denied['reason'])

    def test_p16_14_two_recovery_clients_race_exact_authorization_converge_one_binding(self):
        auth=self._auth('REC-RACE'); results=[]
        def run():results.append(self.proc.advance(copy.deepcopy(auth)))
        a=threading.Thread(target=run); b=threading.Thread(target=run); a.start(); b.start(); a.join(); b.join()
        self.assertEqual(len(results),2); self.assertTrue(all(x['ok'] for x in results)); self.assertEqual(results[0]['minimum'],results[1]['minimum']); self.assertEqual(sum(not x['replay'] for x in results),1)
        c=sqlite3.connect(self.mindb); n=c.execute('SELECT COUNT(*) FROM recovery_ledger').fetchone()[0]; c.close(); self.assertEqual(n,1)

    def test_p16_15_nonplatform_surfaces_retain_zero_minimum_release_or_production_authority(self):
        prohibited={'minimum-advance','release','deploy','production'}
        model_claim={'release','minimum-advance'}; reviewer_claim={'deploy','production'}
        # Claims are inert data: only a valid RecoveryAuthorizationAuthority signature crosses the process gate.
        self.assertTrue(model_claim & prohibited); self.assertTrue(reviewer_claim & prohibited)
        self.assertEqual(self._minimum()[0],1)
        self.assertFalse(self.proc.advance({'requested_authority':list(model_claim)})['ok'])
        self.assertEqual(self._minimum()[0],1)

    def test_p16_16_clean_r2_to_r3_authorized_transition_remains_live(self):
        self._recover_r2('REC-2')
        r3=self.trust.rotate(transition_id='ROOT-T3',expected_prior_root_id='R2',next_root_id='R3',next_public_key_pem=self.root_keys['R3'],activation_registry_epoch=2)
        auth3=self.rec.issue('REC-3',2,self.r2['record_digest'],r3); out=self.proc.advance(auth3); self.assertTrue(out['ok'],out); self.assertEqual(tuple(out['minimum']),(3,r3['record_digest'])); self.assertEqual(self._minimum()[0],3)

if __name__=='__main__':unittest.main()
