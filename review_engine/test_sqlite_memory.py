from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from review_engine.models import MemoryRecord
from review_engine.sqlite_memory import SQLiteMemoryStore


class SQLiteMemoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "memory.db"
        self.store = SQLiteMemoryStore(self.path)

    def tearDown(self):
        self.tmp.cleanup()

    def test_persists_across_store_instances(self):
        record = MemoryRecord("project:name", "PROJECT", "ACTIVE", 1, "user", "Review Engine")
        self.store.append(record)
        reopened = SQLiteMemoryStore(self.path)
        self.assertEqual(reopened.current(), (record,))

    def test_authoritative_memory_requires_external_authority(self):
        record = MemoryRecord("req:1", "AUTHORITATIVE", "ACTIVE", 1, "user-approved", "must verify")
        with self.assertRaises(PermissionError):
            self.store.append(record)
        self.store.append(record, external_authority=True)
        self.assertEqual(self.store.current(), (record,))

    def test_latest_status_controls_current_view(self):
        v1 = MemoryRecord("decision:1", "PROJECT", "ACTIVE", 1, "user", "old")
        v2 = MemoryRecord("decision:1", "PROJECT", "SUPERSEDED", 2, "user", "old superseded", supersedes_version=1)
        self.store.append(v1)
        self.store.append(v2)
        self.assertEqual(self.store.current(), ())
        self.assertEqual(len(self.store.history("decision:1")), 2)

    def test_private_and_protected_memory_never_reaches_reviewer_view(self):
        self.store.append(MemoryRecord("work:1", "WORKING", "ACTIVE", 1, "system", "visible"))
        self.store.append(MemoryRecord("private:1", "MODEL_PRIVATE", "ACTIVE", 1, "R1", "hidden", source_role="R1"))
        self.store.append(MemoryRecord("truth:1", "PROTECTED_TRUTH", "ACTIVE", 1, "scorer", "hidden"))
        visible = self.store.reviewer_visible()
        self.assertEqual([r.record_id for r in visible], ["work:1"])

    def test_stale_supersedes_binding_is_rejected_atomically(self):
        self.store.append(MemoryRecord("req:1", "PROJECT", "ACTIVE", 1, "user", "v1"))
        with self.assertRaises(ValueError):
            self.store.append(MemoryRecord("req:1", "PROJECT", "ACTIVE", 2, "user", "v2", supersedes_version=0))
        self.assertEqual(len(self.store.history("req:1")), 1)


if __name__ == "__main__":
    unittest.main()
