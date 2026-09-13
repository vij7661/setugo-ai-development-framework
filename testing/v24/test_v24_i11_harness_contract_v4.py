import unittest
from v24_i11_harness_contract_v4 import (
    AuthorityEffectObservation,
    CaseRunBinding,
    EnvironmentIdentity,
    GovernedEndpointObservation,
    InsufficientEvidenceEndpointCondition,
    classify_negative,
    validate_binding,
    validate_environment,
)

D = "a"*64
OBS_IE = GovernedEndpointObservation("INSUFFICIENT_EVIDENCE", "candidate", D, ())
EFFECT = AuthorityEffectObservation("O", D, D, 0, 0)

class HarnessV4Tests(unittest.TestCase):
    def binding(self, case_id="WDPC-431", status="NOT_EXECUTED"):
        return CaseRunBinding(
            case_id=case_id,
            run_id="r",
            packet_sha256="b"*64,
            plan_body_sha256="c"*64,
            plan_packet_blob_sha="d"*40,
            harness_blob_sha="e"*40,
            harness_version="1.3.0-PLAN-REVIEW",
            design_sha="db9e4b349fd26e128f4486878a4af64929000a7c",
            implementation_sha="9836dc3ff233cca582f485434fc1c6494cf7eb05",
            implementation_tree="d68cbccdceebad88715c8b37ddfcd524fc16ce8a",
            governance_generation="V24",
            target_module_blobs=("f"*40,),
            fixture_digest="1"*64,
            environment_digest="2"*64,
            case_status=status,
        )

    def ie(self, case_id="WDPC-473", **kw):
        d = dict(
            case_id=case_id,
            case_execution_evidence_bundle_present=True,
            case_preconditions_valid=True,
            target_condition_evidence_present=True,
            target_condition_observed=True,
            missing_case_execution_evidence=False,
            endpoint_emitted_by_candidate=True,
            endpoint_trigger_evidence_digest="3"*64,
            target_reason="preregistered target insufficiency",
        )
        d.update(kw)
        return InsufficientEvidenceEndpointCondition(**d)

    def test_packet_sha_is_load_bearing(self):
        b=self.binding()
        p=validate_binding(b,packet_sha256="9"*64,plan_body_sha256="c"*64,plan_packet_blob_sha="d"*40,harness_blob_sha="e"*40)
        self.assertIn("PLAN_PACKET_SHA256_MISMATCH", p)

    def test_only_469_495_may_use_i1_blocked_status(self):
        b=self.binding("WDPC-431", "BLOCKED_BY_I1_SEMANTIC_QUALIFICATION")
        p=validate_binding(b,packet_sha256="b"*64,plan_body_sha256="c"*64,plan_packet_blob_sha="d"*40,harness_blob_sha="e"*40)
        self.assertIn("NONBLOCKED_CASE_CANNOT_USE_I1_BLOCKED_STATUS", p)

    def test_469_requires_blocked_status(self):
        b=self.binding("WDPC-469", "NOT_EXECUTED")
        p=validate_binding(b,packet_sha256="b"*64,plan_body_sha256="c"*64,plan_packet_blob_sha="d"*40,harness_blob_sha="e"*40)
        self.assertIn("BLOCKED_CASE_STATUS_REQUIRED", p)

    def test_473_is_ie_guarded(self):
        self.assertEqual(classify_negative(case_id="WDPC-473",expected_endpoint="INSUFFICIENT_EVIDENCE",observed=OBS_IE,effect=EFFECT,fixture_valid=True,harness_valid=True,ie_condition=self.ie()),"PASS")

    def test_ie_missing_bundle_cannot_pass(self):
        self.assertEqual(classify_negative(case_id="WDPC-473",expected_endpoint="INSUFFICIENT_EVIDENCE",observed=OBS_IE,effect=EFFECT,fixture_valid=True,harness_valid=True,ie_condition=self.ie(case_execution_evidence_bundle_present=False,missing_case_execution_evidence=True)),"NOT_EXECUTABLE_EXTERNAL_EVIDENCE_REQUIRED")

    def test_ie_digest_must_be_hex(self):
        c=self.ie(endpoint_trigger_evidence_digest="z"*64)
        self.assertFalse(c.qualifies_for_endpoint_pass)

    def test_exact_python_version(self):
        env=EnvironmentIdentity(python_version="3.12.7",os_release_digest="1"*64,uname_digest="2"*64,dependency_lock_digest="3"*64,dependency_lock_method="PIP_FREEZE",timezone="UTC",pythonhashseed="0",fixture_random_seed=24011,clock_model="FROZEN_LOGICAL_CLOCK")
        self.assertEqual(validate_environment(env, exact_python_version="3.12.7"), [])
        self.assertIn("HARNESS_EXACT_PYTHON_VERSION_MISMATCH",validate_environment(env, exact_python_version="3.12.6"))

    def test_stdlib_fallback_rejects_nonstdlib_imports(self):
        env=EnvironmentIdentity(python_version="3.12.7",os_release_digest="1"*64,uname_digest="2"*64,dependency_lock_digest="3"*64,dependency_lock_method="STDLIB_ONLY_PIP_UNAVAILABLE",timezone="UTC",pythonhashseed="0",fixture_random_seed=24011,clock_model="FROZEN_LOGICAL_CLOCK",nonstdlib_imports=("requests",))
        self.assertIn("HARNESS_NONSTDLIB_IMPORT_UNDER_PIP_UNAVAILABLE",validate_environment(env, exact_python_version="3.12.7"))

    def test_wall_clock_reads_are_rejected(self):
        env=EnvironmentIdentity(python_version="3.12.7",os_release_digest="1"*64,uname_digest="2"*64,dependency_lock_digest="3"*64,dependency_lock_method="PIP_FREEZE",timezone="UTC",pythonhashseed="0",fixture_random_seed=24011,clock_model="FROZEN_LOGICAL_CLOCK",unexpected_wall_clock_read_count=1)
        self.assertIn("HARNESS_UNEXPECTED_WALL_CLOCK_READ",validate_environment(env, exact_python_version="3.12.7"))

if __name__ == "__main__":
    unittest.main()
