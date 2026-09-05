from __future__ import annotations

import sqlite3
import tempfile
import threading
import unittest
from pathlib import Path

from review_engine.session_store import SQLiteSessionStore


class SessionStoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "sessions.db"
        self.store = SQLiteSessionStore(self.path)

    def tearDown(self):
        self.tmp.cleanup()

    def test_session_events_are_hash_linked_and_persistent(self):
        e1 = self.store.append("s1", "REQUEST_RECEIVED", {"request_id": "r1"})
        e2 = self.store.append("s1", "R1_COMPLETED", {"artifact_hash": "abc"})
        self.assertEqual(e1.seq, 1)
        self.assertEqual(e2.seq, 2)
        self.assertEqual(e2.previous_hash, e1.event_hash)
        reopened = SQLiteSessionStore(self.path)
        self.assertTrue(reopened.validate_chain("s1"))
        self.assertEqual(len(reopened.events("s1")), 2)

    def test_latest_final_decision_is_queryable_for_dashboard(self):
        self.store.append("s1", "REQUEST_RECEIVED", {"request_id": "r1"})
        self.store.append("s1", "FINAL_DECISION", {"state": "CONVERGED_PASS", "reasons": ["R2 clean"], "artifact_hash": "h"})
        decision = self.store.latest_decision("s1")
        self.assertEqual(decision.payload["state"], "CONVERGED_PASS")
        self.assertEqual(self.store.latest_terminal("s1"), decision)
        summary = self.store.list_sessions()[0]
        self.assertEqual(summary.session_id, "s1")
        self.assertEqual(summary.final_state, "CONVERGED_PASS")
        self.assertEqual(summary.final_reasons, ("R2 clean",))
        self.assertEqual(summary.artifact_hash, "h")
        self.assertTrue(summary.chain_valid)

    def test_in_progress_session_has_no_final_state(self):
        self.store.append("open", "REQUEST_RECEIVED", {"request_id": "open"})
        summary = self.store.list_sessions()[0]
        self.assertIsNone(summary.final_state)

    def test_privileged_rewrite_is_detected_but_not_prevented_by_hash_chain(self):
        self.store.append("s1", "REQUEST_RECEIVED", {"request_id": "r1"})
        self.store.append("s1", "FINAL_DECISION", {"state": "CONVERGED_PASS"})
        with sqlite3.connect(self.path) as conn:
            conn.execute("UPDATE review_events SET payload_json='{}' WHERE session_id='s1' AND seq=1")
        self.assertFalse(self.store.validate_chain("s1"))
        self.assertFalse(self.store.list_sessions()[0].chain_valid)

    def test_duplicate_request_received_is_atomically_rejected(self):
        self.store.append("same", "REQUEST_RECEIVED", {"request_id": "same", "input": "first"})
        with self.assertRaisesRegex(ValueError, "already exists"):
            self.store.append("same", "REQUEST_RECEIVED", {"request_id": "same", "input": "different"})
        events = self.store.events("same")
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].payload["input"], "first")
        self.assertTrue(self.store.validate_chain("same"))

    def test_final_decision_seals_session_against_late_events(self):
        self.store.append("sealed", "REQUEST_RECEIVED", {"request_id": "sealed"})
        self.store.append("sealed", "FINAL_DECISION", {"state": "CONVERGED_PASS"})
        with self.assertRaisesRegex(ValueError, "already terminal"):
            self.store.append("sealed", "R1_COMPLETED", {"artifact_hash": "late"})
        self.assertTrue(self.store.validate_chain("sealed"))
        self.assertEqual(len(self.store.events("sealed")), 2)

    def test_owned_execution_abort_seals_open_session_and_is_visible_in_summary(self):
        with self.store.execution_attempt("attempt-owner"):
            request = self.store.append("aborted", "REQUEST_RECEIVED", {"request_id": "aborted"})
        self.assertEqual(request.payload["execution_attempt_id"], "attempt-owner")

        aborted = self.store.abort_if_owned("aborted", "attempt-owner")
        self.assertIsNotNone(aborted)
        self.assertEqual(aborted.event_type, "EXECUTION_ABORTED")
        self.assertEqual(aborted.payload["state"], "EXECUTION_ABORTED")
        self.assertEqual(
            aborted.payload["reasons"],
            ["review execution failed before a governed final decision"],
        )
        self.assertTrue(self.store.validate_chain("aborted"))
        self.assertEqual(self.store.latest_terminal("aborted"), aborted)
        self.assertIsNone(self.store.latest_decision("aborted"))

        summary = self.store.list_sessions()[0]
        self.assertEqual(summary.session_id, "aborted")
        self.assertEqual(summary.final_state, "EXECUTION_ABORTED")
        self.assertEqual(
            summary.final_reasons,
            ("review execution failed before a governed final decision",),
        )
        with self.assertRaisesRegex(ValueError, "already terminal"):
            self.store.append("aborted", "R1_COMPLETED", {"artifact_hash": "late"})

    def test_wrong_execution_attempt_cannot_abort_another_open_session(self):
        with self.store.execution_attempt("winning-attempt"):
            self.store.append("owned", "REQUEST_RECEIVED", {"request_id": "owned"})

        self.assertIsNone(self.store.abort_if_owned("owned", "losing-attempt"))
        events = self.store.events("owned")
        self.assertEqual([event.event_type for event in events], ["REQUEST_RECEIVED"])
        self.assertTrue(self.store.validate_chain("owned"))

        aborted = self.store.abort_if_owned("owned", "winning-attempt")
        self.assertIsNotNone(aborted)
        self.assertEqual([event.event_type for event in self.store.events("owned")], ["REQUEST_RECEIVED", "EXECUTION_ABORTED"])

    def test_abort_is_idempotent_after_terminal_event(self):
        with self.store.execution_attempt("owner"):
            self.store.append("once", "REQUEST_RECEIVED", {"request_id": "once"})
        first = self.store.abort_if_owned("once", "owner")
        second = self.store.abort_if_owned("once", "owner")
        self.assertIsNotNone(first)
        self.assertIsNone(second)
        self.assertEqual(len(self.store.events("once")), 2)
        self.assertTrue(self.store.validate_chain("once"))

    def test_concurrent_event_writers_serialize_without_corrupting_chain(self):
        self.store.append("parallel", "REQUEST_RECEIVED", {"request_id": "parallel"})
        errors: list[Exception] = []

        def writer(index: int) -> None:
            try:
                self.store.append("parallel", f"TEST_EVENT_{index}", {"index": index})
            except Exception as exc:  # pragma: no cover - asserted below
                errors.append(exc)

        threads = [threading.Thread(target=writer, args=(i,)) for i in range(8)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=10)

        self.assertFalse(errors, errors)
        self.assertTrue(self.store.validate_chain("parallel"))
        events = self.store.events("parallel")
        self.assertEqual(len(events), 9)
        self.assertEqual([event.seq for event in events], list(range(1, 10)))


if __name__ == "__main__":
    unittest.main()
