from __future__ import annotations

import copy
import json
import os
import unittest
from pathlib import Path

from test_v24_v6_proof_reference_closure import proof_bundle
from v24_v6_construction_root_attestation import (
    ATTESTATION_REJECTED,
    ATTESTATION_VALID,
    verify_construction_attestation,
)
from v24_v6_proof_reference_closure import (
    TRUSTED_BOUNDARY_ANCHOR_ENV,
    trusted_boundary_anchor_digest,
)

FIXTURE_PATH = Path(__file__).with_name("fixtures") / "v24_v6_successor4_positive_attestation.json"


def positive_attestation() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))["attestation"]


class Successor4ConstructionRootAttestationTests(unittest.TestCase):
    def test_signed_context_positive(self):
        context, boundary, _ = proof_bundle()
        attestation = positive_attestation()
        self.assertEqual(context["context_digest"], attestation["proof_context_digest"])
        self.assertEqual(
            context["genesis_trusted_scope"]["scope_digest"],
            attestation["genesis_scope_digest"],
        )
        result = verify_construction_attestation(context, boundary, attestation)
        self.assertTrue(result["qualified"], result)
        self.assertEqual(ATTESTATION_VALID, result["state"])

    def test_unsigned_context_rejected(self):
        context, boundary, _ = proof_bundle()
        result = verify_construction_attestation(context, boundary, None)
        self.assertFalse(result["qualified"], result)
        self.assertEqual(ATTESTATION_REJECTED, result["state"])
        self.assertIn("CONSTRUCTION_ROOT_ATTESTATION_REQUIRED", result["problems"])

    def test_wrong_context_signature_rejected(self):
        context, boundary, _ = proof_bundle()
        context = copy.deepcopy(context)
        context["context_digest"] = "0" * 64
        boundary = copy.deepcopy(boundary)
        boundary["expected_proof_context_digest"] = context["context_digest"]
        attestation = copy.deepcopy(positive_attestation())
        attestation["proof_context_digest"] = context["context_digest"]
        result = verify_construction_attestation(context, boundary, attestation)
        self.assertFalse(result["qualified"], result)
        self.assertIn("ATTESTATION_SIGNATURE_INVALID", result["problems"])

    def test_caller_selected_public_key_rejected(self):
        context, boundary, _ = proof_bundle()
        attestation = copy.deepcopy(positive_attestation())
        attestation["rsa_public_exponent"] = 3
        attestation["rsa_modulus_hex"] = "01"
        result = verify_construction_attestation(context, boundary, attestation)
        self.assertFalse(result["qualified"], result)
        self.assertTrue(
            any(p.startswith("ATTESTATION_FIELD_NOT_ALLOWED:") for p in result["problems"]),
            result,
        )

    def test_attestation_scope_substitution_rejected(self):
        context, boundary, _ = proof_bundle()
        attestation = copy.deepcopy(positive_attestation())
        attestation["genesis_scope_digest"] = "f" * 64
        result = verify_construction_attestation(context, boundary, attestation)
        self.assertFalse(result["qualified"], result)
        self.assertIn("ATTESTATION_CONTEXT_SCOPE_DIGEST_MISMATCH", result["problems"])
        self.assertIn("ATTESTATION_SIGNATURE_INVALID", result["problems"])

    def test_same_process_anchor_rewrite_does_not_create_attestation(self):
        context, boundary, _ = proof_bundle()
        old = os.environ.get(TRUSTED_BOUNDARY_ANCHOR_ENV)
        try:
            os.environ[TRUSTED_BOUNDARY_ANCHOR_ENV] = trusted_boundary_anchor_digest(boundary)
            result = verify_construction_attestation(context, boundary, None)
        finally:
            if old is None:
                os.environ.pop(TRUSTED_BOUNDARY_ANCHOR_ENV, None)
            else:
                os.environ[TRUSTED_BOUNDARY_ANCHOR_ENV] = old
        self.assertFalse(result["qualified"], result)
        self.assertIn("CONSTRUCTION_ROOT_ATTESTATION_REQUIRED", result["problems"])


if __name__ == "__main__":
    unittest.main()
