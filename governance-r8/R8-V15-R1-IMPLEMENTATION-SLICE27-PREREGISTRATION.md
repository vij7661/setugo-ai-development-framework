# R8 v15-r1 — Implementation Slice 27: Local ScopeReplacementMapping Validation

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
Implement exact local ScopeReplacementMapping structure including two CanonicalScopeTuple-shaped values, specificity bounds, enums and Sequence syntax, without replacement effectiveness or constitutional authorization.

## Frozen acceptance invariants
- I27-01 exact fifteen required fields and frozen enum/reference parity.
- I27-02 structurally valid mapping passes.
- I27-03 top-level non-Mapping, missing, and extra fields reject.
- I27-04 required CanonicalId/Digest strings reject non-string, empty, non-NFC, and noncharacter values.
- I27-05 old_scope_tuple and new_scope_tuple require exact nine-field CanonicalScopeTuple shape.
- I27-06 exact ANY and ordinary stable scope components pass in both tuples.
- I27-07 stable components beginning with LF/CR/U+2028/U+2029 reject in every tuple position; later/trailing terminators remain pattern-valid.
- I27-08 empty/non-string/non-NFC/noncharacter scope components reject.
- I27-09 old_specificity/new_specificity accept integers 0..9 and reject bool/non-int/out-of-range.
- I27-10 old_scope_effect closes to the three frozen values.
- I27-11 effective_sequence accepts 0..9223372036854775807 and rejects bool/non-int/out-of-range.
- I27-12 lifecycle_state closes to ACTIVE|SUSPENDED|RETIRED|REVOKED.
- I27-13 opaque non-SHA digests pass structurally.
- I27-14 object existence, scope relation, mapping effectiveness/currentness, amendment evidence and replacement authority remain unverified; authority effect NONE.
- I27-15 failure does not poison later validation and no sibling validator dependency is used.
- I27-16 frozen schema/closed Slice1-7 modules remain unchanged and workflow binds this exact slice.

## Nonclaims
- source/destination object existence
- old/new specificity correctness relative to tuples
- scope relation
- mapping effectiveness/currentness
- replacement eligibility
- constitutional amendment evidence correctness
- scope expansion authority
- semantic selection
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
