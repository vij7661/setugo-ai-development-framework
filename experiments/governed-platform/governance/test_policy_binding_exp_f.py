import unittest

from policy_binding import authorize_policy_bound_execution, evidence_policy_admissible


class ExpFPolicyBindingTests(unittest.TestCase):
    def authority(self):
        return {"policy_epoch": 5, "policy_hash": "policy-sha-5", "artifact_hash": "artifact-a", "capability_id": "cap-1", "revoked": False}

    def current(self):
        return {"policy_epoch": 5, "policy_hash": "policy-sha-5", "artifact_hash": "artifact-a"}

    def request(self):
        return {"policy_epoch": 5, "policy_hash": "policy-sha-5", "artifact_hash": "artifact-a", "capability_id": "cap-1"}

    def test_current_exact_binding_can_execute(self):
        self.assertTrue(authorize_policy_bound_execution(self.authority(), self.current(), self.request())["authorized"])

    def test_policy_epoch_change_invalidates_authority(self):
        current = self.current(); current["policy_epoch"] = 6
        self.assertFalse(authorize_policy_bound_execution(self.authority(), current, self.request())["authorized"])

    def test_policy_hash_change_with_same_epoch_invalidates_authority(self):
        current = self.current(); current["policy_hash"] = "policy-sha-5b"
        self.assertFalse(authorize_policy_bound_execution(self.authority(), current, self.request())["authorized"])

    def test_request_artifact_change_after_authorization_fails_closed(self):
        request = self.request(); request["artifact_hash"] = "artifact-b"
        self.assertFalse(authorize_policy_bound_execution(self.authority(), self.current(), request)["authorized"])

    def test_current_artifact_change_after_authorization_fails_closed(self):
        current = self.current(); current["artifact_hash"] = "artifact-b"
        result = authorize_policy_bound_execution(self.authority(), current, self.request())
        self.assertFalse(result["authorized"])
        self.assertEqual("current artifact changed after authorization", result["reason"])

    def test_stale_request_cannot_match_old_artifact_after_current_changes(self):
        current = self.current(); current["artifact_hash"] = "artifact-b"
        request = self.request()
        self.assertFalse(authorize_policy_bound_execution(self.authority(), current, request)["authorized"])

    def test_capability_substitution_fails_closed(self):
        request = self.request(); request["capability_id"] = "cap-2"
        self.assertFalse(authorize_policy_bound_execution(self.authority(), self.current(), request)["authorized"])

    def test_stale_request_policy_epoch_fails_closed(self):
        request = self.request(); request["policy_epoch"] = 4
        self.assertFalse(authorize_policy_bound_execution(self.authority(), self.current(), request)["authorized"])

    def test_stale_request_policy_hash_fails_closed(self):
        request = self.request(); request["policy_hash"] = "old-policy"
        self.assertFalse(authorize_policy_bound_execution(self.authority(), self.current(), request)["authorized"])

    def test_revoked_authority_cannot_execute(self):
        authority = self.authority(); authority["revoked"] = True
        self.assertFalse(authorize_policy_bound_execution(authority, self.current(), self.request())["authorized"])

    def test_evidence_bound_to_old_policy_is_not_admissible(self):
        evidence = {"valid": True, "policy_epoch": 4, "policy_hash": "old", "artifact_hash": "artifact-a"}
        self.assertFalse(evidence_policy_admissible(evidence, self.current()))

    def test_current_policy_bound_evidence_is_admissible(self):
        evidence = {"valid": True, "policy_epoch": 5, "policy_hash": "policy-sha-5", "artifact_hash": "artifact-a"}
        self.assertTrue(evidence_policy_admissible(evidence, self.current()))


if __name__ == "__main__": unittest.main()
