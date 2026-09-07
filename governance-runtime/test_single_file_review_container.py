from __future__ import annotations

from copy import deepcopy
import unittest

from build_portable_review_packet import (
    build_single_file_container,
    verify_single_file_container,
)
from review_protocol import build_review_request


class SingleFileReviewContainerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.request = build_review_request(
            review_request_id="REV-PORTABLE-TEST-001",
            trigger="MATERIAL_GOVERNANCE_CHANGE",
            artifact_type="live_conversation_governance_runtime_candidate",
            artifact_ref="PR-5",
            artifact_commit="a" * 40,
            proposer={"provider": "openai", "model": "gpt-5.6-sol"},
            required_reviewer={"provider": "deepseek", "model_class": "deepseek"},
            blind_review_required=True,
            review_questions=["Review independently."],
            evidence_refs=[
                {"type": "file", "ref": "a.txt"},
                {"type": "file", "ref": "b.py"},
            ],
            material_authority_transition=True,
            required_review_dimensions=[
                {
                    "id": "raw_byte_integrity",
                    "mandatory": True,
                    "description": "Inspect embedded byte-authoritative artifacts.",
                }
            ],
        )
        self.artifacts = [
            {"path": "a.txt", "content": "alpha\n"},
            {"path": "b.py", "content": "print('beta')\n"},
        ]
        self.container = build_single_file_container(
            request=self.request,
            embedded_artifacts=self.artifacts,
            evidence_summary={"repository_access_required": False},
            output_contract={"disposition": "PASS | INSUFFICIENT_EVIDENCE"},
        )

    def test_p2_01_all_embedded_artifacts_reconstruct_exact_bytes(self) -> None:
        ok, reason = verify_single_file_container(
            request=self.request,
            container=self.container,
            expected_paths=["a.txt", "b.py"],
        )
        self.assertTrue(ok, reason)
        self.assertEqual(self.container["manual_relay_upload_files_required"], 1)
        self.assertTrue(self.container["all_required_artifacts_embedded"])

    def test_p2_02_modified_embedded_content_fails(self) -> None:
        container = deepcopy(self.container)
        container["artifacts"][0]["content"] = "tampered\n"
        ok, reason = verify_single_file_container(
            request=self.request,
            container=container,
            expected_paths=["a.txt", "b.py"],
        )
        self.assertFalse(ok)
        self.assertIn("payload hash", reason)

    def test_p2_03_modified_byte_length_fails_even_if_payload_rehashed(self) -> None:
        container = deepcopy(self.container)
        container["artifacts"][0]["bytes_utf8"] += 1
        from build_portable_review_packet import canonical_json_bytes, sha256_bytes
        material = deepcopy(container)
        material.pop("container_payload_sha256")
        container["container_payload_sha256"] = sha256_bytes(canonical_json_bytes(material))
        ok, reason = verify_single_file_container(
            request=self.request,
            container=container,
            expected_paths=["a.txt", "b.py"],
        )
        self.assertFalse(ok)
        self.assertIn("byte length", reason)

    def test_p2_04_omitted_required_artifact_fails_coverage(self) -> None:
        container = build_single_file_container(
            request=self.request,
            embedded_artifacts=[self.artifacts[0]],
            evidence_summary={"repository_access_required": False},
            output_contract={"disposition": "PASS | INSUFFICIENT_EVIDENCE"},
        )
        ok, reason = verify_single_file_container(
            request=self.request,
            container=container,
            expected_paths=["a.txt", "b.py"],
        )
        self.assertFalse(ok)
        self.assertIn("coverage", reason)

    def test_p2_05_container_payload_tamper_fails(self) -> None:
        container = deepcopy(self.container)
        container["evidence_summary"]["injected"] = True
        ok, reason = verify_single_file_container(
            request=self.request,
            container=container,
            expected_paths=["a.txt", "b.py"],
        )
        self.assertFalse(ok)
        self.assertIn("payload hash", reason)

    def test_p2_06_review_request_semantics_cannot_be_rebound(self) -> None:
        container = deepcopy(self.container)
        container["review_request"]["required_reviewer"]["provider"] = "anthropic"
        from build_portable_review_packet import canonical_json_bytes, sha256_bytes
        material = deepcopy(container)
        material.pop("container_payload_sha256")
        container["container_payload_sha256"] = sha256_bytes(canonical_json_bytes(material))
        ok, reason = verify_single_file_container(
            request=self.request,
            container=container,
            expected_paths=["a.txt", "b.py"],
        )
        self.assertFalse(ok)
        self.assertIn("ReviewRequest semantics", reason)

    def test_p2_07_one_file_handoff_is_explicit_and_raw_reconstructable(self) -> None:
        self.assertEqual(self.container["container_type"], "SINGLE_FILE_MANUAL_REVIEW_EXPORT")
        self.assertEqual(self.container["manual_relay_upload_files_required"], 1)
        self.assertEqual(
            self.container["byte_reconstruction_rule"],
            "UTF8_ENCODE_EACH_ARTIFACT_CONTENT_EXACTLY",
        )
        for item in self.container["artifacts"]:
            self.assertEqual(item["encoding"], "utf-8")
            self.assertIn("RAW_GIT_BLOB_UTF8_BYTES", item["hash_basis"])
            self.assertGreater(item["bytes_utf8"], 0)
            self.assertEqual(len(item["content_sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
