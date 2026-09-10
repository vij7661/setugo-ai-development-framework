from qualification_boundary_policy import (
    policy_binding,
    qualification_policy_hash,
    review_dimensions,
    review_required,
    terminal_authority_allowed,
    testing_matrix_binding,
    verify_review_dimensions,
    verify_testing_matrix_results,
)


def test_policy_binding_is_deterministic_and_nonempty():
    binding = policy_binding()
    assert binding["qualification_policy_hash"] == qualification_policy_hash()
    assert len(binding["qualification_policy_hash"]) == 64


def test_candidate_cannot_lower_governance_review_floor_with_benign_trigger():
    assert review_required(
        trigger="ROUTINE_FORMATTING",
        material_authority_transition=False,
        standard_requires_review=False,
        changed_paths=["governance-runtime/review_protocol.py"],
    )


def test_unresolved_materiality_fails_closed_to_review():
    assert review_required(
        trigger="UNRECOGNIZED_LABEL",
        unresolved_materiality=True,
    )


def test_platform_review_dimensions_are_owned_by_policy():
    dimensions = review_dimensions("GOVERNANCE_MATERIAL")
    ok, reason = verify_review_dimensions("GOVERNANCE_MATERIAL", dimensions)
    assert ok, reason


def test_candidate_cannot_delete_mandatory_dimension():
    dimensions = review_dimensions("GOVERNANCE_MATERIAL")
    dimensions = [d for d in dimensions if d["id"] != "qualification_boundary_ownership"]
    ok, reason = verify_review_dimensions("GOVERNANCE_MATERIAL", dimensions)
    assert not ok
    assert "missing platform-mandatory" in reason


def test_candidate_cannot_downgrade_mandatory_dimension():
    dimensions = review_dimensions("GOVERNANCE_MATERIAL")
    dimensions[0]["mandatory"] = False
    ok, reason = verify_review_dimensions("GOVERNANCE_MATERIAL", dimensions)
    assert not ok
    assert "rebound or weakened" in reason


def test_candidate_cannot_narrow_dimension_description():
    dimensions = review_dimensions("GOVERNANCE_MATERIAL")
    dimensions[0]["description"] = "Only inspect obvious bypasses."
    ok, reason = verify_review_dimensions("GOVERNANCE_MATERIAL", dimensions)
    assert not ok
    assert "rebound or weakened" in reason


def test_extra_dimension_may_escalate_but_not_lower_policy_floor():
    dimensions = review_dimensions("GOVERNANCE_MATERIAL")
    dimensions.append({
        "id": "extra_reviewer_question",
        "mandatory": False,
        "description": "Additional reviewer-selected exploration.",
    })
    ok, reason = verify_review_dimensions("GOVERNANCE_MATERIAL", dimensions)
    assert ok, reason


def test_testing_matrix_requires_exact_platform_binding_and_all_cases():
    binding = testing_matrix_binding()
    results = {case_id: "PASS" for case_id in binding["required_case_ids"]}
    ok, reason = verify_testing_matrix_results(binding, results)
    assert ok, reason


def test_candidate_cannot_replace_testing_matrix_with_weaker_binding():
    binding = testing_matrix_binding()
    binding["required_case_ids"] = binding["required_case_ids"][:-1]
    results = {case_id: "PASS" for case_id in binding["required_case_ids"]}
    ok, reason = verify_testing_matrix_results(binding, results)
    assert not ok
    assert "rebound" in reason


def test_missing_required_adversarial_case_blocks_testing_complete():
    binding = testing_matrix_binding()
    results = {case_id: "PASS" for case_id in binding["required_case_ids"]}
    results.pop("QO-04")
    ok, reason = verify_testing_matrix_results(binding, results)
    assert not ok
    assert "QO-04" in reason


def test_model_or_reviewer_cannot_self_appoint_terminal_authority():
    for issuer in ("MODEL", "REVIEWER", "CODING_AGENT", "CI_JOB", "ORCHESTRATOR", None):
        ok, _ = terminal_authority_allowed(
            phase="TESTING",
            action="READY_TO_BEGIN_RELEASE_QUALIFICATION",
            issuer_class=issuer,
            provenance_verified=True,
            current=True,
        )
        assert not ok


def test_testing_terminal_authority_is_narrowly_scoped():
    ok, reason = terminal_authority_allowed(
        phase="TESTING",
        action="READY_TO_BEGIN_RELEASE_QUALIFICATION",
        issuer_class="HUMAN_GOVERNANCE_OWNER",
        provenance_verified=True,
        current=True,
    )
    assert ok, reason

    for forbidden in ("DEPLOY_PRODUCTION", "MERGE_RELEASE_CANDIDATE", "BEGIN_PRODUCTION_QUALIFICATION"):
        ok, _ = terminal_authority_allowed(
            phase="TESTING",
            action=forbidden,
            issuer_class="HUMAN_GOVERNANCE_OWNER",
            provenance_verified=True,
            current=True,
        )
        assert not ok


def test_terminal_authority_requires_verified_current_provenance():
    ok, _ = terminal_authority_allowed(
        phase="TESTING",
        action="READY_TO_BEGIN_RELEASE_QUALIFICATION",
        issuer_class="HUMAN_GOVERNANCE_OWNER",
        provenance_verified=False,
        current=True,
    )
    assert not ok

    ok, _ = terminal_authority_allowed(
        phase="TESTING",
        action="READY_TO_BEGIN_RELEASE_QUALIFICATION",
        issuer_class="HUMAN_GOVERNANCE_OWNER",
        provenance_verified=True,
        current=False,
    )
    assert not ok
