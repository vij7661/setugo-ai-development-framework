# Integrated Governed MVP — Slice 10 External Side-Effect Gateway Contract

Status: **PRE-IMPLEMENTATION FROZEN BOUNDARY**

Current authoritative `main` parent: `ab3454a84a5afbfeeb9a15bcf87f0be8d4e8a137`.
Accepted prior boundary: Slice 9 external credential lease gate, exact accepted candidate `16ae65c9d4939efc05aeff76f0ae2e708428b3b1`.

## 1. Goal

Falsify whether an exact already-governed remote execution binding plus a valid current credential lease can invoke one bounded external side-effect adapter without allowing a model, worker, reviewer, retry path, stale authority record, stale lease, transport ambiguity, provider success label, or local crash to widen the target/action/payload, duplicate the external effect, launder ambiguous outcomes into success, or convert credential possession/provider response into completion authority.

Slice 10 introduces a deterministic **safe reference external side-effect gateway** with durable idempotency and ambiguous-outcome recovery. It does not call a real production GitHub/cloud/deployment/payment endpoint and does not perform a production consequence.

## 2. Included

- exact consumption of accepted Slice8 remote-execution lineage and accepted Slice9 credential lease evidence;
- platform-owned provider/endpoint/action/resource binding;
- deterministic external idempotency key derived from the frozen execution identity;
- one external idempotency key → one exact provider/endpoint/action/resource/payload binding;
- pre-call revalidation of terminal authority and credential lease validity;
- safe loopback/reference external endpoint that persists provider-side effect identity separately from the caller;
- durable caller-side intent, attempt, reconciliation, and completion records;
- explicit handling of timeout/connection loss/unknown response after the provider may already have committed the effect;
- reconciliation/query before retry when outcome is ambiguous;
- crash recovery when provider commit succeeds before caller completion persistence;
- rejection of provider/endpoint/action/resource/payload substitution;
- provider HTTP success or model/reviewer/CI claim retained only as evidence, never completion authority;
- secret-value non-persistence/non-disclosure;
- response/effect evidence bound to exact request, external effect identity, result digest, and current lineage;
- preserved accepted Slice1→Slice9 regression lineage.

## 3. Deferred / nonclaims

- real GitHub merge/release/deploy mutation;
- real cloud infrastructure mutation;
- real payment/message/production API;
- production secret manager/IAM correctness;
- external provider cryptographic identity attestation;
- TLS/PKI/DNS/proxy/service-mesh correctness;
- third-party provider bugs, eventual-consistency guarantees, or global exactly-once semantics;
- multi-region consensus;
- malicious host/root compromise resistance;
- autonomous release/deploy/merge authority;
- proof that a provider HTTP 2xx means the intended business effect occurred unless independently reconciled under this contract.

## 4. Frozen input contract

### External effect request

- `side_effect_request_id`
- `project_id`
- `task_id`
- `effect_id`
- `terminal_execution_id`
- `remote_idempotency_key`
- `credential_lease_id`
- `credential_profile_id`
- `provider_id`
- `endpoint_id`
- `action`
- `resource_id`
- `artifact_sha`
- `state_version`
- `payload_digest`
- `authority_snapshot_hash`
- `lease_evidence_hash`
- `now_epoch`

No raw secret/API key/token/password field is permitted.

### External provider/reference result

- `provider_id`
- `endpoint_id`
- `external_idempotency_key`
- `external_effect_id`
- `provider_status`
- `provider_result_digest`
- `provider_committed`
- `observed_at_epoch`

The result is evidence only. It is not terminal completion authority.

## 5. Frozen invariants

**S10-I01 Exact accepted upstream lineage** — no external attempt is permitted without valid exact Slice8 remote execution lineage and valid exact Slice9 credential lease evidence.

**S10-I02 Platform-owned target binding** — provider, endpoint, action, resource, and credential profile are platform-controlled; model/worker/reviewer input cannot replace them.

**S10-I03 Use-time authority and lease validity** — current terminal authority and credential lease/profile validity must be rechecked immediately before each external invocation/reconciliation step.

**S10-I04 Deterministic external idempotency** — the external idempotency key is platform-derived from the exact frozen effect binding and reused for retries of the same intent; transport attempts never mint new effect intent.

**S10-I05 One external key, one binding** — reuse of an external idempotency key with changed provider/endpoint/action/resource/artifact/state/payload/lease binding is denied.

**S10-I06 Ambiguous outcome is not failure or success** — timeout, connection loss, process death, missing body, malformed body, or unknown transport state after dispatch must enter `OUTCOME_UNKNOWN_RECONCILE_REQUIRED`; it must not be retried as a fresh effect or marked successful without reconciliation.

**S10-I07 Reconcile before retry** — after an ambiguous attempt, the gateway must query/recover provider-side state using the same external idempotency key before another mutating call.

**S10-I08 Crash-after-provider-commit recovery** — if the provider committed the effect before caller persistence/crash, restart must recover the same external effect identity and must not duplicate the effect.

**S10-I09 Provider success is not completion authority** — HTTP 2xx, provider `SUCCESS`, model/reviewer agreement, CI green, or credential possession cannot mint terminal completion/release/deploy/merge authority.

**S10-I10 Provider response integrity** — external effect evidence must bind exact provider/endpoint/idempotency/effect/result digest and must reject tampered or mismatched responses.

**S10-I11 Scope containment** — payload/resource/action may not exceed the intersection of terminal authority, remote execution binding, and credential lease/profile policy.

**S10-I12 Revocation dominates retry** — if authority/lease/profile is revoked/expired after an ambiguous attempt, reconciliation may inspect existing provider state but no new mutating retry may occur under stale authority.

**S10-I13 Secret-value non-persistence/disclosure** — no raw secret may appear in request/evidence/ledger/telemetry/diagnostics/provider error records.

**S10-I14 Durable intent before dispatch** — the exact effect intent/binding must be persisted before any mutating provider dispatch.

**S10-I15 Reference endpoint only** — a passing local/reference external target proves bounded transport/idempotency/reconciliation semantics only, not production external-provider safety.

## 6. Frozen result states

- `DENY_UPSTREAM_LINEAGE`
- `DENY_AUTHORITY_OR_LEASE`
- `DENY_TARGET_SUBSTITUTION`
- `DENY_SCOPE_WIDENING`
- `DENY_IDEMPOTENCY_REBIND`
- `DENY_RESPONSE_INTEGRITY`
- `OUTCOME_UNKNOWN_RECONCILE_REQUIRED`
- `RECONCILED_EXISTING_EFFECT`
- `REFERENCE_EFFECT_APPLIED`
- `REFERENCE_EFFECT_REPLAYED`
- `REFERENCE_EFFECT_FAILED`

Only `RECONCILED_EXISTING_EFFECT`, `REFERENCE_EFFECT_APPLIED`, and `REFERENCE_EFFECT_REPLAYED` may carry positive external-effect evidence. None constitutes merge/deploy/release/completion authority.

## 7. Frozen acceptance cases

- `S10-01` exact accepted Slice8+Slice9 lineage applies one bounded reference external effect.
- `S10-02` exact replay reuses the same external idempotency key/effect identity without duplicate provider mutation.
- `S10-03` missing/malformed/non-success Slice8 lineage denies before provider access.
- `S10-04` missing/malformed/non-success Slice9 lease evidence denies before provider access.
- `S10-05` provider substitution denies.
- `S10-06` endpoint substitution denies.
- `S10-07` action/resource/artifact/state/payload widening denies.
- `S10-08` caller-supplied replacement external idempotency key denies.
- `S10-09` same external key with changed binding denies.
- `S10-10` raw secret input denies before dispatch.
- `S10-11` expired/revoked authority denies dispatch.
- `S10-12` expired/revoked/stale credential lease/profile denies dispatch.
- `S10-13` timeout before provider commit yields safe failure/no provider effect.
- `S10-14` timeout after provider commit yields `OUTCOME_UNKNOWN_RECONCILE_REQUIRED`, not fresh retry/success.
- `S10-15` reconciliation after ambiguous provider commit recovers the same external effect identity.
- `S10-16` crash after provider commit but before caller completion persistence recovers after restart without duplicate effect.
- `S10-17` repeated recovery/replay after committed effect never increments provider effect count.
- `S10-18` ambiguous attempt followed by authority/lease revocation may reconcile existing state but cannot issue a new mutating retry.
- `S10-19` provider HTTP 200 with mismatched effect/idempotency/result digest is rejected.
- `S10-20` provider self-reported success without provider-side committed evidence cannot become positive completion evidence.
- `S10-21` provider 5xx before commit remains failure and does not mint completion evidence.
- `S10-22` governed evidence/telemetry/diagnostics contain no raw secret value.
- `S10-23` mutated provider/endpoint/action/resource/artifact/state/payload/lease/idempotency fields change or invalidate evidence hash.
- `S10-24` provider/model/reviewer/CI success claims cannot become terminal authority.
- `S10-25` synthetic future provider/endpoint identifiers work without provider-specific evidence/dashboard branching.
- `S10-26` no result claims a real production GitHub/cloud/deploy/payment action occurred.

## 8. Construction and freeze rules

1. Commit this contract before acceptance tests or mechanism implementation.
2. Add `S10-01..S10-26` falsification tests before mechanism implementation wherever scientifically feasible.
3. Preserve the first RED run; do not weaken tests to obtain green.
4. Include explicit provider-side effect counters/state so duplicate mutations are observable.
5. Include crash points before dispatch, after dispatch-before-response, after provider commit-before-local-completion, and after local completion.
6. Keep the reference endpoint deterministic and network-local/safe; no production credential or production API is permitted.
7. Provider/endpoint behavior must be registry/config driven; include a synthetic future provider/endpoint case.
8. Preserve accepted Slice1→Slice9 regressions.
9. Freeze an exact candidate only after all Slice10 cases and prior regressions are green.
10. Fresh independent review of the exact candidate is mandatory before promotion.
11. Deterministic review-of-review and exact closure-head validation are mandatory before merge.
12. Green CI, provider success, credential possession, model/reviewer PASS, or reconciliation success is evidence only and never merge/deploy/release authority by itself.

## 9. Claim boundary

A bounded pass supports only that the tested safe reference external side-effect gateway enforced exact target/lineage binding, durable idempotency, ambiguous-outcome reconciliation, crash recovery, replay non-duplication, current authority/lease checks, response integrity, and secret non-disclosure under the frozen cases. It does not establish production external-provider safety, production IAM/secret-manager correctness, global exactly-once semantics, real deployment/release safety, or autonomous terminal authority.
