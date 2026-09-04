import unittest
from experiments.governed_platform.continuation.controller import decide


class ControllerTests(unittest.TestCase):
    def test_success_continues_without_write_authority(self):
        result = decide({"conclusion": "success", "case_id": "X"})
        self.assertEqual(result["decision"], "CONTINUE")
        self.assertEqual(result["authority"], "EVIDENCE_ONLY")

    def test_unclassified_failure_must_diagnose(self):
        result = decide({"conclusion": "failure", "case_id": "X"})
        self.assertEqual(result["decision"], "DIAGNOSE")
        self.assertEqual(result["authority"], "NONE_UNTIL_CLASSIFIED")

    def test_environment_failure_only_grants_environment_scope(self):
        result = decide({"conclusion": "failure", "case_id": "X", "classification": "ENVIRONMENT-TOOLING DEFECT"})
        self.assertEqual(result["decision"], "REPAIR")
        self.assertEqual(result["allowed_artifacts"], ["ci", "tooling", "environment_config", "build_config"])
        self.assertNotIn("production_code", result["allowed_artifacts"])

    def test_test_defect_cannot_modify_production(self):
        result = decide({"conclusion": "failure", "case_id": "X", "classification": "TEST DEFECT"})
        self.assertEqual(result["allowed_artifacts"], ["tests", "test_harness"])

    def test_requirement_unresolved_requires_human(self):
        result = decide({"conclusion": "failure", "case_id": "X", "classification": "REQUIREMENT UNRESOLVED"})
        self.assertEqual(result["decision"], "REQUEST_HUMAN")
        self.assertEqual(result["authority"], "NONE")
        self.assertTrue(result["human_required"])

    def test_repair_budget_exhaustion_requires_human(self):
        result = decide({"conclusion": "failure", "case_id": "X", "repair_attempt": 2, "max_repair_attempts": 2, "classification": "CODE DEFECT"})
        self.assertEqual(result["decision"], "REQUEST_HUMAN")
        self.assertEqual(result["authority"], "NONE")


if __name__ == "__main__":
    unittest.main()
