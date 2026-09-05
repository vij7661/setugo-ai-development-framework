import unittest

from qualification_guard import authorize_qualified_execution, evidence_still_admissible


def registry(**overrides):
    value = {
        "provider": "groq",
        "model": "openai/gpt-oss-20b",
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
        "qualification_ref": "QUAL-42",
        "qualification_epoch": 7,
    }
    value.update(overrides)
    return value


def evidence(**overrides):
    value = {
        "provider": "groq",
        "model": "openai/gpt-oss-20b",
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


if __name__ == "__main__":
    unittest.main()
