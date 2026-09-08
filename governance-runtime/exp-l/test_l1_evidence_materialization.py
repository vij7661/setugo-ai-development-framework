from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path("governance-runtime/review-trust-kernel/materialization_v2.py")


def load_module(repo_root):
    spec = importlib.util.spec_from_file_location("materialization_v2", repo_root / MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True).stdout


def make_repo():
    td = tempfile.TemporaryDirectory()
    root = Path(td.name)
    run(["git", "init", "-q"], root)
    run(["git", "config", "user.email", "exp-l@example.invalid"], root)
    run(["git", "config", "user.name", "EXP-L"], root)
    (root / "policy.txt").write_text("authoritative policy\n", encoding="utf-8")
    run(["git", "add", "."], root)
    run(["git", "commit", "-q", "-m", "candidate"], root)
    commit = run(["git", "rev-parse", "HEAD"], root).strip()
    return td, root, commit


class EvidenceMaterializationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo_root = Path(__file__).resolve().parents[2]
        cls.m = load_module(cls.repo_root)

    def test_l1_01_file_ref_materialized_and_candidate_bound(self):
        td, root, commit = make_repo(); self.addCleanup(td.cleanup)
        out = self.m.materialize_evidence_refs(root, commit, [{"type":"file","ref":"policy.txt"}])
        self.assertEqual(out["declared_count"], 1)
        self.assertEqual(out["materialized_count"], 1)
        a = out["artifacts"][0]
        self.assertEqual(a["candidate_commit"], commit)
        self.assertEqual(len(a["sha256"]), 64)

    def test_l1_02_missing_file_fails_closed(self):
        td, root, commit = make_repo(); self.addCleanup(td.cleanup)
        with self.assertRaisesRegex(RuntimeError, "candidate evidence file unavailable"):
            self.m.materialize_evidence_refs(root, commit, [{"type":"file","ref":"missing.txt"}])

    def test_l1_03_ci_run_without_resolver_fails_closed(self):
        td, root, commit = make_repo(); self.addCleanup(td.cleanup)
        with self.assertRaisesRegex(RuntimeError, "unsupported or unresolved"):
            self.m.materialize_evidence_refs(root, commit, [{"type":"ci_run","ref":"34189633886"}])

    def test_l1_04_ci_run_with_trusted_resolver_is_hashed(self):
        td, root, commit = make_repo(); self.addCleanup(td.cleanup)
        def resolve_ci(ref):
            return {"run_id": ref["ref"], "status":"completed", "conclusion":"success", "head_sha":commit}
        out = self.m.materialize_evidence_refs(
            root, commit, [{"type":"ci_run","ref":"34189633886"}], {"ci_run":resolve_ci}
        )
        a = out["artifacts"][0]
        self.assertEqual(a["content"]["head_sha"], commit)
        self.assertEqual(len(a["sha256"]), 64)

    def test_l1_05_unknown_type_fails_closed(self):
        td, root, commit = make_repo(); self.addCleanup(td.cleanup)
        with self.assertRaisesRegex(RuntimeError, "unsupported or unresolved"):
            self.m.materialize_evidence_refs(root, commit, [{"type":"mystery","ref":"x"}])

    def test_l1_06_mixed_refs_are_all_materialized_or_fail(self):
        td, root, commit = make_repo(); self.addCleanup(td.cleanup)
        def resolve_ci(ref):
            return {"run_id": ref["ref"], "status":"completed", "conclusion":"success", "head_sha":commit}
        refs = [{"type":"file","ref":"policy.txt"},{"type":"ci_run","ref":"7"}]
        out = self.m.materialize_evidence_refs(root, commit, refs, {"ci_run":resolve_ci})
        self.assertEqual(out["declared_count"], 2)
        self.assertEqual(out["materialized_count"], 2)
        self.assertEqual(len(out["artifacts"]), 2)
        self.assertEqual(len(out["manifest_sha256"]), 64)


if __name__ == "__main__":
    unittest.main(verbosity=2)
