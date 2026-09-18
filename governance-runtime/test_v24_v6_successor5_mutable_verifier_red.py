from __future__ import annotations

import unittest

import v24_v6_proof_reference_closure as prc
from test_v24_v6_successor4_external_anchor_red import (
    TARGET_CONTENT,
    attacker_constructed_bundle,
)


class Successor5MutableVerifierRed(unittest.TestCase):
    def test_same_process_imported_verifier_substitution_cannot_self_grant(self):
        context, boundary, leaf_ref = attacker_constructed_bundle()

        original = prc.validate_root_attestation
        try:
            # Manual-review attack C-01: the same candidate process replaces the
            # imported verifier decision with unconditional success.
            prc.validate_root_attestation = lambda *args, **kwargs: []

            result = prc.resolve_governed_qualification(
                leaf_ref,
                context,
                boundary,
                expected_subject_id="ATTACK-TARGET",
                expected_subject_content_digest=TARGET_CONTENT,
            )
        finally:
            prc.validate_root_attestation = original

        # This is intentionally RED against frozen Successor-4.  A future
        # Successor-5 authority-bearing gate must remain closed even when this
        # Python-local verifier is replaced.
        self.assertFalse(result["qualified"], result)
        self.assertNotEqual("PROOF_REFERENCE_CLOSED", result["state"], result)


if __name__ == "__main__":
    unittest.main()
