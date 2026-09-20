"""Test-only EXP-M fixture adapters.

These adapters are outside the production governor.  Context derivation from a
state mapping is retained only to construct adversarial fixtures; a context
created here is never authority-bearing and production admissibility rejects it.
"""
from __future__ import annotations
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any, Mapping
from exp_m_deterministic import *

def context_from_state(state: Mapping[str, Any]) -> PredicateContext:
    """Test/fixture adapter; production callers must supply frozen context explicitly."""
    return PredicateContext(
        request_id=str(state.get("expected_request_id", "r")),
        attempt_id=str(state.get("expected_attempt_id", "a")),
        session_id=str(state.get("expected_session_id", "s")),
        reviewed_commit=str(state.get("expected_reviewed_commit", "0" * 40)),
        authority_snapshot_id=str(state.get("expected_authority_snapshot_id", getattr(state.get("authority_snapshot"), "snapshot_id", ""))),
        authority_snapshot_hash=str(state.get("expected_authority_snapshot_hash", getattr(state.get("authority_snapshot"), "content_hash", ""))),
        authority_version=str(state.get("expected_authority_version", getattr(state.get("authority_snapshot"), "version", ""))),
        expected_provider=str(state.get("expected_provider", "fake")), expected_model=str(state.get("expected_model", "deterministic")),
        expected_adapter=str(state.get("expected_adapter", "adapter")), expected_operating_point=str(state.get("expected_operating_point", "default")),
        expected_profile_hash=str(state.get("expected_profile_hash", "profile-hash")), expected_egress_version=str(state.get("expected_egress_version", "1")),
        transition_class=str(state.get("transition_class", "LOWER")), fence_version=str(state.get("expected_fence_version", "1")),
        prompt_provider=str(state.get("prompt_provider", "fake")), prompt_mode=str(state.get("prompt_mode", "inline")),
        witness_provider=str(state.get("witness_provider", "fake")), witness_mode=str(state.get("witness_mode", "inline")), witness_prompt_mode=str(state.get("witness_prompt_mode", "prompt")),
        retrieval_source=str(state.get("retrieval_source", "file")), retrieval_version=str(state.get("retrieval_version", "v")),
        final_context_id=str(state.get("final_context_id", "ctx")), final_context_hash=str(state.get("final_context_hash", "ctx-h")),
        max_context_bytes=int(state.get("max_context_bytes", 1_000_000)), predicate_registry_version=str(state.get("predicate_registry_version", "2")),
        reviewed_tree=str(state.get("expected_reviewed_tree", "")),
        promotable_dispositions=tuple(state.get("promotable_dispositions", ("PASS",))),
        expected_semantic_hash=str(state.get("expected_semantic_hash", "")),
        expected_transition_class=str(state.get("expected_transition_class", state.get("transition_class", "LOWER"))),
        expected_fence_version=str(state.get("expected_fence_version", "1")),
        expected_witness_answer_hash=str(state.get("expected_witness_answer_hash", digest(state.get("witness_expected_answer", "answer")))),
        expected_challenge_id=str(state.get("expected_challenge_id", "challenge")),
        expected_reviewer_policy_hash=str(state.get("expected_reviewer_policy_hash", "policy")),
        expected_context_state_hash=str(state.get("expected_context_state_hash", "")),
        expected_fence_state_hash=str(state.get("expected_fence_state_hash", digest({"fence_id": "fence", "version": "1", "current": True}))),
        expected_qualification_profile=str(state.get("expected_qualification_profile", "TEST_PROFILE")),
    )


def bundle_from_state(state: Mapping[str, Any], context: PredicateContext) -> EvidenceBundle:
    """Test-only fixture adapter. Production callers construct typed bundles directly."""
    out = dict(state)
    if "review_request" not in state or not isinstance(state.get("review_request"), Mapping):
        return EvidenceBundle(out)
    request_id, attempt_id, session_id = context.request_id, context.attempt_id, context.session_id
    if "interaction_contract" in state and "final_context_interactions" not in out and isinstance(state.get("interaction_contract"), RequiredInteractionContract):
        out["final_context_interactions"] = FinalContextInteractionEvidence(request_id, session_id, context.final_context_hash, tuple(sorted({item for interaction in state["interaction_contract"].interactions for item in interaction})), tuple(state["interaction_contract"].interactions), True, digest({"context_id": context.final_context_id, "source_hash": context.reviewed_commit, "members": tuple(sorted({item for interaction in state["interaction_contract"].interactions for item in interaction})), "assembly": "trusted-final-context-v1"}))
    reviewed_commit = context.reviewed_commit
    profile = ProviderCapabilityProfile("fake", "deterministic", "adapter", "profile-hash", True, supported_formats=("text",), max_context_bytes=1_000_000)
    plan = ProviderQualificationExecutionPlan("plan", "fake", "default", ("a1",), ("a1",))
    record = ProviderCapabilityQualificationRecord("plan", "profile-hash", True, True, 0, "default", ("a1",), ("a1",), "fake", "deterministic", attempt_records=(PhysicalAttemptRecord("a1", "a1", None, "FIRST", request_id, session_id, "wire-a1", "OK"),))
    out.setdefault("capability_profile", profile); out.setdefault("qualification_plan", plan); out.setdefault("capability_record", record)
    if not isinstance(out.get("capability_profile"), ProviderCapabilityProfile): out["capability_profile"] = profile
    if not isinstance(out.get("qualification_plan"), ProviderQualificationExecutionPlan): out["qualification_plan"] = plan
    if not isinstance(out.get("capability_record"), ProviderCapabilityQualificationRecord): out["capability_record"] = record
    if isinstance(state.get("capability"), Mapping) and state["capability"].get("validated") is False: out["capability_record"] = ProviderCapabilityQualificationRecord("bad", "bad", False, False)
    channel_observations = tuple({"channel": channel, "observed_hash": "state", "expected_hash": "state", "readable": True, "fenced": True, "generation": 1, "observer_id": "platform-context-observer"} for channel in ("memory", "config"))
    isolation = ContextIsolationVerdict(ProviderContextIsolationPolicy("policy", "COMPLETE_READABLE_FENCED_STATE"), ProviderContextStateEvidence(True, ("memory", "config"), True, "state", channel_observations=channel_observations), AdmissionFenceRecord("fence", "1", True), "LOWER", ("memory", "config"))
    if isinstance(state.get("context_isolation"), Mapping) and state["context_isolation"].get("satisfied") is False:
        isolation = ContextIsolationVerdict(ProviderContextIsolationPolicy("", "INVALID"), isolation.evidence, isolation.fence, "LOWER", isolation.required_channels)
    if isinstance(state.get("hidden_state_policy"), Mapping) and state["hidden_state_policy"].get("hidden_state_allowed") is True:
        isolation = ContextIsolationVerdict(ProviderContextIsolationPolicy("policy", "COMPLETE_READABLE_FENCED_STATE", True), isolation.evidence, isolation.fence, "LOWER", isolation.required_channels)
    if isinstance(state.get("context_state"), Mapping) and (state["context_state"].get("clean") is False or state["context_state"].get("sentinel_passed") is False):
        cs = state["context_state"]; channels = tuple(cs.get("observable_channels", ()))
        isolation = ContextIsolationVerdict(isolation.policy, ProviderContextStateEvidence(bool(cs.get("clean")), channels, bool(cs.get("sentinel_passed")), str(cs.get("state_hash", "")), channel_observations=tuple({"channel": c, "observed_hash": "wrong", "expected_hash": "state", "readable": True, "fenced": False, "generation": 1, "observer_id": "platform-context-observer"} for c in channels)), isolation.fence, "LOWER", isolation.required_channels)
    if isinstance(state.get("fence"), Mapping) and state["fence"].get("current") is False:
        isolation = ContextIsolationVerdict(isolation.policy, isolation.evidence, AdmissionFenceRecord("fence", str(state["fence"].get("version", "")), False), "LOWER", isolation.required_channels)
    out["context_isolation_verdict"] = isolation
    if isinstance(state.get("accessibility_policy"), Mapping) and state["accessibility_policy"].get("satisfied") is False:
        out["accessibility_policy_record"] = ProviderAccessibilityRiskPolicy("LOWER", "invalid", True, False)
    elif not isinstance(out.get("accessibility_policy_record"), ProviderAccessibilityRiskPolicy): out["accessibility_policy_record"] = ProviderAccessibilityRiskPolicy("LOWER", "inline-deterministic", True, False)
    challenge = WitnessChallengeEvidence("challenge", "slice", "slice-hash", digest("answer"), "fake", "inline", "prompt", digest("answer"), len("answer"), "ctx", 10, 16)
    out.setdefault("witness_challenge", challenge); out.setdefault("witness_expected_answer", "answer"); out.setdefault("witness_response", "answer"); out.setdefault("witness_challenge_text", "extract token")
    if isinstance(state.get("witness"), Mapping) and state["witness"].get("validated") is False:
        out["witness"] = WitnessProtocolQualificationRecord("w", "fake", "inline", 100, False, "prompt", "2000-01-01T00:00:00Z")
    else:
        out.setdefault("witness", WitnessProtocolQualificationRecord("w", "fake", "inline", 100, True, "prompt", "2099-01-01T00:00:00Z"))
    if isinstance(state.get("prompt_isolation"), Mapping) and state["prompt_isolation"].get("current") is False:
        out["prompt_isolation"] = PromptIsolationQualificationRecord("prompt", "fake", "inline", False, "2000-01-01T00:00:00Z")
    if isinstance(state.get("semantic_context"), Mapping) and state["semantic_context"].get("qualified") is False:
        out["semantic_context"] = SemanticContextQualificationRecord("ctx", "wrong", False, "")
    elif not isinstance(out.get("semantic_context"), SemanticContextQualificationRecord): out["semantic_context"] = SemanticContextQualificationRecord("ctx", "ctx-h", True, reviewed_commit, b"", digest({"context_id": "ctx", "source_hash": reviewed_commit, "members": ("a",), "assembly": "trusted-final-context-v1"}), ("a",))
    if isinstance(state.get("semantic_coverage"), Mapping) and state["semantic_coverage"].get("complete") is False:
        out["semantic_coverage"] = SemanticCoverageRecord("cov", "ctx", False, "", "", "wrong")
    elif not isinstance(out.get("semantic_coverage"), SemanticCoverageRecord) or not out["semantic_coverage"].source_hash:
        out["semantic_coverage"] = SemanticCoverageRecord("cov", "ctx", True, reviewed_commit, "coverage-h", "ctx-h", ("a",), "coverage-v1", "")
    raw_items = {"a": b"a"}; manifest = EvidenceDeliveryManifest.freeze(request_id, reviewed_commit, raw_items); materialized = materialize_entries(raw_items, source_hash=reviewed_commit)
    provider = DeterministicFakeProvider(); receipt, wire = provider.deliver(manifest, raw_items)
    out["manifest"] = manifest
    if isinstance(state.get("delivery"), Mapping) and (state["delivery"].get("computed_complete") is False or state["delivery"].get("complete") is False): out["delivery"] = DeliveryCompletenessResult(False)
    if isinstance(state.get("wire"), Mapping) and state["wire"].get("valid") is False: out["wire"] = None
    if not (isinstance(state.get("materialization"), MaterializationResult) and state["materialization"].success is False):
        out["materialization"] = materialized
    if isinstance(state.get("representation"), Mapping) and state["representation"].get("governed") is False:
        out["representation"] = None
    else:
        out["representation"] = RepresentationRecord("raw-v1", "1", digest({"transform_id": "raw-v1", "version": "1", "registry": QUALIFIED_TRANSFORMS["raw-v1"]}), QUALIFIED_TRANSFORMS["raw-v1"], manifest.manifest_hash, materialized.representation_hash, digest({"parameters": "raw"}), digest({"coverage": "raw", "source": manifest.manifest_hash}))
    contract = out.get("evidence_contract"); interaction_contract = out.get("interaction_contract")
    required_hash = digest({"required": getattr(contract, "required_ids", ()), "optional": getattr(contract, "optional_ids", ()), "interactions": getattr(interaction_contract, "interactions", ())})
    coverage_hash = digest({"algorithm": "coverage-v1", "required": getattr(contract, "required_ids", ()), "interactions": getattr(interaction_contract, "interactions", ()), "evidence_ids": tuple(sorted(manifest.items)), "source_hash": reviewed_commit, "context_hash": context.final_context_hash})
    if not (isinstance(state.get("semantic_coverage"), Mapping) and state["semantic_coverage"].get("complete") is False):
        out["semantic_coverage"] = SemanticCoverageRecord("cov", context.final_context_id, True, reviewed_commit, coverage_hash, context.final_context_hash, tuple(sorted(manifest.items)), "coverage-v1", required_hash)
    out.setdefault("returned_items", raw_items); out["receipt"] = receipt
    if not (isinstance(state.get("wire"), Mapping) and state["wire"].get("valid") is False): out["wire"] = wire
    if isinstance(state.get("accessibility"), Mapping) and state["accessibility"].get("proven") is False:
        out["accessibility"] = AccessibilityProofRecord("proof", "challenge", "fake", "inline-deterministic", "ctx", False, "inline-deterministic", "LOWER", "")
    elif not isinstance(out.get("accessibility"), AccessibilityProofRecord) or not out["accessibility"].evidence_hash:
        out["accessibility"] = AccessibilityProofRecord("proof", "challenge", "fake", "inline-deterministic", "ctx", True, "inline-deterministic", "LOWER", digest(challenge), digest({"challenge": challenge, "context_id": "ctx", "provider": "fake", "policy": "LOWER"}))
    if isinstance(state.get("reviewer"), Mapping) and state["reviewer"].get("trusted") is False:
        out["reviewer"] = ReviewerProvenanceRecord("reviewer", "", False, "")
    elif not isinstance(out.get("reviewer"), ReviewerProvenanceRecord) or not out["reviewer"].authorization_source:
        out["reviewer"] = ReviewerProvenanceRecord("reviewer", "policy", True, "trusted-review-artifact")
    return EvidenceBundle(out)


PREDICATES = (
    "review_request_current", "authority_snapshot_current", "evidence_contract_closed",
    "interaction_contract_closed", "materialization_complete", "representation_governed",
    "egress_authorized", "capability_current", "accessibility_policy_satisfied",
    "context_isolation_satisfied", "hidden_state_policy_satisfied", "context_state_clean",
    "admission_fence_current", "semantic_context_qualified", "wire_binding_valid",
    "delivery_complete", "accessibility_proven", "witness_record_current",
    "session_retrieval_coverage", "prompt_isolation_current", "semantic_coverage",
    "reviewer_provenance", "disposition_promotable",
)

# These are intentionally independent declarations.  They are not derived
# from one shared tuple so closure can detect omissions and aliases.
PREDICATE_DEFINITIONS = tuple({"id": p, "validator": f"validate_{p}"} for p in PREDICATES)
LOGIC_MUTATION_TARGETS = (
    "review_request_current", "authority_snapshot_current", "evidence_contract_closed",
    "interaction_contract_closed", "materialization_complete", "representation_governed",
    "egress_authorized", "capability_current", "accessibility_policy_satisfied",
    "context_isolation_satisfied", "hidden_state_policy_satisfied", "context_state_clean",
    "admission_fence_current", "semantic_context_qualified", "wire_binding_valid",
    "delivery_complete", "accessibility_proven", "witness_record_current",
    "session_retrieval_coverage", "prompt_isolation_current", "semantic_coverage",
    "reviewer_provenance", "disposition_promotable",
)
# Independent, review-owned catalogs.  These are intentionally declared in a
# separate block rather than generated from the production validator map.
INDEPENDENT_MUTATION_CATALOG = (
    {"id": "negative:review_request_current", "target": "review_request_current"},
    {"id": "negative:authority_snapshot_current", "target": "authority_snapshot_current"},
    {"id": "negative:evidence_contract_closed", "target": "evidence_contract_closed"},
    {"id": "negative:interaction_contract_closed", "target": "interaction_contract_closed"},
    {"id": "negative:materialization_complete", "target": "materialization_complete"},
    {"id": "negative:representation_governed", "target": "representation_governed"},
    {"id": "negative:egress_authorized", "target": "egress_authorized"},
    {"id": "negative:capability_current", "target": "capability_current"},
    {"id": "negative:accessibility_policy_satisfied", "target": "accessibility_policy_satisfied"},
    {"id": "negative:context_isolation_satisfied", "target": "context_isolation_satisfied"},
    {"id": "negative:hidden_state_policy_satisfied", "target": "hidden_state_policy_satisfied"},
    {"id": "negative:context_state_clean", "target": "context_state_clean"},
    {"id": "negative:admission_fence_current", "target": "admission_fence_current"},
    {"id": "negative:semantic_context_qualified", "target": "semantic_context_qualified"},
    {"id": "negative:wire_binding_valid", "target": "wire_binding_valid"},
    {"id": "negative:delivery_complete", "target": "delivery_complete"},
    {"id": "negative:accessibility_proven", "target": "accessibility_proven"},
    {"id": "negative:witness_record_current", "target": "witness_record_current"},
    {"id": "negative:session_retrieval_coverage", "target": "session_retrieval_coverage"},
    {"id": "negative:prompt_isolation_current", "target": "prompt_isolation_current"},
    {"id": "negative:semantic_coverage", "target": "semantic_coverage"},
    {"id": "negative:reviewer_provenance", "target": "reviewer_provenance"},
    {"id": "negative:disposition_promotable", "target": "disposition_promotable"},
)
# Review-owned negative fixtures are independently declared.  They are not
# aliases of the mutation catalog and each names its immutable constructor and
# rejection expectation.
INDEPENDENT_FIXTURE_CATALOG = (
    {"fixture_id": "negative:review_request_current", "target_predicate_id": "review_request_current", "constructor": "fixture_review_request_not_current", "expected_rejection": "review_request_current"},
    {"fixture_id": "negative:authority_snapshot_current", "target_predicate_id": "authority_snapshot_current", "constructor": "fixture_candidate_writable_snapshot", "expected_rejection": "authority_snapshot_current"},
    {"fixture_id": "negative:evidence_contract_closed", "target_predicate_id": "evidence_contract_closed", "constructor": "fixture_open_evidence_contract", "expected_rejection": "evidence_contract_closed"},
    {"fixture_id": "negative:interaction_contract_closed", "target_predicate_id": "interaction_contract_closed", "constructor": "fixture_open_interaction_contract", "expected_rejection": "interaction_contract_closed"},
    {"fixture_id": "negative:materialization_complete", "target_predicate_id": "materialization_complete", "constructor": "fixture_failed_materialization", "expected_rejection": "materialization_complete"},
    {"fixture_id": "negative:representation_governed", "target_predicate_id": "representation_governed", "constructor": "fixture_unqualified_representation", "expected_rejection": "representation_governed"},
    {"fixture_id": "negative:egress_authorized", "target_predicate_id": "egress_authorized", "constructor": "fixture_revoked_egress", "expected_rejection": "egress_authorized"},
    {"fixture_id": "negative:capability_current", "target_predicate_id": "capability_current", "constructor": "fixture_expired_capability", "expected_rejection": "capability_current"},
    {"fixture_id": "negative:accessibility_policy_satisfied", "target_predicate_id": "accessibility_policy_satisfied", "constructor": "fixture_wrong_accessibility_policy", "expected_rejection": "accessibility_policy_satisfied"},
    {"fixture_id": "negative:context_isolation_satisfied", "target_predicate_id": "context_isolation_satisfied", "constructor": "fixture_dirty_context", "expected_rejection": "context_isolation_satisfied"},
    {"fixture_id": "negative:hidden_state_policy_satisfied", "target_predicate_id": "hidden_state_policy_satisfied", "constructor": "fixture_hidden_state", "expected_rejection": "hidden_state_policy_satisfied"},
    {"fixture_id": "negative:context_state_clean", "target_predicate_id": "context_state_clean", "constructor": "fixture_dirty_context_state", "expected_rejection": "context_state_clean"},
    {"fixture_id": "negative:admission_fence_current", "target_predicate_id": "admission_fence_current", "constructor": "fixture_stale_fence", "expected_rejection": "admission_fence_current"},
    {"fixture_id": "negative:semantic_context_qualified", "target_predicate_id": "semantic_context_qualified", "constructor": "fixture_wrong_context_hash", "expected_rejection": "semantic_context_qualified"},
    {"fixture_id": "negative:wire_binding_valid", "target_predicate_id": "wire_binding_valid", "constructor": "fixture_wrong_wire", "expected_rejection": "wire_binding_valid"},
    {"fixture_id": "negative:delivery_complete", "target_predicate_id": "delivery_complete", "constructor": "fixture_incomplete_delivery", "expected_rejection": "delivery_complete"},
    {"fixture_id": "negative:accessibility_proven", "target_predicate_id": "accessibility_proven", "constructor": "fixture_wrong_accessibility_evidence", "expected_rejection": "accessibility_proven"},
    {"fixture_id": "negative:witness_record_current", "target_predicate_id": "witness_record_current", "constructor": "fixture_expired_witness", "expected_rejection": "witness_record_current"},
    {"fixture_id": "negative:session_retrieval_coverage", "target_predicate_id": "session_retrieval_coverage", "constructor": "fixture_wrong_retrieval_session", "expected_rejection": "session_retrieval_coverage"},
    {"fixture_id": "negative:prompt_isolation_current", "target_predicate_id": "prompt_isolation_current", "constructor": "fixture_expired_prompt_isolation", "expected_rejection": "prompt_isolation_current"},
    {"fixture_id": "negative:semantic_coverage", "target_predicate_id": "semantic_coverage", "constructor": "fixture_incomplete_semantic_coverage", "expected_rejection": "semantic_coverage"},
    {"fixture_id": "negative:reviewer_provenance", "target_predicate_id": "reviewer_provenance", "constructor": "fixture_untrusted_reviewer", "expected_rejection": "reviewer_provenance"},
    {"fixture_id": "negative:disposition_promotable", "target_predicate_id": "disposition_promotable", "constructor": "fixture_non_promotable_disposition", "expected_rejection": "disposition_promotable"},
)
FIXTURE_IDS = tuple(item["fixture_id"] for item in INDEPENDENT_FIXTURE_CATALOG)
