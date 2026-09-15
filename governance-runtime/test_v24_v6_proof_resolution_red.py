from __future__ import annotations

import unittest

from test_v24_v6_decision_apply import bundle
from test_v24_v6_material_surface import ledger_bundle
from v24_v6_decision_apply import evaluate_decision_apply_latch
from v24_v6_material_surface import validate_material_observation_ledger


class V24V6ProofResolutionRegressionTests(unittest.TestCase):
    """Permanent regressions for opaque-proof false-greens found after R9.

    Historical R4 RED is preserved by workflow run 35000549932.  Additional
    authority paths are falsified before each repair and retained here so a later
    refactor cannot reintroduce label-as-proof behavior.
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

    def test_fabricated_witness_labels_cannot_qualify_observation_ledger(self):
        candidate = ledger_bundle()
        witness = candidate["head"]["witness_currentness_records"][0]
        self.assertEqual(witness["currentness_result"], "CURRENT")
        self.assertEqual(witness["independence_result"], "QUALIFIED")
        self.assertNotIn("witness_qualification_digest", witness)
        self.assertNotIn("witness_independence_qualification_digest", witness)
        self.assertNotIn("witness_currentness_binding_digest", witness)

        result = validate_material_observation_ledger(candidate)

        # Required repaired behavior: labels and a different control-domain string
        # are not independent/current witness evidence.  On the pre-R3-repair
        # implementation this intentionally REDs because result["qualified"] is True.
        self.assertFalse(
            result["qualified"],
            "V6 false-green: fabricated witness labels qualified the observation ledger",
        )
        self.assertTrue(
            any(
                "WITNESS_PROOF" in problem
                or "TRUSTED_PROOF_BOUNDARY_REQUIRED" in problem
                or "PROOF_REFERENCE" in problem
                for problem in result["problems"]
            ),
            result["problems"],
        )


if __name__ == "__main__":
    unittest.main()
