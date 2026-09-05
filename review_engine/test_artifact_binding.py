from __future__ import annotations

import unittest

from review_engine.models import ReviewRequest, ReviewerConfig, ReviewerResponse
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
            qualification_ref=config.qualification_ref,
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


class ArtifactBindingTests(unittest.TestCase):
    def test_nonconformant_r2_response_with_wrong_platform_hash_is_rejected(self):
        r1 = cfg("R1", "lineage-r1")
        r2 = cfg("R2", "lineage-r2")

        def invoke(config, context):
            if config.role == "R1":
                return ReviewerResponse("R1", None, "artifact")
            return ReviewerResponse("R2", "wrong-platform-binding", "clean")

        engine = ReviewEngine(invoke, qualification_registry=registry(r1, r2))
        with self.assertRaisesRegex(ValueError, "not bound to current frozen artifact"):
            engine.run(
                ReviewRequest("binding-1", "material review", risk="MEDIUM"),
                r1=r1,
                r2=r2,
                r3=None,
            )


if __name__ == "__main__":
    unittest.main()
