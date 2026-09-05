import unittest

from review_decision_engine import decide_review


def base(**overrides):
    signals = {
        "risk": "LOW",
        "materiality": "NONE",
        "uncertainty": "LOW",
        "external_action": False,
        "mutation_requested": False,
        "requirement_ambiguity": False,
        "unresolved_contradiction": False,
        "evidence_complete": True,
        "r2_completed": False,
        "r2_material_disagreement": False,
        "r2_finding_severity": "NONE",
        "material_revision_after_r2": False,
        "r2_available_qualified": True,
        "r3_available_qualified": True,
        "suspected_memory_contamination": False,
        "review_budget_exhausted": False,
    }
    signals.update(overrides)
    return signals


class ExpHReviewDecisionEngineTests(unittest.TestCase):
    def test_h001_simple_low_risk_prompt_does_not_require_review(self):
        self.assertEqual("NO_REVIEW", decide_review(base()).decision)

    def test_h002_material_architecture_change_requires_r2(self):
        d = decide_review(base(risk="MEDIUM", materiality="MATERIAL"))
        self.assertEqual("REVIEW_R2", d.decision)

    def test_h003_clean_r2_allows_finalization(self):
        d = decide_review(base(risk="MEDIUM", materiality="MATERIAL", r2_completed=True))
        self.assertEqual("NO_REVIEW", d.decision)

    def test_h004_critical_r2_finding_requires_r3(self):
        d = decide_review(base(risk="HIGH", materiality="MATERIAL", r2_completed=True, r2_finding_severity="CRITICAL"))
        self.assertEqual("REVIEW_R3", d.decision)

    def test_h005_material_revision_after_r2_requires_r3(self):
        d = decide_review(base(risk="MEDIUM", r2_completed=True, material_revision_after_r2=True))
        self.assertEqual("REVIEW_R3", d.decision)

    def test_h006_material_disagreement_requires_r3(self):
        d = decide_review(base(risk="MEDIUM", r2_completed=True, r2_material_disagreement=True))
        self.assertEqual("REVIEW_R3", d.decision)

    def test_h007_requirement_ambiguity_requires_human(self):
        self.assertEqual("HUMAN_REQUIRED", decide_review(base(requirement_ambiguity=True)).decision)

    def test_h008_budget_exhaustion_never_turns_required_review_into_pass(self):
        d = decide_review(base(risk="HIGH", review_budget_exhausted=True))
        self.assertEqual("HUMAN_REQUIRED", d.decision)

    def test_h009_model_cannot_skip_policy_required_review(self):
        # No model override signal exists in the authority function; materiality/risk controls the decision.
        self.assertEqual("REVIEW_R2", decide_review(base(risk="MEDIUM")).decision)

    def test_h010_platform_declines_unnecessary_review(self):
        self.assertEqual("NO_REVIEW", decide_review(base()).decision)

    def test_h011_unqualified_r2_fails_closed(self):
        d = decide_review(base(risk="HIGH", r2_available_qualified=False))
        self.assertEqual("HUMAN_REQUIRED", d.decision)

    def test_h012_unqualified_r3_fails_closed(self):
        d = decide_review(base(risk="HIGH", r2_completed=True, r2_material_disagreement=True, r3_available_qualified=False))
        self.assertEqual("HUMAN_REQUIRED", d.decision)

    def test_h013_memory_contamination_increases_review_strictness(self):
        self.assertEqual("REVIEW_R2", decide_review(base(suspected_memory_contamination=True)).decision)
        self.assertEqual("REVIEW_R3", decide_review(base(r2_completed=True, suspected_memory_contamination=True)).decision)

    def test_h014_clean_control_not_falsely_blocked(self):
        d = decide_review(base(risk="LOW", materiality="REVERSIBLE", uncertainty="MEDIUM"))
        self.assertEqual("NO_REVIEW", d.decision)

    def test_consequential_external_action_requires_review(self):
        self.assertEqual("REVIEW_R2", decide_review(base(external_action=True, materiality="CONSEQUENTIAL")).decision)

    def test_incomplete_evidence_high_risk_requires_human(self):
        self.assertEqual("HUMAN_REQUIRED", decide_review(base(risk="HIGH", evidence_complete=False)).decision)

    def test_unresolved_contradiction_after_r2_requires_human(self):
        self.assertEqual("HUMAN_REQUIRED", decide_review(base(risk="MEDIUM", unresolved_contradiction=True, r2_completed=True)).decision)


if __name__ == "__main__":
    unittest.main()
