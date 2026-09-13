"""V24 I11 reference-only scientific sweep, clusters C-H.

Runs only REFERENCE_HARNESS / REFERENCE_MECHANISM_ONLY cases whose prerequisites
are available from the frozen I10 subject. External/hybrid/manual/static cases
remain NOT_EXECUTED_EXTERNAL_EVIDENCE_REQUIRED. No reviewer/model API calls.
"""
from __future__ import annotations
import copy, hashlib, json, os, platform, sys
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'governance-runtime'),str(ROOT/'testing/v24'),str(ROOT/'experiments/governed-platform/governance')]
from v24_effective_control import validate_effective_control_bundle
from v24_admission_application_witness import digest as i6_digest, validate_i6_bundle
from v24_aggregate_budget import dg as agg_digest, validate_aggregate_bundle
from v24_generation_migration import dg as mig_digest, validate_generation_migration
from v24_completeness_bootstrap import validate_completeness_bundle
from v24_apply_guard import evaluate_v24_apply
from v24_i11_case_specs_v8 import CASE_SPECS
from v24_i11_execution_harness_v1 import ExecutionScheduler, ResultLedger, adjudicate_negative
from v24_i11_harness_contract_v7 import (
 AuthorityEffectObservation, CaseRunBinding, ConjunctiveAssertionObservation,
 EnvironmentIdentity, GovernedEndpointObservation, InsufficientEvidenceEndpointCondition,
 HARNESS_VERSION, IE_TARGET_REASONS, expected_stdlib_fallback_digest,
 validate_binding, validate_environment,
)

PACKET='e62a2528d880e2dc0ad368dc7b030c1a5c2600b8fef7d7610af78b71bd5f5d0e'
BODY='3b442e55bec52aec24042d714d4064985eb85acf914afa5903d00d1a61b373ab'
BINDING='716a2a2917130c898cc4244d44cf0141e49dd83e'
HARNESS='6573767ae85d7ca0cfaa8b7bbafa826a7ba0c5cb'
DESIGN='db9e4b349fd26e128f4486878a4af64929000a7c'
IMPL='9836dc3ff233cca582f485434fc1c6494cf7eb05'; TREE='d68cbccdceebad88715c8b37ddfcd524fc16ce8a'
FRONTIER='e9a02e722edcd5e16b82abeeb37f7ab68c9295bf'
TARGETS={
 'control':(ROOT/'governance-runtime/v24_effective_control.py','b4e7dfac31f319a82c6af28fcfa14fdb559c28ba'),
 'i6':(ROOT/'governance-runtime/v24_admission_application_witness.py','af9d998f2cab4fe0d2b6fbb9d0feadbe9ae55278'),
 'agg':(ROOT/'governance-runtime/v24_aggregate_budget.py','60fad10caa3099123480cffdd531f02080e4c9f9'),
 'migration':(ROOT/'governance-runtime/v24_generation_migration.py','6a17903d5bb82858c9cabfb66af23ffcc2377fbc'),
 'bootstrap':(ROOT/'governance-runtime/v24_completeness_bootstrap.py','5cd17124e5809b963ce64d86ba0bb67801a17e73'),
 'apply':(ROOT/'experiments/governed-platform/governance/v24_apply_guard.py','6bc4dabc2a07c78fc657657f8430ded12e3c5a85'),
}

def canon(v:Any)->bytes:return json.dumps(v,sort_keys=True,separators=(',',':'),default=str).encode()
def sha(v:Any)->str:return hashlib.sha256(canon(v)).hexdigest()
def gitblob(d:bytes)->str:return hashlib.sha1(f'blob {len(d)}\0'.encode()+d).hexdigest()
def target_ids(names):
 blobs=[]; contents=[]
 for n in names:
  p,e=TARGETS[n]; d=p.read_bytes(); a=gitblob(d)
  if a!=e: raise RuntimeError(f'TARGET_BLOB_DRIFT:{n}:{a}:{e}')
  blobs.append(a); contents.append(hashlib.sha256(d).hexdigest())
 return tuple(blobs),tuple(contents)
def environment():
 py=f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}'
 osr=Path('/etc/os-release').read_bytes(); uname='|'.join(platform.uname()).encode()
 e=EnvironmentIdentity(py,hashlib.sha256(osr).hexdigest(),hashlib.sha256(uname).hexdigest(),expected_stdlib_fallback_digest(py),'STDLIB_ONLY_PIP_UNAVAILABLE',os.environ.get('TZ',''),os.environ.get('PYTHONHASHSEED',''),24011,'FROZEN_LOGICAL_CLOCK',(),0)
 p=validate_environment(e,exact_python_version=py)
 if p: raise RuntimeError('ENVIRONMENT_INVALID:'+','.join(p))
 return e,sha(asdict(e))
def bind(cid,fixture_digest,env_digest,names,execution_sha):
 blobs,contents=target_ids(names); token=hashlib.sha256(f'{cid}|{execution_sha}|{fixture_digest}'.encode()).hexdigest()[:16]
 b=CaseRunBinding(cid,f'{cid}:{token}',PACKET,BODY,BINDING,HARNESS,HARNESS_VERSION,DESIGN,IMPL,TREE,'V24',blobs,contents,fixture_digest,env_digest,'RUNNING')
 p=validate_binding(b,packet_sha256=PACKET,plan_body_sha256=BODY,plan_binding_blob_sha=BINDING,harness_blob_sha=HARNESS)
 if p: raise RuntimeError(f'BINDING_INVALID:{cid}:'+','.join(p))
 return b
def endpoint(result): return GovernedEndpointObservation(result.get('state'),'candidate',sha(result),tuple(result.get('problems',())))
def effect(profile):
 d=sha({'profile':profile,'effects':0}); return AuthorityEffectObservation(profile,d,d,0,0,'UNCHANGED','UNCHANGED')
def profile(pid):
 if pid=='O-CONTROL': return {'downstream_guarded_decision_before':0,'downstream_guarded_decision_after':0,'material_effect_before':0,'material_effect_after':0}
 if pid=='O-APPLICATION': return {'valid_applied_state':False,'sink_effect_before':0,'sink_effect_after':0}
 if pid=='O-AGG': return {'authority_transition_state':'BLOCKED','effect_before':0,'effect_after':0}
 if pid=='O-MIGRATION': return {'predecessor_read_accepted':False,'successor_activated':False,'material_effect_before':0,'material_effect_after':0}
 if pid=='O-HISTORY': return {'historical_decision_digest_before':'h','historical_decision_digest_after':'h','historical_result_before':'INSUFFICIENT_EVIDENCE','historical_result_after':'INSUFFICIENT_EVIDENCE','retroactively_upgraded':False,'material_effect_before':0,'material_effect_after':0}
 if pid=='O-APPLY': return {'worker_invocation_before':0,'worker_invocation_after':0,'application_record_count_before':0,'application_record_count_after':0,'material_effect_before':0,'material_effect_after':0}
 if pid=='O-BOOTSTRAP': return {'completeness_current_record_count_before':1,'completeness_current_record_count_after':1,'generation_activated':False,'material_effect_before':0,'material_effect_after':0}
 raise KeyError(pid)
def ie(cid,candidate_endpoint):
 return InsufficientEvidenceEndpointCondition(cid,True,True,True,True,False,candidate_endpoint=='INSUFFICIENT_EVIDENCE','a'*64,IE_TARGET_REASONS[cid])

GEN='GEN-V24'
def control_base():
 return {'governance_generation_id':GEN,'mandatory_source_classes':['DEPLOYMENT_ADMIN','CREDENTIAL_ADMIN'],'control_sources':[{'source_id':'SRC-DEPLOY','source_class':'DEPLOYMENT_ADMIN','control_domain_id':'D-DEPLOY','independent_derivation_evidence_digest':'a'*64,'generation_id':GEN},{'source_id':'SRC-CRED','source_class':'CREDENTIAL_ADMIN','control_domain_id':'D-CRED','independent_derivation_evidence_digest':'b'*64,'generation_id':GEN}],'required_relationship_queries':[{'subject_id':'SINK-A','source_id':'SRC-DEPLOY'},{'subject_id':'SINK-A','source_id':'SRC-CRED'}],'relationships':[{'relationship_id':'REL-1','subject_id':'SINK-A','source_id':'SRC-DEPLOY','status':'CONTROL_PRESENT','generation_id':GEN},{'relationship_id':'REL-2','subject_id':'SINK-A','source_id':'SRC-CRED','status':'NO_RELATIONSHIP_EVIDENCE_FOR_BOUND_SCOPE','negative_evidence_digest':'c'*64,'generation_id':GEN}],'effective_control_closure':{'control_edges':[['SRC-DEPLOY','SINK-A']],'root_threshold_capable_control_sets':[['SRC-DEPLOY'],['SRC-CRED']]},'capability_inventory':[{'capability_id':'CAP-A','owner_control_domain_id':'D-OWNER','generation_id':GEN}],'capability_attestations':[{'attestation_id':'ATT-A','capability_id':'CAP-A','independent_attestor_id':'ATTESTOR-X','attestor_control_domain_id':'D-ATTEST','measured_deployment_digest':'d'*64,'measured_configuration_digest':'e'*64,'state':'CURRENT','generation_id':GEN}],'deployment_observations':[{'observation_id':'OBS-A','capability_id':'CAP-A','deployment_digest':'d'*64,'configuration_digest':'e'*64,'generation_id':GEN}]}
def admission(aid,pre):
 r={'admission_id':aid,'generation_id':GEN,'universe_contract_digest':'u'*64,'semantic_class':'SINK','instance_id':aid,'qualification_evidence_digest':'q'*64,'policy_digest':'p'*64,'state':'CURRENT','predecessor_record_digest':pre}; r['record_digest']=i6_digest(r); return r
def i6_base():
 a1=admission('ADM-1','GENESIS'); a2=admission('ADM-2',a1['record_digest']); dec={'decision_id':'DEC-1','decision_digest':'d'*64,'generation_id':GEN,'admission_record_ids':['ADM-1','ADM-2'],'transition_digest':'t'*64,'sink_set_digest':'s'*64,'state':'APPLIED','self_activates_completeness_machinery':False}
 return {'governance_generation_id':GEN,'admission_records':[a1,a2],'kernel_decisions':[dec],'current_admission_ledger_digest':'L'*64,'current_completeness_ledger_digest':'C'*64,'application_records':[{'application_id':'APP-1','decision_id':'DEC-1','decision_digest':'d'*64,'transition_digest':'t'*64,'sink_set_digest':'s'*64,'pre_state_digest':'a'*64,'post_state_digest':'b'*64,'guarded_writer_id':'GW','atomic_fencing_result':'CAS_COMMITTED','admission_ledger_digest':'L'*64,'completeness_ledger_digest':'C'*64,'generation_id':GEN}],'root_threshold_capable_operational_domains':['D-ROOT'],'witness_policy':{'required_count':2,'ledger_operator_control_domain_id':'D-LEDGER'},'witnesses':[{'witness_id':'W1','control_domain_id':'D-ROOT','state':'CURRENT','generation_id':GEN},{'witness_id':'W2','control_domain_id':'D-EXT','state':'CURRENT','generation_id':GEN}],'ledger_anchor':{'witnessed_ledger_digest':'L'*64,'generation_id':GEN}}
def agg_base():
 dims=['beneficiary','object_lineage','power_class','resource_ancestry','sink_effect_class','policy_class','temporal_persistence']; return {'governance_generation_id':GEN,'independently_derived_mandatory_dimensions':dims[:],'active_policy_dimensions':dims[:],'authority_effects':[{'effect_id':'E1','generation_id':GEN,'state':'ACTIVE','still_effective':True,'aggregation_obligation_active':True,'cessation_proof_state':'NOT_APPLICABLE'}],'transactions':[{'transaction_id':'TX1','generation_id':GEN,'required_keys':['K1','K2'],'key_records':[{'key':'K1','transaction_id':'TX1','state':'COMMITTED','committed_identity':'CID'},{'key':'K2','transaction_id':'TX1','state':'COMMITTED','committed_identity':'CID'}],'reconciliation_outcome':'COMMIT_CONFIRMED_EXISTING','authority_transition_state':'SUCCESS'}]}
CUR='GEN-V24'; PREV='GEN-V23'
def migration_base():
 rec={'object_id':'O1','source_generation_id':PREV,'object_digest':'a'*64,'disposition':'MIGRATE','disposition_evidence_digest':'b'*64}; inv=[rec]
 return {'current_generation_id':CUR,'predecessor_generation_id':PREV,'independently_derived_predecessor_object_ids':['O1'],'migration_inventory':inv,'authority_objects':[{'object_id':'O1','generation_id':PREV,'migration_record_digest':mig_digest(rec)}],'cache_replica_reads':[{'read_id':'R1','object_generation_id':PREV,'generation_guard_checked':True,'qualifying_disposition_checked':True,'accepted':True}],'generation_transition_records':[{'transition_id':'T1','from_generation_id':PREV,'to_generation_id':CUR,'migration_inventory_digest':mig_digest(inv),'state':'COMMITTED'}],'historical_decisions':[{'decision_id':'D1','original_result':'INSUFFICIENT_EVIDENCE','later_invalidity_proved':True,'current_recorded_result':'INSUFFICIENT_EVIDENCE','historical_invalidity_annotation_digest':'c'*64}]}
def apply_base():
 q={k:'QUALIFIED' for k in ('normative_catalog_state','authority_universe_state','effective_control_state','completeness_state','endpoint_precedence_state','admission_state','witness_state','aggregate_budget_state','generation_migration_state')}; q.update({'governance_generation_id':GEN,'decision_generation_id':GEN,'current_admission_ledger_digest':'A'*64,'decision_admission_ledger_digest':'A'*64,'current_completeness_ledger_digest':'C'*64,'decision_completeness_ledger_digest':'C'*64,'material_discovery_pending':False,'sink_id':'SINK','guarded_writer_id':'GW','decision_digest':'D'*64,'transition_digest':'T'*64,'sink_set_digest':'S'*64,'admission_perimeter_record':{'state':'CURRENT','generation_id':GEN,'sink_id':'SINK','admitted_writer_ids':['GW'],'enforcement_configuration_digest':'E'*64,'independent_observation_state':'QUALIFIED'}}); return q
def bootstrap_base():
 return {'governance_generation_id':GEN,'genesis_record':{'bootstrap_completeness_authority_set':{'members':[{'authority_id':'BA1','control_domain_id':'D-EXT','subject_classes':['AUTHORITY_UNIVERSE'],'ordinary_operational_root_only':False}],'threshold':1,'terminal_residual_trust_declared':True,'self_qualified_by_descendant_machinery':False,'generation_id':GEN,'source_contracts':[{'subject_class':'AUTHORITY_UNIVERSE','allowed_source_kinds':['OUT_OF_BAND']}]}},'completeness_records':[{'subject_id':'S1','generation_id':GEN,'authority_universe_digest':'U','independent_derivation_digest':'I','source_evidence_digest':'E','state':'CURRENT','derivation_authority_id':'BA1','subject_owner_id':'OWNER'}],'required_subjects':['S1'],'ordinary_iuda_lineage':[]}

def execute():
 env,ed=environment(); esh=os.environ.get('GITHUB_SHA','LOCAL'); sch=ExecutionScheduler(); ledger=ResultLedger(); cases={}
 baselines=[('control',validate_effective_control_bundle(control_base())),('i6',validate_i6_bundle(i6_base())),('agg',validate_aggregate_bundle(agg_base())),('migration',validate_generation_migration(migration_base())),('apply',evaluate_v24_apply(apply_base())),('bootstrap',validate_completeness_bundle(bootstrap_base()))]
 for name,r in baselines:
  if r.get('problems') or (name=='apply' and not r.get('allowed')): raise RuntimeError(f'BASELINE_INVALID:{name}:{r.get("problems")}')
 def store(x,details):
  x=replace(x,predecessor_record_digest=ledger.head); dg=ledger.append(x); cases[x.case_id]={'scientific_result':asdict(x),'record_digest':dg,**details}; return x
 def run(cid,fixture,validator,target,profile_id,fixture_branch=None,ie_cond=None,conj=None):
  sch.acquire(cid); r=validator(fixture); b=bind(cid,sha(fixture),ed,(target,),esh); ep=endpoint(r)
  x=adjudicate_negative(cid,b,ep,effect(profile_id),profile(profile_id),True,True,fixture_branch,ie_cond if ie_cond is not None else (ie(cid,ep.endpoint) if cid in IE_TARGET_REASONS else None),conj)
  store(x,{'candidate_state':r.get('state'),'candidate_problems':r.get('problems',[]),'candidate_allowed':r.get('allowed')}); sch.release(cid,x.result_state); return x
 def gate(ids,reason='Required external/manual evidence absent'):
  for cid in ids: cases[cid]={'case_status':'NOT_EXECUTED','result_state':'NOT_EXECUTABLE_EXTERNAL_EVIDENCE_REQUIRED','execution_class':CASE_SPECS[cid]['execution_class'],'required_evidence':CASE_SPECS[cid]['evidence_profile'],'reason':reason}

 # Cluster C reference negatives.
 f=control_base(); f['control_sources'].pop(); run('WDPC-432',f,validate_effective_control_bundle,'control','O-CONTROL')
 f=control_base(); f['deployment_observations'][0]['configuration_digest']='f'*64; run('WDPC-436',f,validate_effective_control_bundle,'control','O-CONTROL')
 f=control_base(); f['relationships'].pop(); run('WDPC-437',f,validate_effective_control_bundle,'control','O-CONTROL')
 f=control_base(); f['relationships'].pop(); run('WDPC-451',f,validate_effective_control_bundle,'control','O-CONTROL')
 f=control_base(); f['effective_control_closure']['root_threshold_capable_control_sets']=[]; run('WDPC-452',f,validate_effective_control_bundle,'control','O-CONTROL')
 f=control_base(); f['iuda_projection_sources']=[{'iuda':'I1','source_path':'SHARED'},{'iuda':'I2','source_path':'SHARED'}]; run('WDPC-475',f,validate_effective_control_bundle,'control','O-CONTROL')
 f=control_base(); f['capability_attestations'][0]['measurement_source']='DEPLOYMENT_SELF_REPORT_ONLY'; run('WDPC-476',f,validate_effective_control_bundle,'control','O-CONTROL')
 gate(['WDPC-443','WDPC-458','WDPC-466','WDPC-486','WDPC-489','WDPC-494'])
 cases['WDPC-462']={'case_status':'NOT_EXECUTED','result_state':'BLOCKED_BY_PRIOR_LOAD_BEARING_FAILURE','reason':'Same-mechanism negatives are non-PASS or externally unresolved.'}

 # Cluster D reference negatives.
 f=i6_base(); f['application_records']=[]; run('WDPC-440',f,validate_i6_bundle,'i6','O-APPLICATION')
 f=i6_base(); f['application_records'][0]['sink_set_digest']='x'*64; run('WDPC-456',f,validate_i6_bundle,'i6','O-APPLICATION')
 f=i6_base(); f['kernel_decisions'][0]['admission_record_ids'].append('ADM-MISSING'); run('WDPC-471',f,validate_i6_bundle,'i6','O-APPLICATION')
 gate(['WDPC-449','WDPC-460','WDPC-467','WDPC-472','WDPC-477','WDPC-484','WDPC-485'])
 cases['WDPC-470']={'case_status':'NOT_EXECUTED','result_state':'BLOCKED_BY_PRIOR_LOAD_BEARING_FAILURE','reason':'Same-mechanism negatives are non-PASS or externally unresolved.'}

 # Cluster E negatives.
 f=agg_base(); f['active_policy_dimensions'].remove('temporal_persistence'); run('WDPC-431',f,validate_aggregate_bundle,'agg','O-AGG')
 f=agg_base(); f['transactions'][0]['key_records'][1]['state']='UNKNOWN'; f['transactions'][0]['reconciliation_outcome']='INSUFFICIENT_EVIDENCE'; f['transactions'][0]['authority_transition_state']='BLOCKED'; run('WDPC-434',f,validate_aggregate_bundle,'agg','O-AGG')
 f=agg_base(); f['authority_effects'][0].update({'state':'EXPIRED','still_effective':True,'aggregation_obligation_active':False,'cessation_proof_state':'MISSING'}); run('WDPC-439',f,validate_aggregate_bundle,'agg','O-AGG')
 for cid in ('WDPC-461','WDPC-464'): cases[cid]={'case_status':'NOT_EXECUTED','result_state':'BLOCKED_BY_PRIOR_LOAD_BEARING_FAILURE','reason':'Cluster E negative prerequisite did not all PASS exact endpoints.'}

 # Cluster F negatives.
 f=migration_base(); f['independently_derived_predecessor_object_ids'].append('O2'); run('WDPC-435',f,validate_generation_migration,'migration','O-MIGRATION')
 f=migration_base(); f['cache_replica_reads'][0]['qualifying_disposition_checked']=False; run('WDPC-438',f,validate_generation_migration,'migration','O-MIGRATION')
 f=migration_base(); f['authority_objects'].append({'object_id':'O2','generation_id':PREV}); run('WDPC-455',f,validate_generation_migration,'migration','O-MIGRATION')
 cid='WDPC-457'; sch.acquire(cid); f=migration_base(); f['historical_decisions'][0]['current_recorded_result']='VALID'; r=validate_generation_migration(f); ep=endpoint(r); b=bind(cid,sha(f),ed,('migration',),esh); c=ConjunctiveAssertionObservation(ep,('HISTORICAL_RESULT_UNCHANGED',),(),()); x=adjudicate_negative(cid,b,ep,effect('O-HISTORY'),profile('O-HISTORY'),True,True,'NO_STRICTER_SOURCE_ENDPOINT_HISTORY_UNCHANGED',None,c); store(x,{'candidate_state':r['state'],'candidate_problems':r['problems']}); sch.release(cid,x.result_state)
 cases['WDPC-465']={'case_status':'NOT_EXECUTED','result_state':'BLOCKED_BY_PRIOR_LOAD_BEARING_FAILURE','reason':'Cluster F negative prerequisite did not all PASS exact endpoints.'}

 # Cluster G reference negatives.
 f=apply_base(); f['material_discovery_pending']=True; run('WDPC-445',f,evaluate_v24_apply,'apply','O-APPLY')
 f=apply_base(); f['current_completeness_ledger_digest']='X'*64; run('WDPC-479',f,evaluate_v24_apply,'apply','O-APPLY','BOUND_STATE_ONLY_CHANGE_AFTER_DECISION')
 f=apply_base(); f['completeness_state']='STALE'; run('WDPC-483',f,evaluate_v24_apply,'apply','O-APPLY','ADMITTED_INSTANCE_STALES_COMPLETENESS')
 gate(['WDPC-497','WDPC-498','WDPC-504','WDPC-505'])

 # Cluster H reference negatives.
 f=bootstrap_base(); f['completeness_records'][0]['derivation_authority_id']='OWNER'; run('WDPC-442',f,validate_completeness_bundle,'bootstrap','O-BOOTSTRAP')
 f=bootstrap_base(); f['completeness_records'][0]['storage_class']='PROCESS_MEMORY_ONLY'; run('WDPC-473',f,validate_completeness_bundle,'bootstrap','O-BOOTSTRAP')
 f=bootstrap_base(); f['genesis_record']['bootstrap_completeness_authority_set']['self_qualified_by_descendant_machinery']=True; run('WDPC-499',f,validate_completeness_bundle,'bootstrap','O-BOOTSTRAP','GENESIS_CIRCULARITY')
 f=bootstrap_base(); f['genesis_record']['bootstrap_completeness_authority_set']['source_contracts'][0]['allowed_source_kinds']=['CANDIDATE_SELF']; run('WDPC-501',f,validate_completeness_bundle,'bootstrap','O-BOOTSTRAP')
 f=bootstrap_base(); f['completeness_records'][0].update({'derivation_authority_id':'IUDA-X','ordinary_iuda_lineage_parent_id':None}); f['ordinary_iuda_lineage']=[{'authority_id':'IUDA-X','parent_authority_id':None}]; run('WDPC-502',f,validate_completeness_bundle,'bootstrap','O-BOOTSTRAP','ABSENT_IUDA_LINEAGE')
 gate(['WDPC-468','WDPC-474','WDPC-500','WDPC-503','WDPC-506'])

 executed=[c for c,v in cases.items() if 'scientific_result' in v]; passed=[c for c in executed if cases[c]['scientific_result']['result_state']=='PASS']; nonpass=[c for c in executed if c not in passed]
 return {'artifact':'V24_I11_REFERENCE_SWEEP_C_H','plan':'V8_REVIEWED','execution_sha':esh,'pre_scientific_frontier':FRONTIER,'design_sha':DESIGN,'implementation_sha':IMPL,'implementation_tree':TREE,'environment':asdict(env),'environment_digest':ed,'executed_case_ids':executed,'pass_case_ids':passed,'nonpass_executed_case_ids':nonpass,'cases':cases,'ledger_head_digest':ledger.head,'authority_effect':'NONE_EVIDENCE_ONLY'}

def main():
 r=execute(); p=Path('testing/v24/results/V24-I11-REFERENCE-SWEEP-C-H.json'); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(r,sort_keys=True,indent=2)+'\n'); print(json.dumps({k:r[k] for k in ('executed_case_ids','pass_case_ids','nonpass_executed_case_ids','ledger_head_digest')},sort_keys=True,indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
