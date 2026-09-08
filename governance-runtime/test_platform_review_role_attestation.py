from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0,str(HERE))

import platform_candidate_review as reviewmod  # noqa: E402

DIMS=[{"id":"d1","mandatory":True,"description":"dimension"}]

def request(blind: bool):
    return {
        "review_request_id":"REV-ROLE-TEST",
        "artifact":{"commit":"a"*40},
        "blind_review_required":blind,
        "required_review_dimensions":copy.deepcopy(DIMS),
    }

def result(attestation: str):
    return {
        "review_request_id":"REV-ROLE-TEST",
        "reviewed_artifact_commit":"a"*40,
        "reviewer":{"provider":"gemini","model":"gemini-test"},
        "disposition":"PASS",
        "findings":[],
        "evidence_assessment":"supported",
        "independence_attestation":attestation,
        "review_coverage":[{"dimension_id":"d1","status":"TESTED_SUPPORTED","evidence":["e1"],"assessment":"ok"}],
    }

class PlatformReviewRoleAttestationTests(unittest.TestCase):
    def test_ra_01_blind_prompt_keeps_independent_role(self):
        p=reviewmod.build_prompt(request(True),{"evidence_artifacts":[]},"gemini-test")
        self.assertIn("independent adversarial reviewer",p)
        self.assertIn(reviewmod.BLIND_ATTESTATION,p)

    def test_ra_02_exposed_prompt_is_review_of_review(self):
        p=reviewmod.build_prompt(request(False),{"evidence_artifacts":[]},"gemini-test")
        self.assertIn("R3 adversarial review-of-review critic",p)
        self.assertIn("NOT independent of R2",p)
        self.assertIn(reviewmod.EXPOSED_ATTESTATION,p)

    def test_ra_03_blind_rejects_exposed_attestation(self):
        v=reviewmod.validate(result(reviewmod.EXPOSED_ATTESTATION),request(True),"gemini-test")
        self.assertFalse(v["valid"])
        self.assertIn("attestation mismatch"," ".join(v["errors"]))

    def test_ra_04_exposed_rejects_blind_attestation(self):
        v=reviewmod.validate(result(reviewmod.BLIND_ATTESTATION),request(False),"gemini-test")
        self.assertFalse(v["valid"])
        self.assertIn("attestation mismatch"," ".join(v["errors"]))

    def test_ra_05_exposed_correct_attestation_valid(self):
        v=reviewmod.validate(result(reviewmod.EXPOSED_ATTESTATION),request(False),"gemini-test")
        self.assertTrue(v["valid"],v)
        self.assertEqual(v["effective_disposition"],"PASS")

    def test_ra_06_existing_blind_r2_validation_unchanged(self):
        v=reviewmod.validate(result(reviewmod.BLIND_ATTESTATION),request(True),"gemini-test")
        self.assertTrue(v["valid"],v)
        self.assertTrue(v["all_mandatory_dimensions_supported"])

if __name__=="__main__":
    unittest.main(verbosity=2)
