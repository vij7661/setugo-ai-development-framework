# V24 I11 V6 R6 — Effect-Class and Durable-Ledger Closure Construction Evidence

Status: **CONSTRUCTION COMPLETE / QUALIFICATION NOT GRANTED**

Authority effect: `NONE_EVIDENCE_ONLY`

## Lineage

Branch: `implementation/v24-i11-v6-r6-effect-ledger-closure`

Validated construction head: `076b2d5dd45f48294c891220539bd2020547bd73`

Validated tree: `c12bff936a7219f9631a9941f6183811f934f4cb`

Parent implementation lineage includes R5 construction evidence commit `b26ff417b54572872466772730837856d3bc0692` and ultimately frozen I10 `9836dc3ff233cca582f485434fc1c6494cf7eb05`.

## Implemented mechanisms

- omission-sensitive `EffectClassRegistry` successor validation;
- independently derived effect-class obligation set from current implementation, deployment, and effect-observation source surfaces;
- exact expected/actual set equality through the inherited generic `RegistryCompletenessQualificationRecord` validator;
- unknown/unregistered material effect classes block effect-path classification;
- stale/unqualified effect-class verifier entries block registry qualification;
- durable material-observation and completeness-ledger validation with monotonic sequence, predecessor chain, record digests and cumulative root;
- durable storage and durable anchor classes are mandatory; process-memory/local unanchored heads cannot qualify;
- fork/rollback detection is fail-closed;
- exact current head qualification and currentness are mandatory;
- witness-currentness records bind exact head/sequence, evidence class, currentness rule, independence qualification and witness digest;
- at least one current independent witness outside the operator control domain is required.

## CI

Workflow: `V24 V6 R6 Effect Ledger Closure`

Run: `34754633242`

Result: **SUCCESS**

Validated head: `076b2d5dd45f48294c891220539bd2020547bd73`

Environment: exact Python `3.12.7`.

Passed:
- R6 construction tests: 14/14;
- R1-R5 successor regression;
- inherited material/authority-universe regression;
- inherited admission/application/witness regression;
- anti-case-specific / anti-caller-authority gate;
- construction-only authority assertion.

## Scientific status

No WDPC scientific case was rerun. Historical V24 I11 PASS/RED/blocked/unresolved records remain unchanged and append-only.

WDPC-469 and WDPC-495 remain blocked by I1 semantic qualification. WDPC-503 remains static/manual unresolved.

## Disposition

`R6_CONSTRUCTION = PASS`

`R6_RUNTIME_QUALIFICATION = NOT_CLAIMED`

`V24_I11_SUCCESSOR_SCIENTIFIC_EXECUTION = NOT_PERMITTED_YET`

The next workstream must descend from this evidence commit. This construction record grants no runtime, release, deployment, production, or terminal authority.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`

## Post-review proof-resolution remediation — 2026-09-15

This append-only addendum records two later R6 false-greens discovered during independent proof-resolution review.

### Preserved failure 1 — durable ledger authority

Run `35004577898`: **FAILURE / genuine false-green**.

The durable ledger accepted a caller-supplied qualified/current head plus an independent/current witness using opaque labels and digest-shaped references. Earlier repaired workstreams R2-R5 remained GREEN.

R6 was repaired so exact governed proofs are required for:
- durable head qualification and currentness;
- storage qualification/currentness;
- durable-anchor qualification, independence, and currentness;
- witness-record qualification, witness-identity independence, and witness currentness;
- effect-class derivation mechanism qualification, derivation-authority independence, and currentness;
- effect-class registry and verifier qualification/currentness;
- registry completeness dependencies and the qualified registry result consumed by an effect path.

### Preserved failure 2 — registered effect-class substitution

Run `35005205305`: **FAILURE / genuine digest-binding defect**.

After the first R6 repair, changing `effect_class_id` from one valid registered class to another could reuse an old opaque `path_content_digest` and currentness proof. All repaired R2-R6 suites passed; only the new substitution falsification failed.

The narrow repair introduced canonical effect-path content binding over the path writer, sink, effect class, writer admission, capability, guard, sink writer set, material-surface membership, observation head, dependency edges, and control-plane evidence. Any material path mutation now changes the content digest and requires fresh currentness evidence.

Run `35005595286`: **SUCCESS**, closing the second R6 defect while preserving all earlier regressions.

All-up proof-resolution run `35007121039`: **SUCCESS** for R2-R8 plus permanent false-green regressions.

R9 dependency-closure run `35007800567`: **SUCCESS** with R6 unchanged and protected by the widened successor freeze.

Remediated R6 production blob at this evidence update: `29a4fdd0f04e3fbfc3308367f0e788a7a690ebf7`.

No WDPC scientific case was run. Runtime qualification remains `NOT_CLAIMED`; scientific execution remains closed pending successor review.

`R6_POST_REVIEW_PROOF_RESOLUTION = PASS`

`R6_RUNTIME_QUALIFICATION = NOT_CLAIMED`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
