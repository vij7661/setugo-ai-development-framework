import unittest
from unittest.mock import patch
from manual_review_ingestion import ingest
IDENTITY={"candidate_commit":"a"*40,"candidate_tree":"b"*40}
class Tests(unittest.TestCase):
 def test_gate_is_load_bearing_and_output_grants_no_authority(self):
  with patch("manual_review_ingestion.review_merge_evidence_eligible",return_value=True) as gate:
   result=ingest(review_path="r",freeze_attestation_path="f",linux_statement_path="l",packet_statement_path="p",packet_payload_path="b",receipt_path="e",receipt_sha256="c"*64,expected_identity=IDENTITY)
  gate.assert_called_once();self.assertTrue(result["review_evidence_eligible"]);self.assertEqual(result["authority_effect"],"NONE");self.assertFalse(result["automatic_merge"]);self.assertFalse(any(result[k] for k in ("runtime_authority","release_authority","deployment_authority","production_authority")))
if __name__=="__main__":unittest.main()
