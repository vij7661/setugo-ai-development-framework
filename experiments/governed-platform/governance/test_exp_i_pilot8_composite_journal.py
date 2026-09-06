import sqlite3
import tempfile
import threading
import unittest
from pathlib import Path

from exp_i_claim_convergence_gate import ReviewClaim, VerificationArtifact
from exp_i_composite_journal import DurableCompositeJournalAuthority
from exp_i_durable_convergence_permit import DurableConvergencePermitAuthority

CASE = "EXP-I-P8-CASE"
PERMIT_KEY = b"exp-i-pilot8-permit-key"
PERMIT_INTEGRITY_KEY = b"exp-i-pilot8-permit-integrity-key"
RECON_INTEGRITY_KEY = b"exp-i-pilot8-reconciliation-integrity-key"
COMPOSITE_KEY = b"exp-i-pilot8-composite-key"


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


class ExpIPilot8CompositeJournalTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = str(Path(self.tmp.name) / "p8.db")
        self.permits = DurableConvergencePermitAuthority(self.db, PERMIT_KEY)
        self.permit = self.permits.issue(reviews(), verifier(), signals(), nonce="permit-1")
        self.journal = DurableCompositeJournalAuthority(
            self.db,
            PERMIT_INTEGRITY_KEY,
            RECON_INTEGRITY_KEY,
            COMPOSITE_KEY,
        )
        self.cp1 = self.journal.issue("issuance-1", 1)

    def tearDown(self):
        self.tmp.cleanup()

    def sql(self, statement, params=()):
        con = sqlite3.connect(self.db, timeout=5.0)
        try:
            con.execute("PRAGMA ignore_check_constraints=ON")
            con.execute(statement, params)
            con.commit()
        finally:
            con.close()

    def current_count(self, generation):
        con = sqlite3.connect(self.db)
        try:
            return con.execute(
                "SELECT COUNT(*) FROM composite_checkpoint_journal WHERE generation=? AND status='CURRENT'",
                (generation,),
            ).fetchone()[0]
        finally:
            con.close()

    def test_p8_01_clean_initial_issuance_durably_records_one_current(self):
        self.assertEqual(self.cp1.status, "CURRENT")
        self.assertEqual(self.current_count(1), 1)
        self.assertTrue(self.journal.verify_record(self.cp1, trusted_min_generation=1).valid)

    def test_p8_02_crash_before_journal_insert_leaves_no_false_current(self):
        with self.assertRaises(RuntimeError):
            self.journal.issue("issuance-2", 2, crash_at="before_insert")
        self.assertIsNone(self.journal.get("issuance-2"))
        self.assertEqual(self.current_count(2), 0)

    def test_p8_03_crash_after_pending_insert_remains_noncurrent_after_restart(self):
        with self.assertRaises(RuntimeError):
            self.journal.issue("issuance-2", 2, crash_at="after_pending")
        restarted = DurableCompositeJournalAuthority(self.db, PERMIT_INTEGRITY_KEY, RECON_INTEGRITY_KEY, COMPOSITE_KEY)
        record = restarted.get("issuance-2")
        self.assertEqual(record.status, "PENDING")
        self.assertFalse(restarted.verify_record(record, trusted_min_generation=2).valid)
        self.assertFalse(restarted.recover("issuance-2").valid)

    def test_p8_04_crash_after_authenticated_material_stays_failclosed_until_recovery(self):
        with self.assertRaises(RuntimeError):
            self.journal.issue("issuance-2", 2, crash_at="after_material")
        restarted = DurableCompositeJournalAuthority(self.db, PERMIT_INTEGRITY_KEY, RECON_INTEGRITY_KEY, COMPOSITE_KEY)
        record = restarted.get("issuance-2")
        self.assertEqual(record.status, "PENDING")
        self.assertFalse(restarted.verify_record(record, trusted_min_generation=2).valid)

    def test_p8_05_matching_pending_recovery_promotes_exactly_once(self):
        with self.assertRaises(RuntimeError):
            self.journal.issue("issuance-2", 2, crash_at="after_material")
        restarted = DurableCompositeJournalAuthority(self.db, PERMIT_INTEGRITY_KEY, RECON_INTEGRITY_KEY, COMPOSITE_KEY)
        self.assertTrue(restarted.recover("issuance-2").valid)
        cp2 = restarted.get("issuance-2")
        self.assertEqual(cp2.status, "CURRENT")
        self.assertTrue(restarted.recover("issuance-2").valid)
        self.assertEqual(self.current_count(2), 1)

    def test_p8_06_pending_recovery_refuses_changed_permit_ledger(self):
        with self.assertRaises(RuntimeError):
            self.journal.issue("issuance-2", 2, crash_at="after_material")
        self.permits.advance_epoch()
        self.assertFalse(self.journal.recover("issuance-2").valid)
        self.assertEqual(self.current_count(2), 0)

    def test_p8_07_pending_recovery_refuses_changed_reconciliation_ledger(self):
        with self.assertRaises(RuntimeError):
            self.journal.issue("issuance-2", 2, crash_at="after_material")
        self.sql(
            "INSERT INTO convergence_reconciliation(reconciliation_id,token_nonce,permit_nonce,pre_ledger_digest,post_ledger_digest,checkpoint_generation,status,settlement_checkpoint_digest) VALUES(?,?,?,?,?,?,?,?)",
            ("r-x", "t-x", "permit-1", "a" * 64, "b" * 64, 1, "PENDING", None),
        )
        self.assertFalse(self.journal.recover("issuance-2").valid)
        self.assertEqual(self.current_count(2), 0)

    def test_p8_08_pending_recovery_refuses_changed_permit_authority_epoch(self):
        with self.assertRaises(RuntimeError):
            self.journal.issue("issuance-2", 2, crash_at="after_material")
        self.sql("UPDATE authority_meta SET issuance_epoch=issuance_epoch+1 WHERE singleton=1")
        self.assertFalse(self.journal.recover("issuance-2").valid)

    def test_p8_09_postcurrent_preack_crash_replays_same_checkpoint_idempotently(self):
        with self.assertRaises(RuntimeError):
            self.journal.issue("issuance-2", 2, crash_at="after_current")
        first = self.journal.get("issuance-2")
        replay = self.journal.issue("issuance-2", 2)
        self.assertEqual(first, replay)
        self.assertEqual(self.current_count(2), 1)

    def test_p8_10_same_issuance_identity_cannot_rebind_state_pair(self):
        cp2 = self.journal.issue("issuance-2", 2)
        self.permits.advance_epoch()
        with self.assertRaises(PermissionError):
            self.journal.issue("issuance-2", 2)
        self.assertEqual(self.journal.get("issuance-2"), cp2)

    def test_p8_11_same_issuance_identity_cannot_rebind_generation(self):
        self.journal.issue("issuance-2", 2)
        with self.assertRaises(PermissionError):
            self.journal.issue("issuance-2", 3)

    def test_p8_12_stale_or_invalid_predecessor_blocks_next_generation(self):
        self.sql("UPDATE composite_checkpoint_journal SET tag='00' WHERE issuance_id='issuance-1'")
        with self.assertRaises(PermissionError):
            self.journal.issue("issuance-2", 2)
        self.assertEqual(self.current_count(2), 0)

    def test_p8_13_forged_or_mutated_durable_authentication_fails_after_restart(self):
        cp2 = self.journal.issue("issuance-2", 2)
        self.sql("UPDATE composite_checkpoint_journal SET tag='11' WHERE issuance_id='issuance-2'")
        restarted = DurableCompositeJournalAuthority(self.db, PERMIT_INTEGRITY_KEY, RECON_INTEGRITY_KEY, COMPOSITE_KEY)
        self.assertFalse(restarted.verify_record(restarted.get("issuance-2"), trusted_min_generation=2).valid)
        self.assertFalse(restarted.verify_record(cp2, trusted_min_generation=2).valid)

    def test_p8_14_coherent_journal_row_rewrite_without_key_fails_closed(self):
        self.journal.issue("issuance-2", 2)
        self.sql(
            "UPDATE composite_checkpoint_journal SET permit_ledger_digest=?,reconciliation_digest=? WHERE issuance_id='issuance-2'",
            ("a" * 64, "b" * 64),
        )
        record = self.journal.get("issuance-2")
        self.assertFalse(self.journal.verify_record(record, trusted_min_generation=2).valid)

    def test_p8_15_latest_current_deletion_detected_against_trusted_minimum(self):
        self.journal.issue("issuance-2", 2)
        self.sql("DELETE FROM composite_checkpoint_journal WHERE issuance_id='issuance-2'")
        decision = self.journal.verify_latest(trusted_min_generation=2)
        self.assertFalse(decision.valid)

    def test_p8_16_lower_generation_rollback_rejected_after_minimum_advances(self):
        self.journal.issue("issuance-2", 2)
        decision = self.journal.verify_record(self.cp1, trusted_min_generation=2)
        self.assertFalse(decision.valid)
        self.assertIn("below trusted minimum", decision.reasons[0])

    def test_p8_17_concurrent_same_generation_cannot_both_become_current(self):
        results = []
        lock = threading.Lock()
        barrier = threading.Barrier(2)

        def run(issuance_id):
            local = DurableCompositeJournalAuthority(self.db, PERMIT_INTEGRITY_KEY, RECON_INTEGRITY_KEY, COMPOSITE_KEY)
            barrier.wait()
            try:
                record = local.issue(issuance_id, 2)
                value = ("ok", record.issuance_id)
            except PermissionError:
                value = ("denied", issuance_id)
            with lock:
                results.append(value)

        threads = [threading.Thread(target=run, args=(x,)) for x in ("issuance-a", "issuance-b")]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(sum(1 for status, _ in results if status == "ok"), 1)
        self.assertEqual(self.current_count(2), 1)

    def test_p8_18_distinct_state_pairs_cannot_manufacture_two_current_same_generation(self):
        with self.assertRaises(RuntimeError):
            self.journal.issue("issuance-a", 2, crash_at="after_material")
        self.permits.advance_epoch()
        with self.assertRaises(PermissionError):
            self.journal.issue("issuance-b", 2)
        self.assertFalse(self.journal.recover("issuance-a").valid)
        self.assertEqual(self.current_count(2), 0)

    def test_p8_19_models_reviewers_have_zero_journal_or_release_authority(self):
        d = self.journal.verify_record(self.cp1, trusted_min_generation=1)
        self.assertFalse(d.reviewer_generated_authority)
        self.assertFalse(d.production_authority)
        self.assertFalse(d.release_authority)
        self.assertFalse(hasattr(reviews()[0], "issue_composite_checkpoint"))
        self.assertFalse(hasattr(reviews()[0], "mutate_composite_journal"))

    def test_p8_20_clean_higher_generation_liveness_after_prior_cycle(self):
        cp2 = self.journal.issue("issuance-2", 2)
        self.assertTrue(self.journal.verify_record(cp2, trusted_min_generation=2).valid)
        cp3 = self.journal.issue("issuance-3", 3)
        restarted = DurableCompositeJournalAuthority(self.db, PERMIT_INTEGRITY_KEY, RECON_INTEGRITY_KEY, COMPOSITE_KEY)
        self.assertTrue(restarted.verify_record(cp3, trusted_min_generation=3).valid)
        self.assertEqual(self.current_count(3), 1)


if __name__ == "__main__":
    unittest.main()
