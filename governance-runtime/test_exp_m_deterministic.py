import copy
import sys
import unittest
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
)


def fixture():
    snapshot = GovernanceAuthoritySnapshot("snap-1", "1", "h", True)
    contract = RequiredEvidenceContract("contract-1", "snap-1", ("a", "b"))
    interactions = RequiredInteractionContract("interaction-1", "snap-1", (("a", "b"),))
    items = {"a": b"alpha", "b": b"beta"}
    manifest = EvidenceDeliveryManifest.freeze("request-1", "commit-1", items)
    provider = ProviderCapabilityProfile("fake", "model", "adapter-1", "profile", True, supported_formats=("text",))
    return snapshot, contract, interactions, items, manifest, provider


class ExpMCoreTests(unittest.TestCase):
    def test_complete_one_shot_delivery(self):
        s, c, i, items, m, p = fixture()
        self.assertTrue(preflight_delivery(s, c, i, m, "request-1", p, items).allowed)
        receipt, wire = DeterministicFakeProvider().deliver(m, items)
        self.assertTrue(complete_delivery(m, receipt, wire).complete)

    def test_required_item_missing(self):
        s, c, i, items, m, p = fixture(); items.pop("b")
        result = preflight_delivery(s, c, i, m, "request-1", p, items)
        self.assertFalse(result.allowed); self.assertIn("manifest_item_set_mismatch", result.reasons)

    def test_optional_contract_does_not_change_required_set(self):
        s, c, i, items, m, p = fixture()
        c = RequiredEvidenceContract(c.contract_id, c.snapshot_id, c.required_ids, ("optional",))
        self.assertTrue(preflight_delivery(s, c, i, m, "request-1", p, items).allowed)

    def test_manifest_hash_mismatch(self):
        s, c, i, items, m, p = fixture(); items["a"] = b"changed"
        self.assertFalse(preflight_delivery(s, c, i, m, "request-1", p, items).allowed)

    def test_item_size_mismatch(self):
        s, c, i, items, m, p = fixture(); bad = dict(m.items); bad["a"] = dict(bad["a"], size=99)
        m = EvidenceDeliveryManifest(m.request_id, m.reviewed_commit, bad, m.manifest_hash)
        result = preflight_delivery(s, c, i, m, "request-1", p, items)
        self.assertFalse(result.allowed); self.assertIn("size_mismatch:a", result.reasons)

    def test_duplicate_required_item_rejected_by_wire(self):
        s, c, i, items, m, p = fixture(); receipt, wire = DeterministicFakeProvider().deliver(m, items)
        dup = WireDeliveryRecord(wire.attempt_id, wire.request_id, wire.wire_hash, wire.semantic_hash, wire.session_id, ("a", "a"))
        result = complete_delivery(m, receipt, dup)
        self.assertFalse(result.complete); self.assertIn("wire_item_set_incomplete", result.reasons)

    def test_unmanifested_item_rejected(self):
        s, c, i, items, m, p = fixture(); items["extra"] = b"x"
        self.assertFalse(preflight_delivery(s, c, i, m, "request-1", p, items).allowed)

    def test_wrong_commit_is_bound(self):
        s, c, i, items, m, p = fixture(); wrong = EvidenceDeliveryManifest.freeze("request-1", "other", items)
        self.assertNotEqual(m.reviewed_commit, wrong.reviewed_commit)

    def test_wrong_request_rejected(self):
        s, c, i, items, m, p = fixture()
        self.assertFalse(preflight_delivery(s, c, i, m, "other", p, items).allowed)

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
        self.assertFalse(preflight_delivery(s, c, i, m, "request-1", p, items).allowed)

    def test_unknown_capability_blocks_preflight(self):
        s, c, i, items, m, p = fixture(); p = ProviderCapabilityProfile(p.provider_id, p.model_id, p.adapter_version, p.profile_hash, False)
        self.assertIn("provider_unqualified", preflight_delivery(s, c, i, m, "request-1", p, items).reasons)

    def test_admissibility_requires_every_predicate(self):
        reg = admissibility_registry(); state = {key: True for key in reg.predicate_ids}
        self.assertTrue(evaluate_admissibility(state, reg).admissible)
        state[reg.predicate_ids[0]] = False
        result = evaluate_admissibility(state, reg)
        self.assertFalse(result.admissible); self.assertIn(reg.predicate_ids[0], result.reasons)

    def test_admissibility_exact_predicate_closure(self):
        reg = admissibility_registry(); self.assertTrue(reg.closure(reg.predicate_ids, reg.logic_mutation_ids))

    def test_authority_snapshot_candidate_writable_rejected(self):
        s, c, i, items, m, p = fixture(); s = GovernanceAuthoritySnapshot(s.snapshot_id, s.version, s.content_hash, False)
        self.assertFalse(preflight_delivery(s, c, i, m, "request-1", p, items).allowed)

    def test_snapshot_binding_mismatch_rejected(self):
        s, c, i, items, m, p = fixture(); c = RequiredEvidenceContract(c.contract_id, "other", c.required_ids)
        self.assertFalse(preflight_delivery(s, c, i, m, "request-1", p, items).allowed)

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


if __name__ == "__main__":
    unittest.main(verbosity=2)
