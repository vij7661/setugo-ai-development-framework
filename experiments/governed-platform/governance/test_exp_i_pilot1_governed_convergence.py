import unittest

from exp_i_claim_convergence_gate import ReviewClaim, VerificationArtifact
from exp_i_governed_convergence import governed_convergence

CASE = "EXP-I-P1-INTEGRATION"


def r(reviewer_id, primary="CODE DEFECT", scope=("CODE",)):
    return ReviewClaim(reviewer_id, CASE, primary, tuple(scope))


def reviews(primary="CODE DEFECT", scope=("CODE",)):
    return [r("r1", primary, scope), r("r2", primary, scope), r("r3", primary, scope)]


def v(primary="CODE DEFECT", scope=("CODE",), *, valid=True, platform_issued=True, case_id=CASE):
    return VerificationArtifact("platform-independent-verifier", platform_issued, valid, case_id, primary, tuple(scope))


def signals(**overrides):
    value = {
        "evidence_complete": True,
        "requirement_ambiguity": False,
        "material_conflict": False,
        "r3_completed": True,
        "r3_required": True,
        "r3_available_qualified": True,
        "review_ceiling_reached": False,
        "material_revision_since_review": False,
        "authoritative_failure_established": False,
        "non_material_dissent": False,
        "max_unresolved_severity": "NONE",
    }
    value.update(overrides)
    return value


class ExpIPilot1GovernedConvergenceTests(unittest.TestCase):
    def test_i1c_01_exp_g_style_two_model_majority_cannot_pass(self):
        rs = [r("deepseek", "TEST DEFECT", ("TEST",)), r("claude", "TEST DEFECT", ("TEST",)), r("chatgpt", "FIXTURE-DATA DEFECT", ("FIXTURE-DATA",))]
        d = governed_convergence(rs, None, signals())
        self.assertEqual(d.state, "HUMAN_REQUIRED")
        self.assertEqual(d.claim_gate_state, "ESCALATE_INDEPENDENT_ADJUDICATION")
        self.assertFalse(d.terminal_convergence)

    def test_i1c_02_latest_reviewer_regression_cannot_pass(self):
        rs = [r("deepseek"), r("claude"), r("chatgpt", "FIXTURE-DATA DEFECT", ("FIXTURE-DATA",))]
        d = governed_convergence(rs, None, signals())
        self.assertEqual(d.state, "HUMAN_REQUIRED")

    def test_i1c_03_unanimity_without_verification_cannot_reach_terminal_engine(self):
        d = governed_convergence(reviews(), None, signals())
        self.assertEqual(d.state, "INSUFFICIENT_EVIDENCE")
        self.assertEqual(d.claim_gate_state, "REQUIRE_INDEPENDENT_VERIFICATION")
        self.assertFalse(d.terminal_convergence)

    def test_i1c_04_exact_verified_claim_can_reach_converged_pass(self):
        d = governed_convergence(reviews(), v(), signals())
        self.assertEqual(d.claim_gate_state, "ELIGIBLE_FOR_GOVERNANCE_GATE")
        self.assertEqual(d.state, "CONVERGED_PASS")
        self.assertTrue(d.terminal_convergence)
        self.assertFalse(d.production_authority)

    def test_i1c_05_authoritative_failure_overrides_verified_unanimity(self):
        d = governed_convergence(reviews(), v(), signals(authoritative_failure_established=True))
        self.assertEqual(d.state, "CONVERGED_FAIL")
        self.assertTrue(d.terminal_convergence)

    def test_i1c_06_requirement_ambiguity_overrides_verified_model_agreement(self):
        rs = reviews("REQUIREMENT UNRESOLVED", ())
        ver = v("REQUIREMENT UNRESOLVED", ())
        d = governed_convergence(rs, ver, signals(requirement_ambiguity=True))
        self.assertEqual(d.state, "HUMAN_REQUIRED")
        self.assertFalse(d.terminal_convergence)

    def test_i1c_07_verification_conflict_blocks_before_terminal_engine(self):
        d = governed_convergence(reviews(), v("TEST DEFECT", ("TEST",)), signals())
        self.assertEqual(d.state, "HUMAN_REQUIRED")
        self.assertEqual(d.claim_gate_state, "VERIFICATION_CONFLICT")
        self.assertFalse(d.terminal_convergence)

    def test_i1c_08_material_revision_invalidates_even_previously_verified_claim(self):
        d = governed_convergence(reviews(), v(), signals(material_revision_since_review=True))
        self.assertEqual(d.state, "INSUFFICIENT_EVIDENCE")
        self.assertFalse(d.terminal_convergence)

    def test_i1c_09_review_ceiling_with_material_conflict_never_forces_pass(self):
        d = governed_convergence(reviews(), v(), signals(material_conflict=True, review_ceiling_reached=True))
        self.assertEqual(d.state, "HUMAN_REQUIRED")

    def test_i1c_10_duplicate_reviewer_identity_blocks_composed_path(self):
        rs = [r("same"), r("same"), r("same")]
        d = governed_convergence(rs, v(), signals())
        self.assertEqual(d.state, "INSUFFICIENT_EVIDENCE")
        self.assertEqual(d.claim_gate_state, "INVALID_REVIEW_INPUT")

    def test_i1c_11_invalid_artifact_taxonomy_blocks_composed_path(self):
        rs = [r("r1", "TEST DEFECT", ("TEST DEFECT",)), r("r2", "TEST DEFECT", ("TEST",)), r("r3", "TEST DEFECT", ("TEST",))]
        d = governed_convergence(rs, None, signals())
        self.assertEqual(d.state, "INSUFFICIENT_EVIDENCE")
        self.assertEqual(d.claim_gate_state, "INVALID_REVIEW_INPUT")

    def test_i1c_12_convergence_never_grants_reviewer_or_production_authority(self):
        decisions = [
            governed_convergence(reviews(), v(), signals()),
            governed_convergence(reviews(), v(), signals(authoritative_failure_established=True)),
            governed_convergence(reviews(), v(), signals(non_material_dissent=True)),
        ]
        self.assertTrue(all(not d.reviewer_generated_authority for d in decisions))
        self.assertTrue(all(not d.production_authority for d in decisions))


if __name__ == "__main__":
    unittest.main()
