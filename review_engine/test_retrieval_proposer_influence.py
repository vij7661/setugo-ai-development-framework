from __future__ import annotations

import unittest

from review_engine.context_compiler import ContextCompiler
from review_engine.memory import VersionedMemoryStore
from review_engine.models import MemoryRecord, ReviewArtifact, ReviewRequest
from review_engine.retrieval import GovernedLexicalRetriever, RetrievalResult


class RecordingRetriever:
    STRATEGY = "RECORDING"
    STRATEGY_VERSION = "1"

    def __init__(self) -> None:
        self.queries = []

    def retrieve(self, *, query, memory):
        self.queries.append(query)
        return RetrievalResult(
            records=(),
            strategy=self.STRATEGY,
            strategy_version=self.STRATEGY_VERSION,
            index_id=None,
            index_version=None,
            query_artifact_hash=query.artifact_hash,
            bindings=(),
        )


class ProposerInfluencedRetrievalTests(unittest.TestCase):
    def test_r2_retrieval_admission_query_does_not_include_proposer_artifact_content(self):
        retriever = RecordingRetriever()
        compiler = ContextCompiler(retriever)
        request = ReviewRequest(
            request_id="retrieval-query-r2",
            user_input="Review the payment implementation for safety.",
            risk="HIGH",
            materiality="MATERIAL",
        )
        artifact = ReviewArtifact(
            artifact_id="artifact-1",
            version=1,
            content="proposer-controlled-secret-token idempotency retry wording",
        )

        compiler.compile_r2(request, artifact, VersionedMemoryStore())

        self.assertEqual(len(retriever.queries), 1)
        self.assertEqual(retriever.queries[0].query_text, request.user_input)
        self.assertNotIn("proposer-controlled-secret-token", retriever.queries[0].query_text)

    def test_r3_independent_retrieval_query_does_not_include_proposer_artifact_content(self):
        retriever = RecordingRetriever()
        compiler = ContextCompiler(retriever)
        request = ReviewRequest(
            request_id="retrieval-query-r3",
            user_input="Independently review the payment implementation.",
            risk="HIGH",
            materiality="MATERIAL",
        )
        artifact = ReviewArtifact(
            artifact_id="artifact-2",
            version=1,
            content="proposer-controlled-r3-token duplicate transmission wording",
        )

        compiler.compile_r3_phase_a(request, artifact, VersionedMemoryStore())

        self.assertEqual(len(retriever.queries), 1)
        self.assertEqual(retriever.queries[0].query_text, request.user_input)
        self.assertNotIn("proposer-controlled-r3-token", retriever.queries[0].query_text)

    def test_rewording_artifact_cannot_change_nonmandatory_memory_admission(self):
        memory = VersionedMemoryStore()
        memory.append(
            MemoryRecord(
                record_id="prior-adverse-memory",
                memory_class="PROJECT",
                status="ACTIVE",
                version=1,
                provenance="governed-project-memory",
                content="payment retry idempotency defect duplicate charge",
                source_role="R2",
            )
        )
        retriever = GovernedLexicalRetriever(
            max_nonmandatory_records=8,
            minimum_overlap=2,
        )
        compiler = ContextCompiler(retriever)
        request = ReviewRequest(
            request_id="artifact-rewording-stability",
            user_input="Review this implementation adversarially.",
            risk="HIGH",
            materiality="MATERIAL",
        )
        artifact_with_overlap = ReviewArtifact(
            artifact_id="artifact-stable",
            version=1,
            content="The payment retry idempotency path prevents a duplicate charge.",
        )
        artifact_without_overlap = ReviewArtifact(
            artifact_id="artifact-stable",
            version=2,
            content="Repeated network submissions are collapsed into one financial operation.",
        )

        first = compiler.compile_r2(request, artifact_with_overlap, memory)
        second = compiler.compile_r2(request, artifact_without_overlap, memory)
        first_ids = [item["record_id"] for item in first["memory"]]
        second_ids = [item["record_id"] for item in second["memory"]]

        self.assertEqual(first_ids, second_ids)


if __name__ == "__main__":
    unittest.main()
