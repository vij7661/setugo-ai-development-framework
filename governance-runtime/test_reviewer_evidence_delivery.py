"""Tests for reviewer evidence-delivery completeness and solution contracts."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from reviewer_evidence_delivery import (  # noqa: E402
    sha256_bytes,
    validate_finding_solution_contract,
    validate_solution_adjudication,
    verify_chunked_delivery,
    verify_material_delivery,
    validate_reviewer_access_manifest,
    validate_review_delivery_request,
    verify_whole_delivery,
)


class ReviewerEvidenceDeliveryTests(unittest.TestCase):
    def _manifest(self, mode="PLATFORM_MATERIALIZED_CONTENT"):
        commit = "a" * 40
        raw = b"data"
        obj = {"subject_id": "subject:data", "source_path": "review.txt", "commit_sha": commit, "content_sha256": sha256_bytes(raw), "bytes": len(raw)}
        if mode == "PLATFORM_MATERIALIZED_CONTENT":
            pass
        elif mode == "AUTHENTICATED_GITHUB_MCP_READ_ONLY":
            obj.update(repository="a/b", tool_access="read_only", tool_identity="github.read_file", object_id="blob:b")
        elif mode == "PROVIDER_URL_CONTEXT":
            obj.update(url=f"https://github.com/a/b/blob/{commit}/review.txt", object_id="blob:b")
        return {"provider_identity": "reviewer", "delivery_mode": mode, "repository": "a/b", "commit_sha": commit, "review_request_id": "R", "request_hash": "c" * 64, "corpus_sha256": "d" * 64, "accessed_objects": [obj], "read_only": mode != "URL_ONLY", "mandatory_subjects_covered": mode != "URL_ONLY", "result_status": "SUCCESS"}

    def test_access_manifest_modes_and_url_only_is_not_evidence(self):
        for mode in ("AUTHENTICATED_GITHUB_MCP_READ_ONLY", "PROVIDER_URL_CONTEXT", "PLATFORM_MATERIALIZED_CONTENT"):
            self.assertTrue(validate_reviewer_access_manifest(self._manifest(mode)))
        url_only = self._manifest("URL_ONLY")
        url_only["read_only"] = False
        url_only["mandatory_subjects_covered"] = False
        self.assertTrue(validate_reviewer_access_manifest(url_only))
        raw = b"data"
        item = {"delivery_mode": "native_file", "sha256": sha256_bytes(raw), "bytes": len(raw), "delivered": raw}
        self.assertFalse(validate_review_delivery_request([item], url_only))

    def test_access_manifest_rejects_mutable_or_secret_access(self):
        manifest = self._manifest("PROVIDER_URL_CONTEXT")
        manifest["accessed_objects"][0]["url"] = "https://github.com/a/b/blob/main/review.txt"
        self.assertFalse(validate_reviewer_access_manifest(manifest))
        manifest = self._manifest("AUTHENTICATED_GITHUB_MCP_READ_ONLY")
        manifest["accessed_objects"][0].pop("content_sha256")
        self.assertFalse(validate_reviewer_access_manifest(manifest))
        manifest = self._manifest("PROVIDER_URL_CONTEXT")
        manifest["accessed_objects"][0].pop("content_sha256")
        self.assertFalse(validate_reviewer_access_manifest(manifest))
        manifest = self._manifest()
        manifest["token"] = "must-not-persist"
        self.assertFalse(validate_reviewer_access_manifest(manifest))

    def test_delivery_request_requires_materialized_subject(self):
        raw = b"data"
        item = {"subject_id": "subject:data", "source_path": "review.txt", "commit_sha": "a"*40, "delivery_mode": "native_file", "sha256": sha256_bytes(raw), "bytes": len(raw), "delivered": raw}
        self.assertTrue(validate_review_delivery_request([item], self._manifest()))
        self.assertFalse(validate_review_delivery_request([item], self._manifest("URL_ONLY")))
        self.assertFalse(validate_review_delivery_request([item], self._manifest("AUTHENTICATED_GITHUB_MCP_READ_ONLY"), required_manifest_mode="PLATFORM_MATERIALIZED_CONTENT"))
    def test_url_and_mcp_require_exact_expected_source_object(self):
        raw=b"data"; item={"subject_id":"subject:data","source_path":"review.txt","commit_sha":"a"*40,"delivery_mode":"native_file","sha256":sha256_bytes(raw),"bytes":len(raw),"delivered":raw}
        expected={"subject:data":{"source_path":"review.txt","object_id":"blob:b","tool_identity":"github.read_file"}}
        self.assertTrue(validate_review_delivery_request([item],self._manifest("PROVIDER_URL_CONTEXT"),expected_objects=expected))
        bad=self._manifest("PROVIDER_URL_CONTEXT"); bad["accessed_objects"][0]["url"]=f"https://github.com/a/b/blob/{'a'*40}/wrong.txt"
        self.assertFalse(validate_review_delivery_request([item],bad,expected_objects=expected))
        self.assertTrue(validate_review_delivery_request([item],self._manifest("AUTHENTICATED_GITHUB_MCP_READ_ONLY"),expected_objects=expected))
        bad=self._manifest("AUTHENTICATED_GITHUB_MCP_READ_ONLY"); bad["accessed_objects"][0]["object_id"]="blob:wrong"
        self.assertFalse(validate_review_delivery_request([item],bad,expected_objects=expected))
    def test_summary_only_delivery_is_rejected(self):
        raw = b"complete material"
        item = {"delivery_mode": "native_file", "sha256": sha256_bytes(raw), "bytes": len(raw)}
        self.assertTrue(verify_material_delivery(item, raw))
        self.assertFalse(verify_material_delivery({"delivery_mode": "native_file", "sha256": sha256_bytes(raw), "bytes": len(raw), "summary": "summary only"}))

    def test_chunked_material_delivery_is_exact(self):
        raw = b"abcdef"
        chunks = [{"index": 0, "count": 2, "bytes": b"abc", "sha256": sha256_bytes(b"abc")}, {"index": 1, "count": 2, "bytes": b"def", "sha256": sha256_bytes(b"def")}]
        self.assertTrue(verify_material_delivery({"delivery_mode": "chunked", "sha256": sha256_bytes(raw), "bytes": len(raw)}, chunks=chunks))
    def test_whole_document_must_match_declared_identity(self):
        raw = b"full review packet\n"
        self.assertTrue(
            verify_whole_delivery(
                declared_sha256=sha256_bytes(raw),
                declared_bytes=len(raw),
                delivered=raw,
            )
        )
        self.assertFalse(
            verify_whole_delivery(
                declared_sha256=sha256_bytes(raw),
                declared_bytes=len(raw),
                delivered=b"summary only",
            )
        )

    def test_all_chunks_required_and_reconstruct_whole(self):
        whole = b"abcdefghij"
        chunks = [
            {"index": 0, "count": 2, "bytes": b"abcde", "sha256": sha256_bytes(b"abcde")},
            {"index": 1, "count": 2, "bytes": b"fghij", "sha256": sha256_bytes(b"fghij")},
        ]
        self.assertTrue(
            verify_chunked_delivery(
                declared_sha256=sha256_bytes(whole),
                declared_bytes=len(whole),
                chunks=chunks,
            )
        )
        self.assertFalse(
            verify_chunked_delivery(
                declared_sha256=sha256_bytes(whole),
                declared_bytes=len(whole),
                chunks=chunks[:1],
            )
        )

    def test_chunk_digest_tampering_fails(self):
        whole = b"abcdef"
        chunks = [
            {"index": 0, "count": 2, "bytes": b"abc", "sha256": sha256_bytes(b"abc")},
            {"index": 1, "count": 2, "bytes": b"def", "sha256": "0" * 64},
        ]
        self.assertFalse(
            verify_chunked_delivery(
                declared_sha256=sha256_bytes(whole),
                declared_bytes=len(whole),
                chunks=chunks,
            )
        )

    def test_reviewer_defect_requires_solution_and_regression(self):
        finding = {
            "finding_id": "F-01",
            "severity": "HIGH",
            "location": "parser",
            "failure_path": "hidden declaration bypass",
            "evidence": "exact adversarial case",
            "impact": "false-clean review",
            "proposed_remediation": "replace literal patch with structural grammar",
            "regression_tests": ["reject the defect family", "preserve valid prose"],
            "candidate_invalidated": True,
            "blocking": True,
        }
        self.assertTrue(validate_finding_solution_contract(finding))
        bad = dict(finding)
        bad["proposed_remediation"] = ""
        self.assertFalse(validate_finding_solution_contract(bad))

    def test_reviewer_solution_is_advisory_and_requires_adjudication(self):
        self.assertTrue(
            validate_solution_adjudication(
                {
                    "finding_id": "F-01",
                    "state": "ACCEPTED_NARROWED",
                    "reason": "same defect reproduced but safer repair preserves valid behavior",
                }
            )
        )
        self.assertFalse(
            validate_solution_adjudication(
                {
                    "finding_id": "F-01",
                    "state": "AUTO_IMPLEMENT_REVIEWER_SOLUTION",
                    "reason": "not a governed adjudication state",
                }
            )
        )


if __name__ == "__main__":
    unittest.main()
