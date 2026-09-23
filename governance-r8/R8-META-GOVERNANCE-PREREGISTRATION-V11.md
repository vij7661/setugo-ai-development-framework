# R8 Meta-Governance Redesign v11 — Successor Preregistration

Status: **PREREGISTERED_DESIGN_V11 — NOT_IMPLEMENTED — INDEPENDENT_REVIEW_REQUIRED**
Authority effect: **NONE**

Effective design lineage:
- R8 v4: `d779eb495b5830674e0258d4d27b768f77e10471`
- R8 v5: `53d695dff34d14365770d1dbdad8c6620e31a503`
- R8 v6: `e0e6995a61dab629ff49efc19f6d6128936b9c20`
- R8 v7: `fad366add685a978c55837e420e3bcb0939d41aa`
- R8 v8: `58e95ca8cc8beb2125413d794ec08d4333a55521`
- R8 v9: `0948ed0e83d9de128ca9c12df5784286f15af9eb`
- R8 v10: `2e85384f759318a17c2ec14b1781dc689a864618`
- This v11 document supersedes prior generations only where stronger or more specific.

## 1. Objective

R8 v11 closes the remaining design blockers before executable-schema freeze.

Core rule:

> Semantic resolution must traverse only explicit constitutional lineage/scope transitions over one canonical semantic registry; scope-permission drift must block at maximum specificity; rotation state transfer must be certified from a sequencer barrier that prevents post-snapshot authority writes; and blind-review projection must deterministically reject residual prior-review metadata.

R8 v11 does not grant schema-freeze, implementation, qualification, merge, release, deploy, production, policy, or terminal authority.

## 2. CSM-4 — Unified Scoped Semantic Registry

### R8V11-I001 — CSM-4 supersedes CSM-3 resolver envelope

CSM-4 is the sole authority-semantic registry consumed by AIM resolution and CSRULE-3.

Canonical envelope:

`{csm_version:"CSM-4", constitution_id, semantic_entries[], lineage_mappings[], scope_replacement_mappings[], any_scope_permissions[], resolver_policy_digest}`

All arrays are part of the CSM-4 canonical digest.

No secondary semantic registry may reinterpret lineage, scope, lifecycle, or permission state.

### R8V11-I002 — Full canonical scope tuple

Every SemanticEntry scope is ordered exactly:

`{trust_domain_id, constitution_id, root_namespace, tenant_id, organization_id, project_id, experiment_or_release_id, object_class, action_class}`

Each component is:
- an exact stable ID/value; or
- literal `ANY` only when the active constitutional ANYScopePermission for that semantic class permits that exact tuple component.

No dimension is implicitly absorbed by another field.

### R8V11-I003 — Scope specificity

`specificity_score` is the count of exact non-ANY components in the nine-component canonical scope tuple.

Stored score must equal the derived score.

### R8V11-I004 — SemanticEntry structure

Each SemanticEntry contains:
- semantic_entry_id;
- semantic_input_id;
- semantic_lineage_id;
- semantic_version;
- canonical scope_tuple;
- derived specificity_score;
- lifecycle_state;
- predecessor_entry_id or null;
- successor_of_entry_id or null;
- scope_replacement_mapping_id or null;
- lineage_mapping_id or null;
- any_scope_permission_id or null;
- semantic_class;
- artifact_or_rule_digest;
- schema/version;
- source authority;
- effective_sequence;
- constitutional binding where applicable.

### R8V11-I005 — SemanticEntry key

`semantic_entry_key = SHA-256(GCP-1({semantic_input_id, semantic_lineage_id, semantic_version, scope_tuple}))`

Duplicate semantic_entry_key is rejected.

Duplicate semantic_input_id alone is valid.

### R8V11-I006 — Canonical CSM-4 ordering

Arrays sort deterministically:

SemanticEntry:
1. semantic_input_id
2. semantic_lineage_id
3. descending specificity_score
4. effective_sequence
5. semantic_version
6. semantic_entry_key

SemanticLineageMapping:
1. semantic_input_id
2. source_lineage_id
3. source_entry_id
4. effective_sequence
5. mapping_id

ScopeReplacementMapping:
1. semantic_input_id
2. semantic_lineage_id
3. revoked_entry_id
4. effective_sequence
5. mapping_id

ANYScopePermission:
1. semantic_class
2. effective_sequence
3. permission_id

## 3. AIM-2 — Resolution entrypoint

### R8V11-I007 — AIM binds starting semantic lineage

Every authority_input_id in AIM-2 binds:
- semantic_input_id;
- source_semantic_lineage_id;
- decision-scope construction rule ID;
- expected semantic class;
- resolver_policy_digest.

### R8V11-I008 — AIM resolution is CSRULE-3 over CSM-4

All inherited wording that describes AIM resolution as “one active CSM entry” is superseded.

Authority resolution is exactly:

`CSRULE-3(AIM-2 descriptor, CSM-4 head, decision_scope, decision_sequence)`

No other resolution path exists.

Zero result, ambiguity, blocked lifecycle, invalid mapping, or unbound input fails closed.

## 4. CSRULE-3 — Deterministic lineage-aware resolver

### R8V11-I009 — Resolver starts from source lineage

For the AIM source_semantic_lineage_id:
1. gather all CSM-4 SemanticEntries for the bound semantic_input_id whose scope matches decision_scope;
2. compute Smax across that source lineage before lifecycle filtering;
3. evaluate every Smax entry under the lifecycle rules below.

Lower specificity is never considered after an Smax blocking state.

### R8V11-I010 — Blocking lifecycle states at Smax

At Smax:
- REVOKED -> successor/mapping resolution is required;
- SCOPE_PERMISSION_REEVALUATION_REQUIRED -> return `SEMANTIC_SCOPE_PERMISSION_REEVALUATION_REQUIRED`;
- more than one ACTIVE eligible entry -> `SEMANTIC_ENTRY_CONFLICT`;
- exactly one ACTIVE and no blocking peer -> eligible;
- only SUPERSEDED/RETIRED with no valid successor path -> `SEMANTIC_DEPENDENCY_UNBOUND`.

`SCOPE_PERMISSION_REEVALUATION_REQUIRED` is blocker-equivalent for fallback purposes: no lower-specificity entry may be selected.

### R8V11-I011 — Functional successor graph

For one SemanticEntry at one decision_sequence:
- at most one effective successor edge may exist;
- successor semantic_version must be strictly greater;
- successor effective_sequence must be greater than predecessor effective_sequence;
- graph must be acyclic;
- a successor already superseded/revoked is traversed according to the same rules;
- multiple effective successors -> `SEMANTIC_SUCCESSOR_CONFLICT`.

There is no heuristic version winner.

### R8V11-I012 — Successor traversal

When an Smax source entry is REVOKED/SUPERSEDED and a successor is required:
1. resolve its explicit same-lineage successor edge, ScopeReplacementMapping, or SemanticLineageMapping;
2. validate mapping is ACTIVE/effective at decision_sequence;
3. validate target entry;
4. traverse until one current eligible ACTIVE target is reached or a blocking/error state occurs.

Traversal records every entry/mapping digest in the authority read set.

### R8V11-I013 — SemanticLineageMapping integrated into resolution

A SemanticLineageMapping is a constitutional CSM-4 object containing:
- mapping_id;
- semantic_input_id;
- source_lineage_id;
- source_entry_id;
- source_scope_tuple;
- destination_lineage_id;
- destination_entry_id;
- destination_scope_tuple;
- effective_sequence;
- mapping_semantics_digest;
- constitutional evidence digest;
- lifecycle state.

When a source successor edge references lineage_mapping_id, CSRULE-3 directly adds the exact mapped destination entry as the next successor candidate.

CSRULE-3 does **not** gather arbitrary general entries from the destination lineage.

### R8V11-I014 — Cross-lineage no-fallback

A destination-lineage entry is eligible only when referenced by a valid active SemanticLineageMapping from the exact source chain.

An unrelated lower/general entry in another lineage can never unblock a source-lineage revoked scope.

### R8V11-I015 — Mapping conflict

For one source_entry_id at one decision_sequence:
- zero effective lineage mappings -> no cross-lineage transition;
- exactly one -> use it;
- more than one -> `SEMANTIC_LINEAGE_CONFLICT`.

### R8V11-I016 — ScopeReplacementMapping traversal

ScopeReplacementMapping contains:
- mapping_id;
- semantic_input_id;
- semantic_lineage_id;
- revoked_entry_id;
- destination_entry_id;
- old_scope_tuple;
- new_scope_tuple;
- old_specificity;
- new_specificity;
- replacement_effect_on_old_scope;
- effective_sequence;
- constitutional amendment evidence digest;
- lifecycle state.

The destination_entry_id is exact. CSRULE-3 does not search lower-general entries to satisfy a replacement.

### R8V11-I017 — Replacement-scope behavior

A changed-scope successor unblocks the old scope only when `replacement_effect_on_old_scope = REPLACES_FOR_MATCHING_DECISIONS` and the constitutional mapping explicitly defines which old decision scopes are covered.

Otherwise the old revoked scope remains `SEMANTIC_SCOPE_REVOKED`.

## 5. ANYScopePermission lifecycle and revalidation

### R8V11-I018 — ANY permission effective sequence

ANYScopePermission has:
- permission_id;
- semantic_class;
- allowed ANY tuple components;
- effective_sequence;
- lifecycle state;
- constitutional authority evidence.

Only ACTIVE permission at decision_sequence is valid.

### R8V11-I019 — Narrowing/revocation transition

When permission P is narrowed/revoked at sequence N:
- every ACTIVE SemanticEntry bound to P whose ANY usage is no longer permitted receives a LAS-committed lifecycle event to `SCOPE_PERMISSION_REEVALUATION_REQUIRED` effective at N;
- this transition is mandatory and derived by Meta-Governor from CSM-4 state;
- until all required lifecycle events are committed, the CSM head is `SEMANTIC_TRANSITION_INCOMPLETE` and cannot authorize affected inputs.

### R8V11-I020 — Revalidation authority

Revalidation requires the constitutional authority class governing ANYScopePermission.

A revalidation event:
- references the affected entry;
- references the current active permission;
- proves its scope now complies;
- creates a new SemanticEntry version or valid successor;
- has effective_sequence > reevaluation sequence.

Project/org policy cannot revalidate a constitutionally disallowed ANY.

### R8V11-I021 — Reevaluation resolver behavior

At decision_sequence >= reevaluation effective sequence:
- an affected Smax entry blocks lower-specificity fallback;
- it is not ACTIVE;
- resolution returns `SEMANTIC_SCOPE_PERMISSION_REEVALUATION_REQUIRED` unless a valid revalidated successor applies.

## 6. Sequencer state-root definitions

### R8V11-I022 — LAS-3 AuthorityStateRoot

At LAS global log index B:

`LASAuthorityStateRoot(B) = SHA-256(GCP-1({B, committed_log_prefix_digest_B, StreamHeadMap_root_B, idempotency_ledger_root_B, authority_state_machine_root_B, revocation_stream_head_B, nonce_ledger_head_B, effect_stream_head_B, configuration_generation, prior_certificate_chain_digest_B}))`

### R8V11-I023 — GGS-3 GenesisStateRoot

At GGS global log index B:

`GGSGenesisStateRoot(B) = SHA-256(GCP-1({B, committed_log_prefix_digest_B, constitution_namespace_root_B, bootstrap_authorization_root_B, idempotency_ledger_root_B, configuration_generation, prior_certificate_chain_digest_B}))`

These exact formulas are CSM-bound semantic artifacts.

## 7. Rotation Barrier Protocol — RBP-1

### R8V11-I024 — ROTATION_PREPARE is linearized

Before STC creation, current old configuration commits:

`ROTATION_PREPARE(rotation_id, old_config_digest, proposed_new_config_digest)`

in the same global sequencer log that orders authority-bearing commits.

The commit certificate binds barrier index `B`.

### R8V11-I025 — Rotation freeze

Immediately after ROTATION_PREPARE commits at B:
- all ordinary authority-bearing state/effect/registry/checkpoint commits governed by that sequencer are rejected with `ROTATION_FROZEN`;
- only rotation-control events and read-only verification are permitted;
- no authority state root may advance beyond B before ENTER_JOINT or ROTATION_ABORT.

This closes the post-snapshot/pre-JOINT commit race.

### R8V11-I026 — Barrier state

STC-2 must certify:
- rotation_id;
- exact ROTATION_PREPARE certificate;
- barrier index B;
- LASAuthorityStateRoot(B) or GGSGenesisStateRoot(B);
- all state fields inherited from STC-1;
- old/new config digests.

A snapshot at any other authority index is rejected.

## 8. STC-2 — Unique committed transfer certificate

### R8V11-I027 — STC_COMMIT

STC-2 itself is committed as one non-commutative configuration-stream event:

`STC_COMMIT(rotation_id, barrier_certificate_digest, stc_digest)`

For one rotation_id/barrier:
- exactly one stc_digest may commit;
- retry same digest returns existing result;
- different digest -> `STC_EQUIVOCATION` and rotation freeze remains.

### R8V11-I028 — Old-config certification

The old quorum signs the exact STC-2 digest after ROTATION_PREPARE.

Since ordinary authority commits are frozen, STC authority state equals the current authority state at ENTER_JOINT.

### R8V11-I029 — New-config acceptance

New replicas install:
- barrier snapshot B;
- required rotation-control log through STC_COMMIT;
- exact idempotency/certificate/configuration state.

New quorum signs `StateTransferAcceptanceCertificate(stc_digest)`.

Mismatch -> non-voting.

### R8V11-I030 — ENTER_JOINT exactness

ENTER_JOINT must reference:
- rotation_id;
- ROTATION_PREPARE certificate;
- exact STC_COMMIT certificate;
- old-quorum STC certificate;
- new-quorum acceptance certificate;
- expected configuration-stream head.

Any mismatch/staleness -> `CONFIG_TRANSITION_MISMATCH`.

After ENTER_JOINT commits, authority commits may resume only under JOINT old+new quorum semantics.

### R8V11-I031 — ROTATION_ABORT

Before ENTER_JOINT, old configuration may commit ROTATION_ABORT under old quorum.

Because authority writes were frozen from B:
- abort returns to PRE_JOINT;
- no catch-up ambiguity exists;
- the abandoned STC/rotation_id cannot later be activated.

## 9. CTS-3 quorum state machine

### R8V11-I032 — Configuration states

- PRE_JOINT: old quorum; normal commits allowed unless ROTATION_PREPARED.
- ROTATION_PREPARED: old quorum for rotation-control only; ordinary authority commits frozen.
- JOINT: both old and new quorums for authority and config-transition commands.
- ACTIVE_NEW: new quorum only after exact ACTIVATE index.

### R8V11-I033 — ACTIVATE

ACTIVATE references exact:
- rotation_id;
- ROTATION_PREPARE certificate;
- STC_COMMIT certificate;
- ENTER_JOINT certificate;
- new_config_digest;
- activation index.

Mismatch -> `CONFIG_TRANSITION_MISMATCH`.

## 10. Blind Semantic Projection — BSP-1

### R8V11-I034 — Exact redaction grammar

Blind review packets are generated from canonical design files using BSP-1.

BSP-1 may remove only:
1. a line matching case-insensitive administrative header patterns:
   - `^R8 v[0-9]+ .*adjudication:$`
   - `^R8 v[0-9]+ .*review adjudication:$`
   - `^Review adjudication:$`
   - `^Independent review evidence:$`
2. the immediately following metadata line if it contains only a path/commit/blob/hash reference associated with that header.

No other line may be removed.

### R8V11-I035 — Residual metadata scan

Packet generation fails if the projected packet contains:
- a line matching `(?i)R8 v[0-9]+ .*adjudication:`;
- a line matching `(?i)review adjudication:`;
- known prior-review-evidence path prefixes;
- any 40-hex commit on a line whose surrounding administrative label denotes prior adjudication/review evidence.

Generic semantic use of the word "adjudication" is not removed.

### R8V11-I036 — Projection manifest

The blind packet contains a projection manifest with:
- each canonical source commit/blob;
- projection algorithm version BSP-1;
- count and SHA-256 digest of removed administrative lines;
- digest of each projected semantic source;
- confirmation residual metadata scan = PASS.

It never includes the removed text itself.

## 11. Additional Guard Catalog v11

| Guard | Mechanism | Positive | Negatives with fault-proof class |
|---|---|---|---|
| G108 | CSM-4 full scope and canonical mapping objects | V11-001 | V11-002 FP5; V11-003 FP5 |
| G109 | CSRULE-3 cross-lineage mapped traversal | V11-004 | V11-005 FP5; V11-006 FP5 |
| G110 | Successor graph determinism | V11-007 | V11-008 FP5; V11-009 FP5 |
| G111 | ANY reevaluation blocks Smax fallback | V11-010 | V11-011 FP5; V11-012 FP5 |
| G112 | AIM-2/CSRULE-3 single resolution path | V11-013 | V11-014 FP4 |
| G113 | RBP-1 post-snapshot write freeze | V11-015 | V11-016 FP2; V11-017 FP3 |
| G114 | STC-2 unique linearized transfer certificate | V11-018 | V11-019 FP2; V11-020 FP5 |
| G115 | CTS-3 exact JOINT/ACTIVATE binding | V11-021 | V11-022 FP2; V11-023 FP5 |
| G116 | BSP-1 residual prior-review metadata rejection | V11-024 | V11-025 FP5 |
| G117 | Full-scope collision isolation | V11-026 | V11-027 FP5 |

## 12. R8 v11 preregistered cases

### CSM-4/full scope
- V11-001 two otherwise identical entries differing only by action_class remain distinct and resolve by exact action scope.
- V11-002 entry omits/aliases trust_domain_id or constitution_id -> invalid scope.
- V11-003 stored/derived scope specificity mismatch -> reject.

### Cross-lineage
- V11-004 revoked source Smax entry references one active constitutional SemanticLineageMapping to exact destination successor -> mapped successor resolves.
- V11-005 revoked source + unrelated lower/general destination-lineage entry without mapping -> no fallback; SEMANTIC_SCOPE_REVOKED.
- V11-006 two effective lineage mappings for same source entry -> SEMANTIC_LINEAGE_CONFLICT.

### Successor graph
- V11-007 single acyclic version-increasing successor chain -> resolves current ACTIVE successor.
- V11-008 cycle in successor/mapping graph -> reject mapping/SEMANTIC_SUCCESSOR_CONFLICT.
- V11-009 two effective successors from one entry at one decision sequence -> SEMANTIC_SUCCESSOR_CONFLICT.

### ANY drift
- V11-010 permission narrowing causes affected Smax entry -> SCOPE_PERMISSION_REEVALUATION_REQUIRED and blocks lower-general fallback.
- V11-011 project/org actor attempts revalidate disallowed ANY -> reject.
- V11-012 constitutionally authorized revalidated successor under current permission -> resolver may use successor.

### AIM closure
- V11-013 AIM-2 input resolves only through CSRULE-3/CSM-4 and all traversed mappings enter AuthorityReadSet.
- V11-014 authority code attempts bypass with direct "one active entry" lookup -> AIEP/AIM violation; authority effect NONE.

### Rotation barrier/STC
- V11-015 ROTATION_PREPARE commits at B, no post-B authority writes, STC-2 matches root at B, ENTER_JOINT succeeds.
- V11-016 authority commit attempted after ROTATION_PREPARE before ENTER_JOINT -> ROTATION_FROZEN; state root unchanged.
- V11-017 STC snapshot/root does not equal barrier state B -> reject rotation.
- V11-018 exactly one STC_COMMIT for rotation/barrier -> valid.
- V11-019 two different STC digests race for one rotation/barrier -> one commit; conflict/equivocation for loser.
- V11-020 new-config acceptance root differs from STC -> new replica non-voting; ENTER_JOINT reject.

### CTS-3
- V11-021 JOINT command has old+new quorum and exact STC/JOIN certificates -> eligible.
- V11-022 JOINT authority/config command has only old or only new quorum -> reject.
- V11-023 ACTIVATE references wrong rotation/STC/JOIN/new-config -> CONFIG_TRANSITION_MISMATCH.

### Blind packet
- V11-024 BSP-1 removes only permitted prior-adjudication metadata; residual scan PASS; semantic guard/case counts preserved.
- V11-025 projected packet retains prior adjudication hash/reference line -> packet construction fails; review packet not frozen.

### Scope collision
- V11-026 entries differing only by trust_domain/constitution/object_class/action_class do not collide and cannot cross-authorize.
- V11-027 a resolver request with mismatched one of those dimensions cannot match the other scope.

## 13. Schema-freeze gate

Even a future v11 `BOUNDED_PASS` authorizes only executable-schema-freeze preparation.

Before implementation:
- CSM-4/AIM-2/CSRULE-3 schemas and resolver algorithm frozen;
- full nine-component scope tuple frozen;
- lineage/scope mapping schemas frozen;
- ANY permission lifecycle/revalidation schemas frozen;
- LAS/GGS state-root formulas frozen;
- RBP-1/STC-2/CTS-3 schemas frozen;
- all G001-G117 CaseProofContracts frozen with positive controls and FP classes;
- BSP-1 projection manifest independently reviewed if required.

## 14. Claim boundary

A future R8 v11 bounded design pass establishes only sufficient design closure to proceed to executable-schema freeze under inherited explicit trust assumptions.

It does not prove:
- implementation correctness;
- trust-root/operator honesty beyond explicit thresholds;
- hardware/workload-attestation correctness;
- provider correctness;
- cloud/IAM security;
- legal/compliance sufficiency.

Until independent closure:
- R8 v1-v10 = CHANGES_REQUIRED;
- R8 v11 = NOT_IMPLEMENTED / INDEPENDENT_REVIEW_REQUIRED;
- executable-schema freeze = BLOCKED;
- PR #39 = NON_AUTHORITATIVE;
- PR #40 = NON_AUTHORITATIVE;
- holistic governance = CHANGES_REQUIRED;
- authority effect = NONE.
