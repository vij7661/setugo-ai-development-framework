from __future__ import annotations

import json
import unittest

from review_engine.single_file_review_container import (
    build_single_file_review_container,
    verify_single_file_review_container,
)


class SingleFileReviewContainerTests(unittest.TestCase):
    def _container(self) -> str:
        return build_single_file_review_container(
            review_id="REV-ONE-001",
            candidate_sha="a" * 40,
            intended_reviewer="deepseek",
            prompt="Review adversarially.",
            artifacts=(
                {"path": "review_engine/a.py", "content": "print('a')\n"},
                {"path": "review_engine/b.md", "content": "# B\n"},
            ),
        )

    def test_all_embedded_artifacts_reconstruct_exact_utf8_bytes(self):
        payload = verify_single_file_review_container(self._container())
        self.assertEqual([item["path"] for item in payload["artifacts"]], [
            "review_engine/a.py",
            "review_engine/b.md",
        ])
        self.assertFalse(payload["provider_api_authenticated"])
        self.assertFalse(payload["can_satisfy_platform_review"])

    def test_modified_embedded_content_fails_even_if_recorded_hash_is_old(self):
        container = json.loads(self._container())
        container["payload"]["artifacts"][0]["content"] = "tampered\n"
        # Rehash outer payload so the per-artifact check, not only the outer hash,
        # must reject the modification.
        import hashlib
        canonical = json.dumps(
            container["payload"],
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
        container["payload_sha256"] = hashlib.sha256(canonical).hexdigest()
        with self.assertRaisesRegex(ValueError, "byte length|content hash"):
            verify_single_file_review_container(json.dumps(container))

    def test_modified_payload_hash_fails(self):
        container = json.loads(self._container())
        container["payload_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "payload hash"):
            verify_single_file_review_container(json.dumps(container))

    def test_duplicate_artifact_path_is_rejected_at_build(self):
        with self.assertRaisesRegex(ValueError, "unique"):
            build_single_file_review_container(
                review_id="REV-ONE-002",
                candidate_sha="b" * 40,
                intended_reviewer="kimi",
                prompt="review",
                artifacts=(
                    {"path": "same.py", "content": "a"},
                    {"path": "same.py", "content": "b"},
                ),
            )

    def test_external_container_cannot_be_relabelled_as_platform_review(self):
        container = json.loads(self._container())
        container["payload"]["provider_api_authenticated"] = True
        import hashlib
        canonical = json.dumps(
            container["payload"],
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
        container["payload_sha256"] = hashlib.sha256(canonical).hexdigest()
        with self.assertRaisesRegex(ValueError, "platform API-review authority"):
            verify_single_file_review_container(json.dumps(container))


if __name__ == "__main__":
    unittest.main()
