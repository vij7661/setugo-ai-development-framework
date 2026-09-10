from qualification_boundary_policy import (
    acceptance_boundary_change_allowed,
    acceptance_boundary_record,
    phase_disposition,
    policy_binding,
    preregistration_required,
    qualification_policy_hash,
    review_dimensions,
    review_required,
    reviewer_finding_adjudication_allowed,
    root_cause_classification_allowed,
    terminal_authority_allowed,
    testing_matrix_binding,
    verify_review_dimensions,
    verify_testing_matrix_results,
)


def test_policy_binding_is_deterministic_and_nonempty():
    binding = policy_binding()
    assert binding["qualification_policy_hash"] == qualification_policy_hash()
    assert len(binding["qualification_policy_hash"]) == 64
    assert binding["qualification_policy_version"] == 2


def test_candidate_cannot_lower_governance_review_floor_with_benign_trigger():
    assert review_required(
        trigger="ROUTINE_FORMATTING",
        material_authority_transition=False,
        standard_requires_review=False,
        changed_paths=["governance-runtime/review_protocol.py"],
    )


def test_unresolved_materiality_fails_closed_to_review():
    assert review_required(trigger="UNRECOGNIZED_LABEL", unresolved_materiality=True)


def test_platform_review_dimensions_are_owned_by_policy():
    dimensions = review_dimensions("GOVERNANCE_MATERIAL")
    ok, reason = verify_review_dimensions("GOVERNANCE_MATERIAL", dimensions)
    assert ok, reason


def test_candidate_cannot_delete_or_downgrade_mandatory_dimension():
    dimensions = review_dimensions("GOVERNANCE_MATERIAL")
    deleted = [d for d in dimensions if d["id"] != "qualification_boundary_ownership"]
    ok, reason = verify_review_dimensions("GOVERNANCE_MATERIAL", deleted)
    assert not ok and "missing platform-mandatory" in reason

    dimensions[0]["mandatory"] = False
    ok, reason = verify_review_dimensions("GOVERNANCE_MATERIAL", dimensions)
    assert not ok and "rebound or weakened" in reason


def test_candidate_cannot_narrow_dimension_description():
    dimensions = review_dimensions("GOVERNANCE_MATERIAL")
    dimensions[0]["description"] = "Only inspect obvious bypasses."
    ok, reason = verify_review_dimensions("GOVERNANCE_MATERIAL", dimensions)
    assert not ok and "rebound or weakened" in reason


def test_extra_dimension_may_escalate_but_not_lower_policy_floor():
    dimensions = review_dimensions("GOVERNANCE_MATERIAL")
    dimensions.append({"id": "extra", "mandatory": False, "description": "extra scrutiny"})
    ok, reason = verify_review_dimensions("GOVERNANCE_MATERIAL", dimensions)
    assert ok, reason


def test_testing_matrix_requires_exact_platform_binding_and_all_eight_cases():
    binding = testing_matrix_binding()
    assert binding["required_case_ids"] == [f"QO-0{i}" for i in range(1, 9)]
    results = {case_id: "PASS" for case_id in binding["required_case_ids"]}
    ok, reason = verify_testing_matrix_results(binding, results)
    assert ok, reason


def test_candidate_cannot_replace_testing_matrix_with_weaker_binding():
    binding = testing_matrix_binding()
    binding["required_case_ids"] = binding["required_case_ids"][:-1]
    results = {case_id: "PASS" for case_id in binding["required_case_ids"]}
    ok, reason = verify_testing_matrix_results(binding, results)
    assert not ok and "rebound" in reason


def test_missing_any_remaining_ownership_case_blocks_testing_complete():
    for missing in ("QO-05", "QO-06", "QO-07", "QO-08"):
        binding = testing_matrix_binding()
        results = {case_id: "PASS" for case_id in binding["required_case_ids"]}
        results.pop(missing)
        ok, reason = verify_testing_matrix_results(binding, results)
        assert not ok and missing in reason


def test_platform_not_candidate_decides_preregistration_floor():
    assert preregistration_required(artifact_type="FALSIFICATION_CONTRACT", candidate_override=False)
    assert not preregistration_required(artifact_type="README", candidate_override=False)
    assert preregistration_required(artifact_type="README", candidate_override=True)


def test_exposed_acceptance_boundary_cannot_be_rewritten_after_first_exposure():
    original = acceptance_boundary_record(
        artifact_type="FALSIFICATION_CONTRACT",
        artifact_sha="a" * 40,
        boundary_hash="b" * 64,
        approved_by="HUMAN_GOVERNANCE_OWNER",
        exposed=True,
    )
    proposed = {**original, "boundary_hash": "c" * 64}
    ok, reason = acceptance_boundary_change_allowed(original=original, proposed=proposed)
    assert not ok and "immutable" in reason


def test_candidate_cannot_approve_its_own_acceptance_boundary():
    try:
        acceptance_boundary_record(
            artifact_type="FALSIFICATION_CONTRACT",
            artifact_sha="a" * 40,
            boundary_hash="b" * 64,
            approved_by="CANDIDATE_IMPLEMENTATION",
        )
    except ValueError as exc:
        assert "governance-owner" in str(exc)
    else:
        raise AssertionError("candidate self-approval unexpectedly accepted")


def test_material_root_cause_requires_independent_adjudicator_and_bound_evidence():
    for role in ("CANDIDATE_IMPLEMENTATION", "REVIEWER", "CODING_AGENT", "ORCHESTRATOR"):
        ok, _ = root_cause_classification_allowed(
            classification="CODE_DEFECT",
            material=True,
            classifier_role=role,
            independent_evidence_bound=True,
        )
        assert not ok

    ok, _ = root_cause_classification_allowed(
        classification="CODE_DEFECT",
        material=True,
        classifier_role="INDEPENDENT_GOVERNANCE_ADJUDICATOR",
        independent_evidence_bound=False,
    )
    assert not ok

    ok, reason = root_cause_classification_allowed(
        classification="CODE_DEFECT",
        material=True,
        classifier_role="INDEPENDENT_GOVERNANCE_ADJUDICATOR",
        independent_evidence_bound=True,
    )
    assert ok, reason


def test_candidate_or_reviewer_cannot_terminally_adjudicate_review_finding():
    for adjudicator in ("CANDIDATE_IMPLEMENTATION", "REVIEWER_R2"):
        ok, _ = reviewer_finding_adjudication_allowed(
            adjudicator_role=adjudicator,
            candidate_role="CANDIDATE_IMPLEMENTATION",
            reviewer_role="REVIEWER_R2",
            exact_sha_bound=True,
            raw_finding_preserved=True,
        )
        assert not ok

    ok, reason = reviewer_finding_adjudication_allowed(
        adjudicator_role="INDEPENDENT_GOVERNANCE_ADJUDICATOR",
        candidate_role="CANDIDATE_IMPLEMENTATION",
        reviewer_role="REVIEWER_R2",
        exact_sha_bound=True,
        raw_finding_preserved=True,
    )
    assert ok, reason


def test_review_adjudication_requires_exact_sha_and_raw_finding_preservation():
    for exact_sha, preserved in ((False, True), (True, False)):
        ok, _ = reviewer_finding_adjudication_allowed(
            adjudicator_role="INDEPENDENT_GOVERNANCE_ADJUDICATOR",
            candidate_role="CANDIDATE_IMPLEMENTATION",
            reviewer_role="REVIEWER_R2",
            exact_sha_bound=exact_sha,
            raw_finding_preserved=preserved,
        )
        assert not ok


def test_candidate_cannot_defer_current_testing_contract_defect():
    disposition, _ = phase_disposition(
        current_phase="TESTING",
        violated_contract_phase="TESTING",
        material=True,
    )
    assert disposition == "BLOCK_TESTING"


def test_only_later_phase_contract_defects_are_deferred():
    disposition, _ = phase_disposition(
        current_phase="TESTING",
        violated_contract_phase="RELEASE",
        material=True,
    )
    assert disposition == "DEFERRED_TO_RELEASE"

    disposition, _ = phase_disposition(
        current_phase="TESTING",
        violated_contract_phase="PRODUCTION",
        material=True,
    )
    assert disposition == "DEFERRED_TO_PRODUCTION"


def test_uncertain_phase_applicability_cannot_be_silently_deferred():
    disposition, _ = phase_disposition(
        current_phase="TESTING",
        violated_contract_phase=None,
        material=True,
        uncertainty=True,
    )
    assert disposition == "REQUIREMENT_UNRESOLVED"


def test_model_or_reviewer_cannot_self_appoint_terminal_authority():
    for issuer in ("MODEL", "REVIEWER", "CODING_AGENT", "CI_JOB", "ORCHESTRATOR", "PLATFORM_POLICY", "HUMAN", None):
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
    for verified, current in ((False, True), (True, False)):
        ok, _ = terminal_authority_allowed(
            phase="TESTING",
            action="READY_TO_BEGIN_RELEASE_QUALIFICATION",
            issuer_class="HUMAN_GOVERNANCE_OWNER",
            provenance_verified=verified,
            current=current,
        )
        assert not ok
