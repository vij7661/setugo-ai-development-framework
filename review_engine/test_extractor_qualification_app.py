from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from review_engine.app import ReviewEngineApp
from review_engine.claim_coverage import RetainedClaimCoverageRegistry
from review_engine.configuration import ReviewEngineConfiguration
from review_engine.extraction_work import ExtractionWorkRegistry
from review_engine.extractor_qualification import (
    ExtractorQualificationRecord,
    ExtractorQualificationRegistry,
)
from review_engine.models import ReviewerConfig
from review_engine.qualification import QualificationRecord
from review_engine.qualified_claim_coverage import QualifiedRetainedClaimCoverageRegistry
from review_engine.work_bound_claim_coverage import WorkOrderBoundClaimCoverageRegistry


class FakeProviders:
    def invoke(self, config, context):
        raise AssertionError("constructor boundary test should not invoke provider")


def reviewer() -> ReviewerConfig:
    return ReviewerConfig(
        role="R1",
        provider="fake",
        model="reviewer-model",
        sku="default",
        deployment_path="api",
        api_key_env="R1_KEY",
        foundation_lineage="reviewer-lineage",
        qualification_ref="r1-q1",
    )


def governed_configuration() -> ReviewEngineConfiguration:
    return ReviewEngineConfiguration(
        reviewers={"R1": reviewer()},
        provider_specs={},
        qualification_records=(
            QualificationRecord(
                qualification_ref="r1-q1",
                provider="fake",
                model="reviewer-model",
                sku="default",
                deployment_path="api",
                role="R1",
                status="QUALIFIED",
                qualification_epoch=1,
                foundation_lineage="reviewer-lineage",
                max_risk="LOW",
                task_types=("*",),
            ),
        ),
    )


def extractor_qualifications() -> ExtractorQualificationRegistry:
    return ExtractorQualificationRegistry((
        ExtractorQualificationRecord(
            qualification_ref="extractor-q1",
            provider="extractor-provider",
            model="extractor-model",
            sku="default",
            deployment_path="api",
            foundation_lineage="extractor-lineage",
            status="QUALIFIED",
            qualification_epoch=1,
            max_risk="CRITICAL",
            task_types=("*",),
        ),
    ))


class ExtractorQualificationAppTests(unittest.TestCase):
    def test_governed_app_rejects_raw_unqualified_coverage_registry(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError, "qualified extractor admission"):
                ReviewEngineApp(
                    governed_configuration(),
                    memory_db=str(Path(td) / "memory.db"),
                    sessions_db=str(Path(td) / "sessions.db"),
                    provider_registry=FakeProviders(),
                    claim_coverage_validator=RetainedClaimCoverageRegistry(),
                )

    def test_governed_app_rejects_qualified_but_free_scope_admission(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError, "platform-issued extraction scope"):
                ReviewEngineApp(
                    governed_configuration(),
                    memory_db=str(Path(td) / "memory.db"),
                    sessions_db=str(Path(td) / "sessions.db"),
                    provider_registry=FakeProviders(),
                    claim_coverage_validator=QualifiedRetainedClaimCoverageRegistry(
                        extractor_qualifications()
                    ),
                )

    def test_governed_app_accepts_work_order_bound_qualified_coverage(self):
        with tempfile.TemporaryDirectory() as td:
            work = ExtractionWorkRegistry(extractor_qualifications())
            app = ReviewEngineApp(
                governed_configuration(),
                memory_db=str(Path(td) / "memory.db"),
                sessions_db=str(Path(td) / "sessions.db"),
                provider_registry=FakeProviders(),
                claim_coverage_validator=WorkOrderBoundClaimCoverageRegistry(work),
            )
            health = app.health()
            self.assertEqual(health["assurance_mode"], "GOVERNED")
            self.assertEqual(health["claim_coverage_validator"], "CONFIGURED")
            self.assertTrue(health["claim_coverage_qualified_admission"])
            self.assertTrue(health["claim_coverage_trusted_scope_binding"])


if __name__ == "__main__":
    unittest.main()
