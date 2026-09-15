from __future__ import annotations

import unittest

from test_v24_v6_decision_apply import bundle
from v24_v6_decision_apply import evaluate_decision_apply_latch


class V24V6ProofResolutionRedTests(unittest.TestCase):
    """Falsify caller-asserted qualification/currentness as authority evidence.

    V6 requires authority-bearing dependencies to inherit generic qualification,
    currentness, independence, and anti-self-qualification.  An opaque SHA-shaped
    digest plus a caller-provided QUALIFIED/CURRENT label is not proof that the
    referenced record exists or validates.
    """

    def test_forged_opaque_proof_labels_cannot_open_apply_latch(self):
        candidate = bundle()

        # The inherited R4 fixture intentionally contains only opaque digest
        # strings and asserted state labels.  It supplies no exact qualification,
        # independence, or currentness records that can be resolved and validated
        # under the R1 generic contracts.
        self.assertNotIn("governance_evidence_store", candidate)

        result = evaluate_decision_apply_latch(candidate)

        # Required V6 behavior: fail closed until all load-bearing references are
        # resolved to exact validated evidence records.  On the frozen R9
        # candidate this assertion is expected to RED: the latch currently
        # returns allowed=True from the labels alone.
        self.assertFalse(
            result["allowed"],
            "V6 false-green: opaque qualification/currentness labels opened the apply latch",
        )
        self.assertTrue(
            any(
                "UNRESOLVED" in problem
                or "EVIDENCE" in problem
                or "QUALIFICATION_REFERENCE" in problem
                for problem in result["problems"]
            ),
            result["problems"],
        )


if __name__ == "__main__":
    unittest.main()
