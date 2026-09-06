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
from exp_i_issuance_anchor_crash_consistency import (
    IssuanceAnchorCrashConsistentSignerProcess,
    ReconciledMinimumAuthorityProcess,
    _anchor_envelope,
    _ensure_anchor_key,
    _paths,
)
from exp_i_root_rotation import PlatformRootTrustAuthority, RootMinimumAuthority


class ExpIPilot19IssuanceAnchorCrashConsistencyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.d = Path(self.tmp.name)
        self.rootdb = self.d / "root.db"; self.rootauth = self.d / "root-auth.key"; self.mindb = self.d / "minimum.db"
        self.store = self.d / "recovery-signer-store"; self.anchor = self.d / "independent-anchor"
        self.trust = PlatformRootTrustAuthority(self.rootdb, self.rootauth); self.minimum = RootMinimumAuthority(self.mindb)
        self.keys = {}
        for rid in ("R1", "R2", "R3"):
            pr = self.d / f"{rid}.priv"; pu = self.d / f"{rid}.pub"; _ensure_ed25519_keypair(str(pr), str(pu)); self.keys[rid] = pu.read_text()
        self.r1 = self.trust.bootstrap(transition_id="ROOT-T1", root_id="R1", public_key_pem=self.keys["R1"], activation_registry_epoch=0)
        self.minimum.advance(1, self.r1["record_digest"])
        self.r2 = self.trust.rotate(transition_id="ROOT-T2", expected_prior_root_id="R1", next_root_id="R2", next_public_key_pem=self.keys["R2"], activation_registry_epoch=1)
        self.signer = IssuanceAnchorCrashConsistentSignerProcess(self.rootdb, self.rootauth, self.mindb, self.store, self.anchor)
        self.minproc = ReconciledMinimumAuthorityProcess(self.rootdb, self.rootauth, self.mindb, self.signer.public_key_pem, self.store, self.anchor)

    def tearDown(self):
        for p in (getattr(self, "minproc", None), getattr(self, "signer", None)):
            if p:
                try: p.stop(kill=True)
                except Exception: pass
        self.tmp.cleanup()

    def _minimum(self):
        c = sqlite3.connect(self.mindb); row = c.execute("SELECT root_epoch,record_digest FROM minimum WHERE id=1").fetchone(); c.close(); return int(row[0]), str(row[1])

    def _advance(self, a):
        return self.minproc.advance({"permit": a["permit"], "signature": a["signature"]})

    def _crash(self, boundary, rid="REC-1", selector="R2"):
        h = self.signer.crash_at(boundary, rid, selector)
        self.assertEqual(h.readiness["ready"], boundary)
        self.assertNotEqual(h.pid, os.getpid())
        self.assertIsNone(h.proc.poll())
        h.kill(); self.assertIsNotNone(h.proc.poll())
        return h

    def _status(self):
        out = self.signer.status(); self.assertTrue(out["ok"], out); return out["status"]

    def _snapshot_paths(self):
        _, _, ledger, anchor, key = _paths(self.store, self.anchor)
        return Path(ledger), Path(anchor), Path(key)

    def _issue_reconciled_r2(self, rid="REC-R2"):
        out = self.signer.issue(rid, "R2"); self.assertTrue(out["ok"], out); self.assertEqual(self._status()["state"], "RECONCILED"); return out

    def test_p19_01_distinct_child_and_parent_external_kill_at_ledger_anchor_boundary(self):
        h = self.signer.crash_at("after_ledger_commit_before_anchor", "REC-PID", "R2")
        self.assertEqual(h.readiness["ready"], "after_ledger_commit_before_anchor"); self.assertNotEqual(h.pid, os.getpid()); self.assertIsNone(h.proc.poll())
        h.kill(); self.assertIsNotNone(h.proc.poll())

    def test_p19_02_kill_after_ledger_commit_leaves_explicit_divergence_not_false_success(self):
        self._crash("after_ledger_commit_before_anchor", "REC-DIVERGE")
        st = self._status(); self.assertEqual(st["state"], "LEDGER_AHEAD_EXACT"); self.assertEqual(st["reason"], "RECONCILIATION_REQUIRED"); self.assertEqual(self._minimum()[0], 1)

    def test_p19_03_fresh_restart_detects_ledger_newer_before_minimum_mutation(self):
        h = self.signer.crash_at("after_ledger_commit_before_anchor", "REC-RESTART", "R2")
        permit = h.readiness["status"]["ledger"]; h.kill(); self.signer.stop(kill=True); self.signer.start()
        st = self._status(); self.assertEqual(st["state"], "LEDGER_AHEAD_EXACT"); self.assertEqual(self._minimum()[0], 1)
        rows = self.signer.ledger_rows(); stored = json.loads(rows[0][3]); denied = self.minproc.advance({"permit": stored, "signature": rows[0][4]}); self.assertFalse(denied["ok"]); self.assertEqual(denied["reason"], "ISSUANCE_ANCHOR_UNRESOLVED")

    def test_p19_04_exact_ledger_ahead_reconciliation_advances_anchor_once(self):
        self._crash("after_ledger_commit_before_anchor", "REC-RECON")
        first = self.signer.reconcile(); self.assertTrue(first["ok"], first); self.assertFalse(first["replay"]); self.assertEqual(self._status()["state"], "RECONCILED")
        second = self.signer.reconcile(); self.assertTrue(second["ok"]); self.assertTrue(second["replay"]); self.assertEqual(self._status()["ledger"]["generation"], 1)

    def test_p19_05_kill_after_anchor_temp_before_replace_never_accepts_temp_as_current(self):
        ledger, anchor, _ = self._snapshot_paths(); prior = anchor.read_text()
        self._crash("after_anchor_temp_before_replace", "REC-TEMP")
        self.assertEqual(anchor.read_text(), prior); self.assertTrue(Path(str(anchor) + ".tmp").exists())
        st = self._status(); self.assertEqual(st["state"], "LEDGER_AHEAD_EXACT"); self.assertNotEqual(st["state"], "RECONCILED")
        out = self.signer.reconcile(); self.assertTrue(out["ok"], out); self.assertEqual(self._status()["state"], "RECONCILED")

    def test_p19_06_kill_after_atomic_replace_before_response_is_replay_safe(self):
        self._crash("after_anchor_replace_before_response", "REC-REPLACE")
        st = self._status(); self.assertEqual(st["state"], "ANCHOR_REPLACED_RECEIPT_PENDING")
        rec = self.signer.reconcile(); self.assertTrue(rec["ok"], rec); self.assertEqual(self._status()["state"], "RECONCILED")
        replay = self.signer.issue("REC-REPLACE", "R2"); self.assertTrue(replay["ok"]); self.assertTrue(replay["replay"]); self.assertEqual(len(self.signer.ledger_rows()), 1)

    def test_p19_07_anchor_newer_than_ledger_is_never_auto_authorized(self):
        ledger, anchor, _ = self._snapshot_paths(); stale = self.d / "ledger-stale.db"; shutil.copy2(ledger, stale)
        self._issue_reconciled_r2("REC-AHEAD")
        self.signer.stop(kill=True); shutil.copy2(stale, ledger); self.signer.start()
        st = self._status(); self.assertEqual(st["state"], "FAIL_CLOSED"); self.assertEqual(st["reason"], "STALE_LEDGER_OR_ANCHOR_AHEAD")
        self.assertFalse(self.signer.reconcile()["ok"]); self.assertEqual(self._minimum()[0], 1)

    def test_p19_08_recovery_identity_cannot_rebind_during_or_after_reconciliation(self):
        self._crash("after_ledger_commit_before_anchor", "REC-SAME")
        denied = self.signer.issue("REC-SAME", "R3"); self.assertFalse(denied["ok"])
        self.assertTrue(self.signer.reconcile()["ok"])
        self.assertTrue(self._advance(self.signer.issue("REC-SAME", "R2"))["ok"])
        self.r3 = self.trust.rotate(transition_id="ROOT-T3", expected_prior_root_id="R2", next_root_id="R3", next_public_key_pem=self.keys["R3"], activation_registry_epoch=2)
        denied2 = self.signer.issue("REC-SAME", "R3"); self.assertFalse(denied2["ok"]); self.assertIn("RECOVERY_ID_REBIND_DENIED", denied2["reason"])

    def test_p19_09_stale_ledger_snapshot_after_reconciliation_fails_closed(self):
        ledger, _, _ = self._snapshot_paths(); stale = self.d / "ledger-before.db"; shutil.copy2(ledger, stale)
        self._issue_reconciled_r2("REC-LEDGER-ROLLBACK")
        self.signer.stop(kill=True); shutil.copy2(stale, ledger); self.signer.start()
        st = self._status(); self.assertEqual(st["state"], "FAIL_CLOSED"); self.assertEqual(st["reason"], "STALE_LEDGER_OR_ANCHOR_AHEAD")

    def test_p19_10_stale_anchor_snapshot_after_reconciliation_fails_closed(self):
        _, anchor, _ = self._snapshot_paths(); stale = self.d / "anchor-before.json"; shutil.copy2(anchor, stale)
        self._issue_reconciled_r2("REC-ANCHOR-ROLLBACK")
        shutil.copy2(stale, anchor)
        st = self._status(); self.assertEqual(st["state"], "FAIL_CLOSED"); self.assertEqual(st["reason"], "STALE_ANCHOR_ROLLBACK"); self.assertFalse(self.signer.reconcile()["ok"])

    def test_p19_11_conflicting_same_generation_anchor_cannot_be_caller_selected(self):
        _, anchor, key_path = self._snapshot_paths(); self._issue_reconciled_r2("REC-CONFLICT")
        st = self._status(); evil = copy.deepcopy(st["anchor"]); evil["last_digest"] = "0" * 64
        key = _ensure_anchor_key(str(key_path)); anchor.write_text(json.dumps(_anchor_envelope(key, evil), sort_keys=True))
        bad = self._status(); self.assertEqual(bad["state"], "FAIL_CLOSED"); self.assertEqual(bad["reason"], "CONFLICTING_SAME_GENERATION_ANCHOR"); self.assertFalse(self.signer.reconcile()["ok"])

    def test_p19_12_two_reconcilers_racing_converge_one_exact_anchor(self):
        self._crash("after_ledger_commit_before_anchor", "REC-RACE")
        results = []
        a = IssuanceAnchorCrashConsistentSignerProcess(self.rootdb, self.rootauth, self.mindb, self.store, self.anchor)
        b = IssuanceAnchorCrashConsistentSignerProcess(self.rootdb, self.rootauth, self.mindb, self.store, self.anchor)
        try:
            t1 = threading.Thread(target=lambda: results.append(a.reconcile())); t2 = threading.Thread(target=lambda: results.append(b.reconcile()))
            t1.start(); t2.start(); t1.join(); t2.join()
            self.assertEqual(len(results), 2); self.assertTrue(all(x["ok"] for x in results)); self.assertEqual(self._status()["state"], "RECONCILED"); self.assertEqual(self._status()["ledger"]["generation"], 1)
        finally:
            a.stop(kill=True); b.stop(kill=True)

    def test_p19_13_repeated_crash_restart_reconciliation_preserves_monotonic_memory(self):
        self._crash("after_anchor_temp_before_replace", "REC-REPEAT")
        for _ in range(3):
            self.signer.stop(kill=True); self.signer.start(); out = self.signer.reconcile(); self.assertTrue(out["ok"], out); self.assertEqual(self._status()["state"], "RECONCILED")
        replay = self.signer.issue("REC-REPEAT", "R2"); self.assertTrue(replay["ok"]); self.assertTrue(replay["replay"]); self.assertEqual(self._status()["ledger"]["generation"], 1)

    def test_p19_14_valid_signature_cannot_bypass_unresolved_ledger_anchor_correspondence(self):
        self._crash("after_ledger_commit_before_anchor", "REC-VALID-SIG")
        row = self.signer.ledger_rows()[0]; authorization = {"permit": json.loads(row[3]), "signature": row[4]}
        out = self.minproc.advance(authorization); self.assertFalse(out["ok"]); self.assertEqual(out["reason"], "ISSUANCE_ANCHOR_UNRESOLVED"); self.assertEqual(self._minimum()[0], 1)

    def test_p19_15_nonplatform_surfaces_gain_zero_reconciliation_or_release_authority(self):
        before = self._minimum(); claims = {"model": ["reconcile", "minimum-advance"], "reviewer": ["release", "deploy"], "registry": ["production"]}
        out = self.signer.issue("REC-CLAIM", "R2", requested_authority=claims, selected_reconciliation="evil")
        self.assertTrue(out["ok"], out); self.assertEqual(self._minimum(), before); self.assertFalse(hasattr(self.minproc, "reconcile")); self.assertFalse(hasattr(self.trust, "reconcile_issuance_anchor")); self.assertEqual(self._status()["state"], "RECONCILED")

    def test_p19_16_r2_r3_liveness_after_killed_divergence_recovery(self):
        self._crash("after_ledger_commit_before_anchor", "REC-R2")
        self.assertTrue(self.signer.reconcile()["ok"]); a2 = self.signer.issue("REC-R2", "R2"); out2 = self._advance(a2); self.assertTrue(out2["ok"], out2); self.assertEqual(tuple(out2["minimum"]), (2, self.r2["record_digest"]))
        r3 = self.trust.rotate(transition_id="ROOT-T3", expected_prior_root_id="R2", next_root_id="R3", next_public_key_pem=self.keys["R3"], activation_registry_epoch=2)
        a3 = self.signer.issue("REC-R3", "R3"); self.assertTrue(a3["ok"], a3); out3 = self._advance(a3); self.assertTrue(out3["ok"], out3); self.assertEqual(tuple(out3["minimum"]), (3, r3["record_digest"])); self.assertEqual(self._status()["ledger"]["generation"], 2)


if __name__ == "__main__":
    unittest.main()
