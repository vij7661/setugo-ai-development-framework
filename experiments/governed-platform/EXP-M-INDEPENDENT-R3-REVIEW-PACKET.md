# EXP-M Independent R3 Review Packet

## Packet status

`R3_EXTERNAL_REVIEW_REQUESTED_NO_AUTHORITY_EFFECT`

This packet is a self-contained R3 design/preregistration review package for:

**EXP-M — Review Evidence Delivery & Reviewer Context Integrity Falsification**

It contains the current governed design, test matrix, live-governance integration, the preserved R2 external review, and the R2 remediation/adjudication.

It does NOT claim EXP-M is implemented, scientifically executed, provider-qualified, or promotable.

## Reviewed source identity

- repository: `vij7661/setugo-ai-development-framework`
- branch: `experiment/exp-m-review-evidence-delivery-integrity`
- base main commit: `87f6e3df73c0c70c5d8ff4da38365ff92721aff7`
- R2 packet reviewed source: `35fada32e3c09b7e43e286c4233d70a3b6f65273`
- current R3 reviewed source commit: `fc5b5b6612b9fe4c9030ce13a6518084acc69655`
- current R3 reviewed source tree: `1404840ef43c73e2ca961670afaacb5c9777848e`

Current reviewed blobs:
- `standards/review-evidence-delivery-integrity.md` — `184575320b6c18679d0ef39c311505c9b2a667e2`
- `experiments/governed-platform/exp-m-review-evidence-delivery-integrity.md` — `773c52aaa9ecc7826493d34ab9745b6ca719b169`
- `experiments/governed-platform/EXP-M-TEST-MATRIX.md` — `5f21e04a126b1450939dfdf1969556dc6e224156`
- `governance-runtime/LIVE-CONVERSATION-GOVERNANCE.md` — `a9e5255244421a67490c13be2ce5b525f253f96a`
- `experiments/governed-platform/EXP-M-R2-EXTERNAL-REVIEW.md` — `1340a7e697cd7dad0f449c8b4a7c6580babaa0f4`
- `experiments/governed-platform/EXP-M-R2-REVIEW-REMEDIATION.md` — `6b6cc316592a3d0f7482d4f8502d0fac358ad0c4`

## R2 disposition being remediated

R2 external review disposition:

`CHANGES_REQUIRED`

R2 identified:

- Critical C-01 — incomplete ReviewRequest can narrow required evidence upstream of the delivery manifest;
- High H-01 — dirty/reused provider session can add ungoverned semantic context;
- High H-02 — provider capability qualification lacked fixed statistical thresholds;
- High H-03 — provider-injected/default semantic context was not fully bound;
- High H-04 — sparse witness canaries could miss internal omissions;
- High H-05 — test matrix lacked adversarial coverage for those gaps;
- Medium M-01 — permissive “where available/applicable” wording;
- Medium M-02 — proposer-authored decomposition interaction list;
- Low/Medium M-03 — capability/egress expiry after final wire call before verdict admission.

The current source accepts these findings as valid and claims they have been remediated.

Do NOT accept that claim without reconstructing it from the inline current source.

## R3 review posture

Assume false-green.

Your job is to determine whether the R2 repairs genuinely close the identified Critical/High defects **without moving the trust problem elsewhere**, and whether any new Critical/High defect is introduced.

Focus especially on:

1. independent RequiredEvidenceContract derivation versus incomplete ReviewRequest;
2. independent RequiredInteractionContract derivation;
3. fresh/clean provider session semantics;
4. provider-injected mutable prompts/memory/connectors;
5. statistical provider-capability qualification policy;
6. dense witness/accessibility coverage;
7. verdict-time capability/egress/session revalidation;
8. interaction with delivery-governor trust root, wire binding, EXP-L dependency, transformations, egress, provider drift, and reviewer tools.

## Required output

Return exactly one:

- `BOUNDED_PASS`
- `CHANGES_REQUIRED`
- `INSUFFICIENT_EVIDENCE`

Then report:

### 1. R2 finding closure

For each:
- C-01
- H-01
- H-02
- H-03
- H-04
- H-05
- M-01
- M-02
- M-03

return:
- CLOSED / OPEN / PARTIAL
- evidence from current source
- any remaining false-green path
- exact narrow correction if not CLOSED

### 2. New findings

List any newly discovered:
- Critical
- High
- Medium/Low

For each:
- finding ID
- severity
- affected section/invariant/test
- concrete false-green/failure path
- why current design is insufficient
- narrow fix

### 3. Gate verdicts

Return:

- REQUIRED_EVIDENCE_AUTHORITY = PASS / FAIL
- DELIVERY_GOVERNOR_TRUST_ROOT = PASS / FAIL
- CLEAN_SESSION_CONTEXT = PASS / FAIL
- PROVIDER_SEMANTIC_CONTEXT_BINDING = PASS / FAIL
- WIRE_BINDING = PASS / FAIL
- CHUNK_CONTEXT_MODEL = PASS / FAIL
- REMOTE_ACCESSIBILITY_MODEL = PASS / FAIL
- PROVIDER_CAPABILITY_QUALIFICATION = PASS / FAIL
- REPRESENTATION_GOVERNANCE = PASS / FAIL
- MATERIALIZATION_SAFETY = PASS / FAIL
- EGRESS_BOUNDARY = PASS / FAIL
- SESSION_FILE_RETRIEVAL_BINDING = PASS / FAIL
- INSUFFICIENT_EVIDENCE_TAXONOMY = PASS / FAIL
- MULTI_REVIEWER_EQUIVALENCE = PASS / FAIL
- DECOMPOSITION_AGGREGATION = PASS / FAIL
- PROMPT_ISOLATION_DEPENDENCY = PASS / FAIL
- TOCTOU_RETRY_INTEGRITY = PASS / FAIL
- REVIEWER_TOOL_EVIDENCE_BOUNDARY = PASS / FAIL
- TEST_MATRIX_SUFFICIENCY = PASS / FAIL

### 4. Statistical policy review

Explicitly adjudicate the default provider capability policy:

- minimum 59 fresh independent trials;
- 0 hard failures;
- one-sided 95% exact-binomial lower bound ~>=0.95;
- ambiguous/timeout/unverifiable = failure;
- 80% smallest-failure-boundary cap;
- or 80% largest-tested-passing cap if no failure boundary found;
- 7-day default expiry plus immediate drift-triggered requalification.

State whether this is sufficiently falsifiable/conservative for preregistration or needs correction.

### 5. Dense witness review

Explicitly test whether:
- <=2048-byte probed text segments;
- per-segment fresh witness framing;
- randomized content-location challenges across trials;
- page/range/member-level opaque-file probing or deterministic retrieval logs

adequately addresses R2 H-04 without falsely claiming model attention.

### 6. Final determination

State:

- whether any Critical defect remains;
- whether any High defect remains;
- whether EXP-M is ready for implementation/deterministic falsification;
- whether live provider pilots may begin (they should not unless deterministic implementation/tests qualify first);
- exact remaining prerequisites;
- explicit confirmation EXP-M remains NOT QUALIFIED;
- explicit confirmation this external/manual review itself grants no platform review authority or promotion.

## Nonclaims

The current design does not claim:
- remote model attention is provable;
- provider internals are cryptographically knowable;
- any real provider capability is qualified;
- current production/main review runtime already implements EXP-M;
- R3 review can itself promote EXP-M.

## Inline review material


---

# INLINE SOURCE: standards/review-evidence-delivery-integrity.md

Git blob: `184575320b6c18679d0ef39c311505c9b2a667e2`

# Review Evidence Delivery Integrity Standard

## Status

`PREREGISTERED_FOR_EXP_M_FALSIFICATION`

This standard governs the boundary between an authoritative evidence set and the evidence context made available to a reviewer through a platform API transport.

It does **not** claim that a platform can cryptographically prove that a remote model cognitively attended to every delivered token. The platform may prove its own materialization and wire delivery, and may rely only on separately qualified provider/model/API capabilities for remote context accessibility. Model attention is a nonclaim.

## Core problem

An unchanged scientific evidence set can produce different reviewer outcomes when different providers, models, API modes, file transports, context limits, or chunking paths expose different subsets or representations of that evidence.

Therefore these are separate governed facts:

1. authoritative evidence existence;
2. required-evidence selection;
3. evidence materialization;
4. representation/transformation;
5. wire delivery;
6. provider/session/file accessibility;
7. qualified reviewer-context availability;
8. reviewer semantic adjudication;
9. verdict admissibility.

A later stage may not self-prove an earlier stage.

## Delivery-governor trust root

The code that decides whether evidence delivery is complete is itself load-bearing governance.

For a material review, the following must execute from an independently governed, pinned platform implementation that is outside the reviewed candidate's self-approval boundary:

- required-evidence derivation;
- evidence materializer;
- representation transformer;
- manifest builder;
- provider capability registry reader;
- delivery preflight;
- chunk/session protocol;
- trusted provider adapter/wire serializer;
- delivery completeness validator;
- insufficient-evidence cause adjudicator;
- verdict-admissibility validator.

A candidate under review must not be able to modify the implementation that decides whether its own evidence was complete. Candidate-supplied delivery code may be tested as an artifact, but it cannot grant its own review admissibility.

## Core authority rule

**A reviewer disposition is inadmissible for a material authority transition unless every mandatory evidence item is governed from source through delivery and the selected provider/mode is qualified to make that exact representation available to the reviewer.**

A `PASS` cannot cure incomplete delivery. A negative result from incomplete delivery may remain useful defect/diagnostic evidence, but it is not a complete scientific adjudication.

## Required-evidence authority

The delivery manifest and the ReviewRequest do not decide what evidence is required by themselves.

Before a ReviewRequest is eligible for delivery, the pinned delivery governor must independently derive a `RequiredEvidenceContract` from the governing standards, experiment/qualification contract, protected transition type, mandatory review dimensions, path/material classification, and any platform-owned evidence-selection rules.

The `ReviewRequest` is a declaration that must be validated against that independently derived contract. It is never the sole source of requiredness.

The `RequiredEvidenceContract` must contain at least:

- contract schema/version;
- governing standard/experiment identities and hashes;
- protected transition classification;
- complete mandatory review-dimension set;
- complete required evidence-reference set or deterministic derivation rules;
- representation requirements for each evidence reference/dimension;
- required cross-evidence interaction families;
- deterministic optional-evidence rules;
- contract hash.

Before manifest freeze, prove all of:

- every standard/experiment-required mandatory dimension appears in the ReviewRequest;
- every `RequiredEvidenceContract` evidence ref is declared by or deterministically materializable from the ReviewRequest;
- no required ref is downgraded to optional;
- no mandatory interaction family is omitted;
- no provider capability limit narrows the required set.

The proposer, packet builder, reviewer, ReviewRequest author, transport adapter, or delivery manifest may not silently:

- omit a governed evidence reference;
- omit a standard-required mandatory dimension;
- change required to optional;
- substitute a summary for required raw evidence;
- omit a governed cross-evidence interaction;
- narrow the required item set because of provider limits.

Before delivery, the platform must prove closure:

`required_contract_refs == validated_review_request_refs == materialized_required_refs == manifest_required_refs`

and:

`required_contract_dimensions == review_request_mandatory_dimensions`

subject only to explicitly governed representation mappings.

Any mismatch fails before manifest freeze as `EVIDENCE_SELECTION_INCOMPLETE`.

If the pinned governor cannot deterministically derive a complete required-evidence or required-interaction contract from the governing materials, the review is not eligible for material authority. Ambiguity is classified as `EVIDENCE_SELECTION_CONTRACT_UNRESOLVED`; the platform may not fall back to trusting the proposer/ReviewRequest declaration.

## Failure taxonomy

At minimum preserve:

- `SCIENTIFIC_EVIDENCE_MISSING`
- `EVIDENCE_SELECTION_INCOMPLETE`
- `EVIDENCE_SELECTION_CONTRACT_UNRESOLVED`
- `REVIEW_CONTEXT_DIRTY_OR_UNBOUND`
- `PROVIDER_SEMANTIC_CONTEXT_UNQUALIFIED`
- `PROVIDER_CAPABILITY_STATISTICAL_POLICY_FAILED`
- `ACCESSIBILITY_PROBE_COVERAGE_INSUFFICIENT`
- `REVIEW_INTERACTION_CONTRACT_INCOMPLETE`
- `EVIDENCE_MATERIALIZATION_FAILED`
- `EVIDENCE_TRANSFORMATION_UNQUALIFIED`
- `EVIDENCE_DELIVERY_INCOMPLETE`
- `REVIEW_CONTEXT_INCOMPLETE`
- `EVIDENCE_FORMAT_UNSUPPORTED`
- `EVIDENCE_ATTACHMENT_UNAVAILABLE`
- `EVIDENCE_CHUNK_MISSING`
- `EVIDENCE_CHUNK_DUPLICATE`
- `EVIDENCE_CHUNK_REORDERED`
- `EVIDENCE_CHUNK_HASH_MISMATCH`
- `EVIDENCE_MANIFEST_MISMATCH`
- `EVIDENCE_WIRE_REQUEST_MISMATCH`
- `EVIDENCE_SESSION_BINDING_MISMATCH`
- `EVIDENCE_FILE_REFERENCE_UNQUALIFIED`
- `PROVIDER_CAPABILITY_PROFILE_UNQUALIFIED`
- `PROVIDER_CAPABILITY_PROFILE_STALE`
- `EVIDENCE_EGRESS_NOT_AUTHORIZED`
- `EVIDENCE_RECEIPT_UNPROVEN`
- `REVIEW_STARTED_BEFORE_DELIVERY_COMPLETE`
- `REVIEW_VERDICT_INADMISSIBLE_DELIVERY_FAILURE`
- `INSUFFICIENT_EVIDENCE_CAUSE_UNRESOLVED`
- `MIXED_INSUFFICIENCY`

A generic reviewer `INSUFFICIENT_EVIDENCE` token is not the platform's final cause classification.

## Evidence Delivery Manifest

Before any provider invocation, create an immutable content-addressed `EvidenceDeliveryManifest` bound to the exact current `ReviewRequest`.

It must contain at least:

- review request ID/hash;
- reviewed artifact commit/tree;
- required review dimensions;
- authoritative required evidence refs and count;
- provider/model/API mode;
- trusted adapter identity/hash/version;
- provider capability profile ID/hash/version/expiry;
- delivery protocol version;
- delivery attempt ID;
- per-item stable evidence ID derived from governed source identity and content hash;
- authoritative source reference;
- evidence class;
- source raw SHA-256 and byte length;
- governed representation ID;
- representation media type;
- representation SHA-256 and byte length;
- required/optional status derived from governed source;
- transformation record when source and representation differ;
- chunk plan where applicable;
- total chunk count;
- per-chunk hash/length/index;
- canonical ordering;
- whole canonical corpus hash;
- exact system/developer/user review prompt hashes where applicable;
- egress/data-classification decision hash;
- expected wire-call count.

The manifest hash is frozen before delivery.

## Representation and transformation governance

A source artifact and a reviewer representation are not automatically equivalent.

When evidence is transformed, record:

- source evidence ID/hash/length/media type;
- transformation tool identity/version/hash;
- transformation parameters;
- produced representation hash/length/media type;
- byte/page/range coverage where relevant;
- whether transformation is lossless, bounded-loss, or summary;
- governed rule permitting the representation for each review dimension.

Examples requiring explicit transformation governance:

- PDF to extracted text;
- binary log to decoded text;
- JSON to Markdown;
- archive extraction;
- image to text/OCR;
- page/range slicing;
- proposer-written summary.

A lossy or partial representation cannot satisfy a full-raw-evidence requirement.

Transformation tools/parsers must be platform-owned/pinned or otherwise independently qualified; candidate-provided parser code cannot transform its own evidence into an authoritative reviewer representation.

Archive/document materialization must be bounded against path traversal, symlink escape, duplicate-name ambiguity, decompression/resource bombs, recursive archive expansion, and parser time/memory exhaustion. Unsafe opaque archives may be preserved as source evidence but cannot be treated as successfully materialized reviewer content merely because an external provider accepts them.

## Data classification and egress authorization

Evidence must not be sent to an external provider merely because it is required for review.

Before delivery, classify each evidence item for:

- secrets/credentials;
- personal/sensitive data;
- proprietary/restricted data;
- provider/region restrictions;
- retention/training restrictions where applicable;
- permitted transformation/redaction.

The egress decision must be platform/governance-owned and bound to the delivery manifest.

If required evidence cannot be safely/legally sent in a qualified representation, that provider/mode is not qualified for the review. The platform must not silently redact or omit load-bearing evidence and then call the review complete.

## Provider capability qualification policy

Live provider qualification must use a preregistered statistical policy; words such as “repeated” or “conservative” are not sufficient.

Unless a stricter provider-specific policy is independently governed before exposure, the default EXP-M material-review capability policy is:

- every claimed operating point uses at least **59 independent fresh trials**;
- a hard delivery/accessibility failure count greater than **0** disqualifies that operating point;
- with 59/59 successes, the one-sided 95% exact binomial lower confidence bound is at least approximately 0.95;
- each trial uses fresh unpredictable witness challenges and fresh delivery-attempt/session identity;
- required evidence/chunk/page positions are randomized across trials so a fixed omission location cannot hide between probes;
- a capability limit is never set above the largest operating point satisfying the criterion;
- the qualified byte/token/file-count limit is additionally capped at **80% of the smallest observed failing boundary** when a failure boundary is observed;
- when no failing boundary has been observed, the qualified bound is capped at **80% of the largest fully tested passing point**, never at an untested vendor-advertised maximum;
- intermittent, timeout, ambiguous, or unverifiable outcomes count as failures for qualification;
- provider profiles expire after **7 days** by default and immediately on material provider/model/deployment/account/endpoint/region/adapter/file-processing/session behavior drift;
- requalification repeats the full applicable acceptance protocol; a single “health check” cannot renew an expired profile.

Provider-specific policies may be stricter but may not be weakened by the candidate under review.

For capabilities that are categorical rather than scalar (for example archive parsing or file visibility), the same 59-fresh-trial/zero-hard-failure criterion applies to every claimed supported mode unless a stricter governed policy is preregistered.

## Provider capability profile

A `ProviderCapabilityProfile` is trusted platform configuration/evidence, not candidate-authored content.

It must bind:

- provider;
- provider account/tenant/project identity where relevant;
- API endpoint/region/data-residency boundary;
- exact requested model and provider-reported model/deployment identity where available;
- model alias/version drift policy;
- API/adapter version;
- trusted adapter hash/version;
- qualified request/body size;
- qualified cumulative context size with safety margin;
- attachment/file support;
- supported representations/media types;
- maximum file count;
- per-file size limits;
- file visibility semantics;
- server-side file reference semantics;
- session/thread/conversation semantics;
- fresh-session guarantee or full prior-context capture semantics;
- provider-injected mutable system/developer/custom instructions;
- account/project/workspace memory behavior;
- provider-side knowledge/retrieval connectors and defaults;
- staged-message behavior;
- context eviction/truncation behavior;
- structured-output behavior;
- provider response/output constraints;
- empirical qualification evidence from repeated fresh witness trials;
- qualification timestamp;
- expiry/requalification policy;
- conservative qualified limit and safety margin derived from repeated trials, not a single success.

Unknown capability is not capability.

Profiles must expire or be invalidated on material provider/model/adapter/API behavior drift. Candidate code may not mint or widen a profile.

A single successful provider call near a limit is not sufficient to widen the qualified bound. Qualification uses fresh canaries over repeated trials and chooses a conservative safe limit under the governed acceptance policy.

Automatic provider/model fallback is a new delivery context. A failure on provider/model A may not silently fall back to B using A's manifest/profile. The fallback requires its own qualified profile, delivery plan/attempt identity, and admissibility record.

The authoritative capability registry must be outside the candidate's self-approval boundary. A capability-profile change is itself governed configuration requiring independent review appropriate to its authority. Material candidate changes must not be able to edit the profile that decides whether their own review delivery is complete.

## Trusted adapter and wire binding

The platform must bind what it intended to send to what its trusted provider adapter actually serialized.

For every provider call, retain a `WireDeliveryRecord` containing:

- delivery attempt ID;
- review request ID;
- manifest hash;
- adapter identity/hash/version;
- call sequence number;
- evidence/chunk IDs included;
- canonical secret-redacted request-body hash;
- exact non-secret request metadata relevant to semantics;
- provider account/endpoint/region identity used;
- requested model identity and provider-reported model/deployment identity when the latter is required by the governed drift policy; if the provider cannot expose a required deployment identity, that identity-dependent qualification cannot be claimed;
- provider request/message/file/thread/session IDs;
- transport status;
- response hash;
- retry/idempotency identity;
- timestamp.

A manifest and prompt hash without wire binding do not prove that the adapter included the frozen evidence in the API request.

The adapter must serialize from the frozen representation bytes/chunks referenced by the manifest. Hashing one file and later reopening the same pathname for upload is insufficient unless byte identity is reverified immediately before dispatch.

Provider secrets are excluded from reproducible hashes but their exclusion must not permit semantic request fields to be omitted from binding.

## Delivery preflight

Before review adjudication:

1. Verify current ReviewRequest integrity.
2. Derive required evidence set from governed sources.
3. Materialize every required reference.
4. Verify source bytes/hashes.
5. Apply only governed representations/transforms.
6. Resolve data-classification/egress authorization.
7. Resolve a non-expired trusted provider capability profile.
8. Build and freeze the EvidenceDeliveryManifest.
9. Prove the exact delivery plan fits the qualified provider/mode.
10. Freeze exact call/chunk ordering and prompt identities.
11. Emit `DELIVERY_PREFLIGHT_PASS` only if every mandatory item is deliverable.
12. Immediately before each wire call, revalidate the still-current capability/egress/session prerequisites.
13. Dispatch the exact frozen representation bytes/chunks produced during preflight; do not re-read mutable source paths.

If a required item cannot be safely represented or delivered, fail before treating any reviewer disposition as authoritative.

Manifest freeze and wire dispatch form a TOCTOU boundary. A source path, generated representation, capability profile, egress decision, or provider file may not change between validation and use without invalidating the attempt or creating a new governed attempt.

## Chunking limitation

**Chunking is a transport mechanism, not a way to exceed the model's qualified adjudication context.**

Sending N chunks over time does not prove that all N remain simultaneously available to the model at final adjudication. Earlier messages may be evicted, summarized, or otherwise unavailable.

Therefore a chunked material review is admissible only when one of these is qualified:

1. the complete final adjudication working set, including prompt and all mandatory representations, remains within the provider's qualified cumulative context; or
2. the provider exposes a qualified persistent file/retrieval mechanism whose content identity, accessibility, and final-review binding are validated; or
3. a governed decomposed-review protocol explicitly scopes independent subreviews and a separately qualified aggregation review covers required cross-evidence interactions.

A plain multi-message sequence must not be used to claim arbitrarily large context.

## Clean material-review context and delivery session binding

A material review must start from a **fresh semantic context** unless the platform can prove the entire pre-existing context is governed and equivalent to the frozen review context.

Preferred rule:

- stateless API mode: use a fresh request containing or referencing all mandatory governed evidence through a qualified mechanism;
- stateful API mode: create a new provider session/thread/conversation for the review attempt, with no prior user/assistant/tool messages.

For a stateful mode, the platform must bind:

- provider session/thread/conversation ID;
- all platform-supplied system/developer/user prompts;
- file IDs;
- message IDs;
- manifest hash;
- delivery attempt ID;
- enabled tools/connectors;
- account/project/workspace custom instructions;
- persistent memory state/configuration;
- provider-side knowledge/retrieval connectors;
- any other mutable semantic context the provider exposes.

Prior conversation messages, prior tool outputs, account/workspace memory, custom instructions, or knowledge connectors must be absent, disabled, or completely captured and governed.

If the provider/mode injects mutable semantic context that cannot be enumerated, disabled, or drift-bound, that provider/mode is `NOT_QUALIFIED_FOR_MATERIAL_REVIEW`.

Provider-internal fixed safety/model policy that cannot be extracted is a provider capability property, not governed review content. The platform must not claim to hash or know it. Material use is allowed only when the provider/mode documents that no additional mutable account/session/project semantic context is injected and the exact provider/model/deployment profile has passed the governed behavioral qualification. Material drift requires requalification.

For stateless provider modes, every final review request must itself contain or reference all mandatory evidence through a qualified mechanism.

A receipt from one session/request cannot prove completeness for a verdict from another. A clean receipt followed by a verdict in a dirty or different context is inadmissible.

## Server-side file references

A successful file upload or opaque provider file ID does not prove model accessibility.

A provider file mechanism is qualified only when the platform has evidence for:

- content identity at upload;
- stable association with exact provider account/context;
- accessibility from the final review request;
- retention/expiry behavior;
- file replacement/mutability behavior;
- supported format parsing and processing/ingestion readiness states;
- retrieval range/coverage semantics where partial retrieval is possible;
- failure behavior.

If these are unknown, file-reference delivery is non-authoritative for material review.

When final adjudication depends on provider retrieval/file tools, the ProviderCapabilityProfile must declare whether deterministic access/range logs are required for the claimed review mode. If those logs are required to prove completeness and the provider does not expose them, the mode is not qualified for that claim.

A semantic review citation to an evidence ID that the platform knows was inaccessible or never retrievable cannot be treated as `TESTED_SUPPORTED`. When deterministic retrieval logs are available and required, review coverage is grounded to those logs rather than reviewer-authored citation text alone.

## Reviewer receipt and availability acknowledgement

A reviewer receipt is a useful diagnostic, not an independent trust root.

Where supported, a staged reviewer may return a non-dispositive receipt with:

- request ID;
- manifest/corpus hash;
- evidence/chunk IDs reported accessible;
- unsupported/inaccessible items;
- session/file references;
- completeness claim.

The platform must compare this receipt against its own delivery records and provider capability profile.

A reviewer statement such as `received_all=true` cannot override missing wire records, hash mismatches, unsupported formats, or an unqualified capability profile.

## Delivery witness probes

For provider/modes where the platform cannot otherwise establish model-visible accessibility, qualification and/or per-attempt delivery may use platform-generated unpredictable witness probes.

A witness probe:

- is generated by the trusted platform after the delivery attempt identity is fixed;
- is not derived from candidate content;
- uses fresh high-entropy values not repeated in the ordinary prompt/manifest visible to the reviewer;
- is placed in platform-controlled framing or synthetic qualification artifacts without modifying the authoritative scientific bytes;
- requires an exact response bound to request/session/chunk/evidence identity;
- is verified by the platform against the secret expected value;
- is non-dispositive and cannot itself satisfy semantic review.

For live provider capability qualification, sparse beginning/middle/end canaries are not sufficient when the provider does not expose deterministic truncation/range semantics.

In that case, qualification must use one of these governed accessibility methods:

1. **dense witness mode** — every required transport chunk/evidence boundary is independently challenged with fresh canaries, and no unprobed required segment exceeds the governed probe granularity;
2. **deterministic range/retrieval mode** — provider retrieval logs or range semantics independently prove complete access to every required range/member/page;
3. **reduced safe bound** — only the densely probed region is qualified and all unprobed required content is treated as context-incomplete.

Default dense-witness granularity for raw-text capability qualification is a maximum of **2048 UTF-8 bytes per probed segment**, with fresh independent witness framing at every segment boundary and randomized content-location challenges across trials. Provider-specific experiments may adopt a smaller granularity or deterministic range proof, but not a larger unprobed interval without independent review.

For opaque attachments, qualification must probe each independently reviewable page/range/member or use deterministic provider retrieval/access logs. If neither is possible, the attachment mode is not qualified for full-artifact material review.

For a material review attempt, witness probes may strengthen evidence that the provider/model could access delivered representations, but they still do not prove semantic attention.

A copied item ID or hash that was already supplied in the prompt is not a valid witness of content access.

## Meaning of REVIEW_CONTEXT_COMPLETE

`REVIEW_CONTEXT_COMPLETE=true` means only:

- the platform proved complete governed materialization and wire delivery;
- the selected provider/mode has a current qualified capability profile for the representation/session mechanism;
- all required evidence is bound to the final adjudication request/session under that profile;
- no known delivery/context defect is present.

It does **not** mean the platform proved model cognition, attention, or semantic use of every token.

## Prompt/evidence isolation dependency

EXP-M does not qualify prompt-injection safety.

For material authority review, delivery admissibility additionally depends on the applicable EXP-L or successor prompt/evidence-isolation controls being qualified.

Delivering all evidence perfectly must not be treated as safe if candidate-controlled evidence can hijack the reviewer instructions.

EXP-M may test delivery independently, but a production review path requires both boundaries.

## Review decomposition and aggregation

If evidence cannot fit one qualified final context, the platform may not simply split it into several reviews and call their agreement a full review.

A decomposed protocol must preregister:

- dimension/subreview scopes;
- exact evidence set per subreview;
- cross-dimension interaction requirements;
- aggregation logic;
- evidence needed by the aggregator;
- conditions under which no global disposition is allowed.

The proposer may not define the interaction list by itself. The pinned delivery/review governor must independently derive a `RequiredInteractionContract` from governing standards, mandatory dimensions, evidence relationships, and protected-transition rules. Any proposer/ReviewRequest interaction declaration is checked against that independently derived contract. Omitted required interaction families block a global disposition before subreview aggregation.

If material cross-evidence interactions cannot be reviewed within a qualified context, the review remains bounded/incomplete.

## Verdict admissibility

A reviewer verdict may enter the promotable review path only when all are true:

- current valid ReviewRequest;
- governed required-evidence closure;
- complete materialization;
- governed representation/transformation;
- egress authorization;
- trusted non-expired provider capability profile;
- trusted adapter/wire binding;
- complete required item/chunk delivery;
- valid session/file-reference binding where used;
- qualified reviewer-context availability;
- applicable prompt/evidence-isolation dependency satisfied;
- semantic review coverage valid;
- reviewer provenance valid;
- disposition otherwise promotable.

Immediately before verdict admission, revalidate that the ProviderCapabilityProfile, egress authorization, provider session/file state, and required prompt/evidence-isolation dependencies are still current. Expiry or revocation after the final wire call but before verdict admission blocks promotion or requires a newly governed decision, according to the governing expiry policy.

A semantic `PASS` with unproven delivery completeness is non-promotable.

## Insufficient-evidence cause adjudication

When a reviewer returns `INSUFFICIENT_EVIDENCE` or equivalent:

1. Compare the reviewer's claimed missing items/dimensions with the authoritative evidence inventory.
2. If required evidence never existed: `SCIENTIFIC_EVIDENCE_MISSING`.
3. If the governed required set was incomplete: `EVIDENCE_SELECTION_INCOMPLETE`.
4. If source existed but materialization failed: `EVIDENCE_MATERIALIZATION_FAILED`.
5. If transformation/representation was unqualified: `EVIDENCE_TRANSFORMATION_UNQUALIFIED`.
6. If materialized representation was omitted/corrupted in delivery: `EVIDENCE_DELIVERY_INCOMPLETE`.
7. If provider/session/file capability was insufficient: `REVIEW_CONTEXT_INCOMPLETE`, `EVIDENCE_FORMAT_UNSUPPORTED`, or `EVIDENCE_ATTACHMENT_UNAVAILABLE`.
8. If both scientific and delivery gaps exist: `MIXED_INSUFFICIENCY`.
9. If cause cannot be proven: `INSUFFICIENT_EVIDENCE_CAUSE_UNRESOLVED`.
10. Never convert delivery failure into scientific failure or scientific absence into a transport excuse.

## Multi-reviewer equivalence

Reviewer agreement is not consensus evidence unless the platform proves evidence-delivery comparability.

For every compared reviewer retain:

- reviewer-specific manifest;
- provider capability profile;
- representation/transformation records;
- wire delivery records;
- session/file bindings;
- completeness result;
- final verdict.

Two reviewers receiving different representations are comparable only if a governed equivalence rule permits those representations for all compared review dimensions.

## Retry and failure history

Each delivery attempt has a stable attempt ID and immutable records.

A retry must either:

- reproduce the same frozen manifest and delivery semantics under a new attempt ID; or
- create a new governed delivery manifest when representation/protocol materially changes.

Failed attempts remain preserved. A later complete retry cannot rewrite an earlier incomplete attempt as complete.

## Reviewer tools and out-of-manifest evidence

A material reviewer must not silently introduce ungoverned external evidence through web search, retrieval plugins, arbitrary tools, or provider-side knowledge connectors.

For a material review, reviewer tools are either:

- disabled; or
- explicitly governed, allowlisted, and their retrieved evidence is captured with provenance, hashes/identifiers, and review-dimension binding under an applicable external-evidence governance path.

Evidence discovered through reviewer tools cannot retroactively count as if it had been part of the frozen delivery manifest. If new material evidence changes the review basis, the platform records a governed supplemental evidence boundary or a new review request/delivery attempt as required.

Model recollection/training knowledge remains non-authoritative evidence.

## Security and false-green rules

The following must never independently establish delivery completeness:

- reviewer says it received everything;
- HTTP 2xx;
- provider upload success;
- opaque file ID;
- evidence count copied from outgoing metadata;
- token estimate;
- whole-corpus hash without required-item closure;
- citation to one or more artifacts;
- green CI;
- proposer assertion;
- candidate-authored provider capability profile;
- chunk count without cumulative-context qualification;
- multi-reviewer agreement;
- candidate-supplied materializer/manifest/checker code;
- one successful provider call near a claimed capability limit;
- automatic fallback to a different provider/model without a new qualified delivery attempt;
- hashing one byte set and uploading a later re-read mutable path without revalidation;
- ungoverned reviewer web/tool retrieval presented as frozen evidence.

## Required audit evidence

Every material platform API review must retain:

- ReviewRequest;
- governed evidence inventory;
- EvidenceDeliveryManifest;
- source and representation hashes;
- stable evidence IDs and canonical source-path/identity mapping;
- pinned delivery-governor implementation identity;
- transformation records;
- egress decision;
- ProviderCapabilityProfile identity;
- prompt identities;
- pre-dispatch revalidation result for capability/egress/session state;
- WireDeliveryRecords;
- chunks where used;
- provider session/file/message IDs where used;
- reviewer receipt if used;
- DeliveryCompletenessResult;
- provider raw responses;
- witness-probe challenges/results where used;
- provider retrieval/tool access logs where available;
- parsed review;
- insufficient-evidence adjudication where needed;
- semantic validation;
- VerdictAdmissibilityResult.

## Governance scope

This standard supplements review provenance, semantic review coverage, portable packet integrity, external-evidence classification, and independent-review prompt/evidence governance.

It specifically governs **required-evidence closure, delivery integrity, provider-context qualification, and verdict admissibility**.


---

# INLINE SOURCE: experiments/governed-platform/exp-m-review-evidence-delivery-integrity.md

Git blob: `773c52aaa9ecc7826493d34ab9745b6ca719b169`

# EXP-M — Review Evidence Delivery & Reviewer Context Integrity Falsification

## Status

`PREREGISTERED_BEFORE_EXECUTION`

## Motivation

The governed platform already distinguishes platform API review from pasted external evidence and binds review requests, reviewer identity, corpus hashes, semantic dimensions, and portable packet integrity.

EXP-M targets the next exposed trust boundary:

**authoritative evidence existing in the platform does not prove that the selected reviewer actually received the complete required evidence context.**

The failure mode is especially important for multi-model API review. Different providers may differ in:

- context capacity;
- file/attachment support;
- file size/count limits;
- format parsing;
- request truncation behavior;
- staged-message semantics;
- attachment visibility to the model.

A model may return `INSUFFICIENT_EVIDENCE` because evidence is truly absent, or because the platform failed to deliver it. Conversely, a model may return `PASS` after receiving only a subset of the required evidence.

EXP-M falsifies whether the platform can distinguish and fail closed on these states.

## Relationship to EXP-L

EXP-L governs independent review evidence/prompt integrity, materialization, citation grounding, prompt-injection boundaries, and frozen review execution.

EXP-M is complementary and narrower:

- EXP-L asks whether the review corpus and prompt are governed correctly.
- EXP-M asks whether that frozen corpus is actually delivered completely into the reviewer context and whether the verdict is admissible only after completeness is proven.

EXP-M does not supersede EXP-L.

## Core hypothesis

A material reviewer disposition cannot become admissible unless the platform proves that every mandatory evidence item in the frozen delivery manifest was delivered in an approved representation and the reviewer context was complete before adjudication.

## Invariants

### M-I01 — Scientific existence and delivery are separate facts

The platform must preserve independent states for:

- authoritative evidence existence;
- evidence materialization;
- evidence delivery;
- reviewer accessibility/context completeness.

### M-I02 — Delivery failure cannot masquerade as scientific insufficiency

If required evidence exists but the reviewer did not receive it, the outcome must not be classified solely as scientific `INSUFFICIENT_EVIDENCE`.

### M-I03 — Scientific absence cannot masquerade as delivery failure

If evidence genuinely does not exist, the platform must not blame transport/provider limits.

### M-I04 — Required evidence set is manifest-bound before dispatch

Every mandatory artifact and chunk is identified, hashed, sized, ordered, and bound to the exact ReviewRequest before provider invocation.

### M-I05 — Provider capability is explicit

The platform must not assume support for file types, attachment visibility, corpus size, or context capacity.

### M-I06 — No silent evidence omission

If required evidence cannot fit or cannot be consumed, dispatch must fail closed or use a separately qualified chunk protocol.

### M-I07 — Chunk completeness

Missing, duplicated, reordered, cross-request, corrupted, or stale chunks cannot establish context completeness.

### M-I08 — Reviewer receipt is non-dispositive

A completeness/receipt phase cannot itself create a review disposition.

### M-I09 — Review cannot begin before delivery completion

The platform must reject a disposition produced before required evidence delivery is complete.

### M-I10 — HTTP/API transport success is not delivery proof

HTTP 2xx, upload success, or API acceptance cannot independently establish model-visible evidence completeness.

### M-I11 — Required raw evidence cannot be replaced by unauthorized summaries

A compacted/summarized representation is only acceptable when the review contract explicitly permits that representation and it is integrity-bound.

### M-I12 — Provider-specific evidence profiles are preserved

When reviewers receive different representations, the difference must be explicit and dispositions must not be treated as directly equivalent without qualification.

### M-I13 — Verdict admissibility depends on delivery completeness

A semantic `PASS` is non-promotable if delivery completeness is not proven.

### M-I14 — Incomplete-context negative verdict remains diagnostic

A reviewer `CHANGES_REQUIRED` or `INSUFFICIENT_EVIDENCE` based on incomplete delivery is useful diagnostic evidence but cannot be misrepresented as a complete scientific adjudication.

### M-I15 — Failed delivery history is immutable

Retries do not erase or rewrite failed delivery attempts.

### M-I16 — Requiredness is platform-owned

A delivery manifest may not decide which evidence is required. Mandatory/optional status must be derived from the current governed ReviewRequest, dimensions, evidence refs, standards, and experiment contract.

### M-I17 — Wire payload is bound

A frozen manifest must be bound to the exact trusted-adapter request payloads that were actually dispatched. Manifest intent without wire binding is insufficient.

### M-I18 — Provider capability profiles are trusted and expiring

Provider/model/API/adapter capability profiles must come from a platform-owned qualified registry, include qualification evidence and expiry, and fail closed on drift or unknown state.

### M-I19 — Chunking cannot manufacture context

Multi-message chunking may transport evidence but may not be used to claim context beyond the provider's qualified cumulative final-review availability.

### M-I20 — Delivery session identity is load-bearing

Evidence delivery, receipt, provider file references, and final verdict must bind to the same qualified delivery attempt/session or to a stateless request that rebinds every mandatory item.

### M-I21 — Representation transformation is governed

Raw evidence converted to text, pages, Markdown, archive members, OCR, or summaries must carry source/representation hashes and an allowed transformation contract. Partial/lossy representations cannot silently satisfy raw evidence requirements.

### M-I22 — Evidence egress is governed

Required evidence may not be sent to a provider unless data-classification and egress policy authorize that provider/mode/representation. Unsafe evidence cannot be silently redacted or omitted and still count complete.

### M-I23 — Prompt/evidence isolation is a production dependency

A material review path cannot qualify from EXP-M alone when candidate-controlled evidence can alter reviewer instructions. Applicable EXP-L/successor prompt-isolation controls must also be qualified.

### M-I24 — Review decomposition cannot overclaim global coverage

Several bounded subreviews cannot be aggregated into a global review unless the protocol preregisters cross-dimension interactions and a qualified aggregation step.

### M-I25 — Remote accessibility is probed, not self-attested

Where provider/model-visible accessibility cannot be established from trusted transport semantics alone, qualification or delivery uses fresh platform-generated witness probes. Reviewer echo of already supplied IDs/hashes is insufficient.

### M-I26 — Capability authority is outside candidate self-approval

The capability profile/registry used to judge review delivery cannot be widened by the candidate under review.

### M-I27 — Retrieval-backed coverage is grounded where possible

When provider retrieval/file tools are used, reviewer evidence references must not claim tested support for evidence known to be inaccessible; platform/tool access logs are retained and used when available.

### M-I28 — Delivery governor is outside candidate self-approval

The materializer, manifest builder, representation transformer, capability-profile authority, preflight, adapter, completeness validator, and verdict-admissibility code must be pinned to an independently governed platform implementation, not mutable candidate code.

### M-I29 — Capability qualification is repeated and conservative

A provider/model/API capability profile cannot be widened from one successful call. Qualification uses repeated fresh probes and a governed safety margin.

### M-I30 — Endpoint/model/account drift invalidates qualification

Provider account/tenant, endpoint/region, adapter, requested model, or provider-reported deployment drift requires requalification or a separately bound delivery attempt.

### M-I31 — Automatic fallback cannot inherit another provider's qualification

Fallback to a different provider/model/API mode requires a new qualified profile and delivery attempt identity.

### M-I32 — Transformation/parsing is a governed attack surface

Candidate-controlled parsers, archive path traversal, symlink escape, duplicate member names, decompression bombs, and parser resource exhaustion cannot silently produce an authoritative reviewer representation.

### M-I33 — Evidence IDs are collision-resistant and canonical

Stable evidence IDs bind governed source identity plus content hash; canonical path/ID collisions cannot replace one required item with another.

### M-I34 — Frozen bytes survive manifest-to-wire TOCTOU

The bytes hashed/materialized during preflight are the bytes dispatched. Mutable source paths, transformed outputs, capability state, egress decisions, or provider files cannot change after validation without revalidation/new attempt identity.

### M-I35 — Reviewer tools cannot silently widen evidence

Web/search/plugin/retrieval evidence outside the frozen delivery corpus is non-authoritative unless separately governed and captured. Tool access cannot silently become part of the review basis.

### M-I36 — ReviewRequest completeness is independently derived

The pinned governor derives a RequiredEvidenceContract and mandatory-dimension set independently from governing standards/experiment/protected-transition rules. ReviewRequest refs/dimensions are validated against that contract and cannot narrow it.

### M-I37 — Material review context is clean

Material reviews use a fresh stateless request or fresh stateful provider session with no ungoverned prior messages, memory, tool outputs, custom instructions, or knowledge connectors. Uncapturable mutable provider-side semantic context disqualifies the provider/mode.

### M-I38 — Capability qualification thresholds are preregistered

Live provider capability qualification uses a fixed statistical acceptance policy before exposure: at least 59 independent fresh trials per claimed operating point, zero hard failures, one-sided 95% exact-binomial lower bound at least approximately 0.95, conservative 80% safety-margin rule, and 7-day/default drift-triggered requalification.

### M-I39 — Accessibility probes are dense enough for the claimed bound

When deterministic truncation/range evidence is unavailable, no required raw-text segment larger than 2048 UTF-8 bytes remains unprobed during capability qualification; opaque files require page/range/member-level probes or deterministic retrieval logs.

### M-I40 — Provider-injected semantic context is fail-closed

Provider/model modes must inventory or disable mutable default/custom prompts, project/account memory, and provider-side knowledge connectors. Unknown mutable semantic context makes the mode NOT_QUALIFIED_FOR_MATERIAL_REVIEW.

### M-I41 — Cross-evidence interaction requirements are independently derived

Review decomposition uses a platform-derived RequiredInteractionContract from standards/mandatory dimensions/evidence relationships; proposer-declared interaction lists cannot silently omit required interaction families.

## Required mechanism surfaces

Future implementation should expose governed objects equivalent to:

- `EvidenceDeliveryManifest`
- `ProviderCapabilityProfile`
- `DeliveryPreflightResult`
- `EvidenceChunk`
- `ReviewerReceipt`
- `DeliveryCompletenessResult`
- `InsufficientEvidenceAdjudication`
- `VerdictAdmissibilityResult`

Names are not authoritative; semantics are.

## Frozen test families

### M-01 — Missing required final chunk

Deliver N-1 of N required chunks.

Expected:
- completeness false;
- review adjudication blocked;
- no promotable verdict.

### M-02 — Missing middle chunk

Drop a non-final chunk while preserving total metadata.

Expected:
- exact missing chunk detected;
- no silent reconstruction/pass.

### M-03 — Duplicate chunk

Deliver one chunk twice and omit another.

Expected:
- duplicate and missing identities both detected.

### M-04 — Reordered chunks

Deliver all chunks out of order.

Expected:
- either deterministic canonical reconstruction with verified IDs/hashes or fail closed;
- no semantic concatenation based on arrival order.

### M-05 — Modified chunk bytes

Alter one byte after manifest freeze.

Expected:
`EVIDENCE_CHUNK_HASH_MISMATCH`.

### M-06 — Wrong-request chunk replay

Replay a valid chunk from a previous ReviewRequest.

Expected:
request/corpus binding rejection.

### M-07 — Stale-reviewer receipt replay

Replay completeness acknowledgement from an earlier corpus.

Expected:
receipt request/corpus mismatch.

### M-08 — Provider unsupported ZIP/TAR

Manifest requires archive evidence but provider mode cannot expose archive contents.

Expected:
`EVIDENCE_FORMAT_UNSUPPORTED`;
no review authority.

### M-09 — Accepted upload but model cannot access attachment

Transport reports upload success; reviewer context cannot enumerate/use attachment.

Expected:
`EVIDENCE_ATTACHMENT_UNAVAILABLE`;
HTTP success does not upgrade completeness.

### M-10 — Context limit truncates trailing evidence

Construct corpus where decisive evidence is in the tail beyond qualified context.

Expected:
preflight blocks dispatch or completeness fails;
no silent reviewer verdict admission.

### M-11 — Context limit truncates middle evidence

Use provider/test adapter that drops an internal segment.

Expected:
item/chunk coverage mismatch.

### M-12 — Evidence count mismatch

Manifest requires 40 items; delivered corpus has 39.

Expected:
completeness false.

### M-13 — Manifest count copied without materialization

Outgoing envelope claims correct count but actual delivered item set is incomplete.

Expected:
independent reconstruction rejects.

### M-14 — Whole-corpus hash only false green

Whole outgoing payload hash exists but per-item required evidence mapping is missing.

Expected:
delivery completeness remains unproven.

### M-15 — Reviewer claims complete without proof

Reviewer returns `received_all_evidence=true` but platform delivery record is incomplete.

Expected:
reviewer self-attestation cannot establish completeness.

### M-16 — Reviewer adjudicates before receipt phase

Provider returns PASS immediately before completeness protocol completes.

Expected:
verdict inadmissible.

### M-17 — Genuine scientific evidence missing

Required artifact is absent from authoritative store before delivery.

Expected:
`SCIENTIFIC_EVIDENCE_MISSING`;
must not be called delivery failure.

### M-18 — Evidence exists, delivery omitted it

Artifact exists and is manifest-bound but is dropped before provider context.

Expected:
`EVIDENCE_DELIVERY_INCOMPLETE`;
must not be scientific insufficiency.

### M-19 — Provider format divergence

Same authoritative evidence sent to Reviewer A as raw Markdown and Reviewer B through unsupported archive/attachment mode.

Expected:
delivery profiles differ;
results not treated as equivalent consensus until both deliveries qualify.

### M-20 — One reviewer complete, one incomplete

Multi-review pipeline: one reviewer receives complete corpus; another misses mandatory evidence.

Expected:
only complete review may be considered under review semantics;
incomplete review is diagnostic/non-promotable.

### M-21 — Summary substituted for required raw artifact

Replace a mandatory raw log with proposer-generated summary.

Expected:
representation-class mismatch unless contract explicitly allows summary.

### M-22 — Chunk retry mutation

Retry a chunk with same index but different bytes/hash.

Expected:
binding mismatch; immutable failed attempt preserved.

### M-23 — Provider retry uses different corpus

Same ReviewRequest retry changes chunking/order/content.

Expected:
reject unless new delivery manifest/review execution boundary is created.

### M-24 — Missing evidence masked by long prompt

Required evidence is absent but prompt describes its supposed contents.

Expected:
prompt assertion cannot satisfy evidence presence.

### M-25 — Citation to inaccessible evidence

Reviewer cites evidence item that was manifest-listed but not delivered.

Expected:
coverage cannot be `TESTED_SUPPORTED`.

### M-26 — Partial file parsing

Provider exposes only first pages/portion of a required artifact.

Expected:
byte/range coverage recorded; full-required artifact remains incomplete.

### M-27 — Binary/encoding corruption

UTF-8/raw artifact transformed during delivery.

Expected:
hash/representation mismatch.

### M-28 — Evidence delivery timeout

Chunk delivery stalls before completion.

Expected:
non-authoritative delivery failure, preserved for retry.

### M-29 — Cross-provider context-capability mismatch

Corpus fits one provider but exceeds another.

Expected:
provider-specific preflight outcomes; no universal "review-ready" claim.

### M-30 — Negative verdict cause adjudication

Reviewer returns `INSUFFICIENT_EVIDENCE`.

Expected:
platform deterministically attributes missing requirement to:
scientific source, delivery/context, format capability, or unresolved cause.

### M-31 — Required evidence downgraded to optional

Mutate a governed mandatory evidence ref to optional only inside the delivery manifest.

Expected:
required-evidence closure mismatch; reject before dispatch.

### M-32 — Trusted adapter omits manifest item from wire request

Manifest is complete but serialized API request drops one required item.

Expected:
wire delivery record mismatch; verdict inadmissible.

### M-33 — Candidate-authored capability profile widens limits

Candidate supplies a permissive profile claiming unsupported files/context are qualified.

Expected:
untrusted profile rejected.

### M-34 — Expired provider capability profile

Use previously qualified profile after expiry or material adapter/model version drift.

Expected:
preflight fail closed; requalification required.

### M-35 — Chunk sequence exceeds cumulative final context

Each chunk individually fits, but the final conversation/context would evict earlier required evidence.

Expected:
chunking does not qualify delivery; review blocked unless qualified persistent retrieval exists.

### M-36 — Receipt and verdict use different provider sessions

Evidence/receipt is bound to session A and final verdict to session B.

Expected:
session binding mismatch; verdict inadmissible.

### M-37 — Opaque provider file ID replay

Reuse a previously valid provider file ID in another request/account/session without independently qualified binding.

Expected:
file reference unqualified or session mismatch.

### M-38 — Lossy representation treated as raw

Send a summary/partial extraction where full raw evidence is required.

Expected:
transformation/representation rejection.

### M-39 — Partial PDF/page extraction

Required PDF has decisive content outside delivered page range.

Expected:
range coverage incomplete; no full-artifact claim.

### M-40 — Unauthorized evidence egress

Required corpus contains evidence not permitted for the selected provider/region/mode.

Expected:
preflight blocks delivery; no silent omission/redaction.

### M-41 — Redaction changes load-bearing evidence

Redaction removes or changes content needed by a mandatory review dimension.

Expected:
representation not sufficient; provider not qualified for that review.

### M-42 — Perfect delivery with prompt-injection boundary unqualified

All evidence delivery checks pass, but applicable EXP-L/successor prompt-isolation gate is not qualified.

Expected:
delivery may be recorded complete but material verdict remains non-promotable.

### M-43 — Decomposed reviews miss cross-evidence interaction

Two subreviews each pass on separate evidence subsets while the defect exists only in their interaction.

Expected:
no global PASS unless cross-interaction aggregation contract is satisfied.

### M-44 — Wire retry changes semantic request body

Retry uses same manifest/attempt semantics but adapter changes system prompt, tool config, or evidence payload.

Expected:
wire hash mismatch and immutable failed-attempt record.

### M-45 — Reviewer echoes visible evidence IDs but cannot answer hidden canary

Provider/model repeats manifest IDs yet fails exact fresh witness values embedded only in delivered content.

Expected:
accessibility qualification fails; self-acknowledgement is insufficient.

### M-46 — Fresh head/middle/tail witness probes

Fresh canaries are placed across context boundaries.

Expected:
all exact values recoverable under the qualified provider profile; any missing position lowers the safe capability bound.

### M-47 — Stale canary replay

Reviewer/provider returns a canary from an earlier qualification attempt.

Expected:
attempt-bound witness mismatch.

### M-48 — Candidate modifies capability registry

Candidate branch changes profile limits/format support used to review itself.

Expected:
untrusted capability authority; review path blocked.

### M-49 — Retrieval citation without tool access

Reviewer cites a required evidence ID but provider tool logs show no successful retrieval/access and mode requires retrieval for availability.

Expected:
coverage cannot be TESTED_SUPPORTED.

### M-50 — Retrieval log proves wrong file version

Tool access succeeds for stale/wrong content hash.

Expected:
evidence identity mismatch; verdict inadmissible.

### M-51 — Candidate modifies delivery governor

Candidate changes its own manifest builder/completeness validator to omit decisive evidence.

Expected:
candidate delivery-governor implementation is not authoritative; review path blocked.

### M-52 — Candidate supplies transformation parser

Candidate-provided parser converts a required artifact into a favorable representation.

Expected:
untrusted transformation implementation rejected.

### M-53 — ZIP path traversal / symlink escape

Archive contains ../ paths, absolute paths, symlink escapes, or duplicate member names.

Expected:
safe materializer rejects/quarantines; no complete evidence claim.

### M-54 — Decompression/resource bomb

Archive/document expansion exceeds governed size/time/memory limits.

Expected:
materialization fails closed without host damage.

### M-55 — Evidence ID collision

Two different source artifacts are assigned same stable ID/path after normalization.

Expected:
collision detected; manifest invalid.

### M-56 — Single lucky capability success

One near-limit canary trial succeeds while repeated trials expose intermittent loss.

Expected:
profile not widened from single success; conservative safe bound retained.

### M-57 — Model alias/backend drift

Requested model name stays the same but provider-reported deployment/version changes materially.

Expected:
profile invalidated or bounded according to drift policy.

### M-58 — Endpoint/region/account mismatch

Qualified profile is for one endpoint/account/region; review runs through another.

Expected:
profile mismatch; preflight/verdict inadmissible.

### M-59 — Automatic fallback reuses primary profile

Primary provider fails and orchestrator silently uses fallback provider/model without new manifest/profile binding.

Expected:
reject; new delivery attempt/profile required.

### M-60 — File processing pending

Provider upload returns success but file ingestion/indexing remains pending at final review.

Expected:
attachment unavailable/context incomplete.

### M-61 — Partial retrieval coverage

Provider retrieval returns only a snippet/range while review contract requires full artifact.

Expected:
coverage incomplete; no TESTED_SUPPORTED for full-artifact dimension.

### M-62 — Source bytes mutate after manifest freeze

Hash/materialize file, mutate pathname before adapter upload, then attempt delivery.

Expected:
adapter uses frozen bytes or immediate revalidation detects mismatch; no silent TOCTOU substitution.

### M-63 — Generated representation mutates before wire send

Transformation output changes after manifest freeze.

Expected:
wire/representation hash mismatch; attempt invalid.

### M-64 — Capability profile expires mid-attempt

Profile valid at preflight but expired/materially invalid before final wire call/verdict.

Expected:
pre-dispatch/final admissibility revalidation blocks completion.

### M-65 — Egress authorization revoked after preflight

Policy allowed at manifest freeze but is revoked before send.

Expected:
dispatch blocked or new authorization required.

### M-66 — Ungoverned reviewer web search

Reviewer uses external web/tool source not in governed evidence set and cites it as basis for PASS.

Expected:
external evidence non-authoritative; review cannot claim frozen-evidence coverage from it.

### M-67 — Governed reviewer tool retrieval

Allowlisted tool returns captured, provenance-bound supplemental evidence under governed boundary.

Expected:
may be retained only under explicit supplemental/new review evidence semantics; no silent manifest rebinding.

### M-68 — ReviewRequest omits standard-required evidence

The governing RequiredEvidenceContract requires evidence E, but the ReviewRequest does not reference or deterministically derive E.

Expected:
EVIDENCE_SELECTION_INCOMPLETE before manifest freeze.

### M-69 — ReviewRequest omits standard-required mandatory dimension

A mandatory dimension derived from governing standards is absent from the ReviewRequest.

Expected:
ReviewRequest invalid; no delivery attempt.

### M-70 — Dirty reused provider thread

Manifest evidence is delivered into a stateful session containing prior ungoverned messages/tool outputs.

Expected:
provider/mode attempt not context-clean; verdict inadmissible.

### M-71 — Provider default/custom prompt drift

Provider/project custom instruction or injected mutable prompt differs from the qualified profile.

Expected:
profile/context drift; NOT_QUALIFIED or requalification required.

### M-72 — Provider-side memory enabled

Account/project/session memory is active but not captured/disabled.

Expected:
material review mode NOT_QUALIFIED.

### M-73 — Provider-side knowledge connector silently enabled

Provider account injects retrieval/knowledge context not governed by the manifest.

Expected:
material review mode NOT_QUALIFIED or separately governed supplemental boundary.

### M-74 — Insufficient provider qualification trials

Operating point has fewer than 59 independent fresh trials even if all pass.

Expected:
capability point remains unqualified.

### M-75 — One hard failure among qualification trials

At least one hard visibility/truncation failure occurs at the claimed operating point.

Expected:
operating point disqualified.

### M-76 — Safety margin omitted

The tested passing/failure boundary is used directly instead of applying the governed 80% cap.

Expected:
profile invalid.

### M-77 — Internal omission between sparse canaries

Head/middle/tail probes pass, but an unprobed required internal segment is omitted.

Expected:
sparse witness method cannot qualify the claimed range; fail closed.

### M-78 — Dense per-segment witness detects omission

A required text segment within the 2048-byte probe granularity is omitted.

Expected:
missing witness/content challenge causes qualification failure.

### M-79 — Opaque attachment has unprobed required page/range

Attachment mode lacks deterministic retrieval logs and not every required page/range/member is probed.

Expected:
full-artifact material review mode unqualified.

### M-80 — Interaction family omitted from proposer plan

Platform RequiredInteractionContract contains interaction X; proposer ReviewRequest/subreview plan omits X.

Expected:
global review aggregation blocked.

### M-81 — Capability expires after final provider response before verdict admission

Provider response exists, but the capability profile becomes expired before verdict admissibility.

Expected:
verdict non-promotable until newly governed validation.

### M-82 — Egress authorization revoked after final provider response before verdict admission

Expected:
verdict admission blocked according to current policy; stale preflight cannot authorize promotion.

## Required mutation/falsification cases

Mutation suite must attempt to make a verdict admissible by:

- forcing `context_complete=true`;
- forcing `received_all=true`;
- deleting a mandatory manifest item;
- altering required/optional flags;
- lowering expected chunk count;
- ignoring hash mismatch;
- trusting HTTP 200;
- trusting provider upload ID;
- accepting reviewer self-acknowledgement;
- converting delivery insufficiency into scientific insufficiency;
- converting scientific insufficiency into delivery failure;
- marking unsupported file as delivered;
- reusing old receipt;
- reusing old chunk;
- rebinding corpus hash;
- ignoring provider capability profile;
- treating different reviewer corpora as consensus;
- admitting PASS before receipt completion;
- allowing manifest-requiredness to override governed requiredness;
- accepting candidate-authored capability profile;
- accepting expired capability profile;
- treating chunk count as proof of cumulative final context;
- accepting receipt from another session;
- accepting opaque file ID without qualified content/session binding;
- accepting lossy transformation as full raw evidence;
- bypassing evidence egress policy;
- aggregating decomposed subreviews without cross-interaction coverage;
- omitting wire-request hash binding;
- admitting material verdict when prompt/evidence-isolation dependency is unqualified;
- trusting candidate-owned manifest/materializer/completeness code;
- accepting one successful near-limit capability probe as qualification;
- ignoring endpoint/account/region/model-deployment drift;
- inheriting capability profile across provider/model fallback;
- trusting candidate-provided transformation parser;
- ignoring archive traversal/resource-limit failures;
- allowing evidence-ID collision to replace required content;
- treating upload success as file processing readiness;
- re-reading mutable source bytes after manifest freeze without revalidation;
- ignoring capability/egress expiry between preflight and dispatch;
- admitting ungoverned reviewer web/tool evidence as frozen corpus evidence;
- trusting an incomplete ReviewRequest as the full required-evidence authority;
- omitting a standard-required mandatory dimension;
- reusing a dirty provider session;
- ignoring provider custom-prompt/memory/connector drift;
- accepting fewer than 59 capability trials;
- accepting any hard capability failure at a claimed point;
- skipping the governed 80% safety margin;
- treating sparse canaries as proof for unprobed required regions;
- omitting a platform-derived cross-evidence interaction;
- accepting an expired capability/egress state at verdict admission.

Every load-bearing mutation must be rejected.

## Required provider test adapters

The experiment should use deterministic fake/provider adapters before live-provider testing:

- `CompleteProviderAdapter`
- `DropFinalChunkAdapter`
- `DropMiddleChunkAdapter`
- `DuplicateChunkAdapter`
- `ReorderChunkAdapter`
- `CorruptChunkAdapter`
- `AttachmentInvisibleAdapter`
- `ContextTailTruncationAdapter`
- `PartialFileAdapter`
- `EarlyVerdictAdapter`
- `UnsupportedFormatAdapter`
- `WireOmissionAdapter`
- `ExpiredCapabilityProfileAdapter`
- `CrossSessionVerdictAdapter`
- `OpaqueFileReplayAdapter`
- `LossyRepresentationAdapter`
- `EgressDeniedAdapter`
- `ContextEvictionAdapter`
- `DecomposedCrossInteractionAdapter`
- `CanaryBlindAdapter`
- `StaleCanaryReplayAdapter`
- `CandidateProfileOverrideAdapter`
- `RetrievalCitationWithoutAccessAdapter`
- `WrongRetrievalVersionAdapter`
- `CandidateGovernorOverrideAdapter`
- `UntrustedTransformerAdapter`
- `ArchiveTraversalAdapter`
- `ArchiveBombAdapter`
- `EvidenceIdCollisionAdapter`
- `FlakyNearLimitAdapter`
- `ModelDriftAdapter`
- `EndpointDriftAdapter`
- `FallbackProfileReuseAdapter`
- `FileProcessingPendingAdapter`
- `PostManifestSourceMutationAdapter`
- `ExpiredMidAttemptAdapter`
- `EgressRevokedAdapter`
- `UngovernedReviewerToolAdapter`
- `IncompleteReviewRequestAdapter`
- `DirtySessionAdapter`
- `ProviderPromptDriftAdapter`
- `ProviderMemoryEnabledAdapter`
- `ProviderKnowledgeConnectorAdapter`
- `InsufficientTrialsAdapter`
- `FlakyCapabilityAdapter`
- `SparseCanaryGapAdapter`
- `MissingInteractionFamilyAdapter`
- `PostResponseExpiryAdapter`

Live API pilots come only after deterministic adapters prove the governor behavior.

## Live provider pilots

For each configured real provider/model/API mode, preregister a capability pilot that measures rather than assumes:

- maximum safe review corpus size;
- usable attachment formats;
- attachment count/size limits;
- whether uploaded files are actually model-visible;
- one-shot vs staged review support;
- response behavior near context limit;
- deterministic or detectable truncation behavior;
- fresh unpredictable witness-canary recovery at beginning/middle/end and across attachment/file boundaries;
- retrieval/tool access-log behavior when that mode is used.

Provider limits are observations bound to provider/model/API/adapter version and an expiry/requalification policy; they are not universal constants.

A live pilot must also preserve exact wire-request hashes, provider request/session/file identifiers, and any server-reported usage/context metadata available. Provider marketing/documentation values may inform preregistration but do not replace observed platform-qualified limits.

## Acceptance rule

EXP-M can reach bounded pass only when:

1. every mandatory frozen test passes;
2. no mutation can make an incomplete delivery verdict promotable;
3. scientific vs delivery insufficiency is deterministically separated;
4. provider capability uncertainty fails closed;
5. multi-reviewer comparison preserves reviewer-specific delivery identity;
6. failed delivery history is preserved;
7. no review authority is minted from completeness self-attestation;
8. required-evidence status cannot be downgraded by the delivery layer;
9. exact trusted-adapter wire requests are bound to the frozen manifest;
10. chunking cannot claim context beyond the provider's qualified final-review availability;
11. provider capability profiles are trusted, version-bound, and non-expired;
12. representation transformations and evidence egress are governed;
13. material review remains blocked when the applicable prompt/evidence-isolation dependency is unqualified;
14. decomposed review cannot overclaim cross-evidence coverage;
15. delivery-governor implementation is pinned outside candidate self-approval;
16. provider capability bounds are repeated/conservative and invalidate on material drift;
17. provider/model fallback cannot inherit a different delivery qualification;
18. representation transformers/materializers are trusted and resource/path safe;
19. stable evidence IDs cannot collide or rebind required content;
20. manifest-to-wire TOCTOU cannot substitute later mutable bytes/state;
21. ungoverned reviewer tools cannot silently widen the evidence basis;
22. ReviewRequest completeness is independently cross-checked against a platform-derived RequiredEvidenceContract;
23. material reviews use a fresh/clean semantic context or the provider/mode is disqualified;
24. provider capability qualification obeys preregistered statistical thresholds, safety margin, and requalification interval;
25. provider-injected mutable semantic context is inventoried/disabled or the provider/mode is disqualified;
26. accessibility probing is dense enough for the claimed content range;
27. cross-evidence interaction requirements are independently derived;
28. capability/egress/session validity is rechecked at verdict admission.

A one-provider success cannot prove cross-provider delivery integrity.

## Nonclaims

EXP-M does not prove:

- the model semantically attended to every delivered token;
- arbitrary provider internals;
- cryptographic proof of remote model memory;
- universal provider limits;
- scientific correctness of the evidence itself.

It governs what the platform can prove about materialization, delivery, context completeness, and verdict admissibility.

## Governance effect

Until EXP-M is qualified for a review path, evidence-delivery completeness for large/multipart/file-based API reviews is a governed open boundary.

This preregistration authorizes no promotion and changes no existing authority state.


---

# INLINE SOURCE: experiments/governed-platform/EXP-M-TEST-MATRIX.md

Git blob: `5f21e04a126b1450939dfdf1969556dc6e224156`

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


---

# INLINE SOURCE: governance-runtime/LIVE-CONVERSATION-GOVERNANCE.md

Git blob: `a9e5255244421a67490c13be2ce5b525f253f96a`

# Live Conversation Governance Runtime

## Purpose

Apply governed-platform rules to the human–LLM development conversation so chat-window changes, model confidence, shared-memory drift, reviewer substitution, reviewer self-identification, review-delivery mode, pasted content, packet representation, or reviewer-disposition overclaim cannot silently change authoritative project state.

This is an operational control for our collaboration. It does not claim that the ChatGPT product itself enforces these rules internally.

## Authority precedence

1. Governed Git/evidence bound to exact revisions.
2. Governed registries/checkpoints referenced by Git.
3. Governed shared project memory as active continuity/coordination whose material pointers must resolve to authority.
4. Current project chats/files as working context.
5. Ungoverned summaries/caches as advisory navigation.
6. Model recollection/confidence has no authority.

Shared memory is actively read and written, but never independently authoritative. Conflict is surfaced; authoritative state wins; memory is repaired rather than silently merged.

## Session bootstrap

Before authoritative continuation in a fresh chat/session:

1. Read `governance-runtime/shared-memory.json`.
2. Read `governance-runtime/session-state.json`.
3. Verify referenced branches, commits, review requests/evidence, and frozen artifacts.
4. Read applicable governed standards.
5. Reconcile memory/chat context with authority.
6. If authority cannot be verified, enter `GROUNDING_REQUIRED`.

A chat boundary may not change claim status, experiment state, review state, revision identity, evidence validity, promotion eligibility, or terminal authority.

## Review levels and platform modes

Review requirement and interaction mode are independent dimensions.

### Review levels

- `NONE` — no review requested for non-authoritative/routine work.
- `RECOMMENDED` — R1 may recommend review for non-mandatory work.
- `REQUIRED` — protected authority transition cannot promote without valid independent review.

R1 may raise `NONE` to `RECOMMENDED`; R1 may not lower a protected transition to optional merely by changing a trigger label.

### `AUTO_MODE`

When review is recommended/required, the platform dispatches the configured provider API automatically via `AUTOMATIC_API`. A successful authenticated execution is classified `PLATFORM_AUTO_API_REVIEW`.

### `MANUAL_MODE`

R1 shows its answer first. When review is recommended/required, the UI shows controls such as `Ask Claude` / `Ask DeepSeek`. A user click dispatches the configured provider API through `USER_INITIATED_API`. A successful authenticated execution is classified `PLATFORM_USER_INITIATED_API_REVIEW`.

For `RECOMMENDED`, the user may skip review. For `REQUIRED`, the user may decline the call, but the protected authoritative transition remains pending/non-authoritative.

Changing AUTO ↔ MANUAL changes **who initiates the provider API call only**. It never changes evidence, identity, independence, semantic review, or promotion rules.

## Review execution classes

There are exactly two platform review execution classes:

1. `PLATFORM_AUTO_API_REVIEW` — `AUTO_MODE` + `AUTOMATIC_API`.
2. `PLATFORM_USER_INITIATED_API_REVIEW` — `MANUAL_MODE` user action + `USER_INITIATED_API`.

Both use trusted provider adapters and the same ReviewRequest, semantic coverage, identity, independence, fail-closed, and promotion semantics. Neither class derives reviewer provenance from reviewer-authored content.

For material review, the provider execution must also use a fresh/clean semantic context under the qualified provider capability profile. Reused threads/conversations with ungoverned prior messages, tool outputs, memory, custom instructions, or knowledge connectors are not eligible unless the entire pre-existing context is independently captured and governed. Unknown mutable provider-side semantic context disqualifies the provider/mode for material review.

Copy/paste is **not** a platform review transport.

## External evidence ingestion

User-pasted/copied material enters a separate evidence family.

### `USER_PROVIDED_EXTERNAL_CONTENT`

This is the default class for pasted review-shaped content when the user has not explicitly identified its source.

- no provider/model origin is inferred from the payload;
- fields such as `reviewer.provider` / `reviewer.model` are self-declared content claims only;
- the content may expose defects or provide useful technical evidence;
- it is not a platform review execution and cannot satisfy a mandatory platform review gate.

### `USER_ATTESTED_EXTERNAL_LLM_REVIEW`

Only after the user explicitly identifies pasted material as a review from an external LLM may it be reclassified to this class.

- user attestation records the reported provider/model source;
- user attestation is **not** provider-API authentication;
- self-declared payload identity must never create or upgrade provenance;
- the content remains external evidence and is non-promotable by itself.

Core rule: **content cannot establish its own provenance**.

Historical `MANUAL_RELAY` artifacts remain readable and preserved, but `MANUAL_RELAY` is no longer a platform review transport. Legacy manual-relay results are external evidence/history only.

## Material authority review floor

`can_promote_material_transition` is the authority boundary. Material promotion is **review-required by definition**, regardless of the caller-supplied `trigger` string.

The UI/orchestration classifier additionally fails closed for:

- known mandatory-review triggers;
- explicit material transitions;
- governing-standard review requirements;
- governance-relevant paths including `governance-runtime/`, `standards/`, `experiments/governed-platform/`, and `.github/workflows/`.

A proposer mislabel such as `ROUTINE_FORMATTING` cannot waive review at the material promotion gate.

## ReviewRequest and current-state binding

A mandatory platform review is represented by an integrity-bound `ReviewRequest` containing at least:

- request identity;
- exact reviewed artifact commit;
- proposer provider/model;
- required reviewer provider plus model/model-class constraint;
- blind-review requirement;
- review questions;
- evidence references;
- material/standard/path classification context.

For material promotion, the runtime additionally requires a semantic review contract (ReviewRequest schema 4+) containing machine-readable `required_review_dimensions`. A legacy review request without this semantic contract may be preserved as historical content but cannot authorize material promotion.

The ReviewRequest is not authoritative about its own completeness. Before delivery, a pinned platform governor independently derives a `RequiredEvidenceContract` and mandatory-dimension/interaction set from governing standards, experiment/qualification contract, protected-transition classification, and platform-owned evidence-selection rules. The ReviewRequest must cover that independently derived contract; any omitted standard-required evidence, mandatory dimension, or required cross-evidence interaction fails closed as `EVIDENCE_SELECTION_INCOMPLETE`.

Promotion must bind review evidence to the currently authoritative review request and current reviewed artifact. A review for a superseded request or older revision cannot be replayed into a later candidate.

## Semantic review coverage and disposition consistency

A reviewer conclusion is not valid merely because its `disposition` token is syntactically allowed.

Every schema-4 material ReviewRequest defines explicit review dimensions with:

- stable dimension ID;
- `mandatory` boolean;
- description;
- governed closed coverage-status vocabulary.

ReviewEvidence must provide one `review_coverage` entry for every dimension, containing:

- `dimension_id`;
- status;
- concrete evidence references/observations where the dimension was tested;
- a non-empty assessment of what was actually examined.

Allowed dimension statuses are:

- `TESTED_SUPPORTED`
- `TESTED_DEFECT_FOUND`
- `CONTRADICTED`
- `NOT_TESTED`
- `UNAVAILABLE`
- `INACCESSIBLE`
- `INSUFFICIENT`

Semantic disposition rules are deterministic:

- `PASS` requires every listed review dimension to be `TESTED_SUPPORTED`, with non-empty evidence for each.
- `BOUNDED_PASS` requires every `mandatory: true` dimension to be `TESTED_SUPPORTED`; only explicitly non-mandatory dimensions may remain bounded.
- `NOT_TESTED` / `INSUFFICIENT_EVIDENCE` are correct when one or more mandatory dimensions are unavailable, inaccessible, not tested, or insufficient.
- `FAIL` / `CHANGES_REQUIRED` require at least one concrete finding and a contradicted, defective, or insufficient coverage state.
- negative review outcomes can be valid review evidence but are not promotable.
- only semantically valid `PASS` or `BOUNDED_PASS` may satisfy the review side of material promotion.

Free-text `evidence_assessment` explains structured coverage but cannot substitute for it. If free text contradicts an asserted `PASS`, the review fails closed. `REV-GOV-PR5-008` is a permanent regression fixture for this failure family.

## Reviewer identity provenance

Reviewer-authored JSON fields such as:

```json
{"reviewer":{"provider":"anthropic","model":"claude-..."}}
```

are content claims, **not authentication**.

`AUTOMATIC_API` and `USER_INITIATED_API` derive provider/model identity from the trusted configured provider adapter/execution envelope. Review content must agree with that trusted identity; disagreement fails closed.

Pasted external evidence has no platform-authenticated provider identity. If the user explicitly identifies the external source, that creates user-attested provenance only.

## Review execution to promotion wiring

Material promotion consumes all of these directly:

1. deterministic gate result;
2. authoritative checkpoint;
3. grounded shared memory;
4. current schema-4 ReviewRequest with required dimensions;
5. ReviewEvidence with complete semantic coverage;
6. a trusted platform API execution/provenance envelope whose review class matches its API transport.

No caller-provided boolean such as `valid_independent_review_present=True`, no pasted JSON, and no user-attested external review can mint review validity.

Review fails closed when execution is missing, pending, errored, non-platform transport, wrong request, wrong revision, unauthenticated, wrong provider/model, self-review, malformed, non-blind when blind review is required, semantically inconsistent, negative/non-promotable, or conflicts with its trusted execution identity.

Consensus is metadata, not evidence, and cannot bypass deterministic evidence gates.

## Review evidence delivery completeness

Material review requires a second independent boundary between **evidence existence/materialization** and **evidence actually delivered into reviewer context**.

The normative delivery rules are defined in `standards/review-evidence-delivery-integrity.md` and falsified by EXP-M.

Core rules:

- a valid ReviewRequest and complete authoritative evidence store do not prove reviewer-context completeness;
- every material API review must freeze a content-addressed evidence delivery manifest before dispatch;
- provider/model/API capability for the selected evidence representation must be explicitly qualified or the review fails closed;
- required evidence may not be silently dropped because of context, file-count, file-type, attachment, or request-size limits;
- large corpora require a qualified deterministic chunk protocol with request/corpus/chunk identity and hashes;
- a reviewer disposition is inadmissible until required evidence delivery/context completeness is established;
- HTTP success, file-upload success, reviewer self-acknowledgement, or a copied evidence count cannot independently prove completeness;
- `INSUFFICIENT_EVIDENCE` must be adjudicated into scientific-source insufficiency, delivery/context insufficiency, format/capability insufficiency, mixed insufficiency, or unresolved cause;
- delivery failure must never be silently converted into scientific failure, and scientific absence must never be excused as delivery failure;
- multi-reviewer consensus is meaningful only when reviewer-specific delivery manifests prove equivalent required evidence or explicitly governed provider-specific representations.

Until EXP-M qualifies this boundary for a provider/mode, large, multipart, or file-dependent platform API reviews remain non-promotable when reviewer-context completeness is unproven.

## Shared-memory grounding

Before material promotion, shared memory must reconcile with authoritative checkpoint state for at least:

- active workstream branch;
- exact workstream head;
- workstream status;
- current review request;
- current review status;
- pending review coordination.

Stale/conflicted memory blocks material promotion until reconciled.

Authoritative persistence occurs before memory synchronization. If memory synchronization later fails, authority remains valid and memory is marked stale. If authoritative persistence fails, authoritative completion is blocked.

## Portable external review/evidence export

A portable packet may still be generated for advisory external review/evidence work when the external model has zero repository/browser/tool access. That export is an **external evidence transport artifact**, not a platform review execution and not a substitute for `AUTOMATIC_API` or `USER_INITIATED_API`.

A portable export should contain:

- exact ReviewRequest or review context;
- exact reviewed candidate identity;
- explicit review dimensions;
- detached manifest;
- human-readable packet;
- raw canonical repository artifacts where required;
- per-artifact SHA-256 and exact byte length over raw Git blob UTF-8 bytes;
- evidence-reference coverage;
- CI/builder evidence;
- whole-packet/logical hashes;
- `repository_access_required: false`.

Raw files are byte-authoritative. Markdown fences are convenience only. If an external reviewer cannot inspect a mandatory dimension, its external result must not claim that dimension was tested.

Portable-packet integrity makes external evidence more useful; it does **not** upgrade external evidence into a platform-authenticated review.

## Frozen evidence and repair discipline

For falsification/acceptance work:

1. preregister/freeze where required before exposure;
2. preserve first exposure;
3. classify before repair;
4. never change frozen tests/fixtures/expectations merely to get green;
5. changes to frozen artifacts after exposure require a new governed boundary and independent review;
6. preserve superseded/invalid attempts and correction history;
7. construction green is not scientific acceptance when a later frozen acceptance run is required.

## Failure taxonomy

At minimum preserve/surface:

- `MEMORY_OVERRIDES_AUTHORITY`
- `SHARED_MEMORY_STALE_UNDETECTED`
- `SHARED_MEMORY_CONFLICT_SILENTLY_MERGED`
- `MODEL_CONFIDENCE_BYPASSED_REVIEW`
- `PROPOSER_CONTROLLED_REVIEW_CLASSIFICATION`
- `MANDATORY_REVIEW_SKIPPED`
- `REVIEWER_IDENTITY_SELF_ATTESTATION_ACCEPTED`
- `EXTERNAL_CONTENT_SELF_PROVENANCE_ACCEPTED`
- `USER_ATTESTATION_TREATED_AS_PROVIDER_AUTHENTICATION`
- `EXTERNAL_EVIDENCE_TREATED_AS_PLATFORM_REVIEW`
- `REVIEW_INDEPENDENCE_UNPROVEN`
- `REVIEW_WRONG_REVISION_ACCEPTED`
- `SUPERSEDED_REVIEW_REPLAY_ACCEPTED`
- `REVIEW_TRANSPORT_CHANGED_POLICY`
- `PLATFORM_MODE_CHANGED_AUTHORITY`
- `API_FAILURE_TREATED_AS_APPROVAL`
- `REVIEW_ID_SEMANTIC_REBIND`
- `CONSENSUS_AS_EVIDENCE`
- `REVIEW_DISPOSITION_EVIDENCE_CONTRADICTION`
- `REVIEW_REQUIRED_DIMENSION_OMITTED`
- `REVIEW_PASS_WITH_UNTESTED_MANDATORY_DIMENSION`
- `NEGATIVE_REVIEW_TREATED_AS_PROMOTABLE`
- `LEGACY_REVIEW_SCHEMA_PROMOTED`
- `PORTABLE_REVIEW_BUNDLE_TAMPERED`
- `PORTABLE_REVIEW_MANIFEST_MISMATCH`
- `PORTABLE_REVIEW_RAW_HASH_UNREPRODUCIBLE`
- `SCIENTIFIC_EVIDENCE_MISSING`
- `EVIDENCE_SELECTION_INCOMPLETE`
- `REVIEW_CONTEXT_DIRTY_OR_UNBOUND`
- `PROVIDER_SEMANTIC_CONTEXT_UNQUALIFIED`
- `PROVIDER_CAPABILITY_STATISTICAL_POLICY_FAILED`
- `ACCESSIBILITY_PROBE_COVERAGE_INSUFFICIENT`
- `REVIEW_INTERACTION_CONTRACT_INCOMPLETE`
- `EVIDENCE_DELIVERY_INCOMPLETE`
- `REVIEW_CONTEXT_INCOMPLETE`
- `EVIDENCE_FORMAT_UNSUPPORTED`
- `EVIDENCE_ATTACHMENT_UNAVAILABLE`
- `EVIDENCE_CHUNK_MISSING`
- `EVIDENCE_CHUNK_DUPLICATE`
- `EVIDENCE_CHUNK_REORDERED`
- `EVIDENCE_CHUNK_HASH_MISMATCH`
- `EVIDENCE_MANIFEST_MISMATCH`
- `EVIDENCE_RECEIPT_UNPROVEN`
- `REVIEW_STARTED_BEFORE_DELIVERY_COMPLETE`
- `REVIEW_VERDICT_INADMISSIBLE_DELIVERY_FAILURE`
- `REVIEW_DELIVERY_GOVERNOR_SELF_APPROVAL`
- `EVIDENCE_WIRE_REQUEST_MISMATCH`
- `EVIDENCE_SESSION_BINDING_MISMATCH`
- `PROVIDER_CAPABILITY_PROFILE_UNQUALIFIED`
- `PROVIDER_CAPABILITY_PROFILE_STALE`
- `EVIDENCE_TRANSFORMATION_UNQUALIFIED`
- `EVIDENCE_EGRESS_NOT_AUTHORIZED`
- `EVIDENCE_DELIVERY_TOCTOU`
- `REVIEW_TOOL_EVIDENCE_UNGOVERNED`
- `FAILURE_HISTORY_REWRITTEN`
- `TERMINAL_AUTHORITY_SELF_GRANTED`

## Live operating procedure

1. Recover shared memory.
2. Verify against authoritative Git/evidence.
3. Reconcile stale/conflicting memory.
4. Classify work/review level.
5. Preregister/freeze when applicable.
6. Execute narrow construction.
7. Preserve first failures/revisions.
8. Apply platform review policy.
9. In AUTO_MODE, dispatch `AUTOMATIC_API`; in MANUAL_MODE, show reviewer controls and dispatch `USER_INITIATED_API` only after user selection.
10. Treat copy/paste as external evidence ingestion, initially `USER_PROVIDED_EXTERNAL_CONTENT`.
11. Reclassify pasted content to `USER_ATTESTED_EXTERNAL_LLM_REVIEW` only when the user explicitly identifies the source; never equate that attestation with API authentication.
12. Bind platform reviewer identity from trusted execution provenance.
13. Materialize and hash every required review evidence item.
14. Independently derive and validate the RequiredEvidenceContract, mandatory dimensions, and required cross-evidence interactions.
15. Validate a current provider capability profile under the preregistered statistical/expiry policy and establish a fresh/clean material-review context.
16. Freeze the evidence delivery manifest.
17. Deliver through a qualified one-shot or deterministic chunk/file/retrieval protocol.
18. Establish reviewer-context completeness using dense witnesses or deterministic range/retrieval evidence where required.
19. Revalidate capability/egress/session state at verdict admission.
20. Validate ReviewRequest + ReviewEvidence + structured semantic coverage + platform API execution envelope + delivery completeness.
21. Require a positive promotable disposition before platform review can satisfy material promotion.
22. Apply deterministic governor/evidence gate.
23. Persist authoritative checkpoint.
24. Synchronize shared memory.
25. New chat resumes from shared memory then verifies Git.

## Current collaboration limitation

This chat can ingest pasted external evidence, but pasted content is not a platform review execution. Therefore it cannot satisfy a mandatory provider-authenticated PR #5 review gate. In the production platform, both AUTO_MODE and MANUAL_MODE avoid this limitation by using trusted provider API adapters (`AUTOMATIC_API` / `USER_INITIATED_API`).


---

# INLINE SOURCE: experiments/governed-platform/EXP-M-R2-EXTERNAL-REVIEW.md

Git blob: `1340a7e697cd7dad0f449c8b4a7c6580babaa0f4`

# EXP-M External Review R2 — Preserved Review

Disposition: `CHANGES_REQUIRED`

This file preserves the user-supplied independent external review used for the R2 remediation. It is evidence/history only and does not itself grant authority.

## Critical findings

### C-01 — Required-evidence authority is not independently closed against an incomplete ReviewRequest

- Severity: Critical
- Affected: review-evidence-delivery-integrity standard — Required-evidence authority; EXP-M M-I04/M-I16; tests M-31/J01-J02.
- False-green path: an incomplete or proposer-mutated ReviewRequest omits a standard-required evidence ref or mandatory dimension. The delivery layer closes against that incomplete request and can report complete delivery even though decisive evidence was never selected.
- Required fix: independently derive mandatory evidence and dimensions from governed standards/experiment contract and cross-check the ReviewRequest. Missing governed refs/dimensions fail before manifest freeze with EVIDENCE_SELECTION_INCOMPLETE.

## High findings

### H-01 — Material review lacks fresh/clean provider-session or full-context binding

- Severity: High
- False-green path: a reused provider thread contains prior ungoverned messages, tool output, cached evidence, custom instructions, memory, or prompt-injection content. Session ID matches but semantic context is dirty.
- Required fix: fresh provider session/thread for material review or governed capture/clear/hash of all pre-existing semantic context. If provider-side mutable context cannot be captured/disabled, mode is NOT_QUALIFIED_FOR_MATERIAL_REVIEW. Add dirty-thread, prior-tool, default-prompt, and memory tests.

### H-02 — Provider capability qualification lacks preregistered statistical criteria

- Severity: High
- False-green path: a small number of lucky near-limit trials widens a capability profile despite intermittent omission/truncation.
- Required fix: preregister minimum fresh trials, acceptable failure rate, confidence/statistical bound, safety margin, nondeterminism handling, and expiry/requalification interval. Add insufficient-trial/flaky qualification tests.

### H-03 — Provider-injected/default semantic context not fully bound

- Severity: High
- False-green path: provider default prompts, memory, or knowledge connectors alter review instructions/evidence basis outside platform wire hashes.
- Required fix: capability profile binds or disables all mutable provider-injected semantic context; unknown mutable context means NOT_QUALIFIED_FOR_MATERIAL_REVIEW. Add default-prompt drift, provider memory, and knowledge-connector tests.

### H-04 — Witness-canary coverage can be too sparse

- Severity: High
- False-green path: provider drops an internal segment between head/middle/tail canaries while all canaries pass.
- Required fix: per-chunk/evidence-boundary dense probes where deterministic truncation semantics are unavailable, or reduce qualified bound to densely probed region. Add internal-gap omission tests.

### H-05 — Test matrix omits adversarial families above

- Severity: High
- Required fix: explicit falsification/mutation tests for incomplete ReviewRequest requiredness, dirty reused sessions, provider-injected semantic context, insufficient qualification trials, and canary-gap omissions.

## Medium/Low findings

### M-01 — Permissive “where available/where applicable” wording

If information is load-bearing for context completeness and unavailable, the provider/mode must fail closed rather than silently treating it as optional.

### M-02 — Decomposition interaction completeness can be proposer-incomplete

Cross-dimension interaction requirements must be independently derived from governed dimensions/standards, not solely proposer-authored.

### M-03 — Capability/egress expiry after final wire call before verdict admission

Add admissibility-time revalidation and tests for capability, egress, and session invalidation after provider response but before verdict acceptance.

## Gate results from review

- REQUIRED_EVIDENCE_AUTHORITY = FAIL
- DELIVERY_GOVERNOR_TRUST_ROOT = PASS
- WIRE_BINDING = PASS
- CHUNK_CONTEXT_MODEL = PASS
- REMOTE_ACCESSIBILITY_MODEL = FAIL
- PROVIDER_CAPABILITY_QUALIFICATION = FAIL
- REPRESENTATION_GOVERNANCE = PASS
- MATERIALIZATION_SAFETY = PASS
- EGRESS_BOUNDARY = PASS
- SESSION_FILE_RETRIEVAL_BINDING = FAIL
- INSUFFICIENT_EVIDENCE_TAXONOMY = PASS
- MULTI_REVIEWER_EQUIVALENCE = PASS
- DECOMPOSITION_AGGREGATION = PASS
- PROMPT_ISOLATION_DEPENDENCY = PASS
- TOCTOU_RETRY_INTEGRITY = PASS
- REVIEWER_TOOL_EVIDENCE_BOUNDARY = PASS
- TEST_MATRIX_SUFFICIENCY = FAIL

## Review conclusion

- Critical defect remained: C-01.
- High defects remained: H-01 through H-05.
- EXP-M was not ready for implementation/falsification as reviewed.
- EXP-M remained NOT QUALIFIED.
- The external/manual review granted no platform-review or promotion authority.


---

# INLINE SOURCE: experiments/governed-platform/EXP-M-R2-REVIEW-REMEDIATION.md

Git blob: `6b6cc316592a3d0f7482d4f8502d0fac358ad0c4`

# EXP-M R2 External Review Adjudication and Remediation

## Disposition of the supplied review

The external review disposition `CHANGES_REQUIRED` is accepted.

The Critical finding C-01, High findings H-01 through H-05, and Medium/Low findings M-01 through M-03 were evaluated as valid and have been incorporated into the preregistration/design.

This record does not claim independent closure. It documents the design response that is being submitted for R3 review.

## Finding adjudication

| Finding | Evaluation | Remediation |
|---|---|---|
| C-01 incomplete ReviewRequest can narrow required evidence | VALID / CRITICAL | Added independently derived `RequiredEvidenceContract`, mandatory-dimension and required-interaction closure. ReviewRequest is now a declaration checked against platform-derived governing requirements. Ambiguous derivation fails closed. |
| H-01 dirty reused provider session | VALID / HIGH | Material reviews require a fresh stateless request or fresh stateful session, unless all prior semantic context is completely governed. Ungoverned prior messages/tools/memory/custom instructions/connectors disqualify the attempt. |
| H-02 no statistical provider-qualification rule | VALID / HIGH | Added default preregistered policy: >=59 fresh independent trials per claimed point, zero hard failures, one-sided 95% exact-binomial lower bound ~>=0.95, 80% safety-margin cap, 7-day/drift-triggered requalification. |
| H-03 provider-injected semantic context unbound | VALID / HIGH | Provider capability profile now covers mutable default/custom prompts, memory and knowledge connectors. Unknown mutable semantic context => NOT_QUALIFIED_FOR_MATERIAL_REVIEW. |
| H-04 sparse witness coverage | VALID / HIGH | Added dense accessibility policy: deterministic range/retrieval proof or <=2048-byte probed text segments; opaque files require page/range/member-level probes or deterministic logs. Sparse head/middle/tail alone cannot qualify full content. |
| H-05 missing adversarial families | VALID / HIGH | Added explicit falsification/mutation tests for incomplete ReviewRequest, dirty sessions, provider semantic-context drift, insufficient/flaky capability trials, sparse-canary gaps, interaction omissions, and post-response expiry. |
| M-01 permissive where-available wording | VALID / MEDIUM | Load-bearing unavailable information now fails closed; provider/mode cannot claim the identity/accessibility property when required evidence is unavailable. |
| M-02 proposer-authored interaction list | VALID / MEDIUM | Added independently derived `RequiredInteractionContract`; proposer/subreview plans are checked against it. |
| M-03 expiry after wire before verdict | VALID / LOW-MEDIUM | Capability, egress and session state are explicitly revalidated immediately before verdict admission. |

## New governed structures

### RequiredEvidenceContract

Derived by the pinned delivery governor from:

- governing standards;
- experiment/qualification contract;
- protected-transition classification;
- mandatory review dimensions;
- platform-owned evidence-selection rules.

The ReviewRequest must fully cover this contract.

### RequiredInteractionContract

Derived independently from:

- mandatory dimensions;
- governing standards;
- evidence relationships;
- protected-transition rules.

Decomposed review cannot omit platform-required cross-evidence interactions.

### Clean material-review context

Material review uses:

- fresh stateless request; or
- fresh provider thread/session with no prior ungoverned semantic content.

Mutable provider memory, custom instructions, account/project knowledge connectors, or other provider-injected semantic context must be disabled/inventoried and profile-bound. If not, the provider/mode is not qualified.

### Default provider capability statistical policy

Unless a stricter provider-specific policy is independently preregistered:

- minimum 59 independent fresh trials per claimed operating point;
- 0 hard delivery/accessibility failures;
- one-sided 95% exact-binomial lower confidence bound approximately >=0.95;
- ambiguous/timeout/unverifiable trial counts as failure;
- qualified limit <= largest qualifying tested point;
- additionally <=80% of the smallest observed failure boundary;
- if no failure boundary is observed, <=80% of largest fully tested passing point;
- default expiry 7 days;
- immediate requalification on material provider/model/deployment/account/endpoint/region/adapter/session/file behavior drift.

### Dense accessibility policy

When deterministic truncation/range evidence is unavailable:

- sparse head/middle/tail canaries are insufficient;
- raw text qualification has <=2048 UTF-8 bytes per probed segment;
- fresh independent witness framing applies at every segment boundary;
- content locations are randomized across qualification trials;
- opaque attachments require page/range/member-level probes or deterministic provider retrieval/access logs;
- unprobed required content remains context-incomplete.

### Verdict-time revalidation

Immediately before admitting a verdict, the platform revalidates:

- provider capability profile;
- egress authorization;
- provider session/file state;
- prompt/evidence-isolation prerequisites.

Post-response expiry or revocation cannot be hidden by a stale preflight result.

## New/expanded falsification coverage

EXP-M now includes explicit tests for:

- ReviewRequest missing a standard-required evidence ref;
- ReviewRequest missing a mandatory dimension;
- dirty reused provider thread with prior messages;
- prior tool output in session;
- provider custom/default prompt drift;
- provider memory enabled;
- provider-side knowledge connector enabled;
- fewer than 59 capability trials;
- one hard failure among capability trials;
- omitted safety margin;
- sparse-canary internal-gap omission;
- dense per-segment witness failure;
- opaque attachment with unprobed required pages/ranges;
- omitted platform-derived interaction family;
- capability expiry after provider response but before verdict admission;
- egress/session invalidation after response before verdict admission.

## Self-check after remediation

A fresh adversarial design pass was performed on the R2 repairs.

No new Critical/High defect was identified in the specific repaired boundaries.

Remaining limitations are deliberately bounded:

- EXP-M is still design/preregistration only;
- no provider capability has been scientifically qualified;
- no implementation has been accepted;
- the numeric capability policy is intentionally conservative and may be revised only through a new governed preregistration/review boundary;
- fixed opaque provider service-level safety behavior remains a provider nonclaim; mutable provider/account/session semantic context must be controlled or the mode is disqualified;
- this adjudication is not independent review.

## R3 readiness

Disposition for handoff:

`READY_FOR_R3_INDEPENDENT_DESIGN_REVIEW`

No authority effect.
No EXP-M qualification.
No current API review is retroactively validated.
