# EXP-M Deterministic Implementation — Internal Self-Adjudication R2D Remediation

Status: `AUTOMATABLE_WORK_REMAINS`

Authority effect: `NONE`

EXP-M remains `NOT_QUALIFIED`.

Live provider/API qualification and execution remain blocked.

This remediation supersedes the R2C external-review stop. Internal review of frozen R2C source `5fa8f07ad12e42c1bbf05b101ab69b9c7b351e3b` found remaining automatable Critical/High false-green paths. Do not send the R2C packet externally.

Preserve R2C S3/E3/P3 as superseded historical evidence. Do not rewrite it.

## 1. Remove fixture/test semantics from production admissibility

Production predicate behavior must never depend on test-fixture metadata.

Remove every production conditional based on fields such as:

- `__negative_target__`
- mutation target IDs
- fixture IDs
- test-case IDs

In particular, context-isolation, hidden-state, context-state and admission-fence predicates must each evaluate their real evidence unconditionally.

A candidate/evidence bundle containing fixture metadata must have no ability to disable or bypass any production predicate.

Also move fail-injection fields such as `force_*_failure` out of production evidence semantics. Test harnesses may wrap/mutate validators externally; production validators must not branch on test-only control fields.

Required attacks:

- set `__negative_target__=context_state_clean` on otherwise dirty evidence;
- set every known fixture/test marker in a candidate bundle;
- verify no predicate becomes easier to satisfy.

## 2. Context cleanliness must be derived from structured observations

`ProviderContextStateEvidence.clean` and `sentinel_passed` are diagnostic/cache values only, but the current validator does not independently derive a clean state.

Introduce structured per-channel observations, e.g.:

- channel ID/type;
- observed version/hash/value class;
- expected version/hash/value class from the frozen authority/context snapshot;
- readability/disablement/fence status;
- observation time/generation;
- trusted adapter identity.

Authoritative context-state validation must prove for every required observable semantic channel that the observed state equals the externally expected state or is disabled/fenced as required.

A self-consistent observation hash over `clean=True` or `clean=False` is not authority.

Required attacks:

- clean=False with self-consistent hash;
- sentinel_passed=False with self-consistent hash;
- missing required channel;
- stale channel generation;
- wrong config hash;
- hidden channel represented as observable clean;
- candidate-created observation record.

## 3. Fence currentness must be externally anchored

A self-hashed `AdmissionFenceRecord` is not itself proof that the protected resource accepted the fence.

Bind fence evidence to an external protected-resource/platform authority snapshot containing at least:

- protected resource ID;
- monotonic fence generation/version;
- authoritative current state hash/token;
- issuer/observer identity;
- artifact hash/attestation identity.

The validator must compare the observed fence to that trusted external state.

Candidate-created `AdmissionFenceRecord(version=expected, current=True)` must not be sufficient.

## 4. Permanent void must be persisted even on state/generation mismatch

Current compare-and-set mismatch behavior may return a VOID checkpoint without durably inserting terminal VOID.

Repair the ledger so any invalidation after an attempt has entered the governed admission window permanently records terminal VOID for that attempt, including:

- generation mismatch;
- state-hash mismatch;
- evidence-verdict token mismatch;
- authority/request/capability/egress/context/fence/prompt/witness/session/registry drift.

The transaction may refuse COMMITTED on protected-state mismatch, but it must still atomically record the attempt as terminal VOID without mutating the protected resource generation.

Required restart attack:

1. attempt observes drift;
2. admission returns VOID;
3. process restarts;
4. external state is restored to the old matching value;
5. same attempt tries COMMITTED;
6. result must remain terminal VOID.

## 5. Persistent ledger is mandatory for authority-bearing admission

No authority-bearing path may return `ADMITTED` when `ledger=None`.

Split diagnostic/test evaluation from authoritative admission.

For material admission:

- persistent transactional ledger required;
- absence/unavailability => fail closed;
- no in-memory fallback;
- durable terminal state required.

## 6. Evidence-verdict token must be governor-owned, not caller-minted

Do not accept `current["evidence_admission_token"]` as proof when the caller can compute the same public digest.

Create the admission candidate/token inside the trusted governor after evidence validation and bind it to:

- exact EvidenceBundle digest;
- exact PredicateContext digest;
- complete predicate result map;
- attempt ID;
- protected generation;
- protected state hash/token;
- registry version;
- creation nonce/sequence.

Persist or pass this token only through the trusted internal admission path.

The final transaction must compare it with the same protected generation/state observed inside the transaction.

Required attacks:

- caller fabricates a token;
- state changes after verdict before CAS;
- ABA state restoration;
- token replay on another attempt/generation;
- token replay after restart.

## 7. Implement the exact frozen R5 production statistical protocol

The frozen EXP-M/R5 protocol is authoritative:

- `p_min = 0.99`;
- one-sided 95% **exact Clopper–Pearson**;
- minimum 299/299 disjoint confirmation successes under zero failures;
- every attempted trial counts;
- zero hard failures;
- no exclusions/rerolls/optional stopping;
- exploration and confirmation disjoint;
- frozen trial IDs/schedule/interleaving seed before exposure;
- >=3 UTC days;
- >=4 time blocks/day;
- exact claimed operating point;
- production-equivalent request envelope/content class;
- append-only failure history;
- health check invalidates only and cannot renew;
- provider-side independence uncertainty is recorded as `STATISTICAL_INDEPENDENCE_UNPROVEN` and must not be silently converted into a universal probability claim.

Do not use a Wilson/normal approximation and do not use a 0.95 acceptance threshold.

For the all-success zero-failure case, compute the exact one-sided Clopper–Pearson lower bound deterministically. For general support, use a mathematically exact/validated beta-binomial implementation or fail closed outside the implemented exact case.

Mandatory boundaries:

- 298/298 must not satisfy the frozen minimum;
- 299/299 must satisfy the preregistered numerical threshold if all other frozen requirements are met;
- 299 attempts with one failure must fail;
- any retry/replacement must fail confirmation closure;
- missing scheduled slot counts as failure;
- exploration ID reused as confirmation fails;
- insufficient day/time-block diversity fails;
- independence unproven is surfaced as a nonclaim/risk state and cannot be silently erased.

`TEST_PROFILE` remains explicitly non-authoritative and cannot satisfy a production material-transition predicate.

## 8. Prompt/witness/reviewer authority must be non-self-forgeable

Self-hashing a record plus copying expected authority strings is not an authority proof.

Introduce a platform-owned trusted authority registry/snapshot outside candidate evidence containing exact authorized artifact digests/scopes/generations.

Prompt isolation, witness qualification and reviewer provenance must validate against this trusted snapshot.

Each trusted artifact must bind:

- issuer identity;
- artifact ID/hash;
- subject/provider/mode/reviewer;
- request/candidate/scope;
- generation;
- issue/expiry;
- revocation state;
- allowed transition/review class.

Candidate evidence supplies a reference to the artifact, not the trust root.

A caller that constructs a self-consistent record with copied issuer/digest strings must fail unless the exact externally registered artifact exists and its scope matches.

Required attacks:

- copied issuer ID/digest;
- forged self-hash;
- replay from another request/candidate;
- expired artifact;
- revoked artifact;
- wrong generation;
- wrong provider/mode/scope.

## 9. Semantic context must bind actual final-context bytes/assembly

`semantic_context_qualified` must not pass because source hash or qualification receipt hash is merely nonempty.

Require either:

1. exact final-context bytes with recomputed context hash; or
2. a trusted context-assembly receipt that binds every included member/range/tool-result and the resulting exact final-context hash.

The assembly receipt must be produced by the trusted delivery/context builder and be outside candidate write authority.

Omitted context bytes require the trusted assembly receipt; arbitrary nonempty receipt hash is insufficient.

## 10. Interaction co-context must be generated by the trusted context builder

`FinalContextInteractionEvidence.derived=True` is not authority.

Generate interaction evidence from the same trusted final-context assembly record used for semantic context.

Validate:

- request/attempt/session;
- final-context hash;
- member/range IDs;
- exact interaction membership;
- source/retrieval identity;
- builder/authority artifact identity.

A candidate-created `FinalContextInteractionEvidence` that copies the required interaction contract must fail.

## 11. Semantic coverage must bind actual final-context membership

Coverage cannot be computed only from manifest IDs.

Recompute coverage from:

- RequiredEvidenceContract;
- RequiredInteractionContract;
- trusted final-context assembly;
- exact representation/retrieval member/range IDs;
- final-context hash;
- source hashes;
- algorithm/version.

Require `coverage.evidence_ids` to exactly match the governed covered set.

A manifest may be complete while the final context is incomplete; that case must fail semantic coverage.

## 12. Accessibility proof must be policy- and witness-derived

`accessibility_proven` must validate against:

- exact ProviderAccessibilityRiskPolicy;
- transition class;
- deterministic-required rule;
- trusted witness challenge/expected answer;
- actual response hash;
- final-context assembly;
- provider/mode/prompt isolation;
- trusted authority record.

A proof whose `evidence_hash == digest(challenge)` is not enough by itself.

Highest material-authority transitions must fail if only probabilistic witness evidence is available where deterministic proof is required.

## 13. Archive/materialization limits must be enforced before decompression

Do not call `archive.read(member)` before validating size/ratio/resource limits from container metadata.

For every nested archive member:

- inspect `ZipInfo.file_size` and `compress_size` first;
- reject member/cumulative uncompressed size over limit before extraction;
- reject per-member/cumulative compression ratio over limit;
- enforce global member count across recursion;
- enforce recursion depth before descending;
- detect symlink entries from archive metadata before treating bytes as file content;
- resolve symlink targets under extraction root;
- prevent nested archive/path alias duplicates.

Add zip-bomb-style fixtures that must be rejected before large allocation/decompression.

## 14. Phase A–T must exercise the load-bearing production mechanisms

Positive/negative case results may be independently invoked, but each phase must test the actual mechanism claimed by that phase.

At minimum:

- F includes an explicit R5_PRODUCTION boundary family (298/298 fail, 299/299 pass, one failure fail), separate from TEST_PROFILE;
- K/R exercise trusted expected-answer verification and trusted witness authority, not only nonempty response/budget;
- L exercises full recursive typed materialization, not only `safe_archive_member`;
- O/T consume real registry + mutation catalog + real fixture catalog + executed mutation artifacts;
- P/Q exercise structured channel observations and external protected-resource fence authority;
- admission phase/cases exercise the mandatory persistent ledger and verdict-bound CAS token.

Phase status must be derived only from executed case artifacts. Do not maintain a parallel precomputed phase status that can disagree with the case records.

Each case artifact must record an invocation/output digest so packet review can prove it corresponds to an executed call.

## 15. Self-adjudication must be adversarial, not aggregate-only

The R2C self-adjudicator primarily rechecks that result files say PASS.

R2D self-adjudication must execute independent adversarial cases and must not hardcode claims such as `provider_execution_false=True`.

Verify live-provider non-execution from observable execution configuration/log/provider class/network stub evidence.

Add independent attacks for every item 1–14, especially:

- production `__negative_target__` bypass;
- clean=false self-consistent context hash;
- self-minted fence;
- nonpersisted VOID after state mismatch;
- authoritative admission with no ledger;
- caller-minted evidence token;
- 298/298 production statistical false-green;
- one-failure statistical case;
- forged prompt/witness/reviewer authority strings;
- semantic context with empty bytes + arbitrary receipt hash;
- candidate-created FinalContextInteractionEvidence;
- complete manifest but incomplete final context;
- accessibility proof with challenge hash only;
- zip bomb rejected before extraction;
- phase F/K/L/P/Q using shallow helper instead of load-bearing mechanism.

Internal self-adjudication returns zero Critical/High only when these attacks are behaviorally rejected.

## 16. Mutation/fixture closure hardening

Keep the separate registry/mutation/fixture modules.

Additionally require:

- mutation catalog is explicit records, not generated from the production registry;
- fixture catalog is the exact catalog used by `build_negative_fixture`;
- each fixture's expected rejection predicate is observed in the normal result;
- each isolated mutant changes exactly one validator;
- the mutant false-greens only after that exact guard is disabled;
- fixture-target typo fails closure;
- duplicate/missing/extra predicate, mutation or fixture target fails closure.

No production code may inspect fixture metadata to make this isolation possible.

## 17. Fresh source/evidence/packet sequence

R2C S3/E3/P3 remain immutable historical evidence.

After R2D repair:

### S4
Commit only source/test/mutation/self-adjudication/packet-builder changes.

### E4
Run exactly S4 and commit only fresh generated evidence/log/result artifacts.

Every evidence artifact must bind:

- S4 commit;
- S4 tree;
- command;
- UTC;
- interpreter/runtime;
- exit status;
- source manifest/hash set.

### P4
Commit only the external independent-review packet and prompt.

Packet must explicitly identify S4 and E4 and state that R2C is superseded.

## 18. R2D exit criteria

Do not request external review until all are true:

1. no production predicate behavior depends on fixture/test markers;
2. context cleanliness is derived from structured externally expected channel observations;
3. fence currentness is externally anchored;
4. every governed invalidation durably persists terminal VOID;
5. persistent ledger is mandatory for authority-bearing admission;
6. caller cannot mint the verdict/admission token;
7. exact frozen R5 0.99 / one-sided 95% exact Clopper–Pearson / 299-of-299 protocol is implemented;
8. statistical-independence uncertainty is preserved as a nonclaim/risk state;
9. prompt/witness/reviewer trust cannot be self-forged;
10. semantic context binds actual final-context bytes/assembly;
11. interaction co-context is trusted-builder derived;
12. semantic coverage binds actual final-context membership;
13. accessibility proof is policy/witness/final-context derived;
14. archive limits are enforced before decompression and recursively;
15. A–T phases exercise the actual load-bearing mechanisms;
16. mutation/fixture exact closure has no production test hook;
17. independent self-adjudication finds zero unresolved Critical/High;
18. fresh S4 -> E4 -> P4 exists;
19. all fresh evidence is source-bound to S4;
20. EXP-M remains NOT_QUALIFIED;
21. live provider/API execution remains false;
22. authority effect remains NONE.

Then return `DETERMINISTIC_REVIEW_REQUIRED`.

## 19. No-stop rule

If any R2D item remains automatable:

`AUTOMATABLE_WORK_REMAINS`

and continue automatically.

Do not stop after a green subtest, mutation run, phase, commit, source freeze or evidence generation.

Do not use live provider APIs.
