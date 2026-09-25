# R8 v15-r1 — Implementation Slice 16: Local ResolverConformanceEvidence Validation

Status: **PREREGISTERED BEFORE ACCEPTANCE HARNESS OR MECHANISM IMPLEMENTATION**

## 1. Baseline
Governance-only batch 11–13 closure anchor:
`0441370a1d9f2d80a75926839294eb5fba32faaf`

Frozen executable-schema candidate:
`f93ca26975ecb64f0da13779889c75b36140cdfc`

Closed implementation baseline remains Slice 7:
`751162ee42c603cb6c84ee12021d16bab6fa626b`

Slices 14 and 15 are independently frozen for the next combined review but grant no dependency authority to Slice 16. Slice 16 therefore validates its nested vector-result and aggregate-result shapes directly from the frozen schema rather than importing unreviewed sibling mechanisms.

## 2. Goal
Implement a repository-local pure structural validator for `ResolverConformanceEvidence`.

It validates exact top-level shape, nested RCS-1 suite shape, non-empty vector arrays, nested vector-result structure, nested aggregate-result structure, enum closure, integer bounds, and non-empty GCP-valid opaque IDs/digests.

It does NOT prove any frozen x-validator semantic invariant.

## 3. Frozen top-level fields
Exact required fields:
- rir_record_digest
- rir_record_id
- resolver_policy_digest
- implementation_id
- resolver_implementation_digest
- resolver_runtime_manifest_digest
- runtime_identity_digest
- workload_identity_digest
- conformance_suite_digest
- rcs_suite
- rcs_suite_digest
- rcs_vector_digests
- raw_per_vector_results
- deterministic_aggregate_result
- registry_head_digest
- freshness_profile_id
- status
- evidence_digest

No extras allowed.

`status` is exactly PASS | FAIL | EXPIRED | UNAVAILABLE.
Generic CanonicalId/Digest fields are non-empty GCP-valid opaque strings.
`rcs_vector_digests` is a non-empty list of GCP-valid opaque Digest strings.
`raw_per_vector_results` is a non-empty list of structurally valid frozen ResolverConformanceVectorResult objects.
`deterministic_aggregate_result` is a structurally valid frozen ResolverConformanceAggregateResult object.
`rcs_suite` is a structurally valid frozen ResolverConformanceSuite1 object.

No local array-length/count/status relation is invented beyond the frozen JSON schema.

## 4. Frozen x-validator invariants that remain NONCLAIMS
- rcs_suite.suite_digest == rcs_suite_digest == conformance_suite_digest;
- required resolver runtime/workload identities equal top-level runtime/workload identity digests;
- rcs_vector_digests/raw_per_vector_results bind the exact vector manifest represented by rcs_suite.vector_manifest_digest;
- only current PASS evidence for the exact authorized tuple can qualify resolver;
- cached/stale prior PASS cannot substitute during outage.

All corresponding result metadata must remain false/unverified.

## 5. Frozen invariants
I16-01 exact top-level required-field parity.
I16-02 a valid structurally complete PASS evidence object passes.
I16-03 PASS/FAIL/EXPIRED/UNAVAILABLE are each structurally accepted.
I16-04 missing/extra top-level fields reject.
I16-05 required scalar ID/digest fields reject non-string/empty values.
I16-06 required scalar ID/digest fields reject non-NFC/noncharacter values.
I16-07 rcs_suite requires exact frozen shape and GCP-valid non-empty strings.
I16-08 rcs_vector_digests must be a non-empty list with valid string elements.
I16-09 raw_per_vector_results must be a non-empty list of exact nested vector-result objects.
I16-10 nested vector-result string/result-enum rules are enforced.
I16-11 deterministic_aggregate_result exact shape, status enum, integer bounds, and digest string rules are enforced.
I16-12 opaque non-SHA digest values pass throughout local structure.
I16-13 frozen digest/identity binding invariants remain unproven and mismatches are not self-upgraded.
I16-14 vector-manifest/current-PASS/freshness/qualification/authority claims remain false; no local array/count relation is invented.
I16-15 failure does not poison later validation.
I16-16 frozen schema/closed Slice 1–7 implementation modules unchanged; inherited 140-test baseline stays green; workflow directly covers governed/executed paths.

## 6. Nonclaims
No suite-digest binding proof, runtime/workload identity binding proof, vector-manifest binding proof, conformance execution correctness, current PASS/freshness proof, outage stale-PASS exclusion proof, resolver qualification/authorization, runtime qualification, evidence promotion, release, deployment, production, policy authority, or terminal authority.

## 7. Construction sequence
Preregister -> freeze harness/workflow with absent mechanism -> preserve RED -> implement narrow structural validator -> require I16 16/16 + inherited baseline 140/140 -> freeze exact candidate -> build one fresh combined blind review packet for Slices 14–16 including raw RED/GREEN evidence and the Slice 15 CI-trigger gap.
