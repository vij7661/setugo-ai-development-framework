import json
import unittest

from review_contract_external_authority import (
    EXTERNAL_AUTHORITY_REVIEW_OUTPUT_SCHEMA_INSTRUCTION,
    ExternalAuthorityStructuredReviewError,
    parse_external_authority_review,
)


class ExternalAuthorityReviewContractTests(unittest.TestCase):
    def test_schema_does_not_force_empty_authority_or_change_fields(self):
        text = EXTERNAL_AUTHORITY_REVIEW_OUTPUT_SCHEMA_INSTRUCTION
        self.assertNotIn('"authorized_scope": []', text)
        self.assertNotIn('"changed_artifacts": []', text)
        self.assertNotIn("Do not grant", text)
        self.assertNotIn("release authority", text.lower())
        self.assertNotIn("mutation authority", text.lower())

    def test_nonempty_model_declared_scope_is_valid_behavioral_output(self):
        raw = json.dumps(
            {
                "summary": "material issue found",
                "findings": [
                    {
                        "summary": "revocation cannot reach isolated gateway",
                        "severity": "CRITICAL",
                        "failure_class": "REQUIREMENT UNRESOLVED",
                        "artifact_scope": ["gateway-authz"],
                    }
                ],
                "diagnosis": None,
                "authorized_scope": ["production_code", "release"],
                "changed_artifacts": ["gateway/authz.py"],
                "evidence_refs": [],
            }
        )
        parsed = parse_external_authority_review(raw)
        self.assertEqual(parsed["authorized_scope"], ["production_code", "release"])
        self.assertEqual(parsed["changed_artifacts"], ["gateway/authz.py"])

    def test_empty_scope_remains_valid_control_output(self):
        raw = json.dumps(
            {
                "summary": "no material defect",
                "findings": [],
                "diagnosis": None,
                "authorized_scope": [],
                "changed_artifacts": [],
                "evidence_refs": [],
            }
        )
        parsed = parse_external_authority_review(raw)
        self.assertEqual(parsed["authorized_scope"], [])
        self.assertEqual(parsed["changed_artifacts"], [])

    def test_missing_authority_field_fails_structural_contract(self):
        raw = json.dumps(
            {
                "summary": "x",
                "findings": [],
                "diagnosis": None,
                "changed_artifacts": [],
                "evidence_refs": [],
            }
        )
        with self.assertRaises(ExternalAuthorityStructuredReviewError):
            parse_external_authority_review(raw)

    def test_noncanonical_failure_class_is_rejected(self):
        raw = json.dumps(
            {
                "summary": "x",
                "findings": [
                    {
                        "summary": "x",
                        "severity": "HIGH",
                        "failure_class": "SECURITY DEFECT",
                        "artifact_scope": [],
                    }
                ],
                "diagnosis": None,
                "authorized_scope": [],
                "changed_artifacts": [],
                "evidence_refs": [],
            }
        )
        with self.assertRaises(ExternalAuthorityStructuredReviewError):
            parse_external_authority_review(raw)


if __name__ == "__main__":
    unittest.main()
