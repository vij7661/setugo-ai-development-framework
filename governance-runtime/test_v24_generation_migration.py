from __future__ import annotations
import unittest
from v24_generation_migration import dg,validate_generation_migration
CUR="GEN-V24";PREV="GEN-V23"
def valid_bundle():
 rec={"object_id":"O1","source_generation_id":PREV,"object_digest":"a"*64,"disposition":"MIGRATE","disposition_evidence_digest":"b"*64};inv=[rec];uids=["O1"]
 return {"current_generation_id":CUR,"predecessor_generation_id":PREV,"independently_derived_predecessor_object_ids":uids,"predecessor_universe_evidence":{"object_ids":uids,"object_set_digest":dg(sorted(uids)),"predecessor_generation_id":PREV,"source_kind":"INDEPENDENT_REPOSITORY_DERIVATION","source_evidence_digest":"u"*64,"derivation_authority_id":"AUTH-EXT","candidate_self_derived":False},"migration_inventory":inv,"authority_objects":[{"object_id":"O1","generation_id":PREV,"migration_record_digest":dg(rec)}],"cache_replica_reads":[{"read_id":"R1","object_id":"O1","object_generation_id":PREV,"generation_guard_checked":True,"qualifying_disposition_checked":True,"generation_guard_evidence":{"read_id":"R1","object_id":"O1","object_generation_id":PREV,"current_generation_id":CUR,"result":"PASS","evidence_digest":"g"*64,"candidate_self_derived":False},"qualifying_disposition_evidence":{"read_id":"R1","object_id":"O1","migration_record_digest":dg(rec),"disposition":"MIGRATE","result":"QUALIFIED","evidence_digest":"q"*64,"candidate_self_derived":False},"accepted":True}],"generation_transition_records":[{"transition_id":"T1","from_generation_id":PREV,"to_generation_id":CUR,"migration_inventory_digest":dg(inv),"predecessor_universe_digest":dg(sorted(uids)),"state":"COMMITTED"}],"historical_decisions":[{"decision_id":"D1","original_result":"INSUFFICIENT_EVIDENCE","later_invalidity_proved":True,"current_recorded_result":"INSUFFICIENT_EVIDENCE","historical_invalidity_annotation_digest":"c"*64}]}
class MigrationTests(unittest.TestCase):
 def assertP(self,m,e):
  b=valid_bundle();m(b);r=validate_generation_migration(b);self.assertIn(e,r["problems"]);self.assertFalse(r["qualified"])
 def test_positive(self):
  r=validate_generation_migration(valid_bundle());self.assertEqual(r["state"],"GENERATION_MIGRATION_CONSTRUCTION_VALID");self.assertEqual(r["problems"],[]);self.assertFalse(r["qualified"])
 def test_predecessor_inventory_exact_set(self):self.assertP(lambda b:b["independently_derived_predecessor_object_ids"].append("O2"),"MIGRATION_INVENTORY_OBJECT_MISSING:O2")
 def test_predecessor_universe_cannot_be_empty(self):
  def m(b):
   b["independently_derived_predecessor_object_ids"]=[];b["migration_inventory"]=[];b["authority_objects"]=[];b["generation_transition_records"]=[];b["predecessor_universe_evidence"].update({"object_ids":[],"object_set_digest":dg([])})
  self.assertP(m,"PREDECESSOR_OBJECT_UNIVERSE_EMPTY")
 def test_predecessor_universe_must_be_independently_bound(self):self.assertP(lambda b:b["predecessor_universe_evidence"].__setitem__("candidate_self_derived",True),"PREDECESSOR_UNIVERSE_SELF_DERIVED_FORBIDDEN")
 def test_object_requires_generation_tag(self):self.assertP(lambda b:b["authority_objects"][0].__setitem__("generation_id",None),"AUTHORITY_OBJECT_GENERATION_TAG_REQUIRED:O1")
 def test_predecessor_read_requires_disposition_binding(self):self.assertP(lambda b:b["authority_objects"][0].__setitem__("migration_record_digest","bad"),"PREDECESSOR_AUTHORITY_OBJECT_DISPOSITION_BINDING_INVALID:O1")
 def test_cache_generation_guard_requires_evidence(self):self.assertP(lambda b:b["cache_replica_reads"][0].pop("generation_guard_evidence"),"CACHE_GENERATION_GUARD_EVIDENCE_REQUIRED:R1")
 def test_cache_boolean_cannot_substitute_for_generation_evidence(self):
  def m(b):
   b["cache_replica_reads"][0]["generation_guard_checked"]=True;b["cache_replica_reads"][0].pop("generation_guard_evidence")
  self.assertP(m,"CACHE_GENERATION_GUARD_EVIDENCE_REQUIRED:R1")
 def test_cache_predecessor_disposition_requires_evidence(self):self.assertP(lambda b:b["cache_replica_reads"][0].pop("qualifying_disposition_evidence"),"CACHE_PREDECESSOR_DISPOSITION_EVIDENCE_REQUIRED:R1")
 def test_cache_disposition_evidence_must_bind_record(self):self.assertP(lambda b:b["cache_replica_reads"][0]["qualifying_disposition_evidence"].__setitem__("migration_record_digest","bad"),"CACHE_PREDECESSOR_DISPOSITION_EVIDENCE_INVALID:R1")
 def test_transition_inventory_exact_binding(self):self.assertP(lambda b:b["generation_transition_records"][0].__setitem__("migration_inventory_digest","bad"),"GENERATION_TRANSITION_INVENTORY_BINDING_INVALID:T1")
 def test_transition_universe_exact_binding(self):self.assertP(lambda b:b["generation_transition_records"][0].__setitem__("predecessor_universe_digest","bad"),"GENERATION_TRANSITION_UNIVERSE_BINDING_INVALID:T1")
 def test_unknown_transition_requires_reconciliation(self):
  def m(b):b["generation_transition_records"][0]["state"]="OUTCOME_UNKNOWN"
  self.assertP(m,"GENERATION_TRANSITION_RECONCILIATION_REQUIRED:T1")
 def test_no_retro_validation(self):self.assertP(lambda b:b["historical_decisions"][0].__setitem__("current_recorded_result","VALID"),"RETRO_VALIDATION_FORBIDDEN:D1")
if __name__=="__main__":unittest.main()
