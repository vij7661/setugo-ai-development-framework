import unittest

from tri_reviewer_convergence import decide_convergence


def base(**overrides):
    signals = {
        "evidence_complete": True,
        "requirement_ambiguity": False,
        "material_conflict": False,
        "r3_completed": False,
        "r3_required": False,
        "r3_available_qualified": True,
        "review_ceiling_reached": False,
        "material_revision_since_review": False,
        "authoritative_failure_established": False,
        "non_material_dissent": False,
        "max_unresolved_severity": "NONE",
    }
    signals.update(overrides)
    return signals


class ExpIConvergenceTests(unittest.TestCase):
    def test_i001_unanimous_models_cannot_override_authoritative_failure(self):
        self.assertEqual("CONVERGED_FAIL", decide_convergence(base(authoritative_failure_established=True)).state)

    def test_i002_material_conflict_before_required_r3_is_not_pass(self):
        d = decide_convergence(base(material_conflict=True, r3_required=True, r3_completed=False))
        self.assertEqual("INSUFFICIENT_EVIDENCE", d.state)

    def test_i003_completed_r3_with_resolved_conflict_can_pass(self):
        d = decide_convergence(base(r3_required=True, r3_completed=True))
        self.assertEqual("CONVERGED_PASS", d.state)

    def test_i004_non_material_dissent_is_preserved(self):
        self.assertEqual("CONVERGED_WITH_DISSENT", decide_convergence(base(non_material_dissent=True)).state)

    def test_i005_requirement_ambiguity_requires_human_even_if_reviewers_agree(self):
        self.assertEqual("HUMAN_REQUIRED", decide_convergence(base(requirement_ambiguity=True)).state)

    def test_i006_review_ceiling_with_material_conflict_requires_human(self):
        d = decide_convergence(base(material_conflict=True, review_ceiling_reached=True))
        self.assertEqual("HUMAN_REQUIRED", d.state)

    def test_i007_unavailable_required_r3_fails_closed(self):
        d = decide_convergence(base(r3_required=True, r3_available_qualified=False))
        self.assertEqual("HUMAN_REQUIRED", d.state)

    def test_i008_material_revision_invalidates_prior_reviews(self):
        d = decide_convergence(base(material_revision_since_review=True))
        self.assertEqual("INSUFFICIENT_EVIDENCE", d.state)

    def test_i009_clean_control_passes(self):
        self.assertEqual("CONVERGED_PASS", decide_convergence(base()).state)

    def test_incomplete_evidence_never_passes(self):
        self.assertEqual("INSUFFICIENT_EVIDENCE", decide_convergence(base(evidence_complete=False)).state)

    def test_high_unresolved_finding_requires_human(self):
        self.assertEqual("HUMAN_REQUIRED", decide_convergence(base(max_unresolved_severity="HIGH")).state)

    def test_medium_unresolved_finding_can_converge_with_dissent(self):
        self.assertEqual("CONVERGED_WITH_DISSENT", decide_convergence(base(max_unresolved_severity="MEDIUM")).state)


if __name__ == "__main__":
    unittest.main()
