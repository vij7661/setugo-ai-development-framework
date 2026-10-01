import unittest,shutil
from pathlib import Path
from stage_evidence_data import stage
class Tests(unittest.TestCase):
 def setUp(self):
  self.root=Path(".q18-stage-data-test");shutil.rmtree(self.root,ignore_errors=True);self.src=self.root/"src";self.dst=self.root/"dst";self.src.mkdir(parents=True)
 def tearDown(self):shutil.rmtree(self.root,ignore_errors=True)
 def test_only_explicit_data_is_copied_and_code_is_ignored(self):
  (self.src/"receipt-spec.json").write_text("{}",encoding="utf-8")
  for name in ("github_evidence_ingestion.py","manual_review_ingestion.py","malicious.yml"):(self.src/name).write_text("raise SystemExit",encoding="utf-8")
  stage(self.src,self.dst,("receipt-spec.json",));self.assertEqual([p.name for p in self.dst.iterdir()],["receipt-spec.json"])
 def test_traversal_and_symlink_fail(self):
  (self.src/"receipt-spec.json").write_text("{}")
  with self.assertRaises(ValueError):stage(self.src,self.dst,("../receipt-spec.json",))
  try:(self.src/"blob-map.json").symlink_to(self.src/"receipt-spec.json")
  except OSError:return
  with self.assertRaises(ValueError):stage(self.src,self.dst,("blob-map.json",))
if __name__=="__main__":unittest.main()
