"""Review-owned immutable negative fixture constructors.

This module is intentionally separate from the production predicate registry
and from the mutation runner.  It describes the semantic defect each fixture
must expose; the runner only executes these constructors.
"""
from __future__ import annotations
from copy import deepcopy
from hashlib import sha256
from typing import Any, Mapping

from exp_m_deterministic import (
    GovernanceAuthoritySnapshot, RequiredEvidenceContract,
    RequiredInteractionContract, MaterializationResult, RepresentationRecord,
    AccessibilityProofRecord, ProviderContextStateEvidence,
    WitnessProtocolQualificationRecord, SemanticContextQualificationRecord,
    WireDeliveryRecord, ReviewerProvenanceRecord, SemanticCoverageRecord,
    digest,
)

FIXTURE_CATALOG = (
    {"fixture_id": "negative:review_request_current", "target_predicate_id": "review_request_current", "constructor": "review_request_not_current", "expected_rejection": "review_request_current"},
    {"fixture_id": "negative:authority_snapshot_current", "target_predicate_id": "authority_snapshot_current", "constructor": "candidate_writable_snapshot", "expected_rejection": "authority_snapshot_current"},
    {"fixture_id": "negative:evidence_contract_closed", "target_predicate_id": "evidence_contract_closed", "constructor": "open_evidence_contract", "expected_rejection": "evidence_contract_closed"},
    {"fixture_id": "negative:interaction_contract_closed", "target_predicate_id": "interaction_contract_closed", "constructor": "open_interaction_contract", "expected_rejection": "interaction_contract_closed"},
    {"fixture_id": "negative:materialization_complete", "target_predicate_id": "materialization_complete", "constructor": "failed_materialization", "expected_rejection": "materialization_complete"},
    {"fixture_id": "negative:representation_governed", "target_predicate_id": "representation_governed", "constructor": "unqualified_representation", "expected_rejection": "representation_governed"},
    {"fixture_id": "negative:egress_authorized", "target_predicate_id": "egress_authorized", "constructor": "revoked_egress", "expected_rejection": "egress_authorized"},
    {"fixture_id": "negative:capability_current", "target_predicate_id": "capability_current", "constructor": "invalid_capability_summary", "expected_rejection": "capability_current"},
    {"fixture_id": "negative:accessibility_policy_satisfied", "target_predicate_id": "accessibility_policy_satisfied", "constructor": "invalid_accessibility_policy", "expected_rejection": "accessibility_policy_satisfied"},
    {"fixture_id": "negative:context_isolation_satisfied", "target_predicate_id": "context_isolation_satisfied", "constructor": "dirty_isolation", "expected_rejection": "context_isolation_satisfied"},
    {"fixture_id": "negative:hidden_state_policy_satisfied", "target_predicate_id": "hidden_state_policy_satisfied", "constructor": "hidden_state", "expected_rejection": "hidden_state_policy_satisfied"},
    {"fixture_id": "negative:context_state_clean", "target_predicate_id": "context_state_clean", "constructor": "dirty_context", "expected_rejection": "context_state_clean"},
    {"fixture_id": "negative:admission_fence_current", "target_predicate_id": "admission_fence_current", "constructor": "stale_fence", "expected_rejection": "admission_fence_current"},
    {"fixture_id": "negative:semantic_context_qualified", "target_predicate_id": "semantic_context_qualified", "constructor": "wrong_semantic_context", "expected_rejection": "semantic_context_qualified"},
    {"fixture_id": "negative:wire_binding_valid", "target_predicate_id": "wire_binding_valid", "constructor": "invalid_wire", "expected_rejection": "wire_binding_valid"},
    {"fixture_id": "negative:delivery_complete", "target_predicate_id": "delivery_complete", "constructor": "incomplete_delivery", "expected_rejection": "delivery_complete"},
    {"fixture_id": "negative:accessibility_proven", "target_predicate_id": "accessibility_proven", "constructor": "invalid_accessibility_proof", "expected_rejection": "accessibility_proven"},
    {"fixture_id": "negative:witness_record_current", "target_predicate_id": "witness_record_current", "constructor": "expired_witness", "expected_rejection": "witness_record_current"},
    {"fixture_id": "negative:session_retrieval_coverage", "target_predicate_id": "session_retrieval_coverage", "constructor": "invalid_retrieval", "expected_rejection": "session_retrieval_coverage"},
    {"fixture_id": "negative:prompt_isolation_current", "target_predicate_id": "prompt_isolation_current", "constructor": "expired_prompt", "expected_rejection": "prompt_isolation_current"},
    {"fixture_id": "negative:semantic_coverage", "target_predicate_id": "semantic_coverage", "constructor": "incomplete_coverage", "expected_rejection": "semantic_coverage"},
    {"fixture_id": "negative:reviewer_provenance", "target_predicate_id": "reviewer_provenance", "constructor": "untrusted_reviewer", "expected_rejection": "reviewer_provenance"},
    {"fixture_id": "negative:disposition_promotable", "target_predicate_id": "disposition_promotable", "constructor": "non_promotable_disposition", "expected_rejection": "disposition_promotable"},
)

def build_negative_fixture(base: Mapping[str, Any], predicate: str) -> dict[str, Any]:
    """Construct one independent negative fixture from a positive base."""
    state = deepcopy(dict(base))
    state["__negative_target__"] = predicate
    if predicate == "review_request_current": state["review_request"] = {"current": False, "request_id": "r"}
    elif predicate == "authority_snapshot_current": state["authority_snapshot"] = GovernanceAuthoritySnapshot("s", "1", "h", False)
    elif predicate == "evidence_contract_closed": state["evidence_contract"] = RequiredEvidenceContract("e", "s", (), non_vacuous=False)
    elif predicate == "interaction_contract_closed": state["interaction_contract"] = RequiredInteractionContract("i", "s", (), closed=False)
    elif predicate == "materialization_complete": state["materialization"] = MaterializationResult(False, {"a": b"a"}, digest({"a": sha256(b"a").hexdigest()}), "commit", "raw-v1")
    elif predicate == "representation_governed": state["representation"] = {"governed": False, "transform_id": ""}
    elif predicate == "egress_authorized": state["egress"] = {"authorized": False, "version": "1"}
    elif predicate == "capability_current": state["capability"] = {"validated": False}
    elif predicate == "accessibility_policy_satisfied": state["accessibility_policy"] = {"satisfied": False, "risk_policy_version": "r1"}
    elif predicate == "context_isolation_satisfied": state["context_isolation"] = {"satisfied": False, "transition_class": "LOWER"}
    elif predicate == "hidden_state_policy_satisfied": state["hidden_state_policy"] = {"hidden_state_allowed": True}
    elif predicate == "context_state_clean": state["context_state"] = {"clean": False, "sentinel_passed": False, "state_hash": "state"}
    elif predicate == "admission_fence_current": state["fence"] = {"current": False, "version": "1"}
    elif predicate == "semantic_context_qualified": state["semantic_context"] = {"qualified": False, "context_hash": "wrong"}
    elif predicate == "wire_binding_valid": state["wire"] = {"valid": False}
    elif predicate == "delivery_complete": state["delivery"] = {"computed_complete": False}
    elif predicate == "accessibility_proven": state["accessibility"] = {"proven": False, "challenge_id": "ch"}
    elif predicate == "witness_record_current": state["witness"] = {"validated": False}
    elif predicate == "session_retrieval_coverage": state["retrieval"] = {"validated": False, "final_context_id": "ctx"}
    elif predicate == "prompt_isolation_current": state["prompt_isolation"] = {"current": False}
    elif predicate == "semantic_coverage": state["semantic_coverage"] = {"complete": False}
    elif predicate == "reviewer_provenance": state["reviewer"] = {"trusted": False}
    elif predicate == "disposition_promotable": state["disposition"] = "CHANGES_REQUIRED"
    else: raise KeyError(predicate)
    return state
