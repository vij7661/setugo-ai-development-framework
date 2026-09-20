"""Preregistered EXP-M R2E compound-attack suite.

Frozen before C-4 / prior-evidence verification implementation.  Every test
combines at least two controls or crosses an authority boundary.  The suite
must not be edited by candidate remediation; later code must satisfy it.
"""
from __future__ import annotations

import io
import tempfile
import unittest
import zipfile
from pathlib import Path

from exp_m_deterministic import (
    EvidenceBundle,
    EvidenceDeliveryManifest,
    MaterializationEntry,
    MaterializationResult,
    PersistentAdmissionLedger,
    PhysicalAttemptRecord,
    PredicateContext,
    ProviderCapabilityProfile,
    ProviderCapabilityQualificationRecord,
    ProviderQualificationExecutionPlan,
    RetrievalEvidenceRecord,
    ReviewerReceipt,
    WireDeliveryRecord,
    digest,
    evaluate_admissibility,
    materialize_entries,
    validate_capability,
    validate_retrieval,
    validate_wire_delivery,
)
from exp_m_expectation_authority import load_default_authority, load_predicate_context
from exp_m_test_fixtures import bundle_from_state
from verify_exp_m_sep_sequence import verify_reviewer_suite_frozen
from verify_exp_m_prior_evidence import verify_prior_evidence_index


class CompoundAttackSuite(unittest.TestCase):
    def setUp(self):
        self.authority = load_default_authority()
        self.context = load_predicate_context(self.authority)

    def test_ca1_self_consistent_context_plus_forged_complete_receipt(self):
        forged_context = PredicateContext(**{
            name: getattr(self.context, name)
            for name in self.context.__dataclass_fields__
            if name != "expectation_manifest_hash"
        }, expectation_manifest_hash=self.context.expectation_manifest_hash)
        state = {"review_request": {"current": True, "request_id": self.context.request_id},
                 "delivery": {"complete": True}, "disposition": "PASS"}
        bundle = bundle_from_state(state, self.context)
        receipt = bundle.evidence["receipt"]
        bundle.evidence["receipt"] = ReviewerReceipt(
            receipt.attempt_id, receipt.request_id, receipt.session_id,
            receipt.manifest_hash, receipt.received_item_ids,
            receipt.received_bytes, True,
        )
        verdict = evaluate_admissibility(bundle, forged_context, authority=self.authority)
        self.assertFalse(verdict.admissible)
        self.assertIn("expectation_authority_invalid", verdict.reasons)

    def test_ca2_correctly_keyed_token_for_different_bundle(self):
        with tempfile.TemporaryDirectory() as td:
            ledger = PersistentAdmissionLedger(Path(td) / "ledger")
            ledger.seed_protected_state(1, "s1")
            original = {"evidence": {"bundle": "A"}, "generation": 1, "state_hash": "s1"}
            wrong = {"evidence": {"bundle": "B"}, "generation": 1, "state_hash": "s1"}
            cp = ledger.commit_with_verdict(
                "a", 1, "COMMITTED", expected_state_hash="s1",
                expected_evidence_token=digest(original),
                verdict_payload=wrong,
            )
            self.assertTrue(cp.void)
            self.assertIn("evidence_token_mismatch", cp.reasons)

    def test_ca3_fabricated_manifest_plus_matching_caller_commit(self):
        fake = "f" * 40
        items = {"a": b"a"}
        manifest = EvidenceDeliveryManifest.freeze(self.context.request_id, fake, items)
        materialized = MaterializationResult(True, items, digest({"a": digest(b"a")}), fake, "raw-v1")
        wire = WireDeliveryRecord(self.context.attempt_id, self.context.request_id, "w", "w", self.context.session_id, ("a",))
        receipt = ReviewerReceipt(self.context.attempt_id, self.context.request_id, self.context.session_id, manifest.manifest_hash, ("a",), 1, True)
        ok, reasons = validate_wire_delivery(manifest, materialized, wire, receipt, items, expected_commit=fake, authority=self.authority)
        self.assertFalse(ok)
        self.assertIn("authority_reviewed_commit_mismatch", reasons)

    def test_ca4_fabricated_retrieval_bytes_plus_forged_receipt(self):
        forged = b"forged"
        retrieval = RetrievalEvidenceRecord(
            self.context.request_id, self.context.attempt_id, self.context.session_id,
            self.context.retrieval_source, self.context.retrieval_version,
            0, len(forged), digest(forged), len(forged), "tool", 1,
            self.context.final_context_id, self.context.final_context_hash,
        )
        retrieval_ok, _ = validate_retrieval(
            retrieval,
            expected_request=self.context.request_id,
            expected_attempt=self.context.attempt_id,
            expected_session=self.context.session_id,
            expected_source=self.context.retrieval_source,
            expected_version=self.context.retrieval_version,
            expected_context_id=self.context.final_context_id,
            expected_context_hash=self.context.final_context_hash,
            authority=self.authority,
        )
        items = {"a": b"a"}
        commit = self.authority.resolve_reviewed_commit()
        manifest = EvidenceDeliveryManifest.freeze(self.context.request_id, commit, items)
        materialized = MaterializationResult(True, items, digest({"a": digest(b"a")}), commit, "raw-v1")
        wire = WireDeliveryRecord(self.context.attempt_id, self.context.request_id, "w", "w", self.context.session_id, ("a",))
        receipt = ReviewerReceipt(self.context.attempt_id, self.context.request_id, self.context.session_id, manifest.manifest_hash, ("a",), len(forged), True)
        delivery_ok, _ = validate_wire_delivery(manifest, materialized, wire, receipt, {"a": forged}, expected_commit=commit, authority=self.authority)
        self.assertFalse(retrieval_ok or delivery_ok)

    def test_ca5_zip_named_bin_plus_fake_schedule_diversity(self):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as z:
            z.writestr("../escape", b"x")
        mat = materialize_entries((MaterializationEntry("payload.bin", "payload.bin", "file", buf.getvalue()),), source_hash="s")
        protocol = self.authority.load_r5_protocol()
        n = int(protocol["n_min"])
        ids = tuple(f"a{i}" for i in range(n))
        plan = ProviderQualificationExecutionPlan("r5", "fake", "default", ids[:1], ids[1:], "R5_PRODUCTION", "seed",
                                                   ("d1","d2","d3"), ("b1","b2","b3","b4"), "env")
        attempts = tuple(PhysicalAttemptRecord(x, x, None, "FIRST", "r", "s", "w"+x, "OK", utc_day="d1", time_block="b1") for x in ids)
        profile = ProviderCapabilityProfile("fake", "deterministic", "adapter", "profile-hash", True, supported_formats=("text",), max_context_bytes=1000000)
        record = ProviderCapabilityQualificationRecord("r5", "profile-hash", True, True, 0, "default", ids, ids, "fake", "deterministic", attempt_records=attempts)
        cap_ok, cap_reasons = validate_capability(profile, plan, record, now="2026-01-01T00:00:00Z",
            expected_provider="fake", expected_model="deterministic", expected_operating_point="default",
            expected_profile_hash="profile-hash", required_format="text", required_context_bytes=1, authority=self.authority)
        self.assertFalse(mat.success)
        self.assertFalse(cap_ok)
        self.assertTrue(any("schedule" in r for r in cap_reasons))

    def test_ca6_authority_plan_absent_but_caller_plan_self_consistent(self):
        profile = ProviderCapabilityProfile("fake", "deterministic", "adapter", "profile-hash", True, supported_formats=("text",), max_context_bytes=1000000)
        plan = ProviderQualificationExecutionPlan("not-authorized", "fake", "default", ("x",), ("x",))
        rec = ProviderCapabilityQualificationRecord("not-authorized", "profile-hash", True, True, 0, "default", ("x",), ("x",), "fake", "deterministic",
            attempt_records=(PhysicalAttemptRecord("x","x",None,"FIRST","r","s","w","OK"),))
        ok, reasons = validate_capability(profile, plan, rec, now="2026-01-01T00:00:00Z",
            expected_provider="fake", expected_model="deterministic", expected_operating_point="default",
            expected_profile_hash="profile-hash", required_format="text", required_context_bytes=1, authority=self.authority)
        self.assertFalse(ok)
        self.assertIn("qualification_authority_plan_missing", reasons)

    def test_ca7_prior_artifact_deleted_but_index_unchanged(self):
        ok, reasons = verify_prior_evidence_index(simulate_deleted_indexed_artifact=True)
        self.assertFalse(ok)
        self.assertIn("indexed_prior_artifact_missing", reasons)

    def test_ca8_reviewer_suite_modified_after_source_freeze(self):
        ok, reasons = verify_reviewer_suite_frozen(simulate_suite_mutation=True)
        self.assertFalse(ok)
        self.assertIn("reviewer_suite_hash_drift", reasons)

    def test_ca9_caller_pass_with_failed_predicate(self):
        verdict = evaluate_admissibility(EvidenceBundle({"disposition": "PASS"}), self.context, authority=self.authority)
        self.assertFalse(verdict.admissible)
        self.assertFalse(verdict.predicate_results.get("disposition_promotable", True))

    def test_ca10_missing_protocol_with_self_consistent_record(self):
        broken = self.authority.with_missing_r5_protocol_for_test()
        profile = ProviderCapabilityProfile("fake","deterministic","adapter","profile-hash",True,supported_formats=("text",),max_context_bytes=1000000)
        plan = ProviderQualificationExecutionPlan("r5","fake","default",("a",),("b",),"R5_PRODUCTION")
        rec = ProviderCapabilityQualificationRecord("r5","profile-hash",True,True,0,"default",("a","b"),("a","b"),"fake","deterministic")
        ok, reasons = validate_capability(profile, plan, rec, now="2026-01-01T00:00:00Z",
            expected_provider="fake", expected_model="deterministic", expected_operating_point="default",
            expected_profile_hash="profile-hash", required_format="text", required_context_bytes=1, authority=broken)
        self.assertFalse(ok)
        self.assertIn("r5_protocol_unavailable", reasons)


if __name__ == "__main__":
    unittest.main(verbosity=2)
