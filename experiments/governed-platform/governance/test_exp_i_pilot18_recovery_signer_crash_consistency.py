from __future__ import annotations

import copy
import json
import os
import shutil
import sqlite3
import tempfile
import threading
import unittest
from pathlib import Path

from exp_i_asymmetric_checkpoint_signer import _ensure_ed25519_keypair
from exp_i_crash_aware_minimum import CrashAwareMinimumAuthorityProcess
from exp_i_recovery_signer_crash_consistency import CrashConsistentRecoverySignerProcess
from exp_i_root_rotation import PlatformRootTrustAuthority, RootMinimumAuthority


class ExpIPilot18RecoverySignerCrashConsistencyTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.d=Path(self.tmp.name)
        self.rootdb=self.d/'root.db'; self.rootauth=self.d/'root-auth.key'; self.mindb=self.d/'minimum.db'
        self.store=self.d/'recovery-signer-store'; self.anchor=self.d/'independent-anchor'
        self.trust=PlatformRootTrustAuthority(self.rootdb,self.rootauth); self.minimum=RootMinimumAuthority(self.mindb)
        self.keys={}
        for rid in ('R1','R2','R3'):
            pr=self.d/f'{rid}.priv'; pu=self.d/f'{rid}.pub'; _ensure_ed25519_keypair(str(pr),str(pu)); self.keys[rid]=pu.read_text()
        self.r1=self.trust.bootstrap(transition_id='ROOT-T1',root_id='R1',public_key_pem=self.keys['R1'],activation_registry_epoch=0)
        self.minimum.advance(1,self.r1['record_digest'])
        self.r2=self.trust.rotate(transition_id='ROOT-T2',expected_prior_root_id='R1',next_root_id='R2',next_public_key_pem=self.keys['R2'],activation_registry_epoch=1)
        self.signer=CrashConsistentRecoverySignerProcess(self.rootdb,self.rootauth,self.mindb,self.store,self.anchor)
        self.minproc=CrashAwareMinimumAuthorityProcess(self.rootdb,self.rootauth,self.mindb,self.signer.public_key_pem,self.store,self.anchor)
    def tearDown(self):
        for p in (getattr(self,'minproc',None),getattr(self,'signer',None)):
            if p:
                try:p.stop(kill=True)
                except Exception:pass
        self.tmp.cleanup()
    def _minimum(self):
        c=sqlite3.connect(self.mindb); row=c.execute('SELECT root_epoch,record_digest FROM minimum WHERE id=1').fetchone(); c.close(); return int(row[0]),str(row[1])
    def _advance(self,a): return self.minproc.advance({'permit':a['permit'],'signature':a['signature']})
    def _crash(self,boundary,rid='REC-1',selector='R2'):
        h=self.signer.crash_at(boundary,rid,selector); self.assertEqual(h.readiness['ready'],boundary); self.assertNotEqual(h.pid,os.getpid()); h.kill(); return h
    def _rows(self): return self.signer.ledger_rows()
    def _recover_r2(self,rid='REC-2'):
        a=self.signer.issue(rid,'R2'); self.assertTrue(a['ok'],a); out=self._advance(a); self.assertTrue(out['ok'],out); return a,out

    def test_p18_01_parent_observed_distinct_child_and_external_termination(self):
        h=self.signer.crash_at('before_txn','REC-PID','R2'); self.assertEqual(h.readiness['ready'],'before_txn'); self.assertNotEqual(h.pid,os.getpid()); self.assertIsNone(h.proc.poll()); h.kill(); self.assertIsNotNone(h.proc.poll())

    def test_p18_02_kill_before_transaction_leaves_no_issuance_or_authority(self):
        self._crash('before_txn','REC-BEFORE'); self.assertEqual(self._rows(),[]); self.assertEqual(self._minimum(),(1,self.r1['record_digest']))

    def test_p18_03_kill_after_begin_before_insert_leaves_no_row(self):
        self._crash('after_begin','REC-BEGIN'); self.assertEqual(self._rows(),[]); self.assertEqual(self._minimum()[0],1)

    def test_p18_04_kill_after_insert_before_commit_rolls_back(self):
        h=self.signer.crash_at('after_insert_precommit','REC-PRECOMMIT','R2'); captured={'permit':h.readiness['permit'],'signature':h.readiness['signature']}; h.kill(); self.assertEqual(self._rows(),[])
        out=self.minproc.advance(captured); self.assertFalse(out['ok']); self.assertIn('ISSUANCE_NOT_COMMITTED',out['reason']); self.assertEqual(self._minimum()[0],1)

    def test_p18_05_postcommit_preresponse_kill_preserves_exactly_one_row(self):
        self._crash('after_commit_pre_response','REC-DURABLE'); rows=self._rows(); self.assertEqual(len(rows),1); self.assertEqual(rows[0][1],'REC-DURABLE')

    def test_p18_06_retry_after_postcommit_response_loss_returns_exact_same_permit(self):
        h=self.signer.crash_at('after_commit_pre_response','REC-RETRY','R2'); original={'permit':h.readiness['permit'],'signature':h.readiness['signature']}; h.kill()
        replay=self.signer.issue('REC-RETRY','R2'); self.assertTrue(replay['ok']); self.assertTrue(replay['replay']); self.assertEqual(replay['permit'],original['permit']); self.assertEqual(replay['signature'],original['signature']); self.assertEqual(len(self._rows()),1)

    def test_p18_07_same_identity_cannot_rebind_after_killed_committed_issuance(self):
        self._crash('after_commit_pre_response','REC-SAME'); replay=self.signer.issue('REC-SAME','R2'); self.assertTrue(replay['ok']); self.assertTrue(self._advance(replay)['ok'])
        self.r3=self.trust.rotate(transition_id='ROOT-T3',expected_prior_root_id='R2',next_root_id='R3',next_public_key_pem=self.keys['R3'],activation_registry_epoch=2)
        denied=self.signer.issue('REC-SAME','R3'); self.assertFalse(denied['ok']); self.assertIn('RECOVERY_ID_REBIND_DENIED',denied['reason'])

    def test_p18_08_precommit_signed_material_is_not_minimum_authority(self):
        h=self.signer.crash_at('after_insert_precommit','REC-NOCOMMIT','R2'); a={'permit':h.readiness['permit'],'signature':h.readiness['signature']}; h.kill(); out=self.minproc.advance(a); self.assertFalse(out['ok']); self.assertEqual(out['reason'],'ISSUANCE_NOT_COMMITTED'); self.assertEqual(self._minimum()[0],1)

    def test_p18_09_committed_permit_still_requires_minimum_use_time_state_match(self):
        h=self.signer.crash_at('after_commit_pre_response','REC-STALE','R2'); a={'permit':h.readiness['permit'],'signature':h.readiness['signature']}; h.kill(); self.minimum.advance(2,self.r2['record_digest']); out=self.minproc.advance(a); self.assertFalse(out['ok']); self.assertIn('CURRENT_MINIMUM_BINDING_MISMATCH',out['reason']); self.assertEqual(self._minimum()[0],2)

    def test_p18_10_two_retries_after_kill_converge_one_exact_permit(self):
        h=self.signer.crash_at('after_commit_pre_response','REC-RACE','R2'); sig=h.readiness['signature']; h.kill(); results=[]
        def run(): results.append(self.signer.issue('REC-RACE','R2'))
        a=threading.Thread(target=run); b=threading.Thread(target=run); a.start(); b.start(); a.join(); b.join()
        self.assertEqual(len(results),2); self.assertTrue(all(x['ok'] and x['replay'] for x in results)); self.assertTrue(all(x['signature']==sig for x in results)); self.assertEqual(len(self._rows()),1)

    def test_p18_11_repeated_restart_preserves_replay_and_rebinding_memory(self):
        h=self.signer.crash_at('after_commit_pre_response','REC-RESTART','R2'); sig=h.readiness['signature']; h.kill()
        for _ in range(3): self.signer.stop(kill=True); self.signer.start(); out=self.signer.issue('REC-RESTART','R2'); self.assertTrue(out['ok']); self.assertTrue(out['replay']); self.assertEqual(out['signature'],sig)
        self.assertEqual(len(self._rows()),1)

    def test_p18_12_stale_issuance_snapshot_substitution_fails_closed_against_anchor(self):
        ledger=self.store/'issuance.db'; stale=self.d/'stale.db'; shutil.copy2(ledger,stale)
        a=self.signer.issue('REC-NEW','R2'); self.assertTrue(a['ok']); self.assertEqual(len(self._rows()),1)
        self.signer.stop(kill=True); shutil.copy2(stale,ledger); self.signer.start(); out=self.signer.issue('REC-AFTER-ROLLBACK','R2'); self.assertFalse(out['ok']); self.assertIn('ISSUANCE_ROLLBACK_OR_DIVERGENCE',out['reason']); self.assertEqual(self._minimum()[0],1)

    def test_p18_13_signer_outage_after_precommit_kill_cannot_mutate_minimum(self):
        h=self.signer.crash_at('after_insert_precommit','REC-OFF','R2'); a={'permit':h.readiness['permit'],'signature':h.readiness['signature']}; h.kill(); self.signer.stop(kill=True)
        self.assertFalse(self.signer.issue('REC-OFF','R2')['ok']); self.assertFalse(self.minproc.advance(a)['ok']); self.assertEqual(self._minimum()[0],1)

    def test_p18_14_caller_semantic_injection_remains_ineffective_after_crash_retry(self):
        self._crash('after_commit_pre_response','REC-INJECT'); out=self.signer.issue('REC-INJECT','R2',current_minimum_epoch=999,target_root_id='RX',transition_id='EVIL'); self.assertTrue(out['ok']); p=out['permit']; self.assertEqual(p['current_minimum_epoch'],1); self.assertEqual(p['target_root_id'],'R2'); self.assertEqual(p['transition_id'],'ROOT-T2')

    def test_p18_15_nonplatform_surfaces_gain_zero_signer_minimum_release_authority(self):
        before=self._minimum(); claims={'model':['sign','minimum-advance'],'reviewer':['release','deploy'],'registry':['production']}; out=self.signer.issue('REC-CLAIM','R2',requested_authority=claims,current_minimum_epoch=999); self.assertTrue(out['ok']); self.assertEqual(out['permit']['current_minimum_epoch'],1); self.assertEqual(self._minimum(),before); self.assertFalse(hasattr(self.minproc,'sign')); self.assertFalse(hasattr(self.trust,'issue'))

    def test_p18_16_r2_r3_liveness_after_crash_replay_recovery(self):
        self._crash('after_commit_pre_response','REC-R2'); a2=self.signer.issue('REC-R2','R2'); out2=self._advance(a2); self.assertTrue(out2['ok']); self.assertEqual(tuple(out2['minimum']),(2,self.r2['record_digest']))
        r3=self.trust.rotate(transition_id='ROOT-T3',expected_prior_root_id='R2',next_root_id='R3',next_public_key_pem=self.keys['R3'],activation_registry_epoch=2)
        a3=self.signer.issue('REC-R3','R3'); self.assertTrue(a3['ok']); out3=self._advance(a3); self.assertTrue(out3['ok']); self.assertEqual(tuple(out3['minimum']),(3,r3['record_digest']))

if __name__=='__main__': unittest.main()
