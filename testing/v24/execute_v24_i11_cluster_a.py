"""Execute V24 I11 Cluster A under the reviewed V8 falsification plan.

Executed: WDPC-433,446,447,453,454,463,481,482,490.
Gated: WDPC-491. Blocked: WDPC-469,495.
No reviewer/model API calls. AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY.
"""
from __future__ import annotations

import copy, hashlib, json, os, platform, random, sys, tempfile
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[2]
RUNTIME=ROOT/"governance-runtime"; TESTING=ROOT/"testing"/"v24"
sys.path[:0]=[str(RUNTIME),str(TESTING)]

from normative_control_catalog import git_blob_sha_bytes, validate_normative_catalog
from v24_endpoint_proof_compiler import compile_endpoint_precedence, compile_proof_view
from v24_i11_case_specs_v8 import CASE_SPECS
from v24_i11_execution_harness_v1 import ExecutionScheduler, ResultLedger, adjudicate_negative, adjudicate_positive
from v24_i11_harness_contract_v7 import (
    AuthorityEffectObservation, CaseRunBinding, EnvironmentIdentity,
    GovernedEndpointObservation, PositiveAssertionObservation, HARNESS_VERSION,
    expected_stdlib_fallback_digest, validate_binding, validate_environment,
)

AUTHORITY_EFFECT="NONE_EVIDENCE_ONLY"
PACKET_SHA256="e62a2528d880e2dc0ad368dc7b030c1a5c2600b8fef7d7610af78b71bd5f5d0e"
PLAN_BODY_SHA256="3b442e55bec52aec24042d714d4064985eb85acf914afa5903d00d1a61b373ab"
PLAN_BINDING_BLOB="716a2a2917130c898cc4244d44cf0141e49dd83e"
HARNESS_V7_BLOB="6573767ae85d7ca0cfaa8b7bbafa826a7ba0c5cb"
DESIGN_SHA="db9e4b349fd26e128f4486878a4af64929000a7c"
IMPLEMENTATION_SHA="9836dc3ff233cca582f485434fc1c6494cf7eb05"
IMPLEMENTATION_TREE="d68cbccdceebad88715c8b37ddfcd524fc16ce8a"
PRE_SCIENCE_FRONTIER="e9a02e722edcd5e16b82abeeb37f7ab68c9295bf"
ACCIDENTAL_NONSCIENTIFIC_COMMIT="3671d085c80435841426972cb66b0f024a829a75"
TARGETS={
 "endpoint":(ROOT/"governance-runtime/v24_endpoint_proof_compiler.py","1d43d650f6181c87bdd1fb18b5e017e505f9bde6"),
 "normative":(ROOT/"governance-runtime/normative_control_catalog.py","5fdbd561c93049222d55bbc81c2baf592ff906aa"),
 "continuity":(ROOT/"governance-runtime/v24_legacy_continuity_manifest.py","396d27cdaa2a0e1ac7d044bfeb31d4c306c1b902"),
 "preflight":(ROOT/"governance-runtime/v24_normative_bundle_preflight.py","ddf9090c3b69228a3c579e35dd11fd58de8e3c82"),
}

def canon(v:Any)->bytes:return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False,default=str).encode()
def sha(v:Any)->str:return hashlib.sha256(canon(v)).hexdigest()
def git_blob_sha(data:bytes)->str:return hashlib.sha1(f"blob {len(data)}\0".encode()+data).hexdigest()

def target_identity(names):
    blobs=[]; contents=[]
    for name in names:
        path,expected=TARGETS[name]; data=path.read_bytes(); actual=git_blob_sha(data)
        if actual!=expected: raise RuntimeError(f"TARGET_MODULE_GIT_BLOB_DRIFT:{name}:{actual}:{expected}")
        blobs.append(actual); contents.append(hashlib.sha256(data).hexdigest())
    return tuple(blobs),tuple(contents)

def environment():
    py=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    osr=Path("/etc/os-release").read_bytes() if Path("/etc/os-release").exists() else b""
    env=EnvironmentIdentity(py,hashlib.sha256(osr).hexdigest(),hashlib.sha256("|".join(platform.uname()).encode()).hexdigest(),expected_stdlib_fallback_digest(py),"STDLIB_ONLY_PIP_UNAVAILABLE",os.environ.get("TZ",""),os.environ.get("PYTHONHASHSEED",""),24011,"FROZEN_LOGICAL_CLOCK",(),0)
    p=validate_environment(env,exact_python_version=py)
    if p: raise RuntimeError("ENVIRONMENT_BINDING_INVALID:"+",".join(p))
    return env,sha(asdict(env))

def clause_sha(text,heading):
    lines=text.splitlines(keepends=True); start=next(i for i,l in enumerate(lines) if l.rstrip("\r\n")==heading)
    level=len(heading)-len(heading.lstrip("#")); end=len(lines)
    for i in range(start+1,len(lines)):
        s=lines[i].lstrip()
        if s.startswith("#"):
            n=len(s)-len(s.lstrip("#"))
            if n<=level and len(s)>n and s[n]==" ": end=i; break
    return hashlib.sha256(("".join(lines[start:end]).rstrip("\r\n")+"\n").encode()).hexdigest()

def descriptor(cid,path,blob,lid,heading,digest,preds=None):
    return {"control_id":cid,"normative_artifact_path":path,"normative_artifact_blob_sha":blob,"clause_locator":{"locator_id":lid,"heading":heading},"clause_sha256":digest,"inherited_predecessor_control_ids":preds or [],"authority_bearing_predicate_ids":[],"phase_severity_endpoint_mappings":[],"applicability_rules":[{"type":"ALWAYS"}],"required_proof_fields":[],"protected_mutation_strength_class":"ROOT_GOVERNED_NON_WEAKENING","effective_generation":"V24","effective_sequence":1}

def make_normative_fixture(root):
    (root/"standards").mkdir(parents=True,exist_ok=True)
    current="# Current\n\n## P24-16 — Catalog\n\nCurrent rule.\n\n## P24-17 — Endpoint\n\nEndpoint rule.\n"
    legacy="# Legacy\n\n## V5-S1 — Active legacy\n\nLegacy active rule.\n"
    (root/"standards/current.md").write_text(current); (root/"standards/legacy.md").write_text(legacy)
    cb=git_blob_sha_bytes(current.encode()); lb=git_blob_sha_bytes(legacy.encode())
    manifest={"schema_version":1,"governance_generation":"V24","artifacts":[
      {"path":"standards/current.md","blob_sha":cb,"classification":"AUTHORITATIVE_DESCRIPTOR_REQUIRED","required_clause_locators":[{"locator_id":"P24-16","heading":"## P24-16 — Catalog","clause_sha256":clause_sha(current,"## P24-16 — Catalog")},{"locator_id":"P24-17","heading":"## P24-17 — Endpoint","clause_sha256":clause_sha(current,"## P24-17 — Endpoint")}]},
      {"path":"standards/legacy.md","blob_sha":lb,"classification":"AUTHORITATIVE_DESCRIPTOR_REQUIRED","required_clause_locators":[{"locator_id":"V5-S1","heading":"## V5-S1 — Active legacy","clause_sha256":clause_sha(legacy,"## V5-S1 — Active legacy")}]}]}
    catalog={"schema_version":1,"governance_generation":"V24","descriptors":[descriptor("P24-16","standards/current.md",cb,"P24-16","## P24-16 — Catalog",clause_sha(current,"## P24-16 — Catalog")),descriptor("P24-17","standards/current.md",cb,"P24-17","## P24-17 — Endpoint",clause_sha(current,"## P24-17 — Endpoint")),descriptor("INHERITED-V5-S1","standards/legacy.md",lb,"V5-S1","## V5-S1 — Active legacy",clause_sha(legacy,"## V5-S1 — Active legacy"),["V5-S1"])]}
    lq={"schema_version":1,"governance_generation":"V24","legacy_clause_inventory":[{"artifact_path":"standards/legacy.md","locator_id":"V5-S1"}],"records":[{"artifact_path":"standards/legacy.md","locator_id":"V5-S1","status":"ACTIVE_MAPPED","target_control_id":"INHERITED-V5-S1"}]}
    baseline=validate_normative_catalog(repo_root=root,artifact_manifest=manifest,control_catalog=catalog,legacy_qualification=lq)
    if not baseline["qualified"]: raise RuntimeError("BASELINE_NORMATIVE_FIXTURE_INVALID:"+",".join(baseline["problems"]))
    return manifest,catalog,lq,{"current":current,"legacy":legacy}

def binding(cid,fixture_digest,env_digest,target_names,execution_sha):
    blobs,contents=target_identity(target_names); tok=hashlib.sha256(f"{cid}|{execution_sha}|{fixture_digest}".encode()).hexdigest()[:16]
    b=CaseRunBinding(cid,f"{cid}:{tok}",PACKET_SHA256,PLAN_BODY_SHA256,PLAN_BINDING_BLOB,HARNESS_V7_BLOB,HARNESS_VERSION,DESIGN_SHA,IMPLEMENTATION_SHA,IMPLEMENTATION_TREE,"V24",blobs,contents,fixture_digest,env_digest,"RUNNING")
    p=validate_binding(b,packet_sha256=PACKET_SHA256,plan_body_sha256=PLAN_BODY_SHA256,plan_binding_blob_sha=PLAN_BINDING_BLOB,harness_blob_sha=HARNESS_V7_BLOB)
    if p: raise RuntimeError(f"CASE_BINDING_INVALID:{cid}:"+",".join(p))
    return b

def endpoint_obs(r):return GovernedEndpointObservation(r.get("state"),"candidate",sha(r),tuple(r.get("problems",())))
def no_effect(profile):
    d=sha({"profile":profile,"effect_count":0}); return AuthorityEffectObservation(profile,d,d,0,0,"UNCHANGED","UNCHANGED")

def execute():
    random.seed(24011); env,env_digest=environment(); execution_sha=os.environ.get("GITHUB_SHA","LOCAL")
    scheduler=ExecutionScheduler(); ledger=ResultLedger(); cases={}
    def store(result,details):
        result=replace(result,predecessor_record_digest=ledger.head); digest=ledger.append(result)
        cases[result.case_id]={"scientific_result":asdict(result),"record_digest":digest,**details}; return result

    cid="WDPC-433"; scheduler.acquire(cid)
    f={"normative_catalog_qualification_state":"QUALIFIED","active_predicate_ids":["P-A","P-B"],"predicate_descriptors":[{"predicate_id":"P-A","phase":1,"within_phase_rank":1,"severity_rank":5,"endpoint":"E-A","control_id":"C-A"}]}
    r=compile_endpoint_precedence(f); b=binding(cid,sha(f),env_digest,("endpoint",),execution_sha)
    x=adjudicate_negative(cid,b,endpoint_obs(r),no_effect("O-ENDPOINT"),{"table_active":r["state"]=="ENDPOINT_PRECEDENCE_COMPILED","dispatch_before":0,"dispatch_after":0,"material_effect_before":0,"material_effect_after":0},True,True,"OMIT_EXACTLY_ONE_ACTIVE_PREDICATE")
    store(x,{"candidate_state":r["state"],"candidate_problems":r["problems"]}); scheduler.release(cid,x.result_state)

    cid="WDPC-453"; scheduler.acquire(cid)
    f={"normative_catalog_qualification_state":"QUALIFIED","active_predicate_ids":["GENERIC","STRICT"],"predicate_descriptors":[{"predicate_id":"GENERIC","phase":1,"within_phase_rank":1,"severity_rank":5,"endpoint":"GENERIC_FAIL","control_id":"C-G"}]}
    r=compile_endpoint_precedence(f); b=binding(cid,sha(f),env_digest,("endpoint",),execution_sha)
    x=adjudicate_negative(cid,b,endpoint_obs(r),no_effect("O-ENDPOINT"),{"table_active":r["state"]=="ENDPOINT_PRECEDENCE_COMPILED","dispatch_before":0,"dispatch_after":0,"material_effect_before":0,"material_effect_after":0},True,True,"OMIT_EXACTLY_ONE_STRICTER_SUBSYSTEM_PREDICATE")
    store(x,{"candidate_state":r["state"],"candidate_problems":r["problems"]}); scheduler.release(cid,x.result_state)

    cid="WDPC-447"; scheduler.acquire(cid)
    f={"normative_catalog_qualification_state":"QUALIFIED","endpoint_precedence_state":"ENDPOINT_PRECEDENCE_CORRECTNESS_QUALIFIED","exact_decision_path_predicate_ids":["P-REQ"],"admitted_applicability_predicate_ids":[],"producer_requested_field_ids":["OPTIONAL-ONLY"],"kernel_bound_redaction_classes":["VISIBLE"],"proof_field_descriptors":[{"field_id":"F-REQ","predicate_id":"P-REQ","control_id":"C-REQ","source_binding":"SOURCE-REQ","redaction_class":"VISIBLE","qualification_or_failure_field":True}]}
    r=compile_proof_view(f); b=binding(cid,sha(f),env_digest,("endpoint",),execution_sha)
    x=adjudicate_negative(cid,b,endpoint_obs(r),no_effect("O-PROOF"),{"proof_state":"PASS" if r["state"]=="PROOF_VIEW_APPLICABILITY_COMPILED" else "FAIL","consuming_authority_decision_before":0,"consuming_authority_decision_after":0,"material_effect_before":0,"material_effect_after":0},True,True)
    store(x,{"candidate_state":r["state"],"candidate_problems":r["problems"]}); scheduler.release(cid,x.result_state)

    for cid in ["WDPC-446","WDPC-454","WDPC-481","WDPC-482","WDPC-490"]:
        scheduler.acquire(cid)
        with tempfile.TemporaryDirectory() as td:
            temp=Path(td); manifest,catalog,lq,texts=make_normative_fixture(temp); manifest=copy.deepcopy(manifest); catalog=copy.deepcopy(catalog); lq=copy.deepcopy(lq); branch=None
            if cid=="WDPC-446": catalog["descriptors"]=[d for d in catalog["descriptors"] if d["control_id"]!="P24-17"]
            elif cid=="WDPC-454":
                new=texts["current"]+"\n## Hidden Permission — Authorize\n\nThis uncatalogued prose purports to authorize a material authority transition.\n"; (temp/"standards/current.md").write_text(new); nb=git_blob_sha_bytes(new.encode()); manifest["artifacts"][0]["blob_sha"]=nb
                for d in catalog["descriptors"]:
                    if d["normative_artifact_path"]=="standards/current.md": d["normative_artifact_blob_sha"]=nb
            elif cid=="WDPC-481": catalog["descriptors"]=[d for d in catalog["descriptors"] if d["control_id"]!="INHERITED-V5-S1"]
            elif cid=="WDPC-482":
                cb=manifest["artifacts"][0]["blob_sha"]
                for d in catalog["descriptors"]:
                    if d["control_id"]=="INHERITED-V5-S1": d["normative_artifact_blob_sha"]=cb
                branch="WRONG_ARTIFACT_BLOB_ONLY"
            elif cid=="WDPC-490": catalog["descriptors"]=[d for d in catalog["descriptors"] if d["control_id"]!="INHERITED-V5-S1"]; lq["records"]=[]
            fixture={"manifest":manifest,"catalog":catalog,"legacy_qualification":lq,"artifact_texts":{"current":(temp/"standards/current.md").read_text(),"legacy":(temp/"standards/legacy.md").read_text()}}
            r=validate_normative_catalog(repo_root=temp,artifact_manifest=manifest,control_catalog=catalog,legacy_qualification=lq)
            targets=("normative","continuity","preflight") if cid=="WDPC-490" else ("normative",); b=binding(cid,sha(fixture),env_digest,targets,execution_sha)
            x=adjudicate_negative(cid,b,endpoint_obs(r),no_effect("O-NORMATIVE"),{"authority_derived_from_target":bool(r.get("qualified")),"decision_dispatch_before":0,"decision_dispatch_after":0,"material_effect_before":0,"material_effect_after":0},True,True,branch)
            store(x,{"candidate_state":r["state"],"candidate_qualified":r["qualified"],"candidate_problems":r["problems"]})
        scheduler.release(cid,x.result_state)

    cid="WDPC-463"
    try: scheduler.acquire(cid)
    except ValueError as exc: cases[cid]={"case_status":"NOT_EXECUTED","result_state":"BLOCKED_BY_PRIOR_LOAD_BEARING_FAILURE","reason":str(exc)}
    else:
        f={"normative_catalog_qualification_state":"QUALIFIED","active_predicate_ids":["GENERIC","STRICT"],"predicate_descriptors":[{"predicate_id":"GENERIC","phase":1,"within_phase_rank":1,"severity_rank":5,"endpoint":"GENERIC_FAIL","control_id":"C-G"},{"predicate_id":"STRICT","phase":1,"within_phase_rank":2,"severity_rank":4,"endpoint":"STRICT_FAIL","control_id":"C-S","overrides_predicate_id":"GENERIC"}]}
        r=compile_endpoint_precedence(f); satisfied=r["state"]=="ENDPOINT_PRECEDENCE_COMPILED" and not r["problems"] and len(r["compiled_rows"])==2; b=binding(cid,sha(f),env_digest,("endpoint",),execution_sha); po=PositiveAssertionObservation("ENDPOINT_PRECEDENCE_TABLE_ACTIVATABLE",satisfied,(sha(r),)); x=adjudicate_positive(cid,b,po,True,True); store(x,{"candidate_state":r["state"],"candidate_problems":r["problems"],"claim_boundary":"REFERENCE_MECHANISM_ONLY_NO_OPERATIONAL_QUALIFICATION"}); scheduler.release(cid,x.result_state)

    cases["WDPC-491"]={"case_status":"NOT_EXECUTED","result_state":"NOT_EXECUTABLE_EXTERNAL_EVIDENCE_REQUIRED","execution_class":CASE_SPECS["WDPC-491"]["execution_class"],"required_evidence":"E-SEMANTIC","reason":"Manual semantic assessment required; synthetic semantic PASS prohibited."}
    for cid in ("WDPC-469","WDPC-495"): cases[cid]={"case_status":"BLOCKED_BY_I1_SEMANTIC_QUALIFICATION","result_state":"BLOCKED_BY_I1_SEMANTIC_QUALIFICATION","reason":"Frozen I1 semantic qualification prerequisite unresolved; no case body executed."}
    executed=[c for c,v in cases.items() if "scientific_result" in v]; passed=[c for c in executed if cases[c]["scientific_result"]["result_state"]=="PASS"]; red=[c for c in executed if c not in passed]
    return {"artifact":"V24_I11_CLUSTER_A_SCIENTIFIC_EXECUTION","plan":"V8_REVIEWED","execution_sha":execution_sha,"pre_scientific_frontier":PRE_SCIENCE_FRONTIER,"accidental_non_scientific_commit_preserved":ACCIDENTAL_NONSCIENTIFIC_COMMIT,"design_sha":DESIGN_SHA,"implementation_sha":IMPLEMENTATION_SHA,"implementation_tree":IMPLEMENTATION_TREE,"environment":asdict(env),"environment_digest":env_digest,"cases":cases,"executed_case_ids":executed,"pass_case_ids":passed,"nonpass_executed_case_ids":red,"gated_case_ids":["WDPC-491"],"blocked_case_ids":["WDPC-469","WDPC-495"],"ledger_head_digest":ledger.head,"authority_effect":AUTHORITY_EFFECT}

def main():
    report=execute(); out=Path(os.environ.get("V24_I11_CLUSTER_A_REPORT","testing/v24/results/V24-I11-CLUSTER-A-SCIENTIFIC-RESULT.json")); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print(json.dumps({k:report[k] for k in ["artifact","executed_case_ids","pass_case_ids","nonpass_executed_case_ids","gated_case_ids","blocked_case_ids","ledger_head_digest"]},sort_keys=True,indent=2)); return 0

if __name__=="__main__": raise SystemExit(main())
