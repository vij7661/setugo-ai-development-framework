# EXP-M Deterministic Implementation — Remediation R1

Status: `AUTOMATABLE_REMEDIATION_REQUIRED`

Authority effect: `NONE`

EXP-M remains `NOT_QUALIFIED`.

No live provider/API execution is allowed.

This remediation accepts `EXP-M-DETERMINISTIC-EXTERNAL-REVIEW-R1.md` as defect evidence.

## Root-cause rule

Do not patch individual PASS labels.

The central defect is that many frozen R5 invariants were modeled as caller-supplied booleans rather than computed from production evidence, and the test/mutation layer often tested those booleans or shared registries rather than independently attacking production logic.

Repair the architecture so the authoritative verdict is computed from evidence-bearing domain objects and current state.

## R1 remediation loop

```text
INVENTORY CURRENT FALSE-GREEN PATH
-> WRITE RED REPRODUCTION
-> IMPLEMENT PRODUCTION MECHANISM
-> ADD POSITIVE CONTROL
-> ADD NEGATIVE/ADVERSARIAL FIXTURES
-> ADD DATA/STATE MUTATION
-> ADD REAL VALIDATOR-LOGIC MUTATION
-> RUN PHASE
-> RUN FULL A-T
-> RUN FULL MUTATIONS
-> SELF-FALSIFY
-> CHECK GIT FOR NEXT R1 FINDING
-> CONTINUE
```

Stopping is prohibited while any R1 Critical/High item is automatable.

## R1-01 — Replace boolean admissibility with computed production predicates

Introduce predicate-specific production validator functions/objects.

At minimum each load-bearing predicate must derive from evidence/current state rather than `state[pid] is True`.

Required independent sources:

- required predicate registry;
- verdict result predicate IDs;
- mutation catalog/target IDs;
- killed mutation evidence IDs;
- negative fixture IDs.

These sources must not be aliases of one tuple.

Closure must compare independently generated sets.

Validator-logic mutation must alter/delete/weaken the actual validator implementation or dispatch mapping so the corresponding RED fixture becomes false-green if the test does not catch it.

Do not count input-state toggles as validator-logic mutations.

## R1-02 — Production provider qualification/currentness

Make preflight/admission consume:

- ProviderCapabilityProfile;
- ProviderQualificationExecutionPlan;
- ProviderCapabilityQualificationRecord;
- expected provider/model/adapter/operating-point identity;
- profile hash;
- current time/expiry;
- supported format;
- context limit;
- planned attempt closure;
- zero-hard-failure requirement where applicable;
- statistical qualification state required by policy;
- retry transparency/physical request closure.

A bare `qualified=True` can never satisfy the authoritative predicate.

Add RED attacks for:

- expired profile;
- wrong profile hash;
- wrong operating point;
- missing planned attempt;
- failed attempt replaced by retry;
- hidden retry;
- unsupported format;
- over-context;
- profile/plan mismatch;
- qualification record for different provider/model.

## R1-03 — Provider context isolation + hidden-state policy + fence

Compute context predicates from:

- ProviderContextIsolationPolicy;
- ProviderContextStateEvidence;
- required observable channels;
- readback/sentinel evidence;
- hidden-provider-state residual policy;
- transition class;
- current AdmissionFenceRecord.

Add deterministic adversarial provider state supporting:

- clean;
- dirty;
- lying readback;
- hidden semantic state;
- config drift;
- wrong/missing channel;
- stale fence;
- highest-authority hidden residual disallowed;
- dedicated-account residual allowed only under exact policy.

Integrate this into preflight and final admission.

## R1-04 — Atomic admission

Implement an authoritative `admit_review_attempt(...)` or equivalent.

It must:

1. bind the exact attempt;
2. re-read/revalidate all load-bearing current state;
3. compare expected versions/hashes/generations;
4. reject on any drift;
5. perform the authority-result commit atomically against the expected state generation;
6. mark an invalidated attempt permanently void;
7. prevent later requalification from reviving that attempt.

Revalidate at least:

- authority snapshot;
- ReviewRequest identity/currentness;
- capability profile/currentness;
- egress policy;
- context isolation policy/state;
- admission fence;
- prompt isolation record;
- witness qualification record when used;
- session/file/retrieval state;
- AdmissibilityPredicateRegistry version;
- attempt/retry closure.

Add race fixtures at every boundary:
preflight, post-dispatch, post-delivery, post-receipt, post-final-read/pre-CAS.

## R1-05 — Retrieval final-context binding

Implement a production `RetrievalEvidenceRecord` or exact equivalent containing:

- request/attempt/session identity;
- source identity/version;
- page/range/member;
- returned raw bytes hash and length;
- tool/result identity;
- retrieval timestamp/sequence;
- final adjudication context identity/hash.

The final review context must prove the retrieved result was actually inserted/bound to the same adjudication session.

Reject:

- file ID only;
- citation only;
- opened-file event only;
- wrong version;
- partial range;
- other session;
- correct bytes not bound to final context.

## R1-06 — Wire / returned-byte / representation binding

Strengthen EvidenceDeliveryManifest, WireDeliveryRecord, ReviewerReceipt and DeliveryCompletenessResult.

Completion must validate actual returned/delivered bytes, not only item IDs.

Bind:

- exact reviewed commit/source;
- request;
- attempt;
- session;
- manifest;
- raw byte hash/length;
- governed representation hash/identity;
- post-SDK semantic envelope hash;
- wire payload hash;
- receipt byte counts;
- item ordering/coverage where relevant.

A forged `complete=True` receipt with correct IDs and wrong/missing bytes must fail.

## R1-07 — Materialization / representation production path

Implement bounded production materialization sufficient for the frozen R5 contract.

Reject/limit:

- path traversal;
- absolute paths;
- ambiguous normalization;
- duplicate normalized members;
- symlink escape;
- archive recursion;
- decompression/resource bombs;
- parser time/memory/size bound violations;
- unqualified transformation;
- semantic representation mismatch.

Bind transformation identity/version/parameters, source hash, representation hash and coverage.

## R1-08 — Witness/accessibility production path

Witness validation must consume a current WitnessProtocolQualificationRecord bound to provider/mode/prompt-isolation mechanism.

Enforce:

- challenge is accessibility/extraction only;
- response content-bound;
- expected answer not reviewer-controlled;
- response byte/token budget;
- total final-context budget including witness traffic;
- post-witness pre-adjudication context recheck;
- witness output is non-evidence/non-adjudicative;
- record current/not expired/exact provider+mode;
- canary-preserving content loss still caught by load-bearing proof method where policy requires;
- witness-induced eviction rejected.

## R1-09 — Prompt isolation and accessibility-risk policies

Make PromptIsolationQualificationRecord and ProviderAccessibilityRiskPolicy actual production inputs.

Reject:

- missing/wrong/expired prompt-isolation record;
- wrong provider/mode;
- accessibility proof mode weaker than transition policy;
- deterministic-required transition using witness-only probabilistic proof;
- missing risk policy.

Revalidate prompt-isolation currentness at final admission.

## R1-10 — Insufficient-evidence taxonomy

Phase D must call the actual production adjudicator.

Implement deterministic RED/positive cases for:

- exactly one cause;
- multiple causes -> MIXED_INSUFFICIENCY;
- no proven cause -> INSUFFICIENT_EVIDENCE_CAUSE_UNRESOLVED;
- delivery/context failure distinct from scientific evidence absence;
- reviewer contradiction distinct from scientific absence.

Do not derive Phase D from a set-length or constant expression.

## R1-11 — Attempt ledger / retry transparency

Strengthen attempt closure to bind:

- frozen planned trial IDs;
- every first attempt;
- hard failure;
- retry relationship;
- provider/physical request identity;
- wire hash;
- no replacement of failed original;
- no hidden attempt;
- no duplicate first-attempt identity;
- no unscheduled call counting as confirmation.

Implicit client retries must be disabled or surfaced as separate physical attempts.

## R1-12 — Make every A-T phase falsifiable

No phase may contain unconditional PASS.

Each phase must:

- call production mechanism(s);
- have at least one positive control;
- have at least one adversarial negative fixture;
- fail when its load-bearing production guard is disabled/weakend by mutation.

Generate phase status from the actual case results.

Phase G must run the actual mutation suite.
Phase O/T must use independent closure artifacts, not same-source aliases.

## R1-13 — Expand mutation catalog

Data/state mutation coverage must include all load-bearing areas from the external review.

At minimum:

- wrong reviewed source;
- request/manifest mismatch;
- candidate-writable authority;
- evidence/interaction contract mutation;
- materialization/representation corruption;
- egress revocation;
- stale/expired capability;
- wrong qualification profile/plan;
- hidden/replaced attempt;
- retry hiding;
- context isolation violation;
- hidden-state policy violation;
- context/config drift;
- stale admission fence;
- wrong/expired prompt isolation;
- wrong/expired witness qualification;
- witness context eviction;
- retrieval wrong source/range/session/final context;
- wire/semantic/receipt payload mismatch;
- registry version drift;
- state drift before final CAS.

Validator-logic mutation must independently mutate actual production validators for every required admissibility predicate.

## R1-14 — Expand self-falsification

Self-falsification must independently attempt the full Critical/High false-green set, not just mirror normal unit cases.

At minimum reproduce each external R1 Critical and High attack after remediation.

A self-falsification count of zero survivors is meaningful only when the attack suite covers all current Critical/High families.

## R1-15 — Evidence freshness and review packet integrity

After the final production-code change:

1. rerun all unit/integration tests;
2. rerun A-T;
3. rerun data/state mutations;
4. rerun validator-logic mutations;
5. rerun self-falsification;
6. regenerate every result JSON;
7. regenerate review packet from those exact fresh artifacts;
8. bind review packet to exact implementation commit/tree;
9. do not reuse stale result JSON.

Preserve historical false-green R1 evidence and first failures; label them superseded, do not delete them.

## Exit criteria for R1 remediation

Codex may stop only when all are true:

- all 11 Critical findings have direct production fixes and regression tests;
- all 10 High findings have direct production fixes and regression tests;
- all Medium/Low findings are either fixed or explicitly bounded with no Critical/High impact;
- no hard-coded phase PASS remains;
- no load-bearing authority predicate is a caller-supplied summary boolean;
- all A-T phases derive from production positive + adversarial cases;
- all A-T pass;
- data/state mutation survivors = 0;
- validator-logic mutation survivors = 0;
- independent predicate closure is exact;
- expanded self-falsification Critical survivors = 0;
- expanded self-falsification High survivors = 0;
- frozen R5 design has not been weakened;
- EXP-M remains NOT_QUALIFIED;
- live provider execution remains false;
- a fresh independent review packet is generated.

Then return:

`DETERMINISTIC_REVIEW_REQUIRED`

and stop for external review.

## No-stop rule

If any item above remains automatable:

`AUTOMATABLE_WORK_REMAINS`

and Codex must inspect Git/repository state and continue automatically.

Do not stop after a single repaired finding, green test file, commit, phase, or mutation run.
