# R8 Meta-Governance Redesign v7 — Successor Preregistration

Status: **PREREGISTERED_DESIGN_V7 — NOT_IMPLEMENTED — INDEPENDENT_REVIEW_REQUIRED**
Authority effect: **NONE**

Effective design:
- R8 v5 commit `53d695dff34d14365770d1dbdad8c6620e31a503` is the inherited base.
- R8 v6 commit `e0e6995a61dab629ff49efc19f6d6128936b9c20` is the inherited successor overlay.
- This v7 document supersedes v5/v6 only where v7 states a stronger or more specific rule.
- R8 v5 and v6 remain immutable and CHANGES_REQUIRED.

R8 v6 review adjudication:
- `5824d88dd68ca0f36ef6ea1a4294a3b385209d23`

## 1. Objective

R8 v7 closes the remaining design and review-packet blockers before executable-schema freeze.

Core rule:

> Authority freshness is live and challenge-bound; genesis and authority logs are rollback-resistant across configuration changes; every schema element and authority input has authoritative provenance; consequential effects remain non-complete until externally reconciled; and every load-bearing guard is present in one complete falsification catalog with explicit positive controls and fault-proof classes.

R8 v7 does not grant implementation, schema-freeze, qualification, merge, release, deploy, production, policy, or terminal authority.

## 2. MTR Freshness Protocol — MTRF-1

### R8V7-I001 — No cached MTR token for authority-bearing use

For any authority-bearing decision, a cached or previously issued MTR high-water token is insufficient.

The verifier must perform a live MTRF-1 challenge-response.

If live MTR freshness cannot be established, the result is `MTR_UNAVAILABLE`.

This supersedes the v6 allowance for a "still-valid previously attested high-water token" in authority-bearing use.

### R8V7-I002 — MTR challenge

The verifier generates:
- `mtr_challenge_id` as a random 256-bit value;
- `verifier_instance_id`;
- `trust_domain_id`;
- `purpose_class`;
- `expected_min_t0_generation`;
- `expected_min_btw_tree_size`;
- `expected_min_eba_revocation_seq`;
- local monotonic issuance tick.

The challenge is single-use.

### R8V7-I003 — MTRFreshnessAttestation

MTR signs:
- mtr_challenge_id;
- verifier_instance_id;
- trust_domain_id;
- purpose_class;
- current t0_generation + manifest digest;
- current BTW tree_size + root_hash;
- current EBA revocation high-water;
- current T0-domain lifecycle sequence;
- MTR monotonic response sequence;
- MTR configuration generation;
- response nonce echo;
- signature/attestation proof.

The response must satisfy every expected minimum in the challenge.

### R8V7-I004 — Freshness window and replay rejection

The verifier accepts an MTRFreshnessAttestation only:
- for the exact outstanding challenge;
- once;
- within **30 seconds of verifier monotonic time** from challenge issuance;
- before the verifier marks the challenge CONSUMED.

A response for another challenge, another verifier instance, another trust domain, another purpose, or an already-consumed challenge is rejected.

The 30-second window is only a liveness/replay bound; authority ordering remains sequence-based.

### R8V7-I005 — MTR outage

No stale-token fallback exists for root, constitutional, recovery, reviewer-qualification, schema-freeze, terminal, or other authority-bearing use.

MTR timeout/unavailability -> `MTR_UNAVAILABLE` and fail closed.

Non-authority read-only work may use explicitly labelled advisory cache state with authority effect NONE.

## 3. Atomic T0 successor reservation

### R8V7-I006 — RESERVE_T0_SUCCESSOR

MTR exposes one linearizable operation:

`RESERVE_T0_SUCCESSOR(expected_current_generation, next_generation, successor_manifest_digest)`

Preconditions:
- next_generation = expected_current_generation + 1;
- current MTR generation equals expected_current_generation;
- no reservation exists for next_generation.

Success atomically binds exactly one successor_manifest_digest to next_generation.

### R8V7-I007 — Conflicting reservation

A second different digest for the same next_generation is rejected as `T0_EQUIVOCATION`.

Retry with the same digest returns the same reservation certificate.

The reservation certificate is required before BTW inclusion/activation of the successor.

### R8V7-I008 — Activation binding

T0 successor activation requires:
- valid predecessor signatures/policy;
- MTR reservation certificate;
- BTW inclusion + consistency under predecessor trust;
- exact successor digest equal to reservation digest;
- MTR activation of the reserved generation.

No other digest can activate at that generation.

## 4. GGS-2 rollback-resistant genesis sequencer

### R8V7-I009 — GGS-2 supersedes GGS-1

Pre-genesis namespace sequencing uses GGS-2.

GGS-2 remains 3-replica / 2-of-3 but adds rollback-resistant hard state and configuration continuity.

### R8V7-I010 — GGSHardState

Each GGS replica persists in T0-approved monotonic/attested storage:
- highest_seen_term;
- vote_for_current_term;
- highest_committed_genesis_index;
- last_committed_genesis_digest;
- constitution_namespace_root_digest;
- bootstrap_authorization_state_root_digest;
- GGS configuration generation.

A replica with unverifiable or rolled-back hard state is non-voting.

### R8V7-I011 — GGS namespace root mirroring

After every committed genesis operation, GGS updates a signed namespace-root checkpoint containing:
- committed genesis index;
- constitution namespace root;
- authorization-state root;
- GGS configuration generation.

The latest checkpoint sequence/digest is mirrored into MTR high-water state.

A presented GGS state below MTR high-water is stale and cannot vote or authorize genesis.

### R8V7-I012 — Genesis commit certificate v2

A GenesisCommitCertificate binds:
- constitution_id;
- bootstrap_authorization_id;
- authorized_genesis_digest;
- GGS term/index;
- prior namespace-root digest;
- new namespace-root digest;
- prior authorization-root digest;
- new authorization-root digest;
- idempotency key;
- GGS configuration generation;
- 2-of-3 signer identities/signatures.

Rollback of a committed namespace to EMPTY cannot yield a valid current certificate.

## 5. LAS-3 configuration rotation continuity

### R8V7-I013 — LAS configuration is a constitutional semantic artifact

Every LAS configuration contains:
- config_generation;
- replica IDs/controller attestations;
- quorum rule;
- replica executable/config digests;
- workload-attestation requirements.

Its digest is CSM-bound.

### R8V7-I014 — Joint-consensus rotation

LAS rotation uses two committed phases:

1. `LAS_CONFIG_JOINT(old_config,new_config)`
2. `LAS_CONFIG_ACTIVATE(new_config)`

During JOINT state, every authority commit requires:
- majority of old config; and
- majority of new config.

New replicas must first install the exact committed log prefix, StreamHeadMap, idempotency state, highest term/index, and prior certificate chain.

### R8V7-I015 — Activation index

The activation event commits at one exact log index `activation_index`.

For log indices > activation_index:
- only new config certificates are accepted;
- old config-only certificates are rejected;
- config_generation must equal new generation.

MTR mirrors the highest active LAS configuration generation for root/terminal sequencer verification.

### R8V7-I016 — Rotation hard-state continuity

A new replica may vote only after attested hard state proves:
- highest_seen_term >= joint-state term;
- highest_committed_log_index >= activation prerequisite index;
- last committed digest matches transferred log;
- StreamHeadMap root matches current committed state.

Configuration rotation cannot reset term/index/head history.

## 6. Admin-domain quorum eligibility and canonical identity

### R8V7-I017 — ACTIVE-only quorum domains

Only admin domains in state `ACTIVE` at the relevant T0/MTR lifecycle sequence may contribute to:
- EBA quorum;
- GGS quorum;
- LAS quorum;
- recovery quorum;
- anchor quorum;
- time-source quorum;
- constitutional review independence where domain diversity is required.

`SUSPENDED` and `RETIRED` domains are non-voting immediately from their effective lifecycle sequence.

### R8V7-I018 — CanonicalSubjectRegistry

T0/EBA maintains a canonical subject registry mapping:
- canonical_subject_id;
- all controller IDs;
- service IDs;
- human principal IDs;
- delegation roots;
- admin-domain membership history;
- alias identifiers;
- active/revoked state.

Every ControllerAttestation and LineageProof references canonical_subject_id.

### R8V7-I019 — Alias collision / independence

Two authority identities resolving to the same canonical_subject_id count as one controller for independence.

One canonical subject may not simultaneously satisfy multiple admin-domain diversity slots for the same quorum.

Unknown or conflicting alias resolution -> independence failure.

## 7. AuthorityInput Enforcement Profile — AIEP-1

### R8V7-I020 — Broker-only execution

The reference authority evaluator runs under `AIEP-1`:

- Linux OCI/container execution;
- read-only root filesystem;
- empty mutable environment except immutable boot identifiers already declared in AIM;
- no direct database credentials;
- no direct cloud/provider credentials;
- network namespace with no general external network route;
- DNS unavailable;
- only pre-opened IPC channel to AuthorityInputGateway and required local attestation/sequencer clients;
- direct arbitrary file reads outside the immutable code/config image denied;
- runtime/interpreter/compiler/image digest bound by WorkloadAttestation.

### R8V7-I021 — System-call enforcement

AIEP-1 qualification must prove a sandbox policy that denies undeclared:
- socket/connect/network creation except approved broker FDs;
- direct database device/socket access;
- mutable config-file access;
- process environment discovery outside allowlisted immutable keys;
- dynamic module/plugin loading not present in RuntimeManifest.

A blocked direct read is recorded as `AIEP_VIOLATION` and authority evaluation fails closed.

### R8V7-I022 — Gateway bypass claim boundary

R8 claims authority-input closure only for components executing under a qualified AIEP-1 (or independently qualified stronger profile).

Components outside that profile have authority effect NONE.

Static/runtime trace evidence remains additional falsification evidence, not the sole enforcement mechanism.

## 8. CSM-2 lifecycle and AIM resolution

### R8V7-I023 — CSM lifecycle states

A semantic entry has one of:
- `ACTIVE`;
- `SUPERSEDED`;
- `REVOKED`;
- `RETIRED`.

Transitions are LAS-committed and constitutional where the semantic class is constitutional.

Deletion is forbidden.

### R8V7-I024 — Exactly one active resolution

For a given `semantic_input_id + applicable scope`, AIM resolution must identify exactly one ACTIVE CSM entry.

Zero active entries -> `SEMANTIC_DEPENDENCY_UNBOUND`.

More than one active entry -> `SEMANTIC_ENTRY_CONFLICT`.

There is no fallback to SUPERSEDED/RETIRED.

### R8V7-I025 — Evidence bound to semantic version

Immutable candidate evidence binds the exact governing CSM schema/validator entry digest.

A later supersession does not rewrite historical evidence.

A REVOKED semantic entry makes new decisions non-promotable and triggers re-evaluation where policy defines retrospective impact.

## 9. Revocation rollback for all authority-bearing classes

### R8V7-I026 — Universal authority revocation head

Every authority-bearing decision, not only root/terminal decisions, reads the current LAS-committed revocation head through AuthorityInputGateway.

The revocation head is part of AuthorityReadSet and VerifiedStateSeal.

Root/terminal decisions additionally require the MTR-mirrored revocation high-water.

### R8V7-I027 — Lower-risk rollback protection

A lower-risk authority verifier cannot accept a revocation head older than the current LAS StreamHeadMap for the revocation stream.

Projection/local-cache rollback cannot lower revocation authority.

## 10. Workload-attestation claim mode

### R8V7-I028 — RuntimeIdentityMode

The constitutional design defines:
- `ATTESTED_RUNTIME`;
- `UNATTESTED_RUNTIME`.

If qualified workload attestation is unavailable, the component enters UNATTESTED_RUNTIME.

### R8V7-I029 — Unattested restrictions

UNATTESTED_RUNTIME may perform only explicitly permitted non-authority/read-only work.

It cannot act as:
- Meta-Governor authority evaluator;
- GGS/LAS/anchor/time authority;
- checkpoint authority producer;
- terminal/root-sensitive issuer;
- QualifiedEvidenceProducer for strong evidence;
- constitutional reviewer execution provider where runtime identity is required.

The downgrade is an explicit status event; it is never silent.

## 11. GCP v7 rejection vectors

The following are frozen rejection vectors:

- object containing two keys whose canonical NFC interpretation is U+00E9 for both (one precomposed `é`, one decomposed `e + U+0301`) -> reject before object construction;
- authority string or key containing U+FDD0 -> reject;
- authority string or key containing U+FFFE or U+FFFF -> reject;
- extension-map key using reserved `sys:` namespace -> reject;
- extension-map key shadowing a standard field after canonical key interpretation -> reject.

These are deterministic rejection vectors and therefore have no canonical-output digest.

## 12. Schema Semantic Provenance Manifest — SPM-1

### R8V7-I030 — Mandatory schema provenance

Every machine-readable schema element generated for schema freeze must have an SPM-1 entry containing:
- schema artifact ID/digest;
- JSON pointer / field / rule ID;
- semantic purpose;
- authoritative source design ID(s);
- source commit/blob;
- transformation/generator identity;
- generator RuntimeManifest digest;
- reviewer status if required.

### R8V7-I031 — RG-1 enforcement

Schema freeze rejects:
- any element with no SPM-1 entry;
- any element whose only source is PR #39/#40 or other NON_AUTHORITATIVE artifact;
- any manual rule with no governed incorporation source.

Result: `UNAUTHORIZED_SEMANTIC_SOURCE`.

## 13. External Effect State Machine — EESM-1

### R8V7-I032 — Intent is not completion

`COMMIT_WITH_SEAL` may commit an `EffectIntent`, but this never by itself means the external effect succeeded.

Effect state:
- INTENT_COMMITTED;
- DISPATCHING;
- ACKNOWLEDGED_UNVERIFIED;
- SUCCEEDED_RECONCILED;
- FAILED_FINAL;
- UNCERTAIN;
- COMPENSATION_REQUIRED;
- COMPENSATED.

Only SUCCEEDED_RECONCILED is success evidence.

### R8V7-I033 — Idempotent effect key

Every EffectIntent binds:
- effect_id;
- provider/action;
- exact payload digest;
- candidate/action/tenant scope;
- idempotency_key derived once from effect_id;
- originating CommitCertificate/VerifiedStateSeal digest.

All retries reuse the same idempotency_key.

### R8V7-I034 — Effect executor

A QualifiedEffectExecutor:
- is workload-attested/registry-bound;
- consumes committed intents only;
- cannot alter provider/action/payload;
- records every attempt;
- uses the frozen idempotency key;
- writes provider receipts/observations back through LAS effect stream.

### R8V7-I035 — Reconciliation

Provider "success" response alone is not completion authority.

Reconciliation uses the provider-specific qualified observation contract:
- confirmed effect identity;
- payload/effect correlation;
- final state;
- receipt/observation digest.

Missing/ambiguous outcome -> UNCERTAIN, not PASS.

### R8V7-I036 — Compensation

Where an effect class supports compensation, the compensation rule is CSM-bound and executes as a new governed effect with its own idempotency identity.

Where no safe compensation exists, UNCERTAIN/FAILED states remain visible and non-fabricated.

## 14. Migration object completeness

### R8V7-I037 — Migration closure

RequalificationProof contains the complete set of authority-referenced objects in the source scope, derived using the CSM-bound dependency extractor.

If a later authority decision references a source-scope object absent from the migration map, result is `MIGRATION_OBJECT_UNBOUND`.

It cannot inherit destination authority.

## 15. ReviewPresentationSchema — RPS-1

### R8V7-I038 — Reviewer-visible semantic boundary

Before schema freeze, every review packet type has a CSM-bound RPS-1 declaring every displayed field as:
- `REVIEW_SEMANTIC`; or
- `DISPLAY_NON_SEMANTIC`.

Unknown displayed field defaults to REVIEW_SEMANTIC.

### R8V7-I039 — Non-semantic display rule

A DISPLAY_NON_SEMANTIC field:
- cannot encode status, severity, identity, evidence quality, ordering priority, decision recommendation, or substantive claim;
- is excluded from reviewer decision instructions;
- changing it cannot change packet element ordering or evidence association.

If those conditions cannot be proven, the field is REVIEW_SEMANTIC.

## 16. Trust-loss status proof

### R8V7-I040 — TRUST_PATH_UNAVAILABLE

When required T0/EBA/BTW/MTR/recovery proof cannot currently be established, the immediate state is `TRUST_PATH_UNAVAILABLE`.

This state requires only direct failed verification/probe evidence and has no authority effect.

### R8V7-I041 — TRUST_DOMAIN_UNRECOVERABLE declaration

`TRUST_DOMAIN_UNRECOVERABLE` is not inferred automatically from elapsed time.

It can be authoritatively recorded only when a still-lawful recovery quorum exists and commits a `TrustLossAssessment` containing:
- affected trust-domain ID;
- failed trust components;
- current last-good anchored/MTR states;
- independent failure evidence;
- attempted lawful recovery paths;
- explicit decision to abandon the constitution;
- recovery quorum approvals;
- LAS/anchor commit where still lawful.

### R8V7-I042 — No quorum, no authoritative declaration

If no lawful recovery quorum exists, the system remains TRUST_PATH_UNAVAILABLE indefinitely.

It is functionally blocked, but no actor may self-declare a final authoritative trust-loss transition.

A new constitution remains an independent trust domain with no inherited authority.

## 17. Time decision context closure

### R8V7-I043 — DecisionPresealDigest

Before time challenge issuance, the evaluator computes:

`decision_preseal_digest = SHA-256(GCP-1({candidate/action/tenant scope, governance_snapshot_digest, AuthorityReadSet_digest, revocation_head_digest, runtime_attestation_digest, effect_class_if_any}))`

The Time NonceLedger is keyed by decision_preseal_digest.

### R8V7-I044 — Time proof into final seal

TimeAttestations bind:
- decision_preseal_digest;
- single-use nonce;
- source status sequence.

VerifiedStateSeal then includes the accepted time-proof digest and nonce state.

A caller-supplied context label cannot substitute for decision_preseal_digest.

## 18. Complete Guard Catalog — fault-proof classes

Fault-proof classes:

- `FP0` = NOT_APPLICABLE_DETERMINISTIC_INPUT: malformed/mismatched deterministic input is itself the proof.
- `FP1` = REQUIRED_SIGNED_STATE: independent signed/anchored registry, attestation, certificate, revocation, time, or witness state.
- `FP2` = REQUIRED_CONCURRENCY_TRACE: independent trace of concurrent attempts plus commit outcomes.
- `FP3` = REQUIRED_STORAGE_FAULT: independently captured rollback/corruption/outage/store mutation evidence.
- `FP4` = REQUIRED_RUNTIME_ATTESTATION: workload/runtime/sandbox identity or violation evidence independent of target guard result.
- `FP5` = REQUIRED_PROVENANCE_DIFF: exact source/artifact/schema/packet/provenance comparison evidence.
- `FP6` = REQUIRED_EXTERNAL_EFFECT: provider attempt/receipt/observation/reconciliation evidence independent of effect success guard.

Every REQUIRED class must name raw evidence refs in CaseProofContract.

### R8V7-I045 — Consolidated G001-G066 catalog

| Guard | Mechanism | Positive | Negatives with fault-proof class |
|---|---|---|---|
| G001 | EBA ControllerAttestation verification | V4-001 | V4-002 FP0; V4-003 FP1 |
| G002 | BootstrapAuthorization + singleton CAS | V4-004 | V4-005 FP5; V4-006 FP2 |
| G003 | Root quorum independence | V4-007 | V4-008 FP1; V4-009 FP1 |
| G004 | Recovery quorum + trigger proof | V4-010 | V4-011 FP1; V4-012 FP5 |
| G005 | Anchor quorum + witness | V4-013 | V4-014 FP1; V4-015 FP1; V4-016 FP1 |
| G006 | Atomic CAS_APPEND | V4-017 | V4-018 FP2; V4-019 FP1 |
| G007 | Constitutional semantic digest gate | V4-020 | V4-021 FP5; V4-022 FP5 |
| G008 | GCP-1 canonicalization/parser | V4-023 | V4-024 FP0; V4-025 FP0; V4-026 FP0; V4-027 FP0; V4-028 FP0; V4-029 FP5; V4-030 FP5 |
| G009 | SPR lifecycle/stable primitive IDs | V4-031 | V4-032 FP5; V4-033 FP0 |
| G010 | Reviewer independence/two-channel review | V4-034 | V4-035 FP5; V4-036 FP1; V4-037 FP5 |
| G011 | Issuer separation of duties | V4-038 | V4-039 FP1; V4-040 FP5 |
| G012 | Revocation monotonic use-time validation | V4-041 | V4-042 FP1; V4-043 FP1 |
| G013 | Context-bound time quorum | V4-044 | V4-045 FP1; V4-046 FP1; V4-047 FP1 |
| G014 | Materiality field-mask classifier | V4-048 | V4-049 FP5; V4-050 FP5 |
| G015 | QualifiedEvidenceProducer strong evidence | V4-051 | V4-052 FP5; V4-053 FP4; V4-054 FP5 |
| G016 | Stable tenant/authority IDs | V4-055 | V4-056 FP0; V4-057 FP5 |
| G017 | Checkpoint producer/immediate anchor | V4-058 | V4-059 FP1; V4-060 FP2 |
| G018 | State-root mutation detection | V4-061 | V4-062 FP3; V4-063 FP3 |
| G019 | Registry/head rollback-fork guard | V4-064 | V4-065 FP1; V4-066 FP1 |
| G020 | Recovery blocked-state bypass | V4-067 | V4-068 FP5; V4-069 FP5 |
| G021 | Repository/history migration anchor | V4-070 | V4-071 FP5; V4-072 FP5 |
| G022 | Evidence transition closed table | V4-073 | V4-074 FP5; V4-075 FP5 |
| G023 | PLATFORM_POLICY exact-condition issuer | V4-076 | V4-077 FP1; V4-078 FP5 |
| G024 | Constitutional unrecoverable boundary | V4-079 | V4-080 FP1 |
| G025 | Mechanism-proof adjudicator | V4-081 | V4-082 FP5; V4-083 FP5; V4-084 FP5 |
| G026 | T0 manifest pin/rotation/rollback | V5-001 | V5-002 FP5; V5-003 FP1; V5-004 FP1 |
| G027 | BTW pinned STH/consistency/split-view | V5-005 | V5-006 FP1; V5-007 FP1; V5-008 FP1 |
| G028 | BootstrapAuthorization->GenesisDescriptor | V5-009 | V5-010 FP5; V5-011 FP1; V5-012 FP1 |
| G029 | LAS majority linearization/CommitCertificate | V5-013 | V5-014 FP2; V5-015 FP1; V5-016 FP1 |
| G030 | LAS idempotency/retry | V5-017 | V5-018 FP2 |
| G031 | CSM semantic dependency closure | V5-019 | V5-020 FP5; V5-021 FP5 |
| G032 | Runtime dependency attestation | V5-022 | V5-023 FP4 |
| G033 | GCP escape/null/extension/vector closure | V5-024 | V5-025 FP0; V5-026 FP0; V5-027 FP5 |
| G034 | Anchor/witness rotation/freshness | V5-028 | V5-029 FP1; V5-030 FP1 |
| G035 | Time nonce/rotation | V5-031 | V5-032 FP1; V5-033 FP1 |
| G036 | Issuer rotation/parent compromise | V5-034 | V5-035 FP1; V5-036 FP1 |
| G037 | Producer temporal revocation | V5-037 | V5-038 FP1; V5-039 FP1 |
| G038 | Materiality mask/extractor integrity | V5-040 | V5-041 FP5; V5-042 FP4 |
| G039 | Tenant migration/non-inheritance | V5-043 | V5-044 FP5; V5-045 FP5 |
| G040 | Recovery semantic self-protection | V5-046 | V5-047 FP5; V5-048 FP1 |
| G041 | VerifiedStateSeal TOCTOU | V5-049 | V5-050 FP2; V5-051 FP5 |
| G042 | Constitutional Channel X attestation | V5-052 | V5-053 FP1; V5-054 FP1 |
| G043 | MTR T0 monotonic high-water | V6-001 | V6-002 FP3; V6-003 FP1 |
| G044 | Admin-domain lifecycle/quorum | V6-004 | V6-005 FP1 |
| G045 | Scoped ControllerAttestation revocation | V6-006 | V6-007 FP0; V6-008 FP1 |
| G046 | Canonical LineageGraph | V6-009 | V6-010 FP5; V6-011 FP5 |
| G047 | MTR+BTW first-seen bootstrap | V6-012 | V6-013 FP1 |
| G048 | GGS atomic constitution genesis | V6-014 | V6-015 FP2; V6-016 FP2 |
| G049 | LASHardState rollback resistance | V6-017 | V6-018 FP3; V6-019 FP1 |
| G050 | Atomic LAS StreamHeadMap CAS | V6-020 | V6-021 FP2; V6-022 FP1 |
| G051 | AIM/AuthorityInputGateway default-deny | V6-023 | V6-024 FP4; V6-025 FP5 |
| G052 | CSM-2 canonical closure | V6-026 | V6-027 FP0 |
| G053 | GCP Unicode/key collision closure | V6-028 | V6-029 FP0; V6-030 FP0 |
| G054 | WorkloadAttestation runtime identity | V6-031 | V6-032 FP4; V6-033 FP4 |
| G055 | Revocation high-water/undo | V6-034 | V6-035 FP1; V6-036 FP1 |
| G056 | LAS NonceLedger/time status | V6-037 | V6-038 FP1; V6-039 FP1 |
| G057 | Qualified producer execution proof | V6-040 | V6-041 FP4; V6-042 FP5 |
| G058 | Review-influence materiality | V6-043 | V6-044 FP5 |
| G059 | Migration RequalificationProof | V6-045 | V6-046 FP5; V6-047 FP5 |
| G060 | Signed Channel H | V6-048 | V6-049 FP0; V6-050 FP1 |
| G061 | AuthorityReadSet/derived seal | V6-051 | V6-052 FP4; V6-053 FP5 |
| G062 | Atomic COMMIT_WITH_SEAL | V6-054 | V6-055 FP2; V6-056 FP3 |
| G063 | RecoveryContext anti-replay | V6-057 | V6-058 FP1 |
| G064 | TRUST_DOMAIN_UNRECOVERABLE boundary | V6-059 | V6-060 FP5 |
| G065 | RG-1 proposed-semantics exclusion | V6-061 | V6-062 FP5 |
| G066 | Per-guard fault proof/anti-constant-reject | V6-063 | V6-064 FP5; V6-065 FP5 |

### R8V7-I046 — Inherited case semantic index

For G001-G066, the case IDs and one-line semantics are exactly those frozen in the R8 v4/v5/v6 preregistrations.

The v7 blind review packet MUST include this consolidated table plus the canonical v5 and v6 design texts, so no inherited guard is invisible to the reviewer.

## 19. Additional Guard Catalog v7

| Guard | Mechanism | Positive | Negatives with fault-proof class |
|---|---|---|---|
| G067 | MTR live freshness challenge | V7-001 | V7-002 FP1; V7-003 FP1; V7-004 FP3 |
| G068 | Atomic T0 successor reservation | V7-005 | V7-006 FP2; V7-007 FP1 |
| G069 | GGS hard-state rollback resistance | V7-008 | V7-009 FP3; V7-010 FP1 |
| G070 | LAS joint-consensus configuration rotation | V7-011 | V7-012 FP1; V7-013 FP3 |
| G071 | ACTIVE domain + canonical subject independence | V7-014 | V7-015 FP1; V7-016 FP1 |
| G072 | AIEP-1 broker-only authority input enforcement | V7-017 | V7-018 FP4; V7-019 FP4 |
| G073 | CSM lifecycle/AIM resolution | V7-020 | V7-021 FP5; V7-022 FP5 |
| G074 | Universal revocation rollback protection | V7-023 | V7-024 FP1 |
| G075 | Runtime attestation claim-mode restriction | V7-025 | V7-026 FP4 |
| G076 | Schema provenance/RG-1 | V7-027 | V7-028 FP5; V7-029 FP5 |
| G077 | External effect execution/reconciliation | V7-030 | V7-031 FP6; V7-032 FP6; V7-033 FP6 |
| G078 | Migration object completeness | V7-034 | V7-035 FP5 |
| G079 | ReviewPresentationSchema materiality | V7-036 | V7-037 FP5 |
| G080 | Trust-loss declaration boundary | V7-038 | V7-039 FP1; V7-040 FP5 |
| G081 | Time decision-preseal binding | V7-041 | V7-042 FP1 |

## 20. R8 v7 preregistered cases

### MTR freshness
- V7-001 live challenge + exact fresh MTR response + unconsumed nonce -> accepted.
- V7-002 old response replayed under a new challenge -> reject.
- V7-003 response for wrong verifier/trust-domain/purpose -> reject.
- V7-004 MTR unavailable or response exceeds 30-second window -> MTR_UNAVAILABLE.

### T0 generation
- V7-005 one valid next-generation reservation -> reservation certificate.
- V7-006 two different successor digests race for one next generation -> exactly one reservation; loser T0_EQUIVOCATION.
- V7-007 activation digest differs from reserved digest -> reject.

### GGS rollback
- V7-008 current GGSHardState + namespace root >= MTR high-water -> voting/commit eligible.
- V7-009 rolled-back GGS disk image -> replica non-voting.
- V7-010 presented namespace checkpoint below MTR high-water -> stale reject.

### LAS rotation
- V7-011 valid old+new joint quorums with transferred hard state -> activation succeeds.
- V7-012 old-config-only certificate after activation_index -> reject.
- V7-013 new replica missing required hard-state continuity -> non-voting/reject rotation.

### Domain/identity
- V7-014 distinct ACTIVE canonical subjects/domains satisfy quorum.
- V7-015 SUSPENDED/RETIRED domain signature -> non-voting.
- V7-016 two aliases resolve to same canonical_subject_id -> count once; insufficient diversity if threshold depends on both.

### AIEP
- V7-017 authority evaluator obtains all mutable inputs through broker profile -> eligible.
- V7-018 direct undeclared network/database/config access attempt -> AIEP_VIOLATION.
- V7-019 authority component outside qualified AIEP profile -> authority effect NONE.

### CSM lifecycle
- V7-020 exactly one ACTIVE entry resolves AIM input -> valid.
- V7-021 zero active entries -> SEMANTIC_DEPENDENCY_UNBOUND.
- V7-022 multiple active entries -> SEMANTIC_ENTRY_CONFLICT.

### Revocation/runtime mode
- V7-023 current LAS revocation head in seal -> lower-risk authority use may proceed.
- V7-024 stale projected/local revocation head -> reject.
- V7-025 ATTESTED_RUNTIME + matching workload proof -> role eligible.
- V7-026 UNATTESTED_RUNTIME attempts root/terminal/strong-evidence role -> reject.

### Provenance
- V7-027 every schema element has authoritative SPM-1 lineage -> RG-1 eligible.
- V7-028 schema element has no provenance -> UNAUTHORIZED_SEMANTIC_SOURCE.
- V7-029 schema rule sourced only from PR #39/#40 -> UNAUTHORIZED_SEMANTIC_SOURCE.

### Effects
- V7-030 committed intent -> qualified executor -> reconciled provider receipt -> SUCCEEDED_RECONCILED.
- V7-031 provider response says success but reconciliation cannot confirm -> UNCERTAIN, not success.
- V7-032 retry uses different idempotency key -> reject executor attempt.
- V7-033 duplicate/altered provider effect observed -> reconciliation failure/COMPENSATION_REQUIRED where supported.

### Migration/review presentation
- V7-034 complete migration object map + requalification -> eligible.
- V7-035 later authority reference to omitted source object -> MIGRATION_OBJECT_UNBOUND.
- V7-036 only RPS DISPLAY_NON_SEMANTIC field changes under frozen constraints -> old semantic packet binding unaffected.
- V7-037 reviewer-visible semantic/unknown field changes -> old review binding invalid.

### Trust loss/time context
- V7-038 lawful recovery quorum commits TrustLossAssessment -> TRUST_DOMAIN_UNRECOVERABLE recorded.
- V7-039 no lawful recovery quorum -> remain TRUST_PATH_UNAVAILABLE; no authoritative final declaration.
- V7-040 operator/model/admin self-declares unrecoverable and substitutes root -> reject.
- V7-041 time proof binds exact decision_preseal_digest + single-use nonce -> accepted into seal.
- V7-042 time proof binds caller label or stale/different read-set digest -> reject.

## 21. Complete-case packet rule

The blind v7 packet must contain:
1. canonical v5 base;
2. canonical v6 overlay;
3. canonical v7 overlay;
4. complete G001-G081 consolidated catalog;
5. fault-proof class legend;
6. all v7 case semantics;
7. blind reviewer prompt.

Omission of an inherited guard from the review packet invalidates design-review completeness.

## 22. Schema-freeze gate

Even a future v7 `BOUNDED_PASS` authorizes only preparation of machine-readable schemas.

Before implementation:
- schemas must be generated under SPM-1 provenance;
- RG-1 must pass;
- RPS-1 must be frozen for review packet types;
- all G001-G081 CaseProofContracts, positive controls, and per-negative fault-proof artifacts must be frozen;
- external effect schemas must preserve intent != completion;
- schema packet receives independent review if required by effective governance.

## 23. Claim boundary

A future R8 v7 bounded design pass establishes only sufficient design closure to proceed to executable-schema freeze under explicit T0/MTR/GGS/LAS/workload-attestation assumptions.

It does not prove:
- T0/EBA/MTR/BTW operator honesty beyond the explicit threshold trust assumptions;
- hardware/workload attestation vendor security;
- provider-internal model memory isolation;
- external provider correctness;
- implementation correctness;
- cloud/IAM security;
- legal/compliance sufficiency.

Until independent closure:
- R8 v1-v6 = CHANGES_REQUIRED;
- R8 v7 = NOT_IMPLEMENTED / INDEPENDENT_REVIEW_REQUIRED;
- executable-schema freeze = BLOCKED;
- PR #39 = NON_AUTHORITATIVE;
- PR #40 = NON_AUTHORITATIVE;
- holistic governance = CHANGES_REQUIRED;
- authority effect = NONE.
