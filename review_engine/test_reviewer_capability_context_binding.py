from __future__ import annotations

import unittest

from review_engine.context_compiler import ContextCompiler
from review_engine.models import ReviewerConfig, ReviewerResponse, ReviewRequest
from review_engine.orchestrator import ReviewEngine
from review_engine.qualification import QualificationRecord, QualificationRegistry


def cfg(role: str, model: str, lineage: str, ref: str) -> ReviewerConfig:
    return ReviewerConfig(
        role=role,
        provider="p",
        model=model,
        sku="s",
        deployment_path="api",
        api_key_env=f"{role}_KEY",
        foundation_lineage=lineage,
        qualification_ref=ref,
    )


def qualified(config: ReviewerConfig) -> QualificationRecord:
    return QualificationRecord(
        qualification_ref=config.qualification_ref,
        provider=config.provider,
        model=config.model,
        sku=config.sku,
        deployment_path=config.deployment_path,
        role=config.role,
        status="QUALIFIED",
        qualification_epoch=1,
        foundation_lineage=config.foundation_lineage,
        max_risk="HIGH",
        task_types=("GENERAL",),
    )


class TamperingContextCompiler(ContextCompiler):
    """Simulate a faulty extension that swaps content but preserves the platform hash."""

    def compile_r2(self, request, artifact, memory):
        context = super().compile_r2(request, artifact, memory)
        context["artifact"]["content"] = "substituted benign artifact"
        return context


class ReviewerCapabilityContextBindingTests(unittest.TestCase):
    def test_same_hash_but_substituted_model_visible_artifact_cannot_receive_r2_capability(self):
        r1 = cfg("R1", "m1", "lineage-1", "q1")
        r2 = cfg("R2", "m2", "lineage-2", "q2")
        registry = QualificationRegistry((qualified(r1), qualified(r2)))
        calls: list[str] = []

        def invoke(config, context):
            calls.append(config.role)
            if config.role == "R1":
                return ReviewerResponse("R1", None, "materially unsafe artifact")
            self.assertEqual(context["artifact"]["content"], "substituted benign artifact")
            return ReviewerResponse(
                "R2",
                context["artifact"]["artifact_hash"],
                "no material defect found in substituted artifact",
            )

        decision = ReviewEngine(
            invoke,
            context_compiler=TamperingContextCompiler(),
            qualification_registry=registry,
        ).run(
            ReviewRequest(
                "context-substitution",
                "review this material artifact",
                risk="HIGH",
                materiality="MATERIAL",
            ),
            r1=r1,
            r2=r2,
            r3=None,
        )

        self.assertEqual(
            decision.state,
            "HUMAN_REQUIRED",
            "a reviewer must not be authorized on model-visible content that disagrees with the platform artifact binding",
        )
        self.assertEqual(calls, ["R1"], "R2 must not be invoked on substituted model-visible artifact content")
        self.assertTrue(any("context" in reason.lower() or "artifact" in reason.lower() for reason in decision.reasons))


if __name__ == "__main__":
    unittest.main()
