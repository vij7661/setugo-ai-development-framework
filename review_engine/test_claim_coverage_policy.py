from __future__ import annotations

import unittest

from review_engine.claim_coverage import (
    ClaimCoverageInventory,
    ClaimExtractorIdentity,
    CoverageClaim,
    RetainedClaimCoverageRegistry,
)
from review_engine.claim_coverage_policy import MinimumIndependentClaimCoverage
from review_engine.models import content_hash


ARTIFACT = "Deployment succeeded."


def identity(*, model: str, lineage: str, qualification_ref: str) -> ClaimExtractorIdentity:
    return ClaimExtractorIdentity(
        provider="extractor-provider",
        model=model,
        sku="default",
        deployment_path="api",
        foundation_lineage=lineage,
        qualification_ref=qualification_ref,
        qualification_epoch=1,
    )


def inventory(inventory_id: str, extractor: ClaimExtractorIdentity) -> ClaimCoverageInventory:
    return ClaimCoverageInventory(
        inventory_id=inventory_id,
        artifact_hash=content_hash(ARTIFACT),
        claims=(CoverageClaim(ARTIFACT, "EMPIRICAL_FACT", True),),
        extractor_identity=extractor,
        provenance=f"coverage:{inventory_id}",
        complete=True,
    )


def declared(text: str = ARTIFACT) -> list[dict]:
    return [{
        "claim_id": "c1",
        "text": text,
        "claim_type": "EMPIRICAL_FACT",
        "correspondence": "UNVERIFIED",
        "evidence_refs": [],
        "material": True,
    }]


class ClaimCoveragePolicyTests(unittest.TestCase):
    def test_two_distinct_runtime_and_foundation_lineages_satisfy_two_extractor_policy(self):
        policy = MinimumIndependentClaimCoverage((
            inventory("a", identity(model="extractor-a", lineage="lineage-a", qualification_ref="q-a")),
            inventory("b", identity(model="extractor-b", lineage="lineage-b", qualification_ref="q-b")),
        ), minimum_independent_extractors=2)
        result = policy.assess(
            artifact_hash=content_hash(ARTIFACT),
            declared_claims=declared(),
            reviewer_foundation_lineage="reviewer-lineage",
        )
        self.assertEqual(result.status, "VERIFIED_COVERAGE")

    def test_same_runtime_path_aliases_do_not_satisfy_two_extractor_policy(self):
        policy = MinimumIndependentClaimCoverage((
            inventory("a", identity(model="same-model", lineage="lineage-a", qualification_ref="q-a")),
            inventory("b", identity(model="same-model", lineage="lineage-b", qualification_ref="q-b")),
        ), minimum_independent_extractors=2)
        result = policy.assess(
            artifact_hash=content_hash(ARTIFACT),
            declared_claims=declared(),
            reviewer_foundation_lineage="reviewer-lineage",
        )
        self.assertEqual(result.status, "UNVERIFIED")
        self.assertIn("CLAIM_COVERAGE_RUNTIME_ALIAS_CORRELATION", result.correlation_warnings)

    def test_same_foundation_lineage_does_not_satisfy_two_extractor_policy(self):
        policy = MinimumIndependentClaimCoverage((
            inventory("a", identity(model="extractor-a", lineage="shared-lineage", qualification_ref="q-a")),
            inventory("b", identity(model="extractor-b", lineage="shared-lineage", qualification_ref="q-b")),
        ), minimum_independent_extractors=2)
        result = policy.assess(
            artifact_hash=content_hash(ARTIFACT),
            declared_claims=declared(),
            reviewer_foundation_lineage="reviewer-lineage",
        )
        self.assertEqual(result.status, "UNVERIFIED")
        self.assertIn("CLAIM_COVERAGE_FOUNDATION_LINEAGE_CORRELATION", result.correlation_warnings)

    def test_paraphrase_drift_does_not_silently_reuse_exact_claim_inventory(self):
        registry = RetainedClaimCoverageRegistry((
            inventory("a", identity(model="extractor-a", lineage="lineage-a", qualification_ref="q-a")),
        ))
        result = registry.assess(
            artifact_hash=content_hash(ARTIFACT),
            declared_claims=declared("The deployment completed successfully."),
            reviewer_foundation_lineage="reviewer-lineage",
        )
        self.assertEqual(result.status, "OMITTED_MATERIAL_CLAIM")
        self.assertTrue(result.findings("R2"))


if __name__ == "__main__":
    unittest.main()
