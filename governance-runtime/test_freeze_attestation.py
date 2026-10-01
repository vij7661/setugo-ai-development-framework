from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from freeze_attestation import canonical_sha256, verify_freeze_attestation

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

    def statement(self, kind, run="101", job="202"):
        value = {"schema": "r8-candidate-execution-evidence/v1", "kind": kind, "run_id": run, "job_id": job, "workflow_identity": "r8/q16", "baseline_commit": "b" * 40, "candidate_commit": self.value["candidate_commit"], "candidate_tree": self.value["candidate_tree"], "changed_file_count": 53, "conclusion": "SUCCESS" if kind == "LINUX_VALIDATION" else "GENERATED", "artifact_digest": "sha256:" + "e" * 64}
        value["statement_sha256"] = canonical_sha256(value)
        return value

    def test_v2_binds_execution_statements_to_candidate(self):
        v2 = {key: copy.deepcopy(value) for key, value in self.value.items() if key not in {"linux_validation", "review_packet"}}
        v2["schema"] = "r8-external-freeze-attestation/v2"
        v2["linux_validation_statement"] = self.statement("LINUX_VALIDATION")
        v2["review_packet_statement"] = self.statement("REVIEW_PACKET", "303", "404")
        self.assertTrue(verify_freeze_attestation(v2, resolver=self.resolver))
        for field in ("linux_validation_statement", "review_packet_statement"):
            bad = copy.deepcopy(v2); bad[field]["candidate_commit"] = "f" * 40
            self.assertFalse(verify_freeze_attestation(bad, resolver=self.resolver))
            stale = copy.deepcopy(v2); stale[field]["run_id"] = "999"
            self.assertFalse(verify_freeze_attestation(stale, resolver=self.resolver))


if __name__ == "__main__":
    unittest.main()
