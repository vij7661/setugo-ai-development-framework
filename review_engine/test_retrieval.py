from __future__ import annotations

import unittest

from review_engine.memory import VersionedMemoryStore
from review_engine.models import MemoryRecord
from review_engine.retrieval import GovernedLexicalRetriever, RetrievalQuery, ReturnAllRetriever


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

    def test_lexical_retrieval_keeps_authoritative_floor_and_selects_relevant_project_memory(self):
        memory = VersionedMemoryStore()
        memory.append(
            MemoryRecord("policy", "AUTHORITATIVE", "ACTIVE", 1, "platform", "mandatory release governance"),
            external_authority=True,
        )
        memory.append(MemoryRecord("relevant", "PROJECT", "ACTIVE", 1, "user", "provider endpoint qualification binding"))
        memory.append(MemoryRecord("irrelevant", "PROJECT", "ACTIVE", 1, "user", "goat market logistics"))
        memory.append(MemoryRecord("review", "REVIEW_EVIDENCE", "ACTIVE", 1, "R2", "provider endpoint", source_role="R2"))
        memory.append(MemoryRecord("private", "MODEL_PRIVATE", "ACTIVE", 1, "R1", "provider endpoint", source_role="R1"))

        result = GovernedLexicalRetriever(max_nonmandatory_records=2).retrieve(
            query=RetrievalQuery(
                role="R2",
                request_id="req-lexical",
                artifact_hash="artifact-hash",
                query_text="check provider endpoint substitution",
            ),
            memory=memory,
        )

        self.assertEqual([record.record_id for record in result.records], ["policy", "relevant"])
        self.assertEqual(result.strategy, "GOVERNED_LEXICAL_OVERLAP")
        self.assertEqual(result.query_artifact_hash, "artifact-hash")
        self.assertTrue(result.index_id.startswith("memory-index:"))
        self.assertEqual(len(result.index_version), 64)
        self.assertNotIn("review", [record.record_id for record in result.records])
        self.assertNotIn("private", [record.record_id for record in result.records])

    def test_authoritative_memory_cannot_be_dropped_even_with_zero_nonmandatory_budget(self):
        memory = VersionedMemoryStore()
        memory.append(
            MemoryRecord("authority", "AUTHORITATIVE", "ACTIVE", 1, "platform", "unrelated authoritative rule"),
            external_authority=True,
        )
        memory.append(MemoryRecord("project", "PROJECT", "ACTIVE", 1, "user", "exact provider endpoint topic"))

        result = GovernedLexicalRetriever(max_nonmandatory_records=0).retrieve(
            query=RetrievalQuery(role="R1", request_id="req", query_text="provider endpoint"),
            memory=memory,
        )
        self.assertEqual([record.record_id for record in result.records], ["authority"])

    def test_lexical_ties_are_deterministic_and_budgeted(self):
        memory = VersionedMemoryStore()
        memory.append(MemoryRecord("b", "PROJECT", "ACTIVE", 1, "user", "alpha beta"))
        memory.append(MemoryRecord("a", "PROJECT", "ACTIVE", 1, "user", "alpha gamma"))
        memory.append(MemoryRecord("c", "PROJECT", "ACTIVE", 1, "user", "alpha delta"))

        retriever = GovernedLexicalRetriever(max_nonmandatory_records=2)
        first = retriever.retrieve(
            query=RetrievalQuery(role="R1", request_id="one", query_text="alpha"),
            memory=memory,
        )
        second = retriever.retrieve(
            query=RetrievalQuery(role="R1", request_id="two", query_text="alpha"),
            memory=memory,
        )
        self.assertEqual([record.record_id for record in first.records], ["a", "b"])
        self.assertEqual([record.record_id for record in second.records], ["a", "b"])
        self.assertEqual(first.index_version, second.index_version)

    def test_index_version_changes_when_eligible_memory_changes(self):
        memory = VersionedMemoryStore()
        memory.append(MemoryRecord("a", "PROJECT", "ACTIVE", 1, "user", "alpha"))
        retriever = GovernedLexicalRetriever()
        before = retriever.retrieve(
            query=RetrievalQuery(role="R1", request_id="one", query_text="alpha"),
            memory=memory,
        )
        memory.append(MemoryRecord("b", "PROJECT", "ACTIVE", 1, "user", "beta"))
        after = retriever.retrieve(
            query=RetrievalQuery(role="R1", request_id="two", query_text="alpha"),
            memory=memory,
        )
        self.assertNotEqual(before.index_version, after.index_version)

    def test_empty_or_irrelevant_query_does_not_invent_nonmandatory_relevance(self):
        memory = VersionedMemoryStore()
        memory.append(MemoryRecord("project", "PROJECT", "ACTIVE", 1, "user", "completely unrelated"))
        result = GovernedLexicalRetriever().retrieve(
            query=RetrievalQuery(role="R1", request_id="req", query_text="provider endpoint"),
            memory=memory,
        )
        self.assertEqual(result.records, ())


if __name__ == "__main__":
    unittest.main()
