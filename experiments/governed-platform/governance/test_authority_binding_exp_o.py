import unittest

from authority_binding import bind_model_result_to_capability


def capability(**overrides):
    value = {
        "capability_id": "cap-review-1",
        "project_id": "pilot",
        "task_id": "EXP-O-AUTHORITY",
        "subject_id": "reviewer-a",
        "issued_epoch": 1,
        "expires_at": "2026-09-07T00:00:00Z",
        "allowed_actions": [],
        "artifact_classes": [],
        "authority_class": "NONE",
        "revoked": False,
    }
    value.update(overrides)
    return value


def result(**overrides):
    value = {
        "status": "PASS",
        "summary": "review complete",
        "findings": [],
        "authorized_scope": [],
        "changed_artifacts": [],
        "evidence_eligible": True,
    }
    value.update(overrides)
    return value


class ExternalAuthorityBindingTests(unittest.TestCase):
    def test_none_authority_stays_empty_when_model_is_compliant(self):
        bound = bind_model_result_to_capability(result(), capability())
        self.assertEqual(bound["authorized_scope"], [])
        self.assertEqual(bound["authority_binding"]["effective_actions"], [])
        self.assertEqual(bound["authority_binding"]["governance_violations"], [])
        self.assertFalse(bound["authority_binding"]["model_authority_effect"])

    def test_model_cannot_mint_release_or_write_authority(self):
        bound = bind_model_result_to_capability(
            result(authorized_scope=["production_code", "release"]), capability()
        )
        self.assertEqual(bound["authorized_scope"], [])
        self.assertEqual(
            bound["model_claimed_authorized_scope"], ["production_code", "release"]
        )
        self.assertIn(
            "MODEL_AUTHORITY_ESCALATION_ATTEMPT",
            bound["authority_binding"]["governance_violations"],
        )
        self.assertTrue(bound["governance_action_blocked"])

    def test_unsafe_authority_attempt_remains_behavioral_evidence(self):
        bound = bind_model_result_to_capability(
            result(authorized_scope=["release"]), capability()
        )
        self.assertTrue(bound["evidence_eligible"])
        self.assertTrue(bound["governance_action_blocked"])

    def test_model_change_claim_without_mutation_capability_is_blocked(self):
        bound = bind_model_result_to_capability(
            result(changed_artifacts=["src/payment.py"]), capability()
        )
        self.assertIn(
            "UNAUTHORIZED_CHANGE_CLAIM",
            bound["authority_binding"]["governance_violations"],
        )
        self.assertTrue(bound["governance_action_blocked"])

    def test_revoked_capability_fails_closed(self):
        bound = bind_model_result_to_capability(
            result(authorized_scope=["production_code"]),
            capability(
                revoked=True,
                allowed_actions=["WRITE"],
                artifact_classes=["production_code"],
            ),
        )
        self.assertEqual(bound["authorized_scope"], [])
        self.assertEqual(bound["authority_binding"]["effective_actions"], [])
        self.assertIn("CAPABILITY_REVOKED", bound["authority_binding"]["governance_violations"])
        self.assertTrue(bound["governance_action_blocked"])

    def test_malformed_capability_fails_closed(self):
        cap = capability()
        del cap["capability_id"]
        bound = bind_model_result_to_capability(result(), cap)
        self.assertEqual(bound["authorized_scope"], [])
        self.assertEqual(bound["authority_binding"]["effective_actions"], [])
        self.assertTrue(
            any(
                item.startswith("CAPABILITY_INCOMPLETE:")
                for item in bound["authority_binding"]["governance_violations"]
            )
        )

    def test_narrow_platform_scope_cannot_be_widened_by_model(self):
        cap = capability(
            authority_class="SCOPED",
            allowed_actions=["WRITE"],
            artifact_classes=["test_fixture"],
        )
        bound = bind_model_result_to_capability(
            result(authorized_scope=["test_fixture", "production_code"]), cap
        )
        self.assertEqual(bound["authorized_scope"], ["test_fixture"])
        self.assertIn(
            "MODEL_AUTHORITY_ESCALATION_ATTEMPT",
            bound["authority_binding"]["governance_violations"],
        )
        self.assertTrue(bound["governance_action_blocked"])

    def test_platform_scope_is_not_created_from_model_request(self):
        cap = capability(
            authority_class="SCOPED",
            allowed_actions=["WRITE"],
            artifact_classes=["production_code"],
        )
        bound = bind_model_result_to_capability(
            result(authorized_scope=[]), cap
        )
        self.assertEqual(bound["authorized_scope"], ["production_code"])
        self.assertEqual(bound["model_claimed_authorized_scope"], [])
        self.assertFalse(bound["authority_binding"]["model_authority_effect"])
        self.assertTrue(bound["governance_action_blocked"])
        self.assertTrue(bound["authority_binding"]["requires_use_time_capability_revalidation"])

    def test_changed_artifact_must_fit_external_scope(self):
        cap = capability(
            authority_class="SCOPED",
            allowed_actions=["WRITE"],
            artifact_classes=["test_fixture"],
        )
        bound = bind_model_result_to_capability(
            result(changed_artifacts=["production_code"]), cap
        )
        self.assertIn(
            "CHANGED_ARTIFACT_SCOPE_EXCEEDS_CAPABILITY",
            bound["authority_binding"]["governance_violations"],
        )
        self.assertTrue(bound["governance_action_blocked"])

    def test_transport_ineligible_result_does_not_become_eligible(self):
        bound = bind_model_result_to_capability(
            result(evidence_eligible=False, status="ERROR"), capability()
        )
        self.assertFalse(bound["evidence_eligible"])


if __name__ == "__main__":
    unittest.main()
