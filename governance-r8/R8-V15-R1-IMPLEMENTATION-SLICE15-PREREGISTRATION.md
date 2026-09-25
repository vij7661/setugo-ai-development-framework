# R8 v15-r1 — Implementation Slice 15: Local ResolverConformanceAggregateResult Validation

Status: **PREREGISTERED BEFORE ACCEPTANCE HARNESS OR MECHANISM IMPLEMENTATION**

## 1. Baseline
Governance-only batch 11–13 closure anchor:
`0441370a1d9f2d80a75926839294eb5fba32faaf`

Frozen executable-schema candidate:
`f93ca26975ecb64f0da13779889c75b36140cdfc`

Closed implementation baseline remains Slice 7:
`751162ee42c603cb6c84ee12021d16bab6fa626b`

Slice 14 is independently frozen for the next combined review but grants no dependency authority to Slice 15.

## 2. Goal
Implement a repository-local pure validator for `ResolverConformanceAggregateResult`.

The validator proves only exact frozen field shape, PASS/FAIL enum closure, integer bounds, and a non-empty GCP-valid opaque aggregate digest. It does not infer aggregate semantics not frozen in the schema.

## 3. Frozen fields
Exact required fields:
- status
- vector_count
- passed_vector_count
- aggregate_digest

No extras allowed.

`status` is exactly PASS | FAIL.
`vector_count` is a non-boolean integer 1..INT64_MAX.
`passed_vector_count` is a non-boolean integer 0..INT64_MAX.
`aggregate_digest` is a non-empty GCP-valid opaque Digest.

The frozen schema does not require passed_vector_count <= vector_count and does not define an aggregate status formula. This slice does not invent those rules.

## 4. Frozen invariants
I15-01 exact required-field parity.
I15-02 valid PASS aggregate passes.
I15-03 valid FAIL aggregate passes.
I15-04 missing field rejects.
I15-05 extra field rejects.
I15-06 status enum is exactly PASS | FAIL.
I15-07 vector_count accepts 1..INT64_MAX.
I15-08 vector_count rejects 0/negative/max+1/bool/non-int.
I15-09 passed_vector_count accepts 0..INT64_MAX.
I15-10 passed_vector_count rejects negative/max+1/bool/non-int.
I15-11 aggregate_digest rejects empty/non-string/non-NFC/noncharacter values.
I15-12 opaque non-SHA aggregate_digest passes.
I15-13 no passed<=vector_count or status/count relation is invented locally.
I15-14 result metadata grants authority NONE; digest/aggregate semantics/conformance remain unverified.
I15-15 failure does not poison later validation.
I15-16 frozen schema/closed Slice 1–7 implementation modules unchanged; inherited 140-test baseline stays green; workflow directly covers governed/executed paths.

## 5. Nonclaims
No vector-count correctness, passed-count consistency, aggregate status correctness, aggregate digest correctness, conformance qualification, resolver authorization, runtime qualification, evidence promotion, release, deployment, production, policy authority, or terminal authority.

## 6. Construction sequence
Preregister -> freeze harness/workflow with absent mechanism -> preserve RED -> implement narrow validator -> require I15 16/16 + inherited baseline 140/140 -> freeze exact candidate -> do not independently review until Slice 16 also completes.
