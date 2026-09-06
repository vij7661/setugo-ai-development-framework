# EXP-O Pilot 22 — First-Run Failure Diagnosis and Repair Lineage

Status: **RECORDED AFTER FIRST FROZEN RUN AND BEFORE ANY REPAIR**

Frozen first-execution SHA: `79e0c7dfd651afebec327177a23f18de4e1e9b49`

First run: `34026461198`

Observed first-run outcomes:

- P22-01 PASS
- P22-02 ERROR
- P22-03 ERROR
- P22-04 through P22-17 PASS
- P22-18 FAIL
- P22-19 PASS
- P22-20 PASS

No first-run failure created effective authority or a conflicting quorum.

## Diagnosis

### P22-02 / P22-03 — implementation failure-mode defect

Header corruption and truncation caused `SealedWitnessProcess.__init__` / worker startup to call `init_store()` on an already existing damaged SQLite file. SQLite raised `DatabaseError` before the process could expose an explicit fail-closed integrity decision.

This is **not** a false-green authority failure: no signature or authority was produced. It is nevertheless an implementation defect against the preregistered expectation that corrupted storage is recognized and refused rather than crashing the caller during startup.

Permitted repair:

- initialize schema only when the witness store does not already exist;
- never recreate/reset an existing damaged store;
- allow a witness process to start with an existing damaged store and make `verify_store()` the authoritative pre-sign integrity gate;
- preserve all checkpoint, seal, monotonicity and signing rules unchanged.

### P22-18 — test-construction defect

The positive liveness control first bootstrapped honest witnesses at generation 5 with a synthetic statement and then requested a different authority statement at **the same generation 5**. The runtime correctly returned `SAME_GENERATION_EQUIVOCATION_REFUSED`.

The preregistered P22-18 endpoint is intact-two-witness liveness when those witnesses agree on a current statement; it does not require reusing a generation for different content.

Permitted repair:

- retain bootstrap generation 5;
- request the authority statement at a strictly higher generation (generation 6 or later) from both intact witnesses;
- verify 2-of-3 quorum at that same higher generation;
- do not weaken anti-equivocation rules or expected quorum requirements.

## Repair acceptance rule

After the above narrow changes:

1. rerun all original twenty P22 cases;
2. P22-02/P22-03 must produce explicit fail-closed responses rather than process-construction exceptions;
3. P22-18 must exercise a non-equivocating higher-generation liveness path;
4. all other cases remain unchanged in scientific intent;
5. first-run failures remain part of the final adjudication;
6. no claim of first-run 20/20 pass is permitted.
