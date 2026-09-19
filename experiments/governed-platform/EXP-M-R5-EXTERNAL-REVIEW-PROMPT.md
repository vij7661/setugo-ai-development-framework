# EXP-M R5 Independent External Review Prompt

Review the attached/source packet:

`EXP-M-INDEPENDENT-R5-REVIEW-PACKET.md`

Experiment:

`EXP-M — Review Evidence Delivery & Reviewer Context Integrity Falsification`

## Authority boundary

This is an independent **design/preregistration review** only.

EXP-M remains:

`NOT_QUALIFIED`

Do not:

- authorize implementation from this review alone;
- authorize live provider pilots;
- grant platform review authority;
- grant promotion authority;
- treat proposer/model self-adjudication as independent evidence.

## Reviewed identity

Repository:

`vij7661/setugo-ai-development-framework`

Branch:

`experiment/exp-m-review-evidence-delivery-integrity`

Reviewed source commit:

`4d8471a0803c2d5159a4aaa41fc3198660ea41ed`

Reviewed source tree:

`3e6b9f8614072a0290e410a90af124f269eb4cb5`

R5 packet commit:

`d8bb488e4740d0be39db657a1c85d81a8cc3e2df`

R5 packet tree:

`f2f51c259f68dcfde46d747a1e47a94354a9da3c`

R5 packet blob:

`314840360e9149653a25ce4476a1cafd721d13ba`

## Review posture

Assume false-green.

Do not accept the packet's claim that the latest self-review has zero open Critical/High findings.

Try to falsify the design.

R4 previously returned `CHANGES_REQUIRED` with remaining problems around:

- hidden/unexposed provider semantic state;
- incomplete validator-logic mutation coverage;
- normative/live taxonomy mismatch;
- undefined base/head “stricter” comparison;
- missing health-check-renewal test.

The current packet claims those have been repaired and also claims additional self-found issues were closed.

Your task is to determine whether those repairs actually close the authority paths rather than merely moving them.

## Mandatory attack areas

### 1. Governance authority and requiredness

Try to bypass:

- GovernanceAuthoritySnapshot;
- pre-candidate authority pointer;
- transition-class registry;
- evidence-selection registry;
- evidence-relationship registry;
- accessibility-risk registry;
- context-isolation-policy registry;
- admissibility-predicate registry.

Attack:

- deletion;
- rename/replacement;
- same-ID semantic weakening;
- representation downgrade;
- weaker egress;
- weaker statistics;
- weaker accessibility-risk rule;
- weaker context-isolation rule;
- incomparable base/head change.

Check that typed conservative merge rules either preserve the stricter requirement or fail unresolved.

### 2. Provider hidden semantic state

Review ProviderContextIsolationPolicy.

Attack both:

- COMPLETE_READABLE_FENCED_STATE;
- DEDICATED_PLATFORM_ACCOUNT_STATELESS_BOUNDARY.

Try:

- hidden provider memory;
- account/project personalization;
- custom instructions;
- knowledge connectors;
- provider-side mutable context not exposed by API;
- lying/incomplete configuration readback;
- production-account contamination by sentinel qualification;
- provider policy/config-template drift.

Determine whether hidden provider-internal mutable state is honestly represented as a residual/nonclaim instead of “observed clean”.

### 3. Atomic admission and fencing

Attempt races after:

- preflight;
- dispatch;
- provider response;
- final context-state read;
- final policy read;
- immediately before checkpoint compare-and-set.

Attack:

- capability expiry;
- egress revocation;
- provider config mutation;
- session/file invalidation;
- prompt-isolation invalidation;
- registry change;
- witness qualification expiry.

An invalidated attempt must remain permanently void. Later requalification must not revive the old response.

### 4. Provider capability qualification

Review:

- p_min = 0.99;
- one-sided 95% exact Clopper–Pearson;
- 299/299 confirmation minimum;
- zero hard failures;
- every attempted slot counted;
- no rerolls/exclusions/optional stopping;
- exploration and confirmation disjoint;
- frozen trial IDs/schedule/interleaving seed before exposure;
- >=3 UTC days;
- >=4 time blocks/day;
- exact operating point;
- production-equivalent envelope/content class;
- append-only failure history;
- health checks invalidate only.

Attack ProviderQualificationExecutionPlan:

- delete failed slot;
- skip planned slot;
- replace failure with successful retry;
- hidden unscheduled call;
- candidate/operator access to qualification credential;
- implicit SDK retry hiding first failure;
- provider-audit reconciliation gap.

Also adjudicate whether the statistical-independence nonclaim is sufficiently fail-closed.

### 5. Accessibility witnesses

Attack:

- slice size <= min(2048 UTF-8 bytes, 512 provider tokens);
- every required slice challenged;
- same final adjudication session;
- canary-preserving content drop;
- selective sub-slice loss;
- witness traffic causing evidence eviction;
- evaluative witness prompts;
- witness output counted as semantic evidence;
- candidate-authored/stale WitnessProtocolQualificationRecord.

Check ProviderAccessibilityRiskPolicy and whether the highest material-authority class correctly requires deterministic proof when probabilistic witness residual risk is not allowed.

### 6. Retrieval/file proof

For model-selected retrieval require proof of:

- exact source/version;
- exact page/range/member;
- returned-content hash;
- returned length/range;
- retrieval timestamp;
- tool/result identity;
- binding of returned content into the same final adjudication context.

Try to pass with:

- file ID only;
- “opened file” only;
- citation only;
- wrong version;
- partial range;
- correct retrieval in different session;
- correct bytes not inserted into final model context.

### 7. Admissibility predicate closure

Independently reconstruct the current VerdictAdmissibilityResult predicate set.

Verify exact closure:

`registry predicates == verdict predicates == logic-mutation targets == independently killed mutations`

Try:

- add predicate without mutation;
- remove predicate from result;
- delete validator conjunct;
- weaken equality to subset/superset;
- mutation without killing fixture;
- registry drift after preflight;
- candidate changes registry.

### 8. Wire/retry/TOCTOU

Attack:

- source bytes changed after manifest freeze;
- representation changed before dispatch;
- SDK changes model/tool/file/session semantics;
- hidden automatic retry;
- retry with changed body;
- reused attempt identity;
- pre-SDK hash valid but post-SDK semantic envelope different.

### 9. Prompt-isolation dependency

Verify exact provider/mode requires a current machine-checkable:

`PromptIsolationQualificationRecord`

It must be:

- hash-bound;
- exact-mode bound;
- non-expired;
- outside candidate self-approval;
- checked at preflight and atomic admission.

WitnessProtocolQualificationRecord must bind the same isolation mechanism when witnesses are used.

### 10. Taxonomy and insufficient-evidence causes

Compare normative and live taxonomies.

Check:

- every standard EXP-M failure code exists live;
- causes are independently evaluated;
- multiple causes => MIXED_INSUFFICIENCY;
- none proven => INSUFFICIENT_EVIDENCE_CAUSE_UNRESOLVED;
- reviewer contradiction does not become scientific absence;
- delivery failure does not become scientific absence.

### 11. Deterministic falsification/test readiness

Verify the packet's claim that deterministic phases A–T are the complete current gate.

Inspect whether:

- test IDs are unique/namespaced;
- mutation catalog is authoritative;
- data/state mutations and validator-logic mutations are separate;
- every load-bearing predicate is directly mutated;
- adversarial adapters actually simulate the failure rather than merely set a summary boolean;
- qualification-attempt closure is tested;
- retry transparency is tested;
- health-check non-renewal is tested;
- context-isolation residual paths are tested;
- witness context eviction is tested;
- retrieval final-context binding is tested;
- atomic admission races are tested.

## Required output

Return exactly one overall disposition:

`BOUNDED_PASS`

or

`CHANGES_REQUIRED`

or

`INSUFFICIENT_EVIDENCE`

Then report:

### A. R4 finding closure

For each:

- R4-H01
- R4-H02
- R4-M01
- R4-M02
- R4-L01

return:

`CLOSED / PARTIAL / OPEN`

with:
- exact current-source evidence;
- remaining false-green path;
- narrow required correction if not CLOSED.

### B. New findings

List:

- Critical;
- High;
- Medium/Low.

For every finding include:

- finding ID;
- severity;
- affected rule/invariant/test;
- concrete failure/false-green path;
- why current design is insufficient;
- narrow required fix.

### C. Gate verdicts

Return:

- REQUIRED_EVIDENCE_AUTHORITY = PASS / FAIL
- DELIVERY_GOVERNOR_TRUST_ROOT = PASS / FAIL
- GOVERNANCE_AUTHORITY_AND_MERGE = PASS / FAIL
- PROVIDER_CONTEXT_ISOLATION = PASS / FAIL
- PROVIDER_CONTEXT_ADMISSION_FENCE = PASS / FAIL
- WIRE_BINDING = PASS / FAIL
- RETRY_TRANSPARENCY = PASS / FAIL
- CHUNK_CONTEXT_MODEL = PASS / FAIL
- WITNESS_ACCESSIBILITY_BOUNDARY = PASS / FAIL
- WITNESS_PROTOCOL_QUALIFICATION = PASS / FAIL
- ACCESSIBILITY_RISK_POLICY = PASS / FAIL
- PROVIDER_CAPABILITY_QUALIFICATION = PASS / FAIL
- QUALIFICATION_ATTEMPT_CLOSURE = PASS / FAIL
- STATISTICAL_PROTOCOL = PASS / FAIL
- REPRESENTATION_GOVERNANCE = PASS / FAIL
- MATERIALIZATION_SAFETY = PASS / FAIL
- EGRESS_BOUNDARY = PASS / FAIL
- SESSION_FILE_RETRIEVAL_BINDING = PASS / FAIL
- RETRIEVAL_FINAL_CONTEXT_BINDING = PASS / FAIL
- ADMISSIBILITY_PREDICATE_CLOSURE = PASS / FAIL
- INSUFFICIENT_EVIDENCE_TAXONOMY = PASS / FAIL
- MULTI_REVIEWER_EQUIVALENCE = PASS / FAIL
- DECOMPOSITION_AGGREGATION = PASS / FAIL
- PROMPT_ISOLATION_DEPENDENCY = PASS / FAIL
- TOCTOU_RETRY_INTEGRITY = PASS / FAIL
- ATOMIC_VERDICT_ADMISSION = PASS / FAIL
- REVIEWER_TOOL_EVIDENCE_BOUNDARY = PASS / FAIL
- TEST_MATRIX_SUFFICIENCY = PASS / FAIL
- VALIDATOR_LOGIC_MUTATION_COVERAGE = PASS / FAIL

### D. Final determination

State:

- whether any Critical design defect remains;
- whether any High design defect remains;
- whether EXP-M is ready for implementation/deterministic falsification;
- whether live provider pilots may begin;
- exact remaining prerequisites;
- confirmation that EXP-M remains NOT_QUALIFIED;
- confirmation that this R5 review grants no platform-review/promotion authority.

Important:

A BOUNDED_PASS here means only that the design/preregistration is ready to move into deterministic implementation/falsification.

It does NOT mean EXP-M itself is qualified.

Live provider pilots remain blocked until deterministic implementation/testing separately passes.
