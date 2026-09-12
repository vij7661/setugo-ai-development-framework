from __future__ import annotations

import unittest

BASE_MODULES = (
    "test_ecc_governance",
    "test_ecc_governance_full_coverage",
    "test_ecc_governance_v2_review_remediation",
)

V5_MODULE = "test_ecc_governance_v5_closed_boundary"
V6_MODULE = "test_ecc_governance_v6_eligibility_provenance"
V7_MODULE = "test_ecc_governance_v7_seal_capability"
V8_MODULE = "test_ecc_governance_v8_verifier_substitution"
V9_MODULE = "test_ecc_governance_v9_verifier_primitive_integrity"
V10_MODULE = "test_ecc_governance_v10_path_primitive_integrity"

SUPERSEDED_TEST_IDS = {
    "test_ecc_governance_v5_closed_boundary.ECCV5ClosedCandidateBoundary.test_candidate_result_gate_requires_boundary_marker_kind_and_favorable_status":
        "V5 raw-dictionary positive eligibility was superseded by V6 provenance sealing.",
    "test_ecc_governance_v5_closed_boundary.ECCV5ClosedCandidateBoundary.test_policy_is_reverified_immediately_before_candidate_eligibility":
        "V5 used replacement of the public verifier as a proxy for policy change. V8 identifies that replaceability as an authority bypass and replaces it with actual dependency-tamper recheck tests.",
    "test_ecc_governance_v6_eligibility_provenance.ECCV6EligibilityProvenance.test_consumption_rechecks_runtime_policy":
        "V6 patched the public verifier itself. V8 requires consumption to use a closure-held internal verifier and tests actual dependency tamper instead.",
    "test_ecc_governance_v6_eligibility_provenance.ECCV6EligibilityProvenance.test_boundary_failure_remains_ineligible_and_unsealed":
        "V6 induced policy failure by replacing the public verifier. V8 makes the public verifier diagnostic-only and retains fail-closed behavior through actual policy/dependency tamper tests.",
}


def flatten(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from flatten(item)
        else:
            yield item


def add_with_supersession(suite, loader, module):
    for test in flatten(loader.loadTestsFromName(module)):
        full_id = test.id()
        if full_id in SUPERSEDED_TEST_IDS:
            print(f"SUPERSEDED_TEST={full_id} REASON={SUPERSEDED_TEST_IDS[full_id]}")
            continue
        suite.addTest(test)


def main() -> int:
    loader = unittest.defaultTestLoader
    suite = unittest.TestSuite()
    for module in BASE_MODULES:
        suite.addTests(loader.loadTestsFromName(module))

    add_with_supersession(suite, loader, V5_MODULE)
    add_with_supersession(suite, loader, V6_MODULE)
    suite.addTests(loader.loadTestsFromName(V7_MODULE))
    suite.addTests(loader.loadTestsFromName(V8_MODULE))
    suite.addTests(loader.loadTestsFromName(V9_MODULE))
    suite.addTests(loader.loadTestsFromName(V10_MODULE))

    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
