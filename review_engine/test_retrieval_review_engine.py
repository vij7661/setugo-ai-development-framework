from __future__ import annotations

import unittest
from hashlib import sha256

from review_engine.context_compiler import ContextCompiler
from review_engine.memory import VersionedMemoryStore
from review_engine.models import MemoryRecord, ReviewerConfig, ReviewerResponse, ReviewRequest
from review_engine.retrieval import RetrievalQuery, RetrievalResult, RetrievedRecordBinding
from review_engine.retrieval_review_engine import RetrievalAwareReviewEngine


class RecordingSessionStore:
    def __init__(self) -> None:
        self.events: list[tuple[str, str, dict]] = []

    def append(self, session_id: str, event_type: str, payload: dict):
        self.events.append((session_id, event_type, payload))
        return None


def _binding(record: MemoryRecord) -> RetrievedRecordBinding:
    return RetrievedRecordBinding(
        record_id=record.record_id,
        version=record.version,
        memory_class=record.memory_class,
        provenance=record.provenance,
        content_hash=sha256(record.content.encode("utf-8")).hexdigest(),
    )


class SelectiveRetriever:
    def __init__(self, selected_ids: set[str]) -> None:
        self.selected_ids = selected_ids

    def retrieve(self, *, query: RetrievalQuery, memory: VersionedMemoryStore) -> RetrievalResult:
        records = tuple(
            record
            for record in memory.reviewer_visible()
            if record.memory_class != "REVIEW_EVIDENCE" and record.record_id in self.selected_ids
        )
        return RetrievalResult(
            records=records,
            strategy="TEST_SELECTIVE",
            strategy_version="1",
            index_id="test-index",
            index_version="index-v1",
            query_artifact_hash=query.artifact_hash,
            bindings=tuple(_binding(record) for record in records),
        )


class RetrievalAwareReviewEngineTests(unittest.TestCase):
    def _r1(self) -> ReviewerConfig:
        return ReviewerConfig(
            role="R1",
            provider="test",
            model="test-model",
            sku="test-sku",
            deployment_path="local",
            api_key_env="TEST_KEY",
            foundation_lineage="lineage-r1",
        )

    def _memory(self) -> VersionedMemoryStore:
        memory = VersionedMemoryStore()
        memory.append(MemoryRecord("project", "PROJECT", "ACTIVE", 1, "user", "long-tail project context"))
        memory.append(
            MemoryRecord("policy", "AUTHORITATIVE", "ACTIVE", 1, "platform", "must always be seen"),
            external_authority=True,
        )
        return memory

    def test_selective_retrieval_may_omit_nonmandatory_project_memory(self):
        sessions = RecordingSessionStore()
        compiler = ContextCompiler(SelectiveRetriever({"policy"}))
        seen_contexts: list[dict] = []

        def invoker(config, context):
            seen_contexts.append(context)
            return ReviewerResponse("R1", None, "answer")

        decision = RetrievalAwareReviewEngine(
            invoker,
            context_compiler=compiler,
            session_store=sessions,
        ).run(
            ReviewRequest("rag-1", "review"),
            r1=self._r1(),
            r2=None,
            r3=None,
            memory=self._memory(),
        )

        self.assertEqual(decision.state, "CONVERGED_PASS")
        self.assertEqual([record["record_id"] for record in seen_contexts[0]["memory"]], ["policy"])
        completed = next(payload for _, event, payload in sessions.events if event == "R1_COMPLETED")
        self.assertEqual(completed["retrieval_evidence"]["strategy"], "TEST_SELECTIVE")
        self.assertEqual(completed["retrieval_evidence"]["index_version"], "index-v1")
        self.assertEqual(
            [item["record_id"] for item in completed["retrieval_evidence"]["retrieved_records"]],
            ["policy"],
        )

    def test_selective_retrieval_cannot_drop_authoritative_memory(self):
        calls = 0

        def invoker(config, context):
            nonlocal calls
            calls += 1
            return ReviewerResponse("R1", None, "answer")

        decision = RetrievalAwareReviewEngine(
            invoker,
            context_compiler=ContextCompiler(SelectiveRetriever({"project"})),
        ).run(
            ReviewRequest("rag-2", "review"),
            r1=self._r1(),
            r2=None,
            r3=None,
            memory=self._memory(),
        )

        self.assertEqual(decision.state, "HUMAN_REQUIRED")
        self.assertIn("omitted mandatory governance memory", decision.reasons[0])
        self.assertEqual(calls, 0)

    def test_selective_retrieval_manifest_is_bound_to_exact_selected_content(self):
        class BadBindingRetriever(SelectiveRetriever):
            def retrieve(self, *, query, memory):
                result = super().retrieve(query=query, memory=memory)
                bad = RetrievedRecordBinding(
                    record_id=result.bindings[0].record_id,
                    version=result.bindings[0].version,
                    memory_class=result.bindings[0].memory_class,
                    provenance=result.bindings[0].provenance,
                    content_hash="0" * 64,
                )
                return RetrievalResult(
                    records=result.records,
                    strategy=result.strategy,
                    strategy_version=result.strategy_version,
                    index_id=result.index_id,
                    index_version=result.index_version,
                    query_artifact_hash=result.query_artifact_hash,
                    bindings=(bad,),
                )

        calls = 0

        def invoker(config, context):
            nonlocal calls
            calls += 1
            return ReviewerResponse("R1", None, "answer")

        decision = RetrievalAwareReviewEngine(
            invoker,
            context_compiler=ContextCompiler(BadBindingRetriever({"policy"})),
        ).run(
            ReviewRequest("rag-3", "review"),
            r1=self._r1(),
            r2=None,
            r3=None,
            memory=self._memory(),
        )

        self.assertEqual(decision.state, "HUMAN_REQUIRED")
        self.assertIn("content hash", decision.reasons[0])
        self.assertEqual(calls, 0)


if __name__ == "__main__":
    unittest.main()
