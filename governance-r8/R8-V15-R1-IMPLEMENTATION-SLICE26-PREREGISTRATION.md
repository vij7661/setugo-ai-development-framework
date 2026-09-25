# R8 v15-r1 — Implementation Slice 26: Local AIMScopePolicy Validation

Status: **PREREGISTERED BEFORE ACCEPTANCE HARNESS OR MECHANISM IMPLEMENTATION**

## Governance baseline
Post-remediation governance anchor:
`4a401bdf33786b980364784a0c8a19e20acef2df`

Active fallback cadence anchor:
`0410aae4f783b84542d0d491d3d1bb6003ad4216`

Clean post-remediation review count: **1 of 2**.
Maximum unreviewed low-risk slices: **3**.

Frozen executable-schema candidate:
`f93ca26975ecb64f0da13779889c75b36140cdfc`

Closed implementation baseline remains Slice 7:
`751162ee42c603cb6c84ee12021d16bab6fa626b`

## Goal
Implement exact local AIMScopePolicy structure, nested class-rule syntax, unique semantic_class values, Sequence/lifecycle syntax, with broadening/currentness/constitutional authority unverified.

## Frozen acceptance invariants
- I26-01 exact six required fields and frozen nested references/enums.
- I26-02 structurally valid policy passes.
- I26-03 top-level non-Mapping, missing, and extra fields reject.
- I26-04 required CanonicalId/Digest strings reject non-string, empty, non-NFC, and noncharacter values.
- I26-05 class_rules must be a list with minItems 1.
- I26-06 each class rule must have exactly semantic_class and allowed_any_tuple_components.
- I26-07 nested semantic_class must be non-empty GCP-valid string.
- I26-08 nested allowed_any_tuple_components must be a list of exact ScopeComponentName enum values.
- I26-09 duplicate component names inside one class rule reject.
- I26-10 duplicate semantic_class values across class_rules reject per frozen x-validator invariant.
- I26-11 effective_sequence accepts 0..9223372036854775807 and rejects bool/non-int/out-of-range.
- I26-12 lifecycle_state closes to ACTIVE|SUSPENDED|RETIRED|REVOKED.
- I26-13 opaque non-SHA digest values pass structurally.
- I26-14 ACTIVE declaration does not prove policy currentness/effectiveness; constitutional evidence and anti-broadening authority remain unverified.
- I26-15 failure does not poison later validation and no sibling validator dependency is used.
- I26-16 frozen schema/closed Slice1-7 modules remain unchanged and workflow binds this exact slice.

## Nonclaims
- AIM policy currentness
- policy effectiveness
- project/org/experiment anti-broadening authority enforcement
- constitutional evidence correctness
- ANY permission authority
- semantic selection
- scope authorization
- runtime qualification
- evidence promotion
- release
- deployment
- production
- policy authority
- terminal authority

## Early-review trigger screen
This slice is preregistered as structure/syntax only:
- no frozen-schema mutation;
- no current/effective policy decision;
- no authority-bearing semantic selection or transition decision;
- no constitutional authorization decision;
- no runtime qualification/attestation verification;
- no evidence promotion;
- no resolver qualification;
- no cryptographic trust/currentness/revocation decision;
- no external effect;
- no cross-slice dependency authority;
- no concurrency/replay/distributed-state mechanism;
- no SRTT table lookup or replacement eligibility decision.

If implementation or test evidence contradicts this screen, stop for early review.

## Construction sequence
Preregister -> freeze harness/workflow -> preserve scientific RED -> implement narrow validator ->
require slice acceptance + inherited closed baseline -> freeze exact candidate -> fresh independent review
after Slice 28. No Slice 29 construction before that review.
