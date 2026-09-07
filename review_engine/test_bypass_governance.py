from __future__ import annotations

import json
import unittest
from pathlib import Path

from review_engine.bypass_governance import BypassRecord, assert_no_bypass_exception


FAILURE_REF = "github-actions:12345/job/67890@" + "a" * 40
REPAIR_REF = "commit:" + "b" * 40 + ":review_engine/qualification.py"
REGRESSION_REF = "review_engine/test_runtime_regression.py@" + "c" * 40
FULL_SUITE_REF = "review-engine-ci:12345=SUCCESS;integrated-harness:23456=SUCCESS@" + "d" * 40
REVIEW_REF = "platform-review:REV-TEST-001@" + "e" * 40
ALL_REFS = {FAILURE_REF, REPAIR_REF, REGRESSION_REF, FULL_SUITE_REF, REVIEW_REF}


def accepts_known_reference(ref: str) -> bool:
    return ref in ALL_REFS


class BypassGovernanceTests(unittest.TestCase):
    def test_authority_bypass_cannot_close_without_all_required_evidence(self):
        with self.assertRaisesRegex(ValueError, "first_failure_ref"):
            BypassRecord(
                bypass_id="BYP-1",
                invariant="authority path must fail closed",
                status="CLOSED",
            ).validate()

    def test_lifecycle_cannot_skip_or_move_backwards(self):
        record = BypassRecord("BYP-2", "reviewer independence")
        with self.assertRaisesRegex(ValueError, "exactly one stage"):
            record.advance("MECHANISM_REPAIRED", repair_ref=REPAIR_REF)
        preserved = record.advance("PRESERVED", first_failure_ref=FAILURE_REF)
        with self.assertRaisesRegex(ValueError, "exactly one stage"):
            preserved.advance("DISCOVERED")

    def test_authority_bypass_requires_resolved_independent_review_before_closed(self):
        record = BypassRecord("BYP-3", "provider identity")
        record = record.advance("PRESERVED", first_failure_ref=FAILURE_REF)
        record = record.advance("MECHANISM_REPAIRED", repair_ref=REPAIR_REF)
        record = record.advance("REGRESSION_FROZEN", regression_ref=REGRESSION_REF)
        record = record.advance("FULL_SUITE_GREEN", full_suite_ref=FULL_SUITE_REF)
        with self.assertRaisesRegex(ValueError, "independent_review_ref"):
            record.advance("INDEPENDENTLY_REVIEWED")
        with self.assertRaisesRegex(ValueError, "platform evidence verifier required"):
            record.advance("INDEPENDENTLY_REVIEWED", independent_review_ref=REVIEW_REF)
        with self.assertRaisesRegex(ValueError, "rejected reference"):
            record.advance(
                "INDEPENDENTLY_REVIEWED",
                independent_review_ref=REVIEW_REF,
                evidence_verifier=lambda _ref: False,
            )

        record = record.advance(
            "INDEPENDENTLY_REVIEWED",
            independent_review_ref=REVIEW_REF,
            evidence_verifier=accepts_known_reference,
        )
        record = record.advance("CLOSED", evidence_verifier=accepts_known_reference)
        self.assertEqual(record.status, "CLOSED")

    def test_non_authority_observation_can_close_without_independent_review_resolver(self):
        record = BypassRecord(
            "BYP-4",
            "non-authority observability hardening",
            independent_review_required=False,
        )
        record = record.advance("PRESERVED", first_failure_ref=FAILURE_REF)
        record = record.advance("MECHANISM_REPAIRED", repair_ref=REPAIR_REF)
        record = record.advance("REGRESSION_FROZEN", regression_ref=REGRESSION_REF)
        record = record.advance("FULL_SUITE_GREEN", full_suite_ref=FULL_SUITE_REF)
        record = record.advance("INDEPENDENTLY_REVIEWED")
        record = record.advance("CLOSED")
        self.assertEqual(record.status, "CLOSED")

    def test_placeholder_or_unstructured_evidence_refs_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "workflow run, job and exact commit"):
            BypassRecord(
                "BYP-5",
                "evidence shape",
                status="PRESERVED",
                first_failure_ref="run:red",
            ).validate()
        with self.assertRaisesRegex(ValueError, "placeholder"):
            BypassRecord(
                "BYP-6",
                "placeholder evidence",
                status="PRESERVED",
                first_failure_ref="github-actions:12345/job/67890@" + "f" * 40 + "-todo",
            ).validate()

    def test_repository_bypass_records_are_machine_valid_for_their_current_stage(self):
        root = Path(__file__).resolve().parent / "bypasses"
        paths = sorted(root.glob("*.json"))
        self.assertTrue(paths)
        for path in paths:
            data = json.loads(path.read_text(encoding="utf-8"))
            record = BypassRecord(
                bypass_id=data["bypass_id"],
                invariant=data["invariant"],
                status=data["status"],
                independent_review_required=bool(data.get("independent_review_required", True)),
                first_failure_ref=data.get("first_failure_ref"),
                repair_ref=data.get("repair_ref"),
                regression_ref=data.get("regression_ref"),
                full_suite_ref=data.get("full_suite_ref"),
                independent_review_ref=data.get("independent_review_ref"),
            )
            try:
                record.validate()
            except ValueError as exc:
                self.fail(f"{path.name} is not a valid bypass lifecycle record: {exc}")

    def test_no_override_token_exists_for_production_bypass(self):
        assert_no_bypass_exception(requested=False)
        with self.assertRaisesRegex(ValueError, "forbidden"):
            assert_no_bypass_exception(requested=True, reason="legacy compatibility")


if __name__ == "__main__":
    unittest.main()
