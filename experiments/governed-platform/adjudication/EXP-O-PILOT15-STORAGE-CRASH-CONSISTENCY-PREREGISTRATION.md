# EXP-O Pilot 15 — Storage Crash Consistency / Durable Authority Preregistration

Status: **PRE-REGISTERED BEFORE PILOT 15 IMPLEMENTATION OR TEST EXECUTION**

Parent evidence boundary:

`experiments/governed-platform/adjudication/EXP-O-PILOT14-PROCESS-NETWORK-QUORUM-ADJUDICATION.md`

Parent adjudication commit:

`c58e3bf9d63ca54b50532fd2b58c49280e8c599a`

## Motivation

Pilot 14 showed a bounded result for three independent replica processes, authenticated loopback HTTP, quorum use-time revalidation, lease/term fencing, restart, repair, and an exercised SQLite exactly-once effect boundary. It explicitly did **not** test power-loss durability, torn writes, partially durable multi-record transitions, fsync ordering, or corruption of persisted authority/effect evidence.

Pilot 15 tests that missing storage boundary.

The target is not to prove SQLite, filesystems, or hardware correct. The target is to falsify a narrower platform invariant:

> A crash, partial durability event, torn/corrupt persisted record, or restart at any registered authority/effect transition must never revive stale consequential authority, create a second effect for one logical intent, or promote an ambiguous partially durable transition to authoritative success. Recovery may fail closed or require reconciliation; it may not guess authority.

## Scientific hypothesis

For the frozen Pilot 15 crash points and corruption cases, durable recovery will satisfy all of the following:

1. no partially durable authority transition becomes effective authority after restart;
2. no stale pre-takeover owner/epoch revives after a later durable fence;
3. no logical idempotency intent produces more than one durable consequential effect;
4. an effect that may have committed but whose authority/result evidence is incomplete is recovered as ambiguous/reconciliation-required or as the original effect identity, never as permission to execute again blindly;
5. corrupted or checksum-invalid authority/effect records fail closed rather than being interpreted as valid state;
6. durable sequence/term/epoch/index state never rolls backward to a lower valid-looking snapshot solely because the newer record is damaged or missing;
7. a fully durable clean control remains recoverable and live.

## Frozen architecture under test

Pilot 15 will use a new isolated EXP-O durability prototype rather than modifying Pilot 14's adjudicated runtime.

Frozen components:

- one authority-recovery coordinator process;
- one deterministic storage directory representing the local durable authority/effect boundary;
- append-only framed journal records with:
  - monotonically increasing sequence number;
  - record type;
  - canonical payload;
  - previous-record digest;
  - record digest/checksum;
- explicit durable checkpoint/manifest containing the highest fully committed sequence and digest;
- idempotency key bound to exact effect digest;
- lease owner + lease epoch + authority term/index retained in durable records;
- effect identity recorded independently from model output;
- recovery scans and validates the durable prefix before reconstructing authority state;
- no model-visible input and no model-issued authority.

Pilot 15 is an isolated falsification harness. It is not a replacement filesystem, database, Raft log, or production write-ahead log.

## Frozen durability model

The test harness may inject a crash or storage fault only at preregistered named cut points.

The durability model distinguishes:

- **written**: bytes/record are present in the process-visible file;
- **durable**: the prototype has completed its registered flush/fsync boundary for that record or checkpoint;
- **committed authority state**: recovery may use the state only when all required durable records and integrity bindings are present;
- **effect committed**: the deterministic effect sink contains the original idempotency/effect identity;
- **ambiguous**: effect or authority ordering cannot be proven after restart and therefore requires reconciliation/fail-closed handling.

The harness may simulate loss of the non-durable tail after a crash. It may not silently mark non-durable bytes as durable to make a test pass.

## Frozen crash points

The implementation must expose these named crash points before tests execute:

- `AFTER_AUTHORITY_RECORD_WRITE_BEFORE_FSYNC`
- `AFTER_AUTHORITY_RECORD_FSYNC_BEFORE_CHECKPOINT`
- `AFTER_CHECKPOINT_WRITE_BEFORE_FSYNC`
- `AFTER_EFFECT_COMMIT_BEFORE_EFFECT_EVIDENCE_WRITE`
- `AFTER_EFFECT_EVIDENCE_WRITE_BEFORE_FSYNC`
- `AFTER_EFFECT_EVIDENCE_FSYNC_BEFORE_AUTHORITY_CONSUMED`
- `AFTER_AUTHORITY_CONSUMED_WRITE_BEFORE_FSYNC`
- `AFTER_AUTHORITY_CONSUMED_FSYNC_BEFORE_CHECKPOINT`
- `AFTER_TAKEOVER_FENCE_WRITE_BEFORE_FSYNC`
- `AFTER_TAKEOVER_FENCE_FSYNC_BEFORE_CHECKPOINT`

A crash injection must terminate/reopen from persisted bytes; the test may not repair in-memory state before recovery.

## Frozen corruption / truncation cases

The suite must also exercise:

- torn final journal frame;
- valid JSON/canonical payload with invalid record digest;
- valid record digest but broken previous-digest chain;
- checkpoint pointing beyond the validated journal prefix;
- checkpoint digest not matching its referenced record;
- duplicated sequence number with different content;
- lower-sequence stale journal/checkpoint pair substituted after a higher durable fence has been independently anchored in the test fixture;
- effect-ledger row with mismatched idempotency/effect digest;
- authority-consumed record whose referenced effect identity is missing;
- effect identity present while authority-consumed record is missing.

## Frozen recovery rule

Recovery must reconstruct state from the **highest integrity-valid durable prefix** consistent with the durable checkpoint/anchor and effect ledger.

It must fail closed when a unique authoritative state cannot be established.

Specifically forbidden recovery shortcuts:

- trust the last parseable JSON record merely because it parses;
- ignore a checksum or chain mismatch and continue from later records;
- use wall-clock freshness to select between conflicting durable states;
- recreate or widen authority from model output;
- execute an effect a second time because the prior response/result record is missing;
- roll back a durable takeover/epoch fence to an older owner solely to regain liveness;
- treat an ambiguous effect outcome as a clean failure that authorizes a new effect;
- repair corruption by mutating the journal during the initial recovery decision.

## Frozen exactly-once rule

The logical key is `(idempotency_key, effect_digest)`.

For one idempotency key:

- the same effect digest may reconcile to the original durable result identity;
- a different effect digest must be denied as rebinding;
- crash recovery must never create a second durable effect row for the same logical intent;
- absence of post-effect authority evidence does not by itself imply the effect did not occur.

## Frozen authority rule

Effective consequential authority after restart requires:

- integrity-valid durable authority lineage;
- current non-stale term/index/lease epoch;
- exact semantic/effect/idempotency bindings;
- no unresolved higher durable fence;
- no corruption/ambiguity affecting the required lineage;
- explicit use-time revalidation in the recovered state machine before any new effect.

A model, caller, or stale local object cannot mint authority during recovery.

## Pre-registered falsifiers

The implementation/test suite must contain exactly the following primary Pilot 15 cases before first execution.

### P15-01 — clean durable authority control

A fully fsynced authority acquisition plus checkpoint survives restart with exact term/index/owner/epoch/bindings.

Expected: authoritative recovery succeeds.

### P15-02 — authority write lost before fsync

Crash after authority record write but before fsync; simulated power loss removes the non-durable tail.

Expected: the uncommitted authority transition is absent after recovery and cannot authorize use.

### P15-03 — authority fsynced but checkpoint not advanced

Crash after authority record fsync but before durable checkpoint advancement.

Expected: recovery does not silently promote the uncheckpointed transition to consequential authority; it is either reconciled by an explicit registered rule or fails closed.

### P15-04 — torn final authority frame

Final journal frame is truncated/torn.

Expected: torn frame is rejected; later authority cannot be invented from partial bytes.

### P15-05 — checksum-valid syntax is insufficient

The final record remains parseable but its record digest/checksum is invalid.

Expected: record rejected, no authority from it.

### P15-06 — broken digest chain

A later record is individually parseable/checksummed but its previous-record digest does not bind to the validated prefix.

Expected: chain break fails closed at that boundary.

### P15-07 — checkpoint beyond validated prefix

Checkpoint claims a sequence greater than the integrity-valid journal prefix.

Expected: recovery rejects checkpoint/state promotion.

### P15-08 — checkpoint digest mismatch

Checkpoint sequence exists but referenced digest differs.

Expected: fail closed; no authoritative state from the mismatched checkpoint.

### P15-09 — duplicate sequence with conflicting content

Two durable-looking records claim the same sequence with different payload/digest.

Expected: ambiguity/corruption is detected; neither conflict is chosen by convenience.

### P15-10 — stale snapshot substitution after durable fence

A lower-term/lower-epoch journal/checkpoint pair is substituted after the test has independently retained evidence of a higher durable takeover fence.

Expected: stale authority cannot revive; recovery fails closed rather than rolling back the fence.

### P15-11 — takeover fence write lost before fsync

Crash after takeover-fence write but before fsync and simulate non-durable-tail loss.

Expected: non-durable new owner is not authoritative; recovery cannot fabricate the takeover.

### P15-12 — durable takeover fence before checkpoint

Takeover-fence record is durable but checkpoint advancement is not.

Expected: old owner must not regain consequential authority merely because checkpoint lags; recovery must preserve or explicitly reconcile the durable higher fence without stale-owner execution.

### P15-13 — effect commits before evidence write

Effect sink commits, then process crashes before effect-evidence record is written.

Expected: restart detects effect-side evidence for the idempotency key; it must not execute again blindly. Outcome is reconciliation/original-result recovery, not duplicate execution.

### P15-14 — effect evidence written but not durable

Effect commits; effect-evidence journal record is written but crashes before fsync; simulated tail loss removes that evidence.

Expected: effect sink still prevents duplicate execution; recovery remains reconciliation-safe.

### P15-15 — durable effect evidence before consumed authority

Effect and its evidence are durable, but authority-consumed record is absent due crash.

Expected: retry/recovery converges to the original result identity without a second effect.

### P15-16 — consumed record written but not durable

Authority-consumed record is written after effect evidence but lost before fsync.

Expected: durable effect identity still prevents duplicate effect and recovery does not reopen fresh authority.

### P15-17 — consumed record durable before checkpoint

Consumed authority state is fsynced but checkpoint lags.

Expected: the effect cannot be executed again; stale pre-consumed authority must not revive.

### P15-18 — effect-ledger idempotency rebinding corruption

Persisted effect identity for the same idempotency key is presented with a different effect digest.

Expected: rebinding denied/fail closed; no second effect.

### P15-19 — consumed record references missing effect identity

Authority lineage claims consumed/result identity but the referenced effect-side record is missing.

Expected: inconsistency is not reported as clean success; reconciliation or human/operator repair is required and no new effect is authorized.

### P15-20 — clean restart after all fault cases

A fresh fully durable authority/effect sequence after prior isolated fault tests restarts successfully and returns the original effect identity exactly once.

Expected: positive liveness control passes without weakening any fail-closed rule.

## Primary endpoints

1. **authority resurrection rate** — any case where stale, non-durable, corrupt, or ambiguous state yields effective consequential authority;
2. **duplicate durable effect rate** — any logical intent producing more than one durable effect identity;
3. **silent ambiguity promotion rate** — any incomplete/corrupt persistence state reported as authoritative clean success without the required lineage;
4. **monotonic fence preservation** — higher durable term/index/epoch fences are never silently rolled back;
5. **clean recovery liveness** — fully durable valid controls remain usable.

Any non-zero authority resurrection or duplicate-effect event is a Pilot 15 falsification for that path.

## Evidence policy

- All 20 preregistered primary cases must execute in the first scientific run.
- All valid first-run failures are retained.
- A failing test may be classified as implementation defect, test defect, or environment/tooling defect only after inspecting the exact persisted bytes/state and expected invariant.
- Green CI is operational evidence only.
- No failed case may be removed, renamed, weakened, or converted to a positive result after execution.
- Any repair after first execution requires explicit recorded diagnosis and rerun lineage.

## Isolation

Pilot 15 must not modify the adjudicated Pilot 14 runtime or tests.

Pilot 15 must not modify or trigger EXP-N Pilot 8/9 frozen provider paths.

No external LLM/provider call is required for Pilot 15.

## Production limitations frozen in advance

Even a complete Pilot 15 pass will not prove:

- actual hardware power-loss semantics;
- drive write-cache/barrier correctness;
- filesystem-specific fsync guarantees;
- SQLite or another production database's complete crash consistency;
- multi-host consensus correctness;
- Byzantine storage or malicious administrator resistance;
- kernel or hypervisor correctness;
- atomic sector-write assumptions across all storage devices;
- distributed transactions across real services;
- cloud-provider durability SLAs;
- formal exactly-once semantics for arbitrary external side effects.

Allowed conclusion after a complete pass is limited to the deterministic crash/corruption model and exact storage prototype exercised here.
