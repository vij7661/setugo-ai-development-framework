from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
from typing import Any

MEMORY_CLASSES = {
    "AUTHORITATIVE",
    "PROJECT",
    "WORKING",
    "REVIEW_EVIDENCE",
    "MODEL_PRIVATE",
    "PROTECTED_TRUTH",
}
MEMORY_STATUSES = {"ACTIVE", "SUPERSEDED", "REVOKED", "HISTORICAL", "PENDING"}
REVIEW_ROLES = {"R1", "R2", "R3"}
SEVERITIES = {"NONE", "LOW", "MEDIUM", "HIGH", "CRITICAL"}


def content_hash(text: str) -> str:
    return sha256(text.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ReviewerConfig:
    role: str
    provider: str
    model: str
    sku: str
    deployment_path: str
    api_key_env: str
    foundation_lineage: str
    qualification_ref: str | None = None
    enabled: bool = True

    def validate(self) -> None:
        if self.role not in REVIEW_ROLES:
            raise ValueError("invalid reviewer role")
        for name in ("provider", "model", "sku", "deployment_path", "api_key_env", "foundation_lineage"):
            if not getattr(self, name):
                raise ValueError(f"reviewer {name} required")
        if not self.api_key_env.replace("_", "").isalnum():
            raise ValueError("api_key_env must be an environment/secret name, not a raw key")


@dataclass(frozen=True)
class ReviewRequest:
    request_id: str
    user_input: str
    risk: str = "LOW"
    materiality: str = "NONE"
    external_action: bool = False
    mutation_requested: bool = False
    requirement_ambiguity: bool = False
    evidence_complete: bool = True
    uncertainty: str = "LOW"
    platform_facts: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ReviewArtifact:
    artifact_id: str
    version: int
    content: str

    @property
    def artifact_hash(self) -> str:
        return content_hash(self.content)


@dataclass(frozen=True)
class ReviewFinding:
    finding_id: str
    reviewer_role: str
    severity: str
    material: bool
    summary: str
    violated_invariant: str | None = None
    evidence_refs: tuple[str, ...] = ()
    affected_scope: tuple[str, ...] = ()
    first_invalid_claim: str | None = None

    def validate(self) -> None:
        if self.reviewer_role not in REVIEW_ROLES:
            raise ValueError("invalid finding reviewer role")
        if self.severity not in SEVERITIES:
            raise ValueError("invalid finding severity")
        if not self.finding_id or not self.summary:
            raise ValueError("finding id and summary required")


@dataclass(frozen=True)
class ReviewerResponse:
    role: str
    artifact_hash: str | None
    output: str
    findings: tuple[ReviewFinding, ...] = ()
    complete: bool = True
    proposed_signals: dict[str, Any] = field(default_factory=dict)
    # Structured Truth & Veracity Contract evidence. Direct in-process test
    # adapters may omit it; real provider adapters validate and populate it.
    epistemic_review: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if self.role not in REVIEW_ROLES:
            raise ValueError("invalid response role")
        if not self.complete:
            raise ValueError("incomplete reviewer response is not admissible")
        if not isinstance(self.epistemic_review, dict):
            raise ValueError("epistemic_review must be an object")
        for finding in self.findings:
            finding.validate()
            if finding.reviewer_role != self.role:
                raise ValueError("finding role must match response role")


@dataclass(frozen=True)
class ReviewDecision:
    state: str
    reasons: tuple[str, ...]
    final_output: str | None = None
    artifact_hash: str | None = None
    dissent: tuple[str, ...] = ()


@dataclass(frozen=True)
class MemoryRecord:
    record_id: str
    memory_class: str
    status: str
    version: int
    provenance: str
    content: str
    source_role: str | None = None
    supersedes_version: int | None = None

    def validate(self) -> None:
        if not self.record_id:
            raise ValueError("memory record_id required")
        if self.memory_class not in MEMORY_CLASSES:
            raise ValueError("invalid memory class")
        if self.status not in MEMORY_STATUSES:
            raise ValueError("invalid memory status")
        if self.version < 1:
            raise ValueError("memory version must be >= 1")
        if not self.provenance:
            raise ValueError("memory provenance required")
        if self.source_role is not None and self.source_role not in REVIEW_ROLES:
            raise ValueError("invalid memory source role")
