import unittest

from evidence_retention import evidence_is_admissible


def current(**overrides):
    value = {
        "project_id": "pilot1",
        "task_id": "EXP-F-RET",
        "execution_sha": "sha-current",
        "policy_epoch": 4,
        "qualification_epoch": 7,
        "capability_epoch": 9,
        "revoked_evidence_ids": [],
    }
    value.update(overrides)
    return value


def record(**overrides):
    value = {
        "evidence_id": "ev-1",
        "project_id": "pilot1",
        "task_id": "EXP-F-RET",
        "execution_sha": "sha-current",
        "policy_epoch": 4,
        "qualification_epoch": 7,
        "capability_epoch": 9,
        "issued_epoch": 100,
        "retention_until_epoch": 200,
        "invalidated": False,
    }
    value.update(overrides)
    return value


class ExpFEvidenceRetentionTests(unittest.TestCase):
    def test_current_evidence_within_retention_is_admissible(self):
        self.assertTrue(evidence_is_admissible(record(), current(), now_epoch=150)["admissible"])

    def test_expired_retention_cannot_be_replayed(self):
        result = evidence_is_admissible(record(retention_until_epoch=120), current(), now_epoch=150)
        self.assertFalse(result["admissible"])
        self.assertIn("expired", result["reason"])

    def test_policy_epoch_change_invalidates_historical_evidence(self):
        self.assertFalse(evidence_is_admissible(record(), current(policy_epoch=5), now_epoch=150)["admissible"])

    def test_execution_lineage_change_invalidates_historical_evidence(self):
        self.assertFalse(evidence_is_admissible(record(), current(execution_sha="sha-new"), now_epoch=150)["admissible"])

    def test_qualification_epoch_change_invalidates_historical_evidence(self):
        self.assertFalse(evidence_is_admissible(record(), current(qualification_epoch=8), now_epoch=150)["admissible"])

    def test_capability_epoch_change_invalidates_historical_evidence(self):
        self.assertFalse(evidence_is_admissible(record(), current(capability_epoch=10), now_epoch=150)["admissible"])

    def test_explicitly_invalidated_evidence_cannot_return(self):
        self.assertFalse(evidence_is_admissible(record(invalidated=True), current(), now_epoch=150)["admissible"])

    def test_revoked_evidence_id_cannot_return(self):
        self.assertFalse(evidence_is_admissible(record(), current(revoked_evidence_ids=["ev-1"]), now_epoch=150)["admissible"])

    def test_cross_task_historical_evidence_cannot_be_reused(self):
        self.assertFalse(evidence_is_admissible(record(task_id="other-task"), current(), now_epoch=150)["admissible"])

    def test_cross_project_historical_evidence_cannot_be_reused(self):
        self.assertFalse(evidence_is_admissible(record(project_id="other-project"), current(), now_epoch=150)["admissible"])


if __name__ == "__main__":
    unittest.main()
