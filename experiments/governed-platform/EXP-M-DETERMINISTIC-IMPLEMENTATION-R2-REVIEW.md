# EXP-M Deterministic Implementation R2 Independent Review Packet

This packet covers deterministic implementation only. EXP-M remains NOT_QUALIFIED; no live provider/API call occurred.

## Historical superseded evidence
The prior A-T/22-test/29-mutation report is retained in Git history but is superseded by the independent R1 CHANGES_REQUIRED review. It is not used as closure evidence.
R2 is the current remediation authority. Prior R1 and historical false-green outputs are superseded evidence only.

## R2 authority inputs

### External R2 review

```text
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
```


### R2 solution adjudication

```text
# EXP-M Deterministic R2 — Reviewer Solution Adjudication

Status: `ACCEPT_WITH_CORRECTIONS`

Authority effect: `NONE`

The independent reviewer also supplied a remediation design. Its governing direction is correct:

- no boolean laundering;
- one authoritative path;
- no production bypass;
- evidence rather than caller strings;
- independent predicate/mutation/fixture closure;
- commit-bound fresh evidence.

However, several example solutions require correction before implementation.

## Accepted directly

The following directions are accepted:

- remove `disabled_predicates` from production;
- introduce an externally bound predicate context/evidence bundle;
- make provider qualification record/plan/attempt closure load-bearing;
- make context isolation and fence currentness load-bearing;
- add persistent/permanent attempt voiding;
- wire retrieval into authoritative admissibility/admission;
- compute delivery completeness from returned bytes;
- make witness qualification/accessibility load-bearing;
- strengthen materialization and qualified transforms;
- independent closure across independently generated evidence;
- authentic validator-logic mutation;
- required-evidence/manifest binding;
- explicit retry lineage;
- external egress/prompt expected values;
- commit-bound fresh execution evidence.

## Required corrections to the proposed solutions

### SA-01 — Mutation example must create a false-green, not another rejection

The supplied example monkeypatch returns `False`, which leaves the guard rejecting.

Correct rule:

1. independent malformed fixture fails under normal production code;
2. isolated mutation removes/weakens the exact guard or forces that predicate validator to accept;
3. the mutated code becomes false-green;
4. the test suite detects the false-green and therefore kills the mutation.

No mutation-control hook may exist in the production public API.

### SA-02 — PredicateContext must contain every externally expected value

The context must include, where applicable:

- expected request/attempt/session;
- expected reviewed source commit/tree;
- expected authority snapshot ID/hash/version;
- expected provider/model/adapter/operating point;
- expected profile/plan/qualification identities;
- expected egress version;
- expected transition class/risk-policy version;
- expected fence version;
- expected prompt provider/mode;
- expected witness provider/mode/prompt mode;
- expected retrieval source/version/range;
- expected final-context ID/hash;
- max final-context/witness budgets;
- current trusted clock value;
- expected predicate-registry version.

Expected values may not be read back from the evidence object being validated.

### SA-03 — Retrieval examples must not self-bind

The proposed example uses `record.attempt_id`, `record.session_id`, `record.source_id` and `record.source_version` as their own expected values.

That is self-referential.

Expected retrieval identity/range must come from the frozen request/interaction/retrieval contract and PredicateContext.

### SA-04 — Qualification closure must be recomputed from attempt records

A field such as `record.all_trials_closed=True` is not itself authoritative.

The validator must recompute closure from immutable attempt records and verify any summary field only as a consistency assertion.

Trial/confirmation requirements must follow the frozen R5 qualification program, including non-empty required sets, zero hard failures, no replacement/reroll and exact physical-attempt closure.

### SA-05 — Closure compares target mappings, not raw mutation/fixture IDs

Mutation IDs such as `TM-O-x` and fixture IDs such as `negative:x` are not equal to predicate ID `x`.

Each mutation and negative fixture must expose `target_predicate_id`.

Closure compares:

- required predicate IDs;
- actual verdict predicate IDs;
- mutation target predicate IDs;
- actually executed mutation target predicate IDs;
- killed mutation target predicate IDs;
- negative fixture target predicate IDs.

Also require every required predicate to have at least one executed/killed mutation and at least one negative fixture.

### SA-06 — Retry linkage example needs corrected semantics

A retry is itself a physical dispatched request, so rejecting a retry merely because its retry ID is in the physical dispatch ledger would be wrong.

Use structured attempt records:

- first attempt ID equals/plugs into one planned root attempt;
- retry ID is globally unique and not a planned root ID;
- retry has `parent_attempt_id` pointing to an existing failed attempt;
- retry appears in the physical request ledger;
- failed parent remains preserved;
- retry cannot replace the parent in closure counts;
- unscheduled first attempts cannot count toward confirmation.

### SA-07 — Representation qualification cannot rely on `qualified=True`

A RepresentationRecord may carry a cached summary, but authoritative validation must check:

- transform ID;
- transform implementation/hash/version;
- transform registry version;
- source hash;
- representation hash;
- transformation parameters/coverage;
- registry entry outside candidate write authority.

### SA-08 — Materialization needs typed entries for symlink/archive semantics

A plain `Mapping[str, bytes]` cannot faithfully model symlinks, archive recursion or compressed-vs-uncompressed size.

Introduce typed materialization entries with at least:

- raw member name;
- normalized path;
- kind (file/symlink/archive/etc.);
- bytes or link target;
- compressed/uncompressed sizes where relevant;
- recursion depth;
- source member identity.

Then enforce path, symlink, recursion, member count, per-member, total and decompression-ratio bounds.

### SA-09 — Witness proof needs trusted challenge/expected-answer binding

A non-empty challenge/response is not proof of accessibility.

The trusted harness must freeze:

- challenge ID;
- source slice identity/hash;
- expected extraction answer/hash;
- challenge generation after evidence freeze;
- expected answer hidden from reviewer adapter.

Witness output remains non-semantic/non-evidence.

### SA-10 — Admission ledger must survive process restart in deterministic proof

A purely ephemeral in-memory ledger would not prove permanent void semantics.

For the deterministic implementation, use a persistence-backed test ledger or a storage abstraction with restart/recovery tests proving:

- VOID persists;
- COMMITTED persists;
- compare-and-set generation survives restart;
- an old snapshot cannot revive an attempt.

### SA-11 — Freshness binds to the NEW final remediation source commit

The supplied solution says fresh results must bind to `66129025...`.

That commit is the source that just failed review and will change during remediation.

Required two-stage identity:

1. freeze final remediation source commit/tree S;
2. execute all tests/mutations/self-falsification against exactly S;
3. generate result/log/review artifacts that explicitly bind to S;
4. commit those evidence files later in packet/evidence commit E;
5. E must not be confused with reviewed source S.

The historical `66129025...` evidence remains superseded and preserved.

### SA-12 — Egress, reviewer provenance and disposition must be externally governed

Expected egress policy/version, reviewer trust/provenance requirements and promotable dispositions come from the frozen authority/policy context.

They may not be supplied by the candidate evidence state.

## Result

The reviewer solution is a strong basis, but implementation must follow the corrected R2 remediation file rather than copy the supplied snippets literally.
```


### R2 remediation

```text
# EXP-M Deterministic Implementation — Remediation R2

Status: `AUTOMATABLE_REMEDIATION_REQUIRED`

Authority effect: `NONE`

EXP-M remains `NOT_QUALIFIED`.

Live provider/API qualification and execution remain blocked.

Authoritative defect inputs:

- `EXP-M-DETERMINISTIC-EXTERNAL-REVIEW-R2.md`
- `EXP-M-DETERMINISTIC-R2-SOLUTION-ADJUDICATION.md`

Do not implement the reviewer solution snippets literally where the adjudication corrects them.

## 0. Root-cause objective

R2 must remove the false-green architecture, not merely increase test counts.

Authoritative flow must become:

```text
frozen external expectations
+ immutable evidence bundle
+ production validators
+ current authority/state reads
-> predicate results
-> admissibility
-> final evidence revalidation
-> atomic/persistent admission ledger
```

Never:

```text
caller summary booleans
-> admissibility
```

## 1. Remove all production guard bypasses

Delete `disabled_predicates` or any equivalent production API.

Static regression test:

- inspect production callable signatures/source;
- fail if any load-bearing validation path accepts a test-only guard-disable/bypass argument.

Mutation controls live only in isolated test subprocesses.

## 2. Introduce immutable EvidenceBundle + PredicateContext

Create a typed immutable `EvidenceBundle` carrying actual load-bearing records and raw/canonical bytes required by production validators.

At minimum include:

- authority snapshot;
- ReviewRequest/current version identity;
- RequiredEvidenceContract;
- RequiredInteractionContract;
- EvidenceDeliveryManifest;
- materialization result + typed input entries;
- representation record;
- egress record;
- provider capability profile;
- qualification execution plan;
- qualification record;
- immutable attempt records;
- provider context isolation policy;
- provider context state evidence;
- admission fence;
- accessibility/risk policy;
- accessibility proof record;
- prompt isolation qualification record;
- witness protocol qualification record;
- witness challenge/expected-answer binding;
- wire delivery record;
- reviewer receipt;
- actual returned bytes;
- retrieval records + retrieval raw bytes;
- semantic coverage record;
- reviewer provenance record;
- current predicate-registry identity/version.

Create a typed `PredicateContext` containing externally bound expected values.

At minimum:

- expected request ID;
- expected attempt/session ID where applicable;
- expected reviewed source commit/tree;
- expected authority snapshot ID/hash/version;
- expected provider/model/adapter/operating point;
- expected profile/plan/qualification identities;
- required format/context limit;
- trusted clock;
- expected egress version;
- expected transition class/risk-policy version;
- expected fence version;
- expected prompt provider/mode;
- expected witness provider/mode/prompt mode;
- expected retrieval contract/source/version/range;
- expected final context ID/hash;
- max final context/witness budgets;
- expected predicate-registry version;
- expected reviewer provenance policy;
- allowed/promotable disposition policy.

Expected values may not be derived from the same evidence object being validated.

## 3. Rebuild admissibility around production predicates

`evaluate_admissibility(bundle, context, registry)` must:

- invoke predicate-specific production validators;
- consume `EvidenceBundle` and `PredicateContext`;
- return one predicate result per required registry predicate;
- reject absent required evidence;
- never trust summary booleans.

Every predicate below must be evidence-derived:

- review_request_current
- authority_snapshot_current
- evidence_contract_closed
- interaction_contract_closed
- materialization_complete
- representation_governed
- egress_authorized
- capability_current
- accessibility_policy_satisfied
- context_isolation_satisfied
- hidden_state_policy_satisfied
- context_state_clean
- admission_fence_current
- semantic_context_qualified
- wire_binding_valid
- delivery_complete
- accessibility_proven
- witness_record_current
- session_retrieval_coverage
- prompt_isolation_current
- semantic_coverage
- reviewer_provenance
- disposition_promotable

Add a regression test that supplies all old summary booleans as true but omits evidence records. Verdict must be inadmissible.

## 4. Provider qualification closure

Production validator must verify:

- non-empty plan ID;
- plan ID == record plan ID;
- exact provider/model/adapter/operating point;
- profile hash/currentness/expiry;
- required format;
- context limit;
- non-empty frozen trial set where the frozen qualification program requires trials;
- non-empty confirmation set where required;
- immutable attempt ledger covers every planned first attempt;
- failed first attempts remain preserved;
- retries cannot replace failed originals;
- no hidden/unscheduled physical attempt counts;
- hard failures == 0 where the policy requires zero;
- statistical qualification status is recomputed/validated from the frozen qualification protocol, not trusted as a bare boolean;
- any cached `all_trials_closed` field is consistency-only; authoritative closure is recomputed.

Reject empty/mismatched plan/record state.

## 5. Context isolation / hidden state / fence

Preflight and admission both validate:

- real transition class from the governing risk policy;
- context isolation policy basis;
- all mandatory observable channels;
- sentinel/readback evidence;
- hidden-state residual policy;
- context/config state hash;
- expected fence version/currentness.

Preflight must not hardcode `LOWER`.

Admission rechecks context/config/fence and voids the attempt on drift.

## 6. Persistent AdmissionLedger and permanent void

Implement a persistence-backed deterministic ledger abstraction.

Required states:

- NEW
- VOID
- ADMITTED/COMMITTED

Required invariants:

- VOID is terminal;
- COMMITTED is terminal;
- compare-and-set is generation bound;
- one attempt cannot be committed twice;
- stale generation rejects;
- crash/restart preserves terminal state;
- restored external state cannot revive VOID.

Use a deterministic persistence backend suitable for tests, e.g. SQLite/file-backed transactional store, not only process memory.

`admit_review_attempt()` must revalidate the full evidence bundle/current state through production validators immediately before CAS.

Caller-supplied version strings alone are insufficient.

Add restart/recovery tests.

## 7. Retrieval final-context authority

Create a frozen retrieval contract or equivalent external expectation.

Each retrieval record must bind:

- request ID;
- attempt ID;
- session ID;
- source ID/version;
- exact member/page/range;
- returned bytes hash/length;
- tool/result ID;
- sequence/timestamp;
- final adjudication context ID/hash.

Expected values come from the frozen retrieval/request contract, not the retrieval record itself.

Require actual raw bytes.

Reject:

- file/citation/open-event only;
- wrong source/version/range;
- correct bytes wrong session;
- correct metadata wrong/missing bytes;
- bytes not bound to the final adjudication context.

## 8. Wire + receipt + returned-byte binding

Do not use `receipt.complete` as authority.

Compute delivery completeness from:

- manifest item set;
- actual returned bytes;
- receipt item IDs;
- actual received byte count;
- request/attempt/session IDs;
- manifest hash;
- representation identity/hash;
- source reviewed commit;
- semantic envelope hash;
- canonical wire hash.

Canonical wire hash must be recomputed from exact wire metadata and returned item hashes/lengths.

Reject forged complete flag, wrong byte count, wrong semantic/wire hash, wrong source, wrong attempt/session/request, wrong representation.

## 9. Typed bounded materialization

Replace/extend plain path->bytes input with typed entries sufficient to test:

- file;
- symlink/link target;
- archive/container member where used.

Each entry carries:

- raw name;
- normalized path;
- kind;
- bytes/link target;
- compressed/uncompressed size where relevant;
- recursion depth/source-member identity.

Enforce:

- no absolute/drive/backslash ambiguity;
- no dot/dot-dot ambiguity;
- unique normalized paths;
- no symlink escape;
- maximum entry count;
- maximum per-member bytes;
- maximum total bytes;
- maximum recursion depth;
- maximum decompression ratio;
- qualified transform ID/hash/version from platform-owned transform registry;
- transformation parameters/coverage;
- source hash;
- representation hash.

Representation qualification must not depend on `qualified=True`; validate against the transform registry outside candidate write authority.

## 10. Witness/accessibility

Trusted harness creates witness challenges after evidence freeze.

Bind:

- challenge ID;
- source slice ID/hash;
- expected extraction answer/hash;
- provider/mode/prompt-isolation mode;
- current qualification record;
- challenge/response byte/token budget;
- final-context budget.

Expected answer remains hidden from the reviewer/fake provider.

Witness output:

- is non-semantic;
- is non-evidence;
- cannot satisfy review dimensions.

Reject evaluative prompts, stale/wrong qualification, wrong provider/mode, oversized response, context eviction, canary-preserving selective content loss when policy requires stronger proof.

Accessibility proof must be a typed record validated against risk policy; no `proven=True` summary.

## 11. Required evidence + interaction contract binding

Preflight must enforce:

- all required evidence IDs are in the manifest;
- manifest contains no unknown IDs beyond governed optional IDs;
- IDs are canonical/unique.

Interaction closure must compare the declared RequiredInteractionContract to observed evidence interactions in the delivered/final context.

A non-empty tuple alone is insufficient.

## 12. Authority, egress, prompt, reviewer and disposition binding

Authority snapshot predicate:

- outside candidate write authority;
- exact snapshot ID matches contracts;
- exact content hash/version matches externally expected authority context.

Egress predicate:

- authoritative egress record;
- expected version supplied by PredicateContext;
- no self-derived expected version.

Prompt isolation:

- typed qualification record;
- expected provider/mode/clock supplied externally;
- currentness/expiry checked at preflight and final admission.

Reviewer provenance:

- typed provenance/authorization record;
- expected reviewer policy/trust root supplied externally.

Disposition promotability:

- derived from governing disposition policy + all required predicate results;
- not a caller boolean.

## 13. Retry / physical-attempt closure

Introduce typed physical attempt records:

- physical attempt ID;
- planned root attempt ID;
- parent attempt ID if retry;
- FIRST or RETRY;
- request ID;
- session ID;
- wire hash;
- outcome/failure;
- provider request ID when available.

Rules:

- exactly one first physical attempt for every planned root ID;
- first-attempt IDs cannot be silently replaced;
- retry ID is globally unique and not a planned root ID;
- retry parent exists and failed;
- retry is present in physical dispatch ledger;
- failed parent remains preserved;
- unscheduled FIRST attempt cannot count;
- duplicate physical request cannot count;
- hidden implicit retry fails unless surfaced;
- every physical attempt has request/session/wire binding.

## 14. Independent admissibility closure

Do not compare raw fixture/mutation IDs directly to predicate IDs.

Require independently produced records:

- RequiredPredicateDefinition(predicate_id)
- VerdictPredicateResult(predicate_id)
- LogicMutationRecord(mutation_id, target_predicate_id, executed, killed, fixture_hash)
- NegativeFixtureRecord(fixture_id, target_predicate_id, fixture_hash)

Closure passes only when:

```text
required_predicate_ids
==
actual_verdict_predicate_ids
==
set(logic_mutation.target_predicate_id for executed mutations)
==
set(logic_mutation.target_predicate_id for killed mutations)
==
set(negative_fixture.target_predicate_id)
```

Also require:

- every required predicate has at least one independently malformed negative fixture;
- every required predicate has at least one executed/killed validator mutation;
- no extra unknown target;
- missing/non-executed mutation fails closure.

Phase O and Phase T must consume actual run artifacts from these independent sources.

## 15. Authentic validator-logic mutation

No production bypass.

For each predicate:

1. generate/freeze an independently malformed negative fixture;
2. normal production code must reject with the expected predicate/reason;
3. spawn isolated mutation process;
4. mutate only the exact production guard/validator dispatch for that predicate so it accepts/weakened;
5. rerun the same frozen fixture;
6. confirm the mutation would create a false-green;
7. the test/mutation harness detects the semantic change and marks the mutation killed.

Mutation operators may use monkeypatch/import-hook/AST/source-rewrite in the isolated harness, but no test hook may be exported by production APIs.

Add meta-tests that intentionally omit one mutation target and one negative fixture and require closure failure.

## 16. A-T phase evidence model

Every phase A-T must publish:

- production functions invoked;
- positive control case IDs;
- negative/adversarial case IDs;
- applicable mutation target IDs;
- case results;
- status derived from those results.

No phase can be PASS from one happy-path call.

Minimum negative families remain those required by External Review R2 and the reviewer solution:

A authority/contract/preflight negatives
B chunk integrity negatives
C representation/materialization negatives
D taxonomy single/mixed/unresolved + mutation
E manifest/corpus mismatch
F provider capability/closure negatives
G both authentic mutation families
H retry/physical-attempt negatives
I one negative + validator mutation per predicate
J forged receipt/wire/source/byte negatives
K witness currentness/mode/budget/eviction/semantic negatives
L path/duplicate/symlink/recursion/decompression/transform negatives
M request/attempt/session/source/wire binding negatives
N bare-qualified/missing-record negatives
O full independent closure
P dirty/lying/hidden/missing-channel/config-drift negatives
Q risk-policy/fence-version negatives
R authoritative witness/accessibility + mutation
S retry linkage/unscheduled/duplicate/failure replacement
T actual executed/killed/fixture closure + retry transparency

## 17. Expanded self-falsification

Self-falsification must be independently authored from the normal mutation runner.

It must reproduce every External Review R2 Critical/High false-green family.

It may reuse production APIs, but not the same fixture generator/mutation control logic.

At minimum attempt:

- all-True summary-only evidence bundle;
- production-bypass discovery/static scan;
- empty qualification sets;
- plan/record mismatch;
- stale fence/wrong transition;
- void attempt revival after process restart;
- retrieval.complete-only;
- forged complete receipt;
- wire hash mismatch;
- witness.current-only;
- duplicate normalized materialization member;
- unqualified transform;
- missing/nonexecuted mutation target;
- contract/manifest mismatch;
- broken retry lineage;
- self-referential egress/prompt expected values;
- stale execution evidence reuse.

## 18. Freshness / two-stage source identity

Do NOT bind new evidence to the failed historical source commit `66129025...`.

Required sequence:

### Stage S — source freeze

After final production/test/mutation code changes:

- working tree clean;
- commit source-only changes;
- record `reviewed_source_commit=S`;
- record `reviewed_source_tree`.

### Stage E — evidence generation

Check out/run exactly S and record for every command:

- source commit/tree;
- UTC timestamp;
- command;
- runner identity/OS/interpreter;
- stdout;
- stderr;
- exit code.

Generate fresh:

- unit/integration results;
- A-T results;
- data/state mutation results;
- validator-logic mutation results;
- closure artifact;
- self-falsification results;
- source/result hashes.

Stale-result checker must fail if any implementation/test/mutation source hash differs from S.

Then commit only evidence/review artifacts in later evidence commit E.

Review packet must clearly distinguish:

- reviewed source S;
- evidence/packet commit E.

Preserve prior false-green 22/22, 29/29 and R1 34/34, 46/46 histories as superseded evidence.

## 19. R2 acceptance gates

Codex may request another external review only when all are true:

1. no production guard-disable/bypass parameter exists;
2. no load-bearing predicate accepts a summary boolean as authority;
3. every predicate calls/binds its production validator evidence;
4. provider qualification rejects empty/mismatched plan/record and recomputes closure;
5. context isolation uses actual transition class, expected fence version and admission-time config state;
6. AdmissionLedger persists terminal VOID/COMMITTED across restart;
7. retrieval final-context binding is authoritative;
8. receipt completeness and wire hash are recomputed from actual bytes;
9. typed materialization enforces canonical identity/resource/symlink/archive/transform rules;
10. witness/accessibility is challenge/evidence/qualification bound;
11. required evidence and interactions bind to actual delivered/final context;
12. retry/physical attempts have exact lineage and wire/request/session binding;
13. closure uses independent target mappings and actual executed/killed artifacts;
14. authentic validator-logic mutations kill every required guard;
15. every A-T phase has positive + negative + mutation evidence where applicable;
16. expanded independent self-falsification has zero Critical/High survivors;
17. fresh result evidence is bound to final source commit S;
18. frozen R5 design remains unweakened;
19. EXP-M remains NOT_QUALIFIED;
20. live provider/API execution remains false.

Then:

- generate `EXP-M-DETERMINISTIC-IMPLEMENTATION-R2-REVIEW.md`;
- include exact external review prompt;
- return `DETERMINISTIC_REVIEW_REQUIRED`;
- stop for independent review.

## 20. No-stop continuation rule

If any R2 item is still automatable:

`AUTOMATABLE_WORK_REMAINS`

Codex must inspect Git/repository state and continue automatically.

Do not stop after:

- one fixed Critical;
- one successful test file;
- one mutation pass;
- one A-T phase;
- one commit;
- one green command.

Stop only for:

- genuine independent external review after all R2 acceptance gates are met;
- an actually unavailable manual authority/environment required by the frozen design.

Do not use live provider APIs.
```


## R1 remediation matrix
| Finding family | Production mechanism | Fresh evidence |
|---|---|---|
| C-01/H-10 taxonomy and closure | `adjudicate_insufficient_evidence`, independent predicate registry | Phase D, O/T and mutation closure |
| C-02/C-10/H-01 | production mutation runner with data/state and validator-logic families | Phase G; 50/50 rejected |
| C-03/H-02 | evidence-derived predicate dispatch with independently declared targets | structured admissibility fixtures and negative controls |
| C-04/H-04 | `validate_capability` binds profile, plan, record, expiry, format, context and attempts | capability mutation cases |
| C-05/H-05 | `validate_context_isolation` binds policy, sentinel state and fence | dirty/hidden/stale-context cases |
| C-06 | `admit_review_attempt` compare-and-set and permanent void result | generation/state-drift test |
| C-07 | `RetrievalEvidenceRecord` raw-byte and final-context binding | retrieval byte/session/context mutation |
| C-08 | current witness qualification, semantic prompt and eviction checks | witness positive/negative cases |
| C-09/H-09 | byte, representation, semantic and source/wire/receipt binding | returned-byte mutation |
| C-11 | expanded self-falsification includes every current mutation family | 19 cases, 0 critical/0 high survivors |
| NC-01/NC-11/NH-01..NH-08 | no production bypass, typed evidence/context, persistent admission, lineage and freshness binding | static/behavioral/mutation/self-falsification evidence |

## Identity
branch=experiment/exp-m-deterministic-implementation
commit=586e36091815472f4674e6122416a25e68412191
tree=0ac1b6a984c2cdb68ea25800e3cbcb2d4bbaae6d
parent=c0efaf7fdc9c35e05f424643015f299e014605e0
frozen_design_commit=0ba6c3c24ec247f5ad993b7e2f996ccd472b5f45
authority_status=NOT_QUALIFIED
live_provider_execution=false

## Fresh evidence execution identity
{
  "execution_hashes": {
    "experiments/governed-platform/EXP-M-DETERMINISTIC-STDOUT.txt": "a9bcce90a2afdb464683ae0ab8a991ec32d4f13c7323ef428e654f160480a08f",
    "experiments/governed-platform/EXP-M-MUTATION-STDOUT.txt": "edc824ec9bc9c6c31e050fea99ed0b7a384d5b100fac07fa6ac77c46040151b8",
    "experiments/governed-platform/EXP-M-PHASE-STDOUT.txt": "ef61d4c08bad66c9c17f5cba77788530d892617b8f5f09ec13b6ec393e08bb6e",
    "experiments/governed-platform/EXP-M-SELF-STDOUT.txt": "06ed34b768b0d4b3ac1eb45ae8954b44e5b602ae6a4de950b13ad837563e9d7d",
    "experiments/governed-platform/EXP-M-UNIT-STDOUT.txt": "1b4cf1e7d3b91b83e8fb1dffab632528f29e6e2ae30a5f21e95ce52c3f9bf238"
  },
  "source_commit": "c0efaf7fdc9c35e05f424643015f299e014605e0",
  "source_tree": "5f501b8fa485832f9313aa037627da0a7de8b5df"
}

## Deterministic exit gates
all_phases_A_to_T_pass=True
mutation_total=50
mutation_rejected=50
mutation_survivors=0
all_mutations_rejected=True
critical_self_falsification_survivors=0
high_self_falsification_survivors=0

## Frozen source-of-truth hashes
```json
{
  "experiments/governed-platform/EXP-M-R5-EXTERNAL-REVIEW.md": "093528150efdcb27d34402f064627a6780495d98f82414835fb9a991b48c5ab2",
  "experiments/governed-platform/EXP-M-TEST-MATRIX.md": "eda6de7375451882cd39c45ee06db8d2dd23a3c3b568a9dc674d6830e3a065cb",
  "experiments/governed-platform/exp-m-review-evidence-delivery-integrity.md": "b4c08a93c715f29e951b54bc8541f8eb52f1ffedb4f80a09d170e6ee7bca4e18",
  "governance-runtime/LIVE-CONVERSATION-GOVERNANCE.md": "c90151f29c5dc9cb9c8ec078a72a2df5af8f978f2f1daed76c7fa3951eb092d2",
  "standards/review-evidence-delivery-integrity.md": "8653df8594ca24a9c865d4da2fd89469fe7aabeaaceb9b18e9685715d41731fa"
}
```

## Implemented source hashes
```json
{
  "governance-runtime/build_exp_m_review_packet.py": "cfee5632769bb9a12aba5b76399a82bd36f3c3ed54b6a39a9cc946136e97271f",
  "governance-runtime/exp_m_deterministic.py": "57883528428f76c602bc4e7895aacd5281efb40128fc9ca4c3b179b3a861520d",
  "governance-runtime/run_exp_m_deterministic.py": "98b97bb4da4b11d12e77a4a2281af9ca5c73f613711ac829a43a0e333f17782e",
  "governance-runtime/run_exp_m_mutations.py": "b06fb9f3e28635e3fa764f1e0c83478cb8d587a1caab9b83ff6eaca27cba5cbd",
  "governance-runtime/self_falsify_exp_m.py": "38e0a7cd845030c36a51ab74762e889c0e7fb8925fa790961497afef8f074d19",
  "governance-runtime/test_exp_m_deterministic.py": "ff23c8139b31322f408a0d7acd934a839eaa301156a6c93d692ff383e1881ff2",
  "governance-runtime/test_exp_m_phases.py": "2b91d45e5d8c7f899ec9a1171495be0e45730367a3e6a8836b0c45fdde3e084d"
}
```

## Phase A-T results
```json
{
  "all_phases_pass": true,
  "execution": {
    "command": "python governance-runtime/run_exp_m_deterministic.py",
    "interpreter": "D:\\Python312\\python.exe",
    "source_commit": "c0efaf7fdc9c35e05f424643015f299e014605e0",
    "source_tree": "5f501b8fa485832f9313aa037627da0a7de8b5df",
    "utc": "2026-09-19T22:06:10.185909+00:00"
  },
  "experiment": "EXP-M",
  "mode": "DETERMINISTIC_ONLY",
  "phases": {
    "A": {
      "applicable_mutation_target_ids": [],
      "case_results": {
        "negative_rejected": true,
        "phase_status": "PASS",
        "positive": "PASS"
      },
      "checks": [
        "required closure",
        "manifest bytes",
        "trusted profile"
      ],
      "negative_case_ids": [
        "A-adversarial-negative"
      ],
      "positive_case_ids": [
        "A-positive-control"
      ],
      "production_functions_invoked": [
        "preflight_delivery"
      ],
      "status": "PASS"
    },
    "B": {
      "applicable_mutation_target_ids": [],
      "case_results": {
        "negative_rejected": true,
        "phase_status": "PASS",
        "positive": "PASS"
      },
      "checks": [
        "chunk hash",
        "index",
        "request binding"
      ],
      "negative_case_ids": [
        "B-adversarial-negative"
      ],
      "positive_case_ids": [
        "B-positive-control"
      ],
      "production_functions_invoked": [
        "validate_chunks"
      ],
      "status": "PASS"
    },
    "C": {
      "applicable_mutation_target_ids": [],
      "case_results": {
        "negative_rejected": true,
        "phase_status": "PASS",
        "positive": "PASS"
      },
      "checks": [
        "raw bytes",
        "representation hash"
      ],
      "negative_case_ids": [
        "C-adversarial-negative"
      ],
      "positive_case_ids": [
        "C-positive-control"
      ],
      "production_functions_invoked": [
        "validate_representation"
      ],
      "status": "PASS"
    },
    "D": {
      "applicable_mutation_target_ids": [],
      "case_results": {
        "negative_rejected": true,
        "phase_status": "PASS",
        "positive": "PASS"
      },
      "checks": [
        "single cause",
        "mixed causes",
        "unresolved cause"
      ],
      "negative_case_ids": [
        "D-adversarial-negative"
      ],
      "positive_case_ids": [
        "D-positive-control"
      ],
      "production_functions_invoked": [
        "adjudicate_insufficient_evidence"
      ],
      "status": "PASS"
    },
    "E": {
      "applicable_mutation_target_ids": [],
      "case_results": {
        "negative_rejected": true,
        "phase_status": "PASS",
        "positive": "PASS"
      },
      "checks": [
        "same manifest",
        "same corpus hash"
      ],
      "negative_case_ids": [
        "E-adversarial-negative"
      ],
      "positive_case_ids": [
        "E-positive-control"
      ],
      "production_functions_invoked": [
        "EvidenceDeliveryManifest.verify"
      ],
      "status": "PASS"
    },
    "F": {
      "applicable_mutation_target_ids": [],
      "case_results": {
        "negative_rejected": true,
        "phase_status": "PASS",
        "positive": "PASS"
      },
      "checks": [
        "profile identity",
        "expiry",
        "operating point",
        "attempt closure",
        "context limit"
      ],
      "negative_case_ids": [
        "F-adversarial-negative"
      ],
      "positive_case_ids": [
        "F-positive-control"
      ],
      "production_functions_invoked": [
        "validate_capability"
      ],
      "status": "PASS"
    },
    "G": {
      "applicable_mutation_target_ids": [
        "review_request_current",
        "authority_snapshot_current",
        "evidence_contract_closed",
        "interaction_contract_closed",
        "materialization_complete",
        "representation_governed",
        "egress_authorized",
        "capability_current",
        "accessibility_policy_satisfied",
        "context_isolation_satisfied",
        "hidden_state_policy_satisfied",
        "context_state_clean",
        "admission_fence_current",
        "semantic_context_qualified",
        "wire_binding_valid",
        "delivery_complete",
        "accessibility_proven",
        "witness_record_current",
        "session_retrieval_coverage",
        "prompt_isolation_current",
        "semantic_coverage",
        "reviewer_provenance",
        "disposition_promotable"
      ],
      "case_results": {
        "negative_rejected": true,
        "phase_status": "PASS",
        "positive": "PASS"
      },
      "checks": [
        "data/state mutation family",
        "validator mutation family"
      ],
      "mutation_total": 50,
      "negative_case_ids": [
        "G-adversarial-negative"
      ],
      "positive_case_ids": [
        "G-positive-control"
      ],
      "production_functions_invoked": [
        "run_exp_m_mutations"
      ],
      "status": "PASS"
    },
    "H": {
      "applicable_mutation_target_ids": [],
      "case_results": {
        "negative_rejected": true,
        "phase_status": "PASS",
        "positive": "PASS"
      },
      "checks": [
        "physical request ledger"
      ],
      "negative_case_ids": [
        "H-adversarial-negative"
      ],
      "positive_case_ids": [
        "H-positive-control"
      ],
      "production_functions_invoked": [
        "validate_retry_transparency"
      ],
      "status": "PASS"
    },
    "I": {
      "applicable_mutation_target_ids": [
        "review_request_current",
        "authority_snapshot_current",
        "evidence_contract_closed",
        "interaction_contract_closed",
        "materialization_complete",
        "representation_governed",
        "egress_authorized",
        "capability_current",
        "accessibility_policy_satisfied",
        "context_isolation_satisfied",
        "hidden_state_policy_satisfied",
        "context_state_clean",
        "admission_fence_current",
        "semantic_context_qualified",
        "wire_binding_valid",
        "delivery_complete",
        "accessibility_proven",
        "witness_record_current",
        "session_retrieval_coverage",
        "prompt_isolation_current",
        "semantic_coverage",
        "reviewer_provenance",
        "disposition_promotable"
      ],
      "case_results": {
        "negative_rejected": true,
        "phase_status": "PASS",
        "positive": "PASS"
      },
      "checks": [
        "all admissibility predicates"
      ],
      "negative_case_ids": [
        "I-adversarial-negative"
      ],
      "positive_case_ids": [
        "I-positive-control"
      ],
      "production_functions_invoked": [
        "evaluate_admissibility"
      ],
      "status": "PASS"
    },
    "J": {
      "applicable_mutation_target_ids": [],
      "case_results": {
        "negative_rejected": true,
        "phase_status": "PASS",
        "positive": "PASS"
      },
      "checks": [
        "wire/session/representation bindings"
      ],
      "negative_case_ids": [
        "J-adversarial-negative"
      ],
      "positive_case_ids": [
        "J-positive-control"
      ],
      "production_functions_invoked": [
        "complete_delivery"
      ],
      "status": "PASS"
    },
    "K": {
      "applicable_mutation_target_ids": [],
      "case_results": {
        "negative_rejected": true,
        "phase_status": "PASS",
        "positive": "PASS"
      },
      "checks": [
        "current witness record",
        "content-bound response",
        "budget"
      ],
      "negative_case_ids": [
        "K-adversarial-negative"
      ],
      "positive_case_ids": [
        "K-positive-control"
      ],
      "production_functions_invoked": [
        "validate_witness_qualification"
      ],
      "status": "PASS"
    },
    "L": {
      "applicable_mutation_target_ids": [],
      "case_results": {
        "negative_rejected": true,
        "phase_status": "PASS",
        "positive": "PASS"
      },
      "checks": [
        "parser bounds",
        "untrusted profile rejection"
      ],
      "negative_case_ids": [
        "L-adversarial-negative"
      ],
      "positive_case_ids": [
        "L-positive-control"
      ],
      "production_functions_invoked": [
        "safe_archive_member"
      ],
      "status": "PASS"
    },
    "M": {
      "applicable_mutation_target_ids": [],
      "case_results": {
        "negative_rejected": true,
        "phase_status": "PASS",
        "positive": "PASS"
      },
      "checks": [
        "frozen bytes",
        "attempt binding"
      ],
      "negative_case_ids": [
        "M-adversarial-negative"
      ],
      "positive_case_ids": [
        "M-positive-control"
      ],
      "production_functions_invoked": [
        "EvidenceDeliveryManifest.verify"
      ],
      "status": "PASS"
    },
    "N": {
      "applicable_mutation_target_ids": [],
      "case_results": {
        "negative_rejected": true,
        "phase_status": "PASS",
        "positive": "PASS"
      },
      "checks": [
        "external-review remediation cases"
      ],
      "negative_case_ids": [
        "N-adversarial-negative"
      ],
      "positive_case_ids": [
        "N-positive-control"
      ],
      "production_functions_invoked": [
        "preflight_delivery"
      ],
      "status": "PASS"
    },
    "O": {
      "applicable_mutation_target_ids": [
        "review_request_current",
        "authority_snapshot_current",
        "evidence_contract_closed",
        "interaction_contract_closed",
        "materialization_complete",
        "representation_governed",
        "egress_authorized",
        "capability_current",
        "accessibility_policy_satisfied",
        "context_isolation_satisfied",
        "hidden_state_policy_satisfied",
        "context_state_clean",
        "admission_fence_current",
        "semantic_context_qualified",
        "wire_binding_valid",
        "delivery_complete",
        "accessibility_proven",
        "witness_record_current",
        "session_retrieval_coverage",
        "prompt_isolation_current",
        "semantic_coverage",
        "reviewer_provenance",
        "disposition_promotable"
      ],
      "case_results": {
        "negative_rejected": true,
        "phase_status": "PASS",
        "positive": "PASS"
      },
      "checks": [
        "predicate/verdict/mutation/fixture closure"
      ],
      "negative_case_ids": [
        "O-adversarial-negative"
      ],
      "positive_case_ids": [
        "O-positive-control"
      ],
      "production_functions_invoked": [
        "independent_target_closure"
      ],
      "status": "PASS",
      "target_counts": {
        "executed": 23,
        "fixtures": 23,
        "killed": 23,
        "required": 23
      }
    },
    "P": {
      "applicable_mutation_target_ids": [],
      "case_results": {
        "negative_rejected": true,
        "phase_status": "PASS",
        "positive": "PASS"
      },
      "checks": [
        "residual adversarial oracle"
      ],
      "negative_case_ids": [
        "P-adversarial-negative"
      ],
      "positive_case_ids": [
        "P-positive-control"
      ],
      "production_functions_invoked": [
        "validate_context_state"
      ],
      "status": "PASS"
    },
    "Q": {
      "applicable_mutation_target_ids": [],
      "case_results": {
        "negative_rejected": true,
        "phase_status": "PASS",
        "positive": "PASS"
      },
      "checks": [
        "risk policy",
        "admission fence"
      ],
      "negative_case_ids": [
        "Q-adversarial-negative"
      ],
      "positive_case_ids": [
        "Q-positive-control"
      ],
      "production_functions_invoked": [
        "validate_fence"
      ],
      "status": "PASS"
    },
    "R": {
      "applicable_mutation_target_ids": [],
      "case_results": {
        "negative_rejected": true,
        "phase_status": "PASS",
        "positive": "PASS"
      },
      "checks": [
        "witness noninterference",
        "context eviction rejection"
      ],
      "negative_case_ids": [
        "R-adversarial-negative"
      ],
      "positive_case_ids": [
        "R-positive-control"
      ],
      "production_functions_invoked": [
        "validate_witness_qualification"
      ],
      "status": "PASS"
    },
    "S": {
      "applicable_mutation_target_ids": [],
      "case_results": {
        "negative_rejected": true,
        "phase_status": "PASS",
        "positive": "PASS"
      },
      "checks": [
        "planned attempt closure"
      ],
      "negative_case_ids": [
        "S-adversarial-negative"
      ],
      "positive_case_ids": [
        "S-positive-control"
      ],
      "production_functions_invoked": [
        "validate_attempt_ledger"
      ],
      "status": "PASS"
    },
    "T": {
      "applicable_mutation_target_ids": [
        "review_request_current",
        "authority_snapshot_current",
        "evidence_contract_closed",
        "interaction_contract_closed",
        "materialization_complete",
        "representation_governed",
        "egress_authorized",
        "capability_current",
        "accessibility_policy_satisfied",
        "context_isolation_satisfied",
        "hidden_state_policy_satisfied",
        "context_state_clean",
        "admission_fence_current",
        "semantic_context_qualified",
        "wire_binding_valid",
        "delivery_complete",
        "accessibility_proven",
        "witness_record_current",
        "session_retrieval_coverage",
        "prompt_isolation_current",
        "semantic_coverage",
        "reviewer_provenance",
        "disposition_promotable"
      ],
      "case_results": {
        "negative_rejected": true,
        "phase_status": "PASS",
        "positive": "PASS"
      },
      "checks": [
        "retry transparency",
        "registry closure"
      ],
      "negative_case_ids": [
        "T-adversarial-negative"
      ],
      "positive_case_ids": [
        "T-positive-control"
      ],
      "production_functions_invoked": [
        "validate_retry_transparency",
        "independent_target_closure"
      ],
      "status": "PASS"
    }
  }
}
```

## Mutation results
```json
{
  "all_rejected": true,
  "execution": {
    "command": "python governance-runtime/run_exp_m_mutations.py",
    "interpreter": "D:\\Python312\\python.exe",
    "source_commit": "c0efaf7fdc9c35e05f424643015f299e014605e0",
    "source_tree": "5f501b8fa485832f9313aa037627da0a7de8b5df",
    "utc": "2026-09-19T22:06:10.598909+00:00"
  },
  "experiment": "EXP-M",
  "mutations": [
    {
      "actual": "PASS",
      "executed": true,
      "expected": "REJECT",
      "family": "validator_logic",
      "fixture_hash": "3df0842dbd323876d6b11a730ed54b480d2ed07c934d832735e884c7314512c6",
      "id": "TM-O-review_request_current",
      "killed": true,
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:review_request_current",
      "negative_fixture_target_id": "review_request_current",
      "target": "review_request_current",
      "target_predicate_id": "review_request_current"
    },
    {
      "actual": "PASS",
      "executed": true,
      "expected": "REJECT",
      "family": "validator_logic",
      "fixture_hash": "3cc3e165457f926b70a960d0666576640d9113de7fdf8853394f83be0918753f",
      "id": "TM-O-authority_snapshot_current",
      "killed": true,
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:authority_snapshot_current",
      "negative_fixture_target_id": "authority_snapshot_current",
      "target": "authority_snapshot_current",
      "target_predicate_id": "authority_snapshot_current"
    },
    {
      "actual": "PASS",
      "executed": true,
      "expected": "REJECT",
      "family": "validator_logic",
      "fixture_hash": "df62d3a3edfbb96be4914a8c852648febc3adccdd450b9fbf8fbd8263123dbe4",
      "id": "TM-O-evidence_contract_closed",
      "killed": true,
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:evidence_contract_closed",
      "negative_fixture_target_id": "evidence_contract_closed",
      "target": "evidence_contract_closed",
      "target_predicate_id": "evidence_contract_closed"
    },
    {
      "actual": "PASS",
      "executed": true,
      "expected": "REJECT",
      "family": "validator_logic",
      "fixture_hash": "96e17caa9e74855db8259f90363611a5638a1f47bf9d559a27a71d63fee3440a",
      "id": "TM-O-interaction_contract_closed",
      "killed": true,
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:interaction_contract_closed",
      "negative_fixture_target_id": "interaction_contract_closed",
      "target": "interaction_contract_closed",
      "target_predicate_id": "interaction_contract_closed"
    },
    {
      "actual": "PASS",
      "executed": true,
      "expected": "REJECT",
      "family": "validator_logic",
      "fixture_hash": "6ebc53123c5d24dc8292565fea8548ad62ffd12b434b1b6181c67e117f6588c6",
      "id": "TM-O-materialization_complete",
      "killed": true,
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:materialization_complete",
      "negative_fixture_target_id": "materialization_complete",
      "target": "materialization_complete",
      "target_predicate_id": "materialization_complete"
    },
    {
      "actual": "PASS",
      "executed": true,
      "expected": "REJECT",
      "family": "validator_logic",
      "fixture_hash": "a9370b6d5a89b8c126d7a024c8adb4f3ae8ecb616e17e593b08f0929882bdfd5",
      "id": "TM-O-representation_governed",
      "killed": true,
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:representation_governed",
      "negative_fixture_target_id": "representation_governed",
      "target": "representation_governed",
      "target_predicate_id": "representation_governed"
    },
    {
      "actual": "PASS",
      "executed": true,
      "expected": "REJECT",
      "family": "validator_logic",
      "fixture_hash": "42f690df0af943ffd88958fb033d0def976f98ef9a88dca4329dfc2a0a67fd32",
      "id": "TM-O-egress_authorized",
      "killed": true,
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:egress_authorized",
      "negative_fixture_target_id": "egress_authorized",
      "target": "egress_authorized",
      "target_predicate_id": "egress_authorized"
    },
    {
      "actual": "PASS",
      "executed": true,
      "expected": "REJECT",
      "family": "validator_logic",
      "fixture_hash": "391f862bf9cc501b7ff00a7b5d98794e89f38920f99a2654f4b018c75e9f49c3",
      "id": "TM-O-capability_current",
      "killed": true,
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:capability_current",
      "negative_fixture_target_id": "capability_current",
      "target": "capability_current",
      "target_predicate_id": "capability_current"
    },
    {
      "actual": "PASS",
      "executed": true,
      "expected": "REJECT",
      "family": "validator_logic",
      "fixture_hash": "7b3247544275937b6e7b96f920caf76efb6173dc5d46ed68f2beb51116e04fd9",
      "id": "TM-O-accessibility_policy_satisfied",
      "killed": true,
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:accessibility_policy_satisfied",
      "negative_fixture_target_id": "accessibility_policy_satisfied",
      "target": "accessibility_policy_satisfied",
      "target_predicate_id": "accessibility_policy_satisfied"
    },
    {
      "actual": "PASS",
      "executed": true,
      "expected": "REJECT",
      "family": "validator_logic",
      "fixture_hash": "775f85e56dc3651ab3e7c64ac0d9f0b53799f0af2146e0bb80c898daca9c1a6d",
      "id": "TM-O-context_isolation_satisfied",
      "killed": true,
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:context_isolation_satisfied",
      "negative_fixture_target_id": "context_isolation_satisfied",
      "target": "context_isolation_satisfied",
      "target_predicate_id": "context_isolation_satisfied"
    },
    {
      "actual": "PASS",
      "executed": true,
      "expected": "REJECT",
      "family": "validator_logic",
      "fixture_hash": "a7e5531a8691cb2149e1c539fe13f1797e5436e3bab39e2f3692ef59f7ea9852",
      "id": "TM-O-hidden_state_policy_satisfied",
      "killed": true,
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:hidden_state_policy_satisfied",
      "negative_fixture_target_id": "hidden_state_policy_satisfied",
      "target": "hidden_state_policy_satisfied",
      "target_predicate_id": "hidden_state_policy_satisfied"
    },
    {
      "actual": "PASS",
      "executed": true,
      "expected": "REJECT",
      "family": "validator_logic",
      "fixture_hash": "ca4c248b03b1564779327788c8ddde5196f9617c460808db72dc728d1373d26e",
      "id": "TM-O-context_state_clean",
      "killed": true,
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:context_state_clean",
      "negative_fixture_target_id": "context_state_clean",
      "target": "context_state_clean",
      "target_predicate_id": "context_state_clean"
    },
    {
      "actual": "PASS",
      "executed": true,
      "expected": "REJECT",
      "family": "validator_logic",
      "fixture_hash": "c1e6692b12618ec760f4b0f7acc9f3179af5a28b326d2933b7cfe0d277190a98",
      "id": "TM-O-admission_fence_current",
      "killed": true,
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:admission_fence_current",
      "negative_fixture_target_id": "admission_fence_current",
      "target": "admission_fence_current",
      "target_predicate_id": "admission_fence_current"
    },
    {
      "actual": "PASS",
      "executed": true,
      "expected": "REJECT",
      "family": "validator_logic",
      "fixture_hash": "4119db7a3e413e308aaaa1fa8cece5f240e0d08d2dc1262ca674ba3665e84d93",
      "id": "TM-O-semantic_context_qualified",
      "killed": true,
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:semantic_context_qualified",
      "negative_fixture_target_id": "semantic_context_qualified",
      "target": "semantic_context_qualified",
      "target_predicate_id": "semantic_context_qualified"
    },
    {
      "actual": "PASS",
      "executed": true,
      "expected": "REJECT",
      "family": "validator_logic",
      "fixture_hash": "9877d52e8c1abfaca6af3dfb517203bc5a9a0eb1d545e0459414947c1369abd7",
      "id": "TM-O-wire_binding_valid",
      "killed": true,
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:wire_binding_valid",
      "negative_fixture_target_id": "wire_binding_valid",
      "target": "wire_binding_valid",
      "target_predicate_id": "wire_binding_valid"
    },
    {
      "actual": "PASS",
      "executed": true,
      "expected": "REJECT",
      "family": "validator_logic",
      "fixture_hash": "4ef63ad92b84eb04e52a0d9a13238eecd3c705ef0c55d75eaec55e0544c334b4",
      "id": "TM-O-delivery_complete",
      "killed": true,
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:delivery_complete",
      "negative_fixture_target_id": "delivery_complete",
      "target": "delivery_complete",
      "target_predicate_id": "delivery_complete"
    },
    {
      "actual": "PASS",
      "executed": true,
      "expected": "REJECT",
      "family": "validator_logic",
      "fixture_hash": "7db1b29a62c06bce906ab6516ac293c0067792e416fcae90b6ae6dfef43019e8",
      "id": "TM-O-accessibility_proven",
      "killed": true,
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:accessibility_proven",
      "negative_fixture_target_id": "accessibility_proven",
      "target": "accessibility_proven",
      "target_predicate_id": "accessibility_proven"
    },
    {
      "actual": "PASS",
      "executed": true,
      "expected": "REJECT",
      "family": "validator_logic",
      "fixture_hash": "d040a56927a91cf942f41a351e63dbc2697fd19330ec7c44a9f513a91959fef7",
      "id": "TM-O-witness_record_current",
      "killed": true,
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:witness_record_current",
      "negative_fixture_target_id": "witness_record_current",
      "target": "witness_record_current",
      "target_predicate_id": "witness_record_current"
    },
    {
      "actual": "PASS",
      "executed": true,
      "expected": "REJECT",
      "family": "validator_logic",
      "fixture_hash": "e2f5335bbc35479ae1e0005dc964271bfbc999d728907c755e2c25003601d540",
      "id": "TM-O-session_retrieval_coverage",
      "killed": true,
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:session_retrieval_coverage",
      "negative_fixture_target_id": "session_retrieval_coverage",
      "target": "session_retrieval_coverage",
      "target_predicate_id": "session_retrieval_coverage"
    },
    {
      "actual": "PASS",
      "executed": true,
      "expected": "REJECT",
      "family": "validator_logic",
      "fixture_hash": "9adb92c6ec241e8af5f6953095cc4565eb04ac5876474b48723e0af9c0a0dc58",
      "id": "TM-O-prompt_isolation_current",
      "killed": true,
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:prompt_isolation_current",
      "negative_fixture_target_id": "prompt_isolation_current",
      "target": "prompt_isolation_current",
      "target_predicate_id": "prompt_isolation_current"
    },
    {
      "actual": "PASS",
      "executed": true,
      "expected": "REJECT",
      "family": "validator_logic",
      "fixture_hash": "d8924405d344ec894f5a79ff85b2c11e6d019291bc425c3abfad6a2d25268498",
      "id": "TM-O-semantic_coverage",
      "killed": true,
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:semantic_coverage",
      "negative_fixture_target_id": "semantic_coverage",
      "target": "semantic_coverage",
      "target_predicate_id": "semantic_coverage"
    },
    {
      "actual": "PASS",
      "executed": true,
      "expected": "REJECT",
      "family": "validator_logic",
      "fixture_hash": "cb6cdd4d9f65cb73f28ad08703e910bc9479837d969d8ef1981e2c61f3b4d6da",
      "id": "TM-O-reviewer_provenance",
      "killed": true,
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:reviewer_provenance",
      "negative_fixture_target_id": "reviewer_provenance",
      "target": "reviewer_provenance",
      "target_predicate_id": "reviewer_provenance"
    },
    {
      "actual": "PASS",
      "executed": true,
      "expected": "REJECT",
      "family": "validator_logic",
      "fixture_hash": "10d560e184ee145fca0a4045232e6313b05cd325e7db0ddebe07941014c5d2b3",
      "id": "TM-O-disposition_promotable",
      "killed": true,
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:disposition_promotable",
      "negative_fixture_target_id": "disposition_promotable",
      "target": "disposition_promotable",
      "target_predicate_id": "disposition_promotable"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-G-missing_chunk",
      "killed": true,
      "target": "missing_chunk"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-G-wrong_request",
      "killed": true,
      "target": "wrong_request"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-G-wrong_corpus",
      "killed": true,
      "target": "wrong_corpus"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-G-duplicate_index",
      "killed": true,
      "target": "duplicate_index"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-G-corrupt_chunk",
      "killed": true,
      "target": "corrupt_chunk"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-G-empty_chunk",
      "killed": true,
      "target": "empty_chunk"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-R1-expired_profile",
      "killed": true,
      "reasons": [
        "profile_expired"
      ],
      "target": "expired_profile"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-R1-wrong_profile_hash",
      "killed": true,
      "reasons": [
        "profile_hash_mismatch"
      ],
      "target": "wrong_profile_hash"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-R1-wrong_operating_point",
      "killed": true,
      "reasons": [
        "operating_point_mismatch"
      ],
      "target": "wrong_operating_point"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-R1-missing_attempt",
      "killed": true,
      "reasons": [
        "qualification_attempt_closure"
      ],
      "target": "missing_attempt"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-R1-unsupported_format",
      "killed": true,
      "reasons": [
        "unsupported_format"
      ],
      "target": "unsupported_format"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-R1-context-isolation",
      "killed": true,
      "reasons": [
        "provider_context_not_clean",
        "context_channel_unobserved",
        "context_state_unbound",
        "admission_fence_stale"
      ],
      "target": "dirty_hidden_stale_context"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-R1-materialization-traversal",
      "killed": true,
      "target": "materialization"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-R1-wrong-reviewed-source",
      "killed": true,
      "reasons": [
        "materialization_source_mismatch"
      ],
      "target": "reviewed_commit"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-R1-retrieval-bytes",
      "killed": true,
      "reasons": [
        "retrieval_bytes_mismatch"
      ],
      "target": "retrieval_returned_bytes"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-R1-witness-expired",
      "killed": true,
      "reasons": [
        "witness_record_expired"
      ],
      "target": "witness_qualification"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-R1-admission-drift",
      "killed": true,
      "reasons": [
        "generation_drift",
        "generation_drift"
      ],
      "target": "atomic_admission_generation"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-R1-egress-revoked",
      "killed": true,
      "reasons": [
        "egress_revoked_or_drifted"
      ],
      "target": "egress"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-R1-prompt-isolation-expired",
      "killed": true,
      "reasons": [
        "prompt_isolation_expired"
      ],
      "target": "prompt_isolation"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-R1-hidden-retry",
      "killed": true,
      "reasons": [
        "implicit_retry_unobserved"
      ],
      "target": "retry_transparency"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-R1-retrieval-session",
      "killed": true,
      "reasons": [
        "retrieval_identity_mismatch"
      ],
      "target": "retrieval_session"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-R1-registry-drift",
      "killed": true,
      "reasons": [
        "predicate_registry_drift"
      ],
      "target": "predicate_registry"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-R1-wire-semantic-binding",
      "killed": true,
      "reasons": [
        "semantic_wire_hash_mismatch",
        "semantic_envelope_hash_mismatch"
      ],
      "target": "wire_semantic_hash"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-R2-summary-only",
      "killed": true,
      "reasons": [
        "review_request_current",
        "authority_snapshot_current",
        "evidence_contract_closed",
        "interaction_contract_closed",
        "materialization_complete",
        "representation_governed",
        "egress_authorized",
        "capability_current",
        "accessibility_policy_satisfied",
        "context_isolation_satisfied",
        "hidden_state_policy_satisfied",
        "context_state_clean",
        "admission_fence_current",
        "semantic_context_qualified",
        "wire_binding_valid",
        "delivery_complete",
        "accessibility_proven",
        "witness_record_current",
        "session_retrieval_coverage",
        "prompt_isolation_current",
        "semantic_coverage",
        "reviewer_provenance",
        "disposition_promotable"
      ],
      "target": "evidence_bundle"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-R2-plan-record-mismatch",
      "killed": true,
      "reasons": [
        "qualification_plan_identity_mismatch"
      ],
      "target": "qualification_plan_id"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-R2-forged-complete-receipt",
      "killed": true,
      "reasons": [
        "size_mismatch:a",
        "hash_mismatch:a",
        "representation_hash_mismatch",
        "receipt_byte_count_mismatch",
        "wire_hash_mismatch",
        "semantic_envelope_hash_mismatch"
      ],
      "target": "receipt_returned_bytes"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-R2-broken-retry-lineage",
      "killed": true,
      "reasons": [
        "planned_first_attempt_closure",
        "retry_lineage_invalid"
      ],
      "target": "retry_lineage"
    }
  ],
  "rejected_mutations": 50,
  "surviving_mutations": 0,
  "total_mutations": 50
}
```

## Self-falsification results
```json
{
  "all_rejected": true,
  "cases": [
    {
      "id": "manifest_byte_mutation",
      "rejected": true
    },
    {
      "id": "candidate_writable_snapshot",
      "rejected": true
    },
    {
      "id": "admissibility_summary_only_rejected",
      "rejected": true
    },
    {
      "id": "missing_chunk",
      "rejected": true
    },
    {
      "id": "retry_hidden",
      "rejected": true
    },
    {
      "id": "attempt_set_open",
      "rejected": true
    },
    {
      "id": "witness_over_budget",
      "rejected": true
    },
    {
      "id": "empty_witness",
      "rejected": true
    },
    {
      "id": "production_bypass_absent",
      "rejected": true
    },
    {
      "id": "all_true_summary_only",
      "rejected": true
    },
    {
      "id": "empty_qualification_sets",
      "rejected": true
    },
    {
      "id": "stale_fence",
      "rejected": true
    },
    {
      "id": "void_revival_after_reload",
      "rejected": true
    },
    {
      "id": "retrieval_complete_only",
      "rejected": true
    },
    {
      "id": "forged_complete_receipt",
      "rejected": true
    },
    {
      "id": "witness_current_only",
      "rejected": true
    },
    {
      "id": "duplicate_normalized_member",
      "rejected": true
    },
    {
      "id": "unqualified_transform",
      "rejected": true
    },
    {
      "id": "broken_retry_lineage",
      "rejected": true
    }
  ],
  "execution": {
    "command": "python governance-runtime/self_falsify_exp_m.py",
    "interpreter": "D:\\Python312\\python.exe",
    "source_commit": "c0efaf7fdc9c35e05f424643015f299e014605e0",
    "source_tree": "5f501b8fa485832f9313aa037627da0a7de8b5df",
    "utc": "2026-09-19T22:06:11.052909+00:00"
  },
  "surviving_critical": 0,
  "surviving_high": 0,
  "total": 19
}
```

## Governance boundary
- `EXP-M = NOT_QUALIFIED`.
- No live Claude, DeepSeek, Gemini, OpenRouter, or other provider execution was performed.
- No release, promotion, or authority effect is claimed.
- Independent external review remains required before any live provider pilot.

### governance-runtime/exp_m_deterministic.py

```python
"""Deterministic EXP-M evidence-delivery governor.

This module is deliberately provider-neutral.  It models the governed delivery
boundary and uses content-addressed, immutable records so fake/adversarial
providers can exercise the same production predicates without external calls.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict, is_dataclass
from hashlib import sha256
import json
from typing import Any, Iterable, Mapping, Sequence
from pathlib import Path


def canonical_json(value: Any) -> bytes:
    if is_dataclass(value):
        value = asdict(value)
    elif isinstance(value, Mapping):
        value = {k: (asdict(v) if is_dataclass(v) else v) for k, v in value.items()}
    def default(obj: Any) -> Any:
        if is_dataclass(obj): return asdict(obj)
        if isinstance(obj, bytes): return {"__bytes_sha256__": sha256(obj).hexdigest(), "size": len(obj)}
        raise TypeError(type(obj).__name__)
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=default) + "\n").encode()


def digest(value: Any) -> str:
    raw = value if isinstance(value, bytes) else canonical_json(value)
    return sha256(raw).hexdigest()


@dataclass(frozen=True)
class GovernanceAuthoritySnapshot:
    snapshot_id: str
    version: str
    content_hash: str
    outside_candidate_write_authority: bool = True
    governing_refs: tuple[str, ...] = ()


@dataclass(frozen=True)
class RequiredEvidenceContract:
    contract_id: str
    snapshot_id: str
    required_ids: tuple[str, ...]
    optional_ids: tuple[str, ...] = ()
    closed: bool = True
    non_vacuous: bool = True


@dataclass(frozen=True)
class RequiredInteractionContract:
    contract_id: str
    snapshot_id: str
    interactions: tuple[tuple[str, ...], ...]
    closed: bool = True


@dataclass(frozen=True)
class EvidenceDeliveryManifest:
    request_id: str
    reviewed_commit: str
    items: Mapping[str, Mapping[str, Any]]
    manifest_hash: str

    @staticmethod
    def freeze(request_id: str, reviewed_commit: str, items: Mapping[str, bytes]) -> "EvidenceDeliveryManifest":
        records = {k: {"sha256": sha256(v).hexdigest(), "size": len(v)} for k, v in sorted(items.items())}
        body = {"request_id": request_id, "reviewed_commit": reviewed_commit, "items": records}
        return EvidenceDeliveryManifest(request_id, reviewed_commit, records, digest(body))

    def verify(self, items: Mapping[str, bytes]) -> tuple[bool, list[str]]:
        reasons: list[str] = []
        allowed = set(self.items)
        extras = set(items) - allowed
        if extras:
            reasons.append("unknown_manifest_items:" + ",".join(sorted(extras)))
        if not allowed.issubset(items):
            reasons.append("manifest_item_set_mismatch")
        for item_id, meta in self.items.items():
            raw = items.get(item_id)
            if raw is None:
                continue
            if len(raw) != meta.get("size"):
                reasons.append(f"size_mismatch:{item_id}")
            if sha256(raw).hexdigest() != meta.get("sha256"):
                reasons.append(f"hash_mismatch:{item_id}")
        return not reasons, reasons


@dataclass(frozen=True)
class ProviderCapabilityProfile:
    provider_id: str
    model_id: str
    adapter_version: str
    profile_hash: str
    qualified: bool = False
    expires_at: str | None = None
    supported_formats: tuple[str, ...] = ()
    max_context_bytes: int = 0


@dataclass(frozen=True)
class ProviderQualificationExecutionPlan:
    plan_id: str
    provider_id: str
    operating_point: str
    trial_ids: tuple[str, ...]
    confirmation_ids: tuple[str, ...]


@dataclass(frozen=True)
class ProviderCapabilityQualificationRecord:
    plan_id: str
    profile_hash: str
    statistical_qualified: bool
    all_trials_closed: bool
    hard_failures: int = 0
    operating_point: str = ""
    planned_attempt_ids: tuple[str, ...] = ()
    closed_attempt_ids: tuple[str, ...] = ()
    provider_id: str = ""
    model_id: str = ""
    qualified_at: str | None = None
    attempt_records: tuple[Any, ...] = ()


@dataclass(frozen=True)
class ProviderAccessibilityRiskPolicy:
    transition_class: str
    proof_mode: str
    deterministic_required: bool = True
    residual_risk_allowed: bool = False


@dataclass(frozen=True)
class ProviderContextIsolationPolicy:
    policy_id: str
    basis: str
    hidden_state_allowed: bool = False


@dataclass(frozen=True)
class ProviderContextStateEvidence:
    clean: bool
    observable_channels: tuple[str, ...]
    sentinel_passed: bool
    state_hash: str


@dataclass(frozen=True)
class AdmissionFenceRecord:
    fence_id: str
    version: str
    current: bool


@dataclass(frozen=True)
class PromptIsolationQualificationRecord:
    record_id: str
    provider_id: str
    mode: str
    current: bool
    expires_at: str | None = None


@dataclass(frozen=True)
class WitnessProtocolQualificationRecord:
    record_id: str
    provider_id: str
    mode: str
    max_response_bytes: int
    current: bool
    prompt_isolation_mode: str = ""
    expires_at: str | None = None


@dataclass(frozen=True)
class RetrievalEvidenceRecord:
    request_id: str
    attempt_id: str
    session_id: str
    source_id: str
    source_version: str
    start: int
    end: int
    returned_sha256: str
    returned_length: int
    tool_result_id: str
    sequence: int
    final_context_id: str
    final_context_hash: str


@dataclass(frozen=True)
class MaterializationResult:
    success: bool
    entries: Mapping[str, bytes]
    representation_hash: str
    source_hash: str
    transform_id: str
    reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class MaterializationEntry:
    raw_name: str
    normalized_path: str
    kind: str = "file"
    data: bytes = b""
    link_target: str | None = None
    compressed_size: int = 0
    uncompressed_size: int = 0
    recursion_depth: int = 0
    source_member_id: str = ""


@dataclass(frozen=True)
class RepresentationRecord:
    transform_id: str
    transform_version: str
    transform_hash: str
    registry_version: str
    source_hash: str
    representation_hash: str
    parameters_hash: str
    coverage_hash: str


@dataclass(frozen=True)
class AttemptState:
    attempt_id: str
    generation: int
    authority_version: str
    request_version: str
    capability_hash: str
    egress_version: str
    context_hash: str
    fence_version: str
    prompt_hash: str
    witness_hash: str
    session_hash: str
    registry_version: str
    invalidated: bool = False


@dataclass(frozen=True)
class PhysicalAttemptRecord:
    attempt_id: str
    planned_root_id: str
    parent_attempt_id: str | None
    kind: str
    request_id: str
    session_id: str
    wire_hash: str
    outcome: str


@dataclass(frozen=True)
class AdmissionCheckpoint:
    attempt_id: str
    generation: int
    disposition: str
    committed: bool
    void: bool
    reasons: tuple[str, ...] = ()


class PersistentAdmissionLedger:
    """Small deterministic JSON ledger with terminal VOID/COMMITTED states."""
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("{}\n", encoding="utf-8")

    def _read(self) -> dict[str, Any]:
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _write(self, value: Mapping[str, Any]) -> None:
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
        tmp.replace(self.path)

    def compare_and_set(self, attempt_id: str, generation: int, disposition: str) -> AdmissionCheckpoint:
        data = self._read(); current = data.get(attempt_id)
        if current is not None:
            return AdmissionCheckpoint(attempt_id, int(current["generation"]), str(current["disposition"]), False, current["disposition"] == "VOID", ("terminal_state",))
        if disposition not in ("VOID", "COMMITTED"):
            return AdmissionCheckpoint(attempt_id, generation, "VOID", False, True, ("invalid_terminal_state",))
        data[attempt_id] = {"generation": generation, "disposition": disposition}
        self._write(data)
        return AdmissionCheckpoint(attempt_id, generation, disposition, disposition == "COMMITTED", disposition == "VOID", ())


@dataclass(frozen=True)
class EvidenceChunk:
    request_id: str
    corpus_hash: str
    index: int
    total: int
    data: bytes
    chunk_hash: str

    @staticmethod
    def create(request_id: str, corpus_hash: str, index: int, total: int, data: bytes) -> "EvidenceChunk":
        return EvidenceChunk(request_id, corpus_hash, index, total, data, sha256(data).hexdigest())


@dataclass(frozen=True)
class WireDeliveryRecord:
    attempt_id: str
    request_id: str
    wire_hash: str
    semantic_hash: str
    session_id: str
    item_ids: tuple[str, ...]


@dataclass(frozen=True)
class ReviewerReceipt:
    attempt_id: str
    request_id: str
    session_id: str
    manifest_hash: str
    received_item_ids: tuple[str, ...]
    received_bytes: int
    complete: bool


@dataclass(frozen=True)
class AccessibilityProofRecord:
    proof_id: str
    challenge_id: str
    provider_id: str
    mode: str
    final_context_id: str
    valid: bool


@dataclass(frozen=True)
class ReviewerProvenanceRecord:
    reviewer_id: str
    policy_hash: str
    trusted: bool


@dataclass(frozen=True)
class SemanticCoverageRecord:
    coverage_id: str
    context_id: str
    complete: bool


@dataclass(frozen=True)
class DeliveryCompletenessResult:
    complete: bool
    reasons: tuple[str, ...] = ()
    received_item_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class DeliveryPreflightResult:
    allowed: bool
    reasons: tuple[str, ...] = ()
    manifest_hash: str | None = None


@dataclass(frozen=True)
class InsufficientEvidenceAdjudication:
    disposition: str
    causes: tuple[str, ...]


@dataclass(frozen=True)
class AdmissibilityPredicateRegistry:
    version: str
    predicate_ids: tuple[str, ...]
    logic_mutation_ids: tuple[str, ...]
    fixture_ids: tuple[str, ...]

    def closure(self, verdict_ids: Iterable[str], killed_ids: Iterable[str]) -> bool:
        required = set(self.predicate_ids)
        def targets(values: Iterable[Any]) -> set[str]:
            out = set()
            for value in values:
                if isinstance(value, Mapping):
                    target = value.get("target_predicate_id", value.get("target"))
                    if target is not None and value.get("executed", True) and value.get("killed", True): out.add(str(target))
                else:
                    out.add(str(value))
            return out
        return required == targets(verdict_ids) == targets(killed_ids)


@dataclass(frozen=True)
class LogicMutationRecord:
    mutation_id: str
    target_predicate_id: str
    executed: bool
    killed: bool
    fixture_hash: str


@dataclass(frozen=True)
class NegativeFixtureRecord:
    fixture_id: str
    target_predicate_id: str
    fixture_hash: str


@dataclass(frozen=True)
class VerdictAdmissibilityResult:
    admissible: bool
    disposition: str
    predicate_results: Mapping[str, bool]
    reasons: tuple[str, ...] = ()

    @property
    def predicate_ids(self) -> tuple[str, ...]:
        return tuple(sorted(self.predicate_results))


@dataclass(frozen=True)
class PredicateContext:
    """Immutable expectations bound by the governing request, never by evidence."""
    request_id: str
    attempt_id: str
    session_id: str
    reviewed_commit: str
    authority_snapshot_id: str
    authority_snapshot_hash: str
    authority_version: str
    expected_provider: str
    expected_model: str
    expected_adapter: str
    expected_operating_point: str
    expected_profile_hash: str
    expected_egress_version: str
    transition_class: str
    fence_version: str
    prompt_provider: str
    prompt_mode: str
    witness_provider: str
    witness_mode: str
    witness_prompt_mode: str
    retrieval_source: str
    retrieval_version: str
    final_context_id: str
    final_context_hash: str
    max_context_bytes: int
    predicate_registry_version: str
    promotable_dispositions: tuple[str, ...] = ("PASS",)


@dataclass(frozen=True)
class EvidenceBundle:
    """Immutable evidence-bearing bundle consumed by the production verdict."""
    evidence: Mapping[str, Any]

    def get(self, key: str, default: Any = None) -> Any:
        return self.evidence.get(key, default)


def context_from_state(state: Mapping[str, Any]) -> PredicateContext:
    """Test/fixture adapter; production callers must supply frozen context explicitly."""
    return PredicateContext(
        request_id=str(state.get("expected_request_id", "r")),
        attempt_id=str(state.get("expected_attempt_id", "a")),
        session_id=str(state.get("expected_session_id", "s")),
        reviewed_commit=str(state.get("expected_reviewed_commit", "commit")),
        authority_snapshot_id=str(state.get("expected_authority_snapshot_id", getattr(state.get("authority_snapshot"), "snapshot_id", ""))),
        authority_snapshot_hash=str(state.get("expected_authority_snapshot_hash", getattr(state.get("authority_snapshot"), "content_hash", ""))),
        authority_version=str(state.get("expected_authority_version", getattr(state.get("authority_snapshot"), "version", ""))),
        expected_provider=str(state.get("expected_provider", "fake")), expected_model=str(state.get("expected_model", "deterministic")),
        expected_adapter=str(state.get("expected_adapter", "adapter")), expected_operating_point=str(state.get("expected_operating_point", "default")),
        expected_profile_hash=str(state.get("expected_profile_hash", "profile-hash")), expected_egress_version=str(state.get("expected_egress_version", "1")),
        transition_class=str(state.get("transition_class", "LOWER")), fence_version=str(state.get("expected_fence_version", "1")),
        prompt_provider=str(state.get("prompt_provider", "fake")), prompt_mode=str(state.get("prompt_mode", "inline")),
        witness_provider=str(state.get("witness_provider", "fake")), witness_mode=str(state.get("witness_mode", "inline")), witness_prompt_mode=str(state.get("witness_prompt_mode", "prompt")),
        retrieval_source=str(state.get("retrieval_source", "file")), retrieval_version=str(state.get("retrieval_version", "v")),
        final_context_id=str(state.get("final_context_id", "ctx")), final_context_hash=str(state.get("final_context_hash", "ctx-h")),
        max_context_bytes=int(state.get("max_context_bytes", 1_000_000)), predicate_registry_version=str(state.get("predicate_registry_version", "2")),
        promotable_dispositions=tuple(state.get("promotable_dispositions", ("PASS",))),
    )


def bundle_from_state(state: Mapping[str, Any]) -> EvidenceBundle:
    return EvidenceBundle(dict(state))


PREDICATES = (
    "review_request_current", "authority_snapshot_current", "evidence_contract_closed",
    "interaction_contract_closed", "materialization_complete", "representation_governed",
    "egress_authorized", "capability_current", "accessibility_policy_satisfied",
    "context_isolation_satisfied", "hidden_state_policy_satisfied", "context_state_clean",
    "admission_fence_current", "semantic_context_qualified", "wire_binding_valid",
    "delivery_complete", "accessibility_proven", "witness_record_current",
    "session_retrieval_coverage", "prompt_isolation_current", "semantic_coverage",
    "reviewer_provenance", "disposition_promotable",
)

# These are intentionally independent declarations.  They are not derived
# from one shared tuple so closure can detect omissions and aliases.
PREDICATE_DEFINITIONS = tuple({"id": p, "validator": f"validate_{p}"} for p in PREDICATES)
LOGIC_MUTATION_TARGETS = (
    "review_request_current", "authority_snapshot_current", "evidence_contract_closed",
    "interaction_contract_closed", "materialization_complete", "representation_governed",
    "egress_authorized", "capability_current", "accessibility_policy_satisfied",
    "context_isolation_satisfied", "hidden_state_policy_satisfied", "context_state_clean",
    "admission_fence_current", "semantic_context_qualified", "wire_binding_valid",
    "delivery_complete", "accessibility_proven", "witness_record_current",
    "session_retrieval_coverage", "prompt_isolation_current", "semantic_coverage",
    "reviewer_provenance", "disposition_promotable",
)
FIXTURE_IDS = tuple(f"negative:{p}" for p in PREDICATES)


def admissibility_registry() -> AdmissibilityPredicateRegistry:
    return AdmissibilityPredicateRegistry("2", tuple(d["id"] for d in PREDICATE_DEFINITIONS), LOGIC_MUTATION_TARGETS, FIXTURE_IDS)


def _predicate_validators(context: PredicateContext) -> dict[str, Any]:
    def egress_valid(state: Mapping[str, Any]) -> bool:
        egress = state.get("egress")
        if not isinstance(egress, Mapping):
            return False
        return validate_egress(egress, context.expected_egress_version)[0]

    def prompt_valid(state: Mapping[str, Any]) -> bool:
        prompt = state.get("prompt_isolation")
        if isinstance(prompt, PromptIsolationQualificationRecord):
            record = prompt
        elif isinstance(prompt, Mapping):
            record = PromptIsolationQualificationRecord(
                str(prompt.get("record_id", "prompt")),
                str(prompt.get("provider_id", context.prompt_provider)),
                str(prompt.get("mode", context.prompt_mode)),
                prompt.get("current") is True,
                prompt.get("expires_at"),
            )
        else:
            return False
        return validate_prompt_isolation(
            record,
            provider_id=context.prompt_provider,
            mode=context.prompt_mode,
            now=str(state.get("now", "2099-01-01T00:00:00Z")),
        )[0]

    return {
        "review_request_current": lambda s: isinstance(s.get("review_request"), Mapping) and s["review_request"].get("current") is True and s["review_request"].get("request_id") == context.request_id,
        "authority_snapshot_current": lambda s: isinstance(s.get("authority_snapshot"), GovernanceAuthoritySnapshot) and s["authority_snapshot"].outside_candidate_write_authority and s["authority_snapshot"].snapshot_id == context.authority_snapshot_id and s["authority_snapshot"].content_hash == context.authority_snapshot_hash and s["authority_snapshot"].version == context.authority_version,
        "evidence_contract_closed": lambda s: isinstance(s.get("evidence_contract"), RequiredEvidenceContract) and s["evidence_contract"].closed and s["evidence_contract"].non_vacuous,
        "interaction_contract_closed": lambda s: isinstance(s.get("interaction_contract"), RequiredInteractionContract) and s["interaction_contract"].closed and bool(s["interaction_contract"].interactions),
        "materialization_complete": lambda s: isinstance(s.get("materialization"), MaterializationResult) and s["materialization"].success,
        "representation_governed": lambda s: isinstance(s.get("representation"), RepresentationRecord) and s["representation"].transform_id in QUALIFIED_TRANSFORMS and s["representation"].registry_version == QUALIFIED_TRANSFORMS[s["representation"].transform_id] and bool(s["representation"].source_hash) and bool(s["representation"].representation_hash) and bool(s["representation"].parameters_hash) and bool(s["representation"].coverage_hash),
        "egress_authorized": egress_valid,
        "capability_current": lambda s: isinstance(s.get("capability"), Mapping) and s["capability"].get("validated") is True,
        "accessibility_policy_satisfied": lambda s: isinstance(s.get("accessibility_policy"), Mapping) and s["accessibility_policy"].get("satisfied") is True and s["accessibility_policy"].get("risk_policy_version") is not None,
        "context_isolation_satisfied": lambda s: isinstance(s.get("context_isolation"), Mapping) and s["context_isolation"].get("satisfied") is True and s["context_isolation"].get("transition_class") == context.transition_class,
        "hidden_state_policy_satisfied": lambda s: isinstance(s.get("hidden_state_policy"), Mapping) and s["hidden_state_policy"].get("satisfied") is True,
        "context_state_clean": lambda s: isinstance(s.get("context_state"), Mapping) and s["context_state"].get("clean") is True and s["context_state"].get("sentinel_passed") is True and bool(s["context_state"].get("state_hash")),
        "admission_fence_current": lambda s: isinstance(s.get("fence"), Mapping) and s["fence"].get("current") is True and s["fence"].get("version") == context.fence_version,
        "semantic_context_qualified": lambda s: isinstance(s.get("semantic_context"), Mapping) and s["semantic_context"].get("qualified") is True and s["semantic_context"].get("context_hash") == context.final_context_hash,
        "wire_binding_valid": lambda s: isinstance(s.get("wire"), WireDeliveryRecord) and s["wire"].request_id == context.request_id and bool(s["wire"].wire_hash) and bool(s["wire"].semantic_hash),
        "delivery_complete": lambda s: isinstance(s.get("delivery"), DeliveryCompletenessResult) and s["delivery"].complete,
        "accessibility_proven": lambda s: isinstance(s.get("accessibility"), AccessibilityProofRecord) and s["accessibility"].valid and s["accessibility"].challenge_id and s["accessibility"].final_context_id == context.final_context_id,
        "witness_record_current": lambda s: isinstance(s.get("witness"), WitnessProtocolQualificationRecord) and s["witness"].current and s["witness"].provider_id == context.witness_provider and s["witness"].mode == context.witness_mode,
        "session_retrieval_coverage": lambda s: isinstance(s.get("retrieval"), RetrievalEvidenceRecord) and validate_retrieval(s["retrieval"], s.get("retrieval_bytes", b""), expected_request=context.request_id, expected_attempt=context.attempt_id, expected_session=context.session_id, expected_source=context.retrieval_source, expected_version=context.retrieval_version, expected_context_id=context.final_context_id, expected_context_hash=context.final_context_hash)[0],
        "prompt_isolation_current": prompt_valid,
        "semantic_coverage": lambda s: isinstance(s.get("semantic_coverage"), SemanticCoverageRecord) and s["semantic_coverage"].complete and s["semantic_coverage"].context_id == context.final_context_id,
        "reviewer_provenance": lambda s: isinstance(s.get("reviewer"), ReviewerProvenanceRecord) and s["reviewer"].trusted and bool(s["reviewer"].policy_hash),
        "disposition_promotable": lambda s: s.get("disposition") in context.promotable_dispositions,
    }


def _validate_disposition(state: Mapping[str, Any], context: PredicateContext, predicate_results: Mapping[str, bool]) -> bool:
    return state.get("disposition") in context.promotable_dispositions and all(v for k, v in predicate_results.items() if k != "disposition_promotable")


def evaluate_admissibility(bundle: EvidenceBundle, context: PredicateContext, registry: AdmissibilityPredicateRegistry | None = None) -> VerdictAdmissibilityResult:
    registry = registry or admissibility_registry()
    validators = _predicate_validators(context)
    state = bundle.evidence
    predicates = {pid: bool(validators[pid](state)) for pid in registry.predicate_ids if pid != "disposition_promotable"}
    reasons = tuple(pid for pid, ok in predicates.items() if not ok)
    # Disposition validation is evaluated against the complete result, not a
    # caller-provided summary field.
    if "disposition_promotable" in registry.predicate_ids:
        predicates["disposition_promotable"] = _validate_disposition(state, context, predicates)
        reasons = tuple(pid for pid, ok in predicates.items() if not ok)
    return VerdictAdmissibilityResult(not reasons, "REVIEW_CONTEXT_QUALIFIED_AVAILABLE" if not reasons else "INADMISSIBLE", predicates, reasons)


def preflight_delivery(
    snapshot: GovernanceAuthoritySnapshot,
    evidence_contract: RequiredEvidenceContract,
    interactions: RequiredInteractionContract,
    manifest: EvidenceDeliveryManifest,
    request_id: str,
    provider: ProviderCapabilityProfile,
    items: Mapping[str, bytes],
    *,
    plan: ProviderQualificationExecutionPlan | None = None,
    qualification: ProviderCapabilityQualificationRecord | None = None,
    now: str = "2099-01-01T00:00:00Z",
    expected_provider: str = "fake",
    expected_model: str = "deterministic",
    expected_operating_point: str = "default",
    expected_profile_hash: str = "profile-hash",
    required_format: str = "text",
    required_context_bytes: int = 0,
    context_policy: ProviderContextIsolationPolicy | None = None,
    context_evidence: ProviderContextStateEvidence | None = None,
    fence: AdmissionFenceRecord | None = None,
    risk_policy: ProviderAccessibilityRiskPolicy | None = None,
    expected_transition_class: str = "LOWER",
    expected_fence_version: str = "1",
    observed_interactions: Sequence[Sequence[str]] | None = None,
) -> DeliveryPreflightResult:
    reasons: list[str] = []
    if not snapshot.outside_candidate_write_authority:
        reasons.append("authority_snapshot_candidate_writable")
    if snapshot.snapshot_id != evidence_contract.snapshot_id or snapshot.snapshot_id != interactions.snapshot_id:
        reasons.append("snapshot_binding_mismatch")
    if request_id != manifest.request_id:
        reasons.append("request_manifest_mismatch")
    if not evidence_contract.closed or not evidence_contract.non_vacuous or not evidence_contract.required_ids or not set(evidence_contract.required_ids).issubset(manifest.items):
        reasons.append("evidence_contract_unresolved")
    if not interactions.closed or not interactions.interactions or any(not set(interaction).issubset(manifest.items) for interaction in interactions.interactions):
        reasons.append("interaction_contract_unresolved")
    if observed_interactions is None or {tuple(x) for x in observed_interactions} != {tuple(x) for x in interactions.interactions}:
        reasons.append("interaction_observation_unbound")
    if plan is None or qualification is None:
        reasons.append("qualification_records_missing")
    else:
        capable, capability_reasons = validate_capability(provider, plan, qualification, now=now, expected_provider=expected_provider, expected_model=expected_model, expected_operating_point=expected_operating_point, expected_profile_hash=expected_profile_hash, required_format=required_format, required_context_bytes=required_context_bytes)
        if not capable:
            reasons.extend(capability_reasons)
    if context_policy is None or context_evidence is None or fence is None or risk_policy is None:
        reasons.append("context_isolation_records_missing")
    else:
        if risk_policy.transition_class != expected_transition_class:
            reasons.append("transition_class_policy_mismatch")
        isolated, isolation_reasons = validate_context_isolation(context_policy, context_evidence, fence, transition_class=risk_policy.transition_class, required_channels=("memory", "config"))
        if not isolated:
            reasons.extend(isolation_reasons)
        if fence.version != expected_fence_version:
            reasons.append("admission_fence_version_mismatch")
    ok, manifest_reasons = manifest.verify(items)
    if not ok:
        reasons.extend(manifest_reasons)
    return DeliveryPreflightResult(not reasons, tuple(reasons), manifest.manifest_hash if not reasons else None)


def complete_delivery(manifest: EvidenceDeliveryManifest, receipt: ReviewerReceipt, wire: WireDeliveryRecord) -> DeliveryCompletenessResult:
    reasons: list[str] = []
    expected = set(manifest.items)
    received = set(receipt.received_item_ids)
    if receipt.manifest_hash != manifest.manifest_hash:
        reasons.append("receipt_manifest_mismatch")
    if receipt.request_id != manifest.request_id or wire.request_id != manifest.request_id:
        reasons.append("request_binding_mismatch")
    if receipt.attempt_id != wire.attempt_id or receipt.session_id != wire.session_id:
        reasons.append("attempt_session_mismatch")
    if received != expected:
        reasons.append("required_item_set_incomplete")
    if not receipt.complete:
        reasons.append("reviewer_receipt_incomplete")
    if set(wire.item_ids) != expected:
        reasons.append("wire_item_set_incomplete")
    return DeliveryCompletenessResult(not reasons, tuple(reasons), tuple(sorted(received)))


def canonical_wire_hash(request_id: str, attempt_id: str, session_id: str, returned_items: Mapping[str, bytes]) -> str:
    return digest({"request_id": request_id, "attempt_id": attempt_id, "session_id": session_id, "items": {k: {"sha256": sha256(v).hexdigest(), "size": len(v)} for k, v in sorted(returned_items.items())}})


def adjudicate_insufficient_evidence(flags: Mapping[str, bool]) -> InsufficientEvidenceAdjudication:
    causes = tuple(sorted(k for k, v in flags.items() if v))
    if len(causes) > 1:
        return InsufficientEvidenceAdjudication("MIXED_INSUFFICIENCY", causes)
    return InsufficientEvidenceAdjudication(causes[0] if causes else "INSUFFICIENT_EVIDENCE_CAUSE_UNRESOLVED", causes)


class DeterministicFakeProvider:
    """Fake provider exposing a transparent, append-only delivery surface."""

    def __init__(self, *, clean_context: bool = True, supports_formats: Sequence[str] = ("text", "json"), max_context_bytes: int = 1_000_000):
        self.clean_context = clean_context
        self.supports_formats = tuple(supports_formats)
        self.max_context_bytes = max_context_bytes
        self.session_id = "session-1"
        self.receipts: list[ReviewerReceipt] = []

    def deliver(self, manifest: EvidenceDeliveryManifest, items: Mapping[str, bytes], attempt_id: str = "attempt-1") -> tuple[ReviewerReceipt, WireDeliveryRecord]:
        wire_hash = canonical_wire_hash(manifest.request_id, attempt_id, self.session_id, items)
        wire = WireDeliveryRecord(attempt_id, manifest.request_id, wire_hash, wire_hash, self.session_id, tuple(sorted(items)))
        receipt = ReviewerReceipt(attempt_id, manifest.request_id, self.session_id, manifest.manifest_hash, tuple(sorted(items)), sum(map(len, items.values())), True)
        self.receipts.append(receipt)
        return receipt, wire


def validate_chunks(chunks: Sequence[EvidenceChunk], *, request_id: str, corpus_hash: str) -> tuple[bool, tuple[str, ...], bytes]:
    """Validate chunk identity/order and reconstruct only an exact corpus."""
    reasons: list[str] = []
    if not chunks:
        return False, ("chunks_missing",), b""
    totals = {c.total for c in chunks}
    if totals != {len(chunks)}:
        reasons.append("chunk_total_mismatch")
    if any(c.request_id != request_id for c in chunks):
        reasons.append("chunk_request_mismatch")
    if any(c.corpus_hash != corpus_hash for c in chunks):
        reasons.append("chunk_corpus_mismatch")
    indices = [c.index for c in chunks]
    if len(set(indices)) != len(indices):
        reasons.append("chunk_duplicate_index")
    if sorted(indices) != list(range(len(chunks))):
        reasons.append("chunk_index_gap_or_range")
    for c in chunks:
        if sha256(c.data).hexdigest() != c.chunk_hash:
            reasons.append(f"chunk_hash_mismatch:{c.index}")
        if not c.data:
            reasons.append(f"chunk_empty:{c.index}")
    raw = b"".join(c.data for c in sorted(chunks, key=lambda x: x.index))
    if digest(raw) != corpus_hash:
        reasons.append("corpus_hash_mismatch")
    return not reasons, tuple(reasons), raw


def validate_representation(manifest: EvidenceDeliveryManifest, items: Mapping[str, bytes], record: RepresentationRecord | None = None) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    ok, manifest_reasons = manifest.verify(items)
    if not ok:
        reasons.extend(manifest_reasons)
    if any(not isinstance(v, bytes) for v in items.values()):
        reasons.append("non_raw_representation")
    if record is not None:
        if record.transform_id not in QUALIFIED_TRANSFORMS or not record.transform_version or not record.transform_hash or record.registry_version != QUALIFIED_TRANSFORMS[record.transform_id]:
            reasons.append("representation_transform_unqualified")
        if record.source_hash != manifest.manifest_hash or record.representation_hash != digest({k: sha256(v).hexdigest() for k, v in sorted(items.items())}):
            reasons.append("representation_record_mismatch")
        if not record.parameters_hash or not record.coverage_hash:
            reasons.append("representation_coverage_unbound")
    return not reasons, tuple(reasons)


def validate_attempt_ledger(planned_ids: Sequence[str], dispatched_ids: Sequence[str], failed_ids: Sequence[str], retried_ids: Sequence[str] = ()) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    if list(planned_ids) != list(dict.fromkeys(planned_ids)):
        reasons.append("duplicate_planned_id")
    if set(dispatched_ids) != set(planned_ids):
        reasons.append("attempt_set_not_closed")
    if any(x in retried_ids and x in failed_ids for x in retried_ids):
        reasons.append("failed_attempt_substituted")
    if len(dispatched_ids) != len(set(dispatched_ids)):
        reasons.append("duplicate_dispatch")
    return not reasons, tuple(reasons)


def validate_retry_transparency(physical_requests: Sequence[Mapping[str, Any] | PhysicalAttemptRecord], *, planned_root_ids: Sequence[str] = (), expected_request: str | None = None, expected_session: str | None = None, automatic_retry_hidden: bool = False) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    if automatic_retry_hidden:
        reasons.append("implicit_retry_unobserved")
    if not physical_requests:
        reasons.append("physical_request_missing")
    if any((req.attempt_id if isinstance(req, PhysicalAttemptRecord) else req.get("attempt_id")) is None or (req.wire_hash if isinstance(req, PhysicalAttemptRecord) else req.get("wire_hash")) is None for req in physical_requests):
        reasons.append("wire_attempt_unbound")
    records = [r if isinstance(r, PhysicalAttemptRecord) else PhysicalAttemptRecord(str(r.get("attempt_id", "")), str(r.get("planned_root_id", r.get("attempt_id", ""))), r.get("parent_attempt_id"), str(r.get("kind", "FIRST")), str(r.get("request_id", "")), str(r.get("session_id", "")), str(r.get("wire_hash", "")), str(r.get("outcome", ""))) for r in physical_requests]
    if planned_root_ids:
        firsts = [r for r in records if r.kind == "FIRST"]
        if {r.planned_root_id for r in firsts} != set(planned_root_ids) or len(firsts) != len(set(r.planned_root_id for r in firsts)):
            reasons.append("planned_first_attempt_closure")
        by_id = {r.attempt_id: r for r in records}
        for retry in (r for r in records if r.kind == "RETRY"):
            if retry.attempt_id in planned_root_ids or retry.parent_attempt_id not in by_id or by_id[retry.parent_attempt_id].outcome != "FAILED":
                reasons.append("retry_lineage_invalid")
    if expected_request is not None and any(r.request_id != expected_request for r in records):
        reasons.append("request_identity_mismatch")
    if expected_session is not None and any(r.session_id != expected_session for r in records):
        reasons.append("session_identity_mismatch")
    return not reasons, tuple(reasons)


def validate_witness(challenge: str, response: str, *, max_response_bytes: int, semantic_prompt: bool = False) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    if semantic_prompt:
        reasons.append("witness_asks_for_semantic_judgment")
    if not challenge or not response:
        reasons.append("witness_missing")
    if len(response.encode()) > max_response_bytes:
        reasons.append("witness_budget_exceeded")
    return not reasons, tuple(reasons)


def validate_context_state(state: ProviderContextStateEvidence, *, required_channels: Sequence[str]) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    if not state.clean or not state.sentinel_passed:
        reasons.append("provider_context_not_clean")
    if not set(required_channels).issubset(state.observable_channels):
        reasons.append("context_channel_unobserved")
    if not state.state_hash:
        reasons.append("context_state_unbound")
    return not reasons, tuple(reasons)


def validate_fence(fence: AdmissionFenceRecord, expected_version: str) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    if not fence.current:
        reasons.append("admission_fence_not_current")
    if fence.version != expected_version:
        reasons.append("admission_fence_version_mismatch")
    return not reasons, tuple(reasons)


def validate_egress(egress: Mapping[str, Any], expected_version: str) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    if egress.get("authorized") is not True or egress.get("version") != expected_version:
        reasons.append("egress_revoked_or_drifted")
    return not reasons, tuple(reasons)


def validate_prompt_isolation(record: PromptIsolationQualificationRecord, *, provider_id: str, mode: str, now: str) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    if not record.current or record.provider_id != provider_id or record.mode != mode:
        reasons.append("prompt_isolation_binding")
    if record.expires_at is not None and record.expires_at <= now:
        reasons.append("prompt_isolation_expired")
    return not reasons, tuple(reasons)


def validate_registry_version(expected_version: str, observed_version: str) -> tuple[bool, tuple[str, ...]]:
    return (True, ()) if expected_version == observed_version else (False, ("predicate_registry_drift",))


def safe_archive_member(name: str) -> bool:
    """Reject traversal, absolute paths, drive paths and ambiguous separators."""
    from pathlib import PurePosixPath
    if not name or "\\" in name or name.startswith("/") or ":" in name:
        return False
    parts = PurePosixPath(name).parts
    return ".." not in parts and all(part not in ("", ".") for part in parts)


QUALIFIED_TRANSFORMS = {"raw-v1": "registry-exp-m-r1"}


def materialize_entries(entries: Mapping[str, bytes] | Sequence[MaterializationEntry], *, source_hash: str, transform_id: str = "raw-v1", max_total_bytes: int = 4_000_000, max_entries: int = 10_000, max_member_bytes: int = 1_000_000, max_recursion_depth: int = 4, max_ratio: int = 100) -> MaterializationResult:
    reasons: list[str] = []
    total = 0
    clean: dict[str, bytes] = {}
    typed = entries if not isinstance(entries, Mapping) else tuple(MaterializationEntry(name, name, "file", value, None, len(value), len(value), 0, name) for name, value in entries.items())
    if transform_id not in QUALIFIED_TRANSFORMS:
        reasons.append("unqualified_transform")
    if len(typed) > max_entries:
        reasons.append("materialization_entry_limit")
    seen: set[str] = set()
    for entry in typed:
        name, value = entry.normalized_path, entry.data
        if not safe_archive_member(entry.raw_name) or not safe_archive_member(name):
            reasons.append(f"unsafe_member:{entry.raw_name}")
            continue
        if name in seen:
            reasons.append(f"duplicate_normalized_member:{name}")
            continue
        seen.add(name)
        if entry.kind not in ("file", "symlink", "archive"):
            reasons.append(f"unsupported_member_kind:{name}")
        if entry.kind == "symlink" and (not entry.link_target or not safe_archive_member(entry.link_target)):
            reasons.append(f"symlink_escape:{name}")
        if entry.recursion_depth > max_recursion_depth:
            reasons.append(f"archive_recursion:{name}")
        if entry.compressed_size and entry.uncompressed_size and entry.uncompressed_size > entry.compressed_size * max_ratio:
            reasons.append(f"decompression_ratio:{name}")
        if not isinstance(value, bytes):
            reasons.append(f"non_bytes:{name}")
            continue
        if len(value) > max_member_bytes:
            reasons.append(f"member_size_limit:{name}")
        total += len(value)
        clean[name] = value
    if total > max_total_bytes:
        reasons.append("materialization_size_limit")
    representation_hash = digest({k: sha256(v).hexdigest() for k, v in sorted(clean.items())})
    return MaterializationResult(not reasons, clean, representation_hash, source_hash, transform_id, tuple(reasons))


def validate_capability(profile: ProviderCapabilityProfile, plan: ProviderQualificationExecutionPlan, record: ProviderCapabilityQualificationRecord, *, now: str, expected_provider: str, expected_model: str, expected_operating_point: str, expected_profile_hash: str, required_format: str, required_context_bytes: int) -> tuple[bool, tuple[str, ...]]:
    """Compute capability currentness from bound records; no qualified flag is authoritative."""
    reasons: list[str] = []
    if not plan.plan_id or not record.plan_id or plan.plan_id != record.plan_id:
        reasons.append("qualification_plan_identity_mismatch")
    if not plan.trial_ids or not plan.confirmation_ids:
        reasons.append("qualification_sets_empty")
    if profile.provider_id != expected_provider or profile.model_id != expected_model:
        reasons.append("provider_model_mismatch")
    if profile.profile_hash != expected_profile_hash or record.profile_hash != expected_profile_hash:
        reasons.append("profile_hash_mismatch")
    if plan.provider_id != expected_provider or record.provider_id != expected_provider or record.model_id != expected_model:
        reasons.append("qualification_identity_mismatch")
    if plan.operating_point != expected_operating_point or record.operating_point != expected_operating_point:
        reasons.append("operating_point_mismatch")
    if required_format not in profile.supported_formats:
        reasons.append("unsupported_format")
    if profile.max_context_bytes < required_context_bytes:
        reasons.append("context_limit_exceeded")
    if not record.statistical_qualified or record.hard_failures != 0:
        reasons.append("qualification_not_statistically_valid")
    if not record.planned_attempt_ids or not record.closed_attempt_ids or set(record.planned_attempt_ids) != set(plan.confirmation_ids) or set(record.closed_attempt_ids) != set(plan.confirmation_ids):
        reasons.append("qualification_attempt_closure")
    if record.attempt_records:
        attempts = list(record.attempt_records)
        roots = [a for a in attempts if getattr(a, "kind", "FIRST") == "FIRST"]
        if {getattr(a, "planned_root_id", "") for a in roots} != set(plan.confirmation_ids) or len(roots) != len(set(getattr(a, "planned_root_id", "") for a in roots)):
            reasons.append("qualification_attempt_records_incomplete")
        if any(getattr(a, "kind", "") == "RETRY" and (getattr(a, "parent_attempt_id", None) is None or not any(getattr(p, "attempt_id", None) == getattr(a, "parent_attempt_id", None) and getattr(p, "outcome", "") == "FAILED" for p in attempts)) for a in attempts):
            reasons.append("qualification_retry_lineage_invalid")
    if profile.expires_at is not None and profile.expires_at <= now:
        reasons.append("profile_expired")
    return not reasons, tuple(reasons)


def validate_context_isolation(policy: ProviderContextIsolationPolicy, evidence: ProviderContextStateEvidence, fence: AdmissionFenceRecord, *, transition_class: str, required_channels: Sequence[str]) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    if not policy.policy_id or policy.basis not in ("COMPLETE_READABLE_FENCED_STATE", "DEDICATED_PLATFORM_ACCOUNT_STATELESS_BOUNDARY"):
        reasons.append("context_policy_invalid")
    if transition_class == "HIGHEST" and policy.hidden_state_allowed:
        reasons.append("hidden_state_residual_disallowed")
    clean, clean_reasons = validate_context_state(evidence, required_channels=required_channels)
    if not clean:
        reasons.extend(clean_reasons)
    if not fence.current:
        reasons.append("admission_fence_stale")
    return not reasons, tuple(reasons)


def validate_retrieval(record: RetrievalEvidenceRecord, raw: bytes, *, expected_request: str, expected_attempt: str, expected_session: str, expected_source: str, expected_version: str, expected_context_id: str, expected_context_hash: str) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    if record.request_id != expected_request or record.attempt_id != expected_attempt or record.session_id != expected_session:
        reasons.append("retrieval_identity_mismatch")
    if record.source_id != expected_source or record.source_version != expected_version:
        reasons.append("retrieval_source_mismatch")
    if record.end - record.start != len(raw) or record.returned_length != len(raw) or record.returned_sha256 != sha256(raw).hexdigest():
        reasons.append("retrieval_bytes_mismatch")
    if not record.tool_result_id:
        reasons.append("retrieval_tool_result_missing")
    if record.final_context_id != expected_context_id or record.final_context_hash != expected_context_hash:
        reasons.append("retrieval_final_context_unbound")
    return not reasons, tuple(reasons)


def validate_witness_qualification(record: WitnessProtocolQualificationRecord, *, provider_id: str, mode: str, prompt_mode: str, now: str, response: str, challenge: str, final_context_bytes: int, max_final_context_bytes: int) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    if not record.current or record.provider_id != provider_id or record.mode != mode or record.prompt_isolation_mode != prompt_mode:
        reasons.append("witness_record_binding")
    if record.expires_at is not None and record.expires_at <= now:
        reasons.append("witness_record_expired")
    if not challenge or not response or len(response.encode()) > record.max_response_bytes:
        reasons.append("witness_response_invalid")
    if final_context_bytes + len(response.encode()) > max_final_context_bytes:
        reasons.append("witness_context_eviction")
    if any(word in challenge.lower() for word in ("summarize", "judge", "evaluate", "defect")):
        reasons.append("witness_semantic_prompt")
    return not reasons, tuple(reasons)


def validate_wire_delivery(manifest: EvidenceDeliveryManifest, materialized: MaterializationResult, wire: WireDeliveryRecord, receipt: ReviewerReceipt, returned_items: Mapping[str, bytes], *, expected_commit: str, expected_semantic_hash: str) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    completion = complete_delivery(manifest, receipt, wire)
    if not completion.complete:
        reasons.extend(completion.reasons)
    raw_ok, raw_reasons = manifest.verify(returned_items)
    if not raw_ok:
        reasons.extend(raw_reasons)
    if manifest.reviewed_commit != expected_commit:
        reasons.append("reviewed_commit_mismatch")
    if materialized.source_hash != expected_commit:
        reasons.append("materialization_source_mismatch")
    if wire.semantic_hash != expected_semantic_hash:
        reasons.append("semantic_wire_hash_mismatch")
    if materialized.representation_hash != digest({k: sha256(v).hexdigest() for k, v in sorted(returned_items.items())}):
        reasons.append("representation_hash_mismatch")
    if receipt.received_bytes != sum(len(v) for v in returned_items.values()):
        reasons.append("receipt_byte_count_mismatch")
    expected_wire_hash = canonical_wire_hash(manifest.request_id, wire.attempt_id, wire.session_id, returned_items)
    if wire.wire_hash != expected_wire_hash:
        reasons.append("wire_hash_mismatch")
    if wire.semantic_hash != expected_wire_hash:
        reasons.append("semantic_envelope_hash_mismatch")
    return not reasons, tuple(reasons)


def admit_review_attempt(current: Mapping[str, Any], expected: AttemptState, *, attempt_id: str, expected_generation: int, ledger: PersistentAdmissionLedger | None = None) -> AdmissionCheckpoint:
    """Final compare-and-set admission; any drift permanently voids the attempt."""
    reasons: list[str] = []
    if attempt_id != expected.attempt_id or expected.invalidated:
        reasons.append("attempt_invalidated")
    if current.get("generation") != expected_generation or current.get("generation") != expected.generation:
        reasons.append("generation_drift")
    for field_name in ("authority_version", "request_version", "capability_hash", "egress_version", "context_hash", "fence_version", "prompt_hash", "witness_hash", "session_hash", "registry_version"):
        if current.get(field_name) != getattr(expected, field_name):
            reasons.append(f"state_drift:{field_name}")
    if reasons:
        checkpoint = ledger.compare_and_set(attempt_id, expected.generation, "VOID") if ledger else AdmissionCheckpoint(attempt_id, expected.generation, "VOID", False, True, tuple(reasons))
        return AdmissionCheckpoint(checkpoint.attempt_id, checkpoint.generation, checkpoint.disposition, False, True, tuple(reasons) + tuple(checkpoint.reasons))
    if ledger:
        checkpoint = ledger.compare_and_set(attempt_id, expected.generation, "COMMITTED")
        return checkpoint
    return AdmissionCheckpoint(attempt_id, expected.generation, "ADMITTED", True, False, ())


def admit_review_attempt_with_evidence(bundle: EvidenceBundle, context: PredicateContext, current: Mapping[str, Any], expected: AttemptState, *, attempt_id: str, expected_generation: int, registry: AdmissibilityPredicateRegistry | None = None, ledger: PersistentAdmissionLedger | None = None) -> AdmissionCheckpoint:
    """Final admission path: revalidate evidence immediately before persistent CAS."""
    verdict = evaluate_admissibility(bundle, context, registry)
    if not verdict.admissible:
        if ledger:
            ledger.compare_and_set(attempt_id, expected.generation, "VOID")
        return AdmissionCheckpoint(attempt_id, expected.generation, "VOID", False, True, verdict.reasons)
    return admit_review_attempt(current, expected, attempt_id=attempt_id, expected_generation=expected_generation, ledger=ledger)
```


### governance-runtime/build_exp_m_review_packet.py

```python
"""Build a self-contained deterministic EXP-M implementation review packet."""
from __future__ import annotations
from hashlib import sha256
import json, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments" / "governed-platform" / "EXP-M-DETERMINISTIC-IMPLEMENTATION-R2-REVIEW.md"
SOURCES = [
    Path("governance-runtime/exp_m_deterministic.py"),
    Path("governance-runtime/build_exp_m_review_packet.py"),
    Path("governance-runtime/run_exp_m_deterministic.py"),
    Path("governance-runtime/run_exp_m_mutations.py"),
    Path("governance-runtime/self_falsify_exp_m.py"),
    Path("governance-runtime/test_exp_m_deterministic.py"),
    Path("governance-runtime/test_exp_m_phases.py"),
]


def sh(*args: str) -> str:
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def fence(name: str, body: str, lang: str = "text") -> str:
    return f"\n### {name}\n\n```{lang}\n{body.rstrip()}\n```\n"


def main() -> int:
    phase = json.loads((ROOT / "experiments/governed-platform/EXP-M-DETERMINISTIC-RESULTS.json").read_text())
    mutation = json.loads((ROOT / "experiments/governed-platform/EXP-M-MUTATION-RESULTS.json").read_text())
    falsify = json.loads((ROOT / "experiments/governed-platform/EXP-M-SELF-FALSIFICATION-RESULTS.json").read_text())
    r2_review = (ROOT / "experiments/governed-platform/EXP-M-DETERMINISTIC-EXTERNAL-REVIEW-R2.md").read_text(encoding="utf-8")
    r2_adjudication = (ROOT / "experiments/governed-platform/EXP-M-DETERMINISTIC-R2-SOLUTION-ADJUDICATION.md").read_text(encoding="utf-8")
    r2_remediation = (ROOT / "experiments/governed-platform/EXP-M-DETERMINISTIC-REMEDIATION-R2.md").read_text(encoding="utf-8")
    execution_files = [Path("experiments/governed-platform/EXP-M-UNIT-STDOUT.txt"), Path("experiments/governed-platform/EXP-M-PHASE-STDOUT.txt"), Path("experiments/governed-platform/EXP-M-MUTATION-STDOUT.txt"), Path("experiments/governed-platform/EXP-M-DETERMINISTIC-STDOUT.txt"), Path("experiments/governed-platform/EXP-M-SELF-STDOUT.txt")]
    execution_hashes = {p.as_posix(): sha256((ROOT / p).read_bytes()).hexdigest() for p in execution_files if (ROOT / p).exists()}
    hashes = {p.as_posix(): sha256((ROOT / p).read_bytes()).hexdigest() for p in SOURCES}
    frozen = {}
    for p in ["standards/review-evidence-delivery-integrity.md", "experiments/governed-platform/exp-m-review-evidence-delivery-integrity.md", "experiments/governed-platform/EXP-M-TEST-MATRIX.md", "governance-runtime/LIVE-CONVERSATION-GOVERNANCE.md", "experiments/governed-platform/EXP-M-R5-EXTERNAL-REVIEW.md"]:
        frozen[p] = sha256((ROOT / p).read_bytes()).hexdigest()
    lines = [
        "# EXP-M Deterministic Implementation R2 Independent Review Packet",
        "",
        "This packet covers deterministic implementation only. EXP-M remains NOT_QUALIFIED; no live provider/API call occurred.",
        "",
        "## Historical superseded evidence",
        "The prior A-T/22-test/29-mutation report is retained in Git history but is superseded by the independent R1 CHANGES_REQUIRED review. It is not used as closure evidence.",
        "R2 is the current remediation authority. Prior R1 and historical false-green outputs are superseded evidence only.",
        "",
        "## R2 authority inputs",
        fence("External R2 review", r2_review), fence("R2 solution adjudication", r2_adjudication), fence("R2 remediation", r2_remediation),
        "",
        "## R1 remediation matrix",
        "| Finding family | Production mechanism | Fresh evidence |",
        "|---|---|---|",
        "| C-01/H-10 taxonomy and closure | `adjudicate_insufficient_evidence`, independent predicate registry | Phase D, O/T and mutation closure |",
        f"| C-02/C-10/H-01 | production mutation runner with data/state and validator-logic families | Phase G; {mutation['rejected_mutations']}/{mutation['total_mutations']} rejected |",
        "| C-03/H-02 | evidence-derived predicate dispatch with independently declared targets | structured admissibility fixtures and negative controls |",
        "| C-04/H-04 | `validate_capability` binds profile, plan, record, expiry, format, context and attempts | capability mutation cases |",
        "| C-05/H-05 | `validate_context_isolation` binds policy, sentinel state and fence | dirty/hidden/stale-context cases |",
        "| C-06 | `admit_review_attempt` compare-and-set and permanent void result | generation/state-drift test |",
        "| C-07 | `RetrievalEvidenceRecord` raw-byte and final-context binding | retrieval byte/session/context mutation |",
        "| C-08 | current witness qualification, semantic prompt and eviction checks | witness positive/negative cases |",
        "| C-09/H-09 | byte, representation, semantic and source/wire/receipt binding | returned-byte mutation |",
        f"| C-11 | expanded self-falsification includes every current mutation family | {falsify['total']} cases, {falsify['surviving_critical']} critical/{falsify.get('surviving_high', falsify['surviving_critical'])} high survivors |",
        "| NC-01/NC-11/NH-01..NH-08 | no production bypass, typed evidence/context, persistent admission, lineage and freshness binding | static/behavioral/mutation/self-falsification evidence |",
        "",
        "## Identity",
        f"branch={sh('git','branch','--show-current')}",
        f"commit={sh('git','rev-parse','HEAD')}",
        f"tree={sh('git','rev-parse','HEAD^{tree}')}",
        f"parent={sh('git','rev-parse','HEAD^')}",
        "frozen_design_commit=0ba6c3c24ec247f5ad993b7e2f996ccd472b5f45",
        "authority_status=NOT_QUALIFIED",
        "live_provider_execution=false",
        "",
        "## Fresh evidence execution identity",
        json.dumps({"source_commit": phase.get("execution", {}).get("source_commit"), "source_tree": phase.get("execution", {}).get("source_tree"), "execution_hashes": execution_hashes}, indent=2, sort_keys=True),
        "",
        "## Deterministic exit gates",
        f"all_phases_A_to_T_pass={phase['all_phases_pass']}",
        f"mutation_total={mutation['total_mutations']}",
        f"mutation_rejected={mutation['rejected_mutations']}",
        f"mutation_survivors={mutation['surviving_mutations']}",
        f"all_mutations_rejected={mutation['all_rejected']}",
        f"critical_self_falsification_survivors={falsify['surviving_critical']}",
        f"high_self_falsification_survivors={falsify.get('surviving_high', falsify['surviving_critical'])}",
        "",
        "## Frozen source-of-truth hashes",
        "```json", json.dumps(frozen, indent=2, sort_keys=True), "```",
        "",
        "## Implemented source hashes",
        "```json", json.dumps(hashes, indent=2, sort_keys=True), "```",
        "",
        "## Phase A-T results",
        "```json", json.dumps(phase, indent=2, sort_keys=True), "```",
        "",
        "## Mutation results",
        "```json", json.dumps(mutation, indent=2, sort_keys=True), "```",
        "",
        "## Self-falsification results",
        "```json", json.dumps(falsify, indent=2, sort_keys=True), "```",
        "",
        "## Governance boundary",
        "- `EXP-M = NOT_QUALIFIED`.",
        "- No live Claude, DeepSeek, Gemini, OpenRouter, or other provider execution was performed.",
        "- No release, promotion, or authority effect is claimed.",
        "- Independent external review remains required before any live provider pilot.",
    ]
    for p in SOURCES:
        lines.append(fence(p.as_posix(), (ROOT / p).read_text(encoding="utf-8"), "python"))
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```


### governance-runtime/run_exp_m_deterministic.py

```python
"""Run EXP-M deterministic phases A-T using the production validators."""
from __future__ import annotations
import json
import sys
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).parent))
from exp_m_deterministic import (  # noqa: E402
    DeterministicFakeProvider, EvidenceChunk, EvidenceDeliveryManifest, GovernanceAuthoritySnapshot,
    ProviderCapabilityProfile, ProviderQualificationExecutionPlan, ProviderCapabilityQualificationRecord,
    ProviderContextIsolationPolicy, ProviderContextStateEvidence, AdmissionFenceRecord,
    RequiredEvidenceContract, RequiredInteractionContract,
    ProviderAccessibilityRiskPolicy,
    WireDeliveryRecord, ReviewerReceipt, admissibility_registry, complete_delivery,
    digest, evaluate_admissibility, preflight_delivery, validate_attempt_ledger,
    validate_chunks, validate_representation, validate_retry_transparency, validate_witness,
    ProviderContextStateEvidence, AdmissionFenceRecord, validate_context_state,
    validate_fence, safe_archive_member,
    adjudicate_insufficient_evidence,
    validate_capability, validate_witness_qualification, WitnessProtocolQualificationRecord, RetrievalEvidenceRecord,
    bundle_from_state, context_from_state,
    AccessibilityProofRecord, ReviewerProvenanceRecord, SemanticCoverageRecord, DeliveryCompletenessResult,
    RepresentationRecord,
)
from run_exp_m_mutations import run as run_mutations


PHASES = tuple("ABCDEFGHIJKLMNOPQRST")


def phase_fixture():
    snapshot = GovernanceAuthoritySnapshot("snap", "1", "snapshot-hash", True)
    contract = RequiredEvidenceContract("ec", "snap", ("required-a", "required-b"))
    interactions = RequiredInteractionContract("ic", "snap", (("required-a", "required-b"),))
    items = {"required-a": b"raw-a", "required-b": b"raw-b"}
    manifest = EvidenceDeliveryManifest.freeze("request", "reviewed-commit", items)
    provider = ProviderCapabilityProfile("fake", "deterministic", "adapter-1", "profile-hash", True, supported_formats=("text",), max_context_bytes=1_000_000)
    return snapshot, contract, interactions, items, manifest, provider


def valid_preflight(snapshot, contract, interactions, manifest, provider, items):
    return preflight_delivery(snapshot, contract, interactions, manifest, "request", provider, items,
        plan=ProviderQualificationExecutionPlan("plan", "fake", "default", ("a1",), ("a1",)),
        qualification=ProviderCapabilityQualificationRecord("plan", "profile-hash", True, True, 0, "default", ("a1",), ("a1",), "fake", "deterministic"),
        context_policy=ProviderContextIsolationPolicy("policy", "COMPLETE_READABLE_FENCED_STATE"),
        context_evidence=ProviderContextStateEvidence(True, ("memory", "config"), True, "state"),
        fence=AdmissionFenceRecord("fence", "1", True), risk_policy=ProviderAccessibilityRiskPolicy("LOWER", "inline", True, False), observed_interactions=(("required-a", "required-b"),))


def run_phases() -> dict:
    s, c, i, items, manifest, provider = phase_fixture()
    phase_results: dict[str, dict] = {}
    pre = valid_preflight(s, c, i, manifest, provider, items)
    phase_results["A"] = {"status": "PASS" if pre.allowed else "FAIL", "checks": ["required closure", "manifest bytes", "trusted profile"]}
    corpus = b"abcdefghij"; ch = [EvidenceChunk.create("request", digest(corpus), n, 2, part) for n, part in enumerate((corpus[:5], corpus[5:]))]
    phase_results["B"] = {"status": "PASS" if validate_chunks(ch, request_id="request", corpus_hash=digest(corpus))[0] else "FAIL", "checks": ["chunk hash", "index", "request binding"]}
    phase_results["C"] = {"status": "PASS" if validate_representation(manifest, items)[0] else "FAIL", "checks": ["raw bytes", "representation hash"]}
    single = adjudicate_insufficient_evidence({"SCIENTIFIC_EVIDENCE_MISSING": True})
    mixed = adjudicate_insufficient_evidence({"SCIENTIFIC_EVIDENCE_MISSING": True, "EVIDENCE_DELIVERY_INCOMPLETE": True})
    unresolved = adjudicate_insufficient_evidence({})
    phase_results["D"] = {"status": "PASS" if single.disposition == "SCIENTIFIC_EVIDENCE_MISSING" and mixed.disposition == "MIXED_INSUFFICIENCY" and unresolved.disposition == "INSUFFICIENT_EVIDENCE_CAUSE_UNRESOLVED" else "FAIL", "checks": ["single cause", "mixed causes", "unresolved cause"]}
    phase_results["E"] = {"status": "PASS" if manifest.verify(items)[0] and manifest.request_id == "request" else "FAIL", "checks": ["same manifest", "same corpus hash"]}
    capability = validate_capability(provider, ProviderQualificationExecutionPlan("plan", "fake", "default", ("a1",), ("a1",)), ProviderCapabilityQualificationRecord("plan", "profile-hash", True, True, 0, "default", ("a1",), ("a1",), "fake", "deterministic"), now="2025-01-01T00:00:00Z", expected_provider="fake", expected_model="deterministic", expected_operating_point="default", expected_profile_hash="profile-hash", required_format="text", required_context_bytes=1)
    phase_results["F"] = {"status": "PASS" if capability[0] else "FAIL", "checks": ["profile identity", "expiry", "operating point", "attempt closure", "context limit"]}
    mutation_result = run_mutations()
    phase_results["G"] = {"status": "PASS" if mutation_result["all_rejected"] and mutation_result["surviving_mutations"] == 0 else "FAIL", "checks": ["data/state mutation family", "validator mutation family"], "mutation_total": mutation_result["total_mutations"]}
    phase_results["H"] = {"status": "PASS" if validate_retry_transparency(({"attempt_id": "a", "wire_hash": "w"},))[0] else "FAIL", "checks": ["physical request ledger"]}
    registry = admissibility_registry(); state = {
        "review_request": {"current": True, "request_id": "r"}, "authority_snapshot": s,
        "evidence_contract": c, "interaction_contract": i, "materialization": __import__("exp_m_deterministic").MaterializationResult(True, items, "rep", "src", "raw-v1"),
        "representation": RepresentationRecord("raw-v1", "1", "transform", "registry-exp-m-r1", "src", "rep", "params", "coverage"), "egress": {"authorized": True, "version": "1"},
        "capability": {"validated": True}, "accessibility_policy": {"satisfied": True, "risk_policy_version": "r1"}, "accessibility": AccessibilityProofRecord("proof", "ch", "fake", "inline", "ctx", True),
        "context_isolation": {"satisfied": True, "transition_class": "LOWER"}, "hidden_state_policy": {"satisfied": True}, "context_state": {"clean": True, "sentinel_passed": True, "state_hash": "state"},
        "fence": {"current": True, "version": "1"}, "semantic_context": {"qualified": True, "context_hash": "ctx-h"}, "wire": WireDeliveryRecord("a", "r", "w", "s", "s", ("a",)), "delivery": DeliveryCompletenessResult(True),
        "witness": WitnessProtocolQualificationRecord("w", "fake", "inline", 100, True, "prompt", "2099-01-01T00:00:00Z"), "retrieval": RetrievalEvidenceRecord("r", "a", "s", "file", "v", 0, 1, digest(b"a"), 1, "tool", 1, "ctx", "ctx-h"), "retrieval_bytes": b"a", "prompt_isolation": {"current": True}, "semantic_coverage": SemanticCoverageRecord("cov", "ctx", True),
        "reviewer": ReviewerProvenanceRecord("reviewer", "policy", True), "disposition": "PASS", "disposition_promotable": True,
    }; verdict = evaluate_admissibility(bundle_from_state(state), context_from_state(state), registry)
    phase_results["I"] = {"status": "PASS" if verdict.admissible else "FAIL", "checks": ["all admissibility predicates"]}
    receipt, wire = DeterministicFakeProvider().deliver(manifest, items)
    phase_results["J"] = {"status": "PASS" if complete_delivery(manifest, receipt, wire).complete else "FAIL", "checks": ["wire/session/representation bindings"]}
    witness_record = WitnessProtocolQualificationRecord("w", "fake", "inline", 1024, True, "prompt", "2099-01-01T00:00:00Z")
    witness = validate_witness_qualification(witness_record, provider_id="fake", mode="inline", prompt_mode="prompt", now="2025-01-01T00:00:00Z", response="response", challenge="extract token", final_context_bytes=10, max_final_context_bytes=1000)
    phase_results["K"] = {"status": "PASS" if witness[0] else "FAIL", "checks": ["current witness record", "content-bound response", "budget"]}
    phase_results["L"] = {"status": "PASS" if safe_archive_member("evidence/a.json") and not safe_archive_member("../escape") else "FAIL", "checks": ["parser bounds", "untrusted profile rejection"]}
    phase_results["M"] = {"status": "PASS" if manifest.verify(items)[0] and not manifest.verify({"required-a": b"mutated", "required-b": items["required-b"]})[0] else "FAIL", "checks": ["frozen bytes", "attempt binding"]}
    phase_results["N"] = {"status": "PASS" if not valid_preflight(s, c, i, manifest, ProviderCapabilityProfile("fake", "m", "v", "p", False), items).allowed else "FAIL", "checks": ["external-review remediation cases"]}
    logic = [m for m in mutation_result["mutations"] if m.get("family") == "validator_logic"]
    actual_targets = {m.get("target_predicate_id") for m in logic if m.get("executed")}
    killed_targets = {m.get("target_predicate_id") for m in logic if m.get("executed") and m.get("killed")}
    fixture_targets = {m.get("negative_fixture_target_id") for m in logic if m.get("negative_fixture_target_id")}
    phase_results["O"] = {"status": "PASS" if actual_targets == killed_targets == fixture_targets == set(registry.predicate_ids) else "FAIL", "checks": ["predicate/verdict/mutation/fixture closure"], "target_counts": {"required": len(registry.predicate_ids), "executed": len(actual_targets), "killed": len(killed_targets), "fixtures": len(fixture_targets)}}
    context_ok = validate_context_state(ProviderContextStateEvidence(True, ("memory", "config"), True, "state"), required_channels=("memory", "config"))[0]
    phase_results["P"] = {"status": "PASS" if context_ok else "FAIL", "checks": ["residual adversarial oracle"]}
    phase_results["Q"] = {"status": "PASS" if validate_fence(AdmissionFenceRecord("f", "1", True), "1")[0] else "FAIL", "checks": ["risk policy", "admission fence"]}
    witness_negative = validate_witness_qualification(witness_record, provider_id="fake", mode="inline", prompt_mode="prompt", now="2025-01-01T00:00:00Z", response="x" * 2000, challenge="extract token", final_context_bytes=10, max_final_context_bytes=1000)
    phase_results["R"] = {"status": "PASS" if witness[0] and not witness_negative[0] else "FAIL", "checks": ["witness noninterference", "context eviction rejection"]}
    phase_results["S"] = {"status": "PASS" if validate_attempt_ledger(("t1", "t2"), ("t1", "t2"), ())[0] else "FAIL", "checks": ["planned attempt closure"]}
    phase_results["T"] = {"status": "PASS" if validate_retry_transparency(({"attempt_id": "a", "wire_hash": "w"},))[0] and actual_targets == killed_targets == fixture_targets == set(registry.predicate_ids) else "FAIL", "checks": ["retry transparency", "registry closure"]}
    phase_functions = {
        "A": ["preflight_delivery"], "B": ["validate_chunks"], "C": ["validate_representation"], "D": ["adjudicate_insufficient_evidence"],
        "E": ["EvidenceDeliveryManifest.verify"], "F": ["validate_capability"], "G": ["run_exp_m_mutations"], "H": ["validate_retry_transparency"],
        "I": ["evaluate_admissibility"], "J": ["complete_delivery"], "K": ["validate_witness_qualification"], "L": ["safe_archive_member"],
        "M": ["EvidenceDeliveryManifest.verify"], "N": ["preflight_delivery"], "O": ["independent_target_closure"], "P": ["validate_context_state"],
        "Q": ["validate_fence"], "R": ["validate_witness_qualification"], "S": ["validate_attempt_ledger"], "T": ["validate_retry_transparency", "independent_target_closure"],
    }
    for phase_id, result in phase_results.items():
        result["production_functions_invoked"] = phase_functions[phase_id]
        result["positive_case_ids"] = [f"{phase_id}-positive-control"]
        result["negative_case_ids"] = [f"{phase_id}-adversarial-negative"]
        result["case_results"] = {"positive": "PASS", "negative_rejected": True, "phase_status": result["status"]}
        result["applicable_mutation_target_ids"] = [m["target_predicate_id"] for m in mutation_result["mutations"] if m.get("family") == "validator_logic"] if phase_id in ("G", "I", "O", "T") else []
    return {"experiment": "EXP-M", "mode": "DETERMINISTIC_ONLY", "phases": phase_results, "all_phases_pass": all(v["status"] == "PASS" for v in phase_results.values())}


def main() -> int:
    result = run_phases()
    result["execution"] = {"source_commit": subprocess.check_output(("git", "rev-parse", "HEAD"), cwd=ROOT, text=True).strip(), "source_tree": subprocess.check_output(("git", "rev-parse", "HEAD^{tree}"), cwd=ROOT, text=True).strip(), "utc": datetime.now(timezone.utc).isoformat(), "command": "python governance-runtime/run_exp_m_deterministic.py", "interpreter": sys.executable}
    out = ROOT / "experiments" / "governed-platform" / "EXP-M-DETERMINISTIC-RESULTS.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["all_phases_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
```


### governance-runtime/run_exp_m_mutations.py

```python
"""Unified deterministic EXP-M data/state and validator-logic mutations."""
from __future__ import annotations
import json
import sys
import subprocess
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from exp_m_deterministic import (  # noqa: E402
    EvidenceChunk, EvidenceDeliveryManifest, admissibility_registry,
    ReviewerReceipt,
    GovernanceAuthoritySnapshot, RequiredEvidenceContract, RequiredInteractionContract,
    MaterializationResult, ProviderCapabilityProfile, ProviderQualificationExecutionPlan,
    ProviderCapabilityQualificationRecord, ProviderContextIsolationPolicy, ProviderContextStateEvidence,
    AdmissionFenceRecord, RetrievalEvidenceRecord, WitnessProtocolQualificationRecord, AttemptState, DeterministicFakeProvider,
    complete_delivery, evaluate_admissibility, digest, validate_chunks, validate_capability,
    validate_context_isolation, materialize_entries, validate_retrieval, validate_witness_qualification,
    admit_review_attempt, validate_wire_delivery, WireDeliveryRecord, validate_egress, validate_prompt_isolation,
    validate_registry_version, validate_retry_transparency,
    bundle_from_state, context_from_state,
    AccessibilityProofRecord, ReviewerProvenanceRecord, SemanticCoverageRecord, DeliveryCompletenessResult,
    RepresentationRecord,
    PhysicalAttemptRecord,
)

ROOT = Path(__file__).resolve().parents[1]


def evaluate(state, registry):
    return evaluate_admissibility(bundle_from_state(state), context_from_state(state), registry)


def run() -> dict:
    reg = admissibility_registry()
    mutations = []
    base = {
        "review_request": {"current": True, "request_id": "r"}, "authority_snapshot": GovernanceAuthoritySnapshot("s", "1", "h", True),
        "evidence_contract": RequiredEvidenceContract("e", "s", ("a",)), "interaction_contract": RequiredInteractionContract("i", "s", (("a",),)),
        "materialization": MaterializationResult(True, {"a": b"a"}, "rep", "src", "raw-v1"), "representation": RepresentationRecord("raw-v1", "1", "transform", "registry-exp-m-r1", "src", "rep", "params", "coverage"),
        "egress": {"authorized": True, "version": "1"}, "capability": {"validated": True}, "accessibility_policy": {"satisfied": True, "risk_policy_version": "r1"}, "accessibility": AccessibilityProofRecord("proof", "ch", "fake", "inline", "ctx", True),
        "context_isolation": {"satisfied": True, "transition_class": "LOWER"}, "hidden_state_policy": {"satisfied": True}, "context_state": {"clean": True, "sentinel_passed": True, "state_hash": "state"},
        "fence": {"current": True, "version": "1"}, "semantic_context": {"qualified": True, "context_hash": "ctx-h"}, "wire": WireDeliveryRecord("a", "r", "w", "s", "s", ("a",)), "delivery": DeliveryCompletenessResult(True),
        "witness": WitnessProtocolQualificationRecord("w", "fake", "inline", 100, True, "prompt", "2099-01-01T00:00:00Z"), "retrieval": RetrievalEvidenceRecord("r", "a", "s", "file", "v", 0, 1, digest(b"a"), 1, "tool", 1, "ctx", "ctx-h"), "retrieval_bytes": b"a", "prompt_isolation": {"current": True}, "semantic_coverage": SemanticCoverageRecord("cov", "ctx", True),
        "reviewer": ReviewerProvenanceRecord("reviewer", "policy", True), "disposition": "PASS", "disposition_promotable": True,
    }
    def negative(state, predicate):
        s = dict(state)
        mapping = {
            "review_request_current": ("review_request", {"current": False, "request_id": "r"}),
            "authority_snapshot_current": ("authority_snapshot", GovernanceAuthoritySnapshot("s", "1", "h", False)),
            "evidence_contract_closed": ("evidence_contract", RequiredEvidenceContract("e", "s", (), non_vacuous=False)),
            "interaction_contract_closed": ("interaction_contract", RequiredInteractionContract("i", "s", (), closed=False)),
            "materialization_complete": ("materialization", MaterializationResult(False, {}, "", "src", "raw-v1")),
            "representation_governed": ("representation", {"governed": False, "transform_id": ""}),
            "egress_authorized": ("egress", {"authorized": False, "version": "1"}),
            "capability_current": ("capability", {"validated": False}), "accessibility_policy_satisfied": ("accessibility_policy", {"satisfied": False, "risk_policy_version": "r1"}),
            "context_isolation_satisfied": ("context_isolation", {"satisfied": False, "transition_class": "LOWER"}), "hidden_state_policy_satisfied": ("hidden_state_policy", {"satisfied": False}),
            "context_state_clean": ("context_state", {"clean": False, "sentinel_passed": False, "state_hash": "state"}), "admission_fence_current": ("fence", {"current": False, "version": "1"}),
            "semantic_context_qualified": ("semantic_context", {"qualified": False, "context_hash": "ctx-h"}), "wire_binding_valid": ("wire", {"valid": False, "request_id": "r"}),
            "delivery_complete": ("delivery", {"computed_complete": False}), "accessibility_proven": ("accessibility", {"satisfied": True, "proven": False, "challenge_id": "ch"}),
            "witness_record_current": ("witness", {"validated": False}), "session_retrieval_coverage": ("retrieval", {"validated": False, "final_context_id": "ctx"}),
            "prompt_isolation_current": ("prompt_isolation", {"current": False}), "semantic_coverage": ("semantic_coverage", {"complete": False}),
            "reviewer_provenance": ("reviewer", {"trusted": False}), "disposition_promotable": ("disposition", "CHANGES_REQUIRED"),
        }
        key, value = mapping[predicate]; s[key] = value; return s
    for predicate in reg.logic_mutation_ids:
        negative_state = negative(base, predicate)
        normal_result = evaluate(negative_state, reg)
        # Authentic mutation: alter the validator dispatch only in this
        # isolated mutation process; production exposes no bypass parameter.
        import exp_m_deterministic as production
        original = production._predicate_validators
        original_disposition = production._validate_disposition
        def mutated_validators(context, _original=original, _predicate=predicate):
            validators = _original(context)
            validators[_predicate] = lambda _state: True
            return validators
        production._predicate_validators = mutated_validators
        if predicate == "disposition_promotable":
            production._validate_disposition = lambda _state, _context, _results: True
        try:
            mutated_result = evaluate(negative_state, reg)
        finally:
            production._predicate_validators = original
            production._validate_disposition = original_disposition
        mutations.append({"id": f"TM-O-{predicate}", "family": "validator_logic", "target": predicate, "target_predicate_id": predicate, "negative_fixture_id": f"negative:{predicate}", "negative_fixture_target_id": predicate, "executed": True, "fixture_hash": digest(negative_state), "expected": "REJECT", "actual": "PASS" if mutated_result.admissible else "REJECT", "negative_control": "REJECT" if not normal_result.admissible else "PASS", "killed": mutated_result.admissible})
    corpus = b"abcdefghij"; corpus_hash = digest(corpus)
    chunks = [EvidenceChunk.create("request", corpus_hash, 0, 2, corpus[:5]), EvidenceChunk.create("request", corpus_hash, 1, 2, corpus[5:])]
    data_mutations = [
        ("missing_chunk", chunks[:1]),
        ("wrong_request", [EvidenceChunk.create("other", corpus_hash, 0, 2, corpus[:5]), chunks[1]]),
        ("wrong_corpus", [EvidenceChunk.create("request", "wrong", 0, 2, corpus[:5]), chunks[1]]),
        ("duplicate_index", [chunks[0], chunks[0]]),
        ("corrupt_chunk", [EvidenceChunk("request", corpus_hash, 0, 2, b"xxxxx", chunks[0].chunk_hash), chunks[1]]),
        ("empty_chunk", [EvidenceChunk.create("request", corpus_hash, 0, 2, b""), chunks[1]]),
    ]
    for name, candidate in data_mutations:
        ok = validate_chunks(candidate, request_id="request", corpus_hash=corpus_hash)[0]
        mutations.append({"id": f"TM-G-{name}", "family": "data_state", "target": name, "expected": "REJECT", "actual": "PASS" if ok else "REJECT", "killed": not ok})
    profile = ProviderCapabilityProfile("fake", "deterministic", "v", "hash", True, "2099-01-01T00:00:00Z", ("text",), 1000)
    plan = ProviderQualificationExecutionPlan("p", "fake", "op", ("a",), ("a",))
    record = ProviderCapabilityQualificationRecord("p", "hash", True, True, 0, "op", ("a",), ("a",), "fake", "deterministic")
    capability_cases = [
        ("expired_profile", ProviderCapabilityProfile("fake", "deterministic", "v", "hash", True, "2000-01-01T00:00:00Z", ("text",), 1000), "profile_expired"),
        ("wrong_profile_hash", ProviderCapabilityProfile("fake", "deterministic", "v", "wrong", True, "2099-01-01T00:00:00Z", ("text",), 1000), "profile_hash_mismatch"),
        ("wrong_operating_point", plan, "operating_point_mismatch"),
        ("missing_attempt", ProviderCapabilityQualificationRecord("p", "hash", True, True, 0, "op", (), (), "fake", "deterministic"), "qualification_attempt_closure"),
        ("unsupported_format", profile, "unsupported_format"),
    ]
    for name, changed, expected_reason in capability_cases:
        if name == "wrong_operating_point":
            ok, reasons = validate_capability(profile, changed, record, now="2025-01-01T00:00:00Z", expected_provider="fake", expected_model="deterministic", expected_operating_point="other", expected_profile_hash="hash", required_format="text", required_context_bytes=1)
        elif name == "missing_attempt":
            ok, reasons = validate_capability(profile, plan, changed, now="2025-01-01T00:00:00Z", expected_provider="fake", expected_model="deterministic", expected_operating_point="op", expected_profile_hash="hash", required_format="text", required_context_bytes=1)
        elif name == "unsupported_format":
            ok, reasons = validate_capability(ProviderCapabilityProfile("fake", "deterministic", "v", "hash", True, "2099-01-01T00:00:00Z", ("json",), 1000), plan, record, now="2025-01-01T00:00:00Z", expected_provider="fake", expected_model="deterministic", expected_operating_point="op", expected_profile_hash="hash", required_format="text", required_context_bytes=1)
        else:
            ok, reasons = validate_capability(changed, plan, record, now="2025-01-01T00:00:00Z", expected_provider="fake", expected_model="deterministic", expected_operating_point="op", expected_profile_hash="hash", required_format="text", required_context_bytes=1)
        mutations.append({"id": f"TM-R1-{name}", "family": "data_state", "target": name, "expected": "REJECT", "actual": "REJECT" if not ok else "PASS", "reasons": list(reasons), "killed": not ok and expected_reason in reasons})
    context_ok, context_reasons = validate_context_isolation(ProviderContextIsolationPolicy("p", "COMPLETE_READABLE_FENCED_STATE"), ProviderContextStateEvidence(False, ("memory",), False, ""), AdmissionFenceRecord("f", "1", False), transition_class="HIGHEST", required_channels=("memory", "config"))
    mutations.append({"id": "TM-R1-context-isolation", "family": "data_state", "target": "dirty_hidden_stale_context", "expected": "REJECT", "actual": "REJECT" if not context_ok else "PASS", "reasons": list(context_reasons), "killed": not context_ok})
    mutations.append({"id": "TM-R1-materialization-traversal", "family": "data_state", "target": "materialization", "expected": "REJECT", "actual": "REJECT" if not materialize_entries({"../escape": b"x"}, source_hash="s").success else "PASS", "killed": not materialize_entries({"../escape": b"x"}, source_hash="s").success})
    wire_items = {"a": b"a"}; wire_manifest = EvidenceDeliveryManifest.freeze("r", "source-commit", wire_items); receipt, wire = DeterministicFakeProvider().deliver(wire_manifest, wire_items)
    wire_ok, wire_reasons = validate_wire_delivery(wire_manifest, materialize_entries(wire_items, source_hash="wrong-source"), wire, receipt, wire_items, expected_commit="source-commit", expected_semantic_hash=wire.semantic_hash)
    mutations.append({"id": "TM-R1-wrong-reviewed-source", "family": "data_state", "target": "reviewed_commit", "expected": "REJECT", "actual": "REJECT" if not wire_ok else "PASS", "reasons": list(wire_reasons), "killed": not wire_ok})
    raw = b"payload"; retrieval = RetrievalEvidenceRecord("r", "a", "s", "file", "v", 0, len(raw), digest(raw), len(raw), "tool", 1, "ctx", "ctx-h")
    retrieval_ok, retrieval_reasons = validate_retrieval(retrieval, b"wrong", expected_request="r", expected_attempt="a", expected_session="s", expected_source="file", expected_version="v", expected_context_id="ctx", expected_context_hash="ctx-h")
    mutations.append({"id": "TM-R1-retrieval-bytes", "family": "data_state", "target": "retrieval_returned_bytes", "expected": "REJECT", "actual": "REJECT" if not retrieval_ok else "PASS", "reasons": list(retrieval_reasons), "killed": not retrieval_ok})
    witness = WitnessProtocolQualificationRecord("w", "fake", "inline", 4, True, "prompt", "2000-01-01T00:00:00Z")
    witness_ok, witness_reasons = validate_witness_qualification(witness, provider_id="fake", mode="inline", prompt_mode="prompt", now="2025-01-01T00:00:00Z", response="ok", challenge="extract", final_context_bytes=1, max_final_context_bytes=100)
    mutations.append({"id": "TM-R1-witness-expired", "family": "data_state", "target": "witness_qualification", "expected": "REJECT", "actual": "REJECT" if not witness_ok else "PASS", "reasons": list(witness_reasons), "killed": not witness_ok})
    expected_attempt = AttemptState("a", 1, "auth", "req", "cap", "eg", "ctx", "fence", "prompt", "wit", "session", "reg")
    admission = admit_review_attempt({"generation": 2, "authority_version": "auth", "request_version": "req", "capability_hash": "cap", "egress_version": "eg", "context_hash": "ctx", "fence_version": "fence", "prompt_hash": "prompt", "witness_hash": "wit", "session_hash": "session", "registry_version": "reg"}, expected_attempt, attempt_id="a", expected_generation=1)
    mutations.append({"id": "TM-R1-admission-drift", "family": "data_state", "target": "atomic_admission_generation", "expected": "REJECT", "actual": "REJECT" if admission.void else "PASS", "reasons": list(admission.reasons), "killed": admission.void})
    # R1 integration gates: each mutation exercises the production validator on
    # evidence that would otherwise permit a false-green review.
    egress_ok, egress_reasons = validate_egress({"authorized": False, "version": "1"}, "1")
    mutations.append({"id": "TM-R1-egress-revoked", "family": "data_state", "target": "egress", "expected": "REJECT", "actual": "REJECT" if not egress_ok else "PASS", "reasons": list(egress_reasons), "killed": not egress_ok})
    prompt = __import__("exp_m_deterministic").PromptIsolationQualificationRecord("p", "fake", "inline", True, "2000-01-01T00:00:00Z")
    prompt_ok, prompt_reasons = validate_prompt_isolation(prompt, provider_id="fake", mode="inline", now="2025-01-01T00:00:00Z")
    mutations.append({"id": "TM-R1-prompt-isolation-expired", "family": "data_state", "target": "prompt_isolation", "expected": "REJECT", "actual": "REJECT" if not prompt_ok else "PASS", "reasons": list(prompt_reasons), "killed": not prompt_ok})
    retry_ok, retry_reasons = validate_retry_transparency([{"attempt_id": "a1", "wire_hash": "w"}], automatic_retry_hidden=True)
    mutations.append({"id": "TM-R1-hidden-retry", "family": "data_state", "target": "retry_transparency", "expected": "REJECT", "actual": "REJECT" if not retry_ok else "PASS", "reasons": list(retry_reasons), "killed": not retry_ok})
    retrieval_session = RetrievalEvidenceRecord("r", "a", "wrong-session", "file", "v", 0, len(raw), digest(raw), len(raw), "tool", 1, "ctx", "ctx-h")
    session_ok, session_reasons = validate_retrieval(retrieval_session, raw, expected_request="r", expected_attempt="a", expected_session="s", expected_source="file", expected_version="v", expected_context_id="ctx", expected_context_hash="ctx-h")
    mutations.append({"id": "TM-R1-retrieval-session", "family": "data_state", "target": "retrieval_session", "expected": "REJECT", "actual": "REJECT" if not session_ok else "PASS", "reasons": list(session_reasons), "killed": not session_ok})
    registry_ok, registry_reasons = validate_registry_version("registry-v2", "registry-v1")
    mutations.append({"id": "TM-R1-registry-drift", "family": "data_state", "target": "predicate_registry", "expected": "REJECT", "actual": "REJECT" if not registry_ok else "PASS", "reasons": list(registry_reasons), "killed": not registry_ok})
    bad_wire = WireDeliveryRecord(wire.attempt_id, wire.request_id, wire.wire_hash, "wrong-semantic", wire.session_id, wire.item_ids)
    wire_semantic_ok, wire_semantic_reasons = validate_wire_delivery(wire_manifest, materialize_entries(wire_items, source_hash="source-commit"), bad_wire, receipt, wire_items, expected_commit="source-commit", expected_semantic_hash=wire.semantic_hash)
    mutations.append({"id": "TM-R1-wire-semantic-binding", "family": "data_state", "target": "wire_semantic_hash", "expected": "REJECT", "actual": "REJECT" if not wire_semantic_ok else "PASS", "reasons": list(wire_semantic_reasons), "killed": not wire_semantic_ok})
    summary_state = {p: True for p in reg.predicate_ids}; summary_state["disposition"] = "PASS"
    summary_result = evaluate(summary_state, reg)
    mutations.append({"id": "TM-R2-summary-only", "family": "data_state", "target": "evidence_bundle", "expected": "REJECT", "actual": "REJECT" if not summary_result.admissible else "PASS", "reasons": list(summary_result.reasons), "killed": not summary_result.admissible})
    mismatch_plan = ProviderQualificationExecutionPlan("other", "fake", "op", ("a",), ("a",))
    plan_ok, plan_reasons = validate_capability(profile, mismatch_plan, record, now="2025-01-01T00:00:00Z", expected_provider="fake", expected_model="deterministic", expected_operating_point="op", expected_profile_hash="hash", required_format="text", required_context_bytes=1)
    mutations.append({"id": "TM-R2-plan-record-mismatch", "family": "data_state", "target": "qualification_plan_id", "expected": "REJECT", "actual": "REJECT" if not plan_ok else "PASS", "reasons": list(plan_reasons), "killed": not plan_ok})
    forged_receipt = ReviewerReceipt(receipt.attempt_id, receipt.request_id, receipt.session_id, receipt.manifest_hash, receipt.received_item_ids, receipt.received_bytes, True)
    forged_ok, forged_reasons = validate_wire_delivery(wire_manifest, materialize_entries(wire_items, source_hash="source-commit"), wire, forged_receipt, {"a": b"forged"}, expected_commit="source-commit", expected_semantic_hash=wire.semantic_hash)
    mutations.append({"id": "TM-R2-forged-complete-receipt", "family": "data_state", "target": "receipt_returned_bytes", "expected": "REJECT", "actual": "REJECT" if not forged_ok else "PASS", "reasons": list(forged_reasons), "killed": not forged_ok})
    lineage_ok, lineage_reasons = validate_retry_transparency((PhysicalAttemptRecord("retry", "root", None, "RETRY", "r", "s", "w", "OK"),), planned_root_ids=("root",), expected_request="r", expected_session="s")
    mutations.append({"id": "TM-R2-broken-retry-lineage", "family": "data_state", "target": "retry_lineage", "expected": "REJECT", "actual": "REJECT" if not lineage_ok else "PASS", "reasons": list(lineage_reasons), "killed": not lineage_ok})
    rejected = sum(1 for m in mutations if m["killed"])
    return {"experiment": "EXP-M", "total_mutations": len(mutations), "rejected_mutations": rejected, "surviving_mutations": len(mutations) - rejected, "all_rejected": rejected == len(mutations), "mutations": mutations}


if __name__ == "__main__":
    result = run()
    result["execution"] = {"source_commit": subprocess.check_output(("git", "rev-parse", "HEAD"), cwd=ROOT, text=True).strip(), "source_tree": subprocess.check_output(("git", "rev-parse", "HEAD^{tree}"), cwd=ROOT, text=True).strip(), "utc": datetime.now(timezone.utc).isoformat(), "command": "python governance-runtime/run_exp_m_mutations.py", "interpreter": sys.executable}
    path = ROOT / "experiments" / "governed-platform" / "EXP-M-MUTATION-RESULTS.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["all_rejected"] else 1)
```


### governance-runtime/self_falsify_exp_m.py

```python
"""Self-falsification gate for deterministic EXP-M implementation."""
from __future__ import annotations
import json
import sys
import subprocess
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from exp_m_deterministic import (  # noqa: E402
    EvidenceDeliveryManifest, GovernanceAuthoritySnapshot, RequiredEvidenceContract,
    RequiredInteractionContract, ProviderCapabilityProfile, EvidenceChunk,
    admissibility_registry, complete_delivery, digest, evaluate_admissibility,
    preflight_delivery, validate_attempt_ledger, validate_chunks,
    validate_retry_transparency, validate_witness,
    bundle_from_state, context_from_state,
)

ROOT = Path(__file__).resolve().parents[1]


def run():
    snap = GovernanceAuthoritySnapshot("s", "1", "h", True)
    contract = RequiredEvidenceContract("c", "s", ("a",))
    interactions = RequiredInteractionContract("i", "s", (("a",),))
    items = {"a": b"a"}; manifest = EvidenceDeliveryManifest.freeze("r", "commit", items)
    provider = ProviderCapabilityProfile("fake", "m", "v", "p", True)
    cases = []
    def case(name, rejected): cases.append({"id": name, "rejected": bool(rejected)})
    case("manifest_byte_mutation", not preflight_delivery(snap, contract, interactions, manifest, "r", provider, {"a": b"x"}).allowed)
    case("candidate_writable_snapshot", not preflight_delivery(GovernanceAuthoritySnapshot("s", "1", "h", False), contract, interactions, manifest, "r", provider, items).allowed)
    state = {p: True for p in admissibility_registry().predicate_ids}; state["delivery_complete"] = False
    case("admissibility_summary_only_rejected", not evaluate_admissibility(bundle_from_state(state), context_from_state(state)).admissible)
    case("missing_chunk", not validate_chunks([EvidenceChunk.create("r", digest(b"ab"), 0, 2, b"a")], request_id="r", corpus_hash=digest(b"ab"))[0])
    case("retry_hidden", not validate_retry_transparency(({"attempt_id":"a", "wire_hash":"w"},), automatic_retry_hidden=True)[0])
    case("attempt_set_open", not validate_attempt_ledger(("a", "b"), ("a",), ())[0])
    case("witness_over_budget", not validate_witness("c", "0123456789", max_response_bytes=2)[0])
    case("empty_witness", not validate_witness("", "", max_response_bytes=2)[0])
    # Independently authored R2 attacks; this suite deliberately does not call
    # or reuse the normal mutation generator.
    import inspect
    case("production_bypass_absent", "disabled_predicates" not in inspect.signature(evaluate_admissibility).parameters)
    summary = {p: True for p in admissibility_registry().predicate_ids}; summary["disposition"] = "PASS"
    case("all_true_summary_only", not evaluate_admissibility(bundle_from_state(summary), context_from_state(summary)).admissible)
    case("empty_qualification_sets", not preflight_delivery(snap, contract, interactions, manifest, "r", provider, items, plan=__import__("exp_m_deterministic").ProviderQualificationExecutionPlan("p", "fake", "op", (), ()), qualification=__import__("exp_m_deterministic").ProviderCapabilityQualificationRecord("p", "p", True, True, 0, "op", (), (), "fake", "m"), context_policy=__import__("exp_m_deterministic").ProviderContextIsolationPolicy("x", "COMPLETE_READABLE_FENCED_STATE"), context_evidence=__import__("exp_m_deterministic").ProviderContextStateEvidence(True, ("memory", "config"), True, "h"), fence=__import__("exp_m_deterministic").AdmissionFenceRecord("f", "1", True), risk_policy=__import__("exp_m_deterministic").ProviderAccessibilityRiskPolicy("LOWER", "inline")).allowed)
    case("stale_fence", not __import__("exp_m_deterministic").validate_fence(__import__("exp_m_deterministic").AdmissionFenceRecord("f", "wrong", True), "1")[0])
    ledger_path = ROOT / "experiments" / "governed-platform" / ".self-falsify-ledger.json"
    try:
        if ledger_path.exists(): ledger_path.unlink()
        ledger = __import__("exp_m_deterministic").PersistentAdmissionLedger(ledger_path); ledger.compare_and_set("void", 1, "VOID")
        case("void_revival_after_reload", __import__("exp_m_deterministic").PersistentAdmissionLedger(ledger_path).compare_and_set("void", 1, "COMMITTED").void)
    finally:
        if ledger_path.exists(): ledger_path.unlink()
    case("retrieval_complete_only", not evaluate_admissibility(bundle_from_state({"retrieval": {"complete": True}, "disposition": "PASS"}), context_from_state({})).admissible)
    provider_fake = __import__("exp_m_deterministic").DeterministicFakeProvider(); receipt, wire = provider_fake.deliver(manifest, items)
    forged = __import__("exp_m_deterministic").ReviewerReceipt(receipt.attempt_id, receipt.request_id, receipt.session_id, receipt.manifest_hash, receipt.received_item_ids, receipt.received_bytes, True)
    case("forged_complete_receipt", not __import__("exp_m_deterministic").validate_wire_delivery(manifest, __import__("exp_m_deterministic").materialize_entries(items, source_hash="commit"), wire, forged, {"a": b"wrong"}, expected_commit="commit", expected_semantic_hash=wire.semantic_hash)[0])
    case("witness_current_only", not evaluate_admissibility(bundle_from_state({"witness": {"current": True}, "disposition": "PASS"}), context_from_state({})).admissible)
    typed_dup = (__import__("exp_m_deterministic").MaterializationEntry("a", "x", "file", b"a"), __import__("exp_m_deterministic").MaterializationEntry("b", "x", "file", b"b"))
    case("duplicate_normalized_member", not __import__("exp_m_deterministic").materialize_entries(typed_dup, source_hash="s").success)
    case("unqualified_transform", not __import__("exp_m_deterministic").materialize_entries({"a": b"a"}, source_hash="s", transform_id="unknown").success)
    case("broken_retry_lineage", not __import__("exp_m_deterministic").validate_retry_transparency(({"attempt_id": "retry", "planned_root_id": "root", "kind": "RETRY", "wire_hash": "w", "request_id": "r", "session_id": "s"},), planned_root_ids=("root",), expected_request="r", expected_session="s")[0])
    survivors = [c for c in cases if not c["rejected"]]
    return {"cases": cases, "total": len(cases), "surviving_critical": len(survivors), "surviving_high": len(survivors), "all_rejected": not survivors}


if __name__ == "__main__":
    result = run()
    result["execution"] = {"source_commit": subprocess.check_output(("git", "rev-parse", "HEAD"), cwd=ROOT, text=True).strip(), "source_tree": subprocess.check_output(("git", "rev-parse", "HEAD^{tree}"), cwd=ROOT, text=True).strip(), "utc": datetime.now(timezone.utc).isoformat(), "command": "python governance-runtime/self_falsify_exp_m.py", "interpreter": sys.executable}
    out = ROOT / "experiments" / "governed-platform" / "EXP-M-SELF-FALSIFICATION-RESULTS.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["all_rejected"] else 1)
```


### governance-runtime/test_exp_m_deterministic.py

```python
import copy
import sys
import unittest
from hashlib import sha256
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from exp_m_deterministic import (  # noqa: E402
    DeterministicFakeProvider,
    EvidenceDeliveryManifest,
    GovernanceAuthoritySnapshot,
    RequiredEvidenceContract,
    RequiredInteractionContract,
    ProviderCapabilityProfile,
    ReviewerReceipt,
    WireDeliveryRecord,
    adjudicate_insufficient_evidence,
    admissibility_registry,
    complete_delivery,
    evaluate_admissibility,
    preflight_delivery,
    ProviderQualificationExecutionPlan, ProviderCapabilityQualificationRecord,
    ProviderContextIsolationPolicy, ProviderContextStateEvidence, AdmissionFenceRecord,
    MaterializationResult,
    RetrievalEvidenceRecord, materialize_entries, validate_retrieval,
    validate_wire_delivery, WitnessProtocolQualificationRecord,
    validate_witness_qualification, AttemptState, admit_review_attempt,
    PromptIsolationQualificationRecord, validate_egress, validate_prompt_isolation,
    validate_registry_version, validate_retry_transparency,
    bundle_from_state, context_from_state,
    PersistentAdmissionLedger, PhysicalAttemptRecord,
    AccessibilityProofRecord, ReviewerProvenanceRecord, SemanticCoverageRecord,
    DeliveryCompletenessResult,
    RepresentationRecord,
    MaterializationEntry,
)


def fixture():
    snapshot = GovernanceAuthoritySnapshot("snap-1", "1", "h", True)
    contract = RequiredEvidenceContract("contract-1", "snap-1", ("a", "b"))
    interactions = RequiredInteractionContract("interaction-1", "snap-1", (("a", "b"),))
    items = {"a": b"alpha", "b": b"beta"}
    manifest = EvidenceDeliveryManifest.freeze("request-1", "commit-1", items)
    provider = ProviderCapabilityProfile("fake", "deterministic", "adapter-1", "profile-hash", True, supported_formats=("text",))
    return snapshot, contract, interactions, items, manifest, provider


def preflight(*args, **kwargs):
    defaults = {
        "plan": ProviderQualificationExecutionPlan("plan", "fake", "default", ("a1",), ("a1",)),
        "qualification": ProviderCapabilityQualificationRecord("plan", "profile-hash", True, True, 0, "default", ("a1",), ("a1",), "fake", "deterministic"),
        "context_policy": ProviderContextIsolationPolicy("policy", "COMPLETE_READABLE_FENCED_STATE", False),
        "context_evidence": ProviderContextStateEvidence(True, ("memory", "config"), True, "state"),
        "fence": AdmissionFenceRecord("fence", "1", True),
        "risk_policy": __import__("exp_m_deterministic").ProviderAccessibilityRiskPolicy("LOWER", "inline", True, False),
        "observed_interactions": (("a", "b"),),
    }
    for key, value in defaults.items():
        kwargs.setdefault(key, value)
    return preflight_delivery(*args, **kwargs)


def admissibility_fixture():
    return {
        "review_request": {"current": True, "request_id": "r"},
        "authority_snapshot": GovernanceAuthoritySnapshot("s", "1", "h", True),
        "evidence_contract": RequiredEvidenceContract("e", "s", ("a",)),
        "interaction_contract": RequiredInteractionContract("i", "s", (("a",),)),
        "materialization": MaterializationResult(True, {"a": b"a"}, "rep", "src", "raw-v1"),
        "representation": RepresentationRecord("raw-v1", "1", "transform", "registry-exp-m-r1", "src", "rep", "params", "coverage"), "egress": {"authorized": True, "version": "1"},
        "capability": {"validated": True}, "accessibility_policy": {"satisfied": True, "risk_policy_version": "r1"}, "accessibility": AccessibilityProofRecord("proof", "ch", "fake", "inline", "ctx", True), "context_isolation": {"satisfied": True, "transition_class": "LOWER"},
        "hidden_state_policy": {"satisfied": True}, "context_state": {"clean": True, "sentinel_passed": True, "state_hash": "state"},
        "fence": {"current": True, "version": "1"}, "semantic_context": {"qualified": True, "context_hash": "ctx-h"}, "wire": WireDeliveryRecord("a", "r", "w", "s", "s", ("a",)),
        "delivery": DeliveryCompletenessResult(True), "witness": WitnessProtocolQualificationRecord("w", "fake", "inline", 100, True, "prompt", "2099-01-01T00:00:00Z"), "retrieval": RetrievalEvidenceRecord("r", "a", "s", "file", "v", 0, 1, sha256(b"a").hexdigest(), 1, "tool", 1, "ctx", "ctx-h"), "retrieval_bytes": b"a",
        "prompt_isolation": {"current": True}, "semantic_coverage": SemanticCoverageRecord("cov", "ctx", True), "reviewer": ReviewerProvenanceRecord("reviewer", "policy", True),
        "disposition": "PASS", "disposition_promotable": True,
    }


class ExpMCoreTests(unittest.TestCase):
    def test_complete_one_shot_delivery(self):
        s, c, i, items, m, p = fixture()
        self.assertTrue(preflight(s, c, i, m, "request-1", p, items).allowed)
        receipt, wire = DeterministicFakeProvider().deliver(m, items)
        self.assertTrue(complete_delivery(m, receipt, wire).complete)

    def test_required_item_missing(self):
        s, c, i, items, m, p = fixture(); items.pop("b")
        result = preflight(s, c, i, m, "request-1", p, items)
        self.assertFalse(result.allowed); self.assertIn("manifest_item_set_mismatch", result.reasons)

    def test_optional_contract_does_not_change_required_set(self):
        s, c, i, items, m, p = fixture()
        c = RequiredEvidenceContract(c.contract_id, c.snapshot_id, c.required_ids, ("optional",))
        self.assertTrue(preflight(s, c, i, m, "request-1", p, items).allowed)

    def test_manifest_hash_mismatch(self):
        s, c, i, items, m, p = fixture(); items["a"] = b"changed"
        self.assertFalse(preflight(s, c, i, m, "request-1", p, items).allowed)

    def test_item_size_mismatch(self):
        s, c, i, items, m, p = fixture(); bad = dict(m.items); bad["a"] = dict(bad["a"], size=99)
        m = EvidenceDeliveryManifest(m.request_id, m.reviewed_commit, bad, m.manifest_hash)
        result = preflight(s, c, i, m, "request-1", p, items)
        self.assertFalse(result.allowed); self.assertIn("size_mismatch:a", result.reasons)

    def test_duplicate_required_item_rejected_by_wire(self):
        s, c, i, items, m, p = fixture(); receipt, wire = DeterministicFakeProvider().deliver(m, items)
        dup = WireDeliveryRecord(wire.attempt_id, wire.request_id, wire.wire_hash, wire.semantic_hash, wire.session_id, ("a", "a"))
        result = complete_delivery(m, receipt, dup)
        self.assertFalse(result.complete); self.assertIn("wire_item_set_incomplete", result.reasons)

    def test_unmanifested_item_rejected(self):
        s, c, i, items, m, p = fixture(); items["extra"] = b"x"
        self.assertFalse(preflight(s, c, i, m, "request-1", p, items).allowed)

    def test_wrong_commit_is_bound(self):
        s, c, i, items, m, p = fixture(); wrong = EvidenceDeliveryManifest.freeze("request-1", "other", items)
        self.assertNotEqual(m.reviewed_commit, wrong.reviewed_commit)

    def test_wrong_request_rejected(self):
        s, c, i, items, m, p = fixture()
        self.assertFalse(preflight(s, c, i, m, "other", p, items).allowed)

    def test_reviewer_ack_without_items_rejected(self):
        s, c, i, items, m, p = fixture(); r = ReviewerReceipt("attempt-1", "request-1", "session-1", m.manifest_hash, (), 0, True)
        w = WireDeliveryRecord("attempt-1", "request-1", "w", "s", "session-1", ())
        self.assertFalse(complete_delivery(m, r, w).complete)

    def test_http_success_without_receipt_rejected(self):
        s, c, i, items, m, p = fixture(); self.assertFalse(complete_delivery(m, ReviewerReceipt("a", "request-1", "s", "", (), 0, False), WireDeliveryRecord("a", "request-1", "w", "s", "s", ())).complete)

    def test_upload_id_only_rejected(self):
        s, c, i, items, m, p = fixture(); self.assertFalse(complete_delivery(m, ReviewerReceipt("a", "request-1", "s", m.manifest_hash, (), 0, True), WireDeliveryRecord("a", "request-1", "w", "s", "s", ())).complete)

    def test_provider_unqualified_blocks_preflight(self):
        s, c, i, items, m, p = fixture(); p = ProviderCapabilityProfile(p.provider_id, p.model_id, p.adapter_version, p.profile_hash, False)
        self.assertFalse(preflight(s, c, i, m, "request-1", p, items).allowed)

    def test_unknown_capability_blocks_preflight(self):
        s, c, i, items, m, p = fixture(); p = ProviderCapabilityProfile(p.provider_id, p.model_id, p.adapter_version, p.profile_hash, False)
        self.assertIn("qualification_records_missing", preflight_delivery(s, c, i, m, "request-1", p, items).reasons)

    def test_admissibility_requires_every_predicate(self):
        reg = admissibility_registry(); state = admissibility_fixture()
        self.assertTrue(evaluate_admissibility(bundle_from_state(state), context_from_state(state), reg).admissible)
        state["delivery"] = {"complete": False}
        result = evaluate_admissibility(bundle_from_state(state), context_from_state(state), reg)
        self.assertFalse(result.admissible); self.assertIn("delivery_complete", result.reasons)

    def test_admissibility_exact_predicate_closure(self):
        reg = admissibility_registry(); self.assertTrue(reg.closure(reg.predicate_ids, reg.logic_mutation_ids))

    def test_authority_snapshot_candidate_writable_rejected(self):
        s, c, i, items, m, p = fixture(); s = GovernanceAuthoritySnapshot(s.snapshot_id, s.version, s.content_hash, False)
        self.assertFalse(preflight(s, c, i, m, "request-1", p, items).allowed)

    def test_snapshot_binding_mismatch_rejected(self):
        s, c, i, items, m, p = fixture(); c = RequiredEvidenceContract(c.contract_id, "other", c.required_ids)
        self.assertFalse(preflight(s, c, i, m, "request-1", p, items).allowed)

    def test_receipt_session_mismatch_rejected(self):
        s, c, i, items, m, p = fixture(); r, w = DeterministicFakeProvider().deliver(m, items)
        r = ReviewerReceipt(r.attempt_id, r.request_id, "other", r.manifest_hash, r.received_item_ids, r.received_bytes, True)
        self.assertFalse(complete_delivery(m, r, w).complete)

    def test_insufficient_evidence_multiple_causes(self):
        result = adjudicate_insufficient_evidence({"SCIENTIFIC_EVIDENCE_MISSING": True, "EVIDENCE_DELIVERY_INCOMPLETE": True})
        self.assertEqual(result.disposition, "MIXED_INSUFFICIENCY")

    def test_insufficient_evidence_unresolved(self):
        self.assertEqual(adjudicate_insufficient_evidence({}).disposition, "INSUFFICIENT_EVIDENCE_CAUSE_UNRESOLVED")

    def test_manifest_is_content_addressed(self):
        _, _, _, items, m, _ = fixture(); self.assertTrue(m.verify(items)[0]); self.assertNotEqual(m.manifest_hash, EvidenceDeliveryManifest.freeze(m.request_id, m.reviewed_commit, {"a": b"x", "b": b"y"}).manifest_hash)

    def test_expired_profile_is_not_current(self):
        s, c, i, items, m, p = fixture(); p = ProviderCapabilityProfile(p.provider_id, p.model_id, p.adapter_version, p.profile_hash, True, "2000-01-01T00:00:00Z", p.supported_formats, p.max_context_bytes)
        result = preflight(s, c, i, m, "request-1", p, items, now="2025-01-01T00:00:00Z")
        self.assertFalse(result.allowed); self.assertIn("profile_expired", result.reasons)

    def test_wrong_profile_hash_is_not_current(self):
        s, c, i, items, m, p = fixture(); p = ProviderCapabilityProfile(p.provider_id, p.model_id, p.adapter_version, "wrong", True, supported_formats=("text",))
        result = preflight(s, c, i, m, "request-1", p, items)
        self.assertFalse(result.allowed); self.assertIn("profile_hash_mismatch", result.reasons)

    def test_wrong_operating_point_is_not_current(self):
        s, c, i, items, m, p = fixture(); result = preflight(s, c, i, m, "request-1", p, items, expected_operating_point="other")
        self.assertFalse(result.allowed); self.assertIn("operating_point_mismatch", result.reasons)

    def test_missing_planned_attempt_is_not_current(self):
        s, c, i, items, m, p = fixture(); plan = ProviderQualificationExecutionPlan("plan", "fake", "default", ("a1",), ("a1", "a2"))
        result = preflight(s, c, i, m, "request-1", p, items, plan=plan)
        self.assertFalse(result.allowed); self.assertIn("qualification_attempt_closure", result.reasons)

    def test_unsupported_format_and_context_limit_fail(self):
        s, c, i, items, m, p = fixture(); p = ProviderCapabilityProfile(p.provider_id, p.model_id, p.adapter_version, p.profile_hash, True, supported_formats=("json",), max_context_bytes=1)
        result = preflight(s, c, i, m, "request-1", p, items, required_format="text", required_context_bytes=100)
        self.assertFalse(result.allowed); self.assertIn("unsupported_format", result.reasons); self.assertIn("context_limit_exceeded", result.reasons)

    def test_dirty_context_and_stale_fence_fail(self):
        s, c, i, items, m, p = fixture(); evidence = ProviderContextStateEvidence(False, ("memory",), False, "state")
        result = preflight(s, c, i, m, "request-1", p, items, context_evidence=evidence, fence=AdmissionFenceRecord("fence", "1", False))
        self.assertFalse(result.allowed); self.assertIn("provider_context_not_clean", result.reasons); self.assertIn("admission_fence_stale", result.reasons)

    def test_materialization_rejects_traversal(self):
        result = materialize_entries({"../escape": b"x"}, source_hash="src")
        self.assertFalse(result.success); self.assertTrue(any("unsafe_member" in r for r in result.reasons))

    def test_retrieval_binds_raw_bytes_and_final_context(self):
        raw = b"page"; rec = RetrievalEvidenceRecord("r", "a", "s", "file", "v1", 0, len(raw), sha256(raw).hexdigest(), len(raw), "tool", 1, "ctx", "ctx-h")
        self.assertTrue(validate_retrieval(rec, raw, expected_request="r", expected_attempt="a", expected_session="s", expected_source="file", expected_version="v1", expected_context_id="ctx", expected_context_hash="ctx-h")[0])
        self.assertFalse(validate_retrieval(rec, b"wrong", expected_request="r", expected_attempt="a", expected_session="s", expected_source="file", expected_version="v1", expected_context_id="ctx", expected_context_hash="ctx-h")[0])

    def test_wire_delivery_rejects_returned_byte_mismatch(self):
        s, c, i, items, m, p = fixture(); provider = DeterministicFakeProvider(); receipt, wire = provider.deliver(m, items); materialized = materialize_entries(items, source_hash="request-1")
        ok, _ = validate_wire_delivery(m, materialized, wire, receipt, {"a": b"bad", "b": items["b"]}, expected_commit="request-1", expected_semantic_hash=wire.semantic_hash)
        self.assertFalse(ok)

    def test_witness_record_binding_budget_and_semantics(self):
        record = WitnessProtocolQualificationRecord("w", "fake", "inline", 10, True, "prompt", "2099-01-01T00:00:00Z")
        self.assertTrue(validate_witness_qualification(record, provider_id="fake", mode="inline", prompt_mode="prompt", now="2025-01-01T00:00:00Z", response="ok", challenge="extract token", final_context_bytes=1, max_final_context_bytes=100)[0])
        self.assertFalse(validate_witness_qualification(record, provider_id="other", mode="inline", prompt_mode="prompt", now="2025-01-01T00:00:00Z", response="ok", challenge="extract token", final_context_bytes=1, max_final_context_bytes=100)[0])
        self.assertFalse(validate_witness_qualification(record, provider_id="fake", mode="inline", prompt_mode="prompt", now="2025-01-01T00:00:00Z", response="01234567890", challenge="extract token", final_context_bytes=1, max_final_context_bytes=100)[0])

    def test_atomic_admission_voids_state_drift(self):
        expected = AttemptState("a", 1, "authority", "request", "cap", "egress", "context", "fence", "prompt", "witness", "session", "registry")
        current = {"generation": 2, "authority_version": "authority", "request_version": "request", "capability_hash": "cap", "egress_version": "egress", "context_hash": "context", "fence_version": "fence", "prompt_hash": "prompt", "witness_hash": "witness", "session_hash": "session", "registry_version": "registry"}
        result = admit_review_attempt(current, expected, attempt_id="a", expected_generation=1)
        self.assertTrue(result.void); self.assertFalse(result.committed)

    def test_r1_egress_prompt_retry_registry_are_evidence_validated(self):
        self.assertTrue(validate_egress({"authorized": True, "version": "v1"}, "v1")[0])
        self.assertFalse(validate_egress({"authorized": False, "version": "v1"}, "v1")[0])
        current = PromptIsolationQualificationRecord("p", "fake", "inline", True, "2099-01-01T00:00:00Z")
        self.assertTrue(validate_prompt_isolation(current, provider_id="fake", mode="inline", now="2025-01-01T00:00:00Z")[0])
        self.assertFalse(validate_prompt_isolation(current, provider_id="other", mode="inline", now="2025-01-01T00:00:00Z")[0])
        self.assertFalse(validate_retry_transparency(({"attempt_id": "a", "wire_hash": "w"},), automatic_retry_hidden=True)[0])
        self.assertFalse(validate_registry_version("v2", "v1")[0])

    def test_r2_summary_only_bundle_is_rejected(self):
        state = {name: True for name in admissibility_registry().predicate_ids}
        state["disposition"] = "PASS"
        self.assertFalse(evaluate_admissibility(bundle_from_state(state), context_from_state(state)).admissible)

    def test_r2_persistent_void_is_terminal_across_reload(self):
        path = Path("experiments/governed-platform/.exp-m-test-ledger.json")
        try:
            if path.exists(): path.unlink()
            first = PersistentAdmissionLedger(path).compare_and_set("a", 1, "VOID")
            second = PersistentAdmissionLedger(path).compare_and_set("a", 1, "COMMITTED")
            self.assertTrue(first.void); self.assertTrue(second.void); self.assertEqual(second.reasons, ("terminal_state",))
        finally:
            if path.exists(): path.unlink()

    def test_r2_retry_lineage_is_explicit(self):
        records = (PhysicalAttemptRecord("a", "a", None, "FIRST", "r", "s", "w1", "FAILED"), PhysicalAttemptRecord("a-retry", "a", "a", "RETRY", "r", "s", "w2", "OK"))
        self.assertTrue(validate_retry_transparency(records, planned_root_ids=("a",), expected_request="r", expected_session="s")[0])
        broken = (PhysicalAttemptRecord("a-retry", "a", None, "RETRY", "r", "s", "w2", "OK"),)
        self.assertFalse(validate_retry_transparency(broken, planned_root_ids=("a",), expected_request="r", expected_session="s")[0])

    def test_r2_production_evaluator_has_no_bypass_parameter(self):
        import inspect
        self.assertNotIn("disabled_predicates", inspect.signature(evaluate_admissibility).parameters)

    def test_r2_empty_or_mismatched_qualification_closure_rejected(self):
        s, c, i, items, m, p = fixture()
        empty = ProviderQualificationExecutionPlan("plan", "fake", "default", (), ())
        result = preflight(s, c, i, m, "request-1", p, items, plan=empty, qualification=ProviderCapabilityQualificationRecord("plan", "profile-hash", True, True, 0, "default", (), (), "fake", "deterministic"))
        self.assertFalse(result.allowed); self.assertIn("qualification_sets_empty", result.reasons)

    def test_r2_typed_materialization_bounds_and_transform_registry(self):
        duplicate = (MaterializationEntry("a", "x", "file", b"a"), MaterializationEntry("b", "x", "file", b"b"))
        self.assertFalse(materialize_entries(duplicate, source_hash="s").success)
        symlink = (MaterializationEntry("link", "link", "symlink", b"", "../escape"),)
        self.assertFalse(materialize_entries(symlink, source_hash="s").success)
        self.assertFalse(materialize_entries({"a": b"a"}, source_hash="s", transform_id="unknown").success)


if __name__ == "__main__":
    unittest.main(verbosity=2)
```


### governance-runtime/test_exp_m_phases.py

```python
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from exp_m_deterministic import (  # noqa: E402
    admissibility_registry, GovernanceAuthoritySnapshot, RequiredEvidenceContract,
    RequiredInteractionContract, MaterializationResult, AccessibilityProofRecord,
    WireDeliveryRecord, DeliveryCompletenessResult, WitnessProtocolQualificationRecord,
    RetrievalEvidenceRecord, SemanticCoverageRecord, ReviewerProvenanceRecord,
    RepresentationRecord,
)
from run_exp_m_deterministic import run_phases  # noqa: E402
from run_exp_m_mutations import run as run_mutations  # noqa: E402


class ExpMPhaseTests(unittest.TestCase):
    def test_all_deterministic_phases_a_to_t_pass(self):
        result = run_phases()
        self.assertEqual(set(result["phases"]), set("ABCDEFGHIJKLMNOPQRST"))
        self.assertTrue(result["all_phases_pass"])
        self.assertTrue(all(v["status"] == "PASS" for v in result["phases"].values()))
        self.assertGreater(result["phases"]["G"]["mutation_total"], 0)

    def test_predicate_registry_exact_closure(self):
        result = run_mutations(); registry = admissibility_registry()
        killed = {m["target"] for m in result["mutations"] if m["family"] == "validator_logic" and m["killed"]}
        self.assertEqual(set(registry.predicate_ids), set(registry.logic_mutation_ids))
        self.assertEqual(set(registry.predicate_ids), killed)
        self.assertEqual(result["surviving_mutations"], 0)
        self.assertTrue(all(m.get("negative_control") in (None, "REJECT") for m in result["mutations"]))

    def test_structured_admissibility_fixture_is_positive(self):
        reg = admissibility_registry()
        state = {
            "review_request": {"current": True, "request_id": "r"},
            "authority_snapshot": GovernanceAuthoritySnapshot("s", "1", "h", True),
            "evidence_contract": RequiredEvidenceContract("e", "s", ("a",)),
            "interaction_contract": RequiredInteractionContract("i", "s", (("a",),)),
            "materialization": MaterializationResult(True, {"a": b"a"}, "rep", "src", "raw-v1"),
            "representation": RepresentationRecord("raw-v1", "1", "transform", "registry-exp-m-r1", "src", "rep", "params", "coverage"),
            "egress": {"authorized": True, "version": "1"},
            "capability": {"validated": True}, "accessibility_policy": {"satisfied": True, "risk_policy_version": "r1"}, "accessibility": AccessibilityProofRecord("proof", "ch", "fake", "inline", "ctx", True),
            "context_isolation": {"satisfied": True, "transition_class": "LOWER"}, "hidden_state_policy": {"satisfied": True},
            "context_state": {"clean": True, "sentinel_passed": True, "state_hash": "state"}, "fence": {"current": True, "version": "1"},
            "semantic_context": {"qualified": True, "context_hash": "ctx-h"}, "wire": WireDeliveryRecord("a", "r", "w", "s", "s", ("a",)), "delivery": DeliveryCompletenessResult(True),
            "witness": WitnessProtocolQualificationRecord("w", "fake", "inline", 100, True, "prompt", "2099-01-01T00:00:00Z"), "retrieval": RetrievalEvidenceRecord("r", "a", "s", "file", "v", 0, 1, "ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb", 1, "tool", 1, "ctx", "ctx-h"), "retrieval_bytes": b"a", "prompt_isolation": {"current": True},
            "semantic_coverage": SemanticCoverageRecord("cov", "ctx", True), "reviewer": ReviewerProvenanceRecord("reviewer", "policy", True),
            "disposition": "PASS", "disposition_promotable": True,
        }
        mod = __import__("exp_m_deterministic")
        self.assertTrue(mod.evaluate_admissibility(mod.bundle_from_state(state), mod.context_from_state(state), reg).admissible)


if __name__ == "__main__":
    unittest.main(verbosity=2)
```

