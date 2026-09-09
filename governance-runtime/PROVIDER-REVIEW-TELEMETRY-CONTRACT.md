# Provider-Neutral Review Telemetry Contract

Status: **PRE-IMPLEMENTATION FROZEN BOUNDARY**

Authoritative parent governance checkpoint: `cfc8a9c99025d3d8e0abeff87345994dcbc7384d` (`LIVE-CONV-2026-09-09-046`).
Accepted product frontier: `main` = `3a19eff0a735f702bac2807040f361b2dc7a37b6` (accepted Slice 8).

## 1. Goal

Falsify whether every governed reviewer/API attempt can emit one normalized, secret-safe telemetry record and appear automatically in provider/model/credential summaries and dashboard data without provider-specific display logic.

This change is observability only. It must not change review semantics, reviewer independence, provider qualification, retry policy, validation, adjudication, or authority.

## 2. Provider-neutral rule

Telemetry consumers MUST NOT contain branches or enumerations such as `if provider == "openrouter"`, hard-coded Gemini/Groq/OpenRouter rows, or a fixed known-provider list.

Actual provider invocation adapters may still require explicit registration/configuration. Once any adapter emits a conforming telemetry event, aggregation and dashboard rendering must include it without code changes.

A synthetic provider named `future-provider-x` is the mandatory falsification vector for this rule.

## 3. Normalized attempt event

Each provider attempt must emit a JSON object with at least:

- `schema_version`
- `event_type = REVIEW_PROVIDER_ATTEMPT`
- `review_request_id`
- `reviewed_candidate_commit`
- `reviewer_slot`
- `gateway_provider`
- `model`
- `credential_profile` — identity such as `primary` or `r3`; never a secret/key
- `requested_serving_provider` — nullable when not applicable
- `returned_serving_provider` — nullable when unavailable
- `attempt_index`
- `request_started_at`
- `provider_call_started_at`
- `first_response_at` — nullable on failures before any response
- `provider_call_completed_at`
- `provider_latency_ms`
- `attempt_outcome` — `SUCCESS` or `FAILURE`
- `retryable`
- `http_status` — nullable
- `error_classification` — nullable on success
- `error_detail` — bounded/sanitized; must not contain secrets
- `semantic_disposition` — nullable until available
- `validation_valid` — nullable until available
- `authority_effect`

Wall-clock timestamps must be UTC ISO-8601. Duration must be calculated from a monotonic clock where the runtime can do so; durations may not be derived only by subtracting wall-clock strings.

## 4. Secret safety

Telemetry must never persist or render API key values, Authorization headers, bearer tokens, repository secret contents, or raw environment-secret values. `credential_profile` identifies the configured credential slot only.

## 5. Attempt preservation

Retries are separate events. A later success may not overwrite an earlier 429/503/transport failure. For example, Slice 8 Review 001 must be representable as attempt 1 = transient 429 and attempt 2 = success.

## 6. Review-level summary

Aggregation must deterministically produce review-level fields including:

- request/candidate identity;
- provider/model/credential profile;
- attempt count;
- retry count;
- first attempt start;
- first successful response time, if any;
- final completion time;
- total elapsed latency;
- final success/failure;
- final error classification if unsuccessful;
- semantic disposition;
- validation result;
- authority effect.

## 7. Dynamic provider summary

Aggregation groups by values present in telemetry records. It must support arbitrary providers/models/credential profiles discovered at runtime.

The provider summary must expose at least:

- provider identity;
- models observed;
- credential profiles observed;
- review count;
- attempt count;
- success count;
- failure count;
- retry count;
- average successful provider latency when calculable;
- latest event time;
- latest outcome/error classification.

No provider may be omitted because it is unknown to the dashboard code.

## 8. Dashboard data contract

Dashboard publication must include a machine-readable `provider-review-telemetry.json` (or an explicitly versioned successor) containing normalized review records and dynamic provider summaries.

The UI must iterate the supplied records/groups; it may not contain provider-specific rows. A record for `future-provider-x` must render through the same generic path as any current provider.

## 9. Authority isolation

Telemetry is evidence about execution timing and transport outcome only. It cannot:

- convert a failed review to PASS;
- replace semantic validation;
- satisfy independent review by itself;
- authorize merge/release/deploy/completion;
- prove remote model identity cryptographically;
- widen a provider or model claim beyond authenticated/reported evidence.

Every telemetry artifact must use `authority_effect = NONE_PENDING_DETERMINISTIC_INGESTION` unless a separate governed authority mechanism explicitly defines otherwise.

## 10. Frozen acceptance cases

- `TEL-01` a valid arbitrary provider event round-trips through normalized validation.
- `TEL-02` `future-provider-x` appears automatically in provider aggregation with no provider registry/display change.
- `TEL-03` two different unknown providers both appear; neither is collapsed into `other`.
- `TEL-04` provider/model/credential profile are data fields, not dashboard hard-coded enums.
- `TEL-05` a first-attempt 429 followed by success preserves both attempts and reports one retry.
- `TEL-06` a 503-only sequence remains failed and preserves every attempt.
- `TEL-07` a failure before response has `first_response_at = null` and nonnegative latency.
- `TEL-08` successful attempt records first-response and completion timestamps with nonnegative provider latency.
- `TEL-09` attempt index must be positive and unique within one review execution sequence.
- `TEL-10` API key/bearer-like material in credential or error fields is rejected or sanitized before persistence.
- `TEL-11` aggregation never stores a raw Authorization header.
- `TEL-12` review summary preserves semantic disposition, validation result, and authority effect without deriving them from latency/outcome.
- `TEL-13` mixed R1/R2/R3 records aggregate without slot-specific dashboard code.
- `TEL-14` multiple credential profiles remain distinguishable without revealing secret values.
- `TEL-15` requested and returned serving provider are separately retained where available.
- `TEL-16` provider route mismatch/failure telemetry cannot be interpreted as successful semantic review.
- `TEL-17` prior failed attempt remains visible after later successful retry.
- `TEL-18` deterministic aggregation output is stable for identical input records regardless of input ordering.
- `TEL-19` dashboard data builder includes arbitrary providers from normalized records automatically.
- `TEL-20` generated dashboard markup/data contains `future-provider-x` solely because it exists in input records, not because its name appears in renderer source/config.
- `TEL-21` telemetry generation does not change existing review semantic validation/disposition.
- `TEL-22` telemetry failure must not falsely make the review authoritative; observability failure is surfaced separately.
- `TEL-23` credential profile identity is displayed; secret values are absent from artifacts and rendered output.
- `TEL-24` current OpenRouter/DeepInfra route can be represented without any OpenRouter-specific aggregator/dashboard branch.

## 11. Construction order

1. Freeze this contract before implementation.
2. Add TEL-01..TEL-24, including `future-provider-x`, before telemetry mechanism code.
3. Preserve the red pre-mechanism CI run.
4. Implement normalized event validation/aggregation and generic dashboard data generation.
5. Instrument reviewer v7 generically across provider attempts; provider-specific invocation may remain in adapters, but timing/event emission may not be provider-specific.
6. Wire dashboard publication to collect telemetry artifacts dynamically.
7. Keep existing review-governance tests green.
8. Fresh independent review is mandatory before promotion of this observability boundary.

## 12. Claim boundary

A pass proves only that the tested review execution path emits, preserves, aggregates, and renders provider-neutral telemetry under the tested cases. It does not prove provider uptime, model quality, semantic correctness, billing correctness, remote model identity, or production authority.
