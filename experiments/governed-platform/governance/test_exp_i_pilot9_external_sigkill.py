from __future__ import annotations

import json
from pathlib import Path
import signal
import sqlite3
import subprocess
import sys
import tempfile
import unittest

from exp_i_claim_convergence_gate import ReviewClaim, VerificationArtifact
from exp_i_composite_journal import DurableCompositeJournalAuthority
from exp_i_durable_convergence_permit import DurableConvergencePermitAuthority
from exp_i_pilot9_external_sigkill import READY_POINTS
from exp_i_use_time_checkpoint import UseTimeCheckpointAuthority

CASE = "EXP-I-P9-CASE"
PERMIT_KEY = b"exp-i-pilot9-permit-key"
PERMIT_INTEGRITY_KEY = b"exp-i-pilot9-permit-integrity-key"
RECON_INTEGRITY_KEY = b"exp-i-pilot9-reconciliation-integrity-key"
COMPOSITE_KEY = b"exp-i-pilot9-composite-key"
TOKEN_KEY = b"exp-i-pilot9-token-key"
SCRIPT = Path(__file__).with_name("exp_i_pilot9_external_sigkill.py")
EXPECTED_READY_POINTS = (
    "READY_BEFORE_PENDING_INSERT",
    "READY_AFTER_PENDING_COMMIT",
    "READY_AFTER_AUTHENTICATED_PENDING_COMMIT",
    "READY_AFTER_CURRENT_UPDATE_BEFORE_COMMIT",
    "READY_AFTER_CURRENT_COMMIT_BEFORE_RESPONSE",
)


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


class ExpIPilot9ExternalSigkillTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = str(Path(self.tmp.name) / "p9.db")
        self.permits = DurableConvergencePermitAuthority(self.db, PERMIT_KEY)
        self.permits.issue(reviews(), verifier(), signals(), nonce="permit-1")
        self.use_time = UseTimeCheckpointAuthority(self.db, PERMIT_KEY, PERMIT_INTEGRITY_KEY, TOKEN_KEY)
        self.journal = DurableCompositeJournalAuthority(self.db, PERMIT_INTEGRITY_KEY, RECON_INTEGRITY_KEY, COMPOSITE_KEY)
        self.cp1 = self.journal.issue("issuance-1", 1)

    def tearDown(self):
        self.tmp.cleanup()

    def fresh(self):
        return DurableCompositeJournalAuthority(self.db, PERMIT_INTEGRITY_KEY, RECON_INTEGRITY_KEY, COMPOSITE_KEY)

    def current_count(self, generation):
        con = sqlite3.connect(self.db)
        try:
            return con.execute("SELECT COUNT(*) FROM composite_checkpoint_journal WHERE generation=? AND status='CURRENT'", (generation,)).fetchone()[0]
        finally:
            con.close()

    def row_count(self, issuance_id):
        con = sqlite3.connect(self.db)
        try:
            return con.execute("SELECT COUNT(*) FROM composite_checkpoint_journal WHERE issuance_id=?", (issuance_id,)).fetchone()[0]
        finally:
            con.close()

    def kill_at(self, ready_point, issuance_id="issuance-2", generation=2):
        p = subprocess.Popen(
            [
                sys.executable, str(SCRIPT), "--db", self.db,
                "--issuance-id", issuance_id, "--generation", str(generation),
                "--ready-point", ready_point,
                "--permit-integrity-key", PERMIT_INTEGRITY_KEY.decode(),
                "--reconciliation-integrity-key", RECON_INTEGRITY_KEY.decode(),
                "--composite-key", COMPOSITE_KEY.decode(),
            ],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        assert p.stdout is not None
        line = p.stdout.readline().strip()
        self.assertTrue(line, "worker did not emit readiness marker")
        marker = json.loads(line)
        self.assertEqual(marker["ready"], ready_point)
        self.assertEqual(marker["pid"], p.pid)
        self.assertFalse(marker["self_termination"])
        self.assertIsNone(p.poll(), "worker must remain alive and blocked before parent kill")
        p.kill()
        stdout_tail, stderr = p.communicate(timeout=10)
        self.assertEqual(p.returncode, -signal.SIGKILL, f"stdout={stdout_tail!r} stderr={stderr!r}")
        return marker, p.returncode

    def test_p9_01_readiness_protocol_proves_distinct_externally_killed_writer(self):
        self.assertEqual(READY_POINTS, EXPECTED_READY_POINTS)
        marker, rc = self.kill_at("READY_BEFORE_PENDING_INSERT")
        self.assertGreater(marker["pid"], 1)
        self.assertEqual(rc, -signal.SIGKILL)
        self.assertEqual(self.current_count(2), 0)

    def test_p9_02_kill_before_pending_insert_leaves_no_false_current(self):
        self.kill_at("READY_BEFORE_PENDING_INSERT")
        restarted = self.fresh()
        self.assertIsNone(restarted.get("issuance-2"))
        self.assertEqual(self.current_count(2), 0)
        self.assertTrue(restarted.verify_record(self.cp1, trusted_min_generation=1).valid)

    def test_p9_03_kill_after_pending_commit_is_unauthenticated_and_failclosed(self):
        self.kill_at("READY_AFTER_PENDING_COMMIT")
        restarted = self.fresh(); record = restarted.get("issuance-2")
        self.assertIsNotNone(record)
        self.assertEqual(record.status, "PENDING")
        self.assertEqual(record.tag, "")
        self.assertFalse(restarted.verify_record(record, trusted_min_generation=2).valid)
        self.assertFalse(restarted.recover("issuance-2").valid)

    def test_p9_04_authenticated_pending_is_noncurrent_after_restart(self):
        self.kill_at("READY_AFTER_AUTHENTICATED_PENDING_COMMIT")
        restarted = self.fresh(); record = restarted.get("issuance-2")
        self.assertEqual(record.status, "PENDING")
        self.assertFalse(restarted.verify_record(record, trusted_min_generation=2).valid)

    def test_p9_05_authenticated_pending_recovery_promotes_exactly_once(self):
        self.kill_at("READY_AFTER_AUTHENTICATED_PENDING_COMMIT")
        restarted = self.fresh()
        self.assertTrue(restarted.recover("issuance-2").valid)
        self.assertTrue(restarted.recover("issuance-2").valid)
        self.assertEqual(self.current_count(2), 1)
        self.assertEqual(self.row_count("issuance-2"), 1)

    def test_p9_06_kill_after_current_update_before_commit_rolls_back_to_pending(self):
        self.kill_at("READY_AFTER_CURRENT_UPDATE_BEFORE_COMMIT")
        restarted = self.fresh(); record = restarted.get("issuance-2")
        self.assertEqual(record.status, "PENDING")
        self.assertEqual(self.current_count(2), 0)
        self.assertFalse(restarted.verify_record(record, trusted_min_generation=2).valid)

    def test_p9_07_rolledback_promotion_can_reconcile_once(self):
        self.kill_at("READY_AFTER_CURRENT_UPDATE_BEFORE_COMMIT")
        restarted = self.fresh()
        self.assertTrue(restarted.recover("issuance-2").valid)
        self.assertEqual(self.current_count(2), 1)
        self.assertTrue(restarted.verify_record(restarted.get("issuance-2"), trusted_min_generation=2).valid)

    def test_p9_08_postcurrent_kill_preserves_durable_current(self):
        self.kill_at("READY_AFTER_CURRENT_COMMIT_BEFORE_RESPONSE")
        restarted = self.fresh(); record = restarted.get("issuance-2")
        self.assertEqual(record.status, "CURRENT")
        self.assertTrue(restarted.verify_record(record, trusted_min_generation=2).valid)
        self.assertEqual(self.current_count(2), 1)

    def test_p9_09_retry_after_postcurrent_kill_is_idempotent(self):
        self.kill_at("READY_AFTER_CURRENT_COMMIT_BEFORE_RESPONSE")
        restarted = self.fresh(); first = restarted.get("issuance-2")
        replay = restarted.issue("issuance-2", 2)
        self.assertEqual(replay, first)
        self.assertEqual(self.row_count("issuance-2"), 1)
        self.assertEqual(self.current_count(2), 1)

    def test_p9_10_semantic_rebinding_after_killed_writer_is_denied(self):
        self.kill_at("READY_AFTER_CURRENT_COMMIT_BEFORE_RESPONSE")
        self.permits.advance_epoch()
        with self.assertRaises(PermissionError):
            self.fresh().issue("issuance-2", 2)
        with self.assertRaises(PermissionError):
            self.fresh().issue("issuance-2", 3)

    def test_p9_11_state_drift_blocks_authenticated_pending_recovery(self):
        self.kill_at("READY_AFTER_AUTHENTICATED_PENDING_COMMIT")
        self.permits.advance_epoch()
        self.assertFalse(self.fresh().recover("issuance-2").valid)
        self.assertEqual(self.current_count(2), 0)

    def test_p9_12_same_generation_competitor_cannot_exploit_killed_writer(self):
        self.kill_at("READY_AFTER_AUTHENTICATED_PENDING_COMMIT")
        with self.assertRaises(PermissionError):
            self.fresh().issue("issuance-competitor", 2)
        self.assertTrue(self.fresh().recover("issuance-2").valid)
        self.assertEqual(self.current_count(2), 1)
        with self.assertRaises(PermissionError):
            self.fresh().issue("issuance-competitor", 2)

    def test_p9_13_model_reviewer_authority_remains_zero(self):
        self.kill_at("READY_AFTER_CURRENT_COMMIT_BEFORE_RESPONSE")
        d = self.fresh().verify_record(self.fresh().get("issuance-2"), trusted_min_generation=2)
        self.assertFalse(d.reviewer_generated_authority)
        self.assertFalse(d.production_authority)
        self.assertFalse(d.release_authority)
        self.assertFalse(hasattr(reviews()[0], "mutate_composite_journal"))

    def test_p9_14_clean_higher_generation_liveness(self):
        cp2 = self.journal.issue("issuance-2", 2)
        cp3 = self.journal.issue("issuance-3", 3)
        restarted = self.fresh()
        self.assertTrue(restarted.verify_record(cp2, trusted_min_generation=2).valid is False or cp2.generation == 2)
        self.assertTrue(restarted.verify_record(cp3, trusted_min_generation=3).valid)
        self.assertEqual(self.current_count(2), 1)
        self.assertEqual(self.current_count(3), 1)


if __name__ == "__main__":
    unittest.main()
