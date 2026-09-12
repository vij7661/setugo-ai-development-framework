# Platform Authority Endpoint Precedence Table — V23

Status: **PROPOSED — REVIEW REQUIRED — NON-AUTHORITATIVE**

Authority effect: **NONE_EVIDENCE_ONLY**

Table ID: `AUTHORITY-ENDPOINT-PRECEDENCE-V23`

Exact V23 base lineage begins at reviewed V22 commit `61657e8c37b9aa2ac6582c9c284c2398437a7acf`.

Purpose: remove caller/runtime discretion when multiple failure predicates are simultaneously true. This table is intended to be kernel-bound for the governance generation that adopts V23. It does not replace stricter subsystem-specific tables; it defines deterministic cross-cutting precedence and the exact generic fallback endpoint.

## EP-01 — General rule

Evaluation proceeds by phase. A terminal failure in an earlier phase prevents later phases from converting the result into a more permissive outcome. Within a phase, use the most specific applicable endpoint explicitly mapped below. A subsystem-specific endpoint may replace a generic endpoint only when this table or the exact active subsystem table maps the proven predicate class to it.

Missing evidence is not equivalent to proven invalidity.

## EP-02 — Phase 1: terminal root / generation integrity

Evaluate first:

1. attempted in-generation root-kernel/invariant mutation → `ROOT_KERNEL_IN_PLACE_MUTATION_REJECTED`;
2. attempted in-generation strength-contract mutation/substitution → `ROOT_STRENGTH_CONTRACT_MUTATION_REJECTED`;
3. invalid successor-generation self-bootstrap/continuity → `GOVERNANCE_GENERATION_TRANSITION_INVALID`;
4. required genesis evidence missing/unreviewable rather than proven invalid transition → `ROOT_GOVERNANCE_GENESIS_INSUFFICIENT_EVIDENCE`.

A later policy/evidence success cannot override these endpoints.

## EP-03 — Phase 2: meta-governance / identity / authority-graph integrity

Evaluate next:

1. proposed governance-support rules used to approve themselves → `META_GOVERNANCE_SELF_ACTIVATION_REJECTED`;
2. concrete rename/alias/split/merge/reclassification identity escape → `GOVERNED_OBJECT_IDENTITY_RECLASSIFICATION_REJECTED`;
3. protected authority/meta-policy transition proven weaker under the active immutable strength contract → `AUTHORITY_META_POLICY_WEAKENING_REJECTED`;
4. authority dependency cycle/self-parent/ancestor-control path → `AUTHORITY_DEPENDENCY_CYCLE_REJECTED`;
5. authority-bearing edge falsely classified as transport/replica/observation → `AUTHORITY_DEPENDENCY_EDGE_CLASSIFICATION_INVALID`;
6. material authority-affecting object omitted from closure → `AUTHORITY_SURFACE_CLASSIFICATION_INCOMPLETE`;
7. policy-like closure member with no qualifying strength contract → `AUTHORITY_STRENGTH_CONTRACT_MISSING`.

If an attempted identity escape is the mechanism used to enable weakening, the identity-reclassification endpoint applies before the downstream weakening endpoint because the proposed new identity never becomes authoritative.

## EP-04 — Phase 3: authority inventory / sink / migration structure

Evaluate structural availability before consuming authority state:

1. malformed/fake/non-qualifying capability-inventory entry or forged strength-contract mapping → `AUTHORITY_CAPABILITY_INVENTORY_ENTRY_INVALID`;
2. authority-capable runtime component absent from the current inventory → `AUTHORITY_CAPABILITY_INVENTORY_INCOMPLETE`;
3. material authority sink absent from the sink registry → `AUTHORITY_SINK_CLASSIFICATION_INCOMPLETE`;
4. proven equivalent unguarded sink write/effect capability → `AUTHORITY_SINK_FENCING_INVALID`;
5. predecessor generation migration inventory does not exactly equal the dispositioned predecessor set → `GENERATION_MIGRATION_INVENTORY_INCOMPLETE`.

For an attempted successor read/use of a particular predecessor object after migration completeness has otherwise qualified, a missing/non-authoritative disposition for that object returns `PREDECESSOR_AUTHORITY_OBJECT_USE_REJECTED`.

## EP-05 — Phase 4: authority aggregation

For every authority-affecting transition:

1. transition cannot be classified/normalized/keyed or applicable aggregate state is missing/ambiguous → `AUTHORITY_TRANSITION_AGGREGATION_INCOMPLETE`;
2. deterministic aggregate state exists and the proposed below-material transition crosses the non-material aggregate ceiling without a qualifying full material-authority decision → `AGGREGATE_AUTHORITY_BUDGET_EXCEEDED`;
3. if a fresh full material-authority decision binds and approves the exact cumulative post-state, continue to later phases.

A budget-ceiling failure cannot be converted to below-material success by retry, aliasing, resource partitioning, or concurrency.

## EP-06 — Phase 5: independence and evidence-source qualification

For a purported independent actor/source:

1. proven current conflicting effective-control relationship evidence without governed resolution → `EFFECTIVE_CONTROL_RELATIONSHIP_CONFLICT`;
2. proven subsystem-specific independence violation uses that subsystem's exact active independence-invalid endpoint (for example `RECONCILIATION_EVALUATOR_INDEPENDENCE_INVALID`, `DEPENDENCY_UNIVERSE_AUTHORITY_INDEPENDENCE_INVALID`, or `WITNESS_AUTHORITY_OR_CURRENTNESS_INVALID` when its predicate is proven);
3. for evidence-source validity, if a source-class-specific proven-invalid endpoint exists and is mapped by the active table, use it;
4. otherwise proven revoked/expired/compromised/superseded/wrong-generation/wrong-tuple/wrong-class/wrong-policy-bound source evidence → `AUTHORITY_EVIDENCE_SOURCE_INVALID`;
5. if qualification/currentness/independence cannot be established because required evidence or a mandatory control source is missing/unavailable rather than proven invalid → `INSUFFICIENT_EVIDENCE`.

This phase is the controlling prospective rule for the historical WDPC-357 ambiguity.

## EP-07 — Phase 6: kernel decision record and ledger integrity

Before authority apply:

1. proven rollback/fork/sequence integrity failure of `AuthorityKernelDecisionLedger` → `AUTHORITY_KERNEL_DECISION_LEDGER_INTEGRITY_INVALID`;
2. a matching, otherwise qualifying decision record whose bound preconditions/versions/currentness changed after issuance → `ROOT_KERNEL_DECISION_STALE`;
3. absent record, record not anchored in the qualifying ledger, replay to a different transition/tuple, malformed record, wrong-generation record, unqualified signer, or other failure to present a qualifying exact current kernel decision → `ROOT_KERNEL_ENFORCEMENT_REQUIRED`, unless a more specific earlier-phase endpoint already applies.

Historical cryptographic signature validity does not override current signer/ledger/precondition failure.

## EP-08 — Phase 7: multi-sink and reconciliation

Where outcome is uncertain across mandatory sinks/components, use the active deterministic reconciliation order:

1. authenticated structural contradiction / multiple distinct committed decision identities → `RECONCILIATION_CONFLICT`;
2. exactly one complete canonical committed decision identity across every mandatory current component/witness → `COMMIT_CONFIRMED_EXISTING`;
3. complete authoritative proof of absence across every mandatory component with consistent witness/uniqueness/publication state → `NO_COMMIT_CONFIRMED`;
4. otherwise → `INSUFFICIENT_EVIDENCE`.

Partial primary-store success or witness lag never jumps directly to complete success/absence.

If a mandatory sink is provably omitted from the required atomic/effect set before reconciliation, use the stricter subsystem atomic-boundary endpoint when defined; otherwise `AUTHORITY_SINK_ATOMICITY_VIOLATION`.

## EP-09 — Phase 8: proof-view completeness

An underlying authority failure from an earlier phase remains the authority result.

If the underlying state is otherwise evaluable but the reviewer-facing proof view suppresses, falsely marks not-applicable, or fabricates a mandatory field required by its `ProofViewCompletenessManifest`, return `PROOF_VIEW_COMPLETENESS_INVALID` for proof qualification. The proof view cannot report PASS while concealing an earlier-phase failure.

Secret-safe redaction does not count as omission when the manifest-prescribed identity/version/qualification/non-exposure result remains visible.

## EP-10 — No local override

Caller code, UI, model output, reviewer prose, retry logic, local configuration, or subsystem implementation may reorder these phases or select a different endpoint for convenience.

The active table identity/version/digest and selected phase/predicate/endpoint are bound into the `AuthorityKernelDecisionRecord` and reviewer-safe proof view.

## EP-11 — Change rule

The semantics/order of this table are kernel-bound. A change that could make a formerly blocking condition later/permissive inside the same governance generation is a strength/kernel-semantics change and cannot be activated as ordinary policy. It requires the applicable root/meta-governance transition, including a new governance generation where required by the active kernel.

## EP-12 — Nonclaims

This table is a design artifact. It does not prove runtime endpoint dispatch, implementation correctness, or falsification execution.

It grants no implementation freeze, execution freeze, merge, release, deployment, production authority, adjudication, or terminal authority.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
