import copy
import sys
import unittest
import threading
import uuid
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
    validate_registry_version, validate_retry_transparency, validate_capability,
    PersistentAdmissionLedger, PhysicalAttemptRecord,
    AccessibilityProofRecord, ReviewerProvenanceRecord, SemanticCoverageRecord,
    DeliveryCompletenessResult,
    RepresentationRecord,
    MaterializationEntry,
    FinalContextInteractionEvidence,
    digest,
)

from exp_m_test_fixtures import bundle_from_state
from exp_m_expectation_authority import load_default_authority, load_predicate_context

AUTHORITY = load_default_authority()
AUTHORITY_CONTEXT = load_predicate_context(AUTHORITY)


def fixture():
    ctx = AUTHORITY_CONTEXT
    snapshot = GovernanceAuthoritySnapshot(ctx.authority_snapshot_id, ctx.authority_version, ctx.authority_snapshot_hash, True)
    contract = RequiredEvidenceContract("contract-1", ctx.authority_snapshot_id, ("a",))
    interactions = RequiredInteractionContract("interaction-1", ctx.authority_snapshot_id, (("a",),))
    items = {"a": b"a"}
    manifest = EvidenceDeliveryManifest.freeze(ctx.request_id, ctx.reviewed_commit, items)
    provider = ProviderCapabilityProfile(
        ctx.expected_provider, ctx.expected_model, ctx.expected_adapter,
        ctx.expected_profile_hash, True, supported_formats=("text",),
        max_context_bytes=1_000_000,
    )
    return snapshot, contract, interactions, items, manifest, provider


def preflight(*args, **kwargs):
    ctx = AUTHORITY_CONTEXT
    defaults = {
        "context": ctx,
        "authority": AUTHORITY,
        "plan": ProviderQualificationExecutionPlan("plan", ctx.expected_provider, ctx.expected_operating_point, ("a1",), ("a1",)),
        "qualification": ProviderCapabilityQualificationRecord(
            "plan", ctx.expected_profile_hash, True, True, 0, ctx.expected_operating_point,
            ("a1",), ("a1",), ctx.expected_provider, ctx.expected_model,
            attempt_records=(PhysicalAttemptRecord("a1", "a1", None, "FIRST", ctx.request_id, ctx.session_id, "wire-a1", "OK"),),
        ),
        "context_policy": ProviderContextIsolationPolicy("policy", "COMPLETE_READABLE_FENCED_STATE", False),
        "context_evidence": ProviderContextStateEvidence(
            True, ("memory", "config"), True, "state",
            channel_observations=(
                {"channel": "memory", "observed_hash": "state", "expected_hash": "state", "readable": True, "fenced": True, "generation": 1, "observer_id": "platform-context-observer"},
                {"channel": "config", "observed_hash": "state", "expected_hash": "state", "readable": True, "fenced": True, "generation": 1, "observer_id": "platform-context-observer"},
            ),
        ),
        "fence": AdmissionFenceRecord("fence", ctx.expected_fence_version, True),
        "risk_policy": __import__("exp_m_deterministic").ProviderAccessibilityRiskPolicy(ctx.expected_transition_class, "inline", True, False),
        "observed_interactions": (("a",),),
        "observed_context": FinalContextInteractionEvidence(
            ctx.request_id, ctx.session_id, ctx.final_context_hash, ("a",), (("a",),), True,
            digest({"context_id": ctx.final_context_id, "source_hash": ctx.reviewed_commit, "members": ("a",), "assembly": "trusted-final-context-v1"}),
        ),
    }
    for key, value in defaults.items():
        kwargs.setdefault(key, value)
    return preflight_delivery(*args, **kwargs)


def admissibility_fixture():
    return {
        "review_request": {"current": True, "request_id": "r"},
        "authority_snapshot": GovernanceAuthoritySnapshot(AUTHORITY_CONTEXT.authority_snapshot_id, AUTHORITY_CONTEXT.authority_version, AUTHORITY_CONTEXT.authority_snapshot_hash, True),
        "evidence_contract": RequiredEvidenceContract("e", AUTHORITY_CONTEXT.authority_snapshot_id, ("a",)),
        "interaction_contract": RequiredInteractionContract("i", AUTHORITY_CONTEXT.authority_snapshot_id, (("a",),)),
        "materialization": MaterializationResult(True, {"a": b"a"}, "rep", "src", "raw-v1"),
        "representation": RepresentationRecord("raw-v1", "1", "transform", "registry-exp-m-r1", "src", "rep", "params", "coverage"), "egress": {"authorized": True, "version": "1"},
        "capability": {"validated": True}, "accessibility_policy": {"satisfied": True, "risk_policy_version": "r1"}, "accessibility": AccessibilityProofRecord("proof", "ch", "fake", "inline", "ctx", True), "context_isolation": {"satisfied": True, "transition_class": "LOWER"},
        "hidden_state_policy": {"satisfied": True}, "context_state": {"clean": True, "sentinel_passed": True, "state_hash": "state"},
        "fence": {"current": True, "version": "1"}, "semantic_context": {"qualified": True, "context_hash": "ctx-h"}, "wire": WireDeliveryRecord("a", "r", "w", "s", "s", ("a",)),
        "delivery": DeliveryCompletenessResult(True), "witness": WitnessProtocolQualificationRecord("w", "fake", "inline", 100, True, "prompt", "2099-01-01T00:00:00Z"), "retrieval": RetrievalEvidenceRecord("r", "a", "s", "file", "v", 0, 1, sha256(b"a").hexdigest(), 1, "tool", 1, "ctx", "ctx-h"), "retrieval_bytes": b"a",
        "prompt_isolation": {"current": True}, "semantic_coverage": SemanticCoverageRecord("cov", "ctx", True), "reviewer": ReviewerProvenanceRecord("reviewer", "policy", True),
        "disposition": "PASS", "disposition_promotable": True,
    }


class ExpMCoreTests(unittest.TestCase):
    def test_complete_one_shot_delivery(self):
        s, c, i, items, m, p = fixture()
        self.assertTrue(preflight(s, c, i, m, "r", p, items).allowed)
        receipt, wire = DeterministicFakeProvider().deliver(m, items)
        self.assertTrue(complete_delivery(m, receipt, wire).complete)

    def test_required_item_missing(self):
        s, c, i, items, m, p = fixture(); items.pop("a")
        result = preflight(s, c, i, m, "r", p, items)
        self.assertFalse(result.allowed); self.assertIn("manifest_item_set_mismatch", result.reasons)

    def test_optional_contract_does_not_change_required_set(self):
        s, c, i, items, m, p = fixture()
        c = RequiredEvidenceContract(c.contract_id, c.snapshot_id, c.required_ids, ("optional",))
        self.assertTrue(preflight(s, c, i, m, "r", p, items).allowed)

    def test_manifest_hash_mismatch(self):
        s, c, i, items, m, p = fixture(); items["a"] = b"changed"
        self.assertFalse(preflight(s, c, i, m, "r", p, items).allowed)

    def test_item_size_mismatch(self):
        s, c, i, items, m, p = fixture(); bad = dict(m.items); bad["a"] = dict(bad["a"], size=99)
        m = EvidenceDeliveryManifest(m.request_id, m.reviewed_commit, bad, m.manifest_hash)
        result = preflight(s, c, i, m, "r", p, items)
        self.assertFalse(result.allowed); self.assertIn("size_mismatch:a", result.reasons)

    def test_duplicate_required_item_rejected_by_wire(self):
        s, c, i, items, m, p = fixture(); receipt, wire = DeterministicFakeProvider().deliver(m, items)
        dup = WireDeliveryRecord(wire.attempt_id, wire.request_id, wire.wire_hash, wire.semantic_hash, wire.session_id, ("a", "a"))
        result = complete_delivery(m, receipt, dup)
        self.assertFalse(result.complete); self.assertIn("wire_item_set_incomplete", result.reasons)

    def test_unmanifested_item_rejected(self):
        s, c, i, items, m, p = fixture(); items["extra"] = b"x"
        self.assertFalse(preflight(s, c, i, m, "r", p, items).allowed)

    def test_wrong_commit_is_bound(self):
        s, c, i, items, m, p = fixture(); wrong = EvidenceDeliveryManifest.freeze("r", "other", items)
        self.assertNotEqual(m.reviewed_commit, wrong.reviewed_commit)

    def test_wrong_request_rejected(self):
        s, c, i, items, m, p = fixture()
        self.assertFalse(preflight(s, c, i, m, "other", p, items).allowed)

    def test_reviewer_ack_without_items_rejected(self):
        s, c, i, items, m, p = fixture(); r = ReviewerReceipt("attempt-1", "r", "session-1", m.manifest_hash, (), 0, True)
        w = WireDeliveryRecord("attempt-1", "r", "w", "s", "session-1", ())
        self.assertFalse(complete_delivery(m, r, w).complete)

    def test_http_success_without_receipt_rejected(self):
        s, c, i, items, m, p = fixture(); self.assertFalse(complete_delivery(m, ReviewerReceipt("a", "r", "s", "", (), 0, False), WireDeliveryRecord("a", "r", "w", "s", "s", ())).complete)

    def test_upload_id_only_rejected(self):
        s, c, i, items, m, p = fixture(); self.assertFalse(complete_delivery(m, ReviewerReceipt("a", "r", "s", m.manifest_hash, (), 0, True), WireDeliveryRecord("a", "r", "w", "s", "s", ())).complete)

    def test_provider_unqualified_blocks_preflight(self):
        s, c, i, items, m, p = fixture()
        p = ProviderCapabilityProfile(
            p.provider_id, p.model_id, p.adapter_version, p.profile_hash, False,
            p.expires_at, p.supported_formats, p.max_context_bytes,
        )
        result = preflight(s, c, i, m, "r", p, items)
        self.assertFalse(result.allowed)
        self.assertIn("provider_profile_not_qualified", result.reasons)

    def test_unknown_capability_blocks_preflight(self):
        s, c, i, items, m, p = fixture(); p = ProviderCapabilityProfile(p.provider_id, p.model_id, p.adapter_version, p.profile_hash, False)
        self.assertIn(
            "qualification_records_missing",
            preflight_delivery(s, c, i, m, "r", p, items, context=AUTHORITY_CONTEXT, authority=AUTHORITY).reasons,
        )

    def test_admissibility_requires_every_predicate(self):
        reg = admissibility_registry(); state = admissibility_fixture()
        self.assertTrue(evaluate_admissibility(bundle_from_state(state, AUTHORITY_CONTEXT), AUTHORITY_CONTEXT, reg, authority=AUTHORITY).admissible)
        state["delivery"] = {"complete": False}
        result = evaluate_admissibility(bundle_from_state(state, AUTHORITY_CONTEXT), AUTHORITY_CONTEXT, reg, authority=AUTHORITY)
        self.assertFalse(result.admissible); self.assertIn("delivery_complete", result.reasons)

    def test_admissibility_exact_predicate_closure(self):
        reg = admissibility_registry(); self.assertTrue(reg.closure(reg.predicate_ids, reg.logic_mutation_ids,
            declared_mutations=reg.logic_mutation_ids, executed_mutations=reg.logic_mutation_ids,
            killed_mutations=reg.logic_mutation_ids, declared_fixtures=reg.fixture_ids,
            executed_fixtures=reg.fixture_ids, executed_fixture_targets=reg.predicate_ids))

    def test_authority_snapshot_candidate_writable_rejected(self):
        s, c, i, items, m, p = fixture(); s = GovernanceAuthoritySnapshot(s.snapshot_id, s.version, s.content_hash, False)
        self.assertFalse(preflight(s, c, i, m, "r", p, items).allowed)

    def test_snapshot_binding_mismatch_rejected(self):
        s, c, i, items, m, p = fixture(); c = RequiredEvidenceContract(c.contract_id, "other", c.required_ids)
        self.assertFalse(preflight(s, c, i, m, "r", p, items).allowed)

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
        result = preflight(s, c, i, m, "r", p, items, now="2025-01-01T00:00:00Z")
        self.assertFalse(result.allowed); self.assertIn("profile_expired", result.reasons)

    def test_wrong_profile_hash_is_not_current(self):
        s, c, i, items, m, p = fixture(); p = ProviderCapabilityProfile(p.provider_id, p.model_id, p.adapter_version, "wrong", True, supported_formats=("text",))
        result = preflight(s, c, i, m, "r", p, items)
        self.assertFalse(result.allowed); self.assertIn("profile_hash_mismatch", result.reasons)

    def test_wrong_operating_point_is_not_current(self):
        s, c, i, items, m, p = fixture()
        plan = ProviderQualificationExecutionPlan("plan", "fake", "other", ("a1",), ("a1",))
        record = ProviderCapabilityQualificationRecord(
            "plan", "profile-hash", True, True, 0, "other",
            ("a1",), ("a1",), "fake", "deterministic",
            attempt_records=(PhysicalAttemptRecord("a1", "a1", None, "FIRST", "r", "s", "wire-a1", "OK"),),
        )
        result = preflight(s, c, i, m, "r", p, items, plan=plan, qualification=record)
        self.assertFalse(result.allowed); self.assertIn("operating_point_mismatch", result.reasons)

    def test_missing_planned_attempt_is_not_current(self):
        s, c, i, items, m, p = fixture(); plan = ProviderQualificationExecutionPlan("plan", "fake", "default", ("a1",), ("a1", "a2"))
        result = preflight(s, c, i, m, "r", p, items, plan=plan)
        self.assertFalse(result.allowed); self.assertIn("qualification_attempt_closure", result.reasons)

    def test_unsupported_format_and_context_limit_fail(self):
        s, c, i, items, m, p = fixture(); p = ProviderCapabilityProfile(p.provider_id, p.model_id, p.adapter_version, p.profile_hash, True, supported_formats=("json",), max_context_bytes=1)
        result = preflight(s, c, i, m, "r", p, items, required_format="text", required_context_bytes=100)
        self.assertFalse(result.allowed); self.assertIn("unsupported_format", result.reasons); self.assertIn("context_limit_exceeded", result.reasons)

    def test_dirty_context_and_stale_fence_fail(self):
        s, c, i, items, m, p = fixture(); evidence = ProviderContextStateEvidence(False, ("memory",), False, "state")
        result = preflight(s, c, i, m, "r", p, items, context_evidence=evidence, fence=AdmissionFenceRecord("fence", "1", False))
        self.assertFalse(result.allowed); self.assertIn("context_channel_unobserved", result.reasons); self.assertIn("admission_fence_stale", result.reasons)

    def test_materialization_rejects_traversal(self):
        result = materialize_entries({"../escape": b"x"}, source_hash="src")
        self.assertFalse(result.success); self.assertTrue(any("unsafe_member" in r for r in result.reasons))

    def test_retrieval_binds_raw_bytes_and_final_context(self):
        raw = AUTHORITY.resolve_retrieval_bytes("file", "v", 0, 1)
        rec = RetrievalEvidenceRecord("r", "a", "s", "file", "v", 0, 1, sha256(raw).hexdigest(), 1, "tool", 1, "ctx", "ctx-h")
        self.assertTrue(validate_retrieval(rec, expected_request="r", expected_attempt="a", expected_session="s", expected_source="file", expected_version="v", expected_context_id="ctx", expected_context_hash="ctx-h", authority=AUTHORITY)[0])
        forged = RetrievalEvidenceRecord("r", "a", "s", "file", "v", 0, 1, sha256(b"wrong").hexdigest(), len(b"wrong"), "tool", 1, "ctx", "ctx-h")
        self.assertFalse(validate_retrieval(forged, expected_request="r", expected_attempt="a", expected_session="s", expected_source="file", expected_version="v", expected_context_id="ctx", expected_context_hash="ctx-h", authority=AUTHORITY)[0])

    def test_wire_delivery_rejects_returned_byte_mismatch(self):
        s, c, i, items, m, p = fixture(); provider = DeterministicFakeProvider(); receipt, wire = provider.deliver(m, items); materialized = materialize_entries(items, source_hash=AUTHORITY_CONTEXT.reviewed_commit)
        ok, _ = validate_wire_delivery(
            m, materialized, wire, receipt, {"a": b"bad"},
            expected_commit=AUTHORITY_CONTEXT.reviewed_commit,
            expected_semantic_hash=wire.semantic_hash,
            authority=AUTHORITY,
        )
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

    def test_r2_summary_only_bundle_is_rejected(self):
        state = {name: True for name in admissibility_registry().predicate_ids}
        state["disposition"] = "PASS"
        self.assertFalse(evaluate_admissibility(bundle_from_state(state, AUTHORITY_CONTEXT), AUTHORITY_CONTEXT, authority=AUTHORITY).admissible)

    def test_r2_persistent_void_is_terminal_across_reload(self):
        path = Path(f"experiments/governed-platform/.exp-m-test-ledger-{uuid.uuid4().hex}.json")
        try:
            if path.exists(): path.unlink()
            first = PersistentAdmissionLedger(path).compare_and_set("a", 1, "VOID", expected_state_hash="")
            second = PersistentAdmissionLedger(path).compare_and_set("a", 1, "COMMITTED", expected_state_hash="")
            self.assertTrue(first.void); self.assertTrue(second.void); self.assertEqual(second.reasons, ("terminal_state",))
        finally:
            if path.exists(): path.unlink()

    def test_r2_admission_race_has_one_terminal_winner(self):
        path = Path(f"experiments/governed-platform/.exp-m-race-ledger-{uuid.uuid4().hex}.json")
        db = path.with_suffix(path.suffix + ".sqlite")
        ledger = PersistentAdmissionLedger(path); results = []
        def writer(disposition): results.append(ledger.compare_and_set("race", 1, disposition, expected_state_hash=""))
        workers = [threading.Thread(target=writer, args=("COMMITTED",)), threading.Thread(target=writer, args=("VOID",))]
        [w.start() for w in workers]; [w.join() for w in workers]
        self.assertEqual(len(results), 2)
        self.assertEqual(sum(not r.reasons for r in results), 1)
        self.assertTrue(all((not r.reasons) or r.reasons in (("terminal_state",), ("protected_state_generation_drift",), ("protected_state_identity_missing_or_drifted",)) for r in results))

    def test_r2_retry_lineage_is_explicit(self):
        records = (PhysicalAttemptRecord("a", "a", None, "FIRST", "r", "s", "w1", "FAILED"), PhysicalAttemptRecord("a-retry", "a", "a", "RETRY", "r", "s", "w2", "OK"))
        self.assertTrue(validate_retry_transparency(records, planned_root_ids=("a",), expected_request="r", expected_session="s")[0])
        broken = (PhysicalAttemptRecord("a-retry", "a", None, "RETRY", "r", "s", "w2", "OK"),)
        self.assertFalse(validate_retry_transparency(broken, planned_root_ids=("a",), expected_request="r", expected_session="s")[0])

    def test_r2_production_evaluator_has_no_bypass_parameter(self):
        import inspect
        self.assertNotIn("disabled_predicates", inspect.signature(evaluate_admissibility).parameters)

    def test_r2e_preflight_requires_authority_context(self):
        s, c, i, items, m, p = fixture()
        result = preflight_delivery(s, c, i, m, "r", p, items)
        self.assertFalse(result.allowed)
        self.assertIn("preflight_expectation_authority_invalid", result.reasons)

    def test_r2e_adapter_drift_is_rejected(self):
        s, c, i, items, m, p = fixture()
        p = ProviderCapabilityProfile(
            p.provider_id, p.model_id, "attacker-adapter", p.profile_hash, True,
            p.expires_at, p.supported_formats, p.max_context_bytes,
        )
        result = preflight(s, c, i, m, "r", p, items)
        self.assertFalse(result.allowed)
        self.assertTrue(
            "preflight_adapter_mismatch" in result.reasons or "adapter_version_mismatch" in result.reasons
        )

    def test_r2e_false_qualification_summary_is_rejected(self):
        s, c, i, items, m, p = fixture()
        record = ProviderCapabilityQualificationRecord(
            "plan", "profile-hash", False, True, 0, "default",
            ("a1",), ("a1",), "fake", "deterministic",
            attempt_records=(PhysicalAttemptRecord("a1", "a1", None, "FIRST", "r", "s", "wire-a1", "OK"),),
        )
        result = preflight(s, c, i, m, "r", p, items, qualification=record)
        self.assertFalse(result.allowed)
        self.assertIn("qualification_summary_not_qualified", result.reasons)

    def test_r2b_required_optional_manifest_is_exact(self):
        s, c, i, items, m, p = fixture(); extra = dict(items); extra["unknown"] = b"x"
        self.assertFalse(preflight(s, c, i, m, "r", p, extra).allowed)

    def test_r2b_materialization_derives_path_and_rejects_falsified_metadata(self):
        bad = MaterializationEntry("safe/file", "other/file", "file", b"x", None, 999, 999, 99)
        self.assertFalse(materialize_entries((bad,), source_hash="s").success)

    def test_r2b_production_profile_requires_real_plan(self):
        profile = ProviderCapabilityProfile("fake", "deterministic", "v", "hash", True, "2099-01-01T00:00:00Z", ("text",), 1000)
        plan = ProviderQualificationExecutionPlan("p", "fake", "op", ("trial",), ("confirm",), "R5_PRODUCTION")
        record = ProviderCapabilityQualificationRecord("p", "hash", True, True, 0, "op", ("trial",), ("trial",), "fake", "deterministic", attempt_records=(PhysicalAttemptRecord("trial", "trial", None, "FIRST", "r", "s", "w", "OK"),))
        ok, reasons = validate_capability(profile, plan, record, now="2025-01-01T00:00:00Z", expected_provider="fake", expected_model="deterministic", expected_operating_point="op", expected_profile_hash="hash", required_format="text", required_context_bytes=1, authority=AUTHORITY)
        self.assertFalse(ok); self.assertIn("production_confirmation_plan_too_small", reasons)

    def test_r2b_physical_attempt_duplicate_is_rejected(self):
        records = (PhysicalAttemptRecord("a", "a", None, "FIRST", "r", "s", "w", "FAILED"), PhysicalAttemptRecord("b", "a", "a", "RETRY", "r", "s", "w", "OK"))
        ok, reasons = validate_retry_transparency(records, planned_root_ids=("a",), expected_request="r", expected_session="s")
        self.assertFalse(ok); self.assertIn("physical_attempt_or_wire_duplicate", reasons)

    def test_r2b_closure_missing_execution_evidence_fails(self):
        reg = admissibility_registry()
        self.assertFalse(reg.closure(reg.predicate_ids, reg.logic_mutation_ids, declared_mutations=reg.logic_mutation_ids, executed_mutations=reg.logic_mutation_ids, killed_mutations=reg.logic_mutation_ids, declared_fixtures=reg.fixture_ids, executed_fixtures=reg.fixture_ids, executed_fixture_targets=()))

    def test_r2_empty_or_mismatched_qualification_closure_rejected(self):
        s, c, i, items, m, p = fixture()
        empty = ProviderQualificationExecutionPlan("plan", "fake", "default", (), ())
        result = preflight(s, c, i, m, "r", p, items, plan=empty, qualification=ProviderCapabilityQualificationRecord("plan", "profile-hash", True, True, 0, "default", (), (), "fake", "deterministic"))
        self.assertFalse(result.allowed); self.assertIn("qualification_sets_empty", result.reasons)

    def test_r2_typed_materialization_bounds_and_transform_registry(self):
        duplicate = (MaterializationEntry("a", "x", "file", b"a"), MaterializationEntry("b", "x", "file", b"b"))
        self.assertFalse(materialize_entries(duplicate, source_hash="s").success)
        symlink = (MaterializationEntry("link", "link", "symlink", b"", "../escape"),)
        self.assertFalse(materialize_entries(symlink, source_hash="s").success)
        self.assertFalse(materialize_entries({"a": b"a"}, source_hash="s", transform_id="unknown").success)

    def test_r2c_fixture_catalog_is_external_and_exact(self):
        reg = admissibility_registry()
        from exp_m_review_fixtures import FIXTURE_CATALOG
        self.assertEqual(set(reg.fixture_ids), {row["fixture_id"] for row in FIXTURE_CATALOG})
        self.assertEqual(dict(reg.fixture_target_map), {row["fixture_id"]: row["target_predicate_id"] for row in FIXTURE_CATALOG})

    def test_r2c_caller_interactions_cannot_satisfy_context(self):
        s, c, i, items, m, p = fixture()
        self.assertFalse(preflight_delivery(
            s, c, i, m, "r", p, items,
            context=AUTHORITY_CONTEXT, authority=AUTHORITY,
            observed_interactions=(("a", "b"),),
        ).allowed)

    def test_r2c_two_trial_production_profile_rejected(self):
        profile = ProviderCapabilityProfile("fake", "deterministic", "v", "hash", True, "2099-01-01T00:00:00Z", ("text",), 1000)
        plan = ProviderQualificationExecutionPlan("p", "fake", "op", ("a", "b"), ("c",), "R5_PRODUCTION")
        rec = ProviderCapabilityQualificationRecord("p", "hash", True, True, 0, "op", ("a", "b", "c"), ("a", "b", "c"), "fake", "deterministic", attempt_records=tuple(PhysicalAttemptRecord(x, x, None, "FIRST", "r", "s", "w", "OK") for x in ("a", "b")))
        ok, _ = validate_capability(profile, plan, rec, now="2025-01-01T00:00:00Z", expected_provider="fake", expected_model="deterministic", expected_operating_point="op", expected_profile_hash="hash", required_format="text", required_context_bytes=1, authority=AUTHORITY)
        self.assertFalse(ok)

    def test_r2d_exact_r5_298_fails_299_passes_one_failure_fails(self):
        profile = ProviderCapabilityProfile("fake", "deterministic", "v", "hash", True, "2099-01-01T00:00:00Z", ("text",), 1000)
        def run(n, failed=False):
            ids = tuple(f"c{i}" for i in range(n)); all_ids = ("explore",) + ids; plan = ProviderQualificationExecutionPlan("p", "fake", "op", ("explore",), ids, "R5_PRODUCTION", "seed", ("d1", "d2", "d3"), ("b1", "b2", "b3", "b4"), "envelope")
            attempts = tuple(PhysicalAttemptRecord(x, x, None, "FIRST", "r", "s", "w" + x, "FAILED" if failed and i == 0 else "OK", utc_day=f"d{(i % 3) + 1}", time_block=f"b{(i % 4) + 1}") for i, x in enumerate(all_ids))
            rec = ProviderCapabilityQualificationRecord("p", "hash", True, True, 1 if failed else 0, "op", all_ids, all_ids, "fake", "deterministic", attempt_records=attempts)
            return validate_capability(profile, plan, rec, now="2025-01-01T00:00:00Z", expected_provider="fake", expected_model="deterministic", expected_operating_point="op", expected_profile_hash="hash", required_format="text", required_context_bytes=1, authority=AUTHORITY)[0]
        self.assertFalse(run(298)); self.assertTrue(run(299)); self.assertFalse(run(299, True))


if __name__ == "__main__":
    unittest.main(verbosity=2)
