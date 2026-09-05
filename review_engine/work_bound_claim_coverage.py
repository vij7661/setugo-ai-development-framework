from __future__ import annotations

from .claim_coverage import (
    ClaimCoverageAssessment,
    ClaimCoverageInventory,
    RetainedClaimCoverageRegistry,
)
from .extraction_work import ExtractionWorkRegistry


class WorkOrderBoundClaimCoverageRegistry:
    """Coverage registry admitted only through platform-issued extraction work."""

    qualified_admission_enforced = True
    trusted_scope_binding_enforced = True

    def __init__(self, work_registry: ExtractionWorkRegistry) -> None:
        self._work = work_registry
        self._coverage = RetainedClaimCoverageRegistry()
        self._admission: dict[str, dict[str, object]] = {}

    def add(self, inventory: ClaimCoverageInventory, *, work_order_id: str) -> None:
        order = self._work.validate_inventory(work_order_id, inventory)
        # Only consume the work order after the coverage registry accepts the
        # inventory, so an unrelated registry validation error cannot burn a
        # valid capability before admission completes.
        self._coverage.add(inventory)
        self._work.consume(work_order_id)
        self._admission[inventory.inventory_id] = {
            "work_order_id": order.work_order_id,
            "artifact_hash": order.artifact_hash,
            "risk": order.risk,
            "task_type": order.task_type,
            "extractor_id": order.extractor_id,
            "qualification_ref": order.qualification_ref,
            "qualification_epoch": order.qualification_epoch,
        }

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
