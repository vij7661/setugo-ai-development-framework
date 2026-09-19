#!/usr/bin/env python3
import copy, hashlib, unittest
from v24_v6_rq1_rq16_harness import expected_context, evaluate_arm, check_rq17_contamination, validate_authorization_token, expected_authorization_context, expected_fault_observer_context

EXPECTED=expected_context("ENOSPC"); TARGET=EXPECTED["target_record_id"]
OBSERVER=expected_fault_observer_context(); ARTIFACT_DIGEST=hashlib.sha256(b"attestation").hexdigest()
TRUSTED={"issuer_identity":"trusted-governance-authority","issuer_authority_artifact_sha256":hashlib.sha256(b"issuer").hexdigest(),"reviewer_designation":"independent-reviewer","review_artifact_sha256":hashlib.sha256(b"review").hexdigest(),"trusted_storage_identity":"root-owned-rq16-authorization","trusted_owner":"root","trusted_mode":"0600"}
def observation():
    return {s:{"target_record_id":TARGET,"target_hash":"target-hash","records_path":EXPECTED["expected_records_path"],"consumed_path":EXPECTED["expected_consumed_path"],"records_realpath":EXPECTED["expected_records_realpath"],"consumed_realpath":EXPECTED["expected_consumed_realpath"],"records_device":"d1","consumed_device":"d1","records_mount":"m1","consumed_mount":"m1","records_fs":"fs1","consumed_fs":"fs1","records_symlink":False,"consumed_symlink":False,"service_pid":42,"service_binary_sha256":"service-sha","gate_sha256":"gate-sha","socket_state":{"path":"/run/v24-v6-authority/socket","active":True},"records_entries":[TARGET+".record"],"consumed_entries":[]} for s in ("baseline","pre_injection","fault_active","post_failure","pre_cleanup","post_cleanup","restored")}
def good():
    att={"attestation_schema_version":"1","rq_id":"RQ-16","arm":"ENOSPC","mechanism_id":EXPECTED["mechanism_id"],"mechanism_digest":"mechanism-sha","service_pid":42,"service_executable_sha256":"service-sha","target_record_id":TARGET,"target_operation":"write_authority_record","target_syscall":"write","target_path":EXPECTED["expected_records_path"],"records_device":"d1","consumed_device":"d1","records_mount_id":"m1","consumed_mount_id":"m1","filesystem_identity":"fs1","fault_activation_source":"trusted-root-observer","fault_activation_raw_evidence":{"syscall":"quota-state"},"operation_raw_evidence":{"syscall":"write","errno":"ENOSPC"},"observed_errno":"ENOSPC","observation_timestamp":"2026-01-01T00:00:00Z","observer_identity":OBSERVER["observer_identity"],"observer_source_sha256":OBSERVER["observer_source_sha256"],"observer_execution_identity":OBSERVER["observer_execution_identity"],"expected_evidence_root":OBSERVER["expected_evidence_root"],"expected_owner":OBSERVER["expected_owner"],"expected_mode":OBSERVER["expected_mode"],"expected_host_identity":OBSERVER["expected_host_identity"],"expected_runtime_identity":OBSERVER["expected_runtime_identity"],"raw_artifact_path":"/var/lib/v24-rq1/rq16-attestations/a.raw","raw_artifact_sha256":ARTIFACT_DIGEST,"cleanup_reference":"clean"}
    base=copy.deepcopy(EXPECTED["expected_restoration"])
    return {"fault_proof":{"arm":"ENOSPC","mechanism_id":EXPECTED["mechanism_id"],"mechanism_class":"kernel_quota","target_operation":"write_authority_record","target_syscall":"write","target_path":EXPECTED["expected_records_path"],"expected_errno":"ENOSPC","observed_errno":"ENOSPC","kernel_or_filesystem_source":"kernel","activation_evidence":{"observed":True},"operation_evidence":{"observed":True},"timestamp":1.0,"service_pid":42,"target_record_id":TARGET,"device_id":"d1","mount_id":"m1","filesystem_identity":"fs1","independent_observer_reference":"obs","cleanup_reference":"clean"},"trusted_fault_attestation":att,"observations":observation(),"lifecycle":{"target_record_id":TARGET,"deltas":{}},"cleanup_proof":{"mechanism_id":EXPECTED["mechanism_id"],"mutation":"quota","inverse_action":"remove","pre_state":"p","post_inverse_state":"p","hashes":"h","ownership":"o","modes":"m","device_ids":"d","mount_identities":"m","filesystem_identities":"f","service_identity":"s","service_health":"ok","socket_state":"ok","records_state":"r","consumed_state":"c","fault_disabled":True,"independently_verified":True,"baseline_observation":base,"restored_observation":copy.deepcopy(base)},"service_recoverable":True}

class RQ16Tests(unittest.TestCase):
    def test_valid_structured_expected_observed_passes(self): self.assertEqual(evaluate_arm("ENOSPC",good(),EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
    def test_expected_context_required(self): self.assertNotEqual(evaluate_arm("ENOSPC",good(),None)[0],"PASS")
    def test_target_mutations_reject(self):
        for field,value in (("target_record_id","other"),("records_path","/run/v24-v6-authority/private/records/x.record"),("records_realpath","/alias"),("records_device","d2"),("records_mount","m2"),("records_fs","fs2"),("records_symlink",True)):
            e=good(); e["fault_proof"]["target_record_id" if field=="target_record_id" else "target_path" if field=="records_path" else "target_path"] = value if field in ("target_record_id","records_path") else e["fault_proof"]["target_path"]
            if field not in ("target_record_id","records_path"): e["observations"]["baseline"][field]=value
            self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
    def test_provenance_mutations_reject(self):
        for field,value in (("activation_evidence",{}),("operation_evidence",{}),("target_syscall","rename"),("observed_errno","EROFS"),("mechanism_id","fake")):
            e=good(); e["fault_proof"][field]=value; self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
        e=good(); e["trusted_fault_attestation"].pop("operation_raw_evidence"); self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
        e=good(); e["trusted_fault_attestation"]["observer_identity"]="candidate"; self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
        e=good(); e["trusted_fault_attestation"]["service_pid"]=99; self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
    def test_observer_cleanup_lifecycle_mutations_reject(self):
        e=good(); e["observations"].pop("restored"); self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
        e=good(); e["cleanup_proof"].pop("hashes"); self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
        e=good(); e["observations"]["post_failure"]["consumed_entries"]=[TARGET+".record"]; self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
        mutations=[
            ("baseline_target_missing",lambda x:x["observations"]["baseline"].update(records_entries=[])),
            ("baseline_target_already_consumed",lambda x:x["observations"]["baseline"].update(consumed_entries=[TARGET+".record"])),
            ("post_failure_target_missing_both",lambda x:x["observations"]["post_failure"].update(records_entries=[],consumed_entries=[])),
            ("post_failure_target_both",lambda x:x["observations"]["post_failure"].update(consumed_entries=[TARGET+".record"])),
            ("wrong_target_consumed",lambda x:x["observations"]["post_failure"].update(consumed_entries=["other.record"])),
            ("historical_target_consumed",lambda x:x["observations"]["post_failure"].update(consumed_entries=["historical.record"])),
            ("unrelated_target_transition",lambda x:x["observations"]["post_failure"].update(records_entries=[TARGET+".record","other.record"])),
            ("duplicate_authoritative_consumption",lambda x:x.update(authoritative_success=True)),
            ("second_authoritative_retry",lambda x:x["observations"]["post_failure"].update(response={"service_authoritative":True})),
            ("replay_state_mutation",lambda x:x["observations"]["restored"].update(records_entries=["other.record"])),
            ("target_hash_changed",lambda x:x["observations"]["post_failure"].update(target_hash="changed")),
            ("target_identity_changed",lambda x:x["observations"]["post_failure"].update(target_record_id="other")),
        ]
        for _,mut in mutations:
            e=good(); mut(e); self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
    def test_rq17_gate_cannot_be_overridden_by_boolean(self):
        e=good(); e["observations"]["fault_active"]["records_device"]="d2"; self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
        self.assertFalse(check_rq17_contamination(EXPECTED,e["observations"])[0])
    def test_cleanup_exact_baseline_comparison(self):
        fields=("service_binary_sha256","gate_sha256","records_device","consumed_device","records_mount","consumed_mount","records_fs","consumed_fs","records_realpath","consumed_realpath","owner","mode","socket_state","service_identity","security_controls","fault_state","records_entries","consumed_entries","historical_evidence")
        for field in fields:
            e=good(); e["cleanup_proof"]["restored_observation"][field]="arbitrary"; self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
        e=good(); e["cleanup_proof"].update(cleanup_ok=True); e["cleanup_proof"].pop("baseline_observation"); self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
    def test_authority_and_duplicate_transitions_red_or_reject(self):
        e=good(); e["authoritative_success"]=True; self.assertEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"RED")
        e=good(); e["observations"]["post_failure"]["consumed_entries"]=[TARGET+".record",TARGET+".record"]; self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
    def test_token_requires_durable_trusted_binding(self):
        self.assertTrue(validate_authorization_token({},EXPECTED))
        token=expected_authorization_context(EXPECTED,TRUSTED)|{"authorization_schema_version":"1","authorization_timestamp":"2026-01-01T00:00:00Z","expiration":"2026-01-01T00:30:00Z","nonce":"n1","source_path":"/root-owned/rq16-authorization","single_use_registry":"root-owned-durable-ledger"}
        metadata={"trusted_storage_identity":"root-owned-rq16-authorization","trusted_owner":"root","trusted_mode":"0600","issuer_authority_artifact_digest":TRUSTED["issuer_authority_artifact_sha256"]}
        self.assertFalse(validate_authorization_token(token,EXPECTED,now=__import__('datetime').datetime(2026,1,1,tzinfo=__import__('datetime').timezone.utc),trusted_provenance=TRUSTED,actual_file_metadata=metadata,actual_review_artifact_digest=TRUSTED["review_artifact_sha256"]))
        for field,value in (("arm","EIO"),("issuer_identity","candidate"),("nonce",""),("expiration","2025-01-01T00:00:00Z"),("authorization_timestamp","2030-01-01T00:00:00Z")):
            bad=dict(token); bad[field]=value; self.assertTrue(validate_authorization_token(bad,EXPECTED,now=__import__('datetime').datetime(2026,1,1,tzinfo=__import__('datetime').timezone.utc),trusted_provenance=TRUSTED,actual_file_metadata=metadata,actual_review_artifact_digest=TRUSTED["review_artifact_sha256"]))
        self.assertTrue(validate_authorization_token(token,EXPECTED,now=__import__('datetime').datetime(2026,1,1,tzinfo=__import__('datetime').timezone.utc),used_nonces={"n1"},trusted_provenance=TRUSTED,actual_file_metadata=metadata,actual_review_artifact_digest=TRUSTED["review_artifact_sha256"]))
    def test_cross_arm_proof_rejected(self):
        e=good(); self.assertNotEqual(evaluate_arm("EROFS",e,expected_context("EROFS"),OBSERVER,ARTIFACT_DIGEST)[0],"PASS")
    def test_absent_response_not_success(self):
        e=good(); e["lifecycle"]["deltas"]={"response":"absent"}; e["service_recoverable"]=False; self.assertNotEqual(evaluate_arm("ENOSPC",e,EXPECTED,OBSERVER,ARTIFACT_DIGEST)[0],"PASS")

if __name__=="__main__": unittest.main(verbosity=2)
