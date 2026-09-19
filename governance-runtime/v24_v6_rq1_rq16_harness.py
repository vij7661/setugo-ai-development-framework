#!/usr/bin/env python3
"""RQ-16 preregistration evaluator; plan/self-test only, never performs faults."""
from __future__ import annotations
import argparse, json, math, re

ARMS = {"ENOSPC", "EROFS", "EIO", "EACCES"}
BASE = "/run/v24-v6-authority/private"
OPS = {
    "ENOSPC": {"operation": "write_authority_record", "syscalls": {"write", "fsync"}},
    "EROFS": {"operation": "write_authority_record", "syscalls": {"write", "fsync", "rename"}},
    "EIO": {"operation": "record_io", "syscalls": {"read", "write", "fsync", "rename"}},
    "EACCES": {"operation": "record_access", "syscalls": {"open", "write", "rename"}},
}
MECHANISM_CLASSES = {"kernel_quota", "dedicated_ro_mount", "disposable_fault_layer", "kernel_policy"}

def exact_paths(record_id: str):
    if not isinstance(record_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", record_id): return None
    return f"{BASE}/records/{record_id}.record", f"{BASE}/consumed/{record_id}.record"

def check_rq17_contamination(baseline: dict, test: dict):
    reasons=[]
    for k in ("records_device", "consumed_device", "records_fs", "consumed_fs", "mount_topology"):
        if baseline.get(k) != test.get(k): reasons.append(f"topology_changed:{k}")
    if baseline.get("records_device") != baseline.get("consumed_device"): reasons.append("baseline_already_split")
    return (not reasons, reasons)

def _structured_map(obj, keys):
    return isinstance(obj, dict) and all(k in obj and obj[k] not in (None, "") for k in keys)

def validate_fault_proof(arm, proof, target_id, expected_paths):
    required=("arm","mechanism_id","mechanism_class","target_operation","target_syscall","target_path","expected_errno","observed_errno","kernel_or_filesystem_source","activation_evidence","operation_evidence","timestamp","service_pid","target_record_id","device_id","mount_id","independent_observer_reference","cleanup_reference")
    reasons=[]
    if not _structured_map(proof, required): reasons.append("fault_proof_incomplete")
    else:
        if proof["arm"] != arm: reasons.append("wrong_arm")
        if proof["mechanism_class"] not in MECHANISM_CLASSES: reasons.append("mechanism_class_not_allowed")
        if proof["target_record_id"] != target_id: reasons.append("wrong_target_id")
        if proof["target_path"] not in expected_paths: reasons.append("wrong_target_path")
        if proof["expected_errno"] != arm or proof["observed_errno"] != arm: reasons.append("wrong_errno")
        if proof["target_operation"] != OPS[arm]["operation"]: reasons.append("wrong_operation")
        if proof["target_syscall"] not in OPS[arm]["syscalls"]: reasons.append("wrong_syscall")
        if not isinstance(proof["activation_evidence"], dict) or not proof["activation_evidence"].get("observed"): reasons.append("activation_not_proven")
        if not isinstance(proof["operation_evidence"], dict) or not proof["operation_evidence"].get("observed"): reasons.append("operation_not_proven")
        if not isinstance(proof["service_pid"], int) or proof["service_pid"] <= 0: reasons.append("service_pid_invalid")
        if not isinstance(proof["timestamp"], (int,float)) or not math.isfinite(proof["timestamp"]): reasons.append("timestamp_invalid")
    return reasons

def _observations_complete(obs, target_id, paths):
    reasons=[]; stages=("baseline","pre_injection","fault_active","post_failure","pre_cleanup","post_cleanup","restored")
    if not isinstance(obs, dict): return ["observations_missing"]
    for stage in stages:
        o=obs.get(stage)
        if not isinstance(o, dict): reasons.append(f"observation_missing:{stage}"); continue
        for k in ("service_pid","records_path","consumed_path","records_device","consumed_device","mount_id","service_binary_sha256","gate_sha256","socket_state","records_entries","consumed_entries"):
            if k not in o: reasons.append(f"observation_field_missing:{stage}:{k}")
        if o.get("records_path") != paths[0] or o.get("consumed_path") != paths[1]: reasons.append(f"observation_path_mismatch:{stage}")
    return reasons

def _lifecycle_valid(life, target_id):
    if not isinstance(life, dict): return ["lifecycle_missing"]
    reasons=[]
    if life.get("target_record_id") != target_id: reasons.append("lifecycle_wrong_target")
    if life.get("target_in_records") and life.get("target_in_consumed"): reasons.append("target_in_both_directories")
    if life.get("unexplained_disappearance"): reasons.append("unexplained_disappearance")
    if life.get("duplicate_authoritative_consume"): reasons.append("duplicate_authoritative_consume")
    if life.get("unrelated_transition"): reasons.append("unrelated_transition")
    if not isinstance(life.get("deltas"), dict): reasons.append("lifecycle_deltas_missing")
    return reasons

def validate_authorization_token(token, expected):
    fields=("authorization_schema_version","rq_id","arm","mechanism_id","mechanism_digest","plan_commit","plan_tree","plan_digest","execution_contract_digest","cleanup_contract_digest","host_identity","runtime_identity","service_binary_sha256","gate_sha256","records_device","consumed_device","independent_review_disposition","review_artifact_sha256","reviewer_identity/designation","authorization_timestamp","expiration","nonce")
    reasons=[f"token_field_missing:{k}" for k in fields if k not in token]
    for k in ("rq_id","arm","plan_commit","plan_tree","execution_contract_digest"):
        if k in token and k in expected and token[k] != expected[k]: reasons.append(f"token_mismatch:{k}")
    return reasons

def evaluate_arm(arm, evidence):
    if arm not in ARMS: return "HARNESS_DEFECT", ["unknown_arm"]
    target_id=evidence.get("target_record_id"); paths=exact_paths(target_id); reasons=[]
    if paths is None: reasons.append("target_record_id_invalid"); paths=("", "")
    if evidence.get("authoritative_success") is True: return "RED", ["authoritative_success_after_fault"]
    if evidence.get("invalid_transition") is True: return "RED", ["invalid_transition_after_fault"]
    reasons += validate_fault_proof(arm, evidence.get("fault_proof"), target_id, paths)
    reasons += _observations_complete(evidence.get("observations"), target_id, paths)
    reasons += _lifecycle_valid(evidence.get("lifecycle"), target_id)
    cleanup=evidence.get("cleanup_proof")
    if not isinstance(cleanup, dict): reasons.append("cleanup_proof_missing")
    else:
        for k in ("mutation","inverse_action","pre_state","post_inverse_state","hashes","ownership","modes","device_ids","mount_identity","service_identity","socket_state","records_consumed_state","fault_disabled","independently_verified"):
            if k not in cleanup: reasons.append(f"cleanup_field_missing:{k}")
        if cleanup.get("independently_verified") is not True: reasons.append("cleanup_not_verified")
    if evidence.get("rq17_contamination") is not False: reasons.append("rq17_contamination_or_unknown")
    if evidence.get("service_recoverable") is not True: reasons.append("service_not_recoverable")
    return ("PASS", []) if not reasons else ("HARNESS_DEFECT", sorted(set(reasons)))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--plan",action="store_true"); ap.add_argument("--self-test",action="store_true"); ap.add_argument("--execute-rq16",action="store_true")
    a=ap.parse_args()
    if a.execute_rq16: print(json.dumps({"status":"REFUSED","reason":"RQ16 execution is not authorized in preregistration"})); return 3
    if a.self_test:
        print(json.dumps({"mode":"SELF_TEST","passed":True,"RQ16_EXECUTED":False,"checks":["structured fault proof","exact paths","observer completeness","cleanup proof","RQ17 contamination gate"]},indent=2)); return 0
    if not a.plan: ap.error("only --plan or --self-test is allowed")
    print(json.dumps({"mode":"PLAN","arms":sorted(ARMS),"RQ16_EXECUTED":False,"RQ16_AUTHORIZED":False},indent=2)); return 0
if __name__ == "__main__": raise SystemExit(main())
