# GOV-REQUEST-INTEGRITY-001 — Platform Review Request Integrity Gate

Status: **PREREGISTERED BEFORE REPAIR**

## Observed defect

During `REV-MVP-SLICE4-INTEGRATION-001`, the platform-authenticated review workflow invoked Gemini and received semantic `PASS` even though the ReviewRequest carried an invalid canonical `request_hash`. Independent downstream adjudication rejected that review as non-promotable, but the provider invocation itself occurred before request integrity was enforced.

Preserved evidence:
- invalid review request: `governance-runtime/review-requests/REV-MVP-SLICE4-INTEGRATION-001.json`;
- invalid-review adjudication: `governance-runtime/review-evidence/REV-MVP-SLICE4-INTEGRATION-001-invalid-request.json`;
- workflow run `34167633377`, job `101881744220`, artifact `10034669354`;
- effective authority effect: `NONE`.

## Root cause hypothesis

`governance-runtime/platform_candidate_review.py` consumes the request and calls the provider without first applying `review_protocol.verify_review_request()`. The repository already has a deterministic request-integrity verifier, but the authenticated execution path is not wired to it.

## Frozen repair contract

The repair MUST satisfy all of the following without weakening any existing review semantic validation:

1. A platform candidate review MUST deterministically verify the complete ReviewRequest before building the provider corpus or invoking any provider API.
2. Invalid/malformed request hash, unsupported schema, invalid artifact SHA, missing reviewer/proposer binding, invalid state, or invalid semantic dimension contract MUST fail before provider invocation.
3. Provider invocation count for an invalid request MUST be zero.
4. A valid schema-v4 request produced by `build_review_request()` MUST remain accepted and reach the existing corpus/provider path.
5. The existing semantic review validator, API-authenticated execution envelope, exact candidate binding, provider/model checks, and fail-closed negative-disposition logic MUST remain unchanged except where strictly required to insert request verification.
6. No invalid ReviewRequest may produce promotable review evidence merely because provider/model content says `PASS`.
7. Historical `REV-MVP-SLICE4-INTEGRATION-001` remains preserved as an exposed defect and MUST NOT be rewritten as valid.

## Frozen regression cases

- `GRI-01`: invalid canonical `request_hash` is rejected before `build_corpus` and before `invoke`.
- `GRI-02`: malformed/missing `request_hash` is rejected before provider invocation.
- `GRI-03`: valid schema-v4 request passes request-integrity verification.
- `GRI-04`: valid request still reaches the normal provider-review path when downstream functions are stubbed.
- `GRI-05`: rejection error reports the deterministic `verify_review_request()` reason and does not synthesize provider evidence.

## Scientific sequence

1. Commit this preregistration first.
2. Add the frozen regression harness without changing `platform_candidate_review.py`.
3. Preserve the expected failing exposure showing the current platform path does not enforce the integrity gate.
4. Apply only the narrow mechanism repair.
5. Require all frozen regression cases plus the existing live-governance suite to pass.
6. Preserve the original invalid-review history and the pre-repair failing regression evidence.

## Claim boundary

A pass proves only that this repository's authenticated platform candidate-review entrypoint checks deterministic ReviewRequest integrity before provider invocation under the tested conditions. It does not cryptographically prove remote model identity, provider implementation identity, or external service behavior.
