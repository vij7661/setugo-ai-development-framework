import copy
import importlib
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
SCHEMA_DIR = REPO_ROOT / "schemas" / "governance-r8" / "v15-r1"
FROZEN_SCHEMA_CANDIDATE = "f93ca26975ecb64f0da13779889c75b36140cdfc"
SUCCESSOR2_BRANCH = "implementation/r8-v15-r1-slice1-successor-2-2026-09-25"

sys.path.insert(0, str(HERE))
runtime = importlib.import_module("r8_v15_r1_frozen_schema_runtime")


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class Slice1Successor2RepairAcceptance(unittest.TestCase):
    maxDiff = None

    def make_schema_fixture(self):
        td = tempfile.TemporaryDirectory()
        root = Path(td.name)
        dest = root / "schemas" / "governance-r8" / "v15-r1"
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(SCHEMA_DIR, dest)
        return td, root, dest

    def test_s1r2_01_nested_object_negative_zero_rejects(self):
        with self.assertRaises(runtime.GCPError) as cm:
            runtime.canonicalize_json_text('{"n":-0}', schema_context="object")
        self.assertEqual(cm.exception.code, "GCP_REJECT_NEGATIVE_ZERO")

    def test_s1r2_02_nested_array_negative_zero_rejects_and_bounds_preserve(self):
        with self.assertRaises(runtime.GCPError) as cm:
            runtime.canonicalize_json_text('[-0]', schema_context="array")
        self.assertEqual(cm.exception.code, "GCP_REJECT_NEGATIVE_ZERO")

        got = runtime.canonicalize_json_text(
            '[-9223372036854775808,9223372036854775807]',
            schema_context="array",
        )
        self.assertEqual(
            got,
            b'[-9223372036854775808,9223372036854775807]',
        )
        for text in (
            '[-9223372036854775809]',
            '[9223372036854775808]',
        ):
            with self.subTest(text=text):
                with self.assertRaises(runtime.GCPError) as bounds:
                    runtime.canonicalize_json_text(text, schema_context="array")
                self.assertEqual(bounds.exception.code, "GCP_REJECT_OUT_OF_INT64")

    def test_s1r2_03_external_same_byte_symlink_rejects(self):
        if not hasattr(os, "symlink"):
            self.skipTest("symlink unsupported")

        td, root, schema = self.make_schema_fixture()
        self.addCleanup(td.cleanup)

        target = schema / "runtime-contracts.schema.json"
        outside = root / "outside-runtime-contracts.schema.json"
        outside.write_bytes(target.read_bytes())
        target.unlink()
        target.symlink_to(outside)

        with self.assertRaises(runtime.FrozenSchemaError) as cm:
            runtime.FrozenSchemaRuntime(
                root,
                candidate_sha=FROZEN_SCHEMA_CANDIDATE,
            ).load()
        self.assertEqual(cm.exception.code, "ARTIFACT_PATH_SYMLINK")

    def test_s1r2_04_source_map_requires_exact_full_artifact_paths(self):
        self.assertTrue(
            hasattr(runtime, "validate_source_map_artifact_paths"),
            "successor 2 must expose exact full-path source-map/SPM validation",
        )
        spm = load_json(SCHEMA_DIR / "schema-provenance-manifest-candidate.json")
        source_map = load_json(SCHEMA_DIR / "schema-provenance-source-map.json")
        mutated = copy.deepcopy(source_map)
        key = next(iter(mutated["artifact_sources"]))
        value = mutated["artifact_sources"].pop(key)
        mutated["artifact_sources"]["../" + key] = value

        with self.assertRaises(runtime.FrozenSchemaError) as cm:
            runtime.validate_source_map_artifact_paths(spm, mutated)
        self.assertEqual(cm.exception.code, "SOURCE_MAP_ARTIFACT_SET_MISMATCH")

    def test_s1r2_05_artifact_id_and_sha256_shapes_are_enforced(self):
        spm = load_json(SCHEMA_DIR / "schema-provenance-manifest-candidate.json")

        empty_id = copy.deepcopy(spm)
        empty_id["artifacts"][0]["artifact_id"] = ""
        with self.assertRaises(runtime.FrozenSchemaError) as cm1:
            runtime.validate_spm_document(empty_id)
        self.assertEqual(cm1.exception.code, "SPM_ARTIFACT_ID_INVALID")

        bad_sha = copy.deepcopy(spm)
        bad_sha["artifacts"][0]["sha256"] = "ABC"
        with self.assertRaises(runtime.FrozenSchemaError) as cm2:
            runtime.validate_spm_document(bad_sha)
        self.assertEqual(cm2.exception.code, "SPM_ARTIFACT_SHA256_INVALID")

    def test_s1r2_06_workflow_trigger_covers_original_and_successor_paths(self):
        workflow = (
            REPO_ROOT / ".github" / "workflows" / "r8-v15-r1-implementation-slice1.yml"
        ).read_text(encoding="utf-8")
        required = [
            SUCCESSOR2_BRANCH,
            "governance-runtime/r8_v15_r1_frozen_schema_runtime.py",
            "governance-runtime/test_r8_v15_r1_implementation_slice1.py",
            "governance-runtime/test_r8_v15_r1_implementation_slice1_successor1.py",
            "governance-runtime/test_r8_v15_r1_implementation_slice1_successor2.py",
            "governance-runtime/test_r8_v15_r1_post_freeze_regression.py",
            "governance-runtime/test_r8_v15_r1_sfv45_r2_repair.py",
            "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE1-PREREGISTRATION.md",
            "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE1-SUCCESSOR1-PREREGISTRATION.md",
            "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE1-SUCCESSOR2-PREREGISTRATION.md",
            "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE1-MARKER.json",
            ".github/workflows/r8-v15-r1-implementation-slice1.yml",
        ]
        for item in required:
            with self.subTest(item=item):
                self.assertIn(item, workflow)

    def test_s1r2_07_frozen_schema_bytes_remain_unchanged(self):
        import subprocess

        result = subprocess.run(
            [
                "git",
                "diff",
                "--name-only",
                FROZEN_SCHEMA_CANDIDATE,
                "HEAD",
                "--",
                "schemas/governance-r8/v15-r1",
            ],
            cwd=REPO_ROOT,
            check=True,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.stdout.strip(), "")

    def test_s1r2_08_source_ref_catalog_unused_members_are_not_rejected(self):
        # Frozen SPM intentionally includes catalog entries used for source authority/catalog
        # completeness but not directly referenced by an entry row. Successor 2 must not
        # invent an all-catalog-members-must-be-used constraint.
        spm = load_json(SCHEMA_DIR / "schema-provenance-manifest-candidate.json")
        runtime.validate_spm_document(copy.deepcopy(spm))


if __name__ == "__main__":
    unittest.main(verbosity=2)
