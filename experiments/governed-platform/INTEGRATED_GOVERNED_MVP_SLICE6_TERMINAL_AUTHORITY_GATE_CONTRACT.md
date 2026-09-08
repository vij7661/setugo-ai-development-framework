# Integrated Governed MVP — Slice 6 Terminal Authority / Release-Completion Gate Contract

Status: **FROZEN BOUNDARY — AMENDED BY AUTHORITATIVE REQUIREMENT DECISION A**

Parent authoritative integration commit: `f67e0dfb4fe9b4bb67c76dbd43f1485861c96fc0` (accepted Slice 5 authoritative state ledger).

Amendment basis: deterministic review-of-review of `REV-MVP-SLICE6-TERMINAL-AUTHORITY-004` exposed an internal contradiction between the original broad wording of S6-I05 and the already-frozen per-input schemas. The authoritative decision is to preserve those schemas and narrow S6-I05 accordingly. No implementation field expansion is authorized by this amendment.

## 1. Goal

Falsify whether the integrated governed MVP can add the separate external terminal-authority boundary already required by the accepted composition contract without allowing model/worker claims, stale review evidence, stale artifact identity, replay, action substitution, or prior green CI to mint RELEASE / DEPLOY / MERGE / completion authority.

This slice produces a deterministic **terminal authorization receipt** only. It does not perform a remote push, merge, release, deployment, production mutation, or production completion action.

## 2. Required input lineage

A terminal decision consumes explicit bound inputs only:

1. `terminal_request`
   - `project_id`
   - `task_id`
   - `action` — one of `RELEASE`, `DEPLOY`, `MERGE`, `COMPLETE`
   - `effect_id`
   - `artifact_sha`
   - `expected_state_version`
2. `execution_evidence`
   - exact project/task/effect lineage
   - exact resulting artifact SHA
   - successful prior isolated execution state
   - `terminal_authority == false`
   - `release_completion_authority == false`
   - deterministic evidence hash
3. `review_gate`
   - `state == CLEAR`
   - immutable/frozen `evidence_refs`
   - exact reviewed `artifact_sha`
   - exact reviewed `action`
4. `authority_record`
   - `authority_id`
   - `source_class` — `HUMAN` or `PLATFORM_POLICY`
   - `decision` — `APPROVE` or `DENY`
   - exact project/task/effect/action/artifact binding
   - exact `state_version`
   - `issued_at_epoch`
   - `expires_at_epoch`
   - immutable/frozen `evidence_refs`
   - deterministic `authority_record_hash`
5. `current_state`
   - exact `project_id`
   - exact current authoritative `state_version`
6. explicit `now_epoch`

No ambient conversation history, provider/model label, worker assertion, prior workflow status, or stale CI result is authority.

## 3. Frozen authority invariants

**S6-I01 Separate terminal authority** — prior isolated execution success never implies terminal authority.

**S6-I02 External source class** — `MODEL`, `WORKER`, `RESEARCHER`, `JUDGE`, or any unrecognized source class cannot authorize terminal action. Only structurally valid `HUMAN` or `PLATFORM_POLICY` authority records may proceed in this bounded reference mechanism.

**S6-I03 Exact action binding** — approval for one terminal action cannot authorize another action.

**S6-I04 Exact artifact binding** — approval/review for one artifact SHA cannot authorize a different artifact SHA or a changed branch head.

**S6-I05 Scoped exact lineage binding** — bindings are enforced according to each frozen input schema, without inferring absent fields: `terminal_request`, `execution_evidence`, and `authority_record` must share exact project/task/effect/artifact lineage; `review_gate` must bind the exact terminal action and artifact SHA with immutable evidence references; `current_state` must bind the exact project ID and authoritative state version. No task/effect/artifact fields are required in `current_state`, and no project/task/effect fields are required in `review_gate` unless a later separately approved contract explicitly changes those schemas.

**S6-I06 Current authoritative version** — request `expected_state_version` must equal current authoritative `state_version`; stale/future versions fail closed.

**S6-I07 Review required** — terminal authorization requires a well-formed `CLEAR` review gate bound to the exact action and artifact. `REVIEW_REQUIRED`, `HUMAN_REQUIRED`, malformed, missing, or stale review evidence cannot authorize.

**S6-I08 Explicit approval** — only `decision == APPROVE` can authorize. `DENY`, missing, malformed, or contradictory decisions fail closed.

**S6-I09 Time validity** — authority record must be issued no later than `now_epoch` and must not be expired.

**S6-I10 Deterministic authority-record integrity** — the supplied authority-record hash must match canonical deterministic content. Tampering fails closed.

**S6-I11 Evidence integrity** — execution evidence must be self-consistent, deterministically hashed, and explicitly non-terminal in its own authority fields.

**S6-I12 No success laundering** — green CI, model success, reviewer/model agreement, isolated execution success, or repository mutation success cannot substitute for the terminal authority record.

**S6-I13 Idempotent decision** — identical bound inputs produce the same terminal decision receipt and digest.

**S6-I14 Rebinding rejection** — reusing an authority identity/hash for a changed action, artifact, lineage, or state version cannot authorize.

**S6-I15 Receipt is not side effect** — `AUTHORIZED_FOR_TERMINAL_ACTION` means a separately controlled terminal executor may be invoked for the exact bound action; it is not proof that the action occurred.

**S6-I16 Source authentication nonclaim** — this reference validates structure, binding, freshness, and deterministic integrity only. It does not prove cryptographic human identity, production IAM, signature authenticity, KMS custody, or organizational authorization policy.

## 4. Frozen decision states

- `DENY_REQUEST`
- `DENY_EXECUTION_EVIDENCE`
- `DENY_REVIEW_GATE`
- `DENY_AUTHORITY_SOURCE`
- `DENY_AUTHORITY_RECORD`
- `DENY_STATE_VERSION`
- `DENY_EXPIRED_AUTHORITY`
- `TERMINAL_ACTION_DENIED`
- `AUTHORIZED_FOR_TERMINAL_ACTION`

Every decision must include:

- `authorized`
- `terminal_authority`
- `release_completion_authority`
- exact bound lineage
- deterministic `receipt_hash`
- reason

Only `AUTHORIZED_FOR_TERMINAL_ACTION` may set `authorized`, `terminal_authority`, and `release_completion_authority` true.

## 5. Frozen acceptance cases

- `S6-01` exact valid RELEASE approval reaches `AUTHORIZED_FOR_TERMINAL_ACTION`.
- `S6-02` valid MERGE approval reaches authorization only for MERGE.
- `S6-03` valid DEPLOY approval reaches authorization only for DEPLOY.
- `S6-04` valid COMPLETE approval reaches authorization only for COMPLETE.
- `S6-05` prior isolated execution success without authority record is denied.
- `S6-06` model/worker authority source is denied.
- `S6-07` action substitution is denied.
- `S6-08` artifact SHA substitution / moved head is denied.
- `S6-09` project/task/effect lineage mismatch is denied where those fields are present in the frozen input schema.
- `S6-10` stale expected authoritative state version is denied.
- `S6-11` future expected authoritative state version is denied.
- `S6-12` `REVIEW_REQUIRED` cannot authorize.
- `S6-13` `HUMAN_REQUIRED` cannot authorize.
- `S6-14` malformed review gate cannot authorize.
- `S6-15` explicit authority `DENY` returns `TERMINAL_ACTION_DENIED`.
- `S6-16` expired authority is denied.
- `S6-17` future-issued authority is denied.
- `S6-18` tampered authority record hash is denied.
- `S6-19` malformed/tampered execution evidence is denied.
- `S6-20` execution evidence attempting terminal authority is denied.
- `S6-21` identical replay returns identical decision body and receipt hash.
- `S6-22` green-CI/model-success fields in auxiliary evidence cannot authorize without valid authority record.
- `S6-23` authority identity/hash cannot be rebound to a changed artifact/action/state version and remain valid.
- `S6-24` authorized receipt contains no claim that merge/deploy/release/completion actually occurred.
- `S6-25` Option-A schema preservation: a valid authorization succeeds with `review_gate` containing only its frozen action/artifact/evidence fields and `current_state` containing only project/state-version fields; absent non-schema task/effect/artifact fields must not be invented or required.

## 6. Acceptance criteria

A bounded Slice 6 pass requires all `S6-01..S6-25` deterministic tests to pass on one exact candidate SHA and the accepted Slice 1→Slice 5 regression chain to remain green.

Independent integration review remains mandatory before promotion into `main`.

## 7. Forbidden shortcuts

- do not turn green CI into terminal authority;
- do not treat model/reviewer consensus as authority;
- do not accept moved artifact/head identity after review;
- do not widen approval from one terminal action to another;
- do not accept stale/future authoritative state versions;
- do not weaken review requirements to obtain a pass;
- do not infer human identity from a string label;
- do not claim the terminal action occurred merely because the gate authorized it;
- do not invent or require fields outside the frozen per-input schemas to satisfy an over-broad interpretation of lineage;
- do not modify accepted Slice 1→Slice 5 behavior to accommodate this slice.

## 8. Claim boundary

A bounded pass proves only a deterministic reference terminal-authorization gate with scoped per-input action/artifact/lineage/state-version binding, explicit external approval input, review-gate dependency, freshness checks, and model/worker non-authority. It does not prove production identity authentication, cryptographic signatures, IAM/KMS correctness, remote side-effect safety, deployment safety, or organizational release policy correctness.

## 9. Preserved contradiction and decision history

The original S6-I05 wording remains part of repository history and is not rewritten retroactively. `REV-MVP-SLICE6-TERMINAL-AUTHORITY-004` returned semantic PASS but deterministic adjudication classified the contract contradiction as `REQUIREMENT_UNRESOLVED_CONTRACT_INTERNAL_CONTRADICTION` with authority effect `NONE`. The authoritative requirement decision selected Option A: preserve the frozen input schemas and narrow S6-I05 to those per-object bindings. All earlier review outcomes, provider failures, defect exposure, and repair commits remain historical evidence and do not authorize promotion of this amended candidate.
