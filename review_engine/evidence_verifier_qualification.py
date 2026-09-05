from __future__ import annotations

from dataclasses import dataclass

from .evidence_correspondence import EvidenceVerifierIdentity

RISK_ORDER = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}
QUALIFICATION_STATUSES = {"QUALIFIED", "PENDING", "REVOKED", "EXPIRED", "UNQUALIFIED"}


@dataclass(frozen=True)
class EvidenceVerifierQualificationRecord:
    """Retained qualification for independent evidence-correspondence verification."""

    qualification_ref: str
    provider: str
    model: str
    sku: str
    deployment_path: str
    foundation_lineage: str
    status: str
    qualification_epoch: int
    max_risk: str
    task_types: tuple[str, ...] = ("*",)

    def validate(self) -> None:
        for field in (
            "qualification_ref",
            "provider",
            "model",
            "sku",
            "deployment_path",
            "foundation_lineage",
        ):
            value = getattr(self, field)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"evidence verifier qualification {field} required")
        if self.status not in QUALIFICATION_STATUSES:
            raise ValueError("invalid evidence verifier qualification status")
        if self.qualification_epoch < 1:
            raise ValueError("evidence verifier qualification_epoch must be >= 1")
        if self.max_risk not in RISK_ORDER:
            raise ValueError("invalid evidence verifier qualification max_risk")
        if not self.task_types or any(not isinstance(v, str) or not v.strip() for v in self.task_types):
            raise ValueError("evidence verifier qualification task_types cannot be empty or blank")


@dataclass(frozen=True)
class EvidenceVerifierQualificationDecision:
    eligible: bool
    reason: str
    qualification_ref: str | None = None
    qualification_epoch: int | None = None


class EvidenceVerifierQualificationRegistry:
    def __init__(self, records: tuple[EvidenceVerifierQualificationRecord, ...] = ()) -> None:
        self._records: dict[str, EvidenceVerifierQualificationRecord] = {}
        for record in records:
            self.add(record)

    def add(self, record: EvidenceVerifierQualificationRecord) -> None:
        record.validate()
        current = self._records.get(record.qualification_ref)
        if current is not None and record.qualification_epoch <= current.qualification_epoch:
            raise ValueError("evidence verifier qualification epoch must advance")
        self._records[record.qualification_ref] = record

    def evaluate(
        self,
        identity: EvidenceVerifierIdentity,
        *,
        risk: str,
        task_type: str = "GENERAL",
    ) -> EvidenceVerifierQualificationDecision:
        identity.validate()
        if risk not in RISK_ORDER:
            raise ValueError("invalid evidence verifier qualification risk")
        if not isinstance(task_type, str) or not task_type.strip():
            raise ValueError("evidence verifier qualification task_type required")

        ref = identity.qualification_ref
        record = self._records.get(ref)
        if record is None:
            return EvidenceVerifierQualificationDecision(
                False, "evidence verifier qualification reference not found", ref
            )
        if record.status != "QUALIFIED":
            return EvidenceVerifierQualificationDecision(
                False,
                f"evidence verifier qualification status is {record.status}",
                ref,
                record.qualification_epoch,
            )

        bindings = {
            "provider": (record.provider, identity.provider),
            "model": (record.model, identity.model),
            "sku": (record.sku, identity.sku),
            "deployment_path": (record.deployment_path, identity.deployment_path),
            "foundation_lineage": (record.foundation_lineage, identity.foundation_lineage),
            "qualification_epoch": (record.qualification_epoch, identity.qualification_epoch),
        }
        for name, (expected, actual) in bindings.items():
            if expected != actual:
                return EvidenceVerifierQualificationDecision(
                    False,
                    f"evidence verifier qualification {name} binding mismatch",
                    ref,
                    record.qualification_epoch,
                )

        if RISK_ORDER[risk] > RISK_ORDER[record.max_risk]:
            return EvidenceVerifierQualificationDecision(
                False,
                "evidence verifier qualification does not cover requested risk",
                ref,
                record.qualification_epoch,
            )
        if "*" not in record.task_types and task_type not in record.task_types:
            return EvidenceVerifierQualificationDecision(
                False,
                "evidence verifier qualification does not cover requested task type",
                ref,
                record.qualification_epoch,
            )
        return EvidenceVerifierQualificationDecision(True, "qualified", ref, record.qualification_epoch)

    def get(self, qualification_ref: str) -> EvidenceVerifierQualificationRecord | None:
        return self._records.get(qualification_ref)
