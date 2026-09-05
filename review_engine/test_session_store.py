from __future__ import annotations

import sqlite3
import tempfile
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
        self.store.append("s1", "FINAL_DECISION", {"state": "CONVERGED_PASS", "reason": "R2 clean"})
        decision = self.store.latest_decision("s1")
        self.assertEqual(decision.payload["state"], "CONVERGED_PASS")

    def test_privileged_rewrite_is_detected_but_not_prevented_by_hash_chain(self):
        self.store.append("s1", "REQUEST_RECEIVED", {"request_id": "r1"})
        self.store.append("s1", "FINAL_DECISION", {"state": "CONVERGED_PASS"})
        with sqlite3.connect(self.path) as conn:
            conn.execute("UPDATE review_events SET payload_json='{}' WHERE session_id='s1' AND seq=1")
        self.assertFalse(self.store.validate_chain("s1"))


if __name__ == "__main__":
    unittest.main()
