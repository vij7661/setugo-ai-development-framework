from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .evidence_correspondence import EvidenceCorrespondenceValidator, claim_fingerprint
from .models import ReviewFinding

TVC_VERSION = "TVC-1"

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
CORRESPONDENCE_STATES = {"SUPPORTED", "UNSUPPORTED", "UNVERIFIED", "NOT_APPLICABLE"}
COHERENCE_STATES = {"CONSISTENT", "CONTRADICTED", "UNRESOLVED"}
PRAGMATIC_STATES = {"VIABLE", "LIMITED", "NOT_VIABLE", "NOT_APPLICABLE"}
SEMANTIC_STATES = {"PRECISE", "AMBIGUOUS", "MISLEADING"}


@dataclass(frozen=True)
class TruthContractResult:
    normalized: dict[str, Any]
    findings: tuple[ReviewFinding, ...]
    evidence_assessments: tuple[dict[str, Any], ...] = ()


def epistemic_protocol_instructions() -> dict[str, Any]:
    """Machine-readable reviewer protocol.

    The protocol separates correspondence, coherence, pragmatic utility and
    semantic precision. It is evidence structure, not a correctness oracle.
    """
    return {
        "version": TVC_VERSION,
        "correspondence": "Empirical facts need admissible evidence or must remain explicitly unverified.",
        "coherence": "Contradictions and unresolved conflicts must be surfaced, not silently harmonized.",
        "pragmatic": "Operational utility is evaluated separately and cannot override factual or governance defects.",
        "semantic": "Distinguish facts, logical claims, definitions, inferences, assumptions, hypotheses, opinions and recommendations.",
        "agreement_is_not_truth": True,
        "model_judgment_is_evidence_not_authority": True,
        "material_supported_empirical_claim_requires_platform_correspondence": True,
        "evidence_ref_presence_is_not_correspondence_proof": True,
        "claim_types": sorted(CLAIM_TYPES),
        "required_response_object": "epistemic_review",
    }


def neutral_epistemic_review() -> dict[str, Any]:
    """Useful only for platform tests/adapters that have no empirical claim.

    External model responses are still required to send this object explicitly;
    provider parsing never silently manufactures it.
    """
    return {
        "version": TVC_VERSION,
        "correspondence": "NOT_APPLICABLE",
        "coherence": "CONSISTENT",
        "pragmatic": "NOT_APPLICABLE",
        "semantic": "PRECISE",
        "claims": [],
        "contradiction_refs": [],
    }


def _string_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"epistemic_review.{field} must be a list")
    result: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise ValueError(f"epistemic_review.{field} entries must be non-empty strings")
        result.append(item.strip())
    return result


def validate_epistemic_review(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError("epistemic_review object required")
    if value.get("version") != TVC_VERSION:
        raise ValueError(f"epistemic_review.version must be {TVC_VERSION}")

    correspondence = str(value.get("correspondence", ""))
    coherence = str(value.get("coherence", ""))
    pragmatic = str(value.get("pragmatic", ""))
    semantic = str(value.get("semantic", ""))
    if correspondence not in CORRESPONDENCE_STATES:
        raise ValueError("invalid epistemic correspondence state")
    if coherence not in COHERENCE_STATES:
        raise ValueError("invalid epistemic coherence state")
    if pragmatic not in PRAGMATIC_STATES:
        raise ValueError("invalid epistemic pragmatic state")
    if semantic not in SEMANTIC_STATES:
        raise ValueError("invalid epistemic semantic state")

    contradiction_refs = _string_list(value.get("contradiction_refs", []), "contradiction_refs")
    if coherence == "CONTRADICTED" and not contradiction_refs:
        raise ValueError("contradicted epistemic review requires contradiction_refs")

    raw_claims = value.get("claims")
    if not isinstance(raw_claims, list):
        raise ValueError("epistemic_review.claims must be a list")

    claims: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for index, raw in enumerate(raw_claims):
        if not isinstance(raw, dict):
            raise ValueError("epistemic claim must be an object")
        claim_id = str(raw.get("claim_id", "")).strip()
        text = str(raw.get("text", "")).strip()
        claim_type = str(raw.get("claim_type", ""))
        claim_correspondence = str(raw.get("correspondence", ""))
        if not claim_id or not text:
            raise ValueError("epistemic claim_id and text required")
        if claim_id in seen_ids:
            raise ValueError(f"duplicate epistemic claim_id: {claim_id}")
        seen_ids.add(claim_id)
        if claim_type not in CLAIM_TYPES:
            raise ValueError(f"invalid epistemic claim_type at index {index}")
        if claim_correspondence not in CORRESPONDENCE_STATES:
            raise ValueError(f"invalid claim correspondence at index {index}")
        evidence_refs = _string_list(raw.get("evidence_refs", []), f"claims[{index}].evidence_refs")
        material = raw.get("material", False)
        if not isinstance(material, bool):
            raise ValueError("epistemic claim material must be boolean")

        # Structural invariant only. The platform correspondence validator below
        # separately checks whether retained independent evidence actually
        # supports the exact bound claim/artifact.
        if claim_type == "EMPIRICAL_FACT" and claim_correspondence == "SUPPORTED" and not evidence_refs:
            raise ValueError("supported empirical fact requires evidence_refs")

        claims.append(
            {
                "claim_id": claim_id,
                "text": text,
                "claim_type": claim_type,
                "correspondence": claim_correspondence,
                "evidence_refs": evidence_refs,
                "material": material,
            }
        )

    return {
        "version": TVC_VERSION,
        "correspondence": correspondence,
        "coherence": coherence,
        "pragmatic": pragmatic,
        "semantic": semantic,
        "claims": claims,
        "contradiction_refs": contradiction_refs,
    }


def _unverified_platform_assessment(*, artifact_hash: str | None, claim: dict) -> dict[str, Any]:
    return {
        "claim_id": claim["claim_id"],
        "claim_fingerprint": claim_fingerprint(claim["text"]),
        "artifact_hash": artifact_hash,
        "status": "UNVERIFIED",
        "evidence_refs": list(claim["evidence_refs"]),
        "attestation_ids": [],
        "verifier_ids": [],
        "provenance": [],
    }


def evaluate_truth_contract(
    role: str,
    review: dict[str, Any],
    *,
    artifact_hash: str | None = None,
    evidence_validator: EvidenceCorrespondenceValidator | None = None,
) -> TruthContractResult:
    """Convert explicit epistemic failures into platform-visible findings.

    Reviewer labels remain evidence. The platform owns the consequence mapping.
    A model saying an empirical claim is SUPPORTED is insufficient for material
    correspondence: the exact claim/artifact/evidence binding needs a retained
    independent platform-side assessment.
    """
    normalized = validate_epistemic_review(review)
    findings: list[ReviewFinding] = []
    evidence_assessments: list[dict[str, Any]] = []

    for claim in normalized["claims"]:
        if claim["claim_type"] != "EMPIRICAL_FACT":
            continue

        if claim["correspondence"] in {"UNSUPPORTED", "UNVERIFIED"}:
            severity = "HIGH" if claim["material"] else "MEDIUM"
            findings.append(
                ReviewFinding(
                    finding_id=f"tvc-correspondence-{claim['claim_id']}",
                    reviewer_role=role,
                    severity=severity,
                    material=bool(claim["material"]),
                    summary=f"Empirical claim is {claim['correspondence'].lower()}: {claim['text']}",
                    violated_invariant="TVC-CORRESPONDENCE",
                    evidence_refs=tuple(claim["evidence_refs"]),
                    affected_scope=(f"claim:{claim['claim_id']}",),
                    first_invalid_claim=claim["text"],
                )
            )
            continue

        if claim["correspondence"] == "SUPPORTED":
            if evidence_validator is not None and artifact_hash is not None:
                assessment = evidence_validator.assess(artifact_hash=artifact_hash, claim=claim).as_dict()
            else:
                assessment = _unverified_platform_assessment(artifact_hash=artifact_hash, claim=claim)
            evidence_assessments.append(assessment)
            status = assessment["status"]
            if status == "VERIFIED_SUPPORT":
                continue

            severity = "HIGH" if claim["material"] else "MEDIUM"
            material = bool(claim["material"])
            if status == "VERIFIED_CONTRADICTION":
                summary = f"Retained evidence contradicts reviewer-supported empirical claim: {claim['text']}"
            elif status == "CONFLICT":
                summary = f"Retained evidence is materially conflicting for empirical claim: {claim['text']}"
            elif status == "INSUFFICIENT":
                summary = f"Retained evidence is insufficient to verify reviewer-supported empirical claim: {claim['text']}"
            else:
                summary = f"Reviewer-supported empirical claim lacks platform-verified evidence correspondence: {claim['text']}"
            findings.append(
                ReviewFinding(
                    finding_id=f"tvc-evidence-correspondence-{claim['claim_id']}",
                    reviewer_role=role,
                    severity=severity,
                    material=material,
                    summary=summary,
                    violated_invariant="TVC-EVIDENCE-CORRESPONDENCE",
                    evidence_refs=tuple(claim["evidence_refs"]),
                    affected_scope=(f"claim:{claim['claim_id']}",),
                    first_invalid_claim=claim["text"],
                )
            )

    material_claim_present = any(bool(claim["material"]) for claim in normalized["claims"])

    if normalized["coherence"] == "CONTRADICTED":
        findings.append(
            ReviewFinding(
                finding_id="tvc-coherence-contradiction",
                reviewer_role=role,
                severity="HIGH",
                material=True,
                summary="Epistemic review reports an unresolved contradiction.",
                violated_invariant="TVC-COHERENCE",
                evidence_refs=tuple(normalized["contradiction_refs"]),
                affected_scope=("artifact:coherence",),
            )
        )
    elif normalized["coherence"] == "UNRESOLVED":
        findings.append(
            ReviewFinding(
                finding_id="tvc-coherence-unresolved",
                reviewer_role=role,
                severity="MEDIUM",
                material=material_claim_present,
                summary="Epistemic review reports unresolved internal coherence.",
                violated_invariant="TVC-COHERENCE",
                evidence_refs=tuple(normalized["contradiction_refs"]),
                affected_scope=("artifact:coherence",),
            )
        )

    if normalized["semantic"] == "MISLEADING":
        findings.append(
            ReviewFinding(
                finding_id="tvc-semantic-misleading",
                reviewer_role=role,
                severity="HIGH",
                material=True,
                summary="Epistemic review reports materially misleading truth-bearer presentation.",
                violated_invariant="TVC-SEMANTIC-PRECISION",
                affected_scope=("artifact:semantic-presentation",),
            )
        )
    elif normalized["semantic"] == "AMBIGUOUS":
        findings.append(
            ReviewFinding(
                finding_id="tvc-semantic-ambiguous",
                reviewer_role=role,
                severity="MEDIUM",
                material=material_claim_present,
                summary="Epistemic review reports semantic ambiguity.",
                violated_invariant="TVC-SEMANTIC-PRECISION",
                affected_scope=("artifact:semantic-presentation",),
            )
        )

    if normalized["pragmatic"] == "NOT_VIABLE":
        findings.append(
            ReviewFinding(
                finding_id="tvc-pragmatic-not-viable",
                reviewer_role=role,
                severity="MEDIUM",
                material=material_claim_present,
                summary="Epistemic review reports that the proposal is not operationally viable.",
                violated_invariant="TVC-PRAGMATIC-UTILITY",
                affected_scope=("artifact:operational-utility",),
            )
        )

    # Summary correspondence is a cross-check, not a substitute for claim-level
    # evidence. It may raise an issue but can never certify correctness.
    if normalized["correspondence"] in {"UNSUPPORTED", "UNVERIFIED"} and not any(
        f.violated_invariant == "TVC-CORRESPONDENCE" for f in findings
    ):
        findings.append(
            ReviewFinding(
                finding_id="tvc-correspondence-summary",
                reviewer_role=role,
                severity="MEDIUM",
                material=material_claim_present,
                summary=f"Epistemic review correspondence status is {normalized['correspondence']}.",
                violated_invariant="TVC-CORRESPONDENCE",
                affected_scope=("artifact:correspondence",),
            )
        )

    for finding in findings:
        finding.validate()
    return TruthContractResult(
        normalized=normalized,
        findings=tuple(findings),
        evidence_assessments=tuple(evidence_assessments),
    )
