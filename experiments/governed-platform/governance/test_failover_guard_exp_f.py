import unittest

from failover_guard import authorize_failover


class ExpFFailoverGuardTests(unittest.TestCase):
    def setUp(self):
        self.original = {
            "provider": "groq",
            "model": "builder-a",
            "sku": "prod-a",
            "deployment_path": "api/groq/prod-a",
            "role": "BUILDER",
            "task_class": "CODE_CHANGE",
            "privacy_class": "external-approved",
            "policy_hash": "policy-v1",
        }
        self.candidate = {
            "provider": "mistral",
            "model": "builder-b",
            "sku": "prod-b",
            "deployment_path": "api/mistral/prod-b",
            "role": "BUILDER",
            "task_class": "CODE_CHANGE",
            "privacy_class": "external-approved",
            "policy_hash": "policy-v1",
            "qualification_id": "qual-b",
            "qualification_epoch": 3,
        }
        self.qualification = {
            **self.candidate,
            "status": "QUALIFIED",
        }

    def test_current_exact_qualified_failover_is_allowed(self):
        self.assertTrue(authorize_failover(self.original, self.candidate, self.qualification)["authorized"])

    def test_unqualified_candidate_is_denied(self):
        q = dict(self.qualification, status="UNQUALIFIED")
        self.assertFalse(authorize_failover(self.original, self.candidate, q)["authorized"])

    def test_sku_substitution_is_denied(self):
        q = dict(self.qualification, sku="different-sku")
        self.assertFalse(authorize_failover(self.original, self.candidate, q)["authorized"])

    def test_deployment_path_substitution_is_denied(self):
        q = dict(self.qualification, deployment_path="api/mistral/other")
        self.assertFalse(authorize_failover(self.original, self.candidate, q)["authorized"])

    def test_model_substitution_is_denied(self):
        q = dict(self.qualification, model="different-model")
        self.assertFalse(authorize_failover(self.original, self.candidate, q)["authorized"])

    def test_provider_substitution_is_denied(self):
        q = dict(self.qualification, provider="different-provider")
        self.assertFalse(authorize_failover(self.original, self.candidate, q)["authorized"])

    def test_role_substitution_is_denied(self):
        c = dict(self.candidate, role="JUDGE")
        q = dict(self.qualification, role="JUDGE")
        self.assertFalse(authorize_failover(self.original, c, q)["authorized"])

    def test_task_class_substitution_is_denied(self):
        c = dict(self.candidate, task_class="ARCH_REVIEW")
        q = dict(self.qualification, task_class="ARCH_REVIEW")
        self.assertFalse(authorize_failover(self.original, c, q)["authorized"])

    def test_privacy_class_downgrade_is_denied(self):
        c = dict(self.candidate, privacy_class="external-unapproved")
        q = dict(self.qualification, privacy_class="external-unapproved")
        self.assertFalse(authorize_failover(self.original, c, q)["authorized"])

    def test_policy_binding_change_is_denied(self):
        c = dict(self.candidate, policy_hash="policy-v2")
        q = dict(self.qualification, policy_hash="policy-v2")
        self.assertFalse(authorize_failover(self.original, c, q)["authorized"])

    def test_qualification_task_scope_mismatch_is_denied(self):
        q = dict(self.qualification, task_class="ARCH_REVIEW")
        self.assertFalse(authorize_failover(self.original, self.candidate, q)["authorized"])

    def test_qualification_privacy_scope_mismatch_is_denied(self):
        q = dict(self.qualification, privacy_class="internal-only")
        self.assertFalse(authorize_failover(self.original, self.candidate, q)["authorized"])

    def test_qualification_policy_scope_mismatch_is_denied(self):
        q = dict(self.qualification, policy_hash="policy-v2")
        self.assertFalse(authorize_failover(self.original, self.candidate, q)["authorized"])

    def test_missing_sku_fails_closed(self):
        c = dict(self.candidate)
        del c["sku"]
        self.assertFalse(authorize_failover(self.original, c, self.qualification)["authorized"])

    def test_missing_deployment_path_fails_closed(self):
        c = dict(self.candidate)
        del c["deployment_path"]
        self.assertFalse(authorize_failover(self.original, c, self.qualification)["authorized"])


if __name__ == "__main__":
    unittest.main()
