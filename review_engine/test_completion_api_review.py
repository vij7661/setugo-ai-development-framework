import unittest

from review_engine.completion_api_review import (
    MANDATORY_DIMENSIONS,
    validate_completion_review_response,
)


class CompletionAPIReviewSemanticTests(unittest.TestCase):
    request_id = "REV-RE-COMP-001"
    candidate = "a" * 40
    model = "gemini-2.5-flash"

    def supported_review(self):
        return {
            "review_request_id": self.request_id,
            "reviewed_artifact_commit": self.candidate,
            "reviewer": {"provider": "gemini", "model": self.model},
            "disposition": "PASS",
            "findings": [],
            "evidence_assessment": "All mandatory dimensions inspected directly.",
            "independence_attestation": "BLIND_TO_PROPOSER_CONCLUSION",
            "review_coverage": [
                {
                    "dimension_id": dimension,
                    "status": "TESTED_SUPPORTED",
                    "evidence": [f"evidence:{dimension}"],
                    "assessment": "supported",
                }
                for dimension in MANDATORY_DIMENSIONS
            ],
        }

    def validate(self, review):
        return validate_completion_review_response(
            review,
            review_request_id=self.request_id,
            candidate_sha=self.candidate,
            executed_provider="gemini",
            executed_model=self.model,
        )

    def test_pass_requires_every_mandatory_dimension(self):
        review = self.supported_review()
        review["review_coverage"].pop()
        result = self.validate(review)
        self.assertFalse(result["valid"])
        self.assertIn("missing mandatory dimensions", " ".join(result["errors"]))

    def test_pass_with_all_supported_dimensions_is_valid(self):
        result = self.validate(self.supported_review())
        self.assertTrue(result["valid"])
        self.assertEqual(result["effective_disposition"], "PASS")
        self.assertTrue(result["can_close_authority_bypasses"])

    def test_pass_with_medium_finding_is_rejected(self):
        review = self.supported_review()
        review["findings"] = [{
            "id": "F1",
            "severity": "MEDIUM",
            "title": "bypass",
            "evidence": "review_engine/example.py:10",
            "impact": "authority bypass",
            "required_change": "repair",
        }]
        result = self.validate(review)
        self.assertFalse(result["valid"])
        self.assertIn("PASS contradicts", " ".join(result["errors"]))

    def test_candidate_mismatch_is_rejected(self):
        review = self.supported_review()
        review["reviewed_artifact_commit"] = "b" * 40
        result = self.validate(review)
        self.assertFalse(result["valid"])
        self.assertIn("reviewed_artifact_commit mismatch", result["errors"])

    def test_self_declared_provider_cannot_disagree_with_execution(self):
        review = self.supported_review()
        review["reviewer"] = {"provider": "deepseek", "model": "deepseek"}
        result = self.validate(review)
        self.assertFalse(result["valid"])
        self.assertIn("reviewer provider content claim disagrees with execution envelope", result["errors"])

    def test_changes_required_needs_defect_or_blocking_finding(self):
        review = self.supported_review()
        review["disposition"] = "CHANGES_REQUIRED"
        result = self.validate(review)
        self.assertFalse(result["valid"])
        self.assertIn("CHANGES_REQUIRED requires defective coverage or blocking finding", result["errors"])

    def test_changes_required_with_defect_is_valid_but_cannot_close(self):
        review = self.supported_review()
        review["disposition"] = "CHANGES_REQUIRED"
        review["review_coverage"][0]["status"] = "TESTED_DEFECT_FOUND"
        review["findings"] = [{
            "id": "F1",
            "severity": "HIGH",
            "title": "authority defect",
            "evidence": "review_engine/example.py:1",
            "impact": "false green",
            "required_change": "repair",
        }]
        result = self.validate(review)
        self.assertTrue(result["valid"])
        self.assertEqual(result["effective_disposition"], "CHANGES_REQUIRED")
        self.assertFalse(result["can_close_authority_bypasses"])

    def test_insufficient_evidence_requires_incomplete_dimension(self):
        review = self.supported_review()
        review["disposition"] = "INSUFFICIENT_EVIDENCE"
        review["review_coverage"][0]["status"] = "NOT_TESTED"
        review["review_coverage"][0]["evidence"] = []
        result = self.validate(review)
        self.assertTrue(result["valid"])
        self.assertFalse(result["can_close_authority_bypasses"])


if __name__ == "__main__":
    unittest.main()
