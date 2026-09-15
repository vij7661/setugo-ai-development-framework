from __future__ import annotations

import json
from pathlib import Path
import shutil
import tempfile
import unittest

import review_safe_evidence_v16_manifest_validation as mv


ROOT = Path(__file__).resolve().parent


class Slice2IAR5Tests(unittest.TestCase):
    def test_current_iar1_manifest_is_exact_test_source_bound(self) -> None:
        manifest = mv.load_strict_json(ROOT / "review-safe-evidence-v16-slice2-test-manifest-iar1-v2.json")
        self.assertEqual(mv.CURRENT_IAR1_ID, manifest["manifest_id"])
        self.assertEqual(mv.IAR1_TEST_BLOB, manifest["test_source_git_blob_sha"])
        self.assertEqual(
            mv.IAR1_TEST_BLOB,
            mv.git_blob_sha_path(ROOT / "test_review_safe_evidence_v16_independence_v2.py"),
        )

    def test_current_iar2_manifest_is_exact_test_source_bound(self) -> None:
        manifest = mv.load_strict_json(ROOT / "review-safe-evidence-v16-slice2-test-manifest-iar2-v2.json")
        self.assertEqual(mv.CURRENT_IAR2_ID, manifest["manifest_id"])
        self.assertEqual(mv.IAR2_TEST_BLOB, manifest["test_source_git_blob_sha"])
        self.assertEqual(
            mv.IAR2_TEST_BLOB,
            mv.git_blob_sha_path(ROOT / "test_review_safe_evidence_v16_independence_iar2.py"),
        )

    def test_exact_historical_iar1_predecessor_content_passes(self) -> None:
        current = mv.load_strict_json(ROOT / "review-safe-evidence-v16-slice2-test-manifest-iar1-v2.json")
        index = mv.load_strict_json(ROOT / "review-safe-evidence-v16-slice2-current-manifests.json")
        historical = (ROOT / "review-safe-evidence-v16-slice2-test-manifest-iar1.json").read_bytes()
        self.assertEqual(
            [],
            mv.validate_historical_manifest_binding(
                current,
                index,
                historical,
                historical_schema_name="historical_iar1",
                historical_id=mv.HISTORICAL_IAR1_ID,
                historical_blob=mv.HISTORICAL_IAR1_BLOB,
                code_prefix="IAR1",
            ),
        )

    def test_same_historical_iar1_id_with_changed_content_is_rejected(self) -> None:
        current = mv.load_strict_json(ROOT / "review-safe-evidence-v16-slice2-test-manifest-iar1-v2.json")
        index = mv.load_strict_json(ROOT / "review-safe-evidence-v16-slice2-current-manifests.json")
        obj = json.loads((ROOT / "review-safe-evidence-v16-slice2-test-manifest-iar1.json").read_text(encoding="utf-8"))
        obj["predecessor_slice2_candidate"] = "substituted-candidate"
        changed = (json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
        problems = mv.validate_historical_manifest_binding(
            current,
            index,
            changed,
            historical_schema_name="historical_iar1",
            historical_id=mv.HISTORICAL_IAR1_ID,
            historical_blob=mv.HISTORICAL_IAR1_BLOB,
            code_prefix="IAR1",
        )
        self.assertIn("IAR1_HISTORICAL_BLOB_MISMATCH", problems)

    def test_exact_historical_iar2_predecessor_content_passes(self) -> None:
        current = mv.load_strict_json(ROOT / "review-safe-evidence-v16-slice2-test-manifest-iar2-v2.json")
        index = mv.load_strict_json(ROOT / "review-safe-evidence-v16-slice2-current-manifests.json")
        historical = (ROOT / "review-safe-evidence-v16-slice2-test-manifest-iar2.json").read_bytes()
        self.assertEqual(
            [],
            mv.validate_historical_manifest_binding(
                current,
                index,
                historical,
                historical_schema_name="historical_iar2",
                historical_id=mv.HISTORICAL_IAR2_ID,
                historical_blob=mv.HISTORICAL_IAR2_BLOB,
                code_prefix="IAR2",
            ),
        )

    def test_same_historical_iar2_id_with_changed_content_is_rejected(self) -> None:
        current = mv.load_strict_json(ROOT / "review-safe-evidence-v16-slice2-test-manifest-iar2-v2.json")
        index = mv.load_strict_json(ROOT / "review-safe-evidence-v16-slice2-current-manifests.json")
        obj = json.loads((ROOT / "review-safe-evidence-v16-slice2-test-manifest-iar2.json").read_text(encoding="utf-8"))
        obj["predecessor_slice2_candidate"] = "substituted-candidate"
        changed = (json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
        problems = mv.validate_historical_manifest_binding(
            current,
            index,
            changed,
            historical_schema_name="historical_iar2",
            historical_id=mv.HISTORICAL_IAR2_ID,
            historical_blob=mv.HISTORICAL_IAR2_BLOB,
            code_prefix="IAR2",
        )
        self.assertIn("IAR2_HISTORICAL_BLOB_MISMATCH", problems)

    def test_current_index_separates_and_exactly_binds_historical_iar_manifests(self) -> None:
        index = mv.load_strict_json(ROOT / "review-safe-evidence-v16-slice2-current-manifests.json")
        self.assertEqual(list(mv.CURRENT_IDS), index["current_manifest_ids"])
        self.assertEqual(list(mv.HISTORICAL_IDS), index["historical_manifest_ids"])
        self.assertEqual(dict(mv.HISTORICAL_BLOBS), index["historical_manifest_git_blobs"])
        self.assertNotIn(mv.HISTORICAL_IAR1_ID, index["current_manifest_ids"])
        self.assertNotIn(mv.HISTORICAL_IAR2_ID, index["current_manifest_ids"])

    def test_current_iar1_or_iar2_test_source_drift_fails_strict_set_validation(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            copy_root = Path(td) / "governance-runtime"
            shutil.copytree(ROOT, copy_root)
            iar1_source = copy_root / "test_review_safe_evidence_v16_independence_v2.py"
            iar1_source.write_text(iar1_source.read_text(encoding="utf-8") + "\n# drift\n", encoding="utf-8")
            first = mv.validate_current_manifest_set(copy_root)
            self.assertFalse(first["valid"])
            self.assertIn("IAR1_TEST_SOURCE_BLOB_MISMATCH", first["problems"])

        with tempfile.TemporaryDirectory() as td:
            copy_root = Path(td) / "governance-runtime"
            shutil.copytree(ROOT, copy_root)
            iar2_source = copy_root / "test_review_safe_evidence_v16_independence_iar2.py"
            iar2_source.write_text(iar2_source.read_text(encoding="utf-8") + "\n# drift\n", encoding="utf-8")
            second = mv.validate_current_manifest_set(copy_root)
            self.assertFalse(second["valid"])
            self.assertIn("IAR2_TEST_SOURCE_BLOB_MISMATCH", second["problems"])


if __name__ == "__main__":
    unittest.main()
