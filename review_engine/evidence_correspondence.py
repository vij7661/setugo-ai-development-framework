from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from hashlib import sha256
from typing import Iterable, Protocol

VERDICTS = {"SUPPORTS", "CONTRADICTS", "INSUFFICIENT"}
ASSESSMENT_STATES = {
    "VERIFIED_SUPPORT",
    "VERIFIED_CONTRADICTION",
    "CONFLICT",
    "INSUFFICIENT",
    "UNVERIFIED",
}


def claim_fingerprint(text: str) -> str:
    """Bind attestations to a normalized exact claim, not a model claim_id."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("claim text required")
    normalized = " ".join(text.split())
    return sha256(normalized.encode("utf-8")).hexdigest()


def _sha256_hex(value: str, field: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"{field} must be a sha256 hex digest")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be a sha256 hex digest") from exc
    return value.lower()


@dataclass(frozen=True)
class EvidenceVerifierIdentity:
    """Platform-retained bookkeeping identity for evidence verification.

    This binds qualification and assessment records to a concrete configured
    provider/model/SKU/deployment path/foundation lineage. It is not universal
    cryptographic proof that a remote provider executed that exact model.
    """

    provider: str
    model: str
    sku: str
    deployment_path: str
    foundation_lineage: str
    qualification_ref: str
    qualification_epoch: int

    def validate(self) -> None:
        for field in (
            "provider",
            "model",
            "sku",
            "deployment_path",
            "foundation_lineage",
            "qualification_ref",
        ):
            value = getattr(self, field)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"evidence verifier identity {field} required")
        if self.qualification_epoch < 1:
            raise ValueError("evidence verifier qualification_epoch must be >= 1")

    @property
    def verifier_id(self) -> str:
        self.validate()
        payload = json.dumps(
            {
                "provider": self.provider,
                "model": self.model,
                "sku": self.sku,
                "deployment_path": self.deployment_path,
                "foundation_lineage": self.foundation_lineage,
                "qualification_ref": self.qualification_ref,
                "qualification_epoch": self.qualification_epoch,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        return "evidence-verifier:" + sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class EvidenceCorrespondenceAttestation:
    """Platform-retained independent evidence-to-claim assessment.

    Raw/reference registries may retain structurally valid records without a
    structured verifier identity. A governed qualification-enforced registry
    requires `verifier_identity` and independently checks its eligibility.
    """

    attestation_id: str
    artifact_hash: str
    claim_fingerprint: str
    evidence_ref: str
    evidence_content_hash: str
    verdict: str
    verifier_id: str
    provenance: str
    qualification_ref: str | None = None
    verifier_identity: EvidenceVerifierIdentity | None = None

    def validate(self) -> None:
        for field in ("attestation_id", "evidence_ref", "verifier_id", "provenance"):
            value = getattr(self, field)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"evidence attestation {field} required")
        _sha256_hex(self.artifact_hash, "artifact_hash")
        _sha256_hex(self.claim_fingerprint, "claim_fingerprint")
        _sha256_hex(self.evidence_content_hash, "evidence_content_hash")
        if self.verdict not in VERDICTS:
            raise ValueError("invalid evidence correspondence verdict")
        if self.qualification_ref is not None and not self.qualification_ref.strip():
            raise ValueError("qualification_ref cannot be blank")
        if self.verifier_identity is not None:
            self.verifier_identity.validate()
            if self.verifier_id != self.verifier_identity.verifier_id:
                raise ValueError("evidence attestation verifier_id does not match verifier identity")
            if self.qualification_ref != self.verifier_identity.qualification_ref:
                raise ValueError("evidence attestation qualification_ref does not match verifier identity")


@dataclass(frozen=True)
class ClaimEvidenceAssessment:
    claim_id: str
    claim_fingerprint: str
    artifact_hash: str
    status: str
    evidence_refs: tuple[str, ...]
    attestation_ids: tuple[str, ...]
    verifier_ids: tuple[str, ...]
    provenance: tuple[str, ...]

    def validate(self) -> None:
        if self.status not in ASSESSMENT_STATES:
            raise ValueError("invalid evidence assessment status")
        _sha256_hex(self.claim_fingerprint, "claim_fingerprint")
        _sha256_hex(self.artifact_hash, "artifact_hash")

    def as_dict(self) -> dict:
        self.validate()
        return asdict(self)


class EvidenceCorrespondenceValidator(Protocol):
    def assess(
        self,
        *,
        artifact_hash: str,
        claim: dict,
        risk: str = "LOW",
        task_type: str = "GENERAL",
    ) -> ClaimEvidenceAssessment: ...


class RetainedEvidenceCorrespondenceRegistry:
    """In-memory reference registry for retained correspondence attestations.

    This raw registry performs exact artifact/claim/evidence matching but does
    not independently qualify verifier identity. GOVERNED application assurance
    must use a qualification-enforced validator instead.
    """

    def __init__(self, attestations: Iterable[EvidenceCorrespondenceAttestation] = ()) -> None:
        self._records: dict[tuple[str, str, str, str], EvidenceCorrespondenceAttestation] = {}
        self._ids: dict[str, EvidenceCorrespondenceAttestation] = {}
        for attestation in attestations:
            self.add(attestation)

    def add(self, attestation: EvidenceCorrespondenceAttestation) -> None:
        attestation.validate()
        previous_id = self._ids.get(attestation.attestation_id)
        if previous_id is not None and previous_id != attestation:
            raise ValueError("conflicting evidence attestation_id")
        key = (
            attestation.artifact_hash.lower(),
            attestation.claim_fingerprint.lower(),
            attestation.evidence_ref,
            attestation.verifier_id,
        )
        previous = self._records.get(key)
        if previous is not None and previous != attestation:
            raise ValueError("conflicting retained evidence correspondence attestation")
        self._ids[attestation.attestation_id] = attestation
        self._records[key] = attestation

    @staticmethod
    def _claim_inputs(*, artifact_hash: str, claim: dict) -> tuple[str, str, str, tuple[str, ...]]:
        artifact_hash = _sha256_hex(artifact_hash, "artifact_hash")
        claim_id = str(claim.get("claim_id", "")).strip()
        text = str(claim.get("text", "")).strip()
        if not claim_id or not text:
            raise ValueError("claim_id and claim text required for evidence assessment")
        raw_refs = claim.get("evidence_refs", [])
        if not isinstance(raw_refs, list):
            raise ValueError("claim evidence_refs must be a list")
        evidence_refs = tuple(str(value).strip() for value in raw_refs if str(value).strip())
        return artifact_hash, claim_id, claim_fingerprint(text), evidence_refs

    def matching_attestations(self, *, artifact_hash: str, claim: dict) -> tuple[EvidenceCorrespondenceAttestation, ...]:
        artifact_hash, _, fingerprint, evidence_refs = self._claim_inputs(
            artifact_hash=artifact_hash,
            claim=claim,
        )
        return tuple(
            record
            for (bound_artifact, bound_claim, evidence_ref, _), record in self._records.items()
            if bound_artifact == artifact_hash
            and bound_claim == fingerprint
            and evidence_ref in evidence_refs
        )

    @staticmethod
    def assessment_from_records(
        *,
        artifact_hash: str,
        claim: dict,
        records: Iterable[EvidenceCorrespondenceAttestation],
    ) -> ClaimEvidenceAssessment:
        artifact_hash, claim_id, fingerprint, evidence_refs = RetainedEvidenceCorrespondenceRegistry._claim_inputs(
            artifact_hash=artifact_hash,
            claim=claim,
        )
        matched = tuple(records)
        verdicts = {record.verdict for record in matched}
        if "SUPPORTS" in verdicts and "CONTRADICTS" in verdicts:
            status = "CONFLICT"
        elif "CONTRADICTS" in verdicts:
            status = "VERIFIED_CONTRADICTION"
        elif "SUPPORTS" in verdicts:
            status = "VERIFIED_SUPPORT"
        elif matched:
            status = "INSUFFICIENT"
        else:
            status = "UNVERIFIED"

        return ClaimEvidenceAssessment(
            claim_id=claim_id,
            claim_fingerprint=fingerprint,
            artifact_hash=artifact_hash,
            status=status,
            evidence_refs=evidence_refs,
            attestation_ids=tuple(sorted(record.attestation_id for record in matched)),
            verifier_ids=tuple(sorted({record.verifier_id for record in matched})),
            provenance=tuple(sorted({record.provenance for record in matched})),
        )

    def assess(
        self,
        *,
        artifact_hash: str,
        claim: dict,
        risk: str = "LOW",
        task_type: str = "GENERAL",
    ) -> ClaimEvidenceAssessment:
        # risk/task_type are accepted for protocol compatibility; this raw
        # reference registry deliberately does not claim qualification enforcement.
        del risk, task_type
        return self.assessment_from_records(
            artifact_hash=artifact_hash,
            claim=claim,
            records=self.matching_attestations(artifact_hash=artifact_hash, claim=claim),
        )
