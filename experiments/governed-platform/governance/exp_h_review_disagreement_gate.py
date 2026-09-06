from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Optional, Tuple


ALLOWED_FAILURE_CLASSES = {
    "CODE DEFECT",
    "FIXTURE-DATA DEFECT",
    "TEST DEFECT",
    "ENVIRONMENT-TOOLING DEFECT",
    "REQUIREMENT UNRESOLVED",
    "NO MATERIAL DEFECT",
}

ALLOWED_ARTIFACT_SCOPES = {
    "CODE",
    "FIXTURE-DATA",
    "TEST",
    "ENVIRONMENT-TOOLING",
}

NO_MUTATION_CLASSES = {"REQUIREMENT UNRESOLVED", "NO MATERIAL DEFECT"}


class GateState(str, Enum):
    INVALID_REVIEW_INPUT = "INVALID_REVIEW_INPUT"
    ESCALATE_INDEPENDENT_ADJUDICATION = "ESCALATE_INDEPENDENT_ADJUDICATION"
    REQUIRE_INDEPENDENT_VERIFICATION = "REQUIRE_INDEPENDENT_VERIFICATION"
    VERIFICATION_CONFLICT = "VERIFICATION_CONFLICT"
    ELIGIBLE_FOR_GOVERNANCE_GATE = "ELIGIBLE_FOR_GOVERNANCE_GATE"


@dataclass(frozen=True)
class ReviewClaim:
    reviewer_id: str
    case_id: str
    primary_failure_class: str
    authorized_artifact_scope: Tuple[str, ...]

    def canonical_scope(self) -> Tuple[str, ...]:
        return tuple(sorted(set(self.authorized_artifact_scope)))


@dataclass(frozen=True)
class VerificationArtifact:
    issuer: str
    platform_issued: bool
    valid: bool
    case_id: str
    primary_failure_class: str
    authorized_artifact_scope: Tuple[str, ...]

    def canonical_scope(self) -> Tuple[str, ...]:
        return tuple(sorted(set(self.authorized_artifact_scope)))


@dataclass(frozen=True)
class GateDecision:
    state: GateState
    case_id: Optional[str]
    canonical_primary_failure_class: Optional[str]
    canonical_artifact_scope: Tuple[str, ...]
    reasons: Tuple[str, ...]
    reviewer_generated_authority: bool = False
    terminal_approval: bool = False


def _validate_review(review: ReviewClaim) -> Optional[str]:
    if not review.reviewer_id:
        return "missing reviewer_id"
    if not review.case_id:
        return "missing case_id"
    if review.primary_failure_class not in ALLOWED_FAILURE_CLASSES:
        return f"invalid failure class: {review.primary_failure_class}"
    invalid_scope = sorted(set(review.authorized_artifact_scope) - ALLOWED_ARTIFACT_SCOPES)
    if invalid_scope:
        return f"invalid artifact scope: {','.join(invalid_scope)}"
    if review.primary_failure_class in NO_MUTATION_CLASSES and review.canonical_scope():
        return f"{review.primary_failure_class} must have empty artifact scope"
    return None


def evaluate_review_gate(
    reviews: Iterable[ReviewClaim],
    verification: Optional[VerificationArtifact] = None,
) -> GateDecision:
    reviews = tuple(reviews)
    if not reviews:
        return GateDecision(
            state=GateState.INVALID_REVIEW_INPUT,
            case_id=None,
            canonical_primary_failure_class=None,
            canonical_artifact_scope=(),
            reasons=("no reviews supplied",),
        )

    invalid_reasons = tuple(
        reason
        for review in reviews
        for reason in [_validate_review(review)]
        if reason is not None
    )
    if invalid_reasons:
        return GateDecision(
            state=GateState.INVALID_REVIEW_INPUT,
            case_id=None,
            canonical_primary_failure_class=None,
            canonical_artifact_scope=(),
            reasons=invalid_reasons,
        )

    case_ids = {review.case_id for review in reviews}
    if len(case_ids) != 1:
        return GateDecision(
            state=GateState.INVALID_REVIEW_INPUT,
            case_id=None,
            canonical_primary_failure_class=None,
            canonical_artifact_scope=(),
            reasons=("review case_id mismatch",),
        )

    case_id = next(iter(case_ids))
    primary_classes = {review.primary_failure_class for review in reviews}
    if len(primary_classes) != 1:
        return GateDecision(
            state=GateState.ESCALATE_INDEPENDENT_ADJUDICATION,
            case_id=case_id,
            canonical_primary_failure_class=None,
            canonical_artifact_scope=(),
            reasons=("material primary-class disagreement",),
        )

    canonical_primary = next(iter(primary_classes))
    scopes = {review.canonical_scope() for review in reviews}
    if len(scopes) != 1:
        return GateDecision(
            state=GateState.ESCALATE_INDEPENDENT_ADJUDICATION,
            case_id=case_id,
            canonical_primary_failure_class=canonical_primary,
            canonical_artifact_scope=(),
            reasons=("material artifact-scope disagreement",),
        )

    canonical_scope = next(iter(scopes))

    if verification is None:
        return GateDecision(
            state=GateState.REQUIRE_INDEPENDENT_VERIFICATION,
            case_id=case_id,
            canonical_primary_failure_class=canonical_primary,
            canonical_artifact_scope=canonical_scope,
            reasons=("reviewer consensus is evidence only; independent verification required",),
        )

    if not verification.platform_issued or not verification.valid:
        return GateDecision(
            state=GateState.VERIFICATION_CONFLICT,
            case_id=case_id,
            canonical_primary_failure_class=canonical_primary,
            canonical_artifact_scope=canonical_scope,
            reasons=("verification is not valid platform-issued evidence",),
        )

    if verification.case_id != case_id:
        return GateDecision(
            state=GateState.VERIFICATION_CONFLICT,
            case_id=case_id,
            canonical_primary_failure_class=canonical_primary,
            canonical_artifact_scope=canonical_scope,
            reasons=("verification case binding mismatch",),
        )

    if verification.primary_failure_class != canonical_primary:
        return GateDecision(
            state=GateState.VERIFICATION_CONFLICT,
            case_id=case_id,
            canonical_primary_failure_class=canonical_primary,
            canonical_artifact_scope=canonical_scope,
            reasons=("verification primary-class conflict",),
        )

    if verification.canonical_scope() != canonical_scope:
        return GateDecision(
            state=GateState.VERIFICATION_CONFLICT,
            case_id=case_id,
            canonical_primary_failure_class=canonical_primary,
            canonical_artifact_scope=canonical_scope,
            reasons=("verification artifact-scope conflict",),
        )

    return GateDecision(
        state=GateState.ELIGIBLE_FOR_GOVERNANCE_GATE,
        case_id=case_id,
        canonical_primary_failure_class=canonical_primary,
        canonical_artifact_scope=canonical_scope,
        reasons=("exact review consensus plus matching platform-owned verification",),
    )
