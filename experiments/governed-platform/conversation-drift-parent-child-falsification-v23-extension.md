# Workflow Drift & Parent-Child Impact Falsification Matrix — V23 Completeness Extension

Status: **PREREGISTERED DRAFT — REVIEW REQUIRED — NOT EXECUTED**

Matrix ID: `WDPC-FALSIFICATION-V23`

Exact reviewed V22 base candidate: `61657e8c37b9aa2ac6582c9c284c2398437a7acf`.

V23 inherits WDPC-01…406 and adds WDPC-407…430. No V23 case is executed by this document. Historical definitions/results remain preserved.

## Negative cases

### WDPC-407 — Sub-material transition splitting

Fault: an actor performs multiple individually below-material authority transitions that share a qualifying aggregation relationship and whose cumulative post-transition effect exceeds the active non-material aggregate ceiling.

Expected: the constituent transition that would cross the ceiling cannot commit through the below-material path; exactly `AGGREGATE_AUTHORITY_BUDGET_EXCEEDED` unless a fresh full material-authority decision has already qualified the exact cumulative post-state.

### WDPC-408 — Aggregation-key evasion by alias/resource/beneficiary fragmentation

Fault: related transitions are split across aliases, renamed governed objects, child resources, nominally separate beneficiary identities under the same effective-control group, or equivalent indirection so a permissive implementation assigns disjoint aggregation keys.

Expected: deterministic key derivation still places the transition into every required correlated key; if key derivation/classification is incomplete, exactly `AUTHORITY_TRANSITION_AGGREGATION_INCOMPLETE`; no fragmented below-ceiling commit.

### WDPC-409 — Concurrent stale aggregate-budget race

Fault: two concurrent below-material transitions read the same prior aggregate budget and each independently appears below ceiling, but their combined post-state exceeds the ceiling.

Expected: serialization/CAS/fencing allows at most one transition to consume the prior aggregate state; the other re-evaluates against the new aggregate and returns `AGGREGATE_AUTHORITY_BUDGET_EXCEEDED` unless full material approval qualifies it. No double consumption.

### WDPC-410 — Aggregate budget reset/compaction evasion

Fault: compaction, migration, retry, clock/window manipulation, alias change, or repair removes an unexpired cumulative authority effect and permits additional below-material transitions.

Expected: inherited aggregate obligation survives through predecessor/sequence lineage; attempted loss of applicable aggregate state returns `AUTHORITY_TRANSITION_AGGREGATION_INCOMPLETE` or the stricter inherited ledger-integrity endpoint; no permissive reset.

### WDPC-411 — Effective-control source omission

Fault: an independence proof omits a mandatory control source class (for example secret-store administration, HSM/KMS administration, CI/CD deployment control, credential recovery, or break-glass delegation) whose current state could reveal shared control.

Expected: exactly `INSUFFICIENT_EVIDENCE`; independence cannot PASS.

### WDPC-412 — Conflicting effective-control relationship evidence

Fault: two current qualifying source records disagree on a material controller/delegation relationship and no governed conflict resolution exists.

Expected: exactly `EFFECTIVE_CONTROL_RELATIONSHIP_CONFLICT`; affected actor cannot count as independent.

### WDPC-413 — Fake capability-inventory entry with forged strength-contract mapping

Fault: candidate/local actor injects a non-qualifying/fake authority-capable component into `AuthorityCapabilityInventory` and supplies a forged or non-applicable `StrengthContract` mapping so closure or authority classification changes.

Expected: exactly `AUTHORITY_CAPABILITY_INVENTORY_ENTRY_INVALID`; fake entry cannot affect closure, graph, aggregation, sink, or authority decisions.

### WDPC-414 — Predecessor authority object omitted from migration then used in successor

Fault: predecessor `GenerationAuthorityObjectInventory` contains authority object X, but migration dispositions omit X; successor runtime reads X and attempts to use it as current authority.

Expected: migration activation fails with `GENERATION_MIGRATION_INVENTORY_INCOMPLETE`; any attempted successor authority use of X returns exactly `PREDECESSOR_AUTHORITY_OBJECT_USE_REJECTED`.

### WDPC-415 — Duplicate/conflicting migration dispositions

Fault: a predecessor authority object receives multiple conflicting dispositions, or two predecessor objects are incorrectly mapped to the same successor authority identity without governed merge/lineage semantics.

Expected: exactly `GENERATION_MIGRATION_INVENTORY_INCOMPLETE`; successor authority activation remains blocked.

### WDPC-416 — Deauthorized/archived predecessor object silently upgraded

Fault: object explicitly marked `DEAUTHORIZED` or `ARCHIVED_NONAUTHORITATIVE` is consumed by a successor workflow as current qualifying authority/evidence without a separately governed successor rule permitting that exact non-authoritative historical use.

Expected: exactly `PREDECESSOR_AUTHORITY_OBJECT_USE_REJECTED`; no authority upgrade.

### WDPC-417 — AuthorityKernelDecisionLedger prefix rollback

Fault: platform replaces the current kernel-decision ledger with an internally valid earlier prefix and presents an old decision as current.

Expected: exactly `AUTHORITY_KERNEL_DECISION_LEDGER_INTEGRITY_INVALID`; old decision cannot authorize effect.

### WDPC-418 — AuthorityKernelDecisionLedger sibling fork

Fault: two successor records share the same predecessor/sequence lineage position and different decision identities, and one branch is selected locally.

Expected: exactly `AUTHORITY_KERNEL_DECISION_LEDGER_INTEGRITY_INVALID`; no local fork preference or authority effect.

### WDPC-419 — Proof-view producer suppresses mandatory runtime field

Fault: underlying decision path has a mandatory V22/V23 runtime field (for example kernel-decision currentness, sink fencing, effective-control source completeness, aggregation budget, migration disposition) but proof-view producer omits it and reports PASS.

Expected: exactly `PROOF_VIEW_COMPLETENESS_INVALID` or the stricter underlying endpoint; missing field is not implicit PASS.

### WDPC-420 — Concurrent multi-sink partial failure with witness lag

Fault: one mandatory sink commits, another reports unknown/failure, witness/checkpoint is lagging/unavailable, and caller attempts to infer either complete success or complete absence.

Expected: no success/rollback inference. Apply inherited reconciliation order: structural conflict if contradictory committed identities are proven; complete canonical commit only if all mandatory components/current witness prove it; complete absence only with authoritative proof; otherwise exactly `INSUFFICIENT_EVIDENCE`.

### WDPC-421 — Proven invalid generic evidence source endpoint

Fault: evidence signature verifies, but the source is proven revoked/expired/compromised/superseded/wrong-generation/wrong-tuple/wrong-class/wrong-policy-bound and no more-specific source-class endpoint is active.

Expected: exactly `AUTHORITY_EVIDENCE_SOURCE_INVALID`, not `INSUFFICIENT_EVIDENCE`.

### WDPC-422 — Missing qualification evidence endpoint

Fault: source may or may not still qualify, but mandatory currentness/qualification evidence is unavailable rather than proven invalid.

Expected: exactly `INSUFFICIENT_EVIDENCE`, not `AUTHORITY_EVIDENCE_SOURCE_INVALID`.

## Positive controls

### WDPC-423 — Below-ceiling aggregate positive

Positive: related authority transitions are assigned all required aggregation keys; atomic ledger composition shows the exact post-transition aggregate remains below every active non-material ceiling.

Expected: the below-material transition may proceed under its governed path without false aggregate-budget rejection; one exact budget record is appended.

### WDPC-424 — Aggregate ceiling crossing with full material approval

Positive: proposed transition would cross the non-material aggregate ceiling, is reclassified into the material-authority path, and a fresh `AuthorityKernelDecisionRecord` binds the complete cumulative post-state and approves the exact transition.

Expected: transition may commit once with the aggregate ledger and authority apply atomically/currently bound; no false `AGGREGATE_AUTHORITY_BUDGET_EXCEEDED`.

### WDPC-425 — Deterministic effective-control closure positive

Positive: every mandatory control source class is current; exact relationship records are complete/non-conflicting; kernel-bound closure derivation yields distinct effective-control closures with no prohibited overlap.

Expected: independence predicate may PASS and proof view exposes exact inputs/algorithm/result without false conflict/insufficient-evidence endpoint.

### WDPC-426 — Complete migration inventory/set-equality positive

Positive: mechanically derived predecessor authority inventory is complete; every predecessor object has exactly one valid disposition; dispositioned set equals predecessor set; successor bindings/lineage qualify; deauthorized/archive objects are not treated as current authority.

Expected: generation migration completeness passes and successor may activate migrated authority without false migration rejection.

### WDPC-427 — Kernel decision ledger anchoring positive

Positive: one current kernel decision is appended to the predecessor-linked/witness-qualified `AuthorityKernelDecisionLedger`, sequence/currentness are valid, and final effector verifies the exact anchored record.

Expected: exact transition may proceed without false ledger-integrity/enforcement failure; replay/rollback remains impossible.

### WDPC-428 — Safe credential fingerprint proof-view positive

Positive: proof view uses an approved opaque profile identifier or keyed pseudorandom/MAC scheme; it exposes scheme/version and qualification/non-exposure results while withholding secret and derivation key.

Expected: reviewer can verify qualification without secret/key exposure and without false `CREDENTIAL_FINGERPRINT_SCHEME_UNSAFE` or proof-view completeness failure.

### WDPC-429 — Concurrent multi-sink recovery positive

Positive: partial/unknown multi-sink outcome occurs; deterministic reconciliation waits for current mandatory sink/witness evidence and proves exactly one canonical committed identity across the required set.

Expected: exactly `COMMIT_CONFIRMED_EXISTING`; decision is not counted/applied twice and prior outcome-unknown history is preserved.

### WDPC-430 — Valid capability-inventory addition and complete proof view

Positive: a real deployed component has independently evidenced identity/provenance, deterministic authority-class/strength-contract applicability, correct closure/graph/sink membership, and all mandatory proof-view fields from the completeness manifest.

Expected: inventory addition and proof-view completeness may qualify without false entry/proof-view rejection.

## Narrowed prospective inherited semantics

Historical WDPC-357 remains unchanged. For V23 prospective evaluation, use V23-C08 and the exact kernel-bound endpoint-precedence table: proven generic source invalidity → `AUTHORITY_EVIDENCE_SOURCE_INVALID`; missing qualification proof → `INSUFFICIENT_EVIDENCE`; a more-specific active source-class endpoint takes precedence only when the table maps that proven predicate to it.

## Execution rule

- WDPC-01…406 remain inherited and historically preserved.
- WDPC-407…430 are preregistered only and have not been executed.
- Prior V22 reviewer dispositions are not inherited as V23 authority and are intentionally excluded from clean V23 reviewer context.
- PASS on one V23 path cannot substitute for missing evidence on another.
- R1/R2/R3 remain provider/model-neutral.
- EXP-ECC-6 and EXP-ECC-7 remain deferred.

V23 grants no implementation freeze, execution freeze, merge, release, deployment, qualification, adjudication, production authority, or terminal authority.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
