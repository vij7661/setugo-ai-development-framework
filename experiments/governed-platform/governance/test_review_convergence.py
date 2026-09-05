import unittest

from review_convergence import compatibility_gate, evaluate_review_convergence, extract_domain_invariants


class DomainInvariantTests(unittest.TestCase):
    def test_missing_invariants_fail_closed(self):
        with self.assertRaises(ValueError):
            extract_domain_invariants({})

    def test_compatibility_requires_every_invariant(self):
        contract = {"domain_invariants": ["authority_external", "evidence_before_promotion"]}
        result = compatibility_gate(contract, {"preserved_invariants": ["authority_external"]})
        self.assertFalse(result["compatible"])
        self.assertEqual(["evidence_before_promotion"], result["missing_invariants"])

    def test_compatibility_passes_only_when_all_are_preserved(self):
        contract = {"domain_invariants": ["authority_external", "evidence_before_promotion"]}
        result = compatibility_gate(contract, {"preserved_invariants": contract["domain_invariants"]})
        self.assertTrue(result["compatible"])


class ReviewConvergenceTests(unittest.TestCase):
    def policy(self):
        return {"max_reviews": 3, "required_qualified_agreement": 2, "false_positive_rate_threshold": 0.10}

    def test_high_false_positive_reviewer_is_demoted(self):
        reviews = [
            {"reviewer_id": "r1", "false_positive_rate": 0.02, "verdict": "PASS"},
            {"reviewer_id": "r2", "false_positive_rate": 0.40, "verdict": "PASS"},
            {"reviewer_id": "r3", "false_positive_rate": 0.03, "verdict": "PASS"},
        ]
        result = evaluate_review_convergence(self.policy(), reviews)
        self.assertEqual("CONVERGED_PASS", result["decision"])
        self.assertEqual(["r2"], result["demoted_reviewers"])

    def test_ceiling_without_convergence_requires_human(self):
        reviews = [
            {"reviewer_id": "r1", "false_positive_rate": 0.02, "verdict": "PASS"},
            {"reviewer_id": "r2", "false_positive_rate": 0.03, "verdict": "FAIL"},
            {"reviewer_id": "r3", "false_positive_rate": 0.50, "verdict": "PASS"},
        ]
        result = evaluate_review_convergence(self.policy(), reviews)
        self.assertEqual("HUMAN_REQUIRED", result["decision"])
        self.assertTrue(result["ceiling_reached"])

    def test_no_early_pass_from_insufficient_agreement(self):
        result = evaluate_review_convergence(
            self.policy(),
            [{"reviewer_id": "r1", "false_positive_rate": 0.01, "verdict": "PASS"}],
        )
        self.assertEqual("CONTINUE_REVIEW", result["decision"])


if __name__ == "__main__":
    unittest.main()
