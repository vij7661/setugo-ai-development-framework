from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from .claim_coverage import ClaimCoverageInventory, ClaimExtractorIdentity
from .extractor_qualification import ExtractorQualificationRegistry, RISK_ORDER


def _sha256_hex(value: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError("artifact_hash must be a sha256 hex digest")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError("artifact_hash must be a sha256 hex digest") from exc
    return value.lower()


@dataclass(frozen=True)
class ExtractionWorkOrder:
    """Platform-issued, single-use extraction scope.

    The work order binds the exact artifact and governance scope to the qualified
    extractor identity. It is platform bookkeeping/capability state, not a
    cryptographic provider runtime attestation and not external-action authority.
    """

    work_order_id: str
    artifact_hash: str
    risk: str
    task_type: str
    extractor_id: str
    qualification_ref: str
    qualification_epoch: int

    def validate(self) -> None:
        if not isinstance(self.work_order_id, str) or not self.work_order_id.strip():
            raise ValueError("extraction work_order_id required")
        _sha256_hex(self.artifact_hash)
        if self.risk not in RISK_ORDER:
            raise ValueError("invalid extraction work-order risk")
        if not isinstance(self.task_type, str) or not self.task_type.strip():
            raise ValueError("extraction work-order task_type required")
        if not isinstance(self.extractor_id, str) or not self.extractor_id.strip():
            raise ValueError("extraction work-order extractor_id required")
        if not isinstance(self.qualification_ref, str) or not self.qualification_ref.strip():
            raise ValueError("extraction work-order qualification_ref required")
        if self.qualification_epoch < 1:
            raise ValueError("extraction work-order qualification_epoch must be >= 1")


class ExtractionWorkRegistry:
    """Issues and consumes platform-scoped extraction work.

    Work scope is read from the retained order at admission, so callers cannot
    lower risk or swap task type by passing new admission arguments. Orders are
    single-use to prevent replay of an extraction capability across inventories.
    """

    def __init__(self, qualification_registry: ExtractorQualificationRegistry) -> None:
        self._qualifications = qualification_registry
        self._orders: dict[str, ExtractionWorkOrder] = {}
        self._consumed: set[str] = set()

    def issue(
        self,
        *,
        artifact_hash: str,
        extractor_identity: ClaimExtractorIdentity,
        risk: str,
        task_type: str = "GENERAL",
    ) -> ExtractionWorkOrder:
        artifact_hash = _sha256_hex(artifact_hash)
        decision = self._qualifications.evaluate(
            extractor_identity,
            risk=risk,
            task_type=task_type,
        )
        if not decision.eligible:
            raise ValueError(f"cannot issue extraction work: {decision.reason}")
        order = ExtractionWorkOrder(
            work_order_id="extract-work:" + uuid4().hex,
            artifact_hash=artifact_hash,
            risk=risk,
            task_type=task_type,
            extractor_id=extractor_identity.extractor_id,
            qualification_ref=decision.qualification_ref or extractor_identity.qualification_ref,
            qualification_epoch=decision.qualification_epoch or extractor_identity.qualification_epoch,
        )
        order.validate()
        self._orders[order.work_order_id] = order
        return order

    def validate_inventory(
        self,
        work_order_id: str,
        inventory: ClaimCoverageInventory,
    ) -> ExtractionWorkOrder:
        inventory.validate()
        order = self._orders.get(work_order_id)
        if order is None:
            raise ValueError("extraction work order not found")
        if work_order_id in self._consumed:
            raise ValueError("extraction work order already consumed")
        order.validate()
        if inventory.artifact_hash.lower() != order.artifact_hash:
            raise ValueError("extraction inventory artifact does not match work order")
        identity = inventory.extractor_identity
        if identity.extractor_id != order.extractor_id:
            raise ValueError("extraction inventory extractor does not match work order")
        if identity.qualification_ref != order.qualification_ref:
            raise ValueError("extraction inventory qualification_ref does not match work order")
        if identity.qualification_epoch != order.qualification_epoch:
            raise ValueError("extraction inventory qualification_epoch does not match work order")

        # Re-evaluate at admission so revocation, epoch advancement or binding
        # changes after issuance invalidate the outstanding work order.
        decision = self._qualifications.evaluate(
            identity,
            risk=order.risk,
            task_type=order.task_type,
        )
        if not decision.eligible:
            raise ValueError(f"extraction work no longer qualified: {decision.reason}")
        return order

    def consume(self, work_order_id: str) -> None:
        if work_order_id not in self._orders:
            raise ValueError("extraction work order not found")
        if work_order_id in self._consumed:
            raise ValueError("extraction work order already consumed")
        self._consumed.add(work_order_id)

    def get(self, work_order_id: str) -> ExtractionWorkOrder | None:
        return self._orders.get(work_order_id)

    def is_consumed(self, work_order_id: str) -> bool:
        return work_order_id in self._consumed
