# EXP-O Pilot 17 — Parent-Controlled SIGKILL / SQLite Recovery Preregistration

Status: **PRE-REGISTERED BEFORE PILOT 17 IMPLEMENTATION OR TEST EXECUTION**

Parent evidence:

`experiments/governed-platform/adjudication/EXP-O-PILOT16-SQLITE-PROCESS-CRASH-ADJUDICATION.md`

Parent adjudication commit:

`836ae4a799eb79f65887b12bc905e4804bc9c01b`

## Motivation

Pilot 16 used a real distinct worker subprocess and SQLite WAL/FULL transactions, but the worker itself called `os._exit()` at the registered cut. Pilot 17 removes that cooperative termination mechanism.

The worker must instead:

1. reach a registered transaction state;
2. emit a machine-readable readiness marker to the parent through a pipe/stdout;
3. block without committing any additional transition;
4. be terminated externally by the parent with `SIGKILL` / `Popen.kill()`;
5. have the database reopened by a fresh connection/process after confirmed death.

This isolates a stronger process-death boundary while still not claiming physical power-loss semantics.

## Scientific hypothesis

Across the frozen parent-kill cases:

- externally killing a worker before SQLite COMMIT cannot create recoverable effective authority or takeover state;
- killing after COMMIT but before acknowledgement cannot erase committed authority, takeover, effect, or consumed state;
- a committed effect remains the authoritative idempotency fact even if the worker is killed before evidence/status updates;
- parent-controlled kill/restart cannot rebind an idempotency key to a different effect digest;
- stale lower database substitution remains blocked by an independently retained higher fence;
- clean operations remain live after parent-kill fault cases.

Any stale/uncommitted authority resurrection, anchored-fence rollback, or duplicate durable effect falsifies Pilot 17 on that path.

## Frozen runtime boundary

Pilot 17 must be implemented in new isolated files and must not modify Pilots 14–16.

Required runtime characteristics:

- Python parent controller/test process;
- distinct Python SQLite worker subprocess;
- SQLite WAL mode;
- `PRAGMA synchronous=FULL`;
- explicit transactions;
- readiness marker emitted only after the named cut state has actually been reached;
- worker blocks after readiness marker;
- parent waits for exact readiness marker, then calls OS process kill (`Popen.kill()` or equivalent SIGKILL behavior on Linux CI);
- parent waits for child termination before reopen;
- fresh SQLite connection/process performs recovery;
- independent anchor file for stale-database rollback detection;
- exact semantic/effect/idempotency bindings;
- no LLM/provider call and no model-issued authority.

The readiness protocol itself is evidence only; it must not be accepted as authority.

## Frozen externally killed cut points

Exactly these eight coordinated parent-kill points must exist before first execution:

- `READY_AFTER_BEGIN_BEFORE_AUTHORITY_INSERT`
- `READY_AFTER_AUTHORITY_INSERT_BEFORE_COMMIT`
- `READY_AFTER_AUTHORITY_COMMIT_BEFORE_ACK`
- `READY_AFTER_TAKEOVER_INSERT_BEFORE_COMMIT`
- `READY_AFTER_TAKEOVER_COMMIT_BEFORE_ACK`
- `READY_AFTER_EFFECT_INSERT_BEFORE_COMMIT`
- `READY_AFTER_EFFECT_COMMIT_BEFORE_EVIDENCE_UPDATE`
- `READY_AFTER_CONSUMED_UPDATE_BEFORE_COMMIT`

A clean non-killed path must also exist for controls.

## Pre-registered primary falsifiers

Exactly these eighteen primary cases must be present before first scientific execution.

### P17-01 — readiness protocol proves distinct externally killed worker
Expected: parent observes exact marker, kills child, confirms non-zero signal termination; worker does not self-exit as the fault mechanism.

### P17-02 — kill after BEGIN before authority insert
Expected: no authority survives.

### P17-03 — kill after authority insert before COMMIT
Expected: insert rolls back; no effective authority survives.

### P17-04 — kill after authority COMMIT before acknowledgement
Expected: committed authority survives reopen with exact bindings.

### P17-05 — kill after takeover insert before COMMIT
Expected: old committed owner remains; uncommitted takeover is absent.

### P17-06 — kill after takeover COMMIT before acknowledgement
Expected: higher committed takeover survives; stale prior owner does not revive.

### P17-07 — stale lower authority proposal after killed committed takeover
Expected: lower term/index/epoch cannot overwrite the higher committed state.

### P17-08 — stale database substitution below independent higher anchor
Expected: recovery fails closed with rollback blocked.

### P17-09 — kill after effect insert before COMMIT
Expected: no durable effect; valid retry may execute exactly once.

### P17-10 — kill after effect COMMIT before evidence/status update
Expected: durable effect survives and prevents duplicate execution; original result identity is reconciled.

### P17-11 — repeated retry after post-effect kill
Expected: repeated retries return the same original result identity and effect-row count remains one.

### P17-12 — idempotency rebinding after post-effect kill
Expected: same key + different effect digest is denied.

### P17-13 — kill after consumed update before COMMIT
Expected: consumed update rolls back, but existing effect still prevents duplicate execution.

### P17-14 — malformed active authority after restart
Expected: incomplete binding fails closed.

### P17-15 — duplicate active authority ambiguity after restart
Expected: recovery fails closed rather than choosing one row.

### P17-16 — consumed state referencing missing effect identity
Expected: reconciliation required / deny; no fresh authority inferred.

### P17-17 — repeated fresh reopen after parent-kill faults
Expected: monotonic committed state/result identity remains stable across repeated opens.

### P17-18 — clean positive liveness control
Expected: a new clean authority/effect/consume sequence succeeds exactly once after isolated parent-kill fault tests.

## Primary endpoints

1. externally-killed uncommitted authority resurrection rate;
2. externally-killed committed-state loss/rollback rate;
3. duplicate durable effect rate;
4. idempotency rebinding acceptance rate;
5. clean restart liveness.

Any non-zero authority resurrection, anchored rollback, or duplicate effect is a falsification on that exercised path.

## Evidence rules

- all 18 cases execute in the first scientific run;
- exact readiness marker and child return code/termination must be asserted in kill cases;
- first-run failures are retained;
- no failing case may be removed, renamed, weakened, or silently converted;
- post-result repair requires recorded diagnosis first;
- green CI alone is not the scientific verdict.

## Isolation

Pilot 17 must not modify Pilot 14, Pilot 15, Pilot 16, or frozen EXP-N Pilot8/9 paths.

## Frozen limitations

A Pilot 17 pass will still not establish:

- real machine power-loss durability;
- kernel panic/VM reset behavior;
- disk controller/cache/barrier guarantees;
- torn-sector or bit-rot behavior;
- every SQLite WAL/checkpoint interleaving;
- multi-host database correctness;
- distributed consensus correctness;
- exactly-once semantics for arbitrary remote side effects;
- Byzantine storage/admin resistance;
- formal linearizability beyond the exact tested operations.

Allowed conclusions must remain limited to the exact parent-controlled process-kill and SQLite reopen paths exercised here.
