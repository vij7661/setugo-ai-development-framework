from __future__ import annotations

import copy
import json
import os
import sqlite3
import tempfile
import threading
import unittest
from pathlib import Path

from exp_i_asymmetric_checkpoint_signer import _canon, _ensure_ed25519_keypair, _ed25519_sign
from exp_i_isolated_minimum_authority import MinimumAuthorityProcess, RecoveryAuthorizationAuthority
from exp_i_isolated_recovery_signer import RecoverySignerProcess
from exp_i_root_rotation import PlatformRootTrustAuthority, RootMinimumAuthority, RotatingRootSigner, RootRotatingRegistry


class ExpIPilot17IsolatedRecoverySignerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.d = Path(self.tmp.name)
        self.rootdb = self.d / 'root.db'; self.rootauth = self.d / 'root-auth.key'; self.mindb = self.d / 'minimum.db'
        self.trust = PlatformRootTrustAuthority(self.rootdb, self.rootauth); self.minimum = RootMinimumAuthority(self.mindb)
        self.keys = {}
        for rid in ('R1', 'R2', 'R3'):
            pr = self.d / f'{rid}.priv'; pu = self.d / f'{rid}.pub'; _ensure_ed25519_keypair(str(pr), str(pu)); self.keys[rid] = pu.read_text()
        self.r1 = self.trust.bootstrap(transition_id='ROOT-T1', root_id='R1', public_key_pem=self.keys['R1'], activation_registry_epoch=0)
        self.minimum.advance(1, self.r1['record_digest'])
        self.r2 = self.trust.rotate(transition_id='ROOT-T2', expected_prior_root_id='R1', next_root_id='R2', next_public_key_pem=self.keys['R2'], activation_registry_epoch=1)
        self.signer = RecoverySignerProcess(self.rootdb, self.rootauth, self.mindb, self.d / 'recovery-signer-store')
        self.minproc = MinimumAuthorityProcess(self.rootdb, self.rootauth, self.mindb, self.signer.public_key_pem)
    def tearDown(self):
        for p in (getattr(self, 'minproc', None), getattr(self, 'signer', None)):
            if p:
                try: p.stop(kill=True)
                except Exception: pass
        self.tmp.cleanup()
    def _issue_r2(self, rid='REC-1', **extra):
        return self.signer.issue(rid, 'R2', **extra)
    def _minimum(self):
        c = sqlite3.connect(self.mindb); row = c.execute('SELECT root_epoch,record_digest FROM minimum WHERE id=1').fetchone(); c.close(); return (int(row[0]), str(row[1]))
    def _advance(self, auth): return self.minproc.advance({'permit': auth['permit'], 'signature': auth['signature']})
    def _recover_r2(self, rid='REC-1'):
        auth = self._issue_r2(rid); self.assertTrue(auth['ok'], auth); out = self._advance(auth); self.assertTrue(out['ok'], out); return auth, out

    def test_p17_01_recovery_signer_is_distinct_process_with_durable_issuance_store(self):
        ping = self.signer.request({'op':'ping'}); self.assertTrue(ping['ok']); self.assertNotEqual(ping['pid'], os.getpid())
        auth = self._issue_r2(); self.assertTrue(auth['ok']); ledger = self.d/'recovery-signer-store'/'issuance.db'; self.assertTrue(ledger.exists())
        c=sqlite3.connect(ledger); self.assertEqual(c.execute('SELECT COUNT(*) FROM issuance').fetchone()[0],1); c.close()

    def test_p17_02_non_signer_surfaces_expose_no_recovery_private_key_or_direct_sign(self):
        for obj in (self.signer, self.minproc, self.trust, self.minimum):
            self.assertFalse(hasattr(obj,'private_path')); self.assertFalse(hasattr(obj,'sign')); self.assertFalse(hasattr(obj,'issue_recovery_authorization'))
        for cls in (RotatingRootSigner, RootRotatingRegistry): self.assertFalse(hasattr(cls,'recovery_private_path'))
        self.assertNotIn('recovery-signing.private.pem', repr(vars(self.signer)))

    def test_p17_03_clean_ambiguous_r1_r2_derives_exact_contiguous_permit(self):
        auth=self._issue_r2(); self.assertTrue(auth['ok'],auth); p=auth['permit']
        self.assertEqual(p['current_minimum_epoch'],1); self.assertEqual(p['current_minimum_digest'],self.r1['record_digest'])
        self.assertEqual(p['target_root_epoch'],2); self.assertEqual(p['target_root_record_digest'],self.r2['record_digest']); self.assertEqual(p['target_root_id'],'R2')
        self.assertEqual(p['transition_id'],'ROOT-T2'); self.assertEqual(p['predecessor_root_record_digest'],self.r1['record_digest'])

    def test_p17_04_caller_semantic_injection_cannot_influence_signed_permit(self):
        auth=self._issue_r2('REC-INJECT', current_minimum_epoch=999, current_minimum_digest='evil', target_root_epoch=99, target_root_record_digest='evil', target_root_id='RX', target_public_key_fingerprint='evil', predecessor_root_record_digest='evil', transition_id='ROOT-X', activation_registry_epoch=999)
        self.assertTrue(auth['ok'],auth); p=auth['permit']; self.assertEqual(p['current_minimum_epoch'],1); self.assertEqual(p['target_root_epoch'],2); self.assertEqual(p['target_root_id'],'R2'); self.assertEqual(p['transition_id'],'ROOT-T2')

    def test_p17_05_wrong_key_forged_permit_rejected_by_minimum_authority(self):
        good=self._issue_r2(); self.assertTrue(good['ok'])
        pr=self.d/'wrong.priv'; pu=self.d/'wrong.pub'; _ensure_ed25519_keypair(str(pr),str(pu)); forged={'permit':copy.deepcopy(good['permit']),'signature':_ed25519_sign(str(pr),_canon(good['permit']))}
        out=self.minproc.advance(forged); self.assertFalse(out['ok']); self.assertIn('RECOVERY_AUTHORIZATION_INVALID',out['reason']); self.assertEqual(self._minimum()[0],1)

    def test_p17_06_nonexistent_or_wrong_target_selector_denied_without_issuance(self):
        for selector in ('RX','ROOT-NOT-REAL',''):
            out=self.signer.issue('REC-X-'+selector,selector); self.assertFalse(out['ok'])
        ledger=self.d/'recovery-signer-store'/'issuance.db'; c=sqlite3.connect(ledger); self.assertEqual(c.execute('SELECT COUNT(*) FROM issuance').fetchone()[0],0); c.close()

    def test_p17_07_target_at_or_below_current_minimum_denied_for_new_issuance(self):
        out=self.signer.issue('REC-R1','R1'); self.assertFalse(out['ok']); self.assertIn('TARGET_NOT_ABOVE_MINIMUM',out['reason'])
        self._recover_r2('REC-ADV')
        out2=self.signer.issue('REC-R2-OLD','R2'); self.assertFalse(out2['ok']); self.assertIn('TARGET_NOT_ABOVE_MINIMUM',out2['reason'])

    def test_p17_08_future_noncontiguous_root_denied_while_r2_unresolved(self):
        r3=self.trust.rotate(transition_id='ROOT-T3',expected_prior_root_id='R2',next_root_id='R3',next_public_key_pem=self.keys['R3'],activation_registry_epoch=2)
        self.assertEqual(r3['record']['root_epoch'],3); out=self.signer.issue('REC-FUTURE','R3'); self.assertFalse(out['ok']); self.assertIn('TARGET_NOT_CONTIGUOUS',out['reason']); self.assertEqual(self._minimum()[0],1)

    def test_p17_09_exact_issuance_replay_returns_same_permit_signature_one_ledger_row(self):
        a=self._issue_r2('REC-REPLAY'); b=self._issue_r2('REC-REPLAY'); self.assertTrue(a['ok']); self.assertTrue(b['ok']); self.assertFalse(a['replay']); self.assertTrue(b['replay']); self.assertEqual(a['permit'],b['permit']); self.assertEqual(a['signature'],b['signature'])
        c=sqlite3.connect(self.d/'recovery-signer-store'/'issuance.db'); self.assertEqual(c.execute('SELECT COUNT(*) FROM issuance').fetchone()[0],1); c.close()

    def test_p17_10_same_recovery_identity_cannot_rebind_target(self):
        a=self._issue_r2('REC-SAME'); self.assertTrue(a['ok']); self._advance(a)
        self.r3=self.trust.rotate(transition_id='ROOT-T3',expected_prior_root_id='R2',next_root_id='R3',next_public_key_pem=self.keys['R3'],activation_registry_epoch=2)
        out=self.signer.issue('REC-SAME','R3'); self.assertFalse(out['ok']); self.assertIn('RECOVERY_ID_REBIND_DENIED',out['reason'])

    def test_p17_11_signer_restart_preserves_exact_replay_and_rebinding_refusal(self):
        a=self._issue_r2('REC-R'); self.assertTrue(a['ok']); self.signer.stop(kill=True); self.signer.start(); b=self._issue_r2('REC-R'); self.assertTrue(b['ok']); self.assertTrue(b['replay']); self.assertEqual(a['signature'],b['signature'])
        self.assertTrue(self._advance(b)['ok']); self.r3=self.trust.rotate(transition_id='ROOT-T3',expected_prior_root_id='R2',next_root_id='R3',next_public_key_pem=self.keys['R3'],activation_registry_epoch=2)
        denied=self.signer.issue('REC-R','R3'); self.assertFalse(denied['ok']); self.assertIn('RECOVERY_ID_REBIND_DENIED',denied['reason'])

    def test_p17_12_signer_outage_blocks_new_issuance_and_zero_minimum_mutation(self):
        self.signer.stop(kill=True); out=self.signer.issue('REC-OFF','R2'); self.assertFalse(out['ok']); self.assertEqual(out['reason'],'RECOVERY_SIGNER_UNAVAILABLE'); self.assertEqual(self._minimum(),(1,self.r1['record_digest']))

    def test_p17_13_two_callers_racing_exact_issuance_converge_one_signed_permit(self):
        results=[]
        def run(): results.append(self._issue_r2('REC-RACE'))
        a=threading.Thread(target=run); b=threading.Thread(target=run); a.start(); b.start(); a.join(); b.join()
        self.assertEqual(len(results),2); self.assertTrue(all(x['ok'] for x in results)); self.assertEqual(results[0]['permit'],results[1]['permit']); self.assertEqual(results[0]['signature'],results[1]['signature']); self.assertEqual(sum(not x['replay'] for x in results),1)
        c=sqlite3.connect(self.d/'recovery-signer-store'/'issuance.db'); self.assertEqual(c.execute('SELECT COUNT(*) FROM issuance').fetchone()[0],1); c.close()

    def test_p17_14_state_drift_after_issuance_is_caught_at_minimum_use_time(self):
        stale=self._issue_r2('REC-STALE'); self.assertTrue(stale['ok']); self.minimum.advance(2,self.r2['record_digest'])
        out=self._advance(stale); self.assertFalse(out['ok']); self.assertIn('CURRENT_MINIMUM_BINDING_MISMATCH',out['reason']); self.assertEqual(self._minimum(),(2,self.r2['record_digest']))

    def test_p17_15_nonplatform_surfaces_have_zero_permit_mint_minimum_release_deploy_authority(self):
        claims={'model':['permit-mint','release'],'reviewer':['minimum-advance','deploy'],'root':['production']}
        before=self._minimum(); self.assertTrue(claims)
        bad=self.signer.request({'op':'issue','recovery_id':'REC-CLAIM','target_selector':'R2','current_minimum_epoch':999,'requested_authority':claims})
        self.assertTrue(bad['ok']); self.assertEqual(bad['permit']['current_minimum_epoch'],1); self.assertEqual(self._minimum(),before)
        self.assertFalse(hasattr(self.minproc,'sign')); self.assertFalse(hasattr(self.trust,'issue'))

    def test_p17_16_clean_r2_to_r3_signer_derived_recovery_remains_live(self):
        a2,out2=self._recover_r2('REC-2'); self.assertEqual(tuple(out2['minimum']),(2,self.r2['record_digest']))
        r3=self.trust.rotate(transition_id='ROOT-T3',expected_prior_root_id='R2',next_root_id='R3',next_public_key_pem=self.keys['R3'],activation_registry_epoch=2)
        a3=self.signer.issue('REC-3','R3'); self.assertTrue(a3['ok'],a3); self.assertEqual(a3['permit']['target_root_record_digest'],r3['record_digest']); out3=self._advance(a3); self.assertTrue(out3['ok'],out3); self.assertEqual(tuple(out3['minimum']),(3,r3['record_digest']))

if __name__=='__main__': unittest.main()
