# EXP-M Deterministic R1 Remediation — Independent External Review Prompt

Review:

`EXP-M-DETERMINISTIC-IMPLEMENTATION-R1-REVIEW.md`

This is an independent re-review after the prior deterministic implementation review returned `CHANGES_REQUIRED` with 11 Critical and 10 High findings.

## Exact identities

Branch:

`experiment/exp-m-deterministic-implementation`

Reviewed implementation source commit:

`66129025f9b5211a551f191c4367713e78ef14c4`

Reviewed implementation tree:

`1e496ec029092536b0e90bc98483353b957ba8a0`

Review-packet commit:

`895f0a657e9c715e5be262d820784387c85f7231`

Review-packet tree:

`952e89aaba78b8a8c036436b4a8599bff31d281d`

Frozen EXP-M R5 design commit:

`0ba6c3c24ec247f5ad993b7e2f996ccd472b5f45`

EXP-M remains:

`NOT_QUALIFIED`

Live provider/API execution remains:

`BLOCKED`

Authority effect of this review:

`NONE`

## Review posture

Assume false-green.

The prior review found that:

- Phase D was hard-coded;
- Phase G was hard-coded;
- admissibility closure was tautological;
- provider qualification was bypassable with a boolean;
- context isolation was trusted-boolean only;
- atomic admission was absent;
- retrieval final-context binding was absent;
- witness/accessibility enforcement was incomplete;
- wire/receipt completion was not byte-bound;
- data/state mutation coverage was incomplete;
- self-falsification was insufficient;
- A-T phases were largely happy-path;
- many frozen-design invariants were caller-supplied booleans.

The current packet claims those defects are fixed.

Do not trust the new counts or PASS labels. Reconstruct the mechanisms.

## Mandatory R1 closure review

For every prior Critical C-01..C-11 and High H-01..H-10 return:

`CLOSED / PARTIAL / OPEN`

For anything not CLOSED provide:
- exact surviving false-green path;
- affected production function/test/mutation;
- narrow required fix.

## Mandatory additional attacks

### 1. Boolean laundering remains prohibited

Inspect `evaluate_admissibility()` and every load-bearing predicate.

A mapping field such as:

`{"satisfied": true}`, `{"current": true}`, `{"clean": true}`, `{"valid": true}`, `{"complete": true}`, or `{"trusted": true}`

is not acceptable authority evidence unless it is an output of a separately verified production mechanism and the authoritative path consumes/binds that mechanism's evidence/result.

Specifically attack:

- capability_current;
- accessibility_policy_satisfied;
- context_isolation_satisfied;
- hidden_state_policy_satisfied;
- context_state_clean;
- admission_fence_current;
- semantic_context_qualified;
- wire_binding_valid;
- delivery_complete;
- accessibility_proven;
- witness_record_current;
- session_retrieval_coverage;
- semantic_coverage;
- reviewer_provenance;
- disposition_promotable.

Determine whether any of these can still be caller-injected as a true summary without recomputation from the required evidence.

### 2. Validator-logic mutation authenticity

The mutation suite now uses predicate disabling/bypass injection.

Verify this genuinely mutates/bypasses the actual production validator path and that:

- each negative fixture is independently malformed;
- the normal validator rejects it;
- disabling exactly the targeted guard makes it false-green;
- the mutation harness itself does not define success tautologically;
- mutation targets, predicate registry, negative fixtures, and killed results are independently sourced enough to detect omissions.

A mutation that only flips input evidence state is not validator-logic mutation.

### 3. Closure must not remain same-source tautology

Inspect Phase O and Phase T.

A condition such as:

`set(registry.predicate_ids) == set(registry.logic_mutation_ids)`

or equal lengths alone is insufficient.

Require independent closure involving:

- required predicate IDs;
- actual verdict-result IDs;
- mutation target IDs;
- actually executed/killed mutation IDs;
- negative fixture IDs.

Verify a missing mutation target, extra predicate, or non-executed mutation makes the phase fail.

### 4. Provider qualification must be production-bound

Verify authoritative preflight/admission consumes:

- exact ProviderCapabilityProfile;
- exact ProviderQualificationExecutionPlan;
- exact ProviderCapabilityQualificationRecord;
- profile hash;
- expiry/current time;
- exact provider/model/operating point;
- supported format;
- context limit;
- hard-failure state;
- planned/closed attempt identity;
- statistical qualification state when required;
- retry/physical-attempt closure.

Try a bare `qualified=True` profile with invalid/missing bound records and require rejection.

### 5. Context isolation cannot stop at helper validation

Verify `validate_context_isolation()` is wired into the authoritative preflight/admission path.

Try:

- dirty context;
- lying readback/sentinel;
- hidden-state residual disallowed;
- missing observable channel;
- stale fence;
- config drift after preflight.

Require authoritative attempt rejection/void, not merely a helper function returning false.

### 6. Atomic admission

Inspect `admit_review_attempt()`.

Verify final authority commit revalidates all load-bearing current state and cannot be bypassed by caller-supplied matching strings.

Attack drift in:

- authority snapshot;
- request;
- capability;
- egress;
- context;
- fence;
- prompt isolation;
- witness qualification;
- session/retrieval;
- predicate registry.

Verify an attempt once voided cannot be revived by later state restoration/requalification.

### 7. Retrieval final-context binding

Verify a production retrieval record binds:

- request;
- attempt;
- session;
- source/version;
- exact range/member;
- returned bytes/hash/length;
- tool-result identity;
- final adjudication context identity/hash.

Attack correct bytes in wrong session/context and correct metadata with wrong/missing bytes.

### 8. Wire/representation/receipt binding

Verify completion rejects:

- forged `complete=True`;
- correct item IDs with wrong bytes;
- wrong received byte count;
- wrong semantic hash;
- wrong wire hash;
- wrong source commit;
- wrong representation hash/transform;
- wrong attempt/session/request.

### 9. Witness/accessibility

Verify WitnessProtocolQualificationRecord is load-bearing.

Attack:

- stale record;
- wrong provider/mode/prompt isolation;
- evaluative challenge;
- oversized response;
- witness-induced context eviction;
- canary-preserving content loss;
- witness output used as semantic evidence.

### 10. Materialization

Verify production materialization enforces the frozen R5 contract, not only path traversal.

Attack at least:

- absolute path;
- Windows drive path;
- backslash ambiguity;
- duplicate normalized member;
- symlink escape;
- recursion;
- decompression/size/resource bound;
- unqualified transform;
- semantic representation mismatch.

### 11. Attempt/retry closure

Verify:

- exact planned IDs;
- every first attempt retained;
- hard failure cannot be replaced;
- retries link to original;
- implicit retry cannot hide physical attempt;
- unscheduled attempt cannot count;
- duplicate attempt cannot count;
- wire/request identity binds each physical attempt.

### 12. A–T phase validity

Return PASS/FAIL/INSUFFICIENT_EVIDENCE for every phase A through T.

Each phase must have:
- production mechanism invocation;
- positive control;
- adversarial negative fixture(s);
- failure when its relevant production guard is mutated/disabled.

No phase may pass from only a happy-path call plus narrative checks.

### 13. Fresh evidence integrity

Verify:

- 34/34 focused tests actually ran against reviewed source;
- 3/3 phase/closure tests actually ran against reviewed source;
- 46/46 mutation results are fresh after the final implementation change;
- 54 self-falsification cases are fresh;
- no stale result JSON was reused;
- the review packet binds exactly to source commit `66129025...`;
- later packet-only commits are not confused with implementation identity;
- prior 22/22 and 29/29 false-green results remain preserved as superseded history.

## Required overall disposition

Return exactly one:

- `BOUNDED_PASS`
- `CHANGES_REQUIRED`
- `INSUFFICIENT_EVIDENCE`

A BOUNDED_PASS here means only that deterministic implementation/falsification is independently acceptable for the next separately governed planning stage.

It does not qualify EXP-M.

It does not authorize live provider/API execution.

## Required output

### A. Overall disposition

### B. Prior finding closure

- C-01..C-11 = CLOSED/PARTIAL/OPEN
- H-01..H-10 = CLOSED/PARTIAL/OPEN

### C. New Critical findings

For each:
- ID
- affected invariant/function
- concrete false-green path
- why insufficient
- narrow fix

### D. New High findings

Same fields.

### E. Medium/Low findings

### F. Frozen-design fidelity

`PASS / FAIL / INSUFFICIENT_EVIDENCE`

### G. A-T phase verdicts

One verdict for A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T.

### H. Mutation/closure verdicts

- VALIDATOR_LOGIC_MUTATION_COVERAGE = PASS / FAIL
- DATA_STATE_MUTATION_COVERAGE = PASS / FAIL
- ADMISSIBILITY_PREDICATE_CLOSURE = PASS / FAIL
- SURVIVORS_ZERO_PROVEN = PASS / FAIL

### I. Mechanism verdicts

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

### J. Final determination

State:

- unresolved Critical count;
- unresolved High count;
- deterministic implementation review closure yes/no;
- safe for separately governed live-provider qualification planning yes/no;
- live provider/API execution authorized now: must remain NO;
- EXP-M status: must remain NOT_QUALIFIED;
- authority effect of this review: NONE.
