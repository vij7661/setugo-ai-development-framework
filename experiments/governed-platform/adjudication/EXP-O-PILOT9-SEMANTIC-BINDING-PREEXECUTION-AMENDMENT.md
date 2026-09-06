# EXP-O Pilot 9 — Pre-Execution Semantic-Binding Amendment

Status: **PRE-REGISTERED BEFORE ANY PILOT 9 PROVIDER EXECUTION**

Original preregistration: `EXP-O-PILOT9-CAUSAL-SEMANTIC-GATE-PREREGISTRATION.md`

## Reason for amendment

Pre-execution code inspection identified a false-green risk in the existing EXP-O runtime path:

1. `evaluate_action_effect(...)` receives `semantic_verified` only as a boolean;
2. `LocalEnforcementPoint.authorize(...)` receives that boolean without a signed verification-evidence object;
3. the gateway permit's `_effect_binding(...)` does not bind any semantic/candidate payload digest.

Therefore the originally planned S0/S1 boolean replay could prove only that the boolean controls the branch. It could not prove that the semantic content independently verified is the same semantic content later authorized and executed.

Executing the original design without closing this gap would risk a false green.

## Pre-execution change classification

This amendment occurs before any Pilot 9 provider call or result exists.

- provider/model/temperature/sample count: unchanged;
- real-model candidate-generation prompt: unchanged;
- action/resource/base/effect-contract scope: unchanged;
- EXP-N isolation: unchanged;
- behavioral endpoint: none, unchanged;
- structural endpoint: **strengthened** from boolean-gate specificity to exact verification-to-effect binding plus causal S0/S1 specificity.

The final Pilot 9 design commit must be created only after the hardened binding and its falsification tests pass.

## Required hardening before provider execution

Pilot 9 must introduce an EXP-O-specific semantic-verification binding layer with all of the following properties:

1. independent semantic verification is represented as a signed platform evidence envelope, not a caller-controlled boolean alone;
2. the verification envelope binds the exact model candidate semantic payload digest;
3. it also binds the exact action, target resources, base SHA and effect-contract ID;
4. the LEP-facing hardened path validates the envelope signature and exact binding before treating semantic correspondence as established;
5. the requested effect carries the exact `semantic_payload_digest`;
6. the gateway permit effect digest includes `semantic_payload_digest`, preventing a permit from being replayed for different semantic content with otherwise identical action/resource metadata;
7. missing, forged, mutated, wrong-candidate or wrong-effect verification evidence fails closed before permit issuance;
8. the S0 phase uses no valid semantic-verification envelope and must deny;
9. the S1 phase uses a valid independently signed envelope bound to the exact unchanged candidate/effect and must permit exactly once.

## Required fail-first falsifier

Before the hardening is accepted, the tests must encode the substitution attack that motivated this amendment:

- semantic candidate A is independently verified;
- candidate B has different semantic content but the same `WRITE src/app.py` action/resource/base/contract metadata;
- B must not be able to reuse A's verification evidence or permit.

The final secure test must fail closed on this substitution.

## Scientific interpretation

A future green Pilot 9 may support only:

> Within the tested local EXP-O path, signed independent semantic-verification evidence was bound to the exact real-model candidate/effect, and toggling from absent/invalid verification to exact valid verification changed the authorization outcome without allowing semantic substitution.

It must not be described as universal semantic correctness, production attestation or general prompt-injection resistance.

## EXP-N isolation

The hardening must use EXP-O-specific files and, if the existing EXP-O permit binding is extended, must not modify any frozen EXP-N Pilot 8 recovery or Pilot 9 protected dependency.