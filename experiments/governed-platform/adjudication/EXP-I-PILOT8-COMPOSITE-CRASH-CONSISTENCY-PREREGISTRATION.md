# EXP-I Pilot 8 — Composite Checkpoint Crash Consistency and Issuance Reconciliation

## Status
PREREGISTERED — NO SCIENTIFIC RESULT YET

## Motivation
Pilot 7 proved that one authenticated composite checkpoint can bind the current permit-ledger and reconciliation-ledger roots and reject mixed-era pairs. It did not prove that a state transition and the corresponding higher composite checkpoint are durably coordinated. A crash can occur after a ledger transition but before the higher composite checkpoint is durably established, or after checkpoint persistence but before the caller receives acknowledgement.

Pilot 8 tests this exact issuance/recovery boundary. It does not add model, reviewer, production, or release authority.

## Hypothesis
A durable platform-owned composite-checkpoint journal with monotonic generation, exact state-pair binding, idempotent issuance identity, authenticated predecessor chaining, and explicit PENDING/CURRENT recovery state can fail closed across crashes without permitting stale currentness or duplicate/conflicting checkpoint issuance.

## Frozen mechanism class
- A dedicated durable composite-checkpoint journal is maintained separately from the permit/reconciliation semantic rows.
- Each journal entry binds: experiment scope, issuance identity, generation, exact permit-ledger digest, exact reconciliation-ledger digest, permit-authority epoch, predecessor checkpoint digest, and status.
- Status is explicit: PENDING or CURRENT. PENDING is never sufficient for a current-state claim.
- The checkpoint authentication key is platform-held and not exposed to models/reviewers.
- Issuance identity is idempotent: exact retry may return the original durable result; semantic rebinding of the same issuance identity is rejected.
- Generation and predecessor monotonicity are checked from durable journal state, not caller memory.
- Recovery after a crash reads durable journal state and current ledgers before deciding whether a PENDING entry can be promoted, must remain blocked, or conflicts with a later state.
- A durable CURRENT checkpoint is authoritative only for the tested cross-root integrity/currentness relation. It is never production or release authority.

## Frozen endpoints
P8-01 clean initial issuance durably records one CURRENT composite checkpoint.
P8-02 crash before journal insert leaves no checkpoint and no false current state.
P8-03 crash after PENDING insert before authentication/finalization remains non-current after restart.
P8-04 crash after authenticated checkpoint material is durably recorded but before CURRENT promotion remains fail-closed until reconciliation.
P8-05 recovery promotes a matching PENDING entry exactly once when both ledgers still equal its bound pair and predecessor/generation remain valid.
P8-06 recovery refuses a PENDING entry when permit-ledger state changed after the crash.
P8-07 recovery refuses a PENDING entry when reconciliation-ledger state changed after the crash.
P8-08 recovery refuses a PENDING entry when permit-authority epoch changed after the crash.
P8-09 crash after CURRENT commit before acknowledgement replays the same checkpoint idempotently without creating a duplicate generation.
P8-10 same issuance identity cannot be rebound to a different state pair.
P8-11 same issuance identity cannot be rebound to a different generation.
P8-12 stale predecessor cannot issue or recover a newer CURRENT checkpoint.
P8-13 forged or mutated durable checkpoint authentication fails closed after restart.
P8-14 coherent journal-row rewrite without checkpoint key fails closed.
P8-15 deletion of the latest CURRENT journal entry is detected relative to trusted minimum generation.
P8-16 lower-generation rollback bundle is rejected after trusted minimum advances.
P8-17 two concurrent issuers for the same next generation cannot both become CURRENT.
P8-18 two concurrent distinct issuance identities over different state pairs cannot manufacture two CURRENT checkpoints at one generation.
P8-19 models/reviewers have zero journal mutation, checkpoint-minting, production, or release authority.
P8-20 clean higher-generation issuance remains live after prior isolated crash/recovery attack vectors.

## Scientific success criteria
All P8-01..P8-20 must satisfy the frozen expectations and the complete governed-platform regression suite must remain green. Workflow SUCCESS alone is operational evidence and is not scientific approval.

## Failure classification
- Mechanism defect: a preregistered crash/recovery, duplicate/conflicting issuance, stale predecessor, rollback, or tamper vector is accepted as current composite state.
- Test defect: the harness does not faithfully exercise the frozen endpoint while the mechanism behaves according to this preregistration.
- Environment/tooling defect: scientific endpoints are not reached because of runner/tool failure.

## Explicit non-claims
Pilot 8 does not prove distributed atomic transactions between independent storage systems, physical power-loss semantics, atomic commitment to an external KMS/checkpoint service, HSM/KMS key nonextractability, protection after compromise of both the journal and checkpoint key/trusted-minimum authority, administratively independent trust domains, multi-host Byzantine consensus, production/release authority, or universal reviewer correctness.

## Authority rule
The durable composite journal and its checkpoint key remain platform governance mechanisms. Models/reviewers are evidence producers only. A CURRENT composite checkpoint establishes only the tested integrity/currentness relation and never self-authorizes consequential execution or release.
