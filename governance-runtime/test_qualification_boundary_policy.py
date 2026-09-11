from qualification_boundary_policy import (
    _issue_authority_binding_for_platform_ingress,
    acceptance_boundary_change_allowed,
    acceptance_boundary_record,
    build_unsigned_manual_attestation,
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
    verify_authority_binding,
    verify_review_dimensions,
    verify_testing_matrix_results,
)

CANDIDATE_SHA = "a" * 40


def _untrusted_binding(authority_class, scope):
    return _issue_authority_binding_for_platform_ingress(
        candidate_sha=CANDIDATE_SHA,
        authority_class=authority_class,
        decision_scope=scope,
        evidence_ref="candidate-invented",
    )


def test_policy_binding_is_deterministic_and_nonempty():
    binding = policy_binding()
    assert binding["qualification_policy_hash"] == qualification_policy_hash()
    assert len(binding["qualification_policy_hash"]) == 64
    assert binding["qualification_policy_version"] == 7


def test_candidate_cannot_lower_governance_review_floor_with_benign_trigger():
    assert review_required(trigger="ROUTINE_FORMATTING", changed_paths=["governance-runtime/review_protocol.py"])


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


def test_unsigned_attestation_builder_does_not_create_authority():
    attestation = build_unsigned_manual_attestation(
        candidate_sha=CANDIDATE_SHA,
        authority_class="HUMAN_GOVERNANCE_OWNER",
        decision_scope="ACCEPTANCE_BOUNDARY_APPROVAL",
        evidence_ref="manual-review:pending",
    )
    ok, _ = verify_authority_binding(
        {"attestation": attestation, "signature_b64": ""},
        candidate_sha=CANDIDATE_SHA,
        required_authority_class="HUMAN_GOVERNANCE_OWNER",
        required_scope="ACCEPTANCE_BOUNDARY_APPROVAL",
    )
    assert not ok


def test_exposed_acceptance_boundary_freezes_without_reissuing_authority():
    original = {
        "artifact_type": "FALSIFICATION_CONTRACT",
        "artifact_sha": CANDIDATE_SHA,
        "boundary_hash": "b" * 64,
        "approved_by": "HUMAN_GOVERNANCE_OWNER",
        "authority_evidence_ref": "manual-evidence:historical",
        "exposed": True,
        **policy_binding(),
    }
    proposed = {**original, "boundary_hash": "c" * 64}
    ok, reason = acceptance_boundary_change_allowed(original=original, proposed=proposed)
    assert not ok and "immutable" in reason


def test_naked_acceptance_role_string_is_rejected():
    try:
        acceptance_boundary_record(
            artifact_type="FALSIFICATION_CONTRACT",
            artifact_sha=CANDIDATE_SHA,
            boundary_hash="b" * 64,
            approved_by="HUMAN_GOVERNANCE_OWNER",
        )
    except ValueError as exc:
        assert "naked" in str(exc)
    else:
        raise AssertionError("naked privileged role unexpectedly accepted")


def test_candidate_callable_issuer_cannot_create_valid_authority():
    authority = _untrusted_binding("HUMAN_GOVERNANCE_OWNER", "ACCEPTANCE_BOUNDARY_APPROVAL")
    ok, _ = verify_authority_binding(
        authority,
        candidate_sha=CANDIDATE_SHA,
        required_authority_class="HUMAN_GOVERNANCE_OWNER",
        required_scope="ACCEPTANCE_BOUNDARY_APPROVAL",
    )
    assert not ok


def test_material_root_cause_requires_external_signed_attestation_and_bound_evidence():
    for role in ("CANDIDATE_IMPLEMENTATION", "REVIEWER", "CODING_AGENT", "ORCHESTRATOR", "INDEPENDENT_GOVERNANCE_ADJUDICATOR"):
        ok, _ = root_cause_classification_allowed(
            classification="CODE_DEFECT",
            material=True,
            classifier_role=role,
            independent_evidence_bound=True,
        )
        assert not ok
    authority = _untrusted_binding("INDEPENDENT_GOVERNANCE_ADJUDICATOR", "MATERIAL_ROOT_CAUSE_CLASSIFICATION")
    ok, _ = root_cause_classification_allowed(
        classification="CODE_DEFECT", material=True, candidate_sha=CANDIDATE_SHA,
        authority_binding=authority, independent_evidence_bound=True,
    )
    assert not ok


def test_review_finding_requires_external_signed_independent_adjudicator():
    for adjudicator in ("CANDIDATE_IMPLEMENTATION", "REVIEWER_R2", "INDEPENDENT_GOVERNANCE_ADJUDICATOR"):
        ok, _ = reviewer_finding_adjudication_allowed(
            adjudicator_role=adjudicator,
            candidate_role="CANDIDATE_IMPLEMENTATION",
            reviewer_role="REVIEWER_R2",
            exact_sha_bound=True,
            raw_finding_preserved=True,
        )
        assert not ok
    authority = _untrusted_binding("INDEPENDENT_GOVERNANCE_ADJUDICATOR", "REVIEW_FINDING_ADJUDICATION")
    ok, _ = reviewer_finding_adjudication_allowed(
        candidate_sha=CANDIDATE_SHA,
        authority_binding=authority,
        candidate_role="CANDIDATE_IMPLEMENTATION",
        reviewer_role="REVIEWER_R2",
        exact_sha_bound=True,
        raw_finding_preserved=True,
    )
    assert not ok


def test_review_adjudication_requires_exact_sha_and_raw_finding_preservation():
    authority = _untrusted_binding("INDEPENDENT_GOVERNANCE_ADJUDICATOR", "REVIEW_FINDING_ADJUDICATION")
    for exact_sha, preserved in ((False, True), (True, False)):
        ok, _ = reviewer_finding_adjudication_allowed(
            candidate_sha=CANDIDATE_SHA,
            authority_binding=authority,
            candidate_role="CANDIDATE_IMPLEMENTATION",
            reviewer_role="REVIEWER_R2",
            exact_sha_bound=exact_sha,
            raw_finding_preserved=preserved,
        )
        assert not ok


def test_candidate_cannot_defer_current_testing_contract_defect():
    disposition, _ = phase_disposition(
        current_phase="TESTING",
        violated_rule_id="TESTING_QUALIFICATION_BOUNDARY_OWNERSHIP",
        material=True,
    )
    assert disposition == "BLOCK_TESTING"


def test_only_platform_mapped_later_phase_rules_are_deferred():
    disposition, _ = phase_disposition(
        current_phase="TESTING", violated_rule_id="RELEASE_INTEGRATION_QUALIFICATION", material=True
    )
    assert disposition == "DEFERRED_TO_RELEASE"
    disposition, _ = phase_disposition(
        current_phase="TESTING", violated_rule_id="PRODUCTION_ENVIRONMENT_QUALIFICATION", material=True
    )
    assert disposition == "DEFERRED_TO_PRODUCTION"


def test_unknown_or_caller_selected_phase_cannot_be_silently_deferred():
    disposition, _ = phase_disposition(current_phase="TESTING", violated_rule_id="UNKNOWN", material=True)
    assert disposition == "REQUIREMENT_UNRESOLVED"
    disposition, _ = phase_disposition(current_phase="TESTING", violated_contract_phase="RELEASE", material=True)
    assert disposition == "REQUIREMENT_UNRESOLVED"


def test_model_or_reviewer_cannot_self_appoint_terminal_authority():
    for issuer in ("MODEL", "REVIEWER", "CODING_AGENT", "CI_JOB", "ORCHESTRATOR", "PLATFORM_POLICY", "HUMAN", None):
        ok, _ = terminal_authority_allowed(
            phase="TESTING", action="READY_TO_BEGIN_RELEASE_QUALIFICATION",
            issuer_class=issuer, provenance_verified=True, current=True,
        )
        assert not ok


def test_testing_terminal_authority_cannot_use_naked_role_or_booleans():
    ok, _ = terminal_authority_allowed(
        phase="TESTING", action="READY_TO_BEGIN_RELEASE_QUALIFICATION",
        issuer_class="HUMAN_GOVERNANCE_OWNER", provenance_verified=True, current=True,
    )
    assert not ok

    forged = _untrusted_binding(
        "HUMAN_GOVERNANCE_OWNER",
        "TERMINAL_ACTION:TESTING:READY_TO_BEGIN_RELEASE_QUALIFICATION",
    )
    ok, _ = terminal_authority_allowed(
        phase="TESTING",
        action="READY_TO_BEGIN_RELEASE_QUALIFICATION",
        candidate_sha=CANDIDATE_SHA,
        authority_binding=forged,
    )
    assert not ok

    for forbidden in ("DEPLOY_PRODUCTION", "MERGE_RELEASE_CANDIDATE", "BEGIN_PRODUCTION_QUALIFICATION"):
        ok, _ = terminal_authority_allowed(
            phase="TESTING", action=forbidden,
            candidate_sha=CANDIDATE_SHA, authority_binding=forged,
        )
        assert not ok


def test_terminal_authority_requires_verified_current_provenance():
    for verified, current in ((False, True), (True, False)):
        ok, _ = terminal_authority_allowed(
            phase="TESTING", action="READY_TO_BEGIN_RELEASE_QUALIFICATION",
            issuer_class="HUMAN_GOVERNANCE_OWNER", provenance_verified=verified, current=current,
        )
        assert not ok
