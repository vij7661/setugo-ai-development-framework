import unittest

from capability_guard import authorize_capability_use
from idempotency_guard import authorize_intent_append
from policy_binding import authorize_policy_bound_execution
from qualification_guard import authorize_qualified_execution


class CompositeAttackTests(unittest.TestCase):
    def _qualification(self):
        return {
            "provider": "p", "model": "m", "sku": "s", "deployment_path": "api/p/prod",
            "qualification_ref": "q1", "qualification_epoch": 2, "qualification_expires_epoch": 999999,
            "eligible": True, "revoked": False,
        }

    def _route(self):
        return {"provider": "p", "model": "m", "sku": "s", "deployment_path": "api/p/prod", "qualification_ref": "q1", "qualification_epoch": 2}

    def _capability(self):
        return {
            "capability_id": "cap-1", "project_id": "p1", "task_id": "t1", "subject_id": "model-1",
            "issued_epoch": 1, "expires_at": "2030-01-01T00:00:00Z", "allowed_actions": ["WRITE"],
            "artifact_classes": ["CODE"], "revoked": False,
        }

    def _request(self):
        return {"capability_id": "cap-1", "project_id": "p1", "task_id": "t1", "subject_id": "model-1", "issued_epoch": 1, "action": "WRITE", "artifact_classes": ["CODE"]}

    def _authority(self):
        return {"policy_epoch": 5, "policy_hash": "ph", "artifact_hash": "ah", "capability_id": "cap-1", "revoked": False}

    def _current(self):
        return {"policy_epoch": 5, "policy_hash": "ph", "artifact_hash": "ah"}

    def _policy_request(self):
        return {"policy_epoch": 5, "policy_hash": "ph", "artifact_hash": "ah", "capability_id": "cap-1"}

    def test_stale_qualification_plus_duplicate_retry_cannot_produce_authority(self):
        registry = self._qualification(); registry["qualification_epoch"] = 3
        q = authorize_qualified_execution(self._route(), registry, now_epoch=10)
        self.assertFalse(q["authorized"])

        state = {"state_version": 1, "intent_ledger": {}}
        command = {"actor_id": "a", "idempotency_key": "k", "intent_hash": "h", "expected_state_version": 1, "proposed_event_id": "e1"}
        first = authorize_intent_append(state, command)
        second = authorize_intent_append(first["state"], {**command, "expected_state_version": 2, "proposed_event_id": "e2"})
        self.assertTrue(first["authorized"])
        self.assertFalse(second["authorized"])
        self.assertTrue(second["duplicate"])
        self.assertFalse(q["authorized"] and second["authorized"])

    def test_revoked_capability_plus_current_artifact_drift_both_fail_closed(self):
        capability = self._capability(); capability["revoked"] = True
        cap = authorize_capability_use(capability, self._request(), "2026-09-05T00:00:00Z")
        current = self._current(); current["artifact_hash"] = "changed"
        policy = authorize_policy_bound_execution(self._authority(), current, self._policy_request())
        self.assertFalse(cap["authorized"])
        self.assertFalse(policy["authorized"])

    def test_policy_drift_plus_qualification_revocation_cannot_be_ordered_into_pass(self):
        current = self._current(); current["policy_hash"] = "new-policy"
        registry = self._qualification(); registry["revoked"] = True
        decisions = [
            authorize_policy_bound_execution(self._authority(), current, self._policy_request())["authorized"],
            authorize_qualified_execution(self._route(), registry, now_epoch=10)["authorized"],
        ]
        self.assertEqual([False, False], decisions)
        self.assertFalse(all(reversed(decisions)))

    def test_valid_composition_has_no_false_negative_control(self):
        cap = authorize_capability_use(self._capability(), self._request(), "2026-09-05T00:00:00Z")
        policy = authorize_policy_bound_execution(self._authority(), self._current(), self._policy_request())
        qual = authorize_qualified_execution(self._route(), self._qualification(), now_epoch=10)
        self.assertTrue(cap["authorized"] and policy["authorized"] and qual["authorized"])


if __name__ == "__main__": unittest.main()
