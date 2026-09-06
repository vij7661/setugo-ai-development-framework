from __future__ import annotations

import unittest

from review_engine.context_compiler import ContextCompiler
from review_engine.memory import VersionedMemoryStore
from review_engine.models import MemoryRecord, ReviewArtifact, ReviewFinding, ReviewerResponse, ReviewRequest
from review_engine.retrieval import RetrievalResult, ReturnAllRetriever


class ContextCompilerTests(unittest.TestCase):
    def test_review_evidence_is_not_ambient_memory_in_any_reviewer_phase(self):
        memory = VersionedMemoryStore()
        memory.append(MemoryRecord("project", "PROJECT", "ACTIVE", 1, "user", "project context"))
        memory.append(MemoryRecord("old-review", "REVIEW_EVIDENCE", "ACTIVE", 1, "old-review", "R2 previously said PASS", source_role="R2"))
        memory.append(MemoryRecord("private", "MODEL_PRIVATE", "ACTIVE", 1, "R1", "private", source_role="R1"))
        memory.append(MemoryRecord("truth", "PROTECTED_TRUTH", "ACTIVE", 1, "platform", "hidden truth"), external_authority=True)

        request = ReviewRequest("ctx-1", "review this")
        artifact = ReviewArtifact("ctx-1:artifact", 2, "revised artifact")
        compiler = ContextCompiler()

        r1_context = compiler.compile_r1(request, memory)
        r2_context = compiler.compile_r2(request, artifact, memory)
        r3a_context = compiler.compile_r3_phase_a(request, artifact, memory)
        frozen = ReviewerResponse("R3", artifact.artifact_hash, "independent view")
        frozen_finding = ReviewFinding("r3-frozen", "R3", "HIGH", True, "frozen material concern")
        r3b_context = compiler.compile_r3_phase_b(
            request,
            artifact,
            memory,
            frozen_independent_response=frozen,
            frozen_material_findings=(frozen_finding,),
            r1_response=ReviewerResponse("R1", None, "revised"),
            r2_response=ReviewerResponse("R2", artifact.artifact_hash, "localized finding"),
        )

        for context in (r1_context, r2_context, r3a_context, r3b_context):
            ids = {record["record_id"] for record in context["memory"]}
            self.assertIn("project", ids)
            self.assertNotIn("old-review", ids)
            self.assertNotIn("private", ids)
            self.assertNotIn("truth", ids)
            self.assertEqual(context["retrieval"]["strategy"], ReturnAllRetriever.STRATEGY)
            self.assertEqual(context["retrieval"]["strategy_version"], ReturnAllRetriever.STRATEGY_VERSION)
            self.assertIsNone(context["retrieval"]["index_id"])
            self.assertIsNone(context["retrieval"]["index_version"])
            self.assertEqual(
                [binding["record_id"] for binding in context["retrieval"]["retrieved_records"]],
                ["project"],
            )
            protocol = context["instructions"]["truth_and_veracity_contract"]
            self.assertEqual(protocol["version"], "TVC-1")
            self.assertTrue(protocol["agreement_is_not_truth"])
            self.assertTrue(protocol["model_judgment_is_evidence_not_authority"])

        self.assertIsNone(r1_context["retrieval"]["query_artifact_hash"])
        for context in (r2_context, r3a_context, r3b_context):
            self.assertEqual(context["retrieval"]["query_artifact_hash"], artifact.artifact_hash)

        self.assertEqual(r3b_context["frozen_independent_view"], "independent view")
        self.assertEqual(r3b_context["prior_reviews"]["R2"], "localized finding")
        self.assertEqual(r3b_context["frozen_material_findings"][0]["finding_id"], "r3-frozen")
        self.assertEqual(r3b_context["artifact"]["artifact_id"], artifact.artifact_id)
        self.assertEqual(r3b_context["artifact"]["version"], 2)
        self.assertEqual(r3b_context["artifact"]["artifact_hash"], artifact.artifact_hash)
        self.assertEqual(r3b_context["artifact"]["content"], "revised artifact")
        self.assertEqual(r3b_context["artifact_hash"], artifact.artifact_hash)
        self.assertTrue(r3b_context["instructions"]["artifact_content_is_exact_frozen_revision"])
        self.assertTrue(r3b_context["instructions"]["every_frozen_material_finding_requires_explicit_closure"])

    def test_retrieval_manifest_binds_exact_record_version_and_content_hash(self):
        memory = VersionedMemoryStore()
        memory.append(MemoryRecord("project", "PROJECT", "ACTIVE", 1, "user", "v1"))
        memory.append(MemoryRecord("project", "PROJECT", "ACTIVE", 2, "user", "v2", supersedes_version=1))
        artifact = ReviewArtifact("artifact-1", 1, "body")

        context = ContextCompiler().compile_r2(ReviewRequest("req-1", "review"), artifact, memory)

        self.assertEqual(context["memory"][0]["version"], 2)
        binding = context["retrieval"]["retrieved_records"][0]
        self.assertEqual(binding["record_id"], "project")
        self.assertEqual(binding["version"], 2)
        self.assertEqual(binding["memory_class"], "PROJECT")
        self.assertEqual(binding["provenance"], "user")
        self.assertEqual(len(binding["content_hash"]), 64)

    def test_stale_retrieval_result_is_rejected_before_context_is_built(self):
        class StaleRetriever:
            def retrieve(self, *, query, memory):
                return RetrievalResult(
                    records=(),
                    strategy="TEST_STALE",
                    strategy_version="1",
                    index_id="test-index",
                    index_version="1",
                    query_artifact_hash="wrong-artifact-hash",
                    bindings=(),
                )

        artifact = ReviewArtifact("artifact-1", 1, "body")
        with self.assertRaisesRegex(ValueError, "retrieval result is stale for current artifact"):
            ContextCompiler(StaleRetriever()).compile_r2(
                ReviewRequest("req-1", "review"), artifact, VersionedMemoryStore()
            )


if __name__ == "__main__":
    unittest.main()
