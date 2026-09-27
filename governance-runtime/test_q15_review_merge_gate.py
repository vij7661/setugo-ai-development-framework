from __future__ import annotations
import json, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from freeze_attestation import canonical_sha256
from q15_review_merge_gate import review_merge_evidence_eligible

C="a"*40; T="c"*40; B="b"*40
IDENTITY={"candidate_label":"Q15","baseline":B,"candidate_commit":C,"candidate_tree":T,"changed_file_count":53,"packet_run_job":("11","12"),"linux_run_job":("13","14")}
def statement(kind,run,job):
    v={"schema":"r8-candidate-execution-evidence/v1","kind":kind,"run_id":run,"job_id":job,"workflow_identity":"r8/q16","baseline_commit":B,"candidate_commit":C,"candidate_tree":T,"changed_file_count":53,"conclusion":"SUCCESS" if kind=="LINUX_VALIDATION" else "GENERATED","artifact_digest":"sha256:"+"e"*64}; v["statement_sha256"]=canonical_sha256(v); return v
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
class GateTests(unittest.TestCase):
    def run_gate(self,text,att=None,packet=None):
        goodp=statement("REVIEW_PACKET","11","12"); att=att or {"candidate_commit":C,"candidate_tree":T,"linux_validation_statement":statement("LINUX_VALIDATION","13","14"),"review_packet_statement":goodp}; packet=packet or goodp
        with tempfile.TemporaryDirectory() as td:
            r=Path(td); rp=r/"r"; ap=r/"a"; pp=r/"p"; rp.write_text(text,encoding="utf-8"); ap.write_text("{}",encoding="utf-8"); pp.write_text(json.dumps(packet),encoding="utf-8")
            with patch("q15_review_merge_gate.load_and_verify",return_value=att): return review_merge_evidence_eligible(review_path=rp,freeze_attestation_path=ap,review_packet_statement_path=pp,expected_identity=IDENTITY)
    def test_matching(self): self.assertTrue(self.run_gate(review()))
    def test_negative_cross_candidate_and_replay_fail(self):
        self.assertFalse(self.run_gate(review(disposition="CHANGES_REQUIRED"))); self.assertFalse(self.run_gate(review(commit="d"*40)))
        stale={"candidate_commit":C,"candidate_tree":T,"linux_validation_statement":statement("LINUX_VALIDATION","99","14"),"review_packet_statement":statement("REVIEW_PACKET","11","12")}
        self.assertFalse(self.run_gate(review(),att=stale)); self.assertFalse(self.run_gate(review(),packet=statement("REVIEW_PACKET","99","12")))
        cross=statement("REVIEW_PACKET","11","12"); cross["baseline_commit"]="9"*40; cross["statement_sha256"]=canonical_sha256({k:v for k,v in cross.items() if k!="statement_sha256"})
        cross_att={"candidate_commit":C,"candidate_tree":T,"linux_validation_statement":statement("LINUX_VALIDATION","13","14"),"review_packet_statement":cross}
        self.assertFalse(self.run_gate(review(),att=cross_att,packet=cross))
if __name__=="__main__": unittest.main()
