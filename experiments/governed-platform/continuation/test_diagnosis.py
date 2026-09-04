import unittest

from diagnosis import validate_diagnosis


class DiagnosisAuthorityTests(unittest.TestCase):
    def test_code_defect_allows_only_code_scope(self):
        result = validate_diagnosis({
            "primary_failure_class": "CODE DEFECT",
            "contributing_failure_classes": [],
            "authorized_artifact_classes": ["production_code"],
            "requirement_resolution_required": False,
            "evidence_refs": ["ci:123"],
        })
        self.assertEqual(result["decision"], "REPAIR")
        self.assertEqual(result["authorized_artifacts"], ["production_code"])

    def test_requirement_unresolved_has_zero_mutation_authority(self):
        result = validate_diagnosis({
            "primary_failure_class": "REQUIREMENT UNRESOLVED",
            "contributing_failure_classes": [],
            "authorized_artifact_classes": [],
            "requirement_resolution_required": True,
            "evidence_refs": ["contract:conflict"],
        })
        self.assertEqual(result["decision"], "REQUEST_HUMAN")
        self.assertEqual(result["allowed_artifacts"], [])
        self.assertTrue(result["human_required"])

    def test_requirement_contributor_blocks_otherwise_valid_code_authority(self):
        result = validate_diagnosis({
            "primary_failure_class": "CODE DEFECT",
            "contributing_failure_classes": ["REQUIREMENT UNRESOLVED"],
            "authorized_artifact_classes": [],
            "requirement_resolution_required": True,
            "evidence_refs": ["ci:123", "requirement:ambiguous"],
        })
        self.assertEqual(result["allowed_artifacts"], [])
        self.assertEqual(result["authority"], "NONE")

    def test_mixed_code_and_fixture_preserves_both_scopes(self):
        result = validate_diagnosis({
            "primary_failure_class": "CODE DEFECT",
            "contributing_failure_classes": ["FIXTURE-DATA DEFECT"],
            "authorized_artifact_classes": ["production_code", "fixtures"],
            "requirement_resolution_required": False,
            "evidence_refs": ["provider:timeout", "fixture:charged"],
        })
        self.assertEqual(result["primary_failure_class"], "CODE DEFECT")
        self.assertIn("production_code", result["allowed_artifacts"])
        self.assertIn("fixtures", result["allowed_artifacts"])

    def test_wrong_artifact_scope_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_diagnosis({
                "primary_failure_class": "FIXTURE-DATA DEFECT",
                "contributing_failure_classes": [],
                "authorized_artifact_classes": ["tests"],
                "requirement_resolution_required": False,
                "evidence_refs": ["fixture:state"],
            })

    def test_primary_and_contributor_cannot_duplicate(self):
        with self.assertRaises(ValueError):
            validate_diagnosis({
                "primary_failure_class": "TEST DEFECT",
                "contributing_failure_classes": ["TEST DEFECT"],
                "authorized_artifact_classes": ["tests"],
                "requirement_resolution_required": False,
                "evidence_refs": ["test:expectation"],
            })


if __name__ == "__main__":
    unittest.main()
