from __future__ import annotations

import unittest

from review_engine.models import ReviewFinding, ReviewerConfig, ReviewerResponse, ReviewRequest
from review_engine.orchestrator import ReviewEngine
from review_engine.qualification import QualificationRecord, QualificationRegistry


def cfg(role, ref, model):
    return ReviewerConfig(role, "p", model, "s", "api", f"{role}_KEY", f"lineage-{role}", ref)


def qual(role, ref, model, *, status="QUALIFIED", max_risk="HIGH", epoch=1):
    return QualificationRecord(ref, "p", model, "s", "api", role, status, epoch, f"lineage-{role}", max_risk, ("GENERAL",))


class GovernedAssuranceTests(unittest.TestCase):
    def test_unqualified_r1_is_not_invoked_in_governed_mode(self):
        calls = []
        registry = QualificationRegistry((qual("R1", "q1", "m1", status="PENDING"),))
        engine = ReviewEngine(lambda config, context: calls.append(config.role), qualification_registry=registry)
        result = engine.run(ReviewRequest("x", "hello"), r1=cfg("R1", "q1", "m1"), r2=None, r3=None)
        self.assertEqual(result.state, "HUMAN_REQUIRED"); self.assertEqual(calls, []); self.assertIn("not qualified", result.reasons[0])

    def test_r1_is_rechecked_if_it_discovers_higher_risk(self):
        calls = []
        registry = QualificationRegistry((qual("R1", "q1", "m1", max_risk="LOW"),))
        def invoke(config, context):
            calls.append(config.role)
            return ReviewerResponse("R1", None, "candidate", proposed_signals={"risk": "HIGH"})
        result = ReviewEngine(invoke, qualification_registry=registry).run(
            ReviewRequest("raise-risk", "apparently simple", risk="LOW"), r1=cfg("R1", "q1", "m1"), r2=None, r3=None,
        )
        self.assertEqual(result.state, "HUMAN_REQUIRED")
        self.assertEqual(calls, ["R1"])
        self.assertIn("requested risk", result.reasons[0])

    def test_r2_substitution_is_blocked_before_network_call(self):
        calls = []
        registry = QualificationRegistry((qual("R1", "q1", "m1"), qual("R2", "q2", "approved-r2")))
        def invoke(config, context):
            calls.append(config.role)
            return ReviewerResponse("R1", None, "candidate", proposed_signals={"risk": "HIGH"})
        result = ReviewEngine(invoke, qualification_registry=registry).run(
            ReviewRequest("x2", "review", risk="HIGH"),
            r1=cfg("R1", "q1", "m1"), r2=cfg("R2", "q2", "substituted-r2"), r3=None,
        )
        self.assertEqual(result.state, "HUMAN_REQUIRED"); self.assertEqual(calls, ["R1"]); self.assertIn("binding mismatch", result.reasons[0])

    def test_risk_above_qualification_ceiling_fails_closed(self):
        registry = QualificationRegistry((qual("R1", "q1", "m1", max_risk="MEDIUM"),))
        calls = []
        engine = ReviewEngine(lambda config, context: calls.append(config.role), qualification_registry=registry)
        result = engine.run(ReviewRequest("x3", "critical", risk="CRITICAL"), r1=cfg("R1", "q1", "m1"), r2=None, r3=None)
        self.assertEqual(result.state, "HUMAN_REQUIRED"); self.assertEqual(calls, [])

    def test_r1_revoked_after_r2_is_not_invoked_for_scoped_correction(self):
        r1 = cfg("R1", "q1", "m1")
        r2 = cfg("R2", "q2", "m2")
        registry = QualificationRegistry((qual("R1", "q1", "m1"), qual("R2", "q2", "m2")))
        calls = []

        def invoke(config, context):
            calls.append((config.role, context.get("mode"), context.get("phase")))
            if config.role == "R1" and context.get("mode") != "SCOPED_CORRECTION":
                return ReviewerResponse("R1", None, "stable header\nwrong claim\nstable footer")
            if config.role == "R2":
                registry.add(qual("R1", "q1", "m1", status="REVOKED", epoch=2))
                finding = ReviewFinding(
                    "r2-local",
                    "R2",
                    "HIGH",
                    True,
                    "wrong claim",
                    affected_scope=("claim:c1",),
                    first_invalid_claim="wrong claim",
                )
                return ReviewerResponse("R2", context["artifact"]["artifact_hash"], "localized defect", (finding,))
            self.fail("revoked R1 must not receive correction capability")

        decision = ReviewEngine(invoke, qualification_registry=registry).run(
            ReviewRequest("revoke-r1-correction", "material review", risk="HIGH", materiality="MATERIAL"),
            r1=r1,
            r2=r2,
            r3=None,
        )

        self.assertEqual(decision.state, "HUMAN_REQUIRED")
        self.assertEqual([role for role, _, _ in calls], ["R1", "R2"])
        self.assertIn("REVOKED", decision.reasons[0])

    def test_r3_revoked_after_phase_a_is_not_invoked_for_phase_b(self):
        r1 = cfg("R1", "q1", "m1")
        r2 = cfg("R2", "q2", "m2")
        r3 = cfg("R3", "q3", "m3")
        registry = QualificationRegistry((
            qual("R1", "q1", "m1"),
            qual("R2", "q2", "m2"),
            qual("R3", "q3", "m3"),
        ))
        calls = []

        def invoke(config, context):
            calls.append((config.role, context.get("mode"), context.get("phase")))
            if config.role == "R1" and context.get("mode") != "SCOPED_CORRECTION":
                return ReviewerResponse("R1", None, "stable header\nwrong claim\nstable footer")
            if config.role == "R2":
                finding = ReviewFinding(
                    "r2-local",
                    "R2",
                    "HIGH",
                    True,
                    "wrong claim",
                    affected_scope=("claim:c1",),
                    first_invalid_claim="wrong claim",
                )
                return ReviewerResponse("R2", context["artifact"]["artifact_hash"], "localized defect", (finding,))
            if config.role == "R1":
                return ReviewerResponse("R1", None, "stable header\nfixed claim\nstable footer")
            if context.get("phase") == "INDEPENDENT":
                registry.add(qual("R3", "q3", "m3", status="REVOKED", epoch=2))
                finding = ReviewFinding("r3-a", "R3", "HIGH", True, "material independent concern")
                return ReviewerResponse("R3", context["artifact"]["artifact_hash"], "independent concern", (finding,))
            self.fail("revoked R3 must not receive adjudication capability")

        decision = ReviewEngine(invoke, qualification_registry=registry).run(
            ReviewRequest("revoke-r3-phase-b", "material review", risk="HIGH", materiality="MATERIAL"),
            r1=r1,
            r2=r2,
            r3=r3,
        )

        self.assertEqual(decision.state, "HUMAN_REQUIRED")
        self.assertEqual(
            [(role, phase) for role, _, phase in calls],
            [("R1", None), ("R2", None), ("R1", None), ("R3", "INDEPENDENT")],
        )
        self.assertIn("REVOKED", decision.reasons[0])

    def test_revocation_immediately_before_atomic_issue_blocks_provider_call(self):
        class RevokingAtIssuanceRegistry(QualificationRegistry):
            def __init__(self):
                super().__init__((qual("R1", "q1", "m1"),))
                self._revoked_once = False

            def issue_capability(
                self,
                config,
                *,
                risk,
                task_type="GENERAL",
                request_id,
                phase,
                context_hash,
                artifact_hash=None,
            ):
                if not self._revoked_once:
                    self._revoked_once = True
                    self.add(qual("R1", "q1", "m1", status="REVOKED", epoch=2))
                return super().issue_capability(
                    config,
                    risk=risk,
                    task_type=task_type,
                    request_id=request_id,
                    phase=phase,
                    context_hash=context_hash,
                    artifact_hash=artifact_hash,
                )

        registry = RevokingAtIssuanceRegistry()
        calls = []

        def invoke(config, context):
            calls.append(config.role)
            return ReviewerResponse("R1", None, "candidate")

        decision = ReviewEngine(invoke, qualification_registry=registry).run(
            ReviewRequest("qualification-toctou", "simple review", risk="LOW"),
            r1=cfg("R1", "q1", "m1"),
            r2=None,
            r3=None,
        )

        self.assertEqual(decision.state, "HUMAN_REQUIRED")
        self.assertEqual(calls, [], "revoked qualification must not become provider capability")
        self.assertIn("REVOKED", decision.reasons[0])


if __name__ == "__main__": unittest.main()
