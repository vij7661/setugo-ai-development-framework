# Integrated Governed MVP — Slice 7 Terminal Executor Gateway Contract

Status: **PRE-IMPLEMENTATION FROZEN BOUNDARY**

Parent authoritative integration commit: `922a9a0c2c898f5605b1ac1b491e41e494c91ccc` (accepted Slice 6 terminal-authority gate).

## 1. Goal

Falsify whether a separately controlled terminal executor can consume one exact Slice 6 `AUTHORIZED_FOR_TERMINAL_ACTION` receipt and perform one bounded terminal action through a deterministic reference adapter without allowing replay, receipt substitution, moved artifact/state, model or worker claims, stale authority, adapter self-report, crash/retry, or concurrency to duplicate or widen terminal execution.

This slice moves one step beyond authorization by executing a **local deterministic reference terminal adapter** and durably recording completion evidence. It does **not** perform a real GitHub merge, cloud deployment, production release, or production completion operation.

## 2. Included

- exact Slice 6 authorization-receipt validation;
- exact project/task/effect/action/artifact/state-version binding;
- verification that the receipt is internally hash-consistent and `AUTHORIZED_FOR_TERMINAL_ACTION`;
- current authoritative-state revalidation immediately before terminal execution;
- exact target-artifact/head revalidation immediately before terminal execution;
- durable local idempotency/non-rebind keyed by terminal execution identity;
- deterministic local terminal adapter invocation for `RELEASE`, `DEPLOY`, `MERGE`, or `COMPLETE`;
- crash representation before adapter invocation and after adapter success/before response;
- replay recovery without duplicate adapter execution;
- concurrent identical request convergence;
- adapter failure recorded as failure, never laundered into completion;
- durable deterministic completion evidence binding authorization receipt, target, action, execution identity, and adapter result;
- model/worker/reviewer/CI claims retained only as non-authoritative evidence;
- explicit nonclaim for real remote/production side-effect safety.

## 3. Deferred / nonclaims

- real GitHub/GitLab/Bitbucket merge/push;
- real cloud/Kubernetes/server deployment;
- production release publication;
- production completion mutation;
- production credentials, IAM, KMS/HSM, signed human identity, or secret leasing;
- external network correctness;
- remote API idempotency semantics;
- distributed/multi-host exactly-once execution;
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

### Terminal adapter

The reference adapter receives only the already-bound execution request and returns a deterministic adapter result. It may not choose a different action, target artifact, project, task, effect, or state version.

## 5. Frozen authority invariants

**S7-I01 Slice 6 authority required** — terminal execution is unreachable without an exact valid Slice 6 receipt in state `AUTHORIZED_FOR_TERMINAL_ACTION`.

**S7-I02 Receipt integrity** — receipt hash must validate against the complete receipt body; tampering fails closed.

**S7-I03 Exact request binding** — request project/task/effect/action/artifact/state-version must equal the receipt bound lineage.

**S7-I04 Current-state revalidation** — request project/state-version/artifact must still equal current authoritative state immediately before adapter execution.

**S7-I05 No moved-target execution** — changed artifact/head after authorization denies execution.

**S7-I06 Terminal action containment** — authorization for one action cannot execute another action.

**S7-I07 Durable idempotency/non-rebind** — one `terminal_execution_id` maps to at most one exact authorization/request binding.

**S7-I08 Replay non-amplification** — exact replay returns the prior durable result and does not invoke the adapter again.

**S7-I09 Crash-before-execution safety** — a crash before adapter invocation produces no completed terminal action; exact retry may execute once.

**S7-I10 Crash-after-execution recovery** — if the adapter succeeds and durable execution is recorded before response, exact retry returns the recorded completion without duplicate adapter execution.

**S7-I11 Concurrent convergence** — concurrent identical requests converge to one durable adapter execution/result.

**S7-I12 Adapter non-authority** — adapter/model/worker/reviewer/CI self-report cannot widen action/target or turn a failed execution into completion.

**S7-I13 Failure is not completion** — adapter exception/failure records a failed terminal execution and cannot produce a success completion receipt.

**S7-I14 Deterministic completion evidence** — success evidence binds terminal execution id, Slice 6 receipt hash, project/task/effect/action/artifact/state-version, adapter result digest, and deterministic completion hash.

**S7-I15 Reference-only production boundary** — a successful local adapter result proves only bounded reference terminal execution; it is not evidence that a production merge/release/deploy/completion occurred.

## 6. Frozen decision/result states

- `DENY_AUTHORIZATION_RECEIPT`
- `DENY_BINDING`
- `DENY_CURRENT_STATE`
- `DENY_IDEMPOTENCY_REBIND`
- `TERMINAL_EXECUTION_FAILED`
- `TERMINAL_EXECUTION_COMPLETED`
- `TERMINAL_EXECUTION_REPLAYED`
- `TERMINAL_EXECUTION_RECOVERED`

Only `TERMINAL_EXECUTION_COMPLETED`, `TERMINAL_EXECUTION_REPLAYED`, and `TERMINAL_EXECUTION_RECOVERED` may carry a successful completion evidence record.

## 7. Frozen acceptance cases

- `S7-01` exact valid Slice 6 RELEASE receipt + current matching state invokes adapter once and records completion.
- `S7-02` valid MERGE receipt executes only MERGE.
- `S7-03` valid DEPLOY receipt executes only DEPLOY.
- `S7-04` valid COMPLETE receipt executes only COMPLETE.
- `S7-05` missing/non-authorized/malformed receipt denies before adapter invocation.
- `S7-06` tampered Slice 6 receipt hash denies before adapter invocation.
- `S7-07` project/task/effect/action/artifact/state-version substitution between request and receipt denies.
- `S7-08` moved current artifact/head after authorization denies.
- `S7-09` stale or future current authoritative state version denies.
- `S7-10` same execution identity with changed action/artifact/receipt/binding fails as idempotency rebind.
- `S7-11` exact replay returns prior result without second adapter invocation.
- `S7-12` crash before adapter invocation leaves no successful durable completion; retry executes once.
- `S7-13` crash after successful durable execution but before response recovers without duplicate adapter invocation.
- `S7-14` concurrent identical requests invoke adapter at most once and converge to one durable result.
- `S7-15` adapter exception/failure cannot produce successful completion evidence.
- `S7-16` adapter claim of different target/action cannot widen execution or completion evidence.
- `S7-17` green CI/model/reviewer success fields cannot replace Slice 6 authorization.
- `S7-18` completion evidence self-hash is deterministic and changes/invalidates on bound-field mutation.
- `S7-19` restart/reopen preserves idempotency and replay recovery.
- `S7-20` after denial/failure/replay cases, a fresh independently authorized execution id remains live and completes exactly once.
- `S7-21` no result claims a real production remote merge/release/deploy/completion occurred.

## 8. Construction and freeze rules

1. Commit this contract before acceptance harness or mechanism implementation.
2. Freeze `S7-01..S7-21` before repairing any exposed mechanism defect.
3. Preserve the first complete construction failure/result before repair.
4. Repairs may not weaken an invariant, case, or nonclaim.
5. Tests must require no external network or production credentials.
6. Freeze one exact candidate SHA only after the dedicated Slice 7 suite and accepted Slice 1→Slice 6 regression chain are green.
7. Independent integration review is mandatory before promotion to `main`.
8. Green CI or reviewer/model PASS alone is not merge authority.

## 9. Claim boundary

A bounded pass supports only that the tested local reference terminal executor consumed an exact Slice 6 authorization receipt and executed one deterministic local terminal adapter action with the tested binding, replay, crash, restart, failure, and concurrency properties. It does not establish production remote side-effect safety, credential security, distributed exactly-once execution, deployment safety, or organizational release correctness.
