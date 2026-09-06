# EXP-O Pilot 16 — SQLite WAL / Subprocess Crash Recovery Preregistration

Status: **PRE-REGISTERED BEFORE PILOT 16 IMPLEMENTATION OR TEST EXECUTION**

Parent evidence:

`experiments/governed-platform/adjudication/EXP-O-PILOT15-STORAGE-CRASH-CONSISTENCY-ADJUDICATION.md`

Parent adjudication commit:

`79ce2b6aaa57cb5f6bec2f69383c2e429f583b5d`

## Motivation

Pilot 15 exercised a deterministic written-vs-durable journal model. It deliberately did not establish behavior across an actual database engine process boundary, SQLite WAL transaction commit/reopen semantics, subprocess termination, or database-file substitution after independently retained fencing evidence.

Pilot 16 crosses that boundary without claiming physical power-loss correctness.

## Scientific hypothesis

Across the frozen subprocess-termination and SQLite recovery cases:

1. an uncommitted authority transaction never becomes effective authority after the writer process is killed;
2. committed higher term/index/lease-epoch fences never silently roll back to an older owner after reopen;
3. ambiguous post-effect crashes never permit a second effect for the same logical idempotency intent;
4. idempotency key rebinding to a different effect digest is denied after restart;
5. stale database substitution is rejected when an independently retained anchor proves a higher committed fence;
6. malformed, inconsistent, or incomplete relational state fails closed rather than being repaired into authority during initial recovery;
7. fully committed clean transactions remain live across subprocess restart.

Any stale-authority resurrection or duplicate durable effect falsifies Pilot 16 on that path.

## Frozen architecture under test

Pilot 16 will use a new isolated implementation and must not modify Pilots 14 or 15.

Frozen components:

- parent test controller process;
- separate Python worker subprocess for each authority/effect transition;
- SQLite database in WAL mode;
- `PRAGMA synchronous=FULL` for the exercised database connection;
- normalized authority table containing term, commit index, owner, lease epoch, semantic digest, effect digest, idempotency key, status;
- effect table keyed by idempotency key with exact effect digest and result identity;
- metadata table containing monotonic generation/fence information;
- transaction boundaries controlled explicitly by the worker;
- parent process may terminate the worker only at registered cut points;
- database is reopened by a fresh process/object after each kill;
- independent anchor file retained by the parent test fixture for the stale-substitution case;
- no model-visible input and no model-issued authority.

SQLite/WAL is part of the tested runtime boundary, but this remains a CI-hosted prototype rather than a physical power-loss test.

## Frozen transaction/kill points

The implementation must expose these exact named kill points before first execution:

- `AFTER_BEGIN_BEFORE_AUTHORITY_INSERT`
- `AFTER_AUTHORITY_INSERT_BEFORE_COMMIT`
- `AFTER_AUTHORITY_COMMIT_BEFORE_ACK`
- `AFTER_TAKEOVER_INSERT_BEFORE_COMMIT`
- `AFTER_TAKEOVER_COMMIT_BEFORE_ACK`
- `AFTER_EFFECT_INSERT_BEFORE_COMMIT`
- `AFTER_EFFECT_COMMIT_BEFORE_EVIDENCE_UPDATE`
- `AFTER_EVIDENCE_UPDATE_BEFORE_COMMIT`
- `AFTER_CONSUMED_UPDATE_BEFORE_COMMIT`
- `AFTER_CONSUMED_COMMIT_BEFORE_ACK`

The parent must not emulate a crash by merely returning early from the same process. Registered kill cases must terminate a distinct worker subprocess and reopen the database afterward.

## Frozen recovery rules

Recovery may authorize a consequential effect only if all are true:

- relational state is internally consistent;
- the authority row is committed and marked active;
- term/index/lease epoch are not below the independently retained fence anchor;
- exact semantic/effect/idempotency bindings match the request;
- no effect row already exists for the same idempotency key;
- no consumed state exists;
- no unresolved higher fence or relational inconsistency exists;
- recovery itself performs no authority-widening repair.

If an effect row exists for the same idempotency key and same effect digest, recovery/retry must return the original result identity without executing a second effect.

If the same idempotency key is paired with a different effect digest, recovery must deny rebinding.

## Pre-registered primary falsifiers

Exactly these twenty primary cases must be present before the first Pilot 16 scientific execution.

### P16-01 — clean committed authority survives fresh reopen
Expected: committed active authority is recoverable with exact bindings.

### P16-02 — kill after BEGIN before authority insert
Expected: no authority row; no consequential authority after reopen.

### P16-03 — kill after authority insert before COMMIT
Expected: transaction rolls back; inserted authority does not survive as effective authority.

### P16-04 — kill after authority COMMIT before acknowledgement
Expected: committed authority survives reopen; absence of caller acknowledgement does not erase committed state.

### P16-05 — stale lower authority cannot overwrite committed higher fence
Expected: lower term/index/epoch write is denied or recovery fails closed; higher fence remains authoritative.

### P16-06 — kill after takeover insert before COMMIT
Expected: uncommitted takeover does not replace the old committed owner.

### P16-07 — kill after takeover COMMIT before acknowledgement
Expected: higher committed takeover survives reopen; stale prior owner cannot revive merely because acknowledgement was lost.

### P16-08 — stale database-file substitution after independently anchored higher fence
Expected: recovery detects database state below anchor and fails closed.

### P16-09 — authority row binding corruption
Expected: incomplete/mismatched semantic/effect/idempotency binding cannot authorize use.

### P16-10 — duplicate active authority rows for same logical authority identity
Expected: relational ambiguity fails closed; recovery does not choose one by convenience.

### P16-11 — kill after effect insert before COMMIT
Expected: no committed effect row; retry may execute exactly once under still-valid authority.

### P16-12 — kill after effect COMMIT before evidence/status update
Expected: committed effect row prevents duplicate execution; retry reconciles original result identity.

### P16-13 — kill after evidence/status update before COMMIT
Expected: rolled-back evidence update does not erase committed effect identity; retry remains reconciliation-safe.

### P16-14 — durable effect row with authority still active
Expected: effect presence dominates stale active-authority status; second execution denied/reconciled.

### P16-15 — kill after consumed update before COMMIT
Expected: rollback of consumed flag does not permit duplicate effect because effect row remains authoritative for idempotency.

### P16-16 — kill after consumed COMMIT before acknowledgement
Expected: consumed state and original effect identity survive reopen; no re-execution.

### P16-17 — idempotency key rebinding after restart
Expected: same key + different effect digest is denied.

### P16-18 — missing effect row referenced by consumed/result state
Expected: inconsistent state requires reconciliation/fails closed and does not authorize a new effect.

### P16-19 — WAL/reopen repeated clean replay
Expected: repeated fresh-process opens return the same committed authority/effect/result identity without duplicates or rollback.

### P16-20 — fresh clean authority/effect after prior isolated crash cases
Expected: a new clean transaction sequence remains live and exactly-once, demonstrating fail-closed rules did not destroy normal operation.

## Primary endpoints

1. stale/noncommitted authority resurrection rate;
2. duplicate durable effect rate;
3. stale-fence rollback rate;
4. silent relational-ambiguity promotion rate;
5. clean restart liveness.

Any non-zero authority resurrection or duplicate durable effect event is a falsification on that tested path.

## Evidence policy

- all 20 cases execute in the first scientific run;
- first-run failures are retained exactly;
- diagnosis must inspect SQLite rows/transaction outcome and subprocess exit behavior before repair;
- no failing case may be removed, renamed, weakened, or converted after execution;
- any repair after first execution requires a recorded diagnosis and rerun lineage;
- green CI is never the scientific verdict by itself.

## Isolation

Pilot 16 must not modify:

- Pilot 14 runtime/tests/adjudication;
- Pilot 15 runtime/tests/adjudication;
- frozen EXP-N Pilot 8/9 provider paths.

No external LLM/provider call is required.

## Frozen limitations

Even a full Pilot 16 pass will not prove:

- physical power-loss durability;
- filesystem/drive-cache/barrier guarantees;
- SQLite correctness under every platform and failure mode;
- multi-host database correctness;
- distributed consensus correctness;
- Byzantine storage/admin resistance;
- arbitrary external-side-effect exactly-once semantics;
- cloud durability SLAs;
- formal serializability or linearizability beyond the exact exercised operations.

Allowed conclusion is limited to the exact SQLite/WAL subprocess-termination and reopen paths exercised by this pilot.
