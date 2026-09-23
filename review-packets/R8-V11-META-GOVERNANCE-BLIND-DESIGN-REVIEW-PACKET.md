# R8 v11 Meta-Governance — Blind Independent Design Review Packet

Packet status: REVIEW_ONLY / DESIGN_ONLY / NON_AUTHORITATIVE
Authority effect: NONE

Blind semantic projection: BSP-1
Residual prior-review administrative metadata scan: PASS

Projection manifest:
- v4: commit `d779eb495b5830674e0258d4d27b768f77e10471`; canonical blob `8597233a08c77c0ab928868eaec4c13c425a2eac`; projected SHA-256 `9d5333b4b47b7cdb44d94d9262fbb5d116b7ed8af62adc3a436ff5d6ef85272a`; removed admin lines 2; removed-lines SHA-256 `80eee55b2807e584d714e802ba186e1d8ba4f25e757bc0f81f59f23aa9262e1d`
- v5: commit `53d695dff34d14365770d1dbdad8c6620e31a503`; canonical blob `bb3049b9dd4ba5c1691f518b9903900dea65711b`; projected SHA-256 `60912bf0427bd1ecc32b8635c3640cecaf777be3e7227bc0d679b68bd19ca9e4`; removed admin lines 2; removed-lines SHA-256 `18c8b6bfc563a3e5823fae6e8085691ffa7f4968f439030a034ae2a04d4f751b`
- v6: commit `e0e6995a61dab629ff49efc19f6d6128936b9c20`; canonical blob `4604fc38859087f08f941f5bde023214876528cb`; projected SHA-256 `5ce6383aceab5476e583d34948713b02a79fecad576348e5cd17b4457bf5d09c`; removed admin lines 2; removed-lines SHA-256 `f4289418b3a6eb4e8c80bbed2ae1ecdf43ce8792191fe6597d6c44178711972c`
- v7: commit `fad366add685a978c55837e420e3bcb0939d41aa`; canonical blob `4bffae9907735862946e97ff9c608abf960078a8`; projected SHA-256 `68b677d4239f32e0e510b80d7c8a0e074edf52d014a0871802539a960c6f9809`; removed admin lines 2; removed-lines SHA-256 `d4420bd19b7836eb959b522c95fe351c525f0f98caf5ec99d765cf30e6b98323`
- v8: commit `58e95ca8cc8beb2125413d794ec08d4333a55521`; canonical blob `9990ae39ac4508a031860075c1178a94386c8aaa`; projected SHA-256 `2edef21001881006a55b4d68cf0609853b11bc3fb1dc8f036b5a6d483ac09043`; removed admin lines 2; removed-lines SHA-256 `a447aa38c3e68068860ed58612eae92d67bf32f4f938d182f49d2c8411c23964`
- v9: commit `0948ed0e83d9de128ca9c12df5784286f15af9eb`; canonical blob `6e1a8d226579a9adad0cdec4e0fb7b70ce5e7891`; projected SHA-256 `92ed665fc380288e82165ae9d1e03b71845b30bc88789b067e1dc30ed3a056b7`; removed admin lines 2; removed-lines SHA-256 `8041319aef64ab00022b11680df314d80931ed31de3f9e7a7291264e0f0d88ad`
- v10: commit `2e85384f759318a17c2ec14b1781dc689a864618`; canonical blob `28690714f3468c6b584d783d2d1f1f62623de1ef`; projected SHA-256 `88a817be97556b4f18b5d817d6e164b37129254f261fbdeeeb77cfacb618e172`; removed admin lines 2; removed-lines SHA-256 `8243c9d50bbb6af6512aac4bbcd0880fd855be4c365f60ca70cc541cf5d8b76a`
- v11: commit `3d6a0820d851bc629fc4c7ccfee4a081b70ce117`; canonical blob `21e5134fa972d9e62f770beb69e2f3ea5c4f96e6`; projected SHA-256 `55fda5cc94d745c83cff3f714d1083035d25f29b035b5a8f7d4a48a6cd078326`; removed admin lines 0; removed-lines SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`

The removed administrative lines are not reproduced in this packet.
No semantic invariant, guard, case, claim boundary, candidate/source identity, or generic governance semantics are intentionally removed.

---

# Independent Blind Review — R8 Meta-Governance v11

Status: REVIEW_REQUIRED / DESIGN_ONLY / NON_AUTHORITATIVE
Authority effect: NONE

## Frozen subject

Effective candidate lineage:
- R8 v4: `d779eb495b5830674e0258d4d27b768f77e10471`
- R8 v5: `53d695dff34d14365770d1dbdad8c6620e31a503`
- R8 v6: `e0e6995a61dab629ff49efc19f6d6128936b9c20`
- R8 v7: `fad366add685a978c55837e420e3bcb0939d41aa`
- R8 v8: `58e95ca8cc8beb2125413d794ec08d4333a55521`
- R8 v9: `0948ed0e83d9de128ca9c12df5784286f15af9eb`
- R8 v10: `2e85384f759318a17c2ec14b1781dc689a864618`
- R8 v11: `3d6a0820d851bc629fc4c7ccfee4a081b70ce117`

Effective semantics:
- v4 supplies inherited early guard/case semantics;
- v5-v10 remain inherited design layers;
- v11 supersedes prior generations only where stronger/more specific.

Blindness rule:
- no prior reviewer findings/adjudications are included;
- administrative prior-review/adjudication commit/hash reference lines are removed by BSP-1;
- semantic rules, cases, guards, claim boundaries, source/candidate identities, and generic governance use of the term adjudication remain present.

Review the effective v4+v5+v6+v7+v8+v9+v10+v11 design from scratch.

Do NOT use prior R8 v1-v10 reviewer findings, adjudications, or remediation conclusions.

## Objective

Attempt to falsify whether R8 v11 is sufficiently closed to proceed to executable-schema freeze.

Treat explicit T0/EBA/MTR/BTW/GGS/LAS/workload-attestation roots as bounded assumptions. Prefer concrete false-green, fallback, replay, rotation-race, ambiguity, scope-collision, or self-grant paths.

## Mandatory attack areas

1. CSM-4 representability
   - multiple entries per semantic_input_id;
   - full nine-component scope tuple;
   - lineage/scope/version collisions;
   - canonical ordering/digest;
   - canonical mapping-object inclusion.

2. AIM-2 / CSRULE-3
   - exact starting lineage binding;
   - revoked source scope;
   - valid same-lineage successor;
   - valid cross-lineage mapped successor;
   - unrelated cross-lineage fallback;
   - successor cycles/multiple successors;
   - mapping conflicts;
   - changed-scope replacement mapping;
   - lower-specificity fallback prohibition.

3. ANYScopePermission lifecycle
   - narrowing/revocation effective sequence;
   - SCOPE_PERMISSION_REEVALUATION_REQUIRED at Smax;
   - fallback blocking;
   - revalidation authority;
   - incomplete transition state;
   - project/org attempted revalidation/broadening.

4. Scope regression/collision
   - trust_domain_id;
   - constitution_id;
   - root_namespace;
   - tenant/org/project;
   - experiment/release;
   - object_class;
   - action_class;
   - ANY at each permitted/prohibited dimension.

5. Successor graph
   - cycle;
   - multiple effective successors;
   - version monotonicity;
   - effective-sequence ordering;
   - revoked/superseded successor traversal.

6. LAS-3/GGS-3 state-root formulas
   - exact root contents;
   - omitted stream/head;
   - state-root mismatch;
   - config-generation mismatch.

7. RBP-1 rotation barrier
   - post-PREPARE authority write;
   - read-only activity;
   - abort;
   - stale barrier;
   - barrier/index mismatch;
   - effect/checkpoint/registry writes during freeze.

8. STC-2
   - uniqueness;
   - conflicting STCs;
   - old-quorum certification;
   - new-quorum acceptance;
   - snapshot exactly at barrier B;
   - transfer state mismatch.

9. CTS-3
   - PRE_JOINT / ROTATION_PREPARED / JOINT / ACTIVE_NEW quorum semantics;
   - wrong STC/JOIN on ACTIVATE;
   - old-only/new-only JOINT commands;
   - activation index;
   - old certificate after activation.

10. Inherited protections
   - T0 reservation/MTR freshness;
   - AIEP/AIG;
   - revocation/time;
   - schema provenance;
   - effect reconciliation;
   - migration/recovery/trust-loss.

11. BSP-1 blind-packet hygiene
   - verify actual prior adjudication/review-evidence administrative metadata is absent;
   - verify semantic lines were not removed;
   - distinguish semantic use of the word adjudication from prior-review metadata;
   - inspect projection manifest completeness.

12. Guard/case completeness
   - G001-G117 lineage represented;
   - each new guard has a positive case;
   - negatives have fault-proof classes;
   - cross-lineage positive/negative present;
   - ANY-drift Smax case present;
   - post-PREPARE write race present;
   - residual blind-metadata negative present.

13. Over-governance/liveness
   - rotation freeze/abort;
   - permission reevaluation;
   - semantic scope revoked;
   - mapping conflicts;
   - no liveness workaround weakens authority.

## Reviewer constraints

- Design review only.
- Do not claim implementation/runtime verification.
- Do not grant schema-freeze approval, implementation approval, qualification, merge, release, deploy, production, policy, or terminal authority.
- PR #39/#40 remain NON_AUTHORITATIVE.
- Treat explicit trust roots as bounded assumptions; attack bypass/counterfeit/rollback rather than infinite trust regress.
- Prefer concrete false-green/self-grant paths.
- Distinguish design blockers from machine-readable schema details safely deferred until design closure.

## Required output

A. Overall disposition: BOUNDED_PASS, CHANGES_REQUIRED, or INSUFFICIENT_EVIDENCE.

B. Critical findings.

C. High findings.

D. Medium findings.

E. CSM-4/AIM-2/CSRULE-3/ANY assessment.

F. LAS-3/GGS-3/RBP-1/STC-2/CTS-3 assessment.

G. Inherited T0/MTR/AIEP/time/provenance/effect/recovery assessment.

H. Guard/case lineage and packet-completeness assessment.

I. Blind-packet hygiene assessment.

J. Over-governance/deadlock assessment.

K. Minimal required changes before executable-schema freeze.

L. Final bounded statement confirming:
- review grants no authority;
- R8 v11 remains NOT_IMPLEMENTED;
- executable-schema freeze remains BLOCKED unless the design gate closes;
- PR #39/#40 remain NON_AUTHORITATIVE;
- unresolved material findings block implementation start.



---

# BSP-1 semantic projection of canonical R8 v4

# R8 Meta-Governance Redesign v4 — Successor Preregistration

Status: **PREREGISTERED_DESIGN_V4 — NOT_IMPLEMENTED — INDEPENDENT_REVIEW_REQUIRED**
Authority effect: **NONE**

Predecessors:
- R8 v1 — CHANGES_REQUIRED
- R8 v2 — CHANGES_REQUIRED
- R8 v3 commit `aa4a5e6a320002731926e0c9ccbbb62c2bfbb0ca` — CHANGES_REQUIRED


## 1. Objective

R8 v4 closes the remaining design-level trust-root and concurrency gaps by explicitly separating:

- **T0 external trust assumptions** that the platform cannot self-prove;
- **L0 constitutional authority** cryptographically bound to those assumptions;
- **L1+ deterministic governed mechanisms** that may be qualified by falsification.

The design does not claim to mathematically prove real-world non-collusion. It claims only that software cannot replace the frozen T0 attestations, threshold assumptions, and externally witnessed state with self-issued labels.

## 2. T0 External Trust Axiom

### R8V4-I001 — T0 is outside ordinary platform authority

The platform begins from a preregistered **External Bootstrap Authority (EBA-1)** whose verification key set and policy digest are provisioned out of band before any constitution exists.

EBA-1 is not created, amended, or replaced by project/org policy, the Meta-Governor, a reviewer, a model, or an ordinary platform registry.

The platform's design-level trust claim explicitly assumes that EBA-1's threshold key custody and real-world controller attestations are valid within their stated scope.

### R8V4-I002 — No infinite trust claim

The platform does not claim to prove the real-world identity behind EBA-1 itself.

EBA-1 is the explicit trust axiom at which cryptographic verification terminates.

Any claim stronger than "verified against the configured EBA-1 trust root" is out of scope unless separately qualified.

### R8V4-I003 — EBA-1 threshold

The reference EBA-1 has five offline trust officers from at least three separately administered domains.

An EBA certificate requires signatures from at least **3-of-5 trust officers**, with at least **three distinct `admin_domain_id` values** represented.

The exact EBA public-key set and EBA policy digest are deployment bootstrap inputs, not self-generated platform state.

## 3. External controller attestation

### R8V4-I004 — ControllerAttestation

Every controller counted for root, recovery, anchor, time, constitutional reviewer, or root-sensitive issuer independence must present an EBA-1-signed `ControllerAttestation` containing:

- `attestation_serial`;
- `controller_id`;
- `admin_domain_id`;
- `controller_public_key`;
- `credential_class`;
- `allowed_role_classes`;
- `not_before`;
- `not_after`;
- `revocation_endpoint_or_log_id`;
- `EBA_policy_digest`;
- EBA threshold signature/certificate proof.

Self-issued controller IDs or principal labels have zero authority.

### R8V4-I005 — Independence predicate

Two principals do **not** count as independent when any of these are equal or share the same EBA-attested controlling lineage:

- `controller_id`;
- `admin_domain_id` where the applicable quorum requires domain diversity;
- root delegation ancestor;
- root-sensitive credential/key identity;
- persistent execution identity where execution separation is required.

A surface-name difference never establishes independence.

### R8V4-I006 — Attestation freshness/revocation

An expired, revoked, unverifiable, or EBA-policy-mismatched ControllerAttestation cannot satisfy an authority or independence requirement.

Use of controller attestations is bound to the current EBA trust-root version and its revocation state.

## 4. Pre-genesis BootstrapAuthorization

### R8V4-I007 — BootstrapAuthorization

Before genesis, EBA-1 issues one `BootstrapAuthorization` containing:

- unique `bootstrap_authorization_id`;
- unique `constitution_id`;
- 256-bit `bootstrap_nonce`;
- exact three root controller attestation serials;
- exact three recovery controller attestation serials;
- exact anchor-controller attestation serials;
- exact time-controller attestation serials;
- allowed initial Meta-Governor/schema digest set;
- exact initial Constitutional Surface Registry digest;
- exact GCP-1 profile digest;
- exact first-registry schema digest set;
- expiration;
- EBA threshold proof.

Genesis keys not covered by this authorization cannot bootstrap the constitution.

### R8V4-I008 — Root/recovery separation at T0

No ControllerAttestation serial or controller_id may appear in both root and recovery sets of one BootstrapAuthorization.

No root or recovery controller may be an anchor-controller quorum majority.

### R8V4-I009 — Singleton pre-genesis registration

Each BootstrapAuthorization is registered once in an external **Bootstrap Transparency Witness (BTW-1)** before platform genesis.

BTW-1 provides:
- first-seen receipt;
- unique serial index;
- append-only inclusion proof;
- signed tree head;
- consistency proof against prior signed tree head.

A `bootstrap_authorization_id` already recorded by BTW-1 cannot bootstrap again.

### R8V4-I010 — Atomic genesis

Genesis uses one linearizable operation:

`CAS_GENESIS(bootstrap_authorization_id, expected=UNUSED, genesis_digest)`

Success produces a `GenesisCommitCertificate`.

Concurrent attempts using the same authorization cannot both commit.

## 5. Root and recovery quorums

### R8V4-I011 — Root constitutional quorum

Ordinary constitutional amendment requires:
- 2-of-3 active root principals;
- two distinct EBA-attested controller_id values;
- two distinct admin_domain_id values;
- valid current ControllerAttestations;
- signatures over identical canonical amendment bytes.

### R8V4-I012 — Recovery quorum

Root replacement/recovery requires:
- 2-of-3 active recovery principals;
- two distinct EBA-attested controller_id values;
- two distinct admin_domain_id values;
- mandatory typed trigger evidence;
- no root/recovery controller overlap.

### R8V4-I013 — Collusion claim boundary

The platform claim assumes fewer than the required independent T0-attested controllers collude.

If the threshold number of externally attested independent controllers collude, the software cannot prove their intent and may accept a maliciously authorized event.

This is an explicit bounded trust assumption, not a false claim of perfect non-collusion proof.

## 6. Anchor independence and witness model

### R8V4-I014 — Three anchor replicas

CAL-2 uses three append-only replicas:

- `ANCHOR-A`
- `ANCHOR-B`
- `ANCHOR-C`

Each replica controller must have a current EBA ControllerAttestation from a distinct admin_domain_id.

### R8V4-I015 — Anchor quorum certificate

An authority-bearing anchor event commits only with a `2-of-3 AnchorQuorumCertificate` over:

- constitution_id;
- anchor_seq;
- prev_anchor_digest;
- canonical_event_digest.

A replica must not sign two different successors for the same predecessor.

### R8V4-I016 — External transparency witness

Every committed AnchorQuorumCertificate must also receive inclusion in BTW-1 or a constitutionally approved independent transparency witness.

Authority-bearing clients require both:
1. valid 2-of-3 AnchorQuorumCertificate; and
2. witness inclusion proof consistent with a previously trusted signed tree head.

### R8V4-I017 — Anchor equivocation

Conflicting quorum certificates, conflicting witness inclusion, or a replica signing two successors for one predecessor produces `ANCHOR_EQUIVOCATION` and freezes affected authority.

### R8V4-I018 — Anchor collusion bound

History-integrity claims assume that an attacker does not control:
- a valid event-approval authority; **and**
- an anchor signing quorum; **and**
- the configured transparency witness consistency path.

This assumption is explicit in the claim boundary.

## 7. Atomic successor protocol

### R8V4-I019 — CAS_APPEND

Every non-commutative constitutional, registry, checkpoint, revocation, and authority-bearing ledger transition uses:

`CAS_APPEND(stream_id, expected_seq, expected_head_digest, event_digest)`

A commit certificate binds all four values.

### R8V4-I020 — Single predecessor consumption

For a non-commutative stream, at most one event may obtain a valid commit certificate for one `expected_seq + expected_head_digest`.

A losing concurrent writer receives `HEAD_CONFLICT` and must re-evaluate against the new head.

### R8V4-I021 — Committed fork detection

If two valid commit certificates are ever observed for one non-commutative predecessor, the stream enters `LEDGER_EQUIVOCATION` and no branch is selected automatically.

### R8V4-I022 — Commutative exception

Concurrent merge is permitted only when:
- the stream schema explicitly marks the event class commutative;
- a constitutionally frozen merge function exists;
- all permutations produce identical canonical merged bytes.

Otherwise the operation is non-commutative.

## 8. Constitutional semantic surface — no subjective reinterpretation

### R8V4-I023 — Machine-readable constitutional semantics

Authority semantics are defined only by constitutionally bound machine-readable artifacts and exact digests:
- Meta-Governor executable digest;
- validation predicate bundle digest;
- GCP-1 profile digest;
- parser/schema bundle digest;
- Semantic Primitive Registry head/digest;
- policy composition/conflict ontology digest;
- identity/independence rule digest;
- materiality classifier schema/rules digest;
- issuer/revocation rule digest;
- time rule digest;
- checkpoint/history rule digest;
- evidence transition rule digest;
- recovery rule digest;
- tenant namespace rule digest.

Human prose cannot change enforcement semantics.

### R8V4-I024 — Semantic artifact change

Any digest change to an artifact listed in R8V4-I023 is automatically `CONSTITUTIONAL_AMENDMENT_REQUIRED`.

No Meta-Governor discretion is needed to decide whether the change is a "reinterpretation."

### R8V4-I025 — Same digest / different behavior

If runtime behavior differs while the constitutionally bound executable/parser/predicate digests are unchanged, this is an implementation-integrity failure, not a lawful semantic reinterpretation.

## 9. Exact GCP-1 numeric/lexical closure

### R8V4-I026 — Integer range

Governance integers are signed 64-bit:

`-9223372036854775808 .. 9223372036854775807`

Values outside the range are rejected.

### R8V4-I027 — Integer lexical form

Valid JSON integer lexical form:
- zero is exactly `0`;
- non-zero positive integers contain digits only and no leading zero;
- negative integers are `-` followed by a non-zero digit and remaining digits;
- `+1`, `01`, `-0`, exponent form, decimal point, NaN, Infinity are rejected.

### R8V4-I028 — String/escape closure

Input strings must be valid Unicode NFC.

Canonical output:
- emits `"`, `\`, and U+0000..U+001F using the single frozen JSON escape mapping;
- does not escape printable non-control Unicode solely for ASCII conversion;
- rejects unpaired surrogates.

### R8V4-I029 — Frozen reference vectors

The design freezes these canonical-output expectations:

1. Input object keys `{"b":1,"a":2}`
   -> canonical bytes exactly `{"a":2,"b":1}`

2. Input `{"n":0}`
   -> exactly `{"n":0}`

3. Input containing integer `01`
   -> parse rejection before canonicalization.

4. Input with duplicate key `{"a":1,"a":2}`
   -> rejection.

5. Input `{"s":["b","a"]}` where schema marks `s` as an ordered array
   -> exactly `{"s":["b","a"]}`.

6. The same logical values in a schema-defined set are sorted by canonical element digest then bytes; duplicate canonical elements reject.

Exact SHA-256 reference digests for frozen schema/vector files must be generated and committed before implementation code begins.

## 10. Semantic Primitive Registry lifecycle

### R8V4-I030 — SPR append-only lifecycle

SPR primitives have immutable `primitive_id` and append-only versions.

Allowed lifecycle:
- ACTIVE;
- SUPERSEDED;
- RETIRED.

Deletion is forbidden.

### R8V4-I031 — Primitive semantic change

Changing:
- meaning;
- unit/base-unit mapping;
- conversion rule;
- scope semantics;
- alias-to-ID resolution

creates a new primitive version and is constitutional when authority-relevant.

Old evidence remains bound to the old primitive version.

### R8V4-I032 — Alias prohibition in authority inputs

Authority APIs accept primitive IDs only.

Human aliases are UI/display metadata and are rejected as authority-bearing request identifiers.

## 11. Non-overridable separation of duties

### R8V4-I033 — Root-sensitive issuer SoD

For these operations, configurator/controller and beneficiary/controller **MUST** be EBA-attested distinct controllers and this requirement is non-overridable:

- terminal issuer enrollment;
- PLATFORM_POLICY issuer enrollment/configuration;
- root-sensitive issuer scope expansion;
- revocation undo for terminal/root-sensitive issuer;
- issuer reactivation after compromise.

Ordinary project policy cannot waive this rule.

## 12. Revocation monotonicity and exact-use binding

### R8V4-I034 — Every revocation update is immediately committed

Every Authority Revocation Registry event uses CAS_APPEND and receives an AnchorQuorumCertificate + witness inclusion before it is considered current.

### R8V4-I035 — Monotonic revocation head

A verifier persists `last_seen_revocation_seq + digest` per constitution/tenant.

A presented revocation head older than the last seen head is rollback and fails closed.

### R8V4-I036 — Use-context binding

Every authority use constructs:

`decision_context_digest = SHA-256(GCP-1({tenant_id, project_id, task_id/effect_id, action, artifact_digest, governance_snapshot_digest, authority_record_digest, nonce}))`

Revocation and time checks are bound to this exact decision context.

### R8V4-I037 — Revocation freshness bound

For terminal/root-sensitive use:
- current revocation head must be obtained from quorum-validated registry state;
- its anchor/witness proof must verify;
- its sequence must be >= the authority-record issue revocation sequence and >= verifier last-seen sequence.

Unavailable/verifiably stale state -> `REVOCATION_UNAVAILABLE`.

## 13. Time attestation exact-context binding

### R8V4-I038 — Context-bound TimeAttestation

A TimeAttestation signs:
- time_source_id;
- controller_attestation_serial;
- decision_context_digest;
- challenge_nonce;
- attested_unix_seconds;
- uncertainty_ms;
- time_sequence;
- expiration;
- signature.

### R8V4-I039 — Time anti-replay

A time proof is valid only for the exact decision_context_digest and challenge_nonce for which it was issued.

Reusing an old attestation for a different decision context or nonce is rejected.

### R8V4-I040 — Time-source independence

A 2-of-3 time quorum requires distinct active EBA ControllerAttestations and distinct admin_domain_id values.

### R8V4-I041 — Time failure

If a valid context-bound 2-of-3 time quorum cannot be established within the constitutional skew bound, expiry-sensitive action is `TIME_AUTHORITY_UNAVAILABLE`.

## 14. Qualified Evidence Producer path

### R8V4-I042 — QualifiedEvidenceProducer Registry

Any producer allowed to mint a strong evidence class has an anchored registry record containing:
- producer_id;
- EBA/controller/service attestation class;
- exact executable/artifact digest where software;
- allowed source inputs;
- allowed output evidence classes;
- tenant scope;
- network/execution boundary class;
- signing key/credential identity;
- revocation status;
- qualification evidence digest.

### R8V4-I043 — Strong evidence minting

A strong evidence object is valid only when:
- produced by an active QualifiedEvidenceProducer permitted for that class;
- signed by the producer credential;
- producer executable/identity matches the registry record;
- exact input evidence digests are bound;
- candidate/snapshot/tenant bindings match;
- output class is allowed.

### R8V4-I044 — Weak-to-strong no-laundering

Weak evidence cannot become strong evidence by:
- relabeling;
- copying content into a new object;
- new metadata;
- a Meta-Governor-only declaration.

A stronger object must result from a newly executed qualified producer path whose prerequisites permit those weak inputs.

### R8V4-I045 — External manual review

User-pasted or manually relayed external LLM review remains external evidence unless a separately qualified producer/attested human-signature path exists.

It may expose defects but cannot impersonate platform-authenticated review.

## 15. Out-of-band mutation detection

### R8V4-I046 — Authoritative state root

Each authority-bearing store exposes a deterministic `state_root_digest` computed from:
- committed event-chain head;
- current indexed objects derived from that chain;
- schema/version identity.

The expected state root/head is anchored.

### R8V4-I047 — Verify-before-authority

Before an authority-bearing decision consumes a store, the verifier checks:
- committed head certificate;
- anchored head;
- recomputed state root;
- current schema digest.

Mismatch -> `STATE_INTEGRITY_FAILURE`; no authority transition.

### R8V4-I048 — Periodic integrity auditor

A separately enrolled Integrity Auditor periodically recomputes state roots and verifies:
- registry heads;
- checkpoint store;
- issuer/revocation store;
- evidence-transition store;
- tenant store;
- policy/invariant store.

Auditor findings are anchored evidence.

The auditor cannot itself repair or grant authority.

### R8V4-I049 — Unauthorized database mutation

A direct DB edit with no valid event commit certificate cannot alter authoritative derived state.

If storage reflects such a mutation, the state-root mismatch triggers recovery.

## 16. Constitutional review independence compensation

### R8V4-I050 — Constitutional review requires two channels

A constitutional amendment requiring independent review must collect two review channels:

- **Channel H:** one EBA-attested human/controller review from an admin_domain_id not controlling the amendment proposer; and
- **Channel X:** either another independently attested human/controller from a third admin domain or an independently administered external review provider execution.

### R8V4-I051 — Provider-internal-memory boundedness

An external model/provider review alone cannot establish constitutional review independence when provider-internal memory is unverifiable.

Provider review may satisfy Channel X only when Channel H is also present.

Ordinary lower-risk review policy may define different requirements, but cannot weaken constitutional Channel H.

### R8V4-I052 — Reviewer artifact isolation

Each channel receives an independently generated packet from the same exact candidate/snapshot and no other channel's substantive findings.

## 17. Materiality non-material field masks

### R8V4-I053 — No prose "non-material" category

An object class may classify mutations as non-material only through explicit schema field masks.

Example:
- `display_label` may be non-material;
- `authority_scope`, `controller_id`, `predicate_digest`, `policy_rule`, `evidence_class` may not.

Unknown field or unclassified changed field -> materiality unresolved/fail closed.

### R8V4-I054 — Dependency extractor version binding

The exact dependency extractor executable/rule digest is constitutional/registry-bound.

Stale or unknown extractor identity cannot classify a change as non-material.

## 18. Checkpoint anchoring exactness

### R8V4-I055 — Authoritative checkpoint means anchored checkpoint

Every lifecycle-advancing checkpoint must be CAS-committed and receive an AnchorQuorumCertificate + witness inclusion **before** it becomes authoritative.

There is no delayed authoritative checkpoint anchoring window.

Unanchored checkpoint = pending/advisory only.

## 19. Mandatory recovery trigger schemas

### R8V4-I056 — RecoveryTriggerSchema Registry

Recovery trigger schemas are constitutional semantic artifacts.

Every trigger type defines mandatory evidence classes and minimum independent proof.

The constitution may strengthen but ordinary policy may not omit a mandatory trigger-evidence field.

### R8V4-I057 — Reference trigger minima

At minimum:

- `ROOT_KEY_LOSS`: attested controller declaration + failed challenge for the registered credential + no active replacement credential.
- `ROOT_KEY_COMPROMISE`: incident evidence + controller declaration or independent security authority evidence + immediate key suspension event.
- `REGISTRY_CORRUPTION`: state-root mismatch + anchored last-good head proof.
- `ANCHOR_DIVERGENCE`: conflicting quorum certificates or witness consistency failure.
- `STORE_UNAVAILABLE`: independent health evidence from at least two monitoring domains.
- `CREDENTIAL_COMPROMISE`: credential revocation/suspension evidence + incident record.

## 20. Stable-ID-only authority resolution

### R8V4-I058 — Alias rejection

Authority-bearing APIs accept only stable IDs:
- tenant_id;
- principal_id;
- primitive_id;
- registry object ID;
- candidate/artifact digest.

Human aliases/names are rejected in authority fields, including migration and recovery requests.

## 21. Guard Catalog and complete positive-control mapping

The following guard IDs are frozen for design qualification.

| Guard ID | Load-bearing mechanism | Positive control | Negative/adversarial cases |
|---|---|---|---|
| G001 | EBA ControllerAttestation verification | V4-001 | V4-002,V4-003 |
| G002 | BootstrapAuthorization + singleton CAS | V4-004 | V4-005,V4-006 |
| G003 | Root quorum independence | V4-007 | V4-008,V4-009 |
| G004 | Recovery quorum + trigger proof | V4-010 | V4-011,V4-012 |
| G005 | Anchor quorum + witness | V4-013 | V4-014,V4-015,V4-016 |
| G006 | Atomic CAS_APPEND | V4-017 | V4-018,V4-019 |
| G007 | Constitutional semantic digest gate | V4-020 | V4-021,V4-022 |
| G008 | GCP-1 canonicalization/parser | V4-023 | V4-024..V4-030 |
| G009 | SPR lifecycle/stable primitive IDs | V4-031 | V4-032,V4-033 |
| G010 | Reviewer independence + two-channel constitutional review | V4-034 | V4-035,V4-036,V4-037 |
| G011 | Issuer separation of duties | V4-038 | V4-039,V4-040 |
| G012 | Revocation monotonic use-time validation | V4-041 | V4-042,V4-043 |
| G013 | Context-bound time quorum | V4-044 | V4-045,V4-046,V4-047 |
| G014 | Materiality field-mask classifier | V4-048 | V4-049,V4-050 |
| G015 | QualifiedEvidenceProducer strong evidence | V4-051 | V4-052,V4-053,V4-054 |
| G016 | Stable tenant/authority IDs only | V4-055 | V4-056,V4-057 |
| G017 | Checkpoint producer + immediate anchor | V4-058 | V4-059,V4-060 |
| G018 | State-root out-of-band mutation detection | V4-061 | V4-062,V4-063 |
| G019 | Registry/head rollback-fork guard | V4-064 | V4-065,V4-066 |
| G020 | Recovery blocked-state bypass guard | V4-067 | V4-068,V4-069 |
| G021 | Repository/history migration anchor | V4-070 | V4-071,V4-072 |
| G022 | Evidence transition closed table | V4-073 | V4-074,V4-075 |
| G023 | PLATFORM_POLICY exact-condition issuer | V4-076 | V4-077,V4-078 |
| G024 | Constitutional unrecoverable boundary | V4-079 | V4-080 |
| G025 | Mechanism-proof adjudicator | V4-081 | V4-082,V4-083,V4-084 |

Every guard has exactly identified positive coverage and adversarial coverage before implementation begins.

## 22. CaseProofContract v2

Every executable case must freeze:

- case_id;
- target_guard_id;
- prerequisite guard IDs that must already pass;
- exact precondition state digest;
- exact positive/negative mutation;
- independent fault proof artifact definition;
- guard-entry marker;
- guard-decision marker;
- prohibited earlier-guard decisions;
- paired positive case;
- raw evidence refs;
- expected final result.

A negative case rejected by a prohibited earlier guard is `CASE_INVALID`, not PASS.

A case lacking required independent fault proof is `INSUFFICIENT_EVIDENCE`.

## 23. Independent fault proof rules

Independent fault proof must come from a source different from the target guard decision.

Examples:
- revocation outage: direct quorum-read failure evidence from the revocation replicas;
- time skew: signed TimeAttestations showing non-overlapping intervals;
- anchor divergence: two valid conflicting quorum certificates or witness consistency failure;
- store mutation: raw storage snapshot + anchored expected state root;
- checkpoint replay: presented checkpoint sequence/digest + current anchored head;
- concurrent CAS race: both attempted predecessor tuples plus exactly one commit certificate.

## 24. R8 v4 preregistered falsification matrix

### External trust/controller attestation
- V4-001 valid EBA-attested distinct controller accepted.
- V4-002 self-issued controller_id with no EBA attestation -> reject.
- V4-003 revoked/expired EBA controller attestation -> reject.

### Bootstrap
- V4-004 valid BootstrapAuthorization + unused singleton CAS -> genesis succeeds.
- V4-005 attacker-created root keys absent from BootstrapAuthorization -> reject.
- V4-006 concurrent use of same BootstrapAuthorization -> exactly one genesis commits.

### Root/recovery independence
- V4-007 valid 2-of-3 root quorum across distinct EBA admin domains -> succeeds.
- V4-008 two root credentials mapping to same EBA controller -> count as one -> insufficient quorum.
- V4-009 root quorum controllers share prohibited admin domain arrangement -> reject.
- V4-010 valid recovery quorum + mandatory trigger proof -> recovery eligible.
- V4-011 shared-controller recovery quorum -> reject.
- V4-012 recovery trigger missing mandatory independent proof -> reject.

### Anchor/witness
- V4-013 valid 2-of-3 anchor quorum + BTW inclusion/consistency proof -> authoritative anchor.
- V4-014 two anchor labels controlled by same EBA controller/domain -> invalid configuration.
- V4-015 anchor quorum without witness inclusion -> non-authoritative.
- V4-016 conflicting anchor quorum certificates -> ANCHOR_EQUIVOCATION.

### Atomic transitions
- V4-017 valid CAS_APPEND exact current predecessor -> one commit.
- V4-018 two concurrent non-commutative successors -> at most one commit; loser HEAD_CONFLICT.
- V4-019 two commit certificates for same predecessor -> LEDGER_EQUIVOCATION.

### Constitutional semantic surfaces
- V4-020 valid constitutionally approved semantic-artifact digest update -> succeeds.
- V4-021 parser/predicate/evidence semantic artifact digest changes through ordinary registry update -> reject.
- V4-022 migration/recovery changes CSR-bound semantic digest without amendment -> reject.

### GCP-1
- V4-023 frozen valid reference vector canonicalizes to exact expected bytes.
- V4-024 integer > int64 -> reject.
- V4-025 leading-zero integer -> reject.
- V4-026 negative zero -> reject.
- V4-027 duplicate key -> reject.
- V4-028 non-NFC string -> reject.
- V4-029 reordered object keys -> exact same canonical bytes.
- V4-030 ordered array must not be sorted as set.

### SPR
- V4-031 valid new version/supersession preserves old primitive lineage.
- V4-032 delete primitive -> reject.
- V4-033 alias supplied to authority API instead of primitive_id -> reject.

### Constitutional review independence
- V4-034 valid Channel H + independent Channel X on exact candidate -> review contract satisfiable.
- V4-035 provider-only review with no Channel H -> insufficient for constitutional amendment.
- V4-036 Channel H controller equals amendment proposer controller -> reject independence.
- V4-037 reviewer packet includes other channel substantive findings -> isolation violation.

### Issuer SoD
- V4-038 valid distinct-controller terminal issuer configuration/beneficiary path -> allowed for downstream evaluation.
- V4-039 same controller configures and benefits from root-sensitive issuer -> reject.
- V4-040 ordinary policy attempts waive SoD -> reject.

### Revocation
- V4-041 current anchored monotonic revocation head validates unrevoked authority.
- V4-042 revoked authority use -> reject.
- V4-043 stale/rollback/unavailable revocation head -> REVOCATION_UNAVAILABLE.

### Time
- V4-044 2-of-3 context-bound time attestations for same nonce/context -> valid.
- V4-045 replay time attestation under new context -> reject.
- V4-046 shared-controller time sources -> insufficient quorum.
- V4-047 non-overlapping time windows -> TIME_AUTHORITY_UNAVAILABLE.

### Materiality
- V4-048 change only to explicitly non-material schema field -> non-material positive.
- V4-049 authority-relevant field changed -> material.
- V4-050 unknown/unclassified changed field or stale extractor digest -> MATERIALITY_UNRESOLVED.

### Strong evidence
- V4-051 active QualifiedEvidenceProducer mints allowed strong evidence from valid inputs -> accepted class.
- V4-052 weak evidence copied into new object without producer execution -> remains weak/reject strong class.
- V4-053 producer executable/credential mismatch -> reject.
- V4-054 transition to class not allowed by producer record -> reject.

### Stable IDs / tenants
- V4-055 stable-ID tenant-local authority resolution succeeds.
- V4-056 alias used in authority field -> reject.
- V4-057 cross-tenant stable ID mismatch/replay -> reject.

### Checkpoints
- V4-058 valid enrolled producer + CAS + immediate anchor -> authoritative checkpoint.
- V4-059 valid-looking but unanchored checkpoint -> pending/non-authoritative.
- V4-060 stale predecessor or concurrent checkpoint successor -> conflict/fork.

### Out-of-band mutation
- V4-061 expected anchored state root equals recomputed store root -> valid.
- V4-062 direct DB mutation changes recomputed root -> STATE_INTEGRITY_FAILURE.
- V4-063 unauthorized event lacking commit certificate appears in store -> ignored/failure evidence.

### Registry fork/rollback
- V4-064 valid next registry head -> accepted.
- V4-065 lower sequence/old head replay -> reject.
- V4-066 conflicting commit certificates -> LEDGER_EQUIVOCATION/freeze.

### Recovery/bypass
- V4-067 valid recovery transition with proper authority and trigger -> succeeds.
- V4-068 admin/UI/incident flag alone tries blocked-state transition -> reject.
- V4-069 recovery tries weaken constitutional semantic artifact -> amendment required/reject ordinary recovery.

### Repository/history migration
- V4-070 valid migration binds old anchored history, new repository, exact objects -> succeeds.
- V4-071 repository ref rewrite not matching anchored object mapping -> divergence.
- V4-072 migration omits discarded/conflicting history -> reject.

### Evidence transition
- V4-073 valid transition rule + qualified producer/provenance -> succeeds.
- V4-074 metadata-only relabel weak->strong -> reject.
- V4-075 missing/unanchored transition rule -> reject.

### PLATFORM_POLICY
- V4-076 valid independently configured PLATFORM_POLICY exact-condition issuer -> allowed downstream evaluation.
- V4-077 same-controller configuration/benefit -> reject.
- V4-078 composed project policy presented as terminal issuer -> reject.

### Unrecoverable boundary
- V4-079 root quorum unavailable but valid recovery quorum -> use recovery path.
- V4-080 both root and recovery quorum unavailable -> CONSTITUTIONAL_UNRECOVERABLE; new constitution cannot inherit authority.

### Mechanism proof
- V4-081 valid case reaches target guard with paired positive control and proof -> eligible PASS.
- V4-082 earlier unrelated guard blocks adversarial case -> CASE_INVALID, not PASS.
- V4-083 missing independent fault proof -> INSUFFICIENT_EVIDENCE.
- V4-084 constant-reject implementation -> fails positive cases.

## 25. Blocked and bounded states

The design deliberately permits safe non-operation:
- `CONSTITUTIONAL_UNRECOVERABLE`;
- `ANCHOR_EQUIVOCATION`;
- `LEDGER_EQUIVOCATION`;
- `REVOCATION_UNAVAILABLE`;
- `TIME_AUTHORITY_UNAVAILABLE`;
- `REVIEWER_UNAVAILABLE`;
- unresolved `POLICY_CONFLICT`;
- `STATE_INTEGRITY_FAILURE`.

No UI, operator, model, incident declaration, support flag, or ordinary policy may convert these states into authority.

## 26. Construction order

1. Freeze R8 v4.
2. Fresh blind independent design review.
3. Adjudicate review without mutating v4.
4. If design closes, freeze machine-readable schemas for:
   - EBA ControllerAttestation;
   - BootstrapAuthorization;
   - genesis;
   - CommitCertificate/CAS stream;
   - CAL-2/witness proof;
   - GCP-1 schema/reference vectors;
   - SPR;
   - CSR semantic-artifact manifest;
   - reviewer identity/isolation;
   - issuer/revocation;
   - context-bound TimeAttestation;
   - QualifiedEvidenceProducer;
   - state-root integrity proof;
   - recovery trigger evidence;
   - checkpoint;
   - tenant/stable IDs.
5. Freeze schema digests and exact canonicalization reference digests.
6. Freeze all V4 CaseProofContracts and positive-control map.
7. Only then begin implementation.
8. Preserve first RED evidence.
9. Execute falsification/mutation/self-falsification with mechanism proof.
10. Freeze exact implementation candidate.
11. Fresh independent implementation review.
12. Reconcile PR #39/#40 against qualified semantics; no automatic promotion.

## 27. Claim boundary

A future R8 v4 design pass would establish only that this architecture is sufficiently closed to begin implementation under the explicit T0 trust assumptions.

It would **not** prove:
- real-world honesty or non-collusion beyond the attested threshold assumption;
- EBA-1 organizational security;
- hardware custody;
- provider-internal model isolation;
- production cloud/IAM correctness;
- global consensus beyond the specified ledgers;
- legal/compliance sufficiency.

Until independent R8 v4 design closure:
- R8 v1 = CHANGES_REQUIRED;
- R8 v2 = CHANGES_REQUIRED;
- R8 v3 = CHANGES_REQUIRED;
- R8 v4 = NOT_IMPLEMENTED / INDEPENDENT_REVIEW_REQUIRED;
- PR #39 = NON_AUTHORITATIVE;
- PR #40 = NON_AUTHORITATIVE;
- holistic governance = CHANGES_REQUIRED;
- authority effect = NONE.



---

# BSP-1 semantic projection of canonical R8 v5

# R8 Meta-Governance Redesign v5 - Successor Preregistration

Status: **PREREGISTERED_DESIGN_V5 - NOT_IMPLEMENTED - INDEPENDENT_REVIEW_REQUIRED**
Authority effect: **NONE**

Predecessors:
- R8 v1 - CHANGES_REQUIRED
- R8 v2 - CHANGES_REQUIRED
- R8 v3 - CHANGES_REQUIRED
- R8 v4 commit `d779eb495b5830674e0258d4d27b768f77e10471` - CHANGES_REQUIRED


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

# BSP-1 semantic projection of canonical R8 v6

# R8 Meta-Governance Redesign v6 — Successor Preregistration

Status: **PREREGISTERED_DESIGN_V6 — NOT_IMPLEMENTED — INDEPENDENT_REVIEW_REQUIRED**
Authority effect: **NONE**

Effective design:
- R8 v5 commit `53d695dff34d14365770d1dbdad8c6620e31a503` is the inherited base.
- This v6 document supersedes v5 only where it states a stronger or more specific rule.
- Unmodified v5 rules remain in force for design review.
- R8 v5 remains immutable and CHANGES_REQUIRED.


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

# BSP-1 semantic projection of canonical R8 v7

# R8 Meta-Governance Redesign v7 — Successor Preregistration

Status: **PREREGISTERED_DESIGN_V7 — NOT_IMPLEMENTED — INDEPENDENT_REVIEW_REQUIRED**
Authority effect: **NONE**

Effective design:
- R8 v5 commit `53d695dff34d14365770d1dbdad8c6620e31a503` is the inherited base.
- R8 v6 commit `e0e6995a61dab629ff49efc19f6d6128936b9c20` is the inherited successor overlay.
- This v7 document supersedes v5/v6 only where v7 states a stronger or more specific rule.
- R8 v5 and v6 remain immutable and CHANGES_REQUIRED.


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



---

# BSP-1 semantic projection of canonical R8 v8

# R8 Meta-Governance Redesign v8 — Successor Preregistration

Status: **PREREGISTERED_DESIGN_V8 — NOT_IMPLEMENTED — INDEPENDENT_REVIEW_REQUIRED**
Authority effect: **NONE**

Effective design lineage:
- R8 v4 commit `d779eb495b5830674e0258d4d27b768f77e10471` supplies inherited G001-G025/V4 case semantics.
- R8 v5 commit `53d695dff34d14365770d1dbdad8c6620e31a503` is the inherited base.
- R8 v6 commit `e0e6995a61dab629ff49efc19f6d6128936b9c20` is an inherited overlay.
- R8 v7 commit `fad366add685a978c55837e420e3bcb0939d41aa` is an inherited overlay.
- This v8 document supersedes prior generations only where it states a stronger or more specific rule.


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



---

# BSP-1 semantic projection of canonical R8 v9

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



---

# BSP-1 semantic projection of canonical R8 v10

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



---

# BSP-1 semantic projection of canonical R8 v11

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

