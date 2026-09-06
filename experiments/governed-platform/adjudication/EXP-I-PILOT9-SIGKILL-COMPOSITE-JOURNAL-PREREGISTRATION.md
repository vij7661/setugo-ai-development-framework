# EXP-I Pilot 9 — External SIGKILL Composite Checkpoint Crash Consistency

## Status
PREREGISTERED — NO SCIENTIFIC RESULT YET

## Motivation
Pilot 8 established bounded crash/recovery behavior only for simulated exceptions around committed SQLite transitions. A Python exception permits normal interpreter cleanup and is not equivalent to abrupt operating-system process death. Pilot 9 tests the same durable composite-checkpoint currentness boundary using a distinct child process that is externally terminated by its parent after explicit readiness/stage signals.

This pilot does not add model, reviewer, production, release, or checkpoint-minting authority to the caller.

## Hypothesis
For the tested same-host SQLite path, externally terminating the composite-journal writer after precisely observed durable stages will not create false CURRENT state, resurrect stale state, duplicate a generation, or permit semantic rebinding. Fresh-process recovery will either fail closed or deterministically recover the exact previously durable state, and clean later issuance will remain live.

## Frozen mechanism class
- The existing Pilot 8 durable composite journal semantics remain unchanged: PENDING/CURRENT, exact state-pair binding, issuance identity, generation uniqueness, predecessor binding, authenticated material, and trusted-minimum verification.
- A child worker process performs issuance stages against the same durable SQLite database.
- The child emits an explicit line-buffered stage marker only after the corresponding SQLite commit is complete.
- The parent waits for the exact marker and then terminates the child externally with SIGKILL on POSIX runners. No child exception/cleanup path is relied on for the tested kill cases.
- Fresh recovery/verification is performed by a newly constructed authority instance after the child is reaped.
- Child process identity/PID is captured so the test proves that a distinct externally terminated process performed the write.
- The parent does not treat a stage marker as authority; durable state is re-read after process death.
- Existing model/reviewer authority boundaries remain zero.

## Frozen endpoints
P9-01 readiness protocol proves a distinct child writer PID and parent-observed stage handshake.
P9-02 SIGKILL before journal insert leaves no checkpoint and no false CURRENT state.
P9-03 SIGKILL after durable PENDING insert before authenticated material leaves PENDING non-current after fresh reopen.
P9-04 SIGKILL after authenticated PENDING material before CURRENT promotion leaves PENDING fail-closed after fresh reopen.
P9-05 exact matching authenticated PENDING state after SIGKILL can be recovered to CURRENT exactly once from a fresh authority instance.
P9-06 permit-ledger mutation after killed authenticated PENDING prevents recovery.
P9-07 reconciliation-ledger mutation after killed authenticated PENDING prevents recovery.
P9-08 permit-authority epoch change after killed authenticated PENDING prevents recovery.
P9-09 SIGKILL after durable CURRENT commit before acknowledgement preserves one CURRENT record after fresh reopen.
P9-10 retry after post-CURRENT SIGKILL returns the exact durable checkpoint without creating another generation.
P9-11 same issuance identity after restart cannot rebind to a different state pair.
P9-12 same issuance identity after restart cannot rebind to a different generation.
P9-13 invalid or tampered predecessor after writer death blocks subsequent generation issuance.
P9-14 mutated durable authentication after writer death fails closed on fresh reopen.
P9-15 deleting the latest CURRENT record after writer death is detected when trusted minimum requires that generation.
P9-16 old valid lower generation remains rejected after trusted minimum advances.
P9-17 two independently launched child writers racing for the same next generation produce at most one durable CURRENT checkpoint.
P9-18 a killed PENDING writer plus a competing different state pair cannot manufacture two CURRENT checkpoints at the same generation.
P9-19 child process/model/reviewer surfaces have zero production or release authority; process success/exit status is not itself currentness authority.
P9-20 clean higher-generation issuance from a fresh process remains live after the isolated SIGKILL/recovery vectors.

## Scientific success criteria
All P9-01..P9-20 must satisfy the frozen expectations on the supported POSIX GitHub runner, and the complete governed-platform regression suite must remain green. Workflow SUCCESS alone is operational evidence and is not scientific approval.

## Failure classification
- Mechanism defect: a preregistered external-kill/restart, replay, concurrency, stale-state, rollback, or tamper vector is accepted as current state, or clean liveness is broken by the mechanism.
- Test defect: the child/parent orchestration does not faithfully reach the stated stage or kill boundary while the mechanism otherwise behaves according to this preregistration.
- Environment/tooling defect: the runner cannot provide the required process/signal semantics or scientific endpoints are not reached because of tooling failure.

## Explicit non-claims
Pilot 9 does not prove physical power-loss semantics, storage-device cache durability, filesystem/fsync behavior beyond SQLite/runner behavior actually exercised, atomic commitment across independent storage systems, a separate checkpoint signing authority/key process, external KMS/HSM nonextractability, protection after compromise of both SQLite and the composite key/trusted-minimum authority, administratively independent trust domains, multi-host or Byzantine consensus, production/release authority, or universal reviewer correctness.

## Authority rule
A child process executing checkpoint-journal code is an execution component only. Process identity, successful exit, stage output, or possession of model/reviewer evidence never establishes production/release authority. Currentness is determined only by the platform governance mechanism over durable state and authenticated bindings.
