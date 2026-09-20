# EXP-M Deterministic Implementation — Internal Self-Adjudication R2C Remediation

Status: `AUTOMATABLE_WORK_REMAINS`

Authority effect: `NONE`

EXP-M remains `NOT_QUALIFIED`.

Live provider/API qualification and execution remain blocked.

This remediation supersedes the R2B external-review stop. Internal review of frozen R2B source `3ced9164bf55d7f13470a0b254f8decd9871bdeb` found remaining automatable Critical/High false-green paths. Do not send the current R2B packet externally.

## 1. Predicate/fixture/mutation independence must be real

### 1.1 One authoritative required-predicate registry

Move the platform-required predicate definition into one explicit platform-owned registry file/module.

The production validator dispatch may consume that registry, but mutation and fixture catalogs must not be generated from it.

### 1.2 Mutation catalog in separate module/file

Create a separately maintained mutation catalog with records:

- mutation_id
- target_predicate_id
- mutation_operator_id
- expected_false_green_class

Do not colocate it with the production predicate tuple or create it by iterating `PREDICATES`.

### 1.3 Fixture catalog in separate module/file

Create a separately maintained fixture catalog with:

- fixture_id
- target_predicate_id
- constructor_id
- expected_rejection_predicate
- expected_rejection_reason

The fixture catalog must be the catalog actually used by `build_negative_fixture`.

Do not keep a second shadow fixture catalog in `exp_m_deterministic.py`.

### 1.4 Closure must consume the real fixture catalog

The R2B source currently allows closure to be satisfied from mutation-result fields rather than the independent fixture catalog. Fix this.

Closure inputs must be loaded independently from:

- required predicate registry;
- actual verdict artifact;
- declared mutation catalog;
- executed mutation artifact;
- killed mutation artifact;
- declared fixture catalog;
- executed fixture artifact.

A target typo or mismatch in the fixture catalog must fail closure.

Add a regression where one fixture has a wrong `target_predicate_id`; Phase O/T and packet generation must fail.

## 2. Validator mutations must be one-target-at-a-time

Current mutation code can disable a family of predicates for one nominal target.

This does not prove the named predicate is individually load-bearing.

For every required predicate:

1. use one independently frozen negative fixture targeting exactly that predicate;
2. normal production must reject for that target;
3. isolated mutant modifies only the exact target guard;
4. all other validators remain original;
5. mutant must create the target false-green;
6. independent oracle detects the divergence.

No grouped families unless a separately registered compound mutation explicitly names every target and is not counted as coverage for any individual target.

## 3. Context isolation must use external transition/fence expectations

The authoritative context predicate must not use:

`record.transition_class`

as the transition class being governed.

Use:

- `PredicateContext.expected_transition_class`;
- `PredicateContext.expected_fence_version`;
- externally expected context-policy identity/version;
- externally expected observation/config generation.

`validate_context_isolation()` must call `validate_fence(fence, expected_fence_version)`, never `validate_fence(fence, fence.version)`.

Add attacks:

- malicious record downgrades HIGHEST -> LOWER;
- malicious fence supplies its own matching version;
- hidden state allowed only after self-downgrade;
- stale fence with otherwise matching state hash.

## 4. Witness proof must verify the actual answer

A witness record/challenge is not sufficient unless the returned answer is verified.

Trusted harness must bind:

- challenge ID;
- source slice identity/hash;
- expected answer bytes/hash;
- provider/mode/prompt-isolation identity;
- issue/expiry/current authority identity.

Authoritative validation must verify:

- actual response bytes/hash == expected answer hash;
- response hash in challenge/receipt == recomputed response hash;
- challenge expected-answer hash == externally frozen expected-answer hash;
- challenge is extraction/accessibility only;
- response/final-context budgets;
- no context eviction;
- output remains non-semantic/non-evidence.

A wrong non-empty answer must fail even when every metadata field is otherwise valid.

## 5. Prompt and witness qualification records need external provenance

Self-hashing a caller-created record is not a trust root.

PromptIsolationQualificationRecord and WitnessProtocolQualificationRecord must be bound to a platform-owned/independently qualified authority source.

At minimum add:

- authority/issuer ID;
- record version;
- signed or otherwise independently authenticated record digest;
- revocation/current-generation binding;
- issue/expiry time;
- exact provider/mode/prompt mode.

PredicateContext supplies the expected trust root/current generation.

A caller that constructs a self-consistent record cannot qualify itself.

## 6. Reviewer provenance must be authenticated

Current reviewer provenance checks only a policy hash and a nonempty authorization-source string.

Replace with a typed reviewer authorization/provenance record that binds:

- reviewer identity;
- review role/scope;
- authority issuer/trust root;
- authorization artifact hash/signature or independently verified authority reference;
- exact request/candidate/source identity;
- issue/expiry/revocation/current generation;
- allowed review disposition class.

A string such as `authorization_source="trusted-review-artifact"` is not authority.

Candidate/reviewer-written provenance cannot authorize itself.

## 7. Semantic coverage/context must be evidence-derived

### 7.1 Semantic context

Do not qualify semantic context merely because:

- source hash is nonempty;
- qualification receipt hash is nonempty;
- context bytes are omitted.

Bind the exact final-context bytes/hash or a separately qualified context-construction receipt proving the exact evidence/retrieval/tool outputs included.

### 7.2 Semantic coverage

Do not accept arbitrary nonempty `coverage_hash`.

Coverage must be recomputed from:

- required evidence/interaction contract;
- actual final-context member/range identities;
- representation/retrieval records;
- source hashes;
- explicit coverage algorithm/version.

Missing required semantic region must fail even with a syntactically valid coverage record.

## 8. Production statistical qualification must implement the frozen R5 protocol

Current R2B production mode does not compute the frozen statistical qualification; minimum trial counts are insufficient.

Implement the exact frozen R5 statistical protocol from the R5 design.

For the production qualification profile, recompute from immutable physical attempts:

- exact required trial/confirmation population;
- zero hard failures where required;
- no optional stopping;
- no failed-attempt replacement;
- no hidden retry;
- exact one-sided confidence calculation;
- required lower confidence bound / threshold;
- exact confidence level;
- exact qualification program/version.

Do not accept `statistical_qualified=True` as authority.

Do not allow a tiny deterministic test profile to satisfy the production predicate.

Use distinct predicates/profiles for:

- TEST_PROFILE — deterministic unit mechanics only, non-authoritative;
- R5_PRODUCTION — exact frozen qualification protocol.

Add RED tests showing a 2-trial/no-failure record cannot satisfy R5_PRODUCTION when the statistical threshold requires more evidence.

## 9. Persistent admission must not bypass generation when state hash is absent

The transactional ledger must always compare expected protected generation.

Do not condition the generation check on `expected_state_hash is not None`.

Required transaction:

1. BEGIN IMMEDIATE;
2. read protected generation + state hash;
3. require protected generation == expected generation;
4. if a state hash is required, require exact state hash;
5. check attempt terminal state;
6. write VOID/COMMITTED;
7. atomically advance generation/state token on COMMITTED;
8. commit.

Missing expected protected-state identity at an authority transition must fail closed.

### 9.1 Bind evidence verdict to CAS token

`admit_review_attempt_with_evidence()` must produce a content hash/token over:

- evidence bundle identity;
- predicate context identity;
- verdict predicate results;
- current protected generation/state token.

The same token must be checked/consumed inside the admission transaction.

Do not allow a gap where evidence is validated and unrelated current-state strings are later passed to CAS.

Add two-writer, ABA, restart, missing-state-hash and state-change-between-verdict-and-CAS tests.

## 10. Interaction co-context must be observed, not caller asserted

Production admissibility currently permits an `observed_interactions` value in the bundle.

Replace that with an observed-final-context record generated by the delivery/context assembly mechanism.

It must prove that each required interaction's evidence members actually coexisted in the same final adjudication context/session.

The caller/candidate cannot satisfy the predicate by copying RequiredInteractionContract into `observed_interactions`.

## 11. Representation governance must verify transformation outputs

RepresentationRecord must not qualify from nonempty hashes alone.

Authoritative validation must recompute/verify:

- transform ID;
- exact transform implementation hash/version;
- platform-owned transform-registry version;
- input source hashes;
- transform parameters;
- output representation bytes/hash;
- coverage map/hash.

A fabricated record with valid strings and no matching transform execution must fail.

## 12. Materialization must recurse and derive archive/symlink semantics

Current archive handling is only one level and does not derive all trusted metadata.

Required:

- recursively inspect nested archives up to the configured limit;
- derive recursion depth from traversal;
- derive compressed size from archive metadata;
- derive uncompressed size from extracted bytes;
- enforce decompression ratio at every level and cumulatively;
- inspect symlink entries represented by actual archive metadata;
- resolve symlink targets relative to containing directory and extraction root;
- reject links/archives that escape through chained/nested paths;
- enforce total/member/entry bounds across nested traversal.

Do not trust caller-provided recursion/size metadata as the proof.

## 13. A–T positive/negative cases must be independently executed

Current R2B still creates the positive case from the already-computed phase status.

For each phase, define explicit case functions/records before phase aggregation.

Run:

- positive case invocation independently;
- negative case invocation independently;
- mutation case(s) where applicable.

Then compute phase status only from those executed case artifacts.

Do not create:

`positive["result"] = existing_phase_status == PASS`

after the fact.

For phases G/I/O/T, consume actual frozen mutation/closure artifacts and verify their source/run identity.

## 14. Self-falsification must detect harness/cross-source false greens

Add independent self-falsification attacks for:

- wrong fixture target mapping;
- mutation catalog omission;
- grouped-mutation false coverage;
- transition-class self-downgrade;
- fence-version self-binding;
- wrong witness answer with valid metadata;
- forged prompt/witness self-hash;
- forged reviewer authorization-source string;
- fabricated semantic coverage hash;
- R5 production statistical under-sampling;
- CAS with missing expected state hash;
- state changes after admissibility before CAS;
- caller-copied observed interactions;
- fabricated representation record;
- nested archive recursion/decompression bomb;
- phase positive case synthesized from phase status.

Self-falsification must be authored independently from the normal mutation catalog and phase negative-case generator.

## 15. Evidence/package integrity

R2B S2/E2/P2 are preserved as historical superseded evidence.

After R2C fixes:

### S3
Commit only production/test/mutation/self-falsification/packet-builder sources.

### E3
Run exactly S3 and commit only generated result/log artifacts.

### P3
Commit only the independent review packet/prompt.

Every result artifact must bind:

- S3 commit;
- S3 tree;
- command;
- UTC;
- interpreter/runtime;
- exit status where available;
- source manifest/hash set.

Packet P3 must name S3 and E3 separately.

## 16. R2C exit criteria

Do not request external review until all are true:

1. mutation and fixture catalogs are separate from production registry and from each other;
2. real fixture catalog target mapping is part of exact closure;
3. every validator mutation targets exactly one production guard;
4. context transition/fence expectations are externally bound;
5. witness actual answer is cryptographically/content bound to trusted expected answer;
6. prompt/witness qualification records have external trust provenance/currentness;
7. reviewer provenance is independently authenticated;
8. semantic context/coverage is recomputed from actual final-context evidence;
9. R5 production statistical qualification is actually computed from the frozen protocol;
10. admission transaction always checks protected generation and binds verdict/evidence identity to CAS;
11. interaction co-context is generated from actual final context, not caller asserted;
12. representation proof is tied to actual transform execution/output;
13. materialization recursively derives archive/symlink/resource facts;
14. A–T positive/negative cases are independently executed case artifacts;
15. expanded independent self-falsification reports zero unresolved Critical/High;
16. fresh S3 -> E3 -> P3 sequence exists;
17. every test/mutation/falsification artifact is fresh and source-bound to S3;
18. EXP-M remains NOT_QUALIFIED;
19. live provider/API execution remains false;
20. authority effect remains NONE.

Then return `DETERMINISTIC_REVIEW_REQUIRED`.

## 17. No-stop continuation

If any R2C item remains automatable:

`AUTOMATABLE_WORK_REMAINS`

and continue automatically.

Do not stop after one fix, green test, mutation run, phase, source freeze or evidence generation.

Do not use live provider APIs.
