# R8 Meta-Governance Redesign v13 — Successor Preregistration

Status: **PREREGISTERED_DESIGN_V13 — NOT_IMPLEMENTED — INDEPENDENT_REVIEW_REQUIRED**
Authority effect: **NONE**

Effective design lineage:
- R8 v4: `d779eb495b5830674e0258d4d27b768f77e10471`
- R8 v5: `53d695dff34d14365770d1dbdad8c6620e31a503`
- R8 v6: `e0e6995a61dab629ff49efc19f6d6128936b9c20`
- R8 v7: `fad366add685a978c55837e420e3bcb0939d41aa`
- R8 v8: `58e95ca8cc8beb2125413d794ec08d4333a55521`
- R8 v9: `0948ed0e83d9de128ca9c12df5784286f15af9eb`
- R8 v10: `2e85384f759318a17c2ec14b1781dc689a864618`
- R8 v11: `3d6a0820d851bc629fc4c7ccfee4a081b70ce117`
- R8 v12: `8250f35acb371ce85e818c5ecdf9a11250fa1430`
- This v13 document supersedes prior generations only where stronger or more specific.

## 1. Objective

R8 v13 closes the remaining design blockers before executable-schema freeze.

Core rule:

> A resolver is authoritative only when the active ResolverPolicy explicitly authorizes its exact implementation/runtime identity; scope replacement is evaluated by a frozen total truth table; revoked Smax branches dominate unrelated ACTIVE peers; AIM descriptor applicability is deterministic; and guard identity has one authoritative registry rather than multiple inherited manual tables.

R8 v13 grants no implementation, schema-freeze, qualification, merge, release, deploy, production, policy, or terminal authority.

## 2. ResolverImplementationRegistry-1 — RIR-1

### R8V13-I001 — RIR-1 is CSM-bound

CSM-5 binds one append-only `ResolverImplementationRegistry-1` head.

Each record contains:
- `resolver_implementation_record_id`;
- `resolver_policy_digest`;
- `resolver_implementation_digest`;
- `resolver_runtime_manifest_digest`;
- `workload_attestation_policy_digest`;
- `conformance_suite_digest`;
- `activation_sequence`;
- `retirement_or_revocation_sequence` or null;
- lifecycle state = ACTIVE | SUSPENDED | REVOKED | RETIRED;
- predecessor_record_id or null;
- constitutional source/evidence digest.

### R8V13-I002 — exact policy-to-implementation authorization

For authority-bearing resolution, the exact tuple:

`{resolver_policy_digest, resolver_implementation_digest, resolver_runtime_manifest_digest, workload_attestation_policy_digest, conformance_suite_digest}`

must match exactly one ACTIVE RIR-1 record at `semantic_state_sequence`.

Zero matches -> `RESOLVER_IMPLEMENTATION_UNBOUND`.

More than one applicable ACTIVE record for the exact implementation/runtime tuple -> `RESOLVER_IMPLEMENTATION_CONFLICT`.

### R8V13-I003 — conformance is necessary, not sufficient

Passing conformance vectors does not authorize an implementation by itself.

An implementation must both:
1. be ACTIVE in RIR-1 for the exact ResolverPolicy; and
2. produce valid conformance/runtime evidence required by that registry record.

### R8V13-I004 — RIR lifecycle

RIR-1 records are append-only.

Changing policy binding, implementation digest, runtime manifest, workload policy, or conformance suite creates a successor record through the constitutional semantic-amendment path.

Ordinary project/org/experiment policy cannot enroll or reactivate a resolver implementation.

## 3. ResolverConformanceSuite-1 — RCS-1

### R8V13-I005 — frozen conformance suite identity

Each RIR-1 record binds one `ResolverConformanceSuite-1` containing:
- suite_id/version;
- vector_manifest_digest;
- vector_generator_implementation_digest;
- generator_runtime_manifest_digest;
- input corpus digest;
- expected_result_manifest_digest;
- execution harness digest;
- required resolver runtime/workload identity;
- result-schema digest.

### R8V13-I006 — vector generation

Reference vectors are generated only by the exact bound generator/harness identity.

Generated vector artifacts carry:
- suite digest;
- generator/harness digests;
- input corpus digest;
- output manifest digest.

A vector set from another generator/harness is insufficient.

### R8V13-I007 — execution evidence

Resolver qualification evidence binds:
- RIR-1 record ID/digest;
- ResolverPolicy digest;
- exact implementation/runtime digests;
- exact RCS-1 suite/vector digests;
- raw per-vector results;
- deterministic aggregate result.

Any failed/missing vector means the resolver record is not qualified for authority-bearing execution.

## 4. DPS/Seal verification of resolver registry

### R8V13-I008 — preseal resolver fields

DecisionPresealContext includes:
- RIR-1 registry head;
- active RIR-1 record ID/digest;
- ResolverPolicy digest;
- implementation digest;
- runtime manifest digest;
- workload attestation proof digest;
- conformance suite/result digest.

### R8V13-I009 — final seal verification

VerifiedStateSeal binds the same fields.

Before consequential commit, the current LAS semantic snapshot must still:
- contain the same RIR-1 registry head;
- show the same record ACTIVE;
- bind the same policy/implementation/runtime tuple.

Any change -> `STATE_CHANGED`.

## 5. ScopeReplacementTruthTable-2 — SRTT-2

### R8V13-I010 — complete machine-readable inputs

SRTT-2 evaluates these canonical inputs:

- `source_entry_state` = REVOKED only for replacement evaluation;
- `old_scope_match` = NO_MATCH | EXACT_MATCH;
- `destination_scope_match` = NO_MATCH | EXACT_MATCH | MAPPED_MATCH;
- `old_scope_effect` = BLOCK_OLD_SCOPE | REPLACE_OLD_SCOPE_FOR_EXACT_MATCH | REPLACE_OLD_SCOPE_FOR_MAPPED_MATCH;
- `scope_relation` = SAME | NARROWER | BROADER | DISJOINT;
- `any_permission_valid` = true | false;
- `mapping_effective` = true | false;
- `lineage_mapping_valid` = true | false;
- `scope_expansion_authorized` = true | false;
- `decision_inside_authorized_expansion_domain` = true | false.

All values are derived from the current CSM-5 snapshot and decision scope.

### R8V13-I011 — total evaluation order

SRTT-2 evaluates in this exact order:

1. if source_entry_state != REVOKED -> `NOT_A_REPLACEMENT_BRANCH`;
2. if mapping_effective = false -> `SEMANTIC_SCOPE_REVOKED`;
3. if lineage_mapping_valid = false -> `SEMANTIC_SCOPE_REVOKED`;
4. if any_permission_valid = false -> `SEMANTIC_SCOPE_PERMISSION_REEVALUATION_REQUIRED`;
5. if old_scope_match = NO_MATCH -> `MAPPING_NOT_APPLICABLE`;
6. if old_scope_effect = BLOCK_OLD_SCOPE -> `SEMANTIC_SCOPE_REVOKED`;
7. if destination_scope_match = NO_MATCH -> `SEMANTIC_SCOPE_REVOKED`;
8. apply the replacement-specific rows below.

### R8V13-I012 — exact replacement rows

For `REPLACE_OLD_SCOPE_FOR_EXACT_MATCH`:
- destination_scope_match must be EXACT_MATCH;
- scope_relation must be SAME;
- otherwise -> `SEMANTIC_SCOPE_REPLACEMENT_INVALID`;
- when satisfied -> `REPLACEMENT_ELIGIBLE`.

No broader, narrower, mapped, or disjoint destination is allowed under this effect.

### R8V13-I013 — mapped replacement rows

For `REPLACE_OLD_SCOPE_FOR_MAPPED_MATCH`:

- SAME + (EXACT_MATCH or MAPPED_MATCH) -> `REPLACEMENT_ELIGIBLE`;
- NARROWER + (EXACT_MATCH or MAPPED_MATCH) -> `REPLACEMENT_ELIGIBLE`;
- DISJOINT -> `SEMANTIC_SCOPE_REPLACEMENT_INVALID`;
- BROADER -> eligible **only** when:
  - `scope_expansion_authorized = true`; and
  - `decision_inside_authorized_expansion_domain = true`;
  otherwise -> `SEMANTIC_SCOPE_REPLACEMENT_INVALID`.

### R8V13-I014 — expansion authorization

A BROADER replacement requires constitutional authority class:
`SEMANTIC_SCOPE_EXPANSION_AMENDMENT`.

It binds a CSM-5 `AuthorizedExpansionDomain` object containing:
- source_entry_id;
- destination_entry_id;
- old/new scope tuples;
- exact decision-domain predicate/rule digest;
- effective sequence;
- constitutional evidence digest.

Ordinary policy cannot create or broaden this domain.

### R8V13-I015 — no accidental broad unblocking

A decision outside the AuthorizedExpansionDomain cannot be unblocked by a BROADER replacement, even if the destination entry itself matches it.

Result remains `SEMANTIC_SCOPE_REVOKED` or `SEMANTIC_SCOPE_REPLACEMENT_INVALID` according to the frozen row.

### R8V13-I016 — truth-table authority

The complete SRTT-2 table, ordering, enum values, and reference-vector manifest are CSM-5/ResolverPolicy-bound constitutional semantics.

No resolver-local interpretation may add rows or change precedence.

## 6. SRTT-2 reference vectors

The following design vectors are frozen:

1. REVOKED + exact old match + EXACT effect + same exact destination + permission valid + effective mapping -> ELIGIBLE.
2. REVOKED + exact old match + EXACT effect + narrower destination -> INVALID.
3. REVOKED + exact old match + EXACT effect + broader destination -> INVALID.
4. REVOKED + exact old match + MAPPED effect + narrower mapped destination -> ELIGIBLE.
5. REVOKED + exact old match + MAPPED effect + broader destination + no expansion authorization -> INVALID.
6. Same as 5 with valid expansion authorization but decision outside authorized domain -> INVALID/BLOCKED.
7. Same as 5 with valid authorization and decision inside domain -> ELIGIBLE.
8. Any branch with invalid current ANY permission -> PERMISSION_REEVALUATION_REQUIRED.
9. Mapping not yet effective -> SCOPE_REVOKED.
10. Cross-lineage mapping invalid -> SCOPE_REVOKED.
11. Destination no-match -> SCOPE_REVOKED.
12. BLOCK_OLD_SCOPE -> SCOPE_REVOKED.

Executable schema freeze must encode these and all Cartesian branches implied by I011-I015.

## 7. CSRULE-5 — revoked branch dominance

### R8V13-I017 — Smax lifecycle partition

After current ANY validation, CSRULE-5 partitions all Smax entries into:
- REVOKED blockers;
- ACTIVE entries;
- SUPERSEDED/RETIRED entries.

### R8V13-I018 — revoked dominance

If one or more applicable REVOKED entries exist at Smax:
- ordinary ACTIVE selection is suspended;
- every applicable REVOKED branch must be discharged by one unique valid successor/replacement chain under SRTT-2;
- an unrelated ACTIVE peer at Smax cannot bypass the revoked branch.

### R8V13-I019 — successor discharge

A revoked blocker is discharged only by:
- an explicitly linked ACTIVE successor; or
- an explicitly linked mapping/replacement path whose SRTT-2 result is REPLACEMENT_ELIGIBLE.

If a blocker has:
- zero valid discharge paths -> `SEMANTIC_SCOPE_REVOKED`;
- more than one non-equivalent valid discharge path -> `SEMANTIC_SUCCESSOR_CONFLICT`.

### R8V13-I020 — coexistence with ACTIVE peers

After every REVOKED blocker is uniquely discharged:
- the resolved successor/replacement candidates and any directly ACTIVE Smax peers are compared;
- if exactly one semantic result remains -> continue;
- if multiple non-equivalent ACTIVE semantic results remain -> `SEMANTIC_ENTRY_CONFLICT`.

Thus REVOKED dominates traversal, but successful discharge does not silently erase a genuine peer conflict.

## 8. AIMApplicability-1

### R8V13-I021 — descriptor applicability fields

AIM-4 supersedes AIM-3 applicability ambiguity.

Each descriptor additionally contains:
- `applicability_scope_tuple`;
- `aim_scope_policy_id`;
- `specificity_score`.

The scope tuple uses the same nine-dimensional canonical scope order inherited for semantic decisions.

### R8V13-I022 — AIM scope policy

`AIMScopePolicy-1` is CSM-5-bound and defines, per semantic class, which AIM descriptor tuple components may use ANY.

Project/org/experiment policy cannot broaden it.

### R8V13-I023 — deterministic applicability

For a requested `semantic_input_id` and current decision scope:

1. select descriptors with matching semantic_input_id and expected semantic class;
2. retain descriptors effective at semantic_state_sequence;
3. retain descriptors whose exact scope components match and whose ANY components are permitted by current AIMScopePolicy;
4. derive specificity as exact-component count;
5. determine `AIM_Smax` before lifecycle filtering;
6. apply blocker precedence at AIM_Smax.

### R8V13-I024 — AIM lifecycle precedence

At AIM_Smax:
- REVOKED descriptor -> valid linked successor required, else `AIM_DESCRIPTOR_REVOKED`;
- multiple ACTIVE applicable descriptors -> `AIM_DESCRIPTOR_CONFLICT`;
- exactly one ACTIVE -> resolve;
- only SUPERSEDED/RETIRED -> successor traversal or `AIM_DESCRIPTOR_UNBOUND`.

Lower-specificity fallback is prohibited after an AIM_Smax blocker.

### R8V13-I025 — AIM descriptor successor

An AIM successor must explicitly reference its predecessor.

A source-lineage, policy, class, or scope change cannot silently supersede another descriptor without the required constitutional amendment path.

## 9. LASAuthorityStateRoot v13

### R8V13-I026 — explicit sequence and registry heads

`LASAuthorityStateRoot(i) = SHA-256(GCP-1({semantic_state_sequence_i:i, committed_log_prefix_digest_i, StreamHeadMap_root_i, idempotency_ledger_root_i, authority_state_machine_root_i, revocation_stream_head_i, nonce_ledger_head_i, effect_stream_head_i, csm5_registry_head_i, aim4_descriptor_head_i, any_scope_permission_head_i, aim_scope_policy_head_i, resolver_policy_head_i, resolver_implementation_registry_head_i, guard_registry_head_i, configuration_generation, prior_certificate_chain_digest_i}))`

The semantic sequence and all named authority-semantic registry heads are explicit fields.

## 10. BSP-3 version-aware residual scan

### R8V13-I027 — current candidate version input

BSP-3 packet generation has explicit:
`current_candidate_version = 13`.

### R8V13-I028 — review-outcome classifier

A line is prior-review outcome metadata only when all are true:
- it identifies a predecessor version < current_candidate_version, or belongs to a predecessor-status/review-adjudication block;
- it contains a review/disposition status token;
- it is not inside a quoted/code/test vector whose semantic purpose is to test that token.

Those lines are removed.

### R8V13-I029 — current status retention

The current v13 candidate status is retained.

Semantic guard/case text mentioning strings such as CHANGES_REQUIRED or NOT_IMPLEMENTED as test data is retained and marked semantic by projection context.

### R8V13-I030 — residual scan result

Residual scan fails only on classified prior-review outcome metadata, not on raw token occurrence alone.

The manifest records:
- classifier version;
- current candidate version;
- removed records;
- residual classified-record count.

## 11. BarrierRotation error taxonomy v13

### R8V13-I031 — exact reservation outcomes

For barrier B:

- same `rotation_id` + same proposed_config_digest + same STC identity -> idempotent existing result;
- same `rotation_id` + different proposed_config_digest or different STC identity -> `IDEMPOTENCY_CONFLICT`;
- different `rotation_id` while B is RESERVED/JOINT/ACTIVATED -> `BARRIER_ALREADY_RESERVED`;
- observation of two independently valid contradictory reservation certificates for B -> `STC_EQUIVOCATION`.

ABORTED barrier remains permanently closed.

## 12. GuardRegistry-1 — single authoritative guard identity

### R8V13-I032 — CSM-bound registry

One append-only `GuardRegistry-1` is CSM-5-bound.

Each record contains:
- guard_id;
- mechanism_id;
- positive_case_ids[];
- negative_cases[{case_id,fault_proof_class}];
- canonical source case-definition refs;
- activation sequence;
- lifecycle state;
- predecessor_guard_record_id or null.

### R8V13-I033 — one ACTIVE guard record per ID

At the current semantic_state_sequence, exactly one ACTIVE GuardRegistry record may exist per guard_id.

Zero for a required contiguous guard -> `GUARD_REGISTRY_INCOMPLETE`.

More than one non-equivalent ACTIVE record -> `GUARD_REGISTRY_CONFLICT`.

### R8V13-I034 — legacy tables are not guard authority

Legacy manually consolidated guard tables in inherited prose are superseded as **display/index artifacts** for guard identity.

They do not override GuardRegistry-1.

Canonical case/invariant prose remains semantic source material.

Blind review projection may omit legacy manual consolidated tables only when:
- every omitted guard ID is present in GuardRegistry-1;
- canonical case/invariant sections remain included;
- the projection manifest lists the omitted table section digest/source;
- omission does not remove unique case semantics.

### R8V13-I035 — G001-G130 seed identity

The corrected v12 GCC catalog:
- commit `39dd1c1873a0c3b2276eab581a081f2c0afc99a1`;
- blob `cef6d45ecfda5dc780a339f1795c140082f62583`

is the reviewed seed for GuardRegistry-1 G001-G130.

Before v13 blind review, it must be converted to unique GuardRegistry records and extended with v13 guards.

## 13. Additional Guard Catalog v13

| Guard | Mechanism | Positive | Negatives with fault-proof class |
|---|---|---|---|
| G131 | RIR-1 policy-to-implementation binding | V13-001 | V13-002 FP4; V13-003 FP5 |
| G132 | RCS-1 conformance identity | V13-004 | V13-005 FP4; V13-006 FP5 |
| G133 | SRTT-2 exact replacement total table | V13-007 | V13-008 FP5; V13-009 FP5 |
| G134 | SRTT-2 broader-scope expansion boundary | V13-010 | V13-011 FP5; V13-012 FP5 |
| G135 | CSRULE-5 revoked Smax dominance | V13-013 | V13-014 FP5; V13-015 FP5 |
| G136 | AIMApplicability-1 deterministic descriptor resolution | V13-016 | V13-017 FP5; V13-018 FP5 |
| G137 | LASAuthorityStateRoot semantic sequence/registry binding | V13-019 | V13-020 FP5 |
| G138 | BSP-3 version-aware outcome classifier | V13-021 | V13-022 FP5; V13-023 FP5 |
| G139 | BarrierRotation v13 error taxonomy | V13-024 | V13-025 FP2; V13-026 FP1 |
| G140 | GuardRegistry-1 single authority | V13-027 | V13-028 FP5; V13-029 FP5 |

## 14. R8 v13 preregistered cases

### Resolver implementation
- V13-001 exact ACTIVE RIR record matches policy/implementation/runtime/workload/conformance tuple -> resolver eligible.
- V13-002 implementation passes vectors but is absent from RIR -> RESOLVER_IMPLEMENTATION_UNBOUND.
- V13-003 RIR record policy digest differs from current ResolverPolicy -> reject.

### Conformance
- V13-004 exact bound suite/generator/harness/runtime executes all vectors with expected result manifest -> conformance eligible.
- V13-005 vectors generated/executed by different implementation or runtime -> reject qualification evidence.
- V13-006 missing/failed vector -> resolver record unqualified.

### SRTT-2
- V13-007 exact old scope + SAME exact replacement + valid permissions/effective mapping -> REPLACEMENT_ELIGIBLE.
- V13-008 exact-replacement effect with NARROWER/BROADER destination -> SEMANTIC_SCOPE_REPLACEMENT_INVALID.
- V13-009 mapped replacement with DISJOINT destination -> invalid.
- V13-010 broader mapped replacement + valid expansion amendment + decision inside authorized domain -> eligible.
- V13-011 broader replacement without expansion amendment -> invalid.
- V13-012 broader replacement with valid amendment but decision outside authorized domain -> blocked/invalid.

### Revoked dominance
- V13-013 REVOKED Smax entry + valid unique successor + unrelated equivalent ACTIVE peer -> unique semantic result may continue.
- V13-014 REVOKED Smax entry + unrelated ACTIVE peer but no valid discharge path -> SEMANTIC_SCOPE_REVOKED.
- V13-015 REVOKED branch has two non-equivalent valid successor paths -> SEMANTIC_SUCCESSOR_CONFLICT.

### AIM applicability
- V13-016 two ACTIVE AIM descriptors match at different specificity -> highest-specificity descriptor resolves.
- V13-017 two non-equivalent ACTIVE AIM descriptors tie at AIM_Smax -> AIM_DESCRIPTOR_CONFLICT.
- V13-018 revoked AIM descriptor at AIM_Smax + lower ACTIVE descriptor -> no fallback; AIM_DESCRIPTOR_REVOKED.

### State root
- V13-019 state root explicitly binds semantic_state_sequence and all named semantic/registry heads -> valid.
- V13-020 RIR/GuardRegistry/sequence omitted or mismatched -> root verification reject.

### BSP
- V13-021 predecessor outcome lines are removed while current v13 status is retained.
- V13-022 predecessor outcome remains after classification -> REVIEW_PACKET_NOT_BLIND.
- V13-023 semantic test vector containing outcome token is incorrectly removed -> REVIEW_PACKET_INCOMPLETE.

### Barrier taxonomy
- V13-024 same rotation/config/STC retry -> idempotent same result.
- V13-025 same rotation ID with different config/STC -> IDEMPOTENCY_CONFLICT.
- V13-026 contradictory valid reservation certificates for same barrier -> STC_EQUIVOCATION/freeze.

### Guard registry
- V13-027 exactly one ACTIVE GuardRegistry record exists for every contiguous G001-G140 -> registry valid.
- V13-028 duplicate conflicting ACTIVE record for G044 -> GUARD_REGISTRY_CONFLICT.
- V13-029 blind packet exposes a legacy conflicting table as co-authoritative -> REVIEW_PACKET_INCOMPLETE.

## 15. Schema-freeze gate

Even a future v13 `BOUNDED_PASS` authorizes only executable-schema-freeze preparation.

Before implementation:
- RIR-1/RCS-1 schemas and exact registry lifecycle frozen;
- SRTT-2 complete Cartesian truth-table artifact + reference vectors frozen;
- CSRULE-5 and AIMApplicability-1 schemas/contracts frozen;
- LASAuthorityStateRoot v13 frozen;
- BSP-3 classifier/manifest contract frozen;
- BarrierRotation taxonomy frozen;
- GuardRegistry-1 G001-G140 generated and validated;
- all G001-G140 CaseProofContracts frozen;
- fresh blind review closes without unresolved material design findings.

## 16. Claim boundary

A future R8 v13 bounded design pass establishes only sufficient design closure to proceed to executable-schema freeze under inherited explicit trust assumptions.

It does not prove implementation correctness, trust-root/operator honesty beyond explicit thresholds, hardware/workload-attestation correctness, provider correctness, cloud/IAM security, or legal/compliance sufficiency.

Until independent closure:
- R8 v13 = NOT_IMPLEMENTED / INDEPENDENT_REVIEW_REQUIRED;
- executable-schema freeze = BLOCKED;
- PR #39 = NON_AUTHORITATIVE;
- PR #40 = NON_AUTHORITATIVE;
- authority effect = NONE.
