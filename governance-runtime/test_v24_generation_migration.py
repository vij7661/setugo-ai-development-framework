from __future__ import annotations
import unittest
from v24_generation_migration import dg,validate_generation_migration
CUR="GEN-V24";PREV="GEN-V23"
def valid_bundle():
 rec={"object_id":"O1","source_generation_id":PREV,"object_digest":"a"*64,"disposition":"MIGRATE","disposition_evidence_digest":"b"*64}
 inv=[rec]
 return {"current_generation_id":CUR,"predecessor_generation_id":PREV,"independently_derived_predecessor_object_ids":["O1"],"predecessor_universe_derivation_digest":"d"*64,"migration_inventory":inv,"authority_objects":[{"object_id":"O1","generation_id":PREV,"migration_record_digest":dg(rec)}],"cache_replica_reads":[{"read_id":"R1","object_id":"O1","object_generation_id":PREV,"generation_guard_checked":True,"generation_guard_evidence_digest":"g"*64,"qualifying_disposition_checked":True,"qualifying_disposition_record_digest":dg(rec),"accepted":True}],"generation_transition_records":[{"transition_id":"T1","from_generation_id":PREV,"to_generation_id":CUR,"migration_inventory_digest":dg(inv),"state":"COMMITTED"}],"historical_decisions":[{"decision_id":"D1","original_result":"INSUFFICIENT_EVIDENCE","later_invalidity_proved":True,"current_recorded_result":"INSUFFICIENT_EVIDENCE","historical_invalidity_annotation_digest":"c"*64}]}
class MigrationTests(unittest.TestCase):
 def assertP(self,m,e):
  b=valid_bundle();m(b);r=validate_generation_migration(b);self.assertIn(e,r["problems"]);self.assertFalse(r["qualified"])
 def test_positive(self):
  r=validate_generation_migration(valid_bundle());self.assertEqual(r["state"],"GENERATION_MIGRATION_CONSTRUCTION_VALID");self.assertEqual(r["problems"],[]);self.assertFalse(r["qualified"])
 def test_predecessor_inventory_exact_set(self):self.assertP(lambda b:b["independently_derived_predecessor_object_ids"].append("O2"),"MIGRATION_INVENTORY_OBJECT_MISSING:O2")
 def test_object_requires_generation_tag(self):self.assertP(lambda b:b["authority_objects"][0].__setitem__("generation_id",None),"AUTHORITY_OBJECT_GENERATION_TAG_REQUIRED:O1")
 def test_predecessor_read_requires_disposition_binding(self):self.assertP(lambda b:b["authority_objects"][0].__setitem__("migration_record_digest","bad"),"PREDECESSOR_AUTHORITY_OBJECT_DISPOSITION_BINDING_INVALID:O1")
 def test_cache_generation_guard_required(self):self.assertP(lambda b:b["cache_replica_reads"][0].__setitem__("generation_guard_evidence_digest",None),"CACHE_GENERATION_GUARD_EVIDENCE_REQUIRED:R1")
 def test_cache_predecessor_disposition_required(self):self.assertP(lambda b:b["cache_replica_reads"][0].__setitem__("qualifying_disposition_record_digest","bad"),"CACHE_PREDECESSOR_DISPOSITION_EVIDENCE_REQUIRED:R1")
 def test_boolean_guard_label_without_evidence_rejected(self):
  def m(b):b["cache_replica_reads"][0]["generation_guard_checked"]=True;b["cache_replica_reads"][0]["generation_guard_evidence_digest"]=None
  self.assertP(m,"CACHE_GENERATION_GUARD_BOOLEAN_NOT_EVIDENCE:R1")
 def test_transition_inventory_exact_binding(self):self.assertP(lambda b:b["generation_transition_records"][0].__setitem__("migration_inventory_digest","bad"),"GENERATION_TRANSITION_INVENTORY_BINDING_INVALID:T1")
 def test_unknown_transition_requires_reconciliation(self):
  def m(b):b["generation_transition_records"][0]["state"]="OUTCOME_UNKNOWN"
  self.assertP(m,"GENERATION_TRANSITION_RECONCILIATION_REQUIRED:T1")
 def test_no_retro_validation(self):self.assertP(lambda b:b["historical_decisions"][0].__setitem__("current_recorded_result","VALID"),"RETRO_VALIDATION_FORBIDDEN:D1")
 def test_empty_predecessor_universe_rejected(self):self.assertP(lambda b:b.__setitem__("independently_derived_predecessor_object_ids",[]),"PREDECESSOR_OBJECT_UNIVERSE_REQUIRED")
 def test_predecessor_universe_derivation_evidence_required(self):self.assertP(lambda b:b.__setitem__("predecessor_universe_derivation_digest",None),"PREDECESSOR_UNIVERSE_DERIVATION_EVIDENCE_REQUIRED")
if __name__=="__main__":unittest.main()
