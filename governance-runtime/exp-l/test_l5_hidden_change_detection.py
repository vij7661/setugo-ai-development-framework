from __future__ import annotations

import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path("governance-runtime/review-trust-kernel/changed_files_v2.py")


def run(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True).stdout


def load_module(repo_root):
    spec = importlib.util.spec_from_file_location("changed_files_v2", repo_root / MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def make_repo():
    td = tempfile.TemporaryDirectory(); root = Path(td.name)
    run(["git","init","-q"],root); run(["git","config","user.email","exp-l@example.invalid"],root); run(["git","config","user.name","EXP-L"],root)
    for p, text in {
        "governance-runtime/gate.py":"gate=1\n",
        ".github/review-trigger.json":"{}\n",
        "standards/nested/policy.md":"v1\n",
        "governance-runtime/rename-me.txt":"x\n",
        "governance-runtime/delete-me.txt":"y\n",
    }.items():
        path=root/p; path.parent.mkdir(parents=True,exist_ok=True); path.write_text(text,encoding="utf-8")
    run(["git","add","."],root); run(["git","commit","-q","-m","base"],root)
    base=run(["git","rev-parse","HEAD"],root).strip()
    (root/"governance-runtime/gate.py").write_text("gate=2\n",encoding="utf-8")
    (root/".github/review-trigger.json").write_text('{"enabled":true}\n',encoding="utf-8")
    (root/"standards/nested/policy.md").write_text("v2\n",encoding="utf-8")
    run(["git","mv","governance-runtime/rename-me.txt","governance-runtime/renamed.txt"],root)
    (root/"governance-runtime/delete-me.txt").unlink()
    run(["git","add","-A"],root); run(["git","commit","-q","-m","candidate"],root)
    candidate=run(["git","rev-parse","HEAD"],root).strip()
    return td,root,base,candidate


class HiddenChangeDetectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo_root=Path(__file__).resolve().parents[2]
        cls.m=load_module(cls.repo_root)

    def setUp(self):
        self.td,self.root,self.base,self.candidate=make_repo(); self.addCleanup(self.td.cleanup)
        self.inv=self.m.complete_changed_file_inventory(self.root,self.base,self.candidate)

    def paths(self):
        out=set()
        for c in self.inv["changes"]:
            if "path" in c: out.add(c["path"])
            else: out.update([c["old_path"],c["new_path"]])
        return out

    def test_l5_01_gate_change_surfaced(self):
        self.assertIn("governance-runtime/gate.py",self.paths())

    def test_l5_02_hidden_trigger_change_surfaced(self):
        self.assertIn(".github/review-trigger.json",self.paths())

    def test_l5_03_nested_policy_change_surfaced(self):
        self.assertIn("standards/nested/policy.md",self.paths())

    def test_l5_04_rename_represented(self):
        renames=[c for c in self.inv["changes"] if c["status"].startswith("R")]
        self.assertEqual(len(renames),1)
        self.assertEqual(renames[0]["old_path"],"governance-runtime/rename-me.txt")
        self.assertEqual(renames[0]["new_path"],"governance-runtime/renamed.txt")

    def test_l5_05_deletion_represented(self):
        deletions=[c for c in self.inv["changes"] if c["status"]=="D"]
        self.assertTrue(any(c["path"]=="governance-runtime/delete-me.txt" for c in deletions))


if __name__=="__main__": unittest.main(verbosity=2)
