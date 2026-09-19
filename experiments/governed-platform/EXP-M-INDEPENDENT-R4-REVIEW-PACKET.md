# EXP-M Independent R4 Review Packet

## Packet status

`R4_EXTERNAL_REVIEW_REQUESTED_NO_AUTHORITY_EFFECT`

This is a self-contained narrow R4 design/preregistration review packet for:

**EXP-M — Review Evidence Delivery & Reviewer Context Integrity Falsification**

R3 returned `CHANGES_REQUIRED`. The current source accepts the R3 findings and claims to have remediated them. This packet asks the independent reviewer to attack those repairs.

EXP-M remains `NOT_QUALIFIED`.
No implementation, deterministic experiment execution, live provider pilot, review promotion, or authority transition is authorized by this packet.

## Reviewed source identity

- repository: `vij7661/setugo-ai-development-framework`
- branch: `experiment/exp-m-review-evidence-delivery-integrity`
- base main commit: `87f6e3df73c0c70c5d8ff4da38365ff92721aff7`
- prior R3 packet commit: `ceb9440d22430b4c6e4bfda2be6d6f47a572cc73`
- current R4 reviewed source commit: `57df4cecd49cb77e38b2a34aeba8eeae61823e9b`
- current R4 reviewed source tree: `9e7c56449ce7588074cea77bb62719368552f333`

Current reviewed blobs:
- `standards/review-evidence-delivery-integrity.md` — `1592505177b478fdebc5ac05281d603cb3befbfa`
- `experiments/governed-platform/exp-m-review-evidence-delivery-integrity.md` — `8b08055b272945ffcc33dee2b9db518e485c9404`
- `experiments/governed-platform/EXP-M-TEST-MATRIX.md` — `eb3562083888341cdf0ea3d93b31a582542e13d1`
- `governance-runtime/LIVE-CONVERSATION-GOVERNANCE.md` — `a67763a6d204dcc4c2a5bc8ad1fbf584c3239553`
- `experiments/governed-platform/EXP-M-R3-EXTERNAL-REVIEW.md` — `935ce53282e23badc093006d64d7364bcf85a54d`
- `experiments/governed-platform/EXP-M-R3-REVIEW-REMEDIATION.md` — `d40763743b0c0f632e175e7861af3c2ee9ce9a40`

## R3 disposition being remediated

R3 found:

- Critical R3-C01 — requiredness-contract inputs were not bound to authority outside candidate control;
- High R3-H01 — provider semantic context state was declared rather than observed per attempt;
- High R3-H02 — provider-capability statistics were not fully falsifiable;
- High R3-H03 — dense witnesses were qualification-only and not content-bound enough;
- High R3-H04 — retrieval/file completeness could be made profile-discretionary;
- High R3-H05 — test/mutation matrix did not actually attack repaired validator logic;
- R3-M01..M05 and R3-L01..L03 — atomic admission, interaction granularity, hedged requirements, incomplete admissibility predicate set, cause taxonomy, live-procedure ordering, post-SDK wire binding, and EXP-L applicability.

The current source claims all of these are closed at design level and additionally records a self-review that found no remaining Critical/High design defect.

Do not trust that claim.

## R4 attack posture

Assume false-green. Try to show that the R3 repairs merely moved authority or uncertainty elsewhere.

Pay special attention to:

1. GovernanceAuthoritySnapshot and whether its pointer/registries/input semantics are truly outside candidate self-approval.
2. Conservative base/head merge, including same-ID semantic weakening and incomparable constraints.
3. Non-vacuity for unknown transition classes, evidence contracts, interaction contracts, and accessibility-risk policies.
4. ProviderContextStateEvidence and whether hidden provider/user/project semantic state can still escape observation.
5. AdmissionFenceRecord and races between provider-context readback and checkpoint admission.
6. Provider statistical policy:
   - p_min=0.99;
   - one-sided 95% exact Clopper–Pearson;
   - 299/299 zero-hard-failure confirmation;
   - no rerolls/exclusions/optional stopping;
   - exploration separate from confirmation;
   - preregistered schedule across days/time blocks;
   - production-equivalent operating point;
   - append-only failures;
   - independence assumptions explicitly bounded.
7. ProviderAccessibilityRiskPolicy and whether a transition can silently accept selective/sub-slice loss beyond its risk budget.
8. Per-attempt content-bound slice witnesses and whether they actually bind evidence rather than framing.
9. Model-selected retrieval: returned-byte/range/version proof plus tool-result binding into the final adjudication context.
10. Unified validator-logic mutation suite and whether every load-bearing conjunct can really be killed.
11. Atomic final compare-and-set admission and permanent invalidation of an attempt after any mid-attempt drift/expiry/revocation.
12. PromptIsolationQualificationRecord and exact EXP-L/successor dependency.
13. Cause taxonomy and MIXED insufficiency semantics.
14. Any new false-positive or false-negative governance path introduced by making controls too strict or impossible to satisfy.

## Required R4 output

Return exactly one overall disposition:

- `BOUNDED_PASS`
- `CHANGES_REQUIRED`
- `INSUFFICIENT_EVIDENCE`

Then complete the following.

### A. R3 finding closure

For each:

- R3-C01
- R3-H01
- R3-H02
- R3-H03
- R3-H04
- R3-H05
- R3-M01
- R3-M02
- R3-M03
- R3-M04
- R3-M05
- R3-L01
- R3-L02
- R3-L03

return:

`CLOSED / PARTIAL / OPEN`

and give:
- exact current-source evidence;
- any remaining false-green path;
- exact narrow fix if not CLOSED.

### B. Newly discovered findings

List new:
- Critical;
- High;
- Medium/Low.

For each finding provide:
- finding ID;
- severity;
- affected standard/invariant/test;
- concrete false-green/failure path;
- why current design is insufficient;
- narrow required correction.

### C. Gate verdicts

Return:

- REQUIRED_EVIDENCE_AUTHORITY = PASS / FAIL
- DELIVERY_GOVERNOR_TRUST_ROOT = PASS / FAIL
- GOVERNANCE_AUTHORITY_SNAPSHOT = PASS / FAIL
- CLEAN_SESSION_CONTEXT = PASS / FAIL
- PROVIDER_SEMANTIC_CONTEXT_BINDING = PASS / FAIL
- PROVIDER_CONTEXT_ADMISSION_FENCE = PASS / FAIL
- WIRE_BINDING = PASS / FAIL
- CHUNK_CONTEXT_MODEL = PASS / FAIL
- REMOTE_ACCESSIBILITY_MODEL = PASS / FAIL
- PROVIDER_ACCESSIBILITY_RISK_POLICY = PASS / FAIL
- PROVIDER_CAPABILITY_QUALIFICATION = PASS / FAIL
- STATISTICAL_PROTOCOL = PASS / FAIL
- REPRESENTATION_GOVERNANCE = PASS / FAIL
- MATERIALIZATION_SAFETY = PASS / FAIL
- EGRESS_BOUNDARY = PASS / FAIL
- SESSION_FILE_RETRIEVAL_BINDING = PASS / FAIL
- RETRIEVAL_FINAL_CONTEXT_BINDING = PASS / FAIL
- INSUFFICIENT_EVIDENCE_TAXONOMY = PASS / FAIL
- MULTI_REVIEWER_EQUIVALENCE = PASS / FAIL
- DECOMPOSITION_AGGREGATION = PASS / FAIL
- PROMPT_ISOLATION_DEPENDENCY = PASS / FAIL
- TOCTOU_RETRY_INTEGRITY = PASS / FAIL
- ATOMIC_VERDICT_ADMISSION = PASS / FAIL
- REVIEWER_TOOL_EVIDENCE_BOUNDARY = PASS / FAIL
- TEST_MATRIX_SUFFICIENCY = PASS / FAIL
- VALIDATOR_LOGIC_MUTATION_COVERAGE = PASS / FAIL

### D. Statistical protocol adjudication

Explicitly evaluate:

- whether 299/299 is the exact minimum for a one-sided 95% exact-binomial lower bound >=0.99 under the stated model;
- whether the independence/correlation nonclaim is honest enough;
- whether the 3-day/4-time-block schedule and interleaving are falsifiable;
- whether every attempted trial is actually forced into the append-only ledger;
- whether exploration/confirmation separation prevents rerun-until-pass;
- whether production-envelope equivalence is well-defined;
- whether the 80% margin is only supplemental and no untested monotonicity is inferred;
- whether profile expiry/drift behavior is adequate.

### E. Accessibility and retrieval adjudication

Explicitly evaluate:

- max slice <= min(2048 UTF-8 bytes, 512 provider tokens);
- every slice challenged every confirmation trial;
- per-attempt content-bound challenge in the final adjudication session;
- framing canaries only supplemental;
- selective/sub-slice loss recorded as nonclaim/residual;
- ProviderAccessibilityRiskPolicy chooses whether that residual is acceptable;
- highest material-authority transition requires deterministic proof;
- opaque media/modalities cannot inherit text qualification;
- model-selected retrieval requires returned-byte hash/range/version plus tool-result binding into final context.

### F. Authority and atomic-admission adjudication

Try to break:

- authority snapshot pointer;
- base/head conservative merge;
- same-ID semantic mutation;
- unknown/empty contract;
- relationship registry;
- risk policy registry;
- provider context state;
- provider admission fence;
- prompt-isolation qualification;
- atomic compare-and-set checkpoint.

Specifically test whether later requalification can ever revive an old invalidated response. It must not.

### G. Test-plan adjudication

Verify that:

- test IDs no longer collide;
- unified mutation catalog is authoritative;
- all deterministic phases A–Q are gated;
- logic mutations attack code predicates, not only data;
- lying readback, hidden state, correlated burst, failed-trial replay, canary-preserving content loss, missing retrieval log and atomic-admission race all have adversarial oracles;
- `REVIEWER_EVIDENCE_ASSESSMENT_CONTRADICTION`, `EVIDENCE_SELECTION_CONTRACT_UNRESOLVED`, provider-context/retrieval/admission codes are defined consistently.

### H. Final determination

State:

- whether any Critical design defect remains;
- whether any High design defect remains;
- whether EXP-M design is ready for implementation and deterministic falsification;
- whether live provider pilots may begin;
- exact remaining prerequisites;
- explicit confirmation that EXP-M remains NOT QUALIFIED;
- explicit confirmation that this external/manual review itself grants no platform review or promotion authority.

## Nonclaims

This packet does not claim:
- implementation exists;
- deterministic tests have executed;
- any live provider is qualified;
- remote model attention is provable;
- provider internal state is cryptographically knowable;
- the self-adjudication is independent;
- this R4 review may itself promote EXP-M.

## Inline current review material


---

# INLINE SOURCE: standards/review-evidence-delivery-integrity.md

Git blob: `1592505177b478fdebc5ac05281d603cb3befbfa`

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

Registries and the authority-snapshot pointer are maintained outside the candidate write set. A candidate may propose changes to governing inputs, but those proposed changes cannot authorize or narrow their own review.

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
- `PROVIDER_RETRIEVAL_COVERAGE_UNPROVEN`
- `PROVIDER_RETRIEVAL_CONTEXT_BINDING_UNPROVEN`
- `STATISTICAL_INDEPENDENCE_UNPROVEN`
- `VERDICT_ADMISSION_STATE_CHANGED`
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
- the Clopper–Pearson probability interpretation is explicitly conditional on the trial-independence model. When provider-side correlation/route allocation is not observable, the profile records `STATISTICAL_INDEPENDENCE_UNPROVEN`; the numerical bound is not presented as a universal provider failure probability and cannot replace per-attempt accessibility proof.

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
- exact ProviderCapabilityQualificationRecord hash containing all exploration/confirmation attempts, schedule, hard-failure classifications, Clopper–Pearson calculation, content classes, operating-point tuple, and append-only failure history;
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

Provider-internal fixed service/model safety behavior that cannot be extracted is a nonclaim. It is tolerated only when it is not mutable at account/project/session scope and the exact provider/deployment mode passes the governed behavioral qualification. Unknown mutable semantic context is never tolerated.

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
- ProviderContextStateEvidence clean/current;
- AdmissionFenceRecord valid for every load-bearing mutable provider configuration channel;
- provider mutable semantic-context qualification satisfied;
- trusted adapter and post-SDK wire binding valid;
- complete item/chunk delivery;
- per-attempt content-bound accessibility witness valid **or** deterministic range/retrieval proof complete;
- session/file/retrieval coverage valid for the delivery mode;
- PromptIsolationQualificationRecord current/matching;
- semantic review coverage valid;
- reviewer provenance/independence valid;
- disposition otherwise promotable.

Admission is the **last authority operation** and is atomic with checkpoint persistence:

1. capture monotonic versions/hashes for authority snapshot, capability profile, accessibility-risk policy, egress policy, provider context/session/file state, AdmissionFenceRecord, prompt-isolation record, and current review request;
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
- ProviderAccessibilityRiskPolicy identity;
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
- VerdictAdmissibilityResult, including provider statistical lower bound, qualified operating-point identity, per-attempt accessibility method, and explicitly retained residual/nonclaim risk.

## Governance scope

This standard supplements review provenance, semantic review coverage, portable packet integrity, external-evidence classification, and independent-review prompt/evidence governance.

It specifically governs **required-evidence closure, delivery integrity, provider-context qualification, and verdict admissibility**.


---

# INLINE SOURCE: experiments/governed-platform/exp-m-review-evidence-delivery-integrity.md

Git blob: `8b08055b272945ffcc33dee2b9db518e485c9404`

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

The GovernanceAuthoritySnapshot, transition-class registry, evidence-selection registry, relationship registry, capability registry, accessibility-risk registry, and authority-snapshot pointer are outside the candidate write set. Candidate edits to governing inputs are reviewed as evidence and cannot narrow their own review. Governing elements are stable-ID + content-hash bound; changing semantics under the same ID is treated as a changed input, and base/head representation/acceptance/risk constraints preserve the stricter rule or fail unresolved.

### M-I43 — Provider context state is observed per attempt

Every material review carries ProviderContextStateEvidence from the trusted adapter at preflight, before each dispatch, and at atomic admission. Mutable semantic channels that are neither readable nor disable-able make the provider/mode NOT_QUALIFIED_FOR_MATERIAL_REVIEW.

### M-I44 — Confirmation trials are disjoint, scheduled, and append-only

Exploration cannot count as confirmation. Confirmation trial identities/schedule are frozen, all attempted trials count, failures cannot be erased by reruns, and the claimed operating point itself is tested under the production-equivalent envelope.

### M-I45 — Verdict admission is atomic and final

Capability, egress, provider-context/session/file state, authority snapshot, ReviewRequest, and prompt-isolation qualification remain valid from first dispatch through a final compare-and-set admission. Any invalidation in that interval permanently voids the attempt; later requalification cannot revive it.

### M-I46 — Prompt isolation dependency is machine-bound

Material review requires a current hash-bound PromptIsolationQualificationRecord selected deterministically by the governor for the exact provider/representation mode and checked again at atomic admission.

### M-I47 — Accessibility risk is transition-class governed

Every protected transition class has a ProviderAccessibilityRiskPolicy in the GovernanceAuthoritySnapshot. Unknown policy fails closed. The highest material-authority class requires deterministic full-range/page/member proof or an equivalently observable inline mode; probabilistic per-attempt witnesses alone cannot silently satisfy it.

### M-I48 — Mutable provider context is fenced through admission

Every load-bearing mutable provider/account/project/session configuration channel has a readable monotonic version or a platform-enforceable AdmissionFenceRecord. If neither exists, the mode is NOT_QUALIFIED_FOR_MATERIAL_REVIEW.

### M-I49 — “Complete” is not an admissibility claim

The platform uses REVIEW_CONTEXT_QUALIFIED_AVAILABLE, not REVIEW_CONTEXT_COMPLETE, and records the qualified failure model plus residual/nonclaim risk in VerdictAdmissibilityResult.

### M-I50 — Statistical independence is not silently assumed

Provider capability qualification records time/routing/deployment diversity and whether trial independence is actually evidenced. If provider-side correlation cannot be observed, STATISTICAL_INDEPENDENCE_UNPROVEN is recorded and the exact-binomial bound is not treated as a universal provider failure probability.

### M-I51 — Retrieval proof binds returned bytes into final context

Model-selected retrieval logs must prove exact returned content hash/range/version and the resulting tool/message binding into the same final adjudication context. “File opened” or citation-only logs are insufficient.

## Required mechanism surfaces

Future implementation should expose governed objects equivalent to:

- `GovernanceAuthoritySnapshot`
- `RequiredEvidenceContract`
- `RequiredInteractionContract`
- `EvidenceDeliveryManifest`
- `ProviderCapabilityProfile`
- `ProviderAccessibilityRiskPolicy`
- `AdmissionFenceRecord`
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

Candidate head removes or weakens a required evidence/representation/risk rule, including semantic replacement under the same stable ID.

Expected:
GovernanceAuthoritySnapshot/base-head conservative merge preserves the stricter base/head semantics; changed governance file is itself required evidence; incomparable conflicts fail unresolved.

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

### M-102 — Missing transition accessibility-risk policy

Expected:
review ineligible; no default implicit risk acceptance.

### M-103 — Highest-authority transition uses probabilistic witnesses only

Expected:
admissibility fails because deterministic access proof is required by policy.

### M-104 — Mutable provider config has no version/fence

Expected:
NOT_QUALIFIED_FOR_MATERIAL_REVIEW.

### M-105 — Provider configuration changes between final read and checkpoint CAS

Expected:
AdmissionFence/version mismatch kills the attempt.

### M-106 — Legacy REVIEW_CONTEXT_COMPLETE flag forced true

Expected:
flag is ignored/deprecated; authority depends on REVIEW_CONTEXT_QUALIFIED_AVAILABLE predicates and residual-risk record.

### M-107 — Correlated provider route hidden behind fresh request IDs

All requests are fresh but provider-exposed route/deployment identity shows the same correlated backend/time burst.

Expected:
STATISTICAL_INDEPENDENCE_UNPROVEN or confirmation-schedule failure; probability claim not overgeneralized.

### M-108 — Retrieval log says file opened but returned bytes are unbound

Expected:
PROVIDER_RETRIEVAL_CONTEXT_BINDING_UNPROVEN; material verdict inadmissible.

### M-109 — Retrieval returns correct range but tool result is not bound to final adjudication session

Expected:
PROVIDER_RETRIEVAL_CONTEXT_BINDING_UNPROVEN.

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
- skipping atomic compare-and-set admission;
- omitting ProviderAccessibilityRiskPolicy;
- allowing probabilistic witnesses for a transition class requiring deterministic proof;
- accepting mutable provider context without a version/fence;
- trusting a legacy REVIEW_CONTEXT_COMPLETE boolean;
- treating fresh request IDs as proof of statistical independence;
- accepting retrieval/open logs without returned-content and final-context binding.

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
- `MissingAccessibilityRiskPolicyAdapter`
- `UnfencedProviderConfigAdapter`
- `AdmissionFenceRaceAdapter`
- `CorrelatedRouteAdapter`
- `RetrievalOpenOnlyAdapter`
- `RetrievalUnboundToolResultAdapter`

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
37. PromptIsolationQualificationRecord is machine-checkable, current, and admission-bound;
38. ProviderAccessibilityRiskPolicy is explicit for every transition class and the selected proof mode satisfies it;
39. mutable provider context has readable versions or a valid AdmissionFenceRecord through atomic admission;
40. no legacy REVIEW_CONTEXT_COMPLETE boolean can substitute for the explicit qualified-availability predicates;
41. statistical independence assumptions are explicit and cannot be inferred solely from fresh request IDs;
42. model-selected retrieval proves returned-byte identity and final-context tool-result binding.

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


---

# INLINE SOURCE: experiments/governed-platform/EXP-M-TEST-MATRIX.md

Git blob: `eb3562083888341cdf0ea3d93b31a582542e13d1`

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
- AdmissionFenceRecord;
- ProviderCapabilityQualificationRecord with append-only trial ledger;
- ProviderContextStateEvidence;
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

- **all deterministic phases A–Q pass**;
- unified data/state mutation survivors = 0;
- validator-logic mutation survivors = 0;
- crash/retry tests preserve exact identity/history;
- every admissibility conjunct is independently falsified by at least one negative test;
- authority-snapshot/base-head poisoning tests pass;
- clean-context state/sentinel tests pass;
- RequiredEvidenceContract and RequiredInteractionContract non-vacuity/closure tests pass;
- statistical-protocol tests reject insufficient, rerolled, burst-only, mixed exploration/confirmation, and production-envelope-mismatched evidence;
- per-attempt content-bound witness tests and canary-preserving content-drop oracle pass;
- model-selected retrieval is blocked without deterministic full-range access logs;
- atomic final CAS admission and permanent-attempt-void semantics pass;
- prompt-isolation qualification is machine-bound and admission-checked;
- ProviderAccessibilityRiskPolicy exists for every transition class and selected proof mode;
- mutable provider context is versioned/fenced through admission;
- legacy REVIEW_CONTEXT_COMPLETE cannot create authority;
- statistical independence assumptions are explicit and cannot be inferred solely from fresh request IDs;
- model-selected retrieval logs bind exact returned bytes to final adjudication context;
- insufficient-evidence cause adjudication returns all causes and MIXED when multiple predicates hold;
- review consensus cannot hide corpus divergence.

Live provider pilots may begin only after deterministic exit above is green. A provider-specific production mode becomes qualified only after its separate exploration/confirmation capability evidence passes the governed risk budget and all provider-context/accessibility requirements.

Provider-specific `NOT_QUALIFIED_FOR_MATERIAL_REVIEW` is an acceptable fail-closed outcome.


---

# INLINE SOURCE: governance-runtime/LIVE-CONVERSATION-GOVERNANCE.md

Git blob: `a67763a6d204dcc4c2a5bc8ad1fbf584c3239553`

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

For material review, the provider execution must use a fresh stateless request or a fresh stateful session created by the trusted adapter for that delivery attempt. Arbitrary pre-existing threads/conversations are prohibited. ProviderContextStateEvidence must be observed at preflight, before every dispatch, and at atomic admission. Any mutable semantic channel (memory, custom instructions, project/workspace configuration, tools/connectors, knowledge sources) that is neither readable nor disable-able makes the provider/mode NOT_QUALIFIED_FOR_MATERIAL_REVIEW.

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

The ReviewRequest is not authoritative about its own completeness. Before delivery, a pinned platform governor resolves an immutable `GovernanceAuthoritySnapshot` from a pre-candidate authority state outside the candidate write set. RequiredEvidenceContract and RequiredInteractionContract are derived only from that snapshot's transition-class, mandatory-dimension, evidence-selection, relationship, and governing-standard registries.

If the candidate changes governing inputs, the review uses the conservative union/strictest combination of pre-candidate authority requirements and proposed head requirements, and the governing-input change itself becomes mandatory review evidence. Unknown transition class, missing registry rule, or vacuous required set fails as `EVIDENCE_SELECTION_CONTRACT_UNRESOLVED`. ReviewRequest refs/dimensions/interactions are declarations checked against those contracts; they cannot narrow them.

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
- model-selected retrieval/file modes require deterministic per-attempt access logs covering every required range/page/member, otherwise the mode is diagnostic-only;
- modes without deterministic range/retrieval proof require mandatory per-attempt content-bound witnesses, not qualification-only sparse canaries;
- provider capability qualification uses disjoint exploration/confirmation evidence and the exact production operating point under the governed risk budget;
- provider context cleanliness is observed per attempt rather than declared;
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
13. Resolve and verify the pre-candidate GovernanceAuthoritySnapshot outside candidate write authority.
14. Derive RequiredEvidenceContract and RequiredInteractionContract; validate ReviewRequest against them before materialization.
15. Materialize and hash every required review evidence item from frozen source identity.
16. Apply governed transformation and egress policy.
17. Validate a current statistically qualified ProviderCapabilityProfile, transition-class ProviderAccessibilityRiskPolicy, and machine-checkable PromptIsolationQualificationRecord for the exact production operating point.
18. Create a fresh provider review context, capture ProviderContextStateEvidence, and establish a readable monotonic provider configuration version or AdmissionFenceRecord for every load-bearing mutable channel.
19. Freeze the EvidenceDeliveryManifest and monotonic authority/capability/egress/context/prompt-isolation state versions.
20. Before each provider call, re-read/compare context/config state and serialize only frozen representation bytes.
21. Record both platform request hash and post-SDK transport-bound semantic envelope hash.
22. Deliver through the qualified inline/chunk/file/retrieval mechanism.
23. Establish per-attempt accessibility using mandatory content-bound slice witnesses or deterministic full-range retrieval/access logs, according to delivery mode.
24. Validate ReviewRequest + ReviewEvidence + semantic coverage + authenticated execution envelope + delivery/context completeness.
25. If the reviewer reports insufficiency, evaluate all independent cause predicates and return MIXED when multiple causes hold.
26. Immediately before authority admission, re-read all monotonic state versions/hashes, accessibility-risk-policy state, AdmissionFenceRecord, and every load-bearing admissibility predicate.
27. Atomically compare-and-set the authoritative checkpoint together with VerdictAdmissibilityResult only if every state/version remains unchanged since its required observation.
28. Any expiry, revocation, drift, dirty-context event, file/session invalidation, or prompt-isolation invalidation from first dispatch through step 27 permanently voids that attempt; later requalification cannot revive the old response.
29. Synchronize shared memory only after authoritative persistence.
30. New chat resumes from shared memory then verifies Git.

## Current collaboration limitation

This chat can ingest pasted external evidence, but pasted content is not a platform review execution. Therefore it cannot satisfy a mandatory provider-authenticated PR #5 review gate. In the production platform, both AUTO_MODE and MANUAL_MODE avoid this limitation by using trusted provider API adapters (`AUTOMATIC_API` / `USER_INITIATED_API`).


---

# INLINE SOURCE: experiments/governed-platform/EXP-M-R3-EXTERNAL-REVIEW.md

Git blob: `935ce53282e23badc093006d64d7364bcf85a54d`

**Overall disposition:** **`CHANGES_REQUIRED`**

The R2 repairs are real but incomplete. Every R2 finding except M-01..M-03's cores is only PARTIAL, and I found one new Critical and five new High defects. The R2 remediation's claim of "no new Critical/High" is not supported.

*Scope:* I read the inline packet: the standard, the experiment invariants and the frozen tests M-42..M-82, the mutation, adapter, pilot and acceptance sections, all of the test matrix, the relevant live-governance sections, and the R2 review and remediation. I skimmed M-01..M-41. I had no repository access, so I did not verify the commit, tree or blob hashes and treated the inline text as faithful.

## 1. R2 finding closure

| ID Status Remaining false-green path (details in §2)  |             |                                                                                                                                                                                                                                        |
| ----------------------------------------------------- | ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| C-01                                                  | **PARTIAL** | The ReviewRequest can no longer narrow the contract. The contract's own inputs (standards, experiment contract, selection rules, classification, relationship graph) are not bound to an authority the candidate cannot edit. → R3-C01 |
| H-01                                                  | **PARTIAL** | The rule and tests exist, but cleanliness is declared or documented rather than observed per attempt. Nothing defines how "pre-existing context is governed" is proven. → R3-H01                                                       |
| H-02                                                  | **PARTIAL** | Thresholds are fixed, but the protocol around them (independence, exclusions, re-roll, content coverage) is not falsifiable. → R3-H02                                                                                                  |
| H-03                                                  | **PARTIAL** | Fail-closed on paper. The "drift-bound" alternative, the reliance on provider documentation, and the absence of any per-attempt state read leave a gap. → R3-H01                                                                       |
| H-04                                                  | **PARTIAL** | Dense probing exists only at qualification, on synthetic artifacts. Production attempts carry no mandatory witnesses, and K02 and the pilot section still endorse the sparse method. → R3-H03                                          |
| H-05                                                  | **PARTIAL** | Tests were added, but they contradict each other, the exit criteria omit most phases, and none of the new tests attack the validator's own logic. → R3-H05                                                                             |
| M-01                                                  | **PARTIAL** | Hedges remain. → R3-M03                                                                                                                                                                                                                |
| M-02                                                  | **PARTIAL** | The source of "evidence relationships" is undefined, and interaction families are too coarse. → R3-C01, R3-M02                                                                                                                         |
| M-03                                                  | **PARTIAL** | The revalidation step sits before the final gate, and re-admission after the fact is permitted. → R3-M01                                                                                                                               |

## 2. New and residual findings

### Critical

**R3-C01: Requiredness contracts have no bound input authority** (keeps C-01 and M-02 open)

- **Affected:** the standard's "Required-evidence authority", "Delivery-governor trust root" and "Review decomposition" sections; M-I16 versus M-I36; tests M-68, M-69, M-80, N01–N03, N23.
- **False-green path:** 
  - The governor's code is pinned, but its inputs are not.
  - `standards/` and `experiments/governed-platform/` are governance paths in the same repo as the change under review.
  - A candidate that edits those files, or supplies the relationship or classification metadata, gets a contract derived from its own HEAD.
  - The four-way closure equality then passes against the narrowed contract.
  - N01–N03 mutate only the ReviewRequest or manifest, never the contract inputs.
- **Additional defects:** 
  - M-I16 still lists the ReviewRequest as a requiredness input.
  - `EVIDENCE_SELECTION_CONTRACT_UNRESOLVED` appears in the standard only. It is absent from the runtime taxonomy and from every test and adapter.
  - A vacuous derivation (unknown transition class → zero refs) is "deterministic", not "ambiguous", so it passes.
- **Fix:** 
  1. Resolve all derivation inputs from a pre-candidate authority snapshot, hash-pinned in the contract. Registries and the pin pointer sit outside the candidate write set.
  2. When the inputs themselves change, use the strictest of base and head per element, and make the input change a required evidence ref.
  3. Remove the ReviewRequest from M-I16. Take relationships and classification only from the governed registry.
  4. Add per-transition-class minimum baselines and a non-vacuity rule. Unknown class, empty set, or missing rule → `UNRESOLVED`. Add the code to the runtime taxonomy.
  5. Add tests for each input-poisoning path, base/head divergence, unknown class, and empty contract.

### High

**R3-H01: Provider context state is declared, not observed** (keeps H-01 and H-03 open)

- **Affected:** "Data classification and egress"; "Clean material-review context"; preflight step 7; M-70..M-73; N04–N10, N30.
- **False-green path:** 
  - Clause "cannot be enumerated, disabled, or drift-bound" lets un-enumerable context pass if it is "drift-bound". This is weaker than M-I40's "inventory or disable".
  - The fixed-policy carve-out rests on the provider "documenting" that no other context is injected. That is provider self-attestation, with no pinned document version and no behavioral check.
  - The exception "unless the platform can prove the pre-existing context is governed" has no proof mechanism. A readback that omits hidden turns looks the same as a clean one.
  - Preflight step 7 checks only profile expiry. Nothing reads current custom-instruction, memory, connector, or default-prompt state before dispatch or at admission. Drift is caught only at 7-day expiry.
  - The tests use adapters that self-report dirtiness, so undetected dirt is never falsified.
- **Fix:** 
  1. Require per-attempt `ProviderContextStateEvidence`. This means a platform-created session, a provider readback hash of the full transcript, tool and config state, and a config-state hash. Compare it with the profile at preflight, before each dispatch, and at admission.
  2. Any channel that is neither disable-able nor readable makes the mode `NOT_QUALIFIED`. The only exception is a dedicated platform-owned account whose configuration write access is change-controlled outside candidate and user.
  3. Delete the "drift-bound" alternative. Restrict the reuse exception to sessions created by the trusted adapter in the same attempt lineage, with wire records for every message.
  4. Add a behavioral sentinel qualification: plant a sentinel in each mutable channel of a test account and show it is visible when enabled and absent when disabled. Record provider documentation with a version hash as necessary but not sufficient.
  5. Add tests with a lying readback, hidden dirty state, and config change between qualification and dispatch or between dispatch and admission.

**R3-H02: The statistical protocol is not falsifiable** (keeps H-02 open)

- **Affected:** "Provider capability qualification policy"; M-I38; Phase F; M-74..M-76; N11–N17.
- **False-green path:** 
  - 59 back-to-back synthetic trials in one burst qualify the point for 7 days. "Independent" is defined only as fresh session plus fresh witness, so time, route and load correlation are ignored.
  - There are no rules on excluded trials, retries or optional stopping. There is no separation of exploration from confirmation.
  - Failure history is not persisted, so a point can be re-run until it passes.
  - "Hard failure" is undefined.
  - Trials use synthetic content, not the production envelope: real review prompt, output and reasoning limits, tools, structured output, or the worst-case token-dense content class.
  - The claimed point itself need not be tested. The 80% rule assumes monotonic behavior.
- **Fix:** 
  1. Fix the exact Clopper–Pearson criterion and remove "approximately".
  2. Require trials spread over preregistered time blocks and days with interleaved order.
  3. Count every attempted trial, including infrastructure errors. Forbid discarding and optional stopping. Keep confirmation trials disjoint from exploration trials.
  4. Persist observed failure boundaries across requalification within a drift epoch.
  5. Define hard failure and operating point. The claimed point must be tested itself or bracketed by two passing points, and monotonicity must be stated or dropped.
  6. Run qualification under the production request envelope and cover the token-worst-case content class.
  7. Let health checks invalidate a profile but never renew it.

**R3-H03: Dense witness coverage is qualification-only** (keeps H-04 open)

- **Affected:** "Delivery witness probes"; M-I39; the "Live provider pilots" section; K02; M-46; N18–N21.
- **False-green path:** 
  - Production attempts carry no per-attempt witnesses ("may").
  - A provider that loses content selectively, compacts, or behaves differently on real content or token density passes synthetic dense probing. It can then silently drop a decisive ≤2048-byte region in production.
  - Framing witnesses do not bind content. No adapter models canary-preserving content loss; `SparseCanaryGapAdapter` removes canaries.
  - "Randomized content-location challenges" is not defined. If each trial challenges only a subset, per-position and all-segments claims get fewer than 59 tests.
  - Opaque attachments are probed on synthetic text-layer pages. Scans, tables, images and embedded objects pass through an ungoverned provider-side conversion.
  - K02 says head/middle/tail success passes "for tested bound", and the pilot section still lists beginning/middle/end. Both contradict N18 and the standard.
- **Fix:** 
  1. For any mode without deterministic range or retrieval proof, require per-attempt witnesses. Options: (a) a governed lossless slicing representation with slices ≤ the granularity and platform-framing witnesses per slice plus an end sentinel, verified in the same session as the adjudication; or (b) platform-chosen random-offset content extracts per slice, chosen after freeze, which also catch selective loss.
  2. State the failure model for 2048 explicitly. Cover contiguous loss only, in min(2048 bytes, token-equivalent), and put selective or sub-granularity loss in the nonclaims.
  3. Challenge every segment in every trial.
  4. Qualify opaque attachments per media-type and content-modality class, and block other modalities or convert them under a governed transformation.
  5. Fix K02, M-46 and the pilot section. Add a canary-preserving content-drop adapter.

**R3-H04: Retrieval- or file-dependent completeness is profile-discretionary** (drives the FAIL on `SESSION_FILE_RETRIEVAL_BINDING`)

- **Affected:** "Server-side file references"; M-I27; J14; K09; N22, N29.
- **False-green path:** 
  - The profile "declares whether logs are required". When the model decides what to read, attach-time file-ID binding and synthetic qualification cannot show that every range was read this attempt.
  - A profile declaring logs "not required" yields `TESTED_SUPPORTED` from citation text, the very thing M-I27 says is insufficient.
  - N29 fires only if logs are already "required". J14 treats "final request binds all file IDs" as eligible.
- **Fix:** For any mode where the model selects what to read, per-attempt deterministic access logs are unconditionally required. They must show hash-matched coverage of every required range, member or page before admission. Otherwise the mode is diagnostic-only. Platform-forced inline inclusion is the alternative. Change J14 and add tests for missing, partial and wrong-version logs.

**R3-H05: The test matrix does not falsify the repaired invariants** (keeps H-05 open)

- **Affected:** Phases G and K; Phases N, J–M and the "Exit criteria" section; the experiment's mutation list.
- **False-green path:** 
  - K02 contradicts N18.
  - Phase G still lists 24 mutations. The new families appear only in the experiment's separate list.
  - Exit criteria name phases A–E only, so phases F–N are not gated.
  - All mutations perturb data fields. None mutates the governor's logic, such as deleting an admissibility conjunct, weakening closure equality to ⊆, dropping the dirty-session check, accepting 58 trials, or skipping the margin.
  - The fake adapters self-report, so tests exercise helpers, not adversarial oracles.
  - M-10/M-11 and C01/C02 exercise wire-visible omission, not remote silent loss.
  - No tests exist for R3-C01/H01–H04 paths.
  - Test IDs collide: matrix M01–M12 versus M-01.., and the R2 IDs M-01..M-03 versus frozen tests M-01..M-03.
  - D09 expects `REVIEWER_EVIDENCE_ASSESSMENT_CONTRADICTION`, which is defined nowhere.
- **Fix:** 
  1. Add validator-logic mutation testing where every conjunct deletion or weakening must be killed by at least one test.
  2. Merge the mutation lists and make exit criteria cover all phases.
  3. Add adversarial-oracle adapters: lying readback, canary-preserving drop, correlated or time-burst failures, and failed-trial replay.
  4. Add tests for the contract-input, state-evidence, statistical-protocol, and log-mandatory paths.
  5. Namespace the IDs and define D09's code.

### Medium / Low

- **R3-M01 (M-03 residual): revalidation is neither atomic nor final.** 
  - Live-procedure step 19 (revalidate) precedes steps 20–23, which are semantic validation, gate and checkpoint.
  - M-81 says "until newly governed validation", M-82 and N26 say "according to current policy", and the standard allows "a newly governed decision". A requalification after the fact could re-admit the old response.
  - **Fix:** 
    - Make revalidation the last step, done as compare-and-set atomically with the checkpoint.
    - Require validity over the whole interval from first dispatch to admission, with monotonic state versions.
    - Any expiry, revocation or drift inside the interval voids the attempt, and only a new attempt can proceed.
    - Add tests for requalification after expiry and for expiry between steps 20 and 22.
- **R3-M02: interaction granularity.** 
  - Families are dimension-level, and the aggregator may see only subreview outputs.
  - **Fix:** 
    - Define each interaction as a set of evidence refs that must sit raw in one qualified context.
    - The aggregator reviews raw evidence per family, or the global disposition is blocked.
- **R3-M03 (M-01 residual): permissive hedges remain.** 
  - Examples: "identity where available" (the default drift policy decides whether identity is required), "context-middle omission detection if applicable", "estimated tokens if available", "session/file binding where used", "access logs where available", M-I27 "where possible".
  - **Fix:** Default drift policy requires provider-reported deployment identity for material review. Make each item mandatory or an explicit `NOT_QUALIFIED`.
- **R3-M04: the admissibility conjunct list is incomplete.** 
  - It omits clean context, provider-semantic-context qualification, statistical and accessibility qualification, and interaction closure.
  - **Fix:** Enumerate every predicate in `VerdictAdmissibilityResult`.
- **R3-M05: cause adjudication.** 
  - The numbered list reads as first-match, so step 2 (`SCIENTIFIC_EVIDENCE_MISSING`) pre-empts step 8 (`MIXED`).
  - `EVIDENCE_SELECTION_CONTRACT_UNRESOLVED` and D09's code are missing from the runtime taxonomy.
  - **Fix:** Evaluate the causes as independent predicates, return `MIXED` if more than one holds, and reconcile the standard's and live governance's taxonomies.
- **R3-L01:** Live procedure materializes (step 13) before deriving the contract (step 14), and lacks the standard's pre-dispatch revalidation.
- **R3-L02:** Hash the request bytes at the transport boundary after SDK serialization, so SDK-injected headers and fields are captured.
- **R3-L03:** Define "applicable" for the EXP-L dependency via the governor. Require a machine-checkable EXP-L qualification record with hash and expiry, checked at admission.

## 3. Gate verdicts

| Gate Verdict Gate Verdict            |                                                               |                                    |                                                |
| ------------------------------------ | ------------------------------------------------------------- | ---------------------------------- | ---------------------------------------------- |
| REQUIRED\_EVIDENCE\_AUTHORITY        | **FAIL** (C01)                                                | INSUFFICIENT\_EVIDENCE\_TAXONOMY   | PASS (M05)                                     |
| DELIVERY\_GOVERNOR\_TRUST\_ROOT      | **FAIL** (C01: the boundary covers code, not decision inputs) | MULTI\_REVIEWER\_EQUIVALENCE       | PASS                                           |
| CLEAN\_SESSION\_CONTEXT              | **FAIL** (H01)                                                | DECOMPOSITION\_AGGREGATION         | **FAIL** (C01 relationship inputs; M02)        |
| PROVIDER\_SEMANTIC\_CONTEXT\_BINDING | **FAIL** (H01)                                                | PROMPT\_ISOLATION\_DEPENDENCY      | PASS (L03)                                     |
| WIRE\_BINDING                        | PASS (L02)                                                    | TOCTOU\_RETRY\_INTEGRITY           | PASS for manifest→wire (M01 open at admission) |
| CHUNK\_CONTEXT\_MODEL                | PASS                                                          | REVIEWER\_TOOL\_EVIDENCE\_BOUNDARY | PASS                                           |
| REMOTE\_ACCESSIBILITY\_MODEL         | **FAIL** (H03, H04)                                           | TEST\_MATRIX\_SUFFICIENCY          | **FAIL** (H05)                                 |
| PROVIDER\_CAPABILITY\_QUALIFICATION  | **FAIL** (H02)                                                | REPRESENTATION\_GOVERNANCE         | PASS (opaque modality classes under H03)       |
| MATERIALIZATION\_SAFETY              | PASS                                                          | EGRESS\_BOUNDARY                   | PASS                                           |
| SESSION\_FILE\_RETRIEVAL\_BINDING    | **FAIL** (H04)                                                |                                    |                                                |

## 4. Statistical policy adjudication

**Verdict: needs correction before preregistration freeze.**

- **The arithmetic is right.** 0.05^(1/59) ≈ 0.9505, and 58 gives ≈ 0.9497. So 59 is the exact minimum and "approximately" should go.
- **It claims less than it sounds like.** 59/59 supports only "per-trial success ≥ 0.95 at 95% confidence". That is a residual silent-failure rate of up to about 5% per attempt.
- **Power is weak.** A provider with a true 3% failure rate passes 59/59 about 17% of the time, and one at 2% passes about 30%. Since per-attempt witnesses are optional, those failures reach production as "complete".
- **Recommendation.** Preregister a risk budget per transition class. A 0.99 bound needs 299 trials. Or make per-attempt content-bound witnesses mandatory (R3-H03) and treat qualification as a prior. Record the residual in `VerdictAdmissibilityResult`. Do not call the outcome boolean "complete".
- **The 80% margin is an acceptable conservative heuristic,** but it needs the "claimed point is itself tested" rule.
- **The 7-day expiry is arbitrary and detects nothing between requalifications.** Add drift signals: identity headers, and health checks that can invalidate a profile but never renew it.

## 5. Dense-witness adjudication

- **≤2048-byte segments.** This is defensible as a qualification granularity for contiguous truncation or eviction, and not for selective or sub-granularity loss. A decisive line is tens of bytes, and 2048 is not tied to tokens. It does not by itself close H-04. It is honest only if the failure model is stated and the rest is a nonclaim.
- **Per-segment fresh framing.** It is sound for what it tests, but framing does not bind content.
- **Randomized locations.** They are only sound if every segment is challenged in every trial. Otherwise the 59-trial statistic is diluted.
- **Opaque page, range or member probes.** These are the right direction, but they need modality classes and must be page-count-bounded.
- **The design does not overclaim attention.** The fix that meets H-04 without doing so is per-attempt content-bound or slice-bound witnesses (R3-H03).

## 6. Final determination

- **Critical defect remains:** yes, R3-C01.
- **High defects remain:** yes, R3-H01 through R3-H05.
- **Ready for implementation or deterministic falsification:** no, not as reviewed. Under the frozen-evidence discipline, exposing the current text would burn first exposure and force a new boundary. Make a documentation-only revision first, then do a narrow R4 re-review of the items listed here.
- **Live provider pilots:** no.
- **Remaining prerequisites:** 
  1. R3-C01 fix with tests.
  2. Per-attempt provider state evidence and the sentinel qualification (R3-H01).
  3. A falsifiable statistical protocol, or a risk-budget policy (R3-H02).
  4. Per-attempt content-bound witnesses and an explicit failure model, with K02, M-46 and the pilot text corrected (R3-H03).
  5. Mandatory retrieval logs (R3-H04).
  6. Mutation-tested validator logic, merged mutation lists, exit criteria covering all phases, and the new adversarial adapters (R3-H05).
  7. Closure of R3-M01..M05 and R3-L01..L03.
  8. Deterministic phases green before any live pilot.
- **EXP-M remains NOT QUALIFIED.**
- **This review grants no platform-review or promotion authority.**

---

# INLINE SOURCE: experiments/governed-platform/EXP-M-R3-REVIEW-REMEDIATION.md

Git blob: `d40763743b0c0f632e175e7861af3c2ee9ce9a40`

# EXP-M R3 External Review Adjudication and Remediation

## Status

`R3_CHANGES_REQUIRED_ACCEPTED_AND_REMEDIATED_FOR_R4_REVIEW`

The supplied R3 external review is accepted as valid defect evidence. It remains non-authoritative external/manual review evidence and grants no promotion or platform-review authority.

EXP-M remains `NOT_QUALIFIED`. No live provider pilot or scientific execution is authorized by this remediation.

## R3 source review disposition

R3 returned `CHANGES_REQUIRED` and found:

- one Critical: R3-C01;
- five High: R3-H01 through R3-H05;
- Medium/Low: R3-M01 through R3-M05;
- additional lower findings R3-L01 through R3-L03.

The reviewer also found the prior 59/59 statistical rule too weak for the implied assurance and required per-attempt content-bound witnesses plus stronger provider/retrieval/context controls.

## Finding-by-finding adjudication

### R3-C01 — Requiredness contracts have no bound input authority

Evaluation: **VALID / CRITICAL**

Remediation:

1. Added immutable `GovernanceAuthoritySnapshot` from a pre-candidate authority state outside the candidate write set.
2. Transition-class, mandatory-dimension, evidence-selection, evidence-relationship, accessibility-risk and governing-standard registries are authority inputs, not candidate declarations.
3. Candidate edits to governing inputs cannot narrow their own review.
4. Base/head governing changes use a conservative merge:
   - mandatory refs/dimensions/interactions are unioned;
   - representation, evidence semantics, statistical thresholds, accessibility-risk and review constraints preserve the stricter rule;
   - incomparable conflicts fail `EVIDENCE_SELECTION_CONTRACT_UNRESOLVED`.
5. Governing elements are stable-ID + content-hash bound; same-ID semantic replacement is a changed authority input.
6. Unknown transition class, missing rule, empty/vacuous contract or missing risk policy fails closed.
7. RequiredInteractionContract is derived from the authority snapshot, not proposer metadata.
8. Added authority-input poisoning, same-ID semantic weakening, unknown-class and empty-contract falsification.

### R3-H01 — Provider context state declared rather than observed

Evaluation: **VALID / HIGH**

Remediation:

1. Added per-attempt `ProviderContextStateEvidence`.
2. Material reviews use a fresh stateless request or trusted-adapter-created fresh stateful session.
3. Context evidence binds transcript/message IDs, prompt layers, tools/connectors, custom instructions, memory state, knowledge connectors, files, model/deployment, configuration version and adapter identity.
4. Context/config state is checked at preflight, before every dispatch and at final admission.
5. Mutable semantic channels that are neither readable nor disable-able make the mode `NOT_QUALIFIED_FOR_MATERIAL_REVIEW`.
6. Stateful reuse is limited to the same trusted delivery-attempt lineage with a WireDeliveryRecord for every prior mutation.
7. Added behavioral sentinel qualification for every mutable provider semantic channel.
8. Added `AdmissionFenceRecord`/provider version requirement so concurrent candidate/user configuration changes cannot race final admission.
9. Provider documentation is background evidence only; it cannot prove clean context by itself.
10. Added lying-readback, hidden-dirty-state and configuration-race tests/adapters.

### R3-H02 — Statistical capability protocol not falsifiable

Evaluation: **VALID / HIGH**

Remediation:

The former 59/59 rule was replaced.

Default material-review risk budget is now:

- `p_min = 0.99`;
- one-sided 95% exact Clopper–Pearson;
- **299/299** successful confirmation trials at each claimed operating point;
- zero hard failures;
- all attempted trials count, including timeout/provider error/rate limit/ambiguous/unverifiable outcomes;
- no exclusions, rerolls, optional stopping or failed-attempt replacement;
- exploration and confirmation are disjoint;
- confirmation trial IDs and schedule are frozen before exposure;
- confirmation spans at least 3 UTC days and 4 preregistered time blocks/day with randomized/interleaved operating points;
- exact claimed operating point must be tested;
- no monotonic interpolation assumption;
- production-equivalent prompt/tools/structured-output/output budget and worst-case token-density/media classes required;
- append-only failure history persists through the provider drift epoch;
- health checks may invalidate but never renew;
- default expiry remains 7 days with immediate drift-triggered invalidation.

Hard failure and the full operating-point tuple are now explicitly defined.

The exact arithmetic is used: 298/298 is below a 0.99 one-sided 95% lower bound, while 299/299 exceeds it.

The statistical interpretation is also bounded: if provider-side route/trial independence cannot be evidenced, the profile records `STATISTICAL_INDEPENDENCE_UNPROVEN`; the Clopper–Pearson value cannot be presented as a universal provider failure probability.

### R3-H03 — Dense witness coverage qualification-only

Evaluation: **VALID / HIGH**

Remediation:

1. Sparse head/middle/tail canaries are explicitly diagnostic only.
2. For modes without deterministic range/retrieval proof, per-attempt content-bound witnesses are mandatory in the same final adjudication session.
3. Lossless text is sliced to at most:
   - 2048 UTF-8 bytes; and
   - 512 provider-tokenizer tokens;
   whichever is smaller.
4. Every required slice is challenged in every confirmation trial.
5. The platform selects unpredictable slice-local content extracts after representation freeze; expected values are withheld from the reviewer.
6. Framing/end sentinels remain supplemental and cannot substitute for content-bound checks.
7. The failure model is explicit: this witnesses contiguous loss/eviction at or above the slice granularity; arbitrary selective/sub-slice loss remains a nonclaim/residual risk.
8. Added `ProviderAccessibilityRiskPolicy` per transition class. Highest material-authority transitions require deterministic full-range/page/member proof or an equivalently observable inline mode; probabilistic witnesses alone cannot silently satisfy that class.
9. Opaque attachments are qualified by media/modality class; scans/tables/images/embedded objects cannot inherit text-PDF qualification.
10. Added canary-preserving content-loss and selective-loss tests.

### R3-H04 — Retrieval/file completeness discretionary

Evaluation: **VALID / HIGH**

Remediation:

For model-selected retrieval, deterministic per-attempt access logs are now unconditional for material review.

They must prove every required range/page/member with:

- exact source/version identity;
- requested range/member;
- returned content hash and length/range;
- retrieval time;
- tool/result message identity;
- binding of the tool result into the same final adjudication session/context.

“File opened”, file ID binding, citation text or attach-time success are insufficient.

If the provider cannot expose sufficient deterministic retrieval/context logs, that mode is diagnostic-only / `NOT_QUALIFIED_FOR_MATERIAL_REVIEW`. Platform-forced inline inclusion is the alternative.

### R3-H05 — Test matrix did not falsify repaired invariants

Evaluation: **VALID / HIGH**

Remediation:

1. Matrix IDs are namespaced `TM-...` to avoid collision with frozen `M-...` experiment cases.
2. Phase G is now the single unified mutation catalog.
3. Added validator-logic mutation phase:
   - delete each admissibility conjunct;
   - weaken equality to subset;
   - bypass authority snapshot;
   - accept empty contract;
   - drop dirty-context check;
   - accept 298 instead of 299;
   - allow one hard failure;
   - make witnesses/retrieval logs optional;
   - skip final atomic CAS;
   - revive void attempt;
   - skip prompt-isolation/risk/fence predicates.
4. Added adversarial-oracle adapters for:
   - authority-input poisoning;
   - lying context readback;
   - hidden dirty state;
   - correlated/time-burst trials;
   - failed-trial replay;
   - production-envelope mismatch;
   - canary-preserving content loss;
   - missing retrieval logs;
   - atomic admission race.
5. Exit criteria now require **all deterministic phases A–Q** and zero data/state and validator-logic mutation survivors.
6. Defined `REVIEWER_EVIDENCE_ASSESSMENT_CONTRADICTION` and reconciled failure taxonomy.

## Medium/Low closure

### R3-M01 — revalidation not atomic/final

Accepted and repaired.

Verdict admission is now the final authority operation and uses compare-and-set with the checkpoint. Authority snapshot, capability profile, accessibility-risk policy, egress state, provider context/session/file state, AdmissionFenceRecord, prompt-isolation record and ReviewRequest identities are re-read at admission.

Any invalidation from first dispatch through admission permanently voids the attempt. Later requalification cannot revive the old response.

### R3-M02 — interaction granularity

Accepted and repaired.

Each RequiredInteractionContract interaction is an explicit set of raw evidence refs/representations that must coexist in one qualified reviewer context. The aggregator reviews the raw set, not only subreview outputs.

### R3-M03 — permissive hedges

Accepted and narrowed.

Load-bearing provider deployment/retrieval/context facts are mandatory when the selected proof mode needs them. Missing required deployment identity, range logs or context state makes the mode not qualified rather than silently optional.

### R3-M04 — incomplete admissibility conjunct list

Accepted and repaired.

`VerdictAdmissibilityResult` now enumerates all load-bearing predicates: authority snapshot, evidence contract, interaction contract, materialization, transformation, egress, statistical capability, accessibility-risk policy, provider context, admission fence, wire binding, per-attempt accessibility, retrieval/session/file coverage, prompt isolation, semantic coverage, provenance and disposition.

### R3-M05 — cause adjudication first-match

Accepted and repaired.

Insufficiency causes are evaluated independently. Multiple true causes yield `MIXED_INSUFFICIENCY` with the complete cause set.

Added/reconciled:
- `EVIDENCE_SELECTION_CONTRACT_UNRESOLVED`
- `REVIEWER_EVIDENCE_ASSESSMENT_CONTRADICTION`
- provider context/retrieval/admission failure codes.

### R3-L01 — live procedure ordering

Accepted and repaired.

Authority snapshot + required contracts are derived before materialization. Pre-dispatch state revalidation is explicit.

### R3-L02 — SDK serialization boundary

Accepted and repaired.

WireDeliveryRecord now includes:
- pre-SDK platform request hash;
- post-SDK transport-bound semantic envelope hash at the lowest observable adapter boundary;
- all non-secret semantic routing/model/tool/file/session fields.

If the SDK hides a load-bearing semantic mutation, the adapter/mode cannot claim exact wire binding.

### R3-L03 — EXP-L applicability

Accepted and repaired.

The governor now selects a machine-checkable, hash-bound, non-expired `PromptIsolationQualificationRecord` for the exact provider/representation mode. It is checked at preflight and atomic admission.

## Additional self-adjudication after R3 repair

A further false-green pass found and repaired four additional design weaknesses before R4 handoff:

### SA-R4-H01 — governing semantic replacement under same ID

A candidate could retain a required-ref ID while weakening representation/risk semantics.

Repair: governing elements are stable-ID + hash bound; base/head semantic changes preserve the stricter requirement or fail unresolved.

### SA-R4-H02 — probabilistic accessibility used without transition risk authority

Repair: added ProviderAccessibilityRiskPolicy to the authority snapshot. Highest material-authority class requires deterministic proof; missing policy fails closed.

### SA-R4-H03 — provider configuration race at admission

Repair: added AdmissionFenceRecord/readable monotonic provider config version. Unfenceable/unreadable load-bearing mutable channels make the mode unqualified.

### SA-R4-H04 — retrieval logs proved opening but not final-context insertion

Repair: retrieval evidence now binds returned bytes/hash/range and resulting tool-message identity to the final adjudication session.

### SA-R4-M01 — statistical independence overclaim

Repair: correlation/route independence is explicitly bounded. Fresh request IDs alone do not prove independent Bernoulli trials; `STATISTICAL_INDEPENDENCE_UNPROVEN` is recorded when provider-side correlation cannot be evidenced.

## Fresh self-adjudication result

After the above additional repairs, a fresh adversarial design pass found:

- open Critical design findings: **0**
- open High design findings: **0**

This is **self-review only**. It is not independent evidence and does not qualify EXP-M.

## R4 handoff

`READY_FOR_R4_INDEPENDENT_DESIGN_REVIEW`

No implementation or live provider pilot should begin until the R4 review closes the design boundary and deterministic implementation/falsification is separately authorized.
