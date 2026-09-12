from __future__ import annotations
from copy import deepcopy
import os,tempfile,unittest
from integrated_governed_mvp import evaluate_governed_execution
from integrated_governed_mvp_execution_gateway import canonical_hash
from integrated_governed_mvp_v24_execution_gateway import V24ExecutionGateway

class V24GatewayIntegrationTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.db=os.path.join(self.tmp.name,"v24.sqlite3");self.calls=0
  self.route={"provider":"groq","model":"model-a","sku":"sku-a","deployment_path":"api-a","qualification_ref":"q-1","qualification_epoch":7}
  self.registry={**self.route,"qualification_expires_epoch":100,"eligible":True,"revoked":False}
  self.cap={"capability_id":"cap-1","project_id":"p-1","task_id":"t-1","subject_id":"worker-1","issued_epoch":3,"expires_at":"2030-01-01T00:00:00Z","allowed_actions":["WRITE"],"artifact_classes":["CODE"],"revoked":False}
  self.req={"capability_id":"cap-1","project_id":"p-1","task_id":"t-1","subject_id":"worker-1","issued_epoch":3,"action":"WRITE","artifact_classes":["CODE"]}
  self.model={"evidence_eligible":True,"authorized_scope":["CODE"],"changed_artifacts":["CODE"],"review_requested":False};self.review={"state":"CLEAR","evidence_refs":["ev-1"]};self.art={"artifact_id":"src/example.py","artifact_class":"CODE","revision":"sha-a"}
 def tearDown(self):self.tmp.cleanup()
 def worker(self,e):self.calls+=1;return {"status":"SUCCESS","effect_request_hash":canonical_hash(e)}
 def upstream(self):
  d=evaluate_governed_execution(route=self.route,registry_entry=self.registry,normalized_model_result=self.model,capability=self.cap,execution_request=self.req,review_gate=self.review,now_epoch=10,now_iso="2026-09-07T00:00:00Z")
  return {"decision":d,"decision_hash":canonical_hash(d),"route":deepcopy(self.route),"registry_entry":deepcopy(self.registry),"normalized_model_result":deepcopy(self.model),"capability":deepcopy(self.cap),"execution_request":deepcopy(self.req),"review_gate":deepcopy(self.review),"decision_now_epoch":10,"decision_now_iso":"2026-09-07T00:00:00Z","artifact_binding":deepcopy(self.art)}
 def ctx(self):
  q={k:"QUALIFIED" for k in ("normative_catalog_state","authority_universe_state","effective_control_state","completeness_state","endpoint_precedence_state","admission_state","witness_state","aggregate_budget_state","generation_migration_state")}
  return {**q,"governance_generation_id":"GEN-V24","decision_generation_id":"GEN-V24","current_admission_ledger_digest":"A"*64,"decision_admission_ledger_digest":"A"*64,"current_completeness_ledger_digest":"C"*64,"decision_completeness_ledger_digest":"C"*64,"material_discovery_pending":False,"sink_id":"SINK-EXEC","guarded_writer_id":"EXECUTION-GATEWAY","decision_digest":"D"*64,"transition_digest":"T"*64,"sink_set_digest":"S"*64,"pre_apply_state_digest":"P"*64,"expected_post_apply_state_digest":"N"*64,"admission_perimeter_record":{"state":"CURRENT","generation_id":"GEN-V24","sink_id":"SINK-EXEC","admitted_writer_ids":["EXECUTION-GATEWAY"],"enforcement_configuration_digest":"E"*64,"independent_observation_state":"QUALIFIED"}}
 def kwargs(self,key="idem-1"):
  return {"upstream":self.upstream(),"current_registry_entry":deepcopy(self.registry),"current_capability":deepcopy(self.cap),"execution_request":deepcopy(self.req),"current_artifact_binding":deepcopy(self.art),"idempotency_key":key,"now_epoch":11,"now_iso":"2026-09-07T00:01:00Z"}
 def test_v24_positive_executes_once_and_returns_application_record(self):
  g=V24ExecutionGateway(self.db,self.worker);r=g.execute(v24_apply_context=self.ctx(),**self.kwargs());self.assertEqual(r["state"],"EXECUTED");self.assertEqual(self.calls,1);self.assertEqual(r["v24_guard"]["state"],"V24_APPLY_READY");self.assertEqual(r["authority_application_record"]["decision_digest"],"D"*64)
 def test_unqualified_v24_prerequisite_blocks_before_gateway_effect(self):
  g=V24ExecutionGateway(self.db,self.worker);c=self.ctx();c["normative_catalog_state"]="PENDING";r=g.execute(v24_apply_context=c,**self.kwargs());self.assertEqual(r["state"],"V24_APPLY_BLOCKED");self.assertEqual(self.calls,0);self.assertEqual(g.effect_count(),0)
 def test_stale_ledger_blocks(self):
  g=V24ExecutionGateway(self.db,self.worker);c=self.ctx();c["current_admission_ledger_digest"]="OLD";r=g.execute(v24_apply_context=c,**self.kwargs());self.assertEqual(r["state"],"V24_APPLY_BLOCKED");self.assertEqual(self.calls,0)
 def test_unadmitted_writer_blocks(self):
  g=V24ExecutionGateway(self.db,self.worker);c=self.ctx();c["admission_perimeter_record"]["admitted_writer_ids"]=[];r=g.execute(v24_apply_context=c,**self.kwargs());self.assertEqual(r["state"],"V24_APPLY_BLOCKED");self.assertEqual(self.calls,0)
 def test_replay_preserves_exact_application_record_without_duplicate_effect(self):
  g=V24ExecutionGateway(self.db,self.worker);a=g.execute(v24_apply_context=self.ctx(),**self.kwargs());b=g.execute(v24_apply_context=self.ctx(),**self.kwargs());self.assertEqual(b["state"],"REPLAYED");self.assertEqual(a["authority_application_record"],b["authority_application_record"]);self.assertEqual(self.calls,1);self.assertEqual(g.effect_count(),1)
if __name__=="__main__":unittest.main()
