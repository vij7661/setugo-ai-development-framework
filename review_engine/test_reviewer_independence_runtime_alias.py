from __future__ import annotations

import unittest

from review_engine.models import ReviewFinding, ReviewerConfig, ReviewerResponse, ReviewRequest
from review_engine.orchestrator import ReviewEngine
from review_engine.qualification import QualificationRecord, QualificationRegistry


SAME_PROVIDER_BINDING = "a" * 64


def alias_config(
    role: str,
    lineage: str,
    *,
    provider: str = "same-provider",
    model: str = "same-model",
    binding: str | None = None,
) -> ReviewerConfig:
    return ReviewerConfig(
        role=role,
        provider=provider,
        model=model,
        sku="same-sku",
        deployment_path="same-api-path",
        api_key_env=f"{role}_KEY",
        foundation_lineage=lineage,
        qualification_ref=f"qual-{role.lower()}",
        provider_binding_fingerprint=binding,
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

    def test_provider_id_alias_with_same_binding_and_model_is_not_independent(self):
        r1 = alias_config(
            "R1",
            "declared-lineage-a",
            provider="provider-alias-a",
            binding=SAME_PROVIDER_BINDING,
        )
        r2 = alias_config(
            "R2",
            "declared-lineage-b",
            provider="provider-alias-b",
            binding=SAME_PROVIDER_BINDING,
        )
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
                request_id="provider-alias-independence",
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

    def test_r3_same_runtime_as_r1_cannot_count_as_independent_with_new_lineage_label(self):
        r1 = alias_config("R1", "lineage-r1")
        r2 = alias_config("R2", "lineage-r2", provider="distinct-provider", model="distinct-model")
        r3 = alias_config("R3", "fake-lineage-r3")
        calls: list[str] = []

        def invoke(config, context):
            calls.append(config.role)
            if config.role == "R1" and context.get("mode") != "SCOPED_CORRECTION":
                return ReviewerResponse("R1", None, "stable\nmaterial defect\nfooter")
            if config.role == "R2":
                finding = ReviewFinding(
                    "f1",
                    "R2",
                    "HIGH",
                    True,
                    "material defect",
                    affected_scope=("claim:defect",),
                    first_invalid_claim="material defect",
                )
                return ReviewerResponse("R2", context["artifact"]["artifact_hash"], "defect", (finding,))
            if config.role == "R1":
                return ReviewerResponse("R1", None, "stable\nmaterial correction\nfooter")
            self.fail("R3 must be rejected before provider invocation")

        decision = ReviewEngine(
            invoke,
            qualification_registry=registry_for(r1, r2, r3),
        ).run(
            ReviewRequest(
                request_id="r3-runtime-alias-independence",
                user_input="material change",
                risk="HIGH",
                materiality="MATERIAL",
            ),
            r1=r1,
            r2=r2,
            r3=r3,
        )

        self.assertEqual(decision.state, "HUMAN_REQUIRED")
        self.assertEqual(calls, ["R1", "R2", "R1"])
        self.assertIn("runtime identity", decision.reasons[0])


if __name__ == "__main__":
    unittest.main()
