# R8 v13 Independent Design Review — Adjudication

Status: **CHANGES_REQUIRED — SUCCESSOR DESIGN + NORMALIZATION GATE REQUIRED**
Authority effect: **NONE**

Reviewed candidate:
- R8 v13 design commit: `57a3be6ad7c38ad773017c77e74dc72339d51e6e`
- R8 v13 design blob: `841556341da618fa6ed0b7c4be2797d522be4696`
- GuardRegistry-1 commit: `84bb9abe04debbcc441580871a74f641d6e30eb2`
- GuardRegistry-1 blob: `baeff37ecbc878a20a84970cd2c058bb052845b9`
- blind packet commit: `5b42565eae91edcd6105434b9c0a297749f28233`
- blind packet blob: `257212123dfad08cb94c5f03ed3f7a03cc3a21fb`

Independent review evidence:
- preserved at `review-evidence/R8-V13-META-GOVERNANCE-INDEPENDENT-DESIGN-REVIEW.md`
- disposition: `CHANGES_REQUIRED`
- authority effect: `NONE`

## 1. Overall adjudication

The review is materially valid.

R8 v13 closed the previous policy-to-implementation, scope-replacement, revoked-Smax, AIM applicability-shape, state-root, barrier-taxonomy, and guard-registry gaps. However one concrete false-green path remains in AIM applicability ordering, together with several deterministic-closure and packet-reproducibility gaps.

The project will therefore change remediation strategy:

> R8 v14 will be followed by an internal normalization/closure gate before any new independent review packet is created.

The next external reviewer will not receive another overlay-only bundle. The review subject will be a single normalized effective specification plus deterministic support artifacts.

## 2. Accepted critical blocker

### V13-C1 — AIM ANY filtering occurs before AIM_Smax
**ACCEPTED — BLOCKER**

R8 v14 must:
1. form the full set of effective, scope-matching AIM descriptors without filtering invalid ANY permission;
2. derive AIM specificity;
3. compute AIM_Smax;
4. evaluate current AIM ANY-permission validity at AIM_Smax;
5. if any AIM_Smax descriptor has invalid/narrowed/revoked ANY permission, return `AIM_SCOPE_PERMISSION_REEVALUATION_REQUIRED`;
6. prohibit lower-specificity fallback.

This must mirror the semantic-entry no-fallback principle.

## 3. Accepted high findings

### V13-H1 — RIR effective sequence
**ACCEPTED**

An RIR record is usable only when:
- `activation_sequence <= semantic_state_sequence`; and
- `retirement_or_revocation_sequence == null || retirement_or_revocation_sequence > semantic_state_sequence`.

Lifecycle label alone is insufficient.

### V13-H2 — canonical semantic-result equivalence
**ACCEPTED**

R8 v14 must define one CSM-bound `SemanticResultEquivalencePolicy`.

Equivalent result comparison may not be implementation-local prose.

### V13-H3 — required BSP/guard omission manifests absent from packet
**ACCEPTED**

The next blind packet must embed or directly attach:
- the projection manifest;
- guard-table omission manifest;
- source digests;
- residual-scan outcome;
- removed-section digests.

No reviewer should need to trust an out-of-band claim that the projection is complete.

### V13-H4 — BSP classifier grammar not exact
**ACCEPTED**

Freeze exact deterministic grammar/pattern rules.

Version-aware blindness must be reproducible by independent tooling.

## 4. Accepted medium findings

### V13-M1 — SRTT total table
**ACCEPTED**

R8 v14 must freeze either:
- every Cartesian branch explicitly; or
- a deterministic generator whose algorithm and output digest are frozen before independent review.

### V13-M2 — RCS freshness
**ACCEPTED**

Conformance evidence must have exact validity semantics:
- invalidated by bound policy/implementation/runtime/suite change;
- optionally sequence/age bounded where configured;
- cannot survive record revocation;
- fresh evidence required after qualifying-state changes.

### V13-M3 — state-root typo
**ACCEPTED**

Correct `semantic_state_sequence_i:i` to `semantic_state_sequence_i`.

### V13-M4 — omission proof
**ACCEPTED**

Guard-table omission must have machine-verifiable proof that:
- every omitted guard remains in GuardRegistry;
- unique case semantics remain present in normalized spec;
- no omitted section contains unique non-table invariants.

## 5. Process-level finding

Repeated reviews are converging but the overlay-only workflow has become inefficient.

R8 v14 therefore introduces a mandatory **Normalization and Closure Gate (NCG-1)** before another external review.

NCG-1 must produce:
1. one normalized effective current specification;
2. one invariant/dependency matrix;
3. one evaluation-order matrix;
4. one state/registry ownership matrix;
5. one cross-mechanism adversarial corpus;
6. one unresolved-contradiction report;
7. one deterministic guard/case registry;
8. one review-projection completeness report.

No fresh external review packet may be frozen until NCG-1 reports zero unresolved material contradictions.

## 6. Successor rule

Create R8 v14 as a new successor overlay and normalization layer.

Do not mutate v4-v13.

Do not start executable-schema freeze.

Do not create the final v14 independent-review packet until NCG-1 is complete and internally clean.

Until then:
- R8 v1-v13 = `CHANGES_REQUIRED`
- R8 v14 = `NOT_IMPLEMENTED / INTERNAL_NORMALIZATION_REQUIRED`
- executable-schema freeze = `BLOCKED`
- PR #39 = `NON_AUTHORITATIVE`
- PR #40 = `NON_AUTHORITATIVE`
- authority effect = `NONE`
