from __future__ import annotations

import unittest

from review_engine.models import ReviewerConfig, ReviewerResponse, ReviewRequest
from review_engine.orchestrator import ReviewEngine
from review_engine.qualification import QualificationRecord, QualificationRegistry


def cfg(role, ref, model):
    return ReviewerConfig(role, "p", model, "s", "api", f"{role}_KEY", f"lineage-{role}", ref)


def qual(role, ref, model, *, status="QUALIFIED", max_risk="HIGH"):
    return QualificationRecord(ref, "p", model, "s", "api", role, status, 1, f"lineage-{role}", max_risk, ("GENERAL",))


class GovernedAssuranceTests(unittest.TestCase):
    def test_unqualified_r1_is_not_invoked_in_governed_mode(self):
        calls = []
        registry = QualificationRegistry((qual("R1", "q1", "m1", status="PENDING"),))
        engine = ReviewEngine(lambda config, context: calls.append(config.role), qualification_registry=registry)
        result = engine.run(ReviewRequest("x", "hello"), r1=cfg("R1", "q1", "m1"), r2=None, r3=None)
        self.assertEqual(result.state, "HUMAN_REQUIRED")
        self.assertEqual(calls, [])
        self.assertIn("not qualified", result.reasons[0])

    def test_r2_substitution_is_blocked_before_network_call(self):
        calls = []
        registry = QualificationRegistry((
            qual("R1", "q1", "m1"),
            qual("R2", "q2", "approved-r2"),
        ))
        def invoke(config, context):
            calls.append(config.role)
            return ReviewerResponse("R1", None, "candidate", proposed_signals={"risk": "HIGH"})
        engine = ReviewEngine(invoke, qualification_registry=registry)
        result = engine.run(
            ReviewRequest("x2", "review", risk="HIGH"),
            r1=cfg("R1", "q1", "m1"),
            r2=cfg("R2", "q2", "substituted-r2"),
            r3=None,
        )
        self.assertEqual(result.state, "HUMAN_REQUIRED")
        self.assertEqual(calls, ["R1"])
        self.assertIn("binding mismatch", result.reasons[0])

    def test_risk_above_qualification_ceiling_fails_closed(self):
        registry = QualificationRegistry((qual("R1", "q1", "m1", max_risk="MEDIUM"),))
        calls = []
        engine = ReviewEngine(lambda config, context: calls.append(config.role), qualification_registry=registry)
        result = engine.run(ReviewRequest("x3", "critical", risk="CRITICAL"), r1=cfg("R1", "q1", "m1"), r2=None, r3=None)
        self.assertEqual(result.state, "HUMAN_REQUIRED")
        self.assertEqual(calls, [])


if __name__ == "__main__":
    unittest.main()
