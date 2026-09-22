"""Reviewer-authored R2E authority-anchoring attacks (v2).

Frozen before H-1/H-2/H-3 implementation.  This suite exercises only public
production APIs and the preregistered authority loader.
"""
from __future__ import annotations
import inspect
import unittest

from exp_m_deterministic import (
    EvidenceDeliveryManifest,
    MaterializationResult,
    PhysicalAttemptRecord,
    ProviderCapabilityProfile,
    ProviderCapabilityQualificationRecord,
    ProviderQualificationExecutionPlan,
    RetrievalEvidenceRecord,
    ReviewerReceipt,
    WireDeliveryRecord,
    digest,
    validate_capability,
    validate_retrieval,
    validate_wire_delivery,
)
from exp_m_expectation_authority import DEFAULT_AUTHORITY_COMMIT, load_default_authority, load_predicate_context

EXPECTED_AUTHORITY_ROOT_COMMIT = "251647e5f44d394b761f1c6cdbb02a779901bc43"


class ReviewerR2EAuthorityAnchoring(unittest.TestCase):
    def setUp(self):
        self.authority = load_default_authority()
        self.context = load_predicate_context(self.authority)

    def test_root_of_trust_commit_is_preregistered_literal(self):
        self.assertEqual(DEFAULT_AUTHORITY_COMMIT, EXPECTED_AUTHORITY_ROOT_COMMIT)
        self.assertEqual(self.authority.root_commit, EXPECTED_AUTHORITY_ROOT_COMMIT)

    def test_h1_retrieval_validator_has_no_caller_raw_parameter(self):
        self.assertNotIn("raw", inspect.signature(validate_retrieval).parameters)

    def test_h1_matching_fabricated_retrieval_bytes_do_not_pass(self):
        forged = b"forged"
        record = RetrievalEvidenceRecord(
            self.context.request_id, self.context.attempt_id, self.context.session_id,
            self.context.retrieval_source, self.context.retrieval_version,
            0, len(forged), digest(forged), len(forged), "tool", 1,
            self.context.final_context_id, self.context.final_context_hash,
        )
        ok, reasons = validate_retrieval(
            record,
            expected_request=self.context.request_id,
            expected_attempt=self.context.attempt_id,
            expected_session=self.context.session_id,
            expected_source=self.context.retrieval_source,
            expected_version=self.context.retrieval_version,
            expected_context_id=self.context.final_context_id,
            expected_context_hash=self.context.final_context_hash,
            authority=self.authority,
        )
        self.assertFalse(ok)
        self.assertIn("retrieval_bytes_mismatch", reasons)

    def test_h1_authority_source_bytes_pass(self):
        actual = self.authority.resolve_retrieval_bytes(
            self.context.retrieval_source, self.context.retrieval_version, 0, 1
        )
        record = RetrievalEvidenceRecord(
            self.context.request_id, self.context.attempt_id, self.context.session_id,
            self.context.retrieval_source, self.context.retrieval_version,
            0, 1, digest(actual), 1, "tool", 1,
            self.context.final_context_id, self.context.final_context_hash,
        )
        self.assertTrue(validate_retrieval(
            record,
            expected_request=self.context.request_id,
            expected_attempt=self.context.attempt_id,
            expected_session=self.context.session_id,
            expected_source=self.context.retrieval_source,
            expected_version=self.context.retrieval_version,
            expected_context_id=self.context.final_context_id,
            expected_context_hash=self.context.final_context_hash,
            authority=self.authority,
        )[0])

    def test_h2_self_consistent_unregistered_manifest_rejected(self):
        items = {"a": b"different"}
        commit = self.authority.resolve_reviewed_commit()
        manifest = EvidenceDeliveryManifest.freeze(self.context.request_id, commit, items)
        materialized = MaterializationResult(True, items, digest({"a": digest(b"different")}), commit, "raw-v1")
        wire = WireDeliveryRecord(self.context.attempt_id, self.context.request_id, "wrong", "", self.context.session_id, ("a",))
        receipt = ReviewerReceipt(self.context.attempt_id, self.context.request_id, self.context.session_id, manifest.manifest_hash, ("a",), len(b"different"), True)
        ok, reasons = validate_wire_delivery(
            manifest, materialized, wire, receipt, items,
            expected_commit=commit, authority=self.authority,
        )
        self.assertFalse(ok)
        self.assertIn("authority_manifest_hash_mismatch", reasons)

    def test_ca3_fabricated_commit_even_if_expected_string_matches_rejected(self):
        fake_commit = "f" * 40
        items = {"a": b"a"}
        manifest = EvidenceDeliveryManifest.freeze(self.context.request_id, fake_commit, items)
        materialized = MaterializationResult(True, items, digest({"a": digest(b"a")}), fake_commit, "raw-v1")
        wire = WireDeliveryRecord(self.context.attempt_id, self.context.request_id, "w", "", self.context.session_id, ("a",))
        receipt = ReviewerReceipt(self.context.attempt_id, self.context.request_id, self.context.session_id, manifest.manifest_hash, ("a",), 1, True)
        ok, reasons = validate_wire_delivery(
            manifest, materialized, wire, receipt, items,
            expected_commit=fake_commit, authority=self.authority,
        )
        self.assertFalse(ok)
        self.assertTrue("authority_reviewed_commit_mismatch" in reasons or "reviewed_commit_not_resolved_git_object" in reasons)

    def test_h3_caller_qualification_absent_from_authority_rejected(self):
        profile = ProviderCapabilityProfile("fake", "deterministic", "adapter", "profile-hash", True, supported_formats=("text",), max_context_bytes=1000000)
        plan = ProviderQualificationExecutionPlan("attacker-plan", "fake", "default", ("a1",), ("a1",))
        rec = ProviderCapabilityQualificationRecord("attacker-plan", "profile-hash", True, True, 0, "default", ("a1",), ("a1",), "fake", "deterministic",
            attempt_records=(PhysicalAttemptRecord("a1", "a1", None, "FIRST", self.context.request_id, self.context.session_id, "w", "OK"),))
        ok, reasons = validate_capability(
            profile, plan, rec, now="2026-01-01T00:00:00Z",
            expected_provider="fake", expected_model="deterministic",
            expected_operating_point="default", expected_profile_hash="profile-hash",
            required_format="text", required_context_bytes=1,
            authority=self.authority,
        )
        self.assertFalse(ok)
        self.assertIn("qualification_authority_plan_missing", reasons)

    def test_ca6_tampered_caller_plan_cannot_override_authority_plan(self):
        profile = ProviderCapabilityProfile("fake", "deterministic", "adapter", "profile-hash", True, supported_formats=("text",), max_context_bytes=1000000)
        plan = ProviderQualificationExecutionPlan("plan", "fake", "attacker-op", ("a1",), ("a1",))
        rec = ProviderCapabilityQualificationRecord("plan", "profile-hash", True, True, 0, "attacker-op", ("a1",), ("a1",), "fake", "deterministic",
            attempt_records=(PhysicalAttemptRecord("a1", "a1", None, "FIRST", self.context.request_id, self.context.session_id, "w", "OK"),))
        ok, reasons = validate_capability(
            profile, plan, rec, now="2026-01-01T00:00:00Z",
            expected_provider="fake", expected_model="deterministic",
            expected_operating_point="default", expected_profile_hash="profile-hash",
            required_format="text", required_context_bytes=1,
            authority=self.authority,
        )
        self.assertFalse(ok)
        self.assertIn("qualification_authority_plan_mismatch", reasons)


if __name__ == "__main__":
    unittest.main(verbosity=2)
