import unittest

from shared_memory_policy import MemoryRecord, apply_memory_write, build_reviewer_context


def rec(record_id, memory_class, **overrides):
    data = dict(
        record_id=record_id,
        memory_class=memory_class,
        version=1,
        provenance="external:test",
        content="x",
        relevant=True,
        source_role=None,
    )
    data.update(overrides)
    return MemoryRecord(**data)


class ExpJSharedMemoryPolicyTests(unittest.TestCase):
    def test_j001_r2_private_reasoning_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "MODEL_PRIVATE"):
            build_reviewer_context([rec("p", "MODEL_PRIVATE")], reviewer_stage="R2")

    def test_j002_r2_protected_truth_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "PROTECTED_TRUTH"):
            build_reviewer_context([rec("t", "PROTECTED_TRUTH")], reviewer_stage="R2")

    def test_j003_r2_can_receive_frozen_r1_review_evidence_when_protocol_allows(self):
        records = [rec("a", "AUTHORITATIVE"), rec("r1", "REVIEW_EVIDENCE", source_role="R1")]
        ctx = build_reviewer_context(records, reviewer_stage="R2", allow_prior_review_evidence=True)
        self.assertEqual(["a", "r1"], [x.record_id for x in ctx])

    def test_j004_r3_can_receive_frozen_prior_reviews_when_protocol_allows(self):
        records = [rec("r1", "REVIEW_EVIDENCE", source_role="R1"), rec("r2", "REVIEW_EVIDENCE", source_role="R2")]
        ctx = build_reviewer_context(records, reviewer_stage="R3", allow_prior_review_evidence=True)
        self.assertEqual(2, len(ctx))

    def test_j005_model_cannot_overwrite_authoritative_memory(self):
        current = {"req": rec("req", "AUTHORITATIVE")}
        proposal = rec("req", "AUTHORITATIVE", version=2, provenance="model:r1")
        with self.assertRaises(PermissionError):
            apply_memory_write(current, proposal, external_authority=False)

    def test_j006_stale_working_memory_version_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "stale memory version"):
            build_reviewer_context([rec("w", "WORKING", version=1)], reviewer_stage="R2", authoritative_version=2)

    def test_j007_irrelevant_memory_is_excluded(self):
        ctx = build_reviewer_context([rec("a", "PROJECT"), rec("b", "PROJECT", relevant=False)], reviewer_stage="R2")
        self.assertEqual(["a"], [x.record_id for x in ctx])

    def test_j008_clean_shared_project_context_is_available(self):
        records = [rec("a", "AUTHORITATIVE"), rec("p", "PROJECT"), rec("w", "WORKING")]
        for stage in ("R1", "R2", "R3"):
            self.assertEqual(3, len(build_reviewer_context(records, reviewer_stage=stage)))

    def test_j009_missing_provenance_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "provenance"):
            build_reviewer_context([rec("x", "PROJECT", provenance="")], reviewer_stage="R2")

    def test_prior_review_evidence_is_hidden_by_default(self):
        ctx = build_reviewer_context([rec("r", "REVIEW_EVIDENCE")], reviewer_stage="R2")
        self.assertEqual((), ctx)

    def test_duplicate_memory_identity_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            build_reviewer_context([rec("x", "PROJECT"), rec("x", "WORKING")], reviewer_stage="R2")

    def test_external_authority_can_advance_authoritative_memory(self):
        current = {"req": rec("req", "AUTHORITATIVE")}
        proposal = rec("req", "AUTHORITATIVE", version=2, provenance="policy:owner")
        updated = apply_memory_write(current, proposal, external_authority=True)
        self.assertEqual(2, updated["req"].version)


if __name__ == "__main__":
    unittest.main()
