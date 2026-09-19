#!/usr/bin/env python3
import unittest
from v24_v6_rq1_rq16_harness import evaluate_arm

def good(errno="ENOSPC"):
    return {"fault_proof":{"injected":True,"errno":errno},"target_path":"/run/v24-v6-authority/private/records/T.record","observer_ok":True,"cleanup_verified":True,"restored_exact":True,"service_recoverable":True,"lifecycle_explained":True}

class RQ16SelfTests(unittest.TestCase):
    def test_valid_evidence_is_only_candidate_pass(self): self.assertEqual(evaluate_arm("ENOSPC", good())[0], "PASS")
    def test_missing_or_wrong_fault_proof_never_passes(self):
        for ev in ({**good(), "fault_proof":{"injected":False,"errno":"ENOSPC"}}, {**good(), "fault_proof":{"injected":True,"errno":"EROFS"}}, {**good(), "observer_ok":False}): self.assertNotEqual(evaluate_arm("ENOSPC", ev)[0], "PASS")
    def test_authority_and_cleanup_fail_closed(self):
        self.assertEqual(evaluate_arm("ENOSPC", {**good(), "authoritative_success":True})[0], "RED")
        self.assertNotEqual(evaluate_arm("ENOSPC", {**good(), "cleanup_verified":False})[0], "PASS")
    def test_arms_cannot_substitute(self):
        self.assertNotEqual(evaluate_arm("EROFS", good("ENOSPC"))[0], "PASS")
        self.assertNotEqual(evaluate_arm("EIO", good("ENOSPC"))[0], "PASS")
        self.assertNotEqual(evaluate_arm("EACCES", good("EIO"))[0], "PASS")
    def test_absent_response_is_not_success(self): self.assertNotEqual(evaluate_arm("ENOSPC", {**good(), "lifecycle_explained":False})[0], "PASS")

if __name__ == "__main__": unittest.main(verbosity=2)
