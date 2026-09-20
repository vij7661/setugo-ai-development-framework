"""Reviewer-authored preregistered adversarial suite for EXP-M R2E.

This file is frozen before the C-1/C-2/H-1/H-2/H-3/H-5/H-6 remediation.
It imports only public production/authority APIs.  It MUST NOT import the
normal mutation runner, phase runner, predicate validator internals, or
candidate self-falsification module.
"""
from __future__ import annotations
import inspect
import tempfile
import unittest
from pathlib import Path

from exp_m_deterministic import (
    AdmissionCheckpoint,
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
    ReviewerReceipt,
    WireDeliveryRecord,
    digest,
    evaluate_admissibility,
    materialize_entries,
    validate_capability,
    validate_wire_delivery,
)
from exp_m_expectation_authority import (
    authority_context_valid,
    load_default_authority,
    load_predicate_context,
)


class ReviewerR2EAttacks(unittest.TestCase):
    def setUp(self):
        self.authority = load_default_authority()
        self.context = load_predicate_context(self.authority)

    def test_ca1_direct_self_derived_context_is_not_authoritative(self):
        forged = PredicateContext(**{
            name: getattr(self.context, name)
            for name in self.context.__dataclass_fields__
            if name != "expectation_manifest_hash"
        }, expectation_manifest_hash=self.context.expectation_manifest_hash)
        self.assertFalse(authority_context_valid(self.authority, forged))
        verdict = evaluate_admissibility(EvidenceBundle({}), forged, authority=self.authority)
        self.assertFalse(verdict.admissible)
        self.assertIn("expectation_authority_invalid", verdict.reasons)

    def test_c1_production_has_no_context_from_state(self):
        import exp_m_deterministic as production
        self.assertNotIn("context_from_state", inspect.getsource(production))
        self.assertIn("authority", inspect.signature(evaluate_admissibility).parameters)

    def test_ca2_forged_correctly_keyed_verdict_token_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            ledger = PersistentAdmissionLedger(Path(td) / "ledger")
            ledger.seed_protected_state(1, "s1")
            payload = {"evidence": {"x": 1}, "context_hash": "ctx", "predicates": {"p": True}, "generation": 1, "state_hash": "s1"}
            good = digest(payload)
            forged = digest({**payload, "evidence": {"x": 2}})
            cp = ledger.commit_with_verdict(
                "a", 1, "COMMITTED",
                expected_state_hash="s1",
                expected_evidence_token=forged,
                verdict_payload=payload,
                next_state_hash="s2",
            )
            self.assertTrue(cp.void)
            self.assertIn("evidence_token_mismatch", cp.reasons)
            self.assertNotEqual(good, forged)

    def test_c2_public_caller_minting_api_removed(self):
        self.assertFalse(hasattr(PersistentAdmissionLedger, "issue_verdict_token"))
        self.assertFalse(hasattr(PersistentAdmissionLedger, "verdict_token_matches"))

    def test_ca4_forged_complete_receipt_wrong_bytes_rejected(self):
        items = {"a": b"a"}
        commit = self.authority.resolve_reviewed_commit()
        manifest = EvidenceDeliveryManifest.freeze("r", commit, items)
        materialized = MaterializationResult(True, items, digest({"a": digest(b"a")}), commit, "raw-v1")
        wire_hash = self.authority.canonical_wire_hash_for_test(manifest, materialized, items)
        wire = WireDeliveryRecord("a", "r", wire_hash, "", "s", ("a",))
        receipt = ReviewerReceipt("a", "r", "s", manifest.manifest_hash, ("a",), 6, True)
        ok, _ = validate_wire_delivery(manifest, materialized, wire, receipt, {"a": b"forged"}, expected_commit=commit)
        self.assertFalse(ok)

    def test_ca5_archive_content_detection_ignores_extension(self):
        import io, zipfile
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as z:
            z.writestr("../escape", b"x")
        result = materialize_entries(
            (MaterializationEntry("payload.bin", "payload.bin", "file", buf.getvalue()),),
            source_hash="s",
        )
        self.assertFalse(result.success)
        self.assertTrue(any("escape" in r for r in result.reasons))

    def test_h5_r5_attempts_must_match_scheduled_days_and_blocks(self):
        protocol = self.authority.load_r5_protocol()
        n = int(protocol["n_min"])
        ids = tuple(f"a{i}" for i in range(n))
        plan = ProviderQualificationExecutionPlan(
            "r5", "fake", "default", ids[:1], ids[1:],
            qualification_profile="R5_PRODUCTION",
            scheduled_days=("2026-01-01", "2026-01-02", "2026-01-03"),
            scheduled_time_blocks=("00-06", "06-12", "12-18", "18-24"),
        )
        attempts = tuple(
            PhysicalAttemptRecord(i, i, None, "FIRST", "r", "s", f"w-{i}", "OK",
                                  utc_day="2026-01-01", time_block="00-06")
            for i in ids
        )
        profile = ProviderCapabilityProfile("fake", "deterministic", "adapter", "profile-hash", True,
                                            supported_formats=("text",), max_context_bytes=1_000_000)
        record = ProviderCapabilityQualificationRecord(
            "r5", "profile-hash", True, True, 0, "default", ids, ids,
            "fake", "deterministic", attempt_records=attempts, protocol_version=protocol["protocol_id"]
        )
        ok, reasons = validate_capability(
            profile, plan, record, now="2026-01-01T00:00:00Z",
            expected_provider="fake", expected_model="deterministic",
            expected_operating_point="default", expected_profile_hash="profile-hash",
            required_format="text", required_context_bytes=1,
            authority=self.authority,
        )
        self.assertFalse(ok)
        self.assertTrue(any("schedule" in r for r in reasons))

    def test_h6_missing_r5_protocol_fails_closed(self):
        broken = self.authority.with_missing_r5_protocol_for_test()
        profile = ProviderCapabilityProfile("fake", "deterministic", "adapter", "profile-hash", True,
                                            supported_formats=("text",), max_context_bytes=1_000_000)
        plan = ProviderQualificationExecutionPlan("r5", "fake", "default", ("a",), ("b",), qualification_profile="R5_PRODUCTION")
        record = ProviderCapabilityQualificationRecord("r5", "profile-hash", True, True, 0, "default", ("a","b"), ("a","b"), "fake", "deterministic")
        ok, reasons = validate_capability(
            profile, plan, record, now="2026-01-01T00:00:00Z",
            expected_provider="fake", expected_model="deterministic",
            expected_operating_point="default", expected_profile_hash="profile-hash",
            required_format="text", required_context_bytes=1, authority=broken,
        )
        self.assertFalse(ok)
        self.assertIn("r5_protocol_unavailable", reasons)

    def test_h9_caller_pass_cannot_override_failed_predicate(self):
        verdict = evaluate_admissibility(EvidenceBundle({"disposition": "PASS"}), self.context, authority=self.authority)
        self.assertFalse(verdict.admissible)
        self.assertFalse(verdict.predicate_results.get("disposition_promotable", True))


if __name__ == "__main__":
    unittest.main(verbosity=2)
