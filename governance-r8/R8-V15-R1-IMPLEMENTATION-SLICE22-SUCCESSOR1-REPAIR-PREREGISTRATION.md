# R8 v15-r1 — Slice 22 Successor-1 Repair Preregistration

Status: **PREREGISTERED_REPAIR_BEFORE_SUCCESSOR_HARNESS_OR_MECHANISM_CHANGE**

## Binding
Rejected exact candidate:
`8ecdd17ce80549f87dd15bbe1fc29414272b6253`

Triggering independent review:
`governance-r8/R8-V15-R1-IMPLEMENTATION-SLICES20-25-INDEPENDENT-REVIEW-001.txt`

Fallback governance anchor:
`0410aae4f783b84542d0d491d3d1bb6003ad4216`

Frozen schema candidate remains:
`f93ca26975ecb64f0da13779889c75b36140cdfc`

## High finding to repair
CanonicalScopeTuple stable components must enforce referenced StableScopeValue ECMA pattern exactly for every field.

Frozen pattern:
`^(?!ANY$).+`

For this exact frozen pattern under ECMA-style regular-expression semantics:
- exact `ANY` rejects on the StableScopeValue branch;
- an empty string rejects;
- a string whose first scalar is an ECMA line terminator rejects because the leading `.` cannot consume it;
- ECMA line terminators are `U+000A LF`, `U+000D CR`, `U+2028 LS`, and `U+2029 PS`;
- later/trailing line terminators do not by themselves invalidate the pattern because `.+` is not end-anchored;
- therefore `"x\\n"` and `"ANY\\n"` remain pattern matches on the stable branch when represented as actual strings with trailing LF.

## Repair acceptance
Add a successor-only harness that proves:
1. all four leading ECMA line terminators reject;
2. representative trailing ECMA line terminators remain accepted;
3. exact ANY behavior is unchanged;
4. authority/currentness/qualification metadata remains fail-closed.

The original candidate, original harness, RED, GREEN, exact-head GREEN, freeze, and independent review remain immutable historical evidence.

## Scope
This repair is syntax-only. It grants no scope permission, currentness, semantic selection, constitutional authority, runtime qualification, evidence promotion, release, deployment, production, policy, or terminal authority.

## Cadence
This is repair 3 of the active fallback maximum of three. No new Slice 26 construction may begin before the repaired Slices 20–22 receive fresh independent review.
