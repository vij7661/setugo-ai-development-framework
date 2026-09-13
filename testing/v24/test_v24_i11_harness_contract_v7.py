"""Construction tests for the exact reviewed V8 Harness V7 contract.

No WDPC scientific case is executed here.
"""
import unittest

from v24_i11_harness_contract_v7 import (
    EXECUTION_CLASS_POLICY,
    HARNESS_VERSION,
    IE_TARGET_REASONS,
    REQUIRED_CONJUNCTIVE_INVARIANTS,
    InsufficientEvidenceEndpointCondition,
    expected_stdlib_fallback_digest,
)


class HarnessV7ReviewedContractTests(unittest.TestCase):
    def test_exact_harness_version(self):
        self.assertEqual(HARNESS_VERSION, "1.6.0-PLAN-REVIEW")

    def test_exact_ie_case_set_and_458_reason(self):
        self.assertEqual(
            set(IE_TARGET_REASONS),
            {
                "WDPC-443","WDPC-458","WDPC-472","WDPC-473","WDPC-474",
                "WDPC-476","WDPC-480","WDPC-497","WDPC-500","WDPC-502","WDPC-504",
            },
        )
        self.assertEqual(
            IE_TARGET_REASONS["WDPC-458"],
            "required external completeness authority is present but independence is unproven",
        )

    def test_ie_reason_must_match_exactly(self):
        good=InsufficientEvidenceEndpointCondition(
            case_id="WDPC-458",
            case_execution_evidence_bundle_present=True,
            case_preconditions_valid=True,
            target_condition_evidence_present=True,
            target_condition_observed=True,
            missing_case_execution_evidence=False,
            endpoint_emitted_by_candidate=True,
            endpoint_trigger_evidence_digest="a"*64,
            target_reason=IE_TARGET_REASONS["WDPC-458"],
        )
        bad=InsufficientEvidenceEndpointCondition(**{**good.__dict__,"target_reason":"wrong nonempty reason"})
        self.assertTrue(good.qualifies_for_endpoint_pass)
        self.assertFalse(bad.qualifies_for_endpoint_pass)

    def test_457_invariant_is_exact(self):
        self.assertEqual(
            REQUIRED_CONJUNCTIVE_INVARIANTS["WDPC-457"],
            ("HISTORICAL_RESULT_UNCHANGED",),
        )

    def test_blocked_class_consumes_no_execution_evidence(self):
        p=EXECUTION_CLASS_POLICY["BLOCKED_BY_I1_SEMANTIC_QUALIFICATION"]
        self.assertFalse(p.synthetic_execution_permitted)
        self.assertFalse(p.external_or_manual_evidence_required)
        self.assertFalse(p.operational_pass_permitted_without_external_evidence)

    def test_stdlib_fallback_digest_is_deterministic(self):
        self.assertEqual(expected_stdlib_fallback_digest("3.12.7"),expected_stdlib_fallback_digest("3.12.7"))
        self.assertNotEqual(expected_stdlib_fallback_digest("3.12.7"),expected_stdlib_fallback_digest("3.12.8"))

if __name__=="__main__":
    unittest.main()
