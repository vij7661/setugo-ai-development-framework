from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from hashlib import sha256
from typing import Iterable, Protocol

from .evidence_correspondence import claim_fingerprint
from .models import ReviewFinding

CLAIM_TYPES = {
    "EMPIRICAL_FACT",
    "LOGICAL_CLAIM",
    "DEFINITION",
    "INFERENCE",
    "ASSUMPTION",
    "HYPOTHESIS",
    "OPINION",
    "RECOMMENDATION",
}
COVERAGE_STATES = {
    "VERIFIED_COVERAGE",
    "OMITTED_MATERIAL_CLAIM",
    "MISCLASSIFIED_MATERIAL_CLAIM",
    "CONFLICT",
    "UNVERIFIED",
}


def _sha256_hex(value: str, field: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"{field} must be a sha256 hex digest")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be a sha256 hex digest") from exc
    return value.lower()


@dataclass(frozen=True)
class ClaimExtractorIdentity:
    """Platform-retained identity for an independent claim-coverage extractor.

    This is bookkeeping identity bound to the configured extraction path. It is
    not universal cryptographic proof that the remote provider executed that
    exact model; runtime provider attestation remains a separate integration
    boundary.
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
                raise ValueError(f"claim extractor identity {field} required")
        if self.qualification_epoch < 1:
            raise ValueError("claim extractor qualification_epoch must be >= 1")

    @property
    def extractor_id(self) -> str:
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
        return "claim-extractor:" + sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class CoverageClaim:
    text: str
    claim_type: str
    material: bool

    def validate(self) -> None:
        if not isinstance(self.text, str) or not self.text.strip():
            raise ValueError("coverage claim text required")
        if self.claim_type not in CLAIM_TYPES:
            raise ValueError("invalid coverage claim type")
        if not isinstance(self.material, bool):
            raise ValueError("coverage claim material must be boolean")

    @property
    def fingerprint(self) -> str:
        self.validate()
        return claim_fingerprint(self.text)


@dataclass(frozen=True)
class ClaimCoverageInventory:
    """Complete, artifact-bound claim inventory retained by the platform.

    Admission is a trusted integration responsibility. A model under review
    cannot create one by mentioning claims in its own response. Only complete
    inventories are admissible for omission decisions.
    """

    inventory_id: str
    artifact_hash: str
    claims: tuple[CoverageClaim, ...]
    extractor_identity: ClaimExtractorIdentity
    provenance: str
    complete: bool = True

    def validate(self) -> None:
        if not isinstance(self.inventory_id, str) or not self.inventory_id.strip():
            raise ValueError("claim coverage inventory_id required")
        _sha256_hex(self.artifact_hash, "artifact_hash")
        if not isinstance(self.provenance, str) or not self.provenance.strip():
            raise ValueError("claim coverage provenance required")
        if not isinstance(self.complete, bool):
            raise ValueError("claim coverage complete must be boolean")
        self.extractor_identity.validate()
        seen: set[str] = set()
        for claim in self.claims:
            claim.validate()
            fingerprint = claim.fingerprint
            if fingerprint in seen:
                raise ValueError("duplicate claim fingerprint in coverage inventory")
            seen.add(fingerprint)


@dataclass(frozen=True)
class ClaimCoverageAssessment:
    artifact_hash: str
    status: str
    inventory_ids: tuple[str, ...]
    extractor_ids: tuple[str, ...]
    provenance: tuple[str, ...]
    missing_claims: tuple[tuple[str, str, str], ...] = ()
    misclassified_claims: tuple[tuple[str, str, str, str], ...] = ()
    correlation_warnings: tuple[str, ...] = ()

    def validate(self) -> None:
        _sha256_hex(self.artifact_hash, "artifact_hash")
        if self.status not in COVERAGE_STATES:
            raise ValueError("invalid claim coverage status")

    def as_dict(self) -> dict:
        self.validate()
        return asdict(self)

    def findings(self, reviewer_role: str) -> tuple[ReviewFinding, ...]:
        self.validate()
        findings: list[ReviewFinding] = []
        if self.status == "UNVERIFIED":
            findings.append(
                ReviewFinding(
                    finding_id="tvc-coverage-unverified",
                    reviewer_role=reviewer_role,
                    severity="HIGH",
                    material=True,
                    summary="Independent claim coverage is unavailable for the exact artifact/reviewer lineage.",
                    violated_invariant="TVC-COVERAGE",
                    affected_scope=("artifact:claim-coverage",),
                )
            )
        elif self.status == "CONFLICT":
            findings.append(
                ReviewFinding(
                    finding_id="tvc-coverage-conflict",
                    reviewer_role=reviewer_role,
                    severity="HIGH",
                    material=True,
                    summary="Independent claim coverage inventories conflict on a material truth-bearer.",
                    violated_invariant="TVC-COVERAGE",
                    affected_scope=("artifact:claim-coverage",),
                )
            )

        for fingerprint, text, expected_type in self.missing_claims:
            findings.append(
                ReviewFinding(
                    finding_id=f"tvc-coverage-omitted-{fingerprint[:16]}",
                    reviewer_role=reviewer_role,
                    severity="HIGH",
                    material=True,
                    summary=f"Material claim omitted from reviewer epistemic inventory: {text}",
                    violated_invariant="TVC-COVERAGE",
                    affected_scope=(f"claim-fingerprint:{fingerprint}",),
                    first_invalid_claim=text,
                )
            )

        for fingerprint, text, expected_type, declared_type in self.misclassified_claims:
            findings.append(
                ReviewFinding(
                    finding_id=f"tvc-coverage-misclassified-{fingerprint[:16]}",
                    reviewer_role=reviewer_role,
                    severity="HIGH",
                    material=True,
                    summary=(
                        "Material claim classification does not match independent coverage evidence: "
                        f"expected {expected_type}, reviewer declared {declared_type}: {text}"
                    ),
                    violated_invariant="TVC-COVERAGE",
                    affected_scope=(f"claim-fingerprint:{fingerprint}",),
                    first_invalid_claim=text,
                )
            )

        for finding in findings:
            finding.validate()
        return tuple(findings)


class ClaimCoverageValidator(Protocol):
    def assess(
        self,
        *,
        artifact_hash: str,
        declared_claims: list[dict],
        reviewer_foundation_lineage: str,
    ) -> ClaimCoverageAssessment: ...


class RetainedClaimCoverageRegistry:
    """Reference registry for trusted, complete claim-coverage inventories.

    It does not perform language understanding itself. A future independently
    qualified extractor/challenger service may implement the same protocol and
    produce artifact-bound inventories. The governed default requires an exact
    artifact inventory from a different foundation lineage than the reviewer.
    """

    def __init__(self, inventories: Iterable[ClaimCoverageInventory] = ()) -> None:
        self._inventories: dict[tuple[str, str], ClaimCoverageInventory] = {}
        self._ids: dict[str, ClaimCoverageInventory] = {}
        for inventory in inventories:
            self.add(inventory)

    def add(self, inventory: ClaimCoverageInventory) -> None:
        inventory.validate()
        previous_id = self._ids.get(inventory.inventory_id)
        if previous_id is not None and previous_id != inventory:
            raise ValueError("conflicting claim coverage inventory_id")
        key = (inventory.artifact_hash.lower(), inventory.extractor_identity.extractor_id)
        previous = self._inventories.get(key)
        if previous is not None and previous != inventory:
            raise ValueError("conflicting retained claim coverage inventory")
        self._ids[inventory.inventory_id] = inventory
        self._inventories[key] = inventory

    def assess(
        self,
        *,
        artifact_hash: str,
        declared_claims: list[dict],
        reviewer_foundation_lineage: str,
    ) -> ClaimCoverageAssessment:
        artifact_hash = _sha256_hex(artifact_hash, "artifact_hash")
        if not isinstance(reviewer_foundation_lineage, str) or not reviewer_foundation_lineage.strip():
            raise ValueError("reviewer_foundation_lineage required for independent claim coverage")
        if not isinstance(declared_claims, list):
            raise ValueError("declared_claims must be a list")

        exact = [
            inventory
            for (bound_artifact, _), inventory in self._inventories.items()
            if bound_artifact == artifact_hash and inventory.complete
        ]
        independent = [
            inventory
            for inventory in exact
            if inventory.extractor_identity.foundation_lineage != reviewer_foundation_lineage
        ]
        warnings = tuple(
            sorted(
                f"CORRELATED_EXTRACTOR:{inventory.extractor_identity.extractor_id}"
                for inventory in exact
                if inventory.extractor_identity.foundation_lineage == reviewer_foundation_lineage
            )
        )

        if not independent:
            return ClaimCoverageAssessment(
                artifact_hash=artifact_hash,
                status="UNVERIFIED",
                inventory_ids=(),
                extractor_ids=(),
                provenance=(),
                correlation_warnings=warnings,
            )

        required: dict[str, CoverageClaim] = {}
        conflict = False
        for inventory in independent:
            for claim in inventory.claims:
                fingerprint = claim.fingerprint
                previous = required.get(fingerprint)
                if previous is not None and (
                    previous.claim_type != claim.claim_type or previous.material != claim.material
                ):
                    conflict = True
                elif previous is None:
                    required[fingerprint] = claim

        declared: dict[str, dict] = {}
        for claim in declared_claims:
            if not isinstance(claim, dict):
                raise ValueError("declared epistemic claim must be an object")
            text = str(claim.get("text", "")).strip()
            if not text:
                raise ValueError("declared epistemic claim text required")
            declared[claim_fingerprint(text)] = claim

        missing: list[tuple[str, str, str]] = []
        misclassified: list[tuple[str, str, str, str]] = []
        for fingerprint, coverage_claim in required.items():
            if not coverage_claim.material:
                continue
            reviewer_claim = declared.get(fingerprint)
            if reviewer_claim is None:
                missing.append((fingerprint, coverage_claim.text, coverage_claim.claim_type))
                continue
            declared_type = str(reviewer_claim.get("claim_type", ""))
            declared_material = reviewer_claim.get("material", False)
            if declared_type != coverage_claim.claim_type or declared_material is not True:
                effective_declared = declared_type if declared_material is True else f"{declared_type}/material=false"
                misclassified.append(
                    (fingerprint, coverage_claim.text, coverage_claim.claim_type, effective_declared)
                )

        if conflict:
            status = "CONFLICT"
        elif missing:
            status = "OMITTED_MATERIAL_CLAIM"
        elif misclassified:
            status = "MISCLASSIFIED_MATERIAL_CLAIM"
        else:
            status = "VERIFIED_COVERAGE"

        return ClaimCoverageAssessment(
            artifact_hash=artifact_hash,
            status=status,
            inventory_ids=tuple(sorted(inventory.inventory_id for inventory in independent)),
            extractor_ids=tuple(sorted({inventory.extractor_identity.extractor_id for inventory in independent})),
            provenance=tuple(sorted({inventory.provenance for inventory in independent})),
            missing_claims=tuple(sorted(missing)),
            misclassified_claims=tuple(sorted(misclassified)),
            correlation_warnings=warnings,
        )
