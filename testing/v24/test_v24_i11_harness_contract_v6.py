import unittest

from v24_i11_harness_contract_v6 import (
    AuthorityEffectObservation,
    CaseRunBinding,
    ConjunctiveAssertionObservation,
    EnvironmentIdentity,
    GovernedEndpointObservation,
    InsufficientEvidenceEndpointCondition,
    PositiveAssertionObservation,
    classify_conjunctive_negative,
    classify_negative,
    classify_positive,
    expected_stdlib_fallback_digest,
    validate_binding,
    validate_environment,
)

D = "a" * 64
OBS_IE = GovernedEndpointObservation("INSUFFICIENT_EVIDENCE", "candidate", D, ())
EFFECT = AuthorityEffectObservation("O", D, D, 0, 0)


class HarnessV6Tests(unittest.TestCase):
    def binding(self, case_id="WDPC-431", status="NOT_EXECUTED", run_id=None):
        return CaseRunBinding(
            case_id=case_id,
            run_id=run_id or f"{case_id}:" + "1" * 16,
            packet_sha256="2" * 64,
            plan_body_sha256="3" * 64,
            plan_binding_blob_sha="4" * 40,
            harness_blob_sha="5" * 40,
            harness_version="1.5.0-PLAN-REVIEW",
            design_sha="db9e4b349fd26e128f4486878a4af64929000a7c",
            implementation_sha="9836dc3ff233cca582f485434fc1c6494cf7eb05",
            implementation_tree="d68cbccdceebad88715c8b37ddfcd524fc16ce8a",
            governance_generation="V24",
            target_module_git_blobs=("6" * 40,),
            target_module_content_sha256s=("7" * 64,),
            fixture_digest="8" * 64,
            environment_digest="9" * 64,
            case_status=status,
        )

    def ie(self, case_id="WDPC-473", reason=None, **kw):
        reasons = {
            "WDPC-443": "IUDA shares prohibited effective control with candidate",
            "WDPC-458": "required external completeness authority unavailable or independence unproven",
            "WDPC-472": "exact current admission-ledger lineage cannot be established",
            "WDPC-473": "completeness result lacks a bound durable ledger record",
            "WDPC-474": "exact current completeness-ledger lineage cannot be established",
            "WDPC-476": "capability attestation relies only on deployment self-report",
            "WDPC-480": "universe projection lacks a qualifying bound UniverseDerivationDecisionRecord",
            "WDPC-497": "unadmitted direct sink writer prevents closed-world qualification",
            "WDPC-500": "operational root is relabeled independent without control-domain separation",
            "WDPC-502": "ordinary IUDA lacks qualifying governed predecessor lineage",
            "WDPC-504": "material sink lacks unavoidable deny-by-default admission boundary",
        }
        d = dict(
            case_id=case_id,
            case_execution_evidence_bundle_present=True,
            case_preconditions_valid=True,
            target_condition_evidence_present=True,
            target_condition_observed=True,
            missing_case_execution_evidence=False,
            endpoint_emitted_by_candidate=True,
            endpoint_trigger_evidence_digest="a" * 64,
            target_reason=reason or reasons[case_id],
        )
        d.update(kw)
        return InsufficientEvidenceEndpointCondition(**d)

    def test_exact_ie_reason_required(self):
        self.assertTrue(self.ie("WDPC-473").qualifies_for_endpoint_pass)
        self.assertFalse(
            self.ie("WDPC-473", reason="some other reason").qualifies_for_endpoint_pass
        )

    def test_457_exact_invariant_required(self):
        good = ConjunctiveAssertionObservation(
            GovernedEndpointObservation(
                "AUTHORITY_EVIDENCE_SOURCE_INVALID", "candidate", D, ()
            ),
            ("HISTORICAL_RESULT_UNCHANGED",),
            ("HISTORICAL_RESULT_UNCHANGED",),
            ("b" * 64,),
        )
        bad = ConjunctiveAssertionObservation(
            good.primary_endpoint,
            ("WRONG_INVARIANT",),
            ("WRONG_INVARIANT",),
            ("b" * 64,),
        )
        self.assertEqual(
            classify_conjunctive_negative(
                case_id="WDPC-457",
                expected_endpoint="AUTHORITY_EVIDENCE_SOURCE_INVALID",
                observation=good,
                effect=EFFECT,
                fixture_valid=True,
                harness_valid=True,
            ),
            "PASS",
        )
        self.assertEqual(
            classify_conjunctive_negative(
                case_id="WDPC-457",
                expected_endpoint="AUTHORITY_EVIDENCE_SOURCE_INVALID",
                observation=bad,
                effect=EFFECT,
                fixture_valid=True,
                harness_valid=True,
            ),
            "FAIL_CODE_DEFECT",
        )

    def test_stdlib_fallback_digest_exact(self):
        version = "3.12.7"
        env = EnvironmentIdentity(
            version,
            "1" * 64,
            "2" * 64,
            expected_stdlib_fallback_digest(version),
            "STDLIB_ONLY_PIP_UNAVAILABLE",
            "UTC",
            "0",
            24011,
            "FROZEN_LOGICAL_CLOCK",
            (),
            0,
        )
        self.assertEqual(validate_environment(env, exact_python_version=version), [])
        bad = EnvironmentIdentity(
            version,
            "1" * 64,
            "2" * 64,
            "3" * 64,
            "STDLIB_ONLY_PIP_UNAVAILABLE",
            "UTC",
            "0",
            24011,
            "FROZEN_LOGICAL_CLOCK",
            (),
            0,
        )
        self.assertIn(
            "HARNESS_STDLIB_FALLBACK_DIGEST_MISMATCH",
            validate_environment(bad, exact_python_version=version),
        )

    def test_python_patch_level_is_required(self):
        env = EnvironmentIdentity(
            "3.12",
            "1" * 64,
            "2" * 64,
            "3" * 64,
            "PIP_FREEZE",
            "UTC",
            "0",
            24011,
            "FROZEN_LOGICAL_CLOCK",
        )
        p = validate_environment(env, exact_python_version="3.12")
        self.assertIn("HARNESS_EXPECTED_PYTHON_VERSION_NOT_EXACT_PATCH", p)
        self.assertIn("HARNESS_CAPTURED_PYTHON_VERSION_NOT_EXACT_PATCH", p)

    def test_run_id_and_target_module_identity(self):
        b = self.binding(run_id="wrong")
        p = validate_binding(
            b,
            packet_sha256="2" * 64,
            plan_body_sha256="3" * 64,
            plan_binding_blob_sha="4" * 40,
            harness_blob_sha="5" * 40,
        )
        self.assertIn("RUN_ID_INVALID", p)

        b2 = self.binding()
        b2 = CaseRunBinding(
            **{
                **b2.__dict__,
                "target_module_git_blobs": ("not-a-git-oid",),
                "target_module_content_sha256s": ("z" * 64,),
            }
        )
        p2 = validate_binding(
            b2,
            packet_sha256="2" * 64,
            plan_body_sha256="3" * 64,
            plan_binding_blob_sha="4" * 40,
            harness_blob_sha="5" * 40,
        )
        self.assertIn("TARGET_MODULE_GIT_BLOB_INVALID", p2)
        self.assertIn("TARGET_MODULE_CONTENT_SHA256_INVALID", p2)

    def test_positive_classifier(self):
        obs = PositiveAssertionObservation("positive-control", True, ("c" * 64,))
        self.assertEqual(
            classify_positive(
                observation=obs, fixture_valid=True, harness_valid=True
            ),
            "PASS",
        )


if __name__ == "__main__":
    unittest.main()
