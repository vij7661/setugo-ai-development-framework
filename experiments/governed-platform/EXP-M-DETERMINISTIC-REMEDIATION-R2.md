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
