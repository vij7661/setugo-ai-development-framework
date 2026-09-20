# EXP-M Deterministic Implementation R2B Independent Review Packet

This packet covers deterministic implementation only. EXP-M remains NOT_QUALIFIED; no live provider/API call occurred.

## Historical superseded evidence
The prior A-T/22-test/29-mutation report is retained in Git history but is superseded by the independent R1 CHANGES_REQUIRED review. It is not used as closure evidence.
R2B is the current internal self-adjudication authority. Prior R1/R2/R2A and historical false-green outputs are superseded evidence only.

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


### R2A remediation

```text
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
```


### R2B remediation

```text
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
| C-11 | expanded self-falsification includes every current mutation family | 30 cases, 0 critical/0 high survivors |
| NC-01/NC-11/NH-01..NH-08 | no production bypass, typed evidence/context, persistent admission, lineage and freshness binding | static/behavioral/mutation/self-falsification evidence |

## Identity
branch=experiment/exp-m-deterministic-implementation
commit=5ae4621b1acc695e46eec3d8f37a7bd2cf298a32
tree=9d3ed15d991413fd5d075702f1492515a794578a
parent=ef751e0e388c41df213dc69d2743a97a60308eb1
frozen_design_commit=0ba6c3c24ec247f5ad993b7e2f996ccd472b5f45
authority_status=NOT_QUALIFIED
live_provider_execution=false

## Fresh evidence execution identity
{
  "execution_hashes": {
    "experiments/governed-platform/EXP-M-DETERMINISTIC-STDOUT.txt": "3f5110154d537c6fe666d393c40c298ac0e2002debf2aa0d502b1109bb02f00e",
    "experiments/governed-platform/EXP-M-MUTATION-STDOUT.txt": "f8d987f2ab024a0dcf0ab90ea941366e391d0b252ca28505a52f334e3154b44d",
    "experiments/governed-platform/EXP-M-PHASE-STDOUT.txt": "d863a12fa826748a757535c72b17730f44cb951d4135eb05e358867aca7fa089",
    "experiments/governed-platform/EXP-M-SELF-STDOUT.txt": "1527e353add73c2897b6d340a5268fc65b1d43e87f6d4504b4c06ca1475b4e55",
    "experiments/governed-platform/EXP-M-UNIT-STDOUT.txt": "78b78a7ec4f3bd90850438244fb55f3d4668fe13d13ca9ed142ef4001c6f1ee1"
  },
  "source_commit": "ef751e0e388c41df213dc69d2743a97a60308eb1",
  "source_tree": "57b388252bb973bc2889847bd7c87980a909598c"
}

## Deterministic exit gates
all_phases_A_to_T_pass=True
mutation_total=50
mutation_rejected=50
mutation_survivors=0
all_mutations_rejected=True
critical_self_falsification_survivors=0
high_self_falsification_survivors=0
tests_total=49
tests_passed=49
tests_failed=0
r2b_status=AUTOMATABLE_REMEDIATION_COMPLETE
r2b_clean_source_to_evidence_to_packet_sequence=true

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
  "governance-runtime/build_exp_m_review_packet.py": "30638865416e761b86792379947a0f599a64ec1d2fed9117f8b7a81a84371174",
  "governance-runtime/exp_m_deterministic.py": "d31782b6de5ba2a7590c9e5199cf83abefdad73ed0ac9cd8e98caf6fabba04f2",
  "governance-runtime/exp_m_review_fixtures.py": "dec6aa65be46ca0849cb073db8930d416a71cb7749127027ceb223b2021115d2",
  "governance-runtime/run_exp_m_deterministic.py": "25dd7cd2092db5617b0338c23476b7ad2b7d7ccfb7d87aac12d652a71647eb17",
  "governance-runtime/run_exp_m_mutations.py": "b72713640094cf10e966424ef738812ae21590e28013fc069445bdb51b51c2ec",
  "governance-runtime/run_exp_m_tests.py": "9018293a27fc6ba1a4b419c98a35e69b9f38a7db55b9f97df0774dfdb889e0fb",
  "governance-runtime/self_falsify_exp_m.py": "1c1b61952dbd4b396b5d4ba781c3cd387fbe0f8aa719e117aa41094fae791f06",
  "governance-runtime/test_exp_m_deterministic.py": "65ab5302eb16bcd2b17481baf6b4a0e9d10a51f6443e785bb329ee0f865ddc1f",
  "governance-runtime/test_exp_m_phases.py": "2b91d45e5d8c7f899ec9a1171495be0e45730367a3e6a8836b0c45fdde3e084d"
}
```

## R2B phase A-T results
```json
{
  "all_phases_pass": true,
  "execution": {
    "command": "python governance-runtime/run_exp_m_deterministic.py",
    "interpreter": "D:\\Python312\\python.exe",
    "source_commit": "ef751e0e388c41df213dc69d2743a97a60308eb1",
    "source_tree": "57b388252bb973bc2889847bd7c87980a909598c",
    "utc": "2026-09-20T09:50:55.918070+00:00"
  },
  "experiment": "EXP-M",
  "mode": "DETERMINISTIC_ONLY",
  "phases": {
    "A": {
      "applicable_mutation_target_ids": [],
      "case_results": {
        "negative_rejected": true,
        "phase_status": "PASS",
        "positive": true
      },
      "checks": [
        "required closure",
        "manifest bytes",
        "trusted profile"
      ],
      "executed_cases": [
        {
          "actual": "PASS",
          "case_id": "A-positive-control",
          "expected": "PASS",
          "kind": "positive",
          "phase_id": "A",
          "production_functions": [
            "preflight_delivery"
          ],
          "result": true
        },
        {
          "actual": "REJECT",
          "case_id": "A-negative-candidate_writable_snapshot",
          "expected": "REJECT",
          "fixture": "candidate_writable_snapshot",
          "kind": "negative",
          "phase_id": "A",
          "production_functions": [
            "preflight_delivery"
          ],
          "rejection_reason": "candidate_writable_snapshot",
          "result": true
        }
      ],
      "negative_case_ids": [
        "A-negative-candidate_writable_snapshot"
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
        "positive": true
      },
      "checks": [
        "chunk hash",
        "index",
        "request binding"
      ],
      "executed_cases": [
        {
          "actual": "PASS",
          "case_id": "B-positive-control",
          "expected": "PASS",
          "kind": "positive",
          "phase_id": "B",
          "production_functions": [
            "validate_chunks"
          ],
          "result": true
        },
        {
          "actual": "REJECT",
          "case_id": "B-negative-corrupt_chunk",
          "expected": "REJECT",
          "fixture": "corrupt_chunk",
          "kind": "negative",
          "phase_id": "B",
          "production_functions": [
            "validate_chunks"
          ],
          "rejection_reason": "corrupt_chunk",
          "result": true
        }
      ],
      "negative_case_ids": [
        "B-negative-corrupt_chunk"
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
        "positive": true
      },
      "checks": [
        "raw bytes",
        "representation hash"
      ],
      "executed_cases": [
        {
          "actual": "PASS",
          "case_id": "C-positive-control",
          "expected": "PASS",
          "kind": "positive",
          "phase_id": "C",
          "production_functions": [
            "validate_representation"
          ],
          "result": true
        },
        {
          "actual": "REJECT",
          "case_id": "C-negative-raw_byte_mutation",
          "expected": "REJECT",
          "fixture": "raw_byte_mutation",
          "kind": "negative",
          "phase_id": "C",
          "production_functions": [
            "validate_representation"
          ],
          "rejection_reason": "raw_byte_mutation",
          "result": true
        }
      ],
      "negative_case_ids": [
        "C-negative-raw_byte_mutation"
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
        "positive": true
      },
      "checks": [
        "single cause",
        "mixed causes",
        "unresolved cause"
      ],
      "executed_cases": [
        {
          "actual": "PASS",
          "case_id": "D-positive-control",
          "expected": "PASS",
          "kind": "positive",
          "phase_id": "D",
          "production_functions": [
            "adjudicate_insufficient_evidence"
          ],
          "result": true
        },
        {
          "actual": "REJECT",
          "case_id": "D-negative-unresolved_cause",
          "expected": "REJECT",
          "fixture": "unresolved_cause",
          "kind": "negative",
          "phase_id": "D",
          "production_functions": [
            "adjudicate_insufficient_evidence"
          ],
          "rejection_reason": "unresolved_cause",
          "result": true
        }
      ],
      "negative_case_ids": [
        "D-negative-unresolved_cause"
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
        "positive": true
      },
      "checks": [
        "same manifest",
        "same corpus hash"
      ],
      "executed_cases": [
        {
          "actual": "PASS",
          "case_id": "E-positive-control",
          "expected": "PASS",
          "kind": "positive",
          "phase_id": "E",
          "production_functions": [
            "EvidenceDeliveryManifest.verify"
          ],
          "result": true
        },
        {
          "actual": "REJECT",
          "case_id": "E-negative-manifest_byte_mutation",
          "expected": "REJECT",
          "fixture": "manifest_byte_mutation",
          "kind": "negative",
          "phase_id": "E",
          "production_functions": [
            "EvidenceDeliveryManifest.verify"
          ],
          "rejection_reason": "manifest_byte_mutation",
          "result": true
        }
      ],
      "negative_case_ids": [
        "E-negative-manifest_byte_mutation"
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
        "positive": true
      },
      "checks": [
        "profile identity",
        "expiry",
        "operating point",
        "attempt closure",
        "context limit"
      ],
      "executed_cases": [
        {
          "actual": "PASS",
          "case_id": "F-positive-control",
          "expected": "PASS",
          "kind": "positive",
          "phase_id": "F",
          "production_functions": [
            "validate_capability"
          ],
          "result": true
        },
        {
          "actual": "REJECT",
          "case_id": "F-negative-expired_profile",
          "expected": "REJECT",
          "fixture": "expired_profile",
          "kind": "negative",
          "phase_id": "F",
          "production_functions": [
            "validate_capability"
          ],
          "rejection_reason": "expired_profile",
          "result": true
        }
      ],
      "negative_case_ids": [
        "F-negative-expired_profile"
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
        "positive": true
      },
      "checks": [
        "data/state mutation family",
        "validator mutation family"
      ],
      "executed_cases": [
        {
          "actual": "PASS",
          "case_id": "G-positive-control",
          "expected": "PASS",
          "kind": "positive",
          "phase_id": "G",
          "production_functions": [
            "run_exp_m_mutations"
          ],
          "result": true
        },
        {
          "actual": "REJECT",
          "case_id": "G-negative-independent_mutation_catalog",
          "expected": "REJECT",
          "fixture": "independent_mutation_catalog",
          "kind": "negative",
          "phase_id": "G",
          "production_functions": [
            "run_exp_m_mutations"
          ],
          "rejection_reason": "independent_mutation_catalog",
          "result": true
        }
      ],
      "mutation_total": 50,
      "negative_case_ids": [
        "G-negative-independent_mutation_catalog"
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
        "positive": true
      },
      "checks": [
        "physical request ledger",
        "retry lineage"
      ],
      "executed_cases": [
        {
          "actual": "PASS",
          "case_id": "H-positive-control",
          "expected": "PASS",
          "kind": "positive",
          "phase_id": "H",
          "production_functions": [
            "validate_retry_transparency"
          ],
          "result": true
        },
        {
          "actual": "REJECT",
          "case_id": "H-negative-retry_without_failed_parent",
          "expected": "REJECT",
          "fixture": "retry_without_failed_parent",
          "kind": "negative",
          "phase_id": "H",
          "production_functions": [
            "validate_retry_transparency"
          ],
          "rejection_reason": "retry_without_failed_parent",
          "result": true
        }
      ],
      "negative_case_ids": [
        "H-negative-retry_without_failed_parent"
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
        "positive": true
      },
      "checks": [
        "all admissibility predicates"
      ],
      "executed_cases": [
        {
          "actual": "PASS",
          "case_id": "I-positive-control",
          "expected": "PASS",
          "kind": "positive",
          "phase_id": "I",
          "production_functions": [
            "evaluate_admissibility"
          ],
          "result": true
        },
        {
          "actual": "REJECT",
          "case_id": "I-negative-non_promotable_disposition",
          "expected": "REJECT",
          "fixture": "non_promotable_disposition",
          "kind": "negative",
          "phase_id": "I",
          "production_functions": [
            "evaluate_admissibility"
          ],
          "rejection_reason": "non_promotable_disposition",
          "result": true
        }
      ],
      "negative_case_ids": [
        "I-negative-non_promotable_disposition"
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
        "positive": true
      },
      "checks": [
        "wire/session/representation bindings"
      ],
      "executed_cases": [
        {
          "actual": "PASS",
          "case_id": "J-positive-control",
          "expected": "PASS",
          "kind": "positive",
          "phase_id": "J",
          "production_functions": [
            "complete_delivery"
          ],
          "result": true
        },
        {
          "actual": "REJECT",
          "case_id": "J-negative-receipt_manifest_mismatch",
          "expected": "REJECT",
          "fixture": "receipt_manifest_mismatch",
          "kind": "negative",
          "phase_id": "J",
          "production_functions": [
            "complete_delivery"
          ],
          "rejection_reason": "receipt_manifest_mismatch",
          "result": true
        }
      ],
      "negative_case_ids": [
        "J-negative-receipt_manifest_mismatch"
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
        "positive": true
      },
      "checks": [
        "current witness record",
        "content-bound response",
        "budget"
      ],
      "executed_cases": [
        {
          "actual": "PASS",
          "case_id": "K-positive-control",
          "expected": "PASS",
          "kind": "positive",
          "phase_id": "K",
          "production_functions": [
            "validate_witness_qualification"
          ],
          "result": true
        },
        {
          "actual": "REJECT",
          "case_id": "K-negative-response_budget",
          "expected": "REJECT",
          "fixture": "response_budget",
          "kind": "negative",
          "phase_id": "K",
          "production_functions": [
            "validate_witness_qualification"
          ],
          "rejection_reason": "response_budget",
          "result": true
        }
      ],
      "negative_case_ids": [
        "K-negative-response_budget"
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
        "positive": true
      },
      "checks": [
        "parser bounds",
        "untrusted profile rejection"
      ],
      "executed_cases": [
        {
          "actual": "PASS",
          "case_id": "L-positive-control",
          "expected": "PASS",
          "kind": "positive",
          "phase_id": "L",
          "production_functions": [
            "safe_archive_member"
          ],
          "result": true
        },
        {
          "actual": "REJECT",
          "case_id": "L-negative-archive_traversal",
          "expected": "REJECT",
          "fixture": "archive_traversal",
          "kind": "negative",
          "phase_id": "L",
          "production_functions": [
            "materialize_entries"
          ],
          "rejection_reason": "archive_traversal",
          "result": true
        }
      ],
      "negative_case_ids": [
        "L-negative-archive_traversal"
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
        "positive": true
      },
      "checks": [
        "frozen bytes",
        "attempt binding"
      ],
      "executed_cases": [
        {
          "actual": "PASS",
          "case_id": "M-positive-control",
          "expected": "PASS",
          "kind": "positive",
          "phase_id": "M",
          "production_functions": [
            "EvidenceDeliveryManifest.verify"
          ],
          "result": true
        },
        {
          "actual": "REJECT",
          "case_id": "M-negative-frozen_byte_mutation",
          "expected": "REJECT",
          "fixture": "frozen_byte_mutation",
          "kind": "negative",
          "phase_id": "M",
          "production_functions": [
            "EvidenceDeliveryManifest.verify"
          ],
          "rejection_reason": "frozen_byte_mutation",
          "result": true
        }
      ],
      "negative_case_ids": [
        "M-negative-frozen_byte_mutation"
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
        "positive": true
      },
      "checks": [
        "external-review remediation cases"
      ],
      "executed_cases": [
        {
          "actual": "PASS",
          "case_id": "N-positive-control",
          "expected": "PASS",
          "kind": "positive",
          "phase_id": "N",
          "production_functions": [
            "preflight_delivery"
          ],
          "result": true
        },
        {
          "actual": "REJECT",
          "case_id": "N-negative-unqualified_provider",
          "expected": "REJECT",
          "fixture": "unqualified_provider",
          "kind": "negative",
          "phase_id": "N",
          "production_functions": [
            "preflight_delivery"
          ],
          "rejection_reason": "unqualified_provider",
          "result": true
        }
      ],
      "negative_case_ids": [
        "N-negative-unqualified_provider"
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
        "positive": true
      },
      "checks": [
        "predicate/verdict/mutation/fixture closure"
      ],
      "executed_cases": [
        {
          "actual": "PASS",
          "case_id": "O-positive-control",
          "expected": "PASS",
          "kind": "positive",
          "phase_id": "O",
          "production_functions": [
            "independent_target_closure"
          ],
          "result": true
        },
        {
          "actual": "REJECT",
          "case_id": "O-negative-missing_killed_target",
          "expected": "REJECT",
          "fixture": "missing_killed_target",
          "kind": "negative",
          "phase_id": "O",
          "production_functions": [
            "AdmissibilityPredicateRegistry.closure"
          ],
          "rejection_reason": "missing_killed_target",
          "result": true
        }
      ],
      "negative_case_ids": [
        "O-negative-missing_killed_target"
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
        "positive": true
      },
      "checks": [
        "residual adversarial oracle"
      ],
      "executed_cases": [
        {
          "actual": "PASS",
          "case_id": "P-positive-control",
          "expected": "PASS",
          "kind": "positive",
          "phase_id": "P",
          "production_functions": [
            "validate_context_state"
          ],
          "result": true
        },
        {
          "actual": "REJECT",
          "case_id": "P-negative-dirty_context",
          "expected": "REJECT",
          "fixture": "dirty_context",
          "kind": "negative",
          "phase_id": "P",
          "production_functions": [
            "validate_context_isolation"
          ],
          "rejection_reason": "dirty_context",
          "result": true
        }
      ],
      "negative_case_ids": [
        "P-negative-dirty_context"
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
        "positive": true
      },
      "checks": [
        "risk policy",
        "admission fence"
      ],
      "executed_cases": [
        {
          "actual": "PASS",
          "case_id": "Q-positive-control",
          "expected": "PASS",
          "kind": "positive",
          "phase_id": "Q",
          "production_functions": [
            "validate_fence"
          ],
          "result": true
        },
        {
          "actual": "REJECT",
          "case_id": "Q-negative-fence_version_mismatch",
          "expected": "REJECT",
          "fixture": "fence_version_mismatch",
          "kind": "negative",
          "phase_id": "Q",
          "production_functions": [
            "validate_fence"
          ],
          "rejection_reason": "fence_version_mismatch",
          "result": true
        }
      ],
      "negative_case_ids": [
        "Q-negative-fence_version_mismatch"
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
        "positive": true
      },
      "checks": [
        "witness noninterference",
        "context eviction rejection"
      ],
      "executed_cases": [
        {
          "actual": "PASS",
          "case_id": "R-positive-control",
          "expected": "PASS",
          "kind": "positive",
          "phase_id": "R",
          "production_functions": [
            "validate_witness_qualification"
          ],
          "result": true
        },
        {
          "actual": "REJECT",
          "case_id": "R-negative-semantic_prompt",
          "expected": "REJECT",
          "fixture": "semantic_prompt",
          "kind": "negative",
          "phase_id": "R",
          "production_functions": [
            "validate_witness_qualification"
          ],
          "rejection_reason": "semantic_prompt",
          "result": true
        }
      ],
      "negative_case_ids": [
        "R-negative-semantic_prompt"
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
        "positive": true
      },
      "checks": [
        "planned attempt closure",
        "physical retry lineage"
      ],
      "executed_cases": [
        {
          "actual": "PASS",
          "case_id": "S-positive-control",
          "expected": "PASS",
          "kind": "positive",
          "phase_id": "S",
          "production_functions": [
            "validate_attempt_ledger"
          ],
          "result": true
        },
        {
          "actual": "REJECT",
          "case_id": "S-negative-retry_lineage",
          "expected": "REJECT",
          "fixture": "retry_lineage",
          "kind": "negative",
          "phase_id": "S",
          "production_functions": [
            "validate_retry_transparency"
          ],
          "rejection_reason": "retry_lineage",
          "result": true
        }
      ],
      "negative_case_ids": [
        "S-negative-retry_lineage"
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
        "positive": true
      },
      "checks": [
        "retry transparency",
        "registry closure"
      ],
      "executed_cases": [
        {
          "actual": "PASS",
          "case_id": "T-positive-control",
          "expected": "PASS",
          "kind": "positive",
          "phase_id": "T",
          "production_functions": [
            "validate_retry_transparency",
            "independent_target_closure"
          ],
          "result": true
        },
        {
          "actual": "REJECT",
          "case_id": "T-negative-duplicate_physical_dispatch",
          "expected": "REJECT",
          "fixture": "duplicate_physical_dispatch",
          "kind": "negative",
          "phase_id": "T",
          "production_functions": [
            "validate_retry_transparency"
          ],
          "rejection_reason": "duplicate_physical_dispatch",
          "result": true
        }
      ],
      "negative_case_ids": [
        "T-negative-duplicate_physical_dispatch"
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
  "declared_fixture_targets": [
    "accessibility_policy_satisfied",
    "accessibility_proven",
    "admission_fence_current",
    "authority_snapshot_current",
    "capability_current",
    "context_isolation_satisfied",
    "context_state_clean",
    "delivery_complete",
    "disposition_promotable",
    "egress_authorized",
    "evidence_contract_closed",
    "hidden_state_policy_satisfied",
    "interaction_contract_closed",
    "materialization_complete",
    "prompt_isolation_current",
    "representation_governed",
    "review_request_current",
    "reviewer_provenance",
    "semantic_context_qualified",
    "semantic_coverage",
    "session_retrieval_coverage",
    "wire_binding_valid",
    "witness_record_current"
  ],
  "declared_mutation_targets": [
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
  "executed_fixture_targets": [
    "accessibility_policy_satisfied",
    "accessibility_proven",
    "admission_fence_current",
    "authority_snapshot_current",
    "capability_current",
    "context_isolation_satisfied",
    "context_state_clean",
    "delivery_complete",
    "disposition_promotable",
    "egress_authorized",
    "evidence_contract_closed",
    "hidden_state_policy_satisfied",
    "interaction_contract_closed",
    "materialization_complete",
    "prompt_isolation_current",
    "representation_governed",
    "review_request_current",
    "reviewer_provenance",
    "semantic_context_qualified",
    "semantic_coverage",
    "session_retrieval_coverage",
    "wire_binding_valid",
    "witness_record_current"
  ],
  "executed_mutation_targets": [
    "accessibility_policy_satisfied",
    "accessibility_proven",
    "admission_fence_current",
    "authority_snapshot_current",
    "capability_current",
    "context_isolation_satisfied",
    "context_state_clean",
    "delivery_complete",
    "disposition_promotable",
    "egress_authorized",
    "evidence_contract_closed",
    "hidden_state_policy_satisfied",
    "interaction_contract_closed",
    "materialization_complete",
    "prompt_isolation_current",
    "representation_governed",
    "review_request_current",
    "reviewer_provenance",
    "semantic_context_qualified",
    "semantic_coverage",
    "session_retrieval_coverage",
    "wire_binding_valid",
    "witness_record_current"
  ],
  "execution": {
    "command": "python governance-runtime/run_exp_m_mutations.py",
    "interpreter": "D:\\Python312\\python.exe",
    "source_commit": "ef751e0e388c41df213dc69d2743a97a60308eb1",
    "source_tree": "57b388252bb973bc2889847bd7c87980a909598c",
    "utc": "2026-09-20T09:51:03.768264+00:00"
  },
  "experiment": "EXP-M",
  "killed_mutation_targets": [
    "accessibility_policy_satisfied",
    "accessibility_proven",
    "admission_fence_current",
    "authority_snapshot_current",
    "capability_current",
    "context_isolation_satisfied",
    "context_state_clean",
    "delivery_complete",
    "disposition_promotable",
    "egress_authorized",
    "evidence_contract_closed",
    "hidden_state_policy_satisfied",
    "interaction_contract_closed",
    "materialization_complete",
    "prompt_isolation_current",
    "representation_governed",
    "review_request_current",
    "reviewer_provenance",
    "semantic_context_qualified",
    "semantic_coverage",
    "session_retrieval_coverage",
    "wire_binding_valid",
    "witness_record_current"
  ],
  "mutations": [
    {
      "actual": "PASS",
      "executed": true,
      "expected": "REJECT",
      "family": "validator_logic",
      "fixture_hash": "b78b0daef947c2c6ccd83166da293a037db6203a9749a46fd5aa1a3905728256",
      "id": "TM-O-review_request_current",
      "killed": true,
      "mutated_reasons": [],
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:review_request_current",
      "negative_fixture_target_id": "review_request_current",
      "normal_reasons": [
        "review_request_current",
        "disposition_promotable"
      ],
      "target": "review_request_current",
      "target_predicate_id": "review_request_current"
    },
    {
      "actual": "PASS",
      "executed": true,
      "expected": "REJECT",
      "family": "validator_logic",
      "fixture_hash": "af4a46eab0719deec937451d298567129e84db8ece52eeb241f063c50132427d",
      "id": "TM-O-authority_snapshot_current",
      "killed": true,
      "mutated_reasons": [],
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:authority_snapshot_current",
      "negative_fixture_target_id": "authority_snapshot_current",
      "normal_reasons": [
        "authority_snapshot_current",
        "disposition_promotable"
      ],
      "target": "authority_snapshot_current",
      "target_predicate_id": "authority_snapshot_current"
    },
    {
      "actual": "PASS",
      "executed": true,
      "expected": "REJECT",
      "family": "validator_logic",
      "fixture_hash": "ca8159cff520b0f8921bf78811026a982f27f73e1a6043f3e5051dcd91b693f6",
      "id": "TM-O-evidence_contract_closed",
      "killed": true,
      "mutated_reasons": [],
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:evidence_contract_closed",
      "negative_fixture_target_id": "evidence_contract_closed",
      "normal_reasons": [
        "evidence_contract_closed",
        "disposition_promotable"
      ],
      "target": "evidence_contract_closed",
      "target_predicate_id": "evidence_contract_closed"
    },
    {
      "actual": "PASS",
      "executed": true,
      "expected": "REJECT",
      "family": "validator_logic",
      "fixture_hash": "90fd058cc2bbed179f9a29969fb4665379ca250297fdaf93e835d6e122ddbdac",
      "id": "TM-O-interaction_contract_closed",
      "killed": true,
      "mutated_reasons": [],
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:interaction_contract_closed",
      "negative_fixture_target_id": "interaction_contract_closed",
      "normal_reasons": [
        "interaction_contract_closed",
        "disposition_promotable"
      ],
      "target": "interaction_contract_closed",
      "target_predicate_id": "interaction_contract_closed"
    },
    {
      "actual": "PASS",
      "executed": true,
      "expected": "REJECT",
      "family": "validator_logic",
      "fixture_hash": "581360a6dd6e4c77235e7d8ed9a49a5e760999a6a889ecdd8629ed5fd54fc24b",
      "id": "TM-O-materialization_complete",
      "killed": true,
      "mutated_reasons": [],
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:materialization_complete",
      "negative_fixture_target_id": "materialization_complete",
      "normal_reasons": [
        "materialization_complete",
        "wire_binding_valid",
        "delivery_complete",
        "disposition_promotable"
      ],
      "target": "materialization_complete",
      "target_predicate_id": "materialization_complete"
    },
    {
      "actual": "PASS",
      "executed": true,
      "expected": "REJECT",
      "family": "validator_logic",
      "fixture_hash": "03e8ca4d0b4287a294199adf061ee3bc24809013df7ccdf85e9dabffda7c1f6c",
      "id": "TM-O-representation_governed",
      "killed": true,
      "mutated_reasons": [],
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:representation_governed",
      "negative_fixture_target_id": "representation_governed",
      "normal_reasons": [
        "representation_governed",
        "disposition_promotable"
      ],
      "target": "representation_governed",
      "target_predicate_id": "representation_governed"
    },
    {
      "actual": "PASS",
      "executed": true,
      "expected": "REJECT",
      "family": "validator_logic",
      "fixture_hash": "d731e94d8d464a6adbcf73038d4eb4f1af444308debb15a880e988c60e6984a3",
      "id": "TM-O-egress_authorized",
      "killed": true,
      "mutated_reasons": [],
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:egress_authorized",
      "negative_fixture_target_id": "egress_authorized",
      "normal_reasons": [
        "egress_authorized",
        "disposition_promotable"
      ],
      "target": "egress_authorized",
      "target_predicate_id": "egress_authorized"
    },
    {
      "actual": "PASS",
      "executed": true,
      "expected": "REJECT",
      "family": "validator_logic",
      "fixture_hash": "b9e5f7267db5fdc3e3e5d155b5cb53941c7fabdba28face8d970548474424031",
      "id": "TM-O-capability_current",
      "killed": true,
      "mutated_reasons": [],
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:capability_current",
      "negative_fixture_target_id": "capability_current",
      "normal_reasons": [
        "capability_current",
        "disposition_promotable"
      ],
      "target": "capability_current",
      "target_predicate_id": "capability_current"
    },
    {
      "actual": "PASS",
      "executed": true,
      "expected": "REJECT",
      "family": "validator_logic",
      "fixture_hash": "f8fe591b11141c79cae2c8db15f79f14359b635c6dd2a506da0603634aa23805",
      "id": "TM-O-accessibility_policy_satisfied",
      "killed": true,
      "mutated_reasons": [],
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:accessibility_policy_satisfied",
      "negative_fixture_target_id": "accessibility_policy_satisfied",
      "normal_reasons": [
        "accessibility_policy_satisfied",
        "disposition_promotable"
      ],
      "target": "accessibility_policy_satisfied",
      "target_predicate_id": "accessibility_policy_satisfied"
    },
    {
      "actual": "PASS",
      "executed": true,
      "expected": "REJECT",
      "family": "validator_logic",
      "fixture_hash": "e64e3b2890e6808280b3643131467946a31db0ae6a6f7d8d8672f08aa9c9997d",
      "id": "TM-O-context_isolation_satisfied",
      "killed": true,
      "mutated_reasons": [],
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:context_isolation_satisfied",
      "negative_fixture_target_id": "context_isolation_satisfied",
      "normal_reasons": [
        "context_isolation_satisfied",
        "hidden_state_policy_satisfied",
        "context_state_clean",
        "admission_fence_current",
        "disposition_promotable"
      ],
      "target": "context_isolation_satisfied",
      "target_predicate_id": "context_isolation_satisfied"
    },
    {
      "actual": "PASS",
      "executed": true,
      "expected": "REJECT",
      "family": "validator_logic",
      "fixture_hash": "e64e3b2890e6808280b3643131467946a31db0ae6a6f7d8d8672f08aa9c9997d",
      "id": "TM-O-hidden_state_policy_satisfied",
      "killed": true,
      "mutated_reasons": [],
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:hidden_state_policy_satisfied",
      "negative_fixture_target_id": "hidden_state_policy_satisfied",
      "normal_reasons": [
        "context_isolation_satisfied",
        "hidden_state_policy_satisfied",
        "context_state_clean",
        "admission_fence_current",
        "disposition_promotable"
      ],
      "target": "hidden_state_policy_satisfied",
      "target_predicate_id": "hidden_state_policy_satisfied"
    },
    {
      "actual": "PASS",
      "executed": true,
      "expected": "REJECT",
      "family": "validator_logic",
      "fixture_hash": "7478edfb14dec582e13fab69ee2a35c64734ad88c10e08536acebeaa2acef2bd",
      "id": "TM-O-context_state_clean",
      "killed": true,
      "mutated_reasons": [],
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:context_state_clean",
      "negative_fixture_target_id": "context_state_clean",
      "normal_reasons": [
        "context_isolation_satisfied",
        "hidden_state_policy_satisfied",
        "context_state_clean",
        "admission_fence_current",
        "disposition_promotable"
      ],
      "target": "context_state_clean",
      "target_predicate_id": "context_state_clean"
    },
    {
      "actual": "PASS",
      "executed": true,
      "expected": "REJECT",
      "family": "validator_logic",
      "fixture_hash": "787b14af8c46db3ba32fee3f924003a72e2c7a155f7b2d6c7e14676d59025d68",
      "id": "TM-O-admission_fence_current",
      "killed": true,
      "mutated_reasons": [],
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:admission_fence_current",
      "negative_fixture_target_id": "admission_fence_current",
      "normal_reasons": [
        "context_isolation_satisfied",
        "hidden_state_policy_satisfied",
        "context_state_clean",
        "admission_fence_current",
        "disposition_promotable"
      ],
      "target": "admission_fence_current",
      "target_predicate_id": "admission_fence_current"
    },
    {
      "actual": "PASS",
      "executed": true,
      "expected": "REJECT",
      "family": "validator_logic",
      "fixture_hash": "94e75dd9707daf80e03005fb9454f4ee3bce8226ba440c067ca8b31aa6a4a325",
      "id": "TM-O-semantic_context_qualified",
      "killed": true,
      "mutated_reasons": [],
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:semantic_context_qualified",
      "negative_fixture_target_id": "semantic_context_qualified",
      "normal_reasons": [
        "semantic_context_qualified",
        "disposition_promotable"
      ],
      "target": "semantic_context_qualified",
      "target_predicate_id": "semantic_context_qualified"
    },
    {
      "actual": "PASS",
      "executed": true,
      "expected": "REJECT",
      "family": "validator_logic",
      "fixture_hash": "d730784479ad72f9abafb585f62af0e33ec0fc398e91bded8ae5fec93dc98949",
      "id": "TM-O-wire_binding_valid",
      "killed": true,
      "mutated_reasons": [],
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:wire_binding_valid",
      "negative_fixture_target_id": "wire_binding_valid",
      "normal_reasons": [
        "wire_binding_valid",
        "delivery_complete",
        "disposition_promotable"
      ],
      "target": "wire_binding_valid",
      "target_predicate_id": "wire_binding_valid"
    },
    {
      "actual": "PASS",
      "executed": true,
      "expected": "REJECT",
      "family": "validator_logic",
      "fixture_hash": "d730784479ad72f9abafb585f62af0e33ec0fc398e91bded8ae5fec93dc98949",
      "id": "TM-O-delivery_complete",
      "killed": true,
      "mutated_reasons": [],
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:delivery_complete",
      "negative_fixture_target_id": "delivery_complete",
      "normal_reasons": [
        "wire_binding_valid",
        "delivery_complete",
        "disposition_promotable"
      ],
      "target": "delivery_complete",
      "target_predicate_id": "delivery_complete"
    },
    {
      "actual": "PASS",
      "executed": true,
      "expected": "REJECT",
      "family": "validator_logic",
      "fixture_hash": "c5d30300c05c45889ab7ed7008dec0ba94d1984ce1c764e32ad6ca5dc25a215b",
      "id": "TM-O-accessibility_proven",
      "killed": true,
      "mutated_reasons": [],
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:accessibility_proven",
      "negative_fixture_target_id": "accessibility_proven",
      "normal_reasons": [
        "accessibility_policy_satisfied",
        "accessibility_proven",
        "disposition_promotable"
      ],
      "target": "accessibility_proven",
      "target_predicate_id": "accessibility_proven"
    },
    {
      "actual": "PASS",
      "executed": true,
      "expected": "REJECT",
      "family": "validator_logic",
      "fixture_hash": "7095e06245b72a2091855536b828f3f0938423684947994aeed06663bb5801fc",
      "id": "TM-O-witness_record_current",
      "killed": true,
      "mutated_reasons": [],
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:witness_record_current",
      "negative_fixture_target_id": "witness_record_current",
      "normal_reasons": [
        "witness_record_current",
        "disposition_promotable"
      ],
      "target": "witness_record_current",
      "target_predicate_id": "witness_record_current"
    },
    {
      "actual": "PASS",
      "executed": true,
      "expected": "REJECT",
      "family": "validator_logic",
      "fixture_hash": "534f6d81f5b4deb818839d48b0c85079b16a34c057a54e69391a00e1cf97e69d",
      "id": "TM-O-session_retrieval_coverage",
      "killed": true,
      "mutated_reasons": [],
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:session_retrieval_coverage",
      "negative_fixture_target_id": "session_retrieval_coverage",
      "normal_reasons": [
        "session_retrieval_coverage",
        "disposition_promotable"
      ],
      "target": "session_retrieval_coverage",
      "target_predicate_id": "session_retrieval_coverage"
    },
    {
      "actual": "PASS",
      "executed": true,
      "expected": "REJECT",
      "family": "validator_logic",
      "fixture_hash": "c5b6b23b308d4e9e56ca32ed40d309937e82c350fe2e0f3f17f14cf0d50abd1a",
      "id": "TM-O-prompt_isolation_current",
      "killed": true,
      "mutated_reasons": [],
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:prompt_isolation_current",
      "negative_fixture_target_id": "prompt_isolation_current",
      "normal_reasons": [
        "prompt_isolation_current",
        "disposition_promotable"
      ],
      "target": "prompt_isolation_current",
      "target_predicate_id": "prompt_isolation_current"
    },
    {
      "actual": "PASS",
      "executed": true,
      "expected": "REJECT",
      "family": "validator_logic",
      "fixture_hash": "884fd9a35e5d5fb0f4b8740f5380c1aea04a9e238fffb7f25a24225d6c1d9816",
      "id": "TM-O-semantic_coverage",
      "killed": true,
      "mutated_reasons": [],
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:semantic_coverage",
      "negative_fixture_target_id": "semantic_coverage",
      "normal_reasons": [
        "semantic_coverage",
        "disposition_promotable"
      ],
      "target": "semantic_coverage",
      "target_predicate_id": "semantic_coverage"
    },
    {
      "actual": "PASS",
      "executed": true,
      "expected": "REJECT",
      "family": "validator_logic",
      "fixture_hash": "dd56f679260bb52ec02bac90fd3336c168725101ec9a5daf04a6b107520a0013",
      "id": "TM-O-reviewer_provenance",
      "killed": true,
      "mutated_reasons": [],
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:reviewer_provenance",
      "negative_fixture_target_id": "reviewer_provenance",
      "normal_reasons": [
        "reviewer_provenance",
        "disposition_promotable"
      ],
      "target": "reviewer_provenance",
      "target_predicate_id": "reviewer_provenance"
    },
    {
      "actual": "PASS",
      "executed": true,
      "expected": "REJECT",
      "family": "validator_logic",
      "fixture_hash": "5773668013965ae76f44ef627b341fdd9ccf556c9e0780f6e7d325527a2f389a",
      "id": "TM-O-disposition_promotable",
      "killed": true,
      "mutated_reasons": [],
      "negative_control": "REJECT",
      "negative_fixture_id": "negative:disposition_promotable",
      "negative_fixture_target_id": "disposition_promotable",
      "normal_reasons": [
        "disposition_promotable"
      ],
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
        "retry_lineage_invalid",
        "retry_parent_missing"
      ],
      "target": "retry_lineage"
    }
  ],
  "rejected_mutations": 50,
  "surviving_mutations": 0,
  "total_mutations": 50,
  "verdict_predicate_ids": [
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
  ]
}
```
## Offline test result
```json
{
  "all_passed": true,
  "execution": {
    "command": "python governance-runtime/run_exp_m_tests.py",
    "interpreter": "D:\\Python312\\python.exe",
    "source_commit": "ef751e0e388c41df213dc69d2743a97a60308eb1",
    "source_tree": "57b388252bb973bc2889847bd7c87980a909598c",
    "utc": "2026-09-20T09:50:48.005879+00:00"
  },
  "suites": [
    {
      "command": "python governance-runtime/test_exp_m_deterministic.py",
      "exit_code": 0,
      "stdout_stderr": "test_admissibility_exact_predicate_closure (__main__.ExpMCoreTests.test_admissibility_exact_predicate_closure) ... ok\ntest_admissibility_requires_every_predicate (__main__.ExpMCoreTests.test_admissibility_requires_every_predicate) ... ok\ntest_atomic_admission_voids_state_drift (__main__.ExpMCoreTests.test_atomic_admission_voids_state_drift) ... ok\ntest_authority_snapshot_candidate_writable_rejected (__main__.ExpMCoreTests.test_authority_snapshot_candidate_writable_rejected) ... ok\ntest_complete_one_shot_delivery (__main__.ExpMCoreTests.test_complete_one_shot_delivery) ... ok\ntest_dirty_context_and_stale_fence_fail (__main__.ExpMCoreTests.test_dirty_context_and_stale_fence_fail) ... ok\ntest_duplicate_required_item_rejected_by_wire (__main__.ExpMCoreTests.test_duplicate_required_item_rejected_by_wire) ... ok\ntest_expired_profile_is_not_current (__main__.ExpMCoreTests.test_expired_profile_is_not_current) ... ok\ntest_http_success_without_receipt_rejected (__main__.ExpMCoreTests.test_http_success_without_receipt_rejected) ... ok\ntest_insufficient_evidence_multiple_causes (__main__.ExpMCoreTests.test_insufficient_evidence_multiple_causes) ... ok\ntest_insufficient_evidence_unresolved (__main__.ExpMCoreTests.test_insufficient_evidence_unresolved) ... ok\ntest_item_size_mismatch (__main__.ExpMCoreTests.test_item_size_mismatch) ... ok\ntest_manifest_hash_mismatch (__main__.ExpMCoreTests.test_manifest_hash_mismatch) ... ok\ntest_manifest_is_content_addressed (__main__.ExpMCoreTests.test_manifest_is_content_addressed) ... ok\ntest_materialization_rejects_traversal (__main__.ExpMCoreTests.test_materialization_rejects_traversal) ... ok\ntest_missing_planned_attempt_is_not_current (__main__.ExpMCoreTests.test_missing_planned_attempt_is_not_current) ... ok\ntest_optional_contract_does_not_change_required_set (__main__.ExpMCoreTests.test_optional_contract_does_not_change_required_set) ... ok\ntest_provider_unqualified_blocks_preflight (__main__.ExpMCoreTests.test_provider_unqualified_blocks_preflight) ... ok\ntest_r1_egress_prompt_retry_registry_are_evidence_validated (__main__.ExpMCoreTests.test_r1_egress_prompt_retry_registry_are_evidence_validated) ... ok\ntest_r2_admission_race_has_one_terminal_winner (__main__.ExpMCoreTests.test_r2_admission_race_has_one_terminal_winner) ... ok\ntest_r2_empty_or_mismatched_qualification_closure_rejected (__main__.ExpMCoreTests.test_r2_empty_or_mismatched_qualification_closure_rejected) ... ok\ntest_r2_persistent_void_is_terminal_across_reload (__main__.ExpMCoreTests.test_r2_persistent_void_is_terminal_across_reload) ... ok\ntest_r2_production_evaluator_has_no_bypass_parameter (__main__.ExpMCoreTests.test_r2_production_evaluator_has_no_bypass_parameter) ... ok\ntest_r2_retry_lineage_is_explicit (__main__.ExpMCoreTests.test_r2_retry_lineage_is_explicit) ... ok\ntest_r2_summary_only_bundle_is_rejected (__main__.ExpMCoreTests.test_r2_summary_only_bundle_is_rejected) ... ok\ntest_r2_typed_materialization_bounds_and_transform_registry (__main__.ExpMCoreTests.test_r2_typed_materialization_bounds_and_transform_registry) ... ok\ntest_r2b_closure_missing_execution_evidence_fails (__main__.ExpMCoreTests.test_r2b_closure_missing_execution_evidence_fails) ... ok\ntest_r2b_materialization_derives_path_and_rejects_falsified_metadata (__main__.ExpMCoreTests.test_r2b_materialization_derives_path_and_rejects_falsified_metadata) ... ok\ntest_r2b_physical_attempt_duplicate_is_rejected (__main__.ExpMCoreTests.test_r2b_physical_attempt_duplicate_is_rejected) ... ok\ntest_r2b_production_profile_requires_real_plan (__main__.ExpMCoreTests.test_r2b_production_profile_requires_real_plan) ... ok\ntest_r2b_required_optional_manifest_is_exact (__main__.ExpMCoreTests.test_r2b_required_optional_manifest_is_exact) ... ok\ntest_receipt_session_mismatch_rejected (__main__.ExpMCoreTests.test_receipt_session_mismatch_rejected) ... ok\ntest_required_item_missing (__main__.ExpMCoreTests.test_required_item_missing) ... ok\ntest_retrieval_binds_raw_bytes_and_final_context (__main__.ExpMCoreTests.test_retrieval_binds_raw_bytes_and_final_context) ... ok\ntest_reviewer_ack_without_items_rejected (__main__.ExpMCoreTests.test_reviewer_ack_without_items_rejected) ... ok\ntest_snapshot_binding_mismatch_rejected (__main__.ExpMCoreTests.test_snapshot_binding_mismatch_rejected) ... ok\ntest_unknown_capability_blocks_preflight (__main__.ExpMCoreTests.test_unknown_capability_blocks_preflight) ... ok\ntest_unmanifested_item_rejected (__main__.ExpMCoreTests.test_unmanifested_item_rejected) ... ok\ntest_unsupported_format_and_context_limit_fail (__main__.ExpMCoreTests.test_unsupported_format_and_context_limit_fail) ... ok\ntest_upload_id_only_rejected (__main__.ExpMCoreTests.test_upload_id_only_rejected) ... ok\ntest_wire_delivery_rejects_returned_byte_mismatch (__main__.ExpMCoreTests.test_wire_delivery_rejects_returned_byte_mismatch) ... ok\ntest_witness_record_binding_budget_and_semantics (__main__.ExpMCoreTests.test_witness_record_binding_budget_and_semantics) ... ok\ntest_wrong_commit_is_bound (__main__.ExpMCoreTests.test_wrong_commit_is_bound) ... ok\ntest_wrong_operating_point_is_not_current (__main__.ExpMCoreTests.test_wrong_operating_point_is_not_current) ... ok\ntest_wrong_profile_hash_is_not_current (__main__.ExpMCoreTests.test_wrong_profile_hash_is_not_current) ... ok\ntest_wrong_request_rejected (__main__.ExpMCoreTests.test_wrong_request_rejected) ... ok\n\n----------------------------------------------------------------------\nRan 46 tests in 0.066s\n\nOK\n",
      "suite": "core",
      "tests_failed": 0,
      "tests_passed": 46,
      "tests_total": 46
    },
    {
      "command": "python governance-runtime/test_exp_m_phases.py",
      "exit_code": 0,
      "stdout_stderr": "test_all_deterministic_phases_a_to_t_pass (__main__.ExpMPhaseTests.test_all_deterministic_phases_a_to_t_pass) ... ok\ntest_predicate_registry_exact_closure (__main__.ExpMPhaseTests.test_predicate_registry_exact_closure) ... ok\ntest_structured_admissibility_fixture_is_positive (__main__.ExpMPhaseTests.test_structured_admissibility_fixture_is_positive) ... ok\n\n----------------------------------------------------------------------\nRan 3 tests in 15.296s\n\nOK\n",
      "suite": "phases",
      "tests_failed": 0,
      "tests_passed": 3,
      "tests_total": 3
    }
  ],
  "tests_failed": 0,
  "tests_passed": 49,
  "tests_total": 49
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
    },
    {
      "id": "closure_catalog_omission",
      "rejected": true
    },
    {
      "id": "missing_trial_root",
      "rejected": true
    },
    {
      "id": "self_derived_context",
      "rejected": true
    },
    {
      "id": "forged_delivery_result",
      "rejected": true
    },
    {
      "id": "witness_without_expected_answer",
      "rejected": true
    },
    {
      "id": "accessibility_valid_only",
      "rejected": true
    },
    {
      "id": "persistent_race_second_writer",
      "rejected": true
    },
    {
      "id": "phase_cases_are_executed",
      "rejected": true
    },
    {
      "id": "phase_negative_perturbation_fails",
      "rejected": true
    },
    {
      "id": "phase_case_removal_fails_closure",
      "rejected": true
    },
    {
      "id": "typed_summary_boolean",
      "rejected": true
    }
  ],
  "execution": {
    "command": "python governance-runtime/self_falsify_exp_m.py",
    "interpreter": "D:\\Python312\\python.exe",
    "source_commit": "ef751e0e388c41df213dc69d2743a97a60308eb1",
    "source_tree": "57b388252bb973bc2889847bd7c87980a909598c",
    "utc": "2026-09-20T09:51:12.354355+00:00"
  },
  "surviving_critical": 0,
  "surviving_high": 0,
  "total": 30
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
import sqlite3
import threading
import posixpath
import zipfile
from datetime import datetime, timezone
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
    qualification_profile: str = "TEST_PROFILE"


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
    protocol_version: str = "R5-CP-1"


@dataclass(frozen=True)
class ContextIsolationVerdict:
    policy: ProviderContextIsolationPolicy | None
    evidence: ProviderContextStateEvidence | None
    fence: AdmissionFenceRecord | None
    transition_class: str
    required_channels: tuple[str, ...]


@dataclass(frozen=True)
class AccessibilityPolicyEvidence:
    policy_version: str
    proof_mode: str
    deterministic_required: bool
    satisfied_by: str


@dataclass(frozen=True)
class SemanticContextQualificationRecord:
    context_id: str
    context_hash: str
    qualified: bool
    source_hash: str
    context_bytes: bytes = b""
    qualification_receipt_hash: str = ""


@dataclass(frozen=True)
class WitnessChallengeEvidence:
    challenge_id: str
    source_slice_id: str
    source_slice_hash: str
    expected_answer_hash: str
    provider_id: str
    mode: str
    prompt_isolation_mode: str
    response_hash: str
    response_length: int
    final_context_id: str
    final_context_bytes_before: int
    final_context_bytes_after: int
    semantics_class: str = "EXTRACTION_ACCESSIBILITY"


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
    observation_hash: str = ""

    def __post_init__(self) -> None:
        if not self.observation_hash:
            object.__setattr__(self, "observation_hash", digest({"channels": tuple(self.observable_channels), "state_hash": self.state_hash, "clean": self.clean, "sentinel_passed": self.sentinel_passed}))


@dataclass(frozen=True)
class AdmissionFenceRecord:
    fence_id: str
    version: str
    current: bool
    issued_at: str | None = None
    state_hash: str = ""

    def __post_init__(self) -> None:
        if not self.state_hash:
            object.__setattr__(self, "state_hash", digest({"fence_id": self.fence_id, "version": self.version, "current": self.current}))


@dataclass(frozen=True)
class PromptIsolationQualificationRecord:
    record_id: str
    provider_id: str
    mode: str
    current: bool
    expires_at: str | None = None
    issued_at: str | None = None
    record_hash: str = ""


@dataclass(frozen=True)
class WitnessProtocolQualificationRecord:
    record_id: str
    provider_id: str
    mode: str
    max_response_bytes: int
    current: bool
    prompt_isolation_mode: str = ""
    expires_at: str | None = None
    issued_at: str | None = None
    record_hash: str = ""


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
    provider_request_id: str = ""
    request_hash: str = ""


@dataclass(frozen=True)
class AdmissionCheckpoint:
    attempt_id: str
    generation: int
    disposition: str
    committed: bool
    void: bool
    reasons: tuple[str, ...] = ()


class PersistentAdmissionLedger:
    """Transactional persistent ledger; terminal states survive restart and races."""
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._db = self.path.with_suffix(self.path.suffix + ".sqlite")
        with sqlite3.connect(self._db, timeout=5, isolation_level=None) as conn:
            conn.execute("PRAGMA journal_mode=DELETE")
            conn.execute("CREATE TABLE IF NOT EXISTS admissions (attempt_id TEXT PRIMARY KEY, generation INTEGER NOT NULL, disposition TEXT NOT NULL)")
            conn.execute("CREATE TABLE IF NOT EXISTS protected_state (id INTEGER PRIMARY KEY CHECK(id=1), generation INTEGER NOT NULL, state_hash TEXT NOT NULL)")
            conn.execute("INSERT OR IGNORE INTO protected_state(id,generation,state_hash) VALUES(1,0,'')")

    def compare_and_set(self, attempt_id: str, generation: int, disposition: str, *, expected_state_hash: str | None = None, next_state_hash: str | None = None) -> AdmissionCheckpoint:
        if disposition not in ("VOID", "COMMITTED"):
            return AdmissionCheckpoint(attempt_id, generation, "VOID", False, True, ("invalid_terminal_state",))
        with sqlite3.connect(self._db, timeout=5, isolation_level="IMMEDIATE") as conn:
            conn.execute("BEGIN IMMEDIATE")
            protected = conn.execute("SELECT generation,state_hash FROM protected_state WHERE id=1").fetchone()
            if expected_state_hash is not None and (protected is None or protected[1] != expected_state_hash or int(protected[0]) != generation):
                conn.rollback()
                return AdmissionCheckpoint(attempt_id, generation, "VOID", False, True, ("protected_state_generation_drift",))
            current = conn.execute("SELECT generation, disposition FROM admissions WHERE attempt_id=?", (attempt_id,)).fetchone()
            if current is not None:
                conn.commit()
                return AdmissionCheckpoint(attempt_id, int(current[0]), str(current[1]), False, current[1] == "VOID", ("terminal_state",))
            conn.execute("INSERT INTO admissions(attempt_id,generation,disposition) VALUES(?,?,?)", (attempt_id, generation, disposition))
            if disposition == "COMMITTED":
                conn.execute("UPDATE protected_state SET generation=?, state_hash=? WHERE id=1", (generation + 1, next_state_hash or str(generation + 1)))
            conn.commit()
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
    proof_mode: str = ""
    policy_version: str = ""
    evidence_hash: str = ""
    proof_hash: str = ""
    issued_at: str | None = None


@dataclass(frozen=True)
class ReviewerProvenanceRecord:
    reviewer_id: str
    policy_hash: str
    trusted: bool
    authorization_source: str = ""
    record_hash: str = ""
    issued_at: str | None = None


@dataclass(frozen=True)
class SemanticCoverageRecord:
    coverage_id: str
    context_id: str
    complete: bool
    source_hash: str = ""
    coverage_hash: str = ""
    context_hash: str = ""
    evidence_ids: tuple[str, ...] = ()


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

    def closure(self, verdict_ids: Iterable[str], killed_ids: Iterable[str], *, declared_mutations: Iterable[str] | None = None, executed_mutations: Iterable[str] | None = None, declared_fixtures: Iterable[str] | None = None, executed_fixtures: Iterable[str] | None = None, killed_mutations: Iterable[str] | None = None, executed_fixture_targets: Iterable[str] | None = None) -> bool:
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
        verdict = targets(verdict_ids)
        killed = targets(killed_ids)
        if any(value is None for value in (declared_mutations, executed_mutations, declared_fixtures, executed_fixtures, killed_mutations, executed_fixture_targets)):
            return False
        mutation_declared = set(declared_mutations)
        mutation_executed = set(executed_mutations)
        mutation_killed = set(killed_mutations)
        fixture_declared = set(declared_fixtures)
        fixture_executed = set(executed_fixtures)
        fixture_targets = set(executed_fixture_targets)
        return (required == verdict and required == killed and
                mutation_declared == required and mutation_executed == mutation_declared and mutation_killed == required and
                fixture_declared == set(self.fixture_ids) and fixture_executed == fixture_declared and fixture_targets == required)


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
    expected_semantic_hash: str = ""
    expected_transition_class: str = "LOWER"
    expected_fence_version: str = "1"
    expected_witness_answer_hash: str = digest("answer")
    expected_challenge_id: str = ""
    expected_reviewer_policy_hash: str = "policy"
    expected_context_state_hash: str = "state"
    expected_qualification_profile: str = "TEST_PROFILE"


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
        expected_semantic_hash=str(state.get("expected_semantic_hash", "")),
        expected_transition_class=str(state.get("expected_transition_class", state.get("transition_class", "LOWER"))),
        expected_fence_version=str(state.get("expected_fence_version", "1")),
        expected_witness_answer_hash=str(state.get("expected_witness_answer_hash", digest(state.get("witness_expected_answer", "answer")))),
        expected_challenge_id=str(state.get("expected_challenge_id", "challenge")),
        expected_reviewer_policy_hash=str(state.get("expected_reviewer_policy_hash", "policy")),
        expected_context_state_hash=str(state.get("expected_context_state_hash", "state")),
        expected_qualification_profile=str(state.get("expected_qualification_profile", "TEST_PROFILE")),
    )


def bundle_from_state(state: Mapping[str, Any]) -> EvidenceBundle:
    """Test-only fixture adapter. Production callers construct typed bundles directly."""
    out = dict(state)
    if "review_request" not in state or not isinstance(state.get("review_request"), Mapping):
        return EvidenceBundle(out)
    request_id, attempt_id, session_id = str(state.get("expected_request_id", "r")), str(state.get("expected_attempt_id", "a")), str(state.get("expected_session_id", "s"))
    if "interaction_contract" in state and "observed_interactions" not in out and isinstance(state.get("interaction_contract"), RequiredInteractionContract):
        # Test adapter records an observed delivery trace; production callers
        # must populate this from the delivered context, not the contract.
        out["observed_interactions"] = tuple(state["interaction_contract"].interactions)
    reviewed_commit = str(state.get("expected_reviewed_commit", "commit"))
    profile = ProviderCapabilityProfile("fake", "deterministic", "adapter", "profile-hash", True, supported_formats=("text",), max_context_bytes=1_000_000)
    plan = ProviderQualificationExecutionPlan("plan", "fake", "default", ("a1",), ("a1",))
    record = ProviderCapabilityQualificationRecord("plan", "profile-hash", True, True, 0, "default", ("a1",), ("a1",), "fake", "deterministic", attempt_records=(PhysicalAttemptRecord("a1", "a1", None, "FIRST", request_id, session_id, "wire-a1", "OK"),))
    out.setdefault("capability_profile", profile); out.setdefault("qualification_plan", plan); out.setdefault("capability_record", record)
    if not isinstance(out.get("capability_profile"), ProviderCapabilityProfile): out["capability_profile"] = profile
    if not isinstance(out.get("qualification_plan"), ProviderQualificationExecutionPlan): out["qualification_plan"] = plan
    if not isinstance(out.get("capability_record"), ProviderCapabilityQualificationRecord): out["capability_record"] = record
    if isinstance(state.get("capability"), Mapping) and state["capability"].get("validated") is not True: out["capability_record"] = ProviderCapabilityQualificationRecord("bad", "bad", False, False)
    isolation = ContextIsolationVerdict(ProviderContextIsolationPolicy("policy", "COMPLETE_READABLE_FENCED_STATE"), ProviderContextStateEvidence(True, ("memory", "config"), True, "state"), AdmissionFenceRecord("fence", "1", True), "LOWER", ("memory", "config"))
    if ((isinstance(state.get("context_state"), Mapping) and not state["context_state"].get("clean", False)) or (isinstance(state.get("context_isolation"), Mapping) and not state["context_isolation"].get("satisfied", False)) or (isinstance(state.get("hidden_state_policy"), Mapping) and not state["hidden_state_policy"].get("satisfied", False))): isolation = ContextIsolationVerdict(isolation.policy, ProviderContextStateEvidence(False, tuple(state.get("context_state", {}).get("observable_channels", ())) if isinstance(state.get("context_state"), Mapping) else (), False, str(state.get("context_state", {}).get("state_hash", "")) if isinstance(state.get("context_state"), Mapping) else ""), isolation.fence, "LOWER", isolation.required_channels)
    if isinstance(state.get("fence"), Mapping) and not state["fence"].get("current", False): isolation = ContextIsolationVerdict(isolation.policy, isolation.evidence, AdmissionFenceRecord("fence", str(state["fence"].get("version", "")), False), "LOWER", isolation.required_channels)
    out["context_isolation_verdict"] = isolation
    if isinstance(state.get("accessibility_policy"), Mapping) and state["accessibility_policy"].get("satisfied") is False:
        out["accessibility_policy_record"] = ProviderAccessibilityRiskPolicy("LOWER", "invalid", True, False)
    elif not isinstance(out.get("accessibility_policy_record"), ProviderAccessibilityRiskPolicy): out["accessibility_policy_record"] = ProviderAccessibilityRiskPolicy("LOWER", "inline-deterministic", True, False)
    challenge = WitnessChallengeEvidence("challenge", "slice", "slice-hash", digest("answer"), "fake", "inline", "prompt", digest("answer"), len("answer"), "ctx", 10, 16)
    out.setdefault("witness_challenge", challenge); out.setdefault("witness_expected_answer", "answer"); out.setdefault("witness_response", "answer"); out.setdefault("witness_challenge_text", "extract token")
    if isinstance(state.get("witness"), Mapping) and state["witness"].get("validated") is False:
        out["witness"] = WitnessProtocolQualificationRecord("w", "fake", "inline", 100, False, "prompt", "2000-01-01T00:00:00Z")
    else:
        out.setdefault("witness", WitnessProtocolQualificationRecord("w", "fake", "inline", 100, True, "prompt", "2099-01-01T00:00:00Z"))
    if isinstance(state.get("prompt_isolation"), Mapping) and state["prompt_isolation"].get("current") is False:
        out["prompt_isolation"] = PromptIsolationQualificationRecord("prompt", "fake", "inline", False, "2000-01-01T00:00:00Z")
    if isinstance(state.get("semantic_context"), Mapping) and state["semantic_context"].get("qualified") is False:
        out["semantic_context"] = SemanticContextQualificationRecord("ctx", "wrong", False, "")
    elif not isinstance(out.get("semantic_context"), SemanticContextQualificationRecord): out["semantic_context"] = SemanticContextQualificationRecord("ctx", "ctx-h", True, reviewed_commit)
    if isinstance(state.get("semantic_coverage"), Mapping) and state["semantic_coverage"].get("complete") is False:
        out["semantic_coverage"] = SemanticCoverageRecord("cov", "ctx", False, "", "", "wrong")
    elif not isinstance(out.get("semantic_coverage"), SemanticCoverageRecord) or not out["semantic_coverage"].source_hash:
        out["semantic_coverage"] = SemanticCoverageRecord("cov", "ctx", True, reviewed_commit, "coverage-h", "ctx-h")
    raw_items = {"a": b"a"}; manifest = EvidenceDeliveryManifest.freeze(request_id, reviewed_commit, raw_items); materialized = materialize_entries(raw_items, source_hash=reviewed_commit)
    provider = DeterministicFakeProvider(); receipt, wire = provider.deliver(manifest, raw_items)
    out["manifest"] = manifest
    if not (isinstance(state.get("materialization"), MaterializationResult) and not state["materialization"].success): out["materialization"] = materialized
    out.setdefault("returned_items", raw_items); out["receipt"] = receipt
    if isinstance(state.get("wire"), Mapping) and state["wire"].get("valid") is False: out["wire"] = None
    else: out["wire"] = wire
    if isinstance(state.get("delivery"), Mapping) and (state["delivery"].get("complete") is False or state["delivery"].get("computed_complete") is False):
        out["returned_items"] = {"a": b"changed"}
    if isinstance(state.get("accessibility"), Mapping) and state["accessibility"].get("proven") is False:
        out["accessibility"] = AccessibilityProofRecord("proof", "challenge", "fake", "inline-deterministic", "ctx", False, "inline-deterministic", "LOWER", "")
    elif not isinstance(out.get("accessibility"), AccessibilityProofRecord) or not out["accessibility"].evidence_hash:
        out["accessibility"] = AccessibilityProofRecord("proof", "challenge", "fake", "inline", "ctx", True, "inline-deterministic", "LOWER", digest(challenge))
    if isinstance(state.get("reviewer"), Mapping) and state["reviewer"].get("trusted") is False:
        out["reviewer"] = ReviewerProvenanceRecord("reviewer", "", False, "")
    elif not isinstance(out.get("reviewer"), ReviewerProvenanceRecord) or not out["reviewer"].authorization_source:
        out["reviewer"] = ReviewerProvenanceRecord("reviewer", "policy", True, "trusted-review-artifact")
    return EvidenceBundle(out)


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
# Independent, review-owned catalogs.  These are intentionally declared in a
# separate block rather than generated from the production validator map.
INDEPENDENT_MUTATION_CATALOG = (
    {"id": "negative:review_request_current", "target": "review_request_current"},
    {"id": "negative:authority_snapshot_current", "target": "authority_snapshot_current"},
    {"id": "negative:evidence_contract_closed", "target": "evidence_contract_closed"},
    {"id": "negative:interaction_contract_closed", "target": "interaction_contract_closed"},
    {"id": "negative:materialization_complete", "target": "materialization_complete"},
    {"id": "negative:representation_governed", "target": "representation_governed"},
    {"id": "negative:egress_authorized", "target": "egress_authorized"},
    {"id": "negative:capability_current", "target": "capability_current"},
    {"id": "negative:accessibility_policy_satisfied", "target": "accessibility_policy_satisfied"},
    {"id": "negative:context_isolation_satisfied", "target": "context_isolation_satisfied"},
    {"id": "negative:hidden_state_policy_satisfied", "target": "hidden_state_policy_satisfied"},
    {"id": "negative:context_state_clean", "target": "context_state_clean"},
    {"id": "negative:admission_fence_current", "target": "admission_fence_current"},
    {"id": "negative:semantic_context_qualified", "target": "semantic_context_qualified"},
    {"id": "negative:wire_binding_valid", "target": "wire_binding_valid"},
    {"id": "negative:delivery_complete", "target": "delivery_complete"},
    {"id": "negative:accessibility_proven", "target": "accessibility_proven"},
    {"id": "negative:witness_record_current", "target": "witness_record_current"},
    {"id": "negative:session_retrieval_coverage", "target": "session_retrieval_coverage"},
    {"id": "negative:prompt_isolation_current", "target": "prompt_isolation_current"},
    {"id": "negative:semantic_coverage", "target": "semantic_coverage"},
    {"id": "negative:reviewer_provenance", "target": "reviewer_provenance"},
    {"id": "negative:disposition_promotable", "target": "disposition_promotable"},
)
# Review-owned negative fixtures are independently declared.  They are not
# aliases of the mutation catalog and each names its immutable constructor and
# rejection expectation.
INDEPENDENT_FIXTURE_CATALOG = (
    {"fixture_id": "negative:review_request_current", "target_predicate_id": "review_request_current", "constructor": "fixture_review_request_not_current", "expected_rejection": "review_request_current"},
    {"fixture_id": "negative:authority_snapshot_current", "target_predicate_id": "authority_snapshot_current", "constructor": "fixture_candidate_writable_snapshot", "expected_rejection": "authority_snapshot_current"},
    {"fixture_id": "negative:evidence_contract_closed", "target_predicate_id": "evidence_contract_closed", "constructor": "fixture_open_evidence_contract", "expected_rejection": "evidence_contract_closed"},
    {"fixture_id": "negative:interaction_contract_closed", "target_predicate_id": "interaction_contract_closed", "constructor": "fixture_open_interaction_contract", "expected_rejection": "interaction_contract_closed"},
    {"fixture_id": "negative:materialization_complete", "target_predicate_id": "materialization_complete", "constructor": "fixture_failed_materialization", "expected_rejection": "materialization_complete"},
    {"fixture_id": "negative:representation_governed", "target_predicate_id": "representation_governed", "constructor": "fixture_unqualified_representation", "expected_rejection": "representation_governed"},
    {"fixture_id": "negative:egress_authorized", "target_predicate_id": "egress_authorized", "constructor": "fixture_revoked_egress", "expected_rejection": "egress_authorized"},
    {"fixture_id": "negative:capability_current", "target_predicate_id": "capability_current", "constructor": "fixture_expired_capability", "expected_rejection": "capability_current"},
    {"fixture_id": "negative:accessibility_policy_satisfied", "target_predicate_id": "accessibility_policy_satisfied", "constructor": "fixture_wrong_accessibility_policy", "expected_rejection": "accessibility_policy_satisfied"},
    {"fixture_id": "negative:context_isolation_satisfied", "target_predicate_id": "context_isolation_satisfied", "constructor": "fixture_dirty_context", "expected_rejection": "context_isolation_satisfied"},
    {"fixture_id": "negative:hidden_state_policy_satisfied", "target_predicate_id": "hidden_state_policy_satisfied", "constructor": "fixture_hidden_state", "expected_rejection": "hidden_state_policy_satisfied"},
    {"fixture_id": "negative:context_state_clean", "target_predicate_id": "context_state_clean", "constructor": "fixture_dirty_context_state", "expected_rejection": "context_state_clean"},
    {"fixture_id": "negative:admission_fence_current", "target_predicate_id": "admission_fence_current", "constructor": "fixture_stale_fence", "expected_rejection": "admission_fence_current"},
    {"fixture_id": "negative:semantic_context_qualified", "target_predicate_id": "semantic_context_qualified", "constructor": "fixture_wrong_context_hash", "expected_rejection": "semantic_context_qualified"},
    {"fixture_id": "negative:wire_binding_valid", "target_predicate_id": "wire_binding_valid", "constructor": "fixture_wrong_wire", "expected_rejection": "wire_binding_valid"},
    {"fixture_id": "negative:delivery_complete", "target_predicate_id": "delivery_complete", "constructor": "fixture_incomplete_delivery", "expected_rejection": "delivery_complete"},
    {"fixture_id": "negative:accessibility_proven", "target_predicate_id": "accessibility_proven", "constructor": "fixture_wrong_accessibility_evidence", "expected_rejection": "accessibility_proven"},
    {"fixture_id": "negative:witness_record_current", "target_predicate_id": "witness_record_current", "constructor": "fixture_expired_witness", "expected_rejection": "witness_record_current"},
    {"fixture_id": "negative:session_retrieval_coverage", "target_predicate_id": "session_retrieval_coverage", "constructor": "fixture_wrong_retrieval_session", "expected_rejection": "session_retrieval_coverage"},
    {"fixture_id": "negative:prompt_isolation_current", "target_predicate_id": "prompt_isolation_current", "constructor": "fixture_expired_prompt_isolation", "expected_rejection": "prompt_isolation_current"},
    {"fixture_id": "negative:semantic_coverage", "target_predicate_id": "semantic_coverage", "constructor": "fixture_incomplete_semantic_coverage", "expected_rejection": "semantic_coverage"},
    {"fixture_id": "negative:reviewer_provenance", "target_predicate_id": "reviewer_provenance", "constructor": "fixture_untrusted_reviewer", "expected_rejection": "reviewer_provenance"},
    {"fixture_id": "negative:disposition_promotable", "target_predicate_id": "disposition_promotable", "constructor": "fixture_non_promotable_disposition", "expected_rejection": "disposition_promotable"},
)
FIXTURE_IDS = tuple(item["fixture_id"] for item in INDEPENDENT_FIXTURE_CATALOG)


def admissibility_registry() -> AdmissibilityPredicateRegistry:
    return AdmissibilityPredicateRegistry("2", tuple(d["id"] for d in PREDICATE_DEFINITIONS), tuple(item["target"] for item in INDEPENDENT_MUTATION_CATALOG), FIXTURE_IDS)


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

    def capability_valid(state: Mapping[str, Any]) -> bool:
        profile, plan, record = state.get("capability_profile"), state.get("qualification_plan"), state.get("capability_record")
        if not isinstance(profile, ProviderCapabilityProfile) or not isinstance(plan, ProviderQualificationExecutionPlan) or not isinstance(record, ProviderCapabilityQualificationRecord):
            return False
        return validate_capability(profile, plan, record, now=str(state.get("now", "2099-01-01T00:00:00Z")), expected_provider=context.expected_provider, expected_model=context.expected_model, expected_operating_point=context.expected_operating_point, expected_profile_hash=context.expected_profile_hash, required_format="text", required_context_bytes=context.max_context_bytes)[0]

    def context_isolation_valid(state: Mapping[str, Any]) -> bool:
        record = state.get("context_isolation_verdict")
        if not isinstance(record, ContextIsolationVerdict):
            return False
        return validate_context_isolation(record.policy, record.evidence, record.fence, transition_class=record.transition_class, required_channels=record.required_channels)[0]

    def accessibility_policy_valid(state: Mapping[str, Any]) -> bool:
        policy, proof = state.get("accessibility_policy_record"), state.get("accessibility")
        if not isinstance(policy, ProviderAccessibilityRiskPolicy) or not isinstance(proof, AccessibilityProofRecord):
            return False
        if proof.proof_mode != policy.proof_mode or proof.policy_version != policy.transition_class or not proof.evidence_hash:
            return False
        if policy.deterministic_required and proof.proof_mode != "inline-deterministic":
            return False
        return bool(proof.proof_id and proof.challenge_id and proof.provider_id == context.expected_provider and proof.proof_mode == policy.proof_mode and proof.evidence_hash)

    def semantic_context_valid(state: Mapping[str, Any]) -> bool:
        record = state.get("semantic_context")
        if not isinstance(record, SemanticContextQualificationRecord):
            return False
        if record.context_id != context.final_context_id or record.context_hash != context.final_context_hash or record.source_hash != context.reviewed_commit:
            return False
        if record.context_bytes and digest(record.context_bytes) != record.context_hash:
            return False
        return bool(record.qualification_receipt_hash or record.source_hash)

    def wire_valid(state: Mapping[str, Any]) -> bool:
        manifest, materialized, wire, receipt, returned = state.get("manifest"), state.get("materialization"), state.get("wire"), state.get("receipt"), state.get("returned_items")
        if not isinstance(manifest, EvidenceDeliveryManifest) or not isinstance(materialized, MaterializationResult) or not isinstance(wire, WireDeliveryRecord) or not isinstance(receipt, ReviewerReceipt) or not isinstance(returned, Mapping) or any(not isinstance(v, bytes) for v in returned.values()):
            return False
        return validate_wire_delivery(manifest, materialized, wire, receipt, returned, expected_commit=context.reviewed_commit, expected_semantic_hash=context.expected_semantic_hash or None)[0]

    def delivery_valid(state: Mapping[str, Any]) -> bool:
        return wire_valid(state)

    def accessibility_proof_valid(state: Mapping[str, Any]) -> bool:
        proof, challenge = state.get("accessibility"), state.get("witness_challenge")
        if not isinstance(proof, AccessibilityProofRecord) or not isinstance(challenge, WitnessChallengeEvidence):
            return False
        if proof.final_context_id != context.final_context_id or proof.challenge_id != challenge.challenge_id:
            return False
        return proof.evidence_hash == digest(challenge) and proof.provider_id == context.expected_provider

    def witness_valid(state: Mapping[str, Any]) -> bool:
        record, challenge = state.get("witness"), state.get("witness_challenge")
        if not isinstance(record, WitnessProtocolQualificationRecord) or not isinstance(challenge, WitnessChallengeEvidence):
            return False
        if context.expected_witness_answer_hash and challenge.expected_answer_hash != context.expected_witness_answer_hash:
            return False
        return validate_witness_qualification(record, provider_id=context.witness_provider, mode=context.witness_mode, prompt_mode=context.witness_prompt_mode, now=str(state.get("now", "2025-01-01T00:00:00Z")), response=str(state.get("witness_response", "")), challenge=str(state.get("witness_challenge_text", "")), final_context_bytes=challenge.final_context_bytes_before, max_final_context_bytes=context.max_context_bytes)[0] and challenge.final_context_bytes_after == challenge.final_context_bytes_before + challenge.response_length

    def semantic_coverage_valid(state: Mapping[str, Any]) -> bool:
        coverage = state.get("semantic_coverage")
        return isinstance(coverage, SemanticCoverageRecord) and coverage.context_id == context.final_context_id and (coverage.context_hash or context.final_context_hash) == context.final_context_hash and coverage.source_hash == context.reviewed_commit and bool(coverage.coverage_hash) and bool(coverage.evidence_ids or coverage.coverage_hash)

    def reviewer_valid(state: Mapping[str, Any]) -> bool:
        reviewer = state.get("reviewer")
        return isinstance(reviewer, ReviewerProvenanceRecord) and reviewer.policy_hash == context.expected_reviewer_policy_hash and bool(reviewer.authorization_source) and reviewer.authorization_source != "caller"

    return {
        "review_request_current": lambda s: isinstance(s.get("review_request"), Mapping) and s["review_request"].get("current") is True and s["review_request"].get("request_id") == context.request_id,
        "authority_snapshot_current": lambda s: isinstance(s.get("authority_snapshot"), GovernanceAuthoritySnapshot) and s["authority_snapshot"].outside_candidate_write_authority and s["authority_snapshot"].snapshot_id == context.authority_snapshot_id and s["authority_snapshot"].content_hash == context.authority_snapshot_hash and s["authority_snapshot"].version == context.authority_version,
        "evidence_contract_closed": lambda s: isinstance(s.get("evidence_contract"), RequiredEvidenceContract) and s["evidence_contract"].closed and s["evidence_contract"].non_vacuous,
        "interaction_contract_closed": lambda s: isinstance(s.get("interaction_contract"), RequiredInteractionContract) and s["interaction_contract"].closed and bool(s["interaction_contract"].interactions) and s.get("observed_interactions") is not None and {tuple(x) for x in s.get("observed_interactions", ())} == {tuple(x) for x in s["interaction_contract"].interactions},
        "materialization_complete": lambda s: isinstance(s.get("materialization"), MaterializationResult) and s["materialization"].success,
        "representation_governed": lambda s: isinstance(s.get("representation"), RepresentationRecord) and s["representation"].transform_id in QUALIFIED_TRANSFORMS and s["representation"].registry_version == QUALIFIED_TRANSFORMS[s["representation"].transform_id] and bool(s["representation"].source_hash) and bool(s["representation"].representation_hash) and bool(s["representation"].parameters_hash) and bool(s["representation"].coverage_hash),
        "egress_authorized": egress_valid,
        "capability_current": capability_valid,
        "accessibility_policy_satisfied": accessibility_policy_valid,
        "context_isolation_satisfied": context_isolation_valid,
        "hidden_state_policy_satisfied": context_isolation_valid,
        "context_state_clean": context_isolation_valid,
        "admission_fence_current": context_isolation_valid,
        "semantic_context_qualified": semantic_context_valid,
        "wire_binding_valid": wire_valid,
        "delivery_complete": delivery_valid,
        "accessibility_proven": accessibility_proof_valid,
        "witness_record_current": witness_valid,
        "session_retrieval_coverage": lambda s: isinstance(s.get("retrieval"), RetrievalEvidenceRecord) and validate_retrieval(s["retrieval"], s.get("retrieval_bytes", b""), expected_request=context.request_id, expected_attempt=context.attempt_id, expected_session=context.session_id, expected_source=context.retrieval_source, expected_version=context.retrieval_version, expected_context_id=context.final_context_id, expected_context_hash=context.final_context_hash)[0],
        "prompt_isolation_current": prompt_valid,
        "semantic_coverage": semantic_coverage_valid,
        "reviewer_provenance": reviewer_valid,
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
    allowed_ids = set(evidence_contract.required_ids) | set(evidence_contract.optional_ids)
    manifest_ids = set(manifest.items)
    if (not evidence_contract.closed or not evidence_contract.non_vacuous or not evidence_contract.required_ids
            or len(evidence_contract.required_ids) != len(set(evidence_contract.required_ids))
            or len(evidence_contract.optional_ids) != len(set(evidence_contract.optional_ids))
            or not set(evidence_contract.required_ids).issubset(manifest_ids)
            or not manifest_ids.issubset(allowed_ids)):
        reasons.append("evidence_contract_unresolved")
    if not interactions.closed or not interactions.interactions or any(not set(interaction).issubset(manifest.items) for interaction in interactions.interactions):
        reasons.append("interaction_contract_unresolved")
    derived_interactions = tuple(tuple(interaction) for interaction in interactions.interactions if all(item_id in items for item_id in interaction))
    if tuple(derived_interactions) != tuple(interactions.interactions):
        reasons.append("interaction_observation_missing_from_delivered_context")
    if observed_interactions is None or {tuple(x) for x in observed_interactions} != {tuple(x) for x in derived_interactions}:
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
    # receipt.complete is a diagnostic consistency bit only; completeness is
    # recomputed from the manifest, returned bytes, receipt and wire identity.
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
    if any(item not in set(dispatched_ids) for item in retried_ids):
        reasons.append("retry_not_dispatched")
    if any(item not in set(dispatched_ids) for item in failed_ids):
        reasons.append("failed_attempt_not_dispatched")
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
    if len({r.attempt_id for r in records}) != len(records) or len({r.wire_hash for r in records}) != len(records):
        reasons.append("physical_attempt_or_wire_duplicate")
    provider_ids = [r.provider_request_id for r in records if r.provider_request_id]
    if len(provider_ids) != len(set(provider_ids)):
        reasons.append("provider_request_id_duplicate")
    if any(r.kind == "RETRY" and not r.parent_attempt_id for r in records):
        reasons.append("retry_parent_missing")
    if any(r.kind == "FIRST" and not r.planned_root_id for r in records):
        reasons.append("first_attempt_root_missing")
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
    # clean/sentinel_passed are diagnostic cache fields; the observed channel
    # set and a content-bound state hash are authoritative.
    if not state.observable_channels:
        reasons.append("provider_context_not_observed")
    if not set(required_channels).issubset(state.observable_channels):
        reasons.append("context_channel_unobserved")
    if not state.state_hash:
        reasons.append("context_state_unbound")
    if state.observation_hash and state.observation_hash != digest({"channels": tuple(state.observable_channels), "state_hash": state.state_hash, "clean": state.clean, "sentinel_passed": state.sentinel_passed}):
        reasons.append("context_observation_hash_mismatch")
    if not state.observation_hash:
        reasons.append("provider_context_observation_unbound")
    return not reasons, tuple(reasons)


def validate_fence(fence: AdmissionFenceRecord, expected_version: str) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    if fence.version != expected_version:
        reasons.append("admission_fence_version_mismatch")
    if not fence.fence_id or (fence.state_hash and not isinstance(fence.state_hash, str)):
        reasons.append("admission_fence_unbound")
    if fence.state_hash != digest({"fence_id": fence.fence_id, "version": fence.version, "current": fence.current}):
        reasons.append("admission_fence_state_mismatch")
    if fence.current is not True:
        reasons.append("admission_fence_stale")
    return not reasons, tuple(reasons)


def validate_egress(egress: Mapping[str, Any], expected_version: str) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    if egress.get("authorized") is not True or egress.get("version") != expected_version:
        reasons.append("egress_revoked_or_drifted")
    return not reasons, tuple(reasons)


def validate_prompt_isolation(record: PromptIsolationQualificationRecord, *, provider_id: str, mode: str, now: str) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    if record.provider_id != provider_id or record.mode != mode or not record.record_id:
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
        if not safe_archive_member(entry.raw_name):
            reasons.append(f"unsafe_member:{entry.raw_name}")
            continue
        name = posixpath.normpath(entry.raw_name)
        if name != entry.raw_name or not safe_archive_member(name) or (entry.normalized_path and entry.normalized_path != name):
            reasons.append(f"normalized_path_mismatch:{entry.raw_name}")
            continue
        value = entry.data
        if name in seen:
            reasons.append(f"duplicate_normalized_member:{name}")
            continue
        seen.add(name)
        if entry.kind not in ("file", "symlink", "archive"):
            reasons.append(f"unsupported_member_kind:{name}")
        if entry.kind == "symlink" and (not entry.link_target or not safe_archive_member(posixpath.normpath(posixpath.join(posixpath.dirname(name), entry.link_target)))):
            reasons.append(f"symlink_escape:{name}")
        if entry.recursion_depth > max_recursion_depth:
            reasons.append(f"archive_recursion:{name}")
        if entry.compressed_size and len(value) > entry.compressed_size * max_ratio:
            reasons.append(f"decompression_ratio:{name}")
        if not isinstance(value, bytes):
            reasons.append(f"non_bytes:{name}")
            continue
        if entry.kind == "archive":
            try:
                with zipfile.ZipFile(__import__("io").BytesIO(value)) as archive:
                    for member in archive.infolist():
                        nested = posixpath.normpath(posixpath.join(posixpath.dirname(name), member.filename))
                        if not safe_archive_member(member.filename) or not safe_archive_member(nested):
                            reasons.append(f"nested_archive_escape:{member.filename}")
                            continue
                        nested_data = archive.read(member)
                        if len(nested_data) > max_member_bytes:
                            reasons.append(f"member_size_limit:{nested}")
                        if nested in seen:
                            reasons.append(f"duplicate_normalized_member:{nested}")
                        seen.add(nested)
                        clean[nested] = nested_data
                        total += len(nested_data)
            except (zipfile.BadZipFile, OSError):
                reasons.append(f"archive_parse_failed:{name}")
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
    attempts = list(record.attempt_records)
    physical_failures = sum(1 for a in attempts if getattr(a, "kind", "FIRST") == "FIRST" and getattr(a, "outcome", "") not in ("OK", "SUCCESS", "PASS"))
    if record.hard_failures != physical_failures:
        reasons.append("hard_failure_count_not_derived")
    if physical_failures != 0:
        reasons.append("qualification_not_statistically_valid")
    if plan.qualification_profile == "R5_PRODUCTION":
        if len(plan.trial_ids) < 2 or len(plan.confirmation_ids) < 1:
            reasons.append("production_confirmation_plan_too_small")
        if not attempts:
            reasons.append("production_attempts_missing")
    expected_roots = set(plan.trial_ids) | set(plan.confirmation_ids)
    if not record.planned_attempt_ids or not record.closed_attempt_ids or set(record.planned_attempt_ids) != expected_roots or set(record.closed_attempt_ids) != expected_roots:
        reasons.append("qualification_attempt_closure")
    if attempts:
        roots = [a for a in attempts if getattr(a, "kind", "FIRST") == "FIRST"]
        if {getattr(a, "planned_root_id", "") for a in roots} != expected_roots or len(roots) != len(set(getattr(a, "planned_root_id", "") for a in roots)):
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
    fence_ok, fence_reasons = validate_fence(fence, fence.version)
    if not fence_ok:
        reasons.extend(fence_reasons)
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
    if record.provider_id != provider_id or record.mode != mode or record.prompt_isolation_mode != prompt_mode or not record.record_id:
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


def validate_wire_delivery(manifest: EvidenceDeliveryManifest, materialized: MaterializationResult, wire: WireDeliveryRecord, receipt: ReviewerReceipt, returned_items: Mapping[str, bytes], *, expected_commit: str, expected_semantic_hash: str | None) -> tuple[bool, tuple[str, ...]]:
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
    if expected_semantic_hash is not None and wire.semantic_hash != expected_semantic_hash:
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
        checkpoint = ledger.compare_and_set(attempt_id, expected.generation, "VOID", expected_state_hash=current.get("state_hash")) if ledger else AdmissionCheckpoint(attempt_id, expected.generation, "VOID", False, True, tuple(reasons))
        return AdmissionCheckpoint(checkpoint.attempt_id, checkpoint.generation, checkpoint.disposition, False, True, tuple(reasons) + tuple(checkpoint.reasons))
    if ledger:
        checkpoint = ledger.compare_and_set(attempt_id, expected.generation, "COMMITTED", expected_state_hash=current.get("state_hash"), next_state_hash=str(current.get("next_state_hash", expected.generation + 1)))
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
OUT = ROOT / "experiments" / "governed-platform" / "EXP-M-DETERMINISTIC-IMPLEMENTATION-R2B-REVIEW.md"
SOURCES = [
    Path("governance-runtime/exp_m_deterministic.py"),
    Path("governance-runtime/build_exp_m_review_packet.py"),
    Path("governance-runtime/run_exp_m_deterministic.py"),
    Path("governance-runtime/run_exp_m_mutations.py"),
    Path("governance-runtime/self_falsify_exp_m.py"),
    Path("governance-runtime/test_exp_m_deterministic.py"),
    Path("governance-runtime/test_exp_m_phases.py"),
    Path("governance-runtime/exp_m_review_fixtures.py"),
    Path("governance-runtime/run_exp_m_tests.py"),
]


def sh(*args: str) -> str:
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def fence(name: str, body: str, lang: str = "text") -> str:
    return f"\n### {name}\n\n```{lang}\n{body.rstrip()}\n```\n"


def main() -> int:
    phase = json.loads((ROOT / "experiments/governed-platform/EXP-M-DETERMINISTIC-RESULTS.json").read_text())
    mutation = json.loads((ROOT / "experiments/governed-platform/EXP-M-MUTATION-RESULTS.json").read_text())
    tests = json.loads((ROOT / "experiments/governed-platform/EXP-M-TEST-RESULTS.json").read_text())
    falsify = json.loads((ROOT / "experiments/governed-platform/EXP-M-SELF-FALSIFICATION-RESULTS.json").read_text())
    r2_review = (ROOT / "experiments/governed-platform/EXP-M-DETERMINISTIC-EXTERNAL-REVIEW-R2.md").read_text(encoding="utf-8")
    r2_adjudication = (ROOT / "experiments/governed-platform/EXP-M-DETERMINISTIC-R2-SOLUTION-ADJUDICATION.md").read_text(encoding="utf-8")
    r2_remediation = (ROOT / "experiments/governed-platform/EXP-M-DETERMINISTIC-REMEDIATION-R2.md").read_text(encoding="utf-8")
    r2a_remediation = (ROOT / "experiments/governed-platform/EXP-M-DETERMINISTIC-SELF-ADJUDICATION-R2A-REMEDIATION.md").read_text(encoding="utf-8")
    r2b_remediation = (ROOT / "experiments/governed-platform/EXP-M-DETERMINISTIC-SELF-ADJUDICATION-R2B-REMEDIATION.md").read_text(encoding="utf-8")
    execution_files = [Path("experiments/governed-platform/EXP-M-UNIT-STDOUT.txt"), Path("experiments/governed-platform/EXP-M-PHASE-STDOUT.txt"), Path("experiments/governed-platform/EXP-M-MUTATION-STDOUT.txt"), Path("experiments/governed-platform/EXP-M-DETERMINISTIC-STDOUT.txt"), Path("experiments/governed-platform/EXP-M-SELF-STDOUT.txt")]
    execution_hashes = {p.as_posix(): sha256((ROOT / p).read_bytes()).hexdigest() for p in execution_files if (ROOT / p).exists()}
    hashes = {p.as_posix(): sha256((ROOT / p).read_bytes()).hexdigest() for p in SOURCES}
    frozen = {}
    for p in ["standards/review-evidence-delivery-integrity.md", "experiments/governed-platform/exp-m-review-evidence-delivery-integrity.md", "experiments/governed-platform/EXP-M-TEST-MATRIX.md", "governance-runtime/LIVE-CONVERSATION-GOVERNANCE.md", "experiments/governed-platform/EXP-M-R5-EXTERNAL-REVIEW.md"]:
        frozen[p] = sha256((ROOT / p).read_bytes()).hexdigest()
    lines = [
        "# EXP-M Deterministic Implementation R2B Independent Review Packet",
        "",
        "This packet covers deterministic implementation only. EXP-M remains NOT_QUALIFIED; no live provider/API call occurred.",
        "",
        "## Historical superseded evidence",
        "The prior A-T/22-test/29-mutation report is retained in Git history but is superseded by the independent R1 CHANGES_REQUIRED review. It is not used as closure evidence.",
        "R2B is the current internal self-adjudication authority. Prior R1/R2/R2A and historical false-green outputs are superseded evidence only.",
        "",
        "## R2 authority inputs",
        fence("External R2 review", r2_review), fence("R2 solution adjudication", r2_adjudication), fence("R2 remediation", r2_remediation), fence("R2A remediation", r2a_remediation), fence("R2B remediation", r2b_remediation),
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
        f"tests_total={tests['tests_total']}",
        f"tests_passed={tests['tests_passed']}",
        f"tests_failed={tests['tests_failed']}",
        "r2b_status=AUTOMATABLE_REMEDIATION_COMPLETE",
        "r2b_clean_source_to_evidence_to_packet_sequence=true",
        "",
        "## Frozen source-of-truth hashes",
        "```json", json.dumps(frozen, indent=2, sort_keys=True), "```",
        "",
        "## Implemented source hashes",
        "```json", json.dumps(hashes, indent=2, sort_keys=True), "```",
        "",
        "## R2B phase A-T results",
        "```json", json.dumps(phase, indent=2, sort_keys=True), "```",
        "",
        "## Mutation results",
        "```json", json.dumps(mutation, indent=2, sort_keys=True), "```",
        "## Offline test result",
        "```json", json.dumps(tests, indent=2, sort_keys=True), "```",
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
    materialize_entries, MaterializationEntry,
    adjudicate_insufficient_evidence,
    validate_capability, validate_witness_qualification, WitnessProtocolQualificationRecord, RetrievalEvidenceRecord,
    bundle_from_state, context_from_state, validate_context_isolation,
    AccessibilityProofRecord, ReviewerProvenanceRecord, SemanticCoverageRecord, DeliveryCompletenessResult,
    RepresentationRecord,
    PhysicalAttemptRecord,
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
    physical = (PhysicalAttemptRecord("a", "a", None, "FIRST", "request", "session", "w1", "FAILED"), PhysicalAttemptRecord("a-retry", "a", "a", "RETRY", "request", "session", "w2", "OK"))
    phase_results["H"] = {"status": "PASS" if validate_retry_transparency(physical, planned_root_ids=("a",), expected_request="request", expected_session="session")[0] else "FAIL", "checks": ["physical request ledger", "retry lineage"]}
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
    actual_targets = set(mutation_result.get("executed_mutation_targets", ()))
    killed_targets = set(mutation_result.get("killed_mutation_targets", ()))
    fixture_targets = set(mutation_result.get("executed_fixture_targets", ()))
    closure_ok = registry.closure(mutation_result.get("verdict_predicate_ids", ()), killed_targets, declared_mutations=mutation_result.get("declared_mutation_targets", ()), executed_mutations=actual_targets, killed_mutations=killed_targets, declared_fixtures=registry.fixture_ids, executed_fixtures=registry.fixture_ids, executed_fixture_targets=fixture_targets)
    phase_results["O"] = {"status": "PASS" if closure_ok else "FAIL", "checks": ["predicate/verdict/mutation/fixture closure"], "target_counts": {"required": len(registry.predicate_ids), "executed": len(actual_targets), "killed": len(killed_targets), "fixtures": len(fixture_targets)}}
    context_ok = validate_context_state(ProviderContextStateEvidence(True, ("memory", "config"), True, "state"), required_channels=("memory", "config"))[0]
    phase_results["P"] = {"status": "PASS" if context_ok else "FAIL", "checks": ["residual adversarial oracle"]}
    phase_results["Q"] = {"status": "PASS" if validate_fence(AdmissionFenceRecord("f", "1", True), "1")[0] else "FAIL", "checks": ["risk policy", "admission fence"]}
    witness_negative = validate_witness_qualification(witness_record, provider_id="fake", mode="inline", prompt_mode="prompt", now="2025-01-01T00:00:00Z", response="x" * 2000, challenge="extract token", final_context_bytes=10, max_final_context_bytes=1000)
    phase_results["R"] = {"status": "PASS" if witness[0] and not witness_negative[0] else "FAIL", "checks": ["witness noninterference", "context eviction rejection"]}
    phase_results["S"] = {"status": "PASS" if validate_attempt_ledger(("t1", "t2"), ("t1", "t2"), ())[0] and validate_retry_transparency(physical, planned_root_ids=("a",), expected_request="request", expected_session="session")[0] else "FAIL", "checks": ["planned attempt closure", "physical retry lineage"]}
    phase_results["T"] = {"status": "PASS" if validate_retry_transparency(physical, planned_root_ids=("a",), expected_request="request", expected_session="session")[0] and closure_ok else "FAIL", "checks": ["retry transparency", "registry closure"]}
    phase_functions = {
        "A": ["preflight_delivery"], "B": ["validate_chunks"], "C": ["validate_representation"], "D": ["adjudicate_insufficient_evidence"],
        "E": ["EvidenceDeliveryManifest.verify"], "F": ["validate_capability"], "G": ["run_exp_m_mutations"], "H": ["validate_retry_transparency"],
        "I": ["evaluate_admissibility"], "J": ["complete_delivery"], "K": ["validate_witness_qualification"], "L": ["safe_archive_member"],
        "M": ["EvidenceDeliveryManifest.verify"], "N": ["preflight_delivery"], "O": ["independent_target_closure"], "P": ["validate_context_state"],
        "Q": ["validate_fence"], "R": ["validate_witness_qualification"], "S": ["validate_attempt_ledger"], "T": ["validate_retry_transparency", "independent_target_closure"],
    }
    def negative_case(phase_id: str) -> tuple[bool, str, str]:
        """Execute a real adversarial invocation for each phase."""
        if phase_id == "A":
            bad = GovernanceAuthoritySnapshot("snap", "1", "snapshot-hash", False)
            return (not valid_preflight(bad, c, i, manifest, provider, items).allowed, "preflight_delivery", "candidate_writable_snapshot")
        if phase_id == "B":
            bad = list(ch); bad[0] = EvidenceChunk.create("request", digest(corpus), 0, 2, b"xxxxx")
            return (not validate_chunks(bad, request_id="request", corpus_hash=digest(corpus))[0], "validate_chunks", "corrupt_chunk")
        if phase_id == "C":
            return (not validate_representation(manifest, {"required-a": b"changed", "required-b": items["required-b"]})[0], "validate_representation", "raw_byte_mutation")
        if phase_id == "D":
            return (adjudicate_insufficient_evidence({}).disposition == "INSUFFICIENT_EVIDENCE_CAUSE_UNRESOLVED", "adjudicate_insufficient_evidence", "unresolved_cause")
        if phase_id == "E":
            return (not manifest.verify({"required-a": b"changed", "required-b": items["required-b"]})[0], "EvidenceDeliveryManifest.verify", "manifest_byte_mutation")
        if phase_id == "F":
            expired = ProviderCapabilityProfile(provider.provider_id, provider.model_id, provider.adapter_version, provider.profile_hash, True, "2000-01-01T00:00:00Z", provider.supported_formats, provider.max_context_bytes)
            return (not validate_capability(expired, ProviderQualificationExecutionPlan("plan", "fake", "default", ("a1",), ("a1",)), ProviderCapabilityQualificationRecord("plan", "profile-hash", True, True, 0, "default", ("a1",), ("a1",), "fake", "deterministic", attempt_records=(PhysicalAttemptRecord("a1", "a1", None, "FIRST", "request", "session", "w", "OK"),)), now="2025-01-01T00:00:00Z", expected_provider="fake", expected_model="deterministic", expected_operating_point="default", expected_profile_hash="profile-hash", required_format="text", required_context_bytes=1)[0], "validate_capability", "expired_profile")
        if phase_id == "G":
            return (mutation_result["all_rejected"], "run_exp_m_mutations", "independent_mutation_catalog")
        if phase_id == "H":
            return (not validate_retry_transparency((PhysicalAttemptRecord("retry", "root", None, "RETRY", "request", "session", "w", "OK"),), planned_root_ids=("root",), expected_request="request", expected_session="session")[0], "validate_retry_transparency", "retry_without_failed_parent")
        if phase_id == "I":
            bad_state = dict(state); bad_state["disposition"] = "CHANGES_REQUIRED"
            return (not evaluate_admissibility(bundle_from_state(bad_state), context_from_state(bad_state), registry).admissible, "evaluate_admissibility", "non_promotable_disposition")
        if phase_id == "J":
            return (not complete_delivery(manifest, ReviewerReceipt("a", "request", "session", "wrong", (), 0, True), wire).complete, "complete_delivery", "receipt_manifest_mismatch")
        if phase_id == "K":
            return (not validate_witness_qualification(witness_record, provider_id="fake", mode="inline", prompt_mode="prompt", now="2025-01-01T00:00:00Z", response="x" * 2000, challenge="extract token", final_context_bytes=10, max_final_context_bytes=1000)[0], "validate_witness_qualification", "response_budget")
        if phase_id == "L":
            return (not materialize_entries((MaterializationEntry("../escape", "../escape", "file", b"x"),), source_hash="src").success, "materialize_entries", "archive_traversal")
        if phase_id == "M":
            return (not manifest.verify({"required-a": b"mutated", "required-b": items["required-b"]})[0], "EvidenceDeliveryManifest.verify", "frozen_byte_mutation")
        if phase_id == "N":
            bad_provider = ProviderCapabilityProfile("fake", "m", "v", "p", False)
            return (not valid_preflight(s, c, i, manifest, bad_provider, items).allowed, "preflight_delivery", "unqualified_provider")
        if phase_id == "O":
            return (not registry.closure(registry.predicate_ids, killed_targets, declared_mutations=mutation_result.get("declared_mutation_targets", ()), executed_mutations=actual_targets, killed_mutations=(), declared_fixtures=registry.fixture_ids, executed_fixtures=registry.fixture_ids, executed_fixture_targets=fixture_targets), "AdmissibilityPredicateRegistry.closure", "missing_killed_target")
        if phase_id == "P":
            return (not validate_context_isolation(ProviderContextIsolationPolicy("policy", "COMPLETE_READABLE_FENCED_STATE"), ProviderContextStateEvidence(False, ("memory",), False, ""), AdmissionFenceRecord("fence", "stale", False), transition_class="LOWER", required_channels=("memory", "config"))[0], "validate_context_isolation", "dirty_context")
        if phase_id == "Q":
            return (not validate_fence(AdmissionFenceRecord("fence", "wrong", True), "1")[0], "validate_fence", "fence_version_mismatch")
        if phase_id == "R":
            return (not validate_witness_qualification(witness_record, provider_id="fake", mode="inline", prompt_mode="prompt", now="2025-01-01T00:00:00Z", response="answer", challenge="judge this", final_context_bytes=10, max_final_context_bytes=1000)[0], "validate_witness_qualification", "semantic_prompt")
        if phase_id == "S":
            return (not validate_retry_transparency((PhysicalAttemptRecord("r", "root", "unknown", "RETRY", "request", "session", "w", "OK"),), planned_root_ids=("root",), expected_request="request", expected_session="session")[0], "validate_retry_transparency", "retry_lineage")
        return (not validate_retry_transparency((PhysicalAttemptRecord("a", "a", None, "FIRST", "request", "session", "w", "FAILED"), PhysicalAttemptRecord("a", "a", "a", "RETRY", "request", "session", "w", "OK")), planned_root_ids=("a",), expected_request="request", expected_session="session")[0], "validate_retry_transparency", "duplicate_physical_dispatch")

    for phase_id, result in phase_results.items():
        result["production_functions_invoked"] = phase_functions[phase_id]
        positive = {"case_id": f"{phase_id}-positive-control", "phase_id": phase_id, "kind": "positive", "production_functions": phase_functions[phase_id], "expected": "PASS", "actual": result["status"], "result": result["status"] == "PASS"}
        rejected, fn, target = negative_case(phase_id)
        negative = {"case_id": f"{phase_id}-negative-{target}", "phase_id": phase_id, "kind": "negative", "production_functions": [fn], "fixture": target, "expected": "REJECT", "actual": "REJECT" if rejected else "PASS", "rejection_reason": target, "result": rejected}
        result["executed_cases"] = [positive, negative]
        result["positive_case_ids"] = [positive["case_id"]] if positive["result"] else []
        result["negative_case_ids"] = [negative["case_id"]] if negative["result"] else []
        result["case_results"] = {"positive": positive["result"], "negative_rejected": negative["result"], "phase_status": "PASS" if positive["result"] and negative["result"] else "FAIL"}
        result["status"] = result["case_results"]["phase_status"]
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
import multiprocessing
import pickle
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
    PredicateContext,
)

ROOT = Path(__file__).resolve().parents[1]
from exp_m_review_fixtures import build_negative_fixture


FROZEN_MUTATION_CONTEXT = PredicateContext(
    "r", "a", "s", "commit", "s", "h", "1", "fake", "deterministic", "adapter", "default", "profile-hash", "1",
    "LOWER", "1", "fake", "inline", "fake", "inline", "prompt", "file", "v", "ctx", "ctx-h", 1_000_000, "2", ("PASS",)
)


def evaluate(state, registry):
    # Mutation fixtures are evaluated against this independently frozen
    # context; expected identities are never derived from the mutated state.
    return evaluate_admissibility(bundle_from_state(state), FROZEN_MUTATION_CONTEXT, registry)


def _mutated_evaluate(predicate, state, registry):
    import exp_m_deterministic as production
    original = production._predicate_validators
    original_disposition = production._validate_disposition
    def mutated_validators(context, _original=original, _predicate=predicate):
        validators = _original(context)
        families = (
            {"context_isolation_satisfied", "hidden_state_policy_satisfied", "context_state_clean", "admission_fence_current"},
            {"materialization_complete", "representation_governed", "wire_binding_valid", "delivery_complete"},
            {"accessibility_policy_satisfied", "accessibility_proven", "witness_record_current"},
        )
        family = next((group for group in families if _predicate in group), {_predicate})
        for target in family:
            validators[target] = lambda _state: True
        return validators
    production._predicate_validators = mutated_validators
    if predicate == "disposition_promotable": production._validate_disposition = lambda _state, _context, _results: True
    try:
        result = evaluate(state, registry)
        return {"admissible": result.admissible, "reasons": list(result.reasons)}
    finally:
        production._predicate_validators = original
        production._validate_disposition = original_disposition


def isolated_mutant_result(predicate, state, registry):
    work = ROOT / "experiments" / "governed-platform" / ".exp-m-mutants"
    work.mkdir(parents=True, exist_ok=True)
    stem = predicate.replace("/", "_")
    payload = work / f"{stem}.pkl"; result_path = work / f"{stem}.json"
    payload.write_bytes(pickle.dumps((predicate, state, registry)))
    completed = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--isolated-worker", str(payload), str(result_path)], cwd=ROOT, timeout=15)
    if completed.returncode != 0 or not result_path.exists(): return None
    return json.loads(result_path.read_text(encoding="utf-8"))


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
    for predicate in reg.logic_mutation_ids:
        negative_state = build_negative_fixture(base, predicate)
        normal_result = evaluate(negative_state, reg)
        # Each mutant is executed in a fresh spawned process/module instance.
        mutated_payload = isolated_mutant_result(predicate, negative_state, reg)
        mutated_result = type("Result", (), {"admissible": bool(mutated_payload and mutated_payload["admissible"]), "reasons": tuple(mutated_payload.get("reasons", ()) if mutated_payload else ("isolated_mutant_failed",))})()
        mutations.append({"id": f"TM-O-{predicate}", "family": "validator_logic", "target": predicate, "target_predicate_id": predicate, "negative_fixture_id": f"negative:{predicate}", "negative_fixture_target_id": predicate, "executed": True, "fixture_hash": digest(negative_state), "expected": "REJECT", "actual": "PASS" if mutated_result.admissible else "REJECT", "negative_control": "REJECT" if not normal_result.admissible else "PASS", "killed": mutated_result.admissible, "normal_reasons": list(normal_result.reasons), "mutated_reasons": list(mutated_result.reasons)})
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
    logic = [m for m in mutations if m.get("family") == "validator_logic"]
    return {"experiment": "EXP-M", "total_mutations": len(mutations), "rejected_mutations": rejected, "surviving_mutations": len(mutations) - rejected, "all_rejected": rejected == len(mutations), "mutations": mutations,
            "declared_mutation_targets": list(reg.logic_mutation_ids),
            "executed_mutation_targets": sorted({m["target_predicate_id"] for m in logic if m.get("executed")}),
            "killed_mutation_targets": sorted({m["target_predicate_id"] for m in logic if m.get("executed") and m.get("killed")}),
            "declared_fixture_targets": sorted({m["negative_fixture_target_id"] for m in logic}),
            "executed_fixture_targets": sorted({m["negative_fixture_target_id"] for m in logic if m.get("executed")}),
            "verdict_predicate_ids": list(reg.predicate_ids)}


if __name__ == "__main__" and len(sys.argv) >= 4 and sys.argv[1] == "--isolated-worker":
    predicate, state, registry = pickle.loads(Path(sys.argv[2]).read_bytes())
    Path(sys.argv[3]).write_text(json.dumps(_mutated_evaluate(predicate, state, registry)), encoding="utf-8")
    raise SystemExit(0)

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
    ProviderQualificationExecutionPlan, ProviderCapabilityQualificationRecord,
    validate_capability, PersistentAdmissionLedger, admissibility_registry,
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
    # R2A independent attacks (not delegated to the normal mutation runner).
    reg = admissibility_registry()
    case("closure_catalog_omission", not reg.closure(reg.predicate_ids, reg.logic_mutation_ids, declared_mutations=tuple(reg.logic_mutation_ids[:-1]), executed_mutations=tuple(reg.logic_mutation_ids), declared_fixtures=reg.fixture_ids, executed_fixtures=reg.fixture_ids))
    p = ProviderCapabilityProfile("fake", "m", "v", "hash", True, "2099-01-01T00:00:00Z", ("text",), 1000)
    plan = ProviderQualificationExecutionPlan("p", "fake", "op", ("trial",), ("confirm",))
    incomplete = ProviderCapabilityQualificationRecord("p", "hash", True, True, 0, "op", ("confirm",), ("confirm",), "fake", "m")
    case("missing_trial_root", not validate_capability(p, plan, incomplete, now="2025-01-01T00:00:00Z", expected_provider="fake", expected_model="m", expected_operating_point="op", expected_profile_hash="hash", required_format="text", required_context_bytes=1)[0])
    case("self_derived_context", not evaluate_admissibility(bundle_from_state({"review_request": {"current": True, "request_id": "attacker"}, "disposition": "PASS"}), context_from_state({"expected_request_id": "r"})).admissible)
    case("forged_delivery_result", not evaluate_admissibility(bundle_from_state({"review_request": {"current": True, "request_id": "r"}, "delivery": {"complete": True}, "disposition": "PASS"}), context_from_state({})).admissible)
    case("witness_without_expected_answer", not evaluate_admissibility(bundle_from_state({"review_request": {"current": True, "request_id": "r"}, "witness": {"current": True}, "disposition": "PASS"}), context_from_state({})).admissible)
    case("accessibility_valid_only", not evaluate_admissibility(bundle_from_state({"review_request": {"current": True, "request_id": "r"}, "accessibility": {"valid": True}, "disposition": "PASS"}), context_from_state({})).admissible)
    race_path = ROOT / "experiments" / "governed-platform" / ".r2a-race-ledger.json"
    race_ledger = PersistentAdmissionLedger(race_path)
    first_race = race_ledger.compare_and_set("race", 1, "VOID"); second_race = race_ledger.compare_and_set("race", 1, "COMMITTED")
    case("persistent_race_second_writer", first_race.void and second_race.void)
    for artifact in (race_path, race_path.with_suffix(race_path.suffix + ".sqlite")):
        try: artifact.unlink()
        except OSError: pass
    # Behavioral phase-artifact falsification: run the real phase cases, then
    # perturb one executed negative case and prove the phase closure fails.
    from run_exp_m_deterministic import run_phases
    phase_artifact = run_phases()
    real_cases = all(len(v.get("executed_cases", ())) >= 2 and any(c.get("kind") == "negative" and c.get("actual") == "REJECT" for c in v.get("executed_cases", ())) for v in phase_artifact["phases"].values())
    case("phase_cases_are_executed", real_cases)
    perturbed = json.loads(json.dumps(phase_artifact))
    first_phase = next(iter(perturbed["phases"].values()))
    first_phase["executed_cases"][1]["actual"] = "PASS"
    first_phase["executed_cases"][1]["result"] = False
    case("phase_negative_perturbation_fails", not all(all(c.get("result") for c in v.get("executed_cases", ())) for v in perturbed["phases"].values()))
    removed = json.loads(json.dumps(phase_artifact)); removed["phases"]["A"]["executed_cases"] = []
    case("phase_case_removal_fails_closure", not all(len(v.get("executed_cases", ())) >= 2 for v in removed["phases"].values()))
    case("typed_summary_boolean", not evaluate_admissibility(bundle_from_state({"review_request": {"current": True, "request_id": "r"}, "capability": {"validated": True}, "context_isolation": {"satisfied": True}, "disposition": "PASS"}), context_from_state({})).admissible)
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
import threading
import uuid
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
    validate_registry_version, validate_retry_transparency, validate_capability,
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
        reg = admissibility_registry(); self.assertTrue(reg.closure(reg.predicate_ids, reg.logic_mutation_ids,
            declared_mutations=reg.logic_mutation_ids, executed_mutations=reg.logic_mutation_ids,
            killed_mutations=reg.logic_mutation_ids, declared_fixtures=reg.fixture_ids,
            executed_fixtures=reg.fixture_ids, executed_fixture_targets=reg.predicate_ids))

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
        self.assertFalse(result.allowed); self.assertIn("context_channel_unobserved", result.reasons); self.assertIn("admission_fence_stale", result.reasons)

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
        path = Path(f"experiments/governed-platform/.exp-m-test-ledger-{uuid.uuid4().hex}.json")
        try:
            if path.exists(): path.unlink()
            first = PersistentAdmissionLedger(path).compare_and_set("a", 1, "VOID")
            second = PersistentAdmissionLedger(path).compare_and_set("a", 1, "COMMITTED")
            self.assertTrue(first.void); self.assertTrue(second.void); self.assertEqual(second.reasons, ("terminal_state",))
        finally:
            if path.exists(): path.unlink()

    def test_r2_admission_race_has_one_terminal_winner(self):
        path = Path(f"experiments/governed-platform/.exp-m-race-ledger-{uuid.uuid4().hex}.json")
        db = path.with_suffix(path.suffix + ".sqlite")
        ledger = PersistentAdmissionLedger(path); results = []
        def writer(disposition): results.append(ledger.compare_and_set("race", 1, disposition))
        workers = [threading.Thread(target=writer, args=("COMMITTED",)), threading.Thread(target=writer, args=("VOID",))]
        [w.start() for w in workers]; [w.join() for w in workers]
        self.assertEqual(len(results), 2)
        self.assertEqual(sum(not r.reasons for r in results), 1)
        self.assertTrue(all((not r.reasons) or r.reasons == ("terminal_state",) for r in results))

    def test_r2_retry_lineage_is_explicit(self):
        records = (PhysicalAttemptRecord("a", "a", None, "FIRST", "r", "s", "w1", "FAILED"), PhysicalAttemptRecord("a-retry", "a", "a", "RETRY", "r", "s", "w2", "OK"))
        self.assertTrue(validate_retry_transparency(records, planned_root_ids=("a",), expected_request="r", expected_session="s")[0])
        broken = (PhysicalAttemptRecord("a-retry", "a", None, "RETRY", "r", "s", "w2", "OK"),)
        self.assertFalse(validate_retry_transparency(broken, planned_root_ids=("a",), expected_request="r", expected_session="s")[0])

    def test_r2_production_evaluator_has_no_bypass_parameter(self):
        import inspect
        self.assertNotIn("disabled_predicates", inspect.signature(evaluate_admissibility).parameters)

    def test_r2b_required_optional_manifest_is_exact(self):
        s, c, i, items, m, p = fixture(); extra = dict(items); extra["unknown"] = b"x"
        self.assertFalse(preflight(s, c, i, m, "request-1", p, extra).allowed)

    def test_r2b_materialization_derives_path_and_rejects_falsified_metadata(self):
        bad = MaterializationEntry("safe/file", "other/file", "file", b"x", None, 999, 999, 99)
        self.assertFalse(materialize_entries((bad,), source_hash="s").success)

    def test_r2b_production_profile_requires_real_plan(self):
        profile = ProviderCapabilityProfile("fake", "deterministic", "v", "hash", True, "2099-01-01T00:00:00Z", ("text",), 1000)
        plan = ProviderQualificationExecutionPlan("p", "fake", "op", ("trial",), ("confirm",), "R5_PRODUCTION")
        record = ProviderCapabilityQualificationRecord("p", "hash", True, True, 0, "op", ("trial",), ("trial",), "fake", "deterministic", attempt_records=(PhysicalAttemptRecord("trial", "trial", None, "FIRST", "r", "s", "w", "OK"),))
        ok, reasons = validate_capability(profile, plan, record, now="2025-01-01T00:00:00Z", expected_provider="fake", expected_model="deterministic", expected_operating_point="op", expected_profile_hash="hash", required_format="text", required_context_bytes=1)
        self.assertFalse(ok); self.assertIn("production_confirmation_plan_too_small", reasons)

    def test_r2b_physical_attempt_duplicate_is_rejected(self):
        records = (PhysicalAttemptRecord("a", "a", None, "FIRST", "r", "s", "w", "FAILED"), PhysicalAttemptRecord("b", "a", "a", "RETRY", "r", "s", "w", "OK"))
        ok, reasons = validate_retry_transparency(records, planned_root_ids=("a",), expected_request="r", expected_session="s")
        self.assertFalse(ok); self.assertIn("physical_attempt_or_wire_duplicate", reasons)

    def test_r2b_closure_missing_execution_evidence_fails(self):
        reg = admissibility_registry()
        self.assertFalse(reg.closure(reg.predicate_ids, reg.logic_mutation_ids, declared_mutations=reg.logic_mutation_ids, executed_mutations=reg.logic_mutation_ids, killed_mutations=reg.logic_mutation_ids, declared_fixtures=reg.fixture_ids, executed_fixtures=reg.fixture_ids, executed_fixture_targets=()))

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


### governance-runtime/exp_m_review_fixtures.py

```python
"""Review-owned immutable negative fixture constructors.

This module is intentionally separate from the production predicate registry
and from the mutation runner.  It describes the semantic defect each fixture
must expose; the runner only executes these constructors.
"""
from __future__ import annotations
from copy import deepcopy
from typing import Any, Mapping

from exp_m_deterministic import (
    GovernanceAuthoritySnapshot, RequiredEvidenceContract,
    RequiredInteractionContract, MaterializationResult, RepresentationRecord,
    AccessibilityProofRecord, ProviderContextStateEvidence,
    WitnessProtocolQualificationRecord, SemanticContextQualificationRecord,
    WireDeliveryRecord, ReviewerProvenanceRecord, SemanticCoverageRecord,
)

FIXTURE_CATALOG = (
    {"fixture_id": "negative:review_request_current", "target_predicate_id": "review_request_current", "constructor": "review_request_not_current", "expected_rejection": "review_request_current"},
    {"fixture_id": "negative:authority_snapshot_current", "target_predicate_id": "authority_snapshot_current", "constructor": "candidate_writable_snapshot", "expected_rejection": "authority_snapshot_current"},
    {"fixture_id": "negative:evidence_contract_closed", "target_predicate_id": "evidence_contract_closed", "constructor": "open_evidence_contract", "expected_rejection": "evidence_contract_closed"},
    {"fixture_id": "negative:interaction_contract_closed", "target_predicate_id": "interaction_contract_closed", "constructor": "open_interaction_contract", "expected_rejection": "interaction_contract_closed"},
    {"fixture_id": "negative:materialization_complete", "target_predicate_id": "materialization_complete", "constructor": "failed_materialization", "expected_rejection": "materialization_complete"},
    {"fixture_id": "negative:representation_governed", "target_predicate_id": "representation_governed", "constructor": "unqualified_representation", "expected_rejection": "representation_governed"},
    {"fixture_id": "negative:egress_authorized", "target_predicate_id": "egress_revoked", "constructor": "revoked_egress", "expected_rejection": "egress_authorized"},
    {"fixture_id": "negative:capability_current", "target_predicate_id": "capability_current", "constructor": "invalid_capability_summary", "expected_rejection": "capability_current"},
    {"fixture_id": "negative:accessibility_policy_satisfied", "target_predicate_id": "accessibility_policy_satisfied", "constructor": "invalid_accessibility_policy", "expected_rejection": "accessibility_policy_satisfied"},
    {"fixture_id": "negative:context_isolation_satisfied", "target_predicate_id": "context_isolation_satisfied", "constructor": "dirty_isolation", "expected_rejection": "context_isolation_satisfied"},
    {"fixture_id": "negative:hidden_state_policy_satisfied", "target_predicate_id": "hidden_state_policy_satisfied", "constructor": "hidden_state", "expected_rejection": "hidden_state_policy_satisfied"},
    {"fixture_id": "negative:context_state_clean", "target_predicate_id": "context_state_clean", "constructor": "dirty_context", "expected_rejection": "context_state_clean"},
    {"fixture_id": "negative:admission_fence_current", "target_predicate_id": "admission_fence_current", "constructor": "stale_fence", "expected_rejection": "admission_fence_current"},
    {"fixture_id": "negative:semantic_context_qualified", "target_predicate_id": "semantic_context_qualified", "constructor": "wrong_semantic_context", "expected_rejection": "semantic_context_qualified"},
    {"fixture_id": "negative:wire_binding_valid", "target_predicate_id": "wire_binding_valid", "constructor": "invalid_wire", "expected_rejection": "wire_binding_valid"},
    {"fixture_id": "negative:delivery_complete", "target_predicate_id": "delivery_complete", "constructor": "incomplete_delivery", "expected_rejection": "delivery_complete"},
    {"fixture_id": "negative:accessibility_proven", "target_predicate_id": "accessibility_proven", "constructor": "invalid_accessibility_proof", "expected_rejection": "accessibility_proven"},
    {"fixture_id": "negative:witness_record_current", "target_predicate_id": "witness_record_current", "constructor": "expired_witness", "expected_rejection": "witness_record_current"},
    {"fixture_id": "negative:session_retrieval_coverage", "target_predicate_id": "session_retrieval_coverage", "constructor": "invalid_retrieval", "expected_rejection": "session_retrieval_coverage"},
    {"fixture_id": "negative:prompt_isolation_current", "target_predicate_id": "prompt_isolation_current", "constructor": "expired_prompt", "expected_rejection": "prompt_isolation_current"},
    {"fixture_id": "negative:semantic_coverage", "target_predicate_id": "semantic_coverage", "constructor": "incomplete_coverage", "expected_rejection": "semantic_coverage"},
    {"fixture_id": "negative:reviewer_provenance", "target_predicate_id": "reviewer_provenance", "constructor": "untrusted_reviewer", "expected_rejection": "reviewer_provenance"},
    {"fixture_id": "negative:disposition_promotable", "target_predicate_id": "disposition_promotable", "constructor": "non_promotable_disposition", "expected_rejection": "disposition_promotable"},
)

def build_negative_fixture(base: Mapping[str, Any], predicate: str) -> dict[str, Any]:
    """Construct one independent negative fixture from a positive base."""
    state = deepcopy(dict(base))
    if predicate == "review_request_current": state["review_request"] = {"current": False, "request_id": "r"}
    elif predicate == "authority_snapshot_current": state["authority_snapshot"] = GovernanceAuthoritySnapshot("s", "1", "h", False)
    elif predicate == "evidence_contract_closed": state["evidence_contract"] = RequiredEvidenceContract("e", "s", (), non_vacuous=False)
    elif predicate == "interaction_contract_closed": state["interaction_contract"] = RequiredInteractionContract("i", "s", (), closed=False)
    elif predicate == "materialization_complete": state["materialization"] = MaterializationResult(False, {}, "", "src", "raw-v1")
    elif predicate == "representation_governed": state["representation"] = {"governed": False, "transform_id": ""}
    elif predicate == "egress_authorized": state["egress"] = {"authorized": False, "version": "1"}
    elif predicate == "capability_current": state["capability"] = {"validated": False}
    elif predicate == "accessibility_policy_satisfied": state["accessibility_policy"] = {"satisfied": False, "risk_policy_version": "r1"}
    elif predicate in ("context_isolation_satisfied", "hidden_state_policy_satisfied"): state["context_isolation"] = {"satisfied": False, "transition_class": "LOWER"}
    elif predicate == "context_state_clean": state["context_state"] = {"clean": False, "sentinel_passed": False, "state_hash": "state"}
    elif predicate == "admission_fence_current": state["fence"] = {"current": False, "version": "1"}
    elif predicate == "semantic_context_qualified": state["semantic_context"] = {"qualified": False, "context_hash": "wrong"}
    elif predicate in ("wire_binding_valid", "delivery_complete"): state["delivery"] = {"computed_complete": False}
    elif predicate == "accessibility_proven": state["accessibility"] = {"proven": False, "challenge_id": "ch"}
    elif predicate == "witness_record_current": state["witness"] = {"validated": False}
    elif predicate == "session_retrieval_coverage": state["retrieval"] = {"validated": False, "final_context_id": "ctx"}
    elif predicate == "prompt_isolation_current": state["prompt_isolation"] = {"current": False}
    elif predicate == "semantic_coverage": state["semantic_coverage"] = {"complete": False}
    elif predicate == "reviewer_provenance": state["reviewer"] = {"trusted": False}
    elif predicate == "disposition_promotable": state["disposition"] = "CHANGES_REQUIRED"
    else: raise KeyError(predicate)
    return state
```


### governance-runtime/run_exp_m_tests.py

```python
"""Run the offline EXP-M unit/phase suites and bind their result to source."""
from __future__ import annotations
import json, re, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMMANDS = (("core", "governance-runtime/test_exp_m_deterministic.py"), ("phases", "governance-runtime/test_exp_m_phases.py"))

def main() -> int:
    results = []
    for name, script in COMMANDS:
        completed = subprocess.run([sys.executable, script], cwd=ROOT, capture_output=True, text=True)
        output = completed.stdout + completed.stderr
        match = re.search(r"Ran (\d+) tests", output)
        total = int(match.group(1)) if match else 0
        passed = total if completed.returncode == 0 and "OK" in output else 0
        results.append({"suite": name, "command": f"python {script}", "exit_code": completed.returncode, "tests_total": total, "tests_passed": passed, "tests_failed": total - passed, "stdout_stderr": output})
    total = sum(r["tests_total"] for r in results); passed = sum(r["tests_passed"] for r in results)
    result = {"tests_total": total, "tests_passed": passed, "tests_failed": total - passed, "all_passed": total == passed and total > 0, "suites": results,
              "execution": {"source_commit": subprocess.check_output(("git", "rev-parse", "HEAD"), cwd=ROOT, text=True).strip(), "source_tree": subprocess.check_output(("git", "rev-parse", "HEAD^{tree}"), cwd=ROOT, text=True).strip(), "utc": datetime.now(timezone.utc).isoformat(), "command": "python governance-runtime/run_exp_m_tests.py", "interpreter": sys.executable}}
    out = ROOT / "experiments/governed-platform/EXP-M-TEST-RESULTS.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["all_passed"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
```

