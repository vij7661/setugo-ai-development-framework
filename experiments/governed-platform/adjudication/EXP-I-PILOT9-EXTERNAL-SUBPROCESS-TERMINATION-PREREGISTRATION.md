# EXP-I Pilot 9 — External Subprocess Termination Around Composite Checkpoint Issuance

## Status
PREREGISTERED — NO SCIENTIFIC RESULT YET

## Parent evidence
- Parent experiment: EXP-I Pilot 8 — Composite Checkpoint Crash Consistency and Issuance Reconciliation.
- Parent adjudication commit: `3b3be3b6f6e6d57ed36dafed8f99aba6fc98eb57`.
- Pilot 8 bounded result: 20/20 frozen Pilot 8 vectors and 932/932 governor falsification tests passed after preserving one fixture defect and one mechanism defect in the failure lineage.
- Pilot 8 explicitly did not prove abrupt operating-system process death or SIGKILL semantics because its crash points were simulated exceptions.

## Scientific question
Does the same durable composite-checkpoint safety contract survive when the writer disappears by externally imposed process death, without Python exception propagation, `finally` cleanup, cooperative self-exit, or normal response completion?

## Frozen hypothesis
For the tested same-host SQLite prototype, externally killing the checkpoint writer at preregistered issuance boundaries must not increase authority, manufacture CURRENT state from uncommitted/unauthenticated state, duplicate a generation, rebind an issuance identity, or convert ambiguous recovery state into success. Durable committed state must remain replayable/reconcilable exactly according to the Pilot 8 contract, and clean higher-generation issuance must remain live.

## Frozen mechanism and instrumentation rules
- Pilot 8 checkpoint semantics remain unchanged: platform-owned HMAC-authenticated composite checkpoint journal; explicit PENDING/CURRENT status; exact permit-ledger and reconciliation-ledger digest binding; permit-authority epoch binding; monotonic generation; issuance identity; authenticated predecessor chaining; conditional promotion; trusted-minimum verification.
- A distinct Python worker subprocess performs checkpoint issuance against the same SQLite database used by the parent fixture.
- The parent observes a machine-readable readiness marker emitted only after the named durable/transactional boundary is reached.
- After emitting the marker, the child blocks and performs no further checkpoint transition.
- The parent verifies the marker PID equals the live child PID, then terminates the child externally with `Popen.kill()` / SIGKILL semantics on Linux CI and confirms signal termination before reopening state.
- A fresh process/authority instance performs recovery or replay after confirmed child death.
- Fault cases must not use `raise`, injected simulated exceptions, `os._exit()`, graceful shutdown hooks, worker self-termination, or `finally` as the crash mechanism.
- Readiness markers are test evidence only and confer no authority.
- Instrumentation required to expose a cut point must be behaviorally inert when no cut point is supplied and must not weaken Pilot 8 tests or production-facing semantics.
- No model/reviewer gains journal mutation, checkpoint minting, production, release, merge, or approval authority.

## Frozen externally killed cut points
Exactly these five coordinated parent-kill points must exist before first scientific execution:
1. `READY_BEFORE_PENDING_INSERT`
2. `READY_AFTER_PENDING_COMMIT`
3. `READY_AFTER_AUTHENTICATED_PENDING_COMMIT`
4. `READY_AFTER_CURRENT_UPDATE_BEFORE_COMMIT`
5. `READY_AFTER_CURRENT_COMMIT_BEFORE_RESPONSE`

The fourth point is intentionally inside the uncommitted CURRENT-promotion transaction; the fifth is after durable CURRENT commit but before caller response.

## Frozen primary falsifiers
Exactly these fourteen primary Pilot 9 cases must exist before first scientific execution.

### P9-01 — readiness protocol proves distinct externally killed writer
Expected: parent observes exact marker with child PID, child remains alive and blocked until parent kill, termination is externally caused, and no cooperative crash mechanism is used.

### P9-02 — kill before PENDING insert
Expected: generation 2 has no durable issuance and no false CURRENT state; generation 1 remains valid.

### P9-03 — kill after PENDING commit before authenticated material
Expected: durable row may exist only as unauthenticated PENDING; it is non-current and recovery fails closed.

### P9-04 — kill after authenticated PENDING commit
Expected: authenticated PENDING remains non-current immediately after restart; exact matching recovery may promote it according to Pilot 8 rules.

### P9-05 — exact authenticated PENDING recovery promotes once after parent kill
Expected: one and only one CURRENT generation-2 row; repeated recovery is stable and does not mint a duplicate.

### P9-06 — kill after CURRENT update but before COMMIT
Expected: uncommitted promotion rolls back to authenticated PENDING; no CURRENT generation-2 state is accepted before explicit recovery.

### P9-07 — recovery after rolled-back promotion remains safe
Expected: exact matching authenticated PENDING may subsequently reconcile to CURRENT once; recovery does not infer authority from the killed transaction itself.

### P9-08 — kill after CURRENT COMMIT before response
Expected: durable CURRENT generation 2 survives fresh reopen and validates; no response acknowledgement is required for durability.

### P9-09 — retry after post-CURRENT kill is idempotent
Expected: retry with the same issuance identity/generation returns the exact durable checkpoint and journal row count/generation count remain one.

### P9-10 — semantic rebinding after killed writer is denied
Expected: the same issuance identity cannot be reused for a different current state pair or generation after recovery/replay.

### P9-11 — state drift blocks killed authenticated-PENDING recovery
Expected: if bound permit/reconciliation/epoch state changes after the kill and before recovery, the pending issuance cannot be promoted.

### P9-12 — same-generation competitor cannot exploit killed writer
Expected: no sequence involving a killed writer and a distinct issuance identity can produce two CURRENT checkpoints at generation 2.

### P9-13 — model/reviewer authority remains zero after crash/recovery
Expected: recovery evidence and CURRENT checkpoint status confer no model/reviewer mutation, production, release, merge, or approval authority.

### P9-14 — clean higher-generation liveness after isolated kill vectors
Expected: after isolated fault cases, a clean generation-2 then generation-3 issuance path remains live and verifies exactly once per generation.

## Primary endpoints
1. false-CURRENT acceptance rate after external writer death;
2. duplicate CURRENT generation rate after external writer death/retry;
3. issuance semantic-rebinding acceptance rate;
4. unsafe PENDING recovery under state drift;
5. loss of committed CURRENT after response-loss kill;
6. clean post-fault liveness.

Any false CURRENT, duplicate CURRENT generation, accepted semantic rebinding, state-drift promotion, or loss of a committed CURRENT checkpoint falsifies Pilot 9 on the exercised path.

## Evidence rules
- All P9-01..P9-14 execute in the first scientific run.
- Exact readiness marker, PID match, pre-kill liveness, and child return code/signal are asserted for kill cases.
- First-run failures are retained verbatim in adjudication lineage.
- No failing case may be removed, renamed, weakened, or converted after first execution.
- Any repair requires a recorded defect classification first and must remain within the smallest authorized artifact scope.
- The original failing check and full governed-platform regression suite must be rerun after any authorized repair.
- Workflow SUCCESS is operational evidence only, never scientific approval by itself.

## Explicit non-claims
A Pilot 9 pass will still not establish physical power-loss durability, kernel panic or VM reset behavior, storage-controller/cache/barrier guarantees, torn-sector/bit-rot resistance, all SQLite WAL/checkpoint interleavings, multi-host atomic commitment, external KMS/HSM atomicity or key nonextractability, administratively independent trust domains, Byzantine consensus, exactly-once semantics for arbitrary remote side effects, production/release authority, or universal reviewer correctness.

## Authority rule
Authority remains external to models and workers. A recovered or durable CURRENT composite checkpoint proves only the bounded integrity/currentness relation tested here. Neither a model, reviewer, worker, checkpoint, green CI run, nor successful recovery may self-issue production or release authority.
