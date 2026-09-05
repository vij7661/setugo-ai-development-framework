from __future__ import annotations

from dataclasses import replace
from typing import Callable

from .claim_coverage import ClaimCoverageAssessment, ClaimCoverageValidator
from .models import ReviewerConfig, ReviewerResponse, content_hash
from .truth_contract import validate_epistemic_review

ReviewerInvoker = Callable[[ReviewerConfig, dict], ReviewerResponse]


class ClaimCoverageGuardedInvoker:
    """Platform-side wrapper that turns independent coverage evidence into findings.

    The reviewer cannot suppress these findings because they are added after the
    model/provider response is returned. For R1 the artifact hash is derived from
    the returned artifact content; for R2/R3 the platform-bound response hash is
    used. A configured coverage validator therefore fails closed when no exact,
    complete, lineage-independent inventory exists.
    """

    def __init__(self, invoker: ReviewerInvoker, validator: ClaimCoverageValidator) -> None:
        self._invoke = invoker
        self._validator = validator
        self._last_assessments: dict[tuple[str, str], ClaimCoverageAssessment] = {}

    def __call__(self, config: ReviewerConfig, context: dict) -> ReviewerResponse:
        response = self._invoke(config, context)
        response.validate()
        if not response.epistemic_review:
            return response

        normalized = validate_epistemic_review(response.epistemic_review)
        artifact_hash = response.artifact_hash or content_hash(response.output)
        assessment = self._validator.assess(
            artifact_hash=artifact_hash,
            declared_claims=normalized["claims"],
            reviewer_foundation_lineage=config.foundation_lineage,
        )
        self._last_assessments[(config.role, artifact_hash)] = assessment
        platform_findings = assessment.findings(config.role)
        if not platform_findings:
            return response
        return replace(response, findings=tuple(response.findings) + platform_findings)

    def assessment(self, role: str, artifact_hash: str) -> ClaimCoverageAssessment | None:
        return self._last_assessments.get((role, artifact_hash))
