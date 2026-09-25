# R8 v15-r1 — Implementation Slice 28: Local ScopeReplacementOutsideTableInput Validation

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
Implement exact local structural validation of the outside-table input fields and enum/boolean closure, without performing SRTT table lookup or producing replacement-branch authority.

## Frozen acceptance invariants
- I28-01 exact ten required fields and frozen enum/type parity.
- I28-02 structurally valid outside-table input passes.
- I28-03 top-level non-Mapping, missing, and extra fields reject.
- I28-04 source_entry_state closes to ACTIVE|SUSPENDED|SUPERSEDED|RETIRED|SCOPE_PERMISSION_REEVALUATION_REQUIRED.
- I28-05 old_scope_match closes to NO_MATCH|EXACT_MATCH.
- I28-06 destination_scope_match closes to NO_MATCH|EXACT_MATCH|MAPPED_MATCH.
- I28-07 old_scope_effect closes to the three frozen values.
- I28-08 scope_relation closes to SAME|NARROWER|BROADER|DISJOINT.
- I28-09 all five boolean fields require exact bool values and reject numeric/string lookalikes.
- I28-10 all permitted enum cross-products remain structurally accepted; no semantic relation is inferred.
- I28-11 structural validity does not prove mapping effectiveness or permission validity.
- I28-12 structural validity does not perform SRTT table lookup or verify NOT_A_REPLACEMENT_BRANCH.
- I28-13 validation is deterministic.
- I28-14 authority/currentness/qualification metadata remains fail-closed.
- I28-15 failure does not poison later validation and no sibling validator dependency is used.
- I28-16 frozen schema/closed Slice1-7 modules remain unchanged and workflow binds this exact slice.

## Nonclaims
- SRTT table lookup
- NOT_A_REPLACEMENT_BRANCH verification
- mapping effectiveness
- lineage mapping validity
- ANY permission validity
- scope expansion authorization
- decision-inside-expansion authorization
- replacement eligibility
- semantic selection
- constitutional authority
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
