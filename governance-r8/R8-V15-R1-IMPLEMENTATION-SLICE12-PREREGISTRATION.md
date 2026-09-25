# R8 v15-r1 — Implementation Slice 12: Local ResolverImplementationRegistryRecord Validation

Status: **PREREGISTERED BEFORE ACCEPTANCE HARNESS OR MECHANISM IMPLEMENTATION**

## 1. Baseline
Governance-only batch 8–10 closure anchor:
`525e5c90d0f16482b75595e854f647ac88eaa761`

Frozen executable-schema candidate:
`f93ca26975ecb64f0da13779889c75b36140cdfc`

Closed implementation baseline remains Slice 7:
`751162ee42c603cb6c84ee12021d16bab6fa626b`

Slice 11 is independently frozen for the next combined review but is not an authority dependency of Slice 12.

## 2. Goal
Implement a repository-local pure validator for `ResolverImplementationRegistryRecord` (RIR record).

It validates exact frozen field shape, opaque GCP-valid CanonicalId/Digest strings, nullable predecessor ID, Sequence syntax, and lifecycle enum.

It does NOT decide temporal eligibility at any semantic_state_sequence and does NOT authorize a resolver.

## 3. Frozen fields
Exact required fields:
- resolver_implementation_record_id
- rir_record_id
- resolver_policy_digest
- implementation_id
- resolver_implementation_digest
- resolver_runtime_manifest_digest
- workload_attestation_policy_digest
- runtime_identity_digest
- workload_identity_digest
- conformance_suite_digest
- predecessor_record_id
- constitutional_source_evidence_digest
- activation_sequence
- retirement_or_revocation_sequence
- lifecycle_state
- freshness_profile_id
- record_digest

No extras allowed.

Generic IDs/digests are non-empty GCP-valid strings and remain lexically opaque.
`predecessor_record_id` is null or a non-empty GCP-valid string.
`activation_sequence` is frozen Sequence.
`retirement_or_revocation_sequence` is null or frozen Sequence.
`lifecycle_state` is exactly ACTIVE | SUSPENDED | RETIRED | REVOKED.

No local rule is invented requiring retirement_or_revocation_sequence > activation_sequence;
temporal eligibility is evaluated separately under NORM-020 / R8V14-I005.

## 4. Source boundary
NORM-020 / R8V13-I001..I004 / R8V14-I005..I006 define the registry and temporal authority rules.

This slice proves record syntax only. It does not prove:
- the record is append-only/current;
- ACTIVE status is current at a decision sequence;
- activation/retirement temporal eligibility;
- exact tuple uniqueness;
- policy-to-implementation authorization;
- workload/runtime attestation;
- conformance qualification/freshness;
- record_digest cryptographic correctness.

## 5. Frozen invariants
I12-01 exact required-field parity.
I12-02 missing field rejects.
I12-03 extra field rejects.
I12-04 required string fields must be non-empty strings.
I12-05 non-NFC/noncharacter strings reject.
I12-06 predecessor_record_id accepts null or non-empty GCP-valid string; empty/non-string reject.
I12-07 activation_sequence accepts 0..INT64_MAX and rejects bool/non-int/out-of-range.
I12-08 retirement_or_revocation_sequence accepts null or 0..INT64_MAX; rejects bool/non-int/out-of-range.
I12-09 lifecycle enum closure.
I12-10 opaque non-SHA digest values pass.
I12-11 no activation-vs-retirement ordering rule is invented locally.
I12-12 record temporal eligibility remains unproven.
I12-13 record_digest remains unverified.
I12-14 result metadata grants authority NONE and resolver_current/authorized/qualified false.
I12-15 failure does not poison later validation.
I12-16 frozen schema/closed Slice 1–7 implementation modules unchanged; inherited 140-test baseline stays green; workflow directly covers governed/executed paths.

## 6. Acceptance
The frozen harness shall contain one direct test for each I12-01..I12-16.

## 7. Nonclaims
No registry append, current registry head, temporal eligibility, exact tuple uniqueness, resolver authorization, conformance qualification, runtime qualification, evidence promotion, release, deployment, production, policy authority, or terminal authority.

## 8. Construction sequence
Preregister -> freeze harness/workflow with absent mechanism -> preserve RED -> implement narrow validator -> require I12 16/16 + inherited baseline 140/140 -> freeze exact candidate -> no external review until Slice 13 also completes.
