"""Tests for reviewer evidence-delivery completeness and solution contracts."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from reviewer_evidence_delivery import (  # noqa: E402
    sha256_bytes,
    validate_finding_solution_contract,
    validate_solution_adjudication,
    verify_chunked_delivery,
    verify_whole_delivery,
)


class ReviewerEvidenceDeliveryTests(unittest.TestCase):
    def test_whole_document_must_match_declared_identity(self):
        raw = b"full review packet\n"
        self.assertTrue(
            verify_whole_delivery(
                declared_sha256=sha256_bytes(raw),
                declared_bytes=len(raw),
                delivered=raw,
            )
        )
        self.assertFalse(
            verify_whole_delivery(
                declared_sha256=sha256_bytes(raw),
                declared_bytes=len(raw),
                delivered=b"summary only",
            )
        )

    def test_all_chunks_required_and_reconstruct_whole(self):
        whole = b"abcdefghij"
        chunks = [
            {"index": 0, "count": 2, "bytes": b"abcde", "sha256": sha256_bytes(b"abcde")},
            {"index": 1, "count": 2, "bytes": b"fghij", "sha256": sha256_bytes(b"fghij")},
        ]
        self.assertTrue(
            verify_chunked_delivery(
                declared_sha256=sha256_bytes(whole),
                declared_bytes=len(whole),
                chunks=chunks,
            )
        )
        self.assertFalse(
            verify_chunked_delivery(
                declared_sha256=sha256_bytes(whole),
                declared_bytes=len(whole),
                chunks=chunks[:1],
            )
        )

    def test_chunk_digest_tampering_fails(self):
        whole = b"abcdef"
        chunks = [
            {"index": 0, "count": 2, "bytes": b"abc", "sha256": sha256_bytes(b"abc")},
            {"index": 1, "count": 2, "bytes": b"def", "sha256": "0" * 64},
        ]
        self.assertFalse(
            verify_chunked_delivery(
                declared_sha256=sha256_bytes(whole),
                declared_bytes=len(whole),
                chunks=chunks,
            )
        )

    def test_reviewer_defect_requires_solution_and_regression(self):
        finding = {
            "finding_id": "F-01",
            "severity": "HIGH",
            "location": "parser",
            "failure_path": "hidden declaration bypass",
            "evidence": "exact adversarial case",
            "impact": "false-clean review",
            "proposed_remediation": "replace literal patch with structural grammar",
            "regression_tests": ["reject the defect family", "preserve valid prose"],
            "candidate_invalidated": True,
            "blocking": True,
        }
        self.assertTrue(validate_finding_solution_contract(finding))
        bad = dict(finding)
        bad["proposed_remediation"] = ""
        self.assertFalse(validate_finding_solution_contract(bad))

    def test_reviewer_solution_is_advisory_and_requires_adjudication(self):
        self.assertTrue(
            validate_solution_adjudication(
                {
                    "finding_id": "F-01",
                    "state": "ACCEPTED_NARROWED",
                    "reason": "same defect reproduced but safer repair preserves valid behavior",
                }
            )
        )
        self.assertFalse(
            validate_solution_adjudication(
                {
                    "finding_id": "F-01",
                    "state": "AUTO_IMPLEMENT_REVIEWER_SOLUTION",
                    "reason": "not a governed adjudication state",
                }
            )
        )


if __name__ == "__main__":
    unittest.main()
