from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
import unittest
from hashlib import sha256
from pathlib import Path

TRUST_KERNEL_COMMIT = "be3dc453c38f53a8a9868e11951d41ed257e835e"
KERNEL_PATH = "governance-runtime/review-trust-kernel/kernel.py"


def run(cmd, cwd, *, input_text=None):
    return subprocess.run(
        cmd, cwd=cwd, input=input_text, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True,
    ).stdout


def load_frozen_kernel(repo_root: Path):
    content = subprocess.run(
        ["git", "show", f"{TRUST_KERNEL_COMMIT}:{KERNEL_PATH}"],
        cwd=repo_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True,
    ).stdout
    td = tempfile.TemporaryDirectory()
    path = Path(td.name) / "frozen_review_kernel.py"
    path.write_bytes(content)
    spec = importlib.util.spec_from_file_location("frozen_review_kernel", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    module._test_tempdir = td
    module._frozen_bytes = content
    return module


def make_candidate_repo():
    td = tempfile.TemporaryDirectory()
    root = Path(td.name)
    run(["git", "init", "-q"], root)
    run(["git", "config", "user.email", "exp-l@example.invalid"], root)
    run(["git", "config", "user.name", "EXP-L"], root)
    (root / "blocking.txt").write_text("BLOCKING GOVERNANCE EVIDENCE\n", encoding="utf-8")
    (root / "platform_candidate_review.py").write_text(
        "def build_corpus(*a, **k): return {'evidence_artifacts': []}\n"
        "def validate(*a, **k): return {'valid': True, 'effective_disposition': 'PASS'}\n",
        encoding="utf-8",
    )
    (root / "kernel.py").write_text(
        "def collect_candidate_files(*a, **k): return []\n"
        "def validate_review(*a, **k): return {'valid': True}\n",
        encoding="utf-8",
    )
    run(["git", "add", "."], root)
    run(["git", "commit", "-q", "-m", "malicious candidate"], root)
    commit = run(["git", "rev-parse", "HEAD"], root).strip()
    return td, root, commit


class ReviewKernelBootstrapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo_root = Path(__file__).resolve().parents[2]
        cls.kernel = load_frozen_kernel(cls.repo_root)

    def test_l7_01_candidate_collector_cannot_omit_blocking_file(self):
        td, root, commit = make_candidate_repo()
        self.addCleanup(td.cleanup)
        artifacts = self.kernel.collect_candidate_files(
            root, commit, [{"type": "file", "ref": "blocking.txt"}]
        )
        self.assertEqual([a["path"] for a in artifacts], ["blocking.txt"])
        self.assertIn("BLOCKING GOVERNANCE EVIDENCE", artifacts[0]["content"])

    def test_l7_02_candidate_validator_cannot_force_pass(self):
        request = {
            "review_request_id": "R",
            "artifact": {"commit": "a" * 40},
            "required_review_dimensions": [{"id": "D1", "mandatory": True}],
        }
        contradictory_pass = {
            "review_request_id": "R",
            "reviewed_artifact_commit": "a" * 40,
            "reviewer": {"provider": "gemini", "model": "m"},
            "disposition": "PASS",
            "findings": [],
            "review_coverage": [
                {"dimension_id": "D1", "status": "CONTRADICTED", "evidence": ["e1"]}
            ],
        }
        result = self.kernel.validate_review(contradictory_pass, request, "gemini", "m")
        self.assertFalse(result["valid"])
        self.assertEqual(result["effective_disposition"], "INVALID_REVIEW_EVIDENCE")
        self.assertIn("PASS contradicts coverage/findings", result["errors"])

    def test_l7_03_candidate_shadow_module_cannot_replace_frozen_kernel(self):
        td, root, _ = make_candidate_repo()
        self.addCleanup(td.cleanup)
        candidate_shadow = (root / "kernel.py").read_bytes()
        frozen = self.kernel._frozen_bytes
        self.assertNotEqual(sha256(candidate_shadow).hexdigest(), sha256(frozen).hexdigest())
        self.assertEqual(
            sha256(frozen).hexdigest(),
            sha256(
                subprocess.run(
                    ["git", "show", f"{TRUST_KERNEL_COMMIT}:{KERNEL_PATH}"],
                    cwd=self.repo_root, stdout=subprocess.PIPE, check=True,
                ).stdout
            ).hexdigest(),
        )
        self.assertNotEqual(Path(self.kernel.__file__).resolve(), (root / "kernel.py").resolve())

    def test_l7_04_candidate_side_workflow_has_no_authority(self):
        result = self.kernel.classify_candidate_side_execution()
        self.assertFalse(result["trusted"])
        self.assertEqual(result["authority_effect"], "NONE")
        self.assertEqual(result["reason"], "CANDIDATE_CONTROLLED_EXECUTION_PATH")


if __name__ == "__main__":
    unittest.main(verbosity=2)
