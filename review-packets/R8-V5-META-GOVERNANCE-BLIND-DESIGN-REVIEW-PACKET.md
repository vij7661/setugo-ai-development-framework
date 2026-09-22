# R8 v5 Meta-Governance - Blind Independent Design Review Packet

Packet status: REVIEW_ONLY / DESIGN_ONLY / NON_AUTHORITATIVE
Authority effect: NONE

Frozen candidate:
- commit: `53d695dff34d14365770d1dbdad8c6620e31a503`
- blob: `bb3049b9dd4ba5c1691f518b9903900dea65711b`

This packet intentionally excludes all R8 v1-v4 reviewer findings and adjudications.

---

# Independent Blind Review - R8 Meta-Governance v5

Status: REVIEW_REQUIRED / DESIGN_ONLY / NON_AUTHORITATIVE
Authority effect: NONE

## Frozen subject

Primary candidate:
- R8 v5 preregistration commit: `53d695dff34d14365770d1dbdad8c6620e31a503`
- file: `governance-r8/R8-META-GOVERNANCE-PREREGISTRATION-V5.md`

Review v5 from scratch. Do not use prior R8 v1-v4 reviewer findings, adjudications, or remediation conclusions.

## Objective

Attempt to falsify whether R8 v5 is sufficiently closed at design level to proceed to executable-schema freeze.

R8 v5 explicitly terminates trust at T0/EBA. Do not reject it merely because some external trust axiom is necessary. Instead test whether every software-consumed root, witness, controller identity, semantic artifact, sequencer state, and consequential action is cryptographically/procedurally bound to that declared axiom and whether lower layers can evade or replace those bindings.

## Mandatory attack areas

1. T0 bootstrap/rotation/rollback
   - pinned manifest;
   - EBA key replacement;
   - BTW replacement;
   - same-generation equivocation;
   - successor activation;
   - outage/deadlock.

2. BTW transparency
   - initial STH pinning;
   - inclusion/consistency proofs;
   - stale STH;
   - split-view;
   - witness rotation/outage;
   - bootstrap first-seen uniqueness.

3. ControllerAttestation/LineageProof
   - constitution/tenant/role scope;
   - admin-domain fabrication;
   - delegation cycles;
   - wildcard abuse;
   - attestation revocation/expiry;
   - lineage ambiguity.

4. BootstrapAuthorization/genesis
   - exact GenesisDescriptor binding;
   - authorization expiry;
   - reused serial;
   - concurrent genesis;
   - malicious digests embedded in authorized descriptor;
   - retry/idempotency.

5. LAS-1/CAS_APPEND
   - actual linearization semantics;
   - 2-of-3 consensus;
   - term/index rollback;
   - split brain;
   - idempotency conflict;
   - leader/retry ambiguity;
   - commutative exception abuse.

6. CSM-1 semantic closure
   - omitted semantic inputs;
   - runtime/compiler/crypto drift;
   - schema extension loopholes;
   - state-root specification;
   - recovery semantics;
   - guard catalog/CaseProofContract integrity.

7. GCP-1
   - escape mapping;
   - absent/null;
   - extension maps;
   - sets/arrays;
   - int64 boundaries;
   - Unicode;
   - frozen reference digests.

8. Anchor/witness lifecycle
   - anchor rotation;
   - revoked controller;
   - stale witness state;
   - quorum/witness collusion;
   - consistency across rotation.

9. Reviewer independence
   - Channel H authenticity;
   - Qualified Channel X;
   - overlap in controller/admin domains;
   - packet contamination;
   - provider-internal memory boundedness.

10. Issuer/revocation
   - key rotation;
   - parent compromise cascade;
   - revocation undo;
   - monotonic head;
   - hidden/stale revocation;
   - decision-context binding.

11. Time
   - nonce reuse;
   - source rotation;
   - stale source;
   - context replay;
   - skew/outage.

12. Evidence producers
   - producer enrollment;
   - executable mismatch;
   - producer compromise/revocation temporal effects;
   - weak-to-strong laundering;
   - retrospective invalidation.

13. Materiality
   - exact field masks;
   - dependency extractor compromise;
   - hidden semantics in display/non-material fields;
   - unknown/unclassified fields.

14. Tenant/migration
   - constitution+tenant namespace;
   - bare UUID replay;
   - migration widening;
   - cross-constitution import;
   - inherited authority.

15. Recovery
   - self-modification of recovery semantics;
   - required T0/witness dependencies;
   - trigger evidence;
   - outage/deadlock;
   - new-constitution inheritance.

16. Verify-before-authority / TOCTOU
   - VerifiedStateSeal completeness;
   - mutation after verification;
   - derived index coverage;
   - commit-time recheck atomicity;
   - multi-store consistency.

17. Guard catalog/mechanism proof
   - missing load-bearing guards;
   - positive-control completeness;
   - earlier-guard masking;
   - independent fault proof;
   - constant-reject false green.

## Reviewer constraints

- Design review only.
- Do not claim implementation/runtime verification.
- Do not grant implementation approval, qualification, merge, release, deploy, production, policy, or terminal authority.
- PR #39/#40 remain non-authoritative.
- Treat T0 as an explicit bounded trust assumption; attack whether software can counterfeit, bypass, replace, roll back, or mis-scope it.
- Prefer concrete false-green/self-grant paths over stylistic criticism.
- Distinguish true design blockers from details legitimately deferred to machine-readable schema freeze after design closure.

## Required output

A. Overall disposition: BOUNDED_PASS, CHANGES_REQUIRED, or INSUFFICIENT_EVIDENCE.

B. Critical findings.

C. High findings.

D. Medium findings.

E. T0/EBA/BTW/bootstrap assessment.

F. Controller identity/independence assessment.

G. LAS/CAS/anchor concurrency assessment.

H. CSM/GCP/runtime semantic closure assessment.

I. Reviewer/issuer/revocation/time assessment.

J. Evidence/materiality/tenant/recovery assessment.

K. TOCTOU/state-integrity assessment.

L. Guard catalog/falsification-mechanism-proof assessment.

M. Over-governance/deadlock assessment.

N. Minimal required changes before executable-schema freeze.

O. Final bounded statement confirming:
- review grants no authority;
- R8 v5 remains NOT_IMPLEMENTED;
- PR #39/#40 remain NON_AUTHORITATIVE;
- unresolved material findings block implementation start.


---

# Canonical R8 v5 preregistration

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

