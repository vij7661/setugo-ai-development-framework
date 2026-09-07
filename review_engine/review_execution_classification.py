from __future__ import annotations

from dataclasses import dataclass, replace


PLATFORM_AUTO_API_REVIEW = "PLATFORM_AUTO_API_REVIEW"
PLATFORM_USER_INITIATED_API_REVIEW = "PLATFORM_USER_INITIATED_API_REVIEW"
USER_PROVIDED_EXTERNAL_CONTENT = "USER_PROVIDED_EXTERNAL_CONTENT"
USER_ATTESTED_EXTERNAL_LLM_REVIEW = "USER_ATTESTED_EXTERNAL_LLM_REVIEW"

AUTOMATIC_API = "AUTOMATIC_API"
USER_INITIATED_API = "USER_INITIATED_API"
EXTERNAL_EVIDENCE_RELAY = "EXTERNAL_EVIDENCE_RELAY"

PLATFORM_REVIEW_CLASSES = frozenset({
    PLATFORM_AUTO_API_REVIEW,
    PLATFORM_USER_INITIATED_API_REVIEW,
})


@dataclass(frozen=True)
class ReviewExecutionClassification:
    review_class: str
    transport: str
    initiated_by: str
    provider_api_authenticated: bool
    can_satisfy_platform_review: bool
    reported_provider: str | None = None
    reported_model: str | None = None
    provenance_basis: str = "PLATFORM"

    def validate(self) -> None:
        allowed = PLATFORM_REVIEW_CLASSES | {
            USER_PROVIDED_EXTERNAL_CONTENT,
            USER_ATTESTED_EXTERNAL_LLM_REVIEW,
        }
        if self.review_class not in allowed:
            raise ValueError("invalid review execution class")
        if self.review_class in PLATFORM_REVIEW_CLASSES:
            if self.transport not in {AUTOMATIC_API, USER_INITIATED_API}:
                raise ValueError("platform review requires trusted API transport")
            if not self.provider_api_authenticated or not self.can_satisfy_platform_review:
                raise ValueError("platform API review must use authenticated provider execution")
            if self.provenance_basis != "PLATFORM_API_EXECUTION":
                raise ValueError("platform review provenance must come from API execution")
        else:
            if self.transport != EXTERNAL_EVIDENCE_RELAY:
                raise ValueError("external content must use external-evidence relay classification")
            if self.provider_api_authenticated or self.can_satisfy_platform_review:
                raise ValueError("external copy/paste cannot satisfy platform review authority")
            if self.review_class == USER_PROVIDED_EXTERNAL_CONTENT:
                if self.reported_provider is not None or self.reported_model is not None:
                    raise ValueError("unattested external content cannot infer provider/model from content")
                if self.provenance_basis != "UNKNOWN_EXTERNAL_ORIGIN":
                    raise ValueError("unattested external content provenance must remain unknown")
            if self.review_class == USER_ATTESTED_EXTERNAL_LLM_REVIEW:
                if not self.reported_provider:
                    raise ValueError("user-attested external LLM review requires reported provider")
                if self.provenance_basis != "USER_ATTESTATION":
                    raise ValueError("external LLM review provenance must remain user-attested")


def classify_platform_api_review(*, automatic: bool) -> ReviewExecutionClassification:
    result = ReviewExecutionClassification(
        review_class=PLATFORM_AUTO_API_REVIEW if automatic else PLATFORM_USER_INITIATED_API_REVIEW,
        transport=AUTOMATIC_API if automatic else USER_INITIATED_API,
        initiated_by="PLATFORM" if automatic else "USER_PLATFORM_CONTROL",
        provider_api_authenticated=True,
        can_satisfy_platform_review=True,
        provenance_basis="PLATFORM_API_EXECUTION",
    )
    result.validate()
    return result


def ingest_user_provided_external_content() -> ReviewExecutionClassification:
    """Classify copy/pasted content before the user identifies its source.

    Content fields such as `reviewer.provider=deepseek` are intentionally not
    arguments here. Pasted content cannot establish its own provenance.
    """
    result = ReviewExecutionClassification(
        review_class=USER_PROVIDED_EXTERNAL_CONTENT,
        transport=EXTERNAL_EVIDENCE_RELAY,
        initiated_by="USER_EXTERNAL_RELAY",
        provider_api_authenticated=False,
        can_satisfy_platform_review=False,
        provenance_basis="UNKNOWN_EXTERNAL_ORIGIN",
    )
    result.validate()
    return result


def attest_external_llm_review(
    classification: ReviewExecutionClassification,
    *,
    reported_provider: str,
    reported_model: str | None = None,
) -> ReviewExecutionClassification:
    """Upgrade only provenance classification after explicit user attestation.

    User attestation may identify the reported source, but it never becomes
    provider-API authentication and never satisfies a platform review gate.
    """
    if classification.review_class != USER_PROVIDED_EXTERNAL_CONTENT:
        raise ValueError("only unclassified user-provided external content may be attested")
    provider = reported_provider.strip()
    model = reported_model.strip() if isinstance(reported_model, str) else reported_model
    if not provider:
        raise ValueError("reported_provider required")
    result = replace(
        classification,
        review_class=USER_ATTESTED_EXTERNAL_LLM_REVIEW,
        reported_provider=provider,
        reported_model=model or None,
        provenance_basis="USER_ATTESTATION",
    )
    result.validate()
    return result
