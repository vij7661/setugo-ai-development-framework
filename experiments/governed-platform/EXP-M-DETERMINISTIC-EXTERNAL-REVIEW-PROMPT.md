# EXP-M Deterministic Implementation — Independent External Review Prompt

Review the attached/source file:

`EXP-M-DETERMINISTIC-IMPLEMENTATION-REVIEW.md`

## Scope

This is an independent implementation/falsification review of EXP-M deterministic work only.

EXP-M remains:

`NOT_QUALIFIED`

No live Claude, DeepSeek, Gemini, OpenRouter, or other provider qualification is authorized by this review.

## Exact identities

Branch:

`experiment/exp-m-deterministic-implementation`

Implementation source commit reviewed by the packet:

`ec102c738fe76ed7341484f70fb404c1d1cb7cdd`

Implementation tree:

`879e321803a836202eeacc79ec3cb43bac96cf32`

Current branch head containing refreshed review evidence:

`1a66fc6faad455e8dcfb2b1f4abb84c89bd96c6e`

Current branch-head tree:

`5becd1c407b41305c54c2ea1794535b0b451dd4b`

Frozen design source:

`0ba6c3c24ec247f5ad993b7e2f996ccd472b5f45`

Important: distinguish implementation source identity from later review-packet-only commits.

## Required posture

Assume false-green.

Do not trust:

- PASS labels;
- phase names;
- generated counts;
- mutation counts;
- self-falsification claims;
- the review packet's own narrative;
- the fact that a dataclass/type exists;
- a fake provider merely returning expected values.

Reconstruct whether the production-path implementation actually enforces the frozen EXP-M R5 design.

## Mandatory review areas

### 1. Frozen-design fidelity

Compare implementation behavior against the frozen R5 design and test matrix.

Identify any R5 load-bearing invariant that is:

- omitted;
- weakened;
- represented only by a summary boolean;
- checked only in tests but not the production validator;
- hard-coded to PASS;
- modeled with materially weaker semantics.

### 2. A–T phase validity

For every deterministic phase A through T:

- identify the production function(s) exercised;
- identify the adversarial negative fixture(s);
- verify PASS cannot be produced by returning a hard-coded phase status;
- verify the phase tests the frozen invariant rather than only its label.

Return per phase:

`PASS / FAIL / INSUFFICIENT_EVIDENCE`

### 3. Admissibility predicate closure

Verify exact closure:

```text
required predicate IDs
==
VerdictAdmissibilityResult predicate IDs
==
validator-logic mutation target IDs
==
independently killed mutation IDs
```

Check that mutations alter/bypass real production validator logic rather than merely setting the corresponding input state false.

Try deleting or weakening each predicate guard.

### 4. Data/state mutations

Review every data/state mutation.

Check for missing adversarial families, especially:

- wrong request/source identity;
- candidate-writable authority snapshot;
- stale capability/profile;
- context-isolation violation;
- hidden-state policy violation;
- admission fence drift;
- prompt isolation expiry;
- witness record expiry/mismatch;
- retrieval/session mismatch;
- attempt-set incompleteness;
- retry hiding;
- materialization/representation mismatch;
- egress revocation;
- atomic admission drift.

### 5. Provider capability qualification model

Verify deterministic implementation faithfully models:

- qualification execution plan;
- planned attempt closure;
- zero-hard-failure semantics;
- no failed-attempt replacement;
- retry transparency;
- profile current/expiry behavior;
- exact operating-point binding;
- statistical-qualification state.

A simple boolean `qualified=true` must not bypass the mechanisms required by the frozen design where those mechanisms are load-bearing.

### 6. Provider context isolation

Attack:

- dirty context;
- lying readback;
- hidden provider state;
- mutable configuration drift;
- missing/expired admission fence;
- dedicated-account residual policy;
- highest-authority residual DISALLOW behavior.

Verify context cleanliness is not just a trusted boolean.

### 7. Evidence manifest and delivery

Attack:

- missing item;
- duplicate item;
- unmanifested item;
- byte mutation;
- size/hash mismatch;
- request mismatch;
- source/commit mismatch;
- representation mismatch;
- chunk order/index/total mismatch;
- attempt/session mismatch;
- upload/file ID without returned bytes.

### 8. Witness/accessibility boundary

Attack:

- empty witness;
- over-budget witness;
- canary-preserving content loss;
- evidence eviction caused by witness traffic;
- stale/wrong WitnessProtocolQualificationRecord;
- evaluative witness output treated as semantic evidence.

### 9. Retrieval final-context binding

Require evidence that model-selected/fake retrieval binds:

- exact source/version;
- exact range/member;
- returned bytes/hash;
- tool/result identity;
- same final adjudication context.

File-open or citation-only success is insufficient.

### 10. Atomic admission / TOCTOU

Try state changes:

- after preflight;
- after delivery;
- after reviewer receipt;
- after final read but before admission;
- registry change;
- capability expiry;
- fence drift;
- egress revocation;
- prompt-isolation invalidation.

Later requalification must not revive an already void attempt.

### 11. Insufficient-evidence taxonomy

Verify:

- causes are independently evaluated;
- multiple true causes => MIXED_INSUFFICIENCY;
- no proven cause => INSUFFICIENT_EVIDENCE_CAUSE_UNRESOLVED;
- delivery/context failures do not become scientific-evidence absence.

### 12. Self-falsification sufficiency

Do not accept only the eight self-falsification cases as sufficient.

Independently find missing Critical/High attacks across the whole implementation.

### 13. Generated evidence integrity

Verify:

- generated counts come from machine artifacts;
- review packet reflects exact implementation source;
- later documentation-only commits are not confused with implementation identity;
- no stale result JSON is being reused after source changes;
- tests/mutations were rerun after the final implementation change;
- first failures/revisions are preserved as required.

## Required overall disposition

Return exactly one:

- `BOUNDED_PASS`
- `CHANGES_REQUIRED`
- `INSUFFICIENT_EVIDENCE`

A BOUNDED_PASS means only that deterministic implementation/falsification is independently acceptable to proceed to the next separately governed provider-qualification planning stage.

It does **not** qualify EXP-M and does **not** authorize live provider/API calls.

## Required output

### A. Overall disposition

### B. Critical findings

For each:
- ID
- affected implementation/design invariant
- concrete false-green path
- why current implementation is insufficient
- narrow required fix

### C. High findings

Same fields.

### D. Medium/Low findings

### E. Frozen-design fidelity verdict

`PASS / FAIL / INSUFFICIENT_EVIDENCE`

### F. Phase A–T verdicts

Return one verdict for every phase A through T.

### G. Mutation/admissibility verdicts

- VALIDATOR_LOGIC_MUTATION_COVERAGE = PASS / FAIL
- DATA_STATE_MUTATION_COVERAGE = PASS / FAIL
- ADMISSIBILITY_PREDICATE_CLOSURE = PASS / FAIL
- SURVIVORS_ZERO_PROVEN = PASS / FAIL

### H. Mechanism verdicts

- AUTHORITY_SNAPSHOT = PASS / FAIL
- REQUIRED_EVIDENCE_CONTRACT = PASS / FAIL
- INTERACTION_CONTRACT = PASS / FAIL
- MATERIALIZATION = PASS / FAIL
- REPRESENTATION_BINDING = PASS / FAIL
- PROVIDER_CAPABILITY_MODEL = PASS / FAIL
- QUALIFICATION_ATTEMPT_CLOSURE = PASS / FAIL
- RETRY_TRANSPARENCY = PASS / FAIL
- PROVIDER_CONTEXT_ISOLATION = PASS / FAIL
- ADMISSION_FENCE = PASS / FAIL
- WIRE_BINDING = PASS / FAIL
- WITNESS_ACCESSIBILITY = PASS / FAIL
- RETRIEVAL_FINAL_CONTEXT_BINDING = PASS / FAIL
- PROMPT_ISOLATION_BINDING = PASS / FAIL
- INSUFFICIENT_EVIDENCE_TAXONOMY = PASS / FAIL
- ATOMIC_ADMISSION = PASS / FAIL

### I. Final determination

State:

- unresolved Critical count;
- unresolved High count;
- deterministic implementation review closure: yes/no;
- safe to begin separately governed live-provider qualification planning: yes/no;
- safe to execute live provider/API calls now: must remain NO unless a later explicit authorization exists;
- EXP-M qualification state: must remain NOT_QUALIFIED;
- authority effect of this review: NONE.
