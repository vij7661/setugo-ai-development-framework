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
    git_blob_sha,
    validate_integrated_successor_manifest,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "implementation/v24/V24-I11-V6-INTEGRATED-SUCCESSOR-MANIFEST.json"
SHARED_RESOLVER = "governance-runtime/v24_v6_proof_reference_closure.py"


def current_manifest() -> dict:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows = {row["workstream_id"]: row for row in manifest["workstreams"]}
    for wid, path in EXPECTED_PRODUCTION_MODULES.items():
        rows[wid]["production_git_blob_sha"] = git_blob_sha((ROOT / path).read_bytes())
    for wid, path in EXPECTED_EVIDENCE_FILES.items():
        rows[wid]["evidence_git_blob_sha"] = git_blob_sha((ROOT / path).read_bytes())
    return manifest


def copy_bound_surface(target: Path) -> None:
    paths = set(EXPECTED_PRODUCTION_MODULES.values()) | set(EXPECTED_EVIDENCE_FILES.values())
    paths.add(SHARED_RESOLVER)
    for repo_path in sorted(paths):
        src = ROOT / repo_path
        dst = target / repo_path
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)


class R9SharedDependencyFreezeRedTests(unittest.TestCase):
    def test_shared_proof_resolver_mutation_must_invalidate_successor_binding(self):
        manifest = current_manifest()

        baseline = validate_integrated_successor_manifest(
            repo_root=ROOT,
            manifest=manifest,
        )
        self.assertTrue(baseline["integration_valid"], baseline["problems"])

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            copy_bound_surface(temp_root)
            copied = validate_integrated_successor_manifest(
                repo_root=temp_root,
                manifest=copy.deepcopy(manifest),
            )
            self.assertTrue(copied["integration_valid"], copied["problems"])

            resolver = temp_root / SHARED_RESOLVER
            original = resolver.read_bytes()
            resolver.write_bytes(original + b"\n# R9 dependency-falsification mutation\n")

            mutated = validate_integrated_successor_manifest(
                repo_root=temp_root,
                manifest=copy.deepcopy(manifest),
            )

        # Pre-repair R9 binds only the eight headline workstream modules and
        # evidence files. A load-bearing shared resolver mutation therefore
        # remains invisible. Required behavior is fail-closed exact dependency
        # binding under the successor freeze.
        self.assertFalse(
            mutated["integration_valid"],
            "R9 false-green: shared proof resolver changed outside frozen successor binding",
        )
        self.assertTrue(
            any(
                "INTEGRATED_SUCCESSOR_SHARED_DEPENDENCY_BLOB_MISMATCH" in problem
                for problem in mutated["problems"]
            ),
            mutated["problems"],
        )


if __name__ == "__main__":
    unittest.main()
