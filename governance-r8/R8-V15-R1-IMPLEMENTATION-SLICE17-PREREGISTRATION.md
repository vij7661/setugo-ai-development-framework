# R8 v15-r1 — Implementation Slice 17: Local SemanticEntry Validation

Status: **PREREGISTERED BEFORE ACCEPTANCE HARNESS OR MECHANISM IMPLEMENTATION**

## 1. Baseline
Governance-only batch 14–16 closure anchor:
`fa69cd70113c043a285646d0b1bfaef94caa0c69`

Frozen executable-schema candidate:
`f93ca26975ecb64f0da13779889c75b36140cdfc`

Closed implementation baseline remains Slice 7:
`751162ee42c603cb6c84ee12021d16bab6fa626b`

Slices 14–16 are independently closed but are not merged and grant no dependency authority here.

## 2. Goal
Implement a repository-local pure structural validator for `SemanticEntry`.

The validator proves exact frozen field shape, nested `CanonicalScopeTuple` shape, frozen integer/Sequence closure, lifecycle enum closure, nullable string handling, and non-empty GCP-valid opaque string handling.

It does NOT prove any `SemanticEntry` x-validator invariant.

## 3. Frozen fields
Exact required fields:
- semantic_entry_id
- semantic_input_id
- semantic_lineage_id
- semantic_version
- scope_tuple
- specificity_score
- lifecycle_state
- predecessor_entry_id
- successor_of_entry_id
- scope_replacement_mapping_id
- lineage_mapping_id
- any_scope_permission_id
- semantic_class
- artifact_or_rule_digest
- schema_version
- source_authority_digest
- effective_sequence
- constitutional_binding_digest
- semantic_entry_key

No extras allowed.

`scope_tuple` has exactly the nine frozen `CanonicalScopeTuple` components:
trust_domain_id, constitution_id, root_namespace, tenant_id, organization_id,
project_id, experiment_or_release_id, object_class, action_class.

Each scope component is either the exact sentinel `ANY` or a non-empty stable scope string other than `ANY`. String values must pass inherited GCP authority-string validation.

`specificity_score` is a non-boolean integer 0..9.
`effective_sequence` is frozen Sequence 0..INT64_MAX.
`lifecycle_state` is exactly ACTIVE | SUSPENDED | REVOKED | SUPERSEDED | RETIRED | SCOPE_PERMISSION_REEVALUATION_REQUIRED.

Nullable fields predecessor_entry_id, successor_of_entry_id, scope_replacement_mapping_id,
lineage_mapping_id, any_scope_permission_id, constitutional_binding_digest accept null or a
non-empty GCP-valid string.

## 4. Frozen x-validator invariants that remain NONCLAIMS
- specificity_score equals exact non-ANY component count;
- semantic_entry_key equals canonical digest of semantic_input_id+semantic_lineage_id+semantic_version+scope_tuple;
- ANY use requires current matching ANYScopePermission.

This local validator must not reject a structurally valid object merely because those semantic invariants are not proven.

## 5. Frozen invariants
I17-01 exact required-field parity.
I17-02 valid structurally complete entry passes.
I17-03 top-level non-Mapping, missing, and extra fields reject.
I17-04 required scalar ID/digest fields reject non-string/empty/non-NFC/noncharacter values.
I17-05 CanonicalScopeTuple exact nine-field closure and Mapping type.
I17-06 scope components accept exact ANY or non-empty GCP-valid non-ANY strings.
I17-07 invalid scope component type/empty/non-NFC/noncharacter rejects.
I17-08 specificity_score accepts 0..9 and rejects bool/non-int/out-of-range.
I17-09 lifecycle enum closure.
I17-10 each nullable string field accepts null or non-empty GCP-valid string and rejects invalid values.
I17-11 effective_sequence accepts 0..INT64_MAX and rejects bool/non-int/out-of-range.
I17-12 opaque non-SHA digest/key values pass.
I17-13 specificity-vs-scope-count mismatch is structurally accepted and remains unverified.
I17-14 semantic_entry_key/ANY-permission/currentness/authority claims remain false.
I17-15 failure does not poison later validation.
I17-16 frozen schema/closed Slice 1–7 implementation modules unchanged; inherited 140-test baseline stays green; workflow directly covers governed/executed paths.

## 6. Nonclaims
No specificity correctness, semantic_entry_key recomputation, current ANY permission, lifecycle currentness, semantic selection, lineage/scope transition authority, constitutional authorization, runtime qualification, evidence promotion, release, deployment, production, policy authority, or terminal authority.

## 7. Construction sequence
Preregister -> freeze harness/workflow with absent mechanism -> preserve RED -> implement narrow validator -> require I17 16/16 + inherited baseline 140/140 -> freeze exact candidate -> no independent review until Slices 17–19 are complete.
