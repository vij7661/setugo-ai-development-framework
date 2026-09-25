# R8 v15-r1 — Implementation Slice 22: Local CanonicalScopeTuple Validation

Status: **PREREGISTERED BEFORE ACCEPTANCE HARNESS OR MECHANISM IMPLEMENTATION**

## 1. Governance baseline
Active adaptive review-cadence anchor:
`b29619c9307c2a30562a2253f88d052a00bfea6a`

Prior closed governance batch anchor:
`613ad12b29704f44f036e1a275403f58011ae203`

Frozen executable-schema candidate:
`f93ca26975ecb64f0da13779889c75b36140cdfc`

Closed implementation baseline remains Slice 7:
`751162ee42c603cb6c84ee12021d16bab6fa626b`

This is one of at most six low-risk sibling construction slices under
`R8V15R1-REVIEW-CADENCE-ADAPTIVE-001`. No sibling grants dependency authority.

## 2. Goal
Implement exact nine-field CanonicalScopeTuple structure with each component locally validated as ScopeComponent syntax.

This slice is structure/syntax only. It must fail closed on malformed input and must not implement
or imply currentness, authorization, qualification, semantic selection, or cross-slice integration.

## 3. Frozen acceptance invariants
- I22-01 exact required-field parity and frozen canonical-order list.
- I22-02 valid nine-component tuple passes.
- I22-03 top-level non-Mapping rejects.
- I22-04 missing field rejects.
- I22-05 extra field rejects.
- I22-06 every component accepts exact ANY.
- I22-07 every component accepts stable GCP-valid non-ANY string.
- I22-08 empty/non-string component rejects.
- I22-09 non-NFC/noncharacter component rejects.
- I22-10 result preserves frozen canonical component order metadata.
- I22-11 no permission/currentness is inferred from ANY.
- I22-12 validation is deterministic.
- I22-13 failure does not poison later validation.
- I22-14 result metadata grants authority NONE.
- I22-15 no sibling validator dependency is used.
- I22-16 frozen schema/closed Slice 1-7 modules unchanged; inherited 140-test baseline stays green.

## 4. Nonclaims
- ANY permission validity
- scope matching
- scope relation
- scope currentness
- semantic selection
- constitutional authority
- runtime qualification
- evidence promotion
- release
- deployment
- production
- policy authority
- terminal authority

## 5. Early-review trigger screen
No mandatory early-review trigger is intentionally crossed by this slice:
- no frozen-schema mutation;
- no authority-bearing selection/transition logic;
- no constitutional/policy/root/terminal authority;
- no runtime qualification or attestation verification;
- no evidence promotion;
- no resolver qualification;
- no cryptographic trust/currentness/revocation semantics;
- no external effect;
- no cross-slice integration/dependency authority;
- no concurrency/replay/distributed-state semantics;
- no freshness/current-state semantics.

If implementation or test evidence contradicts this screen, construction must stop for early review.

## 6. Construction sequence
Preregister -> freeze harness/workflow with absent mechanism -> preserve RED -> implement narrow
validator -> require I22 16/16 + inherited baseline 140/140 -> freeze exact candidate -> continue
only while the active adaptive-cadence rule remains satisfied.
