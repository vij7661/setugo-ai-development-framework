import unittest

from capability_guard import authorize_capability_use, evidence_from_capability_is_admissible


def capability(**overrides):
    value = {
        "capability_id": "cap-1",
        "project_id": "pilot1",
        "task_id": "EXP-F-CAP",
        "subject_id": "builder-a",
        "issued_epoch": 7,
        "expires_at": "2026-09-05T08:30:00Z",
        "allowed_actions": ["WRITE"],
        "artifact_classes": ["production_code"],
        "revoked": False,
    }
    value.update(overrides)
    return value


def request(**overrides):
    value = {
        "capability_id": "cap-1",
        "project_id": "pilot1",
        "task_id": "EXP-F-CAP",
        "subject_id": "builder-a",
        "issued_epoch": 7,
        "action": "WRITE",
        "artifact_classes": ["production_code"],
    }
    value.update(overrides)
    return value


class ExpFCapabilityGuardTests(unittest.TestCase):
    def test_current_scoped_capability_allows_only_bound_action(self):
        result = authorize_capability_use(capability(), request(), "2026-09-05T08:00:00Z")
        self.assertTrue(result["authorized"])

    def test_expired_capability_cannot_be_used(self):
        result = authorize_capability_use(capability(), request(), "2026-09-05T08:30:00Z")
        self.assertFalse(result["authorized"])
        self.assertIn("expired", result["reason"])

    def test_revoked_capability_cannot_be_used(self):
        result = authorize_capability_use(capability(revoked=True), request(), "2026-09-05T08:00:00Z")
        self.assertFalse(result["authorized"])

    def test_model_cannot_widen_artifact_scope(self):
        result = authorize_capability_use(
            capability(), request(artifact_classes=["production_code", "ci"]), "2026-09-05T08:00:00Z"
        )
        self.assertFalse(result["authorized"])

    def test_model_cannot_change_action_type(self):
        result = authorize_capability_use(capability(), request(action="DEPLOY"), "2026-09-05T08:00:00Z")
        self.assertFalse(result["authorized"])

    def test_capability_cannot_cross_task_boundary(self):
        result = authorize_capability_use(capability(), request(task_id="EXP-F-OTHER"), "2026-09-05T08:00:00Z")
        self.assertFalse(result["authorized"])

    def test_capability_epoch_change_invalidates_old_request(self):
        result = authorize_capability_use(capability(issued_epoch=8), request(issued_epoch=7), "2026-09-05T08:00:00Z")
        self.assertFalse(result["authorized"])

    def test_revoked_capability_invalidates_prior_evidence(self):
        evidence = request()
        self.assertFalse(evidence_from_capability_is_admissible(evidence, capability(revoked=True)))

    def test_reissued_capability_invalidates_old_evidence_lineage(self):
        evidence = request()
        current = capability(capability_id="cap-2", issued_epoch=8)
        self.assertFalse(evidence_from_capability_is_admissible(evidence, current))

    def test_current_capability_evidence_lineage_is_admissible(self):
        evidence = request()
        self.assertTrue(evidence_from_capability_is_admissible(evidence, capability()))


if __name__ == "__main__":
    unittest.main()
