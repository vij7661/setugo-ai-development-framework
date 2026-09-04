import json
import unittest

from review_contract import StructuredReviewError, parse_structured_review


def valid_payload():
    return {
        "summary": "material defect",
        "findings": [
            {
                "summary": "retry policy is violated",
                "severity": "HIGH",
                "failure_class": "CODE DEFECT",
                "artifact_scope": ["production_code"],
            }
        ],
        "diagnosis": {"primary_failure_class": "CODE DEFECT", "contributors": []},
        "authorized_scope": ["production_code"],
        "changed_artifacts": ["CODE-1"],
        "evidence_refs": ["ci:1"],
    }


class ReviewContractTests(unittest.TestCase):
    def test_valid_json_is_normalized(self):
        parsed = parse_structured_review(json.dumps(valid_payload()))
        self.assertEqual(parsed["summary"], "material defect")
        self.assertEqual(parsed["findings"][0]["failure_class"], "CODE DEFECT")

    def test_single_json_fence_is_accepted(self):
        parsed = parse_structured_review("```json\n" + json.dumps(valid_payload()) + "\n```")
        self.assertEqual(parsed["authorized_scope"], ["production_code"])

    def test_surrounding_prose_is_rejected(self):
        with self.assertRaisesRegex(StructuredReviewError, "not one JSON object"):
            parse_structured_review("Here is the result: " + json.dumps(valid_payload()))

    def test_truncated_json_is_rejected(self):
        with self.assertRaises(StructuredReviewError):
            parse_structured_review('{"summary":"x","findings":[')

    def test_noncanonical_failure_class_is_rejected(self):
        payload = valid_payload()
        payload["findings"][0]["failure_class"] = "BUG"
        with self.assertRaisesRegex(StructuredReviewError, "not canonical"):
            parse_structured_review(json.dumps(payload))

    def test_missing_required_key_is_rejected(self):
        payload = valid_payload()
        payload.pop("evidence_refs")
        with self.assertRaisesRegex(StructuredReviewError, "missing required keys"):
            parse_structured_review(json.dumps(payload))


if __name__ == "__main__":
    unittest.main()
