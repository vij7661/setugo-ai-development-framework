from __future__ import annotations

import unittest

from review_engine.memory import VersionedMemoryStore
from review_engine.models import MemoryRecord
from review_engine.retrieval import RetrievalQuery, ReturnAllRetriever


class RetrievalTests(unittest.TestCase):
    def test_return_all_preserves_current_visibility_policy_and_audit_binding(self):
        memory = VersionedMemoryStore()
        memory.append(MemoryRecord("project", "PROJECT", "ACTIVE", 1, "user", "project context"))
        memory.append(MemoryRecord("review", "REVIEW_EVIDENCE", "ACTIVE", 1, "R2", "old review", source_role="R2"))
        memory.append(MemoryRecord("private", "MODEL_PRIVATE", "ACTIVE", 1, "R1", "private", source_role="R1"))
        memory.append(MemoryRecord("truth", "PROTECTED_TRUTH", "ACTIVE", 1, "platform", "truth"), external_authority=True)

        result = ReturnAllRetriever().retrieve(
            query=RetrievalQuery(
                role="R2",
                request_id="req-1",
                artifact_id="artifact-1",
                artifact_version=3,
                artifact_hash="abc123",
            ),
            memory=memory,
        )

        self.assertEqual([record.record_id for record in result.records], ["project"])
        self.assertEqual(result.strategy, "RETURN_ALL_REVIEWER_VISIBLE")
        self.assertEqual(result.strategy_version, "1")
        self.assertEqual(result.query_artifact_hash, "abc123")
        self.assertIsNone(result.index_id)
        self.assertIsNone(result.index_version)
        self.assertEqual(len(result.bindings), 1)
        self.assertEqual(result.bindings[0].record_id, "project")
        self.assertEqual(result.bindings[0].version, 1)
        self.assertEqual(len(result.bindings[0].content_hash), 64)

    def test_latest_active_version_is_the_only_returned_binding(self):
        memory = VersionedMemoryStore()
        memory.append(MemoryRecord("project", "PROJECT", "ACTIVE", 1, "user", "v1"))
        memory.append(MemoryRecord("project", "PROJECT", "ACTIVE", 2, "user", "v2", supersedes_version=1))

        result = ReturnAllRetriever().retrieve(
            query=RetrievalQuery(role="R1", request_id="req-1"),
            memory=memory,
        )

        self.assertEqual([(r.record_id, r.version, r.content) for r in result.records], [("project", 2, "v2")])
        self.assertEqual([(b.record_id, b.version) for b in result.bindings], [("project", 2)])


if __name__ == "__main__":
    unittest.main()
