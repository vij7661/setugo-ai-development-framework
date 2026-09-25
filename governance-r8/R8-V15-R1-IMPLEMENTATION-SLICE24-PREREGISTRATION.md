# R8 v15-r1 — Implementation Slice 24: Local ANYScopePermission Validation

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
Implement exact local structural validation of ANYScopePermission fields, enum/list/Sequence syntax, with all currentness and constitutional permission invariants left unproven.

This slice is structure/syntax only. It must fail closed on malformed input and must not implement
or imply currentness, authorization, qualification, semantic selection, or cross-slice integration.

## 3. Frozen acceptance invariants
- I24-01 exact required-field parity.
- I24-02 valid structurally complete permission passes.
- I24-03 top-level non-Mapping/missing/extra reject.
- I24-04 required ID/digest strings reject non-string/empty/non-NFC/noncharacter.
- I24-05 allowed_any_tuple_components must be a list; empty list is allowed by frozen schema.
- I24-06 list elements must be exact ScopeComponentName enum values.
- I24-07 duplicate list elements reject.
- I24-08 effective_sequence accepts 0..INT64_MAX and rejects bool/non-int/out-of-range.
- I24-09 lifecycle enum ACTIVE|SUSPENDED|RETIRED|REVOKED closure.
- I24-10 opaque non-SHA digests pass structurally.
- I24-11 ACTIVE declaration does not prove current validity at decision sequence.
- I24-12 ANY coverage for SemanticEntry positions remains unverified.
- I24-13 constitutional evidence and anti-broadening invariants remain unverified.
- I24-14 result metadata grants authority NONE.
- I24-15 failure does not poison later validation.
- I24-16 frozen schema/closed Slice 1-7 modules unchanged; inherited 140-test baseline stays green.

## 4. Nonclaims
- permission currentness
- decision-sequence effectiveness
- SemanticEntry ANY coverage
- constitutional evidence correctness
- permission broadening authority
- semantic selection
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
validator -> require I24 16/16 + inherited baseline 140/140 -> freeze exact candidate -> continue
only while the active adaptive-cadence rule remains satisfied.
