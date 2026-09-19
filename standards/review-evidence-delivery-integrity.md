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
- provider context-isolation policy registry reader;
- witness-protocol qualification registry reader;
- delivery preflight;
- chunk/session protocol;
- trusted provider adapter/wire serializer;
- delivery completeness validator;
- insufficient-evidence cause adjudicator;
- verdict-admissibility validator.

A candidate under review must not be able to modify the implementation that decides whether its own evidence was complete. Candidate-supplied delivery code may be tested as an artifact, but it cannot grant its own review admissibility.

The governor's **decision inputs** are also part of this trust root. Every material review must bind an immutable `GovernanceAuthoritySnapshot` created from a pre-candidate authority state outside the candidate write set. It contains the governing standard/experiment/registry/classification/evidence-relationship identities and hashes used to derive required evidence and required interactions.

If the candidate changes any governing input in its own head, that head version cannot silently replace the pre-candidate authority snapshot for the candidate's own review. The review uses a conservative merge rule:

- mandatory evidence refs = union(base-authority requirements, candidate-head proposed requirements);
- mandatory dimensions = union(base-authority dimensions, candidate-head proposed dimensions);
- required interaction sets = union(base-authority interactions, candidate-head proposed interactions);
- representation requirements, evidence semantics, statistical thresholds, accessibility-risk policies, and review constraints preserve the stricter base/head requirement;
- every governing element is content-addressed by stable ID plus hash; reuse of the same ID with different semantics/hash is treated as a changed governing input, never as an in-place semantic replacement;
- restrictive classifications/egress/provider constraints use the stricter applicable rule;
- if two governing inputs conflict and no platform-defined partial order can prove which is stricter, derivation fails as `EVIDENCE_SELECTION_CONTRACT_UNRESOLVED`;
- every governing-input change is itself a mandatory review evidence ref.

Registries, context-isolation policies, witness-protocol qualification records, and the authority-snapshot pointer are maintained outside the candidate write set. A candidate may propose changes to governing inputs, but those proposed changes cannot authorize or narrow their own review.

### Conservative base/head comparison rules

The platform-defined “stricter” relation is explicit per governing element class:

| Governing element | Stricter relation |
|---|---|
| required evidence refs / mandatory dimensions / required interactions | set superset is stricter |
| allowed representations | set intersection is stricter; empty intersection => unresolved |
| representation fidelity | raw/lossless > bounded-loss > summary; incomparable media semantics => unresolved |
| required review level | REQUIRED > RECOMMENDED > NONE |
| allowed provider/account/region/tool set | set intersection is stricter; empty set => not qualified |
| data egress / retention / training permissions | deny > conditional allow > allow; conflicting conditions with no partial order => unresolved |
| minimum statistical success bound / confidence | larger lower-bound requirement and larger confidence are stricter |
| tolerated hard failures / residual risk | smaller tolerated value is stricter |
| required confirmation trials | larger minimum is stricter when all other acceptance semantics match |
| profile expiry / requalification interval | shorter validity is stricter |
| runtime byte/token/file limits | smaller maximum is stricter |
| accessibility proof mode | deterministic full-range proof > probabilistic/content-bound proof > self-attestation |
| prompt-isolation requirement | superset of required isolation predicates is stricter |
| transition-class rank | only the authority registry may define the rank; missing/incomparable rank => unresolved |

A same-dimension semantic change with no comparator is **never auto-merged**. It requires a separate independently authorized governance update; for the candidate review it remains `EVIDENCE_SELECTION_CONTRACT_UNRESOLVED`.

## Core authority rule

**A reviewer disposition is inadmissible for a material authority transition unless every mandatory evidence item is governed from source through delivery and the selected provider/mode is qualified to make that exact representation available to the reviewer.**

A `PASS` cannot cure incomplete delivery. A negative result from incomplete delivery may remain useful defect/diagnostic evidence, but it is not a complete scientific adjudication.

## Required-evidence authority

The delivery manifest and the ReviewRequest do not decide what evidence is required by themselves.

Before a ReviewRequest is eligible for delivery, the pinned delivery governor must independently derive a `RequiredEvidenceContract` from the immutable `GovernanceAuthoritySnapshot`, including the protected transition class, platform-owned mandatory-dimension registry, evidence-selection registry, evidence-relationship registry, and applicable governing standards/experiment contracts.

The `ReviewRequest` is a declaration that must be validated against that independently derived contract. It is never an input that can define requiredness.

Every protected transition class has a governed non-vacuous baseline. Unknown transition class, missing registry rule, empty mandatory-dimension set, empty required-evidence set where the baseline requires evidence, or unresolved authority snapshot produces `EVIDENCE_SELECTION_CONTRACT_UNRESOLVED`. Deterministic derivation of an empty set is not sufficient.

The `RequiredEvidenceContract` must contain at least:

- contract schema/version;
- GovernanceAuthoritySnapshot ID/hash/version;
- pre-candidate governing standard/experiment/registry identities and hashes;
- candidate-head governing-input identities/hashes when changed;
- conservative base/head merge result;
- protected transition classification from the governed registry;
- complete mandatory review-dimension set;
- complete required evidence-reference set or deterministic derivation rules;
- representation requirements for each evidence reference/dimension;
- required cross-evidence interaction families;
- deterministic optional-evidence rules;
- ProviderAccessibilityRiskPolicy identity for the protected transition class;
- ProviderContextIsolationPolicy identity for the protected transition class/provider mode;
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
- `GOVERNANCE_AUTHORITY_SNAPSHOT_MISMATCH`
- `REVIEWER_EVIDENCE_ASSESSMENT_CONTRADICTION`
- `PROVIDER_CONTEXT_STATE_UNPROVEN`
- `PROVIDER_CONTEXT_STATE_DRIFT`
- `PROVIDER_CONTEXT_HIDDEN_STATE_RESIDUAL`
- `PROVIDER_CONTEXT_ISOLATION_POLICY_MISSING`
- `PROVIDER_RETRIEVAL_COVERAGE_UNPROVEN`
- `PROVIDER_RETRIEVAL_CONTEXT_BINDING_UNPROVEN`
- `STATISTICAL_INDEPENDENCE_UNPROVEN`
- `VERDICT_ADMISSION_STATE_CHANGED`
- `ADMISSIBILITY_PREDICATE_COVERAGE_INCOMPLETE`
- `IMPLICIT_RETRY_UNOBSERVED`
- `REVIEW_CONTEXT_DIRTY_OR_UNBOUND`
- `PROVIDER_SEMANTIC_CONTEXT_UNQUALIFIED`
- `PROVIDER_CAPABILITY_STATISTICAL_POLICY_FAILED`
- `QUALIFICATION_ATTEMPT_CLOSURE_UNPROVEN`
- `ACCESSIBILITY_PROBE_COVERAGE_INSUFFICIENT`
- `WITNESS_PROTOCOL_UNQUALIFIED`
- `WITNESS_CONTEXT_EVICTION`
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
- exact hashes for every platform-supplied semantic prompt layer (system/developer/user); an absent layer is represented explicitly as EMPTY rather than omitted;
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

## Provider accessibility risk policy

Every protected transition class has a platform-owned `ProviderAccessibilityRiskPolicy` in the GovernanceAuthoritySnapshot.

The policy states whether a material review may rely on probabilistic/content-bound accessibility evidence or requires deterministic range/retrieval proof.

At minimum it binds:

- transition class;
- allowed accessibility proof modes;
- maximum tolerated residual selective/sub-segment loss risk;
- required statistical lower bound;
- whether evidence of trial-independence/correlation control is mandatory for the statistical probability claim;
- whether a deterministic per-attempt proof mode may substitute when statistical independence is unproven;
- whether per-attempt content-bound witnesses are sufficient;
- whether deterministic full-range/page/member access proof is mandatory.

Unknown/missing risk policy fails closed.

The default for the highest material-authority transition class is deterministic full-range/page/member proof or platform-forced inline content under a provider mode whose qualified failure model covers the complete representation. Per-attempt sampling/witnesses alone cannot satisfy that class.

## Provider capability qualification policy

Live provider qualification uses a preregistered risk-budget and confirmation protocol. Exploration and confirmation are separate evidence families.

### Default material-review risk budget

Unless a stricter transition-specific policy is independently governed before exposure:

- target lower bound for per-trial delivery/accessibility success: **p_min = 0.99**;
- confidence: **one-sided 95% exact Clopper–Pearson**;
- zero hard failures are allowed at a claimed operating point;
- with zero failures, the minimum confirmation sample is **299/299** successful trials, because the exact one-sided lower bound is `0.05^(1/299) >= 0.99`;
- every attempted confirmation trial counts, including timeout, provider error, rate-limit, ambiguous, unverifiable, or infrastructure failure; no exclusions, rerolls, or optional stopping;
- exploration trials used to discover limits are never reused as confirmation trials;
- confirmation trial IDs and schedule are frozen before confirmation exposure;
- confirmation trials are distributed across at least **3 distinct UTC days** and at least **4 preregistered time blocks per day**, with operating points interleaved in randomized order;
- repeated attempts from the same provider session/request lineage do not count as independent confirmation trials;
- every trial uses a fresh delivery-attempt identity, fresh clean provider context, fresh content-bound witnesses, and the production-equivalent request envelope;
- the qualification record captures any provider-exposed routing/deployment/region identity and demonstrates the preregistered time/interleaving diversity;
- the Clopper–Pearson probability interpretation is explicitly conditional on the trial-independence model. When provider-side correlation/route allocation is not observable, the profile records `STATISTICAL_INDEPENDENCE_UNPROVEN`; the numerical bound is not presented as a universal provider failure probability and `statistical_qualified=true` is forbidden unless the governing ProviderAccessibilityRiskPolicy explicitly waives the probability claim and requires a deterministic per-attempt accessibility proof mode instead.

### Qualification execution authority and attempt closure

Confirmation qualification uses a dedicated platform-controlled qualification runner and credential scope that candidate code, candidate users, and ordinary operators cannot invoke directly.

Before confirmation exposure, freeze a `ProviderQualificationExecutionPlan` containing:

- provider/profile drift epoch;
- exact operating-point IDs;
- complete scheduled confirmation trial IDs;
- UTC day/time-block assignment;
- deterministic/randomization seed committed before exposure;
- trusted runner identity/hash;
- qualification credential/configuration identity;
- network/egress policy identity;
- expected number of calls.

Every scheduled trial slot must produce exactly one first-attempt record. A missing/skipped slot is a hard failure. A retry or additional call is a new attempt and cannot replace the original failed/missing slot.

The append-only `ProviderCapabilityQualificationRecord` must reconcile:

- every planned trial ID;
- every trusted-runner dispatch record;
- every provider request ID returned;
- provider usage/audit records when exposed.

If provider usage/audit logs are unavailable, the dedicated qualification credential must be technically inaccessible outside the trusted runner and its governed egress path. If neither provider-side call reconciliation nor credential/egress exclusivity can be established, the confirmation set is `QUALIFICATION_ATTEMPT_CLOSURE_UNPROVEN` and cannot qualify a material review mode.

Unscheduled calls cannot contribute successes. An unexplained call using the dedicated qualification credential invalidates the confirmation epoch.

Qualification adapters must disable implicit SDK retries or expose every physical retry as a separate append-only attempt. If the platform cannot observe whether the SDK/client retried, qualification attempt closure is unproven.

### Hard failure

A hard failure is any attempted trial with one or more of:

- required evidence/range/member/page inaccessible or incorrect;
- content-bound witness missing/incorrect;
- provider context state unproven or dirty;
- wrong model/deployment/account/endpoint/session identity;
- wire/manifest/retrieval hash mismatch;
- incomplete retrieval/access log when that mode requires it;
- timeout, provider/API error, rate limit, parser failure, or ambiguous result;
- output truncation/structured-output failure that prevents the required review protocol.

### Operating point

An operating point is the full tuple of:

- provider/account/project;
- endpoint/region;
- exact requested and provider-reported deployment identity;
- trusted adapter/API version;
- session/file/retrieval mode;
- enabled tools/connectors;
- structured-output mode;
- review prompt class;
- corpus representation/media classes;
- corpus byte size and provider-tokenizer token size;
- file count/per-file sizes;
- output/reasoning budget;
- witness protocol identity/version and maximum challenge/response budget when witnesses are used;
- transformation mode.

The **claimed operating point itself must be tested**. The protocol does not assume monotonic provider behavior and does not qualify untested intermediate points by interpolation.

For scalar size dimensions, the 80% margin is only an additional conservative cap on a point that is itself confirmed. If a failing boundary is observed, the runtime cap cannot exceed 80% of the smallest observed failing boundary. If no failure boundary is observed, the runtime cap cannot exceed 80% of the largest independently confirmed passing point.

The production qualification corpus must exercise the production request envelope and the preregistered worst-case token-density/content-modality classes. Synthetic low-entropy text alone cannot qualify a production review envelope.

Observed failures and failure boundaries are append-only within a provider drift epoch. Re-running until a clean sample appears cannot erase prior failures. A new drift epoch requires a new profile identity and preserves the prior epoch.

Profiles expire after **7 days** by default and immediately on material provider/model/deployment/account/endpoint/region/adapter/session/file-processing behavior drift. Health checks may invalidate a profile but can never renew or extend it.

Provider-specific policies may be stricter but may not be weakened by the candidate under review.

## Provider capability profile

A `ProviderCapabilityProfile` is trusted platform configuration/evidence, not candidate-authored content.

It must bind:

- provider;
- exact provider credential/account/project scope identity used by the platform; if the API does not expose a remote tenant/project identifier, bind the platform-owned credential/configuration identity and do not claim an unobservable remote identity;
- API endpoint/region/data-residency boundary;
- exact requested model and provider-reported model/deployment identity; if the provider cannot expose the deployment identity required by the drift policy, the mode is `NOT_QUALIFIED_FOR_MATERIAL_REVIEW`;
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
- exact ProviderQualificationExecutionPlan identity/hash and exact ProviderCapabilityQualificationRecord hash containing all planned/observed exploration/confirmation attempts, schedule, runner/credential binding, provider request reconciliation, hard-failure classifications, Clopper–Pearson calculation, content classes, operating-point tuple, and append-only failure history;
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
- canonical platform request hash before SDK serialization;
- canonical **transport-bound semantic envelope hash after SDK serialization at the lowest observable adapter boundary**, excluding only authentication secrets and explicitly volatile transport fields;
- exact non-secret headers/fields that can alter semantics, tools, routing, model selection, file/session binding, or output behavior;
- provider account/endpoint/region identity used;
- requested model identity and provider-reported model/deployment identity when the latter is required by the governed drift policy; if the provider cannot expose a required deployment identity, that identity-dependent qualification cannot be claimed;
- provider request/message/file/thread/session IDs;
- transport status;
- response hash;
- retry/idempotency identity;
- timestamp.

A manifest and prompt hash without wire binding do not prove that the adapter included the frozen evidence in the API request.

The adapter must serialize from the frozen representation bytes/chunks referenced by the manifest. Hashing one file and later reopening the same pathname for upload is insufficient unless byte identity is reverified immediately before dispatch.

Provider secrets are excluded from reproducible hashes but their exclusion must not permit semantic request fields to be omitted from binding. If the provider SDK prevents the trusted adapter from observing a semantic field that can materially change the request after serialization, that adapter/mode cannot claim exact wire binding for material review.

Implicit client/SDK retries are prohibited unless every physical provider attempt is surfaced to the trusted adapter with its own WireDeliveryRecord and immutable attempt identity. For material review and provider qualification, the preferred mode is client retry disabled. A hidden first failure followed by an SDK-retried success cannot be represented as one successful attempt.

## Delivery preflight

Before any review dispatch:

1. Verify the current ReviewRequest integrity.
2. Resolve and verify the immutable GovernanceAuthoritySnapshot.
3. Derive RequiredEvidenceContract and RequiredInteractionContract from that snapshot.
4. Validate ReviewRequest dimensions/refs/interactions against those contracts.
5. Materialize every required evidence reference from frozen source identity.
6. Verify source bytes/hashes and apply only governed representations/transforms.
7. Resolve data-classification/egress authorization.
8. Resolve a current trusted ProviderCapabilityProfile and machine-checkable PromptIsolationQualificationRecord.
9. Create or verify a clean ProviderContextStateEvidence record for this exact attempt.
10. Build and freeze the EvidenceDeliveryManifest.
11. Prove the exact production-equivalent delivery plan fits the qualified operating point.
12. Freeze exact call/chunk/file ordering, prompt identities, context-state version, capability-profile version, egress-policy version, and prompt-isolation record version.
13. Emit `DELIVERY_PREFLIGHT_PASS` only if every mandatory item and interaction is deliverable in the qualified mode.
14. Immediately before every wire call, compare-and-check the still-current context/capability/egress/prompt-isolation monotonic state versions.
15. Dispatch only the frozen representation bytes/chunks/file objects produced during preflight.
16. Record the final SDK-serialized semantic envelope hash at the trusted adapter boundary.

If a required item cannot be safely represented or delivered, fail before treating any reviewer disposition as authoritative.

Manifest freeze and wire dispatch form a TOCTOU boundary. A source path, generated representation, capability profile, egress decision, provider context state, prompt-isolation qualification, or provider file may not change between validation and use without voiding the attempt. A later requalification cannot revive an already-void attempt.

## Chunking limitation

**Chunking is a transport mechanism, not a way to exceed the model's qualified adjudication context.**

Sending N chunks over time does not prove that all N remain simultaneously available to the model at final adjudication. Earlier messages may be evicted, summarized, or otherwise unavailable.

Therefore a chunked material review is admissible only when one of these is qualified:

1. the complete final adjudication working set, including prompt and all mandatory representations, remains within the provider's qualified cumulative context; or
2. the provider exposes a qualified persistent file/retrieval mechanism whose content identity, accessibility, and final-review binding are validated; or
3. a governed decomposed-review protocol explicitly scopes independent subreviews and a separately qualified aggregation review covers required cross-evidence interactions.

A plain multi-message sequence must not be used to claim arbitrarily large context.

## Provider context isolation policy

Every material review binds a platform-owned `ProviderContextIsolationPolicy` selected from the GovernanceAuthoritySnapshot for the exact protected transition class and provider mode.

The policy chooses one of these admissible isolation bases:

1. `COMPLETE_READABLE_FENCED_STATE`
   - the provider exposes the complete account/project/session mutable semantic-state inventory relevant to the mode;
   - each mutable channel is readable or disable-able;
   - each load-bearing channel has a monotonic version/fence through admission.

2. `DEDICATED_PLATFORM_ACCOUNT_STATELESS_BOUNDARY`
   - a dedicated platform-owned provider account/project/credential is used only for governed review;
   - candidate and end-user writes to provider configuration are impossible by authorization policy;
   - provider product documentation/contract for the exact API mode is hash/version pinned and states that account/project/session memory, personalization, custom instructions and knowledge connectors are disabled or absent;
   - platform configuration readback proves all exposed mutable semantic features disabled;
   - behavioral sentinel qualification is run on a disposable qualification account/project of the same provider/account class and configuration template, never by contaminating the production review account;
   - production account configuration template/hash is independently matched to the qualified template and fenced.

Provider documentation is necessary provenance, not sufficient proof. The pinned documentation/contract version, provider account class, production configuration-template hash, and isolation-policy identity are part of the ProviderCapabilityProfile/context-isolation binding. A change to any of them invalidates the profile/isolation qualification and requires requalification.

### Hidden provider-internal state nonclaim

The platform cannot prove absence of provider-internal mutable semantic state that the provider does not expose through API/configuration and that cannot be independently controlled.

Therefore each `ProviderContextIsolationPolicy` declares a `hidden_provider_state_residual` rule:

- `DISALLOW` — any unexposed mutable-semantic-state possibility makes the provider/mode `NOT_QUALIFIED_FOR_MATERIAL_REVIEW`;
- `DEDICATED_ACCOUNT_EXTERNAL_TRUST_BOUNDARY` — only the dedicated-account basis above is permitted, and the residual is recorded explicitly as `PROVIDER_CONTEXT_HIDDEN_STATE_RESIDUAL`.

The highest material-authority transition class defaults to `DISALLOW` unless an independent governance decision explicitly authorizes the dedicated-account external trust boundary.

No result may be labeled “clean context” without recording the selected isolation basis and residual/nonclaim.

## Clean material-review context and delivery session binding

A material review uses a fresh stateless request or a **platform-created fresh stateful session**. Reuse of an arbitrary pre-existing provider thread/conversation is prohibited.

Every attempt carries `ProviderContextStateEvidence` created by the trusted adapter. It must bind:

- provider account/project/workspace identity;
- provider session/thread/conversation identity;
- complete platform-visible transcript/message IDs and transcript hash;
- platform-supplied system/developer/user prompts;
- enabled tools and connectors;
- custom/project/workspace instruction state and hash;
- provider memory/personalization state and hash;
- provider-side knowledge/retrieval connector state and hash;
- file set and processing/readiness state;
- provider-reported model/deployment identity;
- configuration-state version;
- evidence timestamp and trusted adapter identity.

The state is read and compared against the qualified profile:

- during preflight;
- immediately before every dispatch;
- immediately before final atomic verdict admission.

For mutable provider/account/project/session configuration used by a material review, the trusted platform must also obtain an `AdmissionFenceRecord`: a provider ETag/version/fencing token or a platform-owned dedicated-account configuration lock/version that makes concurrent configuration mutation detectable and prevents user/candidate writes during the attempt. If a load-bearing mutable channel exposes neither a readable version nor a platform-enforceable fence, the mode is not qualified for material review.

Any mutable semantic channel that is neither disable-able nor readable by the trusted platform makes the mode `NOT_QUALIFIED_FOR_MATERIAL_REVIEW`.

The only exception is a dedicated platform-owned provider account/project whose configuration write access is change-controlled outside candidate and user control, whose mutable semantic features are disabled by policy, and whose state is behaviorally requalified. Provider documentation is necessary background evidence but never sufficient by itself.

Stateful session reuse is allowed only inside the same delivery-attempt lineage when the session was created by the trusted adapter for that attempt and every prior message/tool/file mutation has a matching WireDeliveryRecord and context-state transition record.

Provider-context qualification must include **sentinel tests** for every mutable semantic channel available to the provider mode: enable a controlled sentinel and prove it influences the model when enabled; disable/clear it and prove absence across the governed confirmation trials. Lying/incomplete readback is explicitly tested.

Provider-internal fixed service/model safety behavior that cannot be extracted is a nonclaim. Hidden provider-internal mutable semantic state is governed only through the ProviderContextIsolationPolicy above: it is either disallowed or explicitly retained as a dedicated-account external trust-boundary residual. The platform never claims that such hidden state was observed clean.

For stateless provider modes, the final request itself must contain or qualified-reference all mandatory evidence and context. A receipt from one session/request cannot prove completeness for another.

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

When the model/provider chooses what file content or ranges to retrieve, **per-attempt deterministic access/range logs are mandatory** for material review. Before verdict admission, those logs must prove for every required page/range/member:

- exact source/version identity;
- requested range/member;
- returned content hash and byte/range length;
- successful retrieval time;
- tool/result message identity;
- binding of that tool result to the same final adjudication session/context.

A log that proves only “a file was opened” is insufficient. If the provider cannot prove both hash-matched returned content and binding of the retrieval result into the final adjudication context, that retrieval/file mode is diagnostic-only and `NOT_QUALIFIED_FOR_MATERIAL_REVIEW`.

The alternative is platform-forced inline inclusion of the governed representation inside the qualified final context.

Reviewer citation text, file IDs, or attach-time binding cannot substitute for per-attempt retrieval coverage when retrieval is model-selected.

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

Witnesses are non-dispositive accessibility evidence. They never prove cognition, attention, or semantic use.

### Qualification witnesses

When deterministic provider range/retrieval proof is unavailable, **every confirmation trial challenges every required segment**. Sparse head/middle/end probing is prohibited as qualification for full required content.

The default raw-text failure model is explicitly bounded to **contiguous loss/eviction at or above the segment granularity**. It does not claim detection of arbitrary selective or sub-granularity loss.

A governed lossless text representation is sliced so each slice is no larger than:

- 2048 UTF-8 bytes; and
- 512 provider-tokenizer tokens;

whichever limit is reached first.

For every slice in every confirmation trial, the platform creates a fresh content-bound challenge after representation freeze. The challenge selects unpredictable slice-local offsets and asks the reviewer to return exact short content extracts whose expected values are withheld from the reviewer prompt. Each slice also carries fresh framing/end sentinels. A canary-preserving content drop must therefore be independently attackable by the test adapters.

For production material review attempts using a mode without deterministic range/retrieval proof, the same **per-attempt content-bound witness protocol is mandatory in the same final adjudication session**. Qualification is a prior; it is not a substitute for per-attempt accessibility evidence.

The residual possibility of selective loss outside challenged offsets is recorded in `VerdictAdmissibilityResult` as a nonclaim/risk. A transition class whose governed risk budget does not permit that residual risk must use deterministic retrieval/range proof or a platform-forced representation with stronger observability.

### Witness protocol context budget and noninterference

The witness protocol is part of the qualified production operating point; it is not “free” metadata.

Before dispatch, preflight must include in the cumulative final-context budget:

- evidence representations;
- witness framing/challenges;
- maximum witness-response tokens/bytes;
- tool/result wrappers;
- final semantic adjudication prompt;
- required final review output budget.

After the witness phase and immediately before the final semantic adjudication prompt, the platform rechecks the actual transcript/context size against the qualified bound. If witness traffic could evict required evidence, the attempt is void.

Witness challenges are strictly extraction/accessibility operations. They may not ask for evaluation, summarization, ranking, defect identification, or conclusions.

A material review mode using witnesses additionally requires a platform-owned `WitnessProtocolQualificationRecord` from a qualified registry outside candidate write authority, bound to the exact prompt-isolation mechanism/provider mode. Candidate content/code cannot mint or widen it. That record covers:

- exact witness protocol/version;
- challenge syntax;
- ordering relative to evidence and final adjudication;
- maximum challenge/response budget;
- evidence-slice selection procedure;
- deterministic fake-adapter structural-isolation tests;
- machine-checkable binding to the applicable PromptIsolationQualificationRecord;
- expiry/drift binding.

The platform does **not** claim counterfactual semantic noninterference (“the model would have produced the same verdict without the witness phase”). That is not reliably observable for a stochastic remote model.

Instead, structural isolation requires:

- witness prompts contain accessibility/extraction instructions only;
- witness outputs are tagged non-evidence/non-adjudicative and cannot satisfy semantic review dimensions;
- the final semantic adjudication prompt hash is fixed and governed;
- prompt-isolation controls prevent witness output from being treated as candidate evidence or authority;
- the exact witness transcript remains inside the qualified context budget.

A/B semantic-outcome comparisons may be retained as diagnostics but cannot by themselves qualify or disqualify the witness protocol.

### Opaque attachments

Opaque attachments are qualified per media type **and content-modality class**. Scanned images, text PDFs, tables, embedded objects, archives, and other materially distinct modalities are separate classes.

Full-artifact material review requires either:

- deterministic provider access/range logs proving every required page/range/member/version; or
- governed lossless transformation into a qualified text/structured representation followed by the per-slice protocol.

Synthetic text-layer PDFs cannot qualify scans, tables, images, or embedded-object modalities.

A copied item ID/hash already present in the prompt is not a valid witness.

## Meaning of REVIEW_CONTEXT_QUALIFIED_AVAILABLE

`REVIEW_CONTEXT_QUALIFIED_AVAILABLE=true` means only:

- the platform proved complete governed materialization and wire delivery;
- the selected provider/mode has a current qualified capability profile for the representation/session mechanism;
- all required evidence is bound to the final adjudication request/session under that profile;
- no known delivery/context defect is present under the explicitly qualified failure model and ProviderAccessibilityRiskPolicy.

It does **not** mean the platform proved model cognition, attention, semantic use of every token, or absence of risks outside the qualified failure model. The prior name `REVIEW_CONTEXT_COMPLETE` is deprecated because it overstates what an external API can prove.

## Prompt/evidence isolation dependency

EXP-M does not qualify prompt-injection safety.

For material authority review, the pinned governor deterministically maps the transition/provider/representation mode to a required `PromptIsolationQualificationRecord` from EXP-L or its governed successor. That record must be machine-checkable, hash-bound to the exact isolation mechanism/provider mode, non-expired, and checked at preflight and atomic verdict admission.

If no current matching record exists, the review is non-promotable. “Applicable” is not caller- or proposer-selected.

Delivering all evidence perfectly must not be treated as safe if candidate-controlled evidence can hijack reviewer instructions.

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

The proposer may not define the interaction list by itself. The pinned delivery/review governor derives a `RequiredInteractionContract` only from the GovernanceAuthoritySnapshot's platform-owned evidence-relationship registry, mandatory dimensions, transition class, and governing standards.

Each required interaction is an explicit set of evidence refs/representations that must coexist **raw in one qualified reviewer context** for that interaction. The aggregator must inspect the raw evidence set for each interaction family; subreview verdict summaries alone cannot satisfy the interaction.

Any proposer/ReviewRequest declaration is checked against this contract. Unknown relationship class, empty required interaction set where the transition baseline requires one, or missing registry rule yields `REVIEW_INTERACTION_CONTRACT_INCOMPLETE` and blocks a global disposition.

If material cross-evidence interactions cannot be reviewed within a qualified context, the review remains bounded/incomplete.

## Admissibility predicate registry and mutation closure

The platform maintains a machine-readable `AdmissibilityPredicateRegistry` outside candidate write authority.

Each load-bearing verdict-admissibility predicate has:

- stable predicate ID;
- schema/version;
- human meaning;
- validator function identity/hash;
- required negative fixture ID;
- required logic-mutation ID;
- authority snapshot binding.

`VerdictAdmissibilityResult` must contain exactly the required predicate-ID set for the protected transition/mode.

The deterministic test plan proves set closure:

`required_admissibility_predicates == verdict_result_predicates == validator_logic_mutation_targets == independently_killed_mutations`

Any missing predicate, extra ungoverned predicate, or predicate without a killed deletion/weakening mutation yields `ADMISSIBILITY_PREDICATE_COVERAGE_INCOMPLETE`.

Adding a new load-bearing predicate without updating its negative fixture and logic mutation cannot pass deterministic EXP-M testing.

## Verdict admissibility

`VerdictAdmissibilityResult` contains an explicit predicate for every load-bearing requirement:

- ReviewRequest current/integrity-valid;
- GovernanceAuthoritySnapshot current and outside candidate write authority;
- RequiredEvidenceContract resolved, non-vacuous, and closed;
- RequiredInteractionContract resolved and closed;
- complete materialization;
- governed representation/transformation;
- current egress authorization;
- ProviderCapabilityProfile current and statistically qualified for the exact operating point;
- ProviderAccessibilityRiskPolicy current and satisfied by the selected accessibility proof mode;
- ProviderContextIsolationPolicy current, exact-mode-bound, and satisfied;
- hidden-provider-state residual allowed by the protected transition policy, if any;
- ProviderContextStateEvidence clean/current for all observable channels;
- AdmissionFenceRecord valid for every load-bearing mutable provider configuration channel;
- provider mutable semantic-context qualification satisfied;
- trusted adapter and post-SDK wire binding valid;
- complete item/chunk delivery;
- per-attempt content-bound accessibility witness valid **or** deterministic range/retrieval proof complete;
- when witnesses are used, WitnessProtocolQualificationRecord current/matching and actual witness transcript remains within the qualified final-context budget;
- session/file/retrieval coverage valid for the delivery mode;
- PromptIsolationQualificationRecord current/matching;
- semantic review coverage valid;
- reviewer provenance/independence valid;
- disposition otherwise promotable.

Admission is the **last authority operation** and is atomic with checkpoint persistence:

1. capture monotonic versions/hashes for authority snapshot, capability profile, accessibility-risk policy, context-isolation policy, egress policy, provider context/session/file state, AdmissionFenceRecord, prompt-isolation record, and current review request;
2. validate all predicates;
3. compare-and-set the authoritative checkpoint only if every version/hash is unchanged;
4. persist the VerdictAdmissibilityResult and checkpoint in the same authority transaction/boundary.

All load-bearing state must remain valid over the entire interval from first provider dispatch through admission. Any expiry, revocation, drift, dirty-context event, file/session invalidation, or prompt-isolation invalidation during the interval **voids the attempt permanently**. Later requalification cannot revive that old provider response; only a new delivery attempt may proceed.

A semantic `PASS` with any false/unproven predicate is non-promotable.

## Insufficient-evidence cause adjudication

When a reviewer returns `INSUFFICIENT_EVIDENCE` or equivalent, the platform evaluates all cause predicates independently rather than first-match ordering:

- scientific source missing → `SCIENTIFIC_EVIDENCE_MISSING`;
- requiredness contract unresolved → `EVIDENCE_SELECTION_CONTRACT_UNRESOLVED`;
- governed required set incomplete → `EVIDENCE_SELECTION_INCOMPLETE`;
- source materialization failed → `EVIDENCE_MATERIALIZATION_FAILED`;
- transformation/representation unqualified → `EVIDENCE_TRANSFORMATION_UNQUALIFIED`;
- delivery omitted/corrupted material → `EVIDENCE_DELIVERY_INCOMPLETE`;
- provider context dirty/unproven → `PROVIDER_CONTEXT_STATE_UNPROVEN` / `REVIEW_CONTEXT_INCOMPLETE`;
- attachment/file/retrieval coverage unavailable → `EVIDENCE_ATTACHMENT_UNAVAILABLE` / `PROVIDER_RETRIEVAL_COVERAGE_UNPROVEN`;
- reviewer says evidence is missing although the platform has strong contradictory accessibility evidence → `REVIEWER_EVIDENCE_ASSESSMENT_CONTRADICTION`.

If more than one cause predicate is true, the result is `MIXED_INSUFFICIENCY` with the complete cause set. If no cause can be proven, use `INSUFFICIENT_EVIDENCE_CAUSE_UNRESOLVED`.

Never convert delivery failure into scientific failure or scientific absence into a transport excuse.

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
- ProviderQualificationExecutionPlan and trusted qualification-runner/credential identity;
- ProviderAccessibilityRiskPolicy identity;
- ProviderContextIsolationPolicy identity and selected isolation basis;
- WitnessProtocolQualificationRecord identity when witnesses are used;
- hidden-provider-state residual/nonclaim decision;
- pinned provider documentation/contract identity where the dedicated-account basis is used;
- AdmissionFenceRecord;
- prompt identities;
- pre-dispatch revalidation result for capability/egress/session state;
- WireDeliveryRecords;
- chunks where used;
- provider session/file/message IDs where used;
- reviewer receipt if used;
- DeliveryCompletenessResult;
- provider raw responses;
- witness-probe challenges/results where used;
- mandatory provider retrieval/access logs for any retrieval-selected material-review mode;
- parsed review;
- insufficient-evidence adjudication where needed;
- semantic validation;
- AdmissibilityPredicateRegistry identity and predicate/mutation-coverage closure result;
- VerdictAdmissibilityResult, including provider statistical lower bound, qualified operating-point identity, per-attempt accessibility method, and explicitly retained residual/nonclaim risk.

## Governance scope

This standard supplements review provenance, semantic review coverage, portable packet integrity, external-evidence classification, and independent-review prompt/evidence governance.

It specifically governs **required-evidence closure, delivery integrity, provider-context qualification, and verdict admissibility**.
