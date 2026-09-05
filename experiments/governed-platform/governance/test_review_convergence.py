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
        return {
            "max_reviews": 3,
            "required_qualified_agreement": 2,
            "false_positive_rate_threshold": 0.10,
            "review_role": "JUDGE",
            "task_class": "SECURITY_REVIEW",
            "risk_tier": "HIGH",
        }

    def perf(self, reviewer, rate, epoch=1):
        return {
            "reviewer_id": reviewer,
            "false_positive_rate": rate,
            "role": "JUDGE",
            "task_class": "SECURITY_REVIEW",
            "risk_tier": "HIGH",
            "independently_adjudicated": True,
            "evidence_ref": f"perf-{reviewer}-{epoch}",
            "performance_epoch": epoch,
        }

    def test_high_false_positive_reviewer_is_demoted(self):
        reviews = [
            {"reviewer_id": "r1", "verdict": "PASS"},
            {"reviewer_id": "r2", "verdict": "PASS"},
            {"reviewer_id": "r3", "verdict": "PASS"},
        ]
        records = [self.perf("r1", 0.02), self.perf("r2", 0.40), self.perf("r3", 0.03)]
        result = evaluate_review_convergence(self.policy(), reviews, records)
        self.assertEqual("CONVERGED_PASS", result["decision"])
        self.assertEqual(["r2"], result["demoted_reviewers"])

    def test_ceiling_without_convergence_escalates(self):
        reviews = [
            {"reviewer_id": "r1", "verdict": "PASS"},
            {"reviewer_id": "r2", "verdict": "FAIL"},
            {"reviewer_id": "r3", "verdict": "PASS"},
        ]
        records = [self.perf("r1", 0.02), self.perf("r2", 0.03), self.perf("r3", 0.50)]
        result = evaluate_review_convergence(self.policy(), reviews, records)
        self.assertEqual("CEILING_REACHED_ESCALATE", result["decision"])
        self.assertTrue(result["ceiling_reached"])

    def test_no_early_pass_from_insufficient_agreement(self):
        result = evaluate_review_convergence(
            self.policy(),
            [{"reviewer_id": "r1", "verdict": "PASS"}],
            [self.perf("r1", 0.01)],
        )
        self.assertEqual("CONTINUE_REVIEW", result["decision"])


if __name__ == "__main__":
    unittest.main()
