from __future__ import annotations
import unittest
from v24_completeness_bootstrap import _d,validate_completeness_bundle
GEN="GEN-V24"
def valid_bundle():
 required=["SUB-U"]
 return {"governance_generation_id":GEN,"genesis_record":{"bootstrap_completeness_authority_set":{"generation_id":GEN,"threshold":1,"terminal_residual_trust_declared":True,"self_qualified_by_descendant_machinery":False,"members":[{"authority_id":"BOOT-EXT","control_domain_id":"D-EXT","subject_classes":["AUTHORITY_UNIVERSE","CONTROL_SOURCE_REGISTRY"],"ordinary_operational_root_only":False}],"source_contracts":[{"subject_class":"AUTHORITY_UNIVERSE","allowed_source_kinds":["INDEPENDENT_RUNTIME_OBSERVATION","REPOSITORY_EVIDENCE"]},{"subject_class":"CONTROL_SOURCE_REGISTRY","allowed_source_kinds":["EXTERNAL_CONTROL_PLANE_EVIDENCE"]}]}},"required_subjects":required,"required_subject_universe_evidence":{"subject_ids":required,"subject_set_digest":_d(sorted(required)),"source_kind":"INDEPENDENT_GOVERNANCE_DERIVATION","source_evidence_digest":"e"*64,"derivation_authority_id":"BOOT-EXT","candidate_self_derived":False},"completeness_records":[{"subject_id":"SUB-U","subject_owner_id":"OWNER-U","derivation_authority_id":"BOOT-EXT","generation_id":GEN,"state":"CURRENT","authority_universe_digest":"a"*64,"independent_derivation_digest":"b"*64,"source_evidence_digest":"c"*64}],"ordinary_iuda_lineage":[{"authority_id":"IUDA-2","parent_authority_id":"BOOT-EXT"}]}
class CompletenessBootstrapTests(unittest.TestCase):
 def assertProblem(self,m,e):
  b=valid_bundle();m(b);r=validate_completeness_bundle(b);self.assertIn(e,r["problems"]);self.assertFalse(r["qualified"])
 def test_positive_construction_non_authoritative(self):
  r=validate_completeness_bundle(valid_bundle());self.assertEqual(r["state"],"COMPLETENESS_BOOTSTRAP_CONSTRUCTION_VALID");self.assertEqual(r["problems"],[]);self.assertFalse(r["qualified"])
 def test_bootstrap_cannot_self_prove(self):self.assertProblem(lambda b:b["genesis_record"]["bootstrap_completeness_authority_set"].__setitem__("self_qualified_by_descendant_machinery",True),"BOOTSTRAP_SELF_QUALIFICATION_FORBIDDEN")
 def test_residual_trust_must_be_explicit(self):self.assertProblem(lambda b:b["genesis_record"]["bootstrap_completeness_authority_set"].__setitem__("terminal_residual_trust_declared",False),"BOOTSTRAP_RESIDUAL_TRUST_DECLARATION_REQUIRED")
 def test_operational_root_not_relabelled_independent(self):self.assertProblem(lambda b:b["genesis_record"]["bootstrap_completeness_authority_set"]["members"][0].__setitem__("ordinary_operational_root_only",True),"BOOTSTRAP_OPERATIONAL_ROOT_RELABEL_FORBIDDEN:BOOT-EXT")
 def test_candidate_only_source_forbidden(self):self.assertProblem(lambda b:b["genesis_record"]["bootstrap_completeness_authority_set"]["source_contracts"][0].__setitem__("allowed_source_kinds",["CANDIDATE_SELF"]),"BOOTSTRAP_CANDIDATE_SELF_SOURCE_FORBIDDEN:AUTHORITY_UNIVERSE")
 def test_candidate_self_mixed_source_forbidden(self):self.assertProblem(lambda b:b["genesis_record"]["bootstrap_completeness_authority_set"]["source_contracts"][0].__setitem__("allowed_source_kinds",["CANDIDATE_SELF","REPOSITORY_EVIDENCE"]),"BOOTSTRAP_CANDIDATE_SELF_SOURCE_FORBIDDEN:AUTHORITY_UNIVERSE")
 def test_source_contract_coverage_required(self):self.assertProblem(lambda b:b["genesis_record"]["bootstrap_completeness_authority_set"]["source_contracts"].pop(),"BOOTSTRAP_SOURCE_CONTRACT_COVERAGE_MISSING:CONTROL_SOURCE_REGISTRY")
 def test_subject_cannot_self_qualify(self):self.assertProblem(lambda b:b["completeness_records"][0].__setitem__("derivation_authority_id","OWNER-U"),"COMPLETENESS_SELF_QUALIFICATION_FORBIDDEN:SUB-U")
 def test_exactly_one_current_record(self):self.assertProblem(lambda b:b["completeness_records"][0].__setitem__("state","STALE"),"CURRENT_COMPLETENESS_RECORD_COUNT_INVALID:SUB-U:0")
 def test_required_subjects_cannot_be_empty(self):
  def m(b):
   b["required_subjects"]=[];b["completeness_records"]=[];b["required_subject_universe_evidence"].update({"subject_ids":[],"subject_set_digest":_d([])})
  self.assertProblem(m,"REQUIRED_SUBJECT_SET_EMPTY")
 def test_required_subject_universe_must_match(self):self.assertProblem(lambda b:b["required_subject_universe_evidence"].__setitem__("subject_ids",["OTHER"]),"REQUIRED_SUBJECT_UNIVERSE_MISMATCH")
 def test_required_subject_universe_cannot_self_derive(self):self.assertProblem(lambda b:b["required_subject_universe_evidence"].__setitem__("candidate_self_derived",True),"REQUIRED_SUBJECT_UNIVERSE_SELF_DERIVED_FORBIDDEN")
 def test_underived_completeness_record_rejected(self):
  def m(b):
   x=dict(b["completeness_records"][0]);x["subject_id"]="EXTRA";b["completeness_records"].append(x)
  self.assertProblem(m,"COMPLETENESS_RECORD_UNDERIVED_SUBJECT:EXTRA")
 def test_lineage_must_root_in_bootstrap(self):self.assertProblem(lambda b:b["ordinary_iuda_lineage"][0].__setitem__("parent_authority_id",None),"IUDA_LINEAGE_NOT_ROOTED_IN_BOOTSTRAP:IUDA-2")
if __name__=="__main__":unittest.main()
