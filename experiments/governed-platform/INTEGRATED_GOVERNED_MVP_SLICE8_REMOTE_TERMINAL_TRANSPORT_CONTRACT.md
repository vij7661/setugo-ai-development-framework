# Integrated Governed MVP — Slice 8 Remote Terminal Transport Contract

Status: **PRE-IMPLEMENTATION FROZEN BOUNDARY**

Parent authoritative integration commit: `8d95e59c453e8499cf8079acc8e54818eb131fdc` (accepted Slice 7 terminal executor gateway).

## 1. Goal

Falsify whether an accepted Slice 7 terminal execution can cross a network-style remote transport boundary without duplicate or widened side effects when acknowledgements are lost, responses are delayed, requests are retried, the remote endpoint commits before the caller observes success, or the remote endpoint attempts to alter the frozen terminal binding.

This slice adds a deterministic local HTTP reference remote service and client transport so network ambiguity and remote idempotency semantics can be falsified without external production credentials. It does **not** perform a real GitHub merge, cloud deployment, production release, or production completion mutation.

## 2. Included

- exact consumption of a valid Slice 7 terminal execution binding;
- remote request envelope with exact project/task/effect/action/artifact/state-version/terminal-execution-id binding;
- platform-generated immutable remote idempotency key derived from terminal execution identity + exact binding hash;
- deterministic local HTTP reference remote service with durable request/effect ledger;
- remote service one-idempotency-key → one exact binding enforcement;
- caller retry after connection loss / timeout / lost acknowledgement;
- remote commit-before-response ambiguity;
- remote response replay/recovery by idempotency key;
- duplicate concurrent delivery convergence;
- remote endpoint binding-widening rejection;
- remote structured failure cannot become completion;
- unknown/ambiguous remote outcome remains non-complete until reconciled;
- deterministic remote completion evidence binding request, remote receipt, idempotency key, and exact terminal lineage;
- preserved Slice 1→Slice 7 regressions.

## 3. Deferred / nonclaims

- correctness of GitHub/GitLab/cloud-provider production APIs;
- production credentials, IAM, KMS/HSM, TLS PKI, DNS, proxies, service mesh, or secret leasing;
- Byzantine or malicious remote infrastructure beyond the frozen response/binding attacks;
- multi-region consensus, quorum replication, or globally distributed exactly-once semantics;
- physical power-loss durability beyond the reference SQLite/filesystem semantics;
- provider-specific rate-limit/backoff correctness;
- organizational release-policy correctness.

## 4. Frozen input contract

### Remote terminal request

- `terminal_execution_id`
- `project_id`
- `task_id`
- `effect_id`
- `action`
- `artifact_sha`
- `state_version`
- `slice7_completion_hash`
- `binding_hash`
- `remote_idempotency_key`

`remote_idempotency_key` must be platform-derived from the exact terminal execution identity and binding hash and must not be supplied or replaced by the model, worker, reviewer, adapter, or remote service.

### Remote service durable record

- `remote_idempotency_key`
- `binding_hash`
- exact terminal lineage fields
- `remote_effect_state`: `ACCEPTED`, `APPLIED`, or `FAILED`
- deterministic `remote_result`
- deterministic `remote_receipt_hash`

## 5. Frozen authority/mechanism invariants

**S8-I01 Slice 7 completion binding required** — remote transport is unreachable without an exact valid Slice 7 completed/recovered/replayed terminal binding.

**S8-I02 Platform-owned idempotency identity** — the idempotency key is derived deterministically from terminal execution identity + exact binding hash and cannot be overridden by caller/model/remote content.

**S8-I03 One idempotency key, one binding** — reuse of the same remote idempotency key with any changed project/task/effect/action/artifact/state-version/binding hash is rejected without a second remote effect.

**S8-I04 Remote commit-before-ack non-amplification** — if the remote service durably applies the effect and the caller loses the response, retry/reconciliation must recover the same remote result without reapplying the effect.

**S8-I05 Lost-request safety** — if delivery never reaches the remote durable boundary, retry may deliver once and apply at most one effect.

**S8-I06 Timeout ambiguity is not completion** — caller timeout or transport exception alone cannot mint remote completion evidence.

**S8-I07 Reconciliation required after ambiguous outcome** — an ambiguous caller outcome must be resolved from the remote durable idempotency record before completion can be asserted.

**S8-I08 Concurrent duplicate convergence** — concurrent identical remote deliveries converge to one durable remote effect/result.

**S8-I09 Remote response cannot widen authority** — response fields claiming a different project/task/effect/action/artifact/state/version are rejected and cannot alter platform completion evidence.

**S8-I10 Structured remote failure is not success** — `FAILED`, error, rejected, or malformed remote results cannot be laundered into completion.

**S8-I11 Deterministic remote completion evidence** — success evidence binds terminal execution id, Slice 7 completion hash, binding hash, remote idempotency key, exact lineage, remote receipt hash/result digest, and a deterministic completion hash.

**S8-I12 Replay non-amplification across restart** — reopening both caller state and remote durable service preserves one-effect semantics and returns/reconciles the prior result.

**S8-I13 Reference transport only** — a successful reference HTTP effect proves only the tested local remote-transport protocol; it does not prove a real production merge/deploy/release/completion occurred.

## 6. Frozen decision/result states

- `DENY_SLICE7_BINDING`
- `DENY_REMOTE_IDEMPOTENCY_REBIND`
- `REMOTE_DELIVERY_FAILED`
- `REMOTE_OUTCOME_AMBIGUOUS`
- `REMOTE_EXECUTION_FAILED`
- `REMOTE_EXECUTION_COMPLETED`
- `REMOTE_EXECUTION_RECONCILED`
- `REMOTE_EXECUTION_REPLAYED`

Only `REMOTE_EXECUTION_COMPLETED`, `REMOTE_EXECUTION_RECONCILED`, and `REMOTE_EXECUTION_REPLAYED` may carry successful remote completion evidence.

## 7. Frozen acceptance cases

- `S8-01` exact valid Slice 7 completion delivers one remote RELEASE effect and records deterministic completion evidence.
- `S8-02` valid MERGE binding executes only MERGE remotely.
- `S8-03` valid DEPLOY binding executes only DEPLOY remotely.
- `S8-04` valid COMPLETE binding executes only COMPLETE remotely.
- `S8-05` missing/malformed/non-success Slice 7 completion denies before remote delivery.
- `S8-06` changed project/task/effect/action/artifact/state-version/binding between Slice 7 and remote request denies.
- `S8-07` caller/model-supplied replacement idempotency key is rejected.
- `S8-08` same idempotency key with changed binding is rejected and remote effect count remains one.
- `S8-09` connection failure before remote durable acceptance produces no remote effect; retry applies once.
- `S8-10` remote applies effect then response is lost; caller records ambiguous outcome, retry/reconciliation returns prior result, effect count remains one.
- `S8-11` caller timeout after remote commit cannot directly mint completion evidence.
- `S8-12` explicit reconciliation after S8-11 resolves to one prior durable result and produces completion evidence without a second effect.
- `S8-13` concurrent duplicate identical requests produce one remote effect and converge to one result.
- `S8-14` remote response with widened target/action/lineage is rejected.
- `S8-15` structured remote failure cannot produce completion evidence.
- `S8-16` malformed/missing remote receipt hash cannot produce completion evidence.
- `S8-17` restart caller + remote service after commit-before-ack ambiguity still reconciles without duplicate effect.
- `S8-18` deterministic completion evidence hash changes/invalidates on any bound-field mutation.
- `S8-19` green CI/model/reviewer/remote self-report cannot replace exact Slice 7 binding or remote durable receipt.
- `S8-20` no result claims a real production remote merge/release/deploy/completion occurred.

## 8. Construction and freeze rules

1. Commit this contract before implementation or tests.
2. Add the falsification tests before mechanism implementation wherever scientifically feasible; preserve red evidence for exposed defects.
3. Do not weaken acceptance cases to obtain green.
4. The reference remote service must require no external network credentials and must remain deterministic/replayable.
5. Preserve exact remote effect counts and durable ledgers in test evidence.
6. Freeze a candidate only after S8-01..S8-20 and the accepted Slice 1→Slice 7 regression chain are green.
7. A fresh independent review of the exact Slice 8 candidate is mandatory.
8. Deterministic review-of-review and exact closure-head validation are mandatory before promotion.
9. Green CI or reviewer/model PASS alone is not merge authority.

## 9. Claim boundary

A bounded pass supports only that the tested reference HTTP remote transport, durable remote idempotency ledger, ambiguity reconciliation, and exact lineage binding prevented duplicate/widened effects under the frozen loss, retry, timeout, restart, concurrency, malformed-response, and structured-failure cases. It does not establish production third-party API correctness, production credential security, distributed multi-region exactly-once semantics, or real release/deploy/merge safety.
