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

A delivery manifest and ReviewRequest may not decide which evidence is required. Mandatory/optional status is derived only from the immutable GovernanceAuthoritySnapshot and its platform-owned transition-class, dimension, evidence-selection, evidence-relationship, and governing-standard registries. The ReviewRequest is checked against that contract but is not an input that can narrow it.

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

### M-I27 — Retrieval-backed coverage is mandatory for model-selected retrieval

When the provider/model chooses which file ranges/pages/members to retrieve, deterministic per-attempt access logs are mandatory for material review and must prove hash-matched coverage of every required range before admission. If the provider cannot expose those logs, that retrieval/file mode is diagnostic-only. Reviewer citations never substitute for access logs.

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

Live provider capability qualification uses a fixed risk-budget protocol before exposure: default p_min=0.99, one-sided 95% exact Clopper–Pearson, at least 299/299 successful disjoint confirmation trials at each claimed operating point, zero hard failures, no exclusions/rerolls/optional stopping, production-equivalent envelope/content classes, append-only failure history, conservative 80% scalar safety cap, and 7-day/default drift-triggered requalification.

### M-I39 — Accessibility probes are dense and per-attempt

When deterministic range/retrieval proof is unavailable, qualification and every production material-review attempt use content-bound witnesses for every required lossless slice. Each text slice is no larger than min(2048 UTF-8 bytes, 512 provider-tokenizer tokens). Every slice is challenged in every confirmation trial. Opaque files require media/modality-specific page/range/member proof or governed lossless transformation.

### M-I40 — Provider-injected semantic context is fail-closed

Provider/model modes must inventory or disable mutable default/custom prompts, project/account memory, and provider-side knowledge connectors. Unknown mutable semantic context makes the mode NOT_QUALIFIED_FOR_MATERIAL_REVIEW.

### M-I41 — Cross-evidence interaction requirements are independently derived

Review decomposition uses a RequiredInteractionContract derived only from the GovernanceAuthoritySnapshot's platform-owned relationship registry, mandatory dimensions, transition class, and governing standards. Each interaction is an explicit set of raw evidence refs that must coexist in one qualified context; proposer-declared interaction lists cannot narrow it.

### M-I42 — Governor decision inputs are outside candidate self-approval

The GovernanceAuthoritySnapshot, transition-class registry, evidence-selection registry, relationship registry, capability registry, and authority-snapshot pointer are outside the candidate write set. Candidate edits to governing inputs are reviewed as evidence and cannot narrow their own review.

### M-I43 — Provider context state is observed per attempt

Every material review carries ProviderContextStateEvidence from the trusted adapter at preflight, before each dispatch, and at atomic admission. Mutable semantic channels that are neither readable nor disable-able make the provider/mode NOT_QUALIFIED_FOR_MATERIAL_REVIEW.

### M-I44 — Confirmation trials are disjoint, scheduled, and append-only

Exploration cannot count as confirmation. Confirmation trial identities/schedule are frozen, all attempted trials count, failures cannot be erased by reruns, and the claimed operating point itself is tested under the production-equivalent envelope.

### M-I45 — Verdict admission is atomic and final

Capability, egress, provider-context/session/file state, authority snapshot, ReviewRequest, and prompt-isolation qualification remain valid from first dispatch through a final compare-and-set admission. Any invalidation in that interval permanently voids the attempt; later requalification cannot revive it.

### M-I46 — Prompt isolation dependency is machine-bound

Material review requires a current hash-bound PromptIsolationQualificationRecord selected deterministically by the governor for the exact provider/representation mode and checked again at atomic admission.

## Required mechanism surfaces

Future implementation should expose governed objects equivalent to:

- `GovernanceAuthoritySnapshot`
- `RequiredEvidenceContract`
- `RequiredInteractionContract`
- `EvidenceDeliveryManifest`
- `ProviderCapabilityProfile`
- `ProviderCapabilityQualificationRecord`
- `ProviderContextStateEvidence`
- `PromptIsolationQualificationRecord`
- `DeliveryPreflightResult`
- `WireDeliveryRecord`
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

### M-46 — Dense per-slice content-bound witness probes

Every required lossless text slice carries a fresh content-bound challenge and framing/end witness in every confirmation trial and production attempt when deterministic range/retrieval proof is unavailable.

Expected:
all slice-local challenges succeed in the same adjudication session; any missing/incorrect slice challenge fails accessibility qualification/admission. Sparse head/middle/tail probes alone never qualify full content.

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

Operating point has fewer than 299 disjoint confirmation trials even if all pass.

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

Provider response exists, but the capability profile becomes expired before atomic verdict admission.

Expected:
the attempt is permanently void; later requalification cannot revive that response.

### M-82 — Egress authorization revoked after final provider response before verdict admission

Expected:
the attempt is permanently void; stale preflight and later reauthorization cannot revive the old response.

### M-83 — Candidate poisons governing standard input

Candidate head removes a required evidence rule from a governance file.

Expected:
GovernanceAuthoritySnapshot/base-head conservative union preserves the base requirement; changed governance file is itself required evidence.

### M-84 — Candidate poisons relationship/classification registry

Candidate supplies a weaker transition class or removes a required evidence relationship.

Expected:
registry outside candidate write set wins; snapshot mismatch/rebinding is rejected.

### M-85 — Unknown transition class / empty contract

Derivation returns unknown class, zero mandatory dimensions, or empty evidence despite a non-vacuous baseline.

Expected:
EVIDENCE_SELECTION_CONTRACT_UNRESOLVED.

### M-86 — Lying provider context readback

Provider adapter/readback claims memory/connectors/custom instructions disabled while behavioral sentinel shows influence.

Expected:
ProviderContextStateEvidence invalid; provider mode unqualified.

### M-87 — Hidden dirty provider state

A mutable provider channel is neither readable nor disable-able.

Expected:
NOT_QUALIFIED_FOR_MATERIAL_REVIEW.

### M-88 — Context state changes between preflight and dispatch

Custom instruction/memory/connector state changes after preflight.

Expected:
monotonic state-version mismatch; attempt void before dispatch.

### M-89 — Context state changes between dispatch and admission

Expected:
atomic admission fails and attempt is permanently void.

### M-90 — Correlated burst confirmation

299 trials are run back-to-back in one short burst rather than the preregistered multi-day/time-block schedule.

Expected:
confirmation protocol invalid even if all pass.

### M-91 — Excluded failed trial / reroll

One attempted confirmation trial fails and is discarded before collecting 299 successes.

Expected:
qualification fails; append-only attempt ledger exposes the exclusion.

### M-92 — Exploration reused as confirmation

Expected:
qualification fails due to non-disjoint evidence families.

### M-93 — Production-envelope mismatch

Confirmation uses synthetic easy content while production uses denser prompt/tools/structured-output/content modality.

Expected:
operating point mismatch; profile cannot authorize production review.

### M-94 — Canary-preserving content loss

Provider preserves framing/sentinels but removes the challenged content span from one slice.

Expected:
content-bound slice challenge fails.

### M-95 — Selective unchallenged sub-slice loss

Provider drops content outside the challenged offset but within a qualified slice.

Expected:
recorded residual/nonclaim risk; transition classes that disallow this residual risk require deterministic range/retrieval proof.

### M-96 — Model-selected retrieval without deterministic access logs

Expected:
retrieval/file mode diagnostic-only; verdict inadmissible.

### M-97 — Retrieval logs miss one required range

Expected:
PROVIDER_RETRIEVAL_COVERAGE_UNPROVEN.

### M-98 — Requalification after mid-attempt expiry

Capability expires after response, then is requalified before checkpoint.

Expected:
old attempt remains void; a new attempt is required.

### M-99 — Delete one VerdictAdmissibilityResult conjunct

Mutation removes any one load-bearing predicate.

Expected:
at least one test kills the mutation; no surviving logic mutation.

### M-100 — Weaken required-evidence closure equality to subset

Expected:
logic mutation killed.

### M-101 — Skip dirty-context, 299-trial, dense-witness, retrieval-log, or atomic-CAS check

Expected:
each logic mutation is independently killed by the suite.

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
- accepting fewer than 299 disjoint confirmation trials;
- accepting any hard capability failure at a claimed point;
- skipping the governed 80% safety margin;
- treating sparse canaries as proof for unprobed required regions;
- omitting a platform-derived cross-evidence interaction;
- accepting an expired capability/egress state at verdict admission;
- deriving authority contracts from candidate-mutated governing inputs;
- accepting unknown/empty transition-class contracts;
- trusting lying/incomplete provider context readback;
- accepting hidden mutable provider state;
- allowing excluded/re-rolled confirmation failures;
- mixing exploration and confirmation evidence;
- qualifying a non-production request envelope;
- treating framing canaries as content-bound proof;
- allowing model-selected retrieval without deterministic coverage logs;
- reviving an invalidated attempt after requalification;
- deleting or weakening any VerdictAdmissibilityResult conjunct;
- weakening equality closure to subset/superset;
- skipping atomic compare-and-set admission.

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
- `AuthorityInputPoisoningAdapter`
- `UnknownTransitionClassAdapter`
- `LyingContextReadbackAdapter`
- `HiddenDirtyStateAdapter`
- `CorrelatedBurstFailureAdapter`
- `FailedTrialReplayAdapter`
- `ProductionEnvelopeMismatchAdapter`
- `CanaryPreservingContentDropAdapter`
- `MissingRetrievalLogAdapter`
- `AtomicAdmissionRaceAdapter`
- `VerdictConjunctMutationAdapter`

Live API pilots come only after deterministic adapters and validator-logic mutation tests prove the governor behavior.

## Live provider pilots

Live pilots begin only after all deterministic phases and validator-logic mutation tests are green.

For each exact provider/account/endpoint/region/model/deployment/adapter/session/file/retrieval mode, preregister exploration and confirmation separately.

Exploration identifies candidate operating points and observed failure boundaries. Confirmation then tests each claimed operating point itself using the frozen default or stricter risk budget:

- 299/299 required successful confirmation trials by default;
- zero hard failures;
- no exclusions/rerolls/optional stopping;
- trials distributed over the preregistered multi-day/time-block schedule;
- fresh clean context and fresh content-bound witnesses every trial;
- production-equivalent prompt/tools/structured-output/output budget;
- worst-case token-density and required media/modality classes;
- every required slice/page/range/member challenged in every trial unless deterministic access/range proof exists;
- append-only trial/failure history.

Pilot evidence also preserves post-SDK transport-semantic hashes, provider context-state records, request/session/file identifiers, retrieval/access logs where the delivery mode requires them, usage/context metadata, and exact profile/drift-epoch identity.

Sparse beginning/middle/end probes are diagnostic only and cannot qualify full required content.

Provider documentation and marketing limits may inform exploration but never substitute for the governed confirmation evidence.

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
28. capability/egress/session validity is rechecked at verdict admission;
29. GovernanceAuthoritySnapshot inputs are pinned outside candidate write authority and base/head governance changes use the conservative merge rule;
30. unknown/empty/vacuous transition contracts fail closed;
31. ProviderContextStateEvidence is observed per attempt and behaviorally sentinel-qualified;
32. confirmation evidence is disjoint from exploration, scheduled, append-only, and uses the exact production operating point;
33. per-attempt content-bound witnesses are mandatory when deterministic range/retrieval proof is unavailable;
34. model-selected retrieval requires deterministic per-attempt full-range coverage logs;
35. VerdictAdmissibilityResult enumerates every load-bearing predicate and atomic compare-and-set admission is the final authority step;
36. every validator-logic conjunct deletion/weakening mutation is killed;
37. PromptIsolationQualificationRecord is machine-checkable, current, and admission-bound.

A one-provider success cannot prove cross-provider delivery integrity.

## Nonclaims

EXP-M does not prove:

- the model semantically attended to every delivered token;
- arbitrary provider internals;
- cryptographic proof of remote model memory;
- universal provider limits;
- scientific correctness of the evidence itself;
- detection of arbitrary selective/sub-slice provider loss when deterministic range/retrieval proof is unavailable; such residual risk is explicitly recorded and may be disallowed by higher-risk transition classes.

It governs what the platform can prove about materialization, delivery, context completeness, and verdict admissibility.

## Governance effect

Until EXP-M is qualified for a review path, evidence-delivery completeness for large/multipart/file-based API reviews is a governed open boundary.

This preregistration authorizes no promotion and changes no existing authority state.
