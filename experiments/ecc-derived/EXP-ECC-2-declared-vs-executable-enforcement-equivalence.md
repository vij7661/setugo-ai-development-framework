# EXP-ECC-2 — Declared-vs-Executable Enforcement Equivalence

Status: **PREREGISTERED — NOT EXECUTED**

Authority effect: **NONE_EVIDENCE_ONLY**

Baseline: `290ac043959f30db12c9ae16826eda1dd5bcbdfb`

## Hypothesis

A documentation/skill/policy claim such as `always blocks`, `cannot skip`, `mandatory`, or `fail closed` cannot qualify unless the executable mechanism and its real failure semantics are mechanically equivalent to that claim.

## Required mechanism

Each consequential declared control maps to a machine-readable `DeclaredEnforcementContract` and an `ExecutableEnforcementProfile` bound to exact implementation/version/runtime. A deterministic equivalence checker must reject semantic widening by documentation or silent weakening by code.

## Falsification cases

- E2-01 declaration says fail closed while wrapper catches internal errors and continues.
- E2-02 declaration says mandatory while control can be disabled by an undocumented environment flag.
- E2-03 documentation says exact candidate binding but executable checks only branch/name.
- E2-04 docs claim blocking while runtime only emits telemetry/warning.
- E2-05 implementation changes from blocking to advisory without contract-version change.
- E2-06 generated/translated documentation remains stronger than canonical executable contract.
- E2-07 multiple execution paths exist and only one enforces the declared invariant.
- E2-08 code path enforces more narrowly than docs and a caller relies on the broader claim.

## Positive controls

- E2-P1 executable and declared fail-closed behavior match exactly.
- E2-P2 a deliberately advisory control is truthfully declared advisory and remains usable.
- E2-P3 a controlled contract change updates both declaration and executable profile without rewriting prior history.

## Pass condition

No stronger declaration may be promoted from a weaker executable mechanism, and no missing/unverifiable executable profile may be interpreted as equivalent.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
