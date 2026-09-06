from __future__ import annotations

import copy
import json
import os
import sqlite3
import tempfile
import threading
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from exp_i_claim_convergence_gate import ReviewClaim, VerificationArtifact
from exp_i_composite_authority_process import CompositeCheckpointAuthorityProcess
from exp_i_durable_convergence_permit import DurableConvergencePermitAuthority
from exp_i_use_time_checkpoint import UseTimeCheckpointAuthority

CASE = "EXP-I-P11-CASE"
PERMIT_KEY = b"exp-i-pilot11-permit-key"
PERMIT_INTEGRITY_KEY = b"exp-i-pilot11-permit-integrity-key"
RECON_INTEGRITY_KEY = b"exp-i-pilot11-reconciliation-integrity-key"
CHECKPOINT_KEY = b"exp-i-pilot11-checkpoint-key"
TOKEN_KEY = b"exp-i-pilot11-token-key"


def reviews():
    return [ReviewClaim(x, CASE, "CODE DEFECT", ("CODE",)) for x in ("r1", "r2", "r3")]


def verifier():
    return VerificationArtifact("platform-independent-verifier", True, True, CASE, "CODE DEFECT", ("CODE",))


def signals():
    return {
        "evidence_complete": True,
        "requirement_ambiguity": False,
        "material_conflict": False,
        "r3_completed": True,
        "r3_required": True,
        "r3_available_qualified": True,
        "review_ceiling_reached": False,
        "material_revision_since_review": False,
        "authoritative_failure_established": False,
        "non_material_dissent": False,
        "max_unresolved_severity": "NONE",
    }


class ExpIPilot11DualLiveAuthorityContentionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.main_db = self.root / "governance.sqlite"
        self.authority_db = self.root / "composite-authority.sqlite"
        self.permits = DurableConvergencePermitAuthority(self.main_db, PERMIT_KEY)
        self.permits.issue(reviews(), verifier(), signals(), nonce="permit-1")
        self.use_time = UseTimeCheckpointAuthority(
            self.main_db, PERMIT_KEY, PERMIT_INTEGRITY_KEY, TOKEN_KEY
        )
        self.processes = []

    def tearDown(self):
        for p in self.processes:
            try:
                p.stop(kill=True)
            except Exception:
                pass
        self.tmp.cleanup()

    def authority(self):
        p = CompositeCheckpointAuthorityProcess(
            main_db=self.main_db,
            authority_store=self.authority_db,
            checkpoint_key=CHECKPOINT_KEY,
            permit_integrity_key=PERMIT_INTEGRITY_KEY,
            reconciliation_integrity_key=RECON_INTEGRITY_KEY,
        )
        self.processes.append(p)
        return p

    def pair(self):
        return self.authority(), self.authority()

    def race(self, fn_a, fn_b):
        barrier = threading.Barrier(2)
        def wrapped(fn):
            barrier.wait(timeout=5)
            return fn()
        with ThreadPoolExecutor(max_workers=2) as pool:
            fa = pool.submit(wrapped, fn_a)
            fb = pool.submit(wrapped, fn_b)
            return fa.result(timeout=15), fb.result(timeout=15)

    def rows(self):
        con = sqlite3.connect(self.authority_db, timeout=5.0)
        con.row_factory = sqlite3.Row
        try:
            return [dict(r) for r in con.execute("SELECT * FROM issued ORDER BY generation")]
        finally:
            con.close()

    def advance_governance(self, nonce="permit-2"):
        self.permits.issue(reviews(), verifier(), signals(), nonce=nonce)

    def test_p11_01_two_live_authority_processes_are_distinct_pids_and_share_only_registered_stores(self):
        a, b = self.pair()
        self.assertNotEqual(a.pid, b.pid)
        self.assertNotEqual(a.pid, os.getpid())
        self.assertEqual(Path(a.store).resolve(), Path(b.store).resolve())
        self.assertEqual(Path(a.main_db).resolve(), Path(b.main_db).resolve())

    def test_p11_02_concurrent_distinct_issuances_same_generation_yield_at_most_one_positive_issue(self):
        a, b = self.pair()
        ra, rb = self.race(lambda: a.issue("issuance-A", 1), lambda: b.issue("issuance-B", 1))
        self.assertEqual(sum(bool(r.get("ok")) for r in (ra, rb)), 1, (ra, rb))

    def test_p11_03_same_generation_race_leaves_exactly_one_durable_generation_row(self):
        a, b = self.pair()
        self.race(lambda: a.issue("issuance-A", 1), lambda: b.issue("issuance-B", 1))
        rows = self.rows()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["generation"], 1)

    def test_p11_04_losing_same_generation_process_cannot_verify_its_conflicting_statement(self):
        a, b = self.pair()
        ra, rb = self.race(lambda: a.issue("issuance-A", 1), lambda: b.issue("issuance-B", 1))
        winner = ra if ra.get("ok") else rb
        loser = b if ra.get("ok") else a
        fake = copy.deepcopy(winner)
        fake["statement"]["issuance_id"] = "loser-conflict"
        self.assertFalse(loser.verify(fake, minimum_generation=1).get("ok"))

    def test_p11_05_concurrent_exact_same_issuance_converges_to_same_checkpoint_digest(self):
        a, b = self.pair()
        ra, rb = self.race(lambda: a.issue("issuance-1", 1), lambda: b.issue("issuance-1", 1))
        self.assertTrue(ra.get("ok"), ra)
        self.assertTrue(rb.get("ok"), rb)
        self.assertEqual(ra["checkpoint_digest"], rb["checkpoint_digest"])

    def test_p11_06_concurrent_exact_same_issuance_does_not_create_duplicate_durable_rows(self):
        a, b = self.pair()
        self.race(lambda: a.issue("issuance-1", 1), lambda: b.issue("issuance-1", 1))
        rows = self.rows()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["issuance_id"], "issuance-1")

    def test_p11_07_different_issuance_identity_cannot_rebind_existing_generation(self):
        a, b = self.pair()
        first = a.issue("issuance-1", 1)
        self.assertTrue(first.get("ok"), first)
        conflict = b.issue("issuance-other", 1)
        self.assertFalse(conflict.get("ok"))
        self.assertEqual(len(self.rows()), 1)

    def test_p11_08_same_issuance_identity_cannot_rebind_changed_governance_state(self):
        a, b = self.pair()
        first = a.issue("issuance-1", 1)
        self.assertTrue(first.get("ok"), first)
        self.advance_governance()
        rebound = b.issue("issuance-1", 1)
        self.assertFalse(rebound.get("ok"))
        self.assertEqual(rebound.get("reason"), "ISSUANCE_ID_REBINDING")

    def test_p11_09_authority_a_advances_generation_then_stale_authority_b_lower_generation_is_denied(self):
        a, b = self.pair()
        self.assertTrue(a.issue("issuance-1", 1).get("ok"))
        self.assertTrue(a.issue("issuance-2", 2).get("ok"))
        low = b.issue("issuance-low", 1)
        self.assertFalse(low.get("ok"))
        self.assertEqual(low.get("reason"), "CHECKPOINT_GENERATION_ROLLBACK")

    def test_p11_10_restart_after_higher_generation_preserves_maximum_and_equivocation_memory(self):
        a, b = self.pair()
        self.assertTrue(a.issue("issuance-1", 1).get("ok"))
        r2 = b.issue("issuance-2", 2)
        self.assertTrue(r2.get("ok"), r2)
        a.stop(kill=True); b.stop(kill=True)
        c, d = self.pair()
        self.assertFalse(c.issue("low", 1).get("ok"))
        self.assertFalse(d.issue("conflict", 2).get("ok"))

    def test_p11_11_authority_a_postcommit_response_loss_authority_b_retry_returns_same_checkpoint(self):
        a, b = self.pair()
        lost = a.issue("issuance-1", 1, crash_after_commit=True)
        self.assertFalse(lost.get("ok"))
        retry = b.issue("issuance-1", 1)
        self.assertTrue(retry.get("ok"), retry)
        self.assertTrue(retry.get("replay"))
        self.assertEqual(len(self.rows()), 1)

    def test_p11_12_killed_authority_process_does_not_leave_second_authoritative_generation(self):
        a, b = self.pair()
        lost = a.issue("issuance-1", 1, crash_after_commit=True)
        self.assertFalse(lost.get("ok"))
        conflict = b.issue("issuance-B", 1)
        self.assertFalse(conflict.get("ok"))
        self.assertEqual(len(self.rows()), 1)

    def test_p11_13_database_lock_contention_cannot_create_duplicate_or_false_positive_issue(self):
        a, b = self.pair()
        con = sqlite3.connect(self.authority_db, timeout=5.0, isolation_level=None)
        try:
            con.execute("BEGIN IMMEDIATE")
            with ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(a.issue, "issuance-1", 1)
                time.sleep(0.15)
                self.assertFalse(future.done())
                con.execute("COMMIT")
                r = future.result(timeout=10)
            self.assertTrue(r.get("ok"), r)
            conflict = b.issue("issuance-2", 1)
            self.assertFalse(conflict.get("ok"))
            self.assertEqual(len(self.rows()), 1)
        finally:
            try:
                con.close()
            except Exception:
                pass

    def test_p11_14_tampered_shared_authority_store_blocks_verification_from_both_processes(self):
        a, b = self.pair()
        r = a.issue("issuance-1", 1)
        self.assertTrue(r.get("ok"), r)
        con = sqlite3.connect(self.authority_db)
        try:
            statement = json.loads(con.execute("SELECT statement_json FROM issued WHERE generation=1").fetchone()[0])
            statement["issuance_id"] = "tampered"
            con.execute("UPDATE issued SET statement_json=? WHERE generation=1", (json.dumps(statement, sort_keys=True),))
            con.commit()
        finally:
            con.close()
        self.assertFalse(a.verify(r, minimum_generation=1).get("ok"))
        self.assertFalse(b.verify(r, minimum_generation=1).get("ok"))

    def test_p11_15_deleted_authority_row_blocks_verification_from_both_processes(self):
        a, b = self.pair()
        r = a.issue("issuance-1", 1)
        self.assertTrue(r.get("ok"), r)
        con = sqlite3.connect(self.authority_db)
        try:
            con.execute("DELETE FROM issued WHERE generation=1")
            con.commit()
        finally:
            con.close()
        self.assertFalse(a.verify(r, minimum_generation=1).get("ok"))
        self.assertFalse(b.verify(r, minimum_generation=1).get("ok"))

    def test_p11_16_stale_prior_positive_verification_cannot_survive_current_governance_state_change(self):
        a, b = self.pair()
        r = a.issue("issuance-1", 1)
        self.assertTrue(b.verify(r, minimum_generation=1).get("ok"))
        self.advance_governance()
        self.assertFalse(a.verify(r, minimum_generation=1).get("ok"))
        self.assertFalse(b.verify(r, minimum_generation=1).get("ok"))

    def test_p11_17_one_process_unavailable_other_process_requires_durable_current_state_not_peer_claim(self):
        a, b = self.pair()
        r = a.issue("issuance-1", 1)
        self.assertTrue(r.get("ok"), r)
        a.stop(kill=True)
        fabricated = copy.deepcopy(r)
        fabricated["checkpoint_digest"] = "0" * 64
        self.assertFalse(b.verify(fabricated, minimum_generation=1).get("ok"))
        self.assertTrue(b.verify(r, minimum_generation=1).get("ok"))

    def test_p11_18_repeated_parallel_retries_after_ambiguous_commit_remain_one_logical_checkpoint(self):
        a, b = self.pair()
        lost = a.issue("issuance-1", 1, crash_after_commit=True)
        self.assertFalse(lost.get("ok"))
        c = self.authority()
        for _ in range(4):
            rb, rc = self.race(lambda: b.issue("issuance-1", 1), lambda: c.issue("issuance-1", 1))
            self.assertTrue(rb.get("ok"), rb)
            self.assertTrue(rc.get("ok"), rc)
            self.assertEqual(rb["checkpoint_digest"], rc["checkpoint_digest"])
        self.assertEqual(len(self.rows()), 1)

    def test_p11_19_model_reviewer_or_process_success_flags_have_zero_release_authority(self):
        a, b = self.pair()
        r = a.issue("issuance-1", 1)
        v = b.verify(r, minimum_generation=1)
        self.assertTrue(v.get("ok"), v)
        self.assertFalse(v.get("reviewer_generated_authority"))
        self.assertFalse(v.get("production_authority"))
        self.assertFalse(v.get("release_authority"))

    def test_p11_20_clean_next_generation_liveness_with_two_live_processes_after_fault_cases(self):
        a, b = self.pair()
        r1 = a.issue("issuance-1", 1)
        self.assertTrue(r1.get("ok"), r1)
        r2a, r2b = self.race(lambda: a.issue("issuance-2", 2), lambda: b.issue("issuance-2", 2))
        self.assertTrue(r2a.get("ok"), r2a)
        self.assertTrue(r2b.get("ok"), r2b)
        self.assertEqual(r2a["checkpoint_digest"], r2b["checkpoint_digest"])
        self.assertTrue(a.verify(r2a, minimum_generation=2).get("ok"))
        self.assertTrue(b.verify(r2b, minimum_generation=2).get("ok"))
        self.assertEqual([r["generation"] for r in self.rows()], [1, 2])
