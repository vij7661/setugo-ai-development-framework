from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from threading import RLock
from uuid import uuid4

from .models import ReviewerConfig

RISK_ORDER = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}
QUALIFICATION_STATUSES = {"QUALIFIED", "PENDING", "REVOKED", "EXPIRED", "UNQUALIFIED"}


def reviewer_context_hash(context: dict) -> str:
    """Return a deterministic binding for the exact model-visible context."""
    if not isinstance(context, dict):
        raise ValueError("reviewer context must be an object")
    try:
        canonical = json.dumps(
            context,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise ValueError("reviewer context must be canonical JSON data") from exc
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class QualificationRecord:
    qualification_ref: str
    provider: str
    model: str
    sku: str
    deployment_path: str
    role: str
    status: str
    qualification_epoch: int
    foundation_lineage: str
    max_risk: str
    task_types: tuple[str, ...] = ("*",)

    def validate(self) -> None:
        if not self.qualification_ref:
            raise ValueError("qualification_ref required")
        if self.role not in {"R1", "R2", "R3"}:
            raise ValueError("invalid qualification role")
        if self.status not in QUALIFICATION_STATUSES:
            raise ValueError("invalid qualification status")
        if self.max_risk not in RISK_ORDER:
            raise ValueError("invalid qualification max_risk")
        if self.qualification_epoch < 1:
            raise ValueError("qualification_epoch must be positive")
        if not self.task_types:
            raise ValueError("qualification task_types cannot be empty")


@dataclass(frozen=True)
class QualificationDecision:
    eligible: bool
    reason: str
    qualification_ref: str | None = None
    qualification_epoch: int | None = None


@dataclass(frozen=True)
class ReviewerCapability:
    """Platform-issued, single-use reviewer invocation authority.

    The capability is the linearization point between qualification state and one
    governed provider invocation. It is bound to the exact retained qualification
    epoch, reviewer identity, risk/task, request/phase/artifact scope and the
    canonical hash of the exact model-visible context.

    Revocation before issuance prevents issuance; a later revocation applies to
    future capabilities rather than retroactively rewriting authority that was
    already issued for one call.

    This is platform bookkeeping, not cryptographic proof of remote provider
    runtime identity and not authority for external/production actions.
    """

    capability_id: str
    qualification_ref: str
    qualification_epoch: int
    provider: str
    model: str
    sku: str
    deployment_path: str
    role: str
    foundation_lineage: str
    risk: str
    task_type: str
    request_id: str
    phase: str
    context_hash: str
    artifact_hash: str | None = None

    def validate(self) -> None:
        if not self.capability_id:
            raise ValueError("reviewer capability_id required")
        if not self.qualification_ref:
            raise ValueError("reviewer capability qualification_ref required")
        if self.qualification_epoch < 1:
            raise ValueError("reviewer capability qualification_epoch must be positive")
        if self.role not in {"R1", "R2", "R3"}:
            raise ValueError("invalid reviewer capability role")
        if self.risk not in RISK_ORDER:
            raise ValueError("invalid reviewer capability risk")
        if not self.task_type:
            raise ValueError("reviewer capability task_type required")
        if not self.request_id:
            raise ValueError("reviewer capability request_id required")
        if not self.phase:
            raise ValueError("reviewer capability phase required")
        if len(self.context_hash) != 64 or any(ch not in "0123456789abcdef" for ch in self.context_hash):
            raise ValueError("reviewer capability context_hash must be a sha256 hex digest")
        if self.artifact_hash is not None and not self.artifact_hash:
            raise ValueError("reviewer capability artifact_hash cannot be empty")


class QualificationRegistry:
    def __init__(self, records: tuple[QualificationRecord, ...] = ()) -> None:
        self._lock = RLock()
        self._records: dict[str, QualificationRecord] = {}
        self._capabilities: dict[str, ReviewerCapability] = {}
        self._consumed_capabilities: set[str] = set()
        for record in records:
            self.add(record)

    def add(self, record: QualificationRecord) -> None:
        record.validate()
        with self._lock:
            current = self._records.get(record.qualification_ref)
            if current is not None and record.qualification_epoch <= current.qualification_epoch:
                raise ValueError("qualification epoch must advance")
            self._records[record.qualification_ref] = record

    def _evaluate_unlocked(
        self,
        config: ReviewerConfig,
        *,
        risk: str,
        task_type: str = "GENERAL",
    ) -> QualificationDecision:
        if risk not in RISK_ORDER:
            raise ValueError("invalid risk")
        ref = config.qualification_ref
        if not ref:
            return QualificationDecision(False, "reviewer has no retained qualification reference")
        record = self._records.get(ref)
        if record is None:
            return QualificationDecision(False, "qualification reference not found", ref)
        if record.status != "QUALIFIED":
            return QualificationDecision(False, f"qualification status is {record.status}", ref, record.qualification_epoch)

        bindings = {
            "provider": (record.provider, config.provider),
            "model": (record.model, config.model),
            "sku": (record.sku, config.sku),
            "deployment_path": (record.deployment_path, config.deployment_path),
            "role": (record.role, config.role),
            "foundation_lineage": (record.foundation_lineage, config.foundation_lineage),
        }
        for name, (expected, actual) in bindings.items():
            if expected != actual:
                return QualificationDecision(False, f"qualification {name} binding mismatch", ref, record.qualification_epoch)
        if RISK_ORDER[risk] > RISK_ORDER[record.max_risk]:
            return QualificationDecision(False, "qualification does not cover requested risk", ref, record.qualification_epoch)
        if "*" not in record.task_types and task_type not in record.task_types:
            return QualificationDecision(False, "qualification does not cover requested task type", ref, record.qualification_epoch)
        return QualificationDecision(True, "qualified", ref, record.qualification_epoch)

    def evaluate(self, config: ReviewerConfig, *, risk: str, task_type: str = "GENERAL") -> QualificationDecision:
        with self._lock:
            return self._evaluate_unlocked(config, risk=risk, task_type=task_type)

    def issue_capability(
        self,
        config: ReviewerConfig,
        *,
        risk: str,
        task_type: str = "GENERAL",
        request_id: str,
        phase: str,
        context_hash: str,
        artifact_hash: str | None = None,
    ) -> tuple[QualificationDecision, ReviewerCapability | None]:
        """Atomically evaluate current qualification state and issue one call.

        `add()` uses the same lock, so qualification epoch/status transitions
        cannot interleave between the eligibility read and capability creation.
        """
        if not request_id:
            raise ValueError("reviewer capability request_id required")
        if not phase:
            raise ValueError("reviewer capability phase required")
        if len(context_hash) != 64 or any(ch not in "0123456789abcdef" for ch in context_hash):
            raise ValueError("reviewer capability context_hash must be a sha256 hex digest")
        if artifact_hash is not None and not artifact_hash:
            raise ValueError("reviewer capability artifact_hash cannot be empty")
        with self._lock:
            decision = self._evaluate_unlocked(config, risk=risk, task_type=task_type)
            if not decision.eligible:
                return decision, None
            ref = decision.qualification_ref or config.qualification_ref
            if not ref:
                raise RuntimeError("eligible qualification decision lacks reference")
            record = self._records.get(ref)
            if record is None:
                raise RuntimeError("eligible qualification record disappeared during issuance")
            capability = ReviewerCapability(
                capability_id="review-cap:" + uuid4().hex,
                qualification_ref=record.qualification_ref,
                qualification_epoch=record.qualification_epoch,
                provider=record.provider,
                model=record.model,
                sku=record.sku,
                deployment_path=record.deployment_path,
                role=record.role,
                foundation_lineage=record.foundation_lineage,
                risk=risk,
                task_type=task_type,
                request_id=request_id,
                phase=phase,
                context_hash=context_hash,
                artifact_hash=artifact_hash,
            )
            capability.validate()
            self._capabilities[capability.capability_id] = capability
            return decision, capability

    def consume_capability(
        self,
        capability_id: str,
        config: ReviewerConfig,
        *,
        risk: str,
        task_type: str = "GENERAL",
        request_id: str,
        phase: str,
        context_hash: str,
        artifact_hash: str | None = None,
    ) -> ReviewerCapability:
        """Consume exactly one issued capability without allowing scope reuse."""
        with self._lock:
            capability = self._capabilities.get(capability_id)
            if capability is None:
                raise ValueError("reviewer capability not found")
            if capability_id in self._consumed_capabilities:
                raise ValueError("reviewer capability already consumed")
            bindings = {
                "provider": (capability.provider, config.provider),
                "model": (capability.model, config.model),
                "sku": (capability.sku, config.sku),
                "deployment_path": (capability.deployment_path, config.deployment_path),
                "role": (capability.role, config.role),
                "foundation_lineage": (capability.foundation_lineage, config.foundation_lineage),
                "qualification_ref": (capability.qualification_ref, config.qualification_ref),
                "risk": (capability.risk, risk),
                "task_type": (capability.task_type, task_type),
                "request_id": (capability.request_id, request_id),
                "phase": (capability.phase, phase),
                "context_hash": (capability.context_hash, context_hash),
                "artifact_hash": (capability.artifact_hash, artifact_hash),
            }
            for name, (expected, actual) in bindings.items():
                if expected != actual:
                    raise ValueError(f"reviewer capability {name} binding mismatch")
            self._consumed_capabilities.add(capability_id)
            return capability

    def get(self, qualification_ref: str) -> QualificationRecord | None:
        with self._lock:
            return self._records.get(qualification_ref)

    def get_capability(self, capability_id: str) -> ReviewerCapability | None:
        with self._lock:
            return self._capabilities.get(capability_id)

    def capability_consumed(self, capability_id: str) -> bool:
        with self._lock:
            return capability_id in self._consumed_capabilities
