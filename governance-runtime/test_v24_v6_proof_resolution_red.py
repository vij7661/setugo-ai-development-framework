from __future__ import annotations

import unittest

from test_v24_v6_decision_apply import bundle
from test_v24_v6_endpoint_projection import endpoint_bundle
from test_v24_v6_material_surface import ledger_bundle
from test_v24_v6_normative_clause_projection import qualified_disposition_bundle
from v24_v6_decision_apply import evaluate_decision_apply_latch
from v24_v6_endpoint_projection import compile_qualified_endpoint_table
from v24_v6_material_surface import validate_material_observation_ledger
from v24_v6_normative_clause_projection import qualify_normative_dispositions


class V24V6ProofResolutionRegressionTests(unittest.TestCase):
    """Permanent regressions for opaque-proof false-greens found after R9.

    Historical R4 RED is preserved by workflow run 35000549932. Additional
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

        self.assertFalse(
            result["qualified"],
            "V6 false-green regression: fabricated witness labels qualified the observation ledger",
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

    def test_opaque_endpoint_table_qualification_cannot_qualify_compiled_table(self):
        candidate = endpoint_bundle()
        q = candidate["endpoint_table_qualification"]
        self.assertEqual(q["result"], "QUALIFIED")
        self.assertEqual(q["currentness_result"], "CURRENT")
        self.assertNotIn("subject_object_id", q)
        self.assertNotIn("governance_proof_context", candidate)

        result = compile_qualified_endpoint_table(candidate)

        self.assertFalse(
            result["qualified"],
            "V6 false-green: opaque endpoint-table qualification was accepted as proof",
        )
        self.assertTrue(
            any(
                "PROOF" in problem
                or "TRUSTED_PROOF_BOUNDARY_REQUIRED" in problem
                or "QUALIFICATION_REFERENCE" in problem
                for problem in result["problems"]
            ),
            result["problems"],
        )

    def test_opaque_parser_governance_labels_cannot_qualify_normative_dispositions(self):
        candidate = qualified_disposition_bundle()
        parser = candidate["parser_descriptor"]
        self.assertEqual(parser["qualification_state"], "QUALIFIED")
        self.assertEqual(parser["independence_state"], "QUALIFIED")
        self.assertEqual(parser["currentness_result"], "CURRENT")
        self.assertNotIn("qualification_digest", parser)
        self.assertNotIn("governance_proof_context", candidate)

        result = qualify_normative_dispositions(candidate)

        # Pre-repair R5 accepts the three labels plus SHA-shaped implementation
        # metadata as sufficient parser governance.  Required V6 behavior is to
        # fail closed until exact parser qualification/independence/currentness
        # references are resolved under the separately trusted proof boundary.
        self.assertFalse(
            result["qualified"],
            "V6 false-green: opaque parser governance labels qualified normative dispositions",
        )
        self.assertTrue(
            any(
                "PARSER_PROOF" in problem
                or "TRUSTED_PROOF_BOUNDARY_REQUIRED" in problem
                or "PROOF_REFERENCE" in problem
                for problem in result["problems"]
            ),
            result["problems"],
        )


if __name__ == "__main__":
    unittest.main()
