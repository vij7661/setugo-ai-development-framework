import unittest

from qualification_guard import authorize_qualified_execution, evidence_still_admissible


def registry(**overrides):
    value = {
        "provider": "groq",
        "model": "openai/gpt-oss-20b",
        "sku": "free-tier",
        "deployment_path": "api.groq.com/openai/v1",
        "qualification_ref": "QUAL-42",
        "qualification_epoch": 7,
        "qualification_expires_epoch": 2000,
        "eligible": True,
        "revoked": False,
    }
    value.update(overrides)
    return value


def route(**overrides):
    value = {
        "provider": "groq",
        "model": "openai/gpt-oss-20b",
        "sku": "free-tier",
        "deployment_path": "api.groq.com/openai/v1",
        "qualification_ref": "QUAL-42",
        "qualification_epoch": 7,
    }
    value.update(overrides)
    return value


def evidence(**overrides):
    value = {
        "provider": "groq",
        "model": "openai/gpt-oss-20b",
        "sku": "free-tier",
        "deployment_path": "api.groq.com/openai/v1",
        "qualification_ref": "QUAL-42",
        "qualification_epoch": 7,
    }
    value.update(overrides)
    return value


class ExpFQualificationGuardTests(unittest.TestCase):
    def test_revoked_model_cannot_execute_after_routing(self):
        result = authorize_qualified_execution(route(), registry(revoked=True), now_epoch=1500)
        self.assertFalse(result["authorized"])

    def test_expired_qualification_cannot_execute(self):
        result = authorize_qualified_execution(route(), registry(qualification_expires_epoch=1500), now_epoch=1500)
        self.assertFalse(result["authorized"])

    def test_provider_or_model_replacement_invalidates_route(self):
        result = authorize_qualified_execution(route(), registry(model="replacement-model"), now_epoch=1500)
        self.assertFalse(result["authorized"])

    def test_epoch_drift_invalidates_routing_time_authorization(self):
        result = authorize_qualified_execution(route(), registry(qualification_epoch=8), now_epoch=1500)
        self.assertFalse(result["authorized"])

    def test_current_qualification_can_execute(self):
        result = authorize_qualified_execution(route(), registry(), now_epoch=1500)
        self.assertTrue(result["authorized"])

    def test_revocation_invalidates_previously_green_evidence(self):
        result = evidence_still_admissible(evidence(), registry(revoked=True))
        self.assertFalse(result["admissible"])

    def test_requalification_invalidates_old_evidence_lineage(self):
        result = evidence_still_admissible(evidence(), registry(qualification_ref="QUAL-43", qualification_epoch=8))
        self.assertFalse(result["admissible"])

    def test_current_evidence_lineage_remains_admissible(self):
        result = evidence_still_admissible(evidence(), registry())
        self.assertTrue(result["admissible"])

    def test_same_provider_model_different_sku_cannot_execute(self):
        result = authorize_qualified_execution(route(), registry(sku="enterprise"), now_epoch=1500)
        self.assertFalse(result["authorized"])
        self.assertIn("sku", result["mismatched_identity_fields"])

    def test_same_provider_model_sku_different_deployment_path_cannot_execute(self):
        result = authorize_qualified_execution(
            route(), registry(deployment_path="private-endpoint/groq-prod"), now_epoch=1500
        )
        self.assertFalse(result["authorized"])
        self.assertIn("deployment_path", result["mismatched_identity_fields"])

    def test_missing_sku_in_registry_fails_closed(self):
        current = registry()
        current.pop("sku")
        result = authorize_qualified_execution(route(), current, now_epoch=1500)
        self.assertFalse(result["authorized"])
        self.assertIn("sku", result["missing"])

    def test_missing_deployment_path_in_route_fails_closed(self):
        routed = route()
        routed.pop("deployment_path")
        result = authorize_qualified_execution(routed, registry(), now_epoch=1500)
        self.assertFalse(result["authorized"])
        self.assertIn("deployment_path", result["missing"])

    def test_old_sku_evidence_not_admissible_after_sku_change(self):
        result = evidence_still_admissible(evidence(), registry(sku="enterprise"))
        self.assertFalse(result["admissible"])
        self.assertIn("sku", result["mismatched_identity_fields"])

    def test_old_deployment_evidence_not_admissible_after_path_change(self):
        result = evidence_still_admissible(evidence(), registry(deployment_path="private-endpoint/groq-prod"))
        self.assertFalse(result["admissible"])
        self.assertIn("deployment_path", result["mismatched_identity_fields"])


if __name__ == "__main__":
    unittest.main()
