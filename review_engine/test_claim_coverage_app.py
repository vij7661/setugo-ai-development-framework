from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from review_engine.app import ReviewEngineApp
from review_engine.claim_coverage import (
    ClaimCoverageInventory,
    ClaimExtractorIdentity,
    CoverageClaim,
    RetainedClaimCoverageRegistry,
)
from review_engine.configuration import ReviewEngineConfiguration
from review_engine.models import ReviewerConfig, ReviewerResponse, content_hash
from review_engine.truth_contract import neutral_epistemic_review


ARTIFACT = "Deployment succeeded."


def reviewer() -> ReviewerConfig:
    return ReviewerConfig(
        role="R1",
        provider="fake",
        model="reviewer-model",
        sku="default",
        deployment_path="api",
        api_key_env="R1_KEY",
        foundation_lineage="reviewer-lineage",
        qualification_ref=None,
    )


def extractor() -> ClaimExtractorIdentity:
    return ClaimExtractorIdentity(
        provider="extractor-provider",
        model="extractor-model",
        sku="default",
        deployment_path="api",
        foundation_lineage="extractor-lineage",
        qualification_ref="extractor-q1",
        qualification_epoch=1,
    )


class FakeProviders:
    def invoke(self, config, context):
        return ReviewerResponse(
            role="R1",
            artifact_hash=None,
            output=ARTIFACT,
            findings=(),
            epistemic_review=neutral_epistemic_review(),
        )


class ClaimCoverageApplicationTests(unittest.TestCase):
    def build_app(self, td: str, coverage) -> ReviewEngineApp:
        configuration = ReviewEngineConfiguration(reviewers={"R1": reviewer()}, provider_specs={})
        return ReviewEngineApp(
            configuration,
            memory_db=str(Path(td) / "memory.db"),
            sessions_db=str(Path(td) / "sessions.db"),
            provider_registry=FakeProviders(),
            claim_coverage_validator=coverage,
        )

    def test_model_omission_is_blocked_in_actual_app_path(self):
        coverage = RetainedClaimCoverageRegistry((
            ClaimCoverageInventory(
                inventory_id="inv-1",
                artifact_hash=content_hash(ARTIFACT),
                claims=(CoverageClaim(ARTIFACT, "EMPIRICAL_FACT", True),),
                extractor_identity=extractor(),
                provenance="independent-coverage-test",
                complete=True,
            ),
        ))
        with tempfile.TemporaryDirectory() as td:
            app = self.build_app(td, coverage)
            result = app.review({"request_id": "coverage-omit", "user_input": "summarize the status statement"})
            self.assertEqual(result["state"], "HUMAN_REQUIRED")
            self.assertTrue(result["claim_coverage_validator_configured"])
            events = app.session_events("coverage-omit")
            r1 = next(event for event in events if event["event_type"] == "R1_COMPLETED")
            findings = r1["payload"]["findings"]
            self.assertTrue(any(f["violated_invariant"] == "TVC-COVERAGE" for f in findings))
            self.assertTrue(any("omitted" in f["summary"].lower() for f in findings))

    def test_configured_coverage_without_exact_artifact_inventory_fails_closed(self):
        stale = ClaimCoverageInventory(
            inventory_id="stale",
            artifact_hash=content_hash("different artifact"),
            claims=(CoverageClaim("different artifact", "EMPIRICAL_FACT", True),),
            extractor_identity=extractor(),
            provenance="stale-test",
            complete=True,
        )
        with tempfile.TemporaryDirectory() as td:
            app = self.build_app(td, RetainedClaimCoverageRegistry((stale,)))
            result = app.review({"request_id": "coverage-stale", "user_input": "summarize the status statement"})
            self.assertEqual(result["state"], "HUMAN_REQUIRED")
            events = app.session_events("coverage-stale")
            r1 = next(event for event in events if event["event_type"] == "R1_COMPLETED")
            findings = r1["payload"]["findings"]
            self.assertTrue(any(f["finding_id"] == "tvc-coverage-unverified" for f in findings))

    def test_public_request_fields_cannot_create_coverage_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            app = self.build_app(td, RetainedClaimCoverageRegistry())
            result = app.review({
                "request_id": "coverage-forged",
                "user_input": "summarize the status statement",
                "claim_coverage": {
                    "inventory_id": "caller-forged",
                    "artifact_hash": content_hash(ARTIFACT),
                    "claims": [{"text": ARTIFACT, "claim_type": "EMPIRICAL_FACT", "material": True}],
                },
            })
            self.assertEqual(result["state"], "HUMAN_REQUIRED")
            events = app.session_events("coverage-forged")
            r1 = next(event for event in events if event["event_type"] == "R1_COMPLETED")
            self.assertTrue(any(f["finding_id"] == "tvc-coverage-unverified" for f in r1["payload"]["findings"]))


if __name__ == "__main__":
    unittest.main()
