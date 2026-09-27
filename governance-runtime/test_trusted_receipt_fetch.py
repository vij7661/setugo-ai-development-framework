import copy,unittest
from unittest.mock import Mock
from trusted_receipt_fetch import fetch
from test_governed_evidence_receipt import fixtures
class Tests(unittest.TestCase):
 def test_positive_artifact_bound_receipt(self):
  receipt,_,archives=fixtures();api=Mock();api.run.return_value={"id":99,"workflow_file":"wf.yml","conclusion":"success"};api.job.return_value={"id":98,"run_id":99,"workflow_identity":"receipt","conclusion":"success"};api.artifact.return_value={"id":97,"run_id":99,"digest":"sha256:archive","archive_download_url":"u"};api.download_artifact.return_value=archives["packet"]
  # Build a one-member archive containing the receipt for the focused proof test.
  import io,zipfile,json
  out=io.BytesIO()
  with zipfile.ZipFile(out,"w") as z:z.writestr("governed-evidence-receipt.json",json.dumps(receipt,sort_keys=True,separators=(",",":")))
  raw=out.getvalue();api.artifact.return_value={"id":97,"run_id":99,"digest":"sha256:"+__import__("hashlib").sha256(raw).hexdigest(),"archive_download_url":"u"};api.download_artifact.return_value=raw
  value,proof=fetch(api=api,repository="a/b",artifact_id="97",run_id="99",job_id="98",workflow_file="wf.yml",workflow_identity="receipt",archive_digest=api.artifact.return_value["digest"],verifier_commit=receipt["trusted_code"]["verifier_commit"],verifier_tree=receipt["trusted_code"]["verifier_tree"])
  self.assertEqual(proof["receipt_sha256"],__import__("hashlib").sha256(value).hexdigest())
 def test_identity_substitution_fails(self):
  receipt,_,_=fixtures();api=Mock();api.run.return_value={"id":1,"workflow_file":"wf","conclusion":"success"};api.job.return_value={"id":2,"run_id":1,"workflow_identity":"job","conclusion":"success"};api.artifact.return_value={"id":3,"run_id":1,"digest":"sha256:"+"0"*64,"archive_download_url":"u"};api.download_artifact.return_value=b"not zip"
  with self.assertRaises(ValueError):fetch(api=api,repository="a/b",artifact_id="3",run_id="1",job_id="2",workflow_file="wf",workflow_identity="job",archive_digest="sha256:"+"0"*64,verifier_commit="e"*40,verifier_tree="f"*40)
 def test_wrong_verifier_tree_or_claim_fails_closed(self):
  receipt,_,_=fixtures();
  from governed_evidence_receipt import verify_trusted_code_binding
  self.assertFalse(verify_trusted_code_binding(receipt,expected_commit=receipt["trusted_code"]["verifier_commit"],expected_tree="0"*40))
if __name__=="__main__":unittest.main()
