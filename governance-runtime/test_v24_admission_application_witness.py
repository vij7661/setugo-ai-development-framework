from __future__ import annotations
import unittest
from v24_admission_application_witness import digest, validate_i6_bundle
GEN="GEN-V24"

def adm(aid, predecessor):
    r={"admission_id":aid,"generation_id":GEN,"universe_contract_digest":"u"*64,"semantic_class":"SINK","instance_id":aid,"qualification_evidence_digest":"q"*64,"policy_digest":"p"*64,"state":"CURRENT","predecessor_record_digest":predecessor}
    r["record_digest"]=digest(r); return r

def valid_bundle():
    a1=adm("ADM-1","GENESIS"); a2=adm("ADM-2",a1["record_digest"])
    dec={"decision_id":"DEC-1","decision_digest":"d"*64,"generation_id":GEN,"admission_record_ids":["ADM-1","ADM-2"],"transition_digest":"t"*64,"sink_set_digest":"s"*64,"state":"APPLIED","self_activates_completeness_machinery":False}
    return {"governance_generation_id":GEN,"admission_records":[a1,a2],"kernel_decisions":[dec],"current_admission_ledger_digest":"L"*64,"current_completeness_ledger_digest":"C"*64,"application_records":[{"application_id":"APP-1","decision_id":"DEC-1","decision_digest":"d"*64,"transition_digest":"t"*64,"sink_set_digest":"s"*64,"pre_state_digest":"a"*64,"post_state_digest":"b"*64,"guarded_writer_id":"GW","atomic_fencing_result":"CAS_COMMITTED","admission_ledger_digest":"L"*64,"completeness_ledger_digest":"C"*64,"generation_id":GEN}],"root_threshold_capable_operational_domains":["D-ROOT"],"witness_policy":{"required_count":2,"ledger_operator_control_domain_id":"D-LEDGER"},"witnesses":[{"witness_id":"W1","control_domain_id":"D-ROOT","state":"CURRENT","generation_id":GEN},{"witness_id":"W2","control_domain_id":"D-EXT","state":"CURRENT","generation_id":GEN}],"ledger_anchor":{"witnessed_ledger_digest":"L"*64,"generation_id":GEN}}

class I6Tests(unittest.TestCase):
    def assertProblem(self, mutate, expected):
        b=valid_bundle(); mutate(b); r=validate_i6_bundle(b); self.assertIn(expected,r["problems"]); self.assertFalse(r["qualified"])
    def test_positive_construction_non_authoritative(self):
        r=validate_i6_bundle(valid_bundle()); self.assertEqual(r["state"],"I6_CONSTRUCTION_VALID"); self.assertEqual(r["problems"],[]); self.assertFalse(r["qualified"])
    def test_admission_chain_tamper_blocks(self):
        self.assertProblem(lambda b:b["admission_records"][1].__setitem__("predecessor_record_digest","x"*64),"ADMISSION_PREDECESSOR_MISMATCH:ADM-2")
    def test_revoked_admission_blocks_bound_decision(self):
        self.assertProblem(lambda b:b["admission_records"][0].__setitem__("state","REVOKED"),"DECISION_ADMISSION_NOT_CURRENT:DEC-1:ADM-1")
    def test_completeness_self_activation_forbidden(self):
        self.assertProblem(lambda b:b["kernel_decisions"][0].__setitem__("self_activates_completeness_machinery",True),"DECISION_SELF_ACTIVATION_FORBIDDEN:DEC-1")
    def test_application_exact_decision_binding(self):
        self.assertProblem(lambda b:b["application_records"][0].__setitem__("transition_digest","x"*64),"APPLICATION_TRANSITION_MISMATCH:APP-1")
    def test_apply_revalidates_admission_ledger(self):
        self.assertProblem(lambda b:b["application_records"][0].__setitem__("admission_ledger_digest","OLD"),"APPLICATION_STALE_ADMISSION_LEDGER:APP-1")
    def test_apply_revalidates_completeness_ledger(self):
        self.assertProblem(lambda b:b["application_records"][0].__setitem__("completeness_ledger_digest","OLD"),"APPLICATION_STALE_COMPLETENESS_LEDGER:APP-1")
    def test_applied_decision_requires_one_application_record(self):
        self.assertProblem(lambda b:b.__setitem__("application_records",[]),"APPLIED_DECISION_APPLICATION_RECORD_COUNT_INVALID:DEC-1:0")
    def test_root_only_witnesses_fail(self):
        self.assertProblem(lambda b:b["witnesses"][1].__setitem__("control_domain_id","D-ROOT"),"WITNESS_INDEPENDENCE_INSUFFICIENT")
    def test_witness_anchor_must_match_ledger(self):
        self.assertProblem(lambda b:b["ledger_anchor"].__setitem__("witnessed_ledger_digest","OLD"),"WITNESS_LEDGER_DIGEST_MISMATCH")

if __name__=="__main__": unittest.main()
