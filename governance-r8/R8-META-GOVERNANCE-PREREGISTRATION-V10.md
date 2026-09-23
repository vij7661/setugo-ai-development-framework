# R8 Meta-Governance Redesign v10 — Successor Preregistration

Status: **PREREGISTERED_DESIGN_V10 — NOT_IMPLEMENTED — INDEPENDENT_REVIEW_REQUIRED**
Authority effect: **NONE**

Effective design lineage:
- R8 v4: `d779eb495b5830674e0258d4d27b768f77e10471`
- R8 v5: `53d695dff34d14365770d1dbdad8c6620e31a503`
- R8 v6: `e0e6995a61dab629ff49efc19f6d6128936b9c20`
- R8 v7: `fad366add685a978c55837e420e3bcb0939d41aa`
- R8 v8: `58e95ca8cc8beb2125413d794ec08d4333a55521`
- R8 v9: `0948ed0e83d9de128ca9c12df5784286f15af9eb`
- This v10 document supersedes prior generations only where stronger or more specific.

R8 v9 review adjudication:
- `c209a1fdae549ecbb4713d45f8a7bc34967efa2c`

## 1. Objective

R8 v10 closes the remaining design blockers before executable-schema freeze.

Core rule:

> The semantic registry structure must be capable of representing the resolver's lineage/scope semantics, and sequencer configuration changes must cryptographically bind the exact transferred state into both JOINT entry and activation.

R8 v10 does not grant schema-freeze, implementation, qualification, merge, release, deploy, production, policy, or terminal authority.

## 2. CSM-3 — Scoped Semantic Registry Envelope

### R8V10-I001 — CSM-3 supersedes CSM-2 entry uniqueness

The v6 rule "duplicate semantic_input_id is rejected" is superseded.

CSM-3 contains multiple semantic entries for one semantic_input_id when they differ by lineage, scope, or version.

CSM-3 canonical envelope:

`{csm_version:"CSM-3", constitution_id, semantic_entries[]}`

### R8V10-I002 — SemanticEntry schema

Every SemanticEntry contains:
- `semantic_entry_id`;
- `semantic_input_id`;
- `semantic_lineage_id`;
- `semantic_version`;
- canonical `scope_tuple`;
- `specificity_score`;
- lifecycle state;
- predecessor_entry_id or null;
- successor_of_entry_id or null;
- scope_replacement_mapping_id or null;
- any_scope_permission_id or null;
- semantic_class;
- artifact_or_rule_digest;
- schema/version;
- source authority;
- constitutional binding when applicable.

### R8V10-I003 — Canonical scope tuple

The canonical scope tuple is ordered exactly:

`{root_namespace, tenant_id, organization_id, project_id, experiment_or_release_id}`

Each component is either:
- exact stable ID; or
- literal `ANY`, only where the active ANYScopePermission permits it.

No human alias may appear in scope_tuple.

### R8V10-I004 — SemanticEntryKey

`semantic_entry_key = SHA-256(GCP-1({semantic_input_id, semantic_lineage_id, semantic_version, scope_tuple}))`

Duplicate semantic_entry_key is rejected.

Duplicate semantic_input_id alone is permitted.

### R8V10-I005 — Canonical sorting

`semantic_entries[]` is sorted by:
1. semantic_input_id bytes;
2. semantic_lineage_id bytes;
3. descending specificity_score;
4. semantic_version;
5. semantic_entry_key bytes.

The sorting rule is part of the CSM-3 constitutional semantic artifact.

### R8V10-I006 — Specificity score is derived

specificity_score is derived from scope_tuple as the count of exact non-ANY components.

Stored specificity_score must equal the derived value or registration is rejected.

A caller cannot choose specificity.

## 3. CSM-3 lifecycle and CSRULE-2 integration

### R8V10-I007 — Resolver reads CSM-3 directly

CSRULE-2 candidate construction, lifecycle evaluation, predecessor/successor validation, ANYScopePermission lookup, and cross-lineage mapping all operate directly over CSM-3 SemanticEntry records.

No secondary registry may reinterpret semantic scope or lineage.

### R8V10-I008 — Same-scope revoked replacement registration

If a REVOKED entry exists for one semantic_input_id + lineage + exact scope, a new ACTIVE entry at that same lineage/scope is registrable only when:
- `successor_of_entry_id` references the revoked entry; or
- a valid constitutional ScopeReplacementMapping explicitly maps from that revoked entry.

Otherwise registration returns `SEMANTIC_SUCCESSOR_REQUIRED`.

### R8V10-I009 — ScopeReplacementMapping

A ScopeReplacementMapping is a constitutional semantic object containing:
- mapping_id;
- semantic_input_id;
- semantic_lineage_id;
- revoked_entry_id;
- old_scope_tuple;
- new_scope_tuple;
- old_specificity;
- new_specificity;
- justification/transition class ID;
- constitutional amendment evidence digest;
- effective sequence.

The mapping itself is CSM-bound.

### R8V10-I010 — Replacement-scope specificity

A replacement scope may differ in specificity only when ScopeReplacementMapping explicitly states the new specificity and constitutional amendment authorizes that change.

When such mapping exists:
- the revoked entry and mapped successor form one replacement chain;
- CSRULE-2 evaluates the successor using its new scope for future matching;
- lower-general entries cannot unblock the old revoked scope by themselves;
- the old scope remains blocked unless the mapping explicitly declares that the new scope replaces it for that decision scope.

Absent this mapping, successor re-establishment requires exact scope and equal specificity.

### R8V10-I011 — Revoked-scope resolution

For a decision scope:
1. gather all CSM-3 matching entries in the same semantic_input_id + semantic_lineage_id;
2. compute Smax before lifecycle filtering;
3. if an Smax REVOKED entry exists, resolve only through a valid successor chain or ScopeReplacementMapping;
4. if no valid successor applies, return `SEMANTIC_SCOPE_REVOKED`;
5. never fall back to lower specificity.

### R8V10-I012 — Cross-lineage mapping

Cross-lineage transition is allowed only through a constitutional `SemanticLineageMapping` object binding:
- old_lineage_id;
- new_lineage_id;
- source entry/scope;
- destination entry/scope;
- exact transition semantics;
- constitutional evidence.

No implicit cross-lineage fallback exists.

## 4. ANYScopePermission registration enforcement

### R8V10-I013 — Permission checked at registration

Before a SemanticEntry using ANY is admitted:
- resolve active ANYScopePermission for its semantic_class;
- verify every ANY tuple position is allowed;
- bind `any_scope_permission_id` to the entry.

Policy below constitutional level cannot create or broaden ANY permission.

### R8V10-I014 — Permission drift

If ANYScopePermission is revoked or narrowed:
- affected entries do not silently remain valid;
- their lifecycle enters `SCOPE_PERMISSION_REEVALUATION_REQUIRED`;
- new authority decisions cannot use them until revalidated or superseded.

## 5. State Transfer Certificate — STC-1

### R8V10-I015 — STC-1 common structure

Both LAS-3 and GGS-3 configuration rotations require a `StateTransferCertificate`.

STC-1 binds:
- system_id = LAS-3 or GGS-3;
- old_config_generation;
- old_config_digest;
- proposed_new_config_digest;
- transfer_snapshot_index;
- committed_log_prefix_digest;
- highest_seen_term;
- highest_committed_index;
- highest_applied_index where applicable;
- last_committed_entry_digest;
- state_root_digest;
- StreamHeadMap root where applicable;
- idempotency/dedup ledger root;
- prior certificate-chain digest;
- authorization/namespace roots for GGS where applicable;
- transition_id;
- STC digest.

### R8V10-I016 — Old-config certification

Before ENTER_JOINT, the old configuration must commit/sign the STC-1 snapshot with its current lawful quorum.

The snapshot index must be at least the current committed index and exactly match the state used to seed the new replicas.

### R8V10-I017 — New-config acceptance

Every proposed new replica must:
- install the exact STC-1 state;
- attest matching roots/digests;
- satisfy workload/controller requirements.

The new configuration produces a `StateTransferAcceptanceCertificate` signed by the new quorum over the same STC digest.

### R8V10-I018 — JOINT binding

`ENTER_JOINT(old,new)` must reference:
- exact STC-1 digest;
- old-config STC quorum certificate;
- new-config acceptance certificate;
- expected configuration-stream head.

If any transferred state root/digest differs, ENTER_JOINT is rejected.

### R8V10-I019 — JOINT quorum semantics

Configuration-transition quorum is:

- PRE_JOINT: lawful old configuration quorum only.
- JOINT_ENTERED before ACTIVATE: both old quorum and new quorum are required for every configuration-transition command and authority commit governed by the rotating sequencer.
- POST_ACTIVATE from exact activation index: lawful new configuration quorum only.

"Current valid configuration" is defined solely by this state machine.

### R8V10-I020 — ACTIVATE binding

`ACTIVATE(new)` must reference:
- exact committed ENTER_JOINT certificate;
- exact STC digest;
- exact new_config_digest;
- exact activation index/sequence.

Any mismatch returns `CONFIG_TRANSITION_MISMATCH`.

### R8V10-I021 — State-transfer mismatch

A proposed/joining replica is non-voting and rotation is blocked if any of these mismatch STC:
- term;
- log/commit/applied index;
- last committed entry digest;
- StreamHeadMap/state root;
- idempotency ledger;
- prior certificate-chain digest;
- GGS namespace/authorization root;
- configuration generation.

## 6. CTS-2 — Atomic configuration transition stream

### R8V10-I022 — CTS-2 supersedes ambiguous CTS-1 wording

CTS-2 preserves v9 single-predecessor CAS semantics and additionally requires STC-1 bindings.

A configuration stream event contains:
- transition state = PRE_JOINT | JOINT | ACTIVE;
- old/new config digests;
- STC digest;
- ENTER_JOINT certificate digest;
- activation index when active;
- stream seq/head;
- idempotency key.

### R8V10-I023 — Racing JOINT proposals

Two distinct ENTER_JOINT proposals for one PRE_JOINT predecessor:
- exactly one may commit;
- loser receives `CONFIG_HEAD_CONFLICT`;
- losing STC cannot be activated.

### R8V10-I024 — ACTIVATE exactness

ACTIVATE for:
- a different new config;
- a different STC;
- a different JOINT certificate;
- a stale config-stream predecessor

is rejected.

## 7. Blind review packet hygiene

### R8V10-I025 — Semantic projection rule

The blind reviewer packet may omit/redact administrative lines whose only content is a prior review/adjudication commit/hash reference.

It must not remove or alter:
- any invariant;
- any case;
- any guard;
- any claim boundary;
- any status affecting authority;
- any candidate/source commit or blob needed to bind the reviewed subject.

The packet header states that administrative prior-review references were redacted for blindness.

Canonical repository files remain unchanged and separately verifiable by exact commit/blob.

## 8. Additional Guard Catalog v10

| Guard | Mechanism | Positive | Negatives with fault-proof class |
|---|---|---|---|
| G100 | CSM-3 multi-entry scoped semantic envelope | V10-001 | V10-002 FP0; V10-003 FP5 |
| G101 | CSRULE-2 valid successor/replacement mapping | V10-004 | V10-005 FP5; V10-006 FP5 |
| G102 | Cross-lineage transition control | V10-007 | V10-008 FP5 |
| G103 | ANYScopePermission constitutional boundary | V10-009 | V10-010 FP5; V10-011 FP5 |
| G104 | LAS-3 STC-1 continuity | V10-012 | V10-013 FP3; V10-014 FP5 |
| G105 | GGS-3 STC-1 continuity | V10-015 | V10-016 FP3; V10-017 FP5 |
| G106 | CTS-2 JOINT/ACTIVATE exact binding | V10-018 | V10-019 FP2; V10-020 FP2; V10-021 FP5 |
| G107 | Blind packet semantic projection integrity | V10-022 | V10-023 FP5 |

## 9. R8 v10 preregistered cases

### CSM-3
- V10-001 two valid entries share semantic_input_id but differ by lineage/scope/version -> both register with distinct semantic_entry_key.
- V10-002 two entries have identical semantic_entry_key -> duplicate reject.
- V10-003 stored specificity differs from scope-derived specificity -> SEMANTIC_SCOPE_INVALID.

### Revoked scope successor
- V10-004 revoked exact-scope entry + constitutionally valid ACTIVE successor referencing it -> successor re-establishes scope and resolves.
- V10-005 revoked exact-scope entry + ACTIVE same-scope entry with no successor/mapping reference -> SEMANTIC_SUCCESSOR_REQUIRED at registration.
- V10-006 replacement scope changes specificity without valid ScopeReplacementMapping -> cannot unblock revoked scope.

### Cross-lineage
- V10-007 valid constitutional SemanticLineageMapping from revoked lineage to new lineage -> mapped successor eligible per mapping.
- V10-008 lower/general entry in different lineage with no mapping -> no fallback; blocked/unbound.

### ANY permission
- V10-009 constitutionally permitted ANY position registers and resolves according to specificity.
- V10-010 project/org policy attempts broaden ANYScopePermission -> reject.
- V10-011 ANY entry's bound permission is revoked/narrowed -> SCOPE_PERMISSION_REEVALUATION_REQUIRED; cannot silently remain authority.

### LAS state transfer
- V10-012 old LAS quorum signs STC, new quorum accepts exact same snapshot, ENTER_JOINT/ACTIVATE reference exact certificates -> rotation eligible.
- V10-013 joining LAS replica has mismatched StreamHeadMap/idempotency/log state -> non-voting; ENTER_JOINT reject.
- V10-014 ACTIVATE references different STC or JOINT certificate -> CONFIG_TRANSITION_MISMATCH.

### GGS state transfer
- V10-015 old GGS quorum signs STC including namespace/authorization roots, new quorum accepts exact state -> rotation eligible.
- V10-016 joining GGS replica has mismatched namespace/authorization/idempotency root -> non-voting; ENTER_JOINT reject.
- V10-017 ACTIVATE references state-transfer certificate not accepted by new quorum -> reject.

### Configuration transition races
- V10-018 one valid CTS-2 ENTER_JOINT from PRE_JOINT -> commits and enters JOINT.
- V10-019 two different ENTER_JOINT proposals race from same predecessor -> exactly one commits; loser CONFIG_HEAD_CONFLICT.
- V10-020 same transition ID with different proposed config/STC -> IDEMPOTENCY_CONFLICT.
- V10-021 during JOINT, command signed only by old or only by new quorum -> reject; both required.

### Packet hygiene
- V10-022 blind packet redacts only prior adjudication-reference metadata while semantic digests/sections remain complete -> packet valid.
- V10-023 semantic rule/case/guard removed under guise of blind redaction -> packet invalid/incomplete.

## 10. Schema-freeze gate

Even a future v10 `BOUNDED_PASS` authorizes only executable-schema-freeze preparation.

Before implementation:
- CSM-3/SemanticEntry/ScopeReplacementMapping/SemanticLineageMapping schemas frozen;
- CSRULE-2 resolver contract frozen against CSM-3;
- STC-1 and CTS-2 schemas frozen for LAS-3 and GGS-3;
- all G001-G107 CaseProofContracts frozen with positive controls and FP classes;
- blind schema packet independently reviewed if required by effective governance.

## 11. Claim boundary

A future R8 v10 bounded design pass establishes only sufficient design closure to proceed to executable-schema freeze under inherited explicit trust assumptions.

It does not prove:
- implementation correctness;
- trust-root/operator honesty beyond explicit thresholds;
- hardware/workload-attestation correctness;
- provider correctness;
- cloud/IAM security;
- legal/compliance sufficiency.

Until independent closure:
- R8 v1-v9 = CHANGES_REQUIRED;
- R8 v10 = NOT_IMPLEMENTED / INDEPENDENT_REVIEW_REQUIRED;
- executable-schema freeze = BLOCKED;
- PR #39 = NON_AUTHORITATIVE;
- PR #40 = NON_AUTHORITATIVE;
- holistic governance = CHANGES_REQUIRED;
- authority effect = NONE.
