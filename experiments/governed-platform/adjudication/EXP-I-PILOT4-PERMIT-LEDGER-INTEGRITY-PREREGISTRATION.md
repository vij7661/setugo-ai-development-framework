# EXP-I Pilot 4 — Externally Anchored Permit-Ledger Integrity

## Status
PREREGISTERED — NO SCIENTIFIC RESULT YET

## Motivation
Pilot 3 demonstrated durable replay protection across authority restart using SQLite WAL, but explicitly did not establish integrity against coherent local database rewrite, deletion, rollback, epoch lowering, or resurrection of consumed permits. A local attacker that can rewrite the permit database may be able to present an internally coherent but stale or altered state.

Pilot 4 tests that exact boundary using a platform-held integrity checkpoint stored outside the permit database. It does not expand convergence, production, release, model, or reviewer authority.

## Hypothesis
A signed external checkpoint over the canonical permit-ledger state, combined with a trusted minimum checkpoint generation, can make tested coherent SQLite rewrites and rollbacks fail closed before a permit is treated as live.

## Frozen mechanism class
- Canonical digest covers authority epoch plus every permit-ledger row in deterministic nonce order, including nonce, binding digest, payload JSON, and status.
- Checkpoint contains scope, generation, ledger digest, and prior checkpoint digest.
- Checkpoint authentication uses a separate test-local HMAC integrity key not stored in SQLite.
- The current checkpoint is stored outside the SQLite database.
- Recovery/consumption requires: valid checkpoint authentication, exact scope, generation >= trusted minimum, canonical database digest equal to checkpoint ledger digest, and valid checkpoint-chain predecessor when applicable.
- No model/reviewer receives the integrity key or checkpoint mutation authority.
- This is an integrity prototype, not external-HSM/KMS nonextractability.

## Frozen endpoints
P4-01 clean current database and checkpoint verify.
P4-02 consumed-status resurrection to ISSUED is detected.
P4-03 permit-row deletion is detected.
P4-04 permit payload rewrite is detected even if JSON remains syntactically valid.
P4-05 binding-digest rewrite is detected.
P4-06 authority epoch lowering is detected.
P4-07 coherent database rollback with matching old checkpoint is rejected below trusted minimum generation.
P4-08 stale database paired with current checkpoint is rejected by ledger digest mismatch.
P4-09 current database paired with stale checkpoint is rejected below trusted minimum or by digest mismatch.
P4-10 forged checkpoint authentication tag is rejected.
P4-11 checkpoint field mutation after signing is rejected.
P4-12 wrong checkpoint scope is rejected.
P4-13 checkpoint-chain predecessor mutation is rejected.
P4-14 unknown/missing external checkpoint fails closed.
P4-15 duplicate/reordered SQLite row presentation cannot change canonical digest semantics.
P4-16 coherent rewrite plus recomputed local-only values still fails without the integrity key.
P4-17 one old valid checkpoint cannot authorize a rolled-back database after trusted minimum advances.
P4-18 repeated restart with the same tampered bundle never promotes it to current state.
P4-19 models/reviewers have no API surface to mint or advance trusted checkpoint generation.
P4-20 clean higher-generation checkpoint remains live after prior isolated tamper vectors.

## Scientific success criteria
All P4-01..P4-20 must satisfy the frozen expectations and the full governed-platform regression suite must remain green. Workflow SUCCESS is operational evidence only and is not itself scientific approval.

## Failure classification
- Mechanism defect: a preregistered coherent rewrite/rollback/tamper vector is accepted as current authoritative permit state.
- Test defect: harness construction or assertion fails to measure the frozen requirement while the mechanism behaves correctly.
- Environment/tooling defect: scientific endpoints are not reached because of runner/tool failure.

## Explicit non-claims
Pilot 4 does not prove HSM/KMS key nonextractability, protection when both SQLite and the separate integrity key/checkpoint authority are compromised, physical power-loss semantics, Byzantine consensus, multi-host availability, production/release authority, or universal reviewer correctness.

## Authority rule
The platform remains the only checkpoint authority. Models and reviewers remain evidence producers only. A verified ledger/checkpoint state may permit evaluation of convergence state but never grants production or release authority.
