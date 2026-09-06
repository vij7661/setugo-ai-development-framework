# EXP-I Pilot 19 — Issuance-Ledger / Anti-Rollback-Anchor Crash Consistency

## Status

PREREGISTERED — IMPLEMENTATION NOT YET EXPOSED

## Parent result

EXP-I Pilot 18 is a bounded pass at evaluated SHA `3cffae801b87127912741f9323d87c3bf81c8900`, run `34056102248`, job `101548175050`, with P18-01..P18-16 explicitly passing and the complete governed-platform suite passing 1090/1090 on the same frozen SHA.

Pilot 18 proved recovery-signer crash behavior around issuance transaction boundaries and used an independent anti-rollback anchor. It did not prove crash consistency of the two durable stores themselves when a process dies between issuance-ledger commit and anchor advancement, or while the anchor is being replaced.

## Falsification question

If the issuance ledger and independent anti-rollback anchor are updated as separate durable stores, can an external hard kill, torn/stale anchor, stale ledger snapshot, or concurrent recovery convert divergence into authority, erase durable issuance memory, permit semantic rebinding, or block all future legitimate issuance? Can exact reconciliation restore only the uniquely derivable committed state without allowing either store to self-authorize the other?

## Frozen authority model

- Recovery signer remains the only holder of the recovery-signing private key.
- Issuance ledger and anti-rollback anchor remain physically/logically separate durable artifacts.
- Neither ledger contents nor anchor contents alone create trusted-minimum mutation authority.
- Minimum-side use-time validation requires an issuance to be committed and reconciled to the authoritative anchor state.
- Recovery/reconciliation may repair only a uniquely derivable exact binding; ambiguous or conflicting state fails closed.
- Models, reviewers, signer callers, registry readers, and minimum readers cannot choose the reconciliation result.
- No artifact grants production/release/deploy/completion authority.

## Frozen crash boundaries

1. after issuance ledger COMMIT but before anchor update begins;
2. after anchor temporary material is written but before atomic replace;
3. immediately after anchor replace but before response delivery;
4. recovery with ledger newer than anchor;
5. recovery with anchor newer than ledger;
6. stale ledger snapshot substituted after reconciliation;
7. stale anchor snapshot substituted after reconciliation;
8. concurrent reconciliation attempts on the same divergence.

All kill boundaries must be parent-controlled external process termination. Injected exceptions or child self-termination are not substitutes.

## Frozen scientific vectors

- **P19-01** — Readiness protocol proves distinct child signer/reconciler process and parent-controlled external termination at the ledger-to-anchor boundary.
- **P19-02** — Kill after ledger COMMIT before anchor update leaves an explicitly divergent state, not a false-success/current-authority state.
- **P19-03** — Fresh restart detects ledger-newer-than-anchor divergence before permitting minimum mutation.
- **P19-04** — Exact reconciliation of ledger-newer-than-anchor advances the anchor only to the uniquely committed issuance binding and does so once.
- **P19-05** — Kill after anchor temporary write but before replace leaves either the prior valid anchor or a fail-closed recoverable state; partial material is never accepted as current.
- **P19-06** — Kill after atomic anchor replace before response is replay-safe and does not duplicate issuance/anchor generation.
- **P19-07** — Anchor-newer-than-ledger state is never auto-authorized; without exact committed issuance correspondence it fails closed.
- **P19-08** — Same recovery identity cannot be semantically rebound while ledger/anchor are divergent or after reconciliation.
- **P19-09** — Stale ledger snapshot substitution after a newer reconciled issuance is detected/fails closed against the anchor.
- **P19-10** — Stale anchor snapshot substitution after reconciliation is detected/fails closed against retained ledger/reconciliation state.
- **P19-11** — Conflicting same-generation anchor content cannot be selected by caller/model/reviewer preference; ambiguity fails closed.
- **P19-12** — Two reconciliation workers racing the same ledger-newer-than-anchor state converge on one exact authoritative anchor result.
- **P19-13** — Repeated crash/restart/reconciliation preserves monotonic issuance/anchor memory and exact replay identity.
- **P19-14** — Minimum-side use-time validation rejects any issuance while ledger/anchor correspondence is unresolved, even when its cryptographic signature is valid.
- **P19-15** — Models, reviewers, registry/root/minimum ordinary surfaces retain zero reconciliation-result, signer, minimum, release, deploy, production, or completion authority.
- **P19-16** — After recovering a killed R1→R2 ledger/anchor divergence, a clean R2→R3 issuance, anchor advancement, and trusted-minimum advancement remains live exactly once.

## Primary falsification endpoints

1. divergence silently treated as success;
2. ledger-only authority;
3. anchor-only authority;
4. torn/temporary anchor acceptance;
5. duplicate advancement after post-replace response loss;
6. stale ledger rollback acceptance;
7. stale anchor rollback acceptance;
8. semantic rebinding during recovery;
9. caller-selected conflict resolution;
10. racing reconcilers creating two current states;
11. valid signature bypassing unresolved correspondence;
12. loss of clean next-generation liveness.

## Acceptance rule

Pilot 19 may receive `BOUNDED_PASS` only if P19-01..P19-16 all pass on one explicit frozen implementation SHA and the complete governed-platform regression suite passes on that same SHA. Every crash boundary must be externally parent-triggered. The first frozen-head result must be preserved before any diagnosis-bound repair. CI success alone is not scientific proof; endpoint/log correspondence must be checked.

No repair may weaken a crash boundary, expected outcome, authority separation, reconciliation rule, or acceptance criterion.

## Explicit non-claims

Even a bounded pass will not prove:

- physical power-loss or storage-controller flush guarantees;
- filesystem semantics across all platforms/filesystems;
- OS-user/admin-domain separation;
- KMS/HSM nonextractability;
- security after joint compromise of ledger, anchor and signer key;
- remote/distributed two-store consensus;
- Byzantine fault tolerance;
- hardware attestation;
- production/release/deploy/completion authority.

## Next execution rule

Implement only the frozen Pilot 19 two-store crash/reconciliation mechanism and P19-01..P19-16 on a new isolated branch based on the Pilot 18 adjudicated continuation. Freeze one explicit candidate SHA before scientific exposure and preserve the first frozen-head result before any repair.
