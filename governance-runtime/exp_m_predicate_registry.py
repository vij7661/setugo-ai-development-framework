"""Platform-owned required predicate registry for EXP-M.

This module is the sole authority for the production predicate set.  Mutation
and fixture catalogs are deliberately maintained in different modules.
"""
from __future__ import annotations

PLATFORM_PREDICATE_REGISTRY = (
    {"id": "review_request_current", "validator": "validate_review_request_current"},
    {"id": "authority_snapshot_current", "validator": "validate_authority_snapshot_current"},
    {"id": "evidence_contract_closed", "validator": "validate_evidence_contract_closed"},
    {"id": "interaction_contract_closed", "validator": "validate_interaction_contract_closed"},
    {"id": "materialization_complete", "validator": "validate_materialization_complete"},
    {"id": "representation_governed", "validator": "validate_representation_governed"},
    {"id": "egress_authorized", "validator": "validate_egress_authorized"},
    {"id": "capability_current", "validator": "validate_capability_current"},
    {"id": "accessibility_policy_satisfied", "validator": "validate_accessibility_policy_satisfied"},
    {"id": "context_isolation_satisfied", "validator": "validate_context_isolation_satisfied"},
    {"id": "hidden_state_policy_satisfied", "validator": "validate_hidden_state_policy_satisfied"},
    {"id": "context_state_clean", "validator": "validate_context_state_clean"},
    {"id": "admission_fence_current", "validator": "validate_admission_fence_current"},
    {"id": "semantic_context_qualified", "validator": "validate_semantic_context_qualified"},
    {"id": "wire_binding_valid", "validator": "validate_wire_binding_valid"},
    {"id": "delivery_complete", "validator": "validate_delivery_complete"},
    {"id": "accessibility_proven", "validator": "validate_accessibility_proven"},
    {"id": "witness_record_current", "validator": "validate_witness_record_current"},
    {"id": "session_retrieval_coverage", "validator": "validate_session_retrieval_coverage"},
    {"id": "prompt_isolation_current", "validator": "validate_prompt_isolation_current"},
    {"id": "semantic_coverage", "validator": "validate_semantic_coverage"},
    {"id": "reviewer_provenance", "validator": "validate_reviewer_provenance"},
    {"id": "disposition_promotable", "validator": "validate_disposition_promotable"},
)

def required_predicate_ids() -> tuple[str, ...]:
    return tuple(item["id"] for item in PLATFORM_PREDICATE_REGISTRY)
