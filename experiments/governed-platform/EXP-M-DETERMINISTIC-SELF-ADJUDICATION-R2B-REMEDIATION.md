# EXP-M Deterministic Implementation — Internal Self-Adjudication R2B Remediation

Status: `AUTOMATABLE_WORK_REMAINS`

Authority effect: `NONE`

EXP-M remains `NOT_QUALIFIED`.

Live provider/API qualification and execution remain blocked.

This remediation supersedes the R2A external-review stop. Internal source adjudication of the frozen R2A source commit found remaining automatable Critical/High false-green paths. Do not send the current R2A packet to an external reviewer yet.

## 1. Independent predicate / mutation / fixture closure

### 1.1 Fixture catalog must be genuinely independent

The current source aliases:

`INDEPENDENT_FIXTURE_CATALOG = tuple(INDEPENDENT_MUTATION_CATALOG)`

This is not independent closure.

Replace it with a separately declared fixture catalog whose records contain at least:

- fixture_id
- target_predicate_id
- immutable fixture constructor/reference
- expected rejection predicate/reason

The fixture catalog must not be generated from:

- PREDICATES
- PREDICATE_DEFINITIONS
- mutation catalog
- runtime verdict output

### 1.2 Mutation catalog must be separately declared

Mutation target declarations must live independently from the required predicate registry and fixture catalog.

Closure compares target predicate IDs, not raw mutation/fixture IDs.

### 1.3 Exact closure inputs

Require exact equality among:

- platform-required predicate IDs;
- actual VerdictAdmissibilityResult predicate IDs from the current run;
- declared mutation target predicate IDs;
- executed mutation target predicate IDs;
- killed mutation target predicate IDs;
- declared negative-fixture target predicate IDs;
- executed negative-fixture target predicate IDs.

Also require at least one executed/killed logic mutation and one executed negative fixture per required predicate.

No default argument may silently substitute declared sets for missing executed sets.

Missing evidence => closure FAIL.

## 2. Remove remaining summary-boolean authority

The following types currently still contain authority-like booleans:

- AccessibilityProofRecord.valid
- ReviewerProvenanceRecord.trusted
- SemanticCoverageRecord.complete
- SemanticContextQualificationRecord.qualified
- PromptIsolationQualificationRecord.current
- WitnessProtocolQualificationRecord.current
- ProviderContextStateEvidence.clean/sentinel_passed
- AdmissionFenceRecord.current
- ProviderCapabilityQualificationRecord.statistical_qualified
- ReviewerReceipt.complete
- DeliveryCompletenessResult.complete

A boolean may remain as cached/diagnostic consistency metadata only.

Authoritative predicates must recompute from load-bearing evidence.

### 2.1 Accessibility

`accessibility_proven` must not return `proof.valid`.

Validate:

- proof identity;
- proof mode allowed by risk policy;
- transition class;
- deterministic-required rule;
- challenge/source-slice binding;
- witness/retrieval evidence hash;
- final context identity/hash;
- externally expected provider/mode;
- current policy version.

### 2.2 Semantic context

`semantic_context_qualified` must not trust `record.qualified`.

Validate exact context bytes/hash or an independently derived semantic-context receipt bound to:

- source/evidence set;
- final context ID/hash;
- provider/session/attempt;
- qualification mechanism identity/version.

### 2.3 Reviewer provenance

`reviewer_provenance` must not trust `record.trusted`.

Validate a typed reviewer authorization/provenance record against an externally supplied reviewer policy/trust root/authorization source in PredicateContext.

### 2.4 Prompt/witness currentness

Current/expiry checks must be derived from:

- signed/platform-owned record identity;
- provider/mode binding;
- issue/expiry times;
- trusted clock;
- revocation/current authority state.

A caller-created typed record with `current=True` is insufficient.

### 2.5 Context/fence

Context cleanliness, sentinel success and fence currentness must be recomputed from evidence/current state and externally expected fence/config generation.

A caller-created ContextIsolationVerdict must not be sufficient by itself.

## 3. External expectations must not self-bind

### 3.1 Wire semantic hash

Current authoritative wire validation must not pass:

`expected_semantic_hash = wire.semantic_hash`

Expected semantic envelope identity/hash must come from PredicateContext or be independently recomputed from the frozen request + provider/tool/file/session semantics.

### 3.2 Witness expected answer

Current witness predicate must not accept an expected answer supplied in the same EvidenceBundle as the challenge/response.

PredicateContext or a trusted harness record must bind:

- challenge ID;
- source slice ID/hash;
- expected answer/hash;
- generation time after evidence freeze;
- provider/mode/prompt mode.

The reviewer/fake provider must not receive the expected answer.

### 3.3 Transition/fence

Context isolation validation must use the externally expected transition class and fence version from PredicateContext, not values supplied by the ContextIsolationVerdict itself.

## 4. Provider capability statistical qualification must be recomputed

The authoritative capability validator must not trust:

`record.statistical_qualified`

For the frozen R5 statistical mode, recompute qualification from the exact immutable attempt set and qualification protocol.

Where the R5 program requires the 0.99 lower-bound / one-sided 95% exact Clopper-Pearson / zero-hard-failure confirmation rule:

- confirmation trial requirement is derived from the frozen program;
- all required planned roots are present;
- every physical first attempt is counted;
- retries cannot replace failures;
- hard failures remain failures;
- no optional stopping/reroll/exclusion;
- the statistical lower bound is computed deterministically;
- cached `statistical_qualified` may only be checked for consistency.

A one-trial toy plan must not satisfy a production predicate that claims the full statistical qualification class.

If deterministic unit fixtures use a reduced program, that program must be explicitly a non-authoritative TEST_PROFILE and cannot satisfy the production qualification predicate used for the material transition.

## 5. Persistent admission CAS must bind protected state generation atomically

The current ledger guarantees one terminal insert per attempt, but it does not atomically store/compare the full protected authority generation/current-state identity.

Extend the transactional schema so the same SQLite transaction:

- reads current protected generation/state token;
- compares expected generation/token;
- verifies attempt not terminal;
- writes VOID or COMMITTED;
- advances/records protected generation as required.

The admission call must not:

1. evaluate evidence,
2. release control,
3. compare an unprotected caller dictionary,
4. then write terminal state.

Either perform final revalidation inside the transaction against authoritative persisted state or use a qualified serialized-writer/fencing abstraction whose state token is transactionally checked.

Add two concurrent writer tests and restart/ABA tests.

## 6. Typed materialization must derive rather than trust archive metadata

Current MaterializationEntry fields such as:

- normalized_path
- compressed_size
- uncompressed_size
- recursion_depth

must not be blindly trusted when they are the facts being proved.

For each supported materialization mode:

- derive normalized path from raw member name;
- verify supplied normalized path matches derived canonical path if stored;
- derive archive nesting depth from actual traversal;
- derive uncompressed bytes from actual extracted content;
- obtain compressed-size metadata from the archive/container parser;
- resolve symlink target against the containing path and prove it remains under the extraction root.

Tests must include canonicalization aliases, nested archives, symlink-relative escape and falsified size/depth metadata.

## 7. Required/optional evidence contract exactness

Add an explicit allowed optional-evidence set or equivalent governed rule.

Preflight must prove:

`manifest_ids == required_ids UNION approved_present_optional_ids`

with:

- every required ID present exactly once;
- no unknown extra;
- canonical unique IDs.

Do not allow any manifest item merely because all required IDs are present.

## 8. Interaction contract must prove observed co-context

Observed interactions must be generated from actual delivered/final-context structure.

Do not allow the caller to provide an `observed_interactions` tuple that merely equals RequiredInteractionContract.

The authoritative interaction predicate must derive which required evidence IDs coexisted in the same final adjudication context/session and compare that derived relation to the contract.

## 9. Retry and physical-attempt closure

Qualification and retry predicates must additionally prove:

- every physical attempt has unique physical attempt ID;
- provider request ID when available is unique/bound;
- every FIRST maps to exactly one planned root;
- every RETRY maps to an existing failed parent;
- request/session/wire hashes match frozen root expectations;
- hidden client retries are impossible or surfaced;
- unscheduled FIRST attempts are preserved but excluded from confirmation count;
- duplicate dispatch cannot increment confirmation count.

Cached planned/closed attempt ID sets are consistency-only.

## 10. Phase A–T evidence must be real, not synthetic metadata

The current phase runner appends generic metadata after phase status is already known:

`<phase>-positive-control`
`<phase>-adversarial-negative`

with the negative result derived from `phase status == PASS`.

This violates the R2A requirement.

Remove this generic post-processing.

Define and execute explicit phase case records.

Every case record must include:

- case_id;
- phase_id;
- kind;
- production function(s) invoked;
- exact input/fixture identity;
- expected outcome;
- actual outcome;
- rejection predicate/reason for negative cases;
- applicable mutation target(s).

Phase status is computed from its executed case records.

At minimum:

- every phase has one independently executed positive control;
- every phase has one meaningful negative/adversarial case;
- phases G/I/O/T consume actual mutation artifacts;
- phases O/T consume actual independent closure artifacts;
- Phase L invokes the full typed materialization engine, not only `safe_archive_member`;
- Phase P invokes full context isolation, not only `validate_context_state`;
- Phase Q checks risk policy + expected fence version;
- Phase R checks trusted witness expected-answer/accessibility proof;
- Phase S/T use a nontrivial planned-root + failed-parent + retry physical ledger.

## 11. Mutation authenticity and independence

The isolated subprocess requirement is good but still insufficient if:

- base fixture is constructed from legacy summary fields;
- negative fixture mapping is hardcoded in the same mutation runner;
- several predicates are mutated as one family;
- killed is defined as “mutant returned admissible” without an independent oracle that detects the false-green.

Required:

1. fixture comes from independent fixture catalog;
2. normal production rejects fixture with expected target predicate;
3. exactly one production guard is mutated in fresh process;
4. same immutable fixture/context is used;
5. mutant creates the target false-green;
6. independent harness oracle detects the semantic divergence;
7. mutation is killed only then.

Do not mutate multiple related predicates as a family for a single mutation target unless the frozen mutation definition explicitly declares a compound mutation.

## 12. Self-falsification must not false-green on source-string checks

The self-falsification case for synthetic phase metadata currently searches source text for one literal pattern.

Replace source-string absence checks with behavioral checks over generated phase artifacts:

- verify each negative case corresponds to an actual executed invocation;
- verify its expected rejection reason;
- independently perturb one case and show phase FAIL;
- remove one case artifact and show closure FAIL.

Likewise, static scans may supplement but not substitute for behavioral proof.

## 13. Source/evidence/packet discipline

The existing S -> E -> P sequence is structurally useful but is superseded by this remediation because S still contains the findings above.

For R2B:

### Source S2
- source/test/mutation/self-falsification/packet-builder code only;
- no generated results/review packet changes;
- clean working tree.

### Evidence E2
- run exactly S2;
- every result/log explicitly records S2 commit/tree;
- evidence commit changes generated evidence only.

### Packet P2
- review packet/docs only;
- packet names S2 and E2 explicitly;
- no implementation/test/mutation code changes.

Any post-P2 merge/documentation commit must not be represented as reviewed source.

## 14. R2B self-adjudication exit

Before external review, independently attack every item above.

Required:

- unresolved Critical = 0;
- unresolved High = 0;
- no known automatable false-green path.

Do not expose the detailed self-adjudication findings in the external packet; publish a commitment if needed and reveal after review.

## 15. R2B exit criteria

Do not generate an external-review-ready packet until all are true:

1. fixture catalog is genuinely independent of mutation/predicate registries;
2. exact closure uses declared/executed/killed mutation and declared/executed fixture target sets;
3. accessibility, semantic-context, reviewer provenance, prompt/witness currentness and context/fence predicates do not trust authority booleans;
4. no expected value is self-bound from the evidence record being validated;
5. statistical qualification is recomputed from the frozen qualification protocol and physical attempts;
6. admission CAS atomically binds protected state generation/currentness;
7. materialization derives canonical/archive facts from actual inputs;
8. evidence manifest exact required/optional set is enforced;
9. interaction co-context is observed from actual delivered/final context;
10. retry/physical-attempt closure is complete;
11. A–T phases consist of real executed positive/negative cases, not synthetic metadata;
12. validator mutation fixtures/catalogs/oracles are independent and one-target-at-a-time;
13. self-falsification behaviorally attacks phase/closure evidence;
14. fresh S2 -> E2 -> P2 sequence exists;
15. all tests/mutations/self-falsification bind to S2;
16. self-adjudication finds zero unresolved Critical/High;
17. EXP-M remains NOT_QUALIFIED;
18. live provider/API execution remains false;
19. authority effect remains NONE.

Then return `DETERMINISTIC_REVIEW_REQUIRED` and stop for independent external review.

## 16. No-stop rule

If any R2B item remains automatable:

`AUTOMATABLE_WORK_REMAINS`

and Codex must inspect the repository and continue.

Do not stop on a green subtest, phase, mutation run or commit.

Do not use live provider APIs.
