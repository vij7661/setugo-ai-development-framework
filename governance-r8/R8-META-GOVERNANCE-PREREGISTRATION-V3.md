# R8 Meta-Governance Redesign v3 — Successor Preregistration

Status: **PREREGISTERED_DESIGN_V3 — NOT_IMPLEMENTED — INDEPENDENT_REVIEW_REQUIRED**

Authority effect: **NONE**

Predecessors:
- R8 v1: `d7d4876781fb82bcf8df43cf15bbe069acf33a0a` — CHANGES_REQUIRED
- R8 v2: `fcc6e8dbfb4133b9b9bb891cedaa1190d6e216ab` — CHANGES_REQUIRED

R8 v2 review adjudication:
- `bc0f6b79a1ef1ede7ecd890d92262419c5c33de7`

## 1. Objective

R8 v3 freezes a concrete reference design for the platform meta-governance root before implementation.

It specifically closes:
- L0 bootstrap/root ceremony;
- constitutional quorum independence;
- meta-governor self-amendment surfaces;
- exact canonicalization and semantic primitive rules;
- append-only authoritative history anchoring;
- reviewer isolation and controlling-lineage identity;
- issuer/revocation separation of duties;
- trusted-time authority;
- classifier and evidence-transition registries;
- recovery anti-collusion and bounded deadlock outcomes;
- per-case mechanism proof and paired positive controls.

R8 v3 does not grant implementation, qualification, merge, release, deploy, production, policy, or terminal authority.

## 2. Frozen authority model

Authority layers are:

- **L0 Constitutional Root** — only layer allowed to define or amend constitutional authority.
- **L1 Meta-Governor** — deterministic evaluator of already-authorized constitutional/registry/policy state.
- **L2 Governed Registries** — append-only state under explicit lifecycle authorities.
- **L3 Effective Governance Snapshot** — exact candidate policy/review/materiality/evidence requirements.
- **L4 Governed Action Gates** — bounded action and terminal gates consuming L3 + evidence + authority.

No lower layer may create, widen, replace, or reinterpret a higher layer.

## 3. Concrete L0 reference ceremony

### R8V3-I01 — Root principal model

The reference constitutional root has exactly three root principals:
- `ROOT-A`
- `ROOT-B`
- `ROOT-C`

Each root principal has:
- immutable `principal_id`;
- immutable `controller_id`;
- one active Ed25519 public-key identity;
- one credential/device identity;
- no delegation during bootstrap;
- a tenant/root namespace binding.

Two root principals with the same `controller_id`, credential identity, or device/key identity are not independent and count as one controller for quorum.

### R8V3-I02 — Root quorum

Ordinary constitutional amendment requires **2-of-3 independent root controllers**.

The proposer cannot be the sole controlling lineage behind both quorum approvals.

The Meta-Governor, any model, project/org policy actor, reviewer, worker, service account, or ordinary operator cannot count as a root controller unless explicitly enrolled in the current constitutional manifest as a root principal.

### R8V3-I03 — Separate recovery quorum

The reference recovery set contains exactly three recovery principals:
- `RECOVERY-A`
- `RECOVERY-B`
- `RECOVERY-C`

Root replacement requires **2-of-3 independent recovery controllers**.

No `controller_id` may simultaneously belong to the active root set and active recovery set.

Recovery principals may not perform ordinary constitutional amendment.

### R8V3-I04 — Bootstrap ceremony ID and nonce

Bootstrap uses:
- a globally unique `constitution_id`;
- a random 256-bit `bootstrap_nonce`;
- fixed `ceremony_version = R8V3-L0-1`;
- exact canonical genesis bytes;
- root signatures over `SHA-256(canonical_genesis_bytes)`.

The same `constitution_id + bootstrap_nonce` cannot be accepted twice.

### R8V3-I05 — Genesis approval

Genesis is valid only when:
- all three root principal public identities are present;
- all three recovery principal public identities are present;
- controller-independence predicate is satisfied;
- at least 2 independent root signatures verify;
- genesis canonicalization profile is exactly `GCP-1`;
- initial registry genesis digests are included;
- first anchor event is committed to both Anchor Replica A and Anchor Replica B.

### R8V3-I06 — First registries created atomically with genesis

Genesis commits the initial heads/digests for:
- Constitutional Surface Registry;
- Platform Invariant Registry;
- Policy Registry;
- Authority Issuer Registry;
- Authority Revocation Registry;
- Governance Object-Class Registry;
- Reviewer Principal/Independence Registry;
- Evidence Transition Registry;
- Tenant Registry;
- Recovery Authority Registry;
- Time Authority Registry;
- History Anchor Registry.

A genesis that omits one mandatory registry is invalid.

### R8V3-I07 — Bootstrap anti-replay

A genesis is rejected when:
- its constitution_id already exists;
- bootstrap_nonce was previously used;
- anchor sequence is not zero;
- predecessor is non-null;
- root/recovery identities differ from the signed canonical bytes;
- either anchor replica already records a conflicting genesis.

### R8V3-I08 — Bootstrap positive control

A valid 2-of-3 independent-root ceremony with both anchor replicas available must succeed and produce the exact expected genesis/registry heads.

This positive control is mandatory; a constant-reject implementation cannot qualify.

## 4. Concrete constitutional anchor

### R8V3-I09 — Constitutional Anchor Ledger (CAL-1)

The reference authoritative anchor is `CAL-1`, an append-only hash-chained log.

Each anchor event contains:
- `constitution_id`;
- `anchor_seq`;
- `prev_anchor_digest`;
- `event_class`;
- `subject_id`;
- `subject_digest`;
- `tenant_or_root_namespace`;
- `constitutional_manifest_digest`;
- `approval_proof_digest`;
- `time_proof_digest` when required;
- `canonical_event_digest`.

### R8V3-I10 — Dual independent anchor replicas

CAL-1 is durably written to two independently administered append-only replicas:
- `ANCHOR-A`
- `ANCHOR-B`

For constitutional, root/recovery, registry-schema, history-migration, and terminal-authority-root milestones, a new event becomes authoritative only when both replicas acknowledge the same canonical event digest at the same sequence.

One-replica-only acknowledgement is `ANCHOR_INCOMPLETE`, not authority.

### R8V3-I11 — Anchor fork detection

If A and B expose different digests for the same `constitution_id + anchor_seq`, the system enters `ANCHOR_DIVERGENCE` and freezes authority-bearing transitions.

Neither branch is chosen by wall clock, operator preference, chat context, or repository HEAD.

### R8V3-I12 — Anchor recovery

Anchor repair requires recovery quorum and proof of the last sequence/digest on which both replicas agreed.

The repaired successor event records:
- divergent ranges;
- chosen last-common anchor;
- reconstruction evidence;
- recovery approvals;
- new replica identities if migrated.

Prior divergent/failure history remains preserved.

## 5. Constitutional surface closure

### R8V3-I13 — Constitutional Surface Registry (CSR)

The CSR enumerates every semantic surface whose change can alter authority.

At minimum:
- Meta-Governor executable identity/hash;
- Meta-Governor decision schema;
- all authority-validation predicates;
- GCP-1 canonicalization profile;
- parser implementation/schema version;
- Semantic Primitive Registry;
- registry event schema;
- invariant schema/lifecycle semantics;
- policy schema/composition/conflict ontology;
- identity/controller/delegation semantics;
- reviewer independence semantics;
- object-class/materiality semantics;
- issuer/revocation semantics;
- PLATFORM_POLICY issuer semantics;
- time-authority semantics;
- checkpoint/history-anchor semantics;
- evidence transition semantics;
- recovery/root-replacement semantics;
- migration semantics;
- tenant namespace semantics.

### R8V3-I14 — CSR change is constitutional

Adding, removing, reinterpreting, or changing any CSR entry is `CONSTITUTIONAL_AMENDMENT`.

An ordinary registry or policy write cannot change CSR semantics.

### R8V3-I15 — Meta-governor implementation binding

The exact Meta-Governor executable/artifact digest and authority-relevant schema digest must match the current constitutional manifest.

A deployed binary with a different digest has authority effect NONE until constitutionally approved.

### R8V3-I16 — Migration/recovery cannot launder self-amendment

Recovery, migration, registry reconstruction, repository migration, or schema migration may not change any CSR semantic surface unless the operation also satisfies the constitutional-amendment path.

## 6. Constitutional amendment and root replacement

### R8V3-I17 — Constitutional amendment ceremony

A constitutional amendment requires:
- unique amendment_id;
- exact predecessor constitutional digest;
- exact changed CSR/invariant objects;
- impact analysis;
- required independent review evidence;
- 2-of-3 independent root approvals;
- canonical successor manifest under GCP-1;
- dual CAL-1 anchoring.

### R8V3-I18 — Amendment anti-replay/fork

An amendment is rejected if:
- predecessor is not current authoritative constitutional head;
- amendment_id already exists;
- anchor sequence is stale;
- same predecessor already has an authoritative successor;
- approvals bind different bytes.

### R8V3-I19 — Root-key rotation

Root-key rotation is a constitutional amendment.

A root principal may not approve a change that replaces its key as the sole approval controller; full 2-of-3 independent-root quorum is still required.

### R8V3-I20 — Root replacement

If root quorum is unavailable, replacement requires:
- recovery trigger proof;
- 2-of-3 independent recovery approvals;
- exact last authoritative constitutional digest;
- exact lost/compromised root identities;
- new root identities satisfying controller independence;
- independent review where accessible;
- successor constitutional manifest;
- dual CAL-1 anchor.

A lost/compromised root principal cannot sign its own replacement as recovery authority.

### R8V3-I21 — Simultaneous root + recovery loss

If neither valid root quorum nor valid recovery quorum exists, state becomes `CONSTITUTIONAL_UNRECOVERABLE`.

Authority-bearing operations remain permanently blocked for that constitution.

Permitted operations are limited to:
- forensic export;
- evidence/history verification;
- creation of a wholly new constitution with a new constitution_id.

A new constitution cannot silently inherit terminal/promotion authority from the unrecoverable constitution. Any migration is a separately reviewed import with no inherited authority unless independently requalified.

## 7. Exact governance canonicalization profile GCP-1

### R8V3-I22 — Encoding

Governance enforcement objects use JSON serialized under `GCP-1`:
- UTF-8 only;
- no BOM;
- input must be valid Unicode;
- all strings must already be Unicode NFC; non-NFC input is rejected rather than normalized silently.

### R8V3-I23 — Object keys

- object keys must be unique;
- duplicate keys are rejected before semantic parsing;
- keys are sorted lexicographically by their NFC Unicode scalar sequence;
- unknown fields are rejected unless schema explicitly marks an extension map.

### R8V3-I24 — Numbers

Governance objects may use signed integers only.

Floating point, decimal literals, exponent form, NaN, Infinity, and negative zero are prohibited.

Quantities requiring fractions use explicit integer numerator/denominator fields or fixed integer base units defined by the Semantic Primitive Registry.

### R8V3-I25 — Time representation

Absolute times are signed 64-bit integer Unix seconds plus:
- registered time-source proof identity;
- optional bounded uncertainty in integer milliseconds.

Ordering never uses time when an authoritative sequence exists.

### R8V3-I26 — Arrays and sets

Arrays are ordered unless the schema explicitly defines a field as a set.

Set fields:
- are serialized as arrays;
- elements are canonicalized independently;
- sorted by element canonical SHA-256 digest then canonical bytes;
- duplicates are rejected.

### R8V3-I27 — Null/absence

A field absent from an object is distinct from explicit null.

Null is prohibited unless the exact schema marks the field nullable.

Default values are not inferred during signature/digest validation; defaults must be materialized before canonicalization where the schema requires them.

### R8V3-I28 — Strings and escapes

Canonical output uses the shortest JSON escaping required for control characters, quote, and backslash.

Other Unicode characters remain UTF-8.

No alternate escape spelling may produce a second canonical byte representation.

### R8V3-I29 — Canonical digest

All authority-relevant digests are `SHA-256(GCP-1 canonical bytes)` unless a constitutional successor explicitly changes the algorithm via constitutional amendment.

### R8V3-I30 — Parser version binding

The parser/schema implementation identity used for authority decisions is a CSR entry and is bound in the constitutional manifest.

Changing parser behavior without constitutional amendment yields authority effect NONE.

## 8. Semantic Primitive Registry (SPR)

### R8V3-I31 — No free-text enforcement semantics

Authority predicates use versioned primitive IDs for:
- action classes;
- authority classes;
- evidence classes;
- review dimensions;
- scope types;
- lifecycle states;
- units/base units;
- tenant/object types;
- conflict relation types.

Human prose cannot redefine an SPR primitive.

### R8V3-I32 — Primitive change

Creating, deleting, aliasing, changing meaning, or changing unit conversion for an authority-relevant SPR primitive is a constitutional amendment.

### R8V3-I33 — Alias safety

Human-readable aliases resolve only to immutable primitive IDs and cannot shadow or override an existing primitive ID.

## 9. Registry head and fork authority

### R8V3-I34 — Registry head anchoring

Every authority-bearing registry head is periodically or transactionally anchored into CAL-1 by:
- registry_id;
- registry_seq;
- head_event_digest;
- constitutional digest.

A registry head later presented with a different digest at the same sequence causes `REGISTRY_FORK`.

### R8V3-I35 — Competing successors

Two validly signed registry events with the same predecessor are not resolved by last-write-wins.

They produce `REGISTRY_FORK` unless the registry schema explicitly supports concurrent commutative events and the frozen merge rule proves deterministic equivalence.

### R8V3-I36 — Fork reconciliation

Non-commutative registry fork reconciliation requires:
- freeze of affected authority;
- last anchored common head;
- authorized recovery/adjudication;
- explicit chosen successor;
- preservation of discarded branch evidence;
- new CAL-1 anchor.

## 10. Principal controlling-lineage and reviewer independence

### R8V3-I37 — Controller lineage record

Every authority-bearing principal record includes:
- principal_id;
- controller_id;
- credential_id;
- execution_identity;
- tenant_id;
- delegation_parent if any;
- delegation_scope;
- lifecycle status;
- provenance/attestation method.

### R8V3-I38 — Independence equivalence

Two principals are non-independent when any applicable policy-required dimension overlaps, including:
- same controller_id;
- same credential_id;
- same delegation root;
- same persistent execution/session identity;
- same reviewer cache namespace carrying substantive reviewer outputs.

Provider/model equality alone does not necessarily make principals identical, but policy may require provider/model separation.

### R8V3-I39 — Reviewer execution isolation

Blind reviewer executions require:
- unique review_execution_id;
- new conversation/session/request context under platform control;
- no prior reviewer output in prompt/history;
- no substantive reviewer-output cache reads;
- source-artifact cache keys restricted to immutable candidate digests;
- packet generated from exact candidate/snapshot;
- contamination audit record.

The platform claims isolation only for platform-controlled context. Undetectable provider-internal memory is outside claim scope unless separately qualified.

### R8V3-I40 — Controlling-lineage proof

Reviewer assignment must resolve controller/delegation lineage from the Reviewer Principal Registry before dispatch.

Unknown or unverifiable controlling lineage cannot satisfy an independent slot.

## 11. Issuer / PLATFORM_POLICY separation

### R8V3-I41 — Issuer enrollment authority

Issuer enrollment requires a parent authority class defined in the constitution.

No issuer can:
- enroll itself;
- approve its own scope expansion;
- undo its own revocation;
- reactivate itself;
- rotate to an unbound replacement key without parent approval.

### R8V3-I42 — Separation-of-duties predicate

For terminal or root-sensitive issuer changes, configurator/controller and beneficiary/controller must be disjoint where effective policy requires separation.

A `PLATFORM_POLICY` issuer cannot authorize an actor whose controller_id unilaterally created or materially configured that issuer.

### R8V3-I43 — Revocation freshness

Every authority-bearing use binds:
- revocation registry head sequence/digest;
- latest anchor proving that head;
- authority record issue sequence;
- current use sequence/time proof.

If revocation head cannot be verified, result is `REVOCATION_UNAVAILABLE` and use is denied.

### R8V3-I44 — Revocation undo

Undoing a revocation is a new material issuer-lifecycle event requiring the parent authority defined by the constitution.

The historical revocation remains visible.

## 12. Concrete time authority model

### R8V3-I45 — Time Authority Set

The reference constitution registers three independent time authorities:
- `TIME-A`
- `TIME-B`
- `TIME-C`

Each produces signed `TimeAttestation` objects:
- time_source_id;
- attested_unix_seconds;
- uncertainty_ms;
- attestation_nonce;
- issued_sequence;
- signature.

### R8V3-I46 — Time quorum

Expiry-sensitive constitutional/root/terminal decisions require at least 2-of-3 valid time attestations whose uncertainty windows overlap within the constitutional `max_time_skew_ms`.

Time-source controllers must satisfy the constitutional independence predicate.

### R8V3-I47 — Time outage

If 2-of-3 trustworthy attestations are unavailable or non-overlapping, expiry-sensitive action returns `TIME_AUTHORITY_UNAVAILABLE`.

No local wall clock may silently substitute.

### R8V3-I48 — Expiry/revocation race

Use-time validation is performed against:
- current authoritative revocation head first;
- then time quorum proof;
- then authority expiry.

A newly observed revocation dominates an otherwise time-valid authority record.

## 13. Materiality/classifier registry closure

### R8V3-I49 — Object-Class Registry schema

Each object class record includes:
- object_class_id;
- schema/version;
- authority_impact enum;
- dependency extraction rule identity;
- default materiality;
- allowed non-material mutations;
- review-dimension mapping;
- lifecycle authority;
- constitutional binding when authority-bearing.

### R8V3-I50 — Non-file authority objects

The initial class set explicitly includes:
- constitutional manifests;
- all governed registry events;
- policies;
- reviewer assignments;
- evidence transitions;
- authority records;
- revocations;
- time-source state;
- checkpoints;
- history anchors;
- recovery events;
- CI/gate definitions;
- workflow definitions;
- schema/parser/canonicalization artifacts.

### R8V3-I51 — Dependency proof

Materiality decisions record the exact dependency metadata digest and object-class registry head used.

Caller-authored dependency metadata cannot lower materiality.

### R8V3-I52 — Unknown class

Unknown or unverifiable object class = `MATERIALITY_UNRESOLVED` and cannot be treated as routine.

## 14. Evidence Transition Registry closure

### R8V3-I53 — Transition record schema

Each allowed transition rule binds:
- transition_rule_id/version;
- source evidence class;
- target evidence class;
- required producer/provenance class;
- required validation predicates;
- transition authority class;
- allowed resulting uses;
- non-upgradable flag;
- tenant/scope constraints.

### R8V3-I54 — Initial non-upgradable rules

The initial registry states:
- `USER_PROVIDED_EXTERNAL_CONTENT` cannot become `PLATFORM_AUTHENTICATED_REVIEW`;
- `USER_ATTESTED_EXTERNAL_LLM_REVIEW` cannot become `PLATFORM_AUTHENTICATED_REVIEW`;
- `REVIEW_PROVIDER_TELEMETRY` cannot become semantic review PASS;
- a portable packet manifest cannot become authenticated execution provenance.

A stronger class requires creation of a new evidence object through the required trusted execution path, not metadata upgrade.

### R8V3-I55 — Transition authorization

The Meta-Governor may execute a transition only when:
- transition rule is in current anchored registry head;
- producer/provenance predicates verify;
- tenant/candidate/snapshot bindings match;
- transition authority is satisfied.

Transition-registry change itself is material; authority-bearing semantic changes covered by CSR require constitutional amendment.

## 15. Tenant stable identity

### R8V3-I56 — Tenant ID creation

`tenant_id` is a 128-bit random identifier generated by the Tenant Registry service and committed as a registry event before use.

Display names and aliases never serve as authority IDs.

### R8V3-I57 — Alias collision

Alias collisions across tenants are permitted only as display metadata because authority always resolves through tenant_id.

An alias cannot redirect an authority object from one tenant_id to another.

### R8V3-I58 — Tenant migration

Tenant/project/org migration or reassignment:
- preserves stable IDs where identity remains the same;
- otherwise creates a new stable ID;
- records source/destination lineage;
- revalidates issuer scopes, policies, evidence, reviewer assignments, and authority records.

Cross-tenant authority is not inherited automatically.

## 16. Checkpoint producer identity and history

### R8V3-I59 — Coordination component attestation

An authoritative checkpoint producer must be an enrolled service principal with:
- exact component artifact identity/hash;
- credential identity;
- allowed checkpoint event class;
- tenant scope;
- active/non-revoked status.

Unknown component identity cannot produce authoritative checkpoints.

### R8V3-I60 — Checkpoint anchor

Each accepted lifecycle-advancing checkpoint is hash-chained to its predecessor and its head is anchored into CAL-1 according to the effective anchoring frequency.

Terminal/constitutional/review-barrier checkpoints require immediate dual anchor.

### R8V3-I61 — Fork choice prohibition

Two competing checkpoint successors are `CHECKPOINT_FORK`.

No UI/operator/chat action can choose a branch without the governed reconciliation authority and preserved evidence.

## 17. Recovery trigger proof and anti-collusion

### R8V3-I62 — Recovery Trigger Evidence

Root/registry/history recovery requires a typed trigger:
- `ROOT_KEY_LOSS`
- `ROOT_KEY_COMPROMISE`
- `REGISTRY_CORRUPTION`
- `ANCHOR_DIVERGENCE`
- `STORE_UNAVAILABLE`
- `CREDENTIAL_COMPROMISE`

Each trigger requires evidence defined by the constitution.

A recovery quorum assertion without trigger evidence is insufficient.

### R8V3-I63 — Recovery independence

Recovery quorum uses controlling-lineage independence identical in strength to root quorum.

No shared-controller 2-of-3 recovery approval is valid.

### R8V3-I64 — Root/recovery separation

No controller_id may be simultaneously active in both root and recovery sets.

Changing this separation rule is constitutional amendment.

### R8V3-I65 — Reviewer starvation

If no qualified reviewer exists:
- state remains `REVIEWER_UNAVAILABLE`;
- a preregistered substitution policy may select a different qualified independent reviewer class;
- if no substitute satisfies the frozen floor, progression remains blocked.

Reviewer starvation cannot authorize self-review.

### R8V3-I66 — Unresolvable policy conflict

If `POLICY_CONFLICT` cannot be resolved under ordinary policy authority:
- the affected transition remains blocked;
- if the conflict is caused by non-overridable constitutional semantics, only constitutional amendment may change those semantics;
- if no lawful amendment quorum exists, the constitution may remain non-operational rather than silently weaken the invariant.

## 18. Blocked-state bypass prohibition

### R8V3-I67 — UI/incident paths

UI buttons, admin consoles, incident declarations, alert acknowledgements, support flags, database edits, and chat/operator commands are not authority classes.

Any such path that changes a blocked state must present an already-authorized governed transition record.

### R8V3-I68 — Out-of-band mutation detection

Authority-bearing storage mutated outside an authorized event path creates integrity failure and requires recovery; it does not become current state.

## 19. Per-case mechanism-proof contract

Every executed falsification case has a frozen `CaseProofContract`:

- case_id;
- target_guard_id;
- exact precondition state digest;
- exact adversarial mutation/fault;
- independent fault proof requirement;
- expected guard-entry evidence;
- expected guard-decision evidence;
- prohibited earlier-guard outcomes;
- paired positive_control_case_id;
- expected authoritative endpoint;
- preserved raw evidence refs.

A case is PASS only when the target guard is proven reached.

An earlier unrelated rejection is not PASS for that case.

## 20. Positive-control mapping rule

Each load-bearing guard has at least one paired valid control traversing the same guard without the adversarial condition.

At minimum guards requiring paired controls:
- bootstrap quorum;
- constitutional amendment;
- CAL-1 anchoring;
- registry append/fork validation;
- canonicalization/parser;
- policy composition;
- reviewer independence;
- materiality classifier;
- issuer enrollment;
- revocation lookup;
- time quorum;
- PLATFORM_POLICY separation;
- tenant isolation;
- checkpoint production/replay;
- evidence transition;
- recovery trigger/quorum;
- repository/history migration.

## 21. R8 v3 preregistered falsification matrix

### L0/bootstrap
- V3-001 valid 2-of-3 independent-root genesis + dual anchor succeeds.
- V3-002 one root controller with two credentials attempts 2-of-3 -> reject.
- V3-003 root principals share controller_id -> bootstrap invalid.
- V3-004 reused bootstrap nonce -> reject.
- V3-005 conflicting genesis at same constitution_id -> ANCHOR_DIVERGENCE/reject.
- V3-006 genesis omits mandatory first registry -> reject.
- V3-007 Meta-Governor attempts self-bootstrap -> reject.

### Constitutional amendment/self-amendment
- V3-008 valid constitutional amendment succeeds with independent quorum + dual anchor.
- V3-009 parser behavior changes without amendment -> authority effect NONE.
- V3-010 GCP-1 changes without amendment -> reject.
- V3-011 provenance/evidence semantics change through registry migration without amendment -> reject.
- V3-012 recovery attempts to change CSR surface -> reject unless constitutional amendment requirements also met.
- V3-013 changed Meta-Governor binary/schema not in constitution -> authority effect NONE.

### Canonicalization
- V3-014 valid canonical policy object produces expected exact bytes/digest.
- V3-015 duplicate key -> reject.
- V3-016 non-NFC string -> reject.
- V3-017 float/exponent/negative-zero input -> reject.
- V3-018 reordered ordinary object keys -> same canonical bytes.
- V3-019 set input order differs -> same canonical bytes after canonical set sorting.
- V3-020 duplicate set element -> reject.
- V3-021 absent vs null mismatch -> distinct/reject per schema.
- V3-022 unknown non-extension field -> reject.

### Anchor/history/registry
- V3-023 valid CAL-1 next event written identically to A+B succeeds.
- V3-024 A/B same sequence different digest -> ANCHOR_DIVERGENCE.
- V3-025 one replica unavailable for root milestone -> ANCHOR_INCOMPLETE.
- V3-026 registry lower sequence/old head replay -> reject.
- V3-027 two non-commutative valid successors -> REGISTRY_FORK.
- V3-028 valid governed fork reconciliation preserves discarded branch evidence.
- V3-029 repo ref rewrite after anchored milestone -> detect divergence.
- V3-030 valid repository migration binds old/new anchors and succeeds.

### Reviewer identity/isolation
- V3-031 valid independent reviewer with distinct controller lineage succeeds assignment.
- V3-032 alias/delegated identity same controller as proposer -> reject.
- V3-033 same credential under different principal labels -> reject independence.
- V3-034 reused review session containing prior findings -> isolation violation.
- V3-035 shared substantive reviewer-output cache -> isolation violation.
- V3-036 immutable source-artifact cache only -> allowed positive control.
- V3-037 unknown controlling lineage -> cannot satisfy independent slot.

### Issuer/revocation/PLATFORM_POLICY
- V3-038 valid parent-authorized issuer enrollment succeeds.
- V3-039 issuer self-enrollment -> reject.
- V3-040 issuer self-scope expansion -> reject.
- V3-041 revoked issuer use -> reject.
- V3-042 revocation head unavailable -> REVOCATION_UNAVAILABLE.
- V3-043 unauthorized revocation undo -> reject.
- V3-044 same controller configures PLATFORM_POLICY issuer and is beneficiary -> reject where separation required.
- V3-045 valid independently configured PLATFORM_POLICY issuer exact condition -> succeeds for downstream evaluation only.

### Time
- V3-046 2-of-3 overlapping independent time attestations -> valid time proof.
- V3-047 one time source only -> TIME_AUTHORITY_UNAVAILABLE.
- V3-048 two attestations non-overlapping beyond skew -> TIME_AUTHORITY_UNAVAILABLE.
- V3-049 wall-clock rollback cannot alter event sequence.
- V3-050 revocation observed before expiry check -> revocation dominates.

### Classifier/materiality
- V3-051 valid known non-material object change -> non-material.
- V3-052 new governance object class without registry entry -> MATERIALITY_UNRESOLVED.
- V3-053 non-file revocation/policy/checkpoint state mutation -> material.
- V3-054 attacker-authored dependency metadata attempts downgrade -> reject.
- V3-055 classifier registry rollback -> reject/fail closed.
- V3-056 valid authorized object-class registry extension succeeds and becomes material reviewed change.

### Evidence transitions
- V3-057 valid allowed transition with correct provenance/authority succeeds.
- V3-058 metadata-only class relabel -> no authority change.
- V3-059 USER_ATTESTED external review -> PLATFORM_AUTHENTICATED review -> reject.
- V3-060 telemetry SUCCESS -> semantic PASS -> reject.
- V3-061 packet manifest -> authenticated provenance -> reject.
- V3-062 transition rule missing -> reject.
- V3-063 transition registry rollback -> reject.

### Tenant isolation
- V3-064 valid tenant-local policy/evidence/authority path succeeds.
- V3-065 same display alias in tenant A/B -> stable IDs remain distinct.
- V3-066 tenant A issuer/evidence replay in B -> reject.
- V3-067 valid tenant migration revalidates scopes and succeeds.
- V3-068 reassignment without revalidation attempts authority inheritance -> reject.

### Checkpoints
- V3-069 valid attested checkpoint producer extends current head -> succeeds.
- V3-070 unknown component self-issues checkpoint -> reject.
- V3-071 old valid checkpoint replay -> stale/reject.
- V3-072 two valid successors -> CHECKPOINT_FORK.
- V3-073 operator/UI attempts choose fork without reconciliation authority -> reject.
- V3-074 valid governed checkpoint reconciliation succeeds and preserves losing branch evidence.

### Recovery/deadlock
- V3-075 valid recovery trigger + 2-of-3 independent recovery quorum -> eligible recovery.
- V3-076 shared-controller recovery quorum -> reject.
- V3-077 recovery without trigger evidence -> reject.
- V3-078 root actor also in recovery set -> constitution invalid.
- V3-079 valid root replacement via recovery quorum + dual anchor succeeds.
- V3-080 simultaneous root+recovery loss -> CONSTITUTIONAL_UNRECOVERABLE.
- V3-081 reviewer starvation -> REVIEWER_UNAVAILABLE, no self-review.
- V3-082 valid preregistered reviewer substitute satisfying same floor -> succeeds.
- V3-083 unresolvable non-overridable policy conflict -> remains blocked absent constitutional amendment.
- V3-084 incident/UI/admin flag attempts bypass -> reject.

### Mechanism proof
- V3-085 each negative case with target guard blocked by earlier guard -> case FAIL/INVALID, not PASS.
- V3-086 independent fault proof missing for injected fault -> INSUFFICIENT_EVIDENCE.
- V3-087 paired positive control does not traverse target guard -> both case/control invalid for qualification.
- V3-088 constant-reject implementation -> fails positive controls.
- V3-089 canonicalization case V3-018 must produce exact frozen bytes/digest; “or reject” is not accepted.
- V3-090 revocation/time/anchor faults require independent state proof before denial can count.

## 22. Deadlock and bounded non-operational states

Fail-closed states are not automatically defects.

The design explicitly allows permanent non-operational outcomes when no lawful trust path exists:
- `CONSTITUTIONAL_UNRECOVERABLE`
- unresolved `POLICY_CONFLICT`
- `REVIEWER_UNAVAILABLE` with no qualified substitute
- `ANCHOR_DIVERGENCE` pending valid recovery
- `REVOCATION_UNAVAILABLE`
- `TIME_AUTHORITY_UNAVAILABLE`

No emergency bypass may convert these into authority.

Business-continuity mitigation must be designed prospectively through independent root/recovery/time/reviewer diversity, not invented after failure.

## 23. Construction order

1. Freeze R8 v3 exactly.
2. Obtain fresh blind independent design review of R8 v3.
3. Adjudicate review without mutating v3.
4. Only after bounded design closure, freeze executable schemas and exact GCP-1 reference vectors.
5. Freeze every V3 case with CaseProofContract and positive-control mapping.
6. Implement minimal deterministic constitutional root, CAL-1, registries, Meta-Governor, and validation components.
7. Preserve first RED evidence.
8. Execute mechanism-proof tests, positive controls, adversarial negatives, mutation/self-falsification.
9. Freeze exact implementation candidate.
10. Fresh independent implementation review.
11. Reconcile PR #39/#40 against qualified R8 semantics; neither is automatically promoted.

## 24. Claim boundary

A future R8 v3 bounded design pass would mean only that the preregistered design is sufficiently closed to begin implementation.

It would not prove implementation correctness, production IAM/KMS, real hardware-key custody, provider-internal reviewer isolation, global distributed consensus, legal compliance, or disaster-recovery effectiveness.

Until R8 v3 independently closes:
- R8 v1 = CHANGES_REQUIRED;
- R8 v2 = CHANGES_REQUIRED;
- R8 v3 = NOT_IMPLEMENTED / INDEPENDENT_REVIEW_REQUIRED;
- PR #39 = NON_AUTHORITATIVE;
- PR #40 = NON_AUTHORITATIVE;
- holistic governance = CHANGES_REQUIRED;
- authority effect = NONE.
