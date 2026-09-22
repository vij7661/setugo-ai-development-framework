# R8 v2 Meta-Governance - Blind Independent Design Review Packet

Packet status: REVIEW_ONLY / NON_AUTHORITATIVE
Authority effect: NONE

Frozen R8 v2 candidate:
- commit: `fcc6e8dbfb4133b9b9bb891cedaa1190d6e216ab`

This packet intentionally excludes prior reviewer findings and adjudications.

---

# Independent Blind Review - R8 Meta-Governance v2

Status: REVIEW_REQUIRED / DESIGN_ONLY / NON_AUTHORITATIVE

Authority effect: NONE

## Frozen subject

Primary candidate:
- R8 v2 preregistration commit: `fcc6e8dbfb4133b9b9bb891cedaa1190d6e216ab`
- file: `governance-r8/R8-META-GOVERNANCE-PREREGISTRATION-V2.md`

Do not use prior reviewer findings, prior adjudications, or prior remediation conclusions. Review v2 from scratch.

## Objective

Attempt to falsify whether R8 v2 now closes the meta-governance design sufficiently to proceed to implementation.

Assume every root, registry, issuer, recovery path, time source, tenant namespace, checkpoint, policy engine, reviewer-isolation boundary, evidence transition, and history anchor can be attacker-controlled unless the design closes ownership and lifecycle.

## Mandatory attack areas

1. Constitutional root/bootstrap:
   - genesis creation;
   - quorum independence;
   - root-key compromise/loss;
   - first-registry creation;
   - bootstrap replay;
   - root replacement.

2. Meta-governor self-amendment:
   - can the governor indirectly change its own validation predicate?
   - can a schema/registry update broaden its authority?
   - can constitutional amendment be laundered through recovery/migration?

3. Registry lifecycle:
   - deletion, omission, rollback, fork, retirement, supersession;
   - issuer self-enrollment/scope expansion;
   - revocation undo;
   - classifier registry manipulation.

4. Policy canonicalization/composition:
   - parser ambiguity;
   - Unicode/number/list ordering;
   - semantic redefinition;
   - same-level conflicts;
   - cycles;
   - rollback/migration;
   - hostile but canonical inputs.

5. Reviewer identity/isolation:
   - aliases, delegated agents, shared credentials;
   - same controller behind different reviewer identities;
   - shared caches/memory/history;
   - packet contamination;
   - provider/model indirection.

6. Materiality:
   - new object classes;
   - non-file authority changes;
   - stale dependency metadata;
   - unknown authority-bearing changes;
   - classifier-registry rollback.

7. Authority issuer/revocation:
   - root of issuer enrollment;
   - key rotation;
   - scope expansion;
   - revocation unavailability;
   - PLATFORM_POLICY self-grant;
   - replay and stale authority.

8. Time/sequence:
   - skew, rollback, forward jump;
   - source outage;
   - sequence fork;
   - expiry/revocation race.

9. Tenant isolation:
   - ID collision/alias/rename/migration/reassignment;
   - cross-tenant issuer scope;
   - cross-tenant evidence/policy/reviewer replay.

10. Continuity/history:
   - old checkpoint replay;
   - checkpoint fork;
   - recovery selecting stale history;
   - repository ref rewrite;
   - mirror divergence;
   - repository migration;
   - external anchor loss.

11. Evidence transitions:
   - metadata-only relabeling;
   - transition-registry manipulation;
   - telemetry/review/packet laundering;
   - provenance downgrade/upgrade.

12. Recovery:
   - compromised root/registry;
   - malicious recovery quorum;
   - root replacement;
   - reviewer outage;
   - recovery deadlock;
   - emergency amendment abuse.

13. Positive controls:
   - determine whether a constant-reject implementation can still pass;
   - verify every load-bearing deny path has a valid allowed-path control.

14. Mechanism proof:
   - identify tests that could pass without exercising the claimed guard;
   - identify faults that need independent proof;
   - identify cases where an earlier guard could mask the intended guard.

15. Over-governance:
   - permanent deadlocks;
   - impossible constitutional amendment;
   - unrecoverable root loss;
   - reviewer starvation;
   - policy conflicts that cannot lawfully resolve.

## Reviewer constraints

- Design review only; do not claim implementation/runtime verification.
- Do not grant qualification, implementation approval, merge, release, deploy, production, policy, or terminal authority.
- PR #39/#40 context remains non-authoritative.
- Do not assume a named component is trustworthy from its label.
- Prefer concrete false-green/self-grant paths.
- A design requirement phrased with MUST is not itself enforcement.
- Distinguish missing design semantics from implementation choices that may be safely deferred.

## Required output

A. Overall disposition: BOUNDED_PASS, CHANGES_REQUIRED, or INSUFFICIENT_EVIDENCE.

B. Critical findings.

C. High findings.

D. Medium findings.

E. Constitutional/root-of-trust assessment.

F. Meta-governor self-amendment assessment.

G. Registry lifecycle and issuer/revocation assessment.

H. Policy composition/canonicalization assessment.

I. Reviewer independence/materiality assessment.

J. Time/tenant/continuity/history assessment.

K. Evidence-transition/recovery assessment.

L. Falsification-matrix assessment, including missing positive controls and mechanism-proof gaps.

M. Over-governance/deadlock assessment.

N. Minimal required changes before implementation.

O. Final bounded statement confirming:
- review grants no authority;
- R8 v2 remains NOT_IMPLEMENTED;
- PR #39/#40 remain non-authoritative;
- unresolved material design findings block implementation start.


---

# Included sources


---

## PRIMARY_R8_V2: governance-r8/R8-META-GOVERNANCE-PREREGISTRATION-V2.md

Ref: fcc6e8dbfb4133b9b9bb891cedaa1190d6e216ab
Git blob SHA: b0b1d240045e9c97d7a2659f7bc856f90ceda759

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



---

## AUTHORITATIVE: governance-runtime/LIVE-CONVERSATION-GOVERNANCE.md

Ref: 87f6e3df73c0c70c5d8ff4da38365ff92721aff7
Git blob SHA: cdba052b3baaa7250b6787bf6954ccfb5059e832

# Live Conversation Governance Runtime

## Purpose

Apply governed-platform rules to the human–LLM development conversation so chat-window changes, model confidence, shared-memory drift, reviewer substitution, reviewer self-identification, review-delivery mode, pasted content, packet representation, or reviewer-disposition overclaim cannot silently change authoritative project state.

This is an operational control for our collaboration. It does not claim that the ChatGPT product itself enforces these rules internally.

## Authority precedence

1. Governed Git/evidence bound to exact revisions.
2. Governed registries/checkpoints referenced by Git.
3. Governed shared project memory as active continuity/coordination whose material pointers must resolve to authority.
4. Current project chats/files as working context.
5. Ungoverned summaries/caches as advisory navigation.
6. Model recollection/confidence has no authority.

Shared memory is actively read and written, but never independently authoritative. Conflict is surfaced; authoritative state wins; memory is repaired rather than silently merged.

## Session bootstrap

Before authoritative continuation in a fresh chat/session:

1. Read `governance-runtime/shared-memory.json`.
2. Read `governance-runtime/session-state.json`.
3. Verify referenced branches, commits, review requests/evidence, and frozen artifacts.
4. Read applicable governed standards.
5. Reconcile memory/chat context with authority.
6. If authority cannot be verified, enter `GROUNDING_REQUIRED`.

A chat boundary may not change claim status, experiment state, review state, revision identity, evidence validity, promotion eligibility, or terminal authority.

## Review levels and platform modes

Review requirement and interaction mode are independent dimensions.

### Review levels

- `NONE` — no review requested for non-authoritative/routine work.
- `RECOMMENDED` — R1 may recommend review for non-mandatory work.
- `REQUIRED` — protected authority transition cannot promote without valid independent review.

R1 may raise `NONE` to `RECOMMENDED`; R1 may not lower a protected transition to optional merely by changing a trigger label.

### `AUTO_MODE`

When review is recommended/required, the platform dispatches the configured provider API automatically via `AUTOMATIC_API`. A successful authenticated execution is classified `PLATFORM_AUTO_API_REVIEW`.

### `MANUAL_MODE`

R1 shows its answer first. When review is recommended/required, the UI shows controls such as `Ask Claude` / `Ask DeepSeek`. A user click dispatches the configured provider API through `USER_INITIATED_API`. A successful authenticated execution is classified `PLATFORM_USER_INITIATED_API_REVIEW`.

For `RECOMMENDED`, the user may skip review. For `REQUIRED`, the user may decline the call, but the protected authoritative transition remains pending/non-authoritative.

Changing AUTO ↔ MANUAL changes **who initiates the provider API call only**. It never changes evidence, identity, independence, semantic review, or promotion rules.

## Review execution classes

There are exactly two platform review execution classes:

1. `PLATFORM_AUTO_API_REVIEW` — `AUTO_MODE` + `AUTOMATIC_API`.
2. `PLATFORM_USER_INITIATED_API_REVIEW` — `MANUAL_MODE` user action + `USER_INITIATED_API`.

Both use trusted provider adapters and the same ReviewRequest, semantic coverage, identity, independence, fail-closed, and promotion semantics. Neither class derives reviewer provenance from reviewer-authored content.

Copy/paste is **not** a platform review transport.

## External evidence ingestion

User-pasted/copied material enters a separate evidence family.

### `USER_PROVIDED_EXTERNAL_CONTENT`

This is the default class for pasted review-shaped content when the user has not explicitly identified its source.

- no provider/model origin is inferred from the payload;
- fields such as `reviewer.provider` / `reviewer.model` are self-declared content claims only;
- the content may expose defects or provide useful technical evidence;
- it is not a platform review execution and cannot satisfy a mandatory platform review gate.

### `USER_ATTESTED_EXTERNAL_LLM_REVIEW`

Only after the user explicitly identifies pasted material as a review from an external LLM may it be reclassified to this class.

- user attestation records the reported provider/model source;
- user attestation is **not** provider-API authentication;
- self-declared payload identity must never create or upgrade provenance;
- the content remains external evidence and is non-promotable by itself.

Core rule: **content cannot establish its own provenance**.

Historical `MANUAL_RELAY` artifacts remain readable and preserved, but `MANUAL_RELAY` is no longer a platform review transport. Legacy manual-relay results are external evidence/history only.

## Material authority review floor

`can_promote_material_transition` is the authority boundary. Material promotion is **review-required by definition**, regardless of the caller-supplied `trigger` string.

The UI/orchestration classifier additionally fails closed for:

- known mandatory-review triggers;
- explicit material transitions;
- governing-standard review requirements;
- governance-relevant paths including `governance-runtime/`, `standards/`, `experiments/governed-platform/`, and `.github/workflows/`.

A proposer mislabel such as `ROUTINE_FORMATTING` cannot waive review at the material promotion gate.

## ReviewRequest and current-state binding

A mandatory platform review is represented by an integrity-bound `ReviewRequest` containing at least:

- request identity;
- exact reviewed artifact commit;
- proposer provider/model;
- required reviewer provider plus model/model-class constraint;
- blind-review requirement;
- review questions;
- evidence references;
- material/standard/path classification context.

For material promotion, the runtime additionally requires a semantic review contract (ReviewRequest schema 4+) containing machine-readable `required_review_dimensions`. A legacy review request without this semantic contract may be preserved as historical content but cannot authorize material promotion.

Promotion must bind review evidence to the currently authoritative review request and current reviewed artifact. A review for a superseded request or older revision cannot be replayed into a later candidate.

## Semantic review coverage and disposition consistency

A reviewer conclusion is not valid merely because its `disposition` token is syntactically allowed.

Every schema-4 material ReviewRequest defines explicit review dimensions with:

- stable dimension ID;
- `mandatory` boolean;
- description;
- governed closed coverage-status vocabulary.

ReviewEvidence must provide one `review_coverage` entry for every dimension, containing:

- `dimension_id`;
- status;
- concrete evidence references/observations where the dimension was tested;
- a non-empty assessment of what was actually examined.

Allowed dimension statuses are:

- `TESTED_SUPPORTED`
- `TESTED_DEFECT_FOUND`
- `CONTRADICTED`
- `NOT_TESTED`
- `UNAVAILABLE`
- `INACCESSIBLE`
- `INSUFFICIENT`

Semantic disposition rules are deterministic:

- `PASS` requires every listed review dimension to be `TESTED_SUPPORTED`, with non-empty evidence for each.
- `BOUNDED_PASS` requires every `mandatory: true` dimension to be `TESTED_SUPPORTED`; only explicitly non-mandatory dimensions may remain bounded.
- `NOT_TESTED` / `INSUFFICIENT_EVIDENCE` are correct when one or more mandatory dimensions are unavailable, inaccessible, not tested, or insufficient.
- `FAIL` / `CHANGES_REQUIRED` require at least one concrete finding and a contradicted, defective, or insufficient coverage state.
- negative review outcomes can be valid review evidence but are not promotable.
- only semantically valid `PASS` or `BOUNDED_PASS` may satisfy the review side of material promotion.

Free-text `evidence_assessment` explains structured coverage but cannot substitute for it. If free text contradicts an asserted `PASS`, the review fails closed. `REV-GOV-PR5-008` is a permanent regression fixture for this failure family.

## Reviewer identity provenance

Reviewer-authored JSON fields such as:

```json
{"reviewer":{"provider":"anthropic","model":"claude-..."}}
```

are content claims, **not authentication**.

`AUTOMATIC_API` and `USER_INITIATED_API` derive provider/model identity from the trusted configured provider adapter/execution envelope. Review content must agree with that trusted identity; disagreement fails closed.

Pasted external evidence has no platform-authenticated provider identity. If the user explicitly identifies the external source, that creates user-attested provenance only.

## Review execution to promotion wiring

Material promotion consumes all of these directly:

1. deterministic gate result;
2. authoritative checkpoint;
3. grounded shared memory;
4. current schema-4 ReviewRequest with required dimensions;
5. ReviewEvidence with complete semantic coverage;
6. a trusted platform API execution/provenance envelope whose review class matches its API transport.

No caller-provided boolean such as `valid_independent_review_present=True`, no pasted JSON, and no user-attested external review can mint review validity.

Review fails closed when execution is missing, pending, errored, non-platform transport, wrong request, wrong revision, unauthenticated, wrong provider/model, self-review, malformed, non-blind when blind review is required, semantically inconsistent, negative/non-promotable, or conflicts with its trusted execution identity.

Consensus is metadata, not evidence, and cannot bypass deterministic evidence gates.

## Shared-memory grounding

Before material promotion, shared memory must reconcile with authoritative checkpoint state for at least:

- active workstream branch;
- exact workstream head;
- workstream status;
- current review request;
- current review status;
- pending review coordination.

Stale/conflicted memory blocks material promotion until reconciled.

Authoritative persistence occurs before memory synchronization. If memory synchronization later fails, authority remains valid and memory is marked stale. If authoritative persistence fails, authoritative completion is blocked.

## Portable external review/evidence export

A portable packet may still be generated for advisory external review/evidence work when the external model has zero repository/browser/tool access. That export is an **external evidence transport artifact**, not a platform review execution and not a substitute for `AUTOMATIC_API` or `USER_INITIATED_API`.

A portable export should contain:

- exact ReviewRequest or review context;
- exact reviewed candidate identity;
- explicit review dimensions;
- detached manifest;
- human-readable packet;
- raw canonical repository artifacts where required;
- per-artifact SHA-256 and exact byte length over raw Git blob UTF-8 bytes;
- evidence-reference coverage;
- CI/builder evidence;
- whole-packet/logical hashes;
- `repository_access_required: false`.

Raw files are byte-authoritative. Markdown fences are convenience only. If an external reviewer cannot inspect a mandatory dimension, its external result must not claim that dimension was tested.

Portable-packet integrity makes external evidence more useful; it does **not** upgrade external evidence into a platform-authenticated review.

## Frozen evidence and repair discipline

For falsification/acceptance work:

1. preregister/freeze where required before exposure;
2. preserve first exposure;
3. classify before repair;
4. never change frozen tests/fixtures/expectations merely to get green;
5. changes to frozen artifacts after exposure require a new governed boundary and independent review;
6. preserve superseded/invalid attempts and correction history;
7. construction green is not scientific acceptance when a later frozen acceptance run is required.

## Failure taxonomy

At minimum preserve/surface:

- `MEMORY_OVERRIDES_AUTHORITY`
- `SHARED_MEMORY_STALE_UNDETECTED`
- `SHARED_MEMORY_CONFLICT_SILENTLY_MERGED`
- `MODEL_CONFIDENCE_BYPASSED_REVIEW`
- `PROPOSER_CONTROLLED_REVIEW_CLASSIFICATION`
- `MANDATORY_REVIEW_SKIPPED`
- `REVIEWER_IDENTITY_SELF_ATTESTATION_ACCEPTED`
- `EXTERNAL_CONTENT_SELF_PROVENANCE_ACCEPTED`
- `USER_ATTESTATION_TREATED_AS_PROVIDER_AUTHENTICATION`
- `EXTERNAL_EVIDENCE_TREATED_AS_PLATFORM_REVIEW`
- `REVIEW_INDEPENDENCE_UNPROVEN`
- `REVIEW_WRONG_REVISION_ACCEPTED`
- `SUPERSEDED_REVIEW_REPLAY_ACCEPTED`
- `REVIEW_TRANSPORT_CHANGED_POLICY`
- `PLATFORM_MODE_CHANGED_AUTHORITY`
- `API_FAILURE_TREATED_AS_APPROVAL`
- `REVIEW_ID_SEMANTIC_REBIND`
- `CONSENSUS_AS_EVIDENCE`
- `REVIEW_DISPOSITION_EVIDENCE_CONTRADICTION`
- `REVIEW_REQUIRED_DIMENSION_OMITTED`
- `REVIEW_PASS_WITH_UNTESTED_MANDATORY_DIMENSION`
- `NEGATIVE_REVIEW_TREATED_AS_PROMOTABLE`
- `LEGACY_REVIEW_SCHEMA_PROMOTED`
- `PORTABLE_REVIEW_BUNDLE_TAMPERED`
- `PORTABLE_REVIEW_MANIFEST_MISMATCH`
- `PORTABLE_REVIEW_RAW_HASH_UNREPRODUCIBLE`
- `FAILURE_HISTORY_REWRITTEN`
- `TERMINAL_AUTHORITY_SELF_GRANTED`

## Live operating procedure

1. Recover shared memory.
2. Verify against authoritative Git/evidence.
3. Reconcile stale/conflicting memory.
4. Classify work/review level.
5. Preregister/freeze when applicable.
6. Execute narrow construction.
7. Preserve first failures/revisions.
8. Apply platform review policy.
9. In AUTO_MODE, dispatch `AUTOMATIC_API`; in MANUAL_MODE, show reviewer controls and dispatch `USER_INITIATED_API` only after user selection.
10. Treat copy/paste as external evidence ingestion, initially `USER_PROVIDED_EXTERNAL_CONTENT`.
11. Reclassify pasted content to `USER_ATTESTED_EXTERNAL_LLM_REVIEW` only when the user explicitly identifies the source; never equate that attestation with API authentication.
12. Bind platform reviewer identity from trusted execution provenance.
13. Validate ReviewRequest + ReviewEvidence + structured semantic coverage + platform API execution envelope.
14. Require a positive promotable disposition before platform review can satisfy material promotion.
15. Apply deterministic governor/evidence gate.
16. Persist authoritative checkpoint.
17. Synchronize shared memory.
18. New chat resumes from shared memory then verifies Git.

## Current collaboration limitation

This chat can ingest pasted external evidence, but pasted content is not a platform review execution. Therefore it cannot satisfy a mandatory provider-authenticated PR #5 review gate. In the production platform, both AUTO_MODE and MANUAL_MODE avoid this limitation by using trusted provider API adapters (`AUTOMATIC_API` / `USER_INITIATED_API`).



---

## AUTHORITATIVE: governance-runtime/EXECUTION-HANDOFF-PROTOCOL.md

Ref: 87f6e3df73c0c70c5d8ff4da38365ff92721aff7
Git blob SHA: 51b514c15a51528242f0c15f7c3f2d47142dcebb

# Deterministic Execution Handoff Protocol

## Problem

Conversation summaries, model memory, repository HEAD, and the last durable commit can each describe different points in a live workflow. A new chat can therefore resume from a historically valid but operationally stale point. Repository truth alone is insufficient when the last completed action and the next required action are not represented explicitly.

## Core rule

A material workflow may not rely on conversational recollection to determine where execution resumes.

The authoritative live checkpoint MUST contain an explicit `execution_handoff` object. A fresh or resumed session MUST execute from `execution_handoff.next_required_action` only after verifying its bindings against governed Git/evidence. It MUST NOT infer a different frontier from chat summaries, model memory, commit recency, or a plausible project narrative.

## Required handoff fields

The checkpoint handoff records at least:

- monotonic `sequence`;
- `workstream` identity;
- exact `candidate_branch`;
- exact `candidate_commit`;
- `phase`;
- `last_completed_action`;
- `next_required_action`;
- `stop_condition`;
- `manual_input_required`;
- `handoff_reason`;
- `historical_failure_preserved`;
- `resume_rule`.

The shared continuity memory mirrors these fields but remains non-authoritative. Any mismatch is a grounding failure, not an invitation to guess.

## Write discipline

1. Persist the material authoritative change first.
2. Verify the resulting authoritative revision/evidence.
3. Update `session-state.json` with a new monotonic handoff sequence bound to the exact current workstream candidate.
4. Update `shared-memory.json` to mirror the handoff.
5. Run deterministic validation.
6. Only then may the assistant report the new execution frontier as durable.

If step 1 fails, authoritative completion is blocked. If steps 3-5 fail after the material change has already become durable, the material authority remains what Git says, but the conversation state is `GROUNDING_REQUIRED` until the handoff is repaired. The assistant must not claim the handoff was saved when it was not.

## Resume discipline

At session/chat start:

1. Read `session-state.json`.
2. Read the authoritative handoff.
3. Verify `candidate_branch` currently resolves to `candidate_commit` when the handoff requires an unmoved candidate.
4. Verify any referenced workflow/review/evidence state.
5. Compare shared memory and current chat context to the authoritative handoff.
6. If they disagree, authoritative handoff wins and the discrepancy is surfaced/repaired.
7. Execute `next_required_action`; do not substitute a nearby task.

A generic user message such as `continue` means `continue from the verified execution_handoff.next_required_action`.

## Manual/review boundary rule

When `stop_condition` is `INDEPENDENT_REVIEW_REQUIRED` or another explicit manual boundary:

- no further authority-changing construction may continue;
- the assistant must provide the exact reviewer prompt and review packet/artifact required for that boundary in the same handoff interaction;
- the checkpoint must identify the exact candidate under review;
- after the reviewer response is received, that response is ingested according to its provenance class and the handoff advances monotonically.

The handoff must not merely say `review required`; it must specify the next operational deliverable so the user is not forced to reconstruct the protocol from prior chat history.

## Failure classes

- `HANDOFF_MISSING`
- `HANDOFF_STALE`
- `HANDOFF_CANDIDATE_MISMATCH`
- `HANDOFF_SEQUENCE_REGRESSION`
- `HANDOFF_NEXT_ACTION_AMBIGUOUS`
- `HANDOFF_MANUAL_DELIVERABLE_OMITTED`
- `CHAT_RESUME_OVERRIDES_HANDOFF`
- `MODEL_MEMORY_OVERRIDES_HANDOFF`
- `REPOSITORY_HEAD_MISTAKEN_FOR_EXECUTION_FRONTIER`
- `FALSE_HANDOFF_PERSISTENCE_ACKNOWLEDGEMENT`

## Current incident classification

The September 2026 continuation failures in which the assistant resumed from EXP-I/EXP-K or from repository HEAD while the live workflow had already advanced to Review Engine closure and then Slice 3 are classified as a real `REPOSITORY_HEAD_MISTAKEN_FOR_EXECUTION_FRONTIER` / `HANDOFF_STALE` failure family. They are preserved as governance evidence rather than treated as a conversational inconvenience.



---

## AUTHORITATIVE: experiments/governed-platform/INTEGRATED_GOVERNED_MVP_SLICE6_TERMINAL_AUTHORITY_GATE_CONTRACT.md

Ref: 87f6e3df73c0c70c5d8ff4da38365ff92721aff7
Git blob SHA: 3d9572cbae5e669bc4883727cc298c13e279ad18

# Integrated Governed MVP — Slice 6 Terminal Authority / Release-Completion Gate Contract

Status: **FROZEN BOUNDARY — AMENDED BY AUTHORITATIVE REQUIREMENT DECISION A**

Parent authoritative integration commit: `f67e0dfb4fe9b4bb67c76dbd43f1485861c96fc0` (accepted Slice 5 authoritative state ledger).

Amendment basis: deterministic review-of-review of `REV-MVP-SLICE6-TERMINAL-AUTHORITY-004` exposed an internal contradiction between the original broad wording of S6-I05 and the already-frozen per-input schemas. The authoritative decision is to preserve those schemas and narrow S6-I05 accordingly. No implementation field expansion is authorized by this amendment.

## 1. Goal

Falsify whether the integrated governed MVP can add the separate external terminal-authority boundary already required by the accepted composition contract without allowing model/worker claims, stale review evidence, stale artifact identity, replay, action substitution, or prior green CI to mint RELEASE / DEPLOY / MERGE / completion authority.

This slice produces a deterministic **terminal authorization receipt** only. It does not perform a remote push, merge, release, deployment, production mutation, or production completion action.

## 2. Required input lineage

A terminal decision consumes explicit bound inputs only:

1. `terminal_request`
   - `project_id`
   - `task_id`
   - `action` — one of `RELEASE`, `DEPLOY`, `MERGE`, `COMPLETE`
   - `effect_id`
   - `artifact_sha`
   - `expected_state_version`
2. `execution_evidence`
   - exact project/task/effect lineage
   - exact resulting artifact SHA
   - successful prior isolated execution state
   - `terminal_authority == false`
   - `release_completion_authority == false`
   - deterministic evidence hash
3. `review_gate`
   - `state == CLEAR`
   - immutable/frozen `evidence_refs`
   - exact reviewed `artifact_sha`
   - exact reviewed `action`
4. `authority_record`
   - `authority_id`
   - `source_class` — `HUMAN` or `PLATFORM_POLICY`
   - `decision` — `APPROVE` or `DENY`
   - exact project/task/effect/action/artifact binding
   - exact `state_version`
   - `issued_at_epoch`
   - `expires_at_epoch`
   - immutable/frozen `evidence_refs`
   - deterministic `authority_record_hash`
5. `current_state`
   - exact `project_id`
   - exact current authoritative `state_version`
6. explicit `now_epoch`

No ambient conversation history, provider/model label, worker assertion, prior workflow status, or stale CI result is authority.

## 3. Frozen authority invariants

**S6-I01 Separate terminal authority** — prior isolated execution success never implies terminal authority.

**S6-I02 External source class** — `MODEL`, `WORKER`, `RESEARCHER`, `JUDGE`, or any unrecognized source class cannot authorize terminal action. Only structurally valid `HUMAN` or `PLATFORM_POLICY` authority records may proceed in this bounded reference mechanism.

**S6-I03 Exact action binding** — approval for one terminal action cannot authorize another action.

**S6-I04 Exact artifact binding** — approval/review for one artifact SHA cannot authorize a different artifact SHA or a changed branch head.

**S6-I05 Scoped exact lineage binding** — bindings are enforced according to each frozen input schema, without inferring absent fields: `terminal_request`, `execution_evidence`, and `authority_record` must share exact project/task/effect/artifact lineage; `review_gate` must bind the exact terminal action and artifact SHA with immutable evidence references; `current_state` must bind the exact project ID and authoritative state version. No task/effect/artifact fields are required in `current_state`, and no project/task/effect fields are required in `review_gate` unless a later separately approved contract explicitly changes those schemas.

**S6-I06 Current authoritative version** — request `expected_state_version` must equal current authoritative `state_version`; stale/future versions fail closed.

**S6-I07 Review required** — terminal authorization requires a well-formed `CLEAR` review gate bound to the exact action and artifact. `REVIEW_REQUIRED`, `HUMAN_REQUIRED`, malformed, missing, or stale review evidence cannot authorize.

**S6-I08 Explicit approval** — only `decision == APPROVE` can authorize. `DENY`, missing, malformed, or contradictory decisions fail closed.

**S6-I09 Time validity** — authority record must be issued no later than `now_epoch` and must not be expired.

**S6-I10 Deterministic authority-record integrity** — the supplied authority-record hash must match canonical deterministic content. Tampering fails closed.

**S6-I11 Evidence integrity** — execution evidence must be self-consistent, deterministically hashed, and explicitly non-terminal in its own authority fields.

**S6-I12 No success laundering** — green CI, model success, reviewer/model agreement, isolated execution success, or repository mutation success cannot substitute for the terminal authority record.

**S6-I13 Idempotent decision** — identical bound inputs produce the same terminal decision receipt and digest.

**S6-I14 Rebinding rejection** — reusing an authority identity/hash for a changed action, artifact, lineage, or state version cannot authorize.

**S6-I15 Receipt is not side effect** — `AUTHORIZED_FOR_TERMINAL_ACTION` means a separately controlled terminal executor may be invoked for the exact bound action; it is not proof that the action occurred.

**S6-I16 Source authentication nonclaim** — this reference validates structure, binding, freshness, and deterministic integrity only. It does not prove cryptographic human identity, production IAM, signature authenticity, KMS custody, or organizational authorization policy.

## 4. Frozen decision states

- `DENY_REQUEST`
- `DENY_EXECUTION_EVIDENCE`
- `DENY_REVIEW_GATE`
- `DENY_AUTHORITY_SOURCE`
- `DENY_AUTHORITY_RECORD`
- `DENY_STATE_VERSION`
- `DENY_EXPIRED_AUTHORITY`
- `TERMINAL_ACTION_DENIED`
- `AUTHORIZED_FOR_TERMINAL_ACTION`

Every decision must include:

- `authorized`
- `terminal_authority`
- `release_completion_authority`
- exact bound lineage
- deterministic `receipt_hash`
- reason

Only `AUTHORIZED_FOR_TERMINAL_ACTION` may set `authorized`, `terminal_authority`, and `release_completion_authority` true.

## 5. Frozen acceptance cases

- `S6-01` exact valid RELEASE approval reaches `AUTHORIZED_FOR_TERMINAL_ACTION`.
- `S6-02` valid MERGE approval reaches authorization only for MERGE.
- `S6-03` valid DEPLOY approval reaches authorization only for DEPLOY.
- `S6-04` valid COMPLETE approval reaches authorization only for COMPLETE.
- `S6-05` prior isolated execution success without authority record is denied.
- `S6-06` model/worker authority source is denied.
- `S6-07` action substitution is denied.
- `S6-08` artifact SHA substitution / moved head is denied.
- `S6-09` project/task/effect lineage mismatch is denied where those fields are present in the frozen input schema.
- `S6-10` stale expected authoritative state version is denied.
- `S6-11` future expected authoritative state version is denied.
- `S6-12` `REVIEW_REQUIRED` cannot authorize.
- `S6-13` `HUMAN_REQUIRED` cannot authorize.
- `S6-14` malformed review gate cannot authorize.
- `S6-15` explicit authority `DENY` returns `TERMINAL_ACTION_DENIED`.
- `S6-16` expired authority is denied.
- `S6-17` future-issued authority is denied.
- `S6-18` tampered authority record hash is denied.
- `S6-19` malformed/tampered execution evidence is denied.
- `S6-20` execution evidence attempting terminal authority is denied.
- `S6-21` identical replay returns identical decision body and receipt hash.
- `S6-22` green-CI/model-success fields in auxiliary evidence cannot authorize without valid authority record.
- `S6-23` authority identity/hash cannot be rebound to a changed artifact/action/state version and remain valid.
- `S6-24` authorized receipt contains no claim that merge/deploy/release/completion actually occurred.
- `S6-25` Option-A schema preservation: a valid authorization succeeds with `review_gate` containing only its frozen action/artifact/evidence fields and `current_state` containing only project/state-version fields; absent non-schema task/effect/artifact fields must not be invented or required.

## 6. Acceptance criteria

A bounded Slice 6 pass requires all `S6-01..S6-25` deterministic tests to pass on one exact candidate SHA and the accepted Slice 1→Slice 5 regression chain to remain green.

Independent integration review remains mandatory before promotion into `main`.

## 7. Forbidden shortcuts

- do not turn green CI into terminal authority;
- do not treat model/reviewer consensus as authority;
- do not accept moved artifact/head identity after review;
- do not widen approval from one terminal action to another;
- do not accept stale/future authoritative state versions;
- do not weaken review requirements to obtain a pass;
- do not infer human identity from a string label;
- do not claim the terminal action occurred merely because the gate authorized it;
- do not invent or require fields outside the frozen per-input schemas to satisfy an over-broad interpretation of lineage;
- do not modify accepted Slice 1→Slice 5 behavior to accommodate this slice.

## 8. Claim boundary

A bounded pass proves only a deterministic reference terminal-authorization gate with scoped per-input action/artifact/lineage/state-version binding, explicit external approval input, review-gate dependency, freshness checks, and model/worker non-authority. It does not prove production identity authentication, cryptographic signatures, IAM/KMS correctness, remote side-effect safety, deployment safety, or organizational release policy correctness.

## 9. Preserved contradiction and decision history

The original S6-I05 wording remains part of repository history and is not rewritten retroactively. `REV-MVP-SLICE6-TERMINAL-AUTHORITY-004` returned semantic PASS but deterministic adjudication classified the contract contradiction as `REQUIREMENT_UNRESOLVED_CONTRACT_INTERNAL_CONTRADICTION` with authority effect `NONE`. The authoritative requirement decision selected Option A: preserve the frozen input schemas and narrow S6-I05 to those per-object bindings. All earlier review outcomes, provider failures, defect exposure, and repair commits remain historical evidence and do not authorize promotion of this amended candidate.



---

## PROPOSED_PR39: standards/conversation-continuity-and-resumption-control.md

Ref: 1029e8a7883abc30975a6bff908f43cf9192dab5
Git blob SHA: 0e5af4b42e39c3a751c13e1b5b162643b45effec

# Conversation Continuity and Resumption Control

Status: **PROPOSED — REVIEW REQUIRED — NON-AUTHORITATIVE**

Authority effect: **NONE_EVIDENCE_ONLY**

Purpose: prevent chat interruption, device switching, context truncation, conversation rollover, model/session changes, or stale conversational state from silently changing governed workflow state or skipping required gates.

## 1. Core invariant

A conversation is an interface, not the authoritative workflow state.

No chat/session/device boundary may itself create, advance, reset, approve, qualify, adjudicate, merge, release, or otherwise authorize a governed state transition.

## 2. Development-time continuity source

While the governed platform itself is still being built, durable project continuity must be recovered from repository-backed evidence and frozen artifacts rather than conversational inference alone.

Before consequential project work resumes after an interruption, the operator/assistant must recover enough durable state to determine:

- current governed phase;
- exact candidate/artifact identity and commit SHA or digest where applicable;
- completed required steps;
- pending required steps;
- reviewer/test/adjudication status;
- current authority effect;
- unresolved findings or stale conditions;
- exact next permitted action.

Repository evidence is a development-time continuity anchor. It is not automatically runtime governance authority.

## 3. Production-time continuity source

In the implemented platform, authoritative resumption state must come from the platform coordination backend plus append-only evidence/governance ledger, not from ChatGPT memory, a conversation transcript, or GitHub UI state.

GitHub may remain a development/reference/mirror adapter but must not become the sole runtime continuity authority.

## 4. Resume-from-checkpoint rule

After any interruption, governed work must resume from the latest valid durable checkpoint whose bindings can be verified.

A checkpoint must bind, as applicable:

- project/workflow identifier;
- phase;
- task/candidate identifier;
- exact commit SHA/artifact digest;
- policy/schema version;
- required reviewer/test set;
- completed evidence references;
- pending evidence requirements;
- authority state;
- next permitted transition/action;
- checkpoint timestamp/sequence;
- predecessor checkpoint/event digest when ledger-backed.

Conversational recollection may help locate the checkpoint but may not override contradictory durable evidence.

## 5. Timestamp recovery rule

If work stops abruptly, recover the latest valid durable event/checkpoint by authoritative sequence first and timestamp second.

Wall-clock recency alone must not override a linearly ordered ledger sequence. In development workflows without a platform ledger, Git commit/order plus explicitly recorded project checkpoint evidence should be preferred over conversational recency.

Incomplete assistant reasoning, proposed next steps, unsent edits, or interrupted tool plans do not become authoritative merely because they occurred later in a chat.

## 6. No stage skipping

Resumption must preserve all prerequisite barriers.

Examples:

- `REVIEW_1_COMPLETE / REVIEW_2_PENDING / REVIEW_3_PENDING` may not resume at adjudication.
- `ALL_REQUIRED_REVIEWS_FROZEN` may resume at adjudication only if the exact candidate binding still matches.
- a failed or stale validation may not resume as qualified.
- a pending adjudication may not resume at repair/merge/release.

For multi-review workflows, the default barrier is:

`ALL_REQUIRED_REVIEWS_FROZEN -> ADJUDICATION -> REPAIR/DECISION`

Receipt of any subset of required reviews must not trigger candidate modification unless the governing policy explicitly permits iterative review and invalidates/restarts the affected review set.

## 7. Exact-artifact binding

Reviews, tests, validations, adjudications, and approvals survive an interruption only for the exact artifact/revision to which they were bound.

Any material candidate change produces a new candidate identity and must trigger the policy-defined stale/revalidation/re-review behavior.

## 8. Approval scope preservation

A user/operator approval survives an interruption only for the exact scoped action it approved.

Examples:

- approval to run Reviewer 2 on candidate X does not authorize Reviewer 3;
- approval to execute tests does not authorize repair;
- approval to repair does not authorize adjudication or merge;
- approval to adjudicate does not grant terminal authority.

A device/chat/model change never broadens approval scope.

## 9. Interruption is non-authoritative

The following events have zero authority effect by themselves:

- switching laptop/phone/desktop;
- opening a new conversation;
- hitting a conversation/context limit;
- reconnecting after network loss;
- changing assistant model/session;
- restarting an application;
- receiving a new conversational summary;
- restoring from assistant memory.

Each is a transport/interface event, not a governance transition.

## 10. Preserve RED, stale, and incomplete history

Resumption must preserve prior failures, rejected evidence, stale records, interrupted attempts, incomplete review sets, and superseded checkpoints.

A new conversation must not reconstruct a cleaner state by omission.

## 11. Contradiction handling

If conversational state conflicts with durable repository/ledger evidence, governed progression must stop at `CONTINUITY_CONFLICT` until the conflict is resolved from authoritative evidence.

The system must not choose the version that is more convenient, more recent in chat, or more permissive.

Resolution itself must be recorded as evidence and must not erase the conflicting history.

## 12. Consequential-action continuity check

Before architecture mutation, implementation, validation, qualification, reviewer orchestration, adjudication, merge, release, deployment, or terminal action after interruption, perform a continuity check that answers:

1. What exact workflow and phase are active?
2. What exact candidate/artifact is bound?
3. What required gates are complete?
4. What required gates remain pending?
5. Has any bound evidence become stale?
6. What authority state currently exists?
7. What is the single next permitted governed action?

If any answer is unresolved, fail closed.

## 13. Reviewer isolation across interruption

Independent reviewer evidence must remain isolated even when the review workflow spans multiple chats/devices.

A resumed session must not expose one reviewer’s substantive findings to another reviewer unless the governing review protocol explicitly requires cross-review.

The continuity checkpoint may record reviewer status and artifact identity, but should not leak substantive reviewer conclusions into a still-pending independent review path.

## 14. API and remote-worker continuity

External API/worker execution is not inherently tied to a ChatGPT conversation.

Its continuity is valid only if the platform durably binds request identity, task/candidate identity, worker/reviewer identity, evidence digests, response/result identity, lifecycle state, and relevant policy/authority state outside the chat transcript.

An API request/response that exists only in conversational memory is not durable governance state.

## 15. Runtime checkpoint ownership

Production checkpoints must be emitted and validated by a trusted coordination/governance component under role/event authorization rules. A worker, candidate, reviewer, or conversational assistant must not be able to self-create an authoritative checkpoint that advances its own lifecycle state.

## 16. Required machine states

At minimum, implementations should support explicit continuity outcomes such as:

- `CONTINUITY_OK`
- `CONTINUITY_STALE`
- `CONTINUITY_CONFLICT`
- `CONTINUITY_INSUFFICIENT_EVIDENCE`
- `CONTINUITY_REVIEW_BARRIER_PENDING`
- `CONTINUITY_AUTHORITY_BARRIER_PENDING`

Exact enums/error codes must be frozen before implementation qualification.

## 17. Current manual operating rule

Until this standard is reviewed and qualified, use the following bounded operating practice for this repository:

- recover current project state from GitHub/frozen artifacts before consequential work after a chat interruption;
- do not treat memory or chat summaries as authoritative when they conflict with repository evidence;
- preserve pending manual-review barriers;
- do not use a partial reviewer set to trigger repair or adjudication;
- keep all reviewer artifacts evidence-only until the preregistered review set is complete and adjudicated.

This operating rule is a safety bound, not proof that the final platform mechanism is sufficient.

## 18. Freeze condition

This standard must not be frozen until its associated continuity/resumption falsification matrix is reviewed and executed to the required policy threshold.

This document grants no merge, release, production, qualification, adjudication, or terminal authority.



---

## PROPOSED_PR40: standards/project-governance-policy-composition.md

Ref: 513bb3304a14f42e0c1a67bb6a408c339a0f4463
Git blob SHA: 1348d2ac63629531f50a0d827697ff648062c973

# Project Governance Policy Composition Standard

Status: PROPOSED_PENDING_INDEPENDENT_REVIEW

## 1. Purpose

This standard defines how user-, organization-, project-, and experiment-specific governance rules compose with mandatory platform governance.

The governing principle is:

> Users may strengthen or specialize governance for their project, but lower-level configuration must not silently weaken mandatory platform invariants.

## 2. Governance hierarchy

Effective governance is composed in this order:

1. Platform mandatory invariants
2. Organization governance
3. Project governance
4. Experiment / release governance

Lower levels inherit all applicable higher-level requirements.

Effective Governance = Platform Mandatory Rules + Organization Rules + Project Rules + Experiment/Release Rules

Project or experiment configuration does not replace the platform baseline.

## 3. Non-weakenable platform floor

A lower-level rule MUST NOT disable, bypass, contradict, redefine, or silently weaken a mandatory platform invariant.

Examples of platform invariants include, where applicable:

- no self-granted PASS or qualification;
- preservation of prior failures, retractions, and contrary evidence;
- exact evidence/source identity binding;
- mandatory independent review where policy requires it;
- no fabricated or candidate-self-authored evidence being treated as independent proof;
- fail closed when mandatory evidence, authority, identity, or review is missing or invalid;
- no unauthorized promotion, deployment, release, or live provider/API authority;
- deterministic or otherwise governed evidence requirements defined by the applicable platform policy.

If a lower-level rule conflicts with a mandatory invariant, the conflict MUST be rejected and the effective policy MUST remain non-promotable until resolved.

## 4. User/project rule capability

Authorized users MAY add project-specific governance requirements, including but not limited to:

- additional independent reviewers;
- stricter mutation or coverage thresholds;
- security/privacy requirements;
- logging restrictions;
- manual approval gates;
- approved-model or approved-provider constraints;
- retention periods;
- domain-specific evidence requirements;
- performance, accessibility, compliance, or release conditions.

Such rules may specialize or strengthen the platform baseline.

## 5. Explicit override policy

No implicit override is permitted.

A higher-level rule MAY be overridden only when all of the following are true:

1. the higher-level rule is explicitly marked overridable;
2. the lower-level actor has explicit authority for that override;
3. the override is recorded as a distinct policy change;
4. the resulting effective policy is recomputed and validated;
5. the override does not weaken any invariant marked mandatory/non-overridable;
6. any required independent review of the governance change is completed before promotion.

Absence of an override declaration means the higher-level rule remains authoritative.

## 6. Effective Governance Snapshot

Before governed execution, the platform MUST derive an immutable Effective Governance Snapshot containing at least:

- platform policy version/identity;
- organization policy version/identity, if any;
- project policy version/identity, if any;
- experiment/release policy version/identity, if any;
- composed effective requirements;
- conflict-resolution result;
- identities/hashes of all contributing policy inputs;
- actor/authority metadata for policy changes;
- creation timestamp or governed sequence identity.

The Effective Governance Snapshot MUST be content-addressed or otherwise immutably bound to the governed candidate and its evidence.

Changing governance after a candidate is frozen MUST produce a new governance snapshot and, where the changed rule is material, a fresh governed candidate/evidence cycle.

## 7. Conflict rules

Policy composition MUST be fail-closed.

For the same governed requirement:

- a stricter compatible constraint wins;
- additive requirements accumulate;
- a contradictory lower-level weakening is rejected;
- ambiguity is non-promotable until resolved;
- missing mandatory policy inputs are non-promotable.

Examples:

- Platform requires >=1 independent reviewer; project requires 2 -> effective requirement is 2.
- Platform requires independent review; project says none -> project rule is invalid.
- Platform requires failures preserved; project says delete old failures -> project rule is invalid.
- Platform allows retention >=1 year; project requires 7 years -> effective retention is 7 years.

## 8. Auditability

Every governance change MUST preserve:

- rule identifier;
- old value/state;
- new value/state;
- actor identity/authority;
- rationale;
- effective policy scope;
- governed sequence/version;
- review/adjudication evidence when required.

Policy history MUST NOT be silently rewritten.

## 9. Authority boundary

Policy definition is not qualification authority.

A user, organization, project owner, model, reviewer, or policy composer MUST NOT gain release/promotion authority merely by authoring or selecting governance rules.

The effective policy determines constraints; separate governed evidence and review determine whether those constraints are satisfied.

## 10. Required implementation architecture

The governed platform should expose these logical components:

- Governance Policy Registry
  - Platform Policy
  - Organization Policy
  - Project Policy
  - Experiment / Release Policy
- Policy Composition Engine
- Effective Governance Snapshot
- Policy Conflict Validator
- Policy Change Audit Log
- Governance Snapshot -> Candidate/Evidence Binding

The composition engine MUST be deterministic for the same ordered policy inputs.

## 11. Required falsification cases

At minimum, implementation tests must attempt to falsify:

1. project rule disables mandatory independent review;
2. project rule enables self-approval;
3. project rule lowers a mandatory evidence threshold;
4. project rule deletes/purges required historical failures;
5. project rule weakens a non-overridable authority boundary;
6. conflicting policies are silently accepted;
7. policy changes after source freeze do not trigger a new governance snapshot;
8. evidence produced under policy version A is presented under policy version B;
9. unauthorized actor changes project governance;
10. policy composer produces different effective policy for identical ordered inputs.

Any surviving case blocks promotion.

## 12. Promotion rule

This standard becomes authoritative only after the repository's applicable governance-change review and promotion process closes successfully.

Until then:

- Status = PROPOSED_PENDING_INDEPENDENT_REVIEW
- Authority effect = NONE

