# EXP-I Pilot 7 — Composite Cross-Root Consistency

## Status
PREREGISTERED — NO SCIENTIFIC RESULT YET

## Motivation
Pilots 4 and 6 protect the permit ledger and reconciliation ledger with separate authenticated checkpoints. Each root can be individually valid while representing a different logical era. Without a higher-level binding, a caller could attempt to combine an independently valid permit-ledger state from one era with an independently valid reconciliation-ledger state from another and present the pair as one current governance state.

Pilot 7 tests that exact cross-root consistency boundary. It does not widen convergence, production, release, model, or reviewer authority.

## Hypothesis
A platform-issued composite checkpoint that cryptographically binds the exact current permit-ledger digest and reconciliation-ledger digest under one monotonic composite generation can make independently valid but mixed-era roots fail closed.

## Frozen mechanism class
- Composite state contains: experiment scope, composite generation, exact canonical permit-ledger digest, exact canonical reconciliation-ledger digest, permit authority epoch, and predecessor composite-checkpoint digest.
- Composite checkpoint authentication uses a dedicated test-local HMAC key not stored in SQLite.
- Trusted minimum composite generation is treated as outside SQLite.
- Composite verification recomputes both canonical ledger digests from current storage at verification time and requires exact equality with the bound pair.
- A higher composite generation requires an authenticated predecessor and strictly increasing generation.
- Independent permit-ledger or reconciliation-ledger checkpoints may remain useful evidence, but neither can substitute for a current composite checkpoint when a cross-root current-state claim is being made.
- Models/reviewers receive neither the composite key nor composite checkpoint/trusted-minimum mutation authority.

## Frozen endpoints
P7-01 clean current permit and reconciliation states verify under one composite checkpoint.
P7-02 permit-ledger mutation with unchanged reconciliation state invalidates the composite checkpoint.
P7-03 reconciliation-ledger mutation with unchanged permit state invalidates the composite checkpoint.
P7-04 both ledgers coherently changed after composite issuance invalidate the old composite checkpoint.
P7-05 stale permit state plus current reconciliation state cannot satisfy a current composite checkpoint.
P7-06 current permit state plus stale reconciliation state cannot satisfy a current composite checkpoint.
P7-07 an old independently valid permit checkpoint cannot be paired with a newer independently valid reconciliation checkpoint to manufacture composite currentness.
P7-08 a newer independently valid permit checkpoint cannot be paired with an old independently valid reconciliation checkpoint to manufacture composite currentness.
P7-09 composite permit-digest field substitution is rejected.
P7-10 composite reconciliation-digest field substitution is rejected.
P7-11 composite permit-authority-epoch substitution is rejected.
P7-12 forged or mutated composite authentication tag is rejected.
P7-13 wrong composite scope is rejected.
P7-14 predecessor substitution or unauthenticated predecessor is rejected.
P7-15 old valid composite checkpoint is rejected after trusted minimum composite generation advances.
P7-16 repeated restart with the same mixed-era/tampered pair never promotes it to current composite state.
P7-17 independent side-root validity alone is insufficient when the composite root is missing.
P7-18 composite verification has zero reviewer/model-generated or production/release authority.
P7-19 coordinated post-consumption/post-reconciliation state can advance to a higher composite generation.
P7-20 clean higher-generation composite checkpoint remains live after prior isolated mixed-era/tamper vectors.

## Scientific success criteria
All P7-01..P7-20 must satisfy the frozen expectations and the complete governed-platform regression suite must remain green. Workflow SUCCESS alone is operational evidence and is not scientific approval.

## Failure classification
- Mechanism defect: a preregistered mixed-era, one-sided rollback/mutation, forged cross-binding, stale-generation, or predecessor attack is accepted as current composite state.
- Test defect: harness construction/assertion does not faithfully measure a frozen endpoint while the mechanism behaves according to this preregistration.
- Environment/tooling defect: scientific endpoints are not reached because of runner/tool failure.

## Explicit non-claims
Pilot 7 does not prove atomic commitment between SQLite and a truly external checkpoint service, physical power-loss semantics, HSM/KMS nonextractability, protection after compromise of SQLite plus the composite key/trusted-minimum authority, administratively independent trust domains, multi-host Byzantine consensus, production/release authority, or universal reviewer correctness.

## Authority rule
The composite checkpoint is a platform integrity artifact only. Models and reviewers remain evidence producers. A valid composite checkpoint establishes only the tested integrity/currentness relationship between the two ledger roots; it never grants production or release authority.
