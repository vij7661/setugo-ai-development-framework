from __future__ import annotations

from dataclasses import dataclass

from .models import ReviewerConfig

RISK_ORDER = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}
QUALIFICATION_STATUSES = {"QUALIFIED", "PENDING", "REVOKED", "EXPIRED", "UNQUALIFIED"}


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


class QualificationRegistry:
    def __init__(self, records: tuple[QualificationRecord, ...] = ()) -> None:
        self._records: dict[str, QualificationRecord] = {}
        for record in records:
            self.add(record)

    def add(self, record: QualificationRecord) -> None:
        record.validate()
        current = self._records.get(record.qualification_ref)
        if current is not None and record.qualification_epoch <= current.qualification_epoch:
            raise ValueError("qualification epoch must advance")
        self._records[record.qualification_ref] = record

    def evaluate(self, config: ReviewerConfig, *, risk: str, task_type: str = "GENERAL") -> QualificationDecision:
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

    def get(self, qualification_ref: str) -> QualificationRecord | None:
        return self._records.get(qualification_ref)
