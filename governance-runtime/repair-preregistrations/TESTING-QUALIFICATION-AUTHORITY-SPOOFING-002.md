# TESTING-QUALIFICATION-AUTHORITY-SPOOFING-002 — Authority provenance and phase ownership repair

## Status

`PREREGISTERED_BEFORE_MECHANISM_CHANGE`

## Phase

`TESTING`

## Exact preserved RED

- candidate SHA: `d415d60cbb29d1943ef926fea384aa91c9be2043`
- workflow run: `34438867816`
- result: `FAILURE`
- observed failures: four frozen manual regressions

## Source findings

Manual review `TESTING-QUALIFICATION-OWNERSHIP-MANUAL-REVIEW-001` found two material defects:

1. `MR-001`: privileged role strings are caller-asserted content and can impersonate `HUMAN_GOVERNANCE_OWNER` or `INDEPENDENT_GOVERNANCE_ADJUDICATOR`.
2. `MR-002`: caller-selected `violated_contract_phase` can convert a TESTING defect into a later-phase deferral.

The corrected unittest bridge produced genuine RED for all four frozen attack cases. The frozen regression file MUST NOT be weakened or rewritten to obtain green.

## Repair invariant

A naked caller string, boolean, or mapping MUST NOT become privileged authority or phase-classification evidence merely because it contains an accepted label.

## Required narrow repair

### MR-001

Privileged decisions must consume a platform-issued authority binding rather than naked role strings. The binding must be scoped to:

- exact candidate SHA;
- qualification policy ID/version/hash;
- decision/action scope;
- authority class;
- trusted manual-governance evidence reference.

The runtime may reconstitute an in-process capability from durable manually attested evidence, but candidate-authored content must not directly mint or substitute that capability.

### MR-002

Phase classification must resolve from a platform-owned governed rule/contract ID to its owning phase. A caller-provided phase label without a governed rule mapping must fail closed as `REQUIREMENT_UNRESOLVED` and cannot produce `DEFERRED_TO_RELEASE` or `DEFERRED_TO_PRODUCTION`.

## Acceptance

1. Preserve run `34438867816` and the four failing regressions as historical RED.
2. Make the unchanged frozen spoofing regression file pass only by mechanism repair.
3. Ensure all ownership module-level tests are actually executed through the unittest bridge.
4. Run phase-policy, review-protocol, ownership, manual RED, and terminal-authority regressions.
5. Construction green is not scientific closure; exact-SHA manual re-falsification remains required afterward.
