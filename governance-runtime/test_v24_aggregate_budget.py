from __future__ import annotations
import unittest
from v24_aggregate_budget import validate_aggregate_bundle
GEN="GEN-V24"
def valid_bundle():
 return {"governance_generation_id":GEN,"independently_derived_mandatory_dimensions":["beneficiary","object_lineage","power_class","resource_ancestry","sink_effect_class","policy_class","temporal_persistence"],"active_policy_dimensions":["beneficiary","object_lineage","power_class","resource_ancestry","sink_effect_class","policy_class","temporal_persistence"],"authority_effects":[{"effect_id":"E1","generation_id":GEN,"state":"ACTIVE","still_effective":True,"aggregation_obligation_active":True,"cessation_proof_state":"NOT_APPLICABLE"}],"transactions":[{"transaction_id":"TX1","generation_id":GEN,"required_keys":["K1","K2"],"key_records":[{"key":"K1","transaction_id":"TX1","state":"COMMITTED","committed_identity":"CID"},{"key":"K2","transaction_id":"TX1","state":"COMMITTED","committed_identity":"CID"}],"reconciliation_outcome":"COMMIT_CONFIRMED_EXISTING","authority_transition_state":"SUCCESS"}]}
class AggTests(unittest.TestCase):
 def assertP(self,m,e):
  b=valid_bundle();m(b);r=validate_aggregate_bundle(b);self.assertIn(e,r["problems"]);self.assertFalse(r["qualified"])
 def test_positive(self):
  r=validate_aggregate_bundle(valid_bundle());self.assertEqual(r["state"],"AGGREGATE_BUDGET_CONSTRUCTION_VALID");self.assertEqual(r["problems"],[]);self.assertFalse(r["qualified"])
 def test_dimension_omission(self):self.assertP(lambda b:b["active_policy_dimensions"].remove("temporal_persistence"),"AGGREGATION_DIMENSION_MISSING:temporal_persistence")
 def test_slow_roll_expiry_forbidden(self):
  def m(b):b["authority_effects"][0].update({"state":"EXPIRED","still_effective":True,"aggregation_obligation_active":False,"cessation_proof_state":"MISSING"})
  self.assertP(m,"AUTHORITY_EFFECT_ARBITRARY_EXPIRY_FORBIDDEN:E1")
 def test_persistent_effect_remains_aggregated(self):self.assertP(lambda b:b["authority_effects"][0].__setitem__("aggregation_obligation_active",False),"PERSISTENT_EFFECT_AGGREGATION_REQUIRED:E1")
 def test_partial_key_set_blocks(self):self.assertP(lambda b:b["transactions"][0]["key_records"].pop(),"AGGREGATE_KEY_SET_INCOMPLETE:TX1")
 def test_conflicting_commits(self):
  def m(b):b["transactions"][0]["key_records"][1]["committed_identity"]="OTHER";b["transactions"][0]["reconciliation_outcome"]="RECONCILIATION_CONFLICT";b["transactions"][0]["authority_transition_state"]="BLOCKED"
  b=valid_bundle();m(b);r=validate_aggregate_bundle(b);self.assertEqual(r["problems"],[])
 def test_unresolved_cannot_success(self):
  def m(b):b["transactions"][0]["key_records"][1]["state"]="UNKNOWN";b["transactions"][0]["reconciliation_outcome"]="INSUFFICIENT_EVIDENCE"
  self.assertP(m,"AGGREGATE_UNRESOLVED_CANNOT_SUCCEED:TX1")
 def test_transaction_id_shared_across_keys(self):self.assertP(lambda b:b["transactions"][0]["key_records"][1].__setitem__("transaction_id","TX2"),"AGGREGATE_TRANSACTION_ID_MISMATCH:TX1")
if __name__=="__main__":unittest.main()
