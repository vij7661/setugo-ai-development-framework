import unittest

from policy_binding import authorize_policy_bound_execution, evidence_policy_admissible


class ExpFPolicyBindingTests(unittest.TestCase):
    def authority(self):
        return {
            "policy_epoch": 5,
            "policy_hash": "policy-sha-5",
            "artifact_hash": "artifact-a",
            "capability_id": "cap-1",
            "revoked": False,
        }

    def current(self):
        return {
            "policy_epoch": 5,
            "policy_hash": "policy-sha-5",
            "artifact_hash": "artifact-a",
        }

    def request(self):
        return {
            "policy_epoch": 5,
            "policy_hash": "policy-sha-5",
            "artifact_hash": "artifact-a",
            "capability_id": "cap-1",
        }

    def test_current_exact_binding_can_execute(self):
        result = authorize_policy_bound_execution(self.authority(), self.current(), self.request())
        self.assertTrue(result["authorized"])

    def test_policy_epoch_change_invalidates_authority(self):
        current = self.current(); current["policy_epoch"] = 6
        result = authorize_policy_bound_execution(self.authority(), current, self.request())
        self.assertFalse(result["authorized"])

    def test_policy_hash_change_with_same_epoch_invalidates_authority(self):
        current = self.current(); current["policy_hash"] = "policy-sha-5b"
        result = authorize_policy_bound_execution(self.authority(), current, self.request())
        self.assertFalse(result["authorized"])

    def test_artifact_change_after_authorization_fails_closed(self):
        request = self.request(); request["artifact_hash"] = "artifact-b"
        result = authorize_policy_bound_execution(self.authority(), self.current(), request)
        self.assertFalse(result["authorized"])

    def test_capability_substitution_fails_closed(self):
        request = self.request(); request["capability_id"] = "cap-2"
        result = authorize_policy_bound_execution(self.authority(), self.current(), request)
        self.assertFalse(result["authorized"])

    def test_stale_request_policy_epoch_fails_closed(self):
        request = self.request(); request["policy_epoch"] = 4
        result = authorize_policy_bound_execution(self.authority(), self.current(), request)
        self.assertFalse(result["authorized"])

    def test_stale_request_policy_hash_fails_closed(self):
        request = self.request(); request["policy_hash"] = "old-policy"
        result = authorize_policy_bound_execution(self.authority(), self.current(), request)
        self.assertFalse(result["authorized"])

    def test_revoked_authority_cannot_execute(self):
        authority = self.authority(); authority["revoked"] = True
        result = authorize_policy_bound_execution(authority, self.current(), self.request())
        self.assertFalse(result["authorized"])

    def test_evidence_bound_to_old_policy_is_not_admissible(self):
        evidence = {"valid": True, "policy_epoch": 4, "policy_hash": "old", "artifact_hash": "artifact-a"}
        self.assertFalse(evidence_policy_admissible(evidence, self.current()))

    def test_current_policy_bound_evidence_is_admissible(self):
        evidence = {"valid": True, "policy_epoch": 5, "policy_hash": "policy-sha-5", "artifact_hash": "artifact-a"}
        self.assertTrue(evidence_policy_admissible(evidence, self.current()))


if __name__ == "__main__":
    unittest.main()
