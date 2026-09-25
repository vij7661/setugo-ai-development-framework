import copy
import importlib
import json
import pathlib
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
SCHEMA_DIR = REPO_ROOT / "schemas" / "governance-r8" / "v15-r1"
FROZEN_SCHEMA_CANDIDATE = "f93ca26975ecb64f0da13779889c75b36140cdfc"
SUCCESSOR_BRANCH = "implementation/r8-v15-r1-slice1-successor-1-2026-09-25"

sys.path.insert(0, str(HERE))
runtime = importlib.import_module("r8_v15_r1_frozen_schema_runtime")


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class Slice1Successor1RepairAcceptance(unittest.TestCase):
    maxDiff = None

    def test_s1r_01_at_most_one_byte_read_per_schema_artifact(self):
        counts = {}
        original = pathlib.Path.read_bytes

        def counted(path_obj):
            resolved = path_obj.resolve()
            try:
                resolved.relative_to(SCHEMA_DIR.resolve())
                counts[str(resolved)] = counts.get(str(resolved), 0) + 1
            except ValueError:
                pass
            return original(path_obj)

        with mock.patch.object(pathlib.Path, "read_bytes", counted):
            bundle = runtime.FrozenSchemaRuntime(
                REPO_ROOT, candidate_sha=FROZEN_SCHEMA_CANDIDATE
            ).load()
        self.assertEqual(bundle["authority_effect"], "NONE")
        duplicates = {path: n for path, n in counts.items() if n > 1}
        self.assertEqual(duplicates, {}, f"schema artifacts reopened: {duplicates}")

    def test_s1r_02_no_post_verification_text_reopen(self):
        original = pathlib.Path.read_text

        def guarded(path_obj, *args, **kwargs):
            resolved = path_obj.resolve()
            try:
                resolved.relative_to(SCHEMA_DIR.resolve())
            except ValueError:
                return original(path_obj, *args, **kwargs)
            raise AssertionError(f"verified schema artifact reopened through read_text: {resolved}")

        with mock.patch.object(pathlib.Path, "read_text", guarded):
            bundle = runtime.FrozenSchemaRuntime(
                REPO_ROOT, candidate_sha=FROZEN_SCHEMA_CANDIDATE
            ).load()
        self.assertEqual(bundle["authority_effect"], "NONE")

    def test_s1r_03_lone_surrogate_rejects_explicitly(self):
        with self.assertRaises(runtime.GCPError) as cm:
            runtime.canonicalize_json_text(
                '{"text":"\\ud800"}',
                schema_context="authority_string",
            )
        self.assertEqual(cm.exception.code, "GCP_REJECT_UNPAIRED_SURROGATE")

    def test_s1r_04_loader_self_checks_all_rejection_vectors(self):
        self.assertTrue(
            hasattr(runtime, "validate_rejection_vectors"),
            "successor mechanism must expose deterministic rejection-vector self-check",
        )
        with mock.patch.object(
            runtime,
            "validate_rejection_vectors",
            wraps=runtime.validate_rejection_vectors,
        ) as checker:
            runtime.FrozenSchemaRuntime(
                REPO_ROOT, candidate_sha=FROZEN_SCHEMA_CANDIDATE
            ).load()
        self.assertEqual(checker.call_count, 1)

    def test_s1r_05_direct_spm_validation_requires_exact_3058_entries(self):
        spm = load_json(SCHEMA_DIR / "schema-provenance-manifest-candidate.json")
        mutated = copy.deepcopy(spm)
        mutated["entries"] = mutated["entries"][:-1]
        mutated["entry_count"] = len(mutated["entries"])
        self.assertEqual(mutated["entry_count"], 3057)
        with self.assertRaises(runtime.FrozenSchemaError) as cm:
            runtime.validate_spm_document(mutated)
        self.assertEqual(cm.exception.code, "SPM_ENTRY_COUNT_MISMATCH")

    def test_s1r_06_spm_artifact_paths_are_confined(self):
        spm = load_json(SCHEMA_DIR / "schema-provenance-manifest-candidate.json")
        mutated = copy.deepcopy(spm)
        original_path = mutated["artifacts"][0]["path"]
        mutated["artifacts"][0]["path"] = "schemas/governance-r8/elsewhere/" + Path(original_path).name
        with self.assertRaises(runtime.FrozenSchemaError) as cm:
            runtime.validate_spm_document(mutated)
        self.assertEqual(cm.exception.code, "SPM_ARTIFACT_PATH_INVALID")

    def test_s1r_07_workflow_trigger_covers_governed_paths(self):
        workflow = (
            REPO_ROOT / ".github" / "workflows" / "r8-v15-r1-implementation-slice1.yml"
        ).read_text(encoding="utf-8")
        required = [
            SUCCESSOR_BRANCH,
            "governance-runtime/r8_v15_r1_frozen_schema_runtime.py",
            "governance-runtime/test_r8_v15_r1_implementation_slice1.py",
            "governance-runtime/test_r8_v15_r1_implementation_slice1_successor1.py",
            "governance-runtime/test_r8_v15_r1_post_freeze_regression.py",
            "governance-runtime/test_r8_v15_r1_sfv45_r2_repair.py",
            "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE1-SUCCESSOR1-PREREGISTRATION.md",
            "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE1-MARKER.json",
            ".github/workflows/r8-v15-r1-implementation-slice1.yml",
        ]
        for item in required:
            with self.subTest(item=item):
                self.assertIn(item, workflow)

    def test_s1r_08_frozen_schema_bytes_remain_unchanged(self):
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
