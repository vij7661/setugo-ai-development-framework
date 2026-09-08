from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
import threading
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
GOVERNANCE = HERE / "governance"
if str(GOVERNANCE) not in sys.path:
    sys.path.insert(0, str(GOVERNANCE))

from authoritative_state_ledger import (  # noqa: E402
    AuthorityClaimRejected,
    AuthoritativeStateLedger,
    IdempotencyConflict,
    InjectedFailure,
    SimulatedCrashAfterCommit,
    VersionConflict,
)


class Slice5AuthoritativeStateLedgerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "ledger.sqlite3"
        self.ledger = AuthoritativeStateLedger(self.db)
        self.project = "project-alpha"

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def apply(self, *, key: str = "intent-1", expected: int = 0, value: str = "ready", fault: str | None = None):
        return self.ledger.apply_command(
            project_id=self.project,
            idempotency_key=key,
            command_type="PATCH_STATE",
            payload={"set": {"status": value}},
            expected_version=expected,
            effect_type="NOTIFY",
            effect_payload={"status": value},
            fault=fault,
        )

    def raw_outbox(self) -> list[dict]:
        con = sqlite3.connect(self.db)
        con.row_factory = sqlite3.Row
        try:
            return [dict(row) for row in con.execute("SELECT * FROM outbox ORDER BY outbox_id")]
        finally:
            con.close()

    def test_s5_01_first_valid_command_is_atomic(self):
        result = self.apply()
        self.assertFalse(result.replayed)
        self.assertEqual(result.version, 1)
        self.assertEqual(self.ledger.get_state(self.project), (1, {"status": "ready"}))
        self.assertEqual(self.ledger.counts(self.project), {"events": 1, "outbox": 1})
        pending = self.ledger.pending_outbox(self.project)
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0]["outbox_id"], result.outbox_id)

    def test_s5_02_exact_retry_returns_original_without_duplicates(self):
        first = self.apply()
        second = self.apply()
        self.assertTrue(second.replayed)
        self.assertEqual(second.event_id, first.event_id)
        self.assertEqual(second.outbox_id, first.outbox_id)
        self.assertEqual(second.result_digest, first.result_digest)
        self.assertEqual(second.version, first.version)
        self.assertEqual(self.ledger.counts(self.project), {"events": 1, "outbox": 1})
        self.assertEqual(self.ledger.get_state(self.project)[0], 1)

    def test_s5_03_idempotency_key_rebinding_is_rejected(self):
        self.apply()
        with self.assertRaises(IdempotencyConflict):
            self.apply(value="changed")
        self.assertEqual(self.ledger.counts(self.project), {"events": 1, "outbox": 1})
        self.assertEqual(self.ledger.get_state(self.project), (1, {"status": "ready"}))

    def test_s5_04_stale_expected_version_is_rejected_without_mutation(self):
        self.apply()
        with self.assertRaises(VersionConflict):
            self.apply(key="intent-2", expected=0, value="next")
        self.assertEqual(self.ledger.counts(self.project), {"events": 1, "outbox": 1})
        self.assertEqual(self.ledger.get_state(self.project), (1, {"status": "ready"}))

    def test_s5_05_future_expected_version_is_rejected_without_mutation(self):
        with self.assertRaises(VersionConflict):
            self.apply(expected=7)
        self.assertEqual(self.ledger.counts(self.project), {"events": 0, "outbox": 0})
        self.assertEqual(self.ledger.get_state(self.project), (0, {}))

    def test_s5_06_failure_after_event_insert_rolls_back_everything(self):
        with self.assertRaises(InjectedFailure):
            self.apply(fault="after_event_insert")
        self.assertEqual(self.ledger.counts(self.project), {"events": 0, "outbox": 0})
        self.assertEqual(self.ledger.get_state(self.project), (0, {}))

    def test_s5_07_failure_after_state_update_rolls_back_everything(self):
        with self.assertRaises(InjectedFailure):
            self.apply(fault="after_state_update")
        self.assertEqual(self.ledger.counts(self.project), {"events": 0, "outbox": 0})
        self.assertEqual(self.ledger.get_state(self.project), (0, {}))

    def test_s5_08_crash_after_commit_preserves_state_and_pending_outbox(self):
        with self.assertRaises(SimulatedCrashAfterCommit):
            self.apply(fault="after_commit")
        reopened = AuthoritativeStateLedger(self.db)
        self.assertEqual(reopened.get_state(self.project), (1, {"status": "ready"}))
        self.assertEqual(reopened.counts(self.project), {"events": 1, "outbox": 1})
        self.assertEqual(len(reopened.pending_outbox(self.project)), 1)

    def test_s5_09_pending_outbox_recovery_after_reopen_is_deterministic(self):
        result = self.apply()
        first = self.ledger.pending_outbox(self.project)
        reopened = AuthoritativeStateLedger(self.db)
        second = reopened.pending_outbox(self.project)
        self.assertEqual(first, second)
        self.assertEqual([row["outbox_id"] for row in second], [result.outbox_id])
        self.assertEqual(reopened.get_state(self.project), (1, {"status": "ready"}))

    def test_s5_10_outbox_completion_is_idempotent(self):
        result = self.apply()
        self.assertTrue(self.ledger.complete_outbox(result.outbox_id, "sha256:completion-1"))
        self.assertFalse(self.ledger.complete_outbox(result.outbox_id, "sha256:completion-1"))
        self.assertEqual(self.ledger.pending_outbox(self.project), [])
        rows = self.raw_outbox()
        self.assertEqual(rows[0]["status"], "COMPLETED")
        self.assertEqual(rows[0]["completion_attempts"], 1)

    def test_s5_11_duplicate_completion_does_not_advance_authoritative_state(self):
        result = self.apply()
        before = self.ledger.get_state(self.project)
        self.ledger.complete_outbox(result.outbox_id, "sha256:completion-1")
        self.assertFalse(self.ledger.complete_outbox(result.outbox_id, "sha256:completion-1"))
        self.assertEqual(self.ledger.get_state(self.project), before)
        self.assertEqual(self.ledger.counts(self.project), {"events": 1, "outbox": 1})

    def test_s5_12_concurrent_identical_submissions_converge(self):
        barrier = threading.Barrier(2)
        results = []
        errors = []
        lock = threading.Lock()

        def worker():
            ledger = AuthoritativeStateLedger(self.db)
            try:
                barrier.wait(timeout=5)
                result = ledger.apply_command(
                    project_id=self.project,
                    idempotency_key="same-intent",
                    command_type="PATCH_STATE",
                    payload={"set": {"status": "ready"}},
                    expected_version=0,
                    effect_type="NOTIFY",
                    effect_payload={"status": "ready"},
                )
                with lock:
                    results.append(result)
            except Exception as exc:  # captured for deterministic assertion
                with lock:
                    errors.append(exc)

        threads = [threading.Thread(target=worker) for _ in range(2)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=15)
        self.assertFalse(any(t.is_alive() for t in threads), "concurrency test deadlocked")
        self.assertEqual(errors, [])
        self.assertEqual(len(results), 2)
        self.assertEqual({r.event_id for r in results}, {results[0].event_id})
        self.assertEqual(sum(not r.replayed for r in results), 1)
        self.assertEqual(sum(r.replayed for r in results), 1)
        self.assertEqual(self.ledger.counts(self.project), {"events": 1, "outbox": 1})
        self.assertEqual(self.ledger.get_state(self.project)[0], 1)

    def test_s5_13_concurrent_distinct_same_version_allows_at_most_one(self):
        barrier = threading.Barrier(2)
        results = []
        errors = []
        lock = threading.Lock()

        def worker(key: str, value: str):
            ledger = AuthoritativeStateLedger(self.db)
            try:
                barrier.wait(timeout=5)
                result = ledger.apply_command(
                    project_id=self.project,
                    idempotency_key=key,
                    command_type="PATCH_STATE",
                    payload={"set": {"status": value}},
                    expected_version=0,
                    effect_type="NOTIFY",
                    effect_payload={"status": value},
                )
                with lock:
                    results.append(result)
            except Exception as exc:
                with lock:
                    errors.append(exc)

        threads = [
            threading.Thread(target=worker, args=("intent-a", "A")),
            threading.Thread(target=worker, args=("intent-b", "B")),
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=15)
        self.assertFalse(any(t.is_alive() for t in threads), "concurrency test deadlocked")
        self.assertEqual(len(results), 1)
        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], VersionConflict)
        self.assertEqual(self.ledger.counts(self.project), {"events": 1, "outbox": 1})
        self.assertEqual(self.ledger.get_state(self.project)[0], 1)

    def test_s5_14_worker_model_authority_claims_are_rejected(self):
        with self.assertRaises(AuthorityClaimRejected):
            self.ledger.apply_command(
                project_id=self.project,
                idempotency_key="claim-intent",
                command_type="PATCH_STATE",
                payload={"set": {"status": "ready"}},
                expected_version=0,
                authority_claims={"set_version": 99, "accepted": True},
            )
        result = self.apply()
        with self.assertRaises(AuthorityClaimRejected):
            self.ledger.complete_outbox(
                result.outbox_id,
                "sha256:completion-1",
                authority_claims={"completed": True, "set_version": 99},
            )
        self.assertEqual(self.ledger.get_state(self.project), (1, {"status": "ready"}))
        self.assertEqual(len(self.ledger.pending_outbox(self.project)), 1)

    def test_s5_15_digests_are_stable_across_reopen_and_replay(self):
        first = self.apply()
        outbox_before = self.raw_outbox()[0]
        reopened = AuthoritativeStateLedger(self.db)
        second = reopened.apply_command(
            project_id=self.project,
            idempotency_key="intent-1",
            command_type="PATCH_STATE",
            payload={"set": {"status": "ready"}},
            expected_version=0,
            effect_type="NOTIFY",
            effect_payload={"status": "ready"},
        )
        outbox_after = self.raw_outbox()[0]
        self.assertTrue(second.replayed)
        self.assertEqual(first.event_id, second.event_id)
        self.assertEqual(first.result_digest, second.result_digest)
        self.assertEqual(first.outbox_id, second.outbox_id)
        self.assertEqual(outbox_before["effect_digest"], outbox_after["effect_digest"])

    def test_s5_16_audit_detects_tampered_or_missing_lineage(self):
        self.apply()
        self.apply(key="intent-2", expected=1, value="done")
        clean = self.ledger.audit(self.project)
        self.assertTrue(clean["valid"], clean)
        self.assertEqual(clean["event_count"], 2)
        self.assertEqual(clean["final_version"], 2)

        con = sqlite3.connect(self.db)
        try:
            con.execute(
                "DELETE FROM accepted_events WHERE project_id=? AND result_version=1",
                (self.project,),
            )
            con.commit()
        finally:
            con.close()
        tampered = self.ledger.audit(self.project)
        self.assertFalse(tampered["valid"], tampered)
        self.assertTrue(any("version_lineage" in p or "state_version_mismatch" in p or "orphan_outbox" in p for p in tampered["problems"]), tampered)


if __name__ == "__main__":
    unittest.main(verbosity=2)
