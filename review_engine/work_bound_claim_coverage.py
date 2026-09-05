from __future__ import annotations

from typing import Any

from .claim_coverage import (
    ClaimCoverageAssessment,
    ClaimCoverageInventory,
    RetainedClaimCoverageRegistry,
)


class WorkOrderBoundClaimCoverageRegistry:
    """Coverage registry admitted only through platform-issued extraction work.

    When the work registry exposes `consume_for_inventory`, inventory validation
    and replay-state consumption happen atomically in that registry before the
    local coverage inventory is retained. This is the required path for durable
    cross-restart/concurrent replay protection.
    """

    qualified_admission_enforced = True
    trusted_scope_binding_enforced = True

    def __init__(self, work_registry: Any) -> None:
        self._work = work_registry
        self._coverage = RetainedClaimCoverageRegistry()
        self._admission: dict[str, dict[str, object]] = {}

    @property
    def durable_work_state_enforced(self) -> bool:
        return bool(getattr(self._work, "durable_replay_protection_enforced", False))

    def add(self, inventory: ClaimCoverageInventory, *, work_order_id: str) -> None:
        atomic_consume = getattr(self._work, "consume_for_inventory", None)
        if callable(atomic_consume):
            # Durable registries validate + consume in one transaction so two
            # processes cannot both admit the same work capability. If the
            # subsequent local coverage add fails, the capability remains spent:
            # fail-closed is preferable to reopening a consumed capability.
            order = atomic_consume(work_order_id, inventory)
            self._coverage.add(inventory)
        else:
            order = self._work.validate_inventory(work_order_id, inventory)
            # Reference/in-memory path only; it is not advertised as durable.
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
            "durable_replay_protection": self.durable_work_state_enforced,
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
