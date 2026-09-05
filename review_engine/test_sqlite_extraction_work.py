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
from review_engine.sqlite_work_bound_claim_coverage import SQLiteWorkOrderBoundClaimCoverageRegistry
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


def declared_claims() -> list[dict]:
    return [
        {
            "claim_id": "c1",
            "text": ARTIFACT,
            "claim_type": "EMPIRICAL_FACT",
            "material": True,
        }
    ]


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

    def test_admitted_inventory_survives_restart_and_reconstructs_exact_coverage(self):
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
            expected = inventory()
            SQLiteWorkOrderBoundClaimCoverageRegistry(first).add(
                expected,
                work_order_id=order.work_order_id,
            )

            restarted = SQLiteExtractionWorkRegistry(path, q)
            self.assertEqual(restarted.retained_inventory(expected.inventory_id), expected)
            self.assertEqual(restarted.retained_inventories(expected.artifact_hash), (expected,))

            assessment = SQLiteWorkOrderBoundClaimCoverageRegistry(restarted).assess(
                artifact_hash=expected.artifact_hash,
                declared_claims=declared_claims(),
                reviewer_foundation_lineage="reviewer-lineage",
                risk="LOW",
                task_type="RESEARCH",
            )
            self.assertEqual(assessment.status, "VERIFIED_COVERAGE")
            self.assertEqual(assessment.inventory_ids, (expected.inventory_id,))
            self.assertEqual(assessment.provenance, (expected.provenance,))

    def test_low_risk_inventory_cannot_satisfy_high_risk_review_scope(self):
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
            coverage = SQLiteWorkOrderBoundClaimCoverageRegistry(work)
            coverage.add(inventory(), work_order_id=order.work_order_id)

            low = coverage.assess(
                artifact_hash=content_hash(ARTIFACT),
                declared_claims=declared_claims(),
                reviewer_foundation_lineage="reviewer-lineage",
                risk="LOW",
                task_type="RESEARCH",
            )
            high = coverage.assess(
                artifact_hash=content_hash(ARTIFACT),
                declared_claims=declared_claims(),
                reviewer_foundation_lineage="reviewer-lineage",
                risk="HIGH",
                task_type="RESEARCH",
            )
            self.assertEqual(low.status, "VERIFIED_COVERAGE")
            self.assertEqual(high.status, "UNVERIFIED")
            self.assertEqual(high.inventory_ids, ())

    def test_task_scoped_inventory_cannot_cross_review_task_type(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "extraction_work.db"
            work = SQLiteExtractionWorkRegistry(path, qualifications())
            order = work.issue(
                artifact_hash=content_hash(ARTIFACT),
                extractor_identity=identity(),
                risk="LOW",
                task_type="RESEARCH",
            )
            coverage = SQLiteWorkOrderBoundClaimCoverageRegistry(work)
            coverage.add(inventory(), work_order_id=order.work_order_id)

            assessment = coverage.assess(
                artifact_hash=content_hash(ARTIFACT),
                declared_claims=declared_claims(),
                reviewer_foundation_lineage="reviewer-lineage",
                risk="LOW",
                task_type="GENERAL",
            )
            self.assertEqual(assessment.status, "UNVERIFIED")
            self.assertEqual(assessment.inventory_ids, ())

    def test_revocation_after_inventory_admission_invalidates_current_scope_assessment(self):
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
            coverage = SQLiteWorkOrderBoundClaimCoverageRegistry(work)
            coverage.add(inventory(), work_order_id=order.work_order_id)
            self.assertEqual(
                coverage.assess(
                    artifact_hash=content_hash(ARTIFACT),
                    declared_claims=declared_claims(),
                    reviewer_foundation_lineage="reviewer-lineage",
                    risk="LOW",
                    task_type="RESEARCH",
                ).status,
                "VERIFIED_COVERAGE",
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
            assessment = coverage.assess(
                artifact_hash=content_hash(ARTIFACT),
                declared_claims=declared_claims(),
                reviewer_foundation_lineage="reviewer-lineage",
                risk="LOW",
                task_type="RESEARCH",
            )
            self.assertEqual(assessment.status, "UNVERIFIED")
            self.assertEqual(assessment.inventory_ids, ())

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
            self.assertEqual(work.retained_inventories(content_hash(ARTIFACT)), ())

            work.consume_for_inventory(order.work_order_id, inventory())
            self.assertTrue(work.is_consumed(order.work_order_id))

    def test_conflicting_inventory_admission_rolls_back_work_consumption(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "extraction_work.db"
            work = SQLiteExtractionWorkRegistry(path, qualifications())
            first_order = work.issue(
                artifact_hash=content_hash(ARTIFACT),
                extractor_identity=identity(),
                risk="LOW",
                task_type="RESEARCH",
            )
            second_order = work.issue(
                artifact_hash=content_hash(ARTIFACT),
                extractor_identity=identity(),
                risk="LOW",
                task_type="RESEARCH",
            )
            first_inventory = inventory(inventory_id="inv-first")
            second_inventory = inventory(inventory_id="inv-second")

            work.consume_for_inventory(first_order.work_order_id, first_inventory)
            with self.assertRaisesRegex(ValueError, "conflicting retained claim coverage inventory"):
                work.consume_for_inventory(second_order.work_order_id, second_inventory)

            self.assertTrue(work.is_consumed(first_order.work_order_id))
            self.assertFalse(work.is_consumed(second_order.work_order_id))
            self.assertEqual(work.retained_inventories(content_hash(ARTIFACT)), (first_inventory,))
            self.assertIsNone(work.retained_inventory(second_inventory.inventory_id))

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
            self.assertEqual(work.retained_inventories(content_hash(ARTIFACT)), ())

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
            restarted = SQLiteExtractionWorkRegistry(path, q)
            self.assertTrue(restarted.is_consumed(order.work_order_id))
            self.assertEqual(len(restarted.retained_inventories(content_hash(ARTIFACT))), 1)

    def test_concurrent_same_extractor_inventory_admission_has_one_winner_and_one_unspent_loser(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "extraction_work.db"
            q = qualifications()
            issuer = SQLiteExtractionWorkRegistry(path, q)
            first_order = issuer.issue(
                artifact_hash=content_hash(ARTIFACT),
                extractor_identity=identity(),
                risk="LOW",
                task_type="RESEARCH",
            )
            second_order = issuer.issue(
                artifact_hash=content_hash(ARTIFACT),
                extractor_identity=identity(),
                risk="LOW",
                task_type="RESEARCH",
            )
            barrier = threading.Barrier(2)

            def attempt(work_order_id: str, inventory_id: str) -> tuple[str, str]:
                registry = SQLiteExtractionWorkRegistry(path, q)
                barrier.wait(timeout=5)
                try:
                    registry.consume_for_inventory(
                        work_order_id,
                        inventory(inventory_id=inventory_id),
                    )
                    return work_order_id, "ADMITTED"
                except ValueError as exc:
                    return work_order_id, str(exc)

            with ThreadPoolExecutor(max_workers=2) as pool:
                outcomes = list(pool.map(
                    lambda args: attempt(*args),
                    (
                        (first_order.work_order_id, "inv-a"),
                        (second_order.work_order_id, "inv-b"),
                    ),
                ))

            winners = [work_id for work_id, outcome in outcomes if outcome == "ADMITTED"]
            losers = [(work_id, outcome) for work_id, outcome in outcomes if outcome != "ADMITTED"]
            self.assertEqual(len(winners), 1)
            self.assertEqual(len(losers), 1)
            self.assertIn("conflicting retained claim coverage inventory", losers[0][1])

            restarted = SQLiteExtractionWorkRegistry(path, q)
            self.assertTrue(restarted.is_consumed(winners[0]))
            self.assertFalse(restarted.is_consumed(losers[0][0]))
            retained = restarted.retained_inventories(content_hash(ARTIFACT))
            self.assertEqual(len(retained), 1)
            self.assertIn(retained[0].inventory_id, {"inv-a", "inv-b"})


if __name__ == "__main__":
    unittest.main()
