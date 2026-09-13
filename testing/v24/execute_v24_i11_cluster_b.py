"""Execute V24 I11 Cluster B under reviewed V8 plan. No reviewer/model API calls."""
from __future__ import annotations
import copy, hashlib, json, os, platform, random, sys
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[2]; RUNTIME=ROOT/"governance-runtime"; TESTING=ROOT/"testing"/"v24"
sys.path[:0]=[str(RUNTIME),str(TESTING),str(ROOT/"experiments/governed-platform/governance")]
from v24_authority_universe import FUNCTIONAL_CATCH_ALL, validate_authority_universe_bundle
from v24_completeness_bootstrap import validate_completeness_bundle
from v24_apply_guard import evaluate_v24_apply
from v24_i11_execution_harness_v1 import ExecutionScheduler, ResultLedger, adjudicate_negative
from v24_i11_harness_contract_v7 import AuthorityEffectObservation, CaseRunBinding, EnvironmentIdentity, GovernedEndpointObservation, HARNESS_VERSION, expected_stdlib_fallback_digest, validate_binding, validate_environment

PACKET_SHA256="e62a2528d880e2dc0ad368dc7b030c1a5c2600b8fef7d7610af78b71bd5f5d0e"; PLAN_BODY_SHA256="3b442e55bec52aec24042d714d4064985eb85acf914afa5903d00d1a61b373ab"; PLAN_BINDING_BLOB="716a2a2917130c898cc4244d44cf0141e49dd83e"; HARNESS_V7_BLOB="6573767ae85d7ca0cfaa8b7bbafa826a7ba0c5cb"; DESIGN_SHA="db9e4b349fd26e128f4486878a4af64929000a7c"; IMPLEMENTATION_SHA="9836dc3ff233cca582f485434fc1c6494cf7eb05"; IMPLEMENTATION_TREE="d68cbccdceebad88715c8b37ddfcd524fc16ce8a"; PRE_SCIENCE_FRONTIER="e9a02e722edcd5e16b82abeeb37f7ab68c9295bf"
TARGETS={"universe":(ROOT/"governance-runtime/v24_authority_universe.py","216acc1168653f0e5d53479ec7c708935b8435ad"),"bootstrap":(ROOT/"governance-runtime/v24_completeness_bootstrap.py","5cd17124e5809b963ce64d86ba0bb67801a17e73"),"apply":(ROOT/"experiments/governed-platform/governance/v24_apply_guard.py","6bc4dabc2a07c78fc657657f8430ded12e3c5a85")}
def canon(v:Any):return json.dumps(v,sort_keys=True,separators=(",",":"),default=str).encode()
def sha(v:Any):return hashlib.sha256(canon(v)).hexdigest()
def gitblob(d:bytes):return hashlib.sha1(f"blob {len(d)}\0".encode()+d).hexdigest()
def targets(names):
 b=[]; s=[]
 for n in names:
  p,e=TARGETS[n]; d=p.read_bytes(); a=gitblob(d)
  if a!=e: raise RuntimeError(f"TARGET_DRIFT:{n}:{a}:{e}")
  b.append(a); s.append(hashlib.sha256(d).hexdigest())
 return tuple(b),tuple(s)
def env_identity():
 py=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"; osr=Path('/etc/os-release').read_bytes(); u='|'.join(platform.uname()).encode(); e=EnvironmentIdentity(py,hashlib.sha256(osr).hexdigest(),hashlib.sha256(u).hexdigest(),expected_stdlib_fallback_digest(py),'STDLIB_ONLY_PIP_UNAVAILABLE',os.environ.get('TZ',''),os.environ.get('PYTHONHASHSEED',''),24011,'FROZEN_LOGICAL_CLOCK',(),0); p=validate_environment(e,exact_python_version=py)
 if p: raise RuntimeError('ENV_INVALID:'+','.join(p))
 return e,sha(asdict(e))
def bind(cid,fd,ed,names,esh):
 bl,cs=targets(names); tok=hashlib.sha256(f"{cid}|{esh}|{fd}".encode()).hexdigest()[:16]; b=CaseRunBinding(cid,f"{cid}:{tok}",PACKET_SHA256,PLAN_BODY_SHA256,PLAN_BINDING_BLOB,HARNESS_V7_BLOB,HARNESS_VERSION,DESIGN_SHA,IMPLEMENTATION_SHA,IMPLEMENTATION_TREE,'V24',bl,cs,fd,ed,'RUNNING'); p=validate_binding(b,packet_sha256=PACKET_SHA256,plan_body_sha256=PLAN_BODY_SHA256,plan_binding_blob_sha=PLAN_BINDING_BLOB,harness_blob_sha=HARNESS_V7_BLOB)
 if p: raise RuntimeError(f"BIND_INVALID:{cid}:"+','.join(p))
 return b
def obs(r):return GovernedEndpointObservation(r.get('state'),'candidate',sha(r),tuple(r.get('problems',())))
def nofx(profile):
 d=sha({'p':profile,'n':0}); return AuthorityEffectObservation(profile,d,d,0,0,'UNCHANGED','UNCHANGED')
def universe_profile(reached=False):return {'unqualified_path_reached_sink':reached,'sink_effect_before':0,'sink_effect_after':0}
def bootstrap_profile():return {'completeness_current_record_count_before':1,'completeness_current_record_count_after':1,'generation_activated':False,'material_effect_before':0,'material_effect_after':0}

def universe_base():
 return {'governance_generation_id':'V24','authority_universe_contract':{'supported_authority_classes':[FUNCTIONAL_CATCH_ALL,'CLASS-A'],'unknown_class_behavior':'FAIL_CLOSED_AUTHORITY_ADMISSION_REQUIRED'},'authority_sinks':[{'sink_id':'S1','admitted_writer_ids':['W1'],'effect_classes':['AUTHORITY_WRITE'],'required_control_plane_ids':['CP1'],'unadmitted_writer_behavior':'DENY','generation_id':'V24'}],'consequential_effectors':[{'effector_id':'E1','sink_id':'S1','authority_classes':['CLASS-A'],'generation_id':'V24'}],'dependency_edges':[{'source_id':'W1','target_id':'S1','edge_type':'AUTHORITY_EFFECT','predicate_id':'P1','material':True}],'effect_paths':[{'path_id':'PATH1','source_component_id':'W1','sink_id':'S1','functional_effects':['MUTATE_AUTHORITY'],'admitted_authority_classes':['CLASS-A'],'control_plane_ids':['CP1'],'guard_ids':['G1'],'material_authority_effect':True,'runtime_observed':True,'generation_id':'V24'}],'control_planes':[{'control_plane_id':'CP1'}],'completeness_required_subjects':[{'subject_id':'SUB-SINK','subject_kind':'AUTHORITY_SINK_REGISTRY'},{'subject_id':'SUB-EFF','subject_kind':'CONSEQUENTIAL_EFFECTOR_REGISTRY'},{'subject_id':'SUB-GRAPH','subject_kind':'AUTHORITY_DEPENDENCY_GRAPH'},{'subject_id':'SUB-PATH','subject_kind':'AUTHORITY_EFFECT_PATH_SET'},{'subject_id':'SUB-CP','subject_kind':'CONTROL_PLANE_SET'}],'independent_universe_projection':{'source_kind':'INDEPENDENT_EXTERNAL','material_path_ids':['PATH1'],'sink_ids':['S1'],'control_plane_ids':['CP1'],'derivation_authority_id':'IUDA-1','source_evidence_digest':'evidence-1'}}
def apply_base():
 q={k:'QUALIFIED' for k in ('normative_catalog_state','authority_universe_state','effective_control_state','completeness_state','endpoint_precedence_state','admission_state','witness_state','aggregate_budget_state','generation_migration_state')}; q.update({'governance_generation_id':'V24','decision_generation_id':'V24','current_admission_ledger_digest':'A','decision_admission_ledger_digest':'A','current_completeness_ledger_digest':'C','decision_completeness_ledger_digest':'C','material_discovery_pending':False,'sink_id':'S1','guarded_writer_id':'W1','decision_digest':'D','transition_digest':'T','sink_set_digest':'S','admission_perimeter_record':{'state':'CURRENT','generation_id':'V24','sink_id':'S1','admitted_writer_ids':['W1'],'enforcement_configuration_digest':'E','independent_observation_state':'QUALIFIED'}}); return q
def bootstrap_base():
 return {'governance_generation_id':'V24','genesis_record':{'bootstrap_completeness_authority_set':{'members':[{'authority_id':'BA1','control_domain_id':'D1','subject_classes':['AUTHORITY_UNIVERSE'],'ordinary_operational_root_only':False}],'threshold':1,'terminal_residual_trust_declared':True,'self_qualified_by_descendant_machinery':False,'generation_id':'V24','source_contracts':[{'subject_class':'AUTHORITY_UNIVERSE','allowed_source_kinds':['OUT_OF_BAND']}]}},'completeness_records':[{'subject_id':'S1','generation_id':'V24','authority_universe_digest':'U','independent_derivation_digest':'I','source_evidence_digest':'E','state':'CURRENT','derivation_authority_id':'BA1','subject_owner_id':'OWNER'}],'required_subjects':['S1'],'ordinary_iuda_lineage':[]}

def execute():
 random.seed(24011); env,ed=env_identity(); esh=os.environ.get('GITHUB_SHA','LOCAL'); sch=ExecutionScheduler(); led=ResultLedger(); cases={}
 ub=universe_base(); base=validate_authority_universe_bundle(ub)
 if base['problems'] or base['state']!='AUTHORITY_UNIVERSE_CONSTRUCTION_VALID': raise RuntimeError('UNIVERSE_BASELINE_INVALID:'+','.join(base['problems']))
 bb=bootstrap_base(); bbase=validate_completeness_bundle(bb)
 if bbase['problems'] or bbase['state']!='COMPLETENESS_BOOTSTRAP_CONSTRUCTION_VALID': raise RuntimeError('BOOTSTRAP_BASELINE_INVALID:'+','.join(bbase['problems']))
 ab=apply_base(); abase=evaluate_v24_apply(ab)
 if not abase['allowed']: raise RuntimeError('APPLY_BASELINE_INVALID:'+','.join(abase['problems']))
 def store(x,details):
  x=replace(x,predecessor_record_digest=led.head); dg=led.append(x); cases[x.case_id]={'scientific_result':asdict(x),'record_digest':dg,**details}; return x
 def run_universe(cid,f):
  sch.acquire(cid); r=validate_authority_universe_bundle(f); b=bind(cid,sha(f),ed,('universe',),esh); x=adjudicate_negative(cid,b,obs(r),nofx('O-UNIVERSE'),universe_profile(False),True,True); store(x,{'candidate_state':r['state'],'candidate_problems':r['problems']}); sch.release(cid,x.result_state)

 # 444: second qualifying projection disagrees; candidate only consumes singular projection.
 f=copy.deepcopy(ub); f['independent_universe_projections']=[copy.deepcopy(f['independent_universe_projection']),{**copy.deepcopy(f['independent_universe_projection']),'material_path_ids':['PATH1','PATH-DIVERGENT'],'source_evidence_digest':'evidence-2'}]; run_universe('WDPC-444',f)
 # 448: remove independently required material edge.
 f=copy.deepcopy(ub); f['dependency_edges']=[]; run_universe('WDPC-448',f)
 # 450: new semantic authority class in current generation.
 f=copy.deepcopy(ub); f['effect_paths'][0]['admitted_authority_classes']=['NEW-SEMANTIC-CLASS']; run_universe('WDPC-450',f)
 # 459: candidate-self-derived projection.
 f=copy.deepcopy(ub); f['independent_universe_projection']['source_kind']='CANDIDATE_SELF_DERIVED'; run_universe('WDPC-459',f)
 # 487: nominally non-authority writer W2 has material sink path but is not admitted writer.
 f=copy.deepcopy(ub); f['effect_paths'].append({'path_id':'PATH2','source_component_id':'W2','nominal_class':'NON_AUTHORITY','sink_id':'S1','functional_effects':['MUTATE_AUTHORITY'],'admitted_authority_classes':[FUNCTIONAL_CATCH_ALL],'control_plane_ids':['CP1'],'guard_ids':['G2'],'material_authority_effect':True,'runtime_observed':True,'generation_id':'V24'}); f['dependency_edges'].append({'source_id':'W2','target_id':'S1','edge_type':'AUTHORITY_EFFECT','predicate_id':'P2','material':True}); f['independent_universe_projection']['material_path_ids'].append('PATH2'); run_universe('WDPC-487',f)
 # 488: independent effect-path audit exposes unregistered direct writer W2.
 f=copy.deepcopy(ub); f['effect_paths'].append({'path_id':'PATH2','source_component_id':'W2','sink_id':'S1','functional_effects':['DIRECT_AUTHORITY_WRITE'],'admitted_authority_classes':[FUNCTIONAL_CATCH_ALL],'control_plane_ids':['CP1'],'guard_ids':['G2'],'material_authority_effect':True,'runtime_observed':True,'generation_id':'V24'}); f['dependency_edges'].append({'source_id':'W2','target_id':'S1','edge_type':'AUTHORITY_EFFECT','predicate_id':'P2','material':True}); f['independent_universe_projection']['material_path_ids'].append('PATH2'); f['effect_path_conformance_source']='INDEPENDENT'; run_universe('WDPC-488',f)
 # 492: later omission-sensitive registry is not named in hard-coded completeness kinds.
 f=copy.deepcopy(ub); f['new_omission_sensitive_registry']=[{'member_id':'M1','material_authority_effect':True}]; run_universe('WDPC-492',f)

 # 441: universe admits the shape, apply guard blocks only generically on perimeter writer admission.
 cid='WDPC-441'; sch.acquire(cid); f=copy.deepcopy(ub); f['effect_paths'].append({'path_id':'PATH2','source_component_id':'W2','sink_id':'S1','functional_effects':['MUTATE_AUTHORITY'],'admitted_authority_classes':[FUNCTIONAL_CATCH_ALL],'control_plane_ids':['CP1'],'guard_ids':['G2'],'material_authority_effect':True,'runtime_observed':True,'generation_id':'V24'}); f['dependency_edges'].append({'source_id':'W2','target_id':'S1','edge_type':'AUTHORITY_EFFECT','predicate_id':'P2','material':True}); f['independent_universe_projection']['material_path_ids'].append('PATH2'); ur=validate_authority_universe_bundle(f); ac=apply_base(); ac['guarded_writer_id']='W2'; ar=evaluate_v24_apply(ac); b=bind(cid,sha({'universe':f,'apply':ac}),ed,('universe','apply'),esh); x=adjudicate_negative(cid,b,obs(ar),nofx('O-UNIVERSE'),universe_profile(False),True,True); store(x,{'universe_state':ur['state'],'universe_problems':ur['problems'],'candidate_state':ar['state'],'candidate_problems':ar['problems']}); sch.release(cid,x.result_state)
 # 478: suppressed discovery represented by extra runtime observation; apply guard ignores it and proceeds.
 cid='WDPC-478'; sch.acquire(cid); ac=apply_base(); ac['runtime_observed_unadmitted_material_path']={'source_component_id':'W2','sink_id':'S1'}; ac['material_discovery_pending']=False; ar=evaluate_v24_apply(ac); b=bind(cid,sha(ac),ed,('universe','apply'),esh); x=adjudicate_negative(cid,b,obs(ar),nofx('O-UNIVERSE'),universe_profile(bool(ar['allowed'])),True,True); store(x,{'candidate_state':ar['state'],'candidate_allowed':ar['allowed'],'candidate_problems':ar['problems']}); sch.release(cid,x.result_state)
 # 480: no UniverseDerivationDecisionRecord is present; current constructor does not model/require it.
 cid='WDPC-480'; sch.acquire(cid); f=copy.deepcopy(bb); r=validate_completeness_bundle(f); b=bind(cid,sha(f),ed,('bootstrap',),esh); x=adjudicate_negative(cid,b,obs(r),nofx('O-BOOTSTRAP'),bootstrap_profile(),True,True); store(x,{'candidate_state':r['state'],'candidate_problems':r['problems'],'universe_derivation_decision_record_present':False}); sch.release(cid,x.result_state)

 for cid in ('WDPC-493','WDPC-496'):
  try: sch.acquire(cid)
  except ValueError as exc: cases[cid]={'case_status':'NOT_EXECUTED','result_state':'BLOCKED_BY_PRIOR_LOAD_BEARING_FAILURE','reason':str(exc)}
  else: raise RuntimeError('POSITIVE_UNEXPECTEDLY_UNBLOCKED:'+cid)
 executed=[c for c,v in cases.items() if 'scientific_result' in v]; passed=[c for c in executed if cases[c]['scientific_result']['result_state']=='PASS']; red=[c for c in executed if c not in passed]
 return {'artifact':'V24_I11_CLUSTER_B_SCIENTIFIC_EXECUTION','plan':'V8_REVIEWED','execution_sha':esh,'pre_scientific_frontier':PRE_SCIENCE_FRONTIER,'design_sha':DESIGN_SHA,'implementation_sha':IMPLEMENTATION_SHA,'implementation_tree':IMPLEMENTATION_TREE,'environment':asdict(env),'environment_digest':ed,'cases':cases,'executed_case_ids':executed,'pass_case_ids':passed,'nonpass_executed_case_ids':red,'blocked_positive_case_ids':[c for c in ('WDPC-493','WDPC-496') if cases.get(c,{}).get('result_state')=='BLOCKED_BY_PRIOR_LOAD_BEARING_FAILURE'],'ledger_head_digest':led.head,'authority_effect':'NONE_EVIDENCE_ONLY'}

def main():
 r=execute(); p=Path('testing/v24/results/V24-I11-CLUSTER-B-SCIENTIFIC-RESULT.json'); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(r,sort_keys=True,indent=2)+'\n'); print(json.dumps({k:r[k] for k in ('executed_case_ids','pass_case_ids','nonpass_executed_case_ids','blocked_positive_case_ids','ledger_head_digest')},indent=2,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
