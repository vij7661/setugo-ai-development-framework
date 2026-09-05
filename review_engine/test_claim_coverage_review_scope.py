from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from review_engine.app import ReviewEngineApp
from review_engine.claim_coverage import ClaimCoverageInventory, ClaimExtractorIdentity, CoverageClaim
from review_engine.configuration import ReviewEngineConfiguration
from review_engine.extractor_qualification import ExtractorQualificationRecord, ExtractorQualificationRegistry
from review_engine.models import ReviewerConfig, ReviewerResponse, content_hash
from review_engine.qualification import QualificationRecord
from review_engine.request_boundary import PlatformExecutionEnvelope
from review_engine.sqlite_extraction_work import SQLiteExtractionWorkRegistry
from review_engine.sqlite_work_bound_claim_coverage import SQLiteWorkOrderBoundClaimCoverageRegistry


ARTIFACT = "A logically entails B."


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
                max_risk="HIGH",
                task_types=("RESEARCH",),
            ),
        ),
    )


def extractor_identity() -> ClaimExtractorIdentity:
    return ClaimExtractorIdentity(
        provider="extractor-provider",
        model="extractor-model",
        sku="default",
        deployment_path="api",
        foundation_lineage="extractor-lineage",
        qualification_ref="extractor-q1",
        qualification_epoch=1,
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
            max_risk="HIGH",
            task_types=("RESEARCH",),
        ),
    ))


def inventory() -> ClaimCoverageInventory:
    return ClaimCoverageInventory(
        inventory_id="coverage-inv-1",
        artifact_hash=content_hash(ARTIFACT),
        claims=(CoverageClaim(ARTIFACT, "LOGICAL_CLAIM", True),),
        extractor_identity=extractor_identity(),
        provenance="scope-regression:test",
        complete=True,
    )


class FakeProviders:
    def __init__(self, *, proposed_risk: str | None = None) -> None:
        self.proposed_risk = proposed_risk

    def invoke(self, config, context):
        proposed = {} if self.proposed_risk is None else {"risk": self.proposed_risk}
        return ReviewerResponse(
            role="R1",
            artifact_hash=None,
            output=ARTIFACT,
            findings=(),
            proposed_signals=proposed,
            epistemic_review={
                "version": "TVC-1",
                "correspondence": "NOT_APPLICABLE",
                "coherence": "CONSISTENT",
                "pragmatic": "NOT_APPLICABLE",
                "semantic": "PRECISE",
                "claims": [
                    {
                        "claim_id": "c1",
                        "text": ARTIFACT,
                        "claim_type": "LOGICAL_CLAIM",
                        "correspondence": "NOT_APPLICABLE",
                        "evidence_refs": [],
                        "material": True,
                    }
                ],
                "contradiction_refs": [],
            },
        )


def r1_event(app: ReviewEngineApp, request_id: str) -> dict:
    return next(
        event for event in app.session_events(request_id)
        if event["event_type"] == "R1_COMPLETED"
    )


class ClaimCoverageReviewScopeApplicationTests(unittest.TestCase):
    def _app_with_inventory(
        self,
        td: str,
        *,
        work_risk: str,
        proposed_risk: str | None = None,
    ) -> ReviewEngineApp:
        q = extractor_qualifications()
        work = SQLiteExtractionWorkRegistry(Path(td) / "coverage.db", q)
        order = work.issue(
            artifact_hash=content_hash(ARTIFACT),
            extractor_identity=extractor_identity(),
            risk=work_risk,
            task_type="RESEARCH",
        )
        coverage = SQLiteWorkOrderBoundClaimCoverageRegistry(work)
        coverage.add(inventory(), work_order_id=order.work_order_id)
        return ReviewEngineApp(
            governed_configuration(),
            memory_db=str(Path(td) / "memory.db"),
            sessions_db=str(Path(td) / "sessions.db"),
            provider_registry=FakeProviders(proposed_risk=proposed_risk),
            execution_envelope=PlatformExecutionEnvelope(task_type="RESEARCH"),
            claim_coverage_validator=coverage,
        )

    def test_high_risk_review_cannot_reuse_low_risk_coverage_inventory(self):
        with tempfile.TemporaryDirectory() as td:
            app = self._app_with_inventory(td, work_risk="LOW")
            result = app.review({
                "request_id": "coverage-high-vs-low",
                "user_input": "analyze the logical claim",
                "risk": "HIGH",
            })
            self.assertEqual(result["state"], "HUMAN_REQUIRED")
            event = r1_event(app, "coverage-high-vs-low")
            self.assertTrue(any(
                finding["violated_invariant"] == "TVC-COVERAGE"
                for finding in event["payload"]["findings"]
            ))
            self.assertTrue(result["claim_coverage_review_scope_binding"])
            self.assertTrue(result["claim_coverage_current_qualification_recheck"])

    def test_r1_risk_escalation_raises_coverage_scope_before_assessment(self):
        with tempfile.TemporaryDirectory() as td:
            app = self._app_with_inventory(
                td,
                work_risk="LOW",
                proposed_risk="HIGH",
            )
            result = app.review({
                "request_id": "coverage-r1-escalation",
                "user_input": "analyze the logical claim",
                "risk": "LOW",
            })
            self.assertEqual(result["state"], "HUMAN_REQUIRED")
            event = r1_event(app, "coverage-r1-escalation")
            self.assertEqual(event["payload"]["effective_signals"]["risk"], "HIGH")
            self.assertTrue(any(
                finding["violated_invariant"] == "TVC-COVERAGE"
                for finding in event["payload"]["findings"]
            ))

    def test_high_scope_inventory_is_not_rejected_as_low_scope(self):
        with tempfile.TemporaryDirectory() as td:
            app = self._app_with_inventory(td, work_risk="HIGH")
            result = app.review({
                "request_id": "coverage-high-matches-high",
                "user_input": "analyze the logical claim",
                "risk": "HIGH",
            })
            self.assertEqual(result["state"], "HUMAN_REQUIRED")
            event = r1_event(app, "coverage-high-matches-high")
            self.assertFalse(any(
                finding["violated_invariant"] == "TVC-COVERAGE"
                for finding in event["payload"]["findings"]
            ))
            self.assertIn("R2 required but unavailable", result["reasons"])


if __name__ == "__main__":
    unittest.main()
