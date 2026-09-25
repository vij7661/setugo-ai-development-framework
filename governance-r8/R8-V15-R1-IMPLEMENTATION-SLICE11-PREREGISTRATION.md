# R8 v15-r1 — Implementation Slice 11: Local ResolverPolicyContract Validation

Status: **PREREGISTERED BEFORE ACCEPTANCE HARNESS OR MECHANISM IMPLEMENTATION**

## 1. Baseline
Governance-only batch 8–10 closure anchor:
`525e5c90d0f16482b75595e854f647ac88eaa761`

Frozen executable-schema candidate:
`f93ca26975ecb64f0da13779889c75b36140cdfc`

Closed implementation baseline remains Slice 7:
`751162ee42c603cb6c84ee12021d16bab6fa626b`

Slices 8–10 are independently closed but are not merged and grant no dependency authority here.

## 2. Goal
Implement a repository-local pure validator for `ResolverPolicyContract`.

The validator proves only exact frozen field shape plus non-empty GCP-valid opaque CanonicalId/Digest values. It does not recompute any digest or prove that the policy's resolver algorithm/rules are semantically correct, active, constitutional, or current.

## 3. Frozen fields
Exact required fields:
- policy_version
- resolver_algorithm_version
- resolver_policy_id
- lineage_start_rule_digest
- candidate_construction_rule_digest
- specificity_rule_digest
- lifecycle_error_precedence_digest
- mapping_traversal_rule_digest
- successor_traversal_rule_digest
- replacement_evaluation_rule_digest
- any_validation_rule_digest
- fallback_prohibition_rule_digest
- forensic_replay_rule_digest
- conformance_suite_id
- resolver_policy_digest
- conformance_vector_set_digest

No extras allowed.

All fields are non-empty strings and must pass inherited GCP authority-string validation.
Digest syntax remains opaque unless a later source fixes a concrete encoding.

## 4. Source boundary
NORM-019 / R8V12-I008 define ResolverPolicy as the machine-readable algorithm contract and identify its rule families and conformance-suite identity.

This slice does not:
- prove those rule digests encode correct rules;
- prove the policy is current/active in CSM;
- prove conformance execution;
- authorize any resolver implementation;
- prove resolver_policy_digest or conformance_vector_set_digest cryptographically.

## 5. Frozen invariants
I11-01 exact required-field parity.
I11-02 missing field rejects.
I11-03 extra field rejects.
I11-04 all fields must be strings.
I11-05 empty values reject.
I11-06 non-NFC values reject.
I11-07 Unicode noncharacters reject.
I11-08 opaque non-SHA digests are accepted.
I11-09 policy_version remains opaque CanonicalId.
I11-10 resolver_algorithm_version remains opaque CanonicalId.
I11-11 conformance_suite_id remains opaque CanonicalId.
I11-12 resolver_policy_digest is not recomputed/verified.
I11-13 conformance_vector_set_digest is not recomputed/verified.
I11-14 result metadata grants authority NONE and policy_current/active/authorized false.
I11-15 failure does not poison later validation.
I11-16 frozen schema/closed Slice 1–7 implementation modules unchanged; inherited 140-test baseline stays green; workflow directly covers governed/executed paths.

## 6. Acceptance
The frozen harness shall contain one direct test for each I11-01..I11-16.

## 7. Nonclaims
No current CSM binding, constitutional authorization, resolver implementation authorization, conformance qualification, runtime qualification, evidence promotion, release, deployment, production, policy authority, or terminal authority.

## 8. Construction sequence
Preregister -> freeze harness/workflow with absent mechanism -> preserve RED -> implement narrow validator -> require I11 16/16 + inherited baseline 140/140 -> freeze exact candidate -> do not independently review until all three requested loops (Slices 11–13) are complete.
