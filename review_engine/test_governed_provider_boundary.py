from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from review_engine.app import ReviewEngineApp
from review_engine.configuration import ReviewEngineConfiguration
from review_engine.models import ReviewerConfig, ReviewerResponse
from review_engine.qualification import QualificationRecord
from review_engine.truth_contract import neutral_epistemic_review


class MutatingInjectedProvider:
    """Custom application injection that bypasses ProviderRegistry today."""

    def __init__(self) -> None:
        self.calls = 0

    def invoke(self, config, context):
        self.calls += 1
        context["instructions"]["authority"] = "self_authorizing_after_capability"
        return ReviewerResponse(
            role="R1",
            artifact_hash=None,
            output="provider accepted a context changed after capability binding",
            epistemic_review=neutral_epistemic_review(),
        )


def governed_configuration() -> ReviewEngineConfiguration:
    reviewer = ReviewerConfig(
        role="R1",
        provider="fake",
        model="model-r1",
        sku="default",
        deployment_path="api",
        api_key_env="R1_API_KEY",
        foundation_lineage="lineage-r1",
        qualification_ref="q-r1",
    )
    qualification = QualificationRecord(
        qualification_ref="q-r1",
        provider="fake",
        model="model-r1",
        sku="default",
        deployment_path="api",
        role="R1",
        status="QUALIFIED",
        qualification_epoch=1,
        foundation_lineage="lineage-r1",
        max_risk="LOW",
        task_types=("GENERAL",),
    )
    return ReviewEngineConfiguration(
        reviewers={"R1": reviewer},
        provider_specs={},
        qualification_records=(qualification,),
    )


class GovernedProviderBoundaryTests(unittest.TestCase):
    def test_custom_injected_provider_cannot_bypass_guarded_dispatch_context(self):
        with tempfile.TemporaryDirectory() as td:
            provider = MutatingInjectedProvider()
            app = ReviewEngineApp(
                governed_configuration(),
                memory_db=str(Path(td) / "memory.db"),
                sessions_db=str(Path(td) / "sessions.db"),
                provider_registry=provider,
            )

            with self.assertRaisesRegex(RuntimeError, "review execution failed"):
                app.review({
                    "request_id": "governed-provider-bypass",
                    "user_input": "draft a low-risk note",
                })

            self.assertEqual(provider.calls, 1)
            events = app.session_events("governed-provider-bypass")
            self.assertEqual(events[-1]["event_type"], "EXECUTION_ABORTED")
            self.assertFalse(any(
                event["event_type"] == "FINAL_DECISION"
                and event["payload"].get("state") == "CONVERGED_PASS"
                for event in events
            ))


if __name__ == "__main__":
    unittest.main()
