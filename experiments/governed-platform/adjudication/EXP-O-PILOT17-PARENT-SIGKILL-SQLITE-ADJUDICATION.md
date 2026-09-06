# EXP-O Pilot 17 — Parent-Controlled SIGKILL / SQLite Recovery Adjudication

Status: **ADJUDICATED — PASS WITH BOUNDED PARENT-SIGKILL / SQLITE REOPEN CLAIM**

A green workflow conclusion is not itself the scientific verdict. This adjudication is based on the preregistered Pilot 17 boundary, the exact eighteen frozen falsifiers, and direct inspection of the first scientific-run job log.

## Frozen lineage

Preregistration:

`experiments/governed-platform/adjudication/EXP-O-PILOT17-PARENT-SIGKILL-SQLITE-PREREGISTRATION.md`

Preregistration commit:

`15701c421dcf29de2d1329621d13e27038510b32`

Parent Pilot 16 adjudication commit:

`836ae4a799eb79f65887b12bc905e4804bc9c01b`

Isolated Pilot 17 implementation:

`experiments/governed-platform/governance/sqlite_parent_sigkill_exp_o.py`

Implementation commit:

`4e78b32cec00f7497ce39f6577d0628584558757`

Frozen eighteen-case suite:

`experiments/governed-platform/governance/test_exp_o_pilot17_parent_sigkill_sqlite.py`

First-execution / frozen-case SHA:

`a84ed914bea1e089913874180387e42a9649995f`

No Pilot 17 test was removed, renamed, weakened, or changed after observing the first scientific execution.

## Tested process-death boundary

The exercised fault path is externally controlled by the parent test process:

1. a distinct Python worker subprocess opens the SQLite database in WAL mode with `PRAGMA synchronous=FULL`;
2. the worker reaches an exact registered transaction cut;
3. it emits a machine-readable readiness record containing the exact cut identity and its PID;
4. it remains alive and blocked in `signal.pause()`;
5. the parent verifies that the reported PID equals the actual `Popen` PID and that `poll()` is still `None`;
6. the parent calls `Popen.kill()`;
7. Linux CI reports child return code `-SIGKILL` (`-9`);
8. only after confirmed child death is SQLite reopened for recovery.

The readiness record is evidence of cut-point position only. It carries no authority and cannot authorize a database transition.

## Frozen externally killed cut points

All eight preregistered points were present before first execution:

- `READY_AFTER_BEGIN_BEFORE_AUTHORITY_INSERT`
- `READY_AFTER_AUTHORITY_INSERT_BEFORE_COMMIT`
- `READY_AFTER_AUTHORITY_COMMIT_BEFORE_ACK`
- `READY_AFTER_TAKEOVER_INSERT_BEFORE_COMMIT`
- `READY_AFTER_TAKEOVER_COMMIT_BEFORE_ACK`
- `READY_AFTER_EFFECT_INSERT_BEFORE_COMMIT`
- `READY_AFTER_EFFECT_COMMIT_BEFORE_EVIDENCE_UPDATE`
- `READY_AFTER_CONSUMED_UPDATE_BEFORE_COMMIT`

## First scientific execution

GitHub Actions workflow run:

`34024789626`

Job:

`101463730907`

The job log explicitly checked out:

`a84ed914bea1e089913874180387e42a9649995f`

Observed Pilot 17 results:

- P17-01 readiness protocol proves distinct externally killed worker — PASS
- P17-02 parent kill after BEGIN before authority insert — PASS
- P17-03 parent kill after authority insert before COMMIT — PASS
- P17-04 parent kill after authority COMMIT before acknowledgement — PASS
- P17-05 parent kill after takeover insert before COMMIT — PASS
- P17-06 parent kill after takeover COMMIT before acknowledgement — PASS
- P17-07 stale lower authority after killed committed takeover denied — PASS
- P17-08 stale database substitution below independent anchor blocked — PASS
- P17-09 parent kill after effect insert before COMMIT — PASS
- P17-10 parent kill after effect COMMIT before evidence/status update — PASS
- P17-11 repeated retry after post-effect kill returns same result — PASS
- P17-12 idempotency rebinding after post-effect kill denied — PASS
- P17-13 parent kill after consumed update before COMMIT — PASS
- P17-14 malformed active authority after restart fails closed — PASS
- P17-15 duplicate active-authority ambiguity fails closed — PASS
- P17-16 consumed state missing effect identity fails closed — PASS
- P17-17 repeated fresh reopen after parent kill remains stable — PASS
- P17-18 clean positive liveness control — PASS

Regression totals from the same job:

- scorer: 36/36
- runner: 51/51
- protected truth: 4/4
- observability: 7/7
- continuation authority: 12/12
- governance/falsification: 591/591
- total: **701/701**

There was no first-run Pilot 17 failure and therefore no post-result repair lineage.

## Independent endpoint adjudication

### External-kill authenticity

**PASS on tested path.**

The fault mechanism is not a cooperative worker self-exit. The parent observed the exact readiness record, confirmed the worker was still alive, delivered the kill itself, and observed signal termination. This closes the specific process-death limitation retained from Pilot 16.

### Uncommitted authority resurrection

**PASS on tested paths.**

A parent SIGKILL before the authority insert or after the insert but before COMMIT did not create recoverable effective authority after reopen.

Observed externally killed uncommitted-authority resurrection events: **0**.

### Committed authority / takeover survival

**PASS on tested paths.**

Authority and higher takeover state committed before the parent kill survived fresh reopen even though acknowledgement was never returned. Conversely, a takeover killed before COMMIT did not replace the prior committed owner.

### Monotonic fence / stale rollback resistance

**PASS on tested paths.**

A stale lower authority proposal following a killed-but-committed higher takeover remained denied. A substituted lower database image below an independently retained higher fence anchor failed closed rather than reviving the lower owner.

Observed tested anchored rollback events: **0**.

### Exactly-once effect recovery

**PASS on tested paths.**

- An effect insert killed before COMMIT did not survive and a later valid retry executed once.
- An effect committed before the parent kill survived and dominated stale ACTIVE authority state.
- Repeated retries after the post-effect kill returned one stable original result identity.
- The durable effect-row count remained one for the tested logical intent.
- A different effect digest under the same idempotency key was denied after restart.
- A consumed-state update killed before COMMIT rolled back, but the durable effect still prevented duplicate execution.

Observed duplicate durable effects for one tested logical intent: **0**.

Observed accepted idempotency-key rebinding events: **0**.

### Relational ambiguity / corruption

**PASS on tested paths.**

Incomplete active-authority binding, duplicate active-authority ambiguity, and consumed state referencing a missing effect identity all failed closed or required reconciliation. Recovery did not invent authority to repair these states.

### Clean restart liveness

**PASS on tested controls.**

Repeated fresh reopens after a parent-killed post-effect state returned a stable original result identity. A separate clean authority/effect/consume sequence remained live and exactly-once.

## Scientific result

**Result:**

`NO_TESTED_PARENT_SIGKILL_SQLITE_REOPEN_PATH_RESURRECTED_UNCOMMITTED_AUTHORITY_ROLLED_BACK_ANCHORED_FENCE_OR_DUPLICATED_EFFECT`

Within the exact Linux CI / SQLite WAL Pilot 17 prototype, externally killing a blocked worker at the preregistered transaction cuts did not manufacture effective authority from uncommitted state, erase committed higher authority in favor of a stale owner, roll back an independently anchored higher fence, silently promote malformed relational state, accept idempotency rebinding, or create a second durable effect for the same tested logical intent. Clean committed controls remained live.

## Important limitations

This result does **not** establish physical power-loss safety or general SQLite/database correctness.

It does not prove:

- real machine power loss;
- kernel panic, VM reset, container-runtime failure, or host loss;
- drive/controller volatile-cache behavior;
- filesystem barriers, directory-entry durability, or torn-sector semantics;
- arbitrary asynchronous kill timing outside the exact coordinated readiness cuts;
- every SQLite WAL/checkpoint/recovery interleaving;
- disk-full, ENOSPC, EIO, bit rot, WAL corruption, or database corruption behavior;
- SQLite correctness on every OS/filesystem/build;
- multi-host consensus or distributed transaction correctness;
- exactly-once semantics for arbitrary remote non-idempotent effects;
- Byzantine storage/admin resistance;
- formal serializability or linearizability beyond the exact exercised operations.

`Popen.kill()` on the Ubuntu Actions runner is a useful externally controlled process-death falsifier; it is not a substitute for storage fault or physical power-loss testing.

## Next distinct boundary

The next useful falsification step should move from process death to **software-level storage failure/corruption injection** rather than add more equivalent SIGKILL cuts. Candidate Pilot 18 scope: bounded SQLite storage-fault behavior including database-full conditions, WAL/database corruption or truncation on isolated copies, checkpoint/reopen failures, stale-file combinations, and explicit fail-closed handling when recovery cannot establish a trustworthy committed prefix. These must remain software fault-injection claims and must not be represented as physical drive-failure proof.
