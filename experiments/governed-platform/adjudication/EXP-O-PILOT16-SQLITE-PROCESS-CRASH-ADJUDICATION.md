# EXP-O Pilot 16 — SQLite WAL / Subprocess Crash Recovery Adjudication

Status: **ADJUDICATED — PASS WITH BOUNDED SQLITE/WAL SUBPROCESS-TERMINATION CLAIM**

A green workflow conclusion is not the scientific verdict. This adjudication is based on the preregistered Pilot 16 boundary, the exact twenty frozen falsifiers, and direct inspection of the first scientific-run job log.

## Frozen lineage

Preregistration:

`experiments/governed-platform/adjudication/EXP-O-PILOT16-SQLITE-PROCESS-CRASH-PREREGISTRATION.md`

Preregistration commit:

`9460c0ee3dd29dcad6ad15783d89ac27fc12879c`

Parent Pilot 15 adjudication commit:

`79ce2b6aaa57cb5f6bec2f69383c2e429f583b5d`

Isolated Pilot 16 implementation:

`experiments/governed-platform/governance/sqlite_process_crash_exp_o.py`

Implementation commit:

`a9b8920e1477b62c898363e4b6fcfbd19e05730d`

Frozen twenty-case suite:

`experiments/governed-platform/governance/test_exp_o_pilot16_sqlite_process_crash.py`

First-execution / frozen-case SHA:

`0b4509f4fbd50616c9e6018ef4baaed5116c8620`

No Pilot 16 test was removed, renamed, weakened, or changed after observing the first scientific execution.

## Tested boundary

The exact exercised boundary uses:

- a parent test process;
- a distinct Python worker subprocess for authority/effect transitions;
- SQLite in WAL mode;
- `PRAGMA synchronous=FULL`;
- explicit transactions;
- process termination via `os._exit(75)` inside the distinct worker at the registered transaction cuts;
- fresh database reopen after termination;
- normalized authority/effect/meta relational state;
- exact semantic/effect/idempotency binding;
- independent parent-retained higher-fence anchor for the stale database substitution falsifier;
- no model-issued authority and no external LLM/provider call.

The subprocess terminates abruptly without transaction cleanup at the registered cut. This is stronger than a same-process early return, but it is not a physical machine power-loss test and is not equivalent to every possible external SIGKILL/kernel/filesystem failure mode.

## Frozen termination points exercised

All ten preregistered points were present before first execution:

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

## First scientific execution

GitHub Actions workflow run:

`34024611872`

Job:

`101463246171`

The job log explicitly checked out:

`0b4509f4fbd50616c9e6018ef4baaed5116c8620`

Observed Pilot 16 results:

- P16-01 clean committed authority survives fresh reopen — PASS
- P16-02 terminate after BEGIN before authority insert — PASS
- P16-03 terminate after authority insert before COMMIT — PASS
- P16-04 terminate after authority COMMIT before acknowledgement — PASS
- P16-05 stale lower authority cannot overwrite committed higher fence — PASS
- P16-06 terminate after takeover insert before COMMIT — PASS
- P16-07 terminate after takeover COMMIT before acknowledgement — PASS
- P16-08 stale database substitution below independent higher anchor — PASS
- P16-09 authority binding corruption — PASS
- P16-10 duplicate active authority rows for same logical identity — PASS
- P16-11 terminate after effect insert before COMMIT — PASS
- P16-12 terminate after effect COMMIT before evidence update — PASS
- P16-13 terminate after evidence update before COMMIT — PASS
- P16-14 durable effect row dominates stale active authority — PASS
- P16-15 terminate after consumed update before COMMIT — PASS
- P16-16 terminate after consumed COMMIT before acknowledgement — PASS
- P16-17 idempotency-key rebinding after restart — PASS
- P16-18 consumed state references missing effect row — PASS
- P16-19 repeated WAL/reopen clean replay — PASS
- P16-20 fresh clean authority/effect after isolated crash cases — PASS

Regression totals from the same job:

- scorer: 36/36
- runner: 51/51
- protected truth: 4/4
- observability: 7/7
- continuation authority: 12/12
- governance/falsification: 573/573
- total: **683/683**

There was no first-run Pilot 16 failure and therefore no post-result repair lineage.

## Independent endpoint adjudication

### Uncommitted authority resurrection

**PASS on tested paths.**

Termination after transaction BEGIN or after authority insertion but before COMMIT did not produce recoverable effective authority. SQLite rollback/reopen behavior on the tested CI runtime preserved the registered expectation.

Observed tested noncommitted-authority resurrection events: **0**.

### Committed authority / takeover survival

**PASS on tested paths.**

Authority and higher takeover state committed before acknowledgement survived the fresh reopen. Lost caller acknowledgement therefore did not cause the implementation to pretend the commit had not occurred. Conversely, an uncommitted takeover did not replace the prior committed owner.

### Monotonic fence / stale substitution resistance

**PASS on tested paths.**

A lower authority proposal could not overwrite the committed higher active fence. When a lower database image was substituted after an independently retained higher fence anchor, recovery failed closed with stale rollback blocked rather than reviving the lower owner.

Observed tested stale-fence rollback events: **0**.

### Relational ambiguity and corruption

**PASS on tested paths.**

Incomplete authority binding, duplicate active authority identity, and consumed state referencing a missing effect identity were not promoted into consequential authority. Recovery failed closed or required reconciliation.

Observed silent relational-ambiguity promotions: **0**.

### Exactly-once effect recovery

**PASS on tested paths.**

- An effect insert terminated before COMMIT did not survive, so a later valid retry executed once.
- An effect committed before authority-evidence update survived and dominated the stale ACTIVE authority row.
- A rolled-back evidence/status update did not erase the already committed effect identity.
- A rolled-back consumed transition did not permit a second effect because the effect row remained authoritative for idempotency.
- A committed consumed transition survived acknowledgement loss.
- Same idempotency key plus a different effect digest was denied after restart.
- Repeated fresh opens returned the original result identity without inserting another effect row.

Observed duplicate durable effects for one tested logical intent: **0**.

### Clean restart liveness

**PASS on tested controls.**

A clean committed authority remained recoverable after fresh reopen. A clean authority/effect/consume sequence also remained exactly-once and replayable by original result identity.

## Scientific result

**Result:**

`NO_TESTED_SQLITE_WAL_SUBPROCESS_TERMINATION_OR_REOPEN_PATH_RESURRECTED_UNCOMMITTED_AUTHORITY_ROLLED_BACK_ANCHORED_FENCE_OR_DUPLICATED_EFFECT`

Within the exact CI-hosted SQLite/WAL Pilot 16 prototype, the twenty preregistered termination, corruption, stale-substitution, and replay cases did not manufacture consequential authority from uncommitted state, roll back an independently anchored higher fence, silently promote relational ambiguity, or produce a second durable effect for the same idempotency identity. Clean committed controls remained live.

## Important limitations

This result does **not** establish production power-loss safety or general database correctness.

It does not prove:

- physical machine or storage-device power-loss durability;
- drive/controller volatile-cache behavior;
- filesystem barrier or directory-entry durability;
- every SQLite WAL/checkpoint/recovery interleaving;
- arbitrary external `SIGKILL` timing outside the exact registered worker cuts;
- kernel panic, VM reset, container-runtime failure, disk-full, ENOSPC, EIO, bit rot, or torn-sector behavior;
- SQLite correctness on every OS/filesystem/build;
- multi-host consensus or distributed transaction correctness;
- Byzantine storage/admin resistance;
- exactly-once semantics for arbitrary external non-idempotent services;
- formal serializability or linearizability beyond the exact exercised operations.

`PRAGMA synchronous=FULL` and a successful CI execution are not substitutes for physical crash/power-loss testing.

## Next distinct boundary

A useful next falsification boundary is external parent-controlled process death rather than child self-termination: a worker should signal that it has reached an exact transaction state, block, and then be killed by the parent with an OS signal before database reopen. That can test whether conclusions survive a less cooperative process-death mechanism while retaining deterministic cut-point coordination. A later boundary can separately target filesystem/storage fault injection; those claims must remain distinct.
