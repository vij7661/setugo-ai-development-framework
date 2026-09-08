from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import platform_candidate_review_v2 as review_v2

CANDIDATE = "1" * 40


class EvidenceMaterializationV2Tests(unittest.TestCase):
    def test_gem_01_history_is_materialized_not_skipped(self):
        item = review_v2.materialize_evidence_ref(Path("."), CANDIDATE, {"type": "history", "ref": "frozen history"})
        self.assertEqual(item["type"], "history")
        self.assertEqual(item["content"], "frozen history")
        self.assertEqual(item["authority_class"], "FROZEN_REQUEST_TEXT_NON_AUTHORITATIVE")

    @patch.object(review_v2, "_fetch_ci_run")
    def test_gem_02_ci_run_is_materialized_and_candidate_bound(self, fetch):
        fetch.return_value = {
            "id": 123,
            "name": "CI",
            "workflow_id": 9,
            "event": "push",
            "status": "completed",
            "conclusion": "success",
            "head_branch": "branch",
            "head_sha": CANDIDATE,
            "run_attempt": 1,
            "created_at": "2026-09-08T00:00:00Z",
            "updated_at": "2026-09-08T00:00:01Z",
        }
        item = review_v2.materialize_evidence_ref(Path("."), CANDIDATE, {"type": "ci_run", "ref": "123"})
        self.assertEqual(item["type"], "ci_run")
        self.assertEqual(item["content"]["head_sha"], CANDIDATE)

    @patch.object(review_v2, "_fetch_ci_run")
    def test_gem_03_ci_run_candidate_mismatch_fails_closed(self, fetch):
        fetch.return_value = {"id": 123, "head_sha": "2" * 40}
        with self.assertRaisesRegex(RuntimeError, "head_sha"):
            review_v2.materialize_evidence_ref(Path("."), CANDIDATE, {"type": "ci_run", "ref": "123"})

    def test_gem_04_unknown_type_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "unsupported evidence ref type"):
            review_v2.materialize_evidence_ref(Path("."), CANDIDATE, {"type": "url", "ref": "x"})

    def test_gem_05_malformed_history_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "history evidence ref required"):
            review_v2.materialize_evidence_ref(Path("."), CANDIDATE, {"type": "history", "ref": ""})

    @patch("platform_candidate_review_v2.subprocess.run")
    def test_gem_06_file_is_exact_candidate_bound(self, run):
        run.return_value = Mock(returncode=0, stdout=b"abc", stderr=b"")
        item = review_v2.materialize_evidence_ref(Path("."), CANDIDATE, {"type": "file", "ref": "governance-runtime/x.txt"})
        self.assertEqual(item["candidate_sha"], CANDIDATE)
        args = run.call_args.args[0]
        self.assertEqual(args[2], f"{CANDIDATE}:governance-runtime/x.txt")

    @patch.object(review_v2.legacy, "require_commit")
    @patch.object(review_v2.legacy, "git")
    @patch.object(review_v2, "materialize_evidence_ref")
    def test_gem_07_build_corpus_materializes_every_ref(self, materialize, git, require_commit):
        materialize.side_effect = [
            {"type": "file", "ref": "a"},
            {"type": "ci_run", "ref": "1"},
            {"type": "history", "ref": "h"},
        ]
        git.side_effect = ["2" * 40 + "\n", "diff"]
        request = {
            "artifact": {"commit": CANDIDATE},
            "evidence_refs": [
                {"type": "file", "ref": "a"},
                {"type": "ci_run", "ref": "1"},
                {"type": "history", "ref": "h"},
            ],
        }
        corpus = review_v2.build_corpus(Path("."), request)
        self.assertEqual(corpus["evidence_ref_count"], 3)
        self.assertEqual(corpus["materialized_evidence_count"], 3)
        self.assertEqual(materialize.call_count, 3)

    @patch.object(review_v2.legacy, "invoke")
    @patch.object(review_v2, "build_corpus")
    @patch.object(review_v2.legacy, "verify_request_integrity")
    def test_gem_08_materialization_failure_prevents_provider_call(self, verify, build, invoke):
        build.side_effect = RuntimeError("unsupported evidence")
        request = {"review_request_id": "X", "artifact": {"commit": CANDIDATE}}
        with tempfile.TemporaryDirectory() as td:
            req = Path(td) / "request.json"
            req.write_text(json.dumps(request), encoding="utf-8")
            with patch("sys.argv", ["platform_candidate_review_v2.py", "--request", str(req), "--output-dir", td, "--model", "m"]):
                with self.assertRaisesRegex(RuntimeError, "unsupported evidence"):
                    review_v2.main()
        invoke.assert_not_called()


if __name__ == "__main__":
    unittest.main()
