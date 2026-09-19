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
