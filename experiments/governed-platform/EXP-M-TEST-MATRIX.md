# EXP-M Review Evidence Delivery Integrity — Test Matrix

## Purpose

This matrix turns EXP-M into an executable falsification plan. It is intentionally split into deterministic platform tests first and live provider capability tests second.

No live provider pilot may be treated as scientific evidence until the deterministic governor tests are green.

## Phase A — Deterministic unit and state-machine tests

| ID | Test | Setup | Expected result |
|---|---|---|---|
| A01 | Complete one-shot delivery | All mandatory items delivered exactly once | REVIEW_CONTEXT_COMPLETE |
| A02 | Required item missing | Remove one required item | EVIDENCE_DELIVERY_INCOMPLETE |
| A03 | Optional item missing | Remove optional item | Complete if contract permits |
| A04 | Manifest hash mismatch | Alter manifest after freeze | Reject |
| A05 | Item byte mismatch | Change one source byte | Reject |
| A06 | Item size mismatch | Correct hash metadata but wrong byte count | Reject |
| A07 | Duplicate required item | Duplicate one item | Reject ambiguous/duplicate delivery |
| A08 | Unexpected extra required-looking item | Add unmanifested item | Reject or quarantine; never silently bind |
| A09 | Wrong reviewed commit | Reuse manifest against another commit | Reject |
| A10 | Wrong ReviewRequest | Reuse corpus for another request | Reject |
| A11 | Reviewer self-ack only | Reviewer claims all received; platform missing item | Incomplete |
| A12 | HTTP 200 only | Provider call succeeds but no receipt evidence | Incomplete |
| A13 | Upload ID only | File upload succeeds but model visibility unproven | Incomplete |
| A14 | PASS before completeness | Early PASS returned | Verdict inadmissible |
| A15 | CHANGES_REQUIRED before completeness | Early negative verdict | Diagnostic only |
| A16 | INSUFFICIENT before completeness | Early insufficient verdict | Cause unresolved/delivery diagnostic, not scientific |
| A17 | Scientific artifact absent | Required source does not exist | SCIENTIFIC_EVIDENCE_MISSING |
| A18 | Artifact exists but omitted | Source exists but delivery omits it | EVIDENCE_DELIVERY_INCOMPLETE |
| A19 | Unsupported format | Provider profile says unsupported | Fail preflight |
| A20 | Unknown provider capability | No qualified profile | Fail preflight |

## Phase B — Chunk protocol tests

| ID | Test | Mutation | Expected result |
|---|---|---|---|
| B01 | All chunks correct | None | Complete |
| B02 | Missing final chunk | Drop N | Incomplete |
| B03 | Missing middle chunk | Drop k | Incomplete |
| B04 | Duplicate chunk | Duplicate k | Reject |
| B05 | Duplicate+missing | Duplicate k, remove j | Detect both |
| B06 | Reordered chunks | Shuffle | Canonical reconstruction or reject |
| B07 | Corrupted chunk | Change one byte | Hash mismatch |
| B08 | Same index, different bytes on retry | Retry mutated k | Reject |
| B09 | Cross-request chunk | Chunk from old request | Reject |
| B10 | Cross-corpus chunk | Correct request, wrong corpus hash | Reject |
| B11 | Wrong total count | Change N | Reject |
| B12 | Wrong chunk index | Out-of-range or repeated index | Reject |
| B13 | Empty mandatory chunk | Replace content with empty bytes | Reject |
| B14 | Chunk metadata only | Claim hash/count without bytes | Incomplete |
| B15 | Stale receipt | Receipt from older corpus | Reject |
| B16 | Receipt missing item IDs | Count matches but IDs absent | Incomplete |
| B17 | Receipt count lies | Says N while delivery has N-1 | Independent check rejects |
| B18 | Completion before last chunk | Reviewer marks complete early | Reject |

## Phase C — Context and representation tests

| ID | Test | Setup | Expected result |
|---|---|---|---|
| C01 | Tail truncation | Decisive artifact last | Preflight block or detectable incomplete |
| C02 | Middle truncation | Decisive artifact in middle | Detect item/chunk gap |
| C03 | Large prompt crowd-out | Prompt consumes context | Required evidence cannot be silently dropped |
| C04 | ZIP unsupported | ZIP required; provider lacks archive visibility | EVIDENCE_FORMAT_UNSUPPORTED |
| C05 | TAR unsupported | TAR required; provider lacks archive visibility | EVIDENCE_FORMAT_UNSUPPORTED |
| C06 | PDF partial visibility | Only some pages exposed | Partial coverage, not complete |
| C07 | Markdown-only substitution | Raw JSON required but summary Markdown sent | Representation mismatch |
| C08 | Encoding transformation | CRLF/UTF-8/normalization changes bytes | Raw-hash mismatch where byte identity required |
| C09 | Binary corruption | Attachment bytes altered | Reject |
| C10 | Attachment accepted but inaccessible | Upload succeeds, reviewer cannot inspect | EVIDENCE_ATTACHMENT_UNAVAILABLE |
| C11 | Summary substitutes raw log | Proposer summary replaces required raw log | Reject |
| C12 | Prompt states missing evidence contents | Evidence absent; prompt describes it | Reject |
| C13 | Citation to undelivered evidence | Reviewer cites manifest-only item | Coverage not TESTED_SUPPORTED |
| C14 | Partial file accepted as whole | Only prefix delivered | Incomplete |

## Phase D — Insufficient-evidence cause adjudication

| ID | Scenario | Expected classification |
|---|---|---|
| D01 | Required artifact never existed | SCIENTIFIC_EVIDENCE_MISSING |
| D02 | Artifact existed, not materialized | EVIDENCE_MATERIALIZATION_FAILED |
| D03 | Materialized, omitted from request | EVIDENCE_DELIVERY_INCOMPLETE |
| D04 | Delivered file ref but provider cannot expose it | EVIDENCE_ATTACHMENT_UNAVAILABLE |
| D05 | Corpus exceeds qualified context | REVIEW_CONTEXT_INCOMPLETE |
| D06 | Required format unsupported | EVIDENCE_FORMAT_UNSUPPORTED |
| D07 | Reviewer says insufficient, platform cause unknown | INSUFFICIENT_EVIDENCE_CAUSE_UNRESOLVED |
| D08 | Scientific + delivery gaps both exist | MIXED_INSUFFICIENCY |
| D09 | Reviewer claims missing item that was verifiably delivered | REVIEWER_EVIDENCE_ASSESSMENT_CONTRADICTION |
| D10 | Platform claims delivery but receipt/manifest disagree | EVIDENCE_RECEIPT_UNPROVEN |

## Phase E — Multi-reviewer equivalence tests

| ID | Test | Expected result |
|---|---|---|
| E01 | Claude and DeepSeek receive identical manifest/hash | Results comparable subject to semantic review |
| E02 | One receives raw JSON, other receives only summary | Not equivalent consensus |
| E03 | One provider complete, one incomplete | Incomplete verdict non-promotable |
| E04 | One provider supports file, other ignores it | Provider-specific delivery states preserved |
| E05 | Different chunking but same canonical corpus | Comparable only if reconstruction proves equivalent corpus |
| E06 | Different required item set | Not comparable |
| E07 | Retry one reviewer with changed corpus | New delivery boundary required |
| E08 | Two reviewers agree after one incomplete delivery | Consensus cannot bypass incomplete evidence |

## Phase F — Provider capability qualification

For each provider/model/API mode execute a provider-specific qualification fixture.

Default EXP-M statistical acceptance policy, unless a stricter provider-specific policy is independently governed before exposure:

- at least 59 independent fresh trials at every claimed operating point;
- 0 hard delivery/accessibility failures;
- one-sided 95% exact-binomial lower confidence bound of approximately 0.95 or greater;
- intermittent/timeout/ambiguous/unverifiable outcomes count as failures;
- qualified operating point no higher than the largest point satisfying the criterion;
- if a failing boundary is observed, qualified scalar limits are capped at 80% of the smallest observed failing boundary;
- if no failure boundary is observed, qualified scalar limits are capped at 80% of the largest fully tested passing point;
- profile expiry is 7 days by default and immediate on material provider/model/deployment/account/endpoint/region/adapter/session/file behavior drift;
- requalification repeats the applicable protocol and may not be replaced by one health-check request.

Required measurements:

1. one-shot raw text corpus near increasing sizes;
2. attachment visibility for supported formats;
3. attachment count boundary;
4. per-file size boundary;
5. ZIP/TAR behavior;
6. PDF full-range versus partial-range visibility;
7. staged chunk continuation;
8. receipt/acknowledgement behavior;
9. context-tail truncation;
10. context-middle omission detection if applicable;
11. request rejection versus silent truncation;
12. retry stability;
13. provider/model/version identity binding.

Each observation must record:

- provider;
- model;
- API/adapter version;
- request size;
- evidence bytes;
- estimated tokens if available;
- response status;
- model-visible evidence IDs;
- truncation/error signal;
- raw response hash;
- timestamp;
- qualified safe limit.

Do not hard-code vendor-advertised limits as platform-qualified limits without empirical binding.

## Phase G — Mutation suite

Starting from one complete, admissible review delivery, mutate one load-bearing field at a time:

1. force `context_complete=true`;
2. force `received_all=true`;
3. lower required item count;
4. lower expected chunk count;
5. mark required item optional;
6. ignore missing item;
7. ignore missing chunk;
8. ignore duplicate chunk;
9. ignore hash mismatch;
10. trust upload success;
11. trust HTTP 200;
12. trust reviewer self-receipt;
13. reuse old receipt;
14. reuse old chunk;
15. rebind request ID;
16. rebind corpus hash;
17. use unknown provider capability profile;
18. override unsupported format;
19. admit PASS before completion;
20. classify delivery miss as scientific miss;
21. classify scientific miss as delivery miss;
22. count incomplete reviewer in consensus;
23. treat citation as delivery proof;
24. allow prompt description to replace missing evidence.

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

A review result must be non-promotable when any of these are false:

- valid ReviewRequest;
- materialized evidence count complete;
- delivery preflight passed;
- provider profile qualified;
- required evidence delivered;
- required chunks complete;
- receipt/completeness validated;
- semantic review coverage valid;
- review provenance valid.

Test dispositions:

- PASS + incomplete delivery => non-promotable.
- BOUNDED_PASS + incomplete mandatory evidence delivery => non-promotable.
- CHANGES_REQUIRED + incomplete delivery => retained diagnostic, not complete adjudication.
- INSUFFICIENT_EVIDENCE + delivery defect => adjudicate cause as delivery/context.
- PASS + complete delivery + semantic coverage => delivery layer permits downstream review validation only; it does not independently grant promotion.

## Phase J — Trust-root, wire, representation, and egress tests

| ID | Test | Expected result |
|---|---|---|
| J01 | Manifest marks governed required item optional | Required-evidence closure fails |
| J02 | Manifest omits governed evidence ref entirely | Preflight fails before provider call |
| J03 | Candidate supplies permissive provider profile | Profile rejected as untrusted |
| J04 | Provider profile expired | Requalification required |
| J05 | Provider model/adapter version drifts from profile | Profile invalid |
| J06 | Manifest complete but trusted adapter omits item from wire body | Wire mismatch; verdict inadmissible |
| J07 | Adapter changes system/developer prompt on retry | Wire hash mismatch |
| J08 | Adapter changes tool/file bindings on retry | Wire/session mismatch |
| J09 | Receipt session A, verdict session B | Verdict inadmissible |
| J10 | Stateless verdict request omits earlier required evidence | Incomplete |
| J11 | Opaque file ID from another attempt/session | Reject |
| J12 | Provider file expired between receipt and verdict | Context incomplete |
| J13 | Chunk sequence individually fits but cumulative final context does not | Preflight fails; chunking cannot expand context |
| J14 | Persistent retrieval mechanism qualified and final request binds all file IDs | Eligible for downstream review validation |
| J15 | Full raw required, partial PDF/text extraction delivered | Representation incomplete |
| J16 | Transformation tool/version/hash mismatch | Reject |
| J17 | Lossy transform not explicitly permitted | Reject |
| J18 | Data classification forbids provider egress | Preflight blocks |
| J19 | Silent redaction of required evidence | Incomplete/unqualified representation |
| J20 | Permitted redaction preserves all load-bearing fields | Eligible only if governed transformation rule says sufficient |
| J21 | All delivery checks pass but EXP-L/prompt-isolation dependency unqualified | Material verdict non-promotable |
| J22 | Two subreviews pass but defect exists only across evidence subsets | No global PASS |
| J23 | Aggregator lacks cross-evidence interaction corpus | Global disposition blocked |
| J24 | Aggregation contract includes interaction evidence and qualified aggregator | Eligible for downstream review validation |
| J25 | Reviewer self-receipt claims inaccessible file visible | Platform delivery/capability record wins; incomplete |
| J26 | Provider docs claim large context but empirical qualified profile is smaller | Empirical qualified bound governs |
| J27 | Provider capability registry record candidate-writable | Profile untrusted |
| J28 | Egress policy record candidate-writable | Egress decision untrusted |
| J29 | Wire record excludes semantic field from canonical hash | Test must fail; semantic request binding incomplete |
| J30 | Secret redaction from wire hash removes only credentials, not semantics | Reproducible semantic wire binding passes |

## Phase K — Remote accessibility witness and retrieval grounding tests

| ID | Test | Expected result |
|---|---|---|
| K01 | Reviewer echoes manifest IDs but fails fresh hidden content canary | Context accessibility not qualified |
| K02 | Fresh beginning/middle/end canaries all recovered exactly | Accessibility probe passes for tested bound |
| K03 | Tail canary missing near context limit | Safe qualified limit lowered; review over limit blocked |
| K04 | Middle canary missing while head/tail pass | Internal omission detected |
| K05 | Canary from prior attempt replayed | Attempt/session binding rejection |
| K06 | Candidate learns/controls canary before delivery | Probe invalid; cannot establish accessibility |
| K07 | Candidate modifies capability registry record | Profile untrusted |
| K08 | Capability registry commit/profile changes with candidate under review | Self-approval boundary violation |
| K09 | Provider file citation with no successful retrieval log in retrieval-required mode | Coverage cannot be TESTED_SUPPORTED |
| K10 | Retrieval log resolves wrong content hash/version | Evidence identity mismatch |
| K11 | Retrieval log shows access after verdict generation | Verdict timing invalid |
| K12 | Receipt and canary probes pass but final adjudication occurs in another session | Session mismatch |
| K13 | Stateless final request omits canary-qualified earlier evidence | Incomplete final context |
| K14 | Same-session final review fits qualified cumulative context after canary qualification | Eligible for downstream semantic validation |
| K15 | Canary value copied into prompt/manifest | Probe invalid because value is not evidence-access dependent |

## Phase L — Delivery-governor trust, parser safety, and provider-drift tests

| ID | Test | Expected result |
|---|---|---|
| L01 | Candidate branch edits manifest builder to omit decisive evidence | Candidate implementation cannot authorize its own delivery |
| L02 | Candidate edits completeness validator to always return true | Trusted platform validator wins; review blocked |
| L03 | Candidate provides its own capability profile | Profile rejected |
| L04 | Candidate provides its own representation transformer | Transformer rejected as untrusted |
| L05 | Archive contains `../` traversal | Safe materializer rejects |
| L06 | Archive contains absolute-path member | Reject |
| L07 | Archive contains symlink escape | Reject |
| L08 | Archive contains duplicate normalized member names | Reject ambiguity |
| L09 | Decompression expansion exceeds size limit | Fail closed without resource exhaustion |
| L10 | Parser exceeds time/memory budget | Fail closed |
| L11 | Two evidence paths normalize to same stable ID | Collision detected |
| L12 | Two different hashes attempt same declared evidence ID | Collision/rebind rejected |
| L13 | One near-limit provider canary run succeeds, subsequent fresh trials fail | Qualified limit not widened |
| L14 | Repeated trials all pass below conservative margin | Bound may be qualified under policy |
| L15 | Same model alias reports different backend/deployment | Drift invalidates profile or requires bounded requalification |
| L16 | Qualified endpoint/region differs from actual call | Fail |
| L17 | Qualified account/tenant differs from actual call | Fail |
| L18 | Primary provider failure triggers fallback with primary profile | Fail/new delivery boundary required |
| L19 | Fallback has its own qualified profile and new attempt | Eligible for downstream validation |
| L20 | File upload accepted but processing/indexing pending | Context incomplete |
| L21 | File later becomes ready in same bound session | May proceed only after new readiness evidence |
| L22 | Retrieval returns only snippet of full-required file | Coverage insufficient |
| L23 | Retrieval returns exact required full content/hash | Eligible for downstream semantic coverage |
| L24 | Candidate modifies egress decision/profile | Untrusted; delivery blocked |

## Phase M — TOCTOU and reviewer-tool boundary tests

| ID | Test | Expected result |
|---|---|---|
| M01 | Source file mutated after manifest hash before upload | Frozen bytes used or mismatch detected |
| M02 | Generated representation mutated after freeze | Representation/wire mismatch |
| M03 | Capability profile expires between preflight and final call | Block completion |
| M04 | Egress authorization revoked before send | Block dispatch |
| M05 | Provider file replaced/mutated after qualification | File identity/access mismatch |
| M06 | Final review uses stale provider file version | Verdict inadmissible |
| M07 | Reviewer web search finds ungoverned evidence and uses it for PASS | Cannot count as frozen review evidence |
| M08 | Reviewer tool fetches different revision of governed file | Revision/hash mismatch |
| M09 | Governed supplemental tool evidence captured with provenance | Requires explicit supplemental/new boundary; not silent rebind |
| M10 | Tool result omitted from audit record but cited in verdict | Coverage invalid |
| M11 | Candidate changes source path after preflight but before adapter serialization | No TOCTOU substitution |
| M12 | Retry after state drift reuses old attempt identity | Reject/new attempt required |

## Phase N — External-review remediation tests

| ID | Test | Expected result |
|---|---|---|
| N01 | Governing standard requires evidence E; ReviewRequest omits E | EVIDENCE_SELECTION_INCOMPLETE before manifest freeze |
| N02 | Governing standard requires mandatory dimension D; ReviewRequest omits D | ReviewRequest rejected |
| N03 | ReviewRequest/manifest are internally closed but RequiredEvidenceContract contains extra mandatory ref | Required-evidence closure fails |
| N04 | Reused provider thread contains prior ungoverned user message | Material review context dirty; verdict inadmissible |
| N05 | Reused provider thread contains prior tool result | Context dirty unless fully governed and bound |
| N06 | Fresh provider session contains only frozen governed content | Session cleanliness passes subject to provider profile |
| N07 | Provider account/project custom instruction changes after qualification | Provider mode/profile invalidated |
| N08 | Provider memory is enabled and cannot be disabled/captured | NOT_QUALIFIED_FOR_MATERIAL_REVIEW |
| N09 | Provider-side knowledge connector enabled but absent from manifest/profile | NOT_QUALIFIED_FOR_MATERIAL_REVIEW |
| N10 | Provider exposes fixed service policy but no mutable account/session context | May proceed only under qualified provider profile/nonclaim |
| N11 | 58/58 fresh capability trials pass | Insufficient trials; operating point unqualified |
| N12 | 59/59 fresh trials pass | Statistical criterion satisfied at tested point, subject to all other gates |
| N13 | 58 successes + 1 hard failure | Operating point disqualified |
| N14 | One ambiguous/timeout trial among 59 | Counts as failure; disqualify point |
| N15 | Smallest observed failure boundary B; profile claims >0.8B | Profile invalid |
| N16 | No failure observed; profile claims >80% of largest tested passing point | Profile invalid |
| N17 | Profile older than 7 days without requalification | Expired |
| N18 | Sparse head/middle/tail canaries pass while internal segment omitted | Claimed range unqualified |
| N19 | Dense 2048-byte-or-smaller text segments all witness-qualified | Accessibility criterion may pass for tested representation |
| N20 | One dense segment witness fails | Operating point fails |
| N21 | Opaque attachment has required pages/ranges not individually probed and no deterministic access logs | Full artifact mode unqualified |
| N22 | Provider retrieval logs prove complete exact required ranges | Eligible for downstream semantic validation |
| N23 | Proposer interaction list omits platform-derived required interaction | Aggregation/global verdict blocked |
| N24 | Platform RequiredInteractionContract and proposer plan match completely | Interaction closure passes |
| N25 | Capability profile expires after provider response but before verdict admission | Verdict non-promotable |
| N26 | Egress permission revoked after provider response but before verdict admission | Verdict non-promotable according to current policy |
| N27 | Session/file state invalidates after provider response but before verdict admission | Verdict blocked |
| N28 | Deployment identity is required by drift policy but provider cannot expose it | Identity-dependent qualification not claimable |
| N29 | Retrieval logs required for completeness but provider does not expose them | Retrieval-based mode unqualified |
| N30 | Dirty-session review returns PASS with otherwise perfect manifest/wire records | PASS remains inadmissible |

## Required evidence outputs

Every EXP-M execution must retain:

- frozen ReviewRequest;
- authoritative evidence inventory;
- EvidenceDeliveryManifest;
- ProviderCapabilityProfile;
- DeliveryPreflightResult;
- each EvidenceChunk;
- transport/provider response envelope;
- ReviewerReceipt;
- DeliveryCompletenessResult;
- reviewer raw response;
- parsed review;
- InsufficientEvidenceAdjudication where applicable;
- VerdictAdmissibilityResult;
- mutation results;
- full hashes and timestamps.

## Exit criteria

EXP-M testing is complete only when:

- deterministic phases A-E pass;
- mutation survivors are zero;
- crash/retry tests preserve exact identity/history;
- admissibility integration tests fail closed;
- at least the platform's intended production provider/API modes have qualified capability profiles;
- no `INSUFFICIENT_EVIDENCE` can be accepted without cause adjudication;
- review consensus cannot hide corpus divergence;
- RequiredEvidenceContract closure prevents an incomplete ReviewRequest from narrowing evidence;
- material-review sessions are fresh/clean or fully governed;
- provider capability profiles satisfy the preregistered statistical thresholds and expiry policy;
- provider-injected mutable semantic context is inventoried/disabled or the mode is disqualified;
- dense accessibility probing or deterministic range evidence covers every required region at the claimed bound;
- RequiredInteractionContract closure prevents proposer-only interaction omission;
- capability/egress/session state remains valid through verdict admission.

Live provider limitations may result in provider-specific `NOT_QUALIFIED_FOR_MATERIAL_REVIEW`; that is an acceptable fail-closed outcome.
