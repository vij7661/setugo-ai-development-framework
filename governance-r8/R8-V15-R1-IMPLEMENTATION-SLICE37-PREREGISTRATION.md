# R8 v15-r1 — Implementation Slice 37: Composite Guard-Omission Evidence + Manifest Family

Status: **PREREGISTERED BEFORE ACCEPTANCE HARNESS OR MECHANISM IMPLEMENTATION**

## Governance baseline
Closed Slices 29–34 governance anchor:
`09fd9c34077b7e1a5a5cad48d76278117845e704`

Restored adaptive cadence anchor:
`dfdeceb297b0eefe54d3a47edc3ae16a6f624ded`

Frozen schema candidate:
`f93ca26975ecb64f0da13779889c75b36140cdfc`

Closed implementation baseline remains Slice 7:
`751162ee42c603cb6c84ee12021d16bab6fa626b`

Maximum unreviewed low-risk slices: **6**.

## Composite-slice rationale
This family shares one structural risk boundary and is intentionally grouped to reduce administrative
slice count. The harness must identify each nested/root invariant group independently. No nested
definition may gain authority from being grouped with another.

## Goal
structurally validate guard-omission source evidence and omission manifest roots/records in one composite slice.

## Acceptance posture
- exact required/additionalProperties/const/enum/type/cardinality semantics;
- exact JSON uniqueItems only where the frozen schema declares it;
- ECMA-regex behavior implemented without Python Unicode-\d widening;
- JSON booleans/integers kept type-distinct;
- declared open objects remain open and are not semantically interpreted;
- deterministic validation and non-poisoning after failure;
- no imports from unreviewed sibling slices;
- all authority/currentness/qualification/recomputation metadata fail closed.

## Explicit nonclaims
- source excerpt digest recomputation
- guard/case set equality recomputation
- current registry membership
- source existence
- reverification execution
- evidence promotion
- runtime qualification
- evidence promotion
- release/deployment/production
- policy/constitutional/root/terminal authority

## Early-review trigger screen
This is structural construction only. It performs no currentness decision, cryptographic trust
verification, evidence promotion, external effect, parser/graph semantic execution, attestation
verification, cross-registry authority decision, or cross-slice dependency authority.

If implementation crosses that boundary, stop for early review.

## Construction sequence
Preregister -> frozen family harness/workflow -> scientific RED -> narrow family validator -> GREEN ->
exact-candidate GREEN -> freeze. Fresh independent review is required after Slice 40 or earlier if a trigger fires.
