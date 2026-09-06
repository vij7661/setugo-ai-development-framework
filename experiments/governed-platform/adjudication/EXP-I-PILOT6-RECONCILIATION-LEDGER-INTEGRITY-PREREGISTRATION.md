# EXP-I Pilot 6 — Reconciliation-Ledger Integrity

## Status
PREREGISTERED — NO SCIENTIFIC RESULT YET

## Motivation
Pilot 5 made permit consumption and creation of a PENDING reconciliation record durable, but the `convergence_reconciliation` table is not covered by Pilot 4's permit-ledger checkpoint. A local coherent rewrite could therefore attempt to change PENDING to SETTLED, alter the recorded post-consumption digest or checkpoint generation, delete a reconciliation row, or roll the reconciliation state backward without violating the permit-ledger checkpoint.

Pilot 6 tests that exact integrity boundary. It does not widen convergence, production, release, model, or reviewer authority.

## Hypothesis
A separately authenticated reconciliation checkpoint over a canonical deterministic representation of every reconciliation row, combined with a trusted minimum reconciliation-checkpoint generation, can make the preregistered coherent rewrite, deletion, resurrection, and rollback attempts fail closed.

## Frozen mechanism class
- Canonical reconciliation state contains every `convergence_reconciliation` row ordered by `reconciliation_id` and all security-relevant fields: reconciliation id, token nonce, permit nonce, pre-ledger digest, post-ledger digest, checkpoint generation, status, and settlement checkpoint digest.
- A reconciliation checkpoint binds scope, generation, canonical reconciliation digest, and predecessor checkpoint digest.
- Authentication uses a dedicated test-local HMAC reconciliation-integrity key not stored in SQLite.
- Current reconciliation checkpoint and trusted minimum generation are treated as outside the SQLite database.
- Verification requires valid authentication, exact scope, generation >= trusted minimum, valid predecessor binding when supplied, and exact equality between checkpoint digest and the canonical current reconciliation state.
- Models/reviewers receive neither the reconciliation-integrity key nor checkpoint/trusted-minimum mutation authority.

## Frozen endpoints
P6-01 clean PENDING reconciliation and checkpoint verify.
P6-02 PENDING-to-SETTLED local rewrite is detected.
P6-03 SETTLED-to-PENDING local rollback is detected.
P6-04 reconciliation-row deletion is detected.
P6-05 post-ledger-digest substitution is detected.
P6-06 pre-ledger-digest substitution is detected.
P6-07 checkpoint-generation lowering in a reconciliation row is detected.
P6-08 checkpoint-generation inflation in a reconciliation row is detected.
P6-09 permit-nonce substitution is detected.
P6-10 token-nonce substitution is detected.
P6-11 settlement-checkpoint-digest substitution is detected.
P6-12 syntactically coherent full-row rewrite with recomputed local values still fails without the reconciliation-integrity key.
P6-13 stale reconciliation DB plus old valid checkpoint is rejected after trusted minimum advances.
P6-14 stale reconciliation DB plus current checkpoint is rejected by reconciliation digest mismatch.
P6-15 current reconciliation DB plus stale checkpoint is rejected below trusted minimum or by digest mismatch.
P6-16 forged/mutated reconciliation checkpoint is rejected.
P6-17 wrong reconciliation checkpoint scope or predecessor is rejected.
P6-18 repeated restart with the same tampered reconciliation bundle never promotes it.
P6-19 models/reviewers cannot mint reconciliation checkpoints or gain production/release authority.
P6-20 clean higher-generation SETTLED reconciliation checkpoint remains live after prior isolated tamper vectors.

## Scientific success criteria
All P6-01..P6-20 must satisfy the frozen expectations and the complete governed-platform regression suite must remain green. Workflow SUCCESS alone is operational evidence, not scientific approval.

## Failure classification
- Mechanism defect: any preregistered coherent reconciliation rewrite/rollback/tamper vector is accepted as current valid reconciliation state.
- Test defect: harness construction/assertion does not faithfully measure the frozen requirement while the mechanism behaves according to the preregistration.
- Environment/tooling defect: scientific endpoints are not reached because of runner/tool failure.

## Explicit non-claims
Pilot 6 does not prove atomic commitment between SQLite and a truly external checkpoint service, physical power-loss semantics, HSM/KMS nonextractability, protection after compromise of both SQLite and the reconciliation-integrity key/trusted-minimum authority, multi-host Byzantine consensus, production/release authority, or universal reviewer correctness.

## Authority rule
Reconciliation integrity remains a platform control. Models and reviewers remain evidence producers only. A valid SETTLED reconciliation checkpoint is integrity evidence, not production or release authority.
