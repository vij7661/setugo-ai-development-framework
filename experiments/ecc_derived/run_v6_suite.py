from __future__ import annotations

import unittest

BASE_MODULES = (
    "test_ecc_governance",
    "test_ecc_governance_full_coverage",
    "test_ecc_governance_v2_review_remediation",
)

V5_MODULE = "test_ecc_governance_v5_closed_boundary"
V6_MODULE = "test_ecc_governance_v6_eligibility_provenance"

SUPERSEDED_TEST_IDS = {
    "test_ecc_governance_v5_closed_boundary.ECCV5ClosedCandidateBoundary.test_candidate_result_gate_requires_boundary_marker_kind_and_favorable_status":
        "V5 correctly required marker+kind+status, but its positive raw-dict assertion is superseded by V6 provenance sealing; caller-constructed dictionaries must no longer be eligible."
}


def flatten(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from flatten(item)
        else:
            yield item


def main() -> int:
    loader = unittest.defaultTestLoader
    suite = unittest.TestSuite()
    for module in BASE_MODULES:
        suite.addTests(loader.loadTestsFromName(module))

    v5_loaded = loader.loadTestsFromName(V5_MODULE)
    for test in flatten(v5_loaded):
        short_id = test.id().split(".", 1)[-1]
        if short_id in SUPERSEDED_TEST_IDS:
            print(f"SUPERSEDED_TEST={short_id} REASON={SUPERSEDED_TEST_IDS[short_id]}")
            continue
        suite.addTest(test)

    suite.addTests(loader.loadTestsFromName(V6_MODULE))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
