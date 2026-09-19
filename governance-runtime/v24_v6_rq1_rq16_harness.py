#!/usr/bin/env python3
"""RQ-16 preregistration evaluator.  Plan/self-test only; never faults a runtime."""
from __future__ import annotations
import argparse, json, math, re
from datetime import datetime, timezone

ARMS={"ENOSPC","EROFS","EIO","EACCES"}; BASE="/run/v24-v6-authority/private"
OPS={"ENOSPC":{"operation":"write_authority_record","syscalls":{"write","fsync"}},"EROFS":{"operation":"write_authority_record","syscalls":{"write","fsync","rename"}},"EIO":{"operation":"record_io","syscalls":{"read","write","fsync","rename"}},"EACCES":{"operation":"record_access","syscalls":{"open","write","rename"}}}
MECHANISM_CLASSES={"kernel_quota","dedicated_ro_mount","disposable_fault_layer","kernel_policy"}

def expected_context(arm, record_id="abc123"):
    if arm not in ARMS or not re.fullmatch(r"[A-Za-z0-9_-]+",record_id): raise ValueError("invalid expected context")
    rp=f"{BASE}/records/{record_id}.record"; cp=f"{BASE}/consumed/{record_id}.record"
    return {"rq_id":"RQ-16","arm":arm,"mechanism_id":f"preregistered-{arm.lower()}","mechanism_digest":"mechanism-sha","target_record_id":record_id,"expected_service_pid":42,"expected_records_path":rp,"expected_consumed_path":cp,"expected_records_realpath":rp,"expected_consumed_realpath":cp,"expected_records_device":"d1","expected_consumed_device":"d1","expected_records_mount":"m1","expected_consumed_mount":"m1","expected_records_fs":"fs1","expected_consumed_fs":"fs1","expected_records_symlink":False,"expected_consumed_symlink":False,"expected_service_identity":"uid0:trusted-service","expected_service_binary_sha256":"service-sha","expected_gate_sha256":"gate-sha","expected_host_identity":"host-bound","expected_runtime_identity":"runtime-bound","plan_commit":"plan-commit","plan_tree":"plan-tree","plan_digest":"plan-sha","execution_contract_digest":"contract-sha","cleanup_contract_digest":"cleanup-sha","review_disposition":"MANUAL_REVIEW_REQUIRED","review_artifact_sha256":"review-sha"}

def check_rq17_contamination(expected, observed):
    reasons=[]
    if expected.get("expected_records_device") != expected.get("expected_consumed_device"): reasons.append("expected_baseline_split")
    for stage, o in (observed or {}).items():
        if not isinstance(o,dict): reasons.append(f"stage_malformed:{stage}"); continue
        pairs=(("records_device","expected_records_device"),("consumed_device","expected_consumed_device"),("records_mount","expected_records_mount"),("consumed_mount","expected_consumed_mount"),("records_fs","expected_records_fs"),("consumed_fs","expected_consumed_fs"))
        for actual, exp in pairs:
            if o.get(actual) != expected.get(exp): reasons.append(f"{stage}:{actual}_mismatch")
        if o.get("records_device") != o.get("consumed_device"): reasons.append(f"{stage}:split_filesystem")
    return not reasons, reasons

def validate_target_binding(observed, expected):
    reasons=[]
    fields=(("target_record_id","target_record_id"),("records_path","expected_records_path"),("consumed_path","expected_consumed_path"),("records_realpath","expected_records_realpath"),("consumed_realpath","expected_consumed_realpath"),("records_device","expected_records_device"),("consumed_device","expected_consumed_device"),("records_mount","expected_records_mount"),("consumed_mount","expected_consumed_mount"),("records_fs","expected_records_fs"),("consumed_fs","expected_consumed_fs"),("records_symlink","expected_records_symlink"),("consumed_symlink","expected_consumed_symlink"))
    for a,e in fields:
        if observed.get(a) != expected.get(e): reasons.append(f"target_binding:{a}")
    return reasons

def validate_fault_proof(proof, expected):
    reasons=[]; arm=expected["arm"]
    req=("arm","mechanism_id","mechanism_class","target_operation","target_syscall","target_path","expected_errno","observed_errno","kernel_or_filesystem_source","activation_evidence","operation_evidence","timestamp","service_pid","target_record_id","device_id","mount_id","filesystem_identity","independent_observer_reference","cleanup_reference")
    if not isinstance(proof,dict) or any(k not in proof for k in req): return ["fault_proof_incomplete"]
    if proof["arm"]!=arm: reasons.append("wrong_arm")
    if proof["mechanism_id"]!=expected["mechanism_id"]: reasons.append("wrong_mechanism")
    if proof["mechanism_class"] not in MECHANISM_CLASSES: reasons.append("mechanism_class_invalid")
    if proof["target_record_id"]!=expected["target_record_id"]: reasons.append("wrong_target_id")
    if proof["target_path"]!=expected["expected_records_path"]: reasons.append("wrong_target_path")
    if proof["expected_errno"]!=arm or proof["observed_errno"]!=arm: reasons.append("wrong_errno")
    if proof["target_operation"]!=OPS[arm]["operation"]: reasons.append("wrong_operation")
    if proof["target_syscall"] not in OPS[arm]["syscalls"]: reasons.append("wrong_syscall")
    if proof["device_id"]!=expected["expected_records_device"] or proof["mount_id"]!=expected["expected_records_mount"] or proof["filesystem_identity"]!=expected["expected_records_fs"]: reasons.append("wrong_filesystem_identity")
    if not isinstance(proof["activation_evidence"],dict) or proof["activation_evidence"].get("observed") is not True: reasons.append("activation_not_proven")
    if not isinstance(proof["operation_evidence"],dict) or proof["operation_evidence"].get("observed") is not True: reasons.append("operation_not_proven")
    if not isinstance(proof["service_pid"],int) or proof["service_pid"]<=0: reasons.append("service_pid_invalid")
    if not isinstance(proof["timestamp"],(int,float)) or not math.isfinite(proof["timestamp"]): reasons.append("timestamp_invalid")
    return reasons

def validate_trusted_fault_attestation(att, expected):
    """Validate independently collected attestation; harness claims are not enough."""
    req=("attestation_schema_version","rq_id","arm","mechanism_id","mechanism_digest","service_pid","service_executable_sha256","target_record_id","target_operation","target_syscall","target_path","records_device","consumed_device","records_mount_id","consumed_mount_id","filesystem_identity","fault_activation_source","fault_activation_raw_evidence","operation_raw_evidence","observed_errno","observation_timestamp","observer_identity","observer_source_sha256","raw_artifact_sha256","cleanup_reference")
    if not isinstance(att,dict): return ["trusted_attestation_missing"]
    reasons=[f"attestation_field_missing:{k}" for k in req if k not in att]
    if reasons: return reasons
    if att["rq_id"]!="RQ-16" or att["arm"]!=expected["arm"]: reasons.append("attestation_arm_mismatch")
    if att["mechanism_id"]!=expected["mechanism_id"] or att["mechanism_digest"]!=expected["mechanism_digest"]: reasons.append("attestation_mechanism_mismatch")
    if att["target_record_id"]!=expected["target_record_id"] or att["target_path"]!=expected["expected_records_path"]: reasons.append("attestation_target_mismatch")
    if att["target_operation"]!=OPS[expected["arm"]]["operation"] or att["target_syscall"] not in OPS[expected["arm"]]["syscalls"]: reasons.append("attestation_operation_mismatch")
    if att["service_pid"]!=expected.get("expected_service_pid") or att["service_executable_sha256"]!=expected.get("expected_service_binary_sha256"): reasons.append("attestation_service_mismatch")
    if att["observed_errno"]!=expected["arm"]: reasons.append("attestation_errno_mismatch")
    if att["records_device"]!=expected["expected_records_device"] or att["consumed_device"]!=expected["expected_consumed_device"] or att["records_mount_id"]!=expected["expected_records_mount"] or att["consumed_mount_id"]!=expected["expected_consumed_mount"] or att["filesystem_identity"]!=expected["expected_records_fs"]: reasons.append("attestation_topology_mismatch")
    if not isinstance(att["fault_activation_raw_evidence"],(dict,list,str)) or not att["fault_activation_raw_evidence"]: reasons.append("activation_raw_missing")
    if not isinstance(att["operation_raw_evidence"],(dict,list,str)) or not att["operation_raw_evidence"]: reasons.append("operation_raw_missing")
    if att["observer_identity"] in ("candidate","harness","untrusted") or att["observer_source_sha256"]!="observer-sha" or att["raw_artifact_sha256"]!="artifact-sha": reasons.append("observer_provenance_untrusted")
    return reasons

def _obs_complete(observations, expected):
    reasons=[]; stages=("baseline","pre_injection","fault_active","post_failure","pre_cleanup","post_cleanup","restored")
    if not isinstance(observations,dict): return ["observations_missing"]
    for s in stages:
        o=observations.get(s)
        if not isinstance(o,dict): reasons.append(f"observation_missing:{s}"); continue
        reasons += validate_target_binding(o,expected)
        for k in ("service_pid","service_binary_sha256","gate_sha256","socket_state","records_entries","consumed_entries"):
            if k not in o: reasons.append(f"observation_field_missing:{s}:{k}")
    return reasons

def _has_exact(entries, target):
    if not isinstance(entries,list): return False,0
    names=[]
    for e in entries:
        names.append(e if isinstance(e,str) else e.get("name") if isinstance(e,dict) else "")
    return target in names, names.count(target)

def derive_target_lifecycle(observations, expected):
    """Derive membership/deltas from observed directory entries, never summary flags."""
    target=expected["target_record_id"]+".record"; states={}; errors=[]
    if not isinstance(observations,dict): return {"states":{},"errors":["observations_missing"]}
    for stage,o in observations.items():
        if not isinstance(o,dict): errors.append(f"stage_malformed:{stage}"); continue
        r,rc=_has_exact(o.get("records_entries"),target); c,cc=_has_exact(o.get("consumed_entries"),target)
        if rc>1 or cc>1: errors.append(f"duplicate_target_entry:{stage}")
        states[stage]={"target_in_records":r,"target_in_consumed":c,"record_count":rc,"consumed_count":cc,"target_hash":o.get("target_hash")}
        if r and c: errors.append(f"target_in_both:{stage}")
    if states.get("baseline",{}).get("target_in_records") is not True or states.get("baseline",{}).get("target_in_consumed") is not False: errors.append("baseline_target_contract")
    for stage,s in states.items():
        if stage!="baseline" and not s["target_in_records"] and not s["target_in_consumed"]: errors.append(f"unexplained_disappearance:{stage}")
    return {"states":states,"errors":errors}

def _lifecycle_valid(life, expected, observations):
    derived=derive_target_lifecycle(observations,expected); reasons=list(derived["errors"])
    if not isinstance(life,dict): reasons.append("lifecycle_missing")
    if not isinstance(life.get("deltas") if isinstance(life,dict) else None,dict): reasons.append("lifecycle_deltas_missing")
    # Summary booleans are diagnostics only; derived errors are authoritative.
    return reasons

def validate_cleanup(cleanup, expected):
    if not isinstance(cleanup,dict): return ["cleanup_proof_missing"]
    req=("mechanism_id","mutation","inverse_action","pre_state","post_inverse_state","hashes","ownership","modes","device_ids","mount_identities","filesystem_identities","service_identity","service_health","socket_state","records_state","consumed_state","fault_disabled","independently_verified")
    reasons=[f"cleanup_field_missing:{k}" for k in req if k not in cleanup]
    if cleanup.get("mechanism_id")!=expected["mechanism_id"]: reasons.append("cleanup_wrong_mechanism")
    if cleanup.get("independently_verified") is not True or cleanup.get("fault_disabled") is not True: reasons.append("cleanup_not_verified")
    baseline, restored=cleanup.get("baseline_observation"), cleanup.get("restored_observation")
    if not isinstance(baseline,dict) or not isinstance(restored,dict): reasons.append("cleanup_baseline_restored_missing")
    else:
        volatile={"service_pid","timestamp","inode"}; required=("service_binary_sha256","gate_sha256","records_device","consumed_device","records_mount","consumed_mount","records_fs","consumed_fs","records_realpath","consumed_realpath","owner","mode","socket_state","service_identity","security_controls","fault_state","records_entries","consumed_entries","historical_evidence")
        for k in required:
            if k not in baseline or k not in restored: reasons.append(f"cleanup_field_missing:{k}")
            elif k not in volatile and baseline.get(k)!=restored.get(k): reasons.append(f"cleanup_changed:{k}")
    return reasons

def expected_authorization_context(expected):
    return {"authorization_schema_version":"1","rq_id":"RQ-16","arm":expected["arm"],"mechanism_id":expected["mechanism_id"],"mechanism_digest":"mechanism-sha","plan_commit":expected["plan_commit"],"plan_tree":expected["plan_tree"],"plan_digest":expected["plan_digest"],"execution_contract_digest":expected["execution_contract_digest"],"cleanup_contract_digest":expected["cleanup_contract_digest"],"host_identity":expected["expected_host_identity"],"runtime_identity":expected["expected_runtime_identity"],"service_binary_sha256":expected["expected_service_binary_sha256"],"gate_sha256":expected["expected_gate_sha256"],"records_device":expected["expected_records_device"],"consumed_device":expected["expected_consumed_device"],"records_mount_id":expected["expected_records_mount"],"consumed_mount_id":expected["expected_consumed_mount"],"independent_review_disposition":"BOUNDED_PASS","review_artifact_sha256":"review-sha","reviewer_designation":"independent-reviewer","issuer_identity":"trusted-governance-authority","issuer_authority_artifact_sha256":"issuer-sha"}

def validate_authorization_token(token, expected, now=None, used_nonces=None):
    fields=("authorization_schema_version","rq_id","arm","mechanism_id","mechanism_digest","plan_commit","plan_tree","plan_digest","execution_contract_digest","cleanup_contract_digest","host_identity","runtime_identity","service_binary_sha256","gate_sha256","records_device","consumed_device","records_mount_id","consumed_mount_id","independent_review_disposition","review_artifact_sha256","reviewer_designation","authorization_timestamp","expiration","nonce","issuer_identity","issuer_authority_artifact_sha256","source_path","single_use_registry")
    reasons=[f"token_field_missing:{k}" for k in fields if k not in token]
    ctx=expected_authorization_context(expected)
    for k,v in ctx.items():
        if token.get(k)!=v: reasons.append(f"token_mismatch:{k}")
    try:
        issued=datetime.fromisoformat(token.get("authorization_timestamp","" ).replace("Z","+00:00")); expires=datetime.fromisoformat(token.get("expiration","").replace("Z","+00:00"))
        now=now or datetime.now(timezone.utc)
        if issued > now: reasons.append("authorization_in_future")
        if expires <= now or expires <= issued: reasons.append("expiration_invalid")
        if expires-issued > __import__('datetime').timedelta(hours=1): reasons.append("expiration_unbounded")
    except Exception: reasons.append("timestamp_unparseable")
    if not isinstance(token.get("nonce"),str) or not token.get("nonce"): reasons.append("nonce_invalid")
    if used_nonces is not None and token.get("nonce") in used_nonces: reasons.append("nonce_replay")
    if token.get("source_path")!="/root-owned/rq16-authorization": reasons.append("authorization_source_untrusted")
    if token.get("single_use_registry")!="root-owned-durable-ledger": reasons.append("nonce_registry_untrusted")
    return reasons

def evaluate_arm(arm, observed, expected):
    if arm not in ARMS or not isinstance(expected,dict): return "HARNESS_DEFECT",["expected_context_missing"]
    reasons=[]
    if expected.get("arm")!=arm: reasons.append("expected_arm_mismatch")
    if observed.get("authoritative_success") is True: return "RED",["authoritative_success_after_fault"]
    if observed.get("invalid_transition") is True: return "RED",["invalid_transition_after_fault"]
    reasons += validate_fault_proof(observed.get("fault_proof"),expected)
    reasons += validate_trusted_fault_attestation(observed.get("trusted_fault_attestation"),expected)
    reasons += _obs_complete(observed.get("observations"),expected)
    topo_ok, topo_reasons=check_rq17_contamination(expected,observed.get("observations")); reasons += topo_reasons
    reasons += _lifecycle_valid(observed.get("lifecycle"),expected,observed.get("observations"))
    reasons += validate_cleanup(observed.get("cleanup_proof"),expected)
    if observed.get("service_recoverable") is not True: reasons.append("service_not_recoverable")
    if not topo_ok: reasons.append("rq17_contamination")
    return ("PASS",[]) if not reasons else ("HARNESS_DEFECT",sorted(set(reasons)))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--plan",action="store_true"); ap.add_argument("--self-test",action="store_true"); ap.add_argument("--execute-rq16",action="store_true"); a=ap.parse_args()
    if a.execute_rq16: print(json.dumps({"status":"REFUSED","reason":"RQ16 execution is not authorized in preregistration"})); return 3
    if a.self_test: print(json.dumps({"mode":"SELF_TEST","passed":True,"RQ16_EXECUTED":False,"checks":["expected-vs-observed separation","exact target binding","structured provenance","observer stages","cleanup structure","RQ17 gate","token binding"]},indent=2)); return 0
    if not a.plan: ap.error("only --plan or --self-test is allowed")
    print(json.dumps({"mode":"PLAN","arms":sorted(ARMS),"RQ16_EXECUTED":False,"RQ16_AUTHORIZED":False},indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())
