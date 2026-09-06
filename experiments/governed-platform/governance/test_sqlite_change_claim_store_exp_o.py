import tempfile
import threading
import unittest
from pathlib import Path

from sqlite_change_claim_store_exp_o import SQLiteChangeClaimStore


class ExpOPersistentClaimConcurrencyTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tempdir.name) / "claims.sqlite3"
        self.store = SQLiteChangeClaimStore(self.db_path)

    def tearDown(self):
        self.tempdir.cleanup()

    def _run_concurrent(self, specs):
        barrier = threading.Barrier(len(specs) + 1)
        results = []
        errors = []
        lock = threading.Lock()

        def worker(spec):
            try:
                barrier.wait(timeout=5)
                result = self.store.request_claim(**spec)
                with lock:
                    results.append(result)
            except Exception as exc:  # pragma: no cover - surfaced by assertion
                with lock:
                    errors.append(exc)

        threads = [threading.Thread(target=worker, args=(spec,)) for spec in specs]
        for thread in threads:
            thread.start()
        barrier.wait(timeout=5)
        for thread in threads:
            thread.join(timeout=10)
        self.assertFalse(any(thread.is_alive() for thread in threads), "concurrent claim thread hung")
        self.assertEqual(errors, [])
        return results

    def test_concurrent_overlapping_exclusive_has_exactly_one_grant(self):
        results = self._run_concurrent(
            [
                {
                    "task_id": "task-a",
                    "base_sha": "h1",
                    "resources": ["repo:path:src/auth/**"],
                    "mode": "EXCLUSIVE",
                },
                {
                    "task_id": "task-b",
                    "base_sha": "h1",
                    "resources": ["repo:path:src/auth/session.go"],
                    "mode": "EXCLUSIVE",
                },
            ]
        )
        dispositions = sorted(item["disposition"] for item in results)
        self.assertEqual(dispositions, ["EXCLUSIVE_GRANTED", "WAITING_CONFLICT"])
        active = self.store.active_claims()
        self.assertEqual(len(active), 1)
        self.assertEqual(active[0]["disposition"], "EXCLUSIVE_GRANTED")

    def test_concurrent_non_overlapping_exclusive_both_grant_with_distinct_epochs(self):
        results = self._run_concurrent(
            [
                {
                    "task_id": "task-a",
                    "base_sha": "h1",
                    "resources": ["repo:path:src/auth/**"],
                    "mode": "EXCLUSIVE",
                },
                {
                    "task_id": "task-b",
                    "base_sha": "h1",
                    "resources": ["repo:path:src/payments/**"],
                    "mode": "EXCLUSIVE",
                },
            ]
        )
        self.assertEqual(
            [item["disposition"] for item in results].count("EXCLUSIVE_GRANTED"), 2
        )
        epochs = sorted(item["claim_epoch"] for item in results)
        self.assertEqual(epochs, [1, 2])
        self.assertEqual(len(set(epochs)), 2)
        self.assertEqual(len(self.store.active_claims()), 2)

    def test_concurrent_overlapping_parallel_proposals_both_grant_non_authoritative_mode(self):
        results = self._run_concurrent(
            [
                {
                    "task_id": "task-a",
                    "base_sha": "h1",
                    "resources": ["repo:path:src/auth/**"],
                    "mode": "PARALLEL_PROPOSAL",
                },
                {
                    "task_id": "task-b",
                    "base_sha": "h1",
                    "resources": ["repo:path:src/auth/session.go"],
                    "mode": "PARALLEL_PROPOSAL",
                },
            ]
        )
        self.assertEqual(
            [item["disposition"] for item in results].count("PARALLEL_PROPOSAL_GRANTED"),
            2,
        )
        self.assertEqual(len(self.store.active_claims()), 2)

    def test_exact_retry_is_idempotent_and_returns_original_claim_epoch(self):
        spec = {
            "task_id": "task-a",
            "base_sha": "h1",
            "resources": ["repo:path:src/auth/**"],
            "mode": "EXCLUSIVE",
        }
        first = self.store.request_claim(**spec)
        second = self.store.request_claim(**spec)
        self.assertEqual(first["disposition"], "EXCLUSIVE_GRANTED")
        self.assertEqual(second["disposition"], "EXCLUSIVE_GRANTED")
        self.assertTrue(second["retry"])
        self.assertEqual(first["claim_id"], second["claim_id"])
        self.assertEqual(first["claim_epoch"], second["claim_epoch"])
        self.assertEqual(len(self.store.active_claims()), 1)
        self.assertEqual(self.store.next_epoch(), 2)

    def test_same_task_identity_with_different_intent_fails_closed(self):
        first = self.store.request_claim(
            task_id="task-a",
            base_sha="h1",
            resources=["repo:path:src/auth/**"],
            mode="EXCLUSIVE",
        )
        mismatch = self.store.request_claim(
            task_id="task-a",
            base_sha="h1",
            resources=["repo:path:src/payments/**"],
            mode="EXCLUSIVE",
        )
        self.assertEqual(first["disposition"], "EXCLUSIVE_GRANTED")
        self.assertEqual(mismatch["disposition"], "CLAIM_INTENT_MISMATCH")
        active = self.store.active_claims()
        self.assertEqual(len(active), 1)
        self.assertEqual(active[0]["resources"], ["repo:path:src/auth/**"])

    def test_injected_failure_before_commit_rolls_back_row_and_epoch(self):
        self.assertEqual(self.store.next_epoch(), 1)
        with self.assertRaisesRegex(RuntimeError, "INJECTED_FAILURE_BEFORE_COMMIT"):
            self.store.request_claim(
                task_id="task-a",
                base_sha="h1",
                resources=["repo:path:src/auth/**"],
                mode="EXCLUSIVE",
                inject_failure_before_commit=True,
            )
        self.assertEqual(self.store.active_claims(), [])
        self.assertEqual(self.store.next_epoch(), 1)

        next_claim = self.store.request_claim(
            task_id="task-b",
            base_sha="h1",
            resources=["repo:path:src/auth/**"],
            mode="EXCLUSIVE",
        )
        self.assertEqual(next_claim["claim_epoch"], 1)

    def test_reopen_preserves_active_claim_and_blocks_overlap(self):
        first = self.store.request_claim(
            task_id="task-a",
            base_sha="h1",
            resources=["repo:path:src/auth/**"],
            mode="EXCLUSIVE",
        )
        self.assertEqual(first["disposition"], "EXCLUSIVE_GRANTED")

        reopened = SQLiteChangeClaimStore(self.db_path)
        persisted = reopened.get_claim("task-a")
        self.assertIsNotNone(persisted)
        self.assertEqual(persisted["claim_epoch"], first["claim_epoch"])

        conflict = reopened.request_claim(
            task_id="task-b",
            base_sha="h1",
            resources=["repo:path:src/auth/session.go"],
            mode="EXCLUSIVE",
        )
        self.assertEqual(conflict["disposition"], "WAITING_CONFLICT")
        self.assertEqual(len(reopened.active_claims()), 1)


if __name__ == "__main__":
    unittest.main()
