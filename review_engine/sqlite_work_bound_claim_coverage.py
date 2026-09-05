from __future__ import annotations

from .claim_coverage import (
    ClaimCoverageAssessment,
    ClaimCoverageInventory,
    RetainedClaimCoverageRegistry,
)
from .sqlite_extraction_work import SQLiteExtractionWorkRegistry


class SQLiteWorkOrderBoundClaimCoverageRegistry:
    """Governed claim coverage backed by atomically retained SQLite inventories.

    The underlying SQLite extraction-work registry validates qualification and
    work-order scope, persists the complete inventory and consumes the single-use
    work order in one transaction. Assessments rebuild the reference coverage
    view from durable retained inventories for the exact artifact.
    """

    qualified_admission_enforced = True
    trusted_scope_binding_enforced = True
    durable_work_state_enforced = True
    durable_inventory_state_enforced = True
    atomic_inventory_admission_enforced = True

    def __init__(self, work_registry: SQLiteExtractionWorkRegistry) -> None:
        if not bool(getattr(work_registry, "durable_replay_protection_enforced", False)):
            raise ValueError("SQLite work-bound claim coverage requires durable work replay protection")
        if not bool(getattr(work_registry, "durable_inventory_state_enforced", False)):
            raise ValueError("SQLite work-bound claim coverage requires durable inventory state")
        if not bool(getattr(work_registry, "atomic_inventory_admission_enforced", False)):
            raise ValueError("SQLite work-bound claim coverage requires atomic inventory admission")
        self._work = work_registry

    def add(self, inventory: ClaimCoverageInventory, *, work_order_id: str) -> None:
        self._work.consume_for_inventory(work_order_id, inventory)

    def assess(
        self,
        *,
        artifact_hash: str,
        declared_claims: list[dict],
        reviewer_foundation_lineage: str,
    ) -> ClaimCoverageAssessment:
        retained = self._work.retained_inventories(artifact_hash)
        return RetainedClaimCoverageRegistry(retained).assess(
            artifact_hash=artifact_hash,
            declared_claims=declared_claims,
            reviewer_foundation_lineage=reviewer_foundation_lineage,
        )

    def admission_evidence(self, inventory_id: str) -> dict[str, object] | None:
        inventory = self._work.retained_inventory(inventory_id)
        if inventory is None:
            return None
        return {
            "inventory_id": inventory.inventory_id,
            "artifact_hash": inventory.artifact_hash,
            "extractor_id": inventory.extractor_identity.extractor_id,
            "qualification_ref": inventory.extractor_identity.qualification_ref,
            "qualification_epoch": inventory.extractor_identity.qualification_epoch,
            "provenance": inventory.provenance,
            "durable_inventory_state": True,
            "atomic_work_consumption": True,
        }
