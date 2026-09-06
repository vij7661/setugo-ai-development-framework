# EXP-I Pilot 5 — Use-Time Checkpoint Binding and Consume/Checkpoint Reconciliation

## Status
PREREGISTERED — NO SCIENTIFIC RESULT YET

## Motivation
Pilot 4 established a bounded integrity check for the durable permit ledger using a separately held authenticated checkpoint. It did not establish that a previously positive integrity verification remains valid at the instant a convergence permit is consumed. The ledger can change after verification, and consumption itself changes the ledger from ISSUED to CONSUMED, making the previous checkpoint stale.

Pilot 5 tests that time-of-check/time-of-use boundary. The goal is not to give the checkpoint authority more power; it is to make a stale integrity result incapable of authorizing terminal convergence.

## Hypothesis
Terminal convergence can be made fail-closed unless the permit authority proves, at use time, that the exact pre-consumption ledger state matches the current authenticated checkpoint and trusted generation, then records consumption and produces a bound post-consumption state that must be reconciled to a newly authenticated checkpoint before that transition is treated as fully settled.

## Frozen mechanism class
- A use-time integrity token is platform-issued only after verifying the exact current checkpoint against the exact current canonical ledger digest and trusted minimum generation.
- The token binds checkpoint digest, checkpoint generation, pre-consumption ledger digest, permit nonce, permit semantic binding, authority epoch, and a one-time token nonce.
- A token may be used only against the exact unchanged pre-consumption ledger state.
- Consumption rechecks the canonical ledger digest inside the same SQLite write transaction before changing permit status.
- Successful consumption records a durable reconciliation record containing pre-state digest, consumed permit nonce, post-state digest, checkpoint generation used, and reconciliation status PENDING.
- Terminal convergence is not considered settled/current for later governance stages while reconciliation is PENDING.
- Reconciliation requires a newly authenticated checkpoint whose ledger digest equals the recorded post-consumption digest and whose generation is strictly higher than the checkpoint generation used for consumption; then the reconciliation record becomes SETTLED.
- A crash after durable permit consumption but before reconciliation must recover as PENDING, never as clean pre-consumption state and never as silently settled.
- Test-local HMAC keys remain prototype-only. No KMS/HSM or administrative-independence claim.
- Models/reviewers receive neither signing keys nor token/checkpoint/reconciliation mutation authority.

## Frozen endpoints
P5-01 clean current checkpoint issues an exact use-time integrity token.
P5-02 stale or invalid checkpoint cannot issue a use-time token.
P5-03 token binds exact permit nonce and semantic binding.
P5-04 token binds exact checkpoint digest and generation.
P5-05 token binds exact pre-consumption ledger digest.
P5-06 ledger mutation after token issuance but before consumption is detected and denied.
P5-07 consumed-status change after token issuance cannot reuse the stale token.
P5-08 unrelated permit issuance after token issuance invalidates the stale whole-ledger token.
P5-09 authority epoch change after token issuance invalidates the token.
P5-10 forged or mutated use-time token is denied.
P5-11 exact token replay after successful consumption is denied.
P5-12 two consumers racing with the same valid token yield at most one durable consumption transition.
P5-13 successful consumption records a durable PENDING reconciliation record before returning terminal convergence evidence.
P5-14 PENDING reconciliation survives process restart.
P5-15 PENDING state cannot be represented as SETTLED merely by restarting or replaying old positive verification.
P5-16 stale/same-generation post-consumption checkpoint cannot settle reconciliation.
P5-17 wrong-ledger-digest higher-generation checkpoint cannot settle reconciliation.
P5-18 exact higher-generation checkpoint over the post-consumption ledger settles reconciliation once.
P5-19 models/reviewers cannot mint integrity tokens, mark reconciliation SETTLED, or gain production/release authority.
P5-20 clean new permit remains live after a prior fully reconciled consumption cycle.

## Scientific success criteria
All P5-01..P5-20 must satisfy the frozen expectations and the complete governed-platform regression suite must remain green. Workflow SUCCESS alone is operational evidence and is not sufficient for scientific approval.

## Failure classification
- Mechanism defect: stale verification/token can authorize use; consumption can be duplicated; crash/restart can erase or silently settle PENDING reconciliation; or an invalid checkpoint can settle it.
- Test defect: harness setup/assertion does not faithfully measure a frozen endpoint while the mechanism behaves according to this preregistration.
- Environment/tooling defect: scientific endpoints are not reached because of runner/tool failure.

## Explicit non-claims
Pilot 5 does not prove atomic commitment between SQLite and an external checkpoint service, physical power-loss semantics, HSM/KMS nonextractability, protection after compromise of all platform integrity secrets, multi-host Byzantine consensus, production/release authority, or universal reviewer correctness.

## Authority rule
Authority remains external to models. The use-time integrity token and reconciliation state are platform control artifacts. Review/model agreement is evidence only. Even a SETTLED convergence reconciliation has zero production or release authority unless a separate governance gate issues it.
