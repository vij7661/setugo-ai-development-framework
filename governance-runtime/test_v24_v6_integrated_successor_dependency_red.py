from __future__ import annotations

import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from v24_v6_integrated_successor import (
    EXPECTED_EVIDENCE_FILES,
    EXPECTED_PRODUCTION_MODULES,
    EXPECTED_SHARED_PRODUCTION_DEPENDENCIES,
    git_blob_sha,
    validate_integrated_successor_manifest,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "implementation/v24/V24-I11-V6-INTEGRATED-SUCCESSOR-MANIFEST.json"


def current_manifest() -> dict:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows = {row["workstream_id"]: row for row in manifest["workstreams"]}
    for wid, path in EXPECTED_PRODUCTION_MODULES.items():
        rows[wid]["production_git_blob_sha"] = git_blob_sha((ROOT / path).read_bytes())
    for wid, path in EXPECTED_EVIDENCE_FILES.items():
        rows[wid]["evidence_git_blob_sha"] = git_blob_sha((ROOT / path).read_bytes())
    manifest["shared_dependencies"] = [
        {
            "dependency_id": dep_id,
            "path": path,
            "git_blob_sha": git_blob_sha((ROOT / path).read_bytes()),
        }
        for dep_id, path in sorted(EXPECTED_SHARED_PRODUCTION_DEPENDENCIES.items())
    ]
    checks = set(manifest.get("mandatory_v6_adversarial_checks", []))
    checks.add("SHARED_PRODUCTION_DEPENDENCY_MUTATION_REJECTED")
    manifest["mandatory_v6_adversarial_checks"] = sorted(checks)
    return manifest


def copy_bound_surface(target: Path) -> None:
    paths = set(EXPECTED_PRODUCTION_MODULES.values()) | set(EXPECTED_EVIDENCE_FILES.values())
    paths |= set(EXPECTED_SHARED_PRODUCTION_DEPENDENCIES.values())
    for repo_path in sorted(paths):
        src = ROOT / repo_path
        dst = target / repo_path
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)


class R9SharedDependencyFreezeRedTests(unittest.TestCase):
    def test_each_audited_shared_dependency_mutation_invalidates_successor_binding(self):
        manifest = current_manifest()
        baseline = validate_integrated_successor_manifest(repo_root=ROOT, manifest=manifest)
        self.assertTrue(baseline["integration_valid"], baseline["problems"])
        self.assertEqual(
            baseline["bound_file_count"],
            16 + len(EXPECTED_SHARED_PRODUCTION_DEPENDENCIES),
        )

        for dep_id, repo_path in sorted(EXPECTED_SHARED_PRODUCTION_DEPENDENCIES.items()):
            with self.subTest(dependency_id=dep_id):
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_root = Path(temp_dir)
                    copy_bound_surface(temp_root)
                    copied = validate_integrated_successor_manifest(
                        repo_root=temp_root,
                        manifest=copy.deepcopy(manifest),
                    )
                    self.assertTrue(copied["integration_valid"], copied["problems"])

                    dependency = temp_root / repo_path
                    dependency.write_bytes(
                        dependency.read_bytes()
                        + f"\n# R9 dependency-falsification mutation: {dep_id}\n".encode("utf-8")
                    )
                    mutated = validate_integrated_successor_manifest(
                        repo_root=temp_root,
                        manifest=copy.deepcopy(manifest),
                    )

                self.assertFalse(
                    mutated["integration_valid"],
                    f"R9 false-green: {dep_id} changed outside frozen successor binding",
                )
                self.assertIn(
                    f"INTEGRATED_SUCCESSOR_SHARED_DEPENDENCY_BLOB_MISMATCH:{dep_id}",
                    mutated["problems"],
                )


if __name__ == "__main__":
    unittest.main()
