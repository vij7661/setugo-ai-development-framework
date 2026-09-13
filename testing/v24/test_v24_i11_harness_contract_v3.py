import unittest
from v24_i11_harness_contract_v3 import (
    GovernedEndpointObservation, AuthorityEffectObservation,
    InsufficientEvidenceEndpointCondition, classify_negative,
)

D="a"*64
OBS=GovernedEndpointObservation("INSUFFICIENT_EVIDENCE","candidate",D,())
EFFECT=AuthorityEffectObservation("O",D,D,0,0)

class V5HarnessContractTests(unittest.TestCase):
    def cond(self, **kw):
        d=dict(
            case_execution_evidence_bundle_present=True,
            case_preconditions_valid=True,
            target_condition_evidence_present=True,
            target_condition_observed=True,
            missing_case_execution_evidence=False,
            endpoint_emitted_by_candidate=True,
            endpoint_trigger_evidence_digest=D,
            target_reason="target insufficiency condition",
        )
        d.update(kw)
        return InsufficientEvidenceEndpointCondition(**d)

    def test_ie_endpoint_can_pass_only_with_qualified_case_condition(self):
        self.assertEqual(classify_negative(
            expected_endpoint="INSUFFICIENT_EVIDENCE", observed=OBS, effect=EFFECT,
            fixture_valid=True, harness_valid=True, ie_condition=self.cond()
        ), "PASS")

    def test_missing_external_case_bundle_cannot_false_green(self):
        self.assertEqual(classify_negative(
            expected_endpoint="INSUFFICIENT_EVIDENCE", observed=OBS, effect=EFFECT,
            fixture_valid=True, harness_valid=True,
            ie_condition=self.cond(case_execution_evidence_bundle_present=False, missing_case_execution_evidence=True)
        ), "NOT_EXECUTABLE_EXTERNAL_EVIDENCE_REQUIRED")

    def test_unqualified_trigger_evidence_is_not_pass(self):
        self.assertEqual(classify_negative(
            expected_endpoint="INSUFFICIENT_EVIDENCE", observed=OBS, effect=EFFECT,
            fixture_valid=True, harness_valid=True,
            ie_condition=self.cond(target_condition_observed=False)
        ), "INSUFFICIENT_EVIDENCE")

    def test_candidate_must_emit_ie_endpoint(self):
        c=self.cond(endpoint_emitted_by_candidate=False)
        self.assertEqual(classify_negative(
            expected_endpoint="INSUFFICIENT_EVIDENCE", observed=OBS, effect=EFFECT,
            fixture_valid=True, harness_valid=True, ie_condition=c
        ), "INSUFFICIENT_EVIDENCE")

if __name__=="__main__":
    unittest.main()
