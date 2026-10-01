import copy,unittest,subprocess
from unittest.mock import Mock
from trusted_receipt_fetch import fetch
from test_governed_evidence_receipt import fixtures
class Tests(unittest.TestCase):
 def test_declared_immutable_trusted_root_is_exact_promoted_v2_successor(self):
  """The declaration is bound to the authorized successor, not candidate HEAD."""
  root="698d390dee9f062c984be8663aafc7994d009542"
  source=subprocess.check_output(["git","show",f"{root}:governance-runtime/q15_review_merge_gate.py"],text=True)
  self.assertIn('r8-trusted-receipt-proof/v2',source)
  self.assertNotIn('r8-trusted-receipt-proof/v1',source)
 def test_positive_artifact_bound_receipt(self):
  receipt,_,archives=fixtures();api=Mock();api.run.return_value={"id":99,"repository":"a/b","head_sha":receipt["trusted_code"]["verifier_commit"],"workflow_file":".github/workflows/governance-evidence-receipt-ingestion.yml","conclusion":"success"};api.job.return_value={"id":98,"run_id":99,"workflow_identity":"receipt-only","conclusion":"success"};api.artifact.return_value={"id":97,"run_id":99,"digest":"sha256:archive","archive_download_url":"u"};api.download_artifact.return_value=archives["packet"]
  # Build a one-member archive containing the receipt for the focused proof test.
  import io,zipfile,json
  out=io.BytesIO()
  with zipfile.ZipFile(out,"w") as z:z.writestr("governed-evidence-receipt.json",json.dumps(receipt,sort_keys=True,separators=(",",":")))
  raw=out.getvalue();api.artifact.return_value={"id":97,"run_id":99,"digest":"sha256:"+__import__("hashlib").sha256(raw).hexdigest(),"archive_download_url":"u"};api.download_artifact.return_value=raw
  value,proof=fetch(api=api,repository="a/b",artifact_id="97",run_id="99",job_id="98",archive_digest=api.artifact.return_value["digest"],verifier_commit=receipt["trusted_code"]["verifier_commit"],verifier_tree=receipt["trusted_code"]["verifier_tree"])
  self.assertEqual(proof["receipt_sha256"],__import__("hashlib").sha256(value).hexdigest())
 def test_identity_substitution_fails(self):
  receipt,_,_=fixtures();api=Mock();api.run.return_value={"id":1,"workflow_file":"wf","conclusion":"success"};api.job.return_value={"id":2,"run_id":1,"workflow_identity":"job","conclusion":"success"};api.artifact.return_value={"id":3,"run_id":1,"digest":"sha256:"+"0"*64,"archive_download_url":"u"};api.download_artifact.return_value=b"not zip"
  with self.assertRaises(ValueError):fetch(api=api,repository="a/b",artifact_id="3",run_id="1",job_id="2",workflow_file="wf",workflow_identity="job",archive_digest="sha256:"+"0"*64,verifier_commit="e"*40,verifier_tree="f"*40)
 def test_wrong_verifier_tree_or_claim_fails_closed(self):
  receipt,_,_=fixtures();
  from governed_evidence_receipt import verify_trusted_code_binding
  self.assertFalse(verify_trusted_code_binding(receipt,expected_commit=receipt["trusted_code"]["verifier_commit"],expected_tree="0"*40))
 def test_wrong_producer_head_or_workflow_fails_before_artifact(self):
  receipt,_,_=fixtures();api=Mock();api.run.return_value={"id":1,"repository":"a/b","head_sha":"0"*40,"workflow_file":".github/workflows/governance-evidence-receipt-ingestion.yml","conclusion":"success"}
  with self.assertRaises(ValueError): fetch(api=api,repository="a/b",artifact_id="3",run_id="1",job_id="2",archive_digest="sha256:"+"0"*64,verifier_commit=receipt["trusted_code"]["verifier_commit"],verifier_tree=receipt["trusted_code"]["verifier_tree"])
 def test_committed_review_requires_receipt_bound_revision_path_and_bytes(self):
  receipt,_,_=fixtures(); from fetch_committed_review import fetch as fetch_review
  api=Mock(); api.committed_review.return_value=(b"review bytes\n",receipt["independent_review"]["git_blob"])
  raw=fetch_review(api=api,repository=receipt["review_source"]["repository"],revision=receipt["review_source"]["revision"],path=receipt["review_source"]["path"],receipt=receipt)
  self.assertEqual(raw,b"review bytes\n")
  with self.assertRaises(ValueError): fetch_review(api=api,repository=receipt["review_source"]["repository"],revision="b"*40,path="review.txt",receipt=receipt)
if __name__=="__main__":unittest.main()
