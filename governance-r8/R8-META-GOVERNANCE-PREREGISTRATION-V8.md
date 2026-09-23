# R8 Meta-Governance Redesign v8 — Successor Preregistration

Status: **PREREGISTERED_DESIGN_V8 — NOT_IMPLEMENTED — INDEPENDENT_REVIEW_REQUIRED**
Authority effect: **NONE**

Effective design lineage:
- R8 v4 commit `d779eb495b5830674e0258d4d27b768f77e10471` supplies inherited G001-G025/V4 case semantics.
- R8 v5 commit `53d695dff34d14365770d1dbdad8c6620e31a503` is the inherited base.
- R8 v6 commit `e0e6995a61dab629ff49efc19f6d6128936b9c20` is an inherited overlay.
- R8 v7 commit `fad366add685a978c55837e420e3bcb0939d41aa` is an inherited overlay.
- This v8 document supersedes prior generations only where it states a stronger or more specific rule.

R8 v7 review adjudication:
- `b46716fb2337beeadff875f7e62713f5dc61aaa0`

## 1. Objective

R8 v8 closes the remaining design blockers before executable-schema freeze.

Core rule:

> No authority-bearing freshness, reservation, brokered input, configuration rotation, provenance generation, effect execution, migration commit, or semantic resolution may rely on an unauthenticated caller assertion, rollbackable local state, or omitted inherited semantics.

R8 v8 does not grant schema-freeze, implementation, qualification, merge, release, deploy, production, policy, or terminal authority.

## 2. Authorized T0 Successor Reservation — TSR-1

### R8V8-I001 — Reservation request is an authority object

`RESERVE_T0_SUCCESSOR` accepts a canonical `T0SuccessorReservationRequest` containing:

- trust_domain_id;
- current_t0_generation;
- predecessor_t0_manifest_digest;
- next_generation;
- exact successor_manifest_digest;
- successor_manifest_schema_version;
- predecessor-policy digest;
- exact EBA/root authorization proof digests;
- MTRFreshnessAttestation digest;
- reservation_nonce;
- request_id/idempotency_key.

### R8V8-I002 — Lawful authorization precondition

MTR may reserve a next generation only when the request proves the exact authorization class required by the current predecessor T0 policy.

For the reference design this requires:
- the predecessor constitutional/root quorum required for T0 succession;
- all approvals over the exact successor_manifest_digest and next_generation;
- valid active ControllerAttestations at the current EBA revocation high-water;
- distinct-controller/admin-domain rules required by the predecessor policy.

An ordinary software caller, Meta-Governor, MTR client, operator, or unprivileged service cannot reserve a T0 generation.

### R8V8-I003 — Authorization precedes slot consumption

MTR verifies the authorization proof before checking/consuming the generation slot.

An unauthorized or malformed request:
- returns `T0_RESERVATION_UNAUTHORIZED`;
- does not create a reservation;
- does not poison the generation slot;
- does not increment MTR generation state.

### R8V8-I004 — Atomic reservation

After authorization succeeds, MTR atomically performs:

`CAS(trust_domain_id, expected_current_generation, next_generation, EMPTY -> successor_manifest_digest)`

Exactly one digest may reserve next_generation.

A second different authorized digest for the same next_generation returns `T0_EQUIVOCATION`.

A retry with identical request_id + digest returns the existing reservation certificate.

### R8V8-I005 — Reservation certificate binding

`T0ReservationCertificate` binds:
- request digest;
- predecessor digest;
- current/next generation;
- successor digest;
- authorization-proof digest;
- MTR freshness/challenge digest;
- MTR response sequence;
- reservation monotonic sequence;
- MTR configuration generation;
- MTR signature/attestation.

BTW inclusion and T0 activation must bind the same certificate/digest.

## 3. MTR Response High-Water and Challenge Ledger — MTRF-2

### R8V8-I006 — MTR response sequence is monotonic authority state

Each verifier participating in authority-bearing decisions persists:
- highest_accepted_mtr_response_seq per trust_domain_id + MTR configuration generation;
- last accepted T0 generation/digest;
- last accepted BTW tree size/root;
- last accepted EBA revocation high-water.

This state is stored in rollback-resistant storage qualified under the deployment's T0/MTR profile.

### R8V8-I007 — Response sequence acceptance

An MTRFreshnessAttestation is rejected when:
- response_seq < verifier highest accepted response_seq;
- response_seq == highest accepted response_seq but any high-water digest/tuple differs;
- configuration generation is stale;
- challenge binding fails.

Acceptance atomically advances the verifier high-water state before the attestation may enter a VerifiedStateSeal.

### R8V8-I008 — MTRChallengeLedger

Authority-bearing MTR challenges are stored in a rollback-resistant `MTRChallengeLedger` with:
- challenge_id;
- trust_domain;
- verifier_instance;
- purpose;
- issued monotonic tick;
- state = ISSUED | CONSUMED | EXPIRED;
- expected minimum tuple;
- response_seq when consumed.

Challenge consumption is atomic with accepted-response high-water advancement.

### R8V8-I009 — Replay/outage rule

A consumed/expired challenge can never return to ISSUED.

No MTR response may be reused under a new challenge.

MTR outage/freshness failure remains fail closed; there is no authority-bearing stale-token fallback.

## 4. GGS-3 Configuration and Replica Rotation

### R8V8-I010 — GGS configuration artifact

The active GGS configuration is T0/CSM-bound and includes:
- configuration generation;
- replica canonical_subject_ids;
- admin-domain IDs;
- executable/configuration digests;
- workload-attestation policy;
- quorum rule;
- GGS state-root checkpoint digest.

### R8V8-I011 — Joint rotation

GGS replica/configuration rotation uses:
1. `GGS_CONFIG_JOINT(old,new)`;
2. state transfer and attestation;
3. `GGS_CONFIG_ACTIVATE(new)`.

During JOINT state, genesis commits require majority from both old and new configs.

### R8V8-I012 — Required transferred state

Each new GGS replica must install and attest:
- highest term/vote state;
- highest committed genesis index;
- last committed genesis digest;
- constitution namespace root;
- authorization-state root;
- idempotency records;
- prior certificate chain;
- MTR-mirrored namespace high-water.

Missing or mismatched state -> replica non-voting.

### R8V8-I013 — Activation and stale-config rejection

Activation commits at exact `ggs_activation_index`.

After activation:
- old-config-only certificates are invalid;
- configuration generation must match current T0/MTR high-water;
- an old configuration cannot regain authority through disk restore or replica replacement.

## 5. Attested AuthorityInputGateway — AIG-2

### R8V8-I014 — Gateway is root-sensitive

AuthorityInputGateway is a root-sensitive service principal.

It must have:
- registry identity;
- canonical_subject_id;
- exact executable/image digest;
- exact AIG configuration digest;
- WorkloadAttestation;
- active/non-revoked credential;
- exact tenant/trust-domain scope.

### R8V8-I015 — Broker channel identity

Each pre-opened broker IPC channel is bound to:
- evaluator WorkloadAttestation digest;
- gateway WorkloadAttestation digest;
- channel_id;
- allowed authority_input_id set or namespace;
- session nonce;
- creation sequence;
- expiration/closure state.

A channel cannot be rebound to another evaluator or gateway instance.

### R8V8-I016 — Gateway output proof

Each gateway response included in AuthorityReadSet binds:
- authority_input_id;
- value digest;
- source stream/store/head;
- semantic entry digest;
- gateway identity/attestation digest;
- channel_id;
- request nonce;
- response sequence;
- response signature/MAC under the qualified broker session.

Counterfeit/unattested gateway output -> `AIG_UNTRUSTED`.

### R8V8-I017 — Gateway revocation

If the gateway credential, workload attestation, or registry identity becomes revoked/invalid:
- new authority reads stop;
- open broker sessions become invalid;
- seals referencing post-revocation gateway responses are rejected.

## 6. Complete Decision Preseal Context — DPS-2

### R8V8-I018 — DecisionPresealContext

The canonical preseal object includes:

- trust_domain_id;
- constitution_id;
- tenant/project/task/effect scope;
- candidate/artifact/action;
- exact effect_id when an external effect is involved;
- effect_class;
- governance_snapshot_digest;
- AuthorityReadSet_digest;
- current T0 generation + manifest digest;
- accepted MTRFreshnessAttestation digest + response sequence;
- active LAS configuration generation + StreamHeadMap root;
- current revocation stream head;
- current MTR-mirrored revocation high-water when required;
- runtime identity mode;
- evaluator WorkloadAttestation digest;
- AuthorityInputGateway WorkloadAttestation digest;
- review/evidence gate state digest where relevant.

`decision_preseal_digest = SHA-256(GCP-1(DecisionPresealContext))`.

### R8V8-I019 — Time challenge binds DPS-2

The Time NonceLedger key and every TimeAttestation bind the exact decision_preseal_digest plus a single-use nonce.

Any change to the listed authority context requires a new time challenge and new final seal.

## 7. Attested Schema Provenance Generator — SPG-1

### R8V8-I020 — Schema generator is a qualified producer

Any generator that emits schema artifacts or SPM-1 provenance entries must be enrolled as `SchemaProvenanceGenerator`.

The registry record binds:
- generator_id;
- executable/image digest;
- RuntimeManifest;
- WorkloadAttestation policy;
- allowed input design artifacts;
- allowed output schema classes;
- signing credential;
- revocation status.

### R8V8-I021 — Generator output proof

Each schema artifact/SPM-1 entry binds:
- exact input design commit/blob IDs;
- generator executable/runtime digest;
- generator workload attestation;
- generation event ID;
- output schema digest;
- provenance-map digest;
- signature.

A provenance map from an unattested/drifted/unregistered generator is invalid.

### R8V8-I022 — Generator revocation/drift

If generator identity/executable/credential is revoked or mismatched:
- new output is rejected;
- prior output follows frozen historical-validity policy;
- schema freeze cannot silently regenerate with a different generator.

## 8. CSM-2 Applicable-Scope Resolution — CSRULE-1

### R8V8-I023 — Canonical scope tuple

Every semantic entry scope is expressed as:

`{trust_domain_id, constitution_id, tenant_id?, organization_id?, project_id?, object_class?, action_class?}`

Each component is either an exact stable ID or explicit `ANY` only when the constitutional semantic class permits it.

Human aliases are prohibited.

### R8V8-I024 — Specificity order

Applicable entries are selected only when every non-ANY component matches the decision scope.

Specificity score is the count of exact non-ANY components.

Resolution:
1. discard non-matching entries;
2. retain ACTIVE entries only;
3. choose the highest specificity score;
4. require exactly one entry at that highest score.

Zero -> `SEMANTIC_DEPENDENCY_UNBOUND`.

More than one -> `SEMANTIC_ENTRY_CONFLICT`.

No lower-specificity fallback occurs after a same-specificity conflict.

### R8V8-I025 — Supersession/revocation

SUPERSEDED/RETIRED entries never win current resolution.

REVOKED entry state cannot be bypassed by an older lower-specificity ACTIVE entry for the same semantic lineage unless a constitutionally valid successor explicitly establishes that scope.

## 9. QualifiedEffectExecutor Revocation State Machine — EESM-2

### R8V8-I026 — Executor validity at dispatch

Before moving INTENT_COMMITTED -> DISPATCHING, the executor must prove:
- active executor registry entry;
- valid workload attestation;
- current credential;
- current revocation head;
- exact allowed provider/action/effect class.

These proofs bind the dispatch attempt.

### R8V8-I027 — Revocation/compromise freeze

When executor revocation/compromise becomes effective:
- new dispatch by that executor is forbidden;
- DISPATCHING/ACKNOWLEDGED_UNVERIFIED effects handled by that executor move to `EXECUTOR_REVOKED_UNCERTAIN` unless already independently reconciled;
- provider reconciliation is required via a still-qualified independent reconciler/executor class;
- receipts signed only by the revoked executor cannot finalize success after the effective revocation sequence.

### R8V8-I028 — Replacement executor

A replacement executor may resume an in-flight effect only using:
- original effect_id;
- original immutable payload digest;
- original idempotency_key;
- original intent certificate;
- current reconciliation state.

It cannot create a new logical effect.

### R8V8-I029 — Compensation uncertainty

Compensation is a separate governed effect.

If compensation becomes uncertain or fails:
- state becomes `COMPENSATION_UNCERTAIN` or `COMPENSATION_FAILED_FINAL`;
- original effect is never relabelled successful;
- all attempts and provider observations remain preserved.

## 10. Migration Commit Freshness — MCF-1

### R8V8-I030 — Destination policy sealed at commit

RequalificationProof binds the exact destination governance snapshot digest used for qualification.

The migration `COMMIT_WITH_SEAL` must include the destination policy/governance stream head and snapshot digest.

If destination governance changed since proof creation:
- result = `MIGRATION_DESTINATION_STATE_CHANGED`;
- no migration authority commits;
- fresh requalification is required.

### R8V8-I031 — Omitted object failure

If any post-migration authority evaluation references a source-scope object not present in the committed migration object map:
- result = `MIGRATION_OBJECT_UNBOUND`;
- imported object has no inherited authority;
- the omission is preserved as failure evidence.

## 11. Trust-Loss Evidence and Sequence

### R8V8-I032 — TrustLossAssessment input proof

A lawful `TrustLossAssessment` binds:
- current MTR freshness response where available;
- last-good T0/MTR/BTW/LAS/anchor proofs;
- exact failed component probes;
- probe timestamps/monotonic sequences;
- recovery-context digest;
- attempted recovery actions;
- recovery quorum identities/approvals.

### R8V8-I033 — Terminal declaration sequence

Where a lawful recovery quorum still exists, TRUST_DOMAIN_UNRECOVERABLE is recorded through the current lawful recovery stream with one exact sequence/certificate.

If no lawful recovery commit path remains, the platform may only report local/advisory `TRUST_PATH_UNAVAILABLE`; it cannot fabricate an authoritative terminal transition.

## 12. GCP Reference Vector Manifest — GCP-RVM-2

### R8V8-I034 — Inherited vectors unchanged

All canonical-output vectors frozen before v7 retain identical expected canonical bytes/digests unless a constitutional GCP amendment explicitly changes them.

v7/v8 rejection vectors add no alternate canonical output.

### R8V8-I035 — RVM contents

`GCP-RVM-2` enumerates:
- vector ID;
- input representation;
- schema context;
- expected canonical bytes+digest OR expected rejection code;
- originating GCP rule/version.

Schema freeze must produce this manifest and independently verify it against the frozen reference implementation/artifact.

## 13. Complete Inherited Review Semantics

### R8V8-I036 — Canonical v4 inclusion is mandatory

The v8 blind design-review packet MUST include canonical R8 v4 design text from commit:

`d779eb495b5830674e0258d4d27b768f77e10471`

including G001-G025 and V4-001…V4-084 semantics.

A lookup/consolidated table alone is insufficient.

### R8V8-I037 — No silent weakening of inherited cases

The reviewer evaluates:
- v4 canonical cases;
- v5 additions;
- v6 additions;
- v7 consolidated FP mapping;
- v8 additions.

Where a later rule supersedes an earlier mechanism, the packet must state the supersession; case intent remains at least as strict unless explicitly constitutionally amended and independently reviewed.

## 14. Additional Guard Catalog v8

| Guard | Mechanism | Positive | Negatives with fault-proof class |
|---|---|---|---|
| G082 | Authorized T0 successor reservation | V8-001 | V8-002 FP1; V8-003 FP2; V8-004 FP5 |
| G083 | MTR response high-water/challenge rollback | V8-005 | V8-006 FP3; V8-007 FP1; V8-008 FP3 |
| G084 | GGS-3 configuration rotation | V8-009 | V8-010 FP3; V8-011 FP1 |
| G085 | Attested AuthorityInputGateway | V8-012 | V8-013 FP4; V8-014 FP1 |
| G086 | Complete decision-preseal context | V8-015 | V8-016 FP5; V8-017 FP1 |
| G087 | Attested SPM generator | V8-018 | V8-019 FP4; V8-020 FP5 |
| G088 | CSM applicable-scope resolution | V8-021 | V8-022 FP5; V8-023 FP5 |
| G089 | Effect executor revocation/reconciliation | V8-024 | V8-025 FP1; V8-026 FP6; V8-027 FP6 |
| G090 | Migration destination-policy freshness | V8-028 | V8-029 FP2; V8-030 FP5 |
| G091 | Inherited-v4 packet completeness | V8-031 | V8-032 FP5 |

## 15. R8 v8 preregistered cases

### T0 reservation
- V8-001 valid authorized successor reservation -> one certificate.
- V8-002 unauthorized caller with valid-looking digest attempts reservation -> T0_RESERVATION_UNAUTHORIZED; slot unchanged.
- V8-003 two separately authorized different digests race for same next generation -> exactly one reservation; other T0_EQUIVOCATION.
- V8-004 activation digest differs from authorized/reserved digest -> reject.

### MTR response/challenge state
- V8-005 fresh challenge + response_seq above persisted high-water -> accepted and atomically consumes challenge/advances high-water.
- V8-006 verifier local rollback presents lower persisted response high-water -> rollback-resistant store prevents authority use.
- V8-007 response_seq equal to accepted seq with conflicting tuple -> reject/equivocation.
- V8-008 consumed challenge ledger rolled-back in ordinary DB -> cannot regain authority.

### GGS rotation
- V8-009 joint old/new GGS quorums + transferred namespace/auth roots -> activation succeeds.
- V8-010 new GGS replica missing committed namespace/auth-root high-water -> non-voting.
- V8-011 old-config-only genesis certificate after activation -> reject.

### AuthorityInputGateway
- V8-012 attested registered gateway + bound broker channel produces valid read-set item.
- V8-013 counterfeit/unattested gateway response -> AIG_UNTRUSTED.
- V8-014 revoked gateway/broker session used for new authority read -> reject.

### Decision preseal/time
- V8-015 time proof binds full DPS-2 including MTR/LAS/revocation/runtime/effect ID -> valid for final seal.
- V8-016 any DPS-2 field changes after nonce issuance -> old time proof reject.
- V8-017 MTR response sequence/digest differs from preseal -> reject.

### SPM generator
- V8-018 enrolled attested SPG emits schema+SPM from exact authoritative inputs -> provenance valid.
- V8-019 generator executable/workload mismatch -> reject provenance.
- V8-020 SPM source commit/blob altered without regeneration event -> provenance mismatch.

### CSM scope
- V8-021 exactly one highest-specificity ACTIVE semantic entry -> resolve.
- V8-022 two ACTIVE entries tie at highest specificity -> SEMANTIC_ENTRY_CONFLICT.
- V8-023 no matching ACTIVE entry -> SEMANTIC_DEPENDENCY_UNBOUND.

### Effect executor
- V8-024 active attested executor dispatches and reconciles original effect -> SUCCEEDED_RECONCILED.
- V8-025 executor revoked before dispatch -> no dispatch.
- V8-026 executor revoked while effect is in-flight -> EXECUTOR_REVOKED_UNCERTAIN until independent reconciliation.
- V8-027 compensation result uncertain/fails -> explicit compensation-failure state; no fabricated success.

### Migration
- V8-028 destination policy head unchanged at commit -> migration may commit.
- V8-029 destination policy changes after RequalificationProof -> MIGRATION_DESTINATION_STATE_CHANGED.
- V8-030 omitted migrated object later referenced -> MIGRATION_OBJECT_UNBOUND.

### Packet completeness
- V8-031 blind packet includes canonical v4+v5+v6+v7+v8 design/case semantics and full guard map -> review-complete input.
- V8-032 canonical inherited case text omitted -> REVIEW_PACKET_INCOMPLETE; design review cannot close.

## 16. Review packet composition rule

The v8 blind packet must contain, in this order:

1. v8 blind reviewer prompt;
2. canonical R8 v4 design text;
3. canonical R8 v5 design text;
4. canonical R8 v6 design text;
5. canonical R8 v7 design text;
6. canonical R8 v8 design text.

It intentionally excludes reviewer findings/adjudications from v1-v7.

The v7 G001-G066 consolidated fault-proof table plus v7 G067-G081 and v8 G082-G091 must be present through canonical v7/v8 text.

## 17. Schema-freeze gate

Even a future v8 `BOUNDED_PASS` authorizes only executable-schema-freeze preparation.

Before implementation:
- SPM-1 generated by attested SPG-1;
- GCP-RVM-2 frozen;
- AIEP-1/AIG-2 schemas and attestation bindings frozen;
- GGS-3/LAS-3 configuration-rotation schemas frozen;
- EffectIntent/EffectState/Reconciliation/Compensation schemas frozen;
- all G001-G091 CaseProofContracts frozen with positive controls and FP0-FP6 requirements;
- schema packet independently reviewed where effective governance requires it.

## 18. Claim boundary

A future R8 v8 bounded design pass establishes only sufficient design closure to proceed to executable-schema freeze under explicit T0/EBA/MTR/BTW/GGS/LAS/workload-attestation assumptions.

It does not prove:
- external trust-root/operator honesty beyond explicit thresholds;
- hardware attestation vendor correctness;
- provider-internal model-memory isolation;
- provider external-effect correctness;
- implementation correctness;
- cloud/IAM security;
- legal/compliance sufficiency.

Until independent closure:
- R8 v1-v7 = CHANGES_REQUIRED;
- R8 v8 = NOT_IMPLEMENTED / INDEPENDENT_REVIEW_REQUIRED;
- executable-schema freeze = BLOCKED;
- PR #39 = NON_AUTHORITATIVE;
- PR #40 = NON_AUTHORITATIVE;
- holistic governance = CHANGES_REQUIRED;
- authority effect = NONE.
