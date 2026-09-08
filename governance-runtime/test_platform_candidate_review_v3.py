from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import platform_candidate_review as legacy
import platform_candidate_review_v3 as v3

CANDIDATE = "a" * 40


def request(provider="groq", blind=True, model_class="groq", model=None):
    required = {"provider": provider}
    if model:
        required["model"] = model
    else:
        required["model_class"] = model_class
    return {
        "schema_version": 4,
        "review_request_id": "REV-TEST-001",
        "artifact": {"commit": CANDIDATE},
        "required_reviewer": required,
        "blind_review_required": blind,
        "required_review_dimensions": [
            {"id": "d1", "mandatory": True, "description": "one"},
            {"id": "d2", "mandatory": True, "description": "two"},
        ],
    }


def valid_review(provider="groq", model="openai/gpt-oss-120b", blind=True):
    return {
        "review_request_id": "REV-TEST-001",
        "reviewed_artifact_commit": CANDIDATE,
        "reviewer": {"provider": provider, "model": model},
        "disposition": "PASS",
        "findings": [],
        "evidence_assessment": "ok",
        "independence_attestation": legacy.BLIND_ATTESTATION if blind else legacy.EXPOSED_ATTESTATION,
        "review_coverage": [
            {"dimension_id": "d1", "status": "TESTED_SUPPORTED", "evidence": ["e1"], "assessment": "ok"},
            {"dimension_id": "d2", "status": "TESTED_SUPPORTED", "evidence": ["e2"], "assessment": "ok"},
        ],
    }


class MultiProviderReviewRunnerTests(unittest.TestCase):
    def test_mpr01_gemini_binding_routes(self):
        v3.verify_provider_binding(request(provider="gemini", model_class="gemini"), "gemini", "gemini-3.6-flash")
        self.assertEqual(v3.required_secret_name("gemini"), "GEMINI_API_KEY")

    def test_mpr02_groq_binding_routes(self):
        v3.verify_provider_binding(request(), "groq", "openai/gpt-oss-120b")
        self.assertEqual(v3.required_secret_name("groq"), "GROQ_API_KEY")

    def test_mpr03_provider_mismatch_fails(self):
        with self.assertRaisesRegex(ValueError, "does not match"):
            v3.verify_provider_binding(request(provider="gemini", model_class="gemini"), "groq", "openai/gpt-oss-120b")

    def test_mpr04_unsupported_provider_fails(self):
        with self.assertRaisesRegex(ValueError, "unsupported"):
            v3.verify_provider_binding(request(), "mystery", "x")
        with self.assertRaisesRegex(ValueError, "unsupported"):
            v3.required_secret_name("mystery")

    def test_mpr05_exact_model_substitution_fails(self):
        req = request(provider="groq", model="openai/gpt-oss-120b")
        with self.assertRaisesRegex(ValueError, "model does not match"):
            v3.verify_provider_binding(req, "groq", "qwen/qwen3.6-27b")

    def test_mpr06_groq_same_dimension_schema_passes(self):
        result = v3.validate(valid_review(), request(), "groq", "openai/gpt-oss-120b")
        self.assertTrue(result["valid"])
        self.assertTrue(result["all_mandatory_dimensions_supported"])

    def test_mpr07_r2_r3_attestation_enforced(self):
        r2 = valid_review(blind=True)
        r2["independence_attestation"] = legacy.EXPOSED_ATTESTATION
        self.assertFalse(v3.validate(r2, request(blind=True), "groq", "openai/gpt-oss-120b")["valid"])
        r3req = request(blind=False)
        r3 = valid_review(blind=False)
        r3["independence_attestation"] = legacy.BLIND_ATTESTATION
        self.assertFalse(v3.validate(r3, r3req, "groq", "openai/gpt-oss-120b")["valid"])

    def test_mpr08_runtime_identity_mismatch_fails(self):
        review = valid_review(provider="gemini", model="gemini-3.6-flash")
        result = v3.validate(review, request(), "groq", "openai/gpt-oss-120b")
        self.assertFalse(result["valid"])
        self.assertTrue(any("identity" in e for e in result["errors"]))

    def test_mpr09_missing_dimension_or_evidence_fails(self):
        review = valid_review()
        review["review_coverage"].pop()
        self.assertFalse(v3.validate(review, request(), "groq", "openai/gpt-oss-120b")["valid"])
        review = valid_review()
        review["review_coverage"][0]["evidence"] = []
        self.assertFalse(v3.validate(review, request(), "groq", "openai/gpt-oss-120b")["valid"])

    def test_mpr10_gemini_validation_regression_equivalent(self):
        req = request(provider="gemini", model_class="gemini")
        review = valid_review(provider="gemini", model="gemini-3.6-flash")
        new = v3.validate(copy.deepcopy(review), req, "gemini", "gemini-3.6-flash")
        old = legacy.validate(copy.deepcopy(review), req, "gemini-3.6-flash")
        self.assertEqual(new["valid"], old["valid"])
        self.assertEqual(new["effective_disposition"], old["effective_disposition"])
        self.assertEqual(new["all_mandatory_dimensions_supported"], old["all_mandatory_dimensions_supported"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
