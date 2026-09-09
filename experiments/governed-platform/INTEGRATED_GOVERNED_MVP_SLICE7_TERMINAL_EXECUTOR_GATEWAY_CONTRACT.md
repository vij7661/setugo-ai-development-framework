# Integrated Governed MVP — Slice 7 Terminal Executor Gateway Contract

Status: **PRE-IMPLEMENTATION FROZEN BOUNDARY — OPTION B AMENDED AFTER FALSE-GREEN REVIEW**

Parent authoritative integration commit: `922a9a0c2c898f5605b1ac1b491e41e494c91ccc` (accepted Slice 6 terminal-authority gate).

Preserved pre-amendment candidate: `c94d8aab9128a5dac418492697bc42992b219a37`.

The pre-amendment candidate passed S7-01..S7-21 and received an authenticated Gemini PASS, but deterministic review-of-review found two uncovered authority/mechanism defects: (1) no use-time authority freshness/revocation input existed, and (2) a crash after adapter side-effect success but before the local completion commit could permit duplicate side effects on retry. Those results remain evidence and do not count as promotion authority.

## 1. Goal

Falsify whether a separately controlled terminal executor can consume one exact Slice 6 `AUTHORIZED_FOR_TERMINAL_ACTION` receipt and perform one bounded terminal action through a deterministic reference adapter without allowing replay, receipt substitution, moved artifact/state, model or worker claims, stale/revoked authority, adapter self-report, crash/retry, or concurrency to duplicate or widen terminal execution.

This slice moves one step beyond authorization by executing a **local deterministic reference terminal adapter** and durably recording completion evidence. It does **not** perform a real GitHub merge, cloud deployment, production release, or production completion operation.

## 2. Included

- exact Slice 6 authorization-receipt validation;
- exact project/task/effect/action/artifact/state-version binding;
- verification that the receipt is internally hash-consistent and `AUTHORIZED_FOR_TERMINAL_ACTION`;
- current authoritative-state revalidation immediately before terminal execution;
- exact target-artifact/head revalidation immediately before terminal execution;
- **use-time external-authority revalidation against a current authority snapshot and explicit current time**;
- denial of revoked, not-yet-valid, expired, replaced, or lineage-mismatched terminal authority at execution time;
- durable local idempotency/non-rebind keyed by terminal execution identity;
- deterministic local terminal adapter invocation for `RELEASE`, `DEPLOY`, `MERGE`, or `COMPLETE`;
- **adapter-level durable idempotency/recovery keyed by the same terminal execution identity and exact binding hash**;
- crash representation before adapter invocation, after adapter side-effect success/before local completion commit, and after local durable completion/before response;
- replay/restart recovery without duplicate adapter execution;
- concurrent identical request convergence;
- adapter failure recorded as failure, never laundered into completion;
- durable deterministic completion evidence binding authorization receipt, authority snapshot, target, action, execution identity, and adapter result;
- model/worker/reviewer/CI claims retained only as non-authoritative evidence;
- explicit nonclaim for real remote/production side-effect safety.

## 3. Deferred / nonclaims

- real GitHub/GitLab/Bitbucket merge/push;
- real cloud/Kubernetes/server deployment;
- production release publication;
- production completion mutation;
- production credentials, IAM, KMS/HSM, signed human identity, or secret leasing;
- external network correctness;
- correctness of third-party remote API idempotency implementations;
- distributed/multi-host exactly-once execution beyond the tested durable adapter protocol;
- physical power-loss durability beyond SQLite/reference filesystem semantics;
- organizational release-policy correctness.

## 4. Frozen input contract

### Terminal execution request

- `terminal_execution_id`
- `project_id`
- `task_id`
- `effect_id`
- `action`
- `artifact_sha`
- `expected_state_version`
- `authorization_receipt`

### Current authoritative state

- `project_id`
- `state_version`
- `artifact_sha`

### Current terminal-authority snapshot

The use-time authority source is external to the model/worker and must provide:

- `authority_id`
- `status`: `ACTIVE` or `REVOKED`
- `not_before_epoch`
- `expires_at_epoch`
- `project_id`
- `task_id`
- `effect_id`
- `action`
- `artifact_sha`
- `state_version`
- `authority_snapshot_hash`

The executor also receives explicit `now_epoch`. It must validate the authority snapshot hash and require:

`status == ACTIVE`, `not_before_epoch <= now_epoch < expires_at_epoch`, exact `authority_id` equality with the Slice 6 receipt, and exact project/task/effect/action/artifact/state-version equality with the terminal request and receipt.

A hash-valid historical Slice 6 authorization receipt alone is insufficient at execution time.

### Terminal adapter protocol

The reference adapter is a separately durable idempotent boundary. It must expose:

- `recover(terminal_execution_id, binding_hash)` → the previously durable adapter result for that exact identity/binding, or `None` if no side effect has been durably accepted;
- `execute_once(terminal_execution_id, binding_hash, binding)` → durably apply/record at most one side effect for that identity/binding and return the deterministic adapter result.

The adapter must reject reuse of one terminal execution identity with a different binding hash. Recovery and execution state must survive reopening the terminal executor. The adapter may not choose a different action, target artifact, project, task, effect, or state version.

A plain non-idempotent callable is insufficient for this amended slice.

## 5. Frozen authority invariants

**S7-I01 Slice 6 authority required** — terminal execution is unreachable without an exact valid Slice 6 receipt in state `AUTHORIZED_FOR_TERMINAL_ACTION`.

**S7-I02 Receipt integrity** — receipt hash must validate against the complete receipt body; tampering fails closed.

**S7-I03 Exact request binding** — request project/task/effect/action/artifact/state-version must equal the receipt bound lineage.

**S7-I04 Current-state revalidation** — request project/state-version/artifact must still equal current authoritative state immediately before adapter execution.

**S7-I05 No moved-target execution** — changed artifact/head after authorization denies execution.

**S7-I06 Terminal action containment** — authorization for one action cannot execute another action.

**S7-I07 Durable idempotency/non-rebind** — one `terminal_execution_id` maps to at most one exact authorization/request/authority-snapshot binding.

**S7-I08 Replay non-amplification** — exact replay returns the prior durable result and does not create a second adapter side effect.

**S7-I09 Crash-before-execution safety** — a crash before adapter invocation produces no completed terminal action; exact retry may execute once.

**S7-I10 Crash-after-local-completion recovery** — if adapter success and local completion are durably recorded before response, exact retry returns the recorded completion without duplicate adapter execution.

**S7-I11 Concurrent convergence** — concurrent identical requests converge to one durable adapter execution/result.

**S7-I12 Adapter non-authority** — adapter/model/worker/reviewer/CI self-report cannot widen action/target or turn a failed execution into completion.

**S7-I13 Failure is not completion** — adapter exception/failure records a failed terminal execution and cannot produce a success completion receipt.

**S7-I14 Deterministic completion evidence** — success evidence binds terminal execution id, Slice 6 receipt hash, current authority snapshot hash, project/task/effect/action/artifact/state-version, adapter result digest, and deterministic completion hash.

**S7-I15 Reference-only production boundary** — a successful local adapter result proves only bounded reference terminal execution; it is not evidence that a production merge/release/deploy/completion occurred.

**S7-I16 Use-time authority freshness** — the terminal executor must validate the external authority snapshot at the actual execution attempt. Revoked, replaced, not-yet-valid, expired, malformed, or lineage-mismatched authority denies before adapter invocation. Prior receipt validity, reviewer PASS, CI, or conversation state cannot substitute.

**S7-I17 Side-effect/local-record crash non-amplification** — if the adapter durably applies its side effect and the process dies before the executor commits local completion, retry must recover the adapter's durable result by terminal execution identity + exact binding hash and must not apply the side effect again.

**S7-I18 Adapter idempotency is part of the authority boundary** — terminal execution must not invoke a plain non-idempotent adapter. The tested adapter protocol must durably enforce one identity → one exact binding/result and reject binding reuse.

## 6. Frozen decision/result states

- `DENY_AUTHORIZATION_RECEIPT`
- `DENY_AUTHORITY_FRESHNESS`
- `DENY_BINDING`
- `DENY_CURRENT_STATE`
- `DENY_IDEMPOTENCY_REBIND`
- `TERMINAL_EXECUTION_FAILED`
- `TERMINAL_EXECUTION_COMPLETED`
- `TERMINAL_EXECUTION_REPLAYED`
- `TERMINAL_EXECUTION_RECOVERED`

Only `TERMINAL_EXECUTION_COMPLETED`, `TERMINAL_EXECUTION_REPLAYED`, and `TERMINAL_EXECUTION_RECOVERED` may carry a successful completion evidence record.

## 7. Frozen acceptance cases

The original S7-01..S7-21 remain frozen and must continue to pass, with valid current-authority input supplied to successful execution paths.

- `S7-01` exact valid Slice 6 RELEASE receipt + current matching state + current active authority invokes adapter once and records completion.
- `S7-02` valid MERGE receipt executes only MERGE.
- `S7-03` valid DEPLOY receipt executes only DEPLOY.
- `S7-04` valid COMPLETE receipt executes only COMPLETE.
- `S7-05` missing/non-authorized/malformed receipt denies before adapter invocation.
- `S7-06` tampered Slice 6 receipt hash denies before adapter invocation.
- `S7-07` project/task/effect/action/artifact/state-version substitution between request and receipt denies.
- `S7-08` moved current artifact/head after authorization denies.
- `S7-09` stale or future current authoritative state version denies.
- `S7-10` same execution identity with changed action/artifact/receipt/binding fails as idempotency rebind.
- `S7-11` exact replay returns prior result without a second adapter side effect.
- `S7-12` crash before adapter invocation leaves no successful durable completion; retry executes once.
- `S7-13` crash after successful durable local completion but before response recovers without duplicate adapter execution.
- `S7-14` concurrent identical requests invoke adapter side effect at most once and converge to one durable result.
- `S7-15` adapter exception/failure cannot produce successful completion evidence.
- `S7-16` adapter claim of different target/action cannot widen execution or completion evidence.
- `S7-17` green CI/model/reviewer success fields cannot replace Slice 6 authorization or current authority.
- `S7-18` completion evidence self-hash is deterministic and changes/invalidates on bound-field mutation.
- `S7-19` restart/reopen preserves idempotency and replay recovery.
- `S7-20` after denial/failure/replay cases, a fresh independently authorized execution id remains live and completes exactly once.
- `S7-21` no result claims a real production remote merge/release/deploy/completion occurred.

**Option B additions, frozen before repair:**

- `S7-22` expired current authority denies before adapter invocation even when the historical Slice 6 receipt remains hash-valid and authorized.
- `S7-23` revoked current authority denies before adapter invocation.
- `S7-24` not-yet-valid authority and authority-id/project/task/effect/action/artifact/state-version substitution deny before adapter invocation.
- `S7-25` tampered authority snapshot hash denies before adapter invocation.
- `S7-26` crash after durable adapter side-effect success but before local completion commit: exact retry recovers the adapter result and the adapter side-effect count remains exactly one.
- `S7-27` reopening both executor and durable adapter after the S7-26 crash still recovers without a second side effect.
- `S7-28` one adapter idempotency identity cannot be rebound to a different binding hash.
- `S7-29` a plain callable/non-idempotent adapter is rejected before any terminal action.
- `S7-30` completion evidence binds the exact current `authority_snapshot_hash`; changing the authority snapshot changes/invalidates completion evidence.

## 8. Construction and freeze rules

1. The original contract and candidate remain preserved.
2. Commit this Option B amendment before adding/repairing mechanism behavior.
3. Add S7-22..S7-30 and expose the pre-repair failures before mechanism repair.
4. Preserve the failing exact candidate and CI evidence.
5. Repairs may not weaken an invariant, acceptance case, or nonclaim.
6. Tests must require no external network or production credentials.
7. Freeze a new exact candidate SHA only after S7-01..S7-30 and the accepted Slice 1→Slice 6 regression chain are green.
8. A fresh independent integration review of the repaired exact candidate is mandatory; prior Gemini PASS cannot be reused.
9. Deterministic review-of-review remains mandatory before promotion.
10. Green CI or reviewer/model PASS alone is not merge authority.

## 9. Claim boundary

A bounded pass supports only that the tested local reference terminal executor consumed an exact Slice 6 authorization receipt, revalidated current terminal authority at use time, and executed one deterministic local terminal adapter action using the tested durable adapter idempotency/recovery protocol under the tested binding, replay, crash, restart, failure, and concurrency conditions. It does not establish production remote side-effect safety, credential security, third-party remote API idempotency correctness, distributed exactly-once execution, deployment safety, or organizational release correctness.
