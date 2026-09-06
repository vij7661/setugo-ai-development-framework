# EXP-I Pilot 17 — Isolated Recovery-Authorization Signer

## Status

PREREGISTERED — IMPLEMENTATION NOT YET EXPOSED

## Parent result

EXP-I Pilot 16 is a bounded pass at evaluated SHA `3727a6cc0972c9995f1b4523b1b9f519ea4ace48`, run `34053851970`, job `101542069597`. Scientific correspondence is established from the exact frozen P16 test file, exact-SHA workflow discovery semantics, exact baseline diff, and successful full governance discovery step; the governed total is derived as 1058/1058 from the P15 1042 baseline plus the only new 16-case governance test file.

Pilot 16 isolated trusted-minimum mutation behind a distinct process, but the recovery-authorization private key remains owned by an in-process platform object. Pilot 17 tests whether recovery authorization can itself be isolated so callers cannot choose or sign governed semantics.

## Falsification question

If recovery-authorization issuance moves behind a distinct platform-owned signer process with a durable issuance ledger, can any caller, minimum-authority process, root signer, root-trust writer, registry writer, model, or reviewer manufacture, widen, stale-replay, or semantically rebind a recovery permit? Can the signer derive the exact next recovery permit from authoritative stores while preserving fail-closed outage/restart/race behavior and positive liveness?

## Frozen architecture boundary

1. A dedicated recovery-signer subprocess owns the recovery Ed25519 private key and durable issuance ledger.
2. Callers, minimum-authority process, root signers, root-trust writers, registry writers, models, and reviewers receive no recovery private key.
3. Caller request surface contains only a recovery identity and a target selector/intent sufficient to identify the desired authoritative transition; callers do not supply governed permit fields.
4. Signer independently reads authenticated root history and trusted-minimum state.
5. Signer derives every governed permit field itself:
   - recovery identity;
   - current minimum epoch/digest;
   - exact target root epoch/digest;
   - target root ID/public-key fingerprint;
   - predecessor digest;
   - transition identity;
   - activation registry epoch.
6. Only the exact contiguous authenticated root immediately above the current minimum is issuable.
7. Exact issuance replay returns the same signed permit; same recovery identity with different target semantics is denied.
8. The Pilot 16 minimum-authority process independently revalidates the signed permit and current durable state at use time before mutation.
9. Successful permit issuance is not itself minimum mutation, release, deploy, production, or completion authority.

## Frozen scientific vectors

- **P17-01** — Recovery signer runs in a distinct process with its own private-key path and durable issuance ledger.
- **P17-02** — Caller, minimum-authority process, root signer, root-trust writer, and registry writer surfaces expose neither recovery private key nor direct permit-sign operation.
- **P17-03** — Clean ambiguous R1→R2 state causes signer to derive and issue the exact contiguous R2 recovery permit from authoritative stores.
- **P17-04** — Caller-supplied semantic fields cannot influence the derived signed permit.
- **P17-05** — Caller-generated or wrong-key forged recovery permit is rejected by the Pilot 16 minimum-authority process.
- **P17-06** — Nonexistent, wrong, or unauthenticated target selector is denied without issuance.
- **P17-07** — Target at or below the current trusted minimum is denied for new issuance.
- **P17-08** — Noncontiguous/future authenticated root target cannot be issued while an earlier ambiguous root remains unresolved.
- **P17-09** — Exact recovery-identity/target replay returns the same permit and signature without duplicate issuance-ledger authority.
- **P17-10** — Same recovery identity cannot be rebound to a different target transition after first issuance.
- **P17-11** — Recovery-signer restart preserves issuance identity, exact replay, and rebinding refusal.
- **P17-12** — Recovery-signer outage blocks new permit issuance and causes zero trusted-minimum mutation.
- **P17-13** — Two callers racing the same exact issuance converge on one durable permit identity/signature.
- **P17-14** — Authoritative minimum/root state drift after issuance is caught by minimum-side use-time verification; stale issued permit cannot mutate newer state.
- **P17-15** — Models, reviewers, minimum-authority process, root signers, root-trust writers, and registry writers retain zero permit-minting/minimum/release/deploy/production authority even if they request or claim it.
- **P17-16** — After exact R1→R2 issuance and minimum advancement, a clean R2→R3 signer-derived permit and minimum advancement remains live.

## Acceptance rule

Pilot 17 may receive `BOUNDED_PASS` only if all P17-01..P17-16 pass on one frozen implementation SHA and the complete governed-platform regression suite passes on that same SHA. CI success alone is not a scientific pass. First frozen-head failure must be preserved and classified before any repair.

A repair may not change a frozen endpoint, expected outcome, authority boundary, target-selection rule, or acceptance rule.

## Explicit non-claims

Even a bounded pass will not prove:

- OS-user or administrator trust-domain separation merely from process isolation;
- KMS/HSM key nonextractability or hardware-backed signing;
- protection if the recovery-signer private key/store and minimum-authority store are jointly compromised;
- physical power-loss guarantees;
- remote/distributed transaction atomicity;
- multi-host/Byzantine consensus;
- production/release/deploy/completion authority.

## Next execution rule

Implement only this frozen mechanism and P17-01..P17-16 on an isolated branch. Freeze one explicit candidate SHA before scientific exposure. Preserve the first frozen-head run before any diagnosis-bound repair.
