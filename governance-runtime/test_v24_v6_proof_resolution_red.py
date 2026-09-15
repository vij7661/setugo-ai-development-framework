from __future__ import annotations

import unittest

from test_v24_v6_atomic_binding_modes import base_sources
from test_v24_v6_decision_apply import bundle
from test_v24_v6_effect_ledger_closure import durable_ledger, registry_and_path_fixture
from test_v24_v6_endpoint_projection import endpoint_bundle
from test_v24_v6_material_surface import ledger_bundle
from test_v24_v6_normative_clause_projection import qualified_disposition_bundle
from v24_v6_atomic_binding_modes import derive_atomic_binding_mode_obligation_set
from v24_v6_decision_apply import evaluate_decision_apply_latch
from v24_v6_effect_ledger_closure import (
    validate_durable_governance_ledger,
    validate_effect_path_against_registry,
)
from v24_v6_endpoint_projection import compile_qualified_endpoint_table
from v24_v6_material_surface import validate_material_observation_ledger
from v24_v6_normative_clause_projection import qualify_normative_dispositions


class V24V6ProofResolutionRegressionTests(unittest.TestCase):
    """Permanent regressions for proof-substitution false-greens found after R9.

    Historical R4 RED is preserved by workflow run 35000549932. Additional
    authority paths are falsified before each repair and retained here so a later
    refactor cannot reintroduce label-as-proof or digest-substitution behavior.
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

    def test_opaque_durable_ledger_head_and_witness_labels_cannot_qualify(self):
        candidate = durable_ledger()
        head = candidate["head"]
        witness = head["witness_currentness_records"][0]
        self.assertEqual(head["head_qualification_state"], "QUALIFIED")
        self.assertEqual(head["currentness_result"], "CURRENT")
        self.assertEqual(witness["independence_result"], "QUALIFIED")
        self.assertEqual(witness["currentness_result"], "CURRENT")
        self.assertNotIn("head_qualification_digest", head)
        self.assertNotIn("witness_qualification_digest", witness)

        result = validate_durable_governance_ledger(
            candidate,
            ledger_kind="MATERIAL_OBSERVATION",
        )
        self.assertFalse(
            result["qualified"],
            "V6 false-green: opaque durable-ledger labels qualified the current head",
        )
        self.assertTrue(
            any(
                "LEDGER_HEAD_PROOF" in problem
                or "LEDGER_WITNESS_PROOF" in problem
                or "TRUSTED_PROOF_BOUNDARY_REQUIRED" in problem
                or "PROOF_REFERENCE" in problem
                for problem in result["problems"]
            ),
            result["problems"],
        )

    def test_registered_effect_class_substitution_invalidates_path_currentness(self):
        path, registry_result, context, boundary = registry_and_path_fixture(
            "STATE_WRITE"
        )
        self.assertIn("REMOTE_EFFECT", registry_result["actual_members"])
        old_content_digest = path["path_content_digest"]
        old_currentness = path["currentness_binding_digest"]

        path["effect_class_id"] = "REMOTE_EFFECT"
        self.assertEqual(path["path_content_digest"], old_content_digest)
        self.assertEqual(path["currentness_binding_digest"], old_currentness)

        result = validate_effect_path_against_registry(
            path,
            current_observation_head_digest="9" * 64,
            registry_result=registry_result,
            proof_context=context,
            trusted_boundary=boundary,
        )
        self.assertFalse(
            result["qualified"],
            "V6 false-green: registered effect-class substitution reused stale path currentness",
        )
        self.assertTrue(
            any(
                "PATH_CONTENT_DIGEST_MISMATCH" in problem
                or "PATH_CURRENTNESS" in problem
                or "MATERIAL_EFFECT_PATH_PROOF" in problem
                for problem in result["problems"]
            ),
            result["problems"],
        )

    def test_opaque_atomic_binding_contract_and_mechanism_labels_cannot_define_obligations(self):
        candidate = base_sources()
        contract = candidate["binding_contracts"][0]
        mechanism = candidate["admitted_binding_mechanisms"][0]
        self.assertEqual(contract["qualification_state"], "QUALIFIED")
        self.assertEqual(contract["authority_independence_state"], "QUALIFIED")
        self.assertEqual(contract["currentness_result"], "CURRENT")
        self.assertEqual(mechanism["admission_state"], "QUALIFIED")
        self.assertEqual(mechanism["qualification_state"], "QUALIFIED")
        self.assertEqual(mechanism["authority_independence_state"], "QUALIFIED")
        self.assertEqual(mechanism["currentness_result"], "CURRENT")
        self.assertNotIn("qualification_digest", contract)
        self.assertNotIn("currentness_binding_digest", contract)

        result = derive_atomic_binding_mode_obligation_set(candidate)

        # Pre-repair R7 accepts these state labels plus SHA-shaped content digests
        # as sufficient authority to define the complete atomic-binding universe.
        self.assertFalse(
            result["qualified"],
            "V6 false-green: opaque contract/mechanism labels defined atomic-binding obligations",
        )
        self.assertTrue(
            any(
                "ATOMIC_BINDING_CONTRACT_PROOF" in problem
                or "ATOMIC_BINDING_MECHANISM_PROOF" in problem
                or "TRUSTED_PROOF_BOUNDARY_REQUIRED" in problem
                or "PROOF_REFERENCE" in problem
                for problem in result["problems"]
            ),
            result["problems"],
        )


if __name__ == "__main__":
    unittest.main()
