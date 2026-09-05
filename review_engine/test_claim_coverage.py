from __future__ import annotations

import unittest

from review_engine.claim_coverage import (
    ClaimCoverageInventory,
    ClaimExtractorIdentity,
    CoverageClaim,
    RetainedClaimCoverageRegistry,
)
from review_engine.claim_coverage_guard import ClaimCoverageGuardedInvoker
from review_engine.models import ReviewerConfig, ReviewerResponse, content_hash
from review_engine.truth_contract import TVC_VERSION, neutral_epistemic_review


def extractor(lineage: str = "extractor-lineage") -> ClaimExtractorIdentity:
    return ClaimExtractorIdentity(
        provider="extractor-provider",
        model="extractor-model",
        sku="default",
        deployment_path="api",
        foundation_lineage=lineage,
        qualification_ref="claim-extractor-q1",
        qualification_epoch=1,
    )


def inventory(artifact: str, claims: tuple[CoverageClaim, ...], *, lineage: str = "extractor-lineage", inventory_id: str = "inv-1") -> ClaimCoverageInventory:
    return ClaimCoverageInventory(
        inventory_id=inventory_id,
        artifact_hash=content_hash(artifact),
        claims=claims,
        extractor_identity=extractor(lineage),
        provenance="platform-retained-independent-extraction",
        complete=True,
    )


def cfg(role: str = "R1", lineage: str = "reviewer-lineage") -> ReviewerConfig:
    return ReviewerConfig(
        role=role,
        provider="reviewer-provider",
        model="reviewer-model",
        sku="default",
        deployment_path="api",
        api_key_env="REVIEWER_KEY",
        foundation_lineage=lineage,
        qualification_ref="reviewer-q1",
    )


class ClaimCoverageTests(unittest.TestCase):
    def test_omitted_material_claim_is_detected(self):
        artifact = "Deployment succeeded."
        registry = RetainedClaimCoverageRegistry((
            inventory(artifact, (CoverageClaim(artifact, "EMPIRICAL_FACT", True),)),
        ))
        assessment = registry.assess(
            artifact_hash=content_hash(artifact),
            declared_claims=[],
            reviewer_foundation_lineage="reviewer-lineage",
        )
        self.assertEqual(assessment.status, "OMITTED_MATERIAL_CLAIM")
        findings = assessment.findings("R1")
        self.assertEqual(findings[0].violated_invariant, "TVC-COVERAGE")
        self.assertTrue(findings[0].material)
        self.assertIn("Deployment succeeded", findings[0].summary)

    def test_material_claim_cannot_be_downgraded_to_inference_or_nonmaterial(self):
        artifact = "Deployment succeeded."
        registry = RetainedClaimCoverageRegistry((
            inventory(artifact, (CoverageClaim(artifact, "EMPIRICAL_FACT", True),)),
        ))
        declared = [{
            "claim_id": "c1",
            "text": artifact,
            "claim_type": "INFERENCE",
            "correspondence": "NOT_APPLICABLE",
            "evidence_refs": [],
            "material": False,
        }]
        assessment = registry.assess(
            artifact_hash=content_hash(artifact),
            declared_claims=declared,
            reviewer_foundation_lineage="reviewer-lineage",
        )
        self.assertEqual(assessment.status, "MISCLASSIFIED_MATERIAL_CLAIM")
        self.assertIn("INFERENCE/material=false", assessment.misclassified_claims[0][3])

    def test_stale_artifact_inventory_is_not_reused(self):
        registry = RetainedClaimCoverageRegistry((
            inventory("old artifact", (CoverageClaim("old artifact", "EMPIRICAL_FACT", True),)),
        ))
        assessment = registry.assess(
            artifact_hash=content_hash("new artifact"),
            declared_claims=[],
            reviewer_foundation_lineage="reviewer-lineage",
        )
        self.assertEqual(assessment.status, "UNVERIFIED")
        self.assertTrue(assessment.findings("R1")[0].material)

    def test_same_lineage_extractor_does_not_satisfy_independent_coverage(self):
        artifact = "Deployment succeeded."
        registry = RetainedClaimCoverageRegistry((
            inventory(
                artifact,
                (CoverageClaim(artifact, "EMPIRICAL_FACT", True),),
                lineage="reviewer-lineage",
            ),
        ))
        assessment = registry.assess(
            artifact_hash=content_hash(artifact),
            declared_claims=[],
            reviewer_foundation_lineage="reviewer-lineage",
        )
        self.assertEqual(assessment.status, "UNVERIFIED")
        self.assertTrue(assessment.correlation_warnings)

    def test_conflicting_independent_inventories_fail_closed(self):
        artifact = "Deployment succeeded."
        registry = RetainedClaimCoverageRegistry((
            inventory(
                artifact,
                (CoverageClaim(artifact, "EMPIRICAL_FACT", True),),
                lineage="extractor-lineage-a",
                inventory_id="inv-a",
            ),
            inventory(
                artifact,
                (CoverageClaim(artifact, "INFERENCE", True),),
                lineage="extractor-lineage-b",
                inventory_id="inv-b",
            ),
        ))
        assessment = registry.assess(
            artifact_hash=content_hash(artifact),
            declared_claims=[],
            reviewer_foundation_lineage="reviewer-lineage",
        )
        self.assertEqual(assessment.status, "CONFLICT")
        self.assertTrue(assessment.findings("R2")[0].material)

    def test_guard_adds_platform_coverage_finding_after_model_response(self):
        artifact = "Deployment succeeded."
        registry = RetainedClaimCoverageRegistry((
            inventory(artifact, (CoverageClaim(artifact, "EMPIRICAL_FACT", True),)),
        ))

        def invoke(config, context):
            return ReviewerResponse(
                role="R1",
                artifact_hash=None,
                output=artifact,
                findings=(),
                epistemic_review=neutral_epistemic_review(),
            )

        guarded = ClaimCoverageGuardedInvoker(invoke, registry)
        response = guarded(cfg(), {})
        self.assertEqual(response.output, artifact)
        self.assertTrue(any(f.violated_invariant == "TVC-COVERAGE" for f in response.findings))
        assessment = guarded.assessment("R1", content_hash(artifact))
        self.assertIsNotNone(assessment)
        self.assertEqual(assessment.status, "OMITTED_MATERIAL_CLAIM")

    def test_guard_accepts_matching_material_inventory(self):
        artifact = "Deployment succeeded."
        registry = RetainedClaimCoverageRegistry((
            inventory(artifact, (CoverageClaim(artifact, "EMPIRICAL_FACT", True),)),
        ))
        epistemic = {
            "version": TVC_VERSION,
            "correspondence": "UNVERIFIED",
            "coherence": "CONSISTENT",
            "pragmatic": "VIABLE",
            "semantic": "PRECISE",
            "contradiction_refs": [],
            "claims": [{
                "claim_id": "c1",
                "text": artifact,
                "claim_type": "EMPIRICAL_FACT",
                "correspondence": "UNVERIFIED",
                "evidence_refs": [],
                "material": True,
            }],
        }

        def invoke(config, context):
            return ReviewerResponse("R1", None, artifact, epistemic_review=epistemic)

        guarded = ClaimCoverageGuardedInvoker(invoke, registry)
        response = guarded(cfg(), {})
        self.assertFalse(any(f.violated_invariant == "TVC-COVERAGE" for f in response.findings))
        self.assertEqual(guarded.assessment("R1", content_hash(artifact)).status, "VERIFIED_COVERAGE")


if __name__ == "__main__":
    unittest.main()
