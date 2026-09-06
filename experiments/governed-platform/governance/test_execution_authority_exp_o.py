import unittest

from authority_binding import bind_model_result_to_capability
from execution_authority import authorize_bound_execution


NOW = "2026-09-06T04:00:00Z"


def capability(**overrides):
    value = {
        "capability_id": "cap-exec-1",
        "project_id": "pilot",
        "task_id": "EXP-O-AUTHORITY",
        "subject_id": "builder-a",
        "issued_epoch": 3,
        "expires_at": "2026-09-07T00:00:00Z",
        "allowed_actions": ["WRITE"],
        "artifact_classes": ["test_fixture"],
        "authority_class": "SCOPED",
        "revoked": False,
    }
    value.update(overrides)
    return value


def model_result(**overrides):
    value = {
        "status": "PASS",
        "summary": "diagnosis complete",
        "findings": [],
        "authorized_scope": [],
        "changed_artifacts": [],
        "evidence_eligible": True,
    }
    value.update(overrides)
    return value


def request(**overrides):
    value = {
        "capability_id": "cap-exec-1",
        "project_id": "pilot",
        "task_id": "EXP-O-AUTHORITY",
        "subject_id": "builder-a",
        "issued_epoch": 3,
        "action": "WRITE",
        "artifact_classes": ["test_fixture"],
    }
    value.update(overrides)
    return value


class UseTimeExternalAuthorityTests(unittest.TestCase):
    def test_clean_scoped_capability_can_authorize_only_at_use_time(self):
        bound = bind_model_result_to_capability(model_result(), capability())
        self.assertTrue(bound["governance_action_blocked"])
        decision = authorize_bound_execution(bound, capability(), request(), NOW)
        self.assertTrue(decision["authorized"])
        self.assertEqual(decision["authority_source"], "PLATFORM_CAPABILITY")

    def test_none_capability_cannot_execute_model_claimed_write(self):
        cap = capability(allowed_actions=[], artifact_classes=[], authority_class="NONE")
        bound = bind_model_result_to_capability(
            model_result(authorized_scope=["test_fixture"]), cap
        )
        decision = authorize_bound_execution(bound, cap, request(), NOW)
        self.assertFalse(decision["authorized"])

    def test_model_scope_escalation_blocks_use_even_when_capability_has_some_write_scope(self):
        cap = capability()
        bound = bind_model_result_to_capability(
            model_result(authorized_scope=["test_fixture", "production_code"]), cap
        )
        decision = authorize_bound_execution(bound, cap, request(), NOW)
        self.assertFalse(decision["authorized"])
        self.assertIn("MODEL_AUTHORITY_ESCALATION_ATTEMPT", decision["governance_violations"])

    def test_capability_revocation_after_binding_blocks_use(self):
        cap = capability()
        bound = bind_model_result_to_capability(model_result(), cap)
        revoked = capability(revoked=True)
        decision = authorize_bound_execution(bound, revoked, request(), NOW)
        self.assertFalse(decision["authorized"])
        self.assertIn("revoked", decision["reason"])

    def test_capability_epoch_change_after_binding_blocks_use(self):
        cap = capability()
        bound = bind_model_result_to_capability(model_result(), cap)
        reissued = capability(capability_id="cap-exec-2", issued_epoch=4)
        decision = authorize_bound_execution(bound, reissued, request(), NOW)
        self.assertFalse(decision["authorized"])
        self.assertIn("changed", decision["reason"])

    def test_expired_capability_blocks_use(self):
        cap = capability(expires_at="2026-09-06T03:59:59Z")
        bound = bind_model_result_to_capability(model_result(), cap)
        decision = authorize_bound_execution(bound, cap, request(), NOW)
        self.assertFalse(decision["authorized"])
        self.assertIn("expired", decision["reason"])

    def test_action_widening_is_denied(self):
        cap = capability()
        bound = bind_model_result_to_capability(model_result(), cap)
        decision = authorize_bound_execution(bound, cap, request(action="RELEASE"), NOW)
        self.assertFalse(decision["authorized"])
        self.assertIn("exceeds", decision["reason"])

    def test_artifact_widening_is_denied(self):
        cap = capability()
        bound = bind_model_result_to_capability(model_result(), cap)
        decision = authorize_bound_execution(
            bound, cap, request(artifact_classes=["test_fixture", "production_code"]), NOW
        )
        self.assertFalse(decision["authorized"])
        self.assertIn("exceed", decision["reason"])

    def test_cross_task_request_is_denied(self):
        cap = capability()
        bound = bind_model_result_to_capability(model_result(), cap)
        decision = authorize_bound_execution(bound, cap, request(task_id="EXP-O-OTHER"), NOW)
        self.assertFalse(decision["authorized"])
        self.assertIn("binding mismatch", decision["reason"])

    def test_missing_binding_fails_closed(self):
        decision = authorize_bound_execution(model_result(), capability(), request(), NOW)
        self.assertFalse(decision["authorized"])
        self.assertIn("binding missing", decision["reason"])

    def test_forged_pre_authorization_flag_fails_closed(self):
        bound = bind_model_result_to_capability(model_result(), capability())
        bound["authority_binding"]["consequential_execution_authorized"] = True
        decision = authorize_bound_execution(bound, capability(), request(), NOW)
        self.assertFalse(decision["authorized"])
        self.assertIn("must not pre-authorize", decision["reason"])


if __name__ == "__main__":
    unittest.main()
