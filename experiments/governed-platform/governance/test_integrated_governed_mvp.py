from copy import deepcopy
import unittest

from integrated_governed_mvp import evaluate_governed_execution


class IntegratedGovernedMVPTests(unittest.TestCase):
    def setUp(self):
        self.route = {
            "provider": "groq",
            "model": "model-a",
            "sku": "sku-a",
            "deployment_path": "api-a",
            "qualification_ref": "q-1",
            "qualification_epoch": 7,
        }
        self.registry = {
            **self.route,
            "qualification_expires_epoch": 100,
            "eligible": True,
            "revoked": False,
        }
        self.capability = {
            "capability_id": "cap-1",
            "project_id": "p-1",
            "task_id": "t-1",
            "subject_id": "worker-1",
            "issued_epoch": 3,
            "expires_at": "2030-01-01T00:00:00Z",
            "allowed_actions": ["WRITE", "RELEASE", "DEPLOY", "MERGE"],
            "artifact_classes": ["CODE", "TEST"],
            "revoked": False,
        }
        self.request = {
            "capability_id": "cap-1",
            "project_id": "p-1",
            "task_id": "t-1",
            "subject_id": "worker-1",
            "issued_epoch": 3,
            "action": "WRITE",
            "artifact_classes": ["CODE"],
        }
        self.model_result = {
            "evidence_eligible": True,
            "authorized_scope": ["CODE"],
            "changed_artifacts": ["CODE"],
            "review_requested": False,
        }
        self.review_gate = {"state": "CLEAR", "evidence_refs": ["ev-1"]}

    def evaluate(self, **overrides):
        values = {
            "route": deepcopy(self.route),
            "registry_entry": deepcopy(self.registry),
            "normalized_model_result": deepcopy(self.model_result),
            "capability": deepcopy(self.capability),
            "execution_request": deepcopy(self.request),
            "review_gate": deepcopy(self.review_gate),
            "now_epoch": 10,
            "now_iso": "2026-09-07T00:00:00Z",
        }
        values.update(overrides)
        return evaluate_governed_execution(**values)

    def test_mvp_01_clean_exact_scoped_write_authorizes_isolated_execution_only(self):
        result = self.evaluate()
        self.assertEqual(result["decision"], "AUTHORIZED_FOR_ISOLATED_EXECUTION")
        self.assertTrue(result["consequential_execution_authorized"])
        self.assertFalse(result["release_completion_authority"])

    def test_mvp_02_each_execution_identity_substitution_denies(self):
        for field in ("provider", "model", "sku", "deployment_path"):
            with self.subTest(field=field):
                route = deepcopy(self.route)
                route[field] += "-substituted"
                self.assertEqual(self.evaluate(route=route)["decision"], "DENY_QUALIFICATION")

    def test_mvp_03_qualification_epoch_drift_revocation_and_expiry_deny(self):
        route = deepcopy(self.route)
        route["qualification_epoch"] = 6
        self.assertEqual(self.evaluate(route=route)["decision"], "DENY_QUALIFICATION")
        registry = deepcopy(self.registry)
        registry["revoked"] = True
        self.assertEqual(self.evaluate(registry_entry=registry)["decision"], "DENY_QUALIFICATION")
        self.assertEqual(self.evaluate(now_epoch=100)["decision"], "DENY_QUALIFICATION")

    def test_mvp_04_model_scope_widening_is_evidence_not_authority(self):
        model = deepcopy(self.model_result)
        model["authorized_scope"] = ["CODE", "SECRETS"]
        result = self.evaluate(normalized_model_result=model)
        self.assertEqual(result["decision"], "DENY_AUTHORITY_BINDING")
        self.assertIn("MODEL_AUTHORITY_ESCALATION_ATTEMPT", result["authority_binding"]["governance_violations"])
        self.assertFalse(result["authority_binding"]["model_authority_effect"])

    def test_mvp_05_revoked_and_expired_capabilities_deny_at_use_time(self):
        cap = deepcopy(self.capability)
        cap["revoked"] = True
        self.assertEqual(self.evaluate(capability=cap)["decision"], "DENY_AUTHORITY_BINDING")
        cap = deepcopy(self.capability)
        cap["expires_at"] = "2026-01-01T00:00:00Z"
        self.assertEqual(self.evaluate(capability=cap)["decision"], "DENY_CAPABILITY")

    def test_mvp_06_action_and_artifact_widening_deny(self):
        request = deepcopy(self.request)
        request["action"] = "DELETE"
        self.assertEqual(self.evaluate(execution_request=request)["decision"], "DENY_CAPABILITY")
        request = deepcopy(self.request)
        request["artifact_classes"] = ["CODE", "SECRETS"]
        self.assertEqual(self.evaluate(execution_request=request)["decision"], "DENY_CAPABILITY")

    def test_mvp_07_human_required_cannot_be_bypassed_by_model_success_or_skip_request(self):
        model = deepcopy(self.model_result)
        model["status"] = "SUCCESS"
        model["skip_review"] = True
        result = self.evaluate(normalized_model_result=model, review_gate={"state": "HUMAN_REQUIRED", "evidence_refs": ["ev-1"]})
        self.assertEqual(result["decision"], "HUMAN_REQUIRED")
        self.assertFalse(result["consequential_execution_authorized"])

    def test_mvp_08_review_required_does_not_execute(self):
        result = self.evaluate(review_gate={"state": "REVIEW_REQUIRED", "evidence_refs": ["ev-r2"]})
        self.assertEqual(result["decision"], "REVIEW_REQUIRED")
        self.assertFalse(result["consequential_execution_authorized"])

    def test_mvp_09_terminal_actions_always_require_separate_external_gate(self):
        for action in ("RELEASE", "DEPLOY", "MERGE"):
            with self.subTest(action=action):
                request = deepcopy(self.request)
                request["action"] = action
                result = self.evaluate(execution_request=request)
                self.assertEqual(result["decision"], "TERMINAL_AUTHORITY_REQUIRED")
                self.assertFalse(result["release_completion_authority"])

    def test_mvp_10_unsafe_model_authority_attempt_retains_evidence_eligibility(self):
        model = deepcopy(self.model_result)
        model["authorized_scope"] = ["CODE", "SECRETS"]
        result = self.evaluate(normalized_model_result=model)
        self.assertEqual(result["decision"], "DENY_AUTHORITY_BINDING")
        self.assertFalse(result["authority_binding"]["model_authority_effect"])

    def test_mvp_11_malformed_review_gate_fails_closed(self):
        self.assertEqual(self.evaluate(review_gate={"state": "MODEL_SAYS_CLEAR", "evidence_refs": []})["decision"], "HUMAN_REQUIRED")
        self.assertEqual(self.evaluate(review_gate={"state": "CLEAR", "evidence_refs": "ev-1"})["decision"], "HUMAN_REQUIRED")

    def test_mvp_12_clean_replay_is_deterministic(self):
        first = self.evaluate()
        second = self.evaluate()
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
