from __future__ import annotations
import hashlib, json, unittest, shutil
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from r8_evidence_bundle_integrity import canonical_entries, verify_bundle


class EvidenceIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.root = Path("stage2-sg1-evidence") / "_bundle-test"
        self.root.mkdir(parents=True, exist_ok=True)
    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)
    def make_bundle(self, root):
        (root / "result.json").write_text('{"ok":true}\n', encoding="utf-8")
        entries = canonical_entries(root, ["result.json"])
        return {"schema": "evidence/v1", "run_id": "run-1", "job_id": "job-1", "workflow": "wf.yml",
                "head_sha": "a" * 40, "input_blobs": {"input": "b" * 40}, "files": entries,
                "archive": {"format": "directory", "sha256": "c" * 64}, "authority_effect": "NONE",
                "activation_verification": {"performed": False, "run_id": "run-1", "job_id": "job-1", "conclusion": "not-run"}}

    @unittest.skipUnless(hasattr(__import__('os'), 'O_NOFOLLOW') and hasattr(__import__('os'), 'O_DIRECTORY'), 'descriptor-safe read unsupported')
    def test_valid_lineage_and_per_file_hash(self):
        root = self.root; bundle = self.make_bundle(root)
        self.assertEqual(verify_bundle(bundle, root=root, expected_authority="NONE", expected_run_id="run-1", expected_job_id="job-1", expected_workflow="wf.yml", expected_head="a" * 40, expected_inputs={"input": "b" * 40}, expected_archive_sha256="c" * 64, expected_activation_verification=bundle["activation_verification"])["status"], "PASS")

    @unittest.skipUnless(hasattr(__import__('os'), 'O_NOFOLLOW') and hasattr(__import__('os'), 'O_DIRECTORY'), 'descriptor-safe read unsupported')
    def test_changed_file_rejected(self):
        root = self.root; bundle = self.make_bundle(root)
        (root / "result.json").write_text("changed\n", encoding="utf-8")
        with self.assertRaises(ValueError): verify_bundle(bundle, root=root, expected_authority="NONE")

    @unittest.skipUnless(hasattr(__import__('os'), 'O_NOFOLLOW') and hasattr(__import__('os'), 'O_DIRECTORY'), 'descriptor-safe read unsupported')
    def test_stale_head_rejected(self):
        root = self.root; bundle = self.make_bundle(root)
        with self.assertRaises(ValueError): verify_bundle(bundle, root=root, expected_authority="NONE", expected_head="d" * 40)

    @unittest.skipUnless(hasattr(__import__('os'), 'O_NOFOLLOW') and hasattr(__import__('os'), 'O_DIRECTORY'), 'descriptor-safe read unsupported')
    def test_authority_cannot_be_promoted(self):
        root = self.root; bundle = self.make_bundle(root); bundle["authority_effect"] = "RUNTIME_QUALIFIED"
        with self.assertRaises(ValueError): verify_bundle(bundle, root=root, expected_authority="NONE")

    @unittest.skipUnless(hasattr(__import__('os'), 'O_NOFOLLOW') and hasattr(__import__('os'), 'O_DIRECTORY'), 'descriptor-safe read unsupported')
    def test_traversal_and_empty_path_rejected(self):
        root = self.root; bundle = self.make_bundle(root)
        bundle["files"] = [{"path": "../escape", "sha256": "0" * 64}]
        with self.assertRaises(ValueError): verify_bundle(bundle, root=root, expected_authority="NONE")

    @unittest.skipUnless(hasattr(__import__('os'), 'O_NOFOLLOW') and hasattr(__import__('os'), 'O_DIRECTORY'), 'descriptor-safe read unsupported')
    def test_activation_evidence_shape_required(self):
        root = self.root; bundle = self.make_bundle(root)
        bundle["activation_verification"] = {"performed": False}
        with self.assertRaises(ValueError): verify_bundle(bundle, root=root, expected_authority="NONE")

    def test_path_aliases_and_absolute_paths_rejected_before_read(self):
        with self.assertRaises(ValueError): canonical_entries(self.root, ["./result.json"])
        with self.assertRaises(ValueError): canonical_entries(self.root, ["nested/../result.json"])
        with self.assertRaises(ValueError): canonical_entries(self.root, ["C:/escape"])
        with self.assertRaises(ValueError): canonical_entries(self.root, ["result.json", "result.json"])

    @unittest.skipUnless(hasattr(__import__('os'), 'O_NOFOLLOW') and hasattr(__import__('os'), 'O_DIRECTORY'), 'descriptor-safe read unsupported')
    def test_exact_lineage_fields_reject_valid_looking_substitutions(self):
        root = self.root; bundle = self.make_bundle(root)
        with self.assertRaises(ValueError): verify_bundle(bundle, root=root, expected_authority="NONE", expected_run_id="other")
        with self.assertRaises(ValueError): verify_bundle(bundle, root=root, expected_authority="NONE", expected_job_id="other")
        with self.assertRaises(ValueError): verify_bundle(bundle, root=root, expected_authority="NONE", expected_workflow="other.yml")
        with self.assertRaises(ValueError): verify_bundle(bundle, root=root, expected_authority="NONE", expected_activation_verification={"performed": True, "run_id": "run-1", "job_id": "job-1", "conclusion": "success"})

    @unittest.skipUnless(hasattr(__import__('os'), 'O_NOFOLLOW') and hasattr(__import__('os'), 'O_DIRECTORY'), 'descriptor-safe read unsupported')
    def test_malformed_and_substituted_identity_values_rejected(self):
        root = self.root; bundle = self.make_bundle(root)
        bundle["head_sha"] = "not-a-sha"
        with self.assertRaises(ValueError): verify_bundle(bundle, root=root, expected_authority="NONE")
        bundle = self.make_bundle(root); bundle["input_blobs"]["input"] = "g" * 40
        with self.assertRaises(ValueError): verify_bundle(bundle, root=root, expected_authority="NONE")
        bundle = self.make_bundle(root); bundle["archive"]["sha256"] = "bad"
        with self.assertRaises(ValueError): verify_bundle(bundle, root=root, expected_authority="NONE")


if __name__ == "__main__": unittest.main()
