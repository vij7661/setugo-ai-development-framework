from __future__ import annotations

import sys
import unittest

ACTIVE_MODULES = (
    "test_ecc_governance",
    "test_ecc_governance_full_coverage",
    "test_ecc_governance_v2_review_remediation",
    "test_ecc_governance_v5_closed_boundary",
)

SUPERSEDED_BY_REVIEW = {
    "test_ecc_governance_v3_omission_hardening": "V3 encodes caller-selectable strict shared-core mode; V4/V5 review requires that mode removed.",
    "test_ecc_governance_v4_mandatory_boundary": "V4 encodes bare strict-class eligibility and same-fixture cross-check assumptions rejected by the V4 re-review.",
}


def main() -> int:
    print("ECC_V5_SUPERSESSION_RECORD")
    for module, reason in SUPERSEDED_BY_REVIEW.items():
        print(f"SUPERSEDED_TEST_MODULE={module} REASON={reason}")
    suite = unittest.TestSuite()
    loader = unittest.defaultTestLoader
    for module in ACTIVE_MODULES:
        suite.addTests(loader.loadTestsFromName(module))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
