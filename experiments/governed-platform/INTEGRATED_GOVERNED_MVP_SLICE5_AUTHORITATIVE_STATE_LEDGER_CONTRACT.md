# Integrated Governed MVP — Slice 5 Authoritative State Ledger Contract

Status: **PRE-IMPLEMENTATION FROZEN BOUNDARY**

Parent product integration commit: `a2fcd2ba9bc0e5828ee69056c23207fb431ecea6` (accepted Slice 4).
Governance prerequisite: PR #11 merged on `main` at `d46db1173db7db5b42459bf49f7fa28ef3dd105a` after authenticated `REV-GOV-PR11-006` PASS and green closure validation.

## 1. Goal

Falsify whether a modular-monolith reference backend can make the **accepted event + idempotency identity + authoritative state version + durable side-effect intent** one atomic transaction, so retries, crashes, concurrency, stale versions, payload rebinding, and worker/model claims cannot create duplicate or ungrounded authoritative transitions.

This slice implements a local SQLite reference mechanism only. It does not claim distributed consensus, physical power-loss guarantees beyond SQLite's documented transaction model, multi-host atomicity, or production-scale persistence.

## 2. Frozen transaction boundary

For a governed command, one database transaction must atomically persist:

1. immutable accepted-event record;
2. `(project_id, idempotency_key)` uniqueness;
3. canonical command/payload digest;
4. expected prior state version;
5. resulting authoritative state/version;
6. deterministic transition/result digest;
7. durable outbox record for any consequential downstream side effect.

No downstream side effect may execute before that transaction commits.

## 3. Authority invariants

**S5-I01 Atomic acceptance** — accepted event, idempotency identity, resulting state and outbox intent commit together or not at all.

**S5-I02 Intent-level idempotency** — the same `(project_id, idempotency_key)` + same canonical command converges to the original result; no new state version or outbox item is created.

**S5-I03 Rebinding rejection** — reuse of an idempotency key with a different command/payload digest fails closed.

**S5-I04 Optimistic version binding** — command acceptance requires exact expected current state version. Stale/future expected versions cannot mutate state.

**S5-I05 Monotonic authoritative version** — every successful non-replay transition increments the project state version exactly once.

**S5-I06 Side-effect-after-commit** — no worker/tool dispatch is permitted until a committed outbox record exists.

**S5-I07 Crash-before-commit** — failure before commit leaves no accepted event, state transition, or outbox side effect intent.

**S5-I08 Crash-after-commit-before-dispatch** — committed authoritative state and pending outbox intent survive and are discoverable for recovery.

**S5-I09 Dispatch replay safety** — repeated claiming/completion of the same outbox item cannot create duplicate authoritative state transitions; side-effect completion status is durable and monotonic.

**S5-I10 Concurrent same-intent convergence** — concurrent identical commands using one idempotency key converge to one accepted event/state version/outbox record.

**S5-I11 Concurrent conflicting intent fail-closed** — concurrent commands competing for the same expected state version cannot both become authoritative.

**S5-I12 Model/worker non-authority** — model or worker output cannot directly set authoritative state/version, mark an event accepted, or invent completion authority; only the ledger transaction may do so.

**S5-I13 Evidence lineage** — accepted events and outbox records expose canonical digests and immutable identifiers sufficient to reconstruct why an authoritative state version exists.

**S5-I14 Recovery is repository/data driven** — recovery enumerates committed pending outbox rows; it never infers completion from process memory, chat state, or worker assertions.

## 4. Frozen cases

- `S5-01` first valid command atomically creates event/state/outbox.
- `S5-02` exact retry returns original result without duplicate version/outbox.
- `S5-03` same idempotency key + changed payload is rejected.
- `S5-04` stale expected version is rejected with no mutation.
- `S5-05` future expected version is rejected with no mutation.
- `S5-06` injected failure after event insert but before state update rolls back everything.
- `S5-07` injected failure after state update but before outbox insert rolls back everything.
- `S5-08` crash immediately after commit preserves state and pending outbox.
- `S5-09` pending outbox recovery after repository/process reopen is deterministic.
- `S5-10` outbox completion is idempotent.
- `S5-11` duplicate completion/replay cannot advance authoritative state.
- `S5-12` concurrent identical submissions converge to one event/version/outbox.
- `S5-13` concurrent distinct submissions at one expected version permit at most one success.
- `S5-14` worker/model-supplied state/version/completion claims are ignored/rejected as authority inputs.
- `S5-15` event/result/outbox digests are stable across reopen/replay.
- `S5-16` invariant audit reconstructs contiguous state version lineage and detects tampered/missing lineage in a copied test database.

## 5. Acceptance criteria

A bounded Slice5 pass requires all `S5-01..S5-16` deterministic tests to pass on the exact implementation candidate and the broader integrated-governed-MVP regression suite to remain green. Provider LLM APIs are not required for the construction run.

A pass proves only the frozen single-database reference mechanism. Independent integration review remains mandatory before this slice can be promoted into the accepted integrated MVP boundary.

## 6. Forbidden shortcuts

- do not dispatch side effects before commit;
- do not treat queue delivery as authoritative state;
- do not overwrite/reuse an idempotency key for new intent;
- do not let worker/model output choose authoritative version or completion;
- do not make tests pass by weakening expected-version checks;
- do not delete failed/crash/replay evidence;
- do not claim distributed or physical durability from this reference mechanism.
