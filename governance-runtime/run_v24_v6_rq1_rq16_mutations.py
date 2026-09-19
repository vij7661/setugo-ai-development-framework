#!/usr/bin/env python3
import copy, json
from datetime import datetime, timezone
from v24_v6_rq1_rq16_harness import evaluate_arm, expected_context, expected_authorization_context, validate_authorization_token
from test_v24_v6_rq1_rq16_harness import good
EXPECTED=expected_context("ENOSPC")
def main():
    specs=[
      ("wrong_device",lambda e:e["observations"]["fault_active"].update(records_device="d2")),
      ("wrong_mount",lambda e:e["observations"]["fault_active"].update(records_mount="m2")),
      ("wrong_filesystem",lambda e:e["observations"]["fault_active"].update(records_fs="fs2")),
      ("symlink",lambda e:e["observations"]["fault_active"].update(records_symlink=True)),
      ("wrong_target",lambda e:e["fault_proof"].update(target_record_id="other")),
      ("wrong_syscall",lambda e:e["fault_proof"].update(target_syscall="rename")),
      ("wrong_errno",lambda e:e["fault_proof"].update(observed_errno="EROFS")),
      ("missing_activation",lambda e:e["fault_proof"].update(activation_evidence={})),
      ("missing_operation",lambda e:e["fault_proof"].update(operation_evidence={})),
      ("attestation_missing_raw_activation",lambda e:e["trusted_fault_attestation"].pop("fault_activation_raw_evidence")),
      ("attestation_missing_raw_operation",lambda e:e["trusted_fault_attestation"].pop("operation_raw_evidence")),
      ("attestation_wrong_observer",lambda e:e["trusted_fault_attestation"].update(observer_identity="candidate")),
      ("attestation_wrong_pid",lambda e:e["trusted_fault_attestation"].update(service_pid=99)),
      ("attestation_wrong_artifact_hash",lambda e:e["trusted_fault_attestation"].update(raw_artifact_sha256="fake")),
      ("missing_observer",lambda e:e["observations"].pop("restored")),
      ("bool_only_observer",lambda e:e.pop("observations")),
      ("missing_cleanup",lambda e:e.pop("cleanup_proof")),
      ("bool_only_cleanup",lambda e:(e.pop("cleanup_proof"),e.update(cleanup_verified=True,restored=True))),
      ("duplicate_consume",lambda e:e["observations"]["post_failure"].update(consumed_entries=["abc123.record","abc123.record"])),
      ("both_directories",lambda e:e["observations"]["post_failure"].update(consumed_entries=["abc123.record"])),
      ("rq17_false_but_changed",lambda e:e["observations"]["fault_active"].update(records_device="d2")),
      ("authoritative_success",lambda e:e.update(authoritative_success=True)),
      ("invalid_transition",lambda e:e.update(invalid_transition=True)),
      ("untrusted_expected_context",lambda e:e["fault_proof"].update(mechanism_id="fake")),
      ("cleanup_service_hash",lambda e:e["cleanup_proof"]["restored_observation"].update(service_binary_sha256="bad")),
      ("cleanup_gate_hash",lambda e:e["cleanup_proof"]["restored_observation"].update(gate_sha256="bad")),
      ("cleanup_mode",lambda e:e["cleanup_proof"]["restored_observation"].update(mode="0777")),
      ("cleanup_owner",lambda e:e["cleanup_proof"]["restored_observation"].update(owner="candidate")),
      ("cleanup_socket",lambda e:e["cleanup_proof"]["restored_observation"].update(socket_state="changed")),
      ("cleanup_fault_active",lambda e:e["cleanup_proof"].update(fault_disabled=False)),
      ("cleanup_target_state",lambda e:e["cleanup_proof"]["restored_observation"].update(records_entries=[])),
      ("cleanup_historical_evidence",lambda e:e["cleanup_proof"]["restored_observation"].update(historical_evidence="changed")),
      ("cleanup_missing_restored",lambda e:e["cleanup_proof"].update(restored_observation={})),
    ]
    rows=[]
    for name,mut in specs:
        e=copy.deepcopy(good()); mut(e); actual,reasons=evaluate_arm("ENOSPC",e,EXPECTED)
        rows.append({"mutation_id":name,"case":"ENOSPC","path":name,"before":"valid","after":"mutated","expected_result":"REJECT","actual_result":actual,"reasons":reasons,"rejected":actual!="PASS"})
    token=expected_authorization_context(EXPECTED)|{"authorization_timestamp":"2026-01-01T00:00:00Z","expiration":"2026-01-01T00:30:00Z","nonce":"n1","source_path":"/root-owned/rq16-authorization","single_use_registry":"root-owned-durable-ledger"}
    auth_fields=["arm","mechanism_id","mechanism_digest","plan_commit","plan_tree","plan_digest","execution_contract_digest","cleanup_contract_digest","host_identity","runtime_identity","service_binary_sha256","gate_sha256","records_device","consumed_device","records_mount_id","consumed_mount_id","independent_review_disposition","review_artifact_sha256","reviewer_designation","issuer_identity","issuer_authority_artifact_sha256"]
    for field in auth_fields:
        bad=dict(token); bad[field]="mutated"; reasons=validate_authorization_token(bad,EXPECTED,now=datetime(2026,1,1,tzinfo=timezone.utc)); rows.append({"mutation_id":"auth_"+field,"case":"AUTHORIZATION","path":field,"before":"valid","after":"mutated","expected_result":"REJECT","actual_result":"REJECT" if reasons else "PASS","reasons":reasons,"rejected":bool(reasons)})
    for name,field,value in (("expired","expiration","2025-01-01T00:00:00Z"),("future_issued","authorization_timestamp","2030-01-01T00:00:00Z"),("malformed_timestamp","expiration","bad"),("empty_nonce","nonce",""),("reused_nonce","nonce","used"),("untrusted_source","source_path","candidate"),("untrusted_registry","single_use_registry","memory")):
        bad=dict(token); bad[field]=value; used={"used"} if name=="reused_nonce" else None; reasons=validate_authorization_token(bad,EXPECTED,now=datetime(2026,1,1,tzinfo=timezone.utc),used_nonces=used); rows.append({"mutation_id":"auth_"+name,"case":"AUTHORIZATION","path":field,"before":"valid","after":value,"expected_result":"REJECT","actual_result":"REJECT" if reasons else "PASS","reasons":reasons,"rejected":bool(reasons)})
    out={"total_mutations":len(rows),"rejected_mutations":sum(r["rejected"] for r in rows),"surviving_mutations":sum(not r["rejected"] for r in rows),"all_rejected":all(r["rejected"] for r in rows),"mutations":rows,"RQ16_EXECUTED":False}
    print(json.dumps(out,indent=2,sort_keys=True)); return 0 if out["all_rejected"] else 2
if __name__=="__main__": raise SystemExit(main())
