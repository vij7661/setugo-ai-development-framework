import json
from pathlib import Path
import tempfile
import unittest

from freeze_truth import build_manifest


class FreezeTruthTests(unittest.TestCase):
    def write_truth(self, root: Path, case_id: str) -> None:
        payload = {
            "case_id": case_id,
            "case_version": "1.0",
            "truth_version": "1.0",
            "defects": [],
            "clean_control": True,
        }
        (root / f"{case_id}.json").write_text(
            json.dumps(payload), encoding="utf-8"
        )

    def test_build_manifest_hashes_external_truth(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_truth(root, "CASE-1")
            manifest = build_manifest(root, {"CASE-1"})
            record = manifest["records"]["CASE-1"]
            self.assertEqual(manifest["status"], "FROZEN")
            self.assertEqual(len(record["sha256"]), 64)

    def test_missing_truth_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                build_manifest(Path(tmp), {"CASE-1"})

    def test_unexpected_truth_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_truth(root, "CASE-1")
            self.write_truth(root, "CASE-2")
            with self.assertRaises(ValueError):
                build_manifest(root, {"CASE-1"})

    def test_invalid_record_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "CASE-1.json").write_text(
                json.dumps({"case_id": "CASE-1"}), encoding="utf-8"
            )
            with self.assertRaises(ValueError):
                build_manifest(root, {"CASE-1"})


if __name__ == "__main__":
    unittest.main()
