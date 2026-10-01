import unittest,json,tempfile
from unittest.mock import patch
from manual_review_ingestion import ingest
from governed_evidence_receipt import canonical_bytes,sha256_bytes
from test_governed_evidence_receipt import fixtures
from pathlib import Path
IDENTITY={"candidate_commit":"a"*40,"candidate_tree":"b"*40}
class Tests(unittest.TestCase):
 def test_gate_is_load_bearing_and_output_grants_no_authority(self):
  with patch("manual_review_ingestion.review_merge_evidence_eligible",return_value=True) as gate:
   result=ingest(review_path="r",freeze_attestation_path="f",linux_statement_path="l",packet_statement_path="p",packet_payload_path="b",receipt_path="e",receipt_sha256="c"*64,expected_identity=IDENTITY)
  gate.assert_called_once();self.assertTrue(result["review_evidence_eligible"]);self.assertEqual(result["authority_effect"],"NONE");self.assertFalse(result["automatic_merge"]);self.assertFalse(any(result[k] for k in ("runtime_authority","release_authority","deployment_authority","production_authority")))
 def test_fake_receipt_and_expected_identity_without_trusted_proof_reject(self):
  receipt,_,_=fixtures();path=Path(".q18-fake-receipt.json");path.write_bytes(canonical_bytes(receipt))
  try:
   with self.assertRaises(ValueError):ingest(review_path="r",freeze_attestation_path="f",linux_statement_path="l",packet_statement_path="p",packet_payload_path="b",receipt_path=path,receipt_sha256=sha256_bytes(path.read_bytes()),expected_identity=IDENTITY,candidate_label="Q18",trusted_receipt_proof_path=None,trusted_verifier_commit="e"*40,trusted_verifier_tree="f"*40)
  finally:path.unlink(missing_ok=True)
 def test_legitimate_receipt_with_forged_expected_identity_uses_receipt_identity(self):
  receipt,_,_=fixtures();path=Path(".q18-fake-receipt.json");proof=Path(".q18-proof.json");path.write_bytes(canonical_bytes(receipt));proof.write_text(__import__("json").dumps({"schema":"r8-trusted-receipt-proof/v2","source":"GITHUB_ACTIONS_ARTIFACT_DOWNLOAD","receipt_sha256":sha256_bytes(path.read_bytes()),"repository":"a/b","run_id":"1","job_id":"2","workflow_file":".github/workflows/governance-evidence-receipt-ingestion.yml","workflow_identity":"receipt-only","artifact_id":"3","archive_digest":"sha256:"+"a"*64,"member":"governed-evidence-receipt.json","producer_head_sha":"e"*40,"verifier_commit":"e"*40,"verifier_tree":"f"*40}))
  try:
   with patch("manual_review_ingestion.review_merge_evidence_eligible",return_value=False) as gate:
    result=ingest(review_path="r",freeze_attestation_path="f",linux_statement_path="l",packet_statement_path="p",packet_payload_path="b",receipt_path=path,receipt_sha256=sha256_bytes(path.read_bytes()),expected_identity={"candidate_commit":"0"*40,"candidate_tree":"0"*40},candidate_label="Q18",trusted_receipt_proof_path=proof,committed_review_path="c",trusted_verifier_commit="e"*40,trusted_verifier_tree="f"*40)
   gate.assert_called_once();self.assertFalse(result["review_evidence_eligible"]);self.assertEqual(gate.call_args.kwargs["expected_identity"]["candidate_commit"],receipt["candidate"]["commit"])
  finally:path.unlink(missing_ok=True);proof.unlink(missing_ok=True)
 def test_v2_trusted_proof_end_to_end_reaches_real_gate(self):
  from test_q15_review_merge_gate import review
  from test_governed_evidence_receipt import fixtures as v2_fixtures
  from governed_evidence_receipt import git_blob_sha1
  receipt,blobs,archives=v2_fixtures(); committed=review().replace("a"*40,"c"*40).replace("c"*40,"d"*40,1).replace("changed-file count from baseline: 53","changed-file count from baseline: 88").replace("11 / 12","21 / 22").replace("13 / 14","11 / 12") .encode()
  receipt["independent_review"]={"original_upload_raw_sha256":sha256_bytes(committed),"committed_review_sha256":sha256_bytes(committed),"git_blob":git_blob_sha1(committed)}
  receipt["trusted_code"]={"verifier_commit":"e"*40,"verifier_tree":"f"*40,"evidence_ref":"evidence/q18"}
  receipt["review_source"]={"repository":receipt["repository"],"revision":"a"*40,"path":"review.txt"}
  receipt_raw=canonical_bytes(receipt); proof={"schema":"r8-trusted-receipt-proof/v2","source":"GITHUB_ACTIONS_ARTIFACT_DOWNLOAD","receipt_sha256":sha256_bytes(receipt_raw),"repository":receipt["repository"],"run_id":"1","job_id":"2","workflow_file":".github/workflows/governance-evidence-receipt-ingestion.yml","workflow_identity":"receipt-only","artifact_id":"3","archive_digest":"sha256:"+"a"*64,"member":"governed-evidence-receipt.json","producer_head_sha":"e"*40,"verifier_commit":"e"*40,"verifier_tree":"f"*40}
  with tempfile.TemporaryDirectory() as td:
   import zipfile
   root=Path(td); paths={"freeze":root/"freeze.json","linux":root/"linux.json","packet":root/"packet.json","payload":root/"payload.bin","receipt":root/"receipt.json"}; paths["freeze"].write_bytes(blobs["freeze_attestation"]); paths["receipt"].write_bytes(receipt_raw)
   with zipfile.ZipFile(__import__('io').BytesIO(archives["linux"])) as z: paths["linux"].write_bytes(z.read(receipt["linux"]["statement_member_path"]));
   with zipfile.ZipFile(__import__('io').BytesIO(archives["packet"])) as z: paths["packet"].write_bytes(z.read(receipt["packet"]["statement_member_path"])); paths["payload"].write_bytes(z.read(receipt["packet"]["payload_member_path"]))
   committed_path=root/"committed-review.txt";committed_path.write_bytes(committed); proof_path=root/"proof.json";proof_path.write_text(json.dumps(proof),encoding="utf-8")
   with patch("q15_review_merge_gate.load_and_verify",return_value=freeze):
    result=ingest(review_path=committed_path,freeze_attestation_path=paths["freeze"],linux_statement_path=paths["linux"],packet_statement_path=paths["packet"],packet_payload_path=paths["payload"],receipt_path=paths["receipt"],receipt_sha256=sha256_bytes(receipt_raw),expected_identity=None,candidate_label="Q15",trusted_receipt_proof_path=proof_path,committed_review_path=committed_path,trusted_verifier_commit="e"*40,trusted_verifier_tree="f"*40)
   self.assertTrue(result["review_evidence_eligible"])
   for field,value in (("producer_head_sha","0"*40),("workflow_file","other.yml"),("workflow_identity","other-job"),("artifact_id","4"),("receipt_sha256","0"*64),("verifier_commit","0"*40)):
    bad=dict(proof);bad[field]=value; bad_path=root/"bad-proof.json";bad_path.write_text(json.dumps(bad),encoding="utf-8")
    with self.assertRaises(ValueError):
     ingest(review_path=committed_path,freeze_attestation_path=paths["freeze"],linux_statement_path=paths["linux"],packet_statement_path=paths["packet"],packet_payload_path=paths["payload"],receipt_path=paths["receipt"],receipt_sha256=sha256_bytes(receipt_raw),expected_identity=None,candidate_label="Q15",trusted_receipt_proof_path=bad_path,committed_review_path=committed_path,trusted_verifier_commit="e"*40,trusted_verifier_tree="f"*40)
   v1=root/"v1-proof.json";v1.write_text(json.dumps({**proof,"schema":"r8-trusted-receipt-proof/v1"}),encoding="utf-8")
   with self.assertRaises(ValueError):
    ingest(review_path=committed_path,freeze_attestation_path=paths["freeze"],linux_statement_path=paths["linux"],packet_statement_path=paths["packet"],packet_payload_path=paths["payload"],receipt_path=paths["receipt"],receipt_sha256=sha256_bytes(receipt_raw),expected_identity=None,candidate_label="Q15",trusted_receipt_proof_path=v1,committed_review_path=committed_path,trusted_verifier_commit="e"*40,trusted_verifier_tree="f"*40)
if __name__=="__main__":unittest.main()
