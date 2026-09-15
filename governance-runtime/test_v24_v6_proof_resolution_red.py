from __future__ import annotations

import unittest

from test_v24_v6_decision_apply import bundle
from v24_v6_decision_apply import evaluate_decision_apply_latch


class V24V6ProofResolutionRegressionTests(unittest.TestCase):
    """Permanent regression for the opaque-proof false-green found in R9.

    Historical RED is preserved by workflow run 35000549932.  This test keeps the
    exact adversarial shape load-bearing after repair: SHA-shaped references plus
    caller-provided QUALIFIED/CURRENT labels cannot open an authority latch when
    the separately supplied proof context/trusted boundary is absent.
    """

    def test_forged_opaque_proof_labels_cannot_open_apply_latch(self):
        candidate = bundle()
        self.assertNotIn("governance_proof_context", candidate)
        self.assertNotIn("trusted_boundary", candidate)

        result = evaluate_decision_apply_latch(candidate)

        self.assertFalse(
            result["allowed"],
            "V6 false-green regression: opaque proof labels opened the apply latch",
        )
        self.assertTrue(
            any(
                "TRUSTED_PROOF_BOUNDARY_REQUIRED" in problem
                or "GOVERNANCE_PROOF_CONTEXT_REQUIRED" in problem
                or "PROOF_REFERENCE_UNRESOLVED" in problem
                for problem in result["problems"]
            ),
            result["problems"],
        )


if __name__ == "__main__":
    unittest.main()
