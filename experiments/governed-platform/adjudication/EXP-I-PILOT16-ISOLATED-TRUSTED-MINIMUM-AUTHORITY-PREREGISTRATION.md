# EXP-I Pilot 16 — Isolated Trusted-Minimum Authority

## Status

PREREGISTERED — IMPLEMENTATION NOT YET EXPOSED

## Parent result

EXP-I Pilot 15 is a bounded pass at evaluated SHA `d44bf958d327547fd5185adfacec19f47f2e5b6a`, run `34053521072`, job `101541223130`: P15-01..P15-16 passed and the governed-platform suite passed 1042/1042. Pilot 15 proved crash-consistent fail-closed behavior across the tested same-host separate-store root rotation boundaries, but the trusted-minimum mutation surface is still not isolated behind its own authority process.

## Falsification question

If trusted-minimum advancement is moved behind a distinct platform-owned process and durable store, can any root signer, root-trust writer, registry writer, model, reviewer, stale recovery client, or replayed request cause the trusted minimum to advance, roll back, or rebind without an exact platform recovery authorization?

## Frozen architecture boundary

1. Root-trust history remains a separate durable store.
2. Trusted-minimum state remains a separate durable store owned by a dedicated minimum-authority process.
3. The minimum-authority process alone may mutate trusted-minimum state.
4. Root signers, root-trust writers, registry writers, models, and reviewers do not receive the minimum-authority mutation key or direct mutation API.
5. A platform recovery-authority surface may issue a one-step recovery authorization binding:
   - recovery authorization identity;
   - current minimum epoch and digest;
   - exact target root epoch and root-record digest;
   - exact target root ID and public-key fingerprint;
   - exact predecessor root-record digest;
   - exact transition identity and activation registry epoch.
6. The minimum-authority process independently validates the authorization and current durable state at use time before mutation.
7. Exact successful replay is idempotent; semantic rebinding under the same authorization identity is denied.
8. No Pilot 16 state is production, release, deploy, or completion authority.

## Frozen scientific vectors

- **P16-01** — Dedicated minimum-authority process is distinct from root signer, root-trust writer, registry writer, and caller process; minimum store is durable and separately opened by that process.
- **P16-02** — Root signer/root-trust writer/registry writer ordinary surfaces expose neither the minimum mutation secret nor the minimum-authority direct advance operation.
- **P16-03** — Clean exact R1→R2 transition plus exact platform recovery authorization advances minimum from epoch 1 to epoch 2.
- **P16-04** — Missing recovery authorization is denied before minimum mutation.
- **P16-05** — Forged recovery authorization is denied before minimum mutation.
- **P16-06** — Current-minimum epoch or digest substitution is denied.
- **P16-07** — Target root-record digest substitution is denied.
- **P16-08** — Target root ID, public-key fingerprint, predecessor digest, transition identity, or activation-epoch substitution is denied.
- **P16-09** — Exact successful recovery-authorization replay is idempotent and returns the same durable minimum binding.
- **P16-10** — Same recovery authorization identity cannot be semantically rebound to a different target transition.
- **P16-11** — Old valid recovery authorization below the current trusted minimum is denied after the minimum advances.
- **P16-12** — Minimum-authority process outage leaves an ambiguous newer root fail-closed and causes zero minimum mutation.
- **P16-13** — Minimum-authority restart preserves the trusted minimum and replay/rebinding memory.
- **P16-14** — Two recovery clients racing the same exact authorization converge on one durable minimum binding; duplicate authority is not created.
- **P16-15** — Models, reviewers, root signers, root-trust writers, and registry writers retain zero minimum/release/production authority even if they request or claim it.
- **P16-16** — After exact R1→R2 recovery, a clean separately authorized R2→R3 transition remains live.

## Acceptance rule

Pilot 16 may receive `BOUNDED_PASS` only if all P16-01..P16-16 pass on one frozen implementation SHA and the complete governed-platform regression suite passes on that same SHA. CI success alone is not a scientific pass; every frozen endpoint must be present in retained evidence.

Any first-run failure must be preserved and classified before repair. A repair may not change a frozen endpoint, authority boundary, expected outcome, or acceptance rule.

## Explicit non-claims

Even a bounded pass will not prove:

- OS-user or administrator separation merely from process separation;
- hardware-backed KMS/HSM protection or nonextractability;
- protection if the independent platform recovery-authorization key and minimum-authority store are both compromised;
- physical power-loss guarantees;
- remote multi-system atomicity;
- multi-host/Byzantine consensus;
- production/release/deploy/completion authority.

## Next execution rule

Implement only this frozen mechanism and P16-01..P16-16 on an isolated branch. Freeze one explicit candidate SHA before scientific exposure. Preserve the first frozen-head run before any diagnosis-bound repair.
