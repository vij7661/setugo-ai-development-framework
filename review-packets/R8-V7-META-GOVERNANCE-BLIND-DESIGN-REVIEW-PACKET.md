# R8 v7 Meta-Governance - Blind Independent Design Review Packet

Packet status: REVIEW_ONLY / DESIGN_ONLY / NON_AUTHORITATIVE
Authority effect: NONE

Effective candidate:
- R8 v5 base commit: `53d695dff34d14365770d1dbdad8c6620e31a503`
- R8 v5 blob: `bb3049b9dd4ba5c1691f518b9903900dea65711b`
- R8 v6 overlay commit: `e0e6995a61dab629ff49efc19f6d6128936b9c20`
- R8 v6 blob: `4604fc38859087f08f941f5bde023214876528cb`
- R8 v7 successor commit: `fad366add685a978c55837e420e3bcb0939d41aa`
- R8 v7 blob: `4bffae9907735862946e97ff9c608abf960078a8`

Effective semantics:
- v5 remains the inherited base;
- v6 supersedes v5 where stronger/more specific;
- v7 supersedes v5/v6 where stronger/more specific;
- this packet intentionally excludes all R8 v1-v6 reviewer findings and adjudications.

---

# Independent Blind Review - R8 Meta-Governance v7

Status: REVIEW_REQUIRED / DESIGN_ONLY / NON_AUTHORITATIVE
Authority effect: NONE

## Frozen subject

Effective candidate:
- R8 v5 base commit: `53d695dff34d14365770d1dbdad8c6620e31a503`
- R8 v6 overlay commit: `e0e6995a61dab629ff49efc19f6d6128936b9c20`
- R8 v7 successor commit: `fad366add685a978c55837e420e3bcb0939d41aa`

Effective semantics:
- v5 is the inherited base;
- v6 supersedes v5 where stronger/more specific;
- v7 supersedes v5/v6 where stronger/more specific.

Review the effective v5+v6+v7 design from scratch.

Do NOT use prior R8 v1-v6 reviewer findings, adjudications, or remediation conclusions.

## Objective

Attempt to falsify whether the effective R8 v5+v6+v7 design is sufficiently closed to proceed to executable-schema freeze.

Treat T0/EBA/MTR/BTW/GGS/LAS/workload-attestation as explicit bounded trust assumptions. Attack whether ordinary software or lower layers can replay, roll back, mis-scope, bypass, counterfeit, omit, or launder any authority-relevant state.

## Mandatory attack areas

1. MTR freshness
   - challenge uniqueness;
   - verifier binding;
   - trust-domain/purpose binding;
   - 30-second freshness rule;
   - stale response replay;
   - outage behavior;
   - MTR response-sequence rollback.

2. T0 successor reservation
   - two successor digests racing for one generation;
   - retry/idempotency;
   - reservation/activation mismatch;
   - BTW inclusion before/after reservation;
   - MTR equivocation.

3. GGS-2
   - hard-state rollback;
   - namespace-root rollback;
   - authorization-state rollback;
   - replica replacement;
   - config rotation;
   - MTR high-water mismatch;
   - concurrent genesis.

4. LAS-3 rotation
   - joint-consensus correctness;
   - hard-state transfer;
   - old-generation certificate acceptance;
   - activation index;
   - StreamHeadMap continuity;
   - idempotency continuity;
   - config rollback.

5. Admin-domain/canonical identity
   - ACTIVE-only voting;
   - suspended/retired domain signatures;
   - aliases mapping to one canonical subject;
   - one subject across multiple domains;
   - domain lifecycle abuse.

6. AIEP-1
   - direct env/config/file/network/database reads;
   - dynamic plugin loading;
   - broker-FD abuse;
   - runtime outside sandbox;
   - syscall/interception bypass;
   - authority effect of unqualified profile.

7. CSM lifecycle/AIM resolution
   - zero/multiple active entries;
   - superseded/revoked semantics;
   - evidence bound to old validator;
   - retrospective invalidation;
   - unknown semantic input.

8. Revocation/runtime mode
   - lower-risk revocation rollback;
   - MTR high-water for sensitive use;
   - UNREVOKE interval;
   - UNATTESTED_RUNTIME privilege escalation;
   - workload-attestation downgrade.

9. GCP v7 vectors
   - NFC key collision;
   - Unicode noncharacters;
   - sys: namespace;
   - extension-map shadowing;
   - inherited GCP rules and reference vectors.

10. RG-1/SPM-1
   - missing schema provenance;
   - manual undocumented rule;
   - proposal-only rule from PR #39/#40;
   - wrong source commit/blob;
   - generator drift.

11. External effects
   - effect intent without real effect;
   - duplicate effect;
   - altered payload;
   - changed idempotency key;
   - provider success without reconciliation;
   - uncertain result;
   - compensation path;
   - executor compromise/revocation.

12. Migration
   - omitted source object;
   - scope widening;
   - stale destination policy;
   - cross-constitution authority inheritance.

13. ReviewPresentationSchema
   - semantic content hidden in display fields;
   - ordering/evidence association changes;
   - unknown displayed fields;
   - human/model reliance on non-semantic fields.

14. Trust loss/recovery
   - proof for TRUST_PATH_UNAVAILABLE;
   - lawful declaration of TRUST_DOMAIN_UNRECOVERABLE;
   - no quorum case;
   - emergency root substitution;
   - new constitution inheritance.

15. Time decision context
   - decision_preseal_digest completeness;
   - AuthorityReadSet mismatch;
   - nonce replay;
   - caller-controlled label substitution.

16. Guard catalog completeness
   - verify G001-G081 are all present;
   - every guard has a positive control;
   - every negative case has FP0-FP6 classification;
   - fault-proof class is appropriate;
   - inherited case IDs are not silently weakened;
   - no missing load-bearing guard.

17. Mechanism proof
   - earlier-guard masking;
   - constant-reject false green;
   - independent fault proof;
   - positive control traverses the same guard;
   - external-effect proof independence.

18. Over-governance/liveness
   - MTR unavailable;
   - GGS/LAS quorum unavailable;
   - external-effect uncertainty;
   - reviewer unavailable;
   - trust-domain loss;
   - whether any liveness workaround weakens the trust model.

## Reviewer constraints

- Design review only.
- Do not claim implementation/runtime verification.
- Do not grant schema-freeze approval, implementation approval, qualification, merge, release, deploy, production, policy, or terminal authority.
- PR #39/#40 remain non-authoritative.
- Treat explicit trust roots as bounded assumptions; attack bypass/counterfeit/rollback rather than demanding infinite trust regress.
- Prefer concrete false-green/self-grant paths.
- Distinguish genuine design blockers from machine-readable schema details that can safely be frozen only after design closure.

## Required output

A. Overall disposition: BOUNDED_PASS, CHANGES_REQUIRED, or INSUFFICIENT_EVIDENCE.

B. Critical findings.

C. High findings.

D. Medium findings.

E. MTR/T0/GGS assessment.

F. LAS rotation/concurrency assessment.

G. Identity/AIEP/semantic-closure assessment.

H. Revocation/runtime/GCP assessment.

I. Provenance/effect/migration/review-presentation assessment.

J. Recovery/trust-loss/time-context assessment.

K. Guard catalog/fault-proof/mechanism-proof assessment.

L. Over-governance/deadlock assessment.

M. Minimal required changes before executable-schema freeze.

N. Final bounded statement confirming:
- review grants no authority;
- R8 v7 remains NOT_IMPLEMENTED;
- executable-schema freeze remains BLOCKED unless design gate closes;
- PR #39/#40 remain NON_AUTHORITATIVE;
- unresolved material findings block implementation start.


---

# Canonical R8 v5 inherited base

# R8 Meta-Governance Redesign v5 - Successor Preregistration

Status: **PREREGISTERED_DESIGN_V5 - NOT_IMPLEMENTED - INDEPENDENT_REVIEW_REQUIRED**
Authority effect: **NONE**

Predecessors:
- R8 v1 - CHANGES_REQUIRED
- R8 v2 - CHANGES_REQUIRED
- R8 v3 - CHANGES_REQUIRED
- R8 v4 commit `d779eb495b5830674e0258d4d27b768f77e10471` - CHANGES_REQUIRED

R8 v4 adjudication:
- `19f2e03bdbd50d380e7c7f5c8cff344e3a2803d4`

## 1. Objective

R8 v5 closes the remaining design gaps before executable-schema freeze.

Core rule:

> Every authority-relevant semantic/configuration input is either pinned in T0 or digest-bound by the current constitutional semantic manifest, and every authority-bearing state transition is committed through an explicitly linearizable protocol whose exact verified state is rechecked at consequential use.

R8 v5 does not grant implementation, qualification, merge, release, deploy, production, policy, or terminal authority.

## 2. Immutable T0 Bootstrap Manifest

### R8V5-I001 - T0BootstrapManifest

Before any constitution exists, deployment has one read-only `T0BootstrapManifest` whose SHA-256 digest is provisioned out of band.

It contains:
- `t0_generation`;
- EBA threshold public-key set;
- EBA quorum policy;
- EBA policy digest;
- EBA controller/admin-domain registry digest;
- BTW verification-key set;
- BTW policy digest;
- BTW initial trusted signed-tree-head digest;
- BTW consistency-proof profile digest;
- crypto profile digest;
- permitted signature/hash algorithms;
- T0 successor-policy digest;
- expiration/activation rules where applicable.

The running platform accepts T0 state only when the full manifest digest matches the out-of-band pinned digest or a valid T0 successor chain.

### R8V5-I002 - T0 replacement/rotation

A `T0SuccessorManifest` must:
- bind the exact predecessor T0 manifest digest;
- increment `t0_generation` by one;
- state all changed EBA/BTW/crypto/policy objects;
- be signed by at least 4-of-5 active EBA trust officers across at least 3 admin domains;
- be included in BTW under the predecessor trust configuration;
- carry a consistency proof from the predecessor trusted STH;
- activate only after a frozen activation sequence/time condition.

Software cannot self-generate, self-approve, or silently substitute a T0 successor.

### R8V5-I003 - T0 rollback protection

The verifier persists the highest accepted `t0_generation + manifest_digest`.

Lower generations or alternate digests at the same generation are rejected as `T0_ROLLBACK` or `T0_EQUIVOCATION`.

### R8V5-I004 - T0 outage

If current T0/EBA/BTW verification state cannot be established, root/constitutional/terminal authority-bearing transitions are blocked.

No ordinary recovery or project policy may replace T0.

## 3. BTW-1 pinned transparency semantics

### R8V5-I005 - BTW trust binding

BTW receipts, STHs, inclusion proofs, and consistency proofs are valid only under the BTW keys/policy pinned by the current T0 manifest.

### R8V5-I006 - STH freshness and anti-rollback

The verifier persists the highest valid BTW `tree_size + root_hash`.

A smaller tree size, conflicting root at the same tree size, or missing consistency proof from the last trusted STH is rejected.

### R8V5-I007 - Split-view evidence

Two valid BTW STHs with the same tree size but different root hashes produce `BTW_EQUIVOCATION`.

Authority-bearing bootstrap/anchor operations freeze until a T0-authorized witness recovery/rotation path resolves the event.

### R8V5-I008 - Witness rotation

BTW key/controller rotation is T0 successor material.

Ordinary constitutional amendment cannot replace the witness trust root.

## 4. Scoped ControllerAttestation and lineage proof

### R8V5-I009 - ControllerAttestation scope

Each EBA ControllerAttestation binds:
- controller_id;
- admin_domain_id;
- controller public key;
- credential class;
- allowed constitution_id set or wildcard explicitly authorized by EBA;
- allowed tenant scope;
- allowed role classes;
- role_instance_id where a unique role instance is required;
- delegation root ID;
- not_before/not_after;
- attestation serial;
- EBA generation/policy digest;
- revocation log identity.

### R8V5-I010 - LineageProof

Independence-sensitive decisions require a signed `LineageProof` that resolves:
- controller_id;
- admin_domain_id;
- root delegation ancestor;
- credential identity;
- execution/service identity when relevant;
- active delegation edges.

Unknown, unverifiable, cyclic, or ambiguous lineage cannot satisfy independence.

### R8V5-I011 - Domain semantics

`admin_domain_id` semantics are part of the T0 EBA policy digest.

The platform cannot create a new admin domain solely to manufacture quorum diversity.

## 5. BootstrapAuthorization and exact genesis binding

### R8V5-I012 - GenesisDescriptor

A canonical `GenesisDescriptor` contains the complete initial authority-relevant state:
- constitution_id;
- bootstrap_nonce;
- root/recovery controller attestation serials;
- anchor/time controller serials;
- Meta-Governor artifact digest;
- Constitutional Semantic Manifest digest;
- GCP profile digest;
- initial registry schema/head digests;
- LAS-1 configuration digest;
- CAL/witness policy digest;
- tenant/root namespace;
- activation constraints.

`authorized_genesis_digest = SHA-256(GCP-1(GenesisDescriptor))`.

### R8V5-I013 - BootstrapAuthorization

EBA-signed BootstrapAuthorization contains:
- bootstrap_authorization_id;
- authorized_genesis_digest;
- constitution_id;
- expiration;
- T0 generation/digest;
- required BTW log identity;
- EBA threshold proof.

### R8V5-I014 - BTW first-seen precondition

Before genesis commit, BootstrapAuthorization must have:
- BTW inclusion proof;
- consistency proof from last trusted T0-pinned STH;
- unique first-seen registration for `bootstrap_authorization_id`;
- no prior committed genesis binding for that authorization.

### R8V5-I015 - CAS_GENESIS

`CAS_GENESIS` accepts only when all are true:
- current T0 verifies;
- BootstrapAuthorization signature/quorum verifies;
- authorization not expired;
- BTW proof verifies against current trusted STH lineage;
- authorization serial is UNUSED;
- supplied GenesisDescriptor canonical digest equals `authorized_genesis_digest`;
- every embedded semantic/configuration digest matches the authorization;
- no existing constitution head exists for constitution_id.

The operation atomically changes authorization state from UNUSED to USED with the genesis digest and returns `GenesisCommitCertificate`.

### R8V5-I016 - Genesis retry/idempotency

A retry with the same authorization ID, same idempotency key, and same genesis digest returns the same GenesisCommitCertificate.

A retry with the same authorization but different genesis digest is rejected.

## 6. LAS-1 linearizable authority sequencer

### R8V5-I017 - LAS-1 reference model

Authority-bearing streams use `LAS-1`, a three-replica consensus sequencer.

Each replica:
- is an EBA-attested service/controller from a distinct admin domain;
- has an exact executable/configuration digest bound by the constitutional semantic manifest;
- signs commit votes.

A commit requires 2-of-3 LAS replicas.

### R8V5-I018 - Linearization point

The linearization point is the first LAS log index at which a majority has durably accepted the exact entry in one consensus term.

For one `stream_id + expected_seq + expected_head_digest`, only one non-commutative entry can become majority-committed.

### R8V5-I019 - CommitCertificate

A `CommitCertificate` binds:
- stream_id;
- consensus_term;
- log_index;
- expected_seq;
- expected_head_digest;
- new_seq;
- event_digest;
- event_class;
- idempotency_key;
- previous_commit_certificate_digest;
- LAS configuration digest;
- signer IDs/signatures.

### R8V5-I020 - CAS_APPEND validation

A CommitCertificate is valid only when:
- 2-of-3 current LAS signatures verify;
- signer admin domains satisfy the configured independence rule;
- expected predecessor equals the currently committed head;
- new_seq = expected_seq + 1;
- previous certificate digest matches;
- event class is allowed by current stream schema.

### R8V5-I021 - Retry/idempotency

Same `stream_id + idempotency_key`:
- same event digest -> returns same committed result;
- different event digest -> `IDEMPOTENCY_CONFLICT`.

A retry never creates a second logical event.

### R8V5-I022 - Split-brain/equivocation

Two valid majority CommitCertificates for the same non-commutative predecessor but different event digests produce `LAS_EQUIVOCATION`.

No branch is automatically authoritative.

### R8V5-I023 - Commutative exception

A stream event may bypass predecessor exclusivity only when its stream schema:
- marks the exact event class commutative;
- binds an exact merge-function digest;
- proves deterministic canonical output for all event permutations covered by the schema.

Stream schema and merge-function digests are constitutional semantic artifacts.

## 7. Complete Constitutional Semantic Manifest (CSM-1)

### R8V5-I024 - CSM-1 closure

The current constitution binds one `CSM-1` digest covering exact digests for:

1. Meta-Governor executable/configuration.
2. Authority validation predicate bundle.
3. GCP-1 canonicalization profile.
4. Parser/schema bundle.
5. Runtime/compiler/crypto dependency manifest.
6. Semantic Primitive Registry schema/head.
7. Registry-event schema.
8. Every authority-bearing stream schema.
9. Every commutative marking and merge-function artifact.
10. Policy schema/composition/conflict ontology.
11. Identity/ControllerAttestation/LineageProof semantics.
12. Reviewer independence/isolation semantics.
13. Materiality object-class schemas.
14. Non-material field-mask manifests.
15. Dependency extractor artifacts.
16. Issuer/enrollment/rotation/revocation semantics.
17. PLATFORM_POLICY issuer semantics.
18. Revocation state-machine schema.
19. Time authority/attestation schema.
20. Checkpoint schema.
21. CAL/anchor policy.
22. BTW verification/rotation policy.
23. T0/EBA successor policy.
24. Evidence Transition Registry schema.
25. QualifiedEvidenceProducer schema.
26. Evidence temporal-validity policy.
27. RecoveryTriggerSchema set.
28. Recovery/root-replacement state machine.
29. State-root computation specification.
30. Integrity Auditor specification.
31. Tenant namespace/migration schema.
32. Repository/history migration schema.
33. Guard Catalog.
34. CaseProofContract schema.
35. Independent-fault-proof schema.
36. GCP reference-vector manifest.

A changed digest in any CSM-1 entry requires constitutional amendment.

### R8V5-I025 - Unknown semantic dependency

An authority-bearing runtime dependency not represented in CSM-1 causes `SEMANTIC_DEPENDENCY_UNBOUND`.

It cannot be assumed harmless.

## 8. Runtime dependency attestation

### R8V5-I026 - RuntimeManifest

Authority-bearing execution records exact:
- application artifact digest;
- interpreter/compiler/runtime version digest;
- crypto library digest;
- schema/parser bundle digest;
- OS/container image digest where relevant;
- LAS/anchor client library digest.

The RuntimeManifest digest must match the CSM-approved set.

### R8V5-I027 - Drift

Unexpected runtime/compiler/crypto dependency drift causes authority effect NONE until constitutionally approved/requalified.

## 9. GCP-1 exact closure

### R8V5-I028 - Whitespace

Canonical output contains no insignificant whitespace outside string values.

### R8V5-I029 - Null and absence

- absent field and null are distinct;
- null is rejected unless schema declares nullable;
- schema defaults are materialized before canonicalization and signing;
- validation never inserts defaults after digest verification.

### R8V5-I030 - Extension maps

Extension maps are allowed only when the schema explicitly names the field as an extension map.

Extension-map keys:
- must satisfy ordinary key canonicalization;
- cannot shadow standard fields;
- are included in canonical bytes/digest;
- cannot alter semantics of standard fields.

### R8V5-I031 - Escape mapping

Canonical string escaping is:
- U+0008 -> `\b`
- U+0009 -> `\t`
- U+000A -> `\n`
- U+000C -> `\f`
- U+000D -> `\r`
- quotation mark -> `\"`
- reverse solidus -> `\\`
- remaining U+0000..U+001F -> lowercase `\u00xx`
- other valid NFC Unicode -> emitted directly in UTF-8.

Unpaired surrogates are rejected.

### R8V5-I032 - Arrays versus sets

Schema type decides array vs set before canonicalization.

An ordinary array preserves order.

A set:
- canonicalizes each element;
- sorts by element SHA-256 digest, then canonical bytes as a tie-breaker;
- rejects duplicate canonical elements.

### R8V5-I033 - Frozen numeric rules

Integers are signed int64 and use the lexical rules frozen in R8 v4.

No alternate numeric representation is accepted.

### R8V5-I034 - Reference-vector manifest

The design freezes these exact canonical-byte digests:

- `{"a":2,"b":1}` -> `d3626ac30a87e6f7a6428233b3c68299976865fa5508e4267c5415c76af7a772`
- `{"n":0}` -> `f3013f933b9fb80ab6d995e7ad9da36f683837ba1d81e950c943d40111eac2f0`
- ordered `{"s":["b","a"]}` -> `654314a25a80232c19ef4b396eb0fcce3db308a937ede43a06092d75211ec903`
- NFC `{"text":"é"}` -> `42d3cbf59fdccced04e5dff14433fb52d34d58e385e9770ffd896ff517d63b92`
- int64 boundary object `{"min":-9223372036854775808,"max":9223372036854775807}` -> `906c504c6a5ceabaf14e06e427a9ed6d202a1a014d3c32616b00da5040590cab`

Duplicate-key, leading-zero, -0, non-NFC and out-of-int64 cases are rejection vectors, not canonical outputs.

## 10. Anchor/witness rotation semantics

### R8V5-I035 - Anchor controller rotation

Anchor controller rotation requires:
- current EBA ControllerAttestation for old/new controller;
- no prohibited root/recovery overlap;
- CSM-approved rotation transition;
- LAS commit;
- old and new anchor quorum certificate linkage;
- BTW witness inclusion.

An expired/revoked controller cannot sign after its effective revocation sequence.

### R8V5-I036 - Witness outage

If BTW freshness/consistency proof cannot be obtained, new root/constitutional/anchor-root milestones are `WITNESS_UNAVAILABLE`.

No stale STH may be silently accepted beyond the frozen freshness policy.

## 11. Time authority rotation and nonce uniqueness

### R8V5-I037 - Challenge nonce

For each decision_context_digest, verifier generates a cryptographically random 256-bit challenge nonce and stores it as single-use until decision completion/expiry.

Reuse of a completed nonce is rejected.

### R8V5-I038 - Time authority rotation

Time source rotation requires:
- EBA-attested new controller;
- CSM-approved time-source lifecycle transition;
- overlap window where old/new status is explicit;
- LAS/anchor commitment.

A time attestation is evaluated against the source status at its attestation sequence.

## 12. Issuer rotation and parent compromise

### R8V5-I039 - Issuer key rotation

Issuer rotation binds:
- issuer_id;
- old/new credential IDs;
- effective sequence;
- parent authority approval;
- non-overridable SoD where root/terminal sensitive;
- LAS/anchor commit.

Old key use after effective sequence is rejected.

### R8V5-I040 - Parent compromise cascade

A parent issuer compromise event freezes:
- new child enrollment;
- child scope expansion;
- revocation undo;
- reactivation operations

for descendants controlled by that parent until recovery adjudication.

Existing child evidence/authority is evaluated under the explicit compromise-effective-sequence policy.

## 13. Producer revocation temporal semantics

### R8V5-I041 - Producer compromise effective sequence

QualifiedEvidenceProducer revocation/compromise records an `effective_from_sequence`.

Evidence minted:
- before effective_from_sequence remains historically attributable unless policy explicitly requires retrospective invalidation;
- at/after effective_from_sequence is non-promotable;
- with uncertain mint sequence is `PRODUCER_VALIDITY_UNCERTAIN`.

### R8V5-I042 - Retrospective invalidation

A retrospective invalidation must be a governed event specifying:
- producer;
- affected sequence/time range;
- affected evidence IDs or derivation rule;
- reason/evidence;
- re-evaluation requirements.

Downstream candidates depending on invalidated evidence become non-promotable pending re-evaluation.

## 14. Materiality exact masks and extractor integrity

### R8V5-I043 - FieldMaskManifest

Each object class has one CSM-bound `FieldMaskManifest` enumerating:
- exact non-material fields;
- always-material fields;
- conditional fields with exact predicate IDs.

No prose-only classification is allowed.

### R8V5-I044 - Dependency extractor compromise

A dependency extractor:
- has a CSM-bound artifact digest;
- outputs a signed/digested dependency map;
- records source object digest.

Unknown/stale extractor identity -> `MATERIALITY_UNRESOLVED`.

If an extractor is later compromised, affected classifications are re-evaluated from the compromise-effective sequence/range.

## 15. Tenant namespace and migration

### R8V5-I045 - Namespaced authority ID

Authority-bearing stable identity is `constitution_id + tenant_uuid + object_uuid`.

A bare object UUID is insufficient across constitutions/tenants.

### R8V5-I046 - Tenant migration

Migration within one constitution requires:
- source tenant ID;
- destination tenant ID;
- exact migrated objects;
- issuer/policy/evidence/reviewer scope revalidation;
- old/new namespace mapping;
- LAS/anchor commitment.

No authority object is implicitly widened by migration.

### R8V5-I047 - Cross-constitution import

Objects imported into a new constitution carry no inherited terminal/promotion authority.

Imported evidence is classified as `IMPORTED_EXTERNAL_EVIDENCE` unless newly requalified under the destination constitution.

## 16. Recovery self-modification closure

### R8V5-I048 - Recovery semantic immutability

RecoveryTriggerSchemas, recovery quorum rules, root/recovery separation, and new-constitution non-inheritance are CSM constitutional artifacts.

Recovery cannot modify these rules.

### R8V5-I049 - Recovery outage/liveness

If valid recovery authority, EBA verification, required witness proof, or mandatory trigger evidence is unavailable, recovery remains blocked.

Liveness mitigation must be prospective; outage does not grant bypass authority.

## 17. TOCTOU-safe VerifiedStateSeal

### R8V5-I050 - VerifiedStateSeal

An authority decision over mutable stores produces a `VerifiedStateSeal` containing:
- decision_context_digest;
- exact store IDs;
- each current CommitCertificate/head digest/sequence;
- each recomputed state_root_digest;
- schema/RuntimeManifest digest;
- governance snapshot digest;
- revocation head;
- verification sequence;
- seal digest.

### R8V5-I051 - Commit-bound authority use

A consequential action commit must call `COMMIT_WITH_SEAL` and atomically verify that all mutable heads named by the seal still equal the sealed head digests/sequences.

If any changed, result is `STATE_CHANGED`; the decision must be recomputed.

### R8V5-I052 - Derived-index completeness

State-root specification explicitly covers all derived/indexed fields used by authority predicates.

A derived value not included in the state-root computation cannot be consumed for authority.

## 18. Constitutional reviewer Channel X attestation

### R8V5-I053 - Channel X identity

A constitutional Channel X reviewer is either:
- EBA-attested human/controller from a distinct admin domain; or
- a QualifiedExternalReviewProvider whose service/controller attestation, execution identity, packet-isolation profile and allowed review class are registry/CSM bound.

"Independently administered" without attestation does not satisfy Channel X.

## 19. Complete Guard Catalog v5

R8 v5 freezes these additional load-bearing guards beyond the v4 set:

| Guard | Mechanism | Positive case | Negative cases |
|---|---|---|---|
| G026 | T0 manifest pin/rotation/rollback | V5-001 | V5-002,V5-003,V5-004 |
| G027 | BTW pinned STH/consistency/split-view | V5-005 | V5-006,V5-007,V5-008 |
| G028 | Exact BootstrapAuthorization->GenesisDescriptor | V5-009 | V5-010,V5-011,V5-012 |
| G029 | LAS-1 majority linearization/CommitCertificate | V5-013 | V5-014,V5-015,V5-016 |
| G030 | LAS idempotency/retry | V5-017 | V5-018 |
| G031 | Complete CSM semantic dependency closure | V5-019 | V5-020,V5-021 |
| G032 | Runtime dependency attestation | V5-022 | V5-023 |
| G033 | GCP exact escape/null/extension/vector closure | V5-024 | V5-025,V5-026,V5-027 |
| G034 | Anchor/witness rotation/freshness | V5-028 | V5-029,V5-030 |
| G035 | Time nonce/rotation | V5-031 | V5-032,V5-033 |
| G036 | Issuer rotation/parent compromise | V5-034 | V5-035,V5-036 |
| G037 | Producer temporal revocation | V5-037 | V5-038,V5-039 |
| G038 | Materiality mask/extractor integrity | V5-040 | V5-041,V5-042 |
| G039 | Tenant migration/cross-constitution non-inheritance | V5-043 | V5-044,V5-045 |
| G040 | Recovery semantic self-protection | V5-046 | V5-047,V5-048 |
| G041 | VerifiedStateSeal TOCTOU revalidation | V5-049 | V5-050,V5-051 |
| G042 | Constitutional Channel X attestation | V5-052 | V5-053,V5-054 |

All prior v4 guard/case obligations remain inherited unless explicitly superseded by a stronger v5 rule.

## 20. R8 v5 preregistered cases

### T0
- V5-001 valid T0 successor chain increments generation and is accepted.
- V5-002 deployment substitutes unpinned EBA key set -> reject.
- V5-003 lower T0 generation replay -> T0_ROLLBACK.
- V5-004 alternate digest at same T0 generation -> T0_EQUIVOCATION.

### BTW
- V5-005 valid inclusion + consistency proof from trusted STH -> accepted.
- V5-006 stale smaller STH -> reject.
- V5-007 same tree size different root -> BTW_EQUIVOCATION.
- V5-008 receipt under unpinned BTW key -> reject.

### Genesis
- V5-009 unexpired authorization + exact authorized genesis + BTW proof -> commit.
- V5-010 valid authorization with different genesis digest -> reject.
- V5-011 expired authorization -> reject.
- V5-012 missing BTW inclusion/consistency proof -> reject.

### LAS
- V5-013 valid majority CAS_APPEND -> one CommitCertificate.
- V5-014 concurrent same-predecessor writers -> only one majority commit.
- V5-015 forged/single-replica CommitCertificate -> reject.
- V5-016 two majority certificates same predecessor/different event -> LAS_EQUIVOCATION.
- V5-017 retry same idempotency key/event -> same result.
- V5-018 same idempotency key/different event -> IDEMPOTENCY_CONFLICT.

### Semantic closure/runtime
- V5-019 all runtime semantic dependencies match CSM -> authority evaluation may proceed.
- V5-020 stream schema/merge function changes without constitutional amendment -> reject.
- V5-021 unknown authority runtime dependency -> SEMANTIC_DEPENDENCY_UNBOUND.
- V5-022 RuntimeManifest exact approved digests -> proceed.
- V5-023 crypto/parser/runtime drift -> authority effect NONE.

### GCP
- V5-024 reference-vector bytes/digests match frozen values.
- V5-025 alternate control-character escaping -> reject/noncanonical.
- V5-026 extension map shadows standard field -> reject.
- V5-027 null inserted after digest/default phase -> reject mismatch.

### Anchor/witness
- V5-028 valid attested anchor rotation + continuity/witness proof -> succeeds.
- V5-029 stale witness STH beyond policy -> WITNESS_UNAVAILABLE/reject.
- V5-030 revoked anchor controller signs new event -> reject.

### Time
- V5-031 fresh unique nonce + valid rotated time-source status -> accepted proof.
- V5-032 completed nonce replay -> reject.
- V5-033 old source attestation after rotation effective sequence -> reject.

### Issuer
- V5-034 valid parent-authorized key rotation -> new key effective.
- V5-035 old key used after effective sequence -> reject.
- V5-036 compromised parent attempts new child/scope expansion -> frozen/reject.

### Evidence producer
- V5-037 evidence minted before compromise effective sequence follows frozen historic-validity policy.
- V5-038 evidence minted after compromise effective sequence -> non-promotable.
- V5-039 unknown mint sequence under compromised producer -> PRODUCER_VALIDITY_UNCERTAIN.

### Materiality
- V5-040 only CSM-bound non-material fields changed -> non-material positive.
- V5-041 unlisted changed field -> MATERIALITY_UNRESOLVED.
- V5-042 extractor digest not current/approved -> MATERIALITY_UNRESOLVED.

### Tenant/new constitution
- V5-043 valid in-constitution migration revalidates all scoped authority.
- V5-044 bare UUID replay across tenant/constitution -> reject.
- V5-045 imported old-constitution authority record attempts inheritance -> reject; evidence only under import class.

### Recovery
- V5-046 valid recovery under frozen trigger/quorum semantics -> eligible.
- V5-047 recovery tries alter its own trigger/quorum schema -> CONSTITUTIONAL_AMENDMENT_REQUIRED.
- V5-048 witness/EBA required proof unavailable -> recovery remains blocked.

### TOCTOU
- V5-049 VerifiedStateSeal unchanged at consequential commit -> action may proceed to next gate.
- V5-050 store head changes after verification but before commit -> STATE_CHANGED.
- V5-051 derived authority field omitted from state-root spec -> semantic/spec validation failure.

### Constitutional Channel X
- V5-052 valid attested Channel H + valid attested Channel X -> review contract satisfiable.
- V5-053 unqualified provider claimed "independent" with no service attestation -> reject Channel X.
- V5-054 Channel X controller/domain overlaps prohibited lineage -> reject independence.

## 21. Mechanism-proof inheritance

Every v5 case uses CaseProofContract v2 and freezes:
- target guard;
- prerequisites;
- exact state digest;
- guard-entry/decision evidence;
- prohibited earlier guards;
- paired valid control;
- independent fault proof where relevant.

A result label alone is never sufficient.

## 22. Bounded liveness

Safe non-operation is permitted when:
- T0 unavailable;
- BTW consistency unavailable;
- LAS quorum unavailable;
- witness unavailable;
- reviewer unavailable;
- revocation/time unavailable;
- state integrity fails;
- constitutional/recovery quorum unavailable.

No liveness recovery may invent a weaker trust root.

## 23. Construction order

1. Freeze R8 v5.
2. Fresh blind independent design review.
3. Adjudicate without mutating v5.
4. Only after bounded design closure, emit exact machine-readable schemas and reference-vector files whose digests match the v5 design.
5. Freeze all inherited v4 + new v5 CaseProofContracts.
6. Begin implementation only after the design gate closes.
7. Preserve first RED evidence.
8. Execute deterministic positive/negative/mechanism-proof/mutation/self-falsification suites.
9. Freeze exact implementation candidate.
10. Fresh independent implementation review.
11. Reconcile PR #39/#40 only after qualified semantics exist.

## 24. Claim boundary

A future R8 v5 bounded design pass establishes only sufficient design closure to begin schema/implementation work under the explicit T0 assumptions.

It does not prove EBA honesty, real-world non-collusion beyond thresholds, hardware custody, cloud/IAM security, provider-internal memory isolation, or legal compliance.

Until independent closure:
- R8 v1 = CHANGES_REQUIRED;
- R8 v2 = CHANGES_REQUIRED;
- R8 v3 = CHANGES_REQUIRED;
- R8 v4 = CHANGES_REQUIRED;
- R8 v5 = NOT_IMPLEMENTED / INDEPENDENT_REVIEW_REQUIRED;
- PR #39 = NON_AUTHORITATIVE;
- PR #40 = NON_AUTHORITATIVE;
- holistic governance = CHANGES_REQUIRED;
- authority effect = NONE.


---

# Canonical R8 v6 inherited overlay

# R8 Meta-Governance Redesign v6 — Successor Preregistration

Status: **PREREGISTERED_DESIGN_V6 — NOT_IMPLEMENTED — INDEPENDENT_REVIEW_REQUIRED**
Authority effect: **NONE**

Effective design:
- R8 v5 commit `53d695dff34d14365770d1dbdad8c6620e31a503` is the inherited base.
- This v6 document supersedes v5 only where it states a stronger or more specific rule.
- Unmodified v5 rules remain in force for design review.
- R8 v5 remains immutable and CHANGES_REQUIRED.

R8 v5 review adjudication:
- `cdb2e35b729f6f16e8437d5dd1de13cc4761e26b`

## 1. Objective

R8 v6 closes the remaining design blockers before executable-schema freeze.

Core rule:

> Every authority transition is linearized through a rollback-resistant sequencer, every authority input is declared and sealed, every T0 high-water state is externally monotonic, and permanent loss of the lawful trust path fails closed as an explicit terminal trust-domain state.

R8 v6 does not grant implementation, qualification, merge, release, deploy, production, policy, schema-freeze, or terminal authority.

## 2. T0 Monotonic Trust Register — MTR-1

### R8V6-I001 — MTR-1 is part of T0

The T0 bootstrap manifest pins one `MTR-1` trust configuration containing:
- MTR verification key/policy digest;
- monotonic namespace ID;
- accepted attestation profile;
- T0 generation key;
- BTW witness binding.

MTR-1 is an external monotonic register or hardware-backed monotonic service whose state cannot be reset by ordinary platform storage rollback.

The platform does not claim to prove MTR-1 hardware/operator honesty beyond the explicit T0 trust assumption.

### R8V6-I002 — T0 high-water state

MTR-1 persists, per trust domain:
- highest accepted `t0_generation`;
- exact T0 manifest digest;
- highest trusted BTW tree_size/root_hash;
- highest EBA attestation-revocation sequence;
- highest T0-domain lifecycle sequence.

A lower generation, lower sequence, or conflicting digest at an already accepted generation/sequence is rejected.

### R8V6-I003 — Local cache is not authority

Local persistent copies of T0/BTW high-water state are caches only.

Authority-bearing verification requires a valid MTR-1 attestation or a still-valid previously attested high-water token whose frozen freshness policy permits use.

Ordinary database rollback cannot lower T0 state.

### R8V6-I004 — T0 successor activation without circular ordinary time

A T0 successor activates by a monotonic `activation_mtr_seq`, not by an ordinary platform clock.

The successor:
- is signed under predecessor T0 policy;
- is BTW included/consistent under predecessor witness trust;
- receives MTR-1 reservation of the next `t0_generation`;
- becomes active only when MTR-1 records `activation_mtr_seq`.

Optional wall-clock not_before/not_after may further restrict use but cannot establish generation ordering.

## 3. T0 admin-domain lifecycle

### R8V6-I005 — AdminDomainRecord

T0 admin domains have append-only records:
- admin_domain_id;
- controller-governance owner proof;
- ACTIVE/SUSPENDED/RETIRED state;
- activation generation;
- retirement generation.

### R8V6-I006 — Domain diversity cannot be manufactured in the same act

Creating or reactivating an admin domain requires a T0 successor.

A newly created/reactivated domain:
- cannot contribute a signature to the T0 successor that creates/reactivates it;
- becomes quorum-eligible only after that successor is activated and witnessed.

No ordinary platform component may mint admin-domain diversity.

## 4. ControllerAttestation scope and revocation

### R8V6-I007 — Root-sensitive wildcard prohibition

For root, recovery, anchor, time, constitutional reviewer Channel H, LAS replica, and terminal/root-sensitive issuer roles:
- `constitution_id` must be exact;
- tenant scope must be exact or explicitly `ROOT_NAMESPACE` where the role is constitution-wide;
- role_instance_id must be exact;
- wildcard constitution/tenant/role-instance scope is prohibited.

Wildcards may exist only for explicitly lower-risk role classes listed by T0 policy.

### R8V6-I008 — Attestation revocation sequence

Every ControllerAttestation binds an EBA revocation-log sequence at issuance.

A revocation event has:
- attestation_serial;
- effective_revocation_seq;
- reason class;
- EBA threshold proof;
- BTW inclusion/consistency proof;
- MTR-1 high-water update.

For new authority use, an attestation revoked at or before the current EBA revocation high-water sequence is invalid.

Historical evidence remains attributable according to the exact event sequence at which it was produced.

## 5. Canonical LineageGraph

### R8V6-I009 — LineageGraph format

Independence lineage is a GCP-1 canonical DAG:
- nodes keyed by stable principal/controller/service ID;
- directed edges `delegated_from -> delegated_to`;
- each edge binds scope, start sequence, end/revocation sequence, and attestation digest;
- exactly one delegation root per active lineage used for independence.

### R8V6-I010 — Cycle/ambiguity resolution

A lineage proof is invalid if:
- a cycle exists;
- two active roots resolve to one principal without a constitutionally defined merge event;
- an edge is missing/revoked/unverifiable;
- two canonical paths yield conflicting controller/admin-domain identity.

Invalid lineage = cannot satisfy independence.

There is no runtime "best path" heuristic.

## 6. Split-view-resistant bootstrap first-seen store

### R8V6-I011 — Bootstrap first-seen is MTR + BTW bound

A BootstrapAuthorization is first-seen only when both are true:
1. BTW includes `bootstrap_authorization_id + authorized_genesis_digest` under a consistency proof from the trusted STH; and
2. MTR-1 atomically records that authorization serial as `UNUSED` and binds the BTW inclusion digest.

BTW-only visibility is insufficient for singleton bootstrap.

## 7. Global Genesis Sequencer — GGS-1

### R8V6-I012 — Pre-genesis sequencer

Because a constitution-local LAS does not exist before genesis, T0 pins one `GGS-1` configuration.

GGS-1 is a three-replica linearizable sequencer:
- each replica is T0/EBA attested;
- replicas are in distinct T0 admin domains;
- exact executable/configuration digest is in T0;
- 2-of-3 majority required.

### R8V6-I013 — Genesis namespace state

GGS-1 maintains one state machine containing:
- `constitution_id -> EMPTY | COMMITTED(genesis_digest, certificate)`;
- `bootstrap_authorization_id -> UNUSED | USED(genesis_digest, certificate)`;
- exact T0 generation/digest used;
- exact BTW/MTR first-seen proof digest.

### R8V6-I014 — GENESIS_CAS linearization

A genesis command supplies:
- constitution_id;
- bootstrap_authorization_id;
- authorized_genesis_digest;
- supplied GenesisDescriptor digest;
- expected namespace state = EMPTY;
- expected authorization state = UNUSED;
- T0/BTW/MTR proof digests;
- idempotency_key.

The GGS-1 state-machine transition atomically:
1. validates both expected states;
2. validates supplied digest equals authorized digest;
3. consumes authorization UNUSED -> USED;
4. changes constitution namespace EMPTY -> COMMITTED;
5. emits exactly one `GenesisCommitCertificate`.

No two different authorizations can commit two genesis heads for one constitution_id.

### R8V6-I015 — Genesis retry

Same constitution_id + same idempotency_key + same genesis digest returns the existing certificate.

Same idempotency key with different digest -> `IDEMPOTENCY_CONFLICT`.

Concurrent losing command -> `CONSTITUTION_EXISTS` or `AUTHORIZATION_USED`, never a second head.

## 8. LAS-2 rollback-resistant linearizable sequencer

### R8V6-I016 — LAS-2 supersedes LAS-1 transition semantics

All constitution-local authority streams use LAS-2.

LAS-2 remains a 3-replica consensus sequencer but adds rollback-resistant hard state and an atomic state-machine head map.

### R8V6-I017 — LASHardState

Each LAS replica persists in T0-approved monotonic/attested storage:
- highest_seen_term;
- vote_for_current_term;
- highest_committed_log_index;
- highest_applied_log_index;
- last_committed_entry_digest;
- LAS configuration generation.

A replica may not sign/vote from a term/index lower than its attested high-water state.

### R8V6-I018 — Durable vote anti-rollback

Before sending a vote/commit signature, a replica must durably advance the relevant LASHardState.

Rollback of ordinary disk state cannot restore an older term/vote state with signing authority.

Unverifiable hard state -> replica is non-voting.

### R8V6-I019 — Atomic head map

The LAS-2 replicated state machine contains the authoritative `StreamHeadMap`:
- stream_id;
- current_seq;
- current_head_digest;
- last_commit_certificate_digest.

A non-commutative append is one replicated command that atomically:
1. compares expected seq+head digest;
2. verifies event class;
3. records event/idempotency state;
4. advances StreamHeadMap;
5. emits the CommitCertificate.

Pre-check and head advancement are not separate operations.

### R8V6-I020 — CommitCertificate v2

CommitCertificate v2 binds:
- constitution_id;
- stream_id;
- consensus_term;
- committed_log_index;
- expected_seq/head;
- new_seq/head;
- event_digest/class;
- idempotency_key;
- prior certificate digest;
- LAS config generation;
- signer identities/signatures;
- majority-commit proof digest.

A certificate whose committed_log_index is lower than the verifier's LAS/MTR high-water state is stale and rejected.

### R8V6-I021 — Equivocation freeze

Observation of two valid majority CommitCertificates for the same non-commutative predecessor with different new heads creates `LAS_EQUIVOCATION`.

All authority streams governed by the affected LAS configuration freeze pending T0/constitutional recovery.

Equivocation detection is defense-in-depth; normal operation must prevent it through the atomic LAS-2 state machine.

### R8V6-I022 — Authority streams have no commutative bypass in v6

The R8 v6 reference design removes the commutative-event exception for authority-bearing streams.

All authority-bearing events serialize through LAS-2.

Any future commutative authority extension requires a new constitutional design amendment and independent review; no proof-format ambiguity exists in v6.

## 9. Authority Input Manifest — AIM-1

### R8V6-I023 — Default-deny semantic input rule

Every value read by an authority predicate must have an `authority_input_id` in AIM-1.

This includes:
- registry state;
- governance snapshots;
- environment/configuration;
- feature flags;
- parser/schema defaults;
- extension-map fields;
- derived/indexed values;
- tenant/project metadata;
- display/presentation fields if they influence a human/model review used by authority;
- runtime/OS/container/crypto properties;
- external proof/witness status.

Authority code may not consume an unregistered input.

Unregistered read -> `SEMANTIC_DEPENDENCY_UNBOUND`.

### R8V6-I024 — AuthorityInputGateway

The Meta-Governor and authority gates obtain mutable/configurable inputs only through `AuthorityInputGateway`.

The gateway:
- resolves authority_input_id;
- records source store/stream;
- records exact value digest/version;
- verifies CSM/AIM membership;
- adds the input to the decision read set.

Direct environment/database/network/config reads by authority code are prohibited by the RuntimeManifest execution profile.

### R8V6-I025 — Static + runtime closure evidence

Before design implementation can qualify, authority components must provide:
- static declared input manifest;
- runtime read trace from deterministic tests;
- comparison proving every observed authority read maps to AIM-1;
- negative test showing an undeclared read fails closed.

This does not claim mathematical completeness for arbitrary code; it qualifies the enforced gateway execution profile.

## 10. CSM-2 canonical envelope

### R8V6-I026 — CSM-2 structure

CSM-2 is one GCP-1 canonical object:

`{csm_version, constitution_id, semantic_entries[]}`

Each semantic entry is:
- semantic_input_id;
- semantic_class;
- artifact_or_rule_digest;
- schema/version;
- source authority;
- lifecycle state.

Entries are sorted by semantic_input_id bytes.

Duplicate semantic_input_id is rejected.

`CSM_digest = SHA-256(GCP-1(CSM-2))`.

### R8V6-I027 — CSM/AIM closure

Every AIM-1 authority_input_id must resolve to one active CSM-2 semantic entry or to an immutable candidate-bound evidence value whose governing schema/validator is itself CSM-bound.

No default "non-semantic" fallthrough exists.

## 11. GCP-1 collision and Unicode closure

### R8V6-I028 — Canonical key collision

Input object keys must already be NFC.

If two distinct input key byte sequences normalize to the same NFC scalar sequence, input is rejected before object construction.

Duplicate keys after canonical key interpretation are rejected.

### R8V6-I029 — Unicode noncharacters

Unicode noncharacters are rejected in authority-bearing strings and keys.

Unpaired surrogates are rejected.

Valid assigned/unassigned scalar values that are not noncharacters are permitted only when NFC validation succeeds.

### R8V6-I030 — Extension-map closure

Extension-map fields:
- are included in AIM-1 if authority code reads them;
- cannot use reserved standard-field names or reserved `sys:` namespace;
- cannot alter parser/default/validation behavior of standard fields.

## 12. Runtime/workload attestation

### R8V6-I031 — WorkloadAttestationRoot

T0/CSM binds one allowed workload-attestation policy for root-sensitive/terminal authority components.

A `WorkloadAttestation` binds:
- component/service identity;
- executable/image digest;
- RuntimeManifest digest;
- boot/runtime measurement digest;
- attestation nonce;
- attestation root/policy identity;
- validity sequence/window.

### R8V6-I032 — Runtime proof requirement

For root-sensitive/terminal authority execution, a matching valid WorkloadAttestation is required.

If the deployment cannot provide a qualified workload-attestation mechanism, the platform must downgrade its claim and cannot treat RuntimeManifest digests as proof of actual execution identity for those roles.

## 13. Revocation monotonicity and undo

### R8V6-I033 — Revocation high-water

Authority Revocation Registry committed sequence/digest is mirrored into MTR-1 high-water state for root-sensitive/terminal use.

A lower sequence or conflicting digest at a known sequence is rollback/equivocation.

### R8V6-I034 — Revocation undo

Revocation is never deleted.

An `UNREVOKE` event:
- references exact prior revocation;
- requires parent authority + non-overridable SoD;
- has new effective sequence;
- is LAS-2 committed/anchored;
- preserves the revoked interval.

Authority records issued/used during the revoked interval do not become retroactively valid.

## 14. Time nonce monotonic ledger

### R8V6-I035 — NonceLedger

Time challenge nonces are allocated and consumed through a LAS-2 `NonceLedger` keyed by decision_context_digest.

States:
- ISSUED;
- CONSUMED;
- EXPIRED.

A consumed nonce cannot return to ISSUED through ordinary store rollback.

### R8V6-I036 — Time source status at sequence

A TimeAttestation is valid only if the source was ACTIVE at the attestation's LAS-2 source-status sequence.

Rotation/suspension/revocation events define exact effective sequence.

## 15. QualifiedEvidenceProducer closure

### R8V6-I037 — Executable mismatch hard fail

A strong evidence object from a software producer is rejected when its WorkloadAttestation/RuntimeManifest executable digest does not match the QualifiedEvidenceProducer registry record.

### R8V6-I038 — No weak-to-strong copy path

A strong evidence producer must bind:
- exact input object IDs/digests;
- execution proof;
- output derivation/event ID.

Rewrapping identical bytes in a new object without qualified execution does not create a stronger class.

## 16. Review-influence materiality

### R8V6-I039 — Review packet digest binds presentation

Every field shown to a human or model reviewer and relied upon for a review decision is inside the frozen review-packet digest.

Any change to presented text, labels, derived summaries, ordering that is semantically meaningful under the review schema, or evidence references invalidates the old review packet binding.

### R8V6-I040 — Non-material display fields

A display-only field may remain non-material to runtime authority only if:
- it is excluded from review decision inputs; or
- a review schema explicitly marks it non-semantic and the reviewer contract forbids relying on it.

Unknown reviewer influence -> review-material.

## 17. Tenant Migration RequalificationProof

### R8V6-I041 — RequalificationProof

A tenant/project migration emits a `RequalificationProof` containing:
- source constitution/tenant namespace;
- destination constitution/tenant namespace;
- exact object map;
- pre/post policy snapshot digests;
- issuer-scope comparison;
- reviewer/evidence scope comparison;
- authority-scope comparison;
- explicit widening boolean for each scope class;
- required fresh approvals/reviews for any widening;
- destination qualification results.

### R8V6-I042 — No implicit widening

Migration commits only when every widening is separately authorized under destination governance.

Cross-constitution import never carries terminal/promotion authority; old authority records remain historical evidence only.

## 18. Channel H authenticity and Channel X boundedness

### R8V6-I043 — Channel H signed human review

Constitutional Channel H review:
- is signed by an active EBA-attested human/controller key;
- binds exact candidate/snapshot/review-packet digest;
- binds review dimension results;
- uses a controller/admin domain independent of amendment proposer;
- records attestation/revocation sequence used.

A pasted unsigned statement cannot satisfy Channel H.

### R8V6-I044 — Channel X provider-memory claim boundary

A model/provider Channel X is considered independent only with respect to platform-controlled prompt/session/cache isolation plus its qualified provider/service controller separation.

Undetectable provider-internal memory is explicitly outside proof.

Therefore Channel X alone never satisfies constitutional independent review; Channel H remains mandatory.

## 19. Authority Read Set and VerifiedStateSeal v2

### R8V6-I045 — AuthorityReadSet

AuthorityInputGateway constructs a complete `AuthorityReadSet` for one decision:
- authority_input_id;
- source stream/store ID;
- exact committed sequence/head;
- exact value/state-root digest;
- schema/semantic entry digest.

Every mutable authority input must appear.

### R8V6-I046 — Derived value rule

An authority predicate may consume a derived/indexed value only when:
- the derived value is in AuthorityReadSet;
- its derivation rule digest is CSM-bound;
- its source inputs are included in the sealed state-root/stream head or exact evidence digests.

Unsealed derived value -> `UNSEALED_AUTHORITY_INPUT`.

### R8V6-I047 — VerifiedStateSeal v2

The seal binds:
- decision_context_digest;
- full AuthorityReadSet digest;
- exact governance snapshot;
- LAS-2 configuration;
- T0/MTR high-water token;
- revocation high-water;
- time/nonce proof where required;
- Runtime/WorkloadAttestation digest;
- seal nonce;
- seal digest.

## 20. Atomic COMMIT_WITH_SEAL v2

### R8V6-I048 — Global head map transaction

LAS-2 maintains, in its replicated state machine, the authoritative head/version map for every mutable authority-bearing stream.

`COMMIT_WITH_SEAL` is one LAS-2 command that:
1. verifies every expected stream head in the seal against the current map;
2. verifies T0/revocation/nonce high-water constraints;
3. verifies seal/candidate/action binding;
4. atomically commits the consequential effect intent and advances its effect stream.

If any expected head differs, no effect intent commits and result is `STATE_CHANGED`.

### R8V6-I049 — External stores are projections

Database/search/cache projections do not independently determine authority.

They must correspond to LAS-2 committed state roots/heads. Projection mismatch causes `STATE_INTEGRITY_FAILURE`.

This removes multi-store atomicity dependence from independent database transactions: authority atomicity is over the LAS-2 head map and sealed state.

## 21. RecoveryTrigger replay binding

### R8V6-I050 — RecoveryContext

Every recovery attempt has:
- recovery_context_id;
- constitution_id;
- exact trigger type;
- affected objects/streams;
- current T0 generation;
- current LAS/anchor heads;
- random 256-bit recovery_nonce;
- trigger evidence digests.

### R8V6-I051 — Single-use recovery nonce

RecoveryContext is LAS-2 committed before approval collection.

The recovery_nonce is single-use.

Approvals and trigger evidence bind the exact recovery_context_digest.

Replay against a different state/context is rejected.

## 22. Explicit terminal trust-loss state

### R8V6-I052 — TRUST_DOMAIN_UNRECOVERABLE

If lawful recovery requires T0/EBA/BTW/MTR/recovery-quorum proof and the required trust path is permanently unavailable, the constitution enters `TRUST_DOMAIN_UNRECOVERABLE`.

This is an accepted permanent fail-closed safety state, not an implementation defect.

### R8V6-I053 — No emergency trust substitution

No project/org admin, model, reviewer, operator, database edit, local backup, or ordinary constitutional actor may substitute a weaker trust root after `TRUST_DOMAIN_UNRECOVERABLE`.

Permitted operations are:
- forensic export;
- verification of already anchored evidence where possible;
- creation of a new independently bootstrapped constitution.

### R8V6-I054 — New constitution non-inheritance

A new constitution created after trust-domain loss receives no inherited:
- terminal authority;
- promotion authority;
- root/recovery status;
- issuer authority;
- reviewer PASS;
- policy override.

Imported artifacts are external/historical evidence until requalified.

## 23. PR #39/#40 Reconciliation Gate — RG-1

### R8V6-I055 — Proposed semantics cannot leak into schema freeze

Executable-schema freeze may consume only:
- R8 effective design semantics;
- artifacts explicitly incorporated by a future governed amendment.

PR #39 and PR #40 remain `NON_AUTHORITATIVE`.

Any schema field/rule traceable only to those proposals is rejected by `RG-1` as `UNAUTHORIZED_SEMANTIC_SOURCE`.

## 24. Independent fault-proof determinism

### R8V6-I056 — Fault-proof requirement is per guard, not runtime discretion

Every negative/adversarial case in the frozen Guard Catalog declares:
- `fault_proof = REQUIRED` with exact artifact class; or
- `fault_proof = NOT_APPLICABLE` with frozen reason.

There is no execution-time "where relevant" judgment.

### R8V6-I057 — Positive control mandatory for every guard

Every load-bearing guard has at least one positive control reaching that exact guard.

A guard without a valid positive control is unqualified.

Constant-reject behavior therefore cannot qualify any guard.

## 25. Additional Guard Catalog v6

The v5 guard catalog is inherited. v6 adds:

| Guard | Mechanism | Positive | Negative |
|---|---|---|---|
| G043 | MTR T0 monotonic high-water | V6-001 | V6-002,V6-003 |
| G044 | Admin-domain lifecycle/quorum eligibility | V6-004 | V6-005 |
| G045 | Scoped ControllerAttestation revocation | V6-006 | V6-007,V6-008 |
| G046 | Canonical LineageGraph | V6-009 | V6-010,V6-011 |
| G047 | MTR+BTW first-seen bootstrap | V6-012 | V6-013 |
| G048 | GGS atomic constitution namespace genesis | V6-014 | V6-015,V6-016 |
| G049 | LASHardState rollback resistance | V6-017 | V6-018,V6-019 |
| G050 | Atomic LAS StreamHeadMap CAS | V6-020 | V6-021,V6-022 |
| G051 | AIM/AuthorityInputGateway default-deny | V6-023 | V6-024,V6-025 |
| G052 | CSM-2 canonical closure | V6-026 | V6-027 |
| G053 | GCP Unicode/key collision closure | V6-028 | V6-029,V6-030 |
| G054 | WorkloadAttestation runtime identity | V6-031 | V6-032,V6-033 |
| G055 | Revocation high-water/undo | V6-034 | V6-035,V6-036 |
| G056 | LAS NonceLedger/time status | V6-037 | V6-038,V6-039 |
| G057 | Qualified producer execution proof | V6-040 | V6-041,V6-042 |
| G058 | Review-influence materiality | V6-043 | V6-044 |
| G059 | Migration RequalificationProof | V6-045 | V6-046,V6-047 |
| G060 | Signed Channel H | V6-048 | V6-049,V6-050 |
| G061 | AuthorityReadSet/derived-input seal | V6-051 | V6-052,V6-053 |
| G062 | Atomic COMMIT_WITH_SEAL | V6-054 | V6-055,V6-056 |
| G063 | RecoveryContext anti-replay | V6-057 | V6-058 |
| G064 | TRUST_DOMAIN_UNRECOVERABLE boundary | V6-059 | V6-060 |
| G065 | RG-1 proposed-semantics exclusion | V6-061 | V6-062 |
| G066 | Per-guard fault proof + anti-constant-reject | V6-063 | V6-064,V6-065 |

## 26. R8 v6 preregistered cases

### T0/MTR
- V6-001 valid higher T0 generation + matching MTR high-water -> accepted.
- V6-002 local disk rollback presents lower T0 generation -> rejected by MTR.
- V6-003 same generation conflicting manifest -> T0_EQUIVOCATION.

### Admin domains
- V6-004 previously activated independent admin domains satisfy quorum diversity.
- V6-005 new domain attempts to sign the T0 successor that creates it -> reject.

### Controller attestations
- V6-006 exact-scope active attestation used in permitted role -> valid.
- V6-007 root-sensitive wildcard attestation -> reject.
- V6-008 attestation revoked at/before current EBA high-water -> reject.

### Lineage
- V6-009 single canonical acyclic lineage -> valid.
- V6-010 delegation cycle -> reject independence.
- V6-011 ambiguous conflicting roots -> reject independence.

### First-seen/genesis
- V6-012 BTW inclusion + MTR UNUSED registration -> bootstrap eligible.
- V6-013 BTW receipt without MTR singleton record -> reject.
- V6-014 one valid GGS genesis command -> one certificate.
- V6-015 two valid authorizations race for same constitution_id -> exactly one commit.
- V6-016 retry same idempotency/genesis -> same certificate; changed digest -> conflict.

### LAS rollback/atomic CAS
- V6-017 current monotonic LASHardState permits valid vote/commit.
- V6-018 rolled-back term/index disk image attempts vote -> reject/non-voting.
- V6-019 old majority certificate below high-water -> stale reject.
- V6-020 valid exact-head append atomically advances StreamHeadMap.
- V6-021 concurrent same-predecessor append -> one commit, loser HEAD_CONFLICT.
- V6-022 observation of conflicting majority certificates -> LAS_EQUIVOCATION/freeze.

### Semantic default-deny
- V6-023 all authority reads through AIM gateway -> evaluation permitted.
- V6-024 direct undeclared env/config read -> SEMANTIC_DEPENDENCY_UNBOUND.
- V6-025 unregistered derived/display input consumed by authority -> SEMANTIC_DEPENDENCY_UNBOUND.
- V6-026 canonical CSM-2 produces exact frozen digest.
- V6-027 duplicate/unregistered semantic_input_id -> reject.

### GCP/Runtime
- V6-028 distinct NFC canonical keys parse without collision.
- V6-029 keys colliding after canonical interpretation -> reject.
- V6-030 Unicode noncharacter in authority key/string -> reject.
- V6-031 valid workload attestation matches approved RuntimeManifest -> root-sensitive execution eligible.
- V6-032 executable/image digest mismatch -> authority effect NONE.
- V6-033 missing qualified workload attestation where required -> authority effect NONE.

### Revocation/time
- V6-034 current revocation head equals/exceeds MTR high-water -> use may continue.
- V6-035 lower revocation head rollback -> REVOCATION_UNAVAILABLE/reject.
- V6-036 UNREVOKE cannot retroactively validate revoked interval.
- V6-037 fresh LAS NonceLedger ISSUED nonce + active time source -> valid time challenge.
- V6-038 consumed nonce replay -> reject.
- V6-039 old/suspended time source at attestation sequence -> reject.

### Evidence producer
- V6-040 qualified producer with matching workload/executable proof mints permitted strong evidence.
- V6-041 executable mismatch -> reject strong class.
- V6-042 weak bytes copied to new object without producer execution -> remains weak.

### Review materiality
- V6-043 unchanged frozen review-packet presentation -> prior review binding preserved.
- V6-044 reviewer-visible decision input changes -> old review binding invalid.

### Tenant migration
- V6-045 no-widening migration + complete RequalificationProof -> may commit.
- V6-046 migration widens issuer/policy/authority scope without fresh approval -> reject.
- V6-047 cross-constitution authority import -> historical/external evidence only.

### Reviewer Channel H
- V6-048 signed EBA-attested independent Channel H review -> valid Channel H.
- V6-049 pasted/unsigned human review -> cannot satisfy Channel H.
- V6-050 proposer-controlled Channel H controller -> reject independence.

### Seal/TOCTOU
- V6-051 all authority-consumed mutable/derived inputs present in AuthorityReadSet -> seal valid.
- V6-052 authority predicate consumes value absent from read set -> UNSEALED_AUTHORITY_INPUT.
- V6-053 derived value rule/source not sealed -> reject.
- V6-054 COMMIT_WITH_SEAL sees all expected heads unchanged -> effect intent may commit.
- V6-055 one sealed head changes before commit -> STATE_CHANGED, no effect intent.
- V6-056 projection DB changes without LAS head change -> projection ignored / integrity failure, no authority effect.

### Recovery
- V6-057 fresh committed RecoveryContext + bound approvals/trigger proof -> eligible.
- V6-058 replay old recovery approvals under new context/state -> reject.
- V6-059 lawful T0/recovery path permanently unavailable -> TRUST_DOMAIN_UNRECOVERABLE.
- V6-060 local operator attempts emergency replacement root -> reject.

### Proposed semantics
- V6-061 schema-freeze input traces only to authoritative R8 semantics -> RG-1 pass.
- V6-062 schema rule sourced only from PR #39/#40 proposal -> UNAUTHORIZED_SEMANTIC_SOURCE.

### Mechanism proof
- V6-063 guard with valid positive control + required fault proof may qualify.
- V6-064 missing guard positive control -> guard unqualified.
- V6-065 missing REQUIRED fault proof -> INSUFFICIENT_EVIDENCE.

## 27. Explicit bounded deadlock adjudication

R8 v6 intentionally accepts permanent fail-closed states when the lawful trust root is gone.

This includes:
- T0/MTR permanently unavailable;
- EBA threshold permanently unavailable;
- BTW trust/consistency permanently unavailable where required for recovery;
- both root and recovery authority unavailable;
- unresolvable LAS/anchor equivocation without lawful recovery proof.

The system favors integrity over liveness.

No post-failure emergency path may invent weaker authority.

## 28. Schema-freeze gate

Even a future R8 v6 `BOUNDED_PASS` authorizes only **schema-freeze preparation**, not implementation authority.

Before implementation:
1. machine-readable schemas must be generated from the effective v5+v6 design;
2. their digests must match CSM-2/AIM requirements;
3. RG-1 must show no non-authoritative PR #39/#40 semantic leakage;
4. all G001-G066 positive/negative CaseProofContracts must be frozen;
5. the schema packet itself must receive independent review if the effective governance requires it.

## 29. Claim boundary

A future R8 v6 design pass establishes only sufficient design closure to proceed to executable-schema freeze under explicit T0/MTR/workload-attestation assumptions.

It does not prove:
- EBA/MTR/BTW honesty beyond their trust assumptions;
- hardware attestation vendor security;
- real-world non-collusion beyond thresholds;
- provider-internal model-memory isolation;
- cloud/IAM security;
- implementation correctness;
- legal/compliance sufficiency.

Until independent closure:
- R8 v1-v5 = CHANGES_REQUIRED;
- R8 v6 = NOT_IMPLEMENTED / INDEPENDENT_REVIEW_REQUIRED;
- executable-schema freeze = BLOCKED;
- PR #39 = NON_AUTHORITATIVE;
- PR #40 = NON_AUTHORITATIVE;
- holistic governance = CHANGES_REQUIRED;
- authority effect = NONE.


---

# Canonical R8 v7 successor overlay

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

