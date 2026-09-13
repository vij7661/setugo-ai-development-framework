from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import secrets
import subprocess
import sys
import tempfile
from typing import Any

OBS_PREFIX = "R13_OBSERVATION="
QUALIFIED = "QUALIFIED"
CURRENT = "CURRENT"

CHECKS = (
    "MIXED_ALLOWED_AND_DISALLOWED_TERMINAL_REJECTED",
    "EVERY_REACHABLE_TERMINAL_ALLOWED",
    "GENESIS_CROSS_PAIR_REJECTED",
    "APPLICABLE_PREDICATE_OMISSION_REJECTED",
    "ATOMIC_BINDING_MODE_OMISSION_REJECTED",
    "LATER_RESOLUTION_PRESERVES_HISTORICAL_PASS_COUNT",
)


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def seal(record: dict[str, Any], field: str) -> dict[str, Any]:
    material = dict(record); material.pop(field, None)
    record[field] = digest(material)
    return record


def h(nonce: str, label: str) -> str:
    return hashlib.sha256(f"{nonce}:{label}".encode("utf-8")).hexdigest()


def actual_interpreter_contract() -> dict[str, Any]:
    flags = {
        "isolated": bool(sys.flags.isolated),
        "no_site": bool(sys.flags.no_site),
        "ignore_environment": bool(sys.flags.ignore_environment),
        "safe_path": bool(sys.flags.safe_path),
    }
    if any(v is not True for v in flags.values()):
        raise SystemExit("R13_ORACLE_INTERPRETER_NOT_ISOLATED")
    executable = pathlib.Path(sys.executable).resolve()
    names = sorted(sys.stdlib_module_names)
    contract = {
        "flags": flags,
        "implementation": sys.implementation.name,
        "cache_tag": sys.implementation.cache_tag,
        "version": [sys.version_info.major, sys.version_info.minor, sys.version_info.micro, sys.version_info.releaselevel, sys.version_info.serial],
        "hexversion": sys.hexversion,
        "executable_sha256": hashlib.sha256(executable.read_bytes()).hexdigest(),
        "stdlib_module_names_digest": digest(names),
        "candidate_path_absent": True,
        "trusted_oracle_imports_candidate": False,
    }
    contract["contract_digest"] = digest(contract)
    return contract


def candidate_modules_loaded(sandbox: pathlib.Path) -> list[str]:
    hits=[]
    for name,module in sys.modules.items():
        f=getattr(module,"__file__",None)
        if not isinstance(f,str): continue
        try: pathlib.Path(f).resolve().relative_to(sandbox)
        except (ValueError,OSError): continue
        hits.append(name)
    return sorted(hits)


def run_observer(*, sandbox: pathlib.Path, observer: pathlib.Path, request: dict[str, Any]) -> dict[str, Any]:
    if candidate_modules_loaded(sandbox):
        raise SystemExit("R13_ORACLE_CANDIDATE_MODULE_PRESENT_IN_TRUSTED_PROCESS")
    python_bin=pathlib.Path(sys.executable).resolve()
    env={"HOME":os.environ.get("HOME","/tmp"),"PATH":f"{python_bin.parent}:/usr/bin:/bin"}
    with tempfile.TemporaryDirectory(prefix="r13-request-") as td:
        req=pathlib.Path(td)/"request.json"
        req.write_bytes(canonical(request)+b"\n")
        cp=subprocess.run(
            [str(python_bin),"-I","-S",str(observer),"--sandbox",str(sandbox),"--request",str(req)],
            cwd=str(observer.parent),env=env,stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=60,check=False,
        )
    if cp.returncode != 0:
        raise SystemExit(f"R13_ORACLE_OBSERVER_FAILED:rc={cp.returncode}:stderr={cp.stderr[-1000:]!r}")
    if cp.stderr.strip():
        raise SystemExit(f"R13_ORACLE_OBSERVER_STDERR:{cp.stderr[-1000:]!r}")
    lines=[x for x in cp.stdout.splitlines() if x.strip()]
    if len(lines)!=1 or not lines[0].startswith(OBS_PREFIX):
        raise SystemExit(f"R13_ORACLE_OBSERVATION_PROTOCOL_INVALID:{lines!r}")
    obs=json.loads(lines[0][len(OBS_PREFIX):])
    if obs.get("schema_version")!=1 or obs.get("request_digest")!=digest(request):
        raise SystemExit("R13_ORACLE_OBSERVATION_REQUEST_BINDING_INVALID")
    if obs.get("module")!=request["module"] or obs.get("function")!=request["function"]:
        raise SystemExit("R13_ORACLE_OBSERVATION_CALL_IDENTITY_INVALID")
    if obs.get("candidate_process_role")!="UNTRUSTED_OBSERVATION_ONLY":
        raise SystemExit("R13_ORACLE_OBSERVATION_ROLE_INVALID")
    if obs.get("authority_effect")!="NONE_EVIDENCE_ONLY":
        raise SystemExit("R13_ORACLE_OBSERVATION_AUTHORITY_EFFECT_INVALID")
    if candidate_modules_loaded(sandbox):
        raise SystemExit("R13_ORACLE_CANDIDATE_MODULE_LEAKED_TO_TRUSTED_PROCESS")
    return obs


def currentness(nonce: str, source: str, source_digest: str) -> dict[str, Any]:
    r={
        "currentness_rule_id":f"CUR-{nonce}","source_object_id":source,
        "source_version_or_sequence":"1","source_digest":source_digest,
        "observed_at_sequence":1,"verifier_qualification_digest":h(nonce,"currentness-verifier"),
        "result":CURRENT,"binding_digest":"",
    }
    return seal(r,"binding_digest")


def completeness_graph(nonce: str, subject: str, root_kind: str="IMPLEMENTATION_DEPLOYMENT_ARTIFACT_INVENTORY") -> dict[str, Any]:
    root=f"ROOT-{nonce}-{subject}"
    return {
        "nodes":[
            {"node_id":subject,"omission_sensitive":True},
            {"node_id":root,"omission_sensitive":False,"root_kind":root_kind,"source_surface_digest":h(nonce,f"root:{subject}")},
        ],
        "edges":[{"from":subject,"to":root}],
    }


def completeness(nonce: str, subject: str, members: list[str], *, root_kind: str="IMPLEMENTATION_DEPLOYMENT_ARTIFACT_INVENTORY") -> dict[str, Any]:
    m=sorted(members); subject_digest=h(nonce,f"subject:{subject}")
    r={
        "subject_object_id":subject,"subject_content_digest":subject_digest,
        "expected_members":m,"actual_members":m,
        "expected_member_set_digest":digest(m),"actual_member_set_digest":digest(m),
        "set_equality_proof_digest":h(nonce,f"set-proof:{subject}"),
        "completeness_derivation_graph":completeness_graph(nonce,subject,root_kind),
        "derivation_mechanism_qualification_digests":[h(nonce,f"mechanism:{subject}")],
        "derivation_authority_independence_digests":[h(nonce,f"independence:{subject}")],
        "source_surface_digests":[h(nonce,f"root:{subject}")],
        "currentness_bindings":[currentness(nonce,subject,subject_digest)],
        "verifier_qualification_digest":h(nonce,f"completeness-verifier:{subject}"),
        "result":QUALIFIED,"qualification_digest":"",
    }
    return seal(r,"qualification_digest")


def request(module: str, function: str, *args: Any, **kwargs: Any) -> dict[str, Any]:
    return {"schema_version":1,"module":module,"function":function,"args":list(args),"kwargs":kwargs}


def require_return(obs: dict[str, Any]) -> Any:
    if obs.get("outcome_kind")!="RETURN":
        raise AssertionError(f"candidate raised instead of returning: {obs.get('payload')!r}")
    return obs.get("payload")


def scenario_mixed_terminal(nonce: str, run) -> tuple[list[dict],dict]:
    reg=f"REG-{nonce}"; root=f"ROOT-{nonce}"; bad=f"BAD-{nonce}"
    graph={
        "nodes":[
            {"node_id":reg,"omission_sensitive":True},
            {"node_id":root,"omission_sensitive":False,"root_kind":"IMPLEMENTATION_DEPLOYMENT_ARTIFACT_INVENTORY","source_surface_digest":h(nonce,"root")},
            {"node_id":bad,"omission_sensitive":True,"root_kind":"CANDIDATE_REGISTRY","source_surface_digest":h(nonce,"bad")},
        ],
        "edges":[{"from":reg,"to":root},{"from":reg,"to":bad}],
    }
    req=request("v24_v6_governance_foundation","validate_completeness_derivation_graph",graph)
    obs=run(req); out=require_return(obs)
    expected1="COMPLETENESS_DERIVATION_CYCLE_OR_UNROOTED_SOURCE_REJECTED"
    expected2=f"COMPLETENESS_GRAPH_DISALLOWED_TERMINAL:{bad}"
    assert expected1 in out.get("problems",[]), out
    assert expected2 in out.get("problems",[]), out
    return [req],{"observations":[obs],"assertion":{"contains":[expected1,expected2]}}


def scenario_allowed_terminal(nonce: str, run) -> tuple[list[dict],dict]:
    reg=f"REG-{nonce}"; root=f"ROOT-{nonce}"
    graph={"nodes":[{"node_id":reg,"omission_sensitive":True},{"node_id":root,"omission_sensitive":False,"root_kind":"IMPLEMENTATION_DEPLOYMENT_ARTIFACT_INVENTORY","source_surface_digest":h(nonce,"root")}],"edges":[{"from":reg,"to":root}]}
    req=request("v24_v6_governance_foundation","validate_completeness_derivation_graph",graph)
    obs=run(req); out=require_return(obs)
    assert out.get("problems")==[], out
    assert out.get("allowed_roots")==[root], out
    return [req],{"observations":[obs],"assertion":{"problems":[],"allowed_roots":[root]}}


def scenario_genesis_cross_pair(nonce: str, run) -> tuple[list[dict],dict]:
    boot=f"BOOT-{nonce}"; anchor=f"ANCHOR-{nonce}"; d1=h(nonce,"boot"); d2=h(nonce,"anchor")
    trusted=[{"object_id":boot,"content_digest":d1},{"object_id":anchor,"content_digest":d2}]
    scope={
        "governance_generation_id":f"GEN-{nonce}","genesis_record_digest":h(nonce,"genesis"),
        "root_kernel_digest":h(nonce,"kernel"),"trusted_objects":trusted,
        "trusted_object_pair_set_digest":digest(sorted(trusted,key=lambda x:(x["object_id"],x["content_digest"]))),
        "permitted_bootstrap_roles":["BOOTSTRAP_VERIFIER","ANCHOR_VERIFIER"],
        "residual_trust_reason_ids":["GENESIS_ROOT"],"creation_ceremony_digest":h(nonce,"ceremony"),
        "durable_anchor_digest":h(nonce,"durable"),"scope_digest":"",
    }
    seal(scope,"scope_digest")
    req=request("v24_v6_governance_foundation","genesis_scope_match",scope,object_id=boot,content_digest=d2)
    obs=run(req); out=require_return(obs)
    assert out.get("matched") is False, out
    assert out.get("endpoint")=="GENESIS_TRUST_SCOPE_MISMATCH_REJECTED", out
    return [req],{"observations":[obs],"assertion":{"matched":False,"endpoint":"GENESIS_TRUST_SCOPE_MISMATCH_REJECTED"}}


def endpoint_material(nonce: str) -> tuple[dict[str,Any],list[dict[str,Any]],str,list[str]]:
    pids=[f"P{i}-{nonce}" for i in (1,2,3)]
    descriptors=[
        {"predicate_id":pids[0],"phase":1,"within_phase_rank":1,"severity_rank":1,"endpoint":f"EARLY-{nonce}","control_id":f"C1-{nonce}"},
        {"predicate_id":pids[1],"phase":2,"within_phase_rank":1,"severity_rank":2,"endpoint":f"LATE-{nonce}","control_id":f"C2-{nonce}"},
        {"predicate_id":pids[2],"phase":3,"within_phase_rank":1,"severity_rank":3,"endpoint":f"LAST-{nonce}","control_id":f"C3-{nonce}"},
    ]
    rows=[{"predicate_id":x["predicate_id"],"phase":x["phase"],"within_phase_rank":x["within_phase_rank"],"severity_rank":x["severity_rank"],"endpoint":x["endpoint"],"control_id":x["control_id"]} for x in descriptors]
    rows=sorted(rows,key=lambda r:(r["phase"],r["within_phase_rank"],r["predicate_id"]))
    table_digest=digest(rows)
    q={"result":QUALIFIED,"subject_content_digest":table_digest,"qualification_digest":h(nonce,"endpoint-q"),"currentness_result":CURRENT}
    bundle={"normative_catalog_qualification_state":QUALIFIED,"predicate_descriptors":descriptors,"active_predicate_ids":pids,"expected_compiled_table_digest":table_digest,"endpoint_table_qualification":q}
    return bundle,rows,table_digest,pids


def scenario_applicability_omission(nonce: str, run) -> tuple[list[dict],dict]:
    endpoint_bundle,rows,table_digest,pids=endpoint_material(nonce)
    req1=request("v24_v6_endpoint_projection","compile_qualified_endpoint_table",endpoint_bundle)
    obs1=run(req1); out1=require_return(obs1)
    assert out1.get("qualified") is True and out1.get("problems")==[], out1
    assert out1.get("compiled_table_digest")==table_digest and out1.get("compiled_rows")==rows, out1
    rules=[{"predicate_id":pids[i],"applicability_rule_id":f"A{i+1}-{nonce}","applies":i<2} for i in range(3)]
    bundle={
        "compiled_endpoint_rows":rows,"endpoint_table_digest":table_digest,"endpoint_table_qualification_state":QUALIFIED,
        "applicability_rules":rules,"applicability_registry_completeness":completeness(nonce,f"APP-R-{nonce}",pids),
        "applicability_compiler_qualification_state":QUALIFIED,"applicability_compiler_qualification_digest":h(nonce,"app-compiler"),
        "decision_context_digest":h(nonce,"decision-context"),
        "applicable_universe_completeness":completeness(nonce,f"APP-U-{nonce}",[pids[0]]),
    }
    req2=request("v24_v6_endpoint_projection","derive_applicable_predicate_universe",bundle)
    obs2=run(req2); out2=require_return(obs2)
    assert out2.get("qualified") is False, out2
    assert "APPLICABLE_UNIVERSE_MEMBER_SET_MISMATCH" in out2.get("problems",[]), out2
    return [req1,req2],{"observations":[obs1,obs2],"assertion":{"qualified":False,"contains":"APPLICABLE_UNIVERSE_MEMBER_SET_MISMATCH"}}


def atomic_currentness(nonce: str, source_id: str, source_digest: str) -> dict[str,Any]:
    r={"currentness_rule_id":f"CURRENT-{nonce}","source_object_id":source_id,"source_version_or_sequence":"1","source_digest":source_digest,"verifier_qualification_digest":h(nonce,"atomic-current-verifier"),"result":CURRENT,"observed_at_sequence":1,"binding_digest":""}
    return seal(r,"binding_digest")


def atomic_completeness(nonce: str, registry_id: str, registry_digest: str, expected: list[str], actual: list[str]) -> dict[str,Any]:
    graph={
        "nodes":[
            {"node_id":registry_id,"omission_sensitive":True},
            {"node_id":f"ROOT-CONTRACTS-{nonce}","omission_sensitive":False,"root_kind":"NORMATIVE_ARTIFACT_BYTES_STRUCTURE","source_surface_digest":h(nonce,"atomic-root-contracts")},
            {"node_id":f"ROOT-MECHANISMS-{nonce}","omission_sensitive":False,"root_kind":"CONTROL_PLANE_OBSERVATION","source_surface_digest":h(nonce,"atomic-root-mechanisms")},
        ],
        "edges":[{"from":registry_id,"to":f"ROOT-CONTRACTS-{nonce}"},{"from":registry_id,"to":f"ROOT-MECHANISMS-{nonce}"}],
    }
    r={
        "subject_object_id":registry_id,"subject_content_digest":registry_digest,
        "expected_member_set_digest":digest(sorted(expected)),"actual_member_set_digest":digest(sorted(actual)),
        "set_equality_proof_digest":digest({"expected":sorted(expected),"actual":sorted(actual)}),
        "verifier_qualification_digest":h(nonce,"atomic-completeness-verifier"),"expected_members":sorted(expected),"actual_members":sorted(actual),
        "completeness_derivation_graph":graph,"derivation_mechanism_qualification_digests":[h(nonce,"atomic-derivation-mech")],
        "derivation_authority_independence_digests":[h(nonce,"atomic-independence")],
        "source_surface_digests":[h(nonce,"atomic-root-contracts"),h(nonce,"atomic-root-mechanisms")],
        "currentness_bindings":[atomic_currentness(nonce,registry_id,registry_digest)],"result":QUALIFIED,"qualification_digest":"",
    }
    return seal(r,"qualification_digest")


def scenario_atomic_omission(nonce: str, run) -> tuple[list[dict],dict]:
    modes=["SAME_AUTHORITATIVE_TRANSACTION","CRYPTOGRAPHICALLY_BOUND_SNAPSHOT"]
    contracts=[
        {"contract_id":f"EVAL-{nonce}","contract_digest":h(nonce,"contract1"),"qualification_state":QUALIFIED,"authority_independence_state":QUALIFIED,"currentness_result":CURRENT,"control_domain_id":f"DOMAIN-C1-{nonce}","required_atomic_binding_mode_ids":[modes[0]]},
        {"contract_id":f"COND-{nonce}","contract_digest":h(nonce,"contract2"),"qualification_state":QUALIFIED,"authority_independence_state":QUALIFIED,"currentness_result":CURRENT,"control_domain_id":f"DOMAIN-C2-{nonce}","required_atomic_binding_mode_ids":[modes[1]]},
    ]
    mechanisms=[
        {"mechanism_id":f"TX-{nonce}","mechanism_kind":"AUTHORITATIVE_TRANSACTION","mechanism_digest":h(nonce,"mech1"),"admission_state":QUALIFIED,"qualification_state":QUALIFIED,"authority_independence_state":QUALIFIED,"currentness_result":CURRENT,"control_domain_id":f"DOMAIN-M1-{nonce}","supported_atomic_binding_mode_ids":[modes[0]]},
        {"mechanism_id":f"SNAP-{nonce}","mechanism_kind":"CRYPTOGRAPHIC_SNAPSHOT","mechanism_digest":h(nonce,"mech2"),"admission_state":QUALIFIED,"qualification_state":QUALIFIED,"authority_independence_state":QUALIFIED,"currentness_result":CURRENT,"control_domain_id":f"DOMAIN-M2-{nonce}","supported_atomic_binding_mode_ids":[modes[1]]},
    ]
    entries=[
        {"mode_id":modes[0],"proof_schema_digest":h(nonce,"schema1"),"verifier_mechanism_id":f"VERIFY-TX-{nonce}","verifier_qualification_digest":h(nonce,"verify1"),"verifier_qualification_state":QUALIFIED,"currentness_result":CURRENT,"required_proof_fields":["transaction_id","transaction_commit_digest","evaluation_digest","condition_digest","decision_context_digest"]},
        {"mode_id":modes[1],"proof_schema_digest":h(nonce,"schema2"),"verifier_mechanism_id":f"VERIFY-SNAP-{nonce}","verifier_qualification_digest":h(nonce,"verify2"),"verifier_qualification_state":QUALIFIED,"currentness_result":CURRENT,"required_proof_fields":["snapshot_digest","snapshot_source_qualification_digest","evaluation_digest","condition_digest","decision_context_digest"]},
    ]
    registry={"registry_id":f"ATOMIC-REG-{nonce}","entries":entries,"qualification_state":QUALIFIED,"currentness_result":CURRENT,"content_digest":""}
    registry["content_digest"]=digest({k:v for k,v in registry.items() if k!="content_digest"})
    cq=atomic_completeness(nonce,registry["registry_id"],registry["content_digest"],modes,modes)
    # Omit one registry mode without weakening the independently derived completeness obligation.
    registry["entries"]=registry["entries"][:-1]
    registry["content_digest"]=digest({k:v for k,v in registry.items() if k!="content_digest"})
    bundle={"binding_contracts":contracts,"admitted_binding_mechanisms":mechanisms,"registry":registry,"completeness_qualification":cq}
    req=request("v24_v6_atomic_binding_modes","validate_atomic_binding_mode_registry",bundle)
    obs=run(req); out=require_return(obs)
    assert out.get("qualified") is False, out
    assert "ATOMIC_BINDING_MODE_REGISTRY_SET_EQUALITY_FAILED" in out.get("problems",[]), out
    return [req],{"observations":[obs],"assertion":{"qualified":False,"contains":"ATOMIC_BINDING_MODE_REGISTRY_SET_EQUALITY_FAILED"}}


def qualification_currentness(nonce: str, source_id: str, source_digest: str) -> dict[str,Any]:
    r={"currentness_rule_id":f"CURRENT-RULE-{nonce}","source_object_id":source_id,"source_version_or_sequence":"1","source_digest":source_digest,"verifier_qualification_digest":h(nonce,"qual-current-verifier"),"result":CURRENT,"observed_at_sequence":1,"binding_digest":""}
    return seal(r,"binding_digest")


def qualification_completeness(nonce: str, subject: str, subject_digest: str, cases: list[str]) -> dict[str,Any]:
    cases=sorted(cases); root=f"ROOT-CASE-{nonce}"
    graph={"nodes":[{"node_id":subject,"omission_sensitive":True},{"node_id":root,"omission_sensitive":False,"root_kind":"NORMATIVE_ARTIFACT_BYTES_STRUCTURE","source_surface_digest":h(nonce,"case-root")}],"edges":[{"from":subject,"to":root}]}
    r={"subject_object_id":subject,"subject_content_digest":subject_digest,"expected_member_set_digest":digest(cases),"actual_member_set_digest":digest(cases),"set_equality_proof_digest":digest({"expected":cases,"actual":cases}),"verifier_qualification_digest":h(nonce,"case-verifier"),"expected_members":cases,"actual_members":cases,"completeness_derivation_graph":graph,"derivation_mechanism_qualification_digests":[h(nonce,"case-derivation")],"derivation_authority_independence_digests":[h(nonce,"case-independence")],"source_surface_digests":[h(nonce,"case-root")],"currentness_bindings":[qualification_currentness(nonce,subject,subject_digest)],"result":QUALIFIED,"qualification_digest":""}
    return seal(r,"qualification_digest")


def result_record(nonce: str, case_id: str, seq: int, disposition: str, commit: str, tree: str, env_digest: str, *, round_id: str, execution: str="EXECUTED", prior: str|None=None) -> dict[str,Any]:
    r={"result_id":f"RESULT-{nonce}-{round_id}-{case_id}-{seq}","qualification_round_id":round_id,"case_id":case_id,"candidate_commit":commit,"candidate_tree":tree,"environment_digest":env_digest,"case_contract_digest":h(nonce,f"case-contract:{case_id}"),"execution_state":execution,"terminal_disposition":disposition,"binding_valid":True,"qualification_basis_digests":[h(nonce,"qual-basis")],"evidence_basis_digests":[h(nonce,"evidence-basis")],"sequence":seq,"resolves_prior_result_digest":prior,"result_record_digest":""}
    return seal(r,"result_record_digest")


def scenario_historical_pass(nonce: str, run, commit: str, tree: str, env_digest: str) -> tuple[list[dict],dict]:
    round1=f"ROUND-1-{nonce}"; round2=f"ROUND-2-{nonce}"; case_a=f"CASE-A-{nonce}"; case_b=f"CASE-B-{nonce}"; cases=[case_a,case_b]
    universe={"universe_id":f"UNIVERSE-{nonce}","qualification_round_id":round1,"candidate_commit":commit,"candidate_tree":tree,"environment_digest":env_digest,"case_contract_set_digest":h(nonce,"case-set"),"case_ids":sorted(cases),"qualification_state":QUALIFIED,"currentness_result":CURRENT,"content_digest":""}
    universe["content_digest"]=digest({k:v for k,v in universe.items() if k!="content_digest"})
    universe["completeness_qualification"]=qualification_completeness(nonce,universe["universe_id"],universe["content_digest"],cases)
    old=result_record(nonce,case_a,1,"UNRESOLVED",commit,tree,env_digest,round_id=round1,execution="NOT_EXECUTED")
    old_b=result_record(nonce,case_b,2,"FAIL_CODE_DEFECT",commit,tree,env_digest,round_id=round1)
    later=result_record(nonce,case_a,3,"PASS",commit,tree,env_digest,round_id=round2,prior=old["result_record_digest"])
    compiler={"compiler_id":f"SUMMARY-{nonce}","compiler_digest":h(nonce,"compiler"),"compiler_qualification_digest":h(nonce,"compiler-q"),"qualification_state":QUALIFIED,"independence_state":QUALIFIED,"currentness_result":CURRENT}
    bundle={"summary_compiler":compiler,"case_universe":universe,"qualification_round_id":round1,"result_records":[old,old_b,later]}
    req=request("v24_v6_qualification_integrity","compile_qualification_summary",bundle)
    obs=run(req); out=require_return(obs)
    assert out.get("pass_count")==0, out
    assert out.get("nonpass",{}).get(case_a)=="UNRESOLVED", out
    return [req],{"observations":[obs],"assertion":{"pass_count":0,"nonpass_case":case_a,"nonpass_value":"UNRESOLVED"}}


def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument("--sandbox",required=True); ap.add_argument("--observer",required=True)
    ap.add_argument("--candidate-commit",required=True); ap.add_argument("--candidate-tree",required=True)
    ap.add_argument("--environment-digest",required=True); ap.add_argument("--interpreter-contract-digest",required=True)
    ap.add_argument("--oracle-git-blob-sha1",required=True); ap.add_argument("--observer-git-blob-sha1",required=True)
    ap.add_argument("--run-id",required=True); ap.add_argument("--round-id",required=True); ap.add_argument("--output",required=True)
    args=ap.parse_args()

    runtime=actual_interpreter_contract()
    if runtime["contract_digest"]!=args.interpreter_contract_digest:
        raise SystemExit("R13_ORACLE_INTERPRETER_CONTRACT_MISMATCH")
    sandbox=pathlib.Path(args.sandbox).resolve(); observer=pathlib.Path(args.observer).resolve()
    if observer.is_relative_to(sandbox): raise SystemExit("R13_ORACLE_OBSERVER_INSIDE_CANDIDATE")
    if "" in sys.path or str(sandbox) in sys.path or str(sandbox/"governance-runtime") in sys.path:
        raise SystemExit("R13_ORACLE_CANDIDATE_PATH_PRESENT")
    if candidate_modules_loaded(sandbox): raise SystemExit("R13_ORACLE_CANDIDATE_MODULE_ALREADY_LOADED")

    scenario_map={
        CHECKS[0]:scenario_mixed_terminal,
        CHECKS[1]:scenario_allowed_terminal,
        CHECKS[2]:scenario_genesis_cross_pair,
        CHECKS[3]:scenario_applicability_omission,
        CHECKS[4]:scenario_atomic_omission,
    }
    records=[]
    for check_id in CHECKS:
        nonce=secrets.token_hex(12)
        def run(req): return run_observer(sandbox=sandbox,observer=observer,request=req)
        if check_id==CHECKS[5]:
            requests,detail=scenario_historical_pass(nonce,run,args.candidate_commit,args.candidate_tree,args.environment_digest)
        else:
            requests,detail=scenario_map[check_id](nonce,run)
        observations=detail["observations"]
        assertion_material={"check_id":check_id,"assertion":detail["assertion"],"observation_digest":digest(observations)}
        record={
            "check_id":check_id,"challenge_digest":digest({"check_id":check_id,"nonce":nonce}),
            "request_digest":digest(requests),"observation_digest":digest(observations),"assertion_digest":digest(assertion_material),
            "candidate_commit":args.candidate_commit,"candidate_tree":args.candidate_tree,"environment_digest":args.environment_digest,
            "interpreter_contract_digest":args.interpreter_contract_digest,"oracle_git_blob_sha1":args.oracle_git_blob_sha1,
            "observer_git_blob_sha1":args.observer_git_blob_sha1,"run_id":args.run_id,"round_id":args.round_id,
            "candidate_process_role":"UNTRUSTED_OBSERVATION_ONLY","oracle_decision_origin":"TRUSTED_EXTERNAL_ORACLE",
            "oracle_control_domain":"R13-EXTERNAL-TRUSTED-ORACLE","candidate_control_domain":"R13-CANDIDATE-EXECUTION",
            "oracle_terminal_result":"PASS",
        }
        record["record_digest"]=digest(record)
        records.append(record)

    bundle={
        "schema_version":1,"authority_origin":"EXTERNAL_REVIEW_BRANCH","candidate_self_grant":False,
        "candidate_side_unittest_role":"NON_AUTHORITATIVE_DIAGNOSTIC_ONLY","candidate_commit":args.candidate_commit,
        "candidate_tree":args.candidate_tree,"environment_digest":args.environment_digest,
        "interpreter_contract_digest":args.interpreter_contract_digest,"oracle_git_blob_sha1":args.oracle_git_blob_sha1,
        "observer_git_blob_sha1":args.observer_git_blob_sha1,"records":records,
        "evidence_set_digest":digest({"record_digests":sorted(r["record_digest"] for r in records)}),
        "scientific_execution_state":"CLOSED_PENDING_SUCCESSOR_REVIEW","authority_effect":"NONE_EVIDENCE_ONLY",
    }
    pathlib.Path(args.output).write_text(json.dumps(bundle,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(f"R13_TRUSTED_ORACLE_CHECKS={len(records)}")
    print(f"R13_TRUSTED_ORACLE_EVIDENCE_SET_DIGEST={bundle['evidence_set_digest']}")


if __name__=="__main__": main()
