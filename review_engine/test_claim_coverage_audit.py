from __future__ import annotations

import unittest

from review_engine.claim_coverage import ClaimCoverageAssessment


class ClaimCoverageAuditTests(unittest.TestCase):
    def test_coverage_finding_retains_inventory_extractor_and_provenance_refs(self):
        assessment = ClaimCoverageAssessment(
            artifact_hash="0" * 64,
            status="OMITTED_MATERIAL_CLAIM",
            inventory_ids=("inv-1",),
            extractor_ids=("claim-extractor:abc",),
            provenance=("authenticated-source:test",),
            missing_claims=(("f" * 64, "Revenue increased 40%.", "EMPIRICAL_FACT"),),
            correlation_warnings=("warning-1",),
        )
        finding = assessment.findings("R2")[0]
        self.assertIn("coverage-inventory:inv-1", finding.evidence_refs)
        self.assertIn("coverage-extractor:claim-extractor:abc", finding.evidence_refs)
        self.assertIn("coverage-provenance:authenticated-source:test", finding.evidence_refs)
        self.assertIn("coverage-warning:warning-1", finding.evidence_refs)


if __name__ == "__main__":
    unittest.main()
