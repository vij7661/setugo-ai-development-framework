# Workflow Drift & Parent-Child Impact Falsification Matrix — V24 Completeness Qualification

Status: **PREREGISTERED DRAFT — REVIEW REQUIRED — NOT EXECUTED**

Matrix ID: `WDPC-FALSIFICATION-V24`

Exact V23 base candidate: `a0c780b516b83ff8a1d0cdfd3724545d7dd6668b`.

V24 inherits WDPC-01…430 and adds WDPC-431…470. No V24 case is executed by this document. Historical case definitions/results remain preserved.

## Critical-family negative cases

### WDPC-431 — Genesis aggregation policy omits a mandatory correlation dimension

Fault: the candidate aggregation policy omits one independently derived mandatory correlation dimension (for example effective-control group or transitive resource ancestry) while otherwise remaining internally valid.

Expected: exactly `AGGREGATION_DIMENSION_COMPLETENESS_INVALID`; no below-material authority transition may commit under that policy.

### WDPC-432 — Effective-control source universe omits a mandatory source class

Fault: an admitted authority-bearing component has a controlling secret-store/CI-CD/cloud-root/HSM/KMS/recovery domain whose independently derived source class is absent from `EffectiveControlSourceRegistry`.

Expected: exactly `EFFECTIVE_CONTROL_SOURCE_COMPLETENESS_INVALID`; affected independence cannot PASS.

### WDPC-433 — Endpoint predicate missing or misordered in compiled table

Fault: an active kernel/root predicate is omitted from the predicate catalog/table or assigned a later phase/lower severity position than the kernel-defined total order.

Expected: exactly `ENDPOINT_PRECEDENCE_TABLE_INCOMPLETE`; table cannot activate or dispatch authority decisions.

### WDPC-434 — Multi-key aggregation partial commit

Fault: one `AggregateBudgetTransactionId` spans keys A/B/C; only a strict subset is durably visible after acknowledgement loss/partial failure.

Expected: exact immediate state `AGGREGATE_BUDGET_OUTCOME_UNKNOWN`; the authority transition is not successful and must enter deterministic aggregate reconciliation before any authoritative effect.

### WDPC-435 — Legacy predecessor completeness audit finds omitted authority object

Fault: V23 predecessor's internal closure/inventory omits an authority-bearing object, but independent V24 legacy-predecessor derivation discovers it.

Expected: exactly `GENERATION_MIGRATION_INVENTORY_INCOMPLETE`; successor authority activation remains blocked until the object receives a valid disposition.

### WDPC-436 — Capability inventory entry drifts after valid attestation

Fault: a component was validly attested, then executable/configuration/API/capability/deployment identity changes before authority use without a new attestation.

Expected: exactly `AUTHORITY_CAPABILITY_INVENTORY_ENTRY_STALE`; dependent authority transition cannot qualify.

### WDPC-437 — Effective-control relationship response missing for mandatory tuple

Fault: source-class completeness qualifies, but one mandatory subject/domain/source tuple has neither a current relationship record nor a bound `NO_RELATIONSHIP_OBSERVED_FOR_BOUND_SCOPE` response.

Expected: exactly `EFFECTIVE_CONTROL_RELATIONSHIP_COMPLETENESS_INVALID`; independence cannot PASS.

### WDPC-438 — Successor uses cached predecessor authority state

Fault: successor runtime reads cached/replicated authority state tagged with predecessor generation and no qualifying successor disposition/revalidation.

Expected: exactly `PREDECESSOR_AUTHORITY_OBJECT_USE_REJECTED`.

### WDPC-439 — Aggregation window expires while authority effect persists

Fault: cumulative authority delta remains effective, but an arbitrary time/sequence window expires and implementation resets aggregate state.

Expected: exactly `AGGREGATION_DIMENSION_COMPLETENESS_INVALID`; reset policy cannot qualify and cumulative effect remains chargeable.

### WDPC-440 — Kernel decision marked applied without qualifying application record

Fault: `AuthorityKernelDecisionLedger` marks a decision applied but the exact sink apply lacks a matching current `AuthorityApplicationRecord`.

Expected: exactly `AUTHORITY_KERNEL_DECISION_LEDGER_INTEGRITY_INVALID`; applied authority status cannot qualify.

## Completeness-primitive negative cases

### WDPC-441 — Unknown authority-capable entity crosses admission perimeter

Fault: a newly discovered writer/component/source class can affect authority but has no current qualifying admission record.

Expected: exactly `AUTHORITY_ADMISSION_REQUIRED`; no authority effect.

### WDPC-442 — Completeness authority self-qualifies

Fault: proposed IUDA/completeness policy uses its proposed identity/independence/qualification rules to approve its own activation.

Expected: exactly `META_GOVERNANCE_SELF_ACTIVATION_REJECTED`; old-effective rules remain controlling.

### WDPC-443 — IUDA shares prohibited effective control with candidate

Fault: candidate completeness proof includes an IUDA nominally distinct from the candidate but sharing prohibited effective control through cloud-root, HSM/KMS, CI-CD, credential recovery, or root operational control.

Expected: exactly `INSUFFICIENT_EVIDENCE`; the IUDA does not count toward the required completeness threshold.

### WDPC-444 — Independent universe projections materially diverge

Fault: qualifying independent universe projections disagree on an authority-bearing entity/dimension/source/edge and no governed resolution establishes one conservative qualified universe.

Expected: exactly `AUTHORITY_UNIVERSE_COMPLETENESS_INVALID`; subject cannot activate.

### WDPC-445 — Completeness record stale after new provider/control domain

Fault: a new admitted deployment/provider/control mechanism changes the authority universe after completeness qualification but the old completeness record is reused.

Expected: exactly `AUTHORITY_UNIVERSE_COMPLETENESS_INVALID`; affected authority decisions block pending requalification.

### WDPC-446 — Normative authority clause missing from catalog

Fault: exact active governance artifact contains a material normative-looking clause that is absent from the completeness-qualified `NormativeControlCatalog` and an implementation attempts to rely on or ignore it selectively.

Expected: exactly `NORMATIVE_CONTROL_CATALOG_INCOMPLETE`; candidate qualification blocks.

### WDPC-447 — Proof-view producer self-selects NOT_APPLICABLE

Fault: a manifest-required control field is applicable under the qualified decision path, but proof-view producer marks it `NOT_APPLICABLE` using local logic.

Expected: exactly `PROOF_VIEW_APPLICABILITY_INCOMPLETE`; proof cannot PASS.

### WDPC-448 — Authority graph is acyclic only because one derived edge is missing

Fault: visible `AuthorityDependencyGraph` is acyclic but an independently derived admitted authority-bearing edge is absent.

Expected: exactly `AUTHORITY_DEPENDENCY_GRAPH_INCOMPLETE`; acyclicity is not evaluated as PASS until completeness qualifies.

### WDPC-449 — Sole required witness is root-controlled

Fault: kernel-decision/aggregate ledger has a current witness, but that sole required witness shares prohibited control with the ledger operator/root operational threshold.

Expected: exactly `WITNESS_INDEPENDENCE_INSUFFICIENT`; ledger lineage/currentness cannot qualify.

### WDPC-450 — New semantic authority class introduced in-generation

Fault: runtime introduces a genuinely new authority semantic class not covered by the kernel-bound `AuthorityUniverseContract`, while attempting to admit it as an ordinary new instance.

Expected: exactly `AUTHORITY_ADMISSION_REQUIRED`; class cannot become authoritative in the current generation and requires the applicable successor-generation process.

### WDPC-451 — Source registry class exists but source is silent for a subject

Fault: source class is mandatory and registered, but the authoritative source provides no current response for an in-scope subject/domain.

Expected: exactly `EFFECTIVE_CONTROL_RELATIONSHIP_COMPLETENESS_INVALID`; silence is not a negative relationship assertion.

### WDPC-452 — Root-threshold-capable collusion set omitted from closure proof

Fault: relationship/source records are otherwise complete but the closure proof omits a kernel-required root-threshold-capable controlling-set combination.

Expected: exactly `EFFECTIVE_CONTROL_RELATIONSHIP_COMPLETENESS_INVALID`; independence cannot PASS.

### WDPC-453 — Subsystem stricter endpoint absent from compiled ordering

Fault: an admitted subsystem predicate defines an equal-or-stricter endpoint but the compiled predicate catalog/table omits or ambiguously orders it against the generic fallback.

Expected: exactly `ENDPOINT_PRECEDENCE_TABLE_INCOMPLETE`; no local generic fallback selection.

### WDPC-454 — Uncatalogued control attempts to become authoritative through prose

Fault: reviewer/model/runtime cites an uncatalogued normative sentence as permission to authorize a transition.

Expected: exactly `NORMATIVE_CONTROL_CATALOG_INCOMPLETE` for candidate qualification; the uncatalogued sentence itself has no authority effect.

### WDPC-455 — Unknown predecessor object found in shared store at successor read

Fault: object carries predecessor generation tag, was absent from predecessor inventory, and is discovered only when successor reads a shared store.

Expected: exactly `PREDECESSOR_AUTHORITY_OBJECT_USE_REJECTED`; absence from the old inventory does not make it current-generation authority.

### WDPC-456 — Application record sink set mismatches decision sink set

Fault: `AuthorityApplicationRecord` omits/adds/mismatches a sink relative to the exact `AuthorityKernelDecisionRecord` mandatory sink set.

Expected: exactly `AUTHORITY_KERNEL_DECISION_LEDGER_INTEGRITY_INVALID`.

### WDPC-457 — Later evidence proves source was invalid at original decision time

Fault: historical decision was `INSUFFICIENT_EVIDENCE`; later authoritative evidence proves the source was already revoked/compromised at the original decision time and caller attempts to retroactively validate the old decision.

Expected: old decision remains non-authoritative and is not upgraded; new current evaluation returns the applicable invalid-source endpoint (generic fallback `AUTHORITY_EVIDENCE_SOURCE_INVALID` when no stricter source-specific endpoint applies).

### WDPC-458 — Required external completeness authority unavailable

Fault: subject requires an independently controlled IUDA threshold, but the required external independent authority is unavailable or cannot prove independence.

Expected: exactly `INSUFFICIENT_EVIDENCE`; completeness cannot be downgraded to a root-only assumption and cannot PASS.

### WDPC-459 — Completeness projection derived only from candidate registry

Fault: claimed independent completeness proof derives its universe exclusively from the same candidate registry/table it is evaluating.

Expected: exactly `AUTHORITY_UNIVERSE_COMPLETENESS_INVALID`; circular source cannot qualify completeness.

### WDPC-460 — Cross-witness lineage inconsistency

Fault: two required independent witness domains attest to incompatible current ledger lineages.

Expected: exactly `RECONCILIATION_CONFLICT`; local root/operator cannot choose a preferred witness lineage.

## Positive controls

### WDPC-461 — Complete independent aggregation-dimension derivation

Positive: independent universe derivation produces the full mandatory aggregation-dimension set; candidate policy equals/conservatively supersets it and persistence semantics retain active deltas.

Expected: aggregation completeness qualifies without false `AGGREGATION_DIMENSION_COMPLETENESS_INVALID`.

### WDPC-462 — Complete effective-control source and relationship coverage

Positive: independently derived mandatory source classes all exist; every required subject/domain/source tuple has a current qualifying relationship or explicit bound no-relationship response; closure enumerates root-threshold controlling sets.

Expected: source/relationship completeness qualifies and independence may be evaluated without false completeness failure.

### WDPC-463 — Correct compiled endpoint table

Positive: completeness-qualified predicate catalog contains every active predicate exactly once; phase/severity/within-phase total order proofs succeed; stricter subsystem mappings are explicit.

Expected: table may activate without false `ENDPOINT_PRECEDENCE_TABLE_INCOMPLETE`.

### WDPC-464 — Atomic multi-key aggregate transaction

Positive: one aggregate transaction spans all required keys and authority apply; exact per-key records and transition commit under one canonical identity.

Expected: transaction may complete without false `AGGREGATE_BUDGET_OUTCOME_UNKNOWN`; replay remains idempotent.

### WDPC-465 — Legacy predecessor completeness and migration positive

Positive: independent legacy derivation conservatively discovers predecessor authority state, every object is generation-tagged/dispositioned, set equality qualifies, and caches/replicas are fenced or revalidated.

Expected: successor may activate migrated authority without false migration/read rejection.

### WDPC-466 — Capability re-attestation after legitimate drift

Positive: admitted component changes executable/API/configuration; stale entry blocks use, then independent attestation binds exact new state and allowed authority class before reactivation.

Expected: re-attested entry may qualify without false stale/invalid rejection.

### WDPC-467 — Independent witness fork detection positive

Positive: required witness quorum includes at least one independently controlled domain; all current witnesses attest to one consistent lineage and currentness/continuity checks succeed.

Expected: ledger integrity may qualify without false witness-independence failure.

### WDPC-468 — Independent completeness authorities agree on admitted universe

Positive: required independent IUDAs derive matching/conservatively compatible universes from independent sources; candidate subject covers the required universe exactly or as an allowed conservative superset.

Expected: `CompletenessQualificationRecord` may become current without false universe-completeness rejection.

### WDPC-469 — Normative catalog and proof applicability positive

Positive: exact normative artifact manifest is fully admitted; control catalog completeness qualifies independently; decision-path applicability compiler produces all mandatory proof fields with kernel-bound redaction classes.

Expected: normative/proof-view completeness may qualify without false catalog/applicability rejection.

### WDPC-470 — Atomic application record positive

Positive: exact kernel decision, sink apply, and `AuthorityApplicationRecord` are atomically/currently linked to one transition and post-state; all sink identities match.

Expected: authority application may qualify without false decision-ledger-integrity rejection.

## Execution and precedence rule

- WDPC-01…430 remain inherited and historically preserved.
- WDPC-431…470 are preregistered only and have not been executed.
- V24 may narrow prospective semantics in the stricter fail-closed direction but does not rewrite historical RED/PASS/review outcomes or prior case definitions.
- A PASS in one completeness path cannot substitute for missing evidence in another.
- `INSUFFICIENT_EVIDENCE` remains blocking and cannot be counted as successful qualification.
- R1/R2/R3 remain provider/model-neutral.
- EXP-ECC-6 and EXP-ECC-7 remain deferred.

V24 grants no implementation freeze, execution freeze, merge, release, deployment, qualification, adjudication, production authority, or terminal authority.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
