from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from freeze_attestation import verify_freeze_attestation

PATH = Path("governance-r8/freeze-attestations/Q14-FREEZE-ATTESTATION.json")


class FreezeAttestationTests(unittest.TestCase):
    def setUp(self):
        self.value = json.loads(PATH.read_text(encoding="utf-8"))

    def resolver(self, root, revision):
        if revision.endswith("^{tree}"):
            return self.value["candidate_tree"]
        return self.value["candidate_commit"]

    def test_exact_external_attestation_verifies(self):
        self.assertTrue(verify_freeze_attestation(self.value, resolver=self.resolver))

    def test_ref_or_tree_mismatch_fails(self):
        for field in ("candidate_commit", "candidate_tree"):
            bad = copy.deepcopy(self.value); bad[field] = "f" * 40
            self.assertFalse(verify_freeze_attestation(bad, resolver=self.resolver))

    def test_authority_and_operating_posture_are_exact(self):
        for field, value in (("authority_effect", "MERGE"), ("fallback_to_3", "INACTIVE"), ("six_slice_cadence", "RESTORED")):
            bad = copy.deepcopy(self.value); bad[field] = value
            self.assertFalse(verify_freeze_attestation(bad, resolver=self.resolver))

    def test_real_frozen_ref_and_tree_resolve(self):
        self.assertTrue(verify_freeze_attestation(self.value))


if __name__ == "__main__":
    unittest.main()
