import unittest

from reviewer_independence import verify_independent_reviews


def review(reviewer_id, provider, model, sku, qualification_ref, prompt_lineage, context_lineage):
    return {
        "reviewer_id": reviewer_id,
        "provider": provider,
        "model": model,
        "sku": sku,
        "qualification_ref": qualification_ref,
        "prompt_lineage": prompt_lineage,
        "context_lineage": context_lineage,
    }


class ExpFReviewerIndependenceTests(unittest.TestCase):
    def test_distinct_ids_same_lineage_do_not_count_as_independent(self):
        r1 = review("r1", "p", "m", "s", "q1", "prompt-a", "ctx-a")
        r2 = review("r2", "p", "m", "s", "q1", "prompt-a", "ctx-a")
        result = verify_independent_reviews([r1, r2], 2)
        self.assertFalse(result["independent"])
        self.assertEqual(1, result["independent_count"])

    def test_same_provider_model_but_distinct_sku_and_lineage_can_be_independent(self):
        r1 = review("r1", "p", "m", "sku-a", "q1", "prompt-a", "ctx-a")
        r2 = review("r2", "p", "m", "sku-b", "q2", "prompt-b", "ctx-b")
        result = verify_independent_reviews([r1, r2], 2)
        self.assertTrue(result["independent"])

    def test_duplicate_reviewer_identity_is_rejected(self):
        r1 = review("r1", "p1", "m1", "s1", "q1", "prompt-a", "ctx-a")
        r2 = review("r1", "p2", "m2", "s2", "q2", "prompt-b", "ctx-b")
        result = verify_independent_reviews([r1, r2], 2)
        self.assertFalse(result["independent"])

    def test_missing_lineage_metadata_fails_closed(self):
        bad = {"reviewer_id": "r1", "provider": "p", "model": "m"}
        result = verify_independent_reviews([bad], 1)
        self.assertFalse(result["independent"])

    def test_two_distinct_complete_lineages_pass(self):
        r1 = review("r1", "p1", "m1", "s1", "q1", "prompt-a", "ctx-a")
        r2 = review("r2", "p2", "m2", "s2", "q2", "prompt-b", "ctx-b")
        result = verify_independent_reviews([r1, r2], 2)
        self.assertTrue(result["independent"])
        self.assertEqual(2, result["independent_count"])


if __name__ == "__main__":
    unittest.main()
