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

    def payload(self, event_type: str) -> dict:
        matches = [payload for _, kind, payload in self.events if kind == event_type]
        if not matches:
            raise AssertionError(f"missing event {event_type}")
        return matches[-1]


class R3DecisionSurfaceTests(unittest.TestCase):
    def test_resolved_material_history_is_not_exported_as_current_dissent_on_pass(self):
        r1 = cfg("R1", "lineage-r1")
        r2 = cfg("R2", "lineage-r2")
        r3 = cfg("R3", "lineage-r3")
        sessions = CaptureSessions()

        def invoke(config, context):
            if config.role == "R1" and context.get("mode") != "SCOPED_CORRECTION":
                return ReviewerResponse("R1", None, "header\nwrong claim\nfooter")
            if config.role == "R2":
                finding = ReviewFinding(
                    "r2-local", "R2", "HIGH", True, "wrong claim",
                    affected_scope=("claim:c1",), first_invalid_claim="wrong claim",
                )
                return ReviewerResponse("R2", context["artifact"]["artifact_hash"], "localized defect", (finding,))
            if config.role == "R1":
                return ReviewerResponse("R1", None, "header\nfixed claim\nfooter")
            if context["phase"] == "INDEPENDENT":
                finding = ReviewFinding("r3-history", "R3", "MEDIUM", True, "material concern later resolved")
                return ReviewerResponse(
                    "R3", context["artifact"]["artifact_hash"], "independent concern", (finding,)
                )
            return ReviewerResponse(
                "R3",
                context["artifact_hash"],
                "resolved after staged evidence comparison",
                resolved_finding_ids=("r3-history",),
            )

        decision = ReviewEngine(
            invoke,
            session_store=sessions,
            qualification_registry=registry(r1, r2, r3),
        ).run(
            ReviewRequest("r3-decision-surface", "material review", risk="HIGH", materiality="MATERIAL"),
            r1=r1,
            r2=r2,
            r3=r3,
        )

        self.assertEqual(decision.state, "CONVERGED_PASS")
        self.assertEqual(decision.dissent, ())

        phase_a = sessions.payload("R3_INDEPENDENT_COMPLETED")
        self.assertEqual(phase_a["material_finding_ids"], ["r3-history"])
        self.assertEqual(phase_a["findings"][0]["summary"], "material concern later resolved")
        final = sessions.payload("FINAL_DECISION")
        self.assertEqual(final["state"], "CONVERGED_PASS")
        self.assertEqual(final["dissent"], [])


if __name__ == "__main__":
    unittest.main()
