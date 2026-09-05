from __future__ import annotations

import unittest

from review_engine.models import ReviewFinding, ReviewerConfig, ReviewerResponse, ReviewRequest
from review_engine.orchestrator import ReviewEngine
from review_engine.qualification import QualificationRecord, QualificationRegistry


def cfg(role: str, lineage: str) -> ReviewerConfig:
    return ReviewerConfig(
        role=role,
        provider=f"p-{role.lower()}",
        model=f"m-{role.lower()}",
        sku="default",
        deployment_path="api",
        api_key_env=f"{role}_KEY",
        foundation_lineage=lineage,
        qualification_ref=f"q-{role.lower()}",
    )


def registry(*configs: ReviewerConfig) -> QualificationRegistry:
    return QualificationRegistry(tuple(
        QualificationRecord(
            qualification_ref=config.qualification_ref or f"q-{config.role.lower()}",
            provider=config.provider,
            model=config.model,
            sku=config.sku,
            deployment_path=config.deployment_path,
            role=config.role,
            status="QUALIFIED",
            qualification_epoch=1,
            foundation_lineage=config.foundation_lineage,
            max_risk="CRITICAL",
            task_types=("*",),
        )
        for config in configs
    ))


class CaptureSessions:
    def __init__(self) -> None:
        self.events: list[tuple[str, str, dict]] = []

    def append(self, session_id: str, event_type: str, payload: dict) -> None:
        self.events.append((session_id, event_type, payload))

    def last_payload(self, event_type: str) -> dict:
        matches = [payload for _, kind, payload in self.events if kind == event_type]
        if not matches:
            raise AssertionError(f"missing event {event_type}")
        return matches[-1]


class R3AdjudicationClosureTests(unittest.TestCase):
    def _run(self, phase_a_findings, phase_b_factory):
        r1 = cfg("R1", "lineage-r1")
        r2 = cfg("R2", "lineage-r2")
        r3 = cfg("R3", "lineage-r3")
        sessions = CaptureSessions()
        calls: list[tuple[str, str | None]] = []

        def invoke(config, context):
            calls.append((config.role, context.get("phase")))
            if config.role == "R1" and context.get("mode") != "SCOPED_CORRECTION":
                return ReviewerResponse("R1", None, "stable header\nwrong claim\nstable footer")
            if config.role == "R2":
                finding = ReviewFinding(
                    "r2-local",
                    "R2",
                    "HIGH",
                    True,
                    "wrong claim violates invariant",
                    affected_scope=("claim:c1",),
                    first_invalid_claim="wrong claim",
                )
                return ReviewerResponse("R2", context["artifact"]["artifact_hash"], "localized defect", (finding,))
            if config.role == "R1":
                return ReviewerResponse("R1", None, "stable header\nfixed claim\nstable footer")
            if context["phase"] == "INDEPENDENT":
                self.assertNotIn("prior_reviews", context)
                return ReviewerResponse(
                    "R3",
                    context["artifact"]["artifact_hash"],
                    "frozen independent view",
                    tuple(phase_a_findings),
                )
            return phase_b_factory(context)

        engine = ReviewEngine(
            invoke,
            session_store=sessions,
            qualification_registry=registry(r1, r2, r3),
        )
        decision = engine.run(
            ReviewRequest(
                "r3-closure-test",
                "material change",
                risk="HIGH",
                materiality="MATERIAL",
            ),
            r1=r1,
            r2=r2,
            r3=r3,
        )
        return decision, calls, sessions

    @staticmethod
    def _phase_a(finding_id: str = "r3-a", summary: str = "independent material concern") -> ReviewFinding:
        return ReviewFinding(finding_id, "R3", "HIGH", True, summary)

    def test_phase_a_material_finding_cannot_disappear_by_phase_b_omission(self):
        def phase_b(context):
            self.assertEqual(context["frozen_material_findings"][0]["finding_id"], "r3-a")
            return ReviewerResponse("R3", context["artifact_hash"], "claims resolved but names nothing")

        decision, calls, sessions = self._run((self._phase_a(),), phase_b)

        self.assertEqual(decision.state, "HUMAN_REQUIRED")
        self.assertIn("explicit staged R3 closure", decision.reasons[0])
        self.assertIn("independent material concern", decision.dissent)
        self.assertEqual([phase for role, phase in calls if role == "R3"], ["INDEPENDENT", "ADJUDICATION"])
        payload = sessions.last_payload("R3_ADJUDICATION_COMPLETED")
        self.assertEqual(payload["frozen_material_finding_ids"], ["r3-a"])
        self.assertEqual(payload["resolved_finding_ids"], [])
        self.assertEqual(payload["unclosed_frozen_finding_ids"], ["r3-a"])

    def test_exact_explicit_closure_can_converge_when_no_material_finding_remains(self):
        def phase_b(context):
            self.assertEqual(context["frozen_material_findings"][0]["finding_id"], "r3-a")
            return ReviewerResponse(
                "R3",
                context["artifact_hash"],
                "resolved against disclosed evidence",
                resolved_finding_ids=("r3-a",),
            )

        decision, _, sessions = self._run((self._phase_a(),), phase_b)

        self.assertEqual(decision.state, "CONVERGED_PASS")
        self.assertIn("explicitly closed every frozen material finding", decision.reasons[0])
        payload = sessions.last_payload("R3_ADJUDICATION_COMPLETED")
        self.assertEqual(payload["resolved_finding_ids"], ["r3-a"])
        self.assertEqual(payload["unclosed_frozen_finding_ids"], [])
        self.assertEqual(payload["invalid_resolution_ids"], [])
        self.assertEqual(payload["unresolved_finding_ids"], [])

    def test_phase_b_receives_exact_revised_artifact_not_hash_only(self):
        def phase_b(context):
            artifact = context["artifact"]
            self.assertEqual(artifact["artifact_id"], "r3-closure-test:artifact")
            self.assertEqual(artifact["version"], 2)
            self.assertEqual(artifact["content"], "stable header\nfixed claim\nstable footer")
            self.assertEqual(artifact["artifact_hash"], context["artifact_hash"])
            self.assertTrue(context["instructions"]["artifact_content_is_exact_frozen_revision"])
            return ReviewerResponse(
                "R3",
                artifact["artifact_hash"],
                "resolved while viewing exact revised artifact",
                resolved_finding_ids=("r3-a",),
            )

        decision, _, _ = self._run((self._phase_a(),), phase_b)
        self.assertEqual(decision.state, "CONVERGED_PASS")

    def test_unknown_resolution_id_cannot_close_frozen_finding(self):
        def phase_b(context):
            return ReviewerResponse(
                "R3",
                context["artifact_hash"],
                "tries to close a different finding",
                resolved_finding_ids=("invented-id",),
            )

        decision, _, sessions = self._run((self._phase_a(),), phase_b)

        self.assertEqual(decision.state, "HUMAN_REQUIRED")
        self.assertIn("unknown frozen material finding ids", decision.reasons[0])
        self.assertEqual(decision.dissent, ("invented-id",))
        payload = sessions.last_payload("R3_ADJUDICATION_COMPLETED")
        self.assertEqual(payload["invalid_resolution_ids"], ["invented-id"])
        self.assertEqual(payload["unclosed_frozen_finding_ids"], ["r3-a"])

    def test_duplicate_phase_a_material_ids_block_phase_b_before_adjudication(self):
        def phase_b(_context):
            self.fail("Phase B must not run when frozen material IDs are ambiguous")

        findings = (
            self._phase_a("dup", "first material concern"),
            self._phase_a("dup", "second material concern"),
        )
        decision, calls, sessions = self._run(findings, phase_b)

        self.assertEqual(decision.state, "HUMAN_REQUIRED")
        self.assertIn("not unique", decision.reasons[0])
        self.assertEqual([phase for role, phase in calls if role == "R3"], ["INDEPENDENT"])
        payload = sessions.last_payload("R3_ADJUDICATION_REJECTED")
        self.assertEqual(payload["frozen_material_finding_ids"], ["dup", "dup"])
        self.assertFalse(payload["adjudication_invoked"])

    def test_new_phase_b_material_finding_remains_unresolved_even_when_phase_a_is_closed(self):
        def phase_b(context):
            new_finding = ReviewFinding("phase-b-new", "R3", "HIGH", True, "new material concern")
            return ReviewerResponse(
                "R3",
                context["artifact_hash"],
                "closed old issue but discovered a new one",
                findings=(new_finding,),
                resolved_finding_ids=("r3-a",),
            )

        decision, _, sessions = self._run((self._phase_a(),), phase_b)

        self.assertEqual(decision.state, "HUMAN_REQUIRED")
        self.assertIn("material conflict remains", decision.reasons[0])
        self.assertIn("new material concern", decision.dissent)
        payload = sessions.last_payload("R3_ADJUDICATION_COMPLETED")
        self.assertEqual(payload["resolved_finding_ids"], ["r3-a"])
        self.assertEqual(payload["unclosed_frozen_finding_ids"], [])
        self.assertIn("phase-b-new", payload["unresolved_finding_ids"])

    def test_partial_explicit_closure_does_not_erase_unclosed_phase_a_finding(self):
        def phase_b(context):
            return ReviewerResponse(
                "R3",
                context["artifact_hash"],
                "only one issue resolved",
                resolved_finding_ids=("r3-a",),
            )

        findings = (
            self._phase_a("r3-a", "first concern"),
            self._phase_a("r3-b", "second concern"),
        )
        decision, _, sessions = self._run(findings, phase_b)

        self.assertEqual(decision.state, "HUMAN_REQUIRED")
        self.assertIn("explicit staged R3 closure", decision.reasons[0])
        self.assertIn("second concern", decision.dissent)
        payload = sessions.last_payload("R3_ADJUDICATION_COMPLETED")
        self.assertEqual(payload["unclosed_frozen_finding_ids"], ["r3-b"])


if __name__ == "__main__":
    unittest.main()
