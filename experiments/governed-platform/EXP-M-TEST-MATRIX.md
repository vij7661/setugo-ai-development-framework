# EXP-M Review Evidence Delivery Integrity — Test Matrix

## Purpose

This matrix turns EXP-M into an executable falsification plan. It is intentionally split into deterministic platform tests first and live provider capability tests second.

No live provider pilot may be treated as scientific evidence until the deterministic governor tests are green.

## Phase A — Deterministic unit and state-machine tests

| ID | Test | Setup | Expected result |
|---|---|---|---|
| TM-A01 | Complete one-shot delivery | All mandatory items delivered exactly once | REVIEW_CONTEXT_QUALIFIED_AVAILABLE |
| TM-A02 | Required item missing | Remove one required item | EVIDENCE_DELIVERY_INCOMPLETE |
| TM-A03 | Optional item missing | Remove optional item | Complete if contract permits |
| TM-A04 | Manifest hash mismatch | Alter manifest after freeze | Reject |
| TM-A05 | Item byte mismatch | Change one source byte | Reject |
| TM-A06 | Item size mismatch | Correct hash metadata but wrong byte count | Reject |
| TM-A07 | Duplicate required item | Duplicate one item | Reject ambiguous/duplicate delivery |
| TM-A08 | Unexpected extra required-looking item | Add unmanifested item | Reject or quarantine; never silently bind |
| TM-A09 | Wrong reviewed commit | Reuse manifest against another commit | Reject |
| TM-A10 | Wrong ReviewRequest | Reuse corpus for another request | Reject |
| TM-A11 | Reviewer self-ack only | Reviewer claims all received; platform missing item | Incomplete |
| TM-A12 | HTTP 200 only | Provider call succeeds but no receipt evidence | Incomplete |
| TM-A13 | Upload ID only | File upload succeeds but model visibility unproven | Incomplete |
| TM-A14 | PASS before completeness | Early PASS returned | Verdict inadmissible |
| TM-A15 | CHANGES_REQUIRED before completeness | Early negative verdict | Diagnostic only |
| TM-A16 | INSUFFICIENT before completeness | Early insufficient verdict | Cause unresolved/delivery diagnostic, not scientific |
| TM-A17 | Scientific artifact absent | Required source does not exist | SCIENTIFIC_EVIDENCE_MISSING |
| TM-A18 | Artifact exists but omitted | Source exists but delivery omits it | EVIDENCE_DELIVERY_INCOMPLETE |
| TM-A19 | Unsupported format | Provider profile says unsupported | Fail preflight |
| TM-A20 | Unknown provider capability | No qualified profile | Fail preflight |

## Phase B — Chunk protocol tests

| ID | Test | Mutation | Expected result |
|---|---|---|---|
| TM-B01 | All chunks correct | None | Complete |
| TM-B02 | Missing final chunk | Drop N | Incomplete |
| TM-B03 | Missing middle chunk | Drop k | Incomplete |
| TM-B04 | Duplicate chunk | Duplicate k | Reject |
| TM-B05 | Duplicate+missing | Duplicate k, remove j | Detect both |
| TM-B06 | Reordered chunks | Shuffle | Canonical reconstruction or reject |
| TM-B07 | Corrupted chunk | Change one byte | Hash mismatch |
| TM-B08 | Same index, different bytes on retry | Retry mutated k | Reject |
| TM-B09 | Cross-request chunk | Chunk from old request | Reject |
| TM-B10 | Cross-corpus chunk | Correct request, wrong corpus hash | Reject |
| TM-B11 | Wrong total count | Change N | Reject |
| TM-B12 | Wrong chunk index | Out-of-range or repeated index | Reject |
| TM-B13 | Empty mandatory chunk | Replace content with empty bytes | Reject |
| TM-B14 | Chunk metadata only | Claim hash/count without bytes | Incomplete |
| TM-B15 | Stale receipt | Receipt from older corpus | Reject |
| TM-B16 | Receipt missing item IDs | Count matches but IDs absent | Incomplete |
| TM-B17 | Receipt count lies | Says N while delivery has N-1 | Independent check rejects |
| TM-B18 | Completion before last chunk | Reviewer marks complete early | Reject |

## Phase C — Context and representation tests

| ID | Test | Setup | Expected result |
|---|---|---|---|
| TM-C01 | Tail truncation | Decisive artifact last | Preflight block or detectable incomplete |
| TM-C02 | Middle truncation | Decisive artifact in middle | Detect item/chunk gap |
| TM-C03 | Large prompt crowd-out | Prompt consumes context | Required evidence cannot be silently dropped |
| TM-C04 | ZIP unsupported | ZIP required; provider lacks archive visibility | EVIDENCE_FORMAT_UNSUPPORTED |
| TM-C05 | TAR unsupported | TAR required; provider lacks archive visibility | EVIDENCE_FORMAT_UNSUPPORTED |
| TM-C06 | PDF partial visibility | Only some pages exposed | Partial coverage, not complete |
| TM-C07 | Markdown-only substitution | Raw JSON required but summary Markdown sent | Representation mismatch |
| TM-C08 | Encoding transformation | CRLF/UTF-8/normalization changes bytes | Raw-hash mismatch where byte identity required |
| TM-C09 | Binary corruption | Attachment bytes altered | Reject |
| TM-C10 | Attachment accepted but inaccessible | Upload succeeds, reviewer cannot inspect | EVIDENCE_ATTACHMENT_UNAVAILABLE |
| TM-C11 | Summary substitutes raw log | Proposer summary replaces required raw log | Reject |
| TM-C12 | Prompt states missing evidence contents | Evidence absent; prompt describes it | Reject |
| TM-C13 | Citation to undelivered evidence | Reviewer cites manifest-only item | Coverage not TESTED_SUPPORTED |
| TM-C14 | Partial file accepted as whole | Only prefix delivered | Incomplete |

## Phase D — Insufficient-evidence cause adjudication

| ID | Scenario | Expected classification |
|---|---|---|
| TM-D01 | Required artifact never existed | SCIENTIFIC_EVIDENCE_MISSING |
| TM-D02 | Artifact existed, not materialized | EVIDENCE_MATERIALIZATION_FAILED |
| TM-D03 | Materialized, omitted from request | EVIDENCE_DELIVERY_INCOMPLETE |
| TM-D04 | Delivered file ref but provider cannot expose it | EVIDENCE_ATTACHMENT_UNAVAILABLE |
| TM-D05 | Corpus exceeds qualified context | REVIEW_CONTEXT_INCOMPLETE |
| TM-D06 | Required format unsupported | EVIDENCE_FORMAT_UNSUPPORTED |
| TM-D07 | Reviewer says insufficient, platform cause unknown | INSUFFICIENT_EVIDENCE_CAUSE_UNRESOLVED |
| TM-D08 | Scientific + delivery gaps both exist | MIXED_INSUFFICIENCY |
| TM-D09 | Reviewer claims missing item that was verifiably delivered | REVIEWER_EVIDENCE_ASSESSMENT_CONTRADICTION |
| TM-D10 | Platform claims delivery but receipt/manifest disagree | EVIDENCE_RECEIPT_UNPROVEN |

## Phase E — Multi-reviewer equivalence tests

| ID | Test | Expected result |
|---|---|---|
| TM-E01 | Claude and DeepSeek receive identical manifest/hash | Results comparable subject to semantic review |
| TM-E02 | One receives raw JSON, other receives only summary | Not equivalent consensus |
| TM-E03 | One provider complete, one incomplete | Incomplete verdict non-promotable |
| TM-E04 | One provider supports file, other ignores it | Provider-specific delivery states preserved |
| TM-E05 | Different chunking but same canonical corpus | Comparable only if reconstruction proves equivalent corpus |
| TM-E06 | Different required item set | Not comparable |
| TM-E07 | Retry one reviewer with changed corpus | New delivery boundary required |
| TM-E08 | Two reviewers agree after one incomplete delivery | Consensus cannot bypass incomplete evidence |

## Phase F — Provider capability qualification

For each exact provider/account/endpoint/region/model/deployment/adapter/session/file/retrieval mode, execute separate exploration and confirmation fixtures.

Default material-review confirmation policy:

- target per-trial success lower bound: p_min=0.99;
- one-sided 95% exact Clopper–Pearson;
- minimum **299/299** successful confirmation trials at each claimed operating point;
- zero hard failures;
- every attempted confirmation trial counts, including timeout/provider error/rate limit/ambiguous/unverifiable outcomes;
- no exclusions, rerolls, optional stopping, or backfilling failed attempts;
- exploration and confirmation trial sets are disjoint;
- confirmation trial IDs/schedule are frozen before exposure;
- confirmation trials span at least 3 UTC days and 4 preregistered time blocks/day, with operating points interleaved in randomized order;
- exact claimed operating point is tested; no interpolation or monotonicity assumption;
- production-equivalent prompt/tools/structured-output/output budget and worst-case token-density/media classes are used;
- 80% scalar cap is an additional margin only on a point that itself qualifies;
- append-only failure history persists across requalification within the same drift epoch;
- profile expiry is 7 days by default and immediate on material drift;
- health checks may invalidate but never renew.

Hard failure includes any required range/witness/context/session/model/wire/retrieval mismatch, timeout/provider error/rate limit, ambiguous result, or output failure preventing protocol completion.

Required measurements include:

1. exact production-equivalent one-shot corpus points;
2. attachment visibility by media/modality class;
3. attachment count/per-file boundaries;
4. staged context behavior;
5. dense per-slice content-bound witness behavior;
6. deterministic retrieval/access logging where used;
7. context-tail and internal omission behavior;
8. retry/fallback behavior;
9. provider-context state readback/sentinel behavior;
10. exact model/deployment/account/endpoint identity;
11. post-SDK transport-semantic envelope identity;
12. profile invalidation/drift signals.

Each attempted trial records the complete operating-point tuple, trial ID, exploration/confirmation class, scheduled time block, provider/context-state evidence, wire hashes, witness/retrieval results, response state, and hard-failure classification.

Vendor documentation may inform exploration but never replaces confirmation.

## Phase G — Unified mutation suite

The matrix and experiment use this single authoritative mutation catalog. Starting from one complete admissible review attempt, mutate one load-bearing field or one validator predicate at a time.

Data/state mutations must cover at least:

1. force context_complete/received_all;
2. lower required item/chunk counts;
3. mark required item optional;
4. omit governed evidence/dimension/interaction;
5. rebind request/corpus/manifest/evidence ID;
6. ignore missing/duplicate/corrupt chunk;
7. trust HTTP/upload/file ID/reviewer receipt/citation;
8. swap scientific vs delivery insufficiency causes;
9. use unknown/expired/candidate-authored capability profile;
10. ignore provider model/account/endpoint/region drift;
11. inherit qualification across provider/model fallback;
12. use dirty/reused provider context;
13. ignore memory/custom-instruction/connector drift;
14. accept incomplete/lying ProviderContextStateEvidence;
15. accept fewer than 299 confirmation trials;
16. discard/reroll a failed trial;
17. reuse exploration trials as confirmation;
18. ignore confirmation schedule/time-block requirements;
19. qualify a non-production envelope/content class;
20. skip 80% scalar cap where applicable;
21. accept sparse witness coverage for unprobed regions;
22. preserve framing canary while dropping challenged content;
23. accept model-selected retrieval without deterministic coverage logs;
24. accept partial/wrong-version retrieval log;
25. trust lossy/untrusted transformation;
26. bypass egress policy;
27. accept archive traversal/resource-limit defect;
28. allow evidence-ID collision;
29. re-read mutable source after freeze;
30. ignore capability/egress/context expiry or revocation;
31. revive a voided attempt after later requalification;
32. admit ungoverned reviewer-tool evidence;
33. omit machine-checkable prompt-isolation qualification.

Validator-logic mutations must cover at least:

34. delete each VerdictAdmissibilityResult conjunct one at a time;
35. replace required-evidence equality with subset/superset;
36. bypass GovernanceAuthoritySnapshot/base-head merge;
37. accept unknown/empty transition class;
38. skip clean-context check;
39. accept 298 instead of 299 confirmation trials;
40. accept one hard confirmation failure;
41. skip per-attempt content-bound witness;
42. skip retrieval-log coverage;
43. skip RequiredInteractionContract raw co-context requirement;
44. skip pre-dispatch state revalidation;
45. skip final atomic compare-and-set admission;
46. allow requalification to revive an invalidated attempt;
47. skip PromptIsolationQualificationRecord check.

Every logic mutation must be killed by at least one independently targeted test.

Required final result:

`surviving_material_false_green_mutations = 0`

## Phase H — Crash/retry and persistence tests

1. Crash after manifest freeze, before first chunk.
2. Crash mid-chunk sequence.
3. Crash after all chunks but before completeness result.
4. Crash after reviewer receipt, before final review.
5. Retry exact frozen delivery.
6. Retry with mutated corpus.
7. Concurrent duplicate deliveries for same request.
8. Resume after process restart.
9. Preserve failed attempt history.
10. Ensure prior incomplete attempt cannot be reclassified as complete by later retry.

## Phase I — Admissibility integration tests

A review result must be non-promotable when any load-bearing predicate is false:

- current ReviewRequest valid;
- GovernanceAuthoritySnapshot current and outside candidate write authority;
- RequiredEvidenceContract resolved/non-vacuous/closed;
- RequiredInteractionContract resolved and raw co-context requirements satisfied;
- complete materialization;
- governed representation/transformation;
- current egress authorization;
- ProviderCapabilityProfile statistically qualified for exact operating point;
- ProviderContextStateEvidence clean/current;
- provider mutable semantic-context qualification satisfied;
- trusted adapter/post-SDK wire binding valid;
- complete required item/chunk delivery;
- per-attempt content-bound witness valid or deterministic retrieval/range proof complete;
- session/file/retrieval coverage valid;
- PromptIsolationQualificationRecord current/matching;
- semantic review coverage valid;
- reviewer provenance/independence valid;
- promotable disposition;
- atomic compare-and-set state versions unchanged.

Test dispositions:

- PASS + any false predicate => non-promotable.
- BOUNDED_PASS + incomplete mandatory evidence/context => non-promotable.
- CHANGES_REQUIRED + incomplete delivery => diagnostic only.
- INSUFFICIENT_EVIDENCE + multiple causes => MIXED_INSUFFICIENCY with all cause predicates.
- PASS + all delivery predicates => delivery layer permits downstream authority gate only; it does not itself promote.

## Phase J — Trust-root, wire, representation, and egress tests

| ID | Test | Expected result |
|---|---|---|
| TM-J01 | Manifest marks governed required item optional | Required-evidence closure fails |
| TM-J02 | Manifest omits governed evidence ref entirely | Preflight fails before provider call |
| TM-J03 | Candidate supplies permissive provider profile | Profile rejected as untrusted |
| TM-J04 | Provider profile expired | Requalification required |
| TM-J05 | Provider model/adapter version drifts from profile | Profile invalid |
| TM-J06 | Manifest complete but trusted adapter omits item from wire body | Wire mismatch; verdict inadmissible |
| TM-J07 | Adapter changes system/developer prompt on retry | Wire hash mismatch |
| TM-J08 | Adapter changes tool/file bindings on retry | Wire/session mismatch |
| TM-J09 | Receipt session A, verdict session B | Verdict inadmissible |
| TM-J10 | Stateless verdict request omits earlier required evidence | Incomplete |
| TM-J11 | Opaque file ID from another attempt/session | Reject |
| TM-J12 | Provider file expired between receipt and verdict | Context incomplete |
| TM-J13 | Chunk sequence individually fits but cumulative final context does not | Preflight fails; chunking cannot expand context |
| TM-J14 | Persistent/model-selected retrieval binds file IDs but has no deterministic per-attempt range-access logs | Diagnostic-only; NOT_QUALIFIED_FOR_MATERIAL_REVIEW |
| TM-J15 | Full raw required, partial PDF/text extraction delivered | Representation incomplete |
| TM-J16 | Transformation tool/version/hash mismatch | Reject |
| TM-J17 | Lossy transform not explicitly permitted | Reject |
| TM-J18 | Data classification forbids provider egress | Preflight blocks |
| TM-J19 | Silent redaction of required evidence | Incomplete/unqualified representation |
| TM-J20 | Permitted redaction preserves all load-bearing fields | Eligible only if governed transformation rule says sufficient |
| TM-J21 | All delivery checks pass but EXP-L/prompt-isolation dependency unqualified | Material verdict non-promotable |
| TM-J22 | Two subreviews pass but defect exists only across evidence subsets | No global PASS |
| TM-J23 | Aggregator lacks cross-evidence interaction corpus | Global disposition blocked |
| TM-J24 | Aggregation contract includes interaction evidence and qualified aggregator | Eligible for downstream review validation |
| TM-J25 | Reviewer self-receipt claims inaccessible file visible | Platform delivery/capability record wins; incomplete |
| TM-J26 | Provider docs claim large context but empirical qualified profile is smaller | Empirical qualified bound governs |
| TM-J27 | Provider capability registry record candidate-writable | Profile untrusted |
| TM-J28 | Egress policy record candidate-writable | Egress decision untrusted |
| TM-J29 | Wire record excludes semantic field from canonical hash | Test must fail; semantic request binding incomplete |
| TM-J30 | Secret redaction from wire hash removes only credentials, not semantics | Reproducible semantic wire binding passes |

## Phase K — Remote accessibility witness and retrieval grounding tests

| ID | Test | Expected result |
|---|---|---|
| TM-K01 | Reviewer echoes manifest IDs but fails fresh hidden content canary | Context accessibility not qualified |
| TM-K02 | Fresh beginning/middle/end canaries all recovered exactly but internal regions are unprobed | Diagnostic only; cannot qualify full required content |
| TM-K03 | Tail canary missing near context limit | Safe qualified limit lowered; review over limit blocked |
| TM-K04 | Middle canary missing while head/tail pass | Internal omission detected |
| TM-K05 | Canary from prior attempt replayed | Attempt/session binding rejection |
| TM-K06 | Candidate learns/controls canary before delivery | Probe invalid; cannot establish accessibility |
| TM-K07 | Candidate modifies capability registry record | Profile untrusted |
| TM-K08 | Capability registry commit/profile changes with candidate under review | Self-approval boundary violation |
| TM-K09 | Provider file citation with no successful retrieval log in retrieval-required mode | Coverage cannot be TESTED_SUPPORTED |
| TM-K10 | Retrieval log resolves wrong content hash/version | Evidence identity mismatch |
| TM-K11 | Retrieval log shows access after verdict generation | Verdict timing invalid |
| TM-K12 | Receipt and canary probes pass but final adjudication occurs in another session | Session mismatch |
| TM-K13 | Stateless final request omits canary-qualified earlier evidence | Incomplete final context |
| TM-K14 | Same-session final review fits qualified context and every required slice passes per-attempt content-bound challenge | Eligible for downstream semantic validation subject to residual-risk policy |
| TM-K15 | Canary value copied into prompt/manifest | Probe invalid because value is not evidence-access dependent |

## Phase L — Delivery-governor trust, parser safety, and provider-drift tests

| ID | Test | Expected result |
|---|---|---|
| TM-L01 | Candidate branch edits manifest builder to omit decisive evidence | Candidate implementation cannot authorize its own delivery |
| TM-L02 | Candidate edits completeness validator to always return true | Trusted platform validator wins; review blocked |
| TM-L03 | Candidate provides its own capability profile | Profile rejected |
| TM-L04 | Candidate provides its own representation transformer | Transformer rejected as untrusted |
| TM-L05 | Archive contains `../` traversal | Safe materializer rejects |
| TM-L06 | Archive contains absolute-path member | Reject |
| TM-L07 | Archive contains symlink escape | Reject |
| TM-L08 | Archive contains duplicate normalized member names | Reject ambiguity |
| TM-L09 | Decompression expansion exceeds size limit | Fail closed without resource exhaustion |
| TM-L10 | Parser exceeds time/memory budget | Fail closed |
| TM-L11 | Two evidence paths normalize to same stable ID | Collision detected |
| TM-L12 | Two different hashes attempt same declared evidence ID | Collision/rebind rejected |
| TM-L13 | One near-limit provider canary run succeeds, subsequent fresh trials fail | Qualified limit not widened |
| TM-L14 | Repeated trials all pass below conservative margin | Bound may be qualified under policy |
| TM-L15 | Same model alias reports different backend/deployment | Drift invalidates profile or requires bounded requalification |
| TM-L16 | Qualified endpoint/region differs from actual call | Fail |
| TM-L17 | Qualified account/tenant differs from actual call | Fail |
| TM-L18 | Primary provider failure triggers fallback with primary profile | Fail/new delivery boundary required |
| TM-L19 | Fallback has its own qualified profile and new attempt | Eligible for downstream validation |
| TM-L20 | File upload accepted but processing/indexing pending | Context incomplete |
| TM-L21 | File later becomes ready in same bound session | May proceed only after new readiness evidence |
| TM-L22 | Retrieval returns only snippet of full-required file | Coverage insufficient |
| TM-L23 | Retrieval returns exact required full content/hash | Eligible for downstream semantic coverage |
| TM-L24 | Candidate modifies egress decision/profile | Untrusted; delivery blocked |

## Phase M — TOCTOU and reviewer-tool boundary tests

| ID | Test | Expected result |
|---|---|---|
| TM-M01 | Source file mutated after manifest hash before upload | Frozen bytes used or mismatch detected |
| TM-M02 | Generated representation mutated after freeze | Representation/wire mismatch |
| TM-M03 | Capability profile expires between preflight and final call | Block completion |
| TM-M04 | Egress authorization revoked before send | Block dispatch |
| TM-M05 | Provider file replaced/mutated after qualification | File identity/access mismatch |
| TM-M06 | Final review uses stale provider file version | Verdict inadmissible |
| TM-M07 | Reviewer web search finds ungoverned evidence and uses it for PASS | Cannot count as frozen review evidence |
| TM-M08 | Reviewer tool fetches different revision of governed file | Revision/hash mismatch |
| TM-M09 | Governed supplemental tool evidence captured with provenance | Requires explicit supplemental/new boundary; not silent rebind |
| TM-M10 | Tool result omitted from audit record but cited in verdict | Coverage invalid |
| TM-M11 | Candidate changes source path after preflight but before adapter serialization | No TOCTOU substitution |
| TM-M12 | Retry after state drift reuses old attempt identity | Reject/new attempt required |

## Phase N — External-review remediation tests

| ID | Test | Expected result |
|---|---|---|
| TM-N01 | Governing standard requires evidence E; ReviewRequest omits E | EVIDENCE_SELECTION_INCOMPLETE before manifest freeze |
| TM-N02 | Governing standard requires mandatory dimension D; ReviewRequest omits D | ReviewRequest rejected |
| TM-N03 | ReviewRequest/manifest are internally closed but RequiredEvidenceContract contains extra mandatory ref | Required-evidence closure fails |
| TM-N04 | Reused provider thread contains prior ungoverned user message | Material review context dirty; verdict inadmissible |
| TM-N05 | Reused provider thread contains prior tool result | Context dirty unless fully governed and bound |
| TM-N06 | Fresh provider session contains only frozen governed content | Session cleanliness passes subject to provider profile |
| TM-N07 | Provider account/project custom instruction changes after qualification | Provider mode/profile invalidated |
| TM-N08 | Provider memory is enabled and cannot be disabled/captured | NOT_QUALIFIED_FOR_MATERIAL_REVIEW |
| TM-N09 | Provider-side knowledge connector enabled but absent from manifest/profile | NOT_QUALIFIED_FOR_MATERIAL_REVIEW |
| TM-N10 | Provider exposes fixed service policy but no mutable account/session context | May proceed only under qualified provider profile/nonclaim |
| TM-N11 | 298/298 disjoint confirmation trials pass | Insufficient trials; operating point unqualified |
| TM-N12 | 299/299 scheduled disjoint confirmation trials pass | Statistical criterion satisfied at exact tested point, subject to all other gates |
| TM-N13 | 298 successes + 1 hard failure | Operating point disqualified; failed attempt remains append-only |
| TM-N14 | One ambiguous/timeout/provider-error trial among 299 attempts | Counts as hard failure; disqualify point |
| TM-N15 | Smallest observed failure boundary B; profile claims >0.8B | Profile invalid |
| TM-N16 | No failure observed; profile claims >80% of largest tested passing point | Profile invalid |
| TM-N17 | Profile older than 7 days without requalification | Expired |
| TM-N18 | Sparse head/middle/tail canaries pass while internal segment omitted | Claimed range unqualified |
| TM-N19 | Every slice <=min(2048 bytes,512 provider tokens) passes content-bound challenge in every confirmation trial | Qualification accessibility criterion may pass for bounded failure model |
| TM-N20 | One dense segment witness fails | Operating point fails |
| TM-N21 | Opaque attachment has required pages/ranges not individually probed and no deterministic access logs | Full artifact mode unqualified |
| TM-N22 | Per-attempt deterministic retrieval logs prove hash-matched access to every required range/page/member | Eligible for downstream semantic validation |
| TM-N23 | Proposer interaction list omits platform-derived required interaction | Aggregation/global verdict blocked |
| TM-N24 | Platform RequiredInteractionContract and proposer plan match completely | Interaction closure passes |
| TM-N25 | Capability profile expires after provider response but before atomic verdict admission | Attempt permanently void; later requalification cannot revive it |
| TM-N26 | Egress permission revoked after provider response but before atomic verdict admission | Attempt permanently void; new attempt required |
| TM-N27 | Session/file state invalidates after provider response but before verdict admission | Verdict blocked |
| TM-N28 | Deployment identity is required by drift policy but provider cannot expose it | Identity-dependent qualification not claimable |
| TM-N29 | Retrieval logs required for completeness but provider does not expose them | Retrieval-based mode unqualified |
| TM-N30 | Dirty-session review returns PASS with otherwise perfect manifest/wire records | PASS remains inadmissible |

## Phase O — Validator-logic mutation tests

| ID | Logic mutation | Expected result |
|---|---|---|
| TM-O01 | Delete governed authority-snapshot predicate | Killed |
| TM-O02 | Derive contract from candidate HEAD only | Killed |
| TM-O03 | Replace evidence closure equality with subset | Killed |
| TM-O04 | Accept unknown transition class/empty contract | Killed |
| TM-O05 | Delete clean-context predicate | Killed |
| TM-O06 | Trust provider context readback without sentinel qualification | Killed |
| TM-O07 | Change 299 minimum to 298 | Killed |
| TM-O08 | Permit one hard confirmation failure | Killed |
| TM-O09 | Allow excluded/rerolled failure | Killed |
| TM-O10 | Reuse exploration as confirmation | Killed |
| TM-O11 | Skip confirmation schedule/time-block check | Killed |
| TM-O12 | Skip production-envelope operating-point equality | Killed |
| TM-O13 | Replace content-bound per-slice witness with framing-only canary | Killed |
| TM-O14 | Make per-attempt witnesses optional | Killed |
| TM-O15 | Make retrieval logs optional for model-selected retrieval | Killed |
| TM-O16 | Accept partial retrieval coverage | Killed |
| TM-O17 | Omit one RequiredInteractionContract raw evidence ref | Killed |
| TM-O18 | Let aggregator use subreview summaries instead of raw interaction evidence | Killed |
| TM-O19 | Skip prompt-isolation qualification predicate | Killed |
| TM-O20 | Skip pre-dispatch monotonic state check | Killed |
| TM-O21 | Skip atomic admission CAS | Killed |
| TM-O22 | Permit later requalification to revive old response | Killed |
| TM-O23 | Remove mixed-cause adjudication and first-match scientific cause | Killed |
| TM-O24 | Accept reviewer contradiction code absent from taxonomy | Killed |
| TM-O25 | Delete ProviderAccessibilityRiskPolicy predicate | Killed |
| TM-O26 | Delete AdmissionFence/version predicate | Killed |
| TM-O27 | Reintroduce legacy REVIEW_CONTEXT_COMPLETE as authority | Killed |
| TM-O28 | Infer statistical independence from fresh request IDs only | Killed |
| TM-O29 | Accept retrieval-open log without returned bytes/context binding | Killed |
| TM-O30 | Delete ReviewRequest current/integrity predicate | Killed by stale/wrong-request fixture |
| TM-O31 | Delete GovernanceAuthoritySnapshot predicate | Killed by authority-snapshot mismatch fixture |
| TM-O32 | Delete RequiredEvidenceContract resolved/non-vacuous/closed predicate | Killed by missing/empty-contract fixture |
| TM-O33 | Delete RequiredInteractionContract predicate | Killed by omitted-interaction fixture |
| TM-O34 | Delete complete materialization predicate | Killed by materialization-missing fixture |
| TM-O35 | Delete governed representation/transformation predicate | Killed by lossy/untrusted-transform fixture |
| TM-O36 | Delete current egress authorization predicate | Killed by egress-denied/revoked fixture |
| TM-O37 | Delete exact-operating-point capability qualification predicate | Killed by unqualified/expired/profile-mismatch fixture |
| TM-O38 | Delete ProviderAccessibilityRiskPolicy predicate | Killed by missing/wrong-proof-mode fixture |
| TM-O39 | Delete ProviderContextIsolationPolicy predicate | Killed by hidden-state-policy fixture |
| TM-O40 | Delete hidden-state-residual transition-policy predicate | Killed by highest-authority residual-disallow fixture |
| TM-O41 | Delete ProviderContextStateEvidence predicate | Killed by lying/dirty-state fixture |
| TM-O42 | Delete AdmissionFenceRecord/version predicate | Killed by provider-config race fixture |
| TM-O43 | Delete provider mutable-semantic-context qualification predicate | Killed by memory/custom-instruction/connector fixture |
| TM-O44 | Delete trusted adapter/post-SDK wire-binding predicate | Killed by SDK/wire mutation fixture |
| TM-O45 | Delete complete required item/chunk delivery predicate | Killed by missing/duplicate/corrupt item fixture |
| TM-O46 | Delete per-attempt accessibility proof predicate | Killed by canary-preserving/content-loss fixture |
| TM-O47 | Delete session/file/retrieval coverage predicate | Killed by partial/unbound retrieval fixture |
| TM-O48 | Delete PromptIsolationQualificationRecord predicate | Killed by missing/expired/wrong-mode isolation fixture |
| TM-O49 | Delete semantic review coverage predicate | Killed by untested mandatory-dimension fixture |
| TM-O50 | Delete reviewer provenance/independence predicate | Killed by self/untrusted-reviewer fixture |
| TM-O51 | Delete promotable-disposition predicate | Killed by CHANGES_REQUIRED/INSUFFICIENT disposition fixture |
| TM-O52 | Delete WitnessProtocolQualificationRecord/context-budget predicate when witnesses are used | Killed by witness-eviction/stale-record fixture |
| TM-O53 | Trust candidate-authored WitnessProtocolQualificationRecord | Killed |
| TM-O54 | Ignore provider-isolation documentation/account-class/config-template drift | Killed |

## Phase P — R3 residual adversarial-oracle tests

| ID | Test | Expected result |
|---|---|---|
| TM-P01 | Candidate edits governing standard to remove decisive requirement | Base/head conservative authority snapshot preserves requirement |
| TM-P02 | Candidate supplies weaker classification/relationship metadata | External registry wins; candidate metadata ignored/rejected |
| TM-P03 | Unknown class deterministically derives zero refs | EVIDENCE_SELECTION_CONTRACT_UNRESOLVED |
| TM-P04 | Lying context readback says clean while sentinel proves hidden memory | ProviderContextStateEvidence fails |
| TM-P05 | Hidden mutable provider channel cannot be read or disabled | NOT_QUALIFIED_FOR_MATERIAL_REVIEW |
| TM-P06 | Context config changes between preflight and dispatch | Attempt blocked/void |
| TM-P07 | Context config changes after response before admission | Atomic CAS fails; attempt void |
| TM-P08 | 299 confirmation attempts performed in one burst | Protocol invalid despite successes |
| TM-P09 | Failed attempt is excluded then 299 successes collected | Qualification fails; no optional stopping |
| TM-P10 | Exploration trials counted as confirmation | Qualification fails |
| TM-P11 | Easy synthetic confirmation but production envelope is token-dense/tools-enabled | Operating point mismatch |
| TM-P12 | Framing canary survives while challenged content extract is dropped | Content-bound witness fails |
| TM-P13 | Unchallenged sub-slice content selectively lost | Residual risk/nonclaim recorded; high-risk class requiring deterministic proof blocks |
| TM-P14 | Retrieval mode supplies file IDs/citations but no access logs | Diagnostic-only |
| TM-P15 | Access log covers all but one required range | PROVIDER_RETRIEVAL_COVERAGE_UNPROVEN |
| TM-P16 | Capability expires, then is requalified before checkpoint | Old attempt remains void |
| TM-P17 | Authority/capability/egress/session version changes between validation and CAS | Checkpoint write fails |
| TM-P18 | Prompt-isolation record expired/wrong provider mode | Verdict inadmissible |
| TM-P19 | Interaction family requires raw evidence A+B; aggregator sees only subreview outputs | Global disposition blocked |
| TM-P20 | SDK mutates semantic tool/model/file field after platform hash but before transport-bound hash | Transport-bound mismatch detected |
| TM-P21 | Provider default deployment identity required but unavailable | Provider/mode NOT_QUALIFIED |
| TM-P22 | Reviewer says evidence missing while strong per-attempt access proof exists | REVIEWER_EVIDENCE_ASSESSMENT_CONTRADICTION diagnostic; not silently scientific failure |

## Phase Q — Accessibility-risk and admission-fence tests

| ID | Test | Expected result |
|---|---|---|
| TM-Q01 | Transition class has no ProviderAccessibilityRiskPolicy | Review ineligible |
| TM-Q02 | Highest-authority transition uses probabilistic witnesses without deterministic range proof | Admissibility fails |
| TM-Q03 | Lower transition class explicitly permits bounded probabilistic witness mode and all predicates pass | Eligible subject to recorded residual risk |
| TM-Q04 | Mutable provider config has neither readable version nor fence | NOT_QUALIFIED_FOR_MATERIAL_REVIEW |
| TM-Q05 | AdmissionFenceRecord changes between final read and CAS | Atomic admission fails |
| TM-Q06 | Candidate/user tries to mutate dedicated-account config while fence held | Write blocked or version mismatch; attempt void |
| TM-Q07 | Provider-internal state changes without observable version/fence | Mode unqualified |
| TM-Q08 | Legacy REVIEW_CONTEXT_COMPLETE=true injected | Ignored/deprecated; cannot authorize |
| TM-Q09 | Verdict record omits residual/nonclaim risk for probabilistic mode | Admissibility fails |
| TM-Q10 | Accessibility proof mode does not satisfy transition-class policy | Admissibility fails |
| TM-Q11 | Fresh request IDs but correlated route/deployment/time burst | Statistical independence remains unproven; no universal probability claim |
| TM-Q12 | Retrieval log records open/citation but no returned-content hash | Retrieval context binding unproven |
| TM-Q13 | Retrieval returns correct bytes but tool-result message is absent from final adjudication context | Retrieval context binding unproven |
| TM-Q14 | Hidden unexposed mutable provider semantic state; no ProviderContextIsolationPolicy | NOT_QUALIFIED_FOR_MATERIAL_REVIEW |
| TM-Q15 | Highest-authority transition tries dedicated-account hidden-state residual | Blocked; residual defaults DISALLOW |
| TM-Q16 | Dedicated lower-authority transition explicitly permits dedicated-account residual with pinned policy/config/sentinel evidence | Eligible only with residual/nonclaim recorded |
| TM-Q17 | Sentinel qualification writes memory/customization into production review account | Qualification invalid |
| TM-Q18 | Health check succeeds after ProviderCapabilityProfile expiry | Profile remains expired; full confirmation requalification required |
| TM-Q19 | Same-dimension governing semantic change has no defined comparator | EVIDENCE_SELECTION_CONTRACT_UNRESOLVED |
| TM-Q20 | Mutate evidence-set union to intersection | Comparator mutation killed |
| TM-Q21 | Mutate allowed-provider set intersection to union | Comparator mutation killed |
| TM-Q22 | Mutate shorter-expiry-is-stricter to longer-expiry-is-stricter | Comparator mutation killed |

## Phase R — Witness noninterference and context-budget tests

| ID | Test | Expected result |
|---|---|---|
| TM-R01 | Preflight excludes witness challenge/response budget | Delivery plan rejected |
| TM-R02 | Actual witness response exceeds preregistered maximum and pushes context over bound | Post-witness pre-adjudication check fails; attempt void |
| TM-R03 | Witness challenge asks for summary/evaluation/defect judgment | Witness protocol invalid |
| TM-R04 | WitnessProtocolQualificationRecord is expired | Witness-based material review inadmissible |
| TM-R05 | WitnessProtocolQualificationRecord is for another provider/model/prompt-isolation mode | Binding mismatch; inadmissible |
| TM-R06 | Baseline and witness-enabled qualification runs use non-identical governed corpus/request envelope | Noninterference experiment invalid |
| TM-R07 | Witness output is accepted as semantic evidence or satisfies a review dimension | Structural-isolation failure; witness output cannot create review authority |
| TM-R08 | Framing/content witness succeeds but final semantic prompt occurs after evidence eviction | Attempt void |
| TM-R09 | Deterministic retrieval mode uses no witness protocol | Witness record not required; retrieval predicates remain required |
| TM-R10 | Witness output includes sensitive evidence and retention/egress policy forbids that response form | Mode/representation blocked or governed safer witness form required |
| TM-R11 | Candidate supplies its own WitnessProtocolQualificationRecord | Rejected as untrusted |
| TM-R12 | Witness qualification registry record is candidate-writable | Review path blocked |
| TM-R13 | Provider account-class documentation/config template changes after witness/context qualification | Qualification invalidated; requalification required |

## Phase S — Qualification attempt-selection and ledger-closure tests

| ID | Test | Expected result |
|---|---|---|
| TM-S01 | Frozen confirmation plan contains 299 IDs; one failed ID is deleted before calculation | Plan/ledger mismatch; qualification fails |
| TM-S02 | Failed trial rerun succeeds and retry is substituted for original | Original failure remains; zero-failure criterion fails |
| TM-S03 | Planned trial is never dispatched | Missing slot counts hard failure |
| TM-S04 | Extra unscheduled call appears in provider audit log | Confirmation epoch invalidated |
| TM-S05 | Provider audit logs unavailable but qualification credential is exclusive to trusted runner/egress | Attempt closure may remain provable from exclusive runner ledger |
| TM-S06 | Provider audit logs unavailable and ordinary operator can use credential | QUALIFICATION_ATTEMPT_CLOSURE_UNPROVEN |
| TM-S07 | Candidate code can invoke qualification endpoint/credential | Qualification trust boundary fails |
| TM-S08 | Randomization/interleaving seed chosen after early trial results | Plan invalid; no qualification |
| TM-S09 | Confirmation trial ID reused across drift epochs | Reject/rebind to new epoch required |
| TM-S10 | Every planned slot reconciles to one first-attempt dispatch/provider request and all pass | Attempt-set closure passes subject to all other gates |

## Phase T — Retry transparency and admissibility-registry closure

| ID | Test | Expected result |
|---|---|---|
| TM-T01 | SDK automatic retry hides first failed physical request then returns success | IMPLICIT_RETRY_UNOBSERVED or explicit hard failure; no single-success claim |
| TM-T02 | Client retry disabled and one physical request maps to one WireDeliveryRecord | Retry transparency passes |
| TM-T03 | Two physical retries exposed as two append-only attempts | Both retained; earlier failure cannot be erased |
| TM-T04 | AdmissibilityPredicateRegistry adds predicate P but Phase O/mutation catalog lacks P | ADMISSIBILITY_PREDICATE_COVERAGE_INCOMPLETE |
| TM-T05 | VerdictAdmissibilityResult omits registry predicate P | Set-closure failure |
| TM-T06 | Mutation target for P exists but no independently killing negative fixture | Coverage incomplete |
| TM-T07 | Negative fixture exists but validator mutation for P survives | Coverage incomplete |
| TM-T08 | Registry/verdict/mutation/killed sets are exactly equal | Predicate-coverage closure passes |
| TM-T09 | Candidate attempts to edit predicate registry used for own review | Untrusted/self-approval boundary violation |
| TM-T10 | Registry version changes after preflight before admission | Attempt void/revalidation required |

## Required evidence outputs

Every EXP-M execution must retain:

- frozen ReviewRequest;
- authoritative evidence inventory;
- EvidenceDeliveryManifest;
- GovernanceAuthoritySnapshot;
- RequiredEvidenceContract;
- RequiredInteractionContract;
- ProviderCapabilityProfile;
- ProviderAccessibilityRiskPolicy;
- ProviderContextIsolationPolicy;
- WitnessProtocolQualificationRecord when witnesses are used;
- pinned provider context-isolation documentation/account-class/config-template identities where the dedicated-account basis is used;
- AdmissionFenceRecord;
- ProviderQualificationExecutionPlan;
- ProviderCapabilityQualificationRecord with append-only trial ledger and planned/observed call reconciliation;
- ProviderContextStateEvidence;
- AdmissibilityPredicateRegistry and exact predicate/mutation closure record;
- PromptIsolationQualificationRecord;
- DeliveryPreflightResult;
- each EvidenceChunk;
- pre-SDK and post-SDK transport-semantic envelope hashes;
- transport/provider response envelope;
- ReviewerReceipt;
- DeliveryCompletenessResult;
- reviewer raw response;
- parsed review;
- InsufficientEvidenceAdjudication where applicable;
- VerdictAdmissibilityResult;
- unified data/state mutation results;
- validator-logic mutation results;
- atomic admission compare-and-set evidence;
- full hashes and timestamps.

## Exit criteria

EXP-M deterministic testing is complete only when:

- **all deterministic phases A–T pass**;
- unified data/state mutation survivors = 0;
- validator-logic mutation survivors = 0;
- crash/retry tests preserve exact identity/history;
- every admissibility conjunct is independently falsified by at least one negative test;
- authority-snapshot/base-head poisoning tests pass;
- clean-context state/sentinel tests pass;
- RequiredEvidenceContract and RequiredInteractionContract non-vacuity/closure tests pass;
- statistical-protocol tests reject insufficient, rerolled, burst-only, mixed exploration/confirmation, production-envelope-mismatched, and attempt-set cherry-picked evidence;
- every planned confirmation slot is reconciled or counted failed and qualification credentials are outside candidate/operator control;
- implicit client/SDK retries are disabled or every physical attempt is visible and append-only;
- admissibility predicate registry/verdict/mutation/killed sets have exact closure;
- per-attempt content-bound witness tests and canary-preserving content-drop oracle pass;
- model-selected retrieval is blocked without deterministic full-range access logs;
- atomic final CAS admission and permanent-attempt-void semantics pass;
- prompt-isolation qualification is machine-bound and admission-checked;
- ProviderAccessibilityRiskPolicy exists for every transition class and selected proof mode;
- mutable observable provider context is versioned/fenced through admission;
- hidden provider-internal mutable-state residual is governed by ProviderContextIsolationPolicy and never mislabeled observed-clean;
- highest-authority transition default DISALLOW for hidden provider-state residual is enforced;
- sentinel qualification cannot contaminate production review account;
- health checks cannot renew expired capability profiles;
- typed base/head comparison rules are mutation-tested and incomparable semantic changes fail unresolved;
- witness challenge/response overhead is included in qualified final-context budgeting and rechecked before adjudication;
- witness protocol is non-evaluative, structurally isolated from semantic evidence/authority, and bound to provider/mode/prompt-isolation qualification;
- witness qualification registry is outside candidate write authority;
- provider context-isolation documentation/account-class/config-template drift invalidates qualification;
- legacy REVIEW_CONTEXT_COMPLETE cannot create authority;
- statistical independence assumptions are explicit and cannot be inferred solely from fresh request IDs;
- model-selected retrieval logs bind exact returned bytes to final adjudication context;
- insufficient-evidence cause adjudication returns all causes and MIXED when multiple predicates hold;
- review consensus cannot hide corpus divergence.

Live provider pilots may begin only after deterministic exit above is green. A provider-specific production mode becomes qualified only after its separate exploration/confirmation capability evidence passes the governed risk budget and all provider-context/accessibility requirements.

Provider-specific `NOT_QUALIFIED_FOR_MATERIAL_REVIEW` is an acceptable fail-closed outcome.
