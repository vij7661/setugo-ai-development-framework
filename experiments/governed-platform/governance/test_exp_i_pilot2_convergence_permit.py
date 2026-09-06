import dataclasses
import unittest

from exp_i_claim_convergence_gate import ReviewClaim, VerificationArtifact
from exp_i_convergence_permit import ConvergencePermit, ConvergencePermitAuthority

CASE = "EXP-I-P2-CASE"
KEY = b"exp-i-pilot2-test-key"


def r(reviewer_id, primary="CODE DEFECT", scope=("CODE",), case_id=CASE):
    return ReviewClaim(reviewer_id, case_id, primary, tuple(scope))


def reviews(primary="CODE DEFECT", scope=("CODE",), case_id=CASE):
    return [r("r1", primary, scope, case_id), r("r2", primary, scope, case_id), r("r3", primary, scope, case_id)]


def v(primary="CODE DEFECT", scope=("CODE",), case_id=CASE, platform_issued=True, valid=True):
    return VerificationArtifact("platform-independent-verifier", platform_issued, valid, case_id, primary, tuple(scope))


def signals(**overrides):
    data = {
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
    data.update(overrides)
    return data


class ExpIPilot2ConvergencePermitTests(unittest.TestCase):
    def setUp(self):
        self.auth = ConvergencePermitAuthority(KEY)

    def issue(self, rs=None, ver=None, sig=None, nonce="n-1"):
        return self.auth.issue(rs or reviews(), ver or v(), sig or signals(), nonce=nonce)

    def test_i2_01_direct_governed_terminal_without_permit_has_no_path(self):
        self.assertFalse(hasattr(self.auth, "converge_without_permit"))

    def test_i2_02_forged_signature_denied(self):
        p = self.issue()
        forged = dataclasses.replace(p, signature="00" * 32)
        self.assertEqual(self.auth.consume(forged, reviews(), v(), signals()).state, "DENIED")

    def test_i2_03_nonplatform_issuer_denied_even_with_original_signature(self):
        p = self.issue()
        forged = dataclasses.replace(p, issuer="reviewer")
        self.assertEqual(self.auth.consume(forged, reviews(), v(), signals()).state, "DENIED")

    def test_i2_04_case_substitution_denied(self):
        p = self.issue()
        changed = reviews(case_id="OTHER")
        self.assertEqual(self.auth.consume(p, changed, v(case_id="OTHER"), signals()).state, "DENIED")

    def test_i2_05_primary_class_substitution_denied(self):
        p = self.issue()
        changed = reviews("TEST DEFECT", ("TEST",))
        self.assertEqual(self.auth.consume(p, changed, v("TEST DEFECT", ("TEST",)), signals()).state, "DENIED")

    def test_i2_06_scope_substitution_denied(self):
        p = self.issue()
        changed = reviews("CODE DEFECT", ("CODE", "FIXTURE-DATA"))
        self.assertEqual(self.auth.consume(p, changed, v("CODE DEFECT", ("CODE", "FIXTURE-DATA")), signals()).state, "DENIED")

    def test_i2_07_verification_substitution_denied(self):
        p = self.issue()
        changed_verifier = VerificationArtifact("different-verifier", True, True, CASE, "CODE DEFECT", ("CODE",))
        self.assertEqual(self.auth.consume(p, reviews(), changed_verifier, signals()).state, "DENIED")

    def test_i2_08_signal_substitution_denied(self):
        p = self.issue()
        self.assertEqual(self.auth.consume(p, reviews(), v(), signals(non_material_dissent=True)).state, "DENIED")

    def test_i2_09_two_reviewers_cannot_mint_permit(self):
        with self.assertRaises(PermissionError):
            self.auth.issue(reviews()[:2], v(), signals(), nonce="two")

    def test_i2_10_duplicate_reviewers_cannot_mint_permit(self):
        rs = [r("same"), r("same"), r("same")]
        with self.assertRaises(PermissionError):
            self.auth.issue(rs, v(), signals(), nonce="dup")

    def test_i2_11_material_disagreement_cannot_mint_permit(self):
        rs = [r("r1"), r("r2"), r("r3", "TEST DEFECT", ("TEST",))]
        with self.assertRaises(PermissionError):
            self.auth.issue(rs, v(), signals(), nonce="disagree")

    def test_i2_12_missing_verification_cannot_be_substituted_at_issue(self):
        with self.assertRaises((AttributeError, TypeError)):
            self.auth.issue(reviews(), None, signals(), nonce="no-verifier")

    def test_i2_13_conflicting_verification_cannot_mint_permit(self):
        with self.assertRaises(PermissionError):
            self.auth.issue(reviews(), v("TEST DEFECT", ("TEST",)), signals(), nonce="bad-verifier")

    def test_i2_14_exact_replay_after_consumption_denied(self):
        p = self.issue()
        first = self.auth.consume(p, reviews(), v(), signals())
        second = self.auth.consume(p, reviews(), v(), signals())
        self.assertEqual(first.state, "CONVERGED_PASS")
        self.assertEqual(second.state, "DENIED")

    def test_i2_15_same_nonce_semantic_rebinding_denied(self):
        self.issue(nonce="shared")
        with self.assertRaises(PermissionError):
            self.auth.issue(reviews("TEST DEFECT", ("TEST",)), v("TEST DEFECT", ("TEST",)), signals(), nonce="shared")

    def test_i2_16_changed_signals_after_issue_denied(self):
        p = self.issue()
        self.assertEqual(self.auth.consume(p, reviews(), v(), signals(max_unresolved_severity="HIGH")).state, "DENIED")

    def test_i2_17_material_revision_after_issue_denied_by_signal_binding(self):
        p = self.issue()
        self.assertEqual(self.auth.consume(p, reviews(), v(), signals(material_revision_since_review=True)).state, "DENIED")

    def test_i2_18_authoritative_failure_after_issue_denied_by_signal_binding(self):
        p = self.issue()
        self.assertEqual(self.auth.consume(p, reviews(), v(), signals(authoritative_failure_established=True)).state, "DENIED")

    def test_i2_19_reviewer_cannot_mutate_permit_control_flags(self):
        p = self.issue()
        self.assertFalse(hasattr(p, "consumed"))
        self.assertFalse(hasattr(p, "terminal"))
        self.assertEqual(self.auth.consume(p, reviews(), v(), signals()).production_authority, False)

    def test_i2_20_clean_verified_three_reviewer_liveness_exactly_once(self):
        p = self.issue(nonce="clean")
        d = self.auth.consume(p, reviews(), v(), signals())
        self.assertEqual(d.state, "CONVERGED_PASS")
        self.assertTrue(d.terminal_convergence)
        self.assertFalse(d.reviewer_generated_authority)
        self.assertFalse(d.production_authority)

    def test_i2_21_epoch_advance_invalidates_unconsumed_permit(self):
        p = self.issue(nonce="epoch")
        self.auth.advance_epoch()
        self.assertEqual(self.auth.consume(p, reviews(), v(), signals()).state, "DENIED")

    def test_i2_22_tampering_any_signed_binding_breaks_signature(self):
        p = self.issue(nonce="tamper")
        mutations = [
            dataclasses.replace(p, case_id="OTHER"),
            dataclasses.replace(p, primary_failure_class="TEST DEFECT"),
            dataclasses.replace(p, authorized_artifact_scope=("TEST",)),
            dataclasses.replace(p, verification_digest="0" * 64),
            dataclasses.replace(p, signals_digest="0" * 64),
            dataclasses.replace(p, issuance_epoch=999),
            dataclasses.replace(p, nonce="other"),
        ]
        self.assertTrue(all(self.auth.consume(x, reviews(), v(), signals()).state == "DENIED" for x in mutations))


if __name__ == "__main__":
    unittest.main()
