import hashlib
import json
import unittest

from review_packet_preflight import validate_packet, git_blob_sha1

class ReviewPacketPreflightTests(unittest.TestCase):
    def artifact(self, path, content):
        return {
            "path": path,
            "git_blob_sha": git_blob_sha1(content.encode("utf-8")),
            "review_surface": "FULL_TEXT",
        }

    def manifest(self, content="## P24-01 — x\n\n## WDPC-431 — y"):
        a = self.artifact("standards/a.md", content)
        return {
            "schema_version": 1,
            "packet_class": "CLEAN_INDEPENDENT_REVIEW",
            "candidate_commit": "a"*40,
            "required_artifacts": [a],
            "required_clause_ids": ["P24-01"],
            "required_case_ids": ["WDPC-431"],
            "forbidden_strings": ["Overall disposition: CHANGES_REQUIRED"],
            "reject_unlisted_artifacts": True,
        }, a, content

    def packet(self, a, content):
        return (
            "# packet\n\ncandidate " + "a"*40 + "\n"
            f"<!-- BEGIN EXACT ARTIFACT path={a['path']} blob={a['git_blob_sha']} -->\n"
            + content
            + f"<!-- END EXACT ARTIFACT path={a['path']} -->\n"
        )

    def test_valid_packet_ready(self):
        manifest, a, content = self.manifest()
        result = validate_packet(self.packet(a, content), manifest)
        self.assertEqual("PACKET_READY", result["result"])

    def test_trailing_newline_is_preserved_in_hash(self):
        content = "## P24-01 — x\n\n## WDPC-431 — y\n"
        manifest, a, _ = self.manifest(content)
        result = validate_packet(self.packet(a, content), manifest)
        self.assertEqual("PACKET_READY", result["result"])

    def test_missing_clause_definition_fails(self):
        content = "## WDPC-431 — y"
        manifest, a, _ = self.manifest(content)
        result = validate_packet(self.packet(a, content), manifest)
        self.assertEqual("PACKET_INVALID", result["result"])
        self.assertTrue(any("P24-01" in c["detail"] for c in result["checks"]))

    def test_hash_mismatch_fails(self):
        manifest, a, content = self.manifest()
        packet = self.packet(a, content.replace("x", "changed"))
        result = validate_packet(packet, manifest)
        self.assertEqual("PACKET_INVALID", result["result"])
        self.assertTrue(any(c["check_id"] == "ARTIFACT_HASH" and c["status"] == "FAIL" for c in result["checks"]))

    def test_prior_review_contamination_fails(self):
        manifest, a, content = self.manifest()
        packet = self.packet(a, content) + "\nOverall disposition: CHANGES_REQUIRED\n"
        result = validate_packet(packet, manifest)
        self.assertEqual("PACKET_INVALID", result["result"])
        self.assertTrue(any(c["check_id"] == "CLEAN_ROOM" and c["status"] == "FAIL" for c in result["checks"]))

    def test_mention_is_not_definition(self):
        content = "This summary mentions P24-01.\n\n## WDPC-431 — y"
        manifest, a, _ = self.manifest(content)
        result = validate_packet(self.packet(a, content), manifest)
        self.assertEqual("PACKET_INVALID", result["result"])

if __name__ == "__main__":
    unittest.main()
