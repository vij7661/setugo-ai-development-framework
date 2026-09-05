from __future__ import annotations

import unittest

from review_engine.claim_coverage import ClaimCoverageInventory, ClaimExtractorIdentity, CoverageClaim
from review_engine.extractor_qualification import (
    ExtractorQualificationRecord,
    ExtractorQualificationRegistry,
)
from review_engine.models import content_hash
from review_engine.qualified_claim_coverage import QualifiedRetainedClaimCoverageRegistry


ARTIFACT = "Revenue increased 40%."


def identity(**overrides) -> ClaimExtractorIdentity:
    values = {
        "provider": "extractor-provider",
        "model": "extractor-model",
        "sku": "default",
        "deployment_path": "api",
        "foundation_lineage": "extractor-lineage",
        "qualification_ref": "extractor-q1",
        "qualification_epoch": 3,
    }
    values.update(overrides)
    return ClaimExtractorIdentity(**values)


def record(**overrides) -> ExtractorQualificationRecord:
    values = {
        "qualification_ref": "extractor-q1",
        "provider": "extractor-provider",
        "model": "extractor-model",
        "sku": "default",
        "deployment_path": "api",
        "foundation_lineage": "extractor-lineage",
        "status": "QUALIFIED",
        "qualification_epoch": 3,
        "max_risk": "HIGH",
        "task_types": ("RESEARCH",),
    }
    values.update(overrides)
    return ExtractorQualificationRecord(**values)


def inventory(extractor_identity: ClaimExtractorIdentity | None = None) -> ClaimCoverageInventory:
    return ClaimCoverageInventory(
        inventory_id="inventory-1",
        artifact_hash=content_hash(ARTIFACT),
        claims=(CoverageClaim(ARTIFACT, "EMPIRICAL_FACT", True),),
        extractor_identity=extractor_identity or identity(),
        provenance="authenticated-source-snapshot:test",
        complete=True,
    )


class ExtractorQualificationTests(unittest.TestCase):
    def test_exact_qualified_extractor_is_eligible(self):
        decision = ExtractorQualificationRegistry((record(),)).evaluate(
            identity(), risk="HIGH", task_type="RESEARCH"
        )
        self.assertTrue(decision.eligible)
        self.assertEqual(decision.qualification_epoch, 3)

    def test_revoked_or_pending_extractor_is_not_eligible(self):
        for status in ("REVOKED", "PENDING", "EXPIRED", "UNQUALIFIED"):
            with self.subTest(status=status):
                decision = ExtractorQualificationRegistry((record(status=status),)).evaluate(
                    identity(), risk="LOW", task_type="RESEARCH"
                )
                self.assertFalse(decision.eligible)
                self.assertIn(status, decision.reason)

    def test_stale_qualification_epoch_is_rejected(self):
        decision = ExtractorQualificationRegistry((record(),)).evaluate(
            identity(qualification_epoch=2), risk="LOW", task_type="RESEARCH"
        )
        self.assertFalse(decision.eligible)
        self.assertIn("qualification_epoch binding mismatch", decision.reason)

    def test_provider_model_sku_deployment_or_lineage_substitution_is_rejected(self):
        substitutions = {
            "provider": "other-provider",
            "model": "other-model",
            "sku": "other-sku",
            "deployment_path": "proxy",
            "foundation_lineage": "other-lineage",
        }
        for field, value in substitutions.items():
            with self.subTest(field=field):
                decision = ExtractorQualificationRegistry((record(),)).evaluate(
                    identity(**{field: value}), risk="LOW", task_type="RESEARCH"
                )
                self.assertFalse(decision.eligible)
                self.assertIn(f"{field} binding mismatch", decision.reason)

    def test_risk_above_extractor_qualification_ceiling_is_rejected(self):
        decision = ExtractorQualificationRegistry((record(max_risk="MEDIUM"),)).evaluate(
            identity(), risk="HIGH", task_type="RESEARCH"
        )
        self.assertFalse(decision.eligible)
        self.assertIn("requested risk", decision.reason)

    def test_task_outside_extractor_qualification_scope_is_rejected(self):
        decision = ExtractorQualificationRegistry((record(task_types=("CODE_REVIEW",)),)).evaluate(
            identity(), risk="LOW", task_type="RESEARCH"
        )
        self.assertFalse(decision.eligible)
        self.assertIn("task type", decision.reason)

    def test_qualification_epoch_must_advance_for_same_reference(self):
        registry = ExtractorQualificationRegistry((record(qualification_epoch=2),))
        registry.add(record(qualification_epoch=3))
        with self.assertRaisesRegex(ValueError, "epoch must advance"):
            registry.add(record(qualification_epoch=3))

    def test_unqualified_inventory_is_rejected_before_becoming_coverage_evidence(self):
        qualifications = ExtractorQualificationRegistry((record(status="REVOKED"),))
        coverage = QualifiedRetainedClaimCoverageRegistry(qualifications)
        with self.assertRaisesRegex(ValueError, "extractor not qualified"):
            coverage.add(inventory(), risk="LOW", task_type="RESEARCH")
        assessment = coverage.assess(
            artifact_hash=content_hash(ARTIFACT),
            declared_claims=[],
            reviewer_foundation_lineage="reviewer-lineage",
        )
        self.assertEqual(assessment.status, "UNVERIFIED")

    def test_qualified_inventory_is_admitted_with_retained_qualification_evidence(self):
        coverage = QualifiedRetainedClaimCoverageRegistry(
            ExtractorQualificationRegistry((record(),))
        )
        coverage.add(inventory(), risk="HIGH", task_type="RESEARCH")
        admission = coverage.admission_evidence("inventory-1")
        self.assertEqual(admission["qualification_ref"], "extractor-q1")
        self.assertEqual(admission["qualification_epoch"], 3)
        self.assertEqual(admission["risk"], "HIGH")
        self.assertEqual(admission["task_type"], "RESEARCH")
        assessment = coverage.assess(
            artifact_hash=content_hash(ARTIFACT),
            declared_claims=[{
                "claim_id": "c1",
                "text": ARTIFACT,
                "claim_type": "EMPIRICAL_FACT",
                "correspondence": "UNVERIFIED",
                "evidence_refs": [],
                "material": True,
            }],
            reviewer_foundation_lineage="reviewer-lineage",
        )
        self.assertEqual(assessment.status, "VERIFIED_COVERAGE")


if __name__ == "__main__":
    unittest.main()
