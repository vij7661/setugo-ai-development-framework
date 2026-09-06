# EXP-O Pilot 18 — SQLite Storage-Fault / Corruption Recovery Preregistration

Status: **PRE-REGISTERED BEFORE PILOT 18 IMPLEMENTATION OR TEST EXECUTION**

Parent evidence:

`experiments/governed-platform/adjudication/EXP-O-PILOT17-PARENT-SIGKILL-SQLITE-ADJUDICATION.md`

Parent adjudication commit:

`34373ce43f7321367cab9b2627013d5451c71d5a`

## Motivation

Pilot 17 strengthened the process-death boundary by using a parent-issued OS SIGKILL after a distinct SQLite worker had reached an exact transaction state. The remaining untested boundary is software-visible storage failure or corruption itself.

Pilot 18 therefore targets bounded SQLite/database storage-fault behavior. It must not be represented as physical hardware-failure or power-loss proof.

## Scientific hypothesis

Across the frozen software-level storage-fault cases:

1. an explicit SQLite database-full/write failure cannot be promoted into committed consequential authority or an assumed effect;
2. corrupted or truncated database/WAL state cannot be silently repaired into effective authority when integrity cannot be established;
3. a missing or stale WAL/database combination cannot roll authority below an independently retained higher fence;
4. an unreadable or inconsistent effect ledger cannot permit duplicate execution by treating missing evidence as absence of prior effect;
5. recovery errors remain fail-closed and distinguish corruption/uncertainty from clean absence;
6. clean copies remain recoverable and live after the isolated fault cases.

Any tested fault that causes stale authority resurrection, anchored rollback, duplicate durable effect, or silent corruption promotion falsifies Pilot 18 on that path.

## Frozen architecture under test

Pilot 18 must use new isolated files and must not modify Pilots 14–17.

Required components:

- SQLite database in WAL mode with `PRAGMA synchronous=FULL` for clean controls;
- authority, effect, and monotonic metadata/fence state with exact semantic/effect/idempotency binding;
- recovery entrypoint that runs an integrity assessment before consequential authority is returned;
- independent higher-fence anchor stored outside the database for rollback tests;
- isolated per-case database copies so deliberate corruption cannot contaminate other cases;
- software-level fault injection only;
- no model-visible input, no provider call, and no model-issued authority.

## Frozen fault classes

Before first execution the implementation must support bounded deterministic injection for these classes:

- `DATABASE_FULL`
- `MAIN_DATABASE_TRUNCATION`
- `MAIN_DATABASE_BYTE_CORRUPTION`
- `WAL_TRUNCATION`
- `WAL_BYTE_CORRUPTION`
- `WAL_REMOVAL_OR_STALE_PAIR`
- `DATABASE_SUBSTITUTION_BELOW_ANCHOR`
- `EFFECT_STATE_CORRUPTION`
- `RELATIONAL_INCONSISTENCY`

The exact mechanism may use SQLite-supported limits (for example `max_page_count`) and direct byte mutation/truncation on disposable copies, but the tests must assert that the fault was actually induced. A no-op mutation does not count as evidence.

## Recovery rules

Recovery may return effective consequential authority only when:

- SQLite can open the relevant state;
- the integrity check is clean enough for the tested policy;
- relational invariants are satisfied;
- active authority is unique;
- semantic/effect/idempotency bindings are complete;
- observed monotonic fence is not below the independent anchor;
- effect/idempotency state is trustworthy and does not show prior execution;
- no unresolved storage error or corruption remains.

Storage uncertainty must never be translated into positive authority for liveness.

If integrity cannot be established, expected posture is fail closed / reconciliation or storage-recovery required, with no consequential execution.

## Pre-registered primary falsifiers

Exactly these twenty primary cases must exist before first scientific execution.

### P18-01 — clean database control
Expected: clean committed authority is recoverable and exact bindings are preserved.

### P18-02 — database-full during authority write
Expected: write/commit failure is observable; no new authority row is treated as committed.

### P18-03 — database-full during higher takeover
Expected: failed takeover cannot displace the previously committed owner/fence.

### P18-04 — database-full during effect insert
Expected: failed effect commit cannot be reported as executed; later valid retry may execute once if authority remains valid.

### P18-05 — main database header/page corruption
Expected: integrity/open failure is fail-closed; no authority inferred from partially readable content.

### P18-06 — main database truncation
Expected: truncation is detected or database becomes unreadable; no effective authority returned.

### P18-07 — corruption of an authority-bearing database page
Expected: recovery does not choose a surviving-looking authority row unless database integrity is established.

### P18-08 — corruption of monotonic metadata/fence state
Expected: inconsistent fence metadata fails closed and cannot lower the current authority epoch by convenience.

### P18-09 — stale lower database substituted below independent higher anchor
Expected: rollback is blocked even if the substituted database is internally valid.

### P18-10 — WAL removed while higher state exists only in WAL
Expected: recovery must not claim the lower database image is authoritative when an independent anchor proves a higher committed fence.

### P18-11 — WAL truncation on isolated copy
Expected: recovery either reconstructs an integrity-consistent committed prefix that satisfies the anchor or fails closed; it must not manufacture stale authority.

### P18-12 — WAL byte corruption on isolated copy
Expected: corruption/error is surfaced and no stale authority or duplicate effect is authorized.

### P18-13 — stale main database paired with newer unrelated WAL
Expected: invalid/mismatched pair cannot be promoted into authority.

### P18-14 — effect-row corruption after committed effect
Expected: uncertainty about prior effect does not authorize blind re-execution.

### P18-15 — effect row deleted while consumed/result state still references it
Expected: inconsistency requires reconciliation/fails closed; no fresh effect authority inferred.

### P18-16 — idempotency key paired with corrupted/different effect digest
Expected: rebinding is denied; no second effect.

### P18-17 — duplicate active authority after storage mutation
Expected: ambiguity fails closed.

### P18-18 — integrity-check failure itself is not classified as clean absence
Expected: recovery status explicitly distinguishes storage corruption/error from `NO_ACTIVE_AUTHORITY`.

### P18-19 — repeated reopen of corrupted copy remains fail-closed
Expected: repeated recovery attempts do not eventually promote the corrupted state to authority.

### P18-20 — fresh clean liveness control after isolated faults
Expected: a new uncorrupted database performs authority/effect/consume exactly once, proving fault handling is not globally disabling the clean path.

## Primary endpoints

1. storage-fault-induced authority resurrection rate;
2. anchored rollback rate;
3. duplicate durable effect rate;
4. silent corruption-as-clean promotion rate;
5. clean recovery liveness.

Any non-zero stale-authority resurrection, anchored rollback, or duplicate effect is a falsification on the exact exercised path.

## Evidence policy

- all 20 cases execute in the first scientific run;
- each mutation/fault case must prove the mutation/fault occurred;
- all corruption operates on disposable isolated case copies;
- first-run failures are retained exactly;
- diagnosis must inspect SQLite error/integrity result and persisted rows/files before repair;
- no failing case may be removed, renamed, weakened, or silently converted after execution;
- any post-result repair requires a recorded diagnosis and rerun lineage;
- workflow SUCCESS remains operational evidence only.

## Isolation

Pilot 18 must not modify:

- Pilot 14 runtime/tests/adjudication;
- Pilot 15 runtime/tests/adjudication;
- Pilot 16 runtime/tests/adjudication;
- Pilot 17 runtime/tests/adjudication;
- frozen EXP-N Pilot 8/9 provider paths.

## Frozen limitations

Even a complete Pilot 18 pass will not prove:

- physical drive failure or real power-loss durability;
- controller/cache/barrier correctness;
- sector atomicity;
- kernel panic or host/VM failure;
- every SQLite corruption pattern or WAL recovery interleaving;
- SQLite correctness on every OS/filesystem/build;
- multi-host database or distributed transaction correctness;
- Byzantine storage/admin resistance;
- exactly-once semantics for arbitrary remote non-idempotent services;
- formal serializability/linearizability outside the exact tested operations.

Allowed conclusions must remain limited to the exact software-level SQLite failure/corruption injections exercised by this pilot.
