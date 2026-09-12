import unittest

from change_control_gate import (
    READY,
    NOT_READY,
    PACKET_REPAIR,
    validate_change_control,
)

BASE = "a" * 40
HEAD = "b" * 40


def base_manifest():
    return {
        "schema_version": 1,
        "reviewed_candidate_commit": BASE,
        "successor_commit": HEAD,
        "change_class": "IMPLEMENTATION_DEFECT",
        "design_candidate_changed": False,
        "all_findings_adjudicated": True,
        "intermediate_partial_repair": False,
        "findings": [
            {
                "id": "F-1",
                "severity": "HIGH",
                "disposition": "ACCEPT",
                "affected_invariant": "exact candidate binding",
                "root_cause_class": "STALE_BINDING",
                "requires_change": True,
                "same_family_consecutive_reviews": 1,
                "remediation_scope": "LOCAL_FIRST_OCCURRENCE",
            }
        ],
        "impact_manifest": {
            "direct_paths": ["governance-runtime/a.py"],
            "transitive_paths": ["governance-runtime/b.py"],
            "no_change_required_paths": [],
            "contract_or_state_changed": False,
            "compatibility_strategy": "NOT_APPLICABLE",
            "cleanup_no_semantic_change_evidence": {},
        },
        "changed_path_classification": {
            "governance-runtime/a.py": "INTENDED_REMEDIATION",
            "governance-runtime/b.py": "REQUIRED_TRANSITIVE_CHANGE",
            "governance-runtime/test_a.py": "TEST_OR_EVIDENCE_CHANGE",
        },
        "validation_obligations": [
            {"id": "targeted", "required": True, "status": "PASS", "evidence": "12/12 targeted tests"},
            {"id": "regression", "required": True, "status": "PASS", "evidence": "full affected regression green"},
            {"id": "negative", "required": True, "status": "PASS", "evidence": "old bypass rejected"},
            {"id": "positive", "required": True, "status": "PASS", "evidence": "valid flow preserved"},
        ],
        "required_cleanliness_checks": ["lint", "unit"],
        "cleanliness_checks": {
            "lint": {"status": "PASS", "evidence": "lint exit 0"},
            "unit": {"status": "PASS", "evidence": "unit suite exit 0"},
        },
        "previous_green_reachable_surface_regressed": False,
        "test_removed_or_weakened_without_disposition": False,
        "production_test_only_branch_added": False,
        "duplicate_authoritative_logic_added": False,
    }


class ChangeControlGateTests(unittest.TestCase):
    def test_coherent_change_ready(self):
        m = base_manifest()
        r = validate_change_control(m, [
            "governance-runtime/a.py",
            "governance-runtime/b.py",
            "governance-runtime/test_a.py",
        ])
        self.assertEqual(r["result"], READY, r["errors"])

    def test_unaccounted_diff_blocks(self):
        m = base_manifest()
        r = validate_change_control(m, [
            "governance-runtime/a.py",
            "governance-runtime/b.py",
            "governance-runtime/test_a.py",
            "governance-runtime/hidden.py",
        ])
        self.assertEqual(r["result"], NOT_READY)
        self.assertIn("UNACCOUNTED_CHANGE:governance-runtime/hidden.py", r["errors"])

    def test_repeated_family_requires_generalized_invariant(self):
        m = base_manifest()
        m["findings"][0]["same_family_consecutive_reviews"] = 2
        r = validate_change_control(m, [
            "governance-runtime/a.py",
            "governance-runtime/b.py",
            "governance-runtime/test_a.py",
        ])
        self.assertEqual(r["result"], NOT_READY)
        self.assertTrue(any(x.startswith("CHANGE_REPEATED_FAMILY_REQUIRES_GENERALIZATION") for x in r["errors"]))

    def test_required_validation_not_pass_blocks(self):
        m = base_manifest()
        m["validation_obligations"][1]["status"] = "NOT_VERIFIED"
        r = validate_change_control(m, [
            "governance-runtime/a.py",
            "governance-runtime/b.py",
            "governance-runtime/test_a.py",
        ])
        self.assertEqual(r["result"], NOT_READY)
        self.assertTrue(any(x.startswith("CHANGE_REQUIRED_VALIDATION_NOT_PASS") for x in r["errors"]))

    def test_contract_change_requires_strategy(self):
        m = base_manifest()
        m["impact_manifest"]["contract_or_state_changed"] = True
        m["impact_manifest"]["compatibility_strategy"] = "NOT_APPLICABLE"
        r = validate_change_control(m, [
            "governance-runtime/a.py",
            "governance-runtime/b.py",
            "governance-runtime/test_a.py",
        ])
        self.assertEqual(r["result"], NOT_READY)
        self.assertIn("CHANGE_COMPATIBILITY_STRATEGY_REQUIRED", r["errors"])

    def test_packet_process_repair_does_not_require_design_version(self):
        m = base_manifest()
        m["change_class"] = "PACKET_PROCESS_DEFECT"
        m["findings"] = [{
            "id": "P-1",
            "severity": "MEDIUM",
            "disposition": "PACKET_PROCESS_DEFECT",
            "requires_change": False,
            "same_family_consecutive_reviews": 0,
        }]
        m["impact_manifest"]["direct_paths"] = []
        m["impact_manifest"]["transitive_paths"] = []
        m["changed_path_classification"] = {
            "review-packets/packet.md": "TEST_OR_EVIDENCE_CHANGE",
        }
        r = validate_change_control(m, ["review-packets/packet.md"])
        self.assertEqual(r["result"], PACKET_REPAIR, r["errors"])

    def test_duplicate_authoritative_logic_blocks(self):
        m = base_manifest()
        m["duplicate_authoritative_logic_added"] = True
        r = validate_change_control(m, [
            "governance-runtime/a.py",
            "governance-runtime/b.py",
            "governance-runtime/test_a.py",
        ])
        self.assertEqual(r["result"], NOT_READY)
        self.assertIn("CHANGE_DUPLICATE_AUTHORITY_LOGIC_REJECTED", r["errors"])


if __name__ == "__main__":
    unittest.main()
