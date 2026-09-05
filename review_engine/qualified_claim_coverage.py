from __future__ import annotations

from typing import Iterable

from .claim_coverage import (
    ClaimCoverageAssessment,
    ClaimCoverageInventory,
    RetainedClaimCoverageRegistry,
)
from .extractor_qualification import ExtractorQualificationRegistry


class QualifiedRetainedClaimCoverageRegistry:
    """Coverage registry whose inventories must pass extractor qualification.

    The caller that admits a retained inventory supplies the platform-known risk
    and task type for the artifact being inventoried. An unqualified, stale,
    substituted, revoked or out-of-scope extractor is rejected before its
    inventory can become coverage evidence.
    """

    def __init__(self, qualification_registry: ExtractorQualificationRegistry) -> None:
        self._qualifications = qualification_registry
        self._coverage = RetainedClaimCoverageRegistry()
        self._admission: dict[str, dict[str, object]] = {}

    def add(
        self,
        inventory: ClaimCoverageInventory,
        *,
        risk: str,
        task_type: str = "GENERAL",
    ) -> None:
        inventory.validate()
        decision = self._qualifications.evaluate(
            inventory.extractor_identity,
            risk=risk,
            task_type=task_type,
        )
        if not decision.eligible:
            raise ValueError(f"claim coverage inventory extractor not qualified: {decision.reason}")
        self._coverage.add(inventory)
        self._admission[inventory.inventory_id] = {
            "qualification_ref": decision.qualification_ref,
            "qualification_epoch": decision.qualification_epoch,
            "risk": risk,
            "task_type": task_type,
        }

    def add_many(
        self,
        inventories: Iterable[tuple[ClaimCoverageInventory, str, str]],
    ) -> None:
        for inventory, risk, task_type in inventories:
            self.add(inventory, risk=risk, task_type=task_type)

    def assess(
        self,
        *,
        artifact_hash: str,
        declared_claims: list[dict],
        reviewer_foundation_lineage: str,
    ) -> ClaimCoverageAssessment:
        return self._coverage.assess(
            artifact_hash=artifact_hash,
            declared_claims=declared_claims,
            reviewer_foundation_lineage=reviewer_foundation_lineage,
        )

    def admission_evidence(self, inventory_id: str) -> dict[str, object] | None:
        evidence = self._admission.get(inventory_id)
        return None if evidence is None else dict(evidence)
