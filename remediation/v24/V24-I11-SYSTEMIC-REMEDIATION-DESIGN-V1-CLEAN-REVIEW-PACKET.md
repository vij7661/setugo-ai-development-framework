# V24 I11 Systemic Remediation Design V1 — Clean Review Packet

**PLAN_BODY_SHA256:** `645377d9b623f375f1ff425234abec768280f50d5c579261ee9b9fb1e133f777`  
**Frozen V24 design:** `db9e4b349fd26e128f4486878a4af64929000a7c`  
**Frozen I10 implementation:** `9836dc3ff233cca582f485434fc1c6494cf7eb05`  
**V8 falsification packet SHA-256:** `e62a2528d880e2dc0ad368dc7b030c1a5c2600b8fef7d7610af78b71bd5f5d0e`  
**Scientific root-cause consolidation:** `3d506cfdc71b10f2f03e05c3ce5a6355b0c2a71e`  
**Status:** `REVIEW_REQUIRED / IMPLEMENTATION_NOT_STARTED`  
**Authority effect:** `NONE_EVIDENCE_ONLY`

The full packet SHA-256 is recorded separately after materialization; the wrapper does not self-hash.

---

# V24 I11 Systemic Remediation Design V1 — Clean Independent Review Surface

Status: **DESIGN ONLY / REVIEW REQUIRED / IMPLEMENTATION NOT STARTED**

Authority effect: `NONE_EVIDENCE_ONLY`

## 1. Review isolation and admissibility

Review only this clean remediation packet. Do not import prior reviewer findings, dispositions, chats, model memory, or proposed implementation patches.

Reviewer type is not an admissibility gate. A human or external AI reviewer may review this packet when the review is manually initiated by the user in a fresh clean context. Automated reviewer/provider API dispatch remains prohibited during TESTING/FALSIFICATION.

The reviewer is not required to have repository access. Repository/object identity verification is performed separately after the review.

No production/runtime repair described below has been implemented by this packet.

## 2. Exact frozen basis

Repository: `vij7661/setugo-ai-development-framework`

Frozen V24 design:
- commit `db9e4b349fd26e128f4486878a4af64929000a7c`
- tree `7986f7a016d97e6c9bbd03c035b3e9c63effda75`

Frozen I10 implementation that was falsified:
- commit `9836dc3ff233cca582f485434fc1c6494cf7eb05`
- tree `d68cbccdceebad88715c8b37ddfcd524fc16ce8a`

Reviewed V8 falsification plan:
- packet SHA-256 `e62a2528d880e2dc0ad368dc7b030c1a5c2600b8fef7d7610af78b71bd5f5d0e`
- plan-body SHA-256 `3b442e55bec52aec24042d714d4064985eb85acf914afa5903d00d1a61b373ab`
- Harness V7 version `1.6.0-PLAN-REVIEW`
- Harness V7 Git blob `6573767ae85d7ca0cfaa8b7bbafa826a7ba0c5cb`

Frozen V24 falsification sources:
- WDPC-431…470: `0f52617114f7d9d549d9822f11d5bc0156c6e676`
- WDPC-471…486: `ff8677ca1170f5cef6318662309ba119145e68cf`
- WDPC-487…496: `17bfa33f6388934d47323cea3c375466c178aadf`
- WDPC-497…506: `042b881795929f9e8d9ff5bb72f8eda8ca93fad0`

Scientific root-cause consolidation:
- commit `3d506cfdc71b10f2f03e05c3ce5a6355b0c2a71e`
- deterministic/reference cases executed: `44`
- PASS: `8`
- `FAIL_CODE_DEFECT`: `36`

Historical scientific REDs remain immutable evidence. This remediation cannot rewrite them.

## 3. Scientific findings this design must repair

### RC-1 — Governed endpoint projection incomplete across V24 validators

Family ID:

`GOVERNED_ENDPOINT_PROJECTION_INCOMPLETE_ACROSS_V24_VALIDATORS`

Affected executed cases:

`431, 432, 434, 435, 436, 437, 438, 439, 440, 441, 442, 445, 448, 450, 451, 452, 455, 456, 457, 459, 471, 479, 483, 499, 501, 502`

Observed shape:
- validators often detected the injected condition internally;
- they exposed coarse states such as `EFFECTIVE_CONTROL_INCOMPLETE`, `I6_CONSTRUCTION_INCOMPLETE`, `AGGREGATE_BUDGET_INCOMPLETE`, `GENERATION_MIGRATION_INCOMPLETE`, `AUTHORITY_UNIVERSE_INCOMPLETE`, `COMPLETENESS_BOOTSTRAP_INCOMPLETE`, or `V24_APPLY_BLOCKED`;
- reviewed V8 requires the exact implementation-emitted governed endpoint;
- the harness is forbidden from translating diagnostic strings or coarse states into an endpoint.

WDPC-434 belongs here even though its `problems[]` was empty: the aggregate validator internally derived an unresolved reconciliation outcome and blocked success but exposed only a construction state rather than the preregistered governed state.

### RC-2 — Material authority surface closure is not independently derived or enforced

Family ID:

`MATERIAL_AUTHORITY_SURFACE_CLOSURE_NOT_DERIVED_OR_ENFORCED`

Affected executed cases:

`444, 454, 473, 475, 476, 478, 480, 487, 488, 492`

Observed manifestations:
- plural independent universe projections can diverge without governed reconciliation;
- caller-declared normative locator inventory can define away a new normative clause;
- completeness can be represented without enforced durable ledger anchoring;
- IUDA source-path provenance can be ignored;
- deployment self-report can satisfy attestation digest matching without independent measurement provenance;
- an observed material discovery can be ignored when a caller-controlled boolean says discovery is not pending;
- no bound `UniverseDerivationDecisionRecord` is required by the completeness construction surface;
- material effect paths/writers are not fully reconciled against admission/capability/sink/guard closure;
- a future omission-sensitive structure can escape completeness because the implementation uses a fixed named subject-kind list.

WDPC-478 is additionally preserved as:

`MATERIAL_DISCOVERY_OBSERVATION_NOT_AUTHORITATIVELY_LATCHED_TO_APPLY_GUARD`

## 4. Existing V24 mechanisms to reuse

This remediation must extend existing V24 mechanisms rather than create a parallel authority system.

### 4.1 Endpoint precedence compiler

Frozen I5 `v24_endpoint_proof_compiler.py` already compiles:
- one descriptor per predicate;
- exact predicate → endpoint mapping;
- phase and within-phase total order;
- severity ordering;
- subsystem override constraints;
- active-predicate set equality;
- a compiled table digest.

That compiled table remains the authoritative ordering source.

### 4.2 Functional authority catch-all

V24 already defines the constitutional functional catch-all:

`ANY_ENTITY_OR_PATH_CAPABLE_OF_MATERIALLY_CREATING_MUTATING_QUALIFYING_SUPPRESSING_PUBLISHING_OR_EFFECTING_AUTHORITY`

The repair must apply that principle to runtime/material discovery and future omission-sensitive structures.

### 4.3 Completeness-required-subject rule

V24 already requires any object whose omission can make an authority decision more permissive to become a `COMPLETENESS_REQUIRED_SUBJECT`.

The repair must implement this generically rather than through a fixed list of known registry names.

## 5. Remediation architecture — RC-1 canonical governed endpoint projection

### 5.1 Typed failure conditions are authoritative; diagnostic strings are not

Every validator/guard participating in authoritative decisions must emit typed `GovernedFailureCondition` records at the point where the predicate is evaluated.

Minimum schema:

```text
GovernedFailureCondition {
  condition_id
  predicate_id
  control_id
  producer_component_id
  governance_generation_id
  subject_ids[]
  source_record_digests[]
  evidence_digests[]
  observed_sequence
  currentness_binding
  condition_payload_digest
}
```

Rules:
1. `condition_id`/`predicate_id` come from a qualified condition descriptor registry.
2. The validator does **not** choose the final endpoint.
3. Human-readable `problems[]` may remain for diagnostics, but they are non-authoritative and may be generated from the typed condition. No runtime code may parse diagnostic text to reconstruct authority.
4. Unknown/unregistered blocking condition IDs fail closed and cannot be ignored.
5. A producer cannot provide phase, precedence rank, or final endpoint as authoritative input.

### 5.2 Condition descriptor registry

Introduce a completeness-qualified `GovernedConditionDescriptorRegistry`.

Each descriptor binds:

```text
ConditionDescriptor {
  condition_id
  predicate_id
  control_id
  schema_version
  allowed_producer_component_classes[]
  required_evidence_classes[]
  condition_schema_digest
}
```

The condition universe is itself omission-sensitive and therefore a `COMPLETENESS_REQUIRED_SUBJECT`.

Required properties:
- no duplicate condition identity;
- no condition without exactly one predicate mapping;
- no predicate-bearing condition omitted from the active governed condition universe;
- no runtime condition emitted by an unadmitted producer;
- no local module endpoint override.

### 5.3 Runtime endpoint projector

Add a single `GovernedEndpointProjector`.

Input:

```text
EndpointProjectionRequest {
  governance_generation_id
  compiled_endpoint_table_digest
  condition_registry_digest
  triggered_conditions[]
  decision_context_digest
}
```

Output:

```text
EndpointProjectionDecision {
  projection_id
  governance_generation_id
  compiled_endpoint_table_digest
  condition_registry_digest
  triggered_condition_digests[]
  selected_predicate_id
  selected_endpoint
  selected_phase
  selected_within_phase_rank
  nonselected_triggered_predicate_ids[]
  decision_context_digest
  projection_digest
}
```

Selection rule:
1. Validate every triggered condition against the condition registry.
2. Resolve each condition only to its bound predicate ID.
3. Resolve predicate IDs through the already-qualified compiled endpoint precedence table.
4. Select the earliest applicable phase and then the exact total-order winner within that phase.
5. Preserve every simultaneously triggered condition in the projection record.
6. If a triggered condition is unmapped, the table/condition binding is incomplete and authority blocks; no caller fallback is allowed.
7. Missing evidence remains distinct from proven invalidity.
8. Subsystem-specific endpoints may win only through the qualified table/override mapping.

### 5.4 Construction state is separate from governed endpoint

Validators may retain construction/evidence states such as `..._INCOMPLETE` or `..._CONSTRUCTION_VALID`.

Those states are never the governed authority result.

The authoritative decision surface must explicitly expose:
- typed triggered conditions;
- the exact `EndpointProjectionDecision`;
- the selected governed endpoint;
- the compiled table digest used.

### 5.5 Decision/apply/proof binding

`AuthorityKernelDecisionRecord`, apply-time revalidation, application records, and reviewer-safe proof must bind:
- condition registry digest;
- endpoint precedence table digest;
- projection decision digest;
- selected predicate and endpoint;
- all load-bearing source/evidence digests.

Any change in a bound condition/evidence source after decision requires full predicate re-evaluation. An earlier-phase newly true predicate wins over stale-decision fallback.

## 6. Remediation architecture — RC-2 closed-world material authority surface

### 6.1 Append-only material authority observation ledger

Introduce an append-only `MaterialAuthorityObservationLedger`.

Record:

```text
MaterialAuthorityObservation {
  observation_id
  governance_generation_id
  observation_sequence
  observer_identity
  observer_control_domain_id
  source_kind
  entity_or_path_id
  functional_effects[]
  affected_sink_ids[]
  writer_or_capability_ids[]
  control_plane_ids[]
  evidence_digest
  currentness_binding
  observation_payload_digest
}
```

Rules:
- observations cannot be silently deleted or collapsed into a caller boolean;
- each append changes the ledger head digest;
- candidate self-report alone cannot establish independent discovery where independence is required;
- an unknown/unmodeled material observation blocks until admitted/classified/requalified.

### 6.2 Independently derived material-surface projection

Introduce `MaterialAuthoritySurfaceProjection`.

It is derived from:
- admitted surfaces;
- runtime observations;
- independent effect-path conformance;
- control-plane conformance;
- relevant store/database/offline/recovery paths;
- normative authority surfaces where applicable.

The projection must not be derived solely from the candidate registry being evaluated.

Every material projection member must resolve to applicable:
- admission;
- capability;
- sink;
- dependency edge;
- control source;
- guard;
- completeness qualification.

An unresolved material member blocks authority.

### 6.3 Generic completeness-required-subject classification

Replace fixed-name completeness coverage as the authority criterion with a functional classifier:

```text
requires_completeness(subject) =
  omission_of_member_or_relationship_can_make_authority_more_permissive
```

Create a `CompletenessSubjectClassificationRecord` for every material candidate structure.

Unknown new registries/tables/graphs/manifests/inventories/derived sets are not presumed non-authoritative. If materiality cannot be excluded with qualifying evidence, authority blocks pending classification.

Named lists may remain as expected-minimum checks, but never as a closed universe.

### 6.4 Plural universe derivation and reconciliation

A singular candidate-owned `independent_universe_projection` is insufficient.

Require one or more `UniverseDerivationDecisionRecord`s, each binding:
- derivation authority identity/control domain;
- exact source/evidence digests;
- derivation algorithm/rule identity;
- derived universe digest;
- generation/currentness.

Where policy requires multiple independent derivations:
- compare them explicitly;
- material divergence cannot be silently selected by root/operator/candidate;
- unresolved divergence returns the existing applicable completeness/conflict outcome and blocks activation;
- reconciliation itself must be governed and independently qualified where required.

### 6.5 Durable completeness qualification ledger

A `CompletenessQualificationRecord` is authoritative only when it is durably appended to the governed completeness ledger.

Required binding includes:
- record identity;
- predecessor/sequence;
- generation;
- subject;
- universe/derivation/source evidence digests;
- durable storage/anchor identity;
- witness/currentness evidence where policy requires it.

Process-memory-only or otherwise unanchored qualification cannot become current authority.

### 6.6 Evidence provenance is load-bearing

Capability/IUDA/completeness evidence must carry provenance sufficient to establish independence.

For capability measurement:
- measurement source identity;
- control domain;
- measured deployment/configuration digest;
- currentness;
- independence relationship to subject/owner.

`DEPLOYMENT_SELF_REPORT_ONLY` cannot establish independent attestation.

For IUDA/universe sources:
- source path/provenance is explicit;
- two nominally distinct authorities sharing a prohibited source/control path do not count as independent.

### 6.7 Functional writer/effect-path closure

For every material effect path:
- path source/writer identity must resolve to current admission;
- capability must permit the exact authority class;
- target sink must include the writer in its admitted writer set;
- required guards and dependency edges must exist;
- required control-plane/source records must qualify.

A friendly/non-authority label cannot override functional capability.

An independently discovered direct writer absent from these records blocks as an unadmitted authority path.

### 6.8 Authoritative discovery latch at decision and apply

Replace boolean-only discovery gating with ledger-bound revalidation.

`AuthorityKernelDecisionRecord` binds:
- material observation ledger head;
- material-surface projection digest;
- unresolved material observation set digest.

At apply:
1. read the latest observation ledger head from the authoritative sequenced source;
2. rederive/revalidate material-surface projection;
3. compare against the decision-bound digests;
4. evaluate any newly discovered material path through normal admission/completeness predicates;
5. project the exact governed endpoint using Section 5.

If a newly observed path is unadmitted, `AUTHORITY_ADMISSION_REQUIRED` applies according to precedence.

If no earlier predicate is true but decision-bound state changed, the applicable stale-decision endpoint applies.

A caller-provided `material_discovery_pending=false` cannot override an actual observation.

### 6.9 Independent normative-clause universe derivation

For normative artifacts, the descriptor/locator inventory cannot be the sole source of the clause universe.

Require a `NormativeClauseProjection` independently derived from the exact authoritative artifact bytes.

The derivation has two stages:
1. deterministic structural candidate enumeration from exact artifact bytes/structure, independent of existing descriptors;
2. governed semantic disposition of each candidate as material normative, non-authoritative/reference-only, superseded, or insufficiently established.

Rules:
- every material normative candidate requires a catalog descriptor/disposition;
- a material candidate absent from the catalog blocks with `NORMATIVE_CONTROL_CATALOG_INCOMPLETE`;
- an ambiguous candidate cannot be silently ignored; it remains blocking/insufficient until dispositioned;
- the projection digest and exact artifact blob are bound into catalog qualification.

This repair must not hard-code the WDPC-454 sentence or rely on one test-specific regex.

## 7. Atomicity, concurrency, and race rules

1. Condition emission and the source-state observation that makes the condition true must be transactionally or cryptographically bound.
2. Material discovery observation append occurs before an effect can rely on absence of that observation.
3. Apply revalidation reads a single authoritative observation-ledger head and condition snapshot.
4. If the head changes during revalidation/apply, the operation retries from the new head or fails closed; it cannot continue using mixed snapshots.
5. Endpoint projection is deterministic and pure over the exact bound condition set + table digest.
6. Result/application records bind the projection digest before authority effect becomes successful.

## 8. Anti-false-green implementation prohibitions

Production code must not contain:
- WDPC case IDs used to choose behavior;
- expected endpoint strings supplied by test fixtures as decision inputs;
- fixture-branch identifiers used by production logic;
- diagnostic-string → endpoint parsing;
- caller-controlled phase/rank/precedence;
- caller-controlled “complete universe” as the sole completeness source;
- boolean-only material-discovery authority;
- self-produced evidence counted as independent without governed independence proof;
- silent ignore of unknown material conditions/subjects;
- test-specific normative sentence recognition.

A repair that makes the current fixtures pass by any of those mechanisms is invalid.

## 9. Implementation workstreams after design approval

Implementation has **not started**. If this design passes review, implementation should branch from the frozen I10 implementation lineage, not from a scientific result branch.

### R1 — Typed condition foundation
- condition records/descriptors;
- condition registry completeness;
- validator emission API;
- existing `problems[]` retained as non-authoritative diagnostics.

### R2 — Canonical endpoint projector
- extend I5 compiled precedence usage into runtime projection;
- deterministic selection;
- decision/apply/proof binding;
- unknown-condition fail-closed.

### R3 — Material observation and projection
- append-only observation ledger;
- functional material-surface projection;
- generic completeness-required-subject classifier;
- plural universe derivation/reconciliation.

### R4 — Evidence/ledger hardening
- durable completeness ledger binding;
- capability measurement provenance;
- IUDA source provenance;
- `UniverseDerivationDecisionRecord`.

### R5 — Writer-path and apply integration
- writer/admission/capability/sink/guard closure;
- authoritative discovery latch;
- apply-time revalidation against latest observation head.

### R6 — Normative clause projection
- independent structural clause candidate derivation;
- semantic disposition;
- catalog set-equality/completeness binding.

### R7 — Regression and proof integration
- reviewer-safe proof exposes projection identity;
- audit binds new digests;
- historical REDs remain preserved.

## 10. Successor verification discipline

A repaired implementation is a **new candidate**. The V8 review of frozen I10 does not automatically authorize that successor.

After implementation:
1. freeze exact successor commit/tree;
2. produce a successor verification packet that preserves V8 case semantics but binds the successor implementation;
3. obtain a fresh clean independent review of that exact verification surface;
4. only then execute successor falsification.

Minimum successor rerun:
- all 44 already-executed deterministic/reference V24 cases, preserving negative-before-positive order;
- previously blocked reference positives only after same-mechanism negatives qualify;
- all affected construction/unit/integration tests;
- affected inherited WDPC-01…430 subset;
- because the repair is cross-cutting to endpoint/apply/completeness surfaces, full inherited WDPC-01…430 regression before qualification.

External/manual V24 cases remain evidence-gated. They cannot be synthesized into PASS.

WDPC-469 and WDPC-495 remain blocked until I1 semantic qualification is actually satisfied.

WDPC-503 remains unresolved until exact implementation/static evidence satisfies its governed rule; design prose alone is not implementation evidence.

## 11. Required review attacks

The reviewer should actively attempt to falsify this remediation design against at least these paths:

1. Can a validator create a new condition that escapes the condition registry?
2. Can a condition producer choose a more permissive endpoint or precedence?
3. Can multiple simultaneous conditions be reordered by caller/module?
4. Can diagnostics still become authority through an indirect mapping?
5. Can a new omission-sensitive registry escape because the generic materiality classifier never sees it?
6. Can the materiality classifier itself be candidate-defined/self-qualifying?
7. Can a runtime observation be lost between observation, decision, and apply?
8. Can discovery-ledger head changes race with apply?
9. Can two “independent” projections share one source/control domain and still count independently?
10. Can a self-report satisfy capability measurement provenance?
11. Can a process-memory completeness record become current authority?
12. Can a direct writer reach a sink without admission/capability/guard closure?
13. Can a new normative clause evade independent candidate enumeration?
14. Can normative clause enumeration over-classify ordinary prose and create an unsafe manual bypass?
15. Can endpoint table/condition registry drift after a decision without invalidating apply?
16. Can a successor implementation rewrite or retroactively mark historical REDs as PASS?
17. Can the repair weaken external/manual evidence requirements?
18. Does any repair path depend on WDPC IDs, fixture IDs, or expected endpoints?

## 12. Required clean review output

A. `SELF_CONTAINED_BINDING = CONSISTENT | INCONSISTENT | INSUFFICIENT_PACKET_CONTENT`

B. Overall disposition:
`READY_FOR_IMPLEMENTATION | NEEDS_REVISION | INSUFFICIENT_TO_ASSESS`

C. Critical findings

D. High / Medium / Low findings

E. RC-1 endpoint-projection audit

F. RC-2 closed-world material-surface audit

G. Atomicity/concurrency/race audit

H. Independence/provenance audit

I. Normative-clause discovery audit

J. Historical-result / successor-binding audit

K. Anti-case-specific-hardcoding audit

L. Missing contracts or false-green paths

M. End exactly:

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`

Do not prepend a reviewer-type declaration.

## 13. Implementation gate

This packet grants no implementation, merge, release, deployment, qualification, production, or terminal authority.

Implementation may begin only after:
- this exact design packet receives `SELF_CONTAINED_BINDING = CONSISTENT`;
- disposition is `READY_FOR_IMPLEMENTATION`;
- repository-connected adjudication verifies that the review corresponds to this exact packet/body identity;
- no unresolved blocking review finding remains.

Any semantic change to this remediation design requires a successor packet and fresh review.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
