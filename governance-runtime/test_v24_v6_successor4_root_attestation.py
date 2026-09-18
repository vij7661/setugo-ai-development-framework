from __future__ import annotations

import copy
import os
import unittest

from test_v24_v6_proof_reference_closure import (
    ROOT_CONTENT,
    proof_bundle,
)
from test_v24_v6_successor4_external_anchor_red import (
    TARGET_CONTENT as ATTACK_TARGET_CONTENT,
    attacker_constructed_bundle,
)
from v24_v6_proof_reference_closure import (
    PROOF_REFERENCE_CLOSED,
    TRUSTED_BOUNDARY_ANCHOR_ENV,
    resolve_governed_qualification,
    seal_proof_context,
    trusted_boundary_anchor_digest,
)


class Successor4RootAttestationRegressions(unittest.TestCase):
    def test_signed_context_positive(self):
        context, boundary, refs = proof_bundle()
        result = resolve_governed_qualification(
            refs["root"],
            context,
            boundary,
            expected_subject_id="ROOT-VERIFIER",
            expected_subject_content_digest=ROOT_CONTENT,
        )
        self.assertTrue(result["qualified"], result)
        self.assertEqual(PROOF_REFERENCE_CLOSED, result["state"])

    def test_unsigned_context_rejected(self):
        context, boundary, refs = proof_bundle()
        unsigned = copy.deepcopy(boundary)
        unsigned.pop("root_attestation", None)
        result = resolve_governed_qualification(
            refs["root"],
            context,
            unsigned,
            expected_subject_id="ROOT-VERIFIER",
            expected_subject_content_digest=ROOT_CONTENT,
        )
        self.assertFalse(result["qualified"], result)
        self.assertIn("ROOT_ATTESTATION_REQUIRED", result["problems"])

    def test_wrong_context_signature_rejected(self):
        context, boundary, refs = proof_bundle()
        forged_context = copy.deepcopy(context)
        forged_context["proof_context_id"] = "CTX-WRONG-SIGNATURE-TARGET"
        seal_proof_context(forged_context)

        forged_boundary = copy.deepcopy(boundary)
        forged_boundary["expected_proof_context_digest"] = forged_context["context_digest"]
        forged_boundary["root_attestation"]["proof_context_digest"] = forged_context[
            "context_digest"
        ]
        # Keep A's signature while claiming it signs B's exact material.
        result = resolve_governed_qualification(
            refs["root"],
            forged_context,
            forged_boundary,
            expected_subject_id="ROOT-VERIFIER",
            expected_subject_content_digest=ROOT_CONTENT,
        )
        self.assertFalse(result["qualified"], result)
        self.assertIn("ROOT_ATTESTATION_SIGNATURE_INVALID", result["problems"])

    def test_caller_selected_public_key_rejected(self):
        context, boundary, refs = proof_bundle()
        forged_boundary = copy.deepcopy(boundary)
        forged_boundary["root_attestation"]["rsa_modulus_hex"] = "01"
        forged_boundary["root_attestation"]["rsa_public_exponent"] = 3
        result = resolve_governed_qualification(
            refs["root"],
            context,
            forged_boundary,
            expected_subject_id="ROOT-VERIFIER",
            expected_subject_content_digest=ROOT_CONTENT,
        )
        self.assertFalse(result["qualified"], result)
        self.assertIn("ROOT_ATTESTATION_FIELDS_EXACT_REQUIRED", result["problems"])

    def test_attestation_scope_substitution_rejected(self):
        context, boundary, refs = proof_bundle()
        forged_boundary = copy.deepcopy(boundary)
        substituted_scope = "ab" * 32
        forged_boundary["expected_genesis_scope_digest"] = substituted_scope
        forged_boundary["root_attestation"][
            "genesis_trusted_scope_digest"
        ] = substituted_scope
        result = resolve_governed_qualification(
            refs["root"],
            context,
            forged_boundary,
            expected_subject_id="ROOT-VERIFIER",
            expected_subject_content_digest=ROOT_CONTENT,
        )
        self.assertFalse(result["qualified"], result)
        self.assertTrue(
            "ROOT_ATTESTATION_SIGNATURE_INVALID" in result["problems"]
            or "PROOF_CONTEXT_GENESIS_TRUSTED_BINDING_MISMATCH" in result["problems"],
            result,
        )

    def test_same_process_anchor_rewrite_rejected(self):
        context, boundary, leaf_ref = attacker_constructed_bundle()
        old = os.environ.get(TRUSTED_BOUNDARY_ANCHOR_ENV)
        try:
            os.environ[TRUSTED_BOUNDARY_ANCHOR_ENV] = trusted_boundary_anchor_digest(
                boundary
            )
            result = resolve_governed_qualification(
                leaf_ref,
                context,
                boundary,
                expected_subject_id="ATTACK-TARGET",
                expected_subject_content_digest=ATTACK_TARGET_CONTENT,
            )
        finally:
            if old is None:
                os.environ.pop(TRUSTED_BOUNDARY_ANCHOR_ENV, None)
            else:
                os.environ[TRUSTED_BOUNDARY_ANCHOR_ENV] = old

        self.assertFalse(result["qualified"], result)
        self.assertNotEqual(PROOF_REFERENCE_CLOSED, result["state"])
        self.assertIn("ROOT_ATTESTATION_REQUIRED", result["problems"])


if __name__ == "__main__":
    unittest.main()
