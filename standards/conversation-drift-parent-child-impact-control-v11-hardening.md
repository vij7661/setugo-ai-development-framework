# Workflow Drift and Parent-Child Impact Control — V11 Hardening Overlay

Status: **PROPOSED V11 — REVIEW REQUIRED — NON-AUTHORITATIVE**

Authority effect: **NONE_EVIDENCE_ONLY**

## V11-C01 — Exact base binding

V11 is an additive hardening layer over exact V10 candidate:

- V10 candidate commit: `f4b895e22f3a39c7673df2b412acad0ac8c44f48`
- V10 hardening blob: `2c2f2867e561fb4f66b8fc24f400d7f9ee19347b`
- V10 precedence/review map blob: `16afad314a63657d692553449f906c1c6b44cf24`
- V10 falsification extension blob: `56fabc4d0f3e06bbb6a8cab2a6ba19792db5d236`

V5–V10 remain active only as mechanically resolved by the composite precedence machinery plus this V11 overlay. Where V11 is stricter, V11 controls.

V11 is design/preregistered falsification material only. It is not runtime implementation evidence.

## V11-C02 — Independent source-repository provenance attestation

Exact packet-byte self-consistency is necessary but not sufficient to prove repository provenance.

Every review packet candidate artifact MUST be covered by a signed `SourceRepositoryAttestation` issued by a source-provenance authority independent of the packet builder and candidate authoring principals.

The attestation binds:

- repository identity and canonical repository ID;
- candidate commit;
- commit tree digest;
- repository path;
- authoritative Git blob SHA or equivalent source digest;
- packet manifest digest;
- exact packet artifact SHA-256;
- source-fetch/attestation method;
- attestation sequence/time;
- source-provenance authority principal/key;
- independence proof.

Qualification verifies both:

1. `git_blob_sha(packet_exact_bytes) == attested_blob_sha`; and
2. the attested path/blob is included in the attested candidate commit tree.

A packet builder cannot self-attest repository provenance.

Missing, stale, conflicting, or unverifiable source attestation emits `REVIEW_PACKET_PROVENANCE_MISMATCH`.

Source attestations and packet manifests MUST also be anchored in an append-only review-provenance transparency log so an older self-consistent manifest cannot silently replace a newer one.

## V11-C03 — Mandatory reviewer clean-room attestation

Reviewer independence cannot be established by reviewer declaration alone.

Every review intended to count toward an independent-review threshold requires a signed `ReviewerCleanRoomAttestation` covering:

- reviewer role/identity;
- exact candidate and packet ID;
- model/runtime/session identity where applicable;
- exact context-assembly digest;
- allowed context sources;
- prohibited context sources;
- retrieval state;
- memory state;
- cache/session-reuse state;
- prior-review access state;
- platform-side context provenance;
- clean-room control version;
- attesting platform/isolation authority;
- result `CLEAN | CONTAMINATED | INSUFFICIENT_EVIDENCE`.

For a qualifying independent review:

- prior-review retrieval MUST be disabled;
- prior-review memory/context MUST be absent or independently proven unavailable to the reviewer runtime;
- cache/session reuse that can carry prior substantive review content MUST be disabled or cryptographically partitioned;
- delivered packet/context digest MUST exactly match the recorded clean-room context;
- platform provenance MUST be available.

If platform-side provenance is unavailable, status is `INSUFFICIENT_EVIDENCE`, never `CLEAN`.

A reviewer declaration may corroborate the attestation but cannot substitute for it.

Failure emits `REVIEWER_CLEAN_ROOM_INSUFFICIENT` or `INDEPENDENT_REVIEW_CONTAMINATED`.

## V11-C04 — CompositeAuditAuthority independence from root-threshold-capable control

V10 CAA independence is extended beyond candidate-author independence.

For each candidate, `CompositeAuditIndependenceRecord` MUST prove that enough CAA principals to satisfy the CAA quorum cannot be controlled, impersonated, recovered, credentialed, or administered by any control combination capable of satisfying the active root-governance threshold.

The proof evaluates:

- control domains;
- administrative domains;
- identity-admin domains;
- credential-admin domains;
- recovery-admin domains;
- HSM/cloud-root domains;
- service-account aliases;
- beneficial ownership.

If any root-threshold-capable combination can also control enough CAA quorum members, emit `COMPOSITE_AUDIT_INDEPENDENCE_REJECTED`.

Recheck is mandatory at candidate freeze and whenever root, CAA, identity, credential, recovery, or beneficial-owner facts change.

## V11-C05 — Global correlated emergency budget

Local and per-root emergency budgets cannot be composed into wider real-world authority.

RGA maintains a `GlobalEmergencyCorrelationRegistry` and durable `GlobalEmergencyBudgetLedger`.

Each emergency-capable action is mapped to one or more global consequence domains such as provider, financial exposure, release/production, data mutation, or other root-governed consequence domain.

Before an emergency action commits, the platform atomically checks:

- per-policy budget;
- workflow-local aggregate budget;
- root-local aggregate budget;
- global correlated consequence-domain budget;
- simultaneous-policy count;
- aggregate duration and invocation count;
- irreversible/external consequence budget;
- forbidden cross-policy combinations.

Cross-workflow or cross-root invocations that affect the same consequence domain consume the same global budget.

Exceeding any global budget emits `AGGREGATE_EMERGENCY_LIMIT_BLOCKED`.

No root/workflow split may create authority unavailable under the global budget.

## V11-C06 — Genesis material-change authority and manual re-acceptance

RGA defines a separate `GenesisMaterialChangeAuthority` (`GMCA`) whose task is to determine whether current root/notary/storage/control facts materially differ from the accepted `GenesisQualificationRecord`.

GMCA:

- cannot be an automated renewal service;
- cannot be solely controlled by active root guardians;
- cannot itself grant terminal workflow authority;
- must use a signed material-change predicate registry;
- evaluates guardian, notary, organization, cloud-root, HSM, identity-admin, credential-admin, recovery-admin, storage architecture, and threshold changes.

If GMCA determines material change, the current genesis qualification becomes `STALE_PENDING_REACCEPTANCE`.

Any renewal/extension after expiry or material change requires new independent **human/manual** out-of-band re-acceptance under the active policy. Automated actors may assemble evidence but cannot issue the acceptance.

Automated renewal attempts emit `GENESIS_QUALIFICATION_STALE`.

Every freeze and terminal qualification rechecks current GMCA status.

## V11-C07 — Runtime effector configuration attestation

Effector re-attestation is bound not only to code/config-file digests but also to mutable runtime enforcement state.

Each active consequential effector requires a signed `EffectorRuntimeConfigurationAttestation` covering at minimum:

- binary/container/image digest;
- environment-variable digest;
- feature-flag digest;
- network/egress policy digest;
- credential identity and scope digest;
- sidecar/proxy/adapter configuration;
- deployment topology/route digest;
- provider endpoint/capability binding;
- fencing schema/version;
- consequence-classification binding;
- attestation sequence and expiry.

Deployment admission compares the live runtime configuration snapshot with the active attestation before enabling consequential traffic.

Any mismatch, unobservable mutable control, or post-attestation change causes `RE_ATTESTATION_REQUIRED` and emits `EFFECTOR_REATTESTATION_REQUIRED`.

No traffic window may exist between detected runtime drift and enforcement.

## V11-C08 — Mandatory post-evasion NCR corpus expansion

A newly discovered normative-evasion pattern creates a governance event, not a documentation suggestion.

RGA governs a `NormativeCorpusExpansionRegistry` recording:

- evasion ID and evidence digest;
- discovery sequence;
- affected candidate/corpus/extraction versions;
- assigned corpus owner;
- required new adversarial fixture;
- extraction-algorithm disposition;
- required re-review/test scope;
- dependent freeze artifacts invalidated;
- completion/revalidation status.

On accepted discovery of a new evasion pattern:

- prior affected `NormativeCoverageStatement = BOUNDED_COVERAGE_ACCEPTED` becomes `STALE_REVALIDATION_REQUIRED`;
- affected NCR PASS cannot qualify a new freeze;
- corpus and/or extractor must be updated;
- new falsification case must be added;
- dependent tests/reviews must rerun as policy requires.

Reusing a stale NCR PASS emits `NORMATIVE_EXTRACTION_INCOMPLETE`.

## V11-C09 — Evidence-class-aware review threshold accounting

Review-counting is mechanical.

A signed `ReviewGatePolicy` defines, per gate:

- required reviewer roles;
- required review count;
- permitted evidence classes;
- required independence/clean-room state;
- exact-candidate requirement;
- required packet-provenance status.

`ReviewThresholdRecord` counts a review only if all gate predicates are satisfied.

An `AI_GENERATED_ENGINEERING_FEEDBACK_ONLY` review contributes zero to a gate requiring `INDEPENDENT_MANUAL_REVIEW`.

Role label `R3` does not override evidence class.

Miscount emits `REVIEW_EVIDENCE_CLASS_INELIGIBLE`.

## V11-C10 — Mechanical candidate/reference artifact separation

Every packet and composite candidate uses a signed `ArtifactRoleRegistry`.

Each artifact is exactly one of:

- `CANDIDATE_NORMATIVE`;
- `CANDIDATE_FALSIFICATION`;
- `REFERENCE_ONLY`.

`REFERENCE_ONLY` artifacts:

- are excluded from composite normative precedence;
- cannot define a candidate endpoint/authority transition;
- cannot satisfy candidate acceptance evidence;
- must use a distinct manifest namespace and artifact ordinal range.

If reference material is cited as candidate authority, emit `REFERENCE_AUTHORITY_REJECTED` and `COMPOSITE_PRECEDENCE_AMBIGUOUS`.

EXP-K remains reference-only unless explicitly promoted through a separate governed candidate change.

## V11-C11 — Consequence-class downgrade quorum independence

Any downgrade from a stricter consequence class to a weaker class requires a `ConsequenceDowngradeIndependenceRecord`.

The downgrade quorum must be independent from:

- proposer/beneficiary;
- operation owner;
- candidate author where applicable;
- any service-account alias or beneficial owner that controls those actors;
- any root-threshold-capable control combination that could simultaneously control enough downgrade approvers.

Independence is evaluated across control/admin/identity/credential/recovery/HSM domains.

Failure emits `CONSEQUENCE_CLASSIFICATION_BLOCKED`.

## V11-C12 — Trusted history start external witness

The initial trusted GEL/WAS history-start boundary requires a signed `HistoryStartWitnessAttestation` from an external witness authority independent of GEL/WAS/root runtime writers.

The attestation binds:

- system/repository/environment identity;
- trusted start sequence;
- initial GEL/WAS anchor/root digest;
- predecessor/nonexistence evidence;
- witness key/domain;
- activation sequence.

Changing or rolling back trusted history start without a new independently governed migration emits `LEDGER_ANCHOR_COVERAGE_GAP`.

## V11-C13 — Predicate-auditor independence recheck on every permissive use

Every `PARENT_UNAFFECTED` decision MUST re-evaluate current predicate-auditor independence facts against all active root-threshold-capable subsets, even when the predicate family/version has not changed.

Cached independence proofs may be used only as evidence inputs; the final decision must confirm they remain current at the decision sequence.

Stale or unverifiable independence emits `PREDICATE_AUDIT_INDEPENDENCE_REJECTED`.

## V11-C14 — Review-provenance transparency and anti-rollback

`ReviewPacketManifest`, `SourceRepositoryAttestation`, `ReviewerCleanRoomAttestation`, and `ReviewerIndependenceRecord` are appended to an immutable review-provenance log with monotonic packet sequence and hash chaining.

A review must bind to the latest non-superseded packet manifest for its exact candidate.

Reusing an older self-consistent manifest after a newer superseding manifest exists emits `REVIEW_PACKET_PROVENANCE_MISMATCH`.

## V11-C15 — New endpoints

V11 adds owner-bound endpoint schemas for:

- `REVIEWER_CLEAN_ROOM_INSUFFICIENT`
- `REVIEW_EVIDENCE_CLASS_INELIGIBLE`
- `REFERENCE_AUTHORITY_REJECTED`

V11 also narrows enforcement of existing endpoints:

- `REVIEW_PACKET_PROVENANCE_MISMATCH`
- `COMPOSITE_AUDIT_INDEPENDENCE_REJECTED`
- `AGGREGATE_EMERGENCY_LIMIT_BLOCKED`
- `GENESIS_QUALIFICATION_STALE`
- `EFFECTOR_REATTESTATION_REQUIRED`
- `NORMATIVE_EXTRACTION_INCOMPLETE`
- `CONSEQUENCE_CLASSIFICATION_BLOCKED`
- `LEDGER_ANCHOR_COVERAGE_GAP`
- `PREDICATE_AUDIT_INDEPENDENCE_REJECTED`
- `INDEPENDENT_REVIEW_CONTAMINATED`

All required endpoint schemas must exist before associated cases execute.

## V11-C16 — Freeze rule

V11 cannot freeze for execution while any unresolved Critical/High design finding remains under the governing review policy.

The clean V10 R3 output is preserved as independent R3 engineering feedback for candidate `f4b895e2...`, but because it is `AI_GENERATED_ENGINEERING_FEEDBACK_ONLY`, it does not satisfy a gate requiring independent human manual review.

This document grants no merge, release, production, qualification, adjudication, or terminal authority.
