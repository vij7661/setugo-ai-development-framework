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
        "path": f"review_request:{REQUEST['review_request_id']}", "commit_sha": CANDIDATE,
        "content_sha256": review_v2._sha_bytes(review_v2._canon(REQUEST)), "bytes": len(review_v2._canon(REQUEST)),
    }, {
        "path": f"candidate_diff:{CANDIDATE}", "commit_sha": CANDIDATE,
        "content_sha256": review_v2._sha_bytes(b"diff"), "bytes": 4,
    }, {
        "path": "history:frozen history", "commit_sha": CANDIDATE,
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
        review_v2.validate_corpus_delivery(REQUEST, CORPUS, manifest())

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
            with patch.object(sys, "argv", argv), patch.object(review_v2.legacy, "verify_request_integrity"), patch.object(review_v2, "build_corpus", return_value=CORPUS), patch.object(review_v2.legacy, "invoke") as invoke:
                with self.assertRaises((ValueError, SystemExit)):
                    review_v2.main()
                invoke.assert_not_called()

    def test_url_only_prevents_provider_invocation(self):
        self.run_main(manifest("URL_ONLY"))

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


if __name__ == "__main__":
    unittest.main()
