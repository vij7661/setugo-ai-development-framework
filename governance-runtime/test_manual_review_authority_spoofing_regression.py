# R10-B adversarial fixture: intentional blob-identity substitution; test count/names preserved.
from qualification_boundary_policy import (
    acceptance_boundary_record,
    phase_disposition,
    reviewer_finding_adjudication_allowed,
    root_cause_classification_allowed,
)


def test_untrusted_caller_cannot_self_assert_human_governance_owner():
    try:
        acceptance_boundary_record(
            artifact_type="FALSIFICATION_CONTRACT",
            artifact_sha="a" * 40,
            boundary_hash="b" * 64,
            approved_by="HUMAN_GOVERNANCE_OWNER",
            exposed=True,
        )
    except (TypeError, ValueError):
        return
    raise AssertionError("naked privileged role string was accepted as authority")


def test_untrusted_caller_cannot_self_assert_independent_root_cause_adjudicator():
    ok, _ = root_cause_classification_allowed(
        classification="CODE_DEFECT",
        material=True,
        classifier_role="INDEPENDENT_GOVERNANCE_ADJUDICATOR",
        independent_evidence_bound=True,
    )
    assert not ok, "naked independent-adjudicator role string was accepted"


def test_untrusted_caller_cannot_self_assert_independent_review_adjudicator():
    ok, _ = reviewer_finding_adjudication_allowed(
        adjudicator_role="INDEPENDENT_GOVERNANCE_ADJUDICATOR",
        candidate_role="CANDIDATE_IMPLEMENTATION",
        reviewer_role="REVIEWER_R2",
        exact_sha_bound=True,
        raw_finding_preserved=True,
    )
    assert not ok, "naked independent-adjudicator role string was accepted"


def test_caller_selected_later_phase_cannot_defer_without_governed_rule_mapping():
    disposition, _ = phase_disposition(
        current_phase="TESTING",
        violated_contract_phase="RELEASE",
        material=True,
    )
    assert disposition != "DEFERRED_TO_RELEASE", (
        "caller-selected violated_contract_phase produced a deferral without a governed rule mapping"
    )
