from __future__ import annotations

import unittest

from review_engine.context_compiler import ContextCompiler
from review_engine.memory import VersionedMemoryStore
from review_engine.models import MemoryRecord, ReviewArtifact, ReviewerResponse, ReviewRequest


class ContextCompilerTests(unittest.TestCase):
    def test_review_evidence_is_not_ambient_memory_in_any_reviewer_phase(self):
        memory = VersionedMemoryStore()
        memory.append(MemoryRecord("project", "PROJECT", "ACTIVE", 1, "user", "project context"))
        memory.append(MemoryRecord("old-review", "REVIEW_EVIDENCE", "ACTIVE", 1, "old-review", "R2 previously said PASS", source_role="R2"))
        memory.append(MemoryRecord("private", "MODEL_PRIVATE", "ACTIVE", 1, "R1", "private", source_role="R1"))

        request = ReviewRequest("ctx-1", "review this")
        artifact = ReviewArtifact("ctx-1:artifact", 2, "revised artifact")
        compiler = ContextCompiler()

        r1_context = compiler.compile_r1(request, memory)
        r2_context = compiler.compile_r2(request, artifact, memory)
        r3a_context = compiler.compile_r3_phase_a(request, artifact, memory)
        frozen = ReviewerResponse("R3", artifact.artifact_hash, "independent view")
        r3b_context = compiler.compile_r3_phase_b(
            request,
            artifact,
            memory,
            frozen_independent_response=frozen,
            r1_response=ReviewerResponse("R1", None, "revised"),
            r2_response=ReviewerResponse("R2", artifact.artifact_hash, "localized finding"),
        )

        for context in (r1_context, r2_context, r3a_context, r3b_context):
            ids = {record["record_id"] for record in context["memory"]}
            self.assertIn("project", ids)
            self.assertNotIn("old-review", ids)
            self.assertNotIn("private", ids)
            protocol = context["instructions"]["truth_and_veracity_contract"]
            self.assertEqual(protocol["version"], "TVC-1")
            self.assertTrue(protocol["agreement_is_not_truth"])
            self.assertTrue(protocol["model_judgment_is_evidence_not_authority"])

        self.assertEqual(r3b_context["frozen_independent_view"], "independent view")
        self.assertEqual(r3b_context["prior_reviews"]["R2"], "localized finding")


if __name__ == "__main__":
    unittest.main()
