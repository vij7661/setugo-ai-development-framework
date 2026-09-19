# EXP-M Independent R5 Review Packet

## Packet status

`R5_EXTERNAL_REVIEW_REQUESTED_NO_AUTHORITY_EFFECT`

This is a self-contained R5 design/preregistration review packet for:

**EXP-M — Review Evidence Delivery & Reviewer Context Integrity Falsification**

R4 returned `CHANGES_REQUIRED` with two remaining High defects and several Medium/Low gaps. The current source accepts those findings and claims to have repaired them, then performed further iterative self-adjudication until no additional Critical/High design defect was found.

Do **not** trust that claim. Reconstruct the trust boundaries from the inline current source.

EXP-M remains `NOT_QUALIFIED`.
No implementation, deterministic experiment execution, live provider pilot, review promotion, or authority transition is authorized by this packet.

## Reviewed source identity

- repository: `vij7661/setugo-ai-development-framework`
- branch: `experiment/exp-m-review-evidence-delivery-integrity`
- base main commit: `87f6e3df73c0c70c5d8ff4da38365ff92721aff7`
- prior R4 packet commit: `27316f07ee05a7a17efac00ce5de26b70d059616`
- current R5 reviewed source commit: `4d8471a0803c2d5159a4aaa41fc3198660ea41ed`
- current R5 reviewed source tree: `3e6b9f8614072a0290e410a90af124f269eb4cb5`

Current reviewed blobs:
- `standards/review-evidence-delivery-integrity.md` — `c4c1e4f561eb36e44f7bb6aa1bc59df8d4c4bf09`
- `experiments/governed-platform/exp-m-review-evidence-delivery-integrity.md` — `1551c007d9e7592d39f1280e504bf107b7aa14c0`
- `experiments/governed-platform/EXP-M-TEST-MATRIX.md` — `15b2b2ceb212fc40d144790b0f68674b26a55013`
- `governance-runtime/LIVE-CONVERSATION-GOVERNANCE.md` — `b749547a0ca7c294139c7f056ca2000a7badcb47`
- `experiments/governed-platform/EXP-M-R4-EXTERNAL-REVIEW.md` — `96faf86db6677402d7184767ca1805b419ca9d12`
- `experiments/governed-platform/EXP-M-R4-REVIEW-REMEDIATION.md` — `07f3fc3a11aedefdb6ab84367049cba311616b81`

## R4 disposition being remediated

R4 overall disposition:

`CHANGES_REQUIRED`

R4 found:

### High
- R4-H01 — hidden unexposed mutable provider semantic state could escape ProviderContextStateEvidence and the admission fence;
- R4-H02 — validator-logic mutation coverage did not delete/weaken every VerdictAdmissibilityResult conjunct.

### Medium/Low
- R4-M01 — live-governance failure taxonomy omitted normative EXP-M codes;
- R4-M02 — base/head “stricter” merge lacked a defined per-element partial order;
- R4-L01 — no explicit health-check-cannot-renew test.

The current source claims these are repaired.

## Additional self-adjudication after direct R4 repair

The proposer/model then found and repaired additional design risks:

- witness challenge/response traffic could evict evidence before final adjudication;
- witness prompts/results could contaminate semantic review authority;
- provider capability confirmation attempts could be cherry-picked or rerun until pass;
- implicit SDK retries could hide first failures;
- the explicit admissibility predicate mutation list could drift again;
- statistical independence could be overclaimed;
- witness-protocol qualification could self-authorize.

The current source claims a fresh pass now has:

- open Critical design findings = 0
- open High design findings = 0

This is self-review only.

## R5 primary objective

Attempt to falsify the claim that the design is now ready for implementation and deterministic falsification.

Focus on whether the repairs actually close the authority/evidence paths rather than merely relabeling them.

## A. R4 finding closure

For each prior finding return:

- R4-H01: CLOSED / PARTIAL / OPEN
- R4-H02: CLOSED / PARTIAL / OPEN
- R4-M01: CLOSED / PARTIAL / OPEN
- R4-M02: CLOSED / PARTIAL / OPEN
- R4-L01: CLOSED / PARTIAL / OPEN

For anything not CLOSED provide:
- exact false-green/failure path;
- affected current rule/invariant/test;
- narrow required correction.

## B. GovernanceAuthoritySnapshot and merge authority

Try to break:

- pre-candidate authority snapshot;
- snapshot pointer outside candidate write authority;
- transition-class registry;
- evidence-selection registry;
- evidence-relationship registry;
- accessibility-risk registry;
- context-isolation-policy registry;
- admissibility-predicate registry.

Challenge base/head merge using:

- deletion;
- same-ID semantic weakening;
- renamed replacement;
- representation downgrade;
- changed egress semantics;
- changed statistical threshold;
- changed risk policy;
- incomparable same-dimension semantics.

Verify that typed comparison rules are complete enough and incomparable changes fail unresolved rather than being guessed.

Return:
`GOVERNANCE_AUTHORITY_AND_MERGE = PASS / FAIL`

## C. Provider hidden-state/context isolation

Review `ProviderContextIsolationPolicy`.

Attempt to break both allowed bases:

1. COMPLETE_READABLE_FENCED_STATE
2. DEDICATED_PLATFORM_ACCOUNT_STATELESS_BOUNDARY

Check:

- candidate/end-user cannot mutate account/project settings;
- production account is not contaminated by sentinel qualification;
- provider docs/contract/account-class/config-template are identity/version bound;
- exposed mutable channels are disabled/read/fenced;
- hidden provider-internal mutable semantic state is not called “observed clean”;
- hidden-state residual is explicit;
- highest material-authority transition defaults to DISALLOW;
- lower transition acceptance, if allowed, is independently governed and recorded;
- provider config drift invalidates qualification.

Try a fake provider with a hidden unexposed mutable state that changes verdicts.

Return:
`PROVIDER_CONTEXT_ISOLATION = PASS / FAIL`

## D. Admission fence and atomic admission

Attempt races:

- config changes after preflight;
- after dispatch;
- after provider response;
- after final state read but before checkpoint CAS;
- profile expires before admission;
- egress revoked before admission;
- prompt-isolation record expires;
- registry version changes;
- provider file/session state changes.

Verify:

- atomic compare-and-set is the final authority operation;
- all required versions/hashes participate;
- any invalidation from first dispatch through admission permanently voids the attempt;
- later requalification NEVER revives the old response.

Return:
`ATOMIC_ADMISSION = PASS / FAIL`

## E. Provider capability statistics and attempt-selection closure

Review the full protocol:

- p_min = 0.99;
- one-sided 95% exact Clopper–Pearson;
- 299/299 confirmation minimum under zero failures;
- every attempted trial counted;
- no exclusions/rerolls/optional stopping;
- exploration and confirmation disjoint;
- frozen trial IDs/schedule/interleaving seed before exposure;
- >=3 UTC days;
- >=4 time blocks/day;
- exact claimed operating point tested;
- production-equivalent request envelope/content class;
- append-only failure history;
- health checks invalidate only and cannot renew.

Then attack `ProviderQualificationExecutionPlan`:

- delete a failed planned slot;
- skip a planned slot;
- replace a failure with successful retry;
- run hidden unscheduled calls;
- let candidate/operator invoke the qualification credential;
- let SDK silently retry.

Verify qualification credentials/runner and attempt ledger make post-result cherry-picking impossible within the stated trust model.

Also adjudicate:

- whether 299 is the exact minimum under the stated exact-binomial model;
- whether `STATISTICAL_INDEPENDENCE_UNPROVEN` is handled honestly;
- whether a profile may claim `statistical_qualified=true` when the transition policy requires the probability claim but provider-side independence cannot be evidenced.

Return:
`PROVIDER_CAPABILITY_AND_ATTEMPT_CLOSURE = PASS / FAIL`

## F. Accessibility witnesses and witness protocol

Attack:

- evidence slices <= min(2048 UTF-8 bytes, 512 provider tokens);
- every slice challenged every confirmation trial;
- per-attempt content-bound witnesses in the same final adjudication session;
- canary-preserving content loss;
- selective sub-slice loss;
- witness response larger than budget;
- witness transcript evicting early evidence;
- evaluative witness prompts;
- witness output being accepted as semantic review evidence;
- stale/wrong-provider WitnessProtocolQualificationRecord;
- candidate-authored witness qualification.

Verify:

- sparse canaries are diagnostic only;
- framing sentinels are supplemental only;
- content-bound witnesses are load-bearing for the bounded failure model;
- actual context size is rechecked after witness phase;
- witness output is non-evidence/non-adjudicative;
- EXP-M does not claim counterfactual semantic invariance;
- witness qualification authority is outside candidate control.

Return:
`WITNESS_ACCESSIBILITY_BOUNDARY = PASS / FAIL`

## G. ProviderAccessibilityRiskPolicy

Verify every protected transition has a risk policy.

Attack:

- missing policy;
- probabilistic witness proof used when deterministic proof is required;
- hidden selective/sub-slice risk accepted without policy;
- statistical independence uncertainty ignored;
- highest material-authority transition using probabilistic witness-only proof.

Return:
`ACCESSIBILITY_RISK_POLICY = PASS / FAIL`

## H. File/retrieval completeness

For model-selected retrieval require per-attempt proof of:

- source/version;
- exact page/range/member;
- returned content hash and length;
- retrieval time;
- tool/result message identity;
- binding of returned content to the same final adjudication context.

Attack:

- file ID only;
- “file opened” log only;
- citation only;
- wrong version;
- partial range;
- correct bytes but tool result not inserted into final context;
- retrieval result from another session.

Return:
`RETRIEVAL_FINAL_CONTEXT_BINDING = PASS / FAIL`

## I. Admissibility predicate registry

Inspect the current VerdictAdmissibilityResult predicate set.

Verify exact closure:

`required registry predicates
 == verdict-result predicates
 == validator logic mutation targets
 == independently killed mutations`

Try:

- add a new predicate without a test;
- remove a predicate from result;
- delete a validator conjunct;
- weaken equality to subset/superset;
- provide mutation target without killing fixture;
- change registry version between preflight and admission;
- candidate edits registry used for its own review.

Confirm Phase O has a targeted logic mutation for every current load-bearing conjunct.

Return:
`ADMISSIBILITY_PREDICATE_CLOSURE = PASS / FAIL`

## J. Retry/TOCTOU/wire binding

Attack:

- source mutation after manifest freeze;
- representation mutation;
- post-SDK semantic mutation;
- hidden SDK/client retry;
- changed model/tool/file/session field;
- retry with changed body;
- reused attempt identity.

Return:
`WIRE_RETRY_TOCTOU = PASS / FAIL`

## K. Prompt isolation dependency

Verify the exact review mode requires a:

`PromptIsolationQualificationRecord`

that is:

- machine-checkable;
- hash-bound;
- provider/mode bound;
- non-expired;
- checked at preflight;
- checked again at atomic admission.

Witness protocol must also be bound to the same prompt-isolation mechanism.

Return:
`PROMPT_ISOLATION_DEPENDENCY = PASS / FAIL`

## L. Taxonomy/cause adjudication

Compare normative standard and live governance taxonomies.

Verify no normative EXP-M failure code is missing.

For INSUFFICIENT_EVIDENCE:

- evaluate cause predicates independently;
- multiple true causes => MIXED_INSUFFICIENCY;
- no proven cause => INSUFFICIENT_EVIDENCE_CAUSE_UNRESOLVED;
- reviewer contradiction does not become scientific absence;
- delivery failure does not become scientific absence.

Return:
`FAILURE_TAXONOMY_AND_CAUSE = PASS / FAIL`

## M. Test matrix and first-exposure readiness

Verify:

- IDs are namespaced;
- all deterministic phases A–T are gated;
- unified mutation catalog is authoritative;
- every admissibility conjunct has targeted logic mutation;
- hidden-state, admission-race, witness-eviction, canary-preserving-drop, qualification-cherry-pick, failed-trial replacement, implicit SDK retry, comparator weakening, and registry drift all have adversarial tests;
- zero mutation survivors is required.

Determine whether any load-bearing invariant is stated but not falsified.

Return:
`TEST_MATRIX_SUFFICIENCY = PASS / FAIL`

## Required overall output

Return exactly one:

- `BOUNDED_PASS`
- `CHANGES_REQUIRED`
- `INSUFFICIENT_EVIDENCE`

Then provide:

### Critical findings
For each:
- ID
- severity
- affected section/invariant/test
- concrete false-green path
- why current design is insufficient
- narrow fix

### High findings
Same fields.

### Medium/Low findings
Same fields.

Then return:

- R4-H01 = CLOSED / PARTIAL / OPEN
- R4-H02 = CLOSED / PARTIAL / OPEN
- R4-M01 = CLOSED / PARTIAL / OPEN
- R4-M02 = CLOSED / PARTIAL / OPEN
- R4-L01 = CLOSED / PARTIAL / OPEN

and:

- REQUIRED_EVIDENCE_AUTHORITY = PASS / FAIL
- DELIVERY_GOVERNOR_TRUST_ROOT = PASS / FAIL
- GOVERNANCE_AUTHORITY_AND_MERGE = PASS / FAIL
- PROVIDER_CONTEXT_ISOLATION = PASS / FAIL
- PROVIDER_CONTEXT_ADMISSION_FENCE = PASS / FAIL
- ATOMIC_ADMISSION = PASS / FAIL
- PROVIDER_CAPABILITY_AND_ATTEMPT_CLOSURE = PASS / FAIL
- STATISTICAL_PROTOCOL = PASS / FAIL
- WITNESS_ACCESSIBILITY_BOUNDARY = PASS / FAIL
- ACCESSIBILITY_RISK_POLICY = PASS / FAIL
- REPRESENTATION_GOVERNANCE = PASS / FAIL
- MATERIALIZATION_SAFETY = PASS / FAIL
- EGRESS_BOUNDARY = PASS / FAIL
- SESSION_FILE_RETRIEVAL_BINDING = PASS / FAIL
- RETRIEVAL_FINAL_CONTEXT_BINDING = PASS / FAIL
- ADMISSIBILITY_PREDICATE_CLOSURE = PASS / FAIL
- FAILURE_TAXONOMY_AND_CAUSE = PASS / FAIL
- MULTI_REVIEWER_EQUIVALENCE = PASS / FAIL
- DECOMPOSITION_AGGREGATION = PASS / FAIL
- PROMPT_ISOLATION_DEPENDENCY = PASS / FAIL
- WIRE_RETRY_TOCTOU = PASS / FAIL
- REVIEWER_TOOL_EVIDENCE_BOUNDARY = PASS / FAIL
- TEST_MATRIX_SUFFICIENCY = PASS / FAIL

Finally state:

- whether any Critical design defect remains;
- whether any High design defect remains;
- whether EXP-M is ready for implementation/deterministic falsification;
- whether live provider pilots may begin;
- exact remaining prerequisites;
- explicit confirmation that EXP-M remains NOT QUALIFIED;
- explicit confirmation that this R5 external/manual review itself grants no platform-review or promotion authority.

## Nonclaims

This packet does not claim:

- implementation exists;
- deterministic tests have executed;
- any live provider is qualified;
- hidden provider internals are fully observable;
- remote model cognition/attention is proved;
- provider telemetry is cryptographic evidence;
- statistical trials are independent when independence cannot be evidenced;
- probabilistic witness probes detect arbitrary selective/sub-slice loss;
- self-adjudication is independent;
- this packet transport is itself a platform-authenticated review execution.

## Inline current review material


---

# INLINE SOURCE: standards/review-evidence-delivery-integrity.md

Git blob: `c4c1e4f561eb36e44f7bb6aa1bc59df8d4c4bf09`

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


---

# INLINE SOURCE: experiments/governed-platform/exp-m-review-evidence-delivery-integrity.md

Git blob: `1551c007d9e7592d39f1280e504bf107b7aa14c0`

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

### M-I37 — Material review context isolation is policy-bound

Material reviews use a fresh stateless request or fresh trusted-adapter stateful session under a ProviderContextIsolationPolicy. Observable mutable provider context must be absent/disabled/readable/fenced. Hidden provider-internal mutable semantic state is never silently called clean: it is either disallowed or retained as an explicit dedicated-account external-trust residual authorized by the transition-class policy.

### M-I38 — Capability qualification thresholds are preregistered

Live provider capability qualification uses a fixed risk-budget protocol before exposure: default p_min=0.99, one-sided 95% exact Clopper–Pearson, at least 299/299 successful disjoint confirmation trials at each claimed operating point, zero hard failures, no exclusions/rerolls/optional stopping, production-equivalent envelope/content classes, append-only failure history, conservative 80% scalar safety cap, and 7-day/default drift-triggered requalification.

### M-I39 — Accessibility probes are dense and per-attempt

When deterministic range/retrieval proof is unavailable, qualification and every production material-review attempt use content-bound witnesses for every required lossless slice. Each text slice is no larger than min(2048 UTF-8 bytes, 512 provider-tokenizer tokens). Every slice is challenged in every confirmation trial. Opaque files require media/modality-specific page/range/member proof or governed lossless transformation.

### M-I40 — Provider-injected semantic context is fail-closed

Provider/model modes must inventory or disable exposed mutable default/custom prompts, project/account memory, and provider-side knowledge connectors. A hidden/unexposed mutable-semantic-state possibility is governed by ProviderContextIsolationPolicy: DISALLOW means NOT_QUALIFIED; the dedicated-account residual mode is permitted only when independently authorized for that transition class and is recorded as a nonclaim.

### M-I41 — Cross-evidence interaction requirements are independently derived

Review decomposition uses a RequiredInteractionContract derived only from the GovernanceAuthoritySnapshot's platform-owned relationship registry, mandatory dimensions, transition class, and governing standards. Each interaction is an explicit set of raw evidence refs that must coexist in one qualified context; proposer-declared interaction lists cannot narrow it.

### M-I42 — Governor decision inputs are outside candidate self-approval

The GovernanceAuthoritySnapshot, transition-class registry, evidence-selection registry, relationship registry, capability registry, accessibility-risk registry, context-isolation-policy registry, and authority-snapshot pointer are outside the candidate write set. Candidate edits to governing inputs are reviewed as evidence and cannot narrow their own review. Governing elements are stable-ID + content-hash bound; changing semantics under the same ID is treated as a changed input, and base/head representation/acceptance/risk constraints preserve the stricter rule or fail unresolved.

### M-I43 — Provider context state is observed per attempt

Every material review carries ProviderContextStateEvidence from the trusted adapter at preflight, before each dispatch, and at atomic admission for every observable semantic channel. ProviderContextIsolationPolicy separately governs unexposed provider-internal mutable-state residuals; observable channels that are neither readable nor disable-able make the provider/mode NOT_QUALIFIED_FOR_MATERIAL_REVIEW.

### M-I44 — Confirmation trials are disjoint, scheduled, and append-only

Exploration cannot count as confirmation. Confirmation trial identities/schedule are frozen, all attempted trials count, failures cannot be erased by reruns, and the claimed operating point itself is tested under the production-equivalent envelope.

### M-I45 — Verdict admission is atomic and final

Capability, egress, provider-context/session/file state, authority snapshot, ReviewRequest, and prompt-isolation qualification remain valid from first dispatch through a final compare-and-set admission. Any invalidation in that interval permanently voids the attempt; later requalification cannot revive it.

### M-I46 — Prompt isolation dependency is machine-bound

Material review requires a current hash-bound PromptIsolationQualificationRecord selected deterministically by the governor for the exact provider/representation mode and checked again at atomic admission.

### M-I47 — Accessibility risk is transition-class governed

Every protected transition class has a ProviderAccessibilityRiskPolicy in the GovernanceAuthoritySnapshot. Unknown policy fails closed. The highest material-authority class requires deterministic full-range/page/member proof or an equivalently observable inline mode; probabilistic per-attempt witnesses alone cannot silently satisfy it.

### M-I48 — Observable mutable provider context is fenced through admission

Every load-bearing observable mutable provider/account/project/session configuration channel has a readable monotonic version or a platform-enforceable AdmissionFenceRecord. If neither exists, the mode is NOT_QUALIFIED_FOR_MATERIAL_REVIEW. Hidden provider-internal state cannot be “fenced by assertion”; it is handled only by ProviderContextIsolationPolicy/nonclaim.

### M-I49 — “Complete” is not an admissibility claim

The platform uses REVIEW_CONTEXT_QUALIFIED_AVAILABLE, not REVIEW_CONTEXT_COMPLETE, and records the qualified failure model plus residual/nonclaim risk in VerdictAdmissibilityResult.

### M-I50 — Statistical independence is not silently assumed

Provider capability qualification records time/routing/deployment diversity and whether trial independence is actually evidenced. If provider-side correlation cannot be observed, STATISTICAL_INDEPENDENCE_UNPROVEN is recorded and the exact-binomial bound is not treated as a universal provider failure probability.

### M-I51 — Retrieval proof binds returned bytes into final context

Model-selected retrieval logs must prove exact returned content hash/range/version and the resulting tool/message binding into the same final adjudication context. “File opened” or citation-only logs are insufficient.

### M-I52 — Hidden provider state is an explicit trust residual, never an observed-clean claim

A material review binds ProviderContextIsolationPolicy. The admissible bases are COMPLETE_READABLE_FENCED_STATE or DEDICATED_PLATFORM_ACCOUNT_STATELESS_BOUNDARY. The highest material-authority transition defaults to DISALLOW for hidden provider mutable-state residuals. Dedicated-account residual acceptance must be independently governed and recorded in VerdictAdmissibilityResult.

### M-I53 — Governing “stricter” comparisons are typed and fail closed

Base/head governance merge uses explicit per-element partial orders. Set requirements use union/intersection rules as applicable; fidelity/review level/risk/statistical/expiry/limit classes have governed comparators. Incomparable same-dimension semantic changes remain unresolved and cannot be auto-merged.

### M-I54 — Witness traffic cannot evict the evidence it is proving

The provider operating point and preflight include witness challenges, maximum witness-response budget, wrappers, final semantic prompt, and final output budget. Actual context size is rechecked after the witness phase and before semantic adjudication. Witness-induced eviction voids the attempt.

### M-I55 — Witness protocol is non-evaluative and structurally isolated

Witness challenges may test exact accessibility only; they cannot ask for evaluation or conclusions. Material witness-based review requires a current WitnessProtocolQualificationRecord bound to provider/mode/prompt-isolation mechanism. Witness outputs are non-evidence/non-adjudicative and cannot satisfy semantic review dimensions. EXP-M does not claim counterfactual semantic invariance of stochastic model outcomes.

### M-I56 — Witness qualification cannot self-authorize

WitnessProtocolQualificationRecord and its registry are platform-owned, outside candidate write authority, version/hash/expiry bound, and invalidated by provider/prompt-isolation/witness-protocol drift. Candidate code/content cannot mint or widen the record.

### M-I57 — Capability confirmation attempt set is closed before exposure

ProviderQualificationExecutionPlan freezes confirmation trial IDs, schedule, interleaving seed, trusted runner and credential/egress identity before confirmation exposure. Candidate/user/operator code cannot select which observed attempts count after results are known. Missing scheduled slots are failures; retries cannot replace failures; unexplained calls on the qualification credential invalidate the epoch when they cannot be reconciled.

### M-I58 — SDK/client retries are observable attempts

Trusted provider adapters disable implicit retries or expose every physical retry with its own immutable WireDeliveryRecord/qualification attempt. A hidden failed request followed by transparent-to-caller retry success cannot count as one success.

### M-I59 — Admissibility predicate coverage is machine-closed

A platform-owned AdmissibilityPredicateRegistry defines every load-bearing predicate, validator identity, negative fixture and logic mutation. The required predicate set, VerdictAdmissibilityResult predicate set, mutation targets and independently killed mutations must be exactly equal.

## Required mechanism surfaces

Future implementation should expose governed objects equivalent to:

- `GovernanceAuthoritySnapshot`
- `RequiredEvidenceContract`
- `RequiredInteractionContract`
- `EvidenceDeliveryManifest`
- `ProviderCapabilityProfile`
- `ProviderAccessibilityRiskPolicy`
- `ProviderContextIsolationPolicy`
- `WitnessProtocolQualificationRecord`
- `AdmissionFenceRecord`
- `ProviderQualificationExecutionPlan`
- `ProviderCapabilityQualificationRecord`
- `ProviderContextStateEvidence`
- `PromptIsolationQualificationRecord`
- `DeliveryPreflightResult`
- `WireDeliveryRecord`
- `EvidenceChunk`
- `ReviewerReceipt`
- `DeliveryCompletenessResult`
- `InsufficientEvidenceAdjudication`
- `AdmissibilityPredicateRegistry`
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

### M-110 — Hidden unexposed provider mutable state with no isolation policy

A fake provider has an unexposed semantic-state channel that changes the verdict.

Expected:
ProviderContextIsolationPolicy missing/unsatisfied; material review NOT_QUALIFIED.

### M-111 — Highest-authority transition attempts dedicated-account residual mode

The provider cannot prove complete readable/fenced mutable state and the transition policy defaults hidden residual to DISALLOW.

Expected:
material review blocked.

### M-112 — Dedicated-account residual explicitly governed for a permitted lower transition

Use a dedicated platform-owned account/project with candidate/user writes disabled, pinned provider product policy, exposed configuration disabled/read/fenced, disposable-account sentinel qualification, and explicit hidden-state residual acceptance.

Expected:
context-isolation predicate may pass only with the residual recorded; no “observed clean” claim.

### M-113 — Sentinel qualification contaminates production review account

Qualification enables a memory/customization sentinel on the production review account rather than a disposable qualification account.

Expected:
qualification invalid; production review account must never be contaminated by sentinel setup.

### M-114 — Health check attempts to renew expired provider profile

An expired capability profile receives a successful health check without full confirmation requalification.

Expected:
profile remains expired; health check can invalidate only.

### M-115 — Incomparable same-dimension governance change

Base and head representation/risk semantics conflict with no defined partial-order winner.

Expected:
EVIDENCE_SELECTION_CONTRACT_UNRESOLVED; no auto-merge.

### M-116 — Typed stricter comparator regression

Mutate one comparator (for example allow-set intersection→union, evidence-set union→intersection, expiry shorter→longer).

Expected:
logic mutation killed.

### M-117 — Witness response causes context eviction

A witness challenge/response transcript pushes an earlier required evidence slice outside the qualified final context.

Expected:
post-witness pre-adjudication context check fails; attempt void.

### M-118 — Witness protocol asks evaluative question

A challenge asks the reviewer to summarize or judge evidence rather than return exact accessibility content.

Expected:
WitnessProtocolQualificationRecord/protocol validation fails.

### M-119 — Witness output is treated as semantic review evidence

The final semantic validator allows witness extracts/answers to satisfy a required review dimension or create authority.

Expected:
structural isolation failure; witness output remains non-evidence/non-adjudicative.

### M-120 — Witness protocol record stale or wrong provider/prompt-isolation mode

Expected:
verdict inadmissible.

### M-121 — Candidate-authored witness qualification record

Candidate supplies a record claiming its own witness protocol is noninterfering.

Expected:
untrusted record rejected; witness-based material review inadmissible.

### M-122 — Provider isolation documentation/config template drifts

Pinned provider account-class documentation or production configuration-template hash changes after qualification.

Expected:
ProviderContextIsolationPolicy/ProviderCapabilityProfile binding invalidated; requalification required.

### M-123 — Confirmation schedule omits failed slot

A planned trial fails or is skipped, then the runner removes that trial ID before final qualification calculation.

Expected:
plan/ledger mismatch; QUALIFICATION_ATTEMPT_CLOSURE_UNPROVEN and qualification fails.

### M-124 — Retry replaces failed confirmation attempt

A failed trial is rerun successfully and only the successful retry is counted.

Expected:
original hard failure remains append-only; zero-failure criterion cannot pass.

### M-125 — Unscheduled hidden qualification calls

Additional provider calls use the dedicated qualification credential outside the frozen plan.

Expected:
if provider audit reconciliation exposes them, confirmation epoch invalidated; if reconciliation is unavailable and credential/egress exclusivity is unproven, QUALIFICATION_ATTEMPT_CLOSURE_UNPROVEN.

### M-126 — Candidate/operator can invoke qualification credential

Expected:
qualification runner trust boundary fails; profile cannot be material-review qualified.

### M-127 — SDK hides failed physical attempt behind automatic retry success

Expected:
IMPLICIT_RETRY_UNOBSERVED or explicit first-attempt hard failure; no single-success representation.

### M-128 — Admissibility predicate added without mutation target

Registry contains a new load-bearing predicate but mutation catalog does not target it.

Expected:
ADMISSIBILITY_PREDICATE_COVERAGE_INCOMPLETE.

### M-129 — Mutation target exists without independent killing fixture

Expected:
ADMISSIBILITY_PREDICATE_COVERAGE_INCOMPLETE.

### M-130 — Verdict result omits one registry predicate

Expected:
predicate-set closure mismatch; verdict inadmissible.

### M-131 — Statistical independence unproven but profile claims probability-qualified

Provider-side route/correlation independence cannot be evidenced, yet the profile sets statistical_qualified=true under a policy requiring the 0.99 probability claim.

Expected:
profile invalid. Only a transition policy that explicitly waives the probability claim and requires deterministic per-attempt proof may proceed.

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
- accepting retrieval/open logs without returned-content and final-context binding;
- treating hidden unexposed provider state as observed-clean without ProviderContextIsolationPolicy;
- permitting dedicated-account hidden-state residual when transition policy says DISALLOW;
- contaminating production account during sentinel qualification;
- renewing an expired capability profile from a health check;
- auto-merging incomparable governing semantics;
- weakening typed base/head comparator direction;
- excluding witness challenge/response overhead from final-context budgeting;
- allowing evaluative witness prompts;
- omitting/staling WitnessProtocolQualificationRecord;
- accepting candidate-authored witness qualification;
- ignoring provider-isolation documentation/account-class/config-template drift;
- dropping a planned failed/missing confirmation slot;
- replacing a failed confirmation attempt with a successful retry;
- accepting unreconciled qualification calls or candidate-accessible qualification credentials;
- hiding a failed physical provider attempt behind implicit SDK retry;
- adding/removing an admissibility predicate without exact mutation/fixture closure;
- marking a profile statistically qualified when independence is unproven and policy requires the probability claim.

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
- `HiddenUnexposedProviderStateAdapter`
- `ProductionAccountSentinelContaminationAdapter`
- `HealthCheckRenewalAdapter`
- `GovernanceComparatorWeakeningAdapter`
- `WitnessContextEvictionAdapter`
- `EvaluativeWitnessAdapter`
- `WitnessEvidenceLeakAdapter`
- `CandidateWitnessQualificationAdapter`
- `ProviderIsolationTemplateDriftAdapter`
- `QualificationPlanTamperAdapter`
- `FailedTrialReplacementAdapter`
- `UnreconciledQualificationCallAdapter`
- `ImplicitSdkRetryAdapter`
- `AdmissibilityPredicateDriftAdapter`

Live API pilots come only after deterministic adapters and validator-logic mutation tests prove the governor behavior.

## Live provider pilots

Live pilots begin only after all deterministic phases and validator-logic mutation tests are green.

For each exact provider/account/endpoint/region/model/deployment/adapter/session/file/retrieval mode, preregister exploration and confirmation separately.

Exploration identifies candidate operating points and observed failure boundaries. Confirmation then tests each claimed operating point itself using the frozen default or stricter risk budget:

- 299/299 required successful confirmation trials by default;
- zero hard failures;
- no exclusions/rerolls/optional stopping;
- trials distributed over the preregistered multi-day/time-block schedule;
- fresh ProviderContextIsolationPolicy-qualified context and fresh content-bound witnesses every trial;
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
42. model-selected retrieval proves returned-byte identity and final-context tool-result binding;
43. ProviderContextIsolationPolicy explicitly governs hidden provider-internal mutable-state residuals and highest-authority transitions fail closed by default;
44. sentinel qualification cannot contaminate the production review account;
45. health checks cannot renew or extend an expired capability profile;
46. every base/head “stricter” comparison uses a typed governed partial order and incomparable changes fail unresolved;
47. witness challenge/response traffic is part of the qualified cumulative context and cannot evict required evidence before adjudication;
48. witness protocols are non-evaluative, structurally isolated from semantic evidence/authority, and have a current provider/mode-bound WitnessProtocolQualificationRecord;
49. witness qualification authority is outside candidate write control;
50. provider isolation documentation/account-class/config-template drift invalidates the associated context-isolation qualification;
51. confirmation attempt membership is frozen before exposure and every planned slot is reconciled or counted failed;
52. qualification credentials/runner are outside candidate and ordinary operator control, and unreconciled calls cannot manufacture a passing sample;
53. implicit SDK/client retries are disabled or every physical attempt is independently recorded;
54. AdmissibilityPredicateRegistry, verdict predicates, logic-mutation targets and killed mutations have exact set closure.

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

Git blob: `15b2b2ceb212fc40d144790b0f68674b26a55013`

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
| TM-T11 | Statistical independence unproven but profile claims CP probability-qualified under policy requiring it | Profile invalid |
| TM-T12 | Independence unproven; transition policy explicitly waives probability claim and requires deterministic per-attempt proof | No CP probability claim; eligibility depends on deterministic proof and all other gates |

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


---

# INLINE SOURCE: governance-runtime/LIVE-CONVERSATION-GOVERNANCE.md

Git blob: `b749547a0ca7c294139c7f056ca2000a7badcb47`

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
- `EVIDENCE_MATERIALIZATION_FAILED`
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
- `INSUFFICIENT_EVIDENCE_CAUSE_UNRESOLVED`
- `MIXED_INSUFFICIENCY`
- `REVIEW_CONTEXT_DIRTY_OR_UNBOUND`
- `PROVIDER_SEMANTIC_CONTEXT_UNQUALIFIED`
- `PROVIDER_CAPABILITY_STATISTICAL_POLICY_FAILED`
- `QUALIFICATION_ATTEMPT_CLOSURE_UNPROVEN`
- `ACCESSIBILITY_PROBE_COVERAGE_INSUFFICIENT`
- `WITNESS_PROTOCOL_UNQUALIFIED`
- `WITNESS_CONTEXT_EVICTION`
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
- `EVIDENCE_FILE_REFERENCE_UNQUALIFIED`
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
17. Validate a current ProviderCapabilityProfile and its ProviderQualificationExecutionPlan/attempt-closure evidence, transition-class ProviderAccessibilityRiskPolicy, ProviderContextIsolationPolicy, machine-checkable PromptIsolationQualificationRecord, and—when witnesses are used—a current WitnessProtocolQualificationRecord for the exact production operating point. If the policy requires a statistical probability claim, `statistical_qualified=true` additionally requires evidenced trial-independence/correlation control; `STATISTICAL_INDEPENDENCE_UNPROVEN` cannot satisfy that predicate.
18. Create a fresh provider review context, capture ProviderContextStateEvidence for every observable channel, apply the selected context-isolation basis, record any permitted hidden-provider-state residual, and establish a readable monotonic provider configuration version or AdmissionFenceRecord for every observable load-bearing mutable channel.
19. Freeze the EvidenceDeliveryManifest and monotonic authority/capability/egress/context/prompt-isolation state versions.
20. Before each provider call, re-read/compare context/config state and serialize only frozen representation bytes.
21. Record both platform request hash and post-SDK transport-bound semantic envelope hash; implicit SDK/client retries must be disabled or each physical attempt must receive its own immutable WireDeliveryRecord.
22. Deliver through the qualified inline/chunk/file/retrieval mechanism.
23. Establish per-attempt accessibility using mandatory content-bound slice witnesses or deterministic full-range retrieval/access logs, according to delivery mode. When witnesses are used, include challenge/response overhead in cumulative context and recheck actual context size immediately before semantic adjudication.
24. Validate ReviewRequest + ReviewEvidence + semantic coverage + authenticated execution envelope + delivery/context completeness.
25. If the reviewer reports insufficiency, evaluate all independent cause predicates and return MIXED when multiple causes hold.
26. Immediately before authority admission, re-read all monotonic state versions/hashes, accessibility-risk-policy state, context-isolation-policy state, witness-protocol qualification state where used, AdmissibilityPredicateRegistry version, AdmissionFenceRecord, and every load-bearing admissibility predicate; require exact registry/result/mutation-coverage predicate closure.
27. Atomically compare-and-set the authoritative checkpoint together with VerdictAdmissibilityResult only if every state/version remains unchanged since its required observation.
28. Any expiry, revocation, drift, dirty-context event, file/session invalidation, or prompt-isolation invalidation from first dispatch through step 27 permanently voids that attempt; later requalification cannot revive the old response.
29. Synchronize shared memory only after authoritative persistence.
30. New chat resumes from shared memory then verifies Git.

## Current collaboration limitation

This chat can ingest pasted external evidence, but pasted content is not a platform review execution. Therefore it cannot satisfy a mandatory provider-authenticated PR #5 review gate. In the production platform, both AUTO_MODE and MANUAL_MODE avoid this limitation by using trusted provider API adapters (`AUTOMATIC_API` / `USER_INITIATED_API`).


---

# INLINE SOURCE: experiments/governed-platform/EXP-M-R4-EXTERNAL-REVIEW.md

Git blob: `96faf86db6677402d7184767ca1805b419ca9d12`

**Overall disposition:** **`CHANGES_REQUIRED`**

I reviewed the R4 packet as inline source only. I did not have repository access, so I did not independently verify the commit/tree/blob hashes and treated the inline text as faithful. The R3 repairs are substantial and many findings are design-closed, but several load-bearing gaps remain, including one High provider-context residual and one High test/mutation-sufficiency gap.

---

## A. R3 finding closure

| R3 ID | Status | Exact current-source evidence | Remaining false-green path | Narrow fix if not CLOSED |
|---|---|---|---|---|
| R3-C01 | **CLOSED** | `GovernanceAuthoritySnapshot`; base/head conservative union/stricter merge; same-ID + hash semantics; unknown/empty/vacuous contract fails `EVIDENCE_SELECTION_CONTRACT_UNRESOLVED`; registries/pointer outside candidate write set; tests M-83..M-85, TM-P01..TM-P03, TM-N01..TM-N03. | None material at design level, provided the external authority snapshot/pointer is actually outside candidate write authority. The undefined “platform-defined partial order” is a residual implementation risk, not a direct narrowing path because incomparable must fail closed. | Define per-element partial-order/comparison rules for “stricter” representation, semantics, statistical, risk, and review constraints. |
| R3-H01 | **PARTIAL** | `ProviderContextStateEvidence`; fresh stateless/trusted-adapter session; transcript/prompt/tool/memory/connector/file/deployment/config binding; checks at preflight, pre-dispatch, admission; `AdmissionFenceRecord`; sentinel tests; lying-readback and hidden-dirty-state adapters. | Provider-internal mutable semantic state that is not exposed by the provider API and not covered by behavioral sentinels can still influence review output while the platform records a clean context. The design says “unknown mutable semantic context is never tolerated,” but it cannot detect unknown hidden mutable state. | Record an explicit nonclaim/residual for hidden provider-internal mutable state not exposed by the provider API; require material review only on a dedicated platform-owned account/project whose mutable semantic features are disabled by provider policy and behaviorally requalified; or require a provider-exposed complete mutable-state inventory and fence. Add an adversarial adapter that simulates hidden unexposed mutable state. |
| R3-H02 | **CLOSED** | `p_min=0.99`; one-sided 95% exact Clopper–Pearson; 299/299 zero-failure minimum; all attempts counted; no rerolls/exclusions/optional stopping; exploration ≠ confirmation; ≥3 UTC days, ≥4 blocks/day; interleaved; exact operating point tested; production-equivalent envelope; append-only failures; health checks invalidate only; `STATISTICAL_INDEPENDENCE_UNPROVEN` when correlation cannot be evidenced. Tests M-74..M-76, M-90..M-93, TM-N11..TM-N17, TM-P08..TM-P11, TM-Q11. | Independence remains conditional, but the design explicitly bounds it and makes per-attempt accessibility proof mandatory when deterministic proof is unavailable. | Minor: add explicit test that a health check cannot renew an expired profile. |
| R3-H03 | **CLOSED** | Per-attempt content-bound witnesses mandatory when deterministic range/retrieval proof unavailable; slices ≤ min(2048 UTF-8 bytes, 512 provider tokens); every slice challenged every confirmation trial; production attempt same session; framing canaries supplemental; selective/sub-slice loss nonclaim; `ProviderAccessibilityRiskPolicy`; highest authority class deterministic proof; opaque modalities separate. Tests M-46, M-94, M-95, TM-N18..TM-N21, TM-P12..TM-P13. | None material at design level. | None required for closure. |
| R3-H04 | **CLOSED** | Model-selected retrieval requires unconditional deterministic per-attempt access logs: source/version, range/page/member, returned-content hash/length, time, tool/result identity, final-context binding. “File opened,” file ID, citation insufficient. Tests M-96..M-98, M-108, M-109, TM-N22, TM-N29, TM-Q12, TM-Q13. | None material at design level. | None required for closure. |
| R3-H05 | **PARTIAL** | Matrix IDs namespaced `TM-`; Phase G unified mutation catalog; phases A–Q required; many validator-logic mutations; adversarial adapters added. | The validator-logic mutation list does not delete/weaken every `VerdictAdmissibilityResult` conjunct one at a time. Missing targeted logic mutations include egress authorization, wire binding, session/file/retrieval coverage, complete materialization, governed representation/transformation, semantic review coverage, reviewer provenance, and promotable disposition. | Add one targeted `TM-O` logic mutation for each remaining admissibility conjunct, with an independently killed expected result. |
| R3-M01 | **CLOSED** | Atomic final compare-and-set admission; all state versions/hashes re-read at admission; any invalidation from first dispatch through admission permanently voids attempt; later requalification cannot revive. Tests M-81, M-82, M-98, TM-N25..TM-N27, TM-P16..TM-P17, TM-O21..TM-O22. | None material at design level. | None required for closure. |
| R3-M02 | **CLOSED** | `RequiredInteractionContract` derived from authority snapshot; each interaction is explicit raw evidence refs/representations that must coexist in one qualified context; aggregator must inspect raw set, not summaries. Tests M-80, TM-N23..TM-N24, TM-O17..TM-O18. | None material at design level. | None required for closure. |
| R3-M03 | **CLOSED** | Load-bearing provider deployment/retrieval/context facts mandatory when needed; missing required identity/logs/context makes mode not qualified rather than silently optional. | None material at design level. | None required for closure. |
| R3-M04 | **CLOSED** | `VerdictAdmissibilityResult` enumerates authority snapshot, evidence contract, interaction contract, materialization, transformation, egress, statistical capability, accessibility-risk policy, provider context, admission fence, wire binding, per-attempt accessibility, retrieval/session/file coverage, prompt isolation, semantic coverage, provenance, disposition. | None material at design level. | None required for closure. |
| R3-M05 | **PARTIAL** | Standard evaluates causes independently; multiple true causes → `MIXED_INSUFFICIENCY`; unresolved → `INSUFFICIENT_EVIDENCE_CAUSE_UNRESOLVED`; added `REVIEWER_EVIDENCE_ASSESSMENT_CONTRADICTION` in standard. | The live governance failure taxonomy still omits critical codes: `EVIDENCE_SELECTION_CONTRACT_UNRESOLVED`, `GOVERNANCE_AUTHORITY_SNAPSHOT_MISMATCH`, `REVIEWER_EVIDENCE_ASSESSMENT_CONTRADICTION`, `PROVIDER_CONTEXT_STATE_UNPROVEN`, `PROVIDER_CONTEXT_STATE_DRIFT`, `PROVIDER_RETRIEVAL_COVERAGE_UNPROVEN`, `PROVIDER_RETRIEVAL_CONTEXT_BINDING_UNPROVEN`, `STATISTICAL_INDEPENDENCE_UNPROVEN`, `VERDICT_ADMISSION_STATE_CHANGED`, `INSUFFICIENT_EVIDENCE_CAUSE_UNRESOLVED`, `MIXED_INSUFFICIENCY`. | Add all missing codes to `LIVE-CONVERSATION-GOVERNANCE.md` failure taxonomy and reconcile with the standard and test matrix. |
| R3-L01 | **CLOSED** | Live procedure now resolves authority snapshot/contracts before materialization; pre-dispatch revalidation explicit. | None material at design level. | None required for closure. |
| R3-L02 | **CLOSED** | `WireDeliveryRecord` includes pre-SDK platform request hash and post-SDK transport-bound semantic envelope hash; if SDK hides load-bearing semantic field, adapter/mode cannot claim exact wire binding. | None material at design level. | None required for closure. |
| R3-L03 | **CLOSED** | Governor deterministically selects machine-checkable, hash-bound, non-expired `PromptIsolationQualificationRecord` for exact provider/representation mode; checked at preflight and atomic admission. | None material at design level. | None required for closure. |

---

## B. Newly discovered findings

### High

**R4-H01 — Hidden unexposed mutable provider semantic state can still escape `ProviderContextStateEvidence`**

- **Severity:** High
- **Affected rule/invariant/test:** M-I37, M-I40, M-I43; standard “Clean material-review context and delivery session binding”; tests TM-P04, TM-P05, TM-N07..TM-N10.
- **Concrete false-green path:** A provider has an undocumented mutable memory/instruction/connector state that is not exposed by its API and is not triggered by the chosen behavioral sentinels. The platform cannot read it, disable it, or fence it. `ProviderContextStateEvidence` appears clean; admission proceeds; the review verdict is treated as material.
- **Why current design is insufficient:** The design requires behavioral sentinel qualification for “every mutable semantic channel available to the provider mode” and says “unknown mutable semantic context is never tolerated.” But if the channel is hidden from the provider API and not discovered by sentinels, the platform cannot know it is unknown. The design does not record this as a residual nonclaim or force a dedicated account with all mutable features disabled by provider policy.
- **Narrow required correction:** Add an explicit nonclaim/residual for hidden provider-internal mutable semantic state not exposed by the provider API. For material review, require either (a) a provider-exposed complete mutable-state inventory plus readable monotonic version/fence, or (b) a dedicated platform-owned account/project whose mutable semantic features are disabled by provider policy and behaviorally requalified. Add an adversarial adapter that simulates hidden unexposed mutable state.

**R4-H02 — Validator-logic mutation coverage does not delete/weaken every admissibility conjunct**

- **Severity:** High
- **Affected rule/invariant/test:** Phase O; exit criteria “every admissibility conjunct is independently falsified”; standard mutation suite “delete each `VerdictAdmissibilityResult` conjunct one at a time”; R3-H05 closure.
- **Concrete false-green path:** A validator implementation omits or weakens an admissibility predicate not covered by a targeted logic mutation, such as egress authorization, wire binding, session/file/retrieval coverage, complete materialization, governed representation/transformation, semantic review coverage, reviewer provenance, or promotable disposition. No Phase O mutation kills that omission, so a false-green verdict could be admitted.
- **Why current design is insufficient:** Phase O lists many logic mutations but not one for every enumerated `VerdictAdmissibilityResult` conjunct. Data/state negative tests may catch some omissions, but the exit criteria and standard require targeted predicate deletion/weakening mutation coverage.
- **Narrow required correction:** Add one targeted `TM-O` logic mutation for each remaining admissibility conjunct, with an independently killed expected result.

### Medium/Low

**R4-M01 — Live governance failure taxonomy still omits critical EXP-M codes**

- **Severity:** Medium
- **Affected rule/invariant/test:** R3-M05; standard failure taxonomy; live procedure step 25; tests TM-D07..TM-D09, TM-P22.
- **Concrete false-green path:** Runtime returns `EVIDENCE_SELECTION_CONTRACT_UNRESOLVED` or `MIXED_INSUFFICIENCY`, but the live taxonomy does not preserve the code. The cause may be collapsed into a generic or first-match failure, weakening the independent-cause adjudication requirement.
- **Why current design is insufficient:** The standard defines the codes, but `LIVE-CONVERSATION-GOVERNANCE.md` does not list them in its failure taxonomy.
- **Narrow required correction:** Add all missing codes to the live taxonomy and reconcile with the standard and test matrix.

**R4-M02 — “Stricter” base/head merge lacks a defined partial order**

- **Severity:** Medium
- **Affected rule/invariant/test:** M-I42; standard “Delivery-governor trust root”; R3-C01 remediation.
- **Concrete false-green path:** If the platform-defined partial order is not actually specified per governing element class, an implementation may treat incomparable representation/semantic/risk changes as comparable and silently accept a weakening. Alternatively, it may fail closed so often that legitimate changes are impossible.
- **Why current design is insufficient:** The standard requires “the stricter base/head requirement” and says incomparable conflicts fail unresolved, but it does not define the comparison operator for each governing element type.
- **Narrow required correction:** Specify per-element partial-order/comparison rules, or require independent authority approval for any same-dimension semantic change rather than attempting automatic merge.

**R4-L01 — Health-check renewal prohibition lacks a targeted test**

- **Severity:** Low
- **Affected rule/invariant/test:** M-I38; Phase F.
- **Concrete false-green path:** A health check could be implemented to renew an expired profile despite the rule that health checks may invalidate but never renew.
- **Why current design is insufficient:** The design states the rule, but no test explicitly attempts health-check renewal.
- **Narrow required correction:** Add a test that an expired profile cannot be renewed by a health check and requires requalification.

---

## C. Gate verdicts

| Gate | Verdict |
|---|---|
| REQUIRED_EVIDENCE_AUTHORITY | **PASS** |
| DELIVERY_GOVERNOR_TRUST_ROOT | **PASS** |
| GOVERNANCE_AUTHORITY_SNAPSHOT | **PASS** |
| CLEAN_SESSION_CONTEXT | **FAIL** |
| PROVIDER_SEMANTIC_CONTEXT_BINDING | **FAIL** |
| PROVIDER_CONTEXT_ADMISSION_FENCE | **FAIL** |
| WIRE_BINDING | **PASS** |
| CHUNK_CONTEXT_MODEL | **PASS** |
| REMOTE_ACCESSIBILITY_MODEL | **PASS** |
| PROVIDER_ACCESSIBILITY_RISK_POLICY | **PASS** |
| PROVIDER_CAPABILITY_QUALIFICATION | **PASS** |
| STATISTICAL_PROTOCOL | **PASS** |
| REPRESENTATION_GOVERNANCE | **PASS** |
| MATERIALIZATION_SAFETY | **PASS** |
| EGRESS_BOUNDARY | **PASS** |
| SESSION_FILE_RETRIEVAL_BINDING | **PASS** |
| RETRIEVAL_FINAL_CONTEXT_BINDING | **PASS** |
| INSUFFICIENT_EVIDENCE_TAXONOMY | **FAIL** |
| MULTI_REVIEWER_EQUIVALENCE | **PASS** |
| DECOMPOSITION_AGGREGATION | **PASS** |
| PROMPT_ISOLATION_DEPENDENCY | **PASS** |
| TOCTOU_RETRY_INTEGRITY | **FAIL** |
| ATOMIC_VERDICT_ADMISSION | **FAIL** |
| REVIEWER_TOOL_EVIDENCE_BOUNDARY | **PASS** |
| TEST_MATRIX_SUFFICIENCY | **FAIL** |
| VALIDATOR_LOGIC_MUTATION_COVERAGE | **FAIL** |

The CLEAN_SESSION_CONTEXT, PROVIDER_SEMANTIC_CONTEXT_BINDING, PROVIDER_CONTEXT_ADMISSION_FENCE, TOCTOU_RETRY_INTEGRITY, and ATOMIC_VERDICT_ADMISSION failures all stem primarily from R4-H01: hidden unexposed mutable provider state can change without a readable version/fence and without being covered by sentinels.

---

## D. Statistical protocol adjudication

- **299/299 exact minimum:** Yes. For zero failures, the one-sided 95% exact Clopper–Pearson lower bound is `0.05^(1/n)`. `0.05^(1/299) >= 0.99`, while `0.05^(1/298) < 0.99`. 299 is the exact minimum.
- **Independence/correlation nonclaim:** Honest enough at design level. The design records `STATISTICAL_INDEPENDENCE_UNPROVEN` when provider-side correlation/route allocation cannot be observed and refuses to present the bound as a universal provider failure probability. It also requires per-attempt accessibility proof when deterministic proof is unavailable.
- **3-day/4-time-block schedule and interleaving:** Falsifiable in principle. Tests M-90, TM-P08, TM-P11, and TM-Q11 cover burst, schedule, production-envelope, and correlated-route attacks. Minor gap: no explicit test that health checks cannot renew.
- **Every attempted trial forced into append-only ledger:** Yes at design level. Rules say all attempts count; no exclusions/rerolls/optional stopping; failed attempts preserved. Tests M-91, TM-P09, TM-O09, TM-N13..TM-N14.
- **Exploration/confirmation separation:** Yes. Disjoint families, frozen confirmation IDs/schedule, exploration never reused. Tests M-92, TM-P10, TM-O10.
- **Production-envelope equivalence:** Defined via the operating-point tuple and explicit production-equivalent prompt/tools/structured-output/output budget and worst-case token-density/media classes. Tests M-93, TM-P11, TM-O12.
- **80% margin:** Correctly supplemental. No monotonicity is inferred; the claimed point itself must be tested. If a failure boundary is observed, cap ≤80% of smallest observed failing boundary; if none, cap ≤80% of largest independently confirmed passing point.
- **Profile expiry/drift:** 7-day default, immediate on material provider/model/deployment/account/endpoint/region/adapter/session/file-processing drift; health checks invalidate only, never renew. Minor gap: add explicit health-check-renewal test.

---

## E. Accessibility and retrieval adjudication

- **Max slice ≤ min(2048 UTF-8 bytes, 512 provider tokens):** Yes, explicitly stated.
- **Every slice challenged every confirmation trial:** Yes, for qualification trials when deterministic range/retrieval proof is unavailable.
- **Per-attempt content-bound challenge in final adjudication session:** Yes, mandatory for production material-review attempts using modes without deterministic range/retrieval proof.
- **Framing canaries only supplemental:** Yes. Content-bound challenges are load-bearing; framing/end sentinels cannot substitute.
- **Selective/sub-slice loss recorded as nonclaim/residual:** Yes. The failure model is explicitly bounded to contiguous loss/eviction at or above slice granularity; arbitrary selective/sub-slice loss remains a nonclaim/residual.
- **ProviderAccessibilityRiskPolicy chooses whether residual acceptable:** Yes. Every protected transition class has a policy; unknown policy fails closed; highest material-authority class requires deterministic full-range/page/member proof or equivalently observable inline mode.
- **Highest material-authority transition requires deterministic proof:** Yes.
- **Opaque media/modalities cannot inherit text qualification:** Yes. Scans, tables, images, embedded objects, archives are separate media/modality classes; synthetic text-layer PDFs cannot qualify them.
- **Model-selected retrieval requires returned-byte hash/range/version plus tool-result binding into final context:** Yes. Unconditional for material review; “file opened,” file ID, or citation alone is insufficient.

---

## F. Authority and atomic-admission adjudication

Attempted breaks:

- **Authority snapshot pointer:** Design places pointer/registries outside candidate write set. No direct candidate narrowing path at design level.
- **Base/head conservative merge:** Deletions/weakenings under same ID are treated as changed inputs; union/stricter merge preserves base requirements; incomparable conflicts must fail unresolved.
- **Same-ID semantic mutation:** Stable-ID + content-hash binding prevents silent in-place replacement.
- **Unknown/empty contract:** Fails `EVIDENCE_SELECTION_CONTRACT_UNRESOLVED`; non-vacuity baselines required.
- **Relationship registry:** `RequiredInteractionContract` derived only from authority snapshot registry, not proposer metadata.
- **Risk policy registry:** Missing `ProviderAccessibilityRiskPolicy` fails closed.
- **Provider context state:** Known mutable channels must be readable/disable-able or mode is `NOT_QUALIFIED`; sentinel qualification required.
- **Provider admission fence:** Required for every load-bearing mutable provider/account/project/session configuration channel; readable monotonic version or platform-enforceable fence; otherwise mode not qualified.
- **Prompt-isolation qualification:** Deterministically selected, hash-bound, non-expired, checked at preflight and admission.
- **Atomic compare-and-set checkpoint:** Defined as final authority operation; all versions/hashes re-read and compared; any invalidation from first dispatch through admission permanently voids the attempt.
- **Can later requalification revive an old invalidated response?** No. The design explicitly forbids revival; only a new delivery attempt may proceed.

**Remaining break:** R4-H01. Hidden unexposed mutable provider state is not covered by a readable version/fence or sentinel, so it can change without detection and without voiding the attempt. This defeats the intended TOCTOU/atomic-admission guarantee for that hidden channel.

---

## G. Test-plan adjudication

- **Test IDs no longer collide:** Yes. Matrix uses `TM-` namespace; frozen experiment tests use `M-`.
- **Unified mutation catalog:** Yes. Phase G is the single authoritative mutation catalog.
- **All deterministic phases A–Q gated:** Yes. Exit criteria require all deterministic phases A–Q.
- **Logic mutations attack code predicates, not only data:** Partially. Phase O includes many predicate-level mutations, but it does not delete/weaken every `VerdictAdmissibilityResult` conjunct. See R4-H02.
- **Lying readback, hidden state, correlated burst, failed-trial replay, canary-preserving content loss, missing retrieval log, atomic-admission race have adversarial oracles:** Mostly yes. Adapters/adapters are listed and tests exist.
- **`REVIEWER_EVIDENCE_ASSESSMENT_CONTRADICTION`, `EVIDENCE_SELECTION_CONTRACT_UNRESOLVED`, provider-context/retrieval/admission codes defined consistently:** No. The standard defines them, but the live governance failure taxonomy is missing many of them. See R4-M01.

---

## H. Final determination

- **Any Critical design defect remains:** No new Critical beyond R3-C01, which is design-closed.
- **Any High design defect remains:** Yes. R4-H01 (hidden unexposed mutable provider state) and R4-H02 (incomplete validator-logic mutation coverage).
- **Is EXP-M ready for deterministic implementation/falsification?** Not yet as reviewed. The remaining High defects should be repaired at design/preregistration level first to avoid burning first exposure.
- **May live provider pilots begin?** No.
- **Exact remaining prerequisites:**
  1. Add explicit nonclaim/residual and dedicated-account/full-inventory requirement for hidden unexposed mutable provider semantic state (R4-H01).
  2. Add targeted validator-logic mutations for every remaining `VerdictAdmissibilityResult` conjunct (R4-H02).
  3. Reconcile live governance failure taxonomy with the standard and test matrix (R4-M01).
  4. Define per-element “stricter” partial-order/comparison rules or require independent authority approval for same-dimension semantic changes (R4-M02).
  5. Add explicit health-check-cannot-renew test (R4-L01).
  6. Keep all deterministic phases A–Q green before any live pilot.
- **EXP-M remains `NOT_QUALIFIED`.**
- **This external/manual review itself grants no platform review or promotion authority.**

---

# INLINE SOURCE: experiments/governed-platform/EXP-M-R4-REVIEW-REMEDIATION.md

Git blob: `07f3fc3a11aedefdb6ab84367049cba311616b81`

# EXP-M R4 External Review Adjudication and Remediation

## Status

`R4_CHANGES_REQUIRED_ACCEPTED_AND_REMEDIATED_FOR_R5_REVIEW`

The supplied R4 external review is accepted as valid defect evidence. It remains external/manual review evidence only and grants no platform review, promotion, implementation, or live-provider authority.

EXP-M remains `NOT_QUALIFIED`.

## R4 disposition

R4 returned `CHANGES_REQUIRED`.

R4 design closure:
- R3-C01: CLOSED
- R3-H02: CLOSED
- R3-H03: CLOSED
- R3-H04: CLOSED
- R3-M01: CLOSED
- R3-M02: CLOSED
- R3-M03: CLOSED
- R3-M04: CLOSED
- R3-L01: CLOSED
- R3-L02: CLOSED
- R3-L03: CLOSED

R4 kept open/partial:
- R3-H01 via R4-H01
- R3-H05 via R4-H02
- R3-M05 via R4-M01

R4 additionally found:
- R4-M02 — undefined per-element “stricter” comparison;
- R4-L01 — no targeted health-check-renewal test.

## R4-H01 — hidden unexposed mutable provider semantic state

Evaluation: **VALID / HIGH**

Repair:

1. Added platform-owned `ProviderContextIsolationPolicy` selected from the GovernanceAuthoritySnapshot.
2. Defined two isolation bases:
   - `COMPLETE_READABLE_FENCED_STATE`;
   - `DEDICATED_PLATFORM_ACCOUNT_STATELESS_BOUNDARY`.
3. The dedicated-account basis requires:
   - platform-owned provider account/project/credential;
   - no candidate/end-user provider-config writes;
   - pinned provider product documentation/contract;
   - exact provider account class and production configuration-template hash;
   - exposed mutable semantic features disabled/read back;
   - disposable qualification account for sentinel tests so production review account is not contaminated;
   - production config template match and fence.
4. Hidden provider-internal mutable semantic state is now an explicit nonclaim/residual, never an “observed clean” assertion.
5. Each transition policy chooses:
   - `DISALLOW`; or
   - `DEDICATED_ACCOUNT_EXTERNAL_TRUST_BOUNDARY`.
6. Highest material-authority transition defaults to `DISALLOW`.
7. Added failure codes:
   - `PROVIDER_CONTEXT_HIDDEN_STATE_RESIDUAL`;
   - `PROVIDER_CONTEXT_ISOLATION_POLICY_MISSING`.
8. Added hidden-state, dedicated-account, sentinel-contamination, config-drift, and admission-fence tests/adapters.

## R4-H02 — incomplete validator-logic mutation coverage

Evaluation: **VALID / HIGH**

Repair:

1. Added explicit targeted Phase-O mutations for every current `VerdictAdmissibilityResult` predicate:
   - ReviewRequest;
   - authority snapshot;
   - evidence contract;
   - interaction contract;
   - materialization;
   - representation/transformation;
   - egress;
   - provider capability;
   - accessibility risk;
   - context isolation;
   - hidden-state residual policy;
   - provider context state;
   - admission fence;
   - semantic-context qualification;
   - post-SDK wire binding;
   - complete item/chunk delivery;
   - per-attempt accessibility proof;
   - witness qualification/context budget;
   - session/file/retrieval coverage;
   - prompt isolation;
   - semantic review coverage;
   - reviewer provenance/independence;
   - promotable disposition.
2. Added platform-owned `AdmissibilityPredicateRegistry`.
3. Required exact closure:

`required predicates == VerdictAdmissibilityResult predicates == logic mutation targets == independently killed mutations`

4. New predicates without a targeted negative fixture and killed logic mutation fail as `ADMISSIBILITY_PREDICATE_COVERAGE_INCOMPLETE`.
5. Candidate edits to the predicate registry used for their own review are rejected.

## R4-M01 — live taxonomy mismatch

Evaluation: **VALID / MEDIUM**

Repair:

The live-governance failure taxonomy was reconciled against the normative standard. It now includes all EXP-M standard codes, including:

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
- `INSUFFICIENT_EVIDENCE_CAUSE_UNRESOLVED`
- `MIXED_INSUFFICIENCY`
- `EVIDENCE_MATERIALIZATION_FAILED`
- `EVIDENCE_FILE_REFERENCE_UNQUALIFIED`
- witness, qualification-attempt, retry and predicate-coverage codes added during self-adjudication.

A source-vs-live taxonomy comparison after repair reports no normative standard code missing from live governance.

## R4-M02 — undefined stricter partial order

Evaluation: **VALID / MEDIUM**

Repair:

Added typed comparison rules:

- required refs/dimensions/interactions: superset stricter;
- allowed representation/provider/region/tool sets: intersection stricter;
- fidelity: raw/lossless > bounded-loss > summary, with incomparable media semantics unresolved;
- review level: REQUIRED > RECOMMENDED > NONE;
- egress: deny > conditional allow > allow; incomparable conditions unresolved;
- statistical lower-bound/confidence: larger requirement stricter;
- tolerated failure/residual risk: smaller stricter;
- minimum confirmation trials: larger stricter when acceptance semantics match;
- expiry interval: shorter stricter;
- runtime size/count limits: smaller stricter;
- accessibility proof: deterministic > probabilistic/content-bound > self-attestation;
- prompt isolation: superset of required predicates stricter;
- transition rank: only authority registry defines order.

Same-dimension semantic changes without a comparator are never auto-merged and fail `EVIDENCE_SELECTION_CONTRACT_UNRESOLVED`.

Comparator mutations are included in deterministic falsification.

## R4-L01 — health check renewal

Evaluation: **VALID / LOW**

Repair:

Added explicit tests that an expired ProviderCapabilityProfile cannot be renewed or extended by a health check. Full governed confirmation requalification is required. Health checks may invalidate only.

## Additional iterative self-adjudication

After the direct R4 repairs, additional adversarial design passes were performed.

### SA-R5-H01 — witness proof could evict evidence before final adjudication

Severity: **High**

Failure path:
witness challenges/responses prove accessibility, but their transcript consumes enough context to evict the evidence before the semantic verdict.

Repair:
- witness challenge/response overhead, wrappers, final prompt and final output budget are part of the qualified operating point;
- actual context size is rechecked after witness phase and before adjudication;
- witness-induced eviction voids the attempt;
- added `WITNESS_CONTEXT_EVICTION`.

### SA-R5-H02 — witness protocol could contaminate semantic review

Severity: **High**

Failure path:
accessibility probes themselves become evaluative evidence or alter the review authority basis.

Repair:
- `WitnessProtocolQualificationRecord` added and kept outside candidate write authority;
- witness prompts are extraction/accessibility only;
- witness outputs are tagged non-evidence/non-adjudicative and cannot satisfy semantic review dimensions;
- exact final semantic prompt remains hash-bound under prompt-isolation governance;
- EXP-M explicitly does **not** claim counterfactual semantic invariance for stochastic remote models;
- A/B outcome comparisons are diagnostic only.

### SA-R5-H03 — provider qualification sample could be cherry-picked

Severity: **High**

Failure path:
failed/skipped confirmation calls are omitted, retried until success, or unlogged calls are used selectively.

Repair:
- added frozen `ProviderQualificationExecutionPlan`;
- complete planned trial IDs/schedule/interleaving seed frozen before exposure;
- dedicated trusted qualification runner and credential/egress identity;
- candidate/user/ordinary-operator invocation prohibited;
- missing planned slot counts hard failure;
- retry cannot replace original failure;
- provider request/audit reconciliation used when exposed;
- where provider audit logs are absent, qualification credential/egress must be technically exclusive to trusted runner;
- unexplained calls invalidate the epoch or yield `QUALIFICATION_ATTEMPT_CLOSURE_UNPROVEN`.

### SA-R5-H04 — implicit SDK retries could hide first failures

Severity: **High**

Failure path:
a physical request fails, SDK silently retries, and platform records only one success.

Repair:
- implicit client/SDK retries disabled by default;
- otherwise every physical attempt requires its own immutable WireDeliveryRecord/qualification record;
- hidden retry produces `IMPLICIT_RETRY_UNOBSERVED`;
- added deterministic retry adapters/tests.

### SA-R5-H05 — explicit predicate list could drift again

Severity: **High**

Failure path:
a future admissibility predicate is added without a matching targeted logic mutation.

Repair:
- added machine-readable `AdmissibilityPredicateRegistry`;
- exact set closure between required predicates, verdict-result predicates, mutation targets and killed mutations;
- registry drift after preflight is admission-invalidating;
- candidate cannot edit the authoritative registry used for own review.

### SA-R5-M01 — statistical independence could be overclaimed

Severity: **Medium**

Repair:
- Clopper–Pearson probability claim is explicitly conditional on evidenced trial-independence/correlation control;
- `STATISTICAL_INDEPENDENCE_UNPROVEN` forbids `statistical_qualified=true` when the transition policy requires the probability claim;
- only a policy that explicitly waives that probability claim and requires deterministic per-attempt proof may proceed without it.

### SA-R5-M02 — witness qualification authority could self-grant

Severity: **Medium**

Repair:
- WitnessProtocolQualificationRecord and registry are platform-owned/outside candidate write authority;
- provider/prompt-isolation/witness-protocol drift invalidates the record;
- candidate-authored witness qualification is rejected.

## Current deterministic preregistration scope

The test matrix now gates deterministic phases **A–T** before any live provider pilot.

The design requires:

- all A–T deterministic phases green;
- zero data/state mutation survivors;
- zero validator-logic mutation survivors;
- exact admissibility predicate/mutation set closure;
- qualification-attempt set closure;
- retry transparency;
- provider-context isolation policy closure;
- witness context-budget and structural-isolation closure;
- atomic final admission;
- no live-provider pilot before deterministic qualification.

## Fresh self-adjudication result

A fresh adversarial pass after the above repairs found:

- open Critical design findings: **0**
- open High design findings: **0**

Residual limitations are explicit rather than silently promoted:

- remote model cognition/attention is not proved;
- hidden provider-internal state is either disallowed or an independently governed external-trust residual;
- provider telemetry remains provider-originated evidence;
- statistical probability claims are conditional on the stated independence model;
- selective sub-slice loss is outside probabilistic witness guarantees unless deterministic proof is required by policy;
- EXP-M is still only design/preregistration;
- no deterministic implementation has run;
- no provider mode is live-qualified.

This is proposer/model self-review only and has no independent authority.

## R5 handoff

`READY_FOR_R5_INDEPENDENT_DESIGN_REVIEW`

EXP-M remains `NOT_QUALIFIED`.

No live provider pilot may begin from this record.
