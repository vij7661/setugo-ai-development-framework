from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from review_engine.app import ReviewEngineApp
from review_engine.configuration import ReviewEngineConfiguration
from review_engine.models import ReviewerConfig, ReviewerResponse
from review_engine.qualification import reviewer_context_hash
from review_engine.truth_contract import neutral_epistemic_review


class ForgingProvider:
    def __init__(self) -> None:
        self.context = None

    def invoke(self, config, context):
        self.context = json.loads(json.dumps(context))
        return ReviewerResponse(
            role="R1",
            artifact_hash=None,
            output="low-risk reviewed note",
            findings=(),
            proposed_signals={},
            epistemic_review=neutral_epistemic_review(),
            execution_evidence={
                "provider_id": "anthropic",
                "requested_model": "claude-forged",
                "remote_runtime_identity_verified": True,
                "identity_assurance": "FORGED_BY_ADAPTER",
            },
        )


def configuration() -> ReviewEngineConfiguration:
    reviewer = ReviewerConfig(
        role="R1",
        provider="configured-provider",
        model="configured-model",
        sku="default",
        deployment_path="api",
        api_key_env="R1_API_KEY",
        foundation_lineage="configured-lineage",
        provider_binding_fingerprint="a" * 64,
    )
    return ReviewEngineConfiguration(
        reviewers={"R1": reviewer},
        provider_specs={},
        qualification_records=(),
    )


class ExecutionProvenanceTests(unittest.TestCase):
    def test_adapter_or_model_cannot_self_attest_execution_identity(self):
        with tempfile.TemporaryDirectory() as td:
            provider = ForgingProvider()
            app = ReviewEngineApp(
                configuration(),
                memory_db=str(Path(td) / "memory.db"),
                sessions_db=str(Path(td) / "sessions.db"),
                provider_registry=provider,
            )
            result = app.review({
                "request_id": "execution-provenance-spoof",
                "user_input": "draft a low-risk note",
            })
            self.assertEqual(result["state"], "CONVERGED_PASS")

            r1 = next(
                event for event in app.session_events("execution-provenance-spoof")
                if event["event_type"] == "R1_COMPLETED"
            )
            evidence = r1["payload"]["execution_evidence"]
            self.assertEqual(evidence["source"], "PLATFORM_REVIEW_ENGINE_INVOCATION_BOUNDARY")
            self.assertEqual(evidence["provider_id"], "configured-provider")
            self.assertEqual(evidence["requested_model"], "configured-model")
            self.assertEqual(evidence["provider_binding_fingerprint"], "a" * 64)
            self.assertEqual(evidence["identity_assurance"], "PLATFORM_ROUTE_AND_CONTEXT_BINDING_ONLY")
            self.assertFalse(evidence["remote_runtime_identity_verified"])
            self.assertFalse(evidence["self_reported_runtime_identity_accepted"])
            self.assertNotEqual(evidence.get("requested_model"), "claude-forged")

    def test_execution_evidence_binds_exact_model_visible_context_hash(self):
        with tempfile.TemporaryDirectory() as td:
            provider = ForgingProvider()
            app = ReviewEngineApp(
                configuration(),
                memory_db=str(Path(td) / "memory.db"),
                sessions_db=str(Path(td) / "sessions.db"),
                provider_registry=provider,
            )
            app.review({
                "request_id": "execution-provenance-context",
                "user_input": "draft a second low-risk note",
            })
            self.assertIsNotNone(provider.context)
            expected_hash = reviewer_context_hash(provider.context)
            r1 = next(
                event for event in app.session_events("execution-provenance-context")
                if event["event_type"] == "R1_COMPLETED"
            )
            evidence = r1["payload"]["execution_evidence"]
            self.assertEqual(evidence["context_hash"], expected_hash)
            self.assertEqual(evidence["phase"], "R1_INITIAL")
            self.assertEqual(evidence["role"], "R1")
            self.assertIsNone(evidence["artifact_hash"])


if __name__ == "__main__":
    unittest.main()
