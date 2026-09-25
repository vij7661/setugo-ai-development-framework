# R8 v15-r1 — Implementation Slice 25: Local AIMScopePolicyClassRule Validation

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
Implement exact local structural validation of semantic_class plus unique ScopeComponentName list.

This slice is structure/syntax only. It must fail closed on malformed input and must not implement
or imply currentness, authorization, qualification, semantic selection, or cross-slice integration.

## 3. Frozen acceptance invariants
- I25-01 exact required-field parity.
- I25-02 valid structurally complete class rule passes.
- I25-03 top-level non-Mapping/missing/extra reject.
- I25-04 semantic_class rejects non-string/empty/non-NFC/noncharacter.
- I25-05 allowed_any_tuple_components must be a list; empty list is allowed.
- I25-06 list elements must be exact ScopeComponentName enum values.
- I25-07 duplicate list elements reject.
- I25-08 all nine enum values can coexist once each.
- I25-09 unknown/case-changed/spaced enum values reject.
- I25-10 boolean/numeric elements reject.
- I25-11 no permission currentness or effective policy is inferred.
- I25-12 validation is deterministic.
- I25-13 failure does not poison later validation.
- I25-14 result metadata grants authority NONE.
- I25-15 no sibling validator dependency is used.
- I25-16 frozen schema/closed Slice 1-7 modules unchanged; inherited 140-test baseline stays green.

## 4. Nonclaims
- AIM policy currentness
- ANY permission authority
- semantic selection
- scope authorization
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
validator -> require I25 16/16 + inherited baseline 140/140 -> freeze exact candidate -> continue
only while the active adaptive-cadence rule remains satisfied.
