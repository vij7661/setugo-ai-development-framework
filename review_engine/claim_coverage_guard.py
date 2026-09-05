from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import replace
from typing import Callable, Iterator

from .claim_coverage import ClaimCoverageAssessment, ClaimCoverageValidator
from .models import ReviewerConfig, ReviewerResponse, content_hash
from .truth_contract import validate_epistemic_review

ReviewerInvoker = Callable[[ReviewerConfig, dict], ReviewerResponse]
RISK_ORDER = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}


class ClaimCoverageGuardedInvoker:
    """Platform-side wrapper that turns independent coverage evidence into findings.

    The reviewer cannot suppress these findings because they are added after the
    model/provider response is returned. A trusted application scope may bind
    coverage assessment to the current review risk/task. The per-request scope
    is held in a ContextVar so concurrent ThreadingHTTPServer requests cannot
    overwrite each other's governance state.

    R1 may raise its own risk signal. When that happens the guard raises the
    retained scope before assessing R1 and keeps the raised value for subsequent
    R2/R3 calls in the same request. A model can therefore make coverage checks
    stricter but cannot lower the platform-provided floor.
    """

    trusted_review_scope_supported = True

    def __init__(self, invoker: ReviewerInvoker, validator: ClaimCoverageValidator) -> None:
        self._invoke = invoker
        self._validator = validator
        self._last_assessments: dict[tuple[str, str], ClaimCoverageAssessment] = {}
        self._request_scope: ContextVar[dict[str, str] | None] = ContextVar(
            f"claim_coverage_scope_{id(self)}",
            default=None,
        )

    @contextmanager
    def assessment_scope(self, *, risk: str, task_type: str) -> Iterator[None]:
        if risk not in RISK_ORDER:
            raise ValueError("invalid claim coverage review risk")
        if not isinstance(task_type, str) or not task_type.strip():
            raise ValueError("claim coverage review task_type required")
        token = self._request_scope.set({"risk": risk, "task_type": task_type.strip()})
        try:
            yield
        finally:
            self._request_scope.reset(token)

    def _scope_for_response(self, config: ReviewerConfig, response: ReviewerResponse) -> tuple[str, str]:
        scope = self._request_scope.get()
        if scope is None:
            return "LOW", "GENERAL"

        risk = scope["risk"]
        if config.role == "R1":
            proposed = response.proposed_signals.get("risk")
            if isinstance(proposed, str) and proposed in RISK_ORDER and RISK_ORDER[proposed] > RISK_ORDER[risk]:
                scope["risk"] = proposed
                risk = proposed
        return risk, scope["task_type"]

    def _assess(
        self,
        *,
        artifact_hash: str,
        declared_claims: list[dict],
        reviewer_foundation_lineage: str,
        risk: str,
        task_type: str,
    ) -> ClaimCoverageAssessment:
        if bool(getattr(self._validator, "review_scope_binding_enforced", False)):
            return self._validator.assess(
                artifact_hash=artifact_hash,
                declared_claims=declared_claims,
                reviewer_foundation_lineage=reviewer_foundation_lineage,
                risk=risk,
                task_type=task_type,
            )
        return self._validator.assess(
            artifact_hash=artifact_hash,
            declared_claims=declared_claims,
            reviewer_foundation_lineage=reviewer_foundation_lineage,
        )

    def __call__(self, config: ReviewerConfig, context: dict) -> ReviewerResponse:
        response = self._invoke(config, context)
        response.validate()
        if not response.epistemic_review:
            return response

        normalized = validate_epistemic_review(response.epistemic_review)
        artifact_hash = response.artifact_hash or content_hash(response.output)
        risk, task_type = self._scope_for_response(config, response)
        assessment = self._assess(
            artifact_hash=artifact_hash,
            declared_claims=normalized["claims"],
            reviewer_foundation_lineage=config.foundation_lineage,
            risk=risk,
            task_type=task_type,
        )
        self._last_assessments[(config.role, artifact_hash)] = assessment
        platform_findings = assessment.findings(config.role)
        if not platform_findings:
            return response
        return replace(response, findings=tuple(response.findings) + platform_findings)

    def assessment(self, role: str, artifact_hash: str) -> ClaimCoverageAssessment | None:
        return self._last_assessments.get((role, artifact_hash))
