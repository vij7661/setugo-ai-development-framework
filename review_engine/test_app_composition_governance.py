from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from review_engine.app import ReviewEngineApp
from review_engine.claim_coverage_guard import ClaimCoverageGuardedInvoker
from review_engine.configuration import ReviewEngineConfiguration
from review_engine.models import ReviewerConfig, ReviewerResponse
from review_engine.retrieval import GovernedLexicalRetriever
from review_engine.retrieval_review_engine import RetrievalAwareReviewEngine
from review_engine.truth_contract import neutral_epistemic_review


class RecordingProviders:
    def invoke(self, config, context):
        return ReviewerResponse(
            role=config.role,
            artifact_hash=context.get("artifact", {}).get("artifact_hash"),
            output="bounded answer",
            findings=(),
            epistemic_review=neutral_epistemic_review(),
        )


class RecordingCoverageValidator:
    def assess(self, **kwargs):
        return None


class RecordingEvidenceValidator:
    def assess(self, **kwargs):
        return None


def configuration() -> ReviewEngineConfiguration:
    return ReviewEngineConfiguration(
        reviewers={
            "R1": ReviewerConfig(
                role="R1",
                provider="fake",
                model="model-r1",
                sku="default",
                deployment_path="api",
                api_key_env="R1_KEY",
                foundation_lineage="lineage-r1",
            )
        },
        provider_specs={},
        qualification_records=(),
    )


class ReviewEngineAppCompositionTests(unittest.TestCase):
    def test_app_wires_coverage_guard_retrieval_context_and_evidence_into_one_engine(self):
        with tempfile.TemporaryDirectory() as td:
            coverage = RecordingCoverageValidator()
            evidence = RecordingEvidenceValidator()
            retriever = GovernedLexicalRetriever(max_nonmandatory_records=3)
            app = ReviewEngineApp(
                configuration(),
                memory_db=str(Path(td) / "memory.db"),
                sessions_db=str(Path(td) / "sessions.db"),
                provider_registry=RecordingProviders(),
                claim_coverage_validator=coverage,
                evidence_validator=evidence,
                context_retriever=retriever,
            )

            self.assertIsInstance(app.engine, RetrievalAwareReviewEngine)
            self.assertIsInstance(app.claim_coverage_guard, ClaimCoverageGuardedInvoker)
            self.assertIs(app.engine._invoke, app.claim_coverage_guard)
            self.assertIs(app.engine._contexts, app.context_compiler)
            self.assertIs(app.engine._evidence_validator, evidence)
            self.assertEqual(app.context_compiler.retrieval_strategy, "GOVERNED_LEXICAL_OVERLAP")
            self.assertEqual(app.context_compiler.retrieval_strategy_version, "1")

    def test_app_without_coverage_guard_still_uses_retrieval_aware_engine_and_evidence_validator(self):
        with tempfile.TemporaryDirectory() as td:
            providers = RecordingProviders()
            evidence = RecordingEvidenceValidator()
            app = ReviewEngineApp(
                configuration(),
                memory_db=str(Path(td) / "memory.db"),
                sessions_db=str(Path(td) / "sessions.db"),
                provider_registry=providers,
                evidence_validator=evidence,
                context_retriever=GovernedLexicalRetriever(max_nonmandatory_records=1),
            )

            self.assertIsNone(app.claim_coverage_guard)
            self.assertIsInstance(app.engine, RetrievalAwareReviewEngine)
            self.assertEqual(app.engine._invoke, providers.invoke)
            self.assertIs(app.engine._contexts, app.context_compiler)
            self.assertIs(app.engine._evidence_validator, evidence)


if __name__ == "__main__":
    unittest.main()
