# EXP-I Pilot 10 — Process-Isolated Composite Checkpoint Authority

## Status
PREREGISTERED — NO SCIENTIFIC RESULT YET

## Motivation
Pilot 9 proved bounded SIGKILL durability for a distinct writer process, but the parent harness still supplied and possessed the composite HMAC key. That is not a checkpoint-authority isolation result. Pilot 10 moves checkpoint minting and verification behind a dedicated authority process with its own durable monotonic store. The caller-facing request path never receives checkpoint-signing material and cannot manufacture a valid checkpoint locally.

This remains a bounded same-host process-isolation prototype. It is not an HSM/KMS or operating-system privilege-separation claim.

## Hypothesis
A dedicated composite-checkpoint authority process that independently reads the current permit/reconciliation state, owns checkpoint authentication material inside its worker environment, persists monotonic issuance state in a separate SQLite authority store, and exposes only ISSUE/VERIFY operations can prevent caller-side checkpoint minting, same-generation equivocation, rollback, stale-positive-verification reuse, and authority substitution while retaining clean higher-generation liveness.

## Frozen mechanism class
- Main governance state remains in the existing permit/reconciliation SQLite database.
- Composite checkpoint authority state is stored in a separate SQLite database.
- The caller sends only issuance identity and requested generation for ISSUE; the authority process independently computes the exact current permit-ledger digest, reconciliation-ledger digest, and permit-authority epoch from the main governance database before minting.
- The checkpoint statement binds version, scope, authority identity, issuance identity, generation, exact permit digest, exact reconciliation digest, permit-authority epoch, and predecessor checkpoint digest.
- The authority process enforces monotonic generation and same-generation anti-equivocation from its own durable store.
- Exact replay of the same issuance/generation/current-state tuple is idempotent.
- VERIFY occurs through the authority process and rechecks authentication, scope, trusted minimum generation, durable authority-store membership, predecessor lineage, and the current governance-state pair. A prior positive verify is not transferable to a changed record or changed governance state.
- The caller-facing process object does not retain checkpoint-signing bytes or place them in argv. Test harness construction necessarily knows fixture keys; therefore this is request-path/process-boundary isolation, not secret nonextractability from the test administrator.
- Models/reviewers do not receive ISSUE/VERIFY control fields and gain no production/release authority.

## Frozen endpoints
P10-01 authority runs in a distinct process and uses a separate durable authority store.
P10-02 caller-facing process object/argv does not expose or retain the checkpoint-signing key.
P10-03 clean ISSUE independently binds the exact current permit/reconciliation pair and epoch.
P10-04 clean VERIFY succeeds only through the authority process for the exact durable record and current state.
P10-05 caller cannot forge a checkpoint with an unrelated key and obtain positive VERIFY.
P10-06 lower-generation issuance is refused after a higher generation is durably established.
P10-07 same-generation conflicting governance-state statement is refused.
P10-08 monotonicity and same-generation anti-equivocation survive authority-process restart.
P10-09 exact issuance replay is idempotent and returns the same checkpoint identity/authentication.
P10-10 checkpoint authentication mutation is rejected.
P10-11 scope, authority identity, issuance identity, generation, state digest, epoch, or predecessor substitution is rejected.
P10-12 valid old checkpoint below trusted minimum generation is rejected.
P10-13 authority-process unavailability fails closed; caller cannot locally substitute verification.
P10-14 a prior positive verification cannot be rebound to a changed checkpoint record.
P10-15 a prior positive verification cannot authorize after permit-ledger state changes.
P10-16 a prior positive verification cannot authorize after reconciliation-ledger state or permit-authority epoch changes.
P10-17 authority crash after durable ISSUE commit but before response is reconciled by restart as the same idempotent checkpoint, not a second issuance.
P10-18 tampering/deletion of authority-store issuance state prevents the corresponding checkpoint from verifying as current.
P10-19 model/reviewer/caller outputs and process success have zero checkpoint-minting, production, or release authority.
P10-20 clean higher-generation issue/verify remains live after authority restart and prior isolated attack vectors.

## Scientific success criteria
All P10-01..P10-20 must satisfy the frozen expectations and the complete governed-platform regression suite must remain green. Workflow SUCCESS alone is operational evidence and is not scientific approval.

## Failure classification
- Mechanism defect: a preregistered forgery, rollback, equivocation, stale verification, authority substitution, durable-state tamper, crash/restart, or liveness endpoint violates the frozen expectation.
- Test defect: the harness fails to exercise the frozen mechanism while the mechanism itself behaves as preregistered.
- Environment/tooling defect: the distinct authority process or SQLite runner path cannot reach the scientific endpoints because of tooling failure.

## Explicit non-claims
Pilot 10 does not prove operating-system privilege separation between same-user processes, checkpoint-key nonextractability from the test administrator/host, HSM/KMS isolation, physical power-loss semantics, independent administrative trust domains, distributed atomic transactions, multi-host or Byzantine consensus, production/release authority, or universal reviewer correctness.

## Authority rule
The composite-checkpoint authority remains a platform governance component. It establishes only the tested integrity/currentness relation. Models, reviewers, caller-provided content, successful process completion, and checkpoint validity never self-authorize consequential execution or release.
