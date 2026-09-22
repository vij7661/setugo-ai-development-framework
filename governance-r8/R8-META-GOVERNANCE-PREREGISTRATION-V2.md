# R8 Meta-Governance Redesign v2 — Successor Preregistration

Status: **PREREGISTERED_DESIGN_V2 — NOT_IMPLEMENTED — INDEPENDENT_REVIEW_REQUIRED**

Authority effect: **NONE**

Predecessor:
- R8 v1 commit: `d7d4876781fb82bcf8df43cf15bbe069acf33a0a`
- R8 v1 remains preserved and `CHANGES_REQUIRED`

Design-review adjudication:
- `review-adjudications/R8-META-GOVERNANCE-DESIGN-REVIEW-ADJUDICATION.md`
- adjudication commit: `2aae80c40bd079376af0a29b98e5905622b6fe89`

## 1. Objective

R8 v2 defines the constitutional and deterministic authority structure required before implementing the platform meta-governor.

It closes design gaps in:
- root/bootstrap authority;
- meta-governor self-amendment;
- registry lifecycle;
- issuer and revocation authority;
- policy canonicalization/composition;
- review identity and independence;
- materiality classification;
- continuity/history anchoring;
- evidence-class transitions;
- recovery/root replacement;
- time/freshness;
- tenant isolation;
- positive-control falsification.

R8 v2 does not grant merge, release, deploy, production, qualification, policy, or terminal authority.

## 2. Authority layers

Authority is separated into five layers.

### L0 — Constitutional Root

The Constitutional Root is outside ordinary project/org/policy governance.

It defines:
- root principals/keys or equivalent authenticated root identities;
- root quorum;
- constitutional operations;
- meta-governor implementation/schema identity;
- registry schemas;
- non-overridable invariant lifecycle authority;
- recovery-authority identities and quorum;
- constitutional amendment rules.

The Meta-Governor cannot create L0 authority.

### L1 — Meta-Governor

The deterministic Meta-Governor:
- consumes a valid Constitutional Root state;
- validates registry transitions;
- composes effective governance;
- derives review requirements;
- classifies governance impact/materiality;
- validates evidence-state transitions;
- validates continuity/recovery transitions;
- decides whether a requested governed transition is admissible.

The Meta-Governor cannot amend its own constitutional authority.

### L2 — Governed registries

Append-only governed registries include at minimum:
- Platform Invariant Registry;
- Policy Registry;
- Authority Issuer Registry;
- Authority Revocation Registry;
- Governance Object-Class / Dependency Registry;
- Reviewer Principal / Independence Registry;
- Evidence Transition Registry;
- Tenant/Namespace Registry;
- Recovery Authority Registry;
- Time/Sequence Source Registry;
- Authoritative History Anchor Registry.

### L3 — Effective candidate governance

For a candidate, the platform derives and freezes:
- Effective Governance Snapshot;
- review dimensions/mandatory flags;
- materiality classification;
- reviewer independence requirements;
- allowed evidence classes/transitions;
- continuity/recovery requirements;
- authority-class requirements.

### L4 — Governed action/terminal layer

Actual consequential actions require:
- exact candidate/effect identity;
- satisfied L3 rules;
- admissible evidence;
- independent review where required;
- authenticated authority issuer where required;
- use-time revocation and freshness checks;
- exact tenant/project/task/effect/action/artifact/state bindings.

No lower layer may mint higher-layer authority.

## 3. Constitutional Root and bootstrap

### R8V2-I01 — Genesis manifest

The first governed state is an immutable `ConstitutionalGenesisManifest` containing at least:
- constitution_id;
- constitutional schema version;
- root principal identities;
- root credential/public-key identities or equivalent authenticated identities;
- quorum threshold;
- recovery-authority identities and recovery quorum;
- meta-governor artifact/schema identity expected at bootstrap;
- initial registry schema identities;
- initial non-overridable invariant-set digest;
- tenant/root namespace;
- sequence = 0;
- predecessor = null;
- canonical digest.

The genesis manifest is externally anchored outside ordinary mutable project refs.

### R8V2-I02 — Bootstrap quorum

Bootstrap requires a preregistered threshold greater than one independent root principal.

A single model, assistant, project owner, policy author, reviewer, worker, or meta-governor process cannot bootstrap the root alone.

### R8V2-I03 — Bootstrap is not policy mutation

Bootstrap, constitutional amendment, root-key rotation, root replacement, and disaster recovery are distinct transition classes. They cannot be executed through ordinary policy-write authority.

### R8V2-I04 — Constitutional successor chain

Every constitutional change creates a new immutable manifest that:
- binds the exact predecessor digest;
- increments constitutional sequence exactly once;
- states the constitutional operation;
- carries the required root/recovery quorum approvals;
- preserves all prior manifests.

Constitutional history is append-only.

### R8V2-I05 — No constitutional deletion

A constitutional manifest or platform invariant lineage entry cannot be deleted from authoritative history. Retirement/supersession creates a successor state; it does not erase prior state.

## 4. Meta-governor self-amendment guard

### R8V2-I06 — Governor cannot approve its own authority change

Any change to:
- meta-governor authority predicate;
- constitutional schema;
- registry schema governing authority;
- root quorum;
- recovery quorum;
- invariant lifecycle authority;
- evidence-transition authority;
- issuer-enrollment authority

is a `CONSTITUTIONAL_AMENDMENT`.

The current Meta-Governor may validate syntax and bindings but cannot supply or substitute the required constitutional approvals.

### R8V2-I07 — Constitutional code/schema binding

A Meta-Governor instance is authoritative only when its exact implementation identity and authority-relevant schema identity are permitted by the current Constitutional Root state.

A changed implementation/schema cannot inherit authority merely because it is deployed.

### R8V2-I08 — Amendment independence

The actor proposing a constitutional amendment cannot alone satisfy the constitutional approval quorum.

Where the constitutional policy requires independent review, proposal, review, and constitutional approval identities are separately bound.

## 5. Principal and identity model

### R8V2-I09 — Stable authenticated principal

Authority-bearing actors use a stable `principal_id` bound to an authenticated credential or qualified execution identity.

Display names, model names, provider strings, email-like labels, or self-declared roles are not authority.

### R8V2-I10 — Delegation lineage

Delegated agents, aliases, service identities, and model executions carry:
- controlling/root principal identity;
- delegated principal identity;
- delegation scope;
- credential/execution identity;
- tenant scope;
- validity/revocation status.

Independence checks evaluate controlling lineage, not only surface identity.

### R8V2-I11 — Reviewer independence predicate

For each review class, effective policy defines required disjointness across applicable dimensions:
- proposer/constructor principal;
- controlling principal;
- credential;
- execution context/session;
- reviewer slot;
- provider/model class where required;
- organization/tenant relation where policy requires it.

Self-review by alias/delegation cannot satisfy independence.

## 6. Append-only registry lifecycle

### R8V2-I12 — Registry event chain

Each governed registry is event-sourced with:
- registry_id;
- tenant/root namespace;
- monotonic registry sequence;
- predecessor event digest;
- operation;
- object identity/version;
- actor principal;
- actor authorization evidence;
- policy/constitutional binding;
- canonical event digest.

No in-place authoritative edit is permitted.

### R8V2-I13 — Registry deletion forbidden

Deletion of authoritative registry history is invalid.

Objects may be:
- ACTIVE;
- SUSPENDED;
- REVOKED;
- SUPERSEDED;
- RETIRED;

but prior states remain in lineage.

### R8V2-I14 — Lifecycle authority is explicit

Each registry object type defines which authority class may:
- create;
- activate;
- suspend;
- supersede;
- retire;
- revoke;
- rotate;
- expand scope;
- reduce scope;
- migrate.

Absence of lifecycle authority means the operation is denied.

### R8V2-I15 — Registry rollback detection

A registry head with a lower sequence, wrong predecessor, unknown lineage, or previously superseded head is non-authoritative.

## 7. Platform invariant registry

### R8V2-I16 — Invariant record

Every platform invariant has:
- invariant_id;
- version;
- canonical semantic predicate/schema;
- scope;
- enforcement owner/component;
- overridable boolean;
- allowed override authority class if overridable;
- review requirements for changing it;
- lifecycle state;
- predecessor invariant version;
- constitutional binding.

### R8V2-I17 — Default non-overridable

An invariant lacking an explicit authenticated `overridable=true` state is non-overridable.

Deletion/omission does not make an invariant disappear because lineage is append-only and the current effective invariant set is derived from authoritative registry state.

### R8V2-I18 — Non-overridable amendment

Changing, retiring, or weakening a non-overridable platform invariant requires `CONSTITUTIONAL_AMENDMENT`, not project/org/policy authority.

## 8. Policy registry and deterministic composition

### R8V2-I19 — Typed policy input

Every policy rule is a typed machine-readable object, not free text as the enforcement representation.

Human-readable prose may accompany it but cannot change enforcement semantics.

### R8V2-I20 — Canonical policy representation

Canonical policy bytes use one frozen serialization profile that specifies:
- UTF-8 encoding;
- Unicode normalization;
- object-key ordering;
- number representation;
- timestamp representation;
- set/list ordering semantics;
- null/absent-field semantics;
- schema version;
- prohibited duplicate keys;
- prohibited ambiguous coercions.

The exact canonicalization profile is versioned and constitutionally bound before implementation qualification.

### R8V2-I21 — Policy scope key

Every rule carries canonical:
- tenant_id;
- organization_id if applicable;
- project_id if applicable;
- experiment/release scope if applicable;
- rule_id;
- rule version;
- governed predicate/constraint;
- priority class derived from governance level, not caller preference.

### R8V2-I22 — Same-level ordering

Same-level rules are ordered only by a frozen deterministic rule key. If two rules apply to the same predicate and cannot be safely combined under the frozen conflict ontology, composition returns `POLICY_CONFLICT`.

No last-write-wins or wall-clock-wins fallback is allowed.

### R8V2-I23 — Conflict ontology

The composition engine distinguishes at minimum:
- compatible strengthening;
- additive independent constraint;
- direct weakening;
- mutually exclusive constraint;
- cyclic dependency;
- undefined semantic relation;
- scope ambiguity;
- schema/version incompatibility.

Only explicitly defined safe combinations compose.

### R8V2-I24 — Indirect weakening protection

A lower-level rule cannot redefine terms, units, scope aliases, identity mappings, evidence classes, or predicates in a way that semantically weakens a higher-level invariant.

Governed semantic primitives used by invariants are themselves versioned and higher-layer controlled.

### R8V2-I25 — Policy rollback/migration

Rollback is not history deletion. A rollback creates a new policy event pointing to a prior rule state and is evaluated as a new material policy change.

Policy migration defines:
- source snapshot;
- target snapshot;
- migration authority;
- impacted candidates/evidence;
- revalidation requirements.

## 9. Effective Governance Snapshot

### R8V2-I26 — Snapshot authority

The Effective Governance Snapshot is produced only by the Meta-Governor from authenticated registry heads.

It includes:
- constitutional manifest identity;
- invariant registry head;
- policy registry heads;
- issuer/revocation registry heads relevant to the candidate;
- classifier/dependency registry head;
- reviewer independence registry head;
- evidence-transition registry head;
- tenant namespace identity;
- canonical composed policy;
- materiality result;
- derived review contract;
- snapshot sequence/digest.

### R8V2-I27 — Snapshot immutability

Evidence, review, authority records, checkpoints, and terminal requests bind the exact snapshot digest.

Material snapshot change makes prior evidence stale unless a frozen migration rule explicitly preserves it.

## 10. Governance object classification

### R8V2-I28 — Object-class registry

Governance-impact classification operates over an authenticated registry of governed object classes, not only paths.

Object classes include file-backed and non-file state such as:
- policy records;
- invariant records;
- registry schemas;
- issuer/revocation state;
- review requirements;
- workflow definitions;
- CI/gate definitions;
- evidence-transition rules;
- checkpoint schemas;
- recovery rules;
- tenant identity mappings.

### R8V2-I29 — Dependency metadata authority

Authority-relevant dependency metadata is generated or approved by a governed component and integrity-bound to the classifier registry version.

Caller-authored dependency metadata cannot lower classification.

### R8V2-I30 — Unknown class fails closed

A changed object with unknown authority impact yields `MATERIALITY_UNRESOLVED` / `REVIEW_REQUIRED`, not routine classification.

### R8V2-I31 — New object class is material

Adding or changing a governance object-class definition is itself a material governance transition.

## 11. Review requirement and independence

### R8V2-I32 — Review dimensions are derived

Review dimensions and mandatory flags are deterministically derived from:
- effective invariants;
- effective policy;
- object/materiality classification;
- requested transition class.

The proposer cannot omit or downgrade them.

### R8V2-I33 — Non-vacuous material review

A material review contract is invalid when:
- mandatory dimension set is empty;
- any required dimension is omitted;
- a dimension lacks its policy/invariant origin;
- artifact/snapshot binding is absent.

### R8V2-I34 — Structural reviewer isolation

A blind independent reviewer execution receives:
- a fresh execution context;
- no prior reviewer substantive outputs;
- a packet bound to exact candidate/snapshot;
- no shared conversational memory;
- no shared prompt history;
- no reviewer-to-reviewer cache containing substantive findings.

Infrastructure caches may be used only for immutable candidate/source artifacts whose content is identical and non-substantive reviewer output is excluded.

### R8V2-I35 — Reviewer evidence bounded

Reviewer assertions are evidence only.

A promotable review must satisfy the defined combination of:
- authenticated execution provenance where required;
- exact candidate/snapshot binding;
- required dimensions;
- inspectable evidence refs;
- independence predicate;
- deterministic contradiction/consistency checks.

The platform does not claim to prove unobservable internal cognition.

## 12. Authority issuer and revocation

### R8V2-I36 — Issuer enrollment

Authority issuers are enrolled through an explicit registry transition authorized by the authority class defined by the Constitutional Root or an already-qualified parent issuer hierarchy.

An issuer cannot enroll itself or expand its own scope without the required higher authority.

### R8V2-I37 — Issuer scope

Issuer records bind:
- issuer principal;
- tenant scope;
- authority classes;
- allowed action classes;
- allowed resource/project scopes;
- credential/key identities;
- validity interval/sequence;
- enrollment authority evidence;
- current status.

### R8V2-I38 — Key rotation and scope expansion

Key rotation, issuer scope expansion, revocation undo, and issuer reactivation are separate material transitions with explicit authorization requirements. They are not ordinary record edits.

### R8V2-I39 — Revocation source

Use-time revocation is read from the authoritative append-only Revocation Registry head bound to the current constitutional/tenant namespace.

For an authority-bearing action, unavailable or unverifiable revocation state fails closed.

### R8V2-I40 — PLATFORM_POLICY issuer separation

A deterministic `PLATFORM_POLICY` terminal issuer:
- is a separately enrolled issuer class;
- has exact machine-readable approval conditions;
- cannot be created/configured by a project/org policy actor alone;
- cannot authorize the actor that unilaterally created or materially configured it;
- is constitutionally or separately higher-authority governed.

Composed project/org/experiment policy is never itself a terminal authority record.

### R8V2-I41 — Authority-record anti-replay

Authority records bind:
- tenant;
- project/task/effect scope as applicable;
- issuer;
- action;
- artifact;
- authoritative state version;
- Effective Governance Snapshot;
- issue sequence;
- expiry;
- nonce/idempotency identity;
- authority-record canonical digest/signature or qualified equivalent.

## 13. Time and sequence authority

### R8V2-I42 — Ordering uses authoritative sequence

Governed event ordering uses append-only sequence/predecessor lineage rather than wall-clock ordering.

### R8V2-I43 — Absolute-time source

Expiry-dependent actions use an explicitly registered trusted time source or bounded set of sources.

Clock source identity and acceptable skew policy are part of the constitutional/effective governance state.

### R8V2-I44 — Time uncertainty fails closed

If trustworthy time cannot be established within the required skew bound, actions whose validity depends on expiry/freshness enter `TIME_AUTHORITY_UNAVAILABLE` and cannot promote/execute.

Clock rollback/forward does not rewrite event ordering.

## 14. Tenant and namespace isolation

### R8V2-I45 — Tenant namespace

Every authority-bearing identity is namespace-bound to a stable `tenant_id` generated under the Tenant Registry.

Human-readable names are aliases only.

### R8V2-I46 — Tenant lifecycle

Tenant/project/org creation, rename, alias, merge, migration, reassignment, and retirement are governed events preserving immutable stable IDs and lineage.

### R8V2-I47 — Cross-tenant denial

Policy, evidence, reviewer assignments, issuer scope, authority records, checkpoints, and registry objects from tenant A cannot authorize tenant B unless an explicit higher-level cross-tenant delegation exists and is bound to both tenant identities.

## 15. Continuity and checkpoint anchor

### R8V2-I48 — Checkpoint canonical record

An authoritative checkpoint binds:
- tenant/workstream;
- candidate identity;
- governance snapshot;
- phase;
- completed gates;
- pending gates;
- review set/status;
- authority state;
- next permitted action;
- sequence;
- predecessor checkpoint digest;
- checkpoint producer principal/component;
- canonical digest/signature or qualified integrity proof.

### R8V2-I49 — Checkpoint producer

Only an enrolled coordination/governance component authorized for the checkpoint event class may create an authoritative checkpoint.

Workers, candidates, reviewers, conversational assistants, or ordinary project policy cannot self-issue lifecycle-advancing checkpoints.

### R8V2-I50 — Checkpoint anti-replay/fork

A checkpoint is admissible only when its predecessor and sequence extend the single currently authoritative lineage.

Old valid checkpoints cannot regain authority.

Competing valid successors produce `CHECKPOINT_FORK` / `GROUNDING_REQUIRED` until governed reconciliation chooses a successor under an authorized recovery procedure.

### R8V2-I51 — Bootstrap before advisory memory

Authoritative checkpoint/history/policy is grounded before reading advisory memory as working context.

Advisory memory may never select between competing authoritative histories.

## 16. Authoritative history anchor

### R8V2-I52 — External or append-only anchor

Accepted authority-bearing milestones are anchored in an append-only history mechanism independent of movable branch refs.

The implementation qualification must define the concrete anchor and prove append-only/fork-detection behavior.

### R8V2-I53 — Ref/history substitution detection

Movement of repository refs, mirror divergence, object replacement attempt, migration, or garbage-collection effects cannot silently change previously anchored accepted history.

### R8V2-I54 — Repository migration

Repository/mirror migration is a governed transition binding old anchor, new anchor, exact object lineage, migration authority, and verification evidence.

## 17. Evidence provenance and transition authority

### R8V2-I55 — Evidence class identity

Every evidence object has:
- evidence_id;
- tenant/candidate/snapshot binding;
- evidence class;
- producer/provenance identity;
- canonical digest;
- allowed uses;
- transition history.

### R8V2-I56 — Closed transition table

The Evidence Transition Registry defines every allowed class transition, required source class, target class, transition authority, validation predicates, and resulting allowed uses.

Unlisted transition = denied.

### R8V2-I57 — Transition performed by Meta-Governor

Evidence-class upgrade requires a Meta-Governor transition decision over verified provenance and the current transition-registry rule.

Changing metadata/labels alone does not change class or authority.

### R8V2-I58 — Non-upgradable classes

Where policy declares a class non-upgradable (for example user-attested external content to platform-authenticated execution provenance), no transition rule may upgrade it without a new independently obtained evidence object from the required trusted execution path.

Telemetry success never becomes semantic review PASS.

## 18. Recovery and constitutional amendment

### R8V2-I59 — Recovery Authority Registry

Recovery actors/quorums are established by the Constitutional Root, not by project policy.

Recovery scope is explicit and narrower than constitutional amendment unless the constitutional manifest explicitly defines a root-replacement ceremony.

### R8V2-I60 — Recovery cannot weaken invariants

Recovery may restore availability, rotate credentials, reconstruct anchored state, or migrate stores, but cannot weaken or remove non-overridable invariants.

Changing a non-overridable invariant requires constitutional amendment.

### R8V2-I61 — Root replacement

Root replacement requires:
- preregistered recovery quorum;
- proof of the triggering recovery condition;
- exact predecessor constitutional manifest;
- new root identities/keys;
- independent review where constitution requires it;
- externally anchored successor manifest;
- preservation of prior root history.

No lost-root actor may self-issue its replacement.

### R8V2-I62 — Compromised-registry recovery

Recovery from issuer/policy/invariant/evidence/checkpoint registry compromise:
- freezes authority-bearing transitions;
- selects the last externally anchored valid state;
- records compromised range;
- reconstructs a successor registry lineage;
- requires the defined recovery authority;
- never silently deletes compromised/failure evidence.

### R8V2-I63 — Reviewer outage

If required reviewers are unavailable, the state is `REVIEWER_UNAVAILABLE`.

Substitution is allowed only through an already-governed reviewer substitution policy satisfying the same independence/qualification floor.

Absence of a valid substitute remains blocked; no emergency self-review.

### R8V2-I64 — Constitutional amendment

A lawful change to constitutional/non-overridable governance requires:
- amendment proposal;
- exact affected constitutional objects/invariants;
- impact analysis;
- required independent review;
- root quorum;
- successor constitutional manifest;
- migration/revalidation rules for affected candidates;
- external anchoring.

## 19. Blocked-state operations

### R8V2-I65 — Observable blocked state

`POLICY_CONFLICT`, `GROUNDING_REQUIRED`, `CHECKPOINT_FORK`, `REVIEWER_UNAVAILABLE`, `RECOVERY_REQUIRED`, `TIME_AUTHORITY_UNAVAILABLE`, `REVOCATION_UNAVAILABLE`, and constitutional/recovery blocks produce durable status and alert events.

### R8V2-I66 — Alert is not authority

Alert acknowledgement, operator UI action, or incident declaration does not itself authorize recovery or bypass.

## 20. Decision states

At minimum:
- `ALLOW_NON_AUTHORITY_WORK`
- `REVIEW_REQUIRED`
- `REVIEWER_UNAVAILABLE`
- `HUMAN_REQUIRED`
- `DENY_POLICY`
- `POLICY_CONFLICT`
- `MATERIALITY_UNRESOLVED`
- `DENY_REVIEW_CONTRACT`
- `DENY_REVIEW_INDEPENDENCE`
- `DENY_AUTHORITY_ISSUER`
- `DENY_AUTHORITY_REVOKED`
- `REVOCATION_UNAVAILABLE`
- `DENY_SCOPE_REPLAY`
- `DENY_TENANT_MISMATCH`
- `TIME_AUTHORITY_UNAVAILABLE`
- `CONTINUITY_CONFLICT`
- `CHECKPOINT_FORK`
- `GROUNDING_REQUIRED`
- `RECOVERY_REQUIRED`
- `CONSTITUTIONAL_AUTHORITY_REQUIRED`
- `TERMINAL_AUTHORITY_REQUIRED`
- `AUTHORIZED_FOR_BOUND_ACTION`

## 21. R8 v2 preregistered falsification matrix

### Constitutional/bootstrap positive and negative controls

- V2-01 valid preregistered multi-principal bootstrap produces the exact genesis manifest and first registry heads.
- V2-02 single actor attempts bootstrap -> reject.
- V2-03 meta-governor attempts to mint root authority -> reject.
- V2-04 ordinary policy actor attempts constitutional amendment -> reject.
- V2-05 valid constitutional amendment with required quorum/review produces one successor manifest.
- V2-06 amendment missing one quorum approval -> reject.
- V2-07 attempt to delete prior constitutional manifest/invariant history -> reject/detect.
- V2-08 root replacement attempted without preregistered recovery quorum -> reject.

### Registry lifecycle

- V2-09 valid authorized registry create/update/supersede path succeeds and preserves lineage.
- V2-10 registry sequence rollback -> reject.
- V2-11 wrong predecessor/forked registry update -> reject.
- V2-12 invariant deletion/omission used to evade non-overridable rule -> reject.
- V2-13 unauthorized actor retires/supersedes invariant -> reject.
- V2-14 issuer self-enrollment -> reject.
- V2-15 issuer self-scope-expansion -> reject.
- V2-16 valid higher-authority issuer enrollment succeeds.
- V2-17 unauthorized revocation undo -> reject.
- V2-18 valid key rotation preserves issuer lineage and old-key invalidation semantics.

### Policy composition and canonicalization

- V2-19 valid compatible platform+org+project policies compose to expected canonical bytes.
- V2-20 same semantic policy represented with hostile key/whitespace ordering produces same canonical bytes or is rejected per frozen profile.
- V2-21 duplicate keys / ambiguous coercion / Unicode ambiguity -> reject.
- V2-22 same-level mutually incompatible rules -> POLICY_CONFLICT.
- V2-23 cyclic policy dependency -> POLICY_CONFLICT.
- V2-24 lower-level indirect term/unit/scope redefinition weakens invariant -> reject.
- V2-25 unauthorized policy-layer write -> reject.
- V2-26 valid explicitly-overridable rule override by authorized class succeeds and is audited.
- V2-27 non-overridable invariant override -> reject.
- V2-28 rollback creates new event; history remains preserved.
- V2-29 policy migration marks impacted evidence/reviews stale as specified.

### Materiality/classification

- V2-30 valid non-material change classifies non-material.
- V2-31 caller labels material change routine -> material remains material.
- V2-32 new governance object class without registered classifier rule -> MATERIALITY_UNRESOLVED.
- V2-33 non-file registry/state change affecting authority -> material.
- V2-34 stale/attacker-authored dependency metadata attempts downgrade -> reject.
- V2-35 classifier registry rollback/omission -> reject/fail closed.
- V2-36 valid authenticated classifier-registry extension succeeds under required review.

### Review requirements and independence

- V2-37 valid material review contract derives all required dimensions with >=1 mandatory dimension.
- V2-38 zero mandatory dimensions -> reject.
- V2-39 required dimension omitted through policy/registry gap -> derivation failure, non-promotable.
- V2-40 proposer downgrades mandatory dimension -> reject.
- V2-41 exact same principal self-review -> reject.
- V2-42 alias/delegated agent/shared credential self-review -> reject.
- V2-43 valid independent reviewer assignment satisfying policy succeeds.
- V2-44 prior reviewer findings in blind context -> isolation violation.
- V2-45 shared substantive reviewer cache/memory contaminates blind context -> isolation violation.
- V2-46 reviewer claims TESTED_SUPPORTED with wrong/missing evidence ref -> non-promotable.
- V2-47 valid positive material review with correct evidence/provenance reaches review-side PASS eligibility.

### Authority issuer/revocation/time

- V2-48 self-declared HUMAN without enrolled authenticated issuer -> reject.
- V2-49 valid enrolled issuer mints exact-scope authority record -> accepted for downstream gate evaluation.
- V2-50 authority revoked after issuance before use -> reject.
- V2-51 revocation store unavailable -> REVOCATION_UNAVAILABLE / fail closed.
- V2-52 issuer attempts scope expansion without parent authority -> reject.
- V2-53 same actor configures PLATFORM_POLICY issuer then attempts to receive authorization from it where separation is required -> reject.
- V2-54 valid separately governed PLATFORM_POLICY issuer under exact conditions succeeds.
- V2-55 authority replay for new project/task/effect/action/artifact/state/snapshot -> reject.
- V2-56 trusted time unavailable for expiry-dependent authority -> TIME_AUTHORITY_UNAVAILABLE.
- V2-57 clock rollback/forward cannot reverse event ordering or extend already-expired authority.

### Tenant isolation

- V2-58 valid operation within one tenant namespace succeeds.
- V2-59 project/org alias collision across tenants -> stable IDs keep scopes distinct.
- V2-60 evidence/authority/policy from tenant A replayed in B -> reject.
- V2-61 tenant rename/migration preserves stable tenant identity and lineage.
- V2-62 unauthorized cross-tenant delegation -> reject.

### Continuity/checkpoint/history

- V2-63 valid checkpoint extends exact predecessor and resumes at correct next action.
- V2-64 checkpoint free-field tamper -> integrity failure.
- V2-65 valid old checkpoint replay -> reject/stale.
- V2-66 two valid competing successors -> CHECKPOINT_FORK.
- V2-67 advisory memory says PASS while checkpoint says review pending -> checkpoint/policy wins.
- V2-68 stale checkpoint attempts regain authority through recovery -> reject.
- V2-69 unauthorized component self-issues checkpoint -> reject.
- V2-70 authoritative repo ref rewritten after anchored milestone -> detect divergence.
- V2-71 mirror divergence -> fail closed/require governed reconciliation.
- V2-72 valid repository migration preserves anchored object lineage.
- V2-73 missing/unverifiable history anchor for authority-bearing milestone -> non-promotable.

### Evidence transitions

- V2-74 valid allowed evidence transition with authorized transition rule succeeds.
- V2-75 metadata-only class relabeling -> no authority change/reject.
- V2-76 telemetry SUCCESS -> semantic review PASS laundering attempt -> reject.
- V2-77 user-attested external review -> platform-authenticated review laundering attempt -> reject.
- V2-78 packet self-manifest with unauthenticated origin -> remains external evidence.
- V2-79 unauthorized transition actor -> reject.
- V2-80 transition-registry rollback -> reject.

### Recovery / blocked states

- V2-81 valid credential/key recovery under recovery quorum succeeds without invariant weakening.
- V2-82 lost root self-issues replacement -> reject.
- V2-83 valid root replacement ceremony creates anchored successor constitutional manifest.
- V2-84 compromised issuer registry recovery freezes authority and reconstructs from last valid anchor.
- V2-85 corrupted policy registry recovery preserves compromised history and restores valid successor lineage.
- V2-86 total reviewer outage -> REVIEWER_UNAVAILABLE, no bypass.
- V2-87 valid preregistered reviewer substitution policy selects qualified independent substitute.
- V2-88 no valid substitute -> remains blocked.
- V2-89 recovery actor attempts to weaken non-overridable invariant -> reject.
- V2-90 POLICY_CONFLICT resolution attempted without authorized policy/constitutional path -> reject.
- V2-91 valid conflict resolution creates audited successor policy state.
- V2-92 alert acknowledgement alone attempts authority transition -> reject.

## 22. Positive-control rule

For every major fail-closed subsystem, the executed falsification suite must contain a paired valid control proving that the subsystem can accept at least one valid authorized path.

At minimum positive controls are mandatory for:
- bootstrap;
- constitutional amendment;
- registry update;
- policy composition;
- materiality classification;
- material review;
- reviewer independence;
- issuer enrollment;
- authority mint/use;
- tenant isolation;
- continuity resume;
- evidence transition;
- recovery;
- repository migration.

A constant-rejection implementation cannot qualify.

## 23. Mechanism-proof rule

A falsification PASS must show that the intended load-bearing mechanism was reached.

Where material:
- injected faults require independent proof of the intended fault;
- rejection must be attributable to the intended guard rather than an earlier unrelated guard;
- positive controls must traverse the same mechanism without the adversarial condition;
- result-label comparison alone is insufficient.

## 24. Construction order

1. Freeze R8 v2 preregistration.
2. Obtain fresh blind independent design review of R8 v2 before implementation.
3. Adjudicate the review without mutating the reviewed v2 artifact.
4. Only after bounded design closure, freeze executable schemas for:
   - constitutional manifest;
   - principal/identity records;
   - registry event;
   - invariant record;
   - policy rule/canonicalization;
   - governance snapshot;
   - review contract;
   - issuer/revocation;
   - tenant namespace;
   - checkpoint;
   - evidence transition;
   - recovery event;
   - history anchor.
5. Freeze V2-01..V2-92 executable expectations before mechanism implementation wherever scientifically feasible.
6. Implement minimal deterministic mechanisms.
7. Preserve first RED evidence.
8. Run positive controls, negative attacks, mutation/self-falsification, and independent fault proof.
9. Freeze exact implementation candidate.
10. Obtain fresh independent implementation review.
11. Reconcile PR #39/#40 against qualified R8 semantics; neither is promoted automatically.

## 25. Claim boundary

A future R8 v2 bounded pass would establish only the exact tested constitutional/meta-governance mechanisms.

It would not automatically establish:
- production IAM/KMS correctness;
- cryptographic hardware custody;
- hosting-provider security;
- disaster-recovery effectiveness outside tested mechanisms;
- external reviewer truthfulness;
- global distributed consensus;
- legal/compliance sufficiency.

Until R8 v2 closes:
- R8 v1 = CHANGES_REQUIRED;
- R8 v2 = NOT_IMPLEMENTED / INDEPENDENT_REVIEW_REQUIRED;
- holistic governance = CHANGES_REQUIRED;
- PR #39 = NON_AUTHORITATIVE;
- PR #40 = NON_AUTHORITATIVE;
- authority effect = NONE.
