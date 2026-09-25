# R8 v15-r1 — Implementation Slice 13: Local ResolverConformanceSuite1 Validation

Status: **PREREGISTERED BEFORE ACCEPTANCE HARNESS OR MECHANISM IMPLEMENTATION**

## 1. Baseline
Governance-only batch 8–10 closure anchor:
`525e5c90d0f16482b75595e854f647ac88eaa761`

Frozen executable-schema candidate:
`f93ca26975ecb64f0da13779889c75b36140cdfc`

Closed implementation baseline remains Slice 7:
`751162ee42c603cb6c84ee12021d16bab6fa626b`

Slices 11 and 12 are independently frozen for the next combined review but grant no dependency authority to Slice 13.

## 2. Goal
Implement a repository-local pure validator for `ResolverConformanceSuite1` (RCS-1 identity object).

It validates exact frozen field shape and non-empty GCP-valid opaque CanonicalId/Digest strings only.

## 3. Frozen fields
Exact required fields:
- suite_id
- suite_version
- vector_manifest_digest
- vector_generator_implementation_digest
- generator_runtime_manifest_digest
- input_corpus_digest
- expected_result_manifest_digest
- execution_harness_digest
- required_resolver_runtime_identity_digest
- required_resolver_workload_identity_digest
- result_schema_digest
- suite_digest

No extras allowed.

All fields are non-empty strings and must pass inherited GCP authority-string validation.
Digest syntax remains opaque unless a governing source fixes an encoding.

## 4. Source boundary
R8V13-I005 defines the RCS-1 suite identity tuple.
R8V13-I006 requires exact bound generator/harness identity for reference-vector generation.
NORM-021 / R8V14-I013..I015 govern conformance freshness/invalidation.

This slice does NOT:
- recompute suite_digest;
- prove vector_manifest_digest contents;
- execute or verify vector generation;
- prove generator/runtime/harness identity;
- prove required resolver runtime/workload identity is current;
- qualify a resolver;
- prove freshness/current PASS evidence.

## 5. Frozen invariants
I13-01 exact required-field parity.
I13-02 missing field rejects.
I13-03 extra field rejects.
I13-04 all fields must be non-empty strings.
I13-05 non-NFC values reject.
I13-06 Unicode noncharacters reject.
I13-07 opaque non-SHA digests pass.
I13-08 suite_id remains opaque CanonicalId.
I13-09 suite_version remains opaque CanonicalId.
I13-10 required runtime identity digest remains opaque/unverified.
I13-11 required workload identity digest remains opaque/unverified.
I13-12 suite_digest remains unverified.
I13-13 generator/harness identity bindings remain unverified.
I13-14 result metadata grants authority NONE and suite_current/executed/qualified false.
I13-15 failure does not poison later validation.
I13-16 frozen schema/closed Slice 1–7 implementation modules unchanged; inherited 140-test baseline stays green; workflow directly covers governed/executed paths.

## 6. Acceptance
The frozen harness shall contain one direct test for each I13-01..I13-16.

## 7. Nonclaims
No generator execution, vector correctness, suite digest correctness, resolver identity currentness, conformance qualification/freshness, runtime qualification, evidence promotion, release, deployment, production, policy authority, or terminal authority.

## 8. Construction sequence
Preregister -> freeze harness/workflow with absent mechanism -> preserve RED -> implement narrow validator -> require I13 16/16 + inherited baseline 140/140 -> freeze exact candidate -> build one fresh combined blind review packet for Slices 11–13, including raw RED logs for all three loops.
