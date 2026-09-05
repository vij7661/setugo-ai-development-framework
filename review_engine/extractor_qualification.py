from __future__ import annotations

from dataclasses import dataclass

from .claim_coverage import ClaimExtractorIdentity

RISK_ORDER = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}
QUALIFICATION_STATUSES = {"QUALIFIED", "PENDING", "REVOKED", "EXPIRED", "UNQUALIFIED"}


@dataclass(frozen=True)
class ExtractorQualificationRecord:
    """Retained qualification for the claim-extraction role.

    Extraction is deliberately not modeled as R1/R2/R3. Eligibility is bound
    to provider/model/SKU/deployment path/foundation lineage, qualification
    epoch, risk ceiling and task scope.
    """

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
                raise ValueError(f"extractor qualification {field} required")
        if self.status not in QUALIFICATION_STATUSES:
            raise ValueError("invalid extractor qualification status")
        if self.qualification_epoch < 1:
            raise ValueError("extractor qualification_epoch must be >= 1")
        if self.max_risk not in RISK_ORDER:
            raise ValueError("invalid extractor qualification max_risk")
        if not self.task_types or any(not isinstance(v, str) or not v.strip() for v in self.task_types):
            raise ValueError("extractor qualification task_types cannot be empty or blank")


@dataclass(frozen=True)
class ExtractorQualificationDecision:
    eligible: bool
    reason: str
    qualification_ref: str | None = None
    qualification_epoch: int | None = None


class ExtractorQualificationRegistry:
    def __init__(self, records: tuple[ExtractorQualificationRecord, ...] = ()) -> None:
        self._records: dict[str, ExtractorQualificationRecord] = {}
        for record in records:
            self.add(record)

    def add(self, record: ExtractorQualificationRecord) -> None:
        record.validate()
        current = self._records.get(record.qualification_ref)
        if current is not None and record.qualification_epoch <= current.qualification_epoch:
            raise ValueError("extractor qualification epoch must advance")
        self._records[record.qualification_ref] = record

    def evaluate(
        self,
        identity: ClaimExtractorIdentity,
        *,
        risk: str,
        task_type: str = "GENERAL",
    ) -> ExtractorQualificationDecision:
        identity.validate()
        if risk not in RISK_ORDER:
            raise ValueError("invalid extractor qualification risk")
        if not isinstance(task_type, str) or not task_type.strip():
            raise ValueError("extractor qualification task_type required")

        ref = identity.qualification_ref
        record = self._records.get(ref)
        if record is None:
            return ExtractorQualificationDecision(False, "extractor qualification reference not found", ref)
        if record.status != "QUALIFIED":
            return ExtractorQualificationDecision(
                False,
                f"extractor qualification status is {record.status}",
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
                return ExtractorQualificationDecision(
                    False,
                    f"extractor qualification {name} binding mismatch",
                    ref,
                    record.qualification_epoch,
                )

        if RISK_ORDER[risk] > RISK_ORDER[record.max_risk]:
            return ExtractorQualificationDecision(
                False,
                "extractor qualification does not cover requested risk",
                ref,
                record.qualification_epoch,
            )
        if "*" not in record.task_types and task_type not in record.task_types:
            return ExtractorQualificationDecision(
                False,
                "extractor qualification does not cover requested task type",
                ref,
                record.qualification_epoch,
            )
        return ExtractorQualificationDecision(True, "qualified", ref, record.qualification_epoch)

    def get(self, qualification_ref: str) -> ExtractorQualificationRecord | None:
        return self._records.get(qualification_ref)
