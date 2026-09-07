from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from review_engine.review_export import (
    MANUAL_RELAY_IDENTITY_ASSURANCE,
    ReviewExportSpec,
    build_review_export,
)


class ReviewExportTests(unittest.TestCase):
    CANDIDATE = "a" * 40

    def _repo(self, td: str) -> Path:
        root = Path(td) / "repo"
        (root / "review_engine").mkdir(parents=True)
        (root / "review_engine" / "a.py").write_text("print('a')\n", encoding="utf-8")
        (root / "review_engine" / "b.md").write_text("# B\n\ncontent\n", encoding="utf-8")
        return root

    def _spec(self, target: str = "provider-neutral") -> ReviewExportSpec:
        return ReviewExportSpec(
            review_id="REV-TEST-001",
            candidate_sha=self.CANDIDATE,
            intended_reviewer=target,
            prompt="Review adversarially. Return only the requested result.",
            source_paths=("review_engine/b.md", "review_engine/a.py"),
        )

    def test_export_retains_exact_raw_bytes_and_hashes(self):
        with tempfile.TemporaryDirectory() as td:
            root = self._repo(td)
            out = Path(td) / "out"
            result = build_review_export(root, out, self._spec())
            self.assertEqual(result["raw_artifact_count"], 2)
            self.assertEqual(
                (out / "raw-artifacts/review_engine/a.py").read_bytes(),
                (root / "review_engine/a.py").read_bytes(),
            )
            request = json.loads((out / "REVIEW_REQUEST.json").read_text(encoding="utf-8"))
            self.assertEqual(request["candidate_sha"], self.CANDIDATE)
            self.assertEqual(request["reviewer_identity_assurance"], MANUAL_RELAY_IDENTITY_ASSURANCE)
            self.assertEqual([entry["path"] for entry in request["raw_artifacts"]], [
                "review_engine/a.py",
                "review_engine/b.md",
            ])
            sums = (out / "SHA256SUMS.txt").read_text(encoding="utf-8")
            self.assertIn("raw-artifacts/review_engine/a.py", sums)
            self.assertIn("REVIEW_PACKET.md", sums)
            self.assertIn("TARGET_TRANSPORT.json", sums)

    def test_target_changes_only_convenience_metadata_not_raw_artifact_hashes(self):
        with tempfile.TemporaryDirectory() as td:
            root = self._repo(td)
            raw_hash_sets = []
            expected_api_families = {
                "claude": "ANTHROPIC_MESSAGES",
                "deepseek": "OPENAI_CHAT_COMPLETIONS_OR_RESPONSES",
                "kimi": "MESSAGES_STYLE_CHAT",
            }
            for target in ("claude", "deepseek", "kimi"):
                out = Path(td) / target
                result = build_review_export(root, out, self._spec(target))
                raw_hash_sets.append(tuple((entry["path"], entry["sha256"]) for entry in result["raw_artifacts"]))
                request = json.loads((out / "REVIEW_REQUEST.json").read_text(encoding="utf-8"))
                self.assertEqual(request["intended_reviewer"], target)
                self.assertEqual(request["transport"], "MANUAL_RELAY")
                transport = json.loads((out / "TARGET_TRANSPORT.json").read_text(encoding="utf-8"))
                self.assertEqual(transport["intended_reviewer"], target)
                self.assertEqual(transport["authority"], "CONVENIENCE_ONLY_NOT_REVIEW_EVIDENCE")
                self.assertEqual(transport["api_family"], expected_api_families[target])
                self.assertTrue(transport["documentation_basis"])
                self.assertEqual(len(result["transport_profile_sha256"]), 64)
            self.assertEqual(raw_hash_sets[0], raw_hash_sets[1])
            self.assertEqual(raw_hash_sets[1], raw_hash_sets[2])

    def test_packet_explicitly_rejects_self_attested_identity(self):
        with tempfile.TemporaryDirectory() as td:
            root = self._repo(td)
            out = Path(td) / "out"
            build_review_export(root, out, self._spec("deepseek"))
            packet = (out / "REVIEW_PACKET.md").read_text(encoding="utf-8")
            self.assertIn("Do not infer reviewer/provider/model identity from self-declared output metadata", packet)
            self.assertIn(MANUAL_RELAY_IDENTITY_ASSURANCE, packet)
            self.assertIn("TARGET_TRANSPORT.json", packet)

    def test_path_traversal_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = self._repo(td)
            outside = Path(td) / "secret.txt"
            outside.write_text("secret\n", encoding="utf-8")
            spec = ReviewExportSpec(
                review_id="REV-TEST-002",
                candidate_sha=self.CANDIDATE,
                intended_reviewer="claude",
                prompt="review",
                source_paths=("../secret.txt",),
            )
            with self.assertRaisesRegex(ValueError, "unsafe review source path"):
                build_review_export(root, Path(td) / "out", spec)

    def test_symlink_escape_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = self._repo(td)
            outside = Path(td) / "outside.txt"
            outside.write_text("outside\n", encoding="utf-8")
            link = root / "review_engine" / "link.txt"
            try:
                link.symlink_to(outside)
            except (OSError, NotImplementedError):
                self.skipTest("symlink unavailable")
            spec = ReviewExportSpec(
                review_id="REV-TEST-003",
                candidate_sha=self.CANDIDATE,
                intended_reviewer="kimi",
                prompt="review",
                source_paths=("review_engine/link.txt",),
            )
            with self.assertRaisesRegex(ValueError, "escapes repository root"):
                build_review_export(root, Path(td) / "out", spec)

    def test_invalid_candidate_or_duplicate_source_manifest_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = self._repo(td)
            with self.assertRaisesRegex(ValueError, "candidate_sha"):
                build_review_export(
                    root,
                    Path(td) / "bad-sha",
                    ReviewExportSpec(
                        review_id="REV-TEST-004",
                        candidate_sha="not-a-sha",
                        intended_reviewer="deepseek",
                        prompt="review",
                        source_paths=("review_engine/a.py",),
                    ),
                )
            with self.assertRaisesRegex(ValueError, "duplicates"):
                build_review_export(
                    root,
                    Path(td) / "duplicate",
                    ReviewExportSpec(
                        review_id="REV-TEST-005",
                        candidate_sha=self.CANDIDATE,
                        intended_reviewer="deepseek",
                        prompt="review",
                        source_paths=("review_engine/a.py", "review_engine/a.py"),
                    ),
                )


if __name__ == "__main__":
    unittest.main()
