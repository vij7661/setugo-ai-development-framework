from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from review_engine.app import ReviewEngineApp
from review_engine.configuration import ReviewEngineConfiguration
from review_engine.models import MemoryRecord, ReviewerConfig, ReviewerResponse
from review_engine.retrieval import GovernedLexicalRetriever
from review_engine.truth_contract import neutral_epistemic_review


class RecordingProviders:
    def __init__(self) -> None:
        self.contexts = []

    def invoke(self, config, context):
        self.contexts.append(context)
        return ReviewerResponse(
            role="R1",
            artifact_hash=None,
            output="bounded low-risk answer",
            findings=(),
            proposed_signals={},
            epistemic_review=neutral_epistemic_review(),
        )


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


class RetrievalApplicationTests(unittest.TestCase):
    def test_selective_retrieval_is_enforced_in_standard_application_path(self):
        with tempfile.TemporaryDirectory() as td:
            providers = RecordingProviders()
            app = ReviewEngineApp(
                configuration(),
                memory_db=str(Path(td) / "memory.db"),
                sessions_db=str(Path(td) / "sessions.db"),
                provider_registry=providers,
                context_retriever=GovernedLexicalRetriever(max_nonmandatory_records=2),
            )
            app.memory.append(
                MemoryRecord(
                    "authority",
                    "AUTHORITATIVE",
                    "ACTIVE",
                    1,
                    "platform",
                    "mandatory governance floor unrelated to lexical score",
                ),
                external_authority=True,
            )
            app.memory.append(
                MemoryRecord(
                    "relevant",
                    "PROJECT",
                    "ACTIVE",
                    1,
                    "user",
                    "provider endpoint qualification binding",
                )
            )
            app.memory.append(
                MemoryRecord(
                    "irrelevant",
                    "PROJECT",
                    "ACTIVE",
                    1,
                    "user",
                    "goat transport market scheduling",
                )
            )

            result = app.review({
                "request_id": "retrieval-app-1",
                "user_input": "explain provider endpoint binding",
            })

            self.assertEqual(result["state"], "CONVERGED_PASS")
            self.assertEqual(result["retrieval_strategy"], "GOVERNED_LEXICAL_OVERLAP")
            self.assertEqual(len(providers.contexts), 1)
            visible_ids = [record["record_id"] for record in providers.contexts[0]["memory"]]
            self.assertEqual(visible_ids, ["authority", "relevant"])

            r1_event = next(
                event for event in app.session_events("retrieval-app-1")
                if event["event_type"] == "R1_COMPLETED"
            )
            retrieval = r1_event["payload"]["retrieval_evidence"]
            self.assertEqual(retrieval["strategy"], "GOVERNED_LEXICAL_OVERLAP")
            self.assertEqual(
                [record["record_id"] for record in retrieval["retrieved_records"]],
                ["authority", "relevant"],
            )

    def test_default_application_behavior_remains_return_all(self):
        with tempfile.TemporaryDirectory() as td:
            providers = RecordingProviders()
            app = ReviewEngineApp(
                configuration(),
                memory_db=str(Path(td) / "memory.db"),
                sessions_db=str(Path(td) / "sessions.db"),
                provider_registry=providers,
            )
            app.memory.append(MemoryRecord("a", "PROJECT", "ACTIVE", 1, "user", "a"))
            app.memory.append(MemoryRecord("b", "PROJECT", "ACTIVE", 1, "user", "b"))
            result = app.review({"request_id": "retrieval-app-default", "user_input": "x"})
            self.assertEqual(result["state"], "CONVERGED_PASS")
            self.assertEqual(result["retrieval_strategy"], "RETURN_ALL_REVIEWER_VISIBLE")
            self.assertEqual(
                [record["record_id"] for record in providers.contexts[0]["memory"]],
                ["a", "b"],
            )


if __name__ == "__main__":
    unittest.main()
