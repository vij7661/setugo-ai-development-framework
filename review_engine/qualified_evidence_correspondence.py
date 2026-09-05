from __future__ import annotations

from typing import Iterable

from .evidence_correspondence import (
    ClaimEvidenceAssessment,
    EvidenceCorrespondenceAttestation,
    RetainedEvidenceCorrespondenceRegistry,
)
from .evidence_verifier_qualification import EvidenceVerifierQualificationRegistry


class QualifiedRetainedEvidenceCorrespondenceRegistry:
    """Evidence correspondence usable only from qualified verifier identities.

    Attestations are structurally retained only when they carry a structured
    verifier identity. At assessment time the verifier is requalified against
    the actual platform review risk and task type. Revocation, stale epochs,
    substitution and out-of-scope qualifications therefore cannot continue to
    produce VERIFIED_SUPPORT.
    """

    qualified_verifier_assessment_enforced = True

    def __init__(
        self,
        qualification_registry: EvidenceVerifierQualificationRegistry,
        attestations: Iterable[EvidenceCorrespondenceAttestation] = (),
    ) -> None:
        self._qualifications = qualification_registry
        self._records = RetainedEvidenceCorrespondenceRegistry()
        for attestation in attestations:
            self.add(attestation)

    def add(self, attestation: EvidenceCorrespondenceAttestation) -> None:
        attestation.validate()
        identity = attestation.verifier_identity
        if identity is None:
            raise ValueError("qualified evidence correspondence requires structured verifier identity")
        # Reject missing/revoked/substituted/stale identities at admission using
        # only static binding/status checks. Risk/task scope is re-evaluated from
        # the actual review context at assess() time.
        record = self._qualifications.get(identity.qualification_ref)
        if record is None:
            raise ValueError("evidence verifier qualification reference not found")
        if record.status != "QUALIFIED":
            raise ValueError(f"evidence verifier qualification status is {record.status}")
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
                raise ValueError(f"evidence verifier qualification {name} binding mismatch")
        self._records.add(attestation)

    def assess(
        self,
        *,
        artifact_hash: str,
        claim: dict,
        risk: str = "LOW",
        task_type: str = "GENERAL",
    ) -> ClaimEvidenceAssessment:
        matched = self._records.matching_attestations(
            artifact_hash=artifact_hash,
            claim=claim,
        )
        eligible: list[EvidenceCorrespondenceAttestation] = []
        for attestation in matched:
            identity = attestation.verifier_identity
            if identity is None:
                continue
            decision = self._qualifications.evaluate(
                identity,
                risk=risk,
                task_type=task_type,
            )
            if decision.eligible:
                eligible.append(attestation)

        return self._records.assessment_from_records(
            artifact_hash=artifact_hash,
            claim=claim,
            records=eligible,
        )
