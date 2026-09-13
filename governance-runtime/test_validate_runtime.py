from __future__ import annotations
import hashlib,json,subprocess,tempfile,unittest
from pathlib import Path
from validate_runtime import validate_latest_result_evidence, require_governed_commit

def dg(v):
 return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()

class RuntimeEvidenceTests(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();self.root=Path(self.t.name)
  subprocess.run(["git","init","-q",str(self.root)],check=True)
  subprocess.run(["git","-C",str(self.root),"config","user.email","test@example.com"],check=True)
  subprocess.run(["git","-C",str(self.root),"config","user.name","Test"],check=True)
  subprocess.run(["git","-C",str(self.root),"remote","add","origin","https://github.com/vij7661/setugo-ai-development-framework.git"],check=True)
  (self.root/"candidate.txt").write_text("candidate",encoding="utf-8")
  subprocess.run(["git","-C",str(self.root),"add","candidate.txt"],check=True)
  subprocess.run(["git","-C",str(self.root),"commit","-q","-m","candidate"],check=True)
  self.candidate=subprocess.run(["git","-C",str(self.root),"rev-parse","HEAD"],check=True,capture_output=True,text=True).stdout.strip()
  record={"authority_origin":"EXTERNAL_TRUSTED_RUNNER","candidate_self_reported":False,"candidate_commit":self.candidate,
          "candidate_tree":"a"*40,"environment_digest":"b"*64,"executed_test_set_digest":"c"*64,"transcript_sha256":"d"*64,
          "test_case_count":3,"passed":3,"failures":[],"process_exit_code":0,"terminal_status":"PASS"}
  record["record_digest"]=dg(record)
  p=self.root/"review/test";p.mkdir(parents=True)
  self.raw=(json.dumps(record,sort_keys=True,separators=(",",":"))+"\n").encode()
  (p/"execution.json").write_bytes(self.raw)
  subprocess.run(["git","-C",str(self.root),"add","review/test/execution.json"],check=True)
  subprocess.run(["git","-C",str(self.root),"commit","-q","-m","evidence"],check=True)
  self.evidence_commit=subprocess.run(["git","-C",str(self.root),"rev-parse","HEAD"],check=True,capture_output=True,text=True).stdout.strip()
  self.latest={"passed":3,"total":3,"failures":[],"execution_evidence":{"evidence_commit":self.evidence_commit,"evidence_path":"review/test/execution.json","evidence_sha256":hashlib.sha256(self.raw).hexdigest()}}
 def tearDown(self):self.t.cleanup()
 def test_latest_result_requires_exact_governed_execution_record(self):
  validate_latest_result_evidence(self.latest,self.candidate,repo_root=self.root)
 def test_count_edit_cannot_forge_latest_result(self):
  latest=json.loads(json.dumps(self.latest));latest["passed"]=2;latest["failures"]=["X"]
  with self.assertRaisesRegex(AssertionError,"result mismatch"):validate_latest_result_evidence(latest,self.candidate,repo_root=self.root)
 def test_sha_shaped_evidence_commit_must_exist(self):
  latest=json.loads(json.dumps(self.latest));latest["execution_evidence"]["evidence_commit"]="f"*40
  with self.assertRaisesRegex(AssertionError,"not a governed Git commit"):validate_latest_result_evidence(latest,self.candidate,repo_root=self.root)
 def test_candidate_binding_must_match_execution_record(self):
  with self.assertRaisesRegex(AssertionError,"candidate mismatch"):validate_latest_result_evidence(self.latest,"e"*40,repo_root=self.root)
 def test_required_governed_commit_rejects_sha_shaped_nonobject(self):
  with self.assertRaisesRegex(AssertionError,"not a governed Git commit"):require_governed_commit("f"*40,"x",repo_root=self.root)
if __name__=="__main__":unittest.main()
