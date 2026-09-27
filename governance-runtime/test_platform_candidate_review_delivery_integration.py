from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import platform_candidate_review_v2 as review_v2

CANDIDATE = "1" * 40
RAW = b"frozen history"
REQUEST = {
    "review_request_id": "REAL-PATH-DELIVERY-001",
    "request_hash": "2" * 64,
    "artifact": {"commit": CANDIDATE},
}
CORPUS = {
    "review_request": REQUEST,
    "candidate_commit": CANDIDATE,
    "candidate_diff": "diff",
    "evidence_artifacts": [{
        "type": "history", "ref": "frozen history", "content": "frozen history",
        "sha256": review_v2._sha_bytes(RAW), "bytes_utf8": len(RAW),
    }],
    "corpus_sha256": "3" * 64,
    "evidence_ref_count": 1,
    "materialized_evidence_count": 1,
}


def manifest(mode="PLATFORM_MATERIALIZED_CONTENT"):
    objects = [{
        "subject_id": f"review_request:{REQUEST['review_request_id']}", "source_path": "review-request.json", "commit_sha": CANDIDATE,
        "content_sha256": review_v2._sha_bytes(review_v2._canon(REQUEST)), "bytes": len(review_v2._canon(REQUEST)),
    }, {
        "subject_id": f"candidate_diff:{CANDIDATE}", "source_path": "candidate.diff", "commit_sha": CANDIDATE,
        "content_sha256": review_v2._sha_bytes(b"diff"), "bytes": 4,
    }, {
        "subject_id": "history:frozen history", "source_path": "history:frozen history", "commit_sha": CANDIDATE,
        "content_sha256": review_v2._sha_bytes(RAW), "bytes": len(RAW),
    }]
    return {
        "provider_identity": "gemini", "delivery_mode": mode, "repository": "a/b",
        "commit_sha": CANDIDATE, "review_request_id": REQUEST["review_request_id"],
        "request_hash": REQUEST["request_hash"], "corpus_sha256": CORPUS["corpus_sha256"], "accessed_objects": objects,
        "read_only": mode != "URL_ONLY", "mandatory_subjects_covered": mode != "URL_ONLY",
        "result_status": "SUCCESS",
    }


class RealReviewPathDeliveryTests(unittest.TestCase):
    def test_exact_materialized_delivery_is_admitted(self):
        review_v2.validate_corpus_delivery(REQUEST, CORPUS, manifest(), expected_repository="a/b")

    def run_main(self, value=None, *, include_argument=True):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            request_path = root / "request.json"
            request_path.write_text(json.dumps(REQUEST), encoding="utf-8")
            argv = ["platform_candidate_review_v2.py", "--request", str(request_path), "--output-dir", str(root / "out"), "--model", "m"]
            if include_argument:
                manifest_path = root / "manifest.json"
                manifest_path.write_text(json.dumps(value), encoding="utf-8")
                argv += ["--access-manifest", str(manifest_path)]
            with patch.object(sys, "argv", argv), patch.dict("os.environ", {"GITHUB_REPOSITORY":"a/b", "GEMINI_API_KEY":"test-only"}), patch.object(review_v2.legacy, "verify_request_integrity"), patch.object(review_v2, "build_corpus", return_value=CORPUS), patch.object(review_v2.legacy, "invoke") as invoke:
                with self.assertRaises((ValueError, SystemExit)):
                    review_v2.main()
                invoke.assert_not_called()

    def test_url_only_prevents_provider_invocation(self):
        self.run_main(manifest("URL_ONLY"))

    def test_other_real_access_modes_cannot_claim_materialized_path(self):
        for mode in ("AUTHENTICATED_GITHUB_MCP_READ_ONLY", "PROVIDER_URL_CONTEXT"):
            self.run_main(manifest(mode))

    def test_wrong_source_object_fails_even_when_bytes_match(self):
        value=manifest(); value["accessed_objects"][0]["source_path"]="wrong-object.json"
        self.run_main(value)

    def test_omitted_manifest_prevents_provider_invocation(self):
        self.run_main(include_argument=False)

    def test_incomplete_delivery_prevents_provider_invocation(self):
        value = manifest()
        value["accessed_objects"] = []
        self.run_main(value)

    def test_candidate_or_request_mismatch_prevents_provider_invocation(self):
        for field, value in (("commit_sha", "f" * 40), ("request_hash", "f" * 64)):
            bad = manifest(); bad[field] = value
            self.run_main(bad)

    def test_false_truthfulness_fields_prevent_provider_invocation(self):
        for field, value in (("mandatory_subjects_covered", False), ("result_status", "FAILED"), ("provider_identity", "other"), ("repository", "wrong/repo")):
            bad = manifest(); bad[field] = value
            self.run_main(bad)

    def test_admitted_manifest_is_persisted_and_envelope_bound(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); req=root/"request.json"; access=root/"manifest.json"; out=root/"out"; value=manifest()
            req.write_text(json.dumps(REQUEST),encoding="utf-8"); access.write_text(json.dumps(value),encoding="utf-8")
            argv=["platform_candidate_review_v2.py","--request",str(req),"--output-dir",str(out),"--model","m","--access-manifest",str(access)]
            with patch.object(sys,"argv",argv), patch.dict("os.environ",{"GITHUB_REPOSITORY":"a/b","GEMINI_API_KEY":"test-only"}), patch.object(review_v2.legacy,"verify_request_integrity"), patch.object(review_v2,"build_corpus",return_value=CORPUS), patch.object(review_v2.legacy,"build_prompt",return_value="prompt"), patch.object(review_v2.legacy,"invoke",return_value=({},{})), patch.object(review_v2.legacy,"validate",return_value={"valid":True}):
                review_v2.main()
            persisted=(out/"access-manifest.json").read_bytes()
            self.assertEqual(persisted,review_v2._canon(value))
            envelope=json.loads((out/"execution-envelope.json").read_text(encoding="utf-8"))
            self.assertEqual(envelope["access_manifest_sha256"],review_v2._sha_bytes(persisted)); self.assertEqual(envelope["delivery_mode"],"PLATFORM_MATERIALIZED_CONTENT"); self.assertEqual(envelope["repository"],"a/b")


if __name__ == "__main__":
    unittest.main()
