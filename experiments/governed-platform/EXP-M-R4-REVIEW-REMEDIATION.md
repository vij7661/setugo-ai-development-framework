# EXP-M R4 External Review Adjudication and Remediation

## Status

`R4_CHANGES_REQUIRED_ACCEPTED_AND_REMEDIATED_FOR_R5_REVIEW`

The supplied R4 external review is accepted as valid defect evidence. It remains external/manual review evidence only and grants no platform review, promotion, implementation, or live-provider authority.

EXP-M remains `NOT_QUALIFIED`.

## R4 disposition

R4 returned `CHANGES_REQUIRED`.

R4 design closure:
- R3-C01: CLOSED
- R3-H02: CLOSED
- R3-H03: CLOSED
- R3-H04: CLOSED
- R3-M01: CLOSED
- R3-M02: CLOSED
- R3-M03: CLOSED
- R3-M04: CLOSED
- R3-L01: CLOSED
- R3-L02: CLOSED
- R3-L03: CLOSED

R4 kept open/partial:
- R3-H01 via R4-H01
- R3-H05 via R4-H02
- R3-M05 via R4-M01

R4 additionally found:
- R4-M02 — undefined per-element “stricter” comparison;
- R4-L01 — no targeted health-check-renewal test.

## R4-H01 — hidden unexposed mutable provider semantic state

Evaluation: **VALID / HIGH**

Repair:

1. Added platform-owned `ProviderContextIsolationPolicy` selected from the GovernanceAuthoritySnapshot.
2. Defined two isolation bases:
   - `COMPLETE_READABLE_FENCED_STATE`;
   - `DEDICATED_PLATFORM_ACCOUNT_STATELESS_BOUNDARY`.
3. The dedicated-account basis requires:
   - platform-owned provider account/project/credential;
   - no candidate/end-user provider-config writes;
   - pinned provider product documentation/contract;
   - exact provider account class and production configuration-template hash;
   - exposed mutable semantic features disabled/read back;
   - disposable qualification account for sentinel tests so production review account is not contaminated;
   - production config template match and fence.
4. Hidden provider-internal mutable semantic state is now an explicit nonclaim/residual, never an “observed clean” assertion.
5. Each transition policy chooses:
   - `DISALLOW`; or
   - `DEDICATED_ACCOUNT_EXTERNAL_TRUST_BOUNDARY`.
6. Highest material-authority transition defaults to `DISALLOW`.
7. Added failure codes:
   - `PROVIDER_CONTEXT_HIDDEN_STATE_RESIDUAL`;
   - `PROVIDER_CONTEXT_ISOLATION_POLICY_MISSING`.
8. Added hidden-state, dedicated-account, sentinel-contamination, config-drift, and admission-fence tests/adapters.

## R4-H02 — incomplete validator-logic mutation coverage

Evaluation: **VALID / HIGH**

Repair:

1. Added explicit targeted Phase-O mutations for every current `VerdictAdmissibilityResult` predicate:
   - ReviewRequest;
   - authority snapshot;
   - evidence contract;
   - interaction contract;
   - materialization;
   - representation/transformation;
   - egress;
   - provider capability;
   - accessibility risk;
   - context isolation;
   - hidden-state residual policy;
   - provider context state;
   - admission fence;
   - semantic-context qualification;
   - post-SDK wire binding;
   - complete item/chunk delivery;
   - per-attempt accessibility proof;
   - witness qualification/context budget;
   - session/file/retrieval coverage;
   - prompt isolation;
   - semantic review coverage;
   - reviewer provenance/independence;
   - promotable disposition.
2. Added platform-owned `AdmissibilityPredicateRegistry`.
3. Required exact closure:

`required predicates == VerdictAdmissibilityResult predicates == logic mutation targets == independently killed mutations`

4. New predicates without a targeted negative fixture and killed logic mutation fail as `ADMISSIBILITY_PREDICATE_COVERAGE_INCOMPLETE`.
5. Candidate edits to the predicate registry used for their own review are rejected.

## R4-M01 — live taxonomy mismatch

Evaluation: **VALID / MEDIUM**

Repair:

The live-governance failure taxonomy was reconciled against the normative standard. It now includes all EXP-M standard codes, including:

- `EVIDENCE_SELECTION_CONTRACT_UNRESOLVED`
- `GOVERNANCE_AUTHORITY_SNAPSHOT_MISMATCH`
- `REVIEWER_EVIDENCE_ASSESSMENT_CONTRADICTION`
- `PROVIDER_CONTEXT_STATE_UNPROVEN`
- `PROVIDER_CONTEXT_STATE_DRIFT`
- `PROVIDER_CONTEXT_HIDDEN_STATE_RESIDUAL`
- `PROVIDER_CONTEXT_ISOLATION_POLICY_MISSING`
- `PROVIDER_RETRIEVAL_COVERAGE_UNPROVEN`
- `PROVIDER_RETRIEVAL_CONTEXT_BINDING_UNPROVEN`
- `STATISTICAL_INDEPENDENCE_UNPROVEN`
- `VERDICT_ADMISSION_STATE_CHANGED`
- `INSUFFICIENT_EVIDENCE_CAUSE_UNRESOLVED`
- `MIXED_INSUFFICIENCY`
- `EVIDENCE_MATERIALIZATION_FAILED`
- `EVIDENCE_FILE_REFERENCE_UNQUALIFIED`
- witness, qualification-attempt, retry and predicate-coverage codes added during self-adjudication.

A source-vs-live taxonomy comparison after repair reports no normative standard code missing from live governance.

## R4-M02 — undefined stricter partial order

Evaluation: **VALID / MEDIUM**

Repair:

Added typed comparison rules:

- required refs/dimensions/interactions: superset stricter;
- allowed representation/provider/region/tool sets: intersection stricter;
- fidelity: raw/lossless > bounded-loss > summary, with incomparable media semantics unresolved;
- review level: REQUIRED > RECOMMENDED > NONE;
- egress: deny > conditional allow > allow; incomparable conditions unresolved;
- statistical lower-bound/confidence: larger requirement stricter;
- tolerated failure/residual risk: smaller stricter;
- minimum confirmation trials: larger stricter when acceptance semantics match;
- expiry interval: shorter stricter;
- runtime size/count limits: smaller stricter;
- accessibility proof: deterministic > probabilistic/content-bound > self-attestation;
- prompt isolation: superset of required predicates stricter;
- transition rank: only authority registry defines order.

Same-dimension semantic changes without a comparator are never auto-merged and fail `EVIDENCE_SELECTION_CONTRACT_UNRESOLVED`.

Comparator mutations are included in deterministic falsification.

## R4-L01 — health check renewal

Evaluation: **VALID / LOW**

Repair:

Added explicit tests that an expired ProviderCapabilityProfile cannot be renewed or extended by a health check. Full governed confirmation requalification is required. Health checks may invalidate only.

## Additional iterative self-adjudication

After the direct R4 repairs, additional adversarial design passes were performed.

### SA-R5-H01 — witness proof could evict evidence before final adjudication

Severity: **High**

Failure path:
witness challenges/responses prove accessibility, but their transcript consumes enough context to evict the evidence before the semantic verdict.

Repair:
- witness challenge/response overhead, wrappers, final prompt and final output budget are part of the qualified operating point;
- actual context size is rechecked after witness phase and before adjudication;
- witness-induced eviction voids the attempt;
- added `WITNESS_CONTEXT_EVICTION`.

### SA-R5-H02 — witness protocol could contaminate semantic review

Severity: **High**

Failure path:
accessibility probes themselves become evaluative evidence or alter the review authority basis.

Repair:
- `WitnessProtocolQualificationRecord` added and kept outside candidate write authority;
- witness prompts are extraction/accessibility only;
- witness outputs are tagged non-evidence/non-adjudicative and cannot satisfy semantic review dimensions;
- exact final semantic prompt remains hash-bound under prompt-isolation governance;
- EXP-M explicitly does **not** claim counterfactual semantic invariance for stochastic remote models;
- A/B outcome comparisons are diagnostic only.

### SA-R5-H03 — provider qualification sample could be cherry-picked

Severity: **High**

Failure path:
failed/skipped confirmation calls are omitted, retried until success, or unlogged calls are used selectively.

Repair:
- added frozen `ProviderQualificationExecutionPlan`;
- complete planned trial IDs/schedule/interleaving seed frozen before exposure;
- dedicated trusted qualification runner and credential/egress identity;
- candidate/user/ordinary-operator invocation prohibited;
- missing planned slot counts hard failure;
- retry cannot replace original failure;
- provider request/audit reconciliation used when exposed;
- where provider audit logs are absent, qualification credential/egress must be technically exclusive to trusted runner;
- unexplained calls invalidate the epoch or yield `QUALIFICATION_ATTEMPT_CLOSURE_UNPROVEN`.

### SA-R5-H04 — implicit SDK retries could hide first failures

Severity: **High**

Failure path:
a physical request fails, SDK silently retries, and platform records only one success.

Repair:
- implicit client/SDK retries disabled by default;
- otherwise every physical attempt requires its own immutable WireDeliveryRecord/qualification record;
- hidden retry produces `IMPLICIT_RETRY_UNOBSERVED`;
- added deterministic retry adapters/tests.

### SA-R5-H05 — explicit predicate list could drift again

Severity: **High**

Failure path:
a future admissibility predicate is added without a matching targeted logic mutation.

Repair:
- added machine-readable `AdmissibilityPredicateRegistry`;
- exact set closure between required predicates, verdict-result predicates, mutation targets and killed mutations;
- registry drift after preflight is admission-invalidating;
- candidate cannot edit the authoritative registry used for own review.

### SA-R5-M01 — statistical independence could be overclaimed

Severity: **Medium**

Repair:
- Clopper–Pearson probability claim is explicitly conditional on evidenced trial-independence/correlation control;
- `STATISTICAL_INDEPENDENCE_UNPROVEN` forbids `statistical_qualified=true` when the transition policy requires the probability claim;
- only a policy that explicitly waives that probability claim and requires deterministic per-attempt proof may proceed without it.

### SA-R5-M02 — witness qualification authority could self-grant

Severity: **Medium**

Repair:
- WitnessProtocolQualificationRecord and registry are platform-owned/outside candidate write authority;
- provider/prompt-isolation/witness-protocol drift invalidates the record;
- candidate-authored witness qualification is rejected.

## Current deterministic preregistration scope

The test matrix now gates deterministic phases **A–T** before any live provider pilot.

The design requires:

- all A–T deterministic phases green;
- zero data/state mutation survivors;
- zero validator-logic mutation survivors;
- exact admissibility predicate/mutation set closure;
- qualification-attempt set closure;
- retry transparency;
- provider-context isolation policy closure;
- witness context-budget and structural-isolation closure;
- atomic final admission;
- no live-provider pilot before deterministic qualification.

## Fresh self-adjudication result

A fresh adversarial pass after the above repairs found:

- open Critical design findings: **0**
- open High design findings: **0**

Residual limitations are explicit rather than silently promoted:

- remote model cognition/attention is not proved;
- hidden provider-internal state is either disallowed or an independently governed external-trust residual;
- provider telemetry remains provider-originated evidence;
- statistical probability claims are conditional on the stated independence model;
- selective sub-slice loss is outside probabilistic witness guarantees unless deterministic proof is required by policy;
- EXP-M is still only design/preregistration;
- no deterministic implementation has run;
- no provider mode is live-qualified.

This is proposer/model self-review only and has no independent authority.

## R5 handoff

`READY_FOR_R5_INDEPENDENT_DESIGN_REVIEW`

EXP-M remains `NOT_QUALIFIED`.

No live provider pilot may begin from this record.
