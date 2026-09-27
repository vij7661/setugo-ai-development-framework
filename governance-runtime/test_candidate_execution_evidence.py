import copy, unittest
from candidate_execution_evidence import build_statement
from freeze_attestation import verify_execution_statement
class Tests(unittest.TestCase):
    def test_candidate_bound_statement_and_replay_rejection(self):
        c="a"*40;t="b"*40
        v=build_statement(kind="LINUX_VALIDATION",run_id="1",job_id="2",workflow_identity="wf/job",baseline_commit="f"*40,candidate_commit=c,candidate_tree=t,changed_file_count=53,conclusion="SUCCESS",artifact_digest="sha256:"+"c"*64)
        self.assertTrue(verify_execution_statement(v,kind="LINUX_VALIDATION",commit=c,tree=t))
        for field,value in (("candidate_commit","d"*40),("candidate_tree","e"*40),("run_id","9")):
            bad=copy.deepcopy(v);bad[field]=value
            self.assertFalse(verify_execution_statement(bad,kind="LINUX_VALIDATION",commit=c,tree=t))
    def test_packet_statement_is_separately_candidate_bound(self):
        c="a"*40;t="b"*40
        v=build_statement(kind="REVIEW_PACKET",run_id="3",job_id="4",workflow_identity="packet/job",baseline_commit="f"*40,candidate_commit=c,candidate_tree=t,changed_file_count=53,conclusion="GENERATED",artifact_digest="sha256:"+"f"*64)
        self.assertTrue(verify_execution_statement(v,kind="REVIEW_PACKET",commit=c,tree=t))
        self.assertFalse(verify_execution_statement(v,kind="REVIEW_PACKET",commit="d"*40,tree=t))
if __name__=="__main__":unittest.main()
