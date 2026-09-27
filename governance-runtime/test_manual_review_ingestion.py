import unittest
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
  receipt,_,_=fixtures();path=Path(".q18-fake-receipt.json");proof=Path(".q18-proof.json");path.write_bytes(canonical_bytes(receipt));proof.write_text(__import__("json").dumps({"schema":"r8-trusted-receipt-proof/v1","source":"GITHUB_ACTIONS_ARTIFACT_DOWNLOAD","receipt_sha256":sha256_bytes(path.read_bytes()),"repository":"a/b","run_id":"1","job_id":"2","workflow_file":"wf","workflow_identity":"job","artifact_id":"3","archive_digest":"sha256:"+"a"*64,"member":"governed-evidence-receipt.json","verifier_commit":"e"*40,"verifier_tree":"f"*40}))
  try:
   with patch("manual_review_ingestion.review_merge_evidence_eligible",return_value=False) as gate:
    result=ingest(review_path="r",freeze_attestation_path="f",linux_statement_path="l",packet_statement_path="p",packet_payload_path="b",receipt_path=path,receipt_sha256=sha256_bytes(path.read_bytes()),expected_identity={"candidate_commit":"0"*40,"candidate_tree":"0"*40},candidate_label="Q18",trusted_receipt_proof_path=proof,committed_review_path="c",trusted_verifier_commit="e"*40,trusted_verifier_tree="f"*40)
   gate.assert_called_once();self.assertFalse(result["review_evidence_eligible"]);self.assertEqual(gate.call_args.kwargs["expected_identity"]["candidate_commit"],receipt["candidate"]["commit"])
  finally:path.unlink(missing_ok=True);proof.unlink(missing_ok=True)
if __name__=="__main__":unittest.main()
