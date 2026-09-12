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

SUPERSEDED_TEST_IDS = {
    "test_ecc_governance_v5_closed_boundary.ECCV5ClosedCandidateBoundary.test_candidate_result_gate_requires_boundary_marker_kind_and_favorable_status":
        "V5 raw-dictionary positive eligibility was superseded by V6 provenance sealing."
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

    for test in flatten(loader.loadTestsFromName(V5_MODULE)):
        full_id = test.id()
        if full_id in SUPERSEDED_TEST_IDS:
            print(f"SUPERSEDED_TEST={full_id} REASON={SUPERSEDED_TEST_IDS[full_id]}")
            continue
        suite.addTest(test)

    suite.addTests(loader.loadTestsFromName(V6_MODULE))
    suite.addTests(loader.loadTestsFromName(V7_MODULE))

    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
