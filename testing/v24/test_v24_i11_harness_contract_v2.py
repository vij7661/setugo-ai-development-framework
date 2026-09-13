import hashlib
import unittest

from v24_i11_harness_contract_v2 import (
    AuthorityEffectObservation,
    CaseRunBinding,
    ConjunctiveAssertionObservation,
    EnvironmentIdentity,
    EXECUTION_CLASS_POLICY,
    GovernedEndpointObservation,
    classify_conjunctive_negative,
    classify_negative,
    validate_binding,
    validate_environment,
)

H="a"*64

class V24I11HarnessContractV2Tests(unittest.TestCase):
    def test_execution_classes_all_have_policy(self):
        self.assertEqual(7, len(EXECUTION_CLASS_POLICY))
        self.assertFalse(EXECUTION_CLASS_POLICY["BLOCKED_BY_I1_SEMANTIC_QUALIFICATION"].synthetic_execution_permitted)
        self.assertFalse(EXECUTION_CLASS_POLICY["REFERENCE_MECHANISM_ONLY"].operational_pass_permitted_without_external_evidence)

    def test_blocked_case_requires_blocked_status(self):
        b=CaseRunBinding("WDPC-469","r",H,H,H,"1.1.0-PLAN-REVIEW","db9e4b349fd26e128f4486878a4af64929000a7c","9836dc3ff233cca582f485434fc1c6494cf7eb05","d68cbccdceebad88715c8b37ddfcd524fc16ce8a","V24",(H,),H,H,"NOT_EXECUTED")
        self.assertIn("BLOCKED_CASE_STATUS_REQUIRED", validate_binding(b,plan_body_sha256=H,plan_packet_blob_sha=H,harness_blob_sha=H))

    def test_blocked_case_accepts_blocked_status(self):
        b=CaseRunBinding("WDPC-495","r",H,H,H,"1.1.0-PLAN-REVIEW","db9e4b349fd26e128f4486878a4af64929000a7c","9836dc3ff233cca582f485434fc1c6494cf7eb05","d68cbccdceebad88715c8b37ddfcd524fc16ce8a","V24",(H,),H,H,"BLOCKED_BY_I1_SEMANTIC_QUALIFICATION")
        self.assertNotIn("BLOCKED_CASE_STATUS_REQUIRED", validate_binding(b,plan_body_sha256=H,plan_packet_blob_sha=H,harness_blob_sha=H))

    def test_conjunctive_requires_all_invariants(self):
        endpoint=GovernedEndpointObservation("AUTHORITY_EVIDENCE_SOURCE_INVALID","x",H)
        obs=ConjunctiveAssertionObservation(endpoint,("HISTORICAL_RESULT_UNCHANGED",),(),())
        effect=AuthorityEffectObservation("O-HISTORY",H,H,0,0)
        self.assertEqual("FAIL_CODE_DEFECT", classify_conjunctive_negative(expected_endpoint="AUTHORITY_EVIDENCE_SOURCE_INVALID",observation=obs,effect=effect,fixture_valid=True,harness_valid=True))

    def test_conjunctive_pass_requires_endpoint_invariant_and_zero_effect(self):
        endpoint=GovernedEndpointObservation("AUTHORITY_EVIDENCE_SOURCE_INVALID","x",H)
        obs=ConjunctiveAssertionObservation(endpoint,("HISTORICAL_RESULT_UNCHANGED",),("HISTORICAL_RESULT_UNCHANGED",),(H,))
        effect=AuthorityEffectObservation("O-HISTORY",H,H,0,0)
        self.assertEqual("PASS", classify_conjunctive_negative(expected_endpoint="AUTHORITY_EVIDENCE_SOURCE_INVALID",observation=obs,effect=effect,fixture_valid=True,harness_valid=True))

    def test_diagnostic_cannot_alias_missing_endpoint(self):
        obs=GovernedEndpointObservation(None,"x",H,("AUTHORITY_ADMISSION_REQUIRED",))
        effect=AuthorityEffectObservation("O-UNIVERSE",H,H,0,0)
        self.assertEqual("FAIL_CODE_DEFECT", classify_negative(expected_endpoint="AUTHORITY_ADMISSION_REQUIRED",observed=obs,effect=effect,fixture_valid=True,harness_valid=True))

    def test_stdlib_no_pip_fallback_is_valid(self):
        env=EnvironmentIdentity("3.12.7",H,H,H,"STDLIB_ONLY_PIP_UNAVAILABLE","UTC","0",24011,"FROZEN_LOGICAL_CLOCK")
        self.assertEqual([], validate_environment(env))

if __name__ == "__main__":
    unittest.main()
