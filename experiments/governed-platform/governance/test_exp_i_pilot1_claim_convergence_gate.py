import itertools
import unittest

from exp_i_claim_convergence_gate import (
    GateState,
    ReviewClaim,
    VerificationArtifact,
    evaluate_review_gate,
)

CASE = "EXP-I-P1-CASE"


def r(reviewer_id, primary="CODE DEFECT", scope=("CODE",), case_id=CASE):
    return ReviewClaim(reviewer_id, case_id, primary, tuple(scope))


def three(primary="CODE DEFECT", scope=("CODE",), case_id=CASE):
    return [r("r1", primary, scope, case_id), r("r2", primary, scope, case_id), r("r3", primary, scope, case_id)]


def v(primary="CODE DEFECT", scope=("CODE",), case_id=CASE, platform_issued=True, valid=True):
    return VerificationArtifact("platform-independent-verifier", platform_issued, valid, case_id, primary, tuple(scope))


class ExpIPilot1ClaimGateTests(unittest.TestCase):
    def test_i1_01_two_of_three_wrong_majority_escalates(self):
        d = evaluate_review_gate([r("r1", "TEST DEFECT", ("TEST",)), r("r2", "TEST DEFECT", ("TEST",)), r("r3", "FIXTURE-DATA DEFECT", ("FIXTURE-DATA",))])
        self.assertEqual(d.state, GateState.ESCALATE_INDEPENDENT_ADJUDICATION)

    def test_i1_02_two_of_three_correct_majority_still_escalates(self):
        d = evaluate_review_gate([r("r1"), r("r2"), r("r3", "TEST DEFECT", ("TEST",))])
        self.assertEqual(d.state, GateState.ESCALATE_INDEPENDENT_ADJUDICATION)

    def test_i1_03_latest_correction_never_self_authorizes(self):
        d = evaluate_review_gate([r("r1", "TEST DEFECT", ("TEST",)), r("r2", "TEST DEFECT", ("TEST",)), r("r3", "FIXTURE-DATA DEFECT", ("FIXTURE-DATA",))])
        self.assertFalse(d.reviewer_generated_authority); self.assertFalse(d.terminal_approval)

    def test_i1_04_latest_regression_never_overrides(self):
        d = evaluate_review_gate([r("r1"), r("r2"), r("r3", "REQUIREMENT UNRESOLVED", ())])
        self.assertEqual(d.state, GateState.ESCALATE_INDEPENDENT_ADJUDICATION)

    def test_i1_05_unanimous_wrong_still_requires_verification(self):
        self.assertEqual(evaluate_review_gate(three("TEST DEFECT", ("TEST",))).state, GateState.REQUIRE_INDEPENDENT_VERIFICATION)

    def test_i1_06_unanimous_correct_without_verifier_not_terminal(self):
        d = evaluate_review_gate(three())
        self.assertEqual(d.state, GateState.REQUIRE_INDEPENDENT_VERIFICATION); self.assertFalse(d.terminal_approval)

    def test_i1_07_scope_disagreement_escalates(self):
        d = evaluate_review_gate([r("r1"), r("r2", scope=("CODE", "FIXTURE-DATA")), r("r3")])
        self.assertEqual(d.state, GateState.ESCALATE_INDEPENDENT_ADJUDICATION)

    def test_i1_08_invalid_failure_class_fails_closed(self):
        d = evaluate_review_gate([r("r1", "BEST GUESS", ()), r("r2"), r("r3")])
        self.assertEqual(d.state, GateState.INVALID_REVIEW_INPUT)

    def test_i1_09_invalid_scope_label_fails_closed(self):
        d = evaluate_review_gate([r("r1", "TEST DEFECT", ("TEST DEFECT",)), r("r2"), r("r3")])
        self.assertEqual(d.state, GateState.INVALID_REVIEW_INPUT)

    def test_i1_10_requirement_unresolved_scope_fails_closed(self):
        d = evaluate_review_gate(three("REQUIREMENT UNRESOLVED", ("CODE",)))
        self.assertEqual(d.state, GateState.INVALID_REVIEW_INPUT)

    def test_i1_11_no_material_defect_scope_fails_closed(self):
        d = evaluate_review_gate(three("NO MATERIAL DEFECT", ("TEST",)))
        self.assertEqual(d.state, GateState.INVALID_REVIEW_INPUT)

    def test_i1_12_matching_verifier_only_reaches_governance_gate(self):
        d = evaluate_review_gate(three(), v())
        self.assertEqual(d.state, GateState.ELIGIBLE_FOR_GOVERNANCE_GATE); self.assertFalse(d.terminal_approval)

    def test_i1_13_verifier_primary_conflict_blocks(self):
        d = evaluate_review_gate(three(), v("TEST DEFECT", ("TEST",)))
        self.assertEqual(d.state, GateState.VERIFICATION_CONFLICT)

    def test_i1_14_verifier_scope_conflict_blocks(self):
        d = evaluate_review_gate(three(), v(scope=("CODE", "FIXTURE-DATA")))
        self.assertEqual(d.state, GateState.VERIFICATION_CONFLICT)

    def test_i1_15_verifier_case_binding_conflict_blocks(self):
        self.assertEqual(evaluate_review_gate(three(), v(case_id="OTHER")).state, GateState.VERIFICATION_CONFLICT)

    def test_i1_16_nonplatform_or_invalid_verifier_blocks(self):
        self.assertEqual(evaluate_review_gate(three(), v(platform_issued=False)).state, GateState.VERIFICATION_CONFLICT)
        self.assertEqual(evaluate_review_gate(three(), v(valid=False)).state, GateState.VERIFICATION_CONFLICT)

    def test_i1_17_review_order_permutation_invariant(self):
        claims = [r("r1", "TEST DEFECT", ("TEST",)), r("r2", "FIXTURE-DATA DEFECT", ("FIXTURE-DATA",)), r("r3", "TEST DEFECT", ("TEST",))]
        self.assertEqual({evaluate_review_gate(p).state for p in itertools.permutations(claims)}, {GateState.ESCALATE_INDEPENDENT_ADJUDICATION})

    def test_i1_18_duplicate_with_dissent_cannot_manufacture_convergence(self):
        d = evaluate_review_gate([r("same", "TEST DEFECT", ("TEST",)), r("same", "TEST DEFECT", ("TEST",)), r("dissent", "FIXTURE-DATA DEFECT", ("FIXTURE-DATA",))])
        self.assertEqual(d.state, GateState.INVALID_REVIEW_INPUT)

    def test_i1_19_clean_control_consensus_still_requires_verification(self):
        self.assertEqual(evaluate_review_gate(three("NO MATERIAL DEFECT", ())).state, GateState.REQUIRE_INDEPENDENT_VERIFICATION)

    def test_i1_20_no_gate_state_is_terminal_approval(self):
        forbidden = {"APPROVED", "RELEASED", "MERGED", "DEPLOYED", "COMPLETE"}
        self.assertTrue(forbidden.isdisjoint({x.value for x in GateState}))

    def test_i1_21_one_reviewer_duplicated_three_times_fails_closed(self):
        d = evaluate_review_gate([r("same"), r("same"), r("same")], v())
        self.assertEqual(d.state, GateState.INVALID_REVIEW_INPUT)

    def test_i1_22_two_distinct_reviewers_with_duplicate_fails_closed(self):
        d = evaluate_review_gate([r("r1"), r("r1"), r("r2")], v())
        self.assertEqual(d.state, GateState.INVALID_REVIEW_INPUT)

    def test_i1_23_wrong_reviewer_cardinality_fails_closed(self):
        self.assertEqual(evaluate_review_gate([r("r1"), r("r2")]).state, GateState.INVALID_REVIEW_INPUT)
        self.assertEqual(evaluate_review_gate([r("r1"), r("r2"), r("r3"), r("r4")]).state, GateState.INVALID_REVIEW_INPUT)


if __name__ == "__main__":
    unittest.main()
