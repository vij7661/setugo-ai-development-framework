# Governed API Call Gate — V1

Status: **PROPOSED — IMPLEMENTED RUNTIME VALIDATOR — REVIEW REQUIRED**

Authority effect: **NONE_EVIDENCE_ONLY**

## ACG-01 — Scope

Every external API call that can create evidence, consume a paid/provider attempt, mutate state, trigger an external effect, or contribute to an authority-bearing workflow must pass a governed preflight before dispatch and a governed receipt check after dispatch.

A successful HTTP status alone is never sufficient evidence that the intended governed call occurred correctly.

## ACG-02 — Exact call envelope

Before dispatch, the caller binds an immutable logical call envelope containing at minimum:

- `call_id` and stable `intent_id`;
- attempt number;
- platform phase;
- exact governance policy ID and digest;
- transport;
- call class;
- authority effect;
- exact provider and model/service identity;
- exact HTTPS endpoint origin;
- credential reference, never credential value;
- request-payload SHA-256;
- context-bundle SHA-256;
- retry policy;
- fallback policy;
- expected response contract;
- exact candidate/review-request binding when the call is a review.

The envelope is canonically hashed. Dispatch of a changed envelope requires a new envelope hash.

## ACG-03 — Phase policy is external to the call

The call may not self-grant permission by declaring its own phase rules.

A separately supplied, hash-bound API governance policy defines allowed call classes/transports per phase.

For the current platform policy, `TESTING_FALSIFICATION` is manual-review-only for review activity: `REVIEW_API` is prohibited there. Read-only API use may be separately permitted by policy, but cannot be represented as a manual reviewer.

Changing the phase policy is a governance change, not an ordinary request parameter change.

## ACG-04 — Provider/model identity and no silent substitution

Requested provider/model are exact governed inputs.

The returned result counts only when a trusted provider adapter attests:

`PROVIDER_ADAPTER_AUTHENTICATED`

and the actual provider/model exactly match the envelope.

Provider/model strings supplied only by model content or an untrusted proxy are not identity proof.

Fallback to another provider/model is allowed only when that exact target appears in the predeclared fallback policy. Silent substitution is prohibited.

## ACG-05 — Stop after first qualified success

For one logical `intent_id`, once a qualified successful result exists, no later fallback/retry call may be dispatched for that intent unless a separate governed policy explicitly requires multiple independent results.

The default fallback policy is:

`stop_on_first_qualified_success = true`

This prevents unnecessary duplicate provider calls and cost.

## ACG-06 — Retry and outcome-unknown rules

Retries reuse the same logical `intent_id`.

The maximum attempt count and retryable HTTP statuses are explicit.

A request that may have been dispatched but whose result is uncertain is `OUTCOME_UNKNOWN`, not `FAILED_BEFORE_DISPATCH`.

Blind retry after outcome unknown is prohibited.

For mutating/external-effect calls, a later attempt requires reconciliation establishing `PROVIDER_CONFIRMED_NOT_APPLIED` or an equal-or-stronger governed resolution.

For non-mutating review/research/read-only calls, a policy may permit a duplicate attempt only when the previous result is not used and duplicate risk is explicitly bounded.

## ACG-07 — Idempotency

`MUTATING_API` and `EXTERNAL_EFFECT_API` calls require an intent-level idempotency key.

The same user/system intent reuses the same idempotency identity across transport retries.

Where a provider lacks native idempotency support, the authoritative sequencer must enforce equivalent deduplication before an external material effect can be considered qualified.

## ACG-08 — Secrets and data egress

Credentials are referenced by governed secret identifiers and are never embedded in prompts, packet context, request metadata, logs, receipts, or review artifacts.

The preflight rejects literal secret-like fields in governed metadata and requires `secrets_in_payload = false`.

Receipts must attest secret redaction before they can qualify as governed evidence.

Additional data-classification/egress controls may be stricter than this gate.

## ACG-09 — Response contract

A successful result must satisfy the exact expected response contract.

For LLM/reviewer calls, this includes presence of assistant content and all required structured fields.

A 2xx response with missing assistant content is `API_RESPONSE_CONTENT_MISSING`, not success.

Malformed/missing required response fields are rejected even if the provider returned HTTP success.

## ACG-10 — Review-call binding

`REVIEW_API` results bind the exact review request ID and exact candidate commit.

A review response for a different candidate, stale candidate, or different request cannot be promoted as evidence for the requested candidate.

Review API output is evidence. It may not self-declare `AUTHORITY_AFFECTING`.

## ACG-11 — Trusted receipt

The provider adapter emits a receipt binding:

- call/intent/attempt IDs;
- exact request-envelope hash;
- authenticated actual provider/model;
- dispatch state;
- HTTP status;
- provider request ID or adapter dispatch correlation ID;
- response-payload SHA-256;
- schema/content validation results;
- candidate/review-request binding where applicable;
- latency;
- secret-redaction state.

A receipt missing these bindings cannot qualify the result.

## ACG-12 — Failure semantics

At minimum the gate distinguishes:

- `API_CALL_READY`
- `API_CALL_BLOCKED`
- `API_RESULT_QUALIFIED`
- `API_RESULT_REJECTED`
- `OUTCOME_UNKNOWN`

Failure to prove correct dispatch/identity/binding is not converted into success by retry count, provider consensus, reviewer prose, or user assumption.

## ACG-13 — Telemetry and history

Attempt history is append-only for a logical intent.

The history preserves provider/model, attempt number, response state, failure reason, latency, and whether the gate accepted a qualified result.

Fallback/retry eligibility is evaluated against this history before each new dispatch.

## ACG-14 — Runtime implementation

The reference implementation is:

- `governance-runtime/api_call_gate.py`
- `governance-runtime/api-call-policy-v1.json`
- `governance-runtime/test_api_call_gate.py`

The current `platform_candidate_review_v2.py` path is migrated to call this gate before dispatch and validate the adapter receipt before accepting results.

Other adapters must be migrated before this standard can be described as runtime-enforced for them.

## ACG-15 — Mandatory attacks

Tests/reviews must attempt at least:

- wrong provider/model behind nominally successful response;
- silent fallback;
- second provider call after first qualified success;
- new `intent_id` generated on retry;
- missing idempotency on mutating call;
- retry after unknown mutating outcome without reconciliation;
- wrong candidate/review-request response;
- 2xx with missing assistant content;
- response-schema omission;
- request/context hash mismatch;
- secret value in metadata/log/receipt;
- API call in a phase where policy prohibits that class;
- forged provider identity using response content only;
- stale or rebound governance policy digest.

## ACG-16 — Nonclaims

This standard and validator do not themselves prove provider availability, provider honesty, production secret-store configuration, network security, or that every existing adapter is already migrated.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
