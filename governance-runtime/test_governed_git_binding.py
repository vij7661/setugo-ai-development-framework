from __future__ import annotations
import subprocess,tempfile,unittest
from pathlib import Path
from governed_git_binding import verify_governed_commit

class GovernedGitBindingTests(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();self.root=Path(self.t.name)
  subprocess.run(["git","init","-q",str(self.root)],check=True)
  subprocess.run(["git","-C",str(self.root),"config","user.email","test@example.com"],check=True)
  subprocess.run(["git","-C",str(self.root),"config","user.name","Test"],check=True)
  subprocess.run(["git","-C",str(self.root),"remote","add","origin","https://github.com/vij7661/setugo-ai-development-framework.git"],check=True)
  (self.root/"x").write_text("x")
  subprocess.run(["git","-C",str(self.root),"add","x"],check=True)
  subprocess.run(["git","-C",str(self.root),"commit","-q","-m","x"],check=True)
  self.head=subprocess.run(["git","-C",str(self.root),"rev-parse","HEAD"],check=True,capture_output=True,text=True).stdout.strip()
 def tearDown(self):self.t.cleanup()
 def test_exact_governed_commit_and_head_pass(self):
  ok,_=verify_governed_commit(repo_root=self.root,expected_repository="vij7661/setugo-ai-development-framework",commit=self.head,expected_head=self.head);self.assertTrue(ok)
 def test_sha_shaped_nonobject_fails(self):
  ok,_=verify_governed_commit(repo_root=self.root,expected_repository="vij7661/setugo-ai-development-framework",commit="f"*40,expected_head="f"*40);self.assertFalse(ok)
 def test_wrong_origin_fails(self):
  ok,_=verify_governed_commit(repo_root=self.root,expected_repository="other/repo",commit=self.head,expected_head=self.head);self.assertFalse(ok)
 def test_head_mismatch_fails(self):
  ok,_=verify_governed_commit(repo_root=self.root,expected_repository="vij7661/setugo-ai-development-framework",commit=self.head,expected_head="a"*40);self.assertFalse(ok)
if __name__=="__main__":unittest.main()
