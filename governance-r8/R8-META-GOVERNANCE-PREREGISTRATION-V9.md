# R8 Meta-Governance Redesign v9 — Successor Preregistration

Status: **PREREGISTERED_DESIGN_V9 — NOT_IMPLEMENTED — INDEPENDENT_REVIEW_REQUIRED**
Authority effect: **NONE**

Effective design lineage:
- R8 v4 commit `d779eb495b5830674e0258d4d27b768f77e10471`
- R8 v5 commit `53d695dff34d14365770d1dbdad8c6620e31a503`
- R8 v6 commit `e0e6995a61dab629ff49efc19f6d6128936b9c20`
- R8 v7 commit `fad366add685a978c55837e420e3bcb0939d41aa`
- R8 v8 commit `58e95ca8cc8beb2125413d794ec08d4333a55521`
- This v9 document supersedes prior generations only where it states a stronger or more specific rule.

R8 v8 review adjudication:
- `e37fb74f2485768d985ba8fdec9fb18c684c0dfb`

## 1. Objective

R8 v9 closes the remaining design blockers before executable-schema freeze.

Core rule:

> A revoked specific semantic rule can never silently fall back to a weaker general rule; sequencer rotation cannot forget replay state or fork at JOINT entry; generator history and reconciliation independence are explicit constitutional semantics; and every scope wildcard is authorized before registration.

R8 v9 does not grant schema-freeze, implementation, qualification, merge, release, deploy, production, policy, or terminal authority.

## 2. CSRULE-2 — Revocation-aware semantic scope resolution

### R8V9-I001 — Scope registration validation precedes resolution

A semantic entry may be registered only when:
- its semantic_input_id exists;
- its scope tuple is canonical;
- every `ANY` component is permitted by the active constitutional `ANYScopePermission` rule for that semantic class;
- its semantic lineage ID is explicit;
- its predecessor/successor relation, if any, is valid;
- no conflicting ACTIVE entry already exists at the exact same semantic_input_id + scope + lineage/version slot.

Invalid scope registration returns `SEMANTIC_SCOPE_INVALID` and never enters the CSM registry.

### R8V9-I002 — ANYScopePermission

For each constitutional semantic class, `ANYScopePermission` is a CSM-bound rule listing which scope tuple components may use `ANY`.

A component not explicitly listed is exact-only.

Project/org policy cannot broaden this permission.

### R8V9-I003 — Candidate-set construction

For one authority resolution, CSRULE-2 first constructs the full matching candidate set from all entries in the same `semantic_input_id + semantic_lineage_id` whose non-ANY scope components match the decision scope.

Lifecycle state is not filtered yet.

Each candidate receives its specificity score as the number of exact non-ANY components.

### R8V9-I004 — Highest matching specificity is fixed before lifecycle filtering

Let `Smax` be the maximum specificity across the full matching candidate set, regardless of lifecycle state.

CSRULE-2 examines every candidate at `Smax`.

It does **not** discard REVOKED/SUPERSEDED/RETIRED candidates before Smax is determined.

### R8V9-I005 — Revoked-specific block

If any candidate at `Smax` is `REVOKED`, and no constitutionally valid ACTIVE successor at the same scope/lineage/version relation explicitly supersedes that revoked entry, resolution returns:

`SEMANTIC_SCOPE_REVOKED`

No lower-specificity ACTIVE entry, including an ANY-scoped general entry, may be selected.

### R8V9-I006 — Successor re-establishment

A revoked scope is re-established only by an ACTIVE successor that:
- references the exact revoked predecessor;
- has the exact same effective scope or an explicitly constitutionally authorized replacement scope;
- was created by the required constitutional amendment path;
- is current under CSM lifecycle state;
- is not itself revoked.

This successor participates at Smax.

### R8V9-I007 — Non-revoked lifecycle handling

After the revoked-scope check:
- SUPERSEDED and RETIRED entries at Smax are ineligible for current use;
- exactly one ACTIVE entry at Smax -> resolve to it;
- zero ACTIVE entries -> `SEMANTIC_DEPENDENCY_UNBOUND`;
- more than one ACTIVE entry -> `SEMANTIC_ENTRY_CONFLICT`.

There is no lower-specificity fallback after an Smax conflict or lifecycle block.

### R8V9-I008 — Cross-lineage fallback forbidden

A matching lower-specificity entry from another lineage cannot replace a blocked/revoked higher-specificity entry unless a constitutional mapping event explicitly declares the lineage transition and successor scope.

Absent that mapping, result remains blocked.

## 3. LAS-3 formal version identity

### R8V9-I009 — LAS-3 is the effective sequencer version

The authority sequencer defined by v6 LAS-2 atomic StreamHeadMap semantics plus v7 joint-consensus rotation is formally named `LAS-3`.

Its CSM-bound configuration artifact contains:
- `sequencer_version = LAS-3`;
- configuration generation;
- replica identities;
- quorum rule;
- executable/config digests;
- workload-attestation policy;
- hard-state schema digest;
- StreamHeadMap schema digest;
- idempotency-ledger schema digest;
- rotation protocol digest.

No runtime may claim LAS-3 while using an older or different semantic artifact set.

## 4. LAS-3 rotation idempotency continuity

### R8V9-I010 — Required transferred state

Before a new LAS-3 replica may vote in JOINT or active configuration, it must install and attest:
- highest_seen_term;
- vote_for_current_term;
- highest_committed_log_index;
- highest_applied_log_index;
- last_committed_entry_digest;
- full current StreamHeadMap root;
- **idempotency/deduplication ledger root and replay-window state**;
- prior certificate chain needed for verification;
- active configuration generation.

### R8V9-I011 — Idempotency ledger equivalence

The joining replica's idempotency-ledger root must equal the root committed by the old configuration at the JOINT-entry prerequisite index.

Mismatch or missing ledger state -> replica is non-voting.

A previously consumed idempotency key remains consumed after rotation.

### R8V9-I012 — Replay after rotation

If a request presents a previously consumed idempotency key:
- same event digest -> returns the previously committed result/certificate;
- different event digest -> `IDEMPOTENCY_CONFLICT`.

Configuration change never resets key consumption.

## 5. Configuration Transition Stream — CTS-1

### R8V9-I013 — One canonical configuration-transition stream

GGS-3 and LAS-3 each maintain one non-commutative configuration-transition stream governed by the current valid configuration.

A transition command binds:
- system = GGS-3 or LAS-3;
- old_config_generation;
- old_config_digest;
- proposed_new_config_digest;
- transition_id/idempotency_key;
- expected_config_stream_seq;
- expected_config_stream_head.

### R8V9-I014 — Atomic JOINT entry

`ENTER_JOINT(old,new)` is a single CAS/linearized configuration-stream command.

At most one distinct proposed new configuration can consume the current old-configuration predecessor.

Concurrent different JOINT proposals:
- exactly one may commit;
- the loser receives `CONFIG_HEAD_CONFLICT`;
- no alternate JOINT branch is authoritative.

### R8V9-I015 — JOINT retry/idempotency

Retry with the same transition_id + same proposed_new_config_digest returns the same committed JOINT result.

Same transition_id with a different proposed digest -> `IDEMPOTENCY_CONFLICT`.

### R8V9-I016 — ACTIVATE binds committed JOINT

`ACTIVATE(new)` must reference the exact committed JOINT transition certificate and proposed_new_config_digest.

An activation for a different new config or a competing JOINT proposal is rejected.

### R8V9-I017 — Rotation race proof applies to GGS-3 and LAS-3

The same CTS-1 race semantics are mandatory for both sequencers.

Neither may rely only on generic stream behavior without its configuration-transition binding.

## 6. Schema Generator Historical Validity Policy — SGHVP-1

### R8V9-I018 — SGHVP-1 is CSM-bound

Every SchemaProvenanceGenerator registry class binds one `SchemaGeneratorHistoricalValidityPolicy`.

The reference SGHVP-1 defines:
- generator revocation/compromise effective sequence;
- historical pre-effective validity rule;
- post-effective invalidity rule;
- retrospective invalidation event schema;
- requalification trigger;
- replacement-generator non-inheritance rule.

### R8V9-I019 — Pre-effective output

Schema/provenance output generated strictly before the compromise/revocation effective sequence remains historically attributable and may remain valid only if no retrospective invalidation event covers it.

Its exact generation event, attestation, input design digests, and output digest remain bound.

### R8V9-I020 — Post-effective output

Output generated at or after the effective compromise/revocation sequence is invalid for schema freeze and returns `SCHEMA_GENERATOR_INVALID_AT_GENERATION`.

Unknown generation sequence -> `SCHEMA_GENERATOR_VALIDITY_UNCERTAIN`.

### R8V9-I021 — Retrospective invalidation

A governed `SchemaGeneratorRetrospectiveInvalidation` event may invalidate an exact:
- generator ID;
- sequence/time range;
- generation-event set;
- output schema/provenance set.

Affected schema-freeze artifacts become non-promotable and require regeneration/requalification.

History is preserved; no deletion or silent rewrite occurs.

### R8V9-I022 — Replacement generator

A replacement generator must be independently enrolled/attested and may regenerate artifacts only from the exact authoritative source design lineage.

It inherits no validity, signature identity, or approval from the replaced generator.

## 7. Reconciler Independence Profile — RIP-1

### R8V9-I023 — Independent effect reconciler identity

A reconciler used after executor revocation/compromise must be an active QualifiedEffectReconciler whose registry record binds:
- canonical_subject_id;
- admin_domain_id;
- root delegation lineage;
- credential ID;
- WorkloadAttestation policy;
- allowed providers/actions/effect classes;
- independence rule ID.

### R8V9-I024 — Independence from compromised executor

For the affected effect class, the reconciler must satisfy:
- canonical_subject_id != compromised executor canonical_subject_id;
- active credential != compromised executor credential;
- workload/execution identity distinct;
- no prohibited common root delegation ancestor;
- distinct admin_domain_id when the effect-class independence rule requires administrative diversity.

Aliases resolving to the same canonical subject count as the same actor.

### R8V9-I025 — Reconciler authority is observation-only

The independent reconciler may:
- query qualified provider state;
- bind provider receipt/observation;
- classify external state.

It cannot:
- alter the original EffectIntent;
- mint a new logical effect;
- mark success without provider-specific reconciliation evidence;
- bypass compensation governance.

## 8. Additional Guard Catalog v9

| Guard | Mechanism | Positive | Negatives with fault-proof class |
|---|---|---|---|
| G092 | CSRULE-2 revoked-specific anti-fallback | V9-001 | V9-002 FP5; V9-003 FP5; V9-004 FP5 |
| G093 | ANYScopePermission registration | V9-005 | V9-006 FP5; V9-007 FP5 |
| G094 | LAS-3 idempotency-ledger rotation continuity | V9-008 | V9-009 FP3; V9-010 FP2 |
| G095 | GGS-3 CTS-1 JOINT race | V9-011 | V9-012 FP2; V9-013 FP2 |
| G096 | LAS-3 CTS-1 JOINT race | V9-014 | V9-015 FP2; V9-016 FP2 |
| G097 | SGHVP-1 generator historical validity | V9-017 | V9-018 FP1; V9-019 FP1; V9-020 FP5 |
| G098 | Effect reconciler independence | V9-021 | V9-022 FP1; V9-023 FP6 |
| G099 | LAS-3 semantic-version identity | V9-024 | V9-025 FP5 |

## 9. R8 v9 preregistered cases

### CSRULE-2 / revoked-specific fallback
- V9-001 higher-specificity ACTIVE rule + lower-general ACTIVE rule -> resolve higher-specificity ACTIVE rule.
- V9-002 higher-specificity REVOKED rule + lower-specificity ACTIVE general rule -> SEMANTIC_SCOPE_REVOKED; no fallback.
- V9-003 higher-specificity REVOKED rule + lower-specificity ACTIVE ANY rule -> SEMANTIC_SCOPE_REVOKED; no fallback.
- V9-004 two ACTIVE rules tied at Smax -> SEMANTIC_ENTRY_CONFLICT; no lower fallback.

### ANY scope
- V9-005 semantic class explicitly permits ANY at project scope and valid entry registers.
- V9-006 semantic class does not permit ANY at requested tuple component -> SEMANTIC_SCOPE_INVALID.
- V9-007 entry attempts ANY to bypass revoked exact-scope lineage -> registration/resolution cannot bypass revoked scope.

### LAS idempotency continuity
- V9-008 new LAS replica transfers matching idempotency root and becomes voting.
- V9-009 new LAS replica lacks/mismatches idempotency ledger -> non-voting.
- V9-010 after rotation, consumed idempotency key + different event digest -> IDEMPOTENCY_CONFLICT.

### GGS JOINT race
- V9-011 one valid ENTER_JOINT from current GGS config -> commits.
- V9-012 two different GGS new-config proposals race from same old config -> exactly one commits; loser CONFIG_HEAD_CONFLICT.
- V9-013 same GGS transition_id retried with different config digest -> IDEMPOTENCY_CONFLICT.

### LAS JOINT race
- V9-014 one valid ENTER_JOINT from current LAS-3 config -> commits.
- V9-015 two different LAS-3 new-config proposals race from same old config -> exactly one commits; loser CONFIG_HEAD_CONFLICT.
- V9-016 same LAS transition_id retried with different config digest -> IDEMPOTENCY_CONFLICT.

### Schema generator historical validity
- V9-017 pre-effective SPG output outside retrospective invalidation -> remains historically valid under SGHVP-1.
- V9-018 post-effective SPG output -> SCHEMA_GENERATOR_INVALID_AT_GENERATION.
- V9-019 unknown generation sequence under compromised generator -> SCHEMA_GENERATOR_VALIDITY_UNCERTAIN.
- V9-020 retrospective invalidation covering frozen schema artifact -> artifact becomes non-promotable pending regeneration/requalification.

### Reconciler independence
- V9-021 independently qualified reconciler with distinct canonical subject and required domain separation verifies provider state -> reconciliation evidence eligible.
- V9-022 reconciler alias resolves to same canonical subject as revoked executor -> independence reject.
- V9-023 reconciler asserts success without qualified external provider observation -> no SUCCEEDED_RECONCILED state.

### LAS version identity
- V9-024 Runtime/CSM LAS artifact set exactly matches LAS-3 semantic digest set -> eligible.
- V9-025 component labelled LAS-3 but idempotency/rotation artifact digest corresponds to older semantics -> semantic/version mismatch; authority effect NONE.

## 10. Review packet completeness

The v9 blind packet MUST contain:
1. v9 blind reviewer prompt;
2. canonical R8 v4 design;
3. canonical R8 v5 design;
4. canonical R8 v6 design;
5. canonical R8 v7 design;
6. canonical R8 v8 design;
7. canonical R8 v9 design.

It intentionally excludes reviewer findings/adjudications from v1-v8.

The packet therefore contains:
- G001-G025 + V4-001…V4-084 from canonical v4;
- G026-G042 from v5;
- G043-G066 from v6;
- G067-G081 plus consolidated FP mapping from v7;
- G082-G091 from v8;
- G092-G099 from v9.

## 11. Schema-freeze gate

Even a future v9 `BOUNDED_PASS` authorizes only executable-schema-freeze preparation.

Before implementation:
- CSRULE-2/ANYScopePermission machine-readable rules frozen;
- LAS-3 and GGS-3 CTS-1 schemas frozen;
- SGHVP-1 frozen and CSM-bound;
- RIP-1 reconciler schema frozen;
- all G001-G099 CaseProofContracts frozen with positive controls and FP classes;
- schema packet independently reviewed where effective governance requires it.

## 12. Claim boundary

A future R8 v9 bounded design pass establishes only sufficient design closure to proceed to executable-schema freeze under the explicit trust assumptions already frozen in v4-v8.

It does not prove:
- trust-root/operator honesty beyond explicit thresholds;
- hardware/workload-attestation vendor correctness;
- provider correctness;
- implementation correctness;
- external provider side-effect correctness;
- cloud/IAM security;
- legal/compliance sufficiency.

Until independent closure:
- R8 v1-v8 = CHANGES_REQUIRED;
- R8 v9 = NOT_IMPLEMENTED / INDEPENDENT_REVIEW_REQUIRED;
- executable-schema freeze = BLOCKED;
- PR #39 = NON_AUTHORITATIVE;
- PR #40 = NON_AUTHORITATIVE;
- holistic governance = CHANGES_REQUIRED;
- authority effect = NONE.
