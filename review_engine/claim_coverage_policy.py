from __future__ import annotations

from typing import Iterable

from .claim_coverage import (
    ClaimCoverageAssessment,
    ClaimCoverageInventory,
    RetainedClaimCoverageRegistry,
)


class MinimumIndependentClaimCoverage:
    """Policy wrapper requiring multiple distinct extractor lineages/runtime paths.

    This is an optional stronger assurance policy. It prevents two aliases of the
    same extractor deployment, or two extractors from the same foundation
    lineage, from satisfying a configured multi-extractor requirement.
    """

    def __init__(
        self,
        inventories: Iterable[ClaimCoverageInventory] = (),
        *,
        minimum_independent_extractors: int = 2,
    ) -> None:
        if minimum_independent_extractors < 1:
            raise ValueError("minimum_independent_extractors must be >= 1")
        self.minimum_independent_extractors = int(minimum_independent_extractors)
        self._inventories = tuple(inventories)
        for inventory in self._inventories:
            inventory.validate()
        self._registry = RetainedClaimCoverageRegistry(self._inventories)

    def assess(
        self,
        *,
        artifact_hash: str,
        declared_claims: list[dict],
        reviewer_foundation_lineage: str,
    ) -> ClaimCoverageAssessment:
        exact = [
            inventory
            for inventory in self._inventories
            if inventory.complete and inventory.artifact_hash.lower() == artifact_hash.lower()
            and inventory.extractor_identity.foundation_lineage != reviewer_foundation_lineage
        ]

        runtime_paths: dict[tuple[str, str, str, str], set[str]] = {}
        lineages: dict[str, set[tuple[str, str, str, str]]] = {}
        for inventory in exact:
            identity = inventory.extractor_identity
            runtime = (identity.provider, identity.model, identity.sku, identity.deployment_path)
            runtime_paths.setdefault(runtime, set()).add(identity.foundation_lineage)
            lineages.setdefault(identity.foundation_lineage, set()).add(runtime)

        unique_runtime_count = len(runtime_paths)
        unique_lineage_count = len(lineages)
        effective_independent = min(unique_runtime_count, unique_lineage_count)
        warnings: list[str] = []
        if len(exact) > unique_runtime_count:
            warnings.append("CLAIM_COVERAGE_RUNTIME_ALIAS_CORRELATION")
        if len(exact) > unique_lineage_count:
            warnings.append("CLAIM_COVERAGE_FOUNDATION_LINEAGE_CORRELATION")

        if effective_independent < self.minimum_independent_extractors:
            return ClaimCoverageAssessment(
                artifact_hash=artifact_hash.lower(),
                status="UNVERIFIED",
                inventory_ids=tuple(sorted(inventory.inventory_id for inventory in exact)),
                extractor_ids=tuple(sorted({inventory.extractor_identity.extractor_id for inventory in exact})),
                provenance=tuple(sorted({inventory.provenance for inventory in exact})),
                correlation_warnings=tuple(warnings) + (
                    f"REQUIRES_{self.minimum_independent_extractors}_INDEPENDENT_EXTRACTORS_FOUND_{effective_independent}",
                ),
            )

        assessment = self._registry.assess(
            artifact_hash=artifact_hash,
            declared_claims=declared_claims,
            reviewer_foundation_lineage=reviewer_foundation_lineage,
        )
        if not warnings:
            return assessment
        return ClaimCoverageAssessment(
            artifact_hash=assessment.artifact_hash,
            status=assessment.status,
            inventory_ids=assessment.inventory_ids,
            extractor_ids=assessment.extractor_ids,
            provenance=assessment.provenance,
            missing_claims=assessment.missing_claims,
            misclassified_claims=assessment.misclassified_claims,
            correlation_warnings=tuple(sorted(set(assessment.correlation_warnings + tuple(warnings)))),
        )
