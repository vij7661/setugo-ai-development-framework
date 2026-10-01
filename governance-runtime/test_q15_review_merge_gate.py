from __future__ import annotations
import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from candidate_execution_evidence import build_statement
from governed_evidence_receipt import git_blob_sha1,sha256_bytes
from q15_review_merge_gate import review_merge_evidence_eligible

C="a"*40;T="c"*40;B="b"*40;REF="frozen/q15"
IDENTITY={"candidate_label":"Q15","baseline":B,"candidate_commit":C,"candidate_tree":T,"changed_file_count":53,"frozen_ref":REF,"packet_run_job":("11","12"),"linux_run_job":("13","14")}
def raw(v):return (json.dumps(v,sort_keys=True)+"\n").encode()
def statement(kind,run,job):return build_statement(kind=kind,run_id=run,job_id=job,workflow_identity="r8/q16",baseline_commit=B,candidate_commit=C,candidate_tree=T,changed_file_count=53,conclusion="SUCCESS" if kind=="LINUX_VALIDATION" else "GENERATED",artifact_digest="sha256:"+"e"*64)
def review(commit=C,disposition="BOUNDED_PASS"):
 return f"""A. OVERALL_DISPOSITION
{disposition}
B. EXACT_CANDIDATE_IDENTITY
- baseline: {B}
- frozen Q15 commit: {commit}
- frozen Q15 tree: {T}
- changed-file count from baseline: 53
- packet-generation run/job: 11 / 12
- exact Linux validation run/job: 13 / 14
C. CRITICAL_FINDINGS
NONE.
D. HIGH_FINDINGS
NONE.
E. MEDIUM_FINDINGS
NONE.
F. LOW_FINDINGS
NONE.
G. PERMANENT_INVARIANT_ASSESSMENT
held
H. API_AND_REVIEWER_DELIVERY_ASSESSMENT
held
I. REMEDIATION_PLAN
none
J. FINAL_GATE
- Frozen Q15 candidate eligible for bounded merge consideration: YES
- Broader Stage2 semantic authority granted: NO
- Runtime qualification granted: NO
- Release/deployment/production authority granted: NO
- Automatic six-slice cadence restoration: NO
- Fallback-to-3 remains ACTIVE
"""
def evidence(review_bytes):
 linux=statement("LINUX_VALIDATION","13","14");packet=statement("REVIEW_PACKET","11","12");payload=b"packet"
 freeze={"schema":"r8-external-freeze-attestation/v2","candidate_commit":C,"candidate_tree":T,"frozen_ref":REF,"linux_validation_statement":linux,"review_packet_statement":packet,"authority_effect":"NONE","fallback_to_3":"ACTIVE","six_slice_cadence":"NOT_RESTORED","attestation_state":"FROZEN_VERIFIED"}
 receipt={"schema":"r8-governed-evidence-receipt/v1","repository":"a/b","candidate":{"baseline":B,"commit":C,"tree":T,"changed_file_count":53,"frozen_ref":REF},"linux":{"run_id":"13","job_id":"14","workflow_identity":"r8/q16","artifact_id":"15","artifact_digest":"sha256:"+"1"*64,"statement_raw_sha256":"sha256:"+sha256_bytes(raw(linux)),"statement_internal_sha256":"sha256:"+linux["statement_sha256"]},"packet":{"run_id":"11","job_id":"12","workflow_identity":"r8/q16","artifact_id":"16","artifact_digest":"sha256:"+"2"*64,"payload_sha256":"sha256:"+sha256_bytes(payload),"statement_raw_sha256":"sha256:"+sha256_bytes(raw(packet)),"statement_internal_sha256":"sha256:"+packet["statement_sha256"]},"freeze_attestation":{"raw_sha256":sha256_bytes(raw(freeze)),"git_blob":git_blob_sha1(raw(freeze))},"independent_review":{"raw_sha256":sha256_bytes(review_bytes),"git_blob":git_blob_sha1(review_bytes)},"authority_effect":"NONE"}
 return linux,packet,payload,freeze,receipt
def write_files(root,review_bytes,linux,packet,payload,freeze,receipt):
 values={"review":review_bytes,"linux":raw(linux),"packet":raw(packet),"payload":payload,"freeze":raw(freeze),"receipt":raw(receipt)};paths={}
 for name,data in values.items():
  filename={"review":"review.txt","linux":"linux.json","packet":"packet.json","payload":"payload.bin","freeze":"freeze.json","receipt":"receipt.json"}[name]
  paths[name]=root/filename;paths[name].write_bytes(data)
 return paths,values
class GateTests(unittest.TestCase):
 def run_gate(self,text):
  rb=text.encode();linux,packet,payload,freeze,receipt=evidence(rb)
  with tempfile.TemporaryDirectory() as td:
   paths,values=write_files(Path(td),rb,linux,packet,payload,freeze,receipt)
   with patch("q15_review_merge_gate.load_and_verify",return_value=freeze):return review_merge_evidence_eligible(review_path=paths["review"],freeze_attestation_path=paths["freeze"],linux_statement_path=paths["linux"],review_packet_statement_path=paths["packet"],packet_payload_path=paths["payload"],governed_receipt_path=paths["receipt"],expected_receipt_sha256=sha256_bytes(values["receipt"]),expected_identity=IDENTITY)
 def test_matching_and_negative(self):
  self.assertTrue(self.run_gate(review()));self.assertFalse(self.run_gate(review(disposition="CHANGES_REQUIRED")));self.assertFalse(self.run_gate(review(commit="d"*40)))
 def test_forged_same_identity_bytes_fail_exact_receipt_binding(self):
  exact=review();linux,packet,payload,freeze,receipt=evidence(exact.encode());forged=(exact+"\nforged bytes").encode()
  with tempfile.TemporaryDirectory() as td:
   paths,values=write_files(Path(td),forged,linux,packet,payload,freeze,receipt)
   with patch("q15_review_merge_gate.load_and_verify",return_value=freeze):self.assertFalse(review_merge_evidence_eligible(review_path=paths["review"],freeze_attestation_path=paths["freeze"],linux_statement_path=paths["linux"],review_packet_statement_path=paths["packet"],packet_payload_path=paths["payload"],governed_receipt_path=paths["receipt"],expected_receipt_sha256=sha256_bytes(values["receipt"]),expected_identity=IDENTITY))
if __name__=="__main__":unittest.main()
