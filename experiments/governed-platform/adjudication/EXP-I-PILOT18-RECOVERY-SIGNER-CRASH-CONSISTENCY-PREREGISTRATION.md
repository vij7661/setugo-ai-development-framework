# EXP-I Pilot 18 — Recovery-Signer Crash Consistency

## Status

PREREGISTERED — IMPLEMENTATION NOT YET EXPOSED

## Parent result

EXP-I Pilot 17 is a bounded pass at evaluated SHA `9e409e411c3fd5e4c2a1b9b9ac90d0145f7d6141`, run `34054524172`, job `101543820461`. P17 isolated recovery-authorization signing in a distinct process with durable issuance memory and signer-derived permit semantics. The next unproven boundary is abrupt process death during issuance itself.

## Falsification question

If the recovery signer is externally terminated at precise issuance transaction boundaries, can restart/retry create a false permit, duplicate logically distinct permits, lose durable issuance memory, rebind a recovery identity, or cause an ambiguous issuance to mutate the trusted minimum? Can a post-commit/pre-response kill replay the exact same signed permit without duplicate authority?

## Frozen failure mechanism

- A parent test process launches a distinct recovery-signer child process.
- Child reports precise readiness only after reaching the preregistered boundary.
- Parent performs external hard termination; child does not self-terminate and injected exceptions are not substitutes.
- Recovery/replay occurs from a fresh signer process opening the durable issuance store.
- Minimum mutation remains delegated to the Pilot 16 minimum-authority process, which independently verifies the permit at use time.

## Frozen crash boundaries

1. before issuance transaction begins;
2. after issuance transaction begins but before ledger insert;
3. after signed permit material and issuance row are inserted but before commit;
4. after issuance commit but before response delivery;
5. after durable exact issuance when a same-ID semantic rebind is attempted;
6. replay after post-commit response loss;
7. concurrent recovery/retry after killed signer.

## Frozen scientific vectors

- **P18-01** — Readiness protocol proves a distinct child signer and parent-controlled external termination.
- **P18-02** — Kill before issuance transaction leaves no issuance row and no permit authority.
- **P18-03** — Kill after transaction begin before insert leaves no issuance row after fresh reopen.
- **P18-04** — Kill after issuance insert/signature generation before commit rolls back the row after fresh reopen.
- **P18-05** — Kill after durable issuance commit before response preserves exactly one issuance record.
- **P18-06** — Retry after post-commit/pre-response kill returns the exact same permit and signature.
- **P18-07** — Same recovery identity cannot be semantically rebound after the killed post-commit issuance.
- **P18-08** — A killed pre-commit issuance cannot be treated by the minimum-authority process as authorization.
- **P18-09** — A durable post-commit issuance remains subject to minimum-side use-time state revalidation; later state drift blocks stale use.
- **P18-10** — Two retry clients after killed post-commit issuance converge on one exact permit/signature and one ledger identity.
- **P18-11** — Repeated signer restart/reopen cannot erase issuance/rebinding memory.
- **P18-12** — Stale issuance-store snapshot substitution after a newer durable issuance is detected or fails closed against an independent signer trusted-minimum/issuance checkpoint; it must not silently resurrect a pre-issuance state.
- **P18-13** — Signer outage after a pre-commit kill yields no new permit and zero trusted-minimum mutation.
- **P18-14** — Caller semantic injection remains ineffective across crash/retry recovery.
- **P18-15** — Models, reviewers, root/minimum/registry surfaces retain zero signer/minimum/release/deploy/production authority through crash recovery.
- **P18-16** — After crash/replay recovery of R1→R2, a clean signer-derived R2→R3 permit and minimum advancement remains live.

## Acceptance rule

Pilot 18 may receive `BOUNDED_PASS` only if all P18-01..P18-16 pass on one frozen implementation SHA and the complete governed-platform regression suite passes on that same SHA. Every crash boundary must be externally parent-triggered. CI success alone is not a scientific pass.

First frozen-head failure must be preserved and classified before any repair. No repair may change a frozen boundary, expected outcome, authority rule, or acceptance criterion.

## Explicit non-claims

Even a bounded pass will not prove:

- physical power-loss or storage-controller durability;
- OS-user/admin-domain separation;
- KMS/HSM nonextractability;
- security after joint compromise of signer key/store and any independent anti-rollback anchor;
- remote multi-system atomicity;
- multi-host/Byzantine consensus;
- production/release/deploy/completion authority.

## Next execution rule

Implement only this frozen crash mechanism and P18-01..P18-16 on an isolated branch. Freeze one explicit candidate SHA before scientific exposure. Preserve the first frozen-head result before any diagnosis-bound repair.
