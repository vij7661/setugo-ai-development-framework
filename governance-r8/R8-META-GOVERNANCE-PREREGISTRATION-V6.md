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
