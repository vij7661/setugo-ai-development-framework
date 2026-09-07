# Review Engine Completion API Review — Preregistration

Status: PREREGISTERED BEFORE COMPLETION-REVIEW MECHANISM

## Objective

Falsify the Review Engine completion candidate with an independent provider API review whose reviewer provenance comes from platform execution, not reviewer self-description or copy/paste.

## Review class

- mode: `AUTO_MODE`
- review class: `PLATFORM_AUTO_API_REVIEW`
- transport: `AUTOMATIC_API`
- intended provider: `gemini`
- provider identity basis: GitHub Actions execution of the platform-owned Gemini API call using repository secret `GEMINI_API_KEY`
- failure posture: fail closed; provider failure, malformed output, missing dimension, candidate mismatch, or missing evidence cannot produce an accepted review

## Exact-candidate rule

The review request MUST name one exact 40-character candidate commit SHA. The workflow may be triggered by a later metadata-only commit, but it MUST check out and build the review corpus from the named candidate SHA. Review evidence MUST retain both trigger SHA and reviewed candidate SHA.

## Mandatory dimensions

Every review must explicitly cover all dimensions below:

1. `provider_configuration_qualification_binding`
2. `reviewer_runtime_independence`
3. `retrieval_admission_and_proposer_influence`
4. `review_execution_provenance_classification`
5. `external_content_non_authority`
6. `single_file_and_review_export_integrity`
7. `authority_bypass_lifecycle_and_escape_hatches`
8. `app_composition_and_standard_path_wiring`
9. `truth_claim_coverage_and_evidence_correspondence`
10. `r3_adjudication_and_scoped_correction_closure`
11. `remaining_false_green_or_authority_bypass_search`

Allowed coverage statuses:

- `TESTED_SUPPORTED`
- `TESTED_DEFECT_FOUND`
- `CONTRADICTED`
- `NOT_TESTED`
- `UNAVAILABLE`
- `INSUFFICIENT`

`PASS` requires every mandatory dimension to be `TESTED_SUPPORTED` and no MEDIUM/HIGH/CRITICAL finding. `CHANGES_REQUIRED` is required when any mandatory dimension is defective/contradicted or any MEDIUM/HIGH/CRITICAL finding exists. `INSUFFICIENT_EVIDENCE` is required when any mandatory dimension is NOT_TESTED/UNAVAILABLE/INSUFFICIENT.

## Evidence corpus

The platform review corpus MUST be derived deterministically from the exact candidate and contain:

- exact candidate SHA and base SHA;
- changed-file list and unified diff from the PR base to candidate;
- full UTF-8 contents plus SHA-256 for authority-sensitive `review_engine` Python/tests/status/bypass files changed by the completion branch;
- PR purpose/review posture;
- existing bypass records RE-BYP-001/002/003;
- no secrets.

The corpus hash MUST be computed before provider dispatch and retained in the execution envelope. The provider response MUST be retained raw and parsed separately.

## Required output

Reviewer output must be strict JSON with:

- `review_request_id`
- `reviewed_artifact_commit`
- `reviewer` content claim
- `disposition`
- `findings`
- `evidence_assessment`
- `independence_attestation`
- `review_coverage` for all mandatory dimensions

Reviewer self-declared provider/model fields are content claims only. The authenticated platform review identity comes from the execution envelope created by the workflow.

## Acceptance boundary

Green CI and a provider `PASS` are evidence, not self-promotion authority. This review can close RE-BYP-001/002/003 only after deterministic ingestion confirms exact candidate binding, authenticated API execution, semantic completeness, and no blocking findings. Any material production-code change after the reviewed candidate requires a new review.
