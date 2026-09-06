import itertools
import unittest

from exp_h_review_disagreement_gate import (
    GateState,
    ReviewClaim,
    VerificationArtifact,
    evaluate_review_gate,
)


CASE = "EXP-H-CASE-001"


def review(reviewer_id, primary="CODE DEFECT", scope=("CODE",), case_id=CASE):
    return ReviewClaim(reviewer_id, case_id, primary, tuple(scope))


def verifier(primary="CODE DEFECT", scope=("CODE",), case_id=CASE, platform_issued=True, valid=True):
    return VerificationArtifact(
        issuer="platform-independent-verifier",
        platform_issued=platform_issued,
        valid=valid,
        case_id=case_id,
        primary_failure_class=primary,
        authorized_artifact_scope=tuple(scope),
    )


class ExpHReviewDisagreementGateTests(unittest.TestCase):
    def test_p01_two_of_three_majority_does_not_converge(self):
        decision = evaluate_review_gate([
            review("r1", "TEST DEFECT", ("TEST",)),
            review("r2", "TEST DEFECT", ("TEST",)),
            review("r3", "FIXTURE-DATA DEFECT", ("FIXTURE-DATA",)),
        ])
        self.assertEqual(decision.state, GateState.ESCALATE_INDEPENDENT_ADJUDICATION)

    def test_p02_two_of_three_correct_majority_still_does_not_converge(self):
        decision = evaluate_review_gate([
            review("r1"), review("r2"), review("r3", "TEST DEFECT", ("TEST",))
        ])
        self.assertEqual(decision.state, GateState.ESCALATE_INDEPENDENT_ADJUDICATION)

    def test_p03_latest_reviewer_correction_does_not_self_authorize(self):
        decision = evaluate_review_gate([
            review("r1", "TEST DEFECT", ("TEST",)),
            review("r2", "TEST DEFECT", ("TEST",)),
            review("r3", "FIXTURE-DATA DEFECT", ("FIXTURE-DATA",)),
        ])
        self.assertFalse(decision.reviewer_generated_authority)
        self.assertFalse(decision.terminal_approval)

    def test_p04_latest_reviewer_regression_does_not_override_prior_reviews(self):
        decision = evaluate_review_gate([
            review("r1"), review("r2"), review("r3", "REQUIREMENT UNRESOLVED", ())
        ])
        self.assertEqual(decision.state, GateState.ESCALATE_INDEPENDENT_ADJUDICATION)

    def test_p05_unanimous_wrong_claim_still_requires_independent_verification(self):
        decision = evaluate_review_gate([
            review("r1", "TEST DEFECT", ("TEST",)),
            review("r2", "TEST DEFECT", ("TEST",)),
            review("r3", "TEST DEFECT", ("TEST",)),
        ])
        self.assertEqual(decision.state, GateState.REQUIRE_INDEPENDENT_VERIFICATION)

    def test_p06_unanimous_correct_claim_without_verifier_still_not_approved(self):
        decision = evaluate_review_gate([review("r1"), review("r2"), review("r3")])
        self.assertEqual(decision.state, GateState.REQUIRE_INDEPENDENT_VERIFICATION)
        self.assertFalse(decision.terminal_approval)

    def test_p07_scope_disagreement_escalates_even_when_primary_matches(self):
        decision = evaluate_review_gate([
            review("r1", scope=("CODE",)),
            review("r2", scope=("CODE", "FIXTURE-DATA")),
            review("r3", scope=("CODE",)),
        ])
        self.assertEqual(decision.state, GateState.ESCALATE_INDEPENDENT_ADJUDICATION)

    def test_p08_invalid_failure_class_fails_closed(self):
        decision = evaluate_review_gate([review("r1", "BEST GUESS", ())])
        self.assertEqual(decision.state, GateState.INVALID_REVIEW_INPUT)

    def test_p09_invalid_scope_label_fails_closed(self):
        decision = evaluate_review_gate([review("r1", "TEST DEFECT", ("TEST DEFECT",))])
        self.assertEqual(decision.state, GateState.INVALID_REVIEW_INPUT)

    def test_p10_requirement_unresolved_cannot_carry_mutation_scope(self):
        decision = evaluate_review_gate([review("r1", "REQUIREMENT UNRESOLVED", ("CODE",))])
        self.assertEqual(decision.state, GateState.INVALID_REVIEW_INPUT)

    def test_p11_no_material_defect_cannot_carry_mutation_scope(self):
        decision = evaluate_review_gate([review("r1", "NO MATERIAL DEFECT", ("TEST",))])
        self.assertEqual(decision.state, GateState.INVALID_REVIEW_INPUT)

    def test_p12_matching_platform_verifier_only_reaches_governance_gate(self):
        decision = evaluate_review_gate(
            [review("r1"), review("r2"), review("r3")], verifier()
        )
        self.assertEqual(decision.state, GateState.ELIGIBLE_FOR_GOVERNANCE_GATE)
        self.assertFalse(decision.terminal_approval)
        self.assertFalse(decision.reviewer_generated_authority)

    def test_p13_verifier_primary_class_conflict_blocks(self):
        decision = evaluate_review_gate(
            [review("r1"), review("r2")], verifier(primary="TEST DEFECT", scope=("TEST",))
        )
        self.assertEqual(decision.state, GateState.VERIFICATION_CONFLICT)

    def test_p14_verifier_scope_conflict_blocks(self):
        decision = evaluate_review_gate(
            [review("r1"), review("r2")], verifier(scope=("CODE", "FIXTURE-DATA"))
        )
        self.assertEqual(decision.state, GateState.VERIFICATION_CONFLICT)

    def test_p15_verifier_case_binding_conflict_blocks(self):
        decision = evaluate_review_gate(
            [review("r1"), review("r2")], verifier(case_id="OTHER-CASE")
        )
        self.assertEqual(decision.state, GateState.VERIFICATION_CONFLICT)

    def test_p16_non_platform_or_invalid_verifier_blocks(self):
        d1 = evaluate_review_gate([review("r1")], verifier(platform_issued=False))
        d2 = evaluate_review_gate([review("r1")], verifier(valid=False))
        self.assertEqual(d1.state, GateState.VERIFICATION_CONFLICT)
        self.assertEqual(d2.state, GateState.VERIFICATION_CONFLICT)

    def test_p17_review_order_permutation_invariant(self):
        claims = [
            review("r1", "TEST DEFECT", ("TEST",)),
            review("r2", "FIXTURE-DATA DEFECT", ("FIXTURE-DATA",)),
            review("r3", "TEST DEFECT", ("TEST",)),
        ]
        states = {evaluate_review_gate(p).state for p in itertools.permutations(claims)}
        self.assertEqual(states, {GateState.ESCALATE_INDEPENDENT_ADJUDICATION})

    def test_p18_duplicate_majority_cannot_manufacture_convergence(self):
        decision = evaluate_review_gate([
            review("same", "TEST DEFECT", ("TEST",)),
            review("same", "TEST DEFECT", ("TEST",)),
            review("dissent", "FIXTURE-DATA DEFECT", ("FIXTURE-DATA",)),
        ])
        self.assertEqual(decision.state, GateState.ESCALATE_INDEPENDENT_ADJUDICATION)

    def test_p19_clean_control_consensus_still_requires_verification(self):
        claims = [
            review("r1", "NO MATERIAL DEFECT", ()),
            review("r2", "NO MATERIAL DEFECT", ()),
            review("r3", "NO MATERIAL DEFECT", ()),
        ]
        decision = evaluate_review_gate(claims)
        self.assertEqual(decision.state, GateState.REQUIRE_INDEPENDENT_VERIFICATION)

    def test_p20_no_gate_state_is_terminal_approval(self):
        forbidden = {"APPROVED", "RELEASED", "MERGED", "DEPLOYED", "COMPLETE"}
        self.assertTrue(forbidden.isdisjoint({state.value for state in GateState}))
        decisions = [
            evaluate_review_gate([review("r1")]),
            evaluate_review_gate([review("r1")], verifier()),
            evaluate_review_gate([review("r1"), review("r2", "TEST DEFECT", ("TEST",))]),
        ]
        self.assertTrue(all(not d.terminal_approval for d in decisions))
        self.assertTrue(all(not d.reviewer_generated_authority for d in decisions))


if __name__ == "__main__":
    unittest.main()
