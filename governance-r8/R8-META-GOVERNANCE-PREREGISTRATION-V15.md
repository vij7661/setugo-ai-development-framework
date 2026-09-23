# R8 Meta-Governance Redesign v15 — Narrow Review-Closure Successor

Status: **PREREGISTERED_DESIGN_V15 — NOT_IMPLEMENTED — INTERNAL_NORMALIZATION_REQUIRED**
Authority effect: **NONE**

Effective lineage:
- R8 v4 through v14 remain immutable historical design layers.
- R8 v15 is a narrow successor to the adjudicated v14 normalized-review findings.
- R8 v15 does not reopen unrelated trust-root, resolver, sealing, rotation, or external-effect semantics.
- Where this document is more specific than v14 normalization, this document governs the v15 normalized candidate.

Adjudication basis:
- `review-adjudications/R8-V14-NORMALIZED-DEEPSEEK-REVIEW-ADJUDICATION-2026-09-23.md`

## 1. Objective

R8 v15 closes the remaining normalized-review surface defects without weakening inherited safety semantics.

Core constraints:
1. do not mutate v14;
2. do not delete valid SRTT rows merely because a reviewer inferred a stronger label relationship than the inherited rule defines;
3. make every generated authority-relevant table independently traceable to declared machine-readable rules;
4. make review projection deterministic rather than heuristic;
5. make multi-revoked composition and cross-mechanism closure explicit;
6. preserve fail-closed behavior when qualified dependencies are unavailable.

## 2. SRTT-4 — explicit fixed domain and rule registry

### R8V15-I001 — fixed replacement domain

SRTT-4 is total only over replacement evaluation.

Machine-readable domain:
- `domain_fixed.source_entry_state = REVOKED`;
- variable dimensions are exactly:
  - `old_scope_match = {NO_MATCH, EXACT_MATCH}`;
  - `destination_scope_match = {NO_MATCH, EXACT_MATCH, MAPPED_MATCH}`;
  - `old_scope_effect = {BLOCK_OLD_SCOPE, REPLACE_OLD_SCOPE_FOR_EXACT_MATCH, REPLACE_OLD_SCOPE_FOR_MAPPED_MATCH}`;
  - `scope_relation = {SAME, NARROWER, BROADER, DISJOINT}`;
  - `any_permission_valid = {false,true}`;
  - `mapping_effective = {false,true}`;
  - `lineage_mapping_valid = {false,true}`;
  - `scope_expansion_authorized = {false,true}`;
  - `decision_inside_authorized_expansion_domain = {false,true}`.

Total row count is therefore exactly 2304.

A non-REVOKED source is outside SRTT-4's table domain and is classified before table lookup as `NOT_A_REPLACEMENT_BRANCH`.

### R8V15-I002 — dedicated SRTT rule registry

A frozen machine-readable `SRTT-4-RuleRegistry` defines every decisive rule used by the table.

Each rule record contains:
- `rule_id`;
- `precedence`;
- `predicate`;
- `result`;
- `source_trace`.

Every table row references exactly one declared `rule_id`.

Undefined, duplicate, or semantically conflicting decisive-rule IDs cause `SRTT_RULE_REGISTRY_INVALID`.

### R8V15-I003 — exact precedence

For an in-domain REVOKED source tuple, SRTT-4 evaluates in this exact order:

1. `mapping_effective = false` -> `SEMANTIC_SCOPE_REVOKED`;
2. `lineage_mapping_valid = false` -> `SEMANTIC_SCOPE_REVOKED`;
3. `any_permission_valid = false` -> `SEMANTIC_SCOPE_PERMISSION_REEVALUATION_REQUIRED`;
4. `old_scope_match = NO_MATCH` -> `MAPPING_NOT_APPLICABLE`;
5. `old_scope_effect = BLOCK_OLD_SCOPE` -> `SEMANTIC_SCOPE_REVOKED`;
6. `destination_scope_match = NO_MATCH` -> `SEMANTIC_SCOPE_REVOKED`;
7. exact-effect rule;
8. mapped-effect SAME/NARROWER rule;
9. mapped-effect BROADER rule;
10. mapped-effect invalid remainder.

No later rule may override an earlier blocker.

### R8V15-I004 — exact replacement semantics

For `REPLACE_OLD_SCOPE_FOR_EXACT_MATCH`:
- destination must be `EXACT_MATCH`;
- relation must be `SAME`;
- when both hold -> `REPLACEMENT_ELIGIBLE`;
- otherwise -> `SEMANTIC_SCOPE_REPLACEMENT_INVALID`.

No NARROWER, BROADER, MAPPED_MATCH, or DISJOINT result is eligible under exact effect.

### R8V15-I005 — mapped replacement semantics preserved exactly

For `REPLACE_OLD_SCOPE_FOR_MAPPED_MATCH`:

- relation `SAME` with destination `EXACT_MATCH` or `MAPPED_MATCH` -> `REPLACEMENT_ELIGIBLE`;
- relation `NARROWER` with destination `EXACT_MATCH` or `MAPPED_MATCH` -> `REPLACEMENT_ELIGIBLE`;
- relation `BROADER` with destination `EXACT_MATCH` or `MAPPED_MATCH` -> eligible only when:
  - `scope_expansion_authorized = true`; and
  - `decision_inside_authorized_expansion_domain = true`;
- otherwise -> `SEMANTIC_SCOPE_REPLACEMENT_INVALID`.

The `old_scope_effect` value is not derived from `destination_scope_match`.

A mapped-replacement branch may terminate at an exact-matching destination. Such a tuple is not malformed merely because the destination is `EXACT_MATCH`.

This preserves canonical v13 I013 and rejects the false assumption that "mapped effect" implies destination must be `MAPPED_MATCH`.

### R8V15-I006 — broader expansion remains constitutional only

BROADER eligibility requires the inherited `SEMANTIC_SCOPE_EXPANSION_AMENDMENT` and a CSM-bound `AuthorizedExpansionDomain`.

Ordinary policy, resolver-local logic, table-generation metadata, or a destination match cannot manufacture expansion authorization.

### R8V15-I007 — table generation and verification

The SRTT-4 table generator:
- consumes only the frozen fixed domain, enum order, and SRTT-4 RuleRegistry;
- enumerates all 2304 variable tuples exactly once;
- applies the lowest-precedence-number matching rule;
- emits exactly one result and one decisive_rule_id per row;
- rejects generation when zero or multiple same-precedence rules match;
- emits a deterministic distribution summary;
- is verified independently by re-evaluating every row from RuleRegistry predicates.

The distribution is diagnostic only and is never evidence of correctness by itself.

## 3. Guard-omission range closure

### R8V15-I008 — deterministic case-range expansion

When a legacy guard table uses compact case syntax such as `V4-024..V4-030`, the omission generator must expand every inclusive identifier before registry comparison.

For G008, the required expanded set is:
`V4-024,V4-025,V4-026,V4-027,V4-028,V4-029,V4-030`.

The final omission manifest stores only explicit case IDs; shorthand ranges are not permitted in `referenced_case_ids`.

### R8V15-I009 — omission proof is set equality

For every omitted legacy table:
- parse every guard record;
- expand every case reference;
- compute the exact set of referenced case IDs;
- require equality between parsed source set and manifest set;
- require every manifest case in current CaseRegistry;
- require every guard ID in current GuardRegistry;
- preserve unique case/invariant semantics.

A subset check is insufficient.

Mismatch -> `REVIEW_PACKET_INCOMPLETE`.

## 4. BSP-5 — deterministic current-status and semantic-test contexts

### R8V15-I010 — explicit current-status markers

The generated normalized review source uses exact structural markers:

`<!-- BSP:CURRENT_STATUS_BEGIN version=15 -->`

and

`<!-- BSP:CURRENT_STATUS_END -->`.

Exactly one such block must exist.

The block version must equal `current_candidate_version`.

Zero, multiple, mismatched, nested, or unterminated current-status blocks -> `REVIEW_PACKET_INCOMPLETE`.

### R8V15-I011 — predecessor status classification

Outside the marked current-status block, predecessor status/review classification uses:
- explicit predecessor version tokens;
- predecessor-status/review section state;
- exact status/review metadata grammar.

A status token by itself is never sufficient.

### R8V15-I012 — exact semantic-test parser states

`SEMANTIC_TEST_LITERAL` is allowed only while the parser is in one of:
- `CASE_SECTION`;
- `GUARD_RECORD_SECTION`;
- `FENCED_SEMANTIC_TEST_DATA`.

A normal prose paragraph mentioning a status token is not automatically a semantic-test literal.

Parser state transitions are deterministic and part of BSP-5.

### R8V15-I013 — projection residual proof

After projection:
- re-run BSP-5 from the initial parser state;
- require zero `PRIOR_STATUS`;
- require zero `PRIOR_REVIEW_METADATA`;
- require exactly one valid current-status block;
- require semantic-test records expected by CaseRegistry/GuardRegistry projection to remain present.

Raw token search remains non-authoritative.

## 5. CSRULE-6 — explicit multiple-revoked composition

### R8V15-I014 — complete revoked blocker set

After semantic Smax and current ANY validation, construct the complete set `B` of applicable REVOKED Smax blockers.

No ACTIVE peer is selectable while `B` is non-empty and unresolved.

### R8V15-I015 — per-blocker discharge

For each blocker `b in B`, independently enumerate only explicitly linked successor/replacement paths.

Each path must terminate in:
- an eligible ACTIVE successor; or
- an SRTT-4 `REPLACEMENT_ELIGIBLE` result.

Normalize each successful path to canonical SREP digest.

For one blocker:
- zero valid paths -> `SEMANTIC_SCOPE_REVOKED`;
- more than one non-equivalent digest -> `SEMANTIC_SUCCESSOR_CONFLICT`;
- one unique digest, even if reached by multiple equivalent paths -> blocker uniquely discharged.

### R8V15-I016 — no partial-discharge authority

No discharge result enters final peer selection until every blocker in `B` is uniquely discharged.

If one blocker is discharged and another is unresolved/invalid, the entire resolution remains blocked.

Implementations may evaluate blockers in any deterministic work order, but final authority semantics are set-based and order-independent.

### R8V15-I017 — final composition

After every blocker is uniquely discharged:
1. collect one canonical result digest per blocker;
2. add canonical result digests from genuine directly ACTIVE Smax peers;
3. compare the complete set using SREP;
4. one unique digest -> one semantic result;
5. more than one unique digest -> `SEMANTIC_ENTRY_CONFLICT`.

Equivalent duplicate digests collapse only for result selection; all path/blocker evidence remains preserved.

## 6. Cross-mechanism closure additions

### R8V15-I018 — blocker ordering remains stage-ordered

AIM permission and lifecycle stages occur before RIR/RCS stages.

If an earlier stage blocks, later stages cannot convert that blocker into eligibility.

Diagnostic systems may report additional later defects only if doing so does not execute an authority-bearing path that the earlier blocker prohibited.

### R8V15-I019 — semantic sequence rollback/replay

`semantic_state_sequence` is internally derived from current LAS committed state.

A lower or replayed sequence is invalid even when presented semantic heads superficially match expected digests.

No caller-supplied sequence may authorize historical-state reuse.

### R8V15-I020 — rotation and external-effect interaction

A rotation barrier does not rewrite committed EffectIntent semantics.

During a barrier:
- new covered authority writes obey the frozen barrier policy;
- already committed external-effect reconciliation may continue only using the exact committed intent and current qualified executor/reconciler rules;
- no barrier state may fabricate external success or duplicate logical effect dispatch;
- any authority state required by reconciliation that becomes unavailable fails closed.

### R8V15-I021 — guard semantics and NCG closure

NCG closure requires not only GuardRegistry contiguity but also proof that every guard-referenced case semantic record required by the normalized review surface is preserved or explicitly traceable.

Registry presence without preserved semantics is insufficient.

## 7. Dependency graph semantics

### R8V15-I022 — direct-edge definition

The NCG dependency graph is a directed acyclic graph of **direct authority-relevant consumption/precondition dependencies**, not a transitive-closure graph.

An edge `A -> B` exists only when B directly consumes A's authority state/output or cannot be evaluated without A's current qualified state.

Transitive edges need not be duplicated.

### R8V15-I023 — generated graph, not hand-added reviewer edges

The structured graph is generated from the normalized dependency matrix.

Every matrix row declares direct inputs and direct consumers.

The graph generator:
- emits edges from those declarations;
- proves all nodes referenced by authority evaluation exist;
- proves acyclicity;
- reports orphan nodes and undeclared direct dependencies;
- rejects manual extra edges not traceable to matrix declarations.

Reviewer-suggested edges are evidence to investigate, not authority to mutate the graph.

## 8. Fail-closed transient dependency policy

### R8V15-I024 — temporary unavailability does not weaken authority

Temporary unavailability, expiry, or failure of qualified:
- time proof;
- resolver conformance evidence/harness;
- revocation freshness;
- MTR/BTW freshness;
- required reviewer/evidence dependency;

leaves the affected authority operation blocked.

No stale cache, emergency weaker root, previous PASS token, locally inferred time, or operator override may substitute.

### R8V15-I025 — liveness recovery

A blocked operation may be retried only after:
- the same qualified dependency is restored; or
- a constitutionally authorized successor dependency of equal-or-stronger assurance is active.

The operation is fully re-evaluated against current authority state.

This is intentional safety-over-liveness behavior.

## 9. Additional Guard Catalog v15

| Guard | Mechanism | Positive | Negatives with fault-proof class |
|---|---|---|---|
| G149 | SRTT-4 explicit fixed domain | V15-001 | V15-002 FP5; V15-003 FP5 |
| G150 | SRTT-4 RuleRegistry / decisive-rule traceability | V15-004 | V15-005 FP5; V15-006 FP5 |
| G151 | Guard-omission inclusive range expansion | V15-007 | V15-008 FP5; V15-009 FP5 |
| G152 | BSP-5 explicit current-status binding | V15-010 | V15-011 FP5; V15-012 FP5 |
| G153 | CSRULE-6 multi-revoked composition | V15-013 | V15-014 FP5; V15-015 FP5; V15-016 FP5 |
| G154 | Cross-mechanism rollback/barrier closure | V15-017 | V15-018 FP3; V15-019 FP5 |
| G155 | NCG direct dependency graph generation | V15-020 | V15-021 FP5; V15-022 FP5 |
| G156 | Fail-closed transient dependency policy | V15-023 | V15-024 FP5; V15-025 FP5 |

## 10. R8 v15 preregistered cases

### SRTT fixed domain
- V15-001 generated table declares fixed REVOKED source domain plus 2304 variable tuples -> domain complete.
- V15-002 table contains REVOKED rows but no fixed-domain declaration -> `SRTT_DOMAIN_UNDECLARED`.
- V15-003 generator attempts ACTIVE/SUSPENDED source row inside replacement table -> `SRTT_DOMAIN_VIOLATION`.

### SRTT rule traceability
- V15-004 every row's decisive_rule_id resolves to exactly one frozen RuleRegistry record and recomputation matches -> valid.
- V15-005 row references undeclared decisive rule -> `SRTT_RULE_REGISTRY_INVALID`.
- V15-006 two same-precedence rules match one tuple with different outputs -> `SRTT_CONFLICT`.

### Guard omission
- V15-007 source `V4-024..V4-030` expands to all seven explicit IDs and all are preserved -> omission proof valid.
- V15-008 expansion omits V4-025..V4-029 while endpoints remain -> `REVIEW_PACKET_INCOMPLETE`.
- V15-009 manifest contains case not referenced by omitted source table -> set-equality proof fails.

### BSP
- V15-010 exactly one version-15 marked current status block survives while predecessor review status is removed -> BSP pass.
- V15-011 two current-status blocks or version mismatch -> `REVIEW_PACKET_INCOMPLETE`.
- V15-012 ordinary prose with status token is misclassified as semantic-test literal -> BSP fail.

### Multi-revoked composition
- V15-013 two revoked blockers each uniquely discharge to same SREP digest -> one semantic result, both path evidences retained.
- V15-014 one revoked blocker discharges, second has zero valid path -> `SEMANTIC_SCOPE_REVOKED`; no partial authority.
- V15-015 two blockers uniquely discharge to different SREP digests -> `SEMANTIC_ENTRY_CONFLICT`.
- V15-016 one blocker has two non-equivalent valid discharge paths -> `SEMANTIC_SUCCESSOR_CONFLICT`.

### Cross mechanism
- V15-017 earlier AIM permission blocker plus later stale RCS evidence -> AIM blocker remains authoritative; later defect cannot create eligibility.
- V15-018 replayed/lower semantic_state_sequence with superficially matching heads -> reject as rollback/replay.
- V15-019 rotation barrier plus committed ambiguous EffectIntent -> no duplicate dispatch and no fabricated success.

### Dependency graph
- V15-020 matrix-derived direct dependency graph is complete and acyclic -> NCG graph pass.
- V15-021 runtime dependency exists in matrix but generated graph omits edge -> NCG fail.
- V15-022 hand-added untraceable edge changes graph semantics -> NCG fail.

### Transient dependency
- V15-023 qualified dependency unavailable -> authority blocked; retry after same qualified dependency restores and full re-evaluation succeeds.
- V15-024 cached prior PASS/time/conformance token used during outage -> reject.
- V15-025 emergency weaker dependency used for liveness -> reject.

## 11. Current state

- R8 v1-v14 = historical / v14 external normalized review disposition CHANGES_REQUIRED.
- R8 v15 = NOT_IMPLEMENTED / INTERNAL_NORMALIZATION_REQUIRED.
- executable-schema freeze = BLOCKED.
- implementation start = BLOCKED.
- PR #39/#40 = NON_AUTHORITATIVE.
- authority effect = NONE.

Before a fresh v15 independent review, NCG must regenerate:
- normalized effective specification;
- SRTT-4 RuleRegistry and total table;
- GuardRegistry/CaseRegistry extension through G156/V15-025;
- repaired GuardOmissionManifest;
- BSP-5 grammar;
- cross-mechanism corpus;
- dependency/evaluation/ownership structures;
- blind review packet and reproducibility manifests.

