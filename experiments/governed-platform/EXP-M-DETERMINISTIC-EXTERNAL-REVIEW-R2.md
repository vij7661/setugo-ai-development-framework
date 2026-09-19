# EXP-M Deterministic Implementation — External Review R2

Overall disposition: `CHANGES_REQUIRED`

Scope: independent re-review after R1 remediation.

Authority effect: `NONE`

EXP-M remains `NOT_QUALIFIED`.

Live provider/API qualification and execution remain blocked.

## Core reviewer determination

The remediation does not close the prior false-green class.

The reviewed source still:

- exposes a production admissibility bypass through `disabled_predicates`;
- accepts caller-supplied summary booleans for load-bearing predicates;
- leaves helper validators disconnected from the authoritative path;
- leaves mutation/closure evidence same-source or tautological;
- permits incomplete provider qualification closure;
- lacks permanent/atomic attempt voiding;
- does not make retrieval, witness, materialization and wire/receipt mechanisms fully load-bearing.

## Prior finding closure

No prior R1 finding was returned fully CLOSED.

C-01 PARTIAL
C-02 OPEN
C-03 OPEN
C-04 PARTIAL
C-05 PARTIAL
C-06 OPEN
C-07 PARTIAL
C-08 OPEN
C-09 OPEN
C-10 OPEN
C-11 OPEN

H-01 OPEN
H-02 OPEN
H-03 PARTIAL
H-04 PARTIAL
H-05 PARTIAL
H-06 OPEN
H-07 OPEN
H-08 PARTIAL
H-09 OPEN
H-10 PARTIAL

## New Critical findings

### NC-01 — Production admissibility bypass

`evaluate_admissibility(..., disabled_predicates=...)` can force predicates true.

Required direction: remove all production guard-disable parameters. Mutation testing must mutate/bypass production guards only in isolated test processes.

### NC-02 — Boolean laundering remains pervasive

Load-bearing predicates can still be satisfied through caller-injected summary booleans.

Required direction: every authoritative predicate consumes evidence-bound production validators; no summary boolean is authority.

### NC-03 — Provider qualification can pass empty/mismatched plan-record state

Qualification does not fully bind plan ID, trials, closure and non-empty attempt sets.

Required direction: exact plan/record binding, non-empty required sets, attempt-ledger-derived closure, zero hard failures and current statistical state.

### NC-04 — Context isolation is not authoritative

Preflight hardcodes a lower transition class and does not validate the expected fence version or post-preflight config drift.

Required direction: real transition/risk policy, externally bound fence version and admission-time config/state revalidation.

### NC-05 — Atomic admission is not atomic/permanent

An attempt voided by drift can later be revived after state restoration.

Required direction: persistent attempt ledger, permanent void state, compare-and-set and evidence revalidation.

### NC-06 — Retrieval final-context binding not authoritative

A caller summary `retrieval.complete=True` can satisfy coverage.

Required direction: exact RetrievalEvidenceRecord + raw bytes + externally expected request/attempt/session/source/range/final-context binding.

### NC-07 — Wire/receipt trusts forged completeness

`receipt.complete=True` and missing wire-hash validation leave byte-binding false-green paths.

Required direction: compute completion from actual returned bytes and canonical wire body; ignore caller completeness summaries.

### NC-08 — Witness/accessibility not load-bearing

Caller summaries can satisfy witness/accessibility.

Required direction: authoritative WitnessProtocolQualificationRecord, trusted challenge/expected-answer binding, budget/non-semantic/eviction checks and final-context binding.

### NC-09 — Materialization contract incomplete

Duplicate normalized paths and unqualified transforms pass; resource/symlink/archive bounds are incomplete.

Required direction: typed materialization entries, canonical normalization/deduplication, qualified transform registry and bounded archive/resource semantics.

### NC-10 — Predicate closure remains tautological

Phase O/T and registry closure do not independently bind predicates, verdict outputs, mutation targets, actually executed/killed mutation targets and negative-fixture targets.

Required direction: independently sourced target mappings and exact closure.

### NC-11 — Validator-logic mutations are not authentic

The mutation suite uses the production bypass itself.

Required direction: remove bypass; independently malformed fixture must fail normally and false-green only when the exact production guard is mutated in an isolated harness.

### NC-12 — Required evidence contract not bound to manifest item set

Required evidence IDs are not authoritatively compared with the delivered manifest.

Required direction: all required IDs present, only governed optional extras permitted, canonical uniqueness enforced.

## New High findings

NH-01 Retry records do not bind retry to original failed attempt.

NH-02 Retry transparency checks field presence instead of full request/session/wire/planned-attempt identity.

NH-03 Authority snapshot currentness does not fully bind snapshot ID/content hash to contracts.

NH-04 Interaction contract does not prove declared interactions occurred in delivered/final context.

NH-05 Representation governance is still a boolean/string rather than transform/source/representation proof.

NH-06 Egress expected version can be derived from the same state being validated.

NH-07 Prompt-isolation expected provider/mode can be self-referential.

NH-08 Fresh execution evidence is asserted but not independently demonstrated with commit-bound logs and stale-result detection.

## Reviewer mechanism verdict

```text
FROZEN_DESIGN_FIDELITY = FAIL
VALIDATOR_LOGIC_MUTATION_COVERAGE = FAIL
DATA_STATE_MUTATION_COVERAGE = FAIL
ADMISSIBILITY_PREDICATE_CLOSURE = FAIL
SURVIVORS_ZERO_PROVEN = FAIL

AUTHORITY_SNAPSHOT = FAIL
REQUIRED_EVIDENCE_CONTRACT = FAIL
INTERACTION_CONTRACT = FAIL
MATERIALIZATION = FAIL
REPRESENTATION_BINDING = FAIL
PROVIDER_CAPABILITY_MODEL = FAIL
QUALIFICATION_ATTEMPT_CLOSURE = FAIL
RETRY_TRANSPARENCY = FAIL
PROVIDER_CONTEXT_ISOLATION = FAIL
ADMISSION_FENCE = FAIL
WIRE_BINDING = FAIL
WITNESS_ACCESSIBILITY = FAIL
RETRIEVAL_FINAL_CONTEXT_BINDING = FAIL
PROMPT_ISOLATION_BINDING = FAIL
INSUFFICIENT_EVIDENCE_TAXONOMY = PASS
ATOMIC_ADMISSION = FAIL
```

All phases A–T were returned FAIL in this review.

## Final reviewer determination

- unresolved Critical: 12+
- unresolved High: 8+
- deterministic implementation closure: NO
- safe for live-provider qualification planning: NO
- live provider/API execution: NO
- EXP-M: NOT_QUALIFIED
- authority effect: NONE

This file preserves the external review as defect evidence. Exact user-supplied review remains outside the repository unless separately archived byte-for-byte.
