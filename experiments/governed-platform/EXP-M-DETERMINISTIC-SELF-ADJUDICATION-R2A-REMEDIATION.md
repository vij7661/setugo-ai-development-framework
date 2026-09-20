# EXP-M Deterministic Implementation — Internal Self-Adjudication R2A Remediation

Status: `AUTOMATABLE_WORK_REMAINS`

Authority effect: `NONE`

EXP-M remains `NOT_QUALIFIED`.

Live provider/API qualification and execution remain blocked.

This document is proposer/internal self-adjudication performed **before** sending the R2 packet to another external reviewer. The goal is to avoid knowingly sending another false-green packet.

Do not treat the current 40/40, A-T PASS, 50/50 mutations, or 19-case self-falsification as closure evidence until every item below is repaired and fresh evidence is regenerated.

## A. Authoritative-path completion

### A1 — Eliminate residual summary-boolean authority

The current `_predicate_validators()` still accepts load-bearing summaries for multiple predicates.

Replace summary checks with production validators over typed evidence.

At minimum:

- `capability_current` must call `validate_capability(...)` using profile + plan + qualification + physical attempts + external expectations;
- `accessibility_policy_satisfied` must validate a typed risk/accessibility policy against a typed proof;
- `context_isolation_satisfied`, `hidden_state_policy_satisfied`, `context_state_clean`, and `admission_fence_current` must derive from the same authoritative context-isolation/fence evidence;
- `semantic_context_qualified` must validate a typed semantic-context qualification record;
- `wire_binding_valid` and `delivery_complete` must re-run byte-level delivery/wire validation, not trust a precomputed boolean/result;
- `accessibility_proven` must validate a typed accessibility proof against policy and trusted witness/retrieval evidence;
- `witness_record_current` must run witness qualification validation;
- `semantic_coverage` must validate a typed coverage record against exact source/context;
- `reviewer_provenance` must validate a typed provenance/authorization record against externally supplied policy/trust requirements.

A typed dataclass containing `valid=True`, `trusted=True`, `complete=True`, `current=True`, or `qualified=True` is still a summary boolean unless the authoritative predicate recomputes/binds the underlying evidence.

Regression gate:

`ALL_TRUE_OR_PRECOMPUTED_SUMMARY_ONLY_BUNDLE -> INADMISSIBLE`

### A2 — Production callers cannot construct expectations from evidence under review

`context_from_state()` may remain only as a clearly test-only fixture helper.

Production/admission/mutation authority paths must receive a `PredicateContext` from a frozen request/authority source independent of the evidence bundle.

Add a static/runtime guard so production entrypoints do not call `context_from_state()`.

Mutation tests must also use an independently frozen context, not derive expected identities from the mutated state.

## B. Independent closure repair

### B1 — Registry closure must use all independent target sources

Current `AdmissibilityPredicateRegistry.closure()` is insufficient.

Required closure inputs:

- required predicate IDs from platform registry;
- actual verdict-result predicate IDs;
- declared mutation target predicate IDs from an independent mutation catalog;
- actually executed mutation target predicate IDs;
- actually killed mutation target predicate IDs;
- declared negative-fixture target predicate IDs from an independent fixture catalog;
- actually executed negative-fixture target predicate IDs.

No catalog may be generated mechanically from `PREDICATES` in the same function/module path being checked.

The fixture catalog must not be `tuple(f"negative:{p}" for p in PREDICATES)`.

The mutation catalog must not simply copy the same predicate tuple.

Create independent declarations/files or separately parsed machine-readable registries and compare them.

Closure fails on:

- missing target;
- extra target;
- declared-but-unexecuted mutation;
- executed-but-surviving mutation;
- missing fixture;
- executed fixture with wrong target;
- verdict omitting a required predicate;
- verdict containing unknown predicate.

### B2 — Phase O/T must consume actual run artifacts

Phase O/T must call the closure function using the actual current run's:

- verdict artifact;
- mutation artifact;
- negative-fixture artifact.

Do not reconstruct success from registry sets or lengths inside `run_phases()`.

## C. Qualification closure repair

### C1 — Trial + confirmation coverage

`validate_capability()` must close over the full frozen qualification execution plan, not confirmation IDs only.

Define exact semantics for `trial_ids` and `confirmation_ids`.

If both are required by frozen R5:

`expected_roots = trial_ids UNION confirmation_ids`

Authoritative closure must be recomputed from immutable physical-attempt records.

Cached fields such as:

- `planned_attempt_ids`
- `closed_attempt_ids`
- `all_trials_closed`
- `statistical_qualified`

are consistency assertions only, not authority.

Reject:

- missing trial root;
- missing confirmation root;
- duplicate root;
- extra unscheduled root;
- retry replacing failed root;
- cached closure true while attempt ledger is incomplete;
- cached statistical-qualified true when recomputation/policy does not justify it.

### C2 — Required-evidence item-set exactness

The evidence contract must distinguish required and governed optional IDs.

Preflight requires:

- every required ID present;
- no unknown/unapproved extra ID;
- canonical unique IDs.

If `RequiredEvidenceContract` lacks optional IDs, extend it or introduce an explicit allowed-item contract.

## D. Context / witness / accessibility repair

### D1 — One context-isolation verdict

Authoritative context predicates must derive from one typed context-isolation result produced from:

- policy;
- actual transition class;
- required observable channels;
- state/readback/sentinel evidence;
- hidden-state residual rule;
- expected fence version;
- config/state hash.

Do not separately accept caller mappings like:

`{"satisfied": true}`, `{"clean": true}`, `{"current": true}`.

### D2 — Trusted witness challenge binding

Witness proof must bind:

- challenge ID;
- frozen source slice ID/hash;
- expected answer/hash generated by trusted harness after evidence freeze;
- exact provider/mode/prompt-isolation identity;
- challenge semantics class = extraction/accessibility only;
- response hash/length;
- final context budget before and after witness traffic.

A non-empty challenge/response pair is not sufficient proof.

### D3 — Accessibility proof cannot be `valid=True`

Replace bare `AccessibilityProofRecord.valid` authority with a production validator that proves the exact proof mode allowed by `ProviderAccessibilityRiskPolicy`.

If deterministic proof is required, witness-only/probabilistic evidence must fail.

## E. Delivery / wire / materialization repair

### E1 — Delivery completeness must be recomputed at predicate time

`complete_delivery()` may produce diagnostics, but the authoritative `delivery_complete` predicate must consume:

- manifest;
- actual returned bytes;
- receipt;
- wire record;
- representation/materialization;
- exact source/request/attempt/session expectations.

It must call the same byte-level delivery validator used by admission.

Never accept a standalone `DeliveryCompletenessResult(complete=True)` as authority.

### E2 — `receipt.complete` is non-authoritative

Do not require or trust `receipt.complete` as a positive authority bit.

It may be used only as a consistency/diagnostic field. Compute completeness from actual bytes and identities.

### E3 — Materialization authority uses typed entries, not helper-only path checks

Phase L and authoritative admissibility must exercise the typed materialization engine including:

- normalized duplicate;
- absolute path;
- Windows drive;
- backslash ambiguity;
- dot/dot-dot;
- symlink target escape;
- recursion;
- member count;
- per-member bytes;
- total bytes;
- decompression ratio;
- qualified transform ID/hash/version;
- source/representation/parameters/coverage binding.

## F. Persistent atomic admission repair

### F1 — CAS must be atomic with protected state generation

The JSON ledger's "insert-if-absent" terminal behavior is not by itself a full compare-and-set over the authoritative state being protected.

Use a transactional deterministic backend (SQLite is acceptable) or an equivalent atomic abstraction in which:

- current protected generation/version is read inside the same transaction;
- expected generation is compared;
- terminal VOID/COMMITTED state is written atomically;
- concurrent writers cannot both commit;
- restart preserves terminal states and generation;
- stale snapshots cannot revive attempts.

### F2 — Final admission revalidates actual evidence/current state

`admit_review_attempt_with_evidence()` must not revalidate evidence and then perform a separate string-map drift check with an unprotected gap.

The final transaction must bind the evidence verdict/current state generation to the same CAS operation or enforce a documented serialized-writer/fence mechanism that makes the gap impossible.

Add concurrent/race tests.

## G. Mutation authenticity repair

### G1 — Mutation must run in isolated process/module instance

Current mutation code monkeypatches `_predicate_validators` in the same process.

Run each validator-logic mutant in an isolated subprocess/module load so:

- mutation state cannot leak across cases;
- production module state is fresh for each mutant;
- one mutant targets exactly one guard;
- normal negative control executes without mutation;
- mutated run executes the same frozen fixture/context.

### G2 — Independent fixture source

Negative fixtures must come from a catalog independent of the mutation target catalog.

Do not generate fixtures by looping over `registry.logic_mutation_ids` and mapping each target inside the same mutation runner without an independent closure artifact.

Each fixture records:

- fixture ID;
- target predicate ID;
- immutable fixture hash;
- expected rejection predicate/reason.

### G3 — Kill semantics

A validator mutation is killed only if:

1. normal production rejects the frozen negative fixture;
2. the isolated mutant would false-green the fixture;
3. the mutation test detects that semantic divergence.

Record all three outcomes.

## H. A–T phase evidence repair

### H1 — No synthetic case metadata

Current phase result generation must not set:

- `positive_case_ids=[...]`
- `negative_case_ids=[...]`
- `case_results={"positive":"PASS","negative_rejected":true,...}`

as generic metadata after the fact.

Each phase must execute explicit case objects and derive:

- positive IDs/results;
- negative IDs/results;
- applicable mutation IDs/results;
- phase PASS/FAIL.

### H2 — Phase-specific negatives

At minimum ensure actual executed negative cases cover:

A authority/contract/request/preflight
B chunk identity/hash/order
C representation/transform/source
D taxonomy single/mixed/unresolved
E manifest/corpus/source
F capability/plan/trial/confirmation/expiry/statistics
G both mutation families
H physical attempt/retry lineage
I every admissibility predicate
J actual byte/wire/receipt/source mismatch
K witness qualification/challenge/expected answer/budget
L typed materialization
M request/attempt/session/wire/source identity
N bare/cached qualification summaries rejected
O full independent closure artifact
P dirty/lying/hidden/missing-channel/config drift
Q fence version + transition/risk policy
R authoritative accessibility/witness path
S attempt ledger hard failure/retry/unscheduled/duplicate
T actual retry transparency + closure from run artifacts

Phase S/T cannot use a two-key dict with no planned roots/request/session and call that sufficient retry transparency.

## I. Source/evidence freeze repair

The current R2 evidence correctly records execution against commit:

`c0efaf7fdc9c35e05f424643015f299e014605e0`

but that commit itself changed evidence/review artifacts rather than being a clean source-only freeze. This is not the requested two-stage discipline.

For the next review:

### S — clean source freeze

After all production/test/mutation/self-falsification code is final:

- commit source/test/mutation/builder changes only;
- no generated result/stdout/review artifacts change in S;
- record source commit/tree S;
- verify clean worktree.

### E — fresh evidence

Run exactly S.

Every result/log must contain S commit/tree.

Then commit only generated evidence/review artifacts in E.

Packet commit P may follow E and must change packet/docs only.

Reviewer must be able to prove:

`source S -> evidence E -> packet P`

without a later source change between S and E.

## J. Self-falsification exit

Before external review, internal self-falsification must specifically attack every item A-I above and report:

- unresolved Critical = 0;
- unresolved High = 0.

Do not report only a survivor count from the normal mutation harness.

Self-falsification must be independently authored and must include:

- precomputed-summary-only typed records;
- self-derived PredicateContext;
- closure catalog alias/omission;
- missing trial root with all cached booleans true;
- forged delivery result;
- witness without trusted expected-answer binding;
- accessibility `valid=True` without allowed proof;
- concurrent admission race;
- generic/synthetic phase metadata;
- source/evidence interleaving violation.

## K. R2A exit criteria

Do not create/send another external review packet until all are true:

1. every load-bearing admissibility predicate is evidence-derived;
2. no production/test authority path self-derives expected values from evidence under review;
3. full independent closure includes required/verdict/mutation declared/executed/killed/fixture declared/executed targets;
4. capability closure covers all frozen trial/confirmation roots and physical attempts;
5. required/optional evidence item set is exact;
6. context/hidden-state/fence verdict is production-derived;
7. witness expected-answer and accessibility proof are production-derived;
8. delivery completeness is recomputed from actual bytes;
9. materialization is typed and fully bounded;
10. admission CAS is transactional/persistent and race-tested;
11. validator mutations execute in isolated processes with independent fixtures;
12. A-T case metadata is produced from actually executed phase cases, not synthesized;
13. self-falsification finds zero unresolved Critical/High across these families;
14. clean source-only S -> evidence-only E -> packet-only P sequence is produced;
15. all fresh tests/mutations/self-falsification are bound to S;
16. EXP-M remains NOT_QUALIFIED;
17. live provider/API execution remains false.

Then return `DETERMINISTIC_REVIEW_REQUIRED` and stop for independent external review.

## L. No-stop rule

If any item above is automatable, classify:

`AUTOMATABLE_WORK_REMAINS`

and continue.

Do not stop because the previous packet said review required; this internal adjudication supersedes that stop until R2A exit criteria are met.

Do not use live provider APIs.
