# EXP-O Pilot 22 — Witness Store Integrity / Rollback Adjudication

Status: **FINAL FOR THE TESTED PILOT 22 BOUNDARY AFTER RECORDED NARROW REPAIR**

## Frozen lineage

- Preregistration: `experiments/governed-platform/adjudication/EXP-O-PILOT22-WITNESS-STORE-INTEGRITY-ROLLBACK-PREREGISTRATION.md`
- Preregistration commit: `c14f941e5ffd7159983793a40a48b2c4bc582883`
- Parent Pilot 21 adjudication: `c5477e22570e69cde9c3eac5e1f1e47f088264fe`
- Initial Pilot 22 implementation commit: `6427dd48a5f11c33aa67e5dd84fbd9aced5f6efb`
- Frozen first-execution SHA: `79e0c7dfd651afebec327177a23f18de4e1e9b49`
- Frozen first run: `34026461198`
- Frozen first job: `101468186057`
- First-run failure diagnosis/repair record: `5dd0949da7aafb513562026f3d66756008258950`
- Corrupted-store startup repair: `5d428a063641cec035edc844cdc725dee5501081`
- Repaired full-suite SHA: `7fceb64c27996fcf28dcb0ea5a55f6fe50ceaaf8`
- Repaired run: `34026719661`
- Repaired job: `101468885355`

The first-run failures are retained below and are not rewritten as a first-run pass.

## Boundary tested

Pilot 22 tested whether an honest witness's durable anti-equivocation memory could be erased, rolled back, coherently rewritten, or made ambiguous by attacks on its SQLite signing store while still obtaining an authoritative witness signature or a conflicting 2-of-3 quorum.

The tested witness path required, before signing:

1. SQLite structural integrity;
2. application row/meta seals;
3. monotonic signing-history consistency;
4. an authenticated external witness-history checkpoint bound to witness id, key id, store identity, maximum signed generation, history root and checkpoint generation;
5. a separately supplied trusted minimum checkpoint generation.

No model output, provider response or model-visible authority participated in this pilot.

## First frozen execution — preserved failures

The first frozen run at `79e0c7dfd651afebec327177a23f18de4e1e9b49` did **not** pass all twenty cases.

Observed first-run outcomes:

- P22-01: PASS
- P22-02: ERROR
- P22-03: ERROR
- P22-04 through P22-17: PASS
- P22-18: FAIL
- P22-19: PASS
- P22-20: PASS

No first-run error/failure produced a witness signature, effective authority, or conflicting quorum.

### P22-02 / P22-03 diagnosis

Header corruption and truncation caused witness construction/startup to call schema initialization on an already damaged SQLite file. SQLite raised a database error before the witness could expose an explicit integrity-refusal response.

This was classified as an **implementation failure-mode defect**, not an authority false green: the path failed closed but did not satisfy the preregistered explicit refusal behavior.

The recorded repair changed only startup behavior:

- initialize schema only when the store does not already exist;
- never recreate/reset an existing damaged store;
- let the child process start and route the existing store through `verify_store()`;
- retain all signing, checkpoint, anti-equivocation, rollback and quorum rules unchanged.

### P22-18 diagnosis

The positive liveness case bootstrapped witnesses at generation 5 with a synthetic statement and then asked those same honest witnesses to sign a different statement at generation 5. The runtime correctly returned same-generation equivocation refusal.

This was classified as a **test-construction defect**: the positive control accidentally asked for behavior the scientific hypothesis expressly forbids.

The recorded repair changed only the liveness construction:

- retain bootstrap generation 5;
- request the current authority statement at generation 6;
- require the same two distinct honest witnesses and 2-of-3 quorum at generation 6.

No anti-equivocation rule or quorum threshold was weakened.

## Repaired execution evidence

At repaired SHA `7fceb64c27996fcf28dcb0ea5a55f6fe50ceaaf8`, workflow run `34026719661` completed successfully operationally.

The actual governance job log was inspected. It shows:

- P22-01 through P22-20: **20 / 20 PASS**;
- P22-02 and P22-03 now produce explicit fail-closed witness responses rather than constructor exceptions;
- P22-18 exercises a non-equivocating higher-generation two-honest-witness liveness path and passes;
- P22-19 proves the history-committed/checkpoint-not-yet-published state fails closed until the external checkpoint is reconciled;
- P22-20 proves higher-generation checkpoint/restart consumed-state recovery with exactly one durable effect.

Regression counts on the repaired run:

- scorer: 36
- runner: 51
- protected truth: 4
- observability: 7
- continuation: 12
- governance/falsification: **691**
- full harness: **801 / 801**

## Endpoint adjudication

Across the tested repaired paths:

- tested structurally corrupt witness stores signing successfully: **0**
- tested coherently rewritten/resealed stores bypassing external history-root binding: **0**
- tested stale store + old checkpoint rollback below trusted minimum: **0**
- tested same-generation conflict after rollback attempt signed by honest witness: **0**
- tested lower-generation request after durable/current history signed by honest witness: **0**
- tested repeated restart of corrupted/stale witness store failing open: **0**
- tested one tampered honest store + one malicious witness manufacturing conflicting quorum: **0**
- two intact honest stores retaining higher-generation liveness when the third store is unavailable/corrupt: **PASS**
- post-history-commit / pre-checkpoint ambiguity automatically authorizing: **0**
- clean higher-generation checkpoint/restart liveness: **PASS**

## Scientific conclusion

**`FIRST_RUN_NONAUTHORITY_FAILURES_RECORDED_AND_NARROWLY_REPAIRED / NO_TESTED_WITNESS_STORE_CORRUPTION_OR_ROLLBACK_ERASED_ANTI_EQUIVOCATION_OR_MANUFACTURED_QUORUM`**

Within the tested same-host subprocess + SQLite + externally authenticated witness-history-checkpoint prototype, the repaired Pilot 22 paths did not allow the tested storage corruption, coherent rollback, stale-store substitution, checkpoint replay, restart or one-malicious-witness conditions to erase durable anti-equivocation memory or manufacture a 2-of-3 conflicting quorum.

The result also shows why the external checkpoint is necessary in this prototype: local row/meta seals alone are not sufficient against coherent rewrite and reseal by an adversary that can modify the witness database.

## What this result does not establish

Pilot 22 must not be cited as proof of:

- production HSM/KMS secret custody;
- asymmetric verify-only cryptographic separation;
- administrative, geographic or cloud-provider independence of witnesses;
- safety after compromise of two threshold witness signing identities;
- correctness under arbitrary Byzantine behavior or arbitrary asynchronous partitions;
- physical power-loss, kernel or filesystem durability of witness storage;
- global transparency/gossip detection of checkpoint equivocation;
- formal consensus or linearizability;
- exactly-once behavior for arbitrary external non-idempotent effects.

The checkpoint prototype uses HMAC fixture material. Because HMAC is symmetric, the component that verifies a checkpoint using the raw HMAC key also possesses material that could mint a checkpoint. That is an explicit remaining trust-boundary weakness and is the next appropriate falsification target.

## Integrity note

Older Pilot 21 subprocess cleanup still emits Python `ResourceWarning` messages for some inherited test-process pipes. Pilot 22's new process wrapper closes its own pipes. The inherited warnings did not change a Pilot 22 endpoint and remain implementation-hygiene debt rather than scientific evidence.
