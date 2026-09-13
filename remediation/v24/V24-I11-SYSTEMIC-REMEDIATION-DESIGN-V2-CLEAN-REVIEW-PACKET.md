# V24 I11 Systemic Remediation Design V2 — Clean Review Packet

**PLAN_BODY_SHA256:** `1b4c05c67e6121fb639026f4cdf6128a11b74e5b3fbf5cb97d45dfee41fec0ce`  
**Frozen V24 design:** `db9e4b349fd26e128f4486878a4af64929000a7c`  
**Frozen I10 implementation:** `9836dc3ff233cca582f485434fc1c6494cf7eb05`  
**V8 falsification packet SHA-256:** `e62a2528d880e2dc0ad368dc7b030c1a5c2600b8fef7d7610af78b71bd5f5d0e`  
**Scientific root-cause consolidation:** `3d506cfdc71b10f2f03e05c3ce5a6355b0c2a71e`  
**Status:** `REVIEW_REQUIRED / IMPLEMENTATION_NOT_STARTED`  
**Authority effect:** `NONE_EVIDENCE_ONLY`

The full packet SHA-256 is recorded separately after materialization; the wrapper does not self-hash.

---

# V24 I11 Systemic Remediation Design V2 — Clean Independent Review Surface

Status: **DESIGN ONLY / REVIEW REQUIRED / IMPLEMENTATION NOT STARTED**

Authority effect: `NONE_EVIDENCE_ONLY`

## 1. Review isolation and admissibility

Review only this clean remediation packet.

Do not use prior reviewer findings, dispositions, chats, model memory, implementation proposals, or adjudication artifacts as substantive review context.

A human or external AI reviewer may review this packet when the review is manually initiated by the user in a fresh clean context. Automated reviewer/provider API dispatch remains prohibited during TESTING/FALSIFICATION.

Repository/object identity verification is performed separately after the clean review.

No production/runtime repair described here has been implemented.

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

Historical scientific REDs remain immutable and cannot be rewritten by remediation.

## 3. Systemic repair targets

### RC-1 — Governed endpoint projection incomplete across V24 validators

Family ID:

`GOVERNED_ENDPOINT_PROJECTION_INCOMPLETE_ACROSS_V24_VALIDATORS`

Required end-state:
- every authoritative predicate applicable to an exact decision context is evaluated;
- every evaluation is visible in a complete coverage record;
- true predicates emit registered typed conditions;
- one qualified precedence table determines the exact governed endpoint;
- diagnostic strings and construction states never become authority.

### RC-2 — Material authority surface closure is not independently derived or enforced

Family ID:

`MATERIAL_AUTHORITY_SURFACE_CLOSURE_NOT_DERIVED_OR_ENFORCED`

Required end-state:
- material candidates are independently enumerated;
- materiality classification is not candidate-self-granted;
- material observations are append-only and apply-visible;
- completeness, capability, universe, normative, and writer-path evidence has governed provenance and independence;
- new omission-sensitive structures cannot escape by not being named in a fixed list.

## 4. Existing V24 mechanisms that remain controlling

### 4.1 Qualified endpoint precedence table

The existing V24 endpoint compiler remains the sole source of:
- predicate → endpoint mapping;
- phase;
- within-phase total order;
- severity/override constraints;
- compiled table digest.

No validator, caller, UI, model, fixture, reviewer, or subsystem may choose an authoritative endpoint locally.

### 4.2 Functional authority rule

The constitutional functional catch-all remains:

`ANY_ENTITY_OR_PATH_CAPABLE_OF_MATERIALLY_CREATING_MUTATING_QUALIFYING_SUPPRESSING_PUBLISHING_OR_EFFECTING_AUTHORITY`

Names and friendly labels never defeat functional materiality.

### 4.3 Functional completeness-subject rule

Any object whose omission can make an authority decision more permissive is a `COMPLETENESS_REQUIRED_SUBJECT`.

A fixed named list may be an expected-minimum check but never the complete universe.

## 5. Governed evidence-class foundation

Introduce a completeness-qualified `GovernedEvidenceClassRegistry`.

Each `EvidenceClassDescriptor` binds:

```text
EvidenceClassDescriptor {
  evidence_class_id
  control_id
  schema_version
  allowed_source_kinds[]
  allowed_producer_component_classes[]
  required_identity_fields[]
  required_currentness_fields[]
  required_anchor_fields[]
  required_independence_rule_id
  evidence_schema_digest
}
```

Rules:
1. “Qualifying evidence” has no authority unless it resolves to an active evidence class.
2. Unknown evidence classes fail closed.
3. Evidence-class descriptors are themselves a `COMPLETENESS_REQUIRED_SUBJECT`.
4. The registry owner cannot self-qualify registry completeness.
5. Evidence-class qualification cannot be populated from WDPC IDs, fixture identities, expected endpoint values, or reviewer-specific knowledge.
6. Evidence currentness and independence are verified from bound evidence, not prose assertion.

## 6. RC-1 — Complete predicate evaluation and canonical endpoint projection

### 6.1 Active decision predicate universe

For each exact decision context, derive `ApplicablePredicateUniverse` from:
- the current qualified compiled endpoint table;
- current qualified applicability rules;
- exact decision/sink/effect class;
- exact admitted subsystem overrides.

`NOT_APPLICABLE` is compiler-derived. A validator or caller cannot self-select it.

The universe binds:
- governance generation;
- compiled endpoint table digest;
- applicability-compiler digest;
- exact decision-context digest;
- ordered applicable predicate IDs;
- universe digest.

### 6.2 Predicate evaluator contract registry

Introduce `PredicateEvaluatorContractRegistry`.

Each descriptor binds:

```text
PredicateEvaluatorContract {
  predicate_id
  evaluator_contract_id
  control_id
  admitted_producer_component_ids_or_classes[]
  required_input_classes[]
  required_evidence_class_ids[]
  evaluation_schema_digest
  evaluator_implementation_identity_rule
}
```

Rules:
- every active predicate has exactly one authoritative primary evaluator contract;
- supplemental observers may exist but cannot replace the primary coverage obligation;
- no authoritative evaluator contract may be omitted merely because the runtime did not emit a condition;
- the registry is omission-sensitive and independently completeness-qualified.

### 6.3 Independent evaluator/condition universe derivation

Introduce `ConditionUniverseDerivationRecord`.

It is not derived solely from the candidate condition registry.

Minimum independent inputs:
1. the exact qualified active predicate set from the compiled endpoint table;
2. the exact admitted evaluator/validator implementation surface, independently inventoried from implementation/deployment evidence;
3. the evaluator contract registry;
4. the governed evidence-class registry.

The derivation authority must be outside the control domain of the condition-registry owner and evaluator implementation owner for the surface being qualified.

Default qualification requires at least two independently controlled derivations whose prohibited effective-control/source-path closures do not intersect. An immutable exact bootstrap residual-trust exception may reduce that threshold only when explicitly bound and exposed in proof.

Set-equality requirements:
- independently derived active predicate IDs = evaluator contract predicate IDs;
- every evaluator contract resolves to at least one registered condition schema for the `TRUE` outcome or a documented no-condition outcome where the predicate semantics cannot be true;
- every registered authoritative condition resolves to exactly one active predicate;
- no extra candidate-only authoritative condition can enter the set.

Material divergence among independent derivations blocks qualification.

### 6.4 Typed predicate evaluation record

Every applicable predicate produces exactly one authoritative `PredicateEvaluationRecord`:

```text
PredicateEvaluationRecord {
  evaluation_id
  governance_generation_id
  decision_context_digest
  predicate_id
  evaluator_contract_id
  evaluator_component_id
  evaluation_status  # TRUE | FALSE | NOT_APPLICABLE
  source_snapshot_digest
  evidence_record_digests[]
  evidence_class_ids[]
  condition_digests[]
  observation_binding_digest
  evaluated_sequence
  currentness_binding
  evaluation_payload_digest
}
```

Rules:
- `NOT_APPLICABLE` is accepted only when it exactly matches compiler-derived applicability;
- a producer-supplied N/A choice is invalid;
- `TRUE` requires one or more registered `GovernedFailureCondition` records as required by the predicate contract;
- `FALSE` requires the predicate contract’s governed negative/absence evidence classes;
- missing evidence cannot be converted to `FALSE`;
- missing evaluation is never equivalent to false.

### 6.5 Complete decision-time coverage record

Before an authoritative kernel decision can exist, create:

```text
PredicateEvaluationCoverageRecord {
  coverage_id
  governance_generation_id
  decision_context_digest
  applicable_predicate_universe_digest
  endpoint_table_digest
  evaluator_contract_registry_digest
  condition_registry_digest
  evidence_class_registry_digest
  evaluation_record_digests[]
  evaluated_predicate_ids[]
  true_predicate_ids[]
  false_predicate_ids[]
  not_applicable_predicate_ids[]
  coverage_set_equality_proof_digest
  coverage_digest
}
```

Coverage qualification requires:
- one and only one evaluation record for every applicable predicate;
- no authoritative evaluation for a predicate outside the derived universe;
- exact set equality;
- all evidence/condition bindings valid;
- all evaluator identities admitted/current;
- all load-bearing registries current.

If coverage is missing/incomplete, no qualifying exact current kernel decision exists. The operation fails closed under the existing endpoint-precedence semantics; it cannot proceed with coarse construction state.

### 6.6 Typed failure conditions

`GovernedFailureCondition` remains the bridge from a `TRUE` evaluation to endpoint projection:

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
  evidence_class_ids[]
  observation_binding_digest
  currentness_binding
  condition_payload_digest
}
```

The validator does not choose phase, rank, or endpoint.

Human-readable `problems[]` may exist only as non-authoritative diagnostics and may never be parsed back into authority.

### 6.7 Condition descriptor registry

`GovernedConditionDescriptorRegistry` binds:

```text
ConditionDescriptor {
  condition_id
  predicate_id
  control_id
  schema_version
  allowed_producer_component_classes[]
  required_evidence_class_ids[]
  condition_schema_digest
}
```

It qualifies only after the independent condition-universe derivation and exact set-equality checks in Section 6.3.

Unknown/unregistered emitted conditions fail closed. Silent non-emission is separately caught by Sections 6.4–6.5.

### 6.8 Condition-observation atomic binding

Introduce:

```text
ConditionObservationBindingRecord {
  binding_id
  governance_generation_id
  predicate_id
  evaluator_id
  source_snapshot_digest
  observation_ledger_head_digest
  evaluation_digest
  condition_digests[]
  atomic_mode
  atomic_proof_digest
  binding_digest
}
```

Accepted `atomic_mode` values are governed descriptors, not free text.

Minimum supported modes:
- `SAME_AUTHORITATIVE_TRANSACTION`: source observation, evaluation, and condition append share one authoritative transactional commit identity;
- `CRYPTOGRAPHICALLY_BOUND_SNAPSHOT`: immutable source snapshot and observation head are digest-bound, signed/anchored by an admitted authority, and verified before condition acceptance.

A deterministic `ConditionObservationBindingVerifier` validates the mode-specific proof.

No unverified statement that records were “transactionally or cryptographically bound” is sufficient.

### 6.9 Canonical runtime endpoint projector

`GovernedEndpointProjector` accepts only a qualified coverage record and current registries:

```text
EndpointProjectionRequest {
  governance_generation_id
  decision_context_digest
  predicate_evaluation_coverage_digest
  compiled_endpoint_table_digest
  condition_registry_digest
  evaluator_contract_registry_digest
  evidence_class_registry_digest
}
```

It:
1. verifies exact current coverage;
2. reads the `TRUE` predicate set from coverage;
3. verifies each required condition;
4. resolves predicates through the qualified compiled endpoint table;
5. selects earliest phase and exact within-phase total-order winner;
6. preserves all simultaneously true predicates/conditions;
7. emits one `EndpointProjectionDecision`.

No runtime diagnostic mapping or caller fallback is permitted.

### 6.10 Decision/apply/proof binding and drift invalidation

`AuthorityKernelDecisionRecord` binds at minimum:
- predicate universe digest;
- predicate coverage digest;
- endpoint precedence table digest;
- evaluator contract registry digest;
- condition registry digest;
- evidence class registry digest;
- endpoint projection digest;
- selected predicate/endpoint;
- all other load-bearing state digests.

At apply, read the current qualified versions/digests of every bound registry/table and current predicate/material observation state.

If any bound endpoint table, evaluator registry, condition registry, evidence-class registry, applicability compiler, observation head, completeness head, or other load-bearing digest changed:
- the prior decision is not usable for apply;
- perform full current re-evaluation and new projection;
- if re-evaluation cannot qualify, fail closed;
- any newly true earlier-phase predicate wins under the current qualified table.

There is no “same semantics probably” bypass.

## 7. RC-2 — Independently closed material authority surface

### 7.1 Independent material-structure universe enumeration

Introduce `MaterialStructureUniverseProjection`.

Candidate structures include any registry, table, graph, manifest, inventory, derived set, service, tool, API, writer, store path, queue, publication path, release path, control plane, recovery path, cache/replica influence, reviewer/model qualification path, or other object capable of affecting authority.

The universe is independently derived from at least:
- exact admitted implementation/deployment surface;
- runtime material observation ledger;
- effect-path conformance evidence;
- control-plane conformance evidence;
- store/database/offline/recovery surfaces;
- normative authority surfaces where applicable.

Candidate-owned registries cannot be the sole enumeration source.

Default qualification requires at least two independently controlled derivations with no prohibited shared effective-control/source path, subject only to an explicit immutable bootstrap residual-trust exception.

Material divergence blocks qualification.

### 7.2 Materiality classifier authority

Materiality is evaluated against the frozen V24 functional rule, not a candidate-defined label.

Introduce `MaterialityClassificationRecord`:

```text
MaterialityClassificationRecord {
  classification_id
  subject_id
  subject_kind
  functional_capability_evidence_digests[]
  evidence_class_ids[]
  classifier_rule_id
  classifier_rule_digest
  classifier_authority_id
  classifier_control_domain_id
  classification  # MATERIAL | PROVEN_NON_MATERIAL | INSUFFICIENT_EVIDENCE
  classification_digest
}
```

Rules:
- classifier rule identity/digest is governance-bound;
- classifier authority cannot be the subject owner/registry owner for its own qualification;
- `INSUFFICIENT_EVIDENCE` blocks exclusion from the material surface;
- unknown structures are not presumed non-material;
- a material candidate enters admission/completeness governance.

### 7.3 Append-only material observation ledger

`MaterialAuthorityObservationLedger` is an authoritative append-only sequence.

Each record binds:

```text
MaterialAuthorityObservation {
  observation_id
  governance_generation_id
  observation_sequence
  predecessor_record_digest
  observer_identity
  observer_control_domain_id
  source_kind
  entity_or_path_id
  functional_effects[]
  affected_sink_ids[]
  writer_or_capability_ids[]
  control_plane_ids[]
  evidence_digest
  evidence_class_id
  currentness_binding
  observation_payload_digest
  record_digest
}
```

Each append changes the canonical ledger-head digest.

No caller boolean can erase or override a recorded material observation.

### 7.4 Observation-before-effect enforcement

Every authority-capable sink/effect path must enforce:

1. read current material-observation ledger head;
2. bind that head into the guard decision;
3. resolve all observations relevant to the attempted effect;
4. project the governed endpoint;
5. only then permit the effect if every applicable authority predicate qualifies.

The exact observation-head digest is bound into the application record.

An effect path capable of bypassing this sequence is itself an unresolved material authority path and blocks until admitted/guarded.

This rule applies to every material sink/effect path, not a named subset.

### 7.5 Plural universe derivation and independence threshold

For each omission-sensitive universe/subject, require at least two `UniverseDerivationDecisionRecord`s by default.

Each record binds:
- derivation authority identity/control domain;
- exact source/evidence digests and evidence classes;
- source-path identifiers;
- derivation algorithm/rule identity and digest;
- derived universe digest;
- generation/currentness.

Independence fails if required derivations share any prohibited effective-control/source path under Section 9.

A threshold lower than two is allowed only by an exact immutable bootstrap residual-trust exception that is:
- explicitly declared;
- bound to subject class;
- included in reviewer-safe proof;
- not created or modified by the descendant subject being qualified.

Unresolved material divergence returns the applicable existing completeness/conflict result and blocks activation.

### 7.6 Durable completeness qualification ledger

A `CompletenessQualificationRecord` is authoritative only after append to the governed `CompletenessQualificationLedger`.

Ledger requirements:
- append-only sequence number;
- predecessor record/head digest;
- exact record digest;
- canonical ledger-head digest;
- generation and subject identity;
- universe/derivation/source evidence digests and evidence classes;
- durable storage identity;
- anchor record identity/digest;
- witness/currentness proof.

Default currentness qualification requires at least one witness from an effective-control domain independent of the ledger operator/root operational domain.

An exact immutable bootstrap residual-trust exception may replace that witness only for its explicitly bound genesis subject classes and must be visible in proof.

Decision and apply both bind and revalidate the current ledger-head digest.

Process-memory-only, local-cache-only, unsequenced, unanchored, or stale records cannot become current authority.

### 7.7 Governed provenance and prohibited shared control

All independence claims use a common `IndependenceRuleDescriptor`.

The effective-control closure includes, as applicable:
- provider/cloud/account/organization root;
- repository administration;
- CI/CD and deployment control;
- configuration control;
- HSM/KMS/secret-store control;
- credential recovery/reset;
- emergency/break-glass administration;
- common measurement source;
- common evidence store or transformation path when it can suppress/fabricate evidence;
- root/operator threshold membership.

Two parties/evidence sources do not count as independent when their prohibited closures intersect for the evaluated rule.

This applies uniformly to:
- capability attestors;
- capability measurement sources;
- IUDAs;
- completeness derivation authorities;
- condition-universe derivation authorities;
- material-surface derivation authorities;
- witnesses;
- normative semantic disposition authorities.

A nominally separate service/account/provider name is not independence proof.

### 7.8 Capability measurement provenance

Capability attestation binds:
- independent attestor identity/control domain;
- measurement source identity/control domain;
- measurement evidence class;
- exact deployment/configuration/API/capability digests;
- source path;
- observation time/sequence/currentness;
- independence rule and proof digest.

`DEPLOYMENT_SELF_REPORT_ONLY` cannot satisfy independent capability measurement.

A shared prohibited control/source path between subject, attestor, or required independent measurement source invalidates the independence claim.

### 7.9 Functional writer/effect-path closure

For every material effect path:
- writer/source identity has current admission;
- current capability permits the exact authority class;
- sink registry includes the writer;
- required dependency edges exist;
- guards are current;
- control-plane/source records qualify;
- the path is represented in the independently derived material surface;
- latest observation ledger state is consumed.

A friendly/non-authority label has no effect on this test.

An independently observed direct writer absent from any required record blocks as an unadmitted authority path.

### 7.10 Authoritative discovery latch at decision and apply

`AuthorityKernelDecisionRecord` binds:
- material observation ledger head;
- material-structure universe digest;
- materiality-classification set digest;
- unresolved material-observation set digest;
- relevant completeness ledger head.

At apply:
1. obtain current authoritative heads/digests;
2. compare with decision-bound values;
3. if changed, fully rederive/reclassify/re-evaluate;
4. evaluate new material paths through admission/completeness predicates;
5. create a new endpoint projection;
6. permit effect only under the new current decision.

A caller-controlled `material_discovery_pending=false` is non-authoritative.

### 7.11 Independent normative clause universe

For every exact authoritative normative artifact, create `NormativeClauseProjection` independent of the existing descriptor inventory.

Stage 1 — structural enumeration:
- derive candidate clause identities from exact artifact bytes/structure;
- bind artifact blob/digest, structural parser/rule identity, candidate spans/anchors, and projection digest;
- existing control descriptors cannot be the sole enumeration source.

Stage 2 — independent semantic disposition:
Every candidate receives a `NormativeSemanticDispositionRecord`:

```text
NormativeSemanticDispositionRecord {
  candidate_clause_id
  artifact_blob_digest
  candidate_span_digest
  disposition_authority_id
  disposition_authority_control_domain_id
  evidence_class_ids[]
  evidence_digests[]
  independence_rule_id
  disposition  # MATERIAL_NORMATIVE | REFERENCE_ONLY | SUPERSEDED | PROVEN_NON_NORMATIVE | INSUFFICIENT_EVIDENCE
  successor_control_id_if_any
  currentness_binding
  disposition_digest
}
```

The `NormativeSemanticDispositionAuthoritySet` is governance-bound, thresholded, and independently qualified from the normative artifact/catalog owner.

Default material semantic disposition requires the configured independent threshold; a single artifact/catalog owner cannot self-disposition its own candidate as non-normative.

`INSUFFICIENT_EVIDENCE` is blocking and cannot default to `REFERENCE_ONLY` or `PROVEN_NON_NORMATIVE`.

Catalog qualification requires exact set coverage of all candidate clause IDs and appropriate descriptors for every `MATERIAL_NORMATIVE` candidate.

This mechanism must not use the WDPC-454 sentence or fixture-specific regexes.

## 8. Completeness-subject classification

For every independently enumerated material candidate structure, evaluate:

```text
requires_completeness(subject) =
  omission_of_member_or_relationship_can_make_authority_more_permissive
```

The result is a governed `CompletenessSubjectClassificationRecord` using the materiality classifier and evidence-class rules above.

Named expected subjects remain regression checks only.

No unknown registry/table/graph/manifest/inventory/derived set may be excluded merely because it is absent from a static allow-list.

## 9. Common independence rule

Every contract that requires independence must identify an exact active `IndependenceRuleDescriptor` and effective-control closure evidence.

Minimum prohibition:
- subject owner and qualifying authority in same prohibited control domain;
- shared provider/account/organization root when that root can control both;
- shared CI/CD/repository/deployment admin that can control both;
- shared HSM/KMS/secret/credential-recovery control that can impersonate/control both;
- shared measurement-source path where independence of evidence is required;
- shared evidence-transformation/storage control that can suppress or fabricate both sides;
- root/operator-only quorum where an external independent domain is required.

Silence is not proof of no relationship.

Missing control evidence yields blocking insufficient evidence, not independence.

## 10. Atomicity and concurrency

### 10.1 Snapshot binding
Every authoritative evaluation binds:
- exact source snapshot;
- observation ledger head;
- evaluator registry/table digests;
- evidence records;
- condition/evaluation records.

### 10.2 Head-change rule
If any authoritative head/digest changes during decision or apply:
- abandon the mixed snapshot;
- retry from one new current snapshot or fail closed;
- never combine old coverage with new material/completeness state.

### 10.3 Observation append order
A material observation must be durably sequenced before an effect may rely on its absence.

### 10.4 Projection purity
Endpoint projection is deterministic/pure over the exact qualified coverage record and exact compiled table digest.

### 10.5 Effect atomicity
Successful authority effect/application state binds the exact current endpoint projection, observation/completeness heads, and application record before success can be authoritative.

## 11. Anti-false-green implementation prohibitions

Production code, registries, derivation authorities, classifiers, and semantic disposition machinery must not use:
- WDPC case IDs to choose behavior;
- fixture branch IDs;
- fixture-provided expected endpoints;
- reviewer finding IDs as runtime predicates;
- diagnostic-string → endpoint parsing;
- caller-controlled phase/rank/precedence;
- candidate-owned registries as the sole universe source;
- caller boolean as material-discovery authority;
- self-produced evidence as independent without governed proof;
- static named lists as the complete omission-sensitive universe;
- fixture-specific condition descriptors;
- fixture-specific materiality classifications;
- fixture-specific normative clause dispositions;
- test-specific sentence recognition;
- synthetic evidence created only to satisfy a falsification expectation.

Any such mechanism invalidates the remediation even if tests turn green.

## 12. Implementation workstreams after exact design approval

Implementation remains **NOT STARTED**.

Only after exact clean approval:

R1 — Evidence classes, predicate evaluator contracts, independent condition universe.

R2 — Predicate evaluation records, complete coverage record, atomic observation binding.

R3 — Canonical endpoint projector and decision/apply/proof digest binding.

R4 — Material observation ledger, independent structure enumeration, materiality classifier.

R5 — Plural universe derivation, common independence rules, durable completeness ledger.

R6 — Capability provenance, writer/effect-path closure, authoritative discovery latch.

R7 — Independent normative clause enumeration and semantic disposition.

R8 — Reviewer-safe proof/audit integration and regression wiring.

The implementation branch must descend from the frozen I10 implementation lineage, not from a scientific-result or review-history branch.

## 13. Successor verification discipline

A repaired implementation is a new candidate.

Before successor falsification:
1. freeze exact successor commit/tree;
2. build a successor verification packet bound to that candidate;
3. obtain a fresh clean independent review of that exact verification packet;
4. only then execute successor cases.

Minimum successor deterministic/reference rerun:
- all 44 already executed V24 deterministic/reference cases;
- same-mechanism positives only after negatives qualify;
- affected unit/construction/integration tests;
- affected inherited WDPC-01…430 subset;
- full inherited WDPC-01…430 regression before qualification because repair crosses endpoint/apply/completeness boundaries.

Explicit unresolved treatment:
- WDPC-469 stays `BLOCKED_BY_I1_SEMANTIC_QUALIFICATION` until I1 semantic qualification exists;
- WDPC-495 stays `BLOCKED_BY_I1_SEMANTIC_QUALIFICATION` until I1 semantic qualification exists;
- WDPC-503 stays `STATIC_OR_MANUAL_REQUIRED / NOT_EXECUTED` until exact qualifying implementation/static evidence exists;
- these cases are excluded from PASS counts/qualification while unresolved;
- external/manual-required cases without qualifying evidence remain non-PASS and cannot be synthetically promoted.

Historical REDs remain append-only and are never retroactively converted to PASS.

## 14. Required clean review attacks

The reviewer should actively attempt to falsify at least:

1. Can a true predicate disappear through non-evaluation?
2. Can a producer mark a true predicate false without governed negative evidence?
3. Can a producer choose `NOT_APPLICABLE`?
4. Can the evaluator contract registry omit an active predicate?
5. Can the condition registry omit a true condition while no runtime emission exposes the omission?
6. Can condition-universe derivation depend only on the candidate registry?
7. Can two nominally independent derivations share one controlling source?
8. Can the evidence-class registry self-qualify?
9. Can the material-candidate enumerator omit the structure that implements the enumerator/classifier itself?
10. Can the materiality classifier owner classify its own structure non-material?
11. Can a newly introduced omission-sensitive structure escape because it is unknown?
12. Can a discovery observation be lost before decision/apply?
13. Can an effect path bypass observation-head consumption?
14. Can a table/registry digest drift after decision yet apply still succeed?
15. Can process-memory/local-cache completeness become current?
16. Can a completeness ledger fork/rollback appear current?
17. Can capability self-report masquerade as independent measurement?
18. Can shared cloud/root/CI/CD/KMS/recovery control masquerade as independence?
19. Can plural universe derivations disagree and root/operator pick one?
20. Can a new normative clause evade structural enumeration?
21. Can the normative artifact/catalog owner self-disposition a material clause as non-normative?
22. Can ambiguity default to non-authoritative?
23. Can atomicity be asserted without a verifiable binding record?
24. Can test IDs/expected endpoints populate runtime registries or classifiers?
25. Can any successor workflow rewrite historical REDs or count unresolved cases as PASS?

## 15. Required clean review output

A. `SELF_CONTAINED_BINDING = CONSISTENT | INCONSISTENT | INSUFFICIENT_PACKET_CONTENT`

B. Overall disposition:
`READY_FOR_IMPLEMENTATION | NEEDS_REVISION | INSUFFICIENT_TO_ASSESS`

C. Critical findings

D. High / Medium / Low findings

E. Predicate-evaluation coverage audit

F. Condition/evaluator universe completeness audit

G. Endpoint projection and drift audit

H. Material-structure enumeration/classification audit

I. Observation/apply race and atomicity audit

J. Independence/provenance audit

K. Completeness-ledger anchoring/currentness audit

L. Normative-clause enumeration/disposition audit

M. Historical-result / successor-binding audit

N. Anti-case-specific-hardcoding audit

O. Missing contracts / false-green paths

End exactly:

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`

Do not prepend a reviewer-type declaration.

## 16. Implementation gate

This packet grants no implementation, merge, release, deployment, qualification, production, adjudication, or terminal authority.

Implementation may begin only after:
- this exact V2 packet receives `SELF_CONTAINED_BINDING = CONSISTENT`;
- disposition is `READY_FOR_IMPLEMENTATION`;
- repository-connected adjudication verifies the response binds to this exact V2 packet/body identity;
- no unresolved blocking design-review finding remains.

Any semantic change to this design creates a successor packet and requires fresh clean review.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
