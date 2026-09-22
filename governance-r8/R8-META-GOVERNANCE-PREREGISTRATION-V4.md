# R8 Meta-Governance Redesign v4 — Successor Preregistration

Status: **PREREGISTERED_DESIGN_V4 — NOT_IMPLEMENTED — INDEPENDENT_REVIEW_REQUIRED**
Authority effect: **NONE**

Predecessors:
- R8 v1 — CHANGES_REQUIRED
- R8 v2 — CHANGES_REQUIRED
- R8 v3 commit `aa4a5e6a320002731926e0c9ccbbb62c2bfbb0ca` — CHANGES_REQUIRED

R8 v3 adjudication:
- `13715113287c3732be3cc4bdc60716fbb95396aa`

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
