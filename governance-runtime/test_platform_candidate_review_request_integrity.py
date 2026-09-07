from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import platform_candidate_review as platform_review
from review_protocol import build_review_request


CANDIDATE = "1" * 40
DIMENSIONS = [
    {
        "id": "request_integrity",
        "mandatory": True,
        "description": "The exact ReviewRequest must be integrity-verified before provider invocation.",
    }
]


def valid_request(request_id: str = "GRI-VALID-001") -> dict:
    return build_review_request(
        review_request_id=request_id,
        trigger="MATERIAL_GOVERNANCE_CHANGE",
        artifact_type="governance_review_candidate",
        artifact_ref="test",
        artifact_commit=CANDIDATE,
        proposer={"provider": "openai", "model": "gpt-5.6-sol"},
        required_reviewer={"provider": "gemini", "model_class": "gemini"},
        blind_review_required=True,
        review_questions=["Verify request integrity."],
        evidence_refs=[{"type": "history", "ref": "frozen regression"}],
        material_authority_transition=True,
        required_review_dimensions=DIMENSIONS,
    )


def valid_review(request_id: str = "GRI-VALID-001") -> dict:
    return {
        "review_request_id": request_id,
        "reviewed_artifact_commit": CANDIDATE,
        "reviewer": {"provider": "gemini", "model": "gemini-3.6-flash"},
        "disposition": "PASS",
        "findings": [],
        "evidence_assessment": "Exact request integrity and bounded review path supported.",
        "independence_attestation": "BLIND_TO_PROPOSER_CONCLUSION",
        "review_coverage": [
            {
                "dimension_id": "request_integrity",
                "status": "TESTED_SUPPORTED",
                "evidence": ["frozen regression"],
                "assessment": "supported",
            }
        ],
    }


class PlatformCandidateReviewRequestIntegrityTests(unittest.TestCase):
    def test_gri_01_invalid_hash_rejected_by_integrity_gate(self):
        request = valid_request("GRI-INVALID-HASH")
        request["request_hash"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "review request hash is invalid"):
            platform_review.verify_request_integrity(request)

    def test_gri_02_missing_hash_rejected_by_integrity_gate(self):
        request = valid_request("GRI-MISSING-HASH")
        request.pop("request_hash")
        with self.assertRaisesRegex(ValueError, "review request is malformed"):
            platform_review.verify_request_integrity(request)

    def test_gri_03_valid_schema_v4_request_is_accepted(self):
        request = valid_request()
        self.assertIs(platform_review.verify_request_integrity(request), request)

    def test_gri_04_main_rejects_invalid_request_before_corpus_or_provider(self):
        request = valid_request("GRI-MAIN-INVALID")
        request["request_hash"] = "f" * 64
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            request_path = root / "request.json"
            output_dir = root / "out"
            request_path.write_text(json.dumps(request), encoding="utf-8")
            argv = [
                "platform_candidate_review.py",
                "--request", str(request_path),
                "--output-dir", str(output_dir),
                "--model", "gemini-3.6-flash",
            ]
            with patch.object(sys, "argv", argv), \
                 patch.dict(os.environ, {"GEMINI_API_KEY": "synthetic-test-key"}, clear=False), \
                 patch.object(platform_review, "build_corpus") as build_corpus, \
                 patch.object(platform_review, "invoke") as invoke:
                with self.assertRaisesRegex(ValueError, "review request hash is invalid"):
                    platform_review.main()
                build_corpus.assert_not_called()
                invoke.assert_not_called()

    def test_gri_05_valid_request_still_reaches_existing_provider_path(self):
        request = valid_request("GRI-MAIN-VALID")
        review = valid_review("GRI-MAIN-VALID")
        corpus = {
            "schema_version": 1,
            "review_request": request,
            "base_commit": "2" * 40,
            "candidate_commit": CANDIDATE,
            "candidate_diff": "",
            "evidence_artifacts": [],
            "posture": "test",
        }
        provider_response = {
            "candidates": [
                {"finishReason": "STOP", "content": {"parts": [{"text": json.dumps(review)}]}}
            ]
        }
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            request_path = root / "request.json"
            output_dir = root / "out"
            request_path.write_text(json.dumps(request), encoding="utf-8")
            argv = [
                "platform_candidate_review.py",
                "--request", str(request_path),
                "--output-dir", str(output_dir),
                "--model", "gemini-3.6-flash",
            ]
            with patch.object(sys, "argv", argv), \
                 patch.dict(os.environ, {"GEMINI_API_KEY": "synthetic-test-key"}, clear=False), \
                 patch.object(platform_review, "build_corpus", return_value=corpus) as build_corpus, \
                 patch.object(platform_review, "invoke", return_value=(provider_response, review)) as invoke:
                platform_review.main()
                build_corpus.assert_called_once()
                invoke.assert_called_once()
                validation = json.loads((output_dir / "validation.json").read_text(encoding="utf-8"))
                self.assertTrue(validation["valid"])
                self.assertEqual(validation["effective_disposition"], "PASS")


if __name__ == "__main__":
    unittest.main()
