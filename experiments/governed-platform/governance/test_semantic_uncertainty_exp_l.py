import unittest

from review_decision_engine import decide_review
from semantic_uncertainty import SemanticProbePolicy, analyze_semantic_samples


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
        "semantic_probe_status": "NOT_RUN",
        "counterfactual_instability": False,
    }
    signals.update(overrides)
    return signals


class ExpLSemanticUncertaintyTests(unittest.TestCase):
    def setUp(self):
        # Test-only policy values exercise mechanics. They are not production thresholds.
        self.policy = SemanticProbePolicy(
            max_normalized_entropy=0.50,
            max_refusal_ratio=0.50,
            policy_version="exp-l-test-policy-v1",
        )

    def test_l001_lexical_variants_in_same_semantic_cluster_are_stable(self):
        result = analyze_semantic_samples(
            ["PARIS", "PARIS", "PARIS", "PARIS"],
            [False, False, False, False],
            self.policy,
        )
        self.assertEqual("STABLE", result.status)
        self.assertEqual(1, result.semantic_cluster_count)
        self.assertEqual(0.0, result.normalized_entropy)

    def test_l002_materially_different_meanings_raise_semantic_uncertainty(self):
        result = analyze_semantic_samples(
            ["FIXTURE", "TEST", "FIXTURE", "TEST"],
            [False, False, False, False],
            self.policy,
        )
        self.assertEqual("UNCERTAIN", result.status)
        self.assertGreater(result.normalized_entropy, 0.50)

    def test_l003_refusal_dominant_probe_escalates(self):
        result = analyze_semantic_samples(
            ["UNKNOWN", "UNKNOWN", "X", "UNKNOWN"],
            [True, True, False, True],
            self.policy,
        )
        self.assertEqual("REFUSAL_DOMINANT", result.status)
        decision = decide_review(base(semantic_probe_status=result.status))
        self.assertEqual("REVIEW_R2", decision.decision)

    def test_l004_high_semantic_uncertainty_triggers_r2_on_low_risk_task(self):
        decision = decide_review(base(semantic_probe_status="UNCERTAIN"))
        self.assertEqual("REVIEW_R2", decision.decision)

    def test_l005_stable_semantic_probe_does_not_override_high_risk_review(self):
        decision = decide_review(base(risk="HIGH", semantic_probe_status="STABLE"))
        self.assertEqual("REVIEW_R2", decision.decision)

    def test_l006_stable_wrong_case_remains_possible_by_design(self):
        # A single semantic cluster can be consistently wrong; the probe must not claim truth.
        result = analyze_semantic_samples(
            ["WRONG_SAME_MEANING"] * 5,
            [False] * 5,
            self.policy,
        )
        self.assertEqual("STABLE", result.status)
        self.assertEqual("NO_REVIEW", decide_review(base(semantic_probe_status=result.status)).decision)
        # Scientific evaluation must count this as a stable-wrong failure if protected truth says it is wrong.

    def test_l007_counterfactual_instability_triggers_r2(self):
        decision = decide_review(base(counterfactual_instability=True))
        self.assertEqual("REVIEW_R2", decision.decision)

    def test_l008_self_reported_low_confidence_is_not_same_as_semantic_uncertainty(self):
        self.assertEqual("NO_REVIEW", decide_review(base(uncertainty="MEDIUM")).decision)
        self.assertEqual("REVIEW_R2", decide_review(base(semantic_probe_status="UNCERTAIN")).decision)

    def test_l009_invalid_policy_without_version_fails_closed(self):
        with self.assertRaises(ValueError):
            analyze_semantic_samples(
                ["A", "B"],
                [False, False],
                SemanticProbePolicy(0.5, 0.5, ""),
            )

    def test_l010_invalid_semantic_probe_status_fails_closed(self):
        with self.assertRaises(ValueError):
            decide_review(base(semantic_probe_status="MAGIC_CONFIDENT"))

    def test_l011_mismatched_sample_metadata_fails_closed(self):
        with self.assertRaises(ValueError):
            analyze_semantic_samples(["A", "B"], [False], self.policy)

    def test_l012_thresholds_are_explicit_policy_inputs_not_hidden_constants(self):
        loose = SemanticProbePolicy(1.0, 1.0, "loose-v1")
        strict = SemanticProbePolicy(0.0, 0.0, "strict-v1")
        clusters = ["A", "B"]
        refusals = [False, False]
        self.assertEqual("STABLE", analyze_semantic_samples(clusters, refusals, loose).status)
        self.assertEqual("UNCERTAIN", analyze_semantic_samples(clusters, refusals, strict).status)


if __name__ == "__main__":
    unittest.main()
