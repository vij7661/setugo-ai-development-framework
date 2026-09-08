from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
KERNEL = HERE / "review-trust-kernel"
if str(KERNEL) not in sys.path:
    sys.path.insert(0, str(KERNEL))

import sequential_review_v2 as v2  # noqa: E402


REQUEST = {
    "review_request_id": "REV-X",
    "artifact": {"commit": "a" * 40},
    "required_reviewer": {"provider": "gemini", "model_class": "gemini"},
}

R2 = {
    "review_request_id": "REV-X",
    "reviewed_artifact_commit": "a" * 40,
    "reviewer": {"provider": "gemini", "model": "gemini-3.6-flash"},
    "disposition": "PASS",
    "findings": [],
    "evidence_assessment": "supported",
    "independence_attestation": "BLIND_TO_PROPOSER_CONCLUSION",
    "review_coverage": [
        {"dimension_id": "d1", "status": "TESTED_SUPPORTED", "assessment": "ok", "evidence": ["e1"]}
    ],
}

POLICY = {
    "risk_class": "PERSISTENCE",
    "promotion_authoritative": True,
    "policy_requires_dual_review": True,
    "material_uncertainty_requires_r3": True,
}

CORPUS = "sha256:" + "1" * 64
MANIFEST = "sha256:" + "2" * 64


def build(r2=R2, policy=POLICY):
    return v2.build_frozen_platform_handoff(
        review_request=REQUEST,
        policy=policy,
        r2_result=r2,
        corpus_hash=CORPUS,
        evidence_manifest_hash=MANIFEST,
        provider_api_authenticated=True,
    )


class SequentialReviewV2Tests(unittest.TestCase):
    def test_v2_01_accepts_platform_r2_losslessly(self):
        handoff = build()
        self.assertEqual(handoff["r2_raw"], R2)
        self.assertEqual(handoff["candidate_sha"], "a" * 40)
        self.assertTrue(handoff["r3_required"])

    def test_v2_02_candidate_mismatch_fails_closed(self):
        bad = copy.deepcopy(R2)
        bad["reviewed_artifact_commit"] = "b" * 40
        with self.assertRaisesRegex(ValueError, "candidate mismatch"):
            build(bad)

    def test_v2_03_request_id_mismatch_fails_closed(self):
        bad = copy.deepcopy(R2)
        bad["review_request_id"] = "REV-Y"
        with self.assertRaisesRegex(ValueError, "ReviewRequest ID mismatch"):
            build(bad)

    def test_v2_04_missing_review_coverage_fails_closed(self):
        bad = copy.deepcopy(R2)
        bad.pop("review_coverage")
        with self.assertRaisesRegex(ValueError, "missing mandatory fields"):
            build(bad)

    def test_v2_05_missing_reviewer_identity_fails_closed(self):
        bad = copy.deepcopy(R2)
        bad["reviewer"] = {"provider": "gemini", "model": ""}
        with self.assertRaisesRegex(ValueError, "reviewer.model required"):
            build(bad)

    def test_v2_06_r1_middle_opinion_fields_fail_closed(self):
        bad = copy.deepcopy(R2)
        bad["r1_recommendation"] = "promote"
        with self.assertRaisesRegex(ValueError, "forbidden"):
            build(bad)

    def test_v2_07_raw_r2_hash_changes_on_material_mutation(self):
        a = build()
        bad = copy.deepcopy(R2)
        bad["evidence_assessment"] = "changed"
        b = build(bad)
        self.assertNotEqual(a["r2_raw_hash"], b["r2_raw_hash"])
        self.assertNotEqual(a["handoff_hash"], b["handoff_hash"])

    def test_v2_08_high_risk_pass_still_requires_r3(self):
        self.assertTrue(build()["r3_required"])

    def test_v2_09_high_risk_fail_still_requires_r3(self):
        bad = copy.deepcopy(R2)
        bad["disposition"] = "FAIL"
        self.assertTrue(build(bad)["r3_required"])

    def test_v2_10_handoff_verification_detects_mutation(self):
        handoff = build()
        self.assertTrue(v2.verify_frozen_platform_handoff(
            handoff,
            review_request=REQUEST,
            policy=POLICY,
            r2_result=R2,
            corpus_hash=CORPUS,
            evidence_manifest_hash=MANIFEST,
            provider_api_authenticated=True,
        ))
        mutated = copy.deepcopy(handoff)
        mutated["r2_raw"]["evidence_assessment"] = "tampered"
        self.assertFalse(v2.verify_frozen_platform_handoff(
            mutated,
            review_request=REQUEST,
            policy=POLICY,
            r2_result=R2,
            corpus_hash=CORPUS,
            evidence_manifest_hash=MANIFEST,
            provider_api_authenticated=True,
        ))


if __name__ == "__main__":
    unittest.main(verbosity=2)
