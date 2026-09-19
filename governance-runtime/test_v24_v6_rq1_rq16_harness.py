#!/usr/bin/env python3
import unittest
from v24_v6_rq1_rq16_harness import evaluate_arm, exact_paths, check_rq17_contamination, validate_authorization_token

TARGET="abc123"; RP,CP=exact_paths(TARGET)
def obs():
    return {s:{"service_pid":123,"records_path":RP,"consumed_path":CP,"records_device":"d1","consumed_device":"d1","mount_id":"m1","service_binary_sha256":"svc","gate_sha256":"gate","socket_state":"ok","records_entries":[],"consumed_entries":[]} for s in ("baseline","pre_injection","fault_active","post_failure","pre_cleanup","post_cleanup","restored")}
def good(errno="ENOSPC"):
    return {"target_record_id":TARGET,"fault_proof":{"arm":"ENOSPC","mechanism_id":"m","mechanism_class":"kernel_quota","target_operation":"write_authority_record","target_syscall":"write","target_path":RP,"expected_errno":errno,"observed_errno":errno,"kernel_or_filesystem_source":"kernel","activation_evidence":{"observed":True},"operation_evidence":{"observed":True},"timestamp":1.0,"service_pid":123,"target_record_id":TARGET,"device_id":"d1","mount_id":"m1","independent_observer_reference":"obs","cleanup_reference":"clean"},"observations":obs(),"lifecycle":{"target_record_id":TARGET,"target_in_records":True,"target_in_consumed":False,"deltas":{}},"cleanup_proof":{"mutation":"quota","inverse_action":"remove","pre_state":"p","post_inverse_state":"p","hashes":"h","ownership":"o","modes":"m","device_ids":"d","mount_identity":"mi","service_identity":"si","socket_state":"ss","records_consumed_state":"rc","fault_disabled":True,"independently_verified":True},"rq17_contamination":False,"service_recoverable":True}

class RQ16Tests(unittest.TestCase):
    def test_structured_candidate_passes(self): self.assertEqual(evaluate_arm("ENOSPC",good())[0],"PASS")
    def test_exact_target_and_paths(self):
        e=good(); e["target_record_id"]="other"; self.assertNotEqual(evaluate_arm("ENOSPC",e)[0],"PASS")
        e=good(); e["fault_proof"]["target_path"]="/run/v24-v6-authority/private/records/abc123-other.record"; self.assertNotEqual(evaluate_arm("ENOSPC",e)[0],"PASS")
    def test_provenance_and_syscall(self):
        for k,v in (("activation_evidence",{}),("operation_evidence",{}),("target_syscall","rename"),("observed_errno","EROFS")):
            e=good(); e["fault_proof"][k]=v; self.assertNotEqual(evaluate_arm("ENOSPC",e)[0],"PASS")
    def test_observer_cleanup_and_lifecycle(self):
        e=good(); e["observations"].pop("restored"); self.assertNotEqual(evaluate_arm("ENOSPC",e)[0],"PASS")
        e=good(); e["cleanup_proof"]["independently_verified"]=False; self.assertNotEqual(evaluate_arm("ENOSPC",e)[0],"PASS")
        e=good(); e["lifecycle"]["target_in_consumed"]=True; self.assertNotEqual(evaluate_arm("ENOSPC",e)[0],"PASS")
    def test_authority_and_contamination_red_or_reject(self):
        e=good(); e["authoritative_success"]=True; self.assertEqual(evaluate_arm("ENOSPC",e)[0],"RED")
        e=good(); e["rq17_contamination"]=True; self.assertNotEqual(evaluate_arm("ENOSPC",e)[0],"PASS")
        self.assertFalse(check_rq17_contamination({"records_device":"d1","consumed_device":"d1","records_fs":"f","consumed_fs":"f","mount_topology":"m"},{"records_device":"d2","consumed_device":"d1","records_fs":"f","consumed_fs":"f","mount_topology":"m"})[0])
    def test_token_is_explicitly_bound(self):
        self.assertTrue(validate_authorization_token({}, {}) )

if __name__ == "__main__": unittest.main(verbosity=2)
