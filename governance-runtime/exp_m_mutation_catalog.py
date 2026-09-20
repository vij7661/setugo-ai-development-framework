"""Independently maintained mutation catalog for EXP-M R2C."""
from __future__ import annotations

MUTATION_CATALOG = tuple(
    {"mutation_id": f"negative:{predicate}", "target_predicate_id": predicate,
     "mutation_operator_id": f"disable_exact_guard:{predicate}",
     "expected_false_green_class": "single_predicate_guard_bypass"}
    for predicate in (
        "review_request_current", "authority_snapshot_current", "evidence_contract_closed",
        "interaction_contract_closed", "materialization_complete", "representation_governed",
        "egress_authorized", "capability_current", "accessibility_policy_satisfied",
        "context_isolation_satisfied", "hidden_state_policy_satisfied", "context_state_clean",
        "admission_fence_current", "semantic_context_qualified", "wire_binding_valid",
        "delivery_complete", "accessibility_proven", "witness_record_current",
        "session_retrieval_coverage", "prompt_isolation_current", "semantic_coverage",
        "reviewer_provenance", "disposition_promotable"))

def mutation_target_ids() -> tuple[str, ...]:
    return tuple(item["target_predicate_id"] for item in MUTATION_CATALOG)
