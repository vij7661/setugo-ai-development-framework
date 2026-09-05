from __future__ import annotations

import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from review_engine.claim_coverage import ClaimCoverageInventory, ClaimExtractorIdentity, CoverageClaim
from review_engine.extractor_qualification import ExtractorQualificationRecord, ExtractorQualificationRegistry
from review_engine.models import content_hash
from review_engine.sqlite_extraction_work import SQLiteExtractionWorkRegistry
from review_engine.work_bound_claim_coverage import WorkOrderBoundClaimCoverageRegistry


ARTIFACT = "Revenue increased 40%."


def identity() -> ClaimExtractorIdentity:
    return ClaimExtractorIdentity(
        provider="extractor-provider",
        model="extractor-model",
        sku="default",
        deployment_path="api",
        foundation_lineage="extractor-lineage",
        qualification_ref="extractor-q1",
        qualification_epoch=1,
    )


def qualifications() -> ExtractorQualificationRegistry:
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


def inventory(*, inventory_id: str = "inv-1", artifact: str = ARTIFACT) -> ClaimCoverageInventory:
    return ClaimCoverageInventory(
        inventory_id=inventory_id,
        artifact_hash=content_hash(artifact),
        claims=(CoverageClaim(artifact, "EMPIRICAL_FACT", True),),
        extractor_identity=identity(),
        provenance="authenticated-extraction:test",
        complete=True,
    )


class SQLiteExtractionWorkTests(unittest.TestCase):
    def test_issued_work_order_survives_process_restart(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "extraction_work.db"
            q = qualifications()
            first = SQLiteExtractionWorkRegistry(path, q)
            order = first.issue(
                artifact_hash=content_hash(ARTIFACT),
                extractor_identity=identity(),
                risk="HIGH",
                task_type="RESEARCH",
            )

            restarted = SQLiteExtractionWorkRegistry(path, q)
            restored = restarted.get(order.work_order_id)
            self.assertEqual(restored, order)
            self.assertFalse(restarted.is_consumed(order.work_order_id))

    def test_consumed_state_survives_restart_and_blocks_replay(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "extraction_work.db"
            q = qualifications()
            first = SQLiteExtractionWorkRegistry(path, q)
            order = first.issue(
                artifact_hash=content_hash(ARTIFACT),
                extractor_identity=identity(),
                risk="LOW",
                task_type="RESEARCH",
            )
            coverage = WorkOrderBoundClaimCoverageRegistry(first)
            coverage.add(inventory(), work_order_id=order.work_order_id)
            self.assertTrue(first.is_consumed(order.work_order_id))

            restarted = SQLiteExtractionWorkRegistry(path, q)
            self.assertTrue(restarted.is_consumed(order.work_order_id))
            with self.assertRaisesRegex(ValueError, "already consumed"):
                restarted.consume_for_inventory(order.work_order_id, inventory(inventory_id="inv-2"))

    def test_invalid_inventory_rolls_back_without_consuming_work_order(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "extraction_work.db"
            work = SQLiteExtractionWorkRegistry(path, qualifications())
            order = work.issue(
                artifact_hash=content_hash(ARTIFACT),
                extractor_identity=identity(),
                risk="LOW",
                task_type="RESEARCH",
            )

            with self.assertRaisesRegex(ValueError, "artifact does not match"):
                work.consume_for_inventory(
                    order.work_order_id,
                    inventory(artifact="Different artifact."),
                )
            self.assertFalse(work.is_consumed(order.work_order_id))

            work.consume_for_inventory(order.work_order_id, inventory())
            self.assertTrue(work.is_consumed(order.work_order_id))

    def test_revocation_after_issue_is_rechecked_during_atomic_consume(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "extraction_work.db"
            q = qualifications()
            work = SQLiteExtractionWorkRegistry(path, q)
            order = work.issue(
                artifact_hash=content_hash(ARTIFACT),
                extractor_identity=identity(),
                risk="LOW",
                task_type="RESEARCH",
            )
            q.add(
                ExtractorQualificationRecord(
                    qualification_ref="extractor-q1",
                    provider="extractor-provider",
                    model="extractor-model",
                    sku="default",
                    deployment_path="api",
                    foundation_lineage="extractor-lineage",
                    status="REVOKED",
                    qualification_epoch=2,
                    max_risk="HIGH",
                    task_types=("RESEARCH",),
                )
            )

            with self.assertRaisesRegex(ValueError, "no longer qualified"):
                work.consume_for_inventory(order.work_order_id, inventory())
            self.assertFalse(work.is_consumed(order.work_order_id))

    def test_concurrent_consumers_cannot_both_spend_one_work_order(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "extraction_work.db"
            q = qualifications()
            issuer = SQLiteExtractionWorkRegistry(path, q)
            order = issuer.issue(
                artifact_hash=content_hash(ARTIFACT),
                extractor_identity=identity(),
                risk="LOW",
                task_type="RESEARCH",
            )
            first = SQLiteExtractionWorkRegistry(path, q)
            second = SQLiteExtractionWorkRegistry(path, q)
            barrier = threading.Barrier(2)

            def attempt(registry: SQLiteExtractionWorkRegistry, inventory_id: str) -> str:
                barrier.wait(timeout=5)
                try:
                    registry.consume_for_inventory(
                        order.work_order_id,
                        inventory(inventory_id=inventory_id),
                    )
                    return "CONSUMED"
                except ValueError as exc:
                    return str(exc)

            with ThreadPoolExecutor(max_workers=2) as pool:
                outcomes = list(pool.map(
                    lambda args: attempt(*args),
                    ((first, "inv-a"), (second, "inv-b")),
                ))

            self.assertEqual(outcomes.count("CONSUMED"), 1)
            failures = [outcome for outcome in outcomes if outcome != "CONSUMED"]
            self.assertEqual(len(failures), 1)
            self.assertIn("already consumed", failures[0])
            self.assertTrue(SQLiteExtractionWorkRegistry(path, q).is_consumed(order.work_order_id))


if __name__ == "__main__":
    unittest.main()
