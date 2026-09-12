# Review Packet + API Call Gate Falsification — V1

Status: **PREREGISTERED — NOT EXECUTED IN PLATFORM CI**

Authority effect: **NONE_EVIDENCE_ONLY**

## RPG-01 — Requested clause missing but summary mention exists
Expected: `PACKET_INVALID`.

## RPG-02 — Requested falsification range partially embedded
Expected: `PACKET_INVALID`.

## RPG-03 — Embedded artifact bytes differ from declared Git blob
Expected: `PACKET_INVALID`.

## RPG-04 — Prior reviewer disposition leaks into clean packet
Expected: `PACKET_INVALID`.

## RPG-05 — Correct complete clean packet
Expected: `PACKET_READY`.

## APIG-01 — Testing/falsification REVIEW_API attempt
Expected: `API_CALL_BLOCKED` under the active manual-review-only phase policy.

## APIG-02 — Provider silently substitutes another model/provider
Expected: returned result rejected with provider/model identity mismatch.

## APIG-03 — First fallback target already produced qualified success
Expected: later fallback blocked with `API_FALLBACK_AFTER_QUALIFIED_SUCCESS`.

## APIG-04 — Provider returns HTTP success with no assistant content
Expected: `API_RESPONSE_CONTENT_MISSING`; result not qualified.

## APIG-05 — Review response bound to another candidate
Expected: `API_REVIEW_CANDIDATE_BINDING_MISMATCH`; result not qualified.

## APIG-06 — Mutating API retry after outcome unknown without reconciliation
Expected: dispatch blocked by `API_OUTCOME_UNKNOWN_REQUIRES_RECONCILIATION`.

## APIG-07 — Literal API key/token supplied in governed metadata
Expected: preflight blocked by secret-literal detection.

## APIG-08 — Mutating call without intent idempotency key
Expected: `API_IDEMPOTENCY_KEY_REQUIRED`.

## APIG-09 — Valid governed review API call in an allowed phase
Expected: preflight may return `API_CALL_READY`; a matching authenticated receipt may return `API_RESULT_QUALIFIED`.

## APIG-10 — Policy digest rebound or changed
Expected: `API_POLICY_HASH_BINDING_MISMATCH` or policy hash failure.

## Execution rule

The included unit tests exercise a bounded subset of these cases locally. That local test evidence does not establish production adapter integration or platform qualification.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
