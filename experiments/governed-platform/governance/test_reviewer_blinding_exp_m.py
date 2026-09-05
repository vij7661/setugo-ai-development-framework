import unittest

from reviewer_blinding import (
    DisclosureRecord,
    build_adjudication_context,
    build_independent_review_context,
)


def rec(record_id, disclosure_class, content="x"):
    return DisclosureRecord(
        record_id=record_id,
        disclosure_class=disclosure_class,
        content=content,
        provenance="exp-m:test",
    )


class ExpMReviewerBlindingTests(unittest.TestCase):
    def test_m001_independent_phase_hides_prior_final_conclusions(self):
        records = [
            rec("req", "AUTHORITATIVE"),
            rec("artifact", "FROZEN_ARTIFACT"),
            rec("r1", "PRIOR_REVIEW_FINAL", "R1 says TEST DEFECT"),
        ]
        ctx = build_independent_review_context(records)
        self.assertEqual(["req", "artifact"], [r.record_id for r in ctx])

    def test_m002_independent_phase_hides_confidence_and_vote_signals(self):
        records = [
            rec("req", "AUTHORITATIVE"),
            rec("confidence", "PRIOR_CONFIDENCE", "99%"),
            rec("votes", "PRIOR_VOTE_SIGNAL", "2 of 2 agree"),
        ]
        ctx = build_independent_review_context(records)
        self.assertEqual(["req"], [r.record_id for r in ctx])

    def test_m003_private_reasoning_and_protected_truth_never_enter_reviewer_context(self):
        records = [
            rec("private", "MODEL_PRIVATE"),
            rec("truth", "PROTECTED_TRUTH"),
        ]
        self.assertEqual((), build_independent_review_context(records))
        self.assertEqual((), build_adjudication_context(records, independent_position_hash="sha256:abc"))

    def test_m004_adjudication_requires_frozen_independent_position(self):
        with self.assertRaises(ValueError):
            build_adjudication_context([rec("r1", "PRIOR_REVIEW_FINAL")], independent_position_hash="")

    def test_m005_after_freeze_prior_final_reviews_can_be_disclosed(self):
        records = [
            rec("req", "AUTHORITATIVE"),
            rec("r1", "PRIOR_REVIEW_FINAL", "R1 final"),
            rec("r2", "PRIOR_REVIEW_FINAL", "R2 final"),
        ]
        ctx = build_adjudication_context(records, independent_position_hash="sha256:frozen")
        self.assertEqual(["req", "r1", "r2"], [r.record_id for r in ctx])

    def test_m006_confidence_and_majority_remain_hidden_even_after_freeze(self):
        records = [
            rec("r1", "PRIOR_REVIEW_FINAL"),
            rec("confidence", "PRIOR_CONFIDENCE"),
            rec("votes", "PRIOR_VOTE_SIGNAL"),
        ]
        ctx = build_adjudication_context(records, independent_position_hash="sha256:frozen")
        self.assertEqual(["r1"], [r.record_id for r in ctx])

    def test_m007_duplicate_disclosure_identity_fails_closed(self):
        with self.assertRaises(ValueError):
            build_independent_review_context([rec("x", "PROJECT"), rec("x", "AUTHORITATIVE")])

    def test_m008_authoritative_and_project_context_remain_available(self):
        records = [rec("req", "AUTHORITATIVE"), rec("project", "PROJECT"), rec("artifact", "FROZEN_ARTIFACT")]
        ctx = build_independent_review_context(records)
        self.assertEqual(3, len(ctx))


if __name__ == "__main__":
    unittest.main()
