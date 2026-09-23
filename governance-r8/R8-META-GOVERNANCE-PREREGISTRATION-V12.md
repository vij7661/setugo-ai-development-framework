# R8 Meta-Governance Redesign v12 — Successor Preregistration

Status: **PREREGISTERED_DESIGN_V12 — NOT_IMPLEMENTED — INDEPENDENT_REVIEW_REQUIRED**
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
- This v12 document supersedes prior generations only where stronger or more specific.

## 1. Objective

R8 v12 closes the remaining design blockers before executable-schema freeze.

Core rule:

> Authority-bearing semantic resolution uses one current LAS-3 semantic-state sequence, over append-only constitutional semantic descriptors, with resolver-time permission validation and a sealed resolver implementation/policy identity. Semantic registry heads are explicit members of authority state and rotation barriers. Blind review input contains no predecessor review outcome metadata.

R8 v12 does not grant schema-freeze, implementation, qualification, merge, release, deploy, production, policy, or terminal authority.

## 2. CSM-5 — Authoritative Semantic State Bundle

### R8V12-I001 — CSM-5 supersedes semantic-state ambiguity

CSM-5 is the sole authority-semantic registry bundle consumed by authority resolution.

Canonical bundle:
`{csm_version:"CSM-5", constitution_id, semantic_entries[], lineage_mappings[], scope_replacement_mappings[], any_scope_permissions[], aim_descriptors[], resolver_policy_ref}`

All arrays and references are part of the CSM-5 canonical digest.

### R8V12-I002 — Named semantic heads

The LAS-3 authority state exposes named committed heads:
- `csm5_registry_head`;
- `aim3_descriptor_head`;
- `any_scope_permission_head`;
- `resolver_policy_head`.

These are not implicit aliases of a generic state-machine root.

### R8V12-I003 — semantic_state_sequence

For authority-bearing evaluation:

`semantic_state_sequence = current committed LAS-3 log index that fixes the named semantic heads used by the decision`.

It is derived by the authority evaluator from the current LAS-3 state.

It is never caller-supplied.

Historical semantic sequences may be used only through a separate forensic/replay interface whose authority effect is always NONE.

### R8V12-I004 — one current semantic snapshot

One authority resolution binds:
- semantic_state_sequence;
- CSM-5 head;
- AIM-3 head;
- ANY permission head;
- ResolverPolicy head/digest.

All are read from the same committed LAS-3 authority-state snapshot.

Mixed-head semantic resolution is invalid.

## 3. AIM-3 — Append-only Authority Input Descriptor Registry

### R8V12-I005 — AIM-3 descriptors are immutable records

Each AIM descriptor contains:
- `aim_descriptor_id`;
- `semantic_input_id`;
- `source_semantic_lineage_id`;
- `decision_scope_rule_id`;
- `expected_semantic_class`;
- `resolver_policy_digest`;
- `semantic_version`;
- `effective_sequence`;
- lifecycle state;
- predecessor_descriptor_id or null;
- constitutional source/evidence digest.

A committed descriptor is never mutated in place.

### R8V12-I006 — descriptor change creates successor

Changing any authority-relevant AIM field creates a new descriptor version and requires the constitutional authority defined for that semantic class.

Ordinary project/org/experiment policy cannot redirect source lineage or resolver policy.

### R8V12-I007 — descriptor resolution

At semantic_state_sequence, exactly one ACTIVE applicable AIM descriptor may resolve for an authority input.

Zero -> `AIM_DESCRIPTOR_UNBOUND`.

More than one -> `AIM_DESCRIPTOR_CONFLICT`.

A historical/superseded descriptor cannot be selected for current authority.

## 4. ResolverPolicy-1 — frozen algorithm + implementation identity

### R8V12-I008 — ResolverPolicy object

`ResolverPolicy-1` is a CSM-5-bound machine-readable constitutional artifact containing:
- policy_version;
- resolver algorithm version;
- starting-lineage rule;
- candidate construction rule;
- specificity rule;
- lifecycle/error precedence;
- successor traversal rule;
- lineage-mapping traversal order;
- scope-replacement truth-table reference;
- ANY permission revalidation rule;
- fallback prohibition rule;
- forensic replay rule;
- conformance_vector_set_digest.

### R8V12-I009 — implementation/runtime binding

Authority-bearing semantic resolution additionally requires:
- `resolver_implementation_digest`;
- `resolver_runtime_manifest_digest`;
- valid workload/runtime attestation where required by inherited policy;
- exact `ResolverPolicy-1` digest.

A resolver implementation not bound to the active policy has authority effect NONE.

### R8V12-I010 — conformance vectors

ResolverPolicy-1 names a deterministic conformance-vector set.

Before qualification, the exact implementation must pass the vector set.

A policy digest without matching implementation/vector evidence is insufficient.

## 5. CSRULE-4 — current-state semantic resolver

### R8V12-I011 — current-state entry point

CSRULE-4 inputs are:
- active AIM-3 descriptor;
- current CSM-5 snapshot;
- derived semantic_state_sequence;
- decision scope;
- ResolverPolicy-1 identity.

There is no authority-bearing API parameter for decision_sequence.

### R8V12-I012 — starting lineage

CSRULE-4 begins only from `source_semantic_lineage_id` in the active AIM-3 descriptor.

Any change to that lineage requires an authorized AIM-3 successor descriptor.

### R8V12-I013 — Smax before lifecycle filtering

Within the current source lineage:
1. gather all matching entries from current CSM-5;
2. compute Smax before lifecycle filtering;
3. evaluate every Smax entry under ResolverPolicy-1 lifecycle precedence.

Lower specificity is never considered after an Smax blocking state.

### R8V12-I014 — blocker precedence

At Smax, blocker precedence is:
1. invalid/missing current ANY permission -> `SEMANTIC_SCOPE_PERMISSION_REEVALUATION_REQUIRED`;
2. REVOKED -> valid successor/mapping required, else `SEMANTIC_SCOPE_REVOKED`;
3. multiple ACTIVE eligible entries -> `SEMANTIC_ENTRY_CONFLICT`;
4. exactly one ACTIVE eligible entry -> candidate;
5. only SUPERSEDED/RETIRED -> successor traversal or `SEMANTIC_DEPENDENCY_UNBOUND`.

This precedence is frozen in ResolverPolicy-1.

## 6. Resolver-time ANY permission enforcement

### R8V12-I015 — resolver validates ANY independently

For every matching candidate that contains ANY in scope:
- CSRULE-4 resolves the current active ANYScopePermission from the same CSM-5 semantic snapshot at semantic_state_sequence;
- verifies that every ANY tuple component is permitted for the semantic class;
- verifies the permission is ACTIVE at semantic_state_sequence.

The resolver does not depend on a prior Meta-Governor lifecycle-marking event for correctness.

### R8V12-I016 — drift blocker

If current permission is absent, narrowed, revoked, conflicting, or does not permit every ANY position:
- candidate is blocker-equivalent;
- result is `SEMANTIC_SCOPE_PERMISSION_REEVALUATION_REQUIRED`;
- no lower-specificity fallback is permitted.

A lifecycle event marking affected entries may still be generated as durable evidence, but it is not the authority source.

### R8V12-I017 — ANY amendment authority

The exact constitutional authority class is:
`ANY_SCOPE_PERMISSION_AMENDMENT`.

It uses the constitutional amendment quorum/review path.

Project/org/experiment policy cannot satisfy or broaden it.

## 7. ScopeReplacementTruthTable-1

### R8V12-I018 — machine-readable replacement rule

Every ScopeReplacementMapping binds:
- mapping_id;
- source_entry_id;
- destination_entry_id;
- old_scope_tuple;
- new_scope_tuple;
- old_scope_effect;
- decision_scope_match_rule;
- effective_sequence;
- constitutional evidence digest.

### R8V12-I019 — old_scope_effect values

Allowed exact values:
- `BLOCK_OLD_SCOPE`;
- `REPLACE_OLD_SCOPE_FOR_EXACT_MATCH`;
- `REPLACE_OLD_SCOPE_FOR_MAPPED_MATCH`.

No free-text replacement semantics are authority-bearing.

### R8V12-I020 — deterministic match

`decision_scope_match_rule` is a CSM-bound executable rule identifier.

The replacement mapping is eligible only when:
- the source revoked scope matches according to the frozen old-scope rule;
- the destination scope matches according to the frozen new-scope rule;
- every ANY position is permitted by current ANY permission;
- effective_sequence <= semantic_state_sequence.

Otherwise the mapping cannot unblock the revoked source scope.

## 8. LASAuthorityStateRoot v12

### R8V12-I021 — explicit semantic membership

`LASAuthorityStateRoot(i) = SHA-256(GCP-1({committed_log_prefix_digest_i, StreamHeadMap_root_i, idempotency_ledger_root_i, authority_state_machine_root_i, revocation_stream_head_i, nonce_ledger_head_i, effect_stream_head_i, csm5_registry_head_i, aim3_descriptor_head_i, any_scope_permission_head_i, resolver_policy_head_i, configuration_generation, prior_certificate_chain_digest_i}))`

Every named semantic head is mandatory.

### R8V12-I022 — semantic streams are LAS-governed

Updates to:
- CSM-5 semantic entries/mappings;
- AIM-3 descriptors;
- ANYScopePermission;
- ResolverPolicy;

are LAS-3-governed authority-bearing events.

Projection/database state cannot change those heads independently.

### R8V12-I023 — GGS semantic binding

Where GGS-3 genesis/rotation certification consumes or initializes semantic state, the exact initial/current semantic bundle digest and relevant heads are named members of the GGS certified state root.

## 9. RBP-2 — semantic registry freeze

### R8V12-I024 — rotation freeze scope

After `ROTATION_PREPARE` at barrier B and until valid ENTER_JOINT or ROTATION_ABORT:
- ordinary authority writes are frozen;
- CSM-5 writes are frozen;
- AIM-3 writes are frozen;
- ANY permission writes are frozen;
- ResolverPolicy writes are frozen;
- revocation/time/effect/checkpoint writes covered by inherited RBP rules remain frozen as applicable.

Attempt -> `ROTATION_FROZEN`.

### R8V12-I025 — STC semantic equality

STC/barrier state must bind the exact named semantic heads at B.

Mismatch between STC semantic heads and the barrier state -> rotation reject.

## 10. One barrier → one lawful rotation

### R8V12-I026 — BarrierRotationRegistry

For each sequencer barrier index B:

`B -> UNUSED | RESERVED(rotation_id, proposed_config_digest) | JOINT | ACTIVATED | ABORTED`

The mapping is a LAS/GGS configuration-stream state.

### R8V12-I027 — unique reservation

Exactly one rotation_id may reserve B.

Same rotation_id + same proposed config -> idempotent replay.

Different rotation_id or config for the same B -> `STC_EQUIVOCATION` / `BARRIER_ALREADY_RESERVED`.

### R8V12-I028 — abort closes barrier

`ROTATION_ABORT` changes B to ABORTED permanently.

A later retry/new rotation requires a fresh ROTATION_PREPARE and a new barrier index.

An aborted barrier cannot be recycled.

## 11. DecisionPresealContext v3 / seal binding

### R8V12-I029 — semantic preseal fields

`DecisionPresealContext-v3` includes:
- candidate/action/tenant/project/effect scope;
- governance_snapshot_digest;
- AuthorityReadSet digest;
- semantic_state_sequence;
- CSM-5 head;
- AIM-3 head;
- ANY permission head;
- ResolverPolicy digest;
- resolver implementation/runtime identity digest;
- revocation head;
- runtime/workload attestation digest.

### R8V12-I030 — VerifiedStateSeal binding

VerifiedStateSeal includes the same semantic fields plus accepted time/nonce proof.

Consequential commit compares the current LAS named semantic heads and semantic_state_sequence to the seal.

Any change -> `STATE_CHANGED`; no effect intent commits.

## 12. Blind Semantic Projection — BSP-2

### R8V12-I031 — authoritative review surface is TXT

The canonical blind reviewer packet is UTF-8 TXT.

TXT is the authoritative reviewer input.

A PDF, if supplied, is `NON_AUTHORITATIVE_CONVENIENCE` unless the projection manifest says `pdf_projection_status=PASS`.

PDF can never override TXT.

### R8V12-I032 — prior-outcome redaction

BSP-2 removes prior-version review/disposition metadata, including prior-version lines or predecessor status blocks carrying:
- `CHANGES_REQUIRED`;
- `BOUNDED_PASS`;
- `INSUFFICIENT_EVIDENCE`;
- `REVIEW_REQUIRED`;
- `INDEPENDENT_REVIEW_REQUIRED`;
- `NOT_IMPLEMENTED` when attached to a predecessor version;
- prior review/adjudication evidence/hash/path metadata.

It does not remove:
- current candidate status;
- semantic invariants;
- guard/case definitions;
- claim boundaries;
- source candidate commits/blobs;
- authority semantics.

### R8V12-I033 — neutral predecessor authority statement

Instead of prior review outcomes, the blind packet may state only:

`Inherited predecessor artifacts confer no independent authority on the current candidate.`

This statement carries no prior reviewer disposition.

### R8V12-I034 — projection manifest

The blind packet manifest records:
- BSP-2 version;
- each canonical source commit/blob;
- projected TXT digest;
- removed-line count;
- SHA-256 digest of canonical ordered removed-line records;
- residual-scan result;
- current candidate ID;
- `pdf_projection_status = PASS | FAIL | NOT_USED`;
- PDF digest if present.

### R8V12-I035 — residual outcome scan

Packet generation fails if prior-version disposition/outcome metadata remains.

The scan is version-aware so the current v12 status is retained.

## 13. Deterministic Guard Catalog Compilation — GCC-1

### R8V12-I036 — canonical guard source records

Every guard definition is a machine-readable record:
- guard_id;
- mechanism_id;
- positive_case_ids[];
- negative_cases[{case_id,fault_proof_class}];
- source_design_commit/blob;
- lifecycle state.

### R8V12-I037 — generated consolidated catalog

The blind packet contains one GCC-1 generated consolidated catalog from G001 through the highest ACTIVE guard.

Compilation fails on:
- missing guard ID in the expected sequence;
- duplicate guard ID;
- missing positive control;
- missing referenced case;
- negative case without FP class;
- duplicate conflicting case definition.

No manually maintained consolidated table is authoritative.

## 14. Additional Guard Catalog v12

| Guard | Mechanism | Positive | Negatives with fault-proof class |
|---|---|---|---|
| G118 | current semantic_state_sequence binding | V12-001 | V12-002 FP1; V12-003 FP5 |
| G119 | AIM-3 append-only descriptor authority | V12-004 | V12-005 FP5; V12-006 FP5 |
| G120 | ResolverPolicy/implementation binding | V12-007 | V12-008 FP4; V12-009 FP5 |
| G121 | resolver-time ANY revalidation | V12-010 | V12-011 FP1; V12-012 FP5 |
| G122 | explicit semantic heads in LAS authority root | V12-013 | V12-014 FP5; V12-015 FP3 |
| G123 | RBP-2 semantic registry freeze | V12-016 | V12-017 FP2; V12-018 FP5 |
| G124 | one barrier one rotation | V12-019 | V12-020 FP2; V12-021 FP2 |
| G125 | ScopeReplacementTruthTable | V12-022 | V12-023 FP5; V12-024 FP5 |
| G126 | DecisionPresealContext-v3 semantic binding | V12-025 | V12-026 FP1; V12-027 FP2 |
| G127 | BSP-2 prior-outcome blindness | V12-028 | V12-029 FP5; V12-030 FP5 |
| G128 | GCC-1 consolidated guard compilation | V12-031 | V12-032 FP5; V12-033 FP5 |
| G129 | ANY_SCOPE_PERMISSION_AMENDMENT authority | V12-034 | V12-035 FP5 |
| G130 | PDF non-authoritative projection boundary | V12-036 | V12-037 FP5 |

## 15. R8 v12 preregistered cases

### Semantic state sequence
- V12-001 current LAS semantic-state sequence and matching heads -> resolution eligible.
- V12-002 caller/historical semantic sequence before later revocation -> authority API rejects historical sequence; forensic path authority NONE.
- V12-003 current CSM/AIM/ANY/resolver heads do not all correspond to one LAS snapshot -> reject mixed semantic state.

### AIM-3
- V12-004 valid constitutionally authorized successor AIM descriptor becomes current at effective sequence.
- V12-005 ordinary policy attempts source-lineage redirect -> CONSTITUTIONAL_AMENDMENT_REQUIRED.
- V12-006 in-place mutation of committed AIM descriptor -> integrity failure/reject.

### Resolver policy
- V12-007 resolver implementation/runtime identity matches active ResolverPolicy and conformance-vector digest -> eligible.
- V12-008 implementation digest differs from active policy binding -> authority effect NONE.
- V12-009 ResolverPolicy changed without constitutional amendment -> reject.

### ANY revalidation
- V12-010 current ANY permission permits all candidate ANY positions -> candidate may continue through lifecycle evaluation.
- V12-011 permission narrowed/revoked but no lifecycle marker exists -> resolver independently returns SEMANTIC_SCOPE_PERMISSION_REEVALUATION_REQUIRED.
- V12-012 project/org policy attempts ANY permission revalidation/broadening -> reject.

### State roots/freeze
- V12-013 LASAuthorityStateRoot includes matching CSM/AIM/ANY/resolver heads -> root valid.
- V12-014 any named semantic head omitted or mismatched -> state-root/rotation verification reject.
- V12-015 projection/database mutation changes semantic data without LAS head -> STATE_INTEGRITY_FAILURE.
- V12-016 semantic registry remains unchanged during ROTATION_PREPARED -> rotation can continue.
- V12-017 CSM/AIM/ANY/resolver update attempted during freeze -> ROTATION_FROZEN.
- V12-018 STC semantic heads differ from barrier B -> rotation reject.

### Barrier uniqueness
- V12-019 one rotation reserves fresh B and retries same identity idempotently.
- V12-020 two different rotation IDs race for B -> exactly one reserves; loser BARRIER_ALREADY_RESERVED.
- V12-021 after ROTATION_ABORT, new rotation attempts reuse B -> reject; new barrier required.

### Scope replacement
- V12-022 valid mapped replacement satisfies exact truth table and current ANY permission -> eligible.
- V12-023 mapping enum/text exists but truth-table conditions do not match decision scope -> cannot unblock source scope.
- V12-024 replacement uses unauthorized ANY position -> blocked.

### Preseal/seal
- V12-025 current semantic sequence/heads bound into preseal, time proof, and final seal -> eligible.
- V12-026 semantic head changes after time nonce issuance -> old time proof invalid.
- V12-027 semantic head changes after seal but before COMMIT_WITH_SEAL -> STATE_CHANGED, no effect intent.

### Blindness
- V12-028 clean BSP-2 packet contains current v12 status and neutral predecessor-authority statement but no prior disposition outcomes -> pass.
- V12-029 prior `CHANGES_REQUIRED`/`BOUNDED_PASS`/etc. attached to predecessor remains -> REVIEW_PACKET_NOT_BLIND.
- V12-030 redaction removes a semantic invariant/guard/case -> REVIEW_PACKET_INCOMPLETE.

### Guard compilation
- V12-031 GCC-1 compiles every ACTIVE guard sequentially with positive/negative/FP references -> catalog valid.
- V12-032 missing or duplicate guard/case reference -> REVIEW_PACKET_INCOMPLETE.
- V12-033 negative case lacks FP class -> REVIEW_PACKET_INCOMPLETE.

### Authority class / PDF
- V12-034 valid ANY_SCOPE_PERMISSION_AMENDMENT constitutional path -> permission successor eligible.
- V12-035 project/org actor attempts same transition -> reject.
- V12-036 TXT authoritative + PDF marked NON_AUTHORITATIVE_CONVENIENCE/validated -> review surface valid.
- V12-037 PDF differs/corrupts while manifest claims authoritative equivalence -> PDF projection FAIL; TXT remains authoritative.

## 16. Schema-freeze gate

Even a future v12 `BOUNDED_PASS` authorizes only executable-schema-freeze preparation.

Before implementation:
- CSM-5, AIM-3, ResolverPolicy-1, ScopeReplacementTruthTable, LASAuthorityStateRoot v12, RBP-2, DecisionPresealContext-v3, BSP-2, GCC-1 schemas/contracts must be frozen;
- GCC-1 consolidated G001-G130 catalog must be generated and validated;
- all G001-G130 CaseProofContracts must be frozen;
- fresh blind review must close without unresolved material findings.

## 17. Claim boundary

A future R8 v12 bounded design pass establishes only sufficient design closure to proceed to executable-schema freeze under inherited explicit trust assumptions.

It does not prove:
- implementation correctness;
- trust-root/operator honesty beyond explicit thresholds;
- hardware/workload-attestation vendor correctness;
- provider correctness;
- cloud/IAM security;
- legal/compliance sufficiency.

Until independent closure:
- R8 v12 = NOT_IMPLEMENTED / INDEPENDENT_REVIEW_REQUIRED;
- executable-schema freeze = BLOCKED;
- PR #39 = NON_AUTHORITATIVE;
- PR #40 = NON_AUTHORITATIVE;
- authority effect = NONE.
