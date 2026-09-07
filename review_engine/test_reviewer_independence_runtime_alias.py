from __future__ import annotations

import unittest

from review_engine.models import ReviewerConfig, ReviewerResponse, ReviewRequest
from review_engine.orchestrator import ReviewEngine
from review_engine.qualification import QualificationRecord, QualificationRegistry


def alias_config(role: str, lineage: str) -> ReviewerConfig:
    return ReviewerConfig(
        role=role,
        provider="same-provider",
        model="same-model",
        sku="same-sku",
        deployment_path="same-api-path",
        api_key_env=f"{role}_KEY",
        foundation_lineage=lineage,
        qualification_ref=f"qual-{role.lower()}",
    )


def registry_for(*configs: ReviewerConfig) -> QualificationRegistry:
    return QualificationRegistry(tuple(
        QualificationRecord(
            qualification_ref=config.qualification_ref or "missing",
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
            provider_binding_fingerprint=config.provider_binding_fingerprint,
        )
        for config in configs
    ))


class ReviewerRuntimeAliasIndependenceTests(unittest.TestCase):
    def test_same_runtime_identity_cannot_masquerade_as_independent_via_lineage_label(self):
        r1 = alias_config("R1", "declared-lineage-a")
        r2 = alias_config("R2", "declared-lineage-b")
        calls: list[str] = []

        def invoke(config, context):
            calls.append(config.role)
            if config.role == "R1":
                return ReviewerResponse("R1", None, "candidate")
            return ReviewerResponse("R2", context["artifact"]["artifact_hash"], "clean")

        decision = ReviewEngine(
            invoke,
            qualification_registry=registry_for(r1, r2),
        ).run(
            ReviewRequest(
                request_id="runtime-alias-independence",
                user_input="material review",
                risk="MEDIUM",
                materiality="MATERIAL",
            ),
            r1=r1,
            r2=r2,
            r3=None,
        )

        self.assertEqual(decision.state, "HUMAN_REQUIRED")
        self.assertEqual(calls, ["R1"])
        self.assertIn("runtime identity", decision.reasons[0])


if __name__ == "__main__":
    unittest.main()
