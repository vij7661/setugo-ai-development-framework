from __future__ import annotations

import unittest

from review_engine.bypass_governance import BypassRecord, assert_no_bypass_exception


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
            record.advance("MECHANISM_REPAIRED", repair_ref="commit")
        preserved = record.advance("PRESERVED", first_failure_ref="run:red")
        with self.assertRaisesRegex(ValueError, "exactly one stage"):
            preserved.advance("DISCOVERED")

    def test_authority_bypass_requires_independent_review_before_closed(self):
        record = BypassRecord("BYP-3", "provider identity")
        record = record.advance("PRESERVED", first_failure_ref="run:red")
        record = record.advance("MECHANISM_REPAIRED", repair_ref="commit:repair")
        record = record.advance("REGRESSION_FROZEN", regression_ref="test:test_identity")
        record = record.advance("FULL_SUITE_GREEN", full_suite_ref="run:green")
        with self.assertRaisesRegex(ValueError, "independent_review_ref"):
            record.advance("INDEPENDENTLY_REVIEWED")
        record = record.advance("INDEPENDENTLY_REVIEWED", independent_review_ref="review:001")
        record = record.advance("CLOSED")
        self.assertEqual(record.status, "CLOSED")

    def test_non_authority_observation_can_reach_reviewed_stage_without_review_ref(self):
        record = BypassRecord(
            "BYP-4",
            "non-authority observability hardening",
            independent_review_required=False,
        )
        record = record.advance("PRESERVED", first_failure_ref="run:red")
        record = record.advance("MECHANISM_REPAIRED", repair_ref="commit")
        record = record.advance("REGRESSION_FROZEN", regression_ref="test")
        record = record.advance("FULL_SUITE_GREEN", full_suite_ref="run")
        record = record.advance("INDEPENDENTLY_REVIEWED")
        record = record.advance("CLOSED")
        self.assertEqual(record.status, "CLOSED")

    def test_no_override_token_exists_for_production_bypass(self):
        assert_no_bypass_exception(requested=False)
        with self.assertRaisesRegex(ValueError, "forbidden"):
            assert_no_bypass_exception(requested=True, reason="legacy compatibility")


if __name__ == "__main__":
    unittest.main()
