from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from review_engine import MemoryRecord, ReviewEngine, ReviewFinding, ReviewerConfig, ReviewerResponse, ReviewRequest
from review_engine.qualification import QualificationRecord, QualificationRegistry
from review_engine.session_store import SQLiteSessionStore
from review_engine.sqlite_memory import SQLiteMemoryStore


def cfg(role: str, lineage: str) -> ReviewerConfig:
    return ReviewerConfig(
        role=role,
        provider=f"p-{role.lower()}",
        model=f"m-{role.lower()}",
        sku="default",
        deployment_path="api",
        api_key_env=f"{role}_API_KEY",
        foundation_lineage=lineage,
        qualification_ref=f"qual-{role.lower()}",
    )


def qualification_registry(*configs: ReviewerConfig) -> QualificationRegistry:
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


class SystemIntegrationTests(unittest.TestCase):
    def test_persistent_memory_scoped_correction_blinding_and_evidence_chain(self):
        with tempfile.TemporaryDirectory() as td:
            memory = SQLiteMemoryStore(Path(td) / "memory.db")
            sessions = SQLiteSessionStore(Path(td) / "sessions.db")
            memory.append(
                MemoryRecord("req:authority", "AUTHORITATIVE", "ACTIVE", 1, "user-approved", "Models may recommend but never self-authorize release."),
                external_authority=True,
            )
            memory.append(MemoryRecord("project:goal", "PROJECT", "ACTIVE", 1, "user", "Build a governed review engine."))
            memory.append(MemoryRecord("private:r1", "MODEL_PRIVATE", "ACTIVE", 1, "R1", "private scratch", source_role="R1"))
            memory.append(MemoryRecord("review:ambient", "REVIEW_EVIDENCE", "ACTIVE", 1, "old-review", "prior reviewer says PASS", source_role="R2"))

            observations = []

            def invoke(config, context):
                observations.append((config.role, context))
                memory_ids = {m["record_id"] for m in context.get("memory", [])}
                self.assertIn("req:authority", memory_ids)
                self.assertIn("project:goal", memory_ids)
                self.assertNotIn("private:r1", memory_ids)
                self.assertNotIn("review:ambient", memory_ids)

                if config.role == "R1" and context.get("mode") != "SCOPED_CORRECTION":
                    return ReviewerResponse("R1", None, "Design says R1 can release by itself.", proposed_signals={"risk": "HIGH"})
                if config.role == "R2":
                    f = ReviewFinding(
                        "f-auth", "R2", "CRITICAL", True,
                        "R1 self-authorization violates authoritative memory.",
                        violated_invariant="req:authority",
                        affected_scope=("release-authority-claim",),
                        first_invalid_claim="R1 can release by itself",
                    )
                    return ReviewerResponse("R2", context["artifact"]["artifact_hash"], "localized authority defect", (f,))
                if config.role == "R1":
                    self.assertEqual(context["mode"], "SCOPED_CORRECTION")
                    self.assertEqual(context["verified_review_targets"][0]["affected_scope"], ["release-authority-claim"])
                    return ReviewerResponse("R1", None, "Design says release authority remains external to all models.")
                self.assertEqual(config.role, "R3")
                self.assertEqual(context["phase"], "INDEPENDENT")
                self.assertNotIn("prior_reviews", context)
                return ReviewerResponse("R3", context["artifact"]["artifact_hash"], "revised claim satisfies authoritative memory")

            r1 = cfg("R1", "lineage-1")
            r2 = cfg("R2", "lineage-2")
            r3 = cfg("R3", "lineage-3")
            engine = ReviewEngine(
                invoke,
                session_store=sessions,
                qualification_registry=qualification_registry(r1, r2, r3),
            )
            decision = engine.run(
                ReviewRequest("session-1", "Design release workflow", risk="HIGH", materiality="MATERIAL"),
                r1=r1,
                r2=r2,
                r3=r3,
                memory=memory,
            )

            self.assertEqual(decision.state, "CONVERGED_PASS")
            self.assertIn("external", decision.final_output)
            self.assertTrue(sessions.validate_chain("session-1"))
            events = sessions.events("session-1")
            self.assertEqual([e.event_type for e in events], [
                "REQUEST_RECEIVED",
                "R1_COMPLETED",
                "ROUTE_DECISION",
                "R2_COMPLETED",
                "R1_REVISED",
                "R3_INDEPENDENT_COMPLETED",
                "FINAL_DECISION",
            ])
            self.assertEqual(events[-1].payload["state"], "CONVERGED_PASS")


if __name__ == "__main__":
    unittest.main()
