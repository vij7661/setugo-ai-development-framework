import unittest

from reviewer_independence import verify_independent_reviews


def review(reviewer_id, provider, model, sku, qualification_ref, prompt_lineage, context_lineage, foundation_lineage):
    return {
        "reviewer_id": reviewer_id,
        "provider": provider,
        "model": model,
        "sku": sku,
        "qualification_ref": qualification_ref,
        "prompt_lineage": prompt_lineage,
        "context_lineage": context_lineage,
        "foundation_lineage": foundation_lineage,
    }


class ExpFReviewerIndependenceTests(unittest.TestCase):
    def test_distinct_ids_same_lineage_do_not_count_as_independent(self):
        r1 = review("r1", "p", "m", "s", "q1", "prompt-a", "ctx-a", "family-x")
        r2 = review("r2", "p", "m", "s", "q1", "prompt-a", "ctx-a", "family-x")
        result = verify_independent_reviews([r1, r2], 2)
        self.assertFalse(result["independent"])
        self.assertEqual(1, result["independent_count"])

    def test_same_foundation_different_provider_path_is_not_independent(self):
        r1 = review("r1", "direct-provider", "model-x", "sku-a", "q1", "prompt-a", "ctx-a", "foundation-model-x")
        r2 = review("r2", "router-provider", "alias-x", "sku-b", "q2", "prompt-b", "ctx-b", "foundation-model-x")
        result = verify_independent_reviews([r1, r2], 2)
        self.assertFalse(result["independent"])
        self.assertEqual(["r2"], result["correlated_or_invalid_reviewers"])

    def test_same_provider_model_distinct_sku_still_requires_foundation_diversity(self):
        r1 = review("r1", "p", "m", "sku-a", "q1", "prompt-a", "ctx-a", "family-a")
        r2 = review("r2", "p", "m", "sku-b", "q2", "prompt-b", "ctx-b", "family-b")
        result = verify_independent_reviews([r1, r2], 2)
        self.assertTrue(result["independent"])

    def test_duplicate_reviewer_identity_is_rejected(self):
        r1 = review("r1", "p1", "m1", "s1", "q1", "prompt-a", "ctx-a", "family-a")
        r2 = review("r1", "p2", "m2", "s2", "q2", "prompt-b", "ctx-b", "family-b")
        self.assertFalse(verify_independent_reviews([r1, r2], 2)["independent"])

    def test_missing_foundation_lineage_fails_closed(self):
        bad = {"reviewer_id": "r1", "provider": "p", "model": "m", "sku": "s", "qualification_ref": "q", "prompt_lineage": "p", "context_lineage": "c"}
        self.assertFalse(verify_independent_reviews([bad], 1)["independent"])

    def test_two_distinct_complete_foundation_lineages_pass(self):
        r1 = review("r1", "p1", "m1", "s1", "q1", "prompt-a", "ctx-a", "family-a")
        r2 = review("r2", "p2", "m2", "s2", "q2", "prompt-b", "ctx-b", "family-b")
        result = verify_independent_reviews([r1, r2], 2)
        self.assertTrue(result["independent"])
        self.assertEqual(2, result["independent_count"])


if __name__ == "__main__":
    unittest.main()
