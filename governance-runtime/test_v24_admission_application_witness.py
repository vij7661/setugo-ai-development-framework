from __future__ import annotations
import unittest
from v24_admission_application_witness import digest, validate_i6_bundle
GEN="GEN-V24"

def adm(aid, predecessor):
    r={"admission_id":aid,"generation_id":GEN,"universe_contract_digest":"u"*64,"semantic_class":"SINK","instance_id":aid,"qualification_evidence_digest":"q"*64,"policy_digest":"p"*64,"state":"CURRENT","predecessor_record_digest":predecessor}
    r["record_digest"]=digest(r); return r

def witness(wid,domain):
    return {"witness_id":wid,"control_domain_id":domain,"state":"CURRENT","generation_id":GEN,"independence_evidence":{"witness_id":wid,"control_domain_id":domain,"generation_id":GEN,"evidence_digest":wid.lower()*32,"attestor_authority_id":"ATT-EXT","attestor_control_domain_id":"D-ATTEST","source_kind":"EXTERNAL_GOVERNANCE_EVIDENCE","candidate_self_derived":False}}

def valid_bundle():
    a1=adm("ADM-1","GENESIS"); a2=adm("ADM-2",a1["record_digest"])
    dec={"decision_id":"DEC-1","decision_digest":"d"*64,"generation_id":GEN,"admission_record_ids":["ADM-1","ADM-2"],"transition_digest":"t"*64,"sink_set_digest":"s"*64,"state":"APPLIED","self_activates_completeness_machinery":False}
    policy={"required_count":2,"ledger_operator_control_domain_id":"D-LEDGER"}; roots=["D-ROOT"]
    return {"governance_generation_id":GEN,"admission_records":[a1,a2],"kernel_decisions":[dec],"current_admission_ledger_digest":"L"*64,"current_completeness_ledger_digest":"C"*64,"application_records":[{"application_id":"APP-1","decision_id":"DEC-1","decision_digest":"d"*64,"transition_digest":"t"*64,"sink_set_digest":"s"*64,"pre_state_digest":"a"*64,"post_state_digest":"b"*64,"guarded_writer_id":"GW","atomic_fencing_result":"CAS_COMMITTED","admission_ledger_digest":"L"*64,"completeness_ledger_digest":"C"*64,"generation_id":GEN}],"root_threshold_capable_operational_domains":roots,"witness_policy":policy,"witness_policy_evidence":{"policy_digest":digest(policy),"source_kind":"EXTERNAL_GOVERNANCE_EVIDENCE","candidate_self_derived":False,"evidence_digest":"e"*64,"authority_id":"POLICY-AUTH","authority_control_domain_id":"D-POLICY"},"root_domain_inventory_evidence":{"root_domains_digest":digest(sorted(roots)),"source_kind":"INDEPENDENT_CONTROL_PLANE_EVIDENCE","candidate_self_derived":False,"evidence_digest":"r"*64,"authority_id":"ROOT-AUTH","authority_control_domain_id":"D-ROOT-AUTH"},"witnesses":[witness("W1","D-ROOT"),witness("W2","D-EXT")],"ledger_anchor":{"witnessed_ledger_digest":"L"*64,"generation_id":GEN}}

class I6Tests(unittest.TestCase):
    def assertProblem(self, mutate, expected):
        b=valid_bundle(); mutate(b); r=validate_i6_bundle(b); self.assertIn(expected,r["problems"]); self.assertFalse(r["qualified"])
    def test_positive_construction_non_authoritative(self):
        r=validate_i6_bundle(valid_bundle()); self.assertEqual(r["state"],"I6_CONSTRUCTION_VALID"); self.assertEqual(r["problems"],[]); self.assertFalse(r["qualified"])
    def test_empty_authority_sets_cannot_vacuously_pass(self):
        self.assertProblem(lambda b:b.__setitem__("admission_records",[]),"ADMISSION_RECORD_SET_EMPTY")
        self.assertProblem(lambda b:b.__setitem__("kernel_decisions",[]),"KERNEL_DECISION_SET_EMPTY")
        self.assertProblem(lambda b:b.__setitem__("application_records",[]),"APPLICATION_RECORD_SET_EMPTY")
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
    def test_witness_policy_requires_external_binding(self):
        self.assertProblem(lambda b:b.__setitem__("witness_policy_evidence",{}),"WITNESS_POLICY_DIGEST_MISMATCH")
    def test_root_inventory_requires_external_binding(self):
        self.assertProblem(lambda b:b["root_domain_inventory_evidence"].__setitem__("candidate_self_derived",True),"ROOT_DOMAIN_INVENTORY_CANDIDATE_SELF_DERIVATION_FORBIDDEN")
    def test_witness_name_alone_is_not_independence(self):
        self.assertProblem(lambda b:b["witnesses"][1].pop("independence_evidence"),"WITNESS_INDEPENDENCE_EVIDENCE_REQUIRED:W2")
    def test_witness_self_attestation_forbidden(self):
        self.assertProblem(lambda b:b["witnesses"][1]["independence_evidence"].__setitem__("attestor_control_domain_id","D-EXT"),"WITNESS_INDEPENDENCE_SELF_ATTESTATION_FORBIDDEN:W2")
    def test_witness_anchor_must_match_ledger(self):
        self.assertProblem(lambda b:b["ledger_anchor"].__setitem__("witnessed_ledger_digest","OLD"),"WITNESS_LEDGER_DIGEST_MISMATCH")

if __name__=="__main__": unittest.main()
