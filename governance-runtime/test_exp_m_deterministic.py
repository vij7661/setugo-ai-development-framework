import copy
import sys
import unittest
from hashlib import sha256
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from exp_m_deterministic import (  # noqa: E402
    DeterministicFakeProvider,
    EvidenceDeliveryManifest,
    GovernanceAuthoritySnapshot,
    RequiredEvidenceContract,
    RequiredInteractionContract,
    ProviderCapabilityProfile,
    ReviewerReceipt,
    WireDeliveryRecord,
    adjudicate_insufficient_evidence,
    admissibility_registry,
    complete_delivery,
    evaluate_admissibility,
    preflight_delivery,
    ProviderQualificationExecutionPlan, ProviderCapabilityQualificationRecord,
    ProviderContextIsolationPolicy, ProviderContextStateEvidence, AdmissionFenceRecord,
    MaterializationResult,
    RetrievalEvidenceRecord, materialize_entries, validate_retrieval,
    validate_wire_delivery, WitnessProtocolQualificationRecord,
    validate_witness_qualification, AttemptState, admit_review_attempt,
    PromptIsolationQualificationRecord, validate_egress, validate_prompt_isolation,
    validate_registry_version, validate_retry_transparency,
)


def fixture():
    snapshot = GovernanceAuthoritySnapshot("snap-1", "1", "h", True)
    contract = RequiredEvidenceContract("contract-1", "snap-1", ("a", "b"))
    interactions = RequiredInteractionContract("interaction-1", "snap-1", (("a", "b"),))
    items = {"a": b"alpha", "b": b"beta"}
    manifest = EvidenceDeliveryManifest.freeze("request-1", "commit-1", items)
    provider = ProviderCapabilityProfile("fake", "deterministic", "adapter-1", "profile-hash", True, supported_formats=("text",))
    return snapshot, contract, interactions, items, manifest, provider


def preflight(*args, **kwargs):
    defaults = {
        "plan": ProviderQualificationExecutionPlan("plan", "fake", "default", ("a1",), ("a1",)),
        "qualification": ProviderCapabilityQualificationRecord("plan", "profile-hash", True, True, 0, "default", ("a1",), ("a1",), "fake", "deterministic"),
        "context_policy": ProviderContextIsolationPolicy("policy", "COMPLETE_READABLE_FENCED_STATE", False),
        "context_evidence": ProviderContextStateEvidence(True, ("memory", "config"), True, "state"),
        "fence": AdmissionFenceRecord("fence", "1", True),
    }
    for key, value in defaults.items():
        kwargs.setdefault(key, value)
    return preflight_delivery(*args, **kwargs)


def admissibility_fixture():
    return {
        "review_request": {"current": True, "request_id": "r"},
        "authority_snapshot": GovernanceAuthoritySnapshot("s", "1", "h", True),
        "evidence_contract": RequiredEvidenceContract("e", "s", ("a",)),
        "interaction_contract": RequiredInteractionContract("i", "s", (("a",),)),
        "materialization": MaterializationResult(True, {"a": b"a"}, "rep", "src", "raw-v1"),
        "representation": {"governed": True, "transform_id": "raw-v1"}, "egress": {"authorized": True, "version": "1"},
        "capability_current": True, "accessibility_policy": {"satisfied": True}, "accessibility": {"satisfied": True, "proven": True}, "context_isolation": {"satisfied": True},
        "hidden_state_policy": {"satisfied": True}, "context_state": {"clean": True, "sentinel_passed": True},
        "fence": {"current": True, "version": "1"}, "semantic_context": {"qualified": True}, "wire": {"valid": True},
        "delivery": {"complete": True}, "witness": {"current": True}, "retrieval": {"complete": True},
        "prompt_isolation": {"current": True}, "semantic_coverage": {"complete": True}, "reviewer": {"trusted": True},
        "disposition": "PASS", "disposition_promotable": True,
    }


class ExpMCoreTests(unittest.TestCase):
    def test_complete_one_shot_delivery(self):
        s, c, i, items, m, p = fixture()
        self.assertTrue(preflight(s, c, i, m, "request-1", p, items).allowed)
        receipt, wire = DeterministicFakeProvider().deliver(m, items)
        self.assertTrue(complete_delivery(m, receipt, wire).complete)

    def test_required_item_missing(self):
        s, c, i, items, m, p = fixture(); items.pop("b")
        result = preflight(s, c, i, m, "request-1", p, items)
        self.assertFalse(result.allowed); self.assertIn("manifest_item_set_mismatch", result.reasons)

    def test_optional_contract_does_not_change_required_set(self):
        s, c, i, items, m, p = fixture()
        c = RequiredEvidenceContract(c.contract_id, c.snapshot_id, c.required_ids, ("optional",))
        self.assertTrue(preflight(s, c, i, m, "request-1", p, items).allowed)

    def test_manifest_hash_mismatch(self):
        s, c, i, items, m, p = fixture(); items["a"] = b"changed"
        self.assertFalse(preflight(s, c, i, m, "request-1", p, items).allowed)

    def test_item_size_mismatch(self):
        s, c, i, items, m, p = fixture(); bad = dict(m.items); bad["a"] = dict(bad["a"], size=99)
        m = EvidenceDeliveryManifest(m.request_id, m.reviewed_commit, bad, m.manifest_hash)
        result = preflight(s, c, i, m, "request-1", p, items)
        self.assertFalse(result.allowed); self.assertIn("size_mismatch:a", result.reasons)

    def test_duplicate_required_item_rejected_by_wire(self):
        s, c, i, items, m, p = fixture(); receipt, wire = DeterministicFakeProvider().deliver(m, items)
        dup = WireDeliveryRecord(wire.attempt_id, wire.request_id, wire.wire_hash, wire.semantic_hash, wire.session_id, ("a", "a"))
        result = complete_delivery(m, receipt, dup)
        self.assertFalse(result.complete); self.assertIn("wire_item_set_incomplete", result.reasons)

    def test_unmanifested_item_rejected(self):
        s, c, i, items, m, p = fixture(); items["extra"] = b"x"
        self.assertFalse(preflight(s, c, i, m, "request-1", p, items).allowed)

    def test_wrong_commit_is_bound(self):
        s, c, i, items, m, p = fixture(); wrong = EvidenceDeliveryManifest.freeze("request-1", "other", items)
        self.assertNotEqual(m.reviewed_commit, wrong.reviewed_commit)

    def test_wrong_request_rejected(self):
        s, c, i, items, m, p = fixture()
        self.assertFalse(preflight(s, c, i, m, "other", p, items).allowed)

    def test_reviewer_ack_without_items_rejected(self):
        s, c, i, items, m, p = fixture(); r = ReviewerReceipt("attempt-1", "request-1", "session-1", m.manifest_hash, (), 0, True)
        w = WireDeliveryRecord("attempt-1", "request-1", "w", "s", "session-1", ())
        self.assertFalse(complete_delivery(m, r, w).complete)

    def test_http_success_without_receipt_rejected(self):
        s, c, i, items, m, p = fixture(); self.assertFalse(complete_delivery(m, ReviewerReceipt("a", "request-1", "s", "", (), 0, False), WireDeliveryRecord("a", "request-1", "w", "s", "s", ())).complete)

    def test_upload_id_only_rejected(self):
        s, c, i, items, m, p = fixture(); self.assertFalse(complete_delivery(m, ReviewerReceipt("a", "request-1", "s", m.manifest_hash, (), 0, True), WireDeliveryRecord("a", "request-1", "w", "s", "s", ())).complete)

    def test_provider_unqualified_blocks_preflight(self):
        s, c, i, items, m, p = fixture(); p = ProviderCapabilityProfile(p.provider_id, p.model_id, p.adapter_version, p.profile_hash, False)
        self.assertFalse(preflight(s, c, i, m, "request-1", p, items).allowed)

    def test_unknown_capability_blocks_preflight(self):
        s, c, i, items, m, p = fixture(); p = ProviderCapabilityProfile(p.provider_id, p.model_id, p.adapter_version, p.profile_hash, False)
        self.assertIn("qualification_records_missing", preflight_delivery(s, c, i, m, "request-1", p, items).reasons)

    def test_admissibility_requires_every_predicate(self):
        reg = admissibility_registry(); state = admissibility_fixture()
        self.assertTrue(evaluate_admissibility(state, reg).admissible)
        state["delivery"] = {"complete": False}
        result = evaluate_admissibility(state, reg)
        self.assertFalse(result.admissible); self.assertIn("delivery_complete", result.reasons)

    def test_admissibility_exact_predicate_closure(self):
        reg = admissibility_registry(); self.assertTrue(reg.closure(reg.predicate_ids, reg.logic_mutation_ids))

    def test_authority_snapshot_candidate_writable_rejected(self):
        s, c, i, items, m, p = fixture(); s = GovernanceAuthoritySnapshot(s.snapshot_id, s.version, s.content_hash, False)
        self.assertFalse(preflight(s, c, i, m, "request-1", p, items).allowed)

    def test_snapshot_binding_mismatch_rejected(self):
        s, c, i, items, m, p = fixture(); c = RequiredEvidenceContract(c.contract_id, "other", c.required_ids)
        self.assertFalse(preflight(s, c, i, m, "request-1", p, items).allowed)

    def test_receipt_session_mismatch_rejected(self):
        s, c, i, items, m, p = fixture(); r, w = DeterministicFakeProvider().deliver(m, items)
        r = ReviewerReceipt(r.attempt_id, r.request_id, "other", r.manifest_hash, r.received_item_ids, r.received_bytes, True)
        self.assertFalse(complete_delivery(m, r, w).complete)

    def test_insufficient_evidence_multiple_causes(self):
        result = adjudicate_insufficient_evidence({"SCIENTIFIC_EVIDENCE_MISSING": True, "EVIDENCE_DELIVERY_INCOMPLETE": True})
        self.assertEqual(result.disposition, "MIXED_INSUFFICIENCY")

    def test_insufficient_evidence_unresolved(self):
        self.assertEqual(adjudicate_insufficient_evidence({}).disposition, "INSUFFICIENT_EVIDENCE_CAUSE_UNRESOLVED")

    def test_manifest_is_content_addressed(self):
        _, _, _, items, m, _ = fixture(); self.assertTrue(m.verify(items)[0]); self.assertNotEqual(m.manifest_hash, EvidenceDeliveryManifest.freeze(m.request_id, m.reviewed_commit, {"a": b"x", "b": b"y"}).manifest_hash)

    def test_expired_profile_is_not_current(self):
        s, c, i, items, m, p = fixture(); p = ProviderCapabilityProfile(p.provider_id, p.model_id, p.adapter_version, p.profile_hash, True, "2000-01-01T00:00:00Z", p.supported_formats, p.max_context_bytes)
        result = preflight(s, c, i, m, "request-1", p, items, now="2025-01-01T00:00:00Z")
        self.assertFalse(result.allowed); self.assertIn("profile_expired", result.reasons)

    def test_wrong_profile_hash_is_not_current(self):
        s, c, i, items, m, p = fixture(); p = ProviderCapabilityProfile(p.provider_id, p.model_id, p.adapter_version, "wrong", True, supported_formats=("text",))
        result = preflight(s, c, i, m, "request-1", p, items)
        self.assertFalse(result.allowed); self.assertIn("profile_hash_mismatch", result.reasons)

    def test_wrong_operating_point_is_not_current(self):
        s, c, i, items, m, p = fixture(); result = preflight(s, c, i, m, "request-1", p, items, expected_operating_point="other")
        self.assertFalse(result.allowed); self.assertIn("operating_point_mismatch", result.reasons)

    def test_missing_planned_attempt_is_not_current(self):
        s, c, i, items, m, p = fixture(); plan = ProviderQualificationExecutionPlan("plan", "fake", "default", ("a1",), ("a1", "a2"))
        result = preflight(s, c, i, m, "request-1", p, items, plan=plan)
        self.assertFalse(result.allowed); self.assertIn("qualification_attempt_closure", result.reasons)

    def test_unsupported_format_and_context_limit_fail(self):
        s, c, i, items, m, p = fixture(); p = ProviderCapabilityProfile(p.provider_id, p.model_id, p.adapter_version, p.profile_hash, True, supported_formats=("json",), max_context_bytes=1)
        result = preflight(s, c, i, m, "request-1", p, items, required_format="text", required_context_bytes=100)
        self.assertFalse(result.allowed); self.assertIn("unsupported_format", result.reasons); self.assertIn("context_limit_exceeded", result.reasons)

    def test_dirty_context_and_stale_fence_fail(self):
        s, c, i, items, m, p = fixture(); evidence = ProviderContextStateEvidence(False, ("memory",), False, "state")
        result = preflight(s, c, i, m, "request-1", p, items, context_evidence=evidence, fence=AdmissionFenceRecord("fence", "1", False))
        self.assertFalse(result.allowed); self.assertIn("provider_context_not_clean", result.reasons); self.assertIn("admission_fence_stale", result.reasons)

    def test_materialization_rejects_traversal(self):
        result = materialize_entries({"../escape": b"x"}, source_hash="src")
        self.assertFalse(result.success); self.assertTrue(any("unsafe_member" in r for r in result.reasons))

    def test_retrieval_binds_raw_bytes_and_final_context(self):
        raw = b"page"; rec = RetrievalEvidenceRecord("r", "a", "s", "file", "v1", 0, len(raw), sha256(raw).hexdigest(), len(raw), "tool", 1, "ctx", "ctx-h")
        self.assertTrue(validate_retrieval(rec, raw, expected_request="r", expected_attempt="a", expected_session="s", expected_source="file", expected_version="v1", expected_context_id="ctx", expected_context_hash="ctx-h")[0])
        self.assertFalse(validate_retrieval(rec, b"wrong", expected_request="r", expected_attempt="a", expected_session="s", expected_source="file", expected_version="v1", expected_context_id="ctx", expected_context_hash="ctx-h")[0])

    def test_wire_delivery_rejects_returned_byte_mismatch(self):
        s, c, i, items, m, p = fixture(); provider = DeterministicFakeProvider(); receipt, wire = provider.deliver(m, items); materialized = materialize_entries(items, source_hash="request-1")
        ok, _ = validate_wire_delivery(m, materialized, wire, receipt, {"a": b"bad", "b": items["b"]}, expected_commit="request-1", expected_semantic_hash=wire.semantic_hash)
        self.assertFalse(ok)

    def test_witness_record_binding_budget_and_semantics(self):
        record = WitnessProtocolQualificationRecord("w", "fake", "inline", 10, True, "prompt", "2099-01-01T00:00:00Z")
        self.assertTrue(validate_witness_qualification(record, provider_id="fake", mode="inline", prompt_mode="prompt", now="2025-01-01T00:00:00Z", response="ok", challenge="extract token", final_context_bytes=1, max_final_context_bytes=100)[0])
        self.assertFalse(validate_witness_qualification(record, provider_id="other", mode="inline", prompt_mode="prompt", now="2025-01-01T00:00:00Z", response="ok", challenge="extract token", final_context_bytes=1, max_final_context_bytes=100)[0])
        self.assertFalse(validate_witness_qualification(record, provider_id="fake", mode="inline", prompt_mode="prompt", now="2025-01-01T00:00:00Z", response="01234567890", challenge="extract token", final_context_bytes=1, max_final_context_bytes=100)[0])

    def test_atomic_admission_voids_state_drift(self):
        expected = AttemptState("a", 1, "authority", "request", "cap", "egress", "context", "fence", "prompt", "witness", "session", "registry")
        current = {"generation": 2, "authority_version": "authority", "request_version": "request", "capability_hash": "cap", "egress_version": "egress", "context_hash": "context", "fence_version": "fence", "prompt_hash": "prompt", "witness_hash": "witness", "session_hash": "session", "registry_version": "registry"}
        result = admit_review_attempt(current, expected, attempt_id="a", expected_generation=1)
        self.assertTrue(result.void); self.assertFalse(result.committed)

    def test_r1_egress_prompt_retry_registry_are_evidence_validated(self):
        self.assertTrue(validate_egress({"authorized": True, "version": "v1"}, "v1")[0])
        self.assertFalse(validate_egress({"authorized": False, "version": "v1"}, "v1")[0])
        current = PromptIsolationQualificationRecord("p", "fake", "inline", True, "2099-01-01T00:00:00Z")
        self.assertTrue(validate_prompt_isolation(current, provider_id="fake", mode="inline", now="2025-01-01T00:00:00Z")[0])
        self.assertFalse(validate_prompt_isolation(current, provider_id="other", mode="inline", now="2025-01-01T00:00:00Z")[0])
        self.assertFalse(validate_retry_transparency(({"attempt_id": "a", "wire_hash": "w"},), automatic_retry_hidden=True)[0])
        self.assertFalse(validate_registry_version("v2", "v1")[0])


if __name__ == "__main__":
    unittest.main(verbosity=2)
