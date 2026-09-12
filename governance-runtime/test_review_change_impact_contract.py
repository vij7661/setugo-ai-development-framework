import unittest

from review_change_impact_gate import validate_review_change_impact_contract
from reviewer_change_reconciliation_gate import validate_reviewer_change_reconciliation
from platform_candidate_review_v3 import validate_change_assessment_output

CANDIDATE = "a" * 40


def base_review_surface():
    return {
        "candidate_commit": CANDIDATE,
        "review_mode": "CLEAN_INDEPENDENT_REVIEW",
        "review_change_impact_contract": {
            "schema_version": 1,
            "deliberate_question": "Are changes required for this exact candidate?",
            "changes_required_vocabulary": ["YES", "NO", "INSUFFICIENT_EVIDENCE"],
            "required_output_fields": [
                "changes_required",
                "change_recommendations",
                "existing_system_impact",
                "verification_requirements",
                "missing_evidence",
            ],
            "required_recommendation_fields": [
                "finding_id",
                "minimum_required_change",
                "why_required",
                "affected_existing_surfaces",
                "regression_risks",
                "evidence_to_verify_fix",
            ],
            "require_existing_system_impact": True,
            "require_regression_risks": True,
            "require_verification_evidence": True,
            "require_missing_evidence": True,
            "reviewer_suggestions_non_authoritative": True,
            "prior_reviewer_conclusions_included": False,
        },
        "verification_evidence_manifest": {
            "schema_version": 1,
            "candidate_commit": CANDIDATE,
            "evidence_classes": [
                {"id": "EXACT_CANDIDATE_ARTIFACTS", "status": "PRESENT", "required_for_review": True, "refs": ["path:a.md"]},
                {"id": "BASE_TO_CANDIDATE_DIFF", "status": "PRESENT", "required_for_review": True, "refs": ["path:diff.txt"]},
                {"id": "APPLICABLE_CONTRACTS", "status": "PRESENT", "required_for_review": True, "refs": ["path:contract.md"]},
                {"id": "EXISTING_CODE_IMPACT_SURFACE", "status": "PRESENT", "required_for_review": True, "refs": ["path:impact.txt"]},
                {"id": "INTERFACES_SCHEMAS_STATE", "status": "PRESENT", "required_for_review": True, "refs": ["path:schema.txt"]},
                {"id": "CURRENT_TESTS_AND_RESULTS", "status": "PRESENT", "required_for_review": True, "refs": ["path:tests.txt"]},
                {"id": "KNOWN_FAILURES_AND_DEFERRED", "status": "PRESENT", "required_for_review": True, "refs": ["path:known.txt"]},
                {"id": "RUNTIME_EXECUTION_EVIDENCE", "status": "NOT_APPLICABLE", "required_for_review": False, "refs": [], "reason": "design-only review"},
            ],
        },
    }


class ReviewChangeImpactContractTests(unittest.TestCase):
    def test_complete_review_surface_ready(self):
        obj = base_review_surface()
        paths = ["a.md", "diff.txt", "contract.md", "impact.txt", "schema.txt", "tests.txt", "known.txt"]
        report = validate_review_change_impact_contract(obj, candidate_commit=CANDIDATE, available_artifact_paths=paths)
        self.assertEqual(report["result"], "REVIEW_CHANGE_IMPACT_READY", report["errors"])

    def test_required_evidence_missing_blocks(self):
        obj = base_review_surface()
        for item in obj["verification_evidence_manifest"]["evidence_classes"]:
            if item["id"] == "CURRENT_TESTS_AND_RESULTS":
                item["status"] = "UNAVAILABLE"
                item["reason"] = "not supplied"
        report = validate_review_change_impact_contract(obj, candidate_commit=CANDIDATE)
        self.assertEqual(report["result"], "REVIEW_CHANGE_IMPACT_NOT_READY")
        self.assertTrue(any(x.startswith("REVIEW_VERIFICATION_REQUIRED_EVIDENCE_NOT_PRESENT:CURRENT_TESTS_AND_RESULTS") for x in report["errors"]))

    def test_clean_mode_prior_conclusions_flag_blocks(self):
        obj = base_review_surface()
        obj["review_change_impact_contract"]["prior_reviewer_conclusions_included"] = True
        report = validate_review_change_impact_contract(obj, candidate_commit=CANDIDATE)
        self.assertIn("REVIEW_CHANGE_CLEAN_MODE_CONTAMINATION_FLAG_INVALID", report["errors"])


def valid_review_output():
    return {
        "change_assessment": {
            "changes_required": "YES",
            "change_recommendations": [{
                "finding_id": "F-1",
                "minimum_required_change": "centralize generation guard",
                "why_required": "predecessor state can bypass successor rules",
                "affected_existing_surfaces": ["runtime/cache.py"],
                "regression_risks": ["valid current-generation reads may be overblocked"],
                "evidence_to_verify_fix": "negative stale read plus positive current read",
            }],
            "existing_system_impact": {"direct_code": ["runtime/cache.py"]},
            "verification_requirements": ["negative stale read", "positive current read"],
            "missing_evidence": [],
        }
    }


class ReviewerOutputContractTests(unittest.TestCase):
    def test_change_assessment_output_valid(self):
        contract = base_review_surface()["review_change_impact_contract"]
        report = validate_change_assessment_output(valid_review_output(), contract)
        self.assertTrue(report["valid"], report["errors"])

    def test_missing_change_assessment_rejected(self):
        contract = base_review_surface()["review_change_impact_contract"]
        report = validate_change_assessment_output({}, contract)
        self.assertFalse(report["valid"])
        self.assertIn("REVIEW_CHANGE_ASSESSMENT_OUTPUT_REQUIRED", report["errors"])


def base_change_manifest():
    return {
        "findings": [{
            "id": "F-1",
            "disposition": "ACCEPT",
            "reviewer_change_assessment": {
                "changes_required": "YES",
                "minimum_required_change": "Bind cache reads to successor generation",
                "why_required": "predecessor state can remain authoritative",
                "affected_existing_surfaces": ["runtime/cache.py", "runtime/reader.py"],
                "regression_risks": ["valid cache reads may be overblocked"],
                "evidence_to_verify_fix": "negative stale-cache test plus positive current-generation cache test",
                "missing_evidence": [],
            },
            "independent_change_assessment": {
                "reviewer_change_considered": True,
                "reviewer_proposal_decision": "ADOPT_WITH_MODIFICATION",
                "rationale": "centralize the guard in the shared read boundary rather than duplicate checks",
                "evidence": "call graph shows both readers use the shared boundary",
            },
        }],
        "impact_manifest": {
            "direct_paths": ["runtime/cache.py"],
            "transitive_paths": ["runtime/reader.py"],
            "no_change_required_paths": [],
            "reviewer_claim_reconciliation": {},
        },
    }


class ReviewerChangeReconciliationTests(unittest.TestCase):
    def test_reviewer_change_and_impacts_reconciled(self):
        report = validate_reviewer_change_reconciliation(base_change_manifest())
        self.assertEqual(report["result"], "REVIEWER_CHANGE_RECONCILED", report["errors"])

    def test_unreconciled_reviewer_impact_blocks(self):
        obj = base_change_manifest()
        obj["findings"][0]["reviewer_change_assessment"]["affected_existing_surfaces"].append("runtime/unknown.py")
        report = validate_reviewer_change_reconciliation(obj)
        self.assertEqual(report["result"], "REVIEWER_CHANGE_NOT_RECONCILED")
        self.assertIn("REVIEWER_IMPACT_CLAIM_UNRESOLVED:F-1:runtime/unknown.py", report["errors"])

    def test_rejected_impact_claim_requires_evidence(self):
        obj = base_change_manifest()
        obj["findings"][0]["reviewer_change_assessment"]["affected_existing_surfaces"].append("runtime/unknown.py")
        obj["impact_manifest"]["reviewer_claim_reconciliation"]["runtime/unknown.py"] = {
            "disposition": "REVIEWER_CLAIM_REJECTED",
            "rationale": "not reachable from changed boundary",
            "evidence": "dependency graph has no path",
        }
        report = validate_reviewer_change_reconciliation(obj)
        self.assertEqual(report["result"], "REVIEWER_CHANGE_RECONCILED", report["errors"])


if __name__ == "__main__":
    unittest.main()
