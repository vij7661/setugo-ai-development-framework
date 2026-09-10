from qualification_boundary_policy import (
    _issue_authority_binding_for_platform_ingress,
    phase_disposition,
    verify_authority_binding,
)

CANDIDATE_SHA = "a" * 40


def test_candidate_callable_module_cannot_mint_privileged_authority_binding():
    binding = _issue_authority_binding_for_platform_ingress(
        candidate_sha=CANDIDATE_SHA,
        authority_class="INDEPENDENT_GOVERNANCE_ADJUDICATOR",
        decision_scope="REVIEW_FINDING_ADJUDICATION",
        evidence_ref="candidate-invented-evidence",
    )
    ok, _ = verify_authority_binding(
        binding,
        candidate_sha=CANDIDATE_SHA,
        required_authority_class="INDEPENDENT_GOVERNANCE_ADJUDICATOR",
        required_scope="REVIEW_FINDING_ADJUDICATION",
    )
    assert not ok, "candidate-callable issuer minted a verifier-accepted privileged binding"


def test_contradictory_legacy_phase_label_cannot_coexist_with_governed_rule_id():
    disposition, _ = phase_disposition(
        current_phase="TESTING",
        violated_rule_id="TESTING_QUALIFICATION_BOUNDARY_OWNERSHIP",
        violated_contract_phase="RELEASE",
        material=True,
    )
    assert disposition == "REQUIREMENT_UNRESOLVED", (
        "contradictory caller phase label was silently ignored instead of failing closed"
    )
