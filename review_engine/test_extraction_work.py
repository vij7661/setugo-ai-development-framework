from __future__ import annotations

import unittest

from review_engine.claim_coverage import ClaimCoverageInventory, ClaimExtractorIdentity, CoverageClaim
from review_engine.extraction_work import ExtractionWorkRegistry
from review_engine.extractor_qualification import ExtractorQualificationRecord, ExtractorQualificationRegistry
from review_engine.models import content_hash
from review_engine.work_bound_claim_coverage import WorkOrderBoundClaimCoverageRegistry


ARTIFACT = "Revenue increased 40%."


def identity(**overrides) -> ClaimExtractorIdentity:
    values = {
        "provider": "extractor-provider",
        "model": "extractor-model",
        "sku": "default",
        "deployment_path": "api",
        "foundation_lineage": "extractor-lineage",
        "qualification_ref": "extractor-q1",
        "qualification_epoch": 1,
    }
    values.update(overrides)
    return ClaimExtractorIdentity(**values)


def qualifications(status: str = "QUALIFIED", epoch: int = 1) -> ExtractorQualificationRegistry:
    return ExtractorQualificationRegistry((
        ExtractorQualificationRecord(
            qualification_ref="extractor-q1",
            provider="extractor-provider",
            model="extractor-model",
            sku="default",
            deployment_path="api",
            foundation_lineage="extractor-lineage",
            status=status,
            qualification_epoch=epoch,
            max_risk="HIGH",
            task_types=("RESEARCH",),
        ),
    ))


def inventory(*, artifact: str = ARTIFACT, extractor_identity: ClaimExtractorIdentity | None = None, inventory_id: str = "inv-1") -> ClaimCoverageInventory:
    return ClaimCoverageInventory(
        inventory_id=inventory_id,
        artifact_hash=content_hash(artifact),
        claims=(CoverageClaim(artifact, "EMPIRICAL_FACT", True),),
        extractor_identity=extractor_identity or identity(),
        provenance="authenticated-extraction:test",
        complete=True,
    )


class ExtractionWorkTests(unittest.TestCase):
    def test_platform_order_binds_artifact_risk_task_and_extractor(self):
        work = ExtractionWorkRegistry(qualifications())
        order = work.issue(
            artifact_hash=content_hash(ARTIFACT),
            extractor_identity=identity(),
            risk="HIGH",
            task_type="RESEARCH",
        )
        self.assertEqual(order.artifact_hash, content_hash(ARTIFACT))
        self.assertEqual(order.risk, "HIGH")
        self.assertEqual(order.task_type, "RESEARCH")
        self.assertEqual(order.extractor_id, identity().extractor_id)

    def test_unqualified_scope_cannot_receive_work_order(self):
        work = ExtractionWorkRegistry(qualifications())
        with self.assertRaisesRegex(ValueError, "requested risk"):
            work.issue(
                artifact_hash=content_hash(ARTIFACT),
                extractor_identity=identity(),
                risk="CRITICAL",
                task_type="RESEARCH",
            )
        with self.assertRaisesRegex(ValueError, "task type"):
            work.issue(
                artifact_hash=content_hash(ARTIFACT),
                extractor_identity=identity(),
                risk="LOW",
                task_type="CODE_REVIEW",
            )

    def test_inventory_cannot_swap_artifact_after_work_is_issued(self):
        work = ExtractionWorkRegistry(qualifications())
        order = work.issue(
            artifact_hash=content_hash(ARTIFACT),
            extractor_identity=identity(),
            risk="LOW",
            task_type="RESEARCH",
        )
        with self.assertRaisesRegex(ValueError, "artifact does not match"):
            work.validate_inventory(order.work_order_id, inventory(artifact="Different artifact."))

    def test_inventory_cannot_swap_extractor_after_work_is_issued(self):
        work = ExtractionWorkRegistry(qualifications())
        order = work.issue(
            artifact_hash=content_hash(ARTIFACT),
            extractor_identity=identity(),
            risk="LOW",
            task_type="RESEARCH",
        )
        with self.assertRaisesRegex(ValueError, "extractor does not match"):
            work.validate_inventory(
                order.work_order_id,
                inventory(extractor_identity=identity(model="substituted-model")),
            )

    def test_revocation_after_issue_invalidates_outstanding_work(self):
        q = qualifications()
        work = ExtractionWorkRegistry(q)
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
            work.validate_inventory(order.work_order_id, inventory())

    def test_work_order_is_single_use_and_cannot_be_replayed(self):
        work = ExtractionWorkRegistry(qualifications())
        order = work.issue(
            artifact_hash=content_hash(ARTIFACT),
            extractor_identity=identity(),
            risk="LOW",
            task_type="RESEARCH",
        )
        coverage = WorkOrderBoundClaimCoverageRegistry(work)
        coverage.add(inventory(), work_order_id=order.work_order_id)
        self.assertTrue(work.is_consumed(order.work_order_id))
        with self.assertRaisesRegex(ValueError, "already consumed"):
            coverage.add(inventory(inventory_id="inv-2"), work_order_id=order.work_order_id)

    def test_admission_scope_comes_from_work_order_not_new_arguments(self):
        work = ExtractionWorkRegistry(qualifications())
        order = work.issue(
            artifact_hash=content_hash(ARTIFACT),
            extractor_identity=identity(),
            risk="HIGH",
            task_type="RESEARCH",
        )
        coverage = WorkOrderBoundClaimCoverageRegistry(work)
        coverage.add(inventory(), work_order_id=order.work_order_id)
        evidence = coverage.admission_evidence("inv-1")
        self.assertEqual(evidence["risk"], "HIGH")
        self.assertEqual(evidence["task_type"], "RESEARCH")
        self.assertEqual(evidence["work_order_id"], order.work_order_id)


if __name__ == "__main__":
    unittest.main()
