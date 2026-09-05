from __future__ import annotations

import unittest

from review_engine.models import ReviewFinding
from review_engine.scoped_correction import CorrectionScopeError, build_scoped_correction_plan


def finding(
    finding_id: str,
    *,
    anchor: str | None,
    scope: tuple[str, ...] = ("claim:c1",),
) -> ReviewFinding:
    return ReviewFinding(
        finding_id=finding_id,
        reviewer_role="R2",
        severity="HIGH",
        material=True,
        summary="localized material defect",
        violated_invariant="TEST-INVARIANT",
        affected_scope=scope,
        first_invalid_claim=anchor,
    )


class ScopedCorrectionTests(unittest.TestCase):
    def test_unique_claim_anchor_can_be_replaced_without_touching_unaffected_text(self):
        original = "stable header\nwrong claim\nstable footer"
        plan = build_scoped_correction_plan(
            original,
            (finding("f1", anchor="wrong claim"),),
        )
        assessment = plan.assess("stable header\ncorrected claim\nstable footer")
        self.assertTrue(assessment.admissible)
        self.assertEqual(plan.editable_ranges, ((14, 25),))

    def test_prefix_rewrite_is_rejected(self):
        original = "stable header\nwrong claim\nstable footer"
        plan = build_scoped_correction_plan(original, (finding("f1", anchor="wrong claim"),))
        assessment = plan.assess("changed header\ncorrected claim\nstable footer")
        self.assertFalse(assessment.admissible)
        self.assertIn("outside", assessment.reason)

    def test_suffix_rewrite_is_rejected(self):
        original = "stable header\nwrong claim\nstable footer"
        plan = build_scoped_correction_plan(original, (finding("f1", anchor="wrong claim"),))
        assessment = plan.assess("stable header\ncorrected claim\nchanged footer")
        self.assertFalse(assessment.admissible)

    def test_text_between_two_authorized_claims_is_immutable(self):
        original = "head\nwrong A\nstable middle\nwrong B\ntail"
        plan = build_scoped_correction_plan(
            original,
            (
                finding("f1", anchor="wrong A", scope=("claim:a",)),
                finding("f2", anchor="wrong B", scope=("claim:b",)),
            ),
        )
        self.assertTrue(plan.assess("head\nfixed A\nstable middle\nfixed B\ntail").admissible)
        self.assertFalse(plan.assess("head\nfixed A\nrewritten middle\nfixed B\ntail").admissible)

    def test_repeated_anchor_is_ambiguous_and_fails_closed(self):
        original = "same claim\nseparator\nsame claim"
        with self.assertRaisesRegex(CorrectionScopeError, "ambiguous"):
            build_scoped_correction_plan(original, (finding("f1", anchor="same claim"),))

    def test_missing_anchor_fails_closed(self):
        with self.assertRaisesRegex(CorrectionScopeError, "lacks an exact"):
            build_scoped_correction_plan(
                "stable\nwrong\nfooter",
                (finding("f1", anchor=None),),
            )

    def test_artifact_wide_scope_does_not_grant_automatic_rewrite_authority(self):
        with self.assertRaisesRegex(CorrectionScopeError, "machine-localizable claim scope"):
            build_scoped_correction_plan(
                "stable\nwrong\nfooter",
                (finding("f1", anchor="wrong", scope=("artifact:semantic-presentation",)),),
            )

    def test_empty_scope_fails_closed(self):
        with self.assertRaisesRegex(CorrectionScopeError, "machine-localizable claim scope"):
            build_scoped_correction_plan(
                "stable\nwrong\nfooter",
                (finding("f1", anchor="wrong", scope=()),),
            )

    def test_anchor_absent_from_frozen_artifact_fails_closed(self):
        with self.assertRaisesRegex(CorrectionScopeError, "absent"):
            build_scoped_correction_plan(
                "stable\nactual text\nfooter",
                (finding("f1", anchor="invented text"),),
            )

    def test_overlapping_different_anchors_fail_closed(self):
        original = "prefix nested wrong claim suffix"
        with self.assertRaisesRegex(CorrectionScopeError, "overlap"):
            build_scoped_correction_plan(
                original,
                (
                    finding("f1", anchor="nested wrong claim", scope=("claim:a",)),
                    finding("f2", anchor="wrong claim", scope=("claim:b",)),
                ),
            )

    def test_entire_artifact_claim_anchor_requires_human_instead_of_full_rewrite_capability(self):
        with self.assertRaisesRegex(CorrectionScopeError, "entire artifact"):
            build_scoped_correction_plan(
                "the whole artifact is one bad claim",
                (finding("f1", anchor="the whole artifact is one bad claim"),),
            )

    def test_single_near_whole_artifact_anchor_is_not_localized_correction_authority(self):
        original = "X" + ("bad" * 120) + "Y"
        oversized_anchor = original[1:-1]
        self.assertGreater(len(oversized_anchor) / len(original), 0.95)
        with self.assertRaisesRegex(CorrectionScopeError, "localized"):
            build_scoped_correction_plan(
                original,
                (finding("near-whole", anchor=oversized_anchor),),
            )

    def test_multiple_anchors_cannot_accumulate_into_near_whole_artifact_authority(self):
        anchor_a = "A" * 80
        stable_middle = "MID"
        anchor_b = "B" * 80
        original = "H" + anchor_a + stable_middle + anchor_b + "T"
        editable_fraction = (len(anchor_a) + len(anchor_b)) / len(original)
        self.assertGreater(editable_fraction, 0.95)
        with self.assertRaisesRegex(CorrectionScopeError, "localized"):
            build_scoped_correction_plan(
                original,
                (
                    finding("a", anchor=anchor_a, scope=("claim:a",)),
                    finding("b", anchor=anchor_b, scope=("claim:b",)),
                ),
            )

    def test_no_change_is_not_an_admissible_material_correction(self):
        original = "stable\nwrong claim\nfooter"
        plan = build_scoped_correction_plan(original, (finding("f1", anchor="wrong claim"),))
        assessment = plan.assess(original)
        self.assertFalse(assessment.admissible)
        self.assertIn("no artifact revision", assessment.reason)


if __name__ == "__main__":
    unittest.main()
