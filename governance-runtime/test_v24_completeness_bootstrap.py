from __future__ import annotations
import unittest
from v24_completeness_bootstrap import validate_completeness_bundle
GEN="GEN-V24"

def valid_bundle():
    return {
      "governance_generation_id":GEN,
      "genesis_record":{"bootstrap_completeness_authority_set":{
        "generation_id":GEN,"threshold":1,"terminal_residual_trust_declared":True,"self_qualified_by_descendant_machinery":False,
        "members":[{"authority_id":"BOOT-EXT","control_domain_id":"D-EXT","subject_classes":["AUTHORITY_UNIVERSE","CONTROL_SOURCE_REGISTRY"],"ordinary_operational_root_only":False}],
        "source_contracts":[
          {"subject_class":"AUTHORITY_UNIVERSE","allowed_source_kinds":["INDEPENDENT_RUNTIME_OBSERVATION","REPOSITORY_EVIDENCE"]},
          {"subject_class":"CONTROL_SOURCE_REGISTRY","allowed_source_kinds":["EXTERNAL_CONTROL_PLANE_EVIDENCE"]}
        ]}},
      "required_subjects":["SUB-U"],
      "completeness_records":[{"subject_id":"SUB-U","subject_owner_id":"OWNER-U","derivation_authority_id":"BOOT-EXT","generation_id":GEN,"state":"CURRENT","authority_universe_digest":"a"*64,"independent_derivation_digest":"b"*64,"source_evidence_digest":"c"*64}],
      "ordinary_iuda_lineage":[{"authority_id":"IUDA-2","parent_authority_id":"BOOT-EXT"}]
    }

class CompletenessBootstrapTests(unittest.TestCase):
    def assertProblem(self,mutate,expected):
        b=valid_bundle(); mutate(b); r=validate_completeness_bundle(b); self.assertIn(expected,r["problems"]); self.assertFalse(r["qualified"])
    def test_positive_construction_non_authoritative(self):
        r=validate_completeness_bundle(valid_bundle()); self.assertEqual(r["state"],"COMPLETENESS_BOOTSTRAP_CONSTRUCTION_VALID"); self.assertEqual(r["problems"],[]); self.assertFalse(r["qualified"])
    def test_bootstrap_cannot_self_prove(self): self.assertProblem(lambda b:b["genesis_record"]["bootstrap_completeness_authority_set"].__setitem__("self_qualified_by_descendant_machinery",True),"BOOTSTRAP_SELF_QUALIFICATION_FORBIDDEN")
    def test_residual_trust_must_be_explicit(self): self.assertProblem(lambda b:b["genesis_record"]["bootstrap_completeness_authority_set"].__setitem__("terminal_residual_trust_declared",False),"BOOTSTRAP_RESIDUAL_TRUST_DECLARATION_REQUIRED")
    def test_operational_root_not_relabelled_independent(self): self.assertProblem(lambda b:b["genesis_record"]["bootstrap_completeness_authority_set"]["members"][0].__setitem__("ordinary_operational_root_only",True),"BOOTSTRAP_OPERATIONAL_ROOT_RELABEL_FORBIDDEN:BOOT-EXT")
    def test_candidate_only_source_forbidden(self): self.assertProblem(lambda b:b["genesis_record"]["bootstrap_completeness_authority_set"]["source_contracts"][0].__setitem__("allowed_source_kinds",["CANDIDATE_SELF"]),"BOOTSTRAP_CANDIDATE_ONLY_SOURCE_FORBIDDEN:AUTHORITY_UNIVERSE")
    def test_source_contract_coverage_required(self): self.assertProblem(lambda b:b["genesis_record"]["bootstrap_completeness_authority_set"]["source_contracts"].pop(),"BOOTSTRAP_SOURCE_CONTRACT_COVERAGE_MISSING:CONTROL_SOURCE_REGISTRY")
    def test_subject_cannot_self_qualify(self): self.assertProblem(lambda b:b["completeness_records"][0].__setitem__("derivation_authority_id","OWNER-U"),"COMPLETENESS_SELF_QUALIFICATION_FORBIDDEN:SUB-U")
    def test_exactly_one_current_record(self): self.assertProblem(lambda b:b["completeness_records"][0].__setitem__("state","STALE"),"CURRENT_COMPLETENESS_RECORD_COUNT_INVALID:SUB-U:0")
    def test_lineage_must_root_in_bootstrap(self): self.assertProblem(lambda b:b["ordinary_iuda_lineage"][0].__setitem__("parent_authority_id",None),"IUDA_LINEAGE_NOT_ROOTED_IN_BOOTSTRAP:IUDA-2")

if __name__=="__main__": unittest.main()
