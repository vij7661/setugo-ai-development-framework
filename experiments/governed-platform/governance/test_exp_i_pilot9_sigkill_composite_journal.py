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
from exp_i_sigkill_composite_worker import READY_POINTS
from exp_i_use_time_checkpoint import UseTimeCheckpointAuthority

CASE = "EXP-I-P9-CASE"
PERMIT_KEY = b"exp-i-pilot9-permit-key"
PERMIT_INTEGRITY_KEY = b"exp-i-pilot9-permit-integrity-key"
RECON_INTEGRITY_KEY = b"exp-i-pilot9-reconciliation-integrity-key"
COMPOSITE_KEY = b"exp-i-pilot9-composite-key"
TOKEN_KEY = b"exp-i-pilot9-token-key"
SCRIPT = Path(__file__).with_name("exp_i_sigkill_composite_worker.py")
EXPECTED_READY_POINTS = (
    "READY_BEFORE_INSERT",
    "READY_AFTER_PENDING_COMMIT",
    "READY_AFTER_MATERIAL_COMMIT",
    "READY_AFTER_CURRENT_COMMIT",
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


class ExpIPilot9SigkillCompositeJournalTests(unittest.TestCase):
    def setUp(self):
        if not hasattr(signal, "SIGKILL"):
            self.skipTest("Pilot 9 requires POSIX SIGKILL semantics")
        self.tmp = tempfile.TemporaryDirectory()
        self.db = str(Path(self.tmp.name) / "p9.db")
        self.permits = DurableConvergencePermitAuthority(self.db, PERMIT_KEY)
        self.permit = self.permits.issue(reviews(), verifier(), signals(), nonce="permit-1")
        self.use_time = UseTimeCheckpointAuthority(self.db, PERMIT_KEY, PERMIT_INTEGRITY_KEY, TOKEN_KEY)
        self.journal = self.fresh()
        self.cp1 = self.journal.issue("issuance-1", 1)

    def tearDown(self):
        self.tmp.cleanup()

    def fresh(self):
        return DurableCompositeJournalAuthority(
            self.db, PERMIT_INTEGRITY_KEY, RECON_INTEGRITY_KEY, COMPOSITE_KEY
        )

    def worker_args(self, issuance_id, generation, ready_point=None):
        args = [
            sys.executable, str(SCRIPT),
            "--db", self.db,
            "--issuance-id", issuance_id,
            "--generation", str(generation),
            "--permit-integrity-key", PERMIT_INTEGRITY_KEY.hex(),
            "--reconciliation-integrity-key", RECON_INTEGRITY_KEY.hex(),
            "--composite-key", COMPOSITE_KEY.hex(),
        ]
        if ready_point:
            args += ["--ready-point", ready_point]
        return args

    def kill_at(self, issuance_id, generation, ready_point):
        p = subprocess.Popen(
            self.worker_args(issuance_id, generation, ready_point),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        assert p.stdout is not None
        line = p.stdout.readline().strip()
        self.assertTrue(line, "worker emitted no stage marker")
        marker = json.loads(line)
        self.assertEqual(marker["ready"], ready_point)
        self.assertEqual(marker["pid"], p.pid)
        self.assertFalse(marker["self_termination"])
        self.assertIsNone(p.poll(), "child must remain alive until parent termination")
        p.kill()
        stdout_tail, stderr = p.communicate(timeout=10)
        self.assertEqual(p.returncode, -signal.SIGKILL, f"stdout={stdout_tail!r} stderr={stderr!r}")
        return marker

    def run_clean(self, issuance_id, generation):
        cp = subprocess.run(
            self.worker_args(issuance_id, generation),
            capture_output=True,
            text=True,
            timeout=10,
        )
        line = cp.stdout.strip().splitlines()[-1] if cp.stdout.strip() else ""
        result = json.loads(line) if line else None
        return cp, result

    def sql(self, statement, params=()):
        con = sqlite3.connect(self.db, timeout=5.0)
        try:
            con.execute("PRAGMA ignore_check_constraints=ON")
            con.execute(statement, params)
            con.commit()
        finally:
            con.close()

    def count_current(self, generation):
        con = sqlite3.connect(self.db)
        try:
            return con.execute(
                "SELECT COUNT(*) FROM composite_checkpoint_journal WHERE generation=? AND status='CURRENT'",
                (generation,),
            ).fetchone()[0]
        finally:
            con.close()

    def test_p9_01_readiness_protocol_proves_distinct_externally_killed_child(self):
        self.assertEqual(READY_POINTS, EXPECTED_READY_POINTS)
        marker = self.kill_at("issuance-2", 2, "READY_BEFORE_INSERT")
        self.assertGreater(marker["pid"], 1)
        self.assertNotEqual(marker["pid"], __import__("os").getpid())
        self.assertIsNone(self.fresh().get("issuance-2"))

    def test_p9_02_sigkill_before_insert_leaves_no_false_current(self):
        self.kill_at("issuance-2", 2, "READY_BEFORE_INSERT")
        j = self.fresh()
        self.assertIsNone(j.get("issuance-2"))
        self.assertFalse(j.verify_latest(trusted_min_generation=2).valid)

    def test_p9_03_sigkill_after_pending_commit_leaves_noncurrent(self):
        self.kill_at("issuance-2", 2, "READY_AFTER_PENDING_COMMIT")
        record = self.fresh().get("issuance-2")
        self.assertIsNotNone(record)
        self.assertEqual(record.status, "PENDING")
        self.assertFalse(self.fresh().verify_record(record, trusted_min_generation=2).valid)

    def test_p9_04_sigkill_after_authenticated_material_stays_failclosed(self):
        self.kill_at("issuance-2", 2, "READY_AFTER_MATERIAL_COMMIT")
        record = self.fresh().get("issuance-2")
        self.assertEqual(record.status, "PENDING")
        self.assertTrue(bool(record.tag))
        self.assertFalse(self.fresh().verify_record(record, trusted_min_generation=2).valid)

    def test_p9_05_matching_authenticated_pending_recovers_once_after_sigkill(self):
        self.kill_at("issuance-2", 2, "READY_AFTER_MATERIAL_COMMIT")
        j = self.fresh()
        self.assertTrue(j.recover("issuance-2").valid)
        self.assertEqual(j.get("issuance-2").status, "CURRENT")
        self.assertTrue(self.fresh().recover("issuance-2").valid)
        self.assertEqual(self.count_current(2), 1)

    def test_p9_06_permit_ledger_mutation_after_kill_blocks_recovery(self):
        self.kill_at("issuance-2", 2, "READY_AFTER_MATERIAL_COMMIT")
        self.permits.issue(reviews(), verifier(), signals(), nonce="permit-2")
        self.assertFalse(self.fresh().recover("issuance-2").valid)
        self.assertEqual(self.count_current(2), 0)

    def test_p9_07_reconciliation_mutation_after_kill_blocks_recovery(self):
        self.kill_at("issuance-2", 2, "READY_AFTER_MATERIAL_COMMIT")
        self.sql(
            "INSERT INTO convergence_reconciliation(reconciliation_id,token_nonce,permit_nonce,pre_ledger_digest,post_ledger_digest,checkpoint_generation,status,settlement_checkpoint_digest) VALUES(?,?,?,?,?,?,?,?)",
            ("r-x", "t-x", "permit-1", "a" * 64, "b" * 64, 1, "PENDING", None),
        )
        self.assertFalse(self.fresh().recover("issuance-2").valid)

    def test_p9_08_permit_epoch_change_after_kill_blocks_recovery(self):
        self.kill_at("issuance-2", 2, "READY_AFTER_MATERIAL_COMMIT")
        self.sql("UPDATE authority_meta SET issuance_epoch=issuance_epoch+1 WHERE singleton=1")
        self.assertFalse(self.fresh().recover("issuance-2").valid)

    def test_p9_09_sigkill_after_current_commit_preserves_exactly_one_current(self):
        self.kill_at("issuance-2", 2, "READY_AFTER_CURRENT_COMMIT")
        j = self.fresh()
        record = j.get("issuance-2")
        self.assertEqual(record.status, "CURRENT")
        self.assertTrue(j.verify_record(record, trusted_min_generation=2).valid)
        self.assertEqual(self.count_current(2), 1)

    def test_p9_10_retry_after_postcurrent_kill_returns_same_durable_checkpoint(self):
        self.kill_at("issuance-2", 2, "READY_AFTER_CURRENT_COMMIT")
        before = self.fresh().get("issuance-2")
        cp, result = self.run_clean("issuance-2", 2)
        self.assertEqual(cp.returncode, 0, cp.stderr)
        self.assertTrue(result["ok"])
        after = self.fresh().get("issuance-2")
        self.assertEqual(before, after)
        self.assertEqual(self.count_current(2), 1)

    def test_p9_11_restart_same_issuance_cannot_rebind_state_pair(self):
        self.kill_at("issuance-2", 2, "READY_AFTER_CURRENT_COMMIT")
        self.permits.issue(reviews(), verifier(), signals(), nonce="permit-2")
        cp, result = self.run_clean("issuance-2", 2)
        self.assertNotEqual(cp.returncode, 0)
        self.assertFalse(result["ok"])
        self.assertEqual(self.count_current(2), 1)

    def test_p9_12_restart_same_issuance_cannot_rebind_generation(self):
        self.kill_at("issuance-2", 2, "READY_AFTER_CURRENT_COMMIT")
        cp, result = self.run_clean("issuance-2", 3)
        self.assertNotEqual(cp.returncode, 0)
        self.assertFalse(result["ok"])
        self.assertIsNone(self.fresh().get("issuance-3"))

    def test_p9_13_tampered_predecessor_after_writer_death_blocks_next_generation(self):
        self.kill_at("issuance-2", 2, "READY_AFTER_CURRENT_COMMIT")
        self.sql("UPDATE composite_checkpoint_journal SET tag='00' WHERE issuance_id='issuance-2'")
        cp, result = self.run_clean("issuance-3", 3)
        self.assertNotEqual(cp.returncode, 0)
        self.assertFalse(result["ok"])
        self.assertEqual(self.count_current(3), 0)

    def test_p9_14_mutated_durable_authentication_fails_fresh_reopen(self):
        self.kill_at("issuance-2", 2, "READY_AFTER_CURRENT_COMMIT")
        self.sql("UPDATE composite_checkpoint_journal SET tag='11' WHERE issuance_id='issuance-2'")
        j = self.fresh()
        self.assertFalse(j.verify_record(j.get("issuance-2"), trusted_min_generation=2).valid)

    def test_p9_15_latest_current_deletion_detected_against_trusted_minimum(self):
        self.kill_at("issuance-2", 2, "READY_AFTER_CURRENT_COMMIT")
        self.sql("DELETE FROM composite_checkpoint_journal WHERE issuance_id='issuance-2'")
        self.assertFalse(self.fresh().verify_latest(trusted_min_generation=2).valid)

    def test_p9_16_old_valid_generation_rejected_after_minimum_advances(self):
        self.kill_at("issuance-2", 2, "READY_AFTER_CURRENT_COMMIT")
        self.assertFalse(self.fresh().verify_record(self.cp1, trusted_min_generation=2).valid)

    def test_p9_17_two_child_writers_same_next_generation_at_most_one_current(self):
        p1 = subprocess.Popen(self.worker_args("issuance-a", 2), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        p2 = subprocess.Popen(self.worker_args("issuance-b", 2), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        out1, err1 = p1.communicate(timeout=10)
        out2, err2 = p2.communicate(timeout=10)
        results = []
        for p, out, err in ((p1, out1, err1), (p2, out2, err2)):
            self.assertTrue(out.strip(), err)
            results.append(json.loads(out.strip().splitlines()[-1]))
        self.assertEqual(sum(1 for x in results if x["ok"]), 1)
        self.assertEqual(self.count_current(2), 1)

    def test_p9_18_killed_pending_plus_competing_state_pair_cannot_make_two_current(self):
        self.kill_at("issuance-a", 2, "READY_AFTER_MATERIAL_COMMIT")
        self.permits.issue(reviews(), verifier(), signals(), nonce="permit-2")
        cp, result = self.run_clean("issuance-b", 2)
        self.assertNotEqual(cp.returncode, 0)
        self.assertFalse(result["ok"])
        self.assertFalse(self.fresh().recover("issuance-a").valid)
        self.assertEqual(self.count_current(2), 0)

    def test_p9_19_process_or_model_success_has_zero_release_authority(self):
        cp, result = self.run_clean("issuance-2", 2)
        self.assertEqual(cp.returncode, 0, cp.stderr)
        self.assertTrue(result["ok"])
        self.assertNotIn("production_authority", result)
        self.assertNotIn("release_authority", result)
        d = self.fresh().verify_latest(trusted_min_generation=2)
        self.assertFalse(d.reviewer_generated_authority)
        self.assertFalse(d.production_authority)
        self.assertFalse(d.release_authority)

    def test_p9_20_clean_higher_generation_fresh_process_liveness(self):
        cp2, r2 = self.run_clean("issuance-2", 2)
        self.assertEqual(cp2.returncode, 0, cp2.stderr)
        self.assertTrue(r2["ok"])
        cp3, r3 = self.run_clean("issuance-3", 3)
        self.assertEqual(cp3.returncode, 0, cp3.stderr)
        self.assertTrue(r3["ok"])
        j = self.fresh()
        self.assertTrue(j.verify_latest(trusted_min_generation=3).valid)
        self.assertEqual(self.count_current(3), 1)


if __name__ == "__main__":
    unittest.main()
