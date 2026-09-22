# Independent Holistic Governance Rules Review Packet

Review packet status: REVIEW_ONLY / NON_AUTHORITATIVE
Authority effect: NONE

## Frozen review scope

This packet asks for one independent adversarial review of the platform governance rules as a coherent system.

Authoritative baseline commit:
- main: 87f6e3df73c0c70c5d8ff4da38365ff92721aff7

Pending proposed governance inputs included for cross-rule analysis but NOT treated as authoritative:
- PR #39 head: 1029e8a7883abc30975a6bff908f43cf9192dab5
- PR #40 head: 513bb3304a14f42e0c1a67bb6a408c339a0f4463

The reviewer must keep authoritative and proposed rules distinct. A proposal may be criticized for conflicts with current rules, but it must not be treated as already active.

## Review objective

Assume the governance can still produce false-green, self-granted authority, inconsistent policy composition, provenance substitution, stale-state promotion, reviewer contamination, or unauthorized terminal effect.

Do not review this as prose quality. Review it as an authority/control system.

Attack at least these dimensions:

1. Rule hierarchy and precedence: contradictions, circular precedence, undefined tie-breaks, silent weakening.
2. Authority separation: proposer, reviewer, governor, policy author, project owner, user, worker, and terminal actor boundaries.
3. Independent review: self-review, reviewer contamination, replay, stale review, wrong revision, negative-review promotion, reviewer identity provenance.
4. Evidence/provenance: content establishing its own provenance, fabricated evidence, missing evidence, evidence substitution, source identity drift.
5. Fail-closed behavior: missing state, unavailable verifier, unavailable reviewer, stale memory, conflicting checkpoints, broken telemetry.
6. Continuity/resumption: chat/session/device changes, stale summaries, handoff ambiguity, policy-version drift, partial work.
7. Policy composition: whether user/project rules can silently weaken platform invariants, override ambiguity, snapshot rebinding, policy migration.
8. Terminal/side-effect authority: whether non-terminal actors can mint or replay merge/release/deploy/external-side-effect authority.
9. Historical integrity: deletion or rewriting of failures, retractions, prior contrary evidence, superseded reviews.
10. Review transport and external packets: whether manual/external review can be mistaken for platform-authenticated review, and whether portable packets preserve independence.
11. Determinism and semantic gaps: rules that rely on labels, free text, model judgment, or caller-controlled classification instead of enforceable predicates.
12. Missing governance: identify material authority transitions or state changes that have no explicit governing rule.
13. Over-governance/deadlock: identify rules that are mutually impossible, permanently blocking, or create authority cycles without a lawful resolution path.
14. Recovery/disaster paths: identify whether emergency recovery, revocation, migration, credential loss, or unavailable authoritative stores create an ad hoc bypass.
15. User-configurable governance: verify lower-level customization can only strengthen/specialize non-overridable platform invariants.

## Reviewer constraints

- Do not assume any PASS label, contract title, or "mandatory" wording is enforced.
- Distinguish design defects from implementation/runtime evidence you cannot inspect.
- Do not invent Git/runtime verification if you do not have it.
- Do not use prior reviewer findings or our internal conclusions as authority.
- Do not grant qualification, release, production, merge, deploy, or terminal authority.
- Treat proposed PR #39/#40 rules as proposals only.
- If two rules conflict, quote both and explain the actual authority consequence.
- Prefer concrete exploit/false-green paths over stylistic criticism.

## Required output

A. Overall disposition: BOUNDED_PASS, CHANGES_REQUIRED, or INSUFFICIENT_EVIDENCE.

B. Critical findings.

C. High findings.

D. Medium findings.

E. Cross-rule contradictions and ambiguity.

F. Missing governance rules / uncovered authority transitions.

G. Over-governance, deadlock, or impossible-closure risks.

H. Review of the proposed continuity/manual-review rules (PR #39): ACCEPTABLE_AS_PROPOSED, CHANGES_REQUIRED, or INSUFFICIENT_EVIDENCE, with reasons.

I. Review of the proposed project-policy composition rule (PR #40): ACCEPTABLE_AS_PROPOSED, CHANGES_REQUIRED, or INSUFFICIENT_EVIDENCE, with reasons.

J. Top 10 falsification scenarios that should be added before treating the governance framework as mature.

K. Final bounded statement explicitly confirming:
- this review grants no authority;
- authoritative current rules remain distinct from proposed rules;
- unresolved material findings block governance promotion.

---

# Included governance sources


---

## AUTHORITATIVE: governance-runtime/LIVE-CONVERSATION-GOVERNANCE.md

Ref: 87f6e3df73c0c70c5d8ff4da38365ff92721aff7
Git blob SHA: cdba052b3baaa7250b6787bf6954ccfb5059e832

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
13. Validate ReviewRequest + ReviewEvidence + structured semantic coverage + platform API execution envelope.
14. Require a positive promotable disposition before platform review can satisfy material promotion.
15. Apply deterministic governor/evidence gate.
16. Persist authoritative checkpoint.
17. Synchronize shared memory.
18. New chat resumes from shared memory then verifies Git.

## Current collaboration limitation

This chat can ingest pasted external evidence, but pasted content is not a platform review execution. Therefore it cannot satisfy a mandatory provider-authenticated PR #5 review gate. In the production platform, both AUTO_MODE and MANUAL_MODE avoid this limitation by using trusted provider API adapters (`AUTOMATIC_API` / `USER_INITIATED_API`).



---

## AUTHORITATIVE: governance-runtime/EXECUTION-HANDOFF-PROTOCOL.md

Ref: 87f6e3df73c0c70c5d8ff4da38365ff92721aff7
Git blob SHA: 51b514c15a51528242f0c15f7c3f2d47142dcebb

# Deterministic Execution Handoff Protocol

## Problem

Conversation summaries, model memory, repository HEAD, and the last durable commit can each describe different points in a live workflow. A new chat can therefore resume from a historically valid but operationally stale point. Repository truth alone is insufficient when the last completed action and the next required action are not represented explicitly.

## Core rule

A material workflow may not rely on conversational recollection to determine where execution resumes.

The authoritative live checkpoint MUST contain an explicit `execution_handoff` object. A fresh or resumed session MUST execute from `execution_handoff.next_required_action` only after verifying its bindings against governed Git/evidence. It MUST NOT infer a different frontier from chat summaries, model memory, commit recency, or a plausible project narrative.

## Required handoff fields

The checkpoint handoff records at least:

- monotonic `sequence`;
- `workstream` identity;
- exact `candidate_branch`;
- exact `candidate_commit`;
- `phase`;
- `last_completed_action`;
- `next_required_action`;
- `stop_condition`;
- `manual_input_required`;
- `handoff_reason`;
- `historical_failure_preserved`;
- `resume_rule`.

The shared continuity memory mirrors these fields but remains non-authoritative. Any mismatch is a grounding failure, not an invitation to guess.

## Write discipline

1. Persist the material authoritative change first.
2. Verify the resulting authoritative revision/evidence.
3. Update `session-state.json` with a new monotonic handoff sequence bound to the exact current workstream candidate.
4. Update `shared-memory.json` to mirror the handoff.
5. Run deterministic validation.
6. Only then may the assistant report the new execution frontier as durable.

If step 1 fails, authoritative completion is blocked. If steps 3-5 fail after the material change has already become durable, the material authority remains what Git says, but the conversation state is `GROUNDING_REQUIRED` until the handoff is repaired. The assistant must not claim the handoff was saved when it was not.

## Resume discipline

At session/chat start:

1. Read `session-state.json`.
2. Read the authoritative handoff.
3. Verify `candidate_branch` currently resolves to `candidate_commit` when the handoff requires an unmoved candidate.
4. Verify any referenced workflow/review/evidence state.
5. Compare shared memory and current chat context to the authoritative handoff.
6. If they disagree, authoritative handoff wins and the discrepancy is surfaced/repaired.
7. Execute `next_required_action`; do not substitute a nearby task.

A generic user message such as `continue` means `continue from the verified execution_handoff.next_required_action`.

## Manual/review boundary rule

When `stop_condition` is `INDEPENDENT_REVIEW_REQUIRED` or another explicit manual boundary:

- no further authority-changing construction may continue;
- the assistant must provide the exact reviewer prompt and review packet/artifact required for that boundary in the same handoff interaction;
- the checkpoint must identify the exact candidate under review;
- after the reviewer response is received, that response is ingested according to its provenance class and the handoff advances monotonically.

The handoff must not merely say `review required`; it must specify the next operational deliverable so the user is not forced to reconstruct the protocol from prior chat history.

## Failure classes

- `HANDOFF_MISSING`
- `HANDOFF_STALE`
- `HANDOFF_CANDIDATE_MISMATCH`
- `HANDOFF_SEQUENCE_REGRESSION`
- `HANDOFF_NEXT_ACTION_AMBIGUOUS`
- `HANDOFF_MANUAL_DELIVERABLE_OMITTED`
- `CHAT_RESUME_OVERRIDES_HANDOFF`
- `MODEL_MEMORY_OVERRIDES_HANDOFF`
- `REPOSITORY_HEAD_MISTAKEN_FOR_EXECUTION_FRONTIER`
- `FALSE_HANDOFF_PERSISTENCE_ACKNOWLEDGEMENT`

## Current incident classification

The September 2026 continuation failures in which the assistant resumed from EXP-I/EXP-K or from repository HEAD while the live workflow had already advanced to Review Engine closure and then Slice 3 are classified as a real `REPOSITORY_HEAD_MISTAKEN_FOR_EXECUTION_FRONTIER` / `HANDOFF_STALE` failure family. They are preserved as governance evidence rather than treated as a conversational inconvenience.



---

## AUTHORITATIVE: governance-runtime/PROVIDER-REVIEW-TELEMETRY-CONTRACT.md

Ref: 87f6e3df73c0c70c5d8ff4da38365ff92721aff7
Git blob SHA: c431272ec7ff51dbc0e7f9c23eb27e019c2ad84e

# Provider-Neutral Review Telemetry Contract

Status: **PRE-IMPLEMENTATION FROZEN BOUNDARY**

Authoritative parent governance checkpoint: `cfc8a9c99025d3d8e0abeff87345994dcbc7384d` (`LIVE-CONV-2026-09-09-046`).
Accepted product frontier: `main` = `3a19eff0a735f702bac2807040f361b2dc7a37b6` (accepted Slice 8).

## 1. Goal

Falsify whether every governed reviewer/API attempt can emit one normalized, secret-safe telemetry record and appear automatically in provider/model/credential summaries and dashboard data without provider-specific display logic.

This change is observability only. It must not change review semantics, reviewer independence, provider qualification, retry policy, validation, adjudication, or authority.

## 2. Provider-neutral rule

Telemetry consumers MUST NOT contain branches or enumerations such as `if provider == "openrouter"`, hard-coded Gemini/Groq/OpenRouter rows, or a fixed known-provider list.

Actual provider invocation adapters may still require explicit registration/configuration. Once any adapter emits a conforming telemetry event, aggregation and dashboard rendering must include it without code changes.

A synthetic provider named `future-provider-x` is the mandatory falsification vector for this rule.

## 3. Normalized attempt event

Each provider attempt must emit a JSON object with at least:

- `schema_version`
- `event_type = REVIEW_PROVIDER_ATTEMPT`
- `review_request_id`
- `reviewed_candidate_commit`
- `reviewer_slot`
- `gateway_provider`
- `model`
- `credential_profile` — identity such as `primary` or `r3`; never a secret/key
- `requested_serving_provider` — nullable when not applicable
- `returned_serving_provider` — nullable when unavailable
- `attempt_index`
- `request_started_at`
- `provider_call_started_at`
- `first_response_at` — nullable on failures before any response
- `provider_call_completed_at`
- `provider_latency_ms`
- `attempt_outcome` — `SUCCESS` or `FAILURE`
- `retryable`
- `http_status` — nullable
- `error_classification` — nullable on success
- `error_detail` — bounded/sanitized; must not contain secrets
- `semantic_disposition` — nullable until available
- `validation_valid` — nullable until available
- `authority_effect`

Wall-clock timestamps must be UTC ISO-8601. Duration must be calculated from a monotonic clock where the runtime can do so; durations may not be derived only by subtracting wall-clock strings.

## 4. Secret safety

Telemetry must never persist or render API key values, Authorization headers, bearer tokens, repository secret contents, or raw environment-secret values. `credential_profile` identifies the configured credential slot only.

## 5. Attempt preservation

Retries are separate events. A later success may not overwrite an earlier 429/503/transport failure. For example, Slice 8 Review 001 must be representable as attempt 1 = transient 429 and attempt 2 = success.

## 6. Review-level summary

Aggregation must deterministically produce review-level fields including:

- request/candidate identity;
- provider/model/credential profile;
- attempt count;
- retry count;
- first attempt start;
- first successful response time, if any;
- final completion time;
- total elapsed latency;
- final success/failure;
- final error classification if unsuccessful;
- semantic disposition;
- validation result;
- authority effect.

## 7. Dynamic provider summary

Aggregation groups by values present in telemetry records. It must support arbitrary providers/models/credential profiles discovered at runtime.

The provider summary must expose at least:

- provider identity;
- models observed;
- credential profiles observed;
- review count;
- attempt count;
- success count;
- failure count;
- retry count;
- average successful provider latency when calculable;
- latest event time;
- latest outcome/error classification.

No provider may be omitted because it is unknown to the dashboard code.

## 8. Dashboard data contract

Dashboard publication must include a machine-readable `provider-review-telemetry.json` (or an explicitly versioned successor) containing normalized review records and dynamic provider summaries.

The UI must iterate the supplied records/groups; it may not contain provider-specific rows. A record for `future-provider-x` must render through the same generic path as any current provider.

## 9. Authority isolation

Telemetry is evidence about execution timing and transport outcome only. It cannot:

- convert a failed review to PASS;
- replace semantic validation;
- satisfy independent review by itself;
- authorize merge/release/deploy/completion;
- prove remote model identity cryptographically;
- widen a provider or model claim beyond authenticated/reported evidence.

Every telemetry artifact must use `authority_effect = NONE_PENDING_DETERMINISTIC_INGESTION` unless a separate governed authority mechanism explicitly defines otherwise.

## 10. Frozen acceptance cases

- `TEL-01` a valid arbitrary provider event round-trips through normalized validation.
- `TEL-02` `future-provider-x` appears automatically in provider aggregation with no provider registry/display change.
- `TEL-03` two different unknown providers both appear; neither is collapsed into `other`.
- `TEL-04` provider/model/credential profile are data fields, not dashboard hard-coded enums.
- `TEL-05` a first-attempt 429 followed by success preserves both attempts and reports one retry.
- `TEL-06` a 503-only sequence remains failed and preserves every attempt.
- `TEL-07` a failure before response has `first_response_at = null` and nonnegative latency.
- `TEL-08` successful attempt records first-response and completion timestamps with nonnegative provider latency.
- `TEL-09` attempt index must be positive and unique within one review execution sequence.
- `TEL-10` API key/bearer-like material in credential or error fields is rejected or sanitized before persistence.
- `TEL-11` aggregation never stores a raw Authorization header.
- `TEL-12` review summary preserves semantic disposition, validation result, and authority effect without deriving them from latency/outcome.
- `TEL-13` mixed R1/R2/R3 records aggregate without slot-specific dashboard code.
- `TEL-14` multiple credential profiles remain distinguishable without revealing secret values.
- `TEL-15` requested and returned serving provider are separately retained where available.
- `TEL-16` provider route mismatch/failure telemetry cannot be interpreted as successful semantic review.
- `TEL-17` prior failed attempt remains visible after later successful retry.
- `TEL-18` deterministic aggregation output is stable for identical input records regardless of input ordering.
- `TEL-19` dashboard data builder includes arbitrary providers from normalized records automatically.
- `TEL-20` generated dashboard markup/data contains `future-provider-x` solely because it exists in input records, not because its name appears in renderer source/config.
- `TEL-21` telemetry generation does not change existing review semantic validation/disposition.
- `TEL-22` telemetry failure must not falsely make the review authoritative; observability failure is surfaced separately.
- `TEL-23` credential profile identity is displayed; secret values are absent from artifacts and rendered output.
- `TEL-24` current OpenRouter/DeepInfra route can be represented without any OpenRouter-specific aggregator/dashboard branch.

## 11. Construction order

1. Freeze this contract before implementation.
2. Add TEL-01..TEL-24, including `future-provider-x`, before telemetry mechanism code.
3. Preserve the red pre-mechanism CI run.
4. Implement normalized event validation/aggregation and generic dashboard data generation.
5. Instrument reviewer v7 generically across provider attempts; provider-specific invocation may remain in adapters, but timing/event emission may not be provider-specific.
6. Wire dashboard publication to collect telemetry artifacts dynamically.
7. Keep existing review-governance tests green.
8. Fresh independent review is mandatory before promotion of this observability boundary.

## 12. Claim boundary

A pass proves only that the tested review execution path emits, preserves, aggregates, and renders provider-neutral telemetry under the tested cases. It does not prove provider uptime, model quality, semantic correctness, billing correctness, remote model identity, or production authority.



---

## AUTHORITATIVE: standards/conversational-drift-contamination-control.md

Ref: 87f6e3df73c0c70c5d8ff4da38365ff92721aff7
Git blob SHA: 0908d676e172c89987305ca9f52078723ea1b6fe

# Conversational Drift and Evidence Contamination Control

## Purpose

Prevent unverified or false claims introduced in one research or agent step from becoming treated as authoritative facts in later steps merely through repetition, consensus, summarization, or conversational inheritance.

Conversation is not authority. Repetition is not evidence. Consensus is not truth. Only provenance-backed, policy-valid evidence may enter authoritative platform state.

## Threat Model

A common failure chain is:

`R1 introduces plausible false claim -> R2 inherits it as context -> R3 derives a requirement -> later agents treat the requirement as established fact`

The conversation can become internally coherent while drifting away from external reality.

A second continuity-specific failure chain is:

`authoritative state verified -> advisory memory/continuity write fails -> failure is hidden or treated as success -> next session resumes from stale/missing continuity -> user repetition or guesswork substitutes for governed recovery`

A continuity-store failure must not become an authority failure.

## Required State Separation

Maintain separate stores/state classes for:

1. Working hypotheses
2. Unverified claims
3. Source-verified claims
4. Independently verified claims
5. Accepted decisions
6. Governed requirements
7. Retracted/superseded claims

Raw conversation transcripts, summaries, model memory, continuity caches, and agent-to-agent messages are not authoritative stores.

## Claim Provenance Contract

Every material claim must carry a durable identifier and at minimum:

- claim_id
- exact claim text or normalized proposition
- status
- source identity
- source version/date when material
- primary/authoritative-source verification status
- producing agent/researcher
- independent reviewer/Judge result
- allowed uses
- prohibited uses
- parent claims
- derived claims/decisions/requirements
- retraction/supersession metadata

Recommended lifecycle:

`UNVERIFIED -> SOURCE_VERIFIED -> INDEPENDENTLY_VERIFIED -> PROMOTABLE -> ACCEPTED`

Non-authoritative states include:

`AMBIGUOUS`, `INSUFFICIENT_EVIDENCE`, `CONTRADICTED`, `DOMAIN_MISMATCH`, `FUNCTION_MISMATCH`, `RETRACTED`, `NEEDS_REASSESSMENT`.

## Context Compartmentalization

Agents must receive authoritative context reconstructed from governed state rather than inheriting the entire raw conversation as if every prior sentence were true.

A resumed or downstream agent should receive, at minimum:

- accepted requirements
- verified claims
- unresolved hypotheses
- active contradictions
- retractions
- decisions with provenance

Unverified claims may be supplied for investigation but must be visibly typed as unverified and prohibited from direct promotion.

## Non-Propagation Rule

An unverified claim may trigger research but may not be used as the sole basis for:

- a governed requirement
- a release decision
- a competitive conclusion
- a corrective action with consequential authority
- a model qualification decision
- an accepted architecture decision

Downstream agents must preserve the claim status rather than laundering uncertainty through paraphrase.

## Consensus Is Not Evidence

Agreement among R1, R2, R3, multiple models, or Researcher + Judge does not increase a claim's evidentiary status unless new independent evidence is added.

If three agents repeat the same unsupported claim, the claim remains unsupported.

## Derived-Claim Invalidation

When a parent claim is falsified, contradicted, or retracted, the governor must traverse its dependency graph and mark every dependent artifact for reassessment.

Required flow:

`parent claim retracted -> locate dependent claims -> locate decisions -> locate requirements -> mark NEEDS_REASSESSMENT -> block affected promotion/release paths until individually adjudicated`

Do not automatically delete downstream requirements: some may have independent support. Reassess each one.

## Grounding Checkpoints

Long-running research and multi-agent workflows must periodically rebuild working context from authoritative governed state.

A grounding checkpoint must not simply summarize prior conversation. It must reconstruct from verified claims, accepted decisions, requirements, unresolved hypotheses, and retractions.

Suggested triggers:

- after N research hops
- before requirement promotion
- before architecture promotion
- before corrective authority issuance
- before release/completion adjudication
- when a contradiction or retraction occurs
- when execution resumes after a context-window/chat/session boundary
- after a continuity-store read/write failure before authoritative work resumes

## Continuity-Store Failure Handling

Model/user memory and other continuity caches are advisory conveniences. They must not be the only durable representation of authoritative project state.

Required behavior when a continuity read or write fails:

1. Detect and surface the failure explicitly; never acknowledge an unsuccessful write as saved, remembered, synchronized, or persisted.
2. Preserve source precedence. Authoritative Git/evidence/registry state remains authoritative regardless of continuity-cache availability.
3. If authoritative state is already durably persisted, the workflow may continue while recording the continuity failure for audit/retry.
4. If the authoritative change itself is not durably persisted, block authoritative completion, promotion, or release rather than relying on the conversation or memory cache.
5. On the next session/context boundary, reconstruct state from governed storage rather than asking the user to restate authoritative definitions or inferring them from stale summaries when governed state is available.
6. A failed continuity write must not alter claim status, experiment status, revision identity, evidence validity, promotion eligibility, or release outcome.
7. Repeated continuity failures must remain observable; retries must not erase the original failure history.

The platform should distinguish at least:

- `CONTINUITY_READ_UNAVAILABLE`
- `CONTINUITY_WRITE_UNAVAILABLE`
- `CONTINUITY_WRITE_REJECTED`
- `CONTINUITY_STATE_STALE`
- `CONTINUITY_STATE_MISSING`

These are continuity conditions, not evidence states. They must not be mapped to `ACCEPTED`, `PROMOTED`, or any other authoritative claim status.

## Drift Detection Signals

The platform should detect and flag at least:

- unsupported claim repeated across multiple agents
- status loss during paraphrase/summarization
- claim promoted without source verification
- downstream artifact depending on retracted evidence
- consensus without evidence diversification
- authoritative context containing RETRACTED or CONTRADICTED claims
- requirements whose only provenance traces to conversation/model assertion
- summary text that upgrades `possible/maybe/unverified` into factual language
- continuity write/read failure hidden from the user or audit trail
- failed continuity write falsely acknowledged as persisted
- fresh-session recovery that asks for user repetition or uses guesswork despite available governed state
- stale continuity state overriding a newer authoritative revision

## Governor Boundary

LLMs may identify drift, but the non-propagation, promotion eligibility, retraction propagation, reassessment requirements, source precedence, and continuity-failure recovery rules must be enforced by deterministic platform mechanisms.

A Judge may recommend ACCEPT, REJECT, or REASSESS, but cannot override missing provenance, invalid parent-claim state, or authoritative source precedence.

A continuity subsystem may improve convenience but cannot confer authority. Its failure cannot upgrade, downgrade, restore, erase, or substitute authoritative state.

## Relationship to External Evidence Validation

This standard complements `standards/external-evidence-semantic-validation.md`.

External semantic validation controls whether a source claim is valid enough to enter the system. Conversational drift control governs how claims propagate after entry, how continuity failures are contained, and how contamination is contained if a claim later proves wrong.

## Historical Integrity

Corrections must preserve history. Do not silently rewrite R1/R2/R3 outputs to make them appear correct after the fact. Store the original claim, the later contradiction, the retraction, affected descendants, and the final adjudication.

Continuity failures must also preserve their own audit history. Do not rewrite a failed memory/cache update as though it succeeded after a later retry.



---

## AUTHORITATIVE: standards/external-evidence-semantic-validation.md

Ref: 87f6e3df73c0c70c5d8ff4da38365ff92721aff7
Git blob SHA: b13287ecd12e5c76a83202ad2bf76a37cbd19270

# External Evidence Semantic Validation Standard

## Purpose

Prevent lexical or branding similarity from being promoted into a governed conclusion without evidence that the external item actually performs the claimed function.

This standard was added after the Archify incident, where a product in physical architecture/interior/exterior design was incorrectly treated as a software-architecture tool because the term "architecture" was interpreted semantically without verifying the product domain and workflow.

## Governing rule

**Do not rely only on keyword or name matches. Inspect and verify the actual functional capability and concept before an external item may influence platform requirements, competitive conclusions, architecture decisions, or evidence-backed completion.**

## Required evidence contract

Before an external finding can enter `PROMOTED`, the evidence record must contain independently checkable support for all applicable fields:

1. `identity` — exact product/project/paper/tool and version/date when relevant.
2. `primary_source` — authoritative source inspected where reasonably available.
3. `domain` — actual problem/domain being addressed.
4. `intended_users` — who the item is designed for.
5. `inputs` — what it consumes.
6. `outputs` — what it produces or changes.
7. `functional_workflow` — what the system actually does, not what its name suggests.
8. `claimed_overlap` — the precise capability alleged to overlap with the governed platform.
9. `claim_support` — source evidence that directly supports that overlap.
10. `independent_judgment` — a Judge disposition that is separate from the researcher/Builder conclusion where the claim is material.

If a required field is absent, contradicted, unsupported, or sourced only from a snippet that the primary source disproves, promotion must be blocked.

## Enforcement model

Model instructions are guidance, not the enforcement boundary. The governor must make `PROMOTED` unreachable unless the evidence contract is satisfied.

A model saying `RELEVANT`, a researcher and Judge agreeing, or several models reaching the same conclusion is not sufficient if required evidence is missing or contradictory.

Suggested state flow:

`DISCOVERED -> SOURCE_VERIFIED -> SEMANTICALLY_CLASSIFIED -> OVERLAP_SUPPORTED -> INDEPENDENTLY_JUDGED -> PROMOTED`

Failure/hold states include:

- `DOMAIN_MISMATCH`
- `FUNCTION_MISMATCH`
- `PRIMARY_SOURCE_CONTRADICTION`
- `INSUFFICIENT_EVIDENCE`
- `AMBIGUOUS`
- `UNSUPPORTED_CLAIM`
- `RETRACTED`

## Semantic-collision risk

Treat overloaded terms as high-risk signals, including but not limited to: `architecture`, `agent`, `judge`, `workflow`, `verification`, `model`, `design`, `factory`, `governance`, and `orchestration`.

Lexical similarity may trigger investigation. It must never by itself satisfy relevance.

## Claim-to-source traceability

Every promoted external claim must retain a link from the claim to the authoritative evidence that substantiates it. If later evidence falsifies the interpretation, the system must preserve the original finding and correction history, retract the unsupported evidence, and reassess derived requirements for independent support rather than silently rewriting history.

## Authority boundary

A Judge is fallible. Judge approval cannot override missing mandatory evidence. Deterministic evidence requirements bound the Judge's authority.

This creates the intended separation:

**LLM judgment proposes a disposition; the governor decides whether that disposition is legally promotable under the evidence contract.**



---

## AUTHORITATIVE: standards/test-data-lifecycle-dependency.md

Ref: 87f6e3df73c0c70c5d8ff4da38365ff92721aff7
Git blob SHA: 26329a73a4f488531da3d707f04dd97eb26de4cd

# Test Data Lifecycle & Dependency Integrity

Every automated test or manual-QA case must declare the authoritative starting state and the data prerequisites required for the behavior under test. Validate those preconditions before executing state-changing actions.

- Eliminate accidental dependencies between tests. A test must not pass only because another test happened to leave mutable database state behind. Use isolated data, deterministic setup, or explicit reset/reseed where independence is required.
- Model legitimate workflow dependencies explicitly. When one step produces identifiers or state required by a later step, capture and propagate that authoritative output rather than reconstructing or hard-coding it.
- When a test mutates persistent lifecycle state, later tests must respect the resulting state. The same identity or record must not be treated as though it remained in an earlier state unless a controlled reset/reseed restored that precondition.
- Test fixtures must represent real contract-defined business states, including prerequisite records, valid relationships, lifecycle checkpoint, and allowed next actions.
- For stateful fixtures define a reuse policy: stable read-only, stable until mutated, disposable/consumable, or reset-required.
- A precondition mismatch must be surfaced and classified rather than bypassed to force the desired path.

## Required stateful test declaration

For stateful workflows record:

`starting state -> prerequisites -> action -> authoritative transition -> resulting state -> reuse/reset policy`

The governing principle is: **eliminate accidental dependencies; explicitly model legitimate dependencies.**



---

## AUTHORITATIVE: experiments/governed-platform/INTEGRATED_GOVERNED_MVP_CONTRACT.md

Ref: 87f6e3df73c0c70c5d8ff4da38365ff92721aff7
Git blob SHA: 253a2d8ed0fecea58070cd7c6dd1e78c967bdfc1

# Integrated Governed MVP — Composition Contract

Status: **PRE-IMPLEMENTATION FROZEN MVP BOUNDARY**

This is a product-integration stage, not EXP-I Pilot 20 and not a new scientific claim. It composes mechanisms already implemented and tested in the experimental repository into one deterministic minimum governed execution slice.

## 1. Goal

Demonstrate one end-to-end backend path in which a model may produce evidence/proposals, but consequential authority remains external to the model from routing through execution and completion.

Governed sequence:

1. Receive bound project/task/action intent.
2. Revalidate exact provider + model + SKU + deployment-path qualification at execution time.
3. Bind normalized model output to a platform-issued capability without granting model authority.
4. Revalidate the capability at the instant of consequential use.
5. Require review/manual escalation signals independently of model preference.
6. Admit consequential execution only when all deterministic gates are current and clean.
7. Produce a normalized decision/evidence record that distinguishes execution authorization from release/completion authority.

## 2. MVP boundaries

### Included

- exact task-specific qualification revalidation;
- provider/model/SKU/deployment-path binding;
- external platform capability as the sole mutation authority source;
- model authority claims retained as evidence but never effective authority;
- use-time capability validation;
- fail-closed review/manual-gate input;
- explicit block on RELEASE/DEPLOY/MERGE as MVP terminal authority;
- deterministic decision record suitable for evidence/audit persistence;
- negative-path tests for stale qualification, revocation, scope widening, model self-authorization, and manual-gate requirements.

### Deferred

- production PostgreSQL service and migrations;
- immutable object store;
- queue/event transport;
- real sandbox or repository write gateway;
- secret-manager leases;
- provider network calls;
- production UI;
- autonomous deployment/release;
- distributed consensus or multi-host correctness.

The MVP executor therefore returns an authorization decision only. It does **not** perform a real repository, browser, shell, deployment, or production side effect.

## 3. Frozen authority invariants

**MVP-01 External authority** — model output can never create, widen, refresh, revoke, or replace platform capability authority.

**MVP-02 Exact qualification** — consequential execution requires current exact provider + model + SKU + deployment path + qualification lineage.

**MVP-03 Use-time validation** — routing-time eligibility or prior capability validity cannot substitute for validation at the instant of requested use.

**MVP-04 Scope containment** — requested action and artifact classes must be a subset of the platform-issued capability.

**MVP-05 Review independence** — a model request to skip review cannot alter a platform review/manual-gate decision.

**MVP-06 Terminal-authority separation** — RELEASE, DEPLOY, and MERGE are never authorized by this MVP executor, even if included in a model claim or a broad capability. They require a separate external release/completion gate.

**MVP-07 Fail-closed composition** — malformed, stale, revoked, incomplete, contradictory, or HUMAN_REQUIRED gate inputs deny consequential execution.

**MVP-08 Evidence without authority** — unsafe model authority claims remain observable evidence while effective consequential authority remains false.

**MVP-09 Determinism** — identical bound inputs produce the same decision record, excluding explicitly external clock/state changes.

**MVP-10 No success laundering** — provider/model success, review agreement, test success, or workflow green status alone cannot become release/completion authority.

## 4. Decision states

- `DENY_QUALIFICATION`
- `DENY_AUTHORITY_BINDING`
- `DENY_CAPABILITY`
- `HUMAN_REQUIRED`
- `REVIEW_REQUIRED`
- `TERMINAL_AUTHORITY_REQUIRED`
- `AUTHORIZED_FOR_ISOLATED_EXECUTION`

`AUTHORIZED_FOR_ISOLATED_EXECUTION` means only that a separately isolated worker/gateway may be invoked for the exact requested action under the exact capability. It is not release, deploy, merge, completion, or production approval.

## 5. Input contract

The integration function receives explicit inputs only:

- `route`
- `registry_entry`
- `normalized_model_result`
- `capability`
- `execution_request`
- `review_gate`
- `now_epoch`
- `now_iso`

No ambient conversation history, model self-report, workflow label, or provider response label is authority.

`review_gate` is platform-derived and has:

- `state`: `CLEAR`, `REVIEW_REQUIRED`, or `HUMAN_REQUIRED`
- `evidence_refs`: list of immutable/frozen evidence identities where applicable

## 6. Acceptance tests

The implementation must demonstrate at minimum:

1. clean exact qualified scoped WRITE reaches `AUTHORIZED_FOR_ISOLATED_EXECUTION`;
2. provider/model/SKU/deployment-path substitution denies before capability use;
3. qualification epoch drift/revocation/expiry denies;
4. model-authorized-scope widening is retained as violation evidence and cannot authorize execution;
5. revoked/expired capability denies at use time;
6. action widening and artifact widening deny;
7. `HUMAN_REQUIRED` cannot be bypassed by model success or model skip-review request;
8. `REVIEW_REQUIRED` does not execute;
9. RELEASE/DEPLOY/MERGE always return `TERMINAL_AUTHORITY_REQUIRED` in this slice;
10. unsafe model authority attempt remains evidence-eligible when transport/result evidence was otherwise eligible;
11. malformed review-gate state fails closed;
12. clean deterministic replay returns the same decision body for the same inputs.

## 7. Nonclaims

Passing the MVP acceptance suite will not establish production readiness, sandbox security, database crash consistency, network correctness, provider attestation, secret isolation, release safety, or autonomous deployment authority. Existing experiment adjudications retain their own bounded claims and are not widened by this integration.



---

## AUTHORITATIVE: experiments/governed-platform/INTEGRATED_GOVERNED_MVP_SLICE5_AUTHORITATIVE_STATE_LEDGER_CONTRACT.md

Ref: 87f6e3df73c0c70c5d8ff4da38365ff92721aff7
Git blob SHA: 8acfe8a5f0cea45f3ce6ed2a18276fbd257a3927

# Integrated Governed MVP — Slice 5 Authoritative State Ledger Contract

Status: **PRE-IMPLEMENTATION FROZEN BOUNDARY**

Parent product integration commit: `a2fcd2ba9bc0e5828ee69056c23207fb431ecea6` (accepted Slice 4).
Governance prerequisite: PR #11 merged on `main` at `d46db1173db7db5b42459bf49f7fa28ef3dd105a` after authenticated `REV-GOV-PR11-006` PASS and green closure validation.

## 1. Goal

Falsify whether a modular-monolith reference backend can make the **accepted event + idempotency identity + authoritative state version + durable side-effect intent** one atomic transaction, so retries, crashes, concurrency, stale versions, payload rebinding, and worker/model claims cannot create duplicate or ungrounded authoritative transitions.

This slice implements a local SQLite reference mechanism only. It does not claim distributed consensus, physical power-loss guarantees beyond SQLite's documented transaction model, multi-host atomicity, or production-scale persistence.

## 2. Frozen transaction boundary

For a governed command, one database transaction must atomically persist:

1. immutable accepted-event record;
2. `(project_id, idempotency_key)` uniqueness;
3. canonical command/payload digest;
4. expected prior state version;
5. resulting authoritative state/version;
6. deterministic transition/result digest;
7. durable outbox record for any consequential downstream side effect.

No downstream side effect may execute before that transaction commits.

## 3. Authority invariants

**S5-I01 Atomic acceptance** — accepted event, idempotency identity, resulting state and outbox intent commit together or not at all.

**S5-I02 Intent-level idempotency** — the same `(project_id, idempotency_key)` + same canonical command converges to the original result; no new state version or outbox item is created.

**S5-I03 Rebinding rejection** — reuse of an idempotency key with a different command/payload digest fails closed.

**S5-I04 Optimistic version binding** — command acceptance requires exact expected current state version. Stale/future expected versions cannot mutate state.

**S5-I05 Monotonic authoritative version** — every successful non-replay transition increments the project state version exactly once.

**S5-I06 Side-effect-after-commit** — no worker/tool dispatch is permitted until a committed outbox record exists.

**S5-I07 Crash-before-commit** — failure before commit leaves no accepted event, state transition, or outbox side effect intent.

**S5-I08 Crash-after-commit-before-dispatch** — committed authoritative state and pending outbox intent survive and are discoverable for recovery.

**S5-I09 Dispatch replay safety** — repeated claiming/completion of the same outbox item cannot create duplicate authoritative state transitions; side-effect completion status is durable and monotonic.

**S5-I10 Concurrent same-intent convergence** — concurrent identical commands using one idempotency key converge to one accepted event/state version/outbox record.

**S5-I11 Concurrent conflicting intent fail-closed** — concurrent commands competing for the same expected state version cannot both become authoritative.

**S5-I12 Model/worker non-authority** — model or worker output cannot directly set authoritative state/version, mark an event accepted, or invent completion authority; only the ledger transaction may do so.

**S5-I13 Evidence lineage** — accepted events and outbox records expose canonical digests and immutable identifiers sufficient to reconstruct why an authoritative state version exists.

**S5-I14 Recovery is repository/data driven** — recovery enumerates committed pending outbox rows; it never infers completion from process memory, chat state, or worker assertions.

## 4. Frozen cases

- `S5-01` first valid command atomically creates event/state/outbox.
- `S5-02` exact retry returns original result without duplicate version/outbox.
- `S5-03` same idempotency key + changed payload is rejected.
- `S5-04` stale expected version is rejected with no mutation.
- `S5-05` future expected version is rejected with no mutation.
- `S5-06` injected failure after event insert but before state update rolls back everything.
- `S5-07` injected failure after state update but before outbox insert rolls back everything.
- `S5-08` crash immediately after commit preserves state and pending outbox.
- `S5-09` pending outbox recovery after repository/process reopen is deterministic.
- `S5-10` outbox completion is idempotent.
- `S5-11` duplicate completion/replay cannot advance authoritative state.
- `S5-12` concurrent identical submissions converge to one event/version/outbox.
- `S5-13` concurrent distinct submissions at one expected version permit at most one success.
- `S5-14` worker/model-supplied state/version/completion claims are ignored/rejected as authority inputs.
- `S5-15` event/result/outbox digests are stable across reopen/replay.
- `S5-16` invariant audit reconstructs contiguous state version lineage and detects tampered/missing lineage in a copied test database.

## 5. Acceptance criteria

A bounded Slice5 pass requires all `S5-01..S5-16` deterministic tests to pass on the exact implementation candidate and the broader integrated-governed-MVP regression suite to remain green. Provider LLM APIs are not required for the construction run.

A pass proves only the frozen single-database reference mechanism. Independent integration review remains mandatory before this slice can be promoted into the accepted integrated MVP boundary.

## 6. Forbidden shortcuts

- do not dispatch side effects before commit;
- do not treat queue delivery as authoritative state;
- do not overwrite/reuse an idempotency key for new intent;
- do not let worker/model output choose authoritative version or completion;
- do not make tests pass by weakening expected-version checks;
- do not delete failed/crash/replay evidence;
- do not claim distributed or physical durability from this reference mechanism.



---

## AUTHORITATIVE: experiments/governed-platform/INTEGRATED_GOVERNED_MVP_SLICE6_TERMINAL_AUTHORITY_GATE_CONTRACT.md

Ref: 87f6e3df73c0c70c5d8ff4da38365ff92721aff7
Git blob SHA: 3d9572cbae5e669bc4883727cc298c13e279ad18

# Integrated Governed MVP — Slice 6 Terminal Authority / Release-Completion Gate Contract

Status: **FROZEN BOUNDARY — AMENDED BY AUTHORITATIVE REQUIREMENT DECISION A**

Parent authoritative integration commit: `f67e0dfb4fe9b4bb67c76dbd43f1485861c96fc0` (accepted Slice 5 authoritative state ledger).

Amendment basis: deterministic review-of-review of `REV-MVP-SLICE6-TERMINAL-AUTHORITY-004` exposed an internal contradiction between the original broad wording of S6-I05 and the already-frozen per-input schemas. The authoritative decision is to preserve those schemas and narrow S6-I05 accordingly. No implementation field expansion is authorized by this amendment.

## 1. Goal

Falsify whether the integrated governed MVP can add the separate external terminal-authority boundary already required by the accepted composition contract without allowing model/worker claims, stale review evidence, stale artifact identity, replay, action substitution, or prior green CI to mint RELEASE / DEPLOY / MERGE / completion authority.

This slice produces a deterministic **terminal authorization receipt** only. It does not perform a remote push, merge, release, deployment, production mutation, or production completion action.

## 2. Required input lineage

A terminal decision consumes explicit bound inputs only:

1. `terminal_request`
   - `project_id`
   - `task_id`
   - `action` — one of `RELEASE`, `DEPLOY`, `MERGE`, `COMPLETE`
   - `effect_id`
   - `artifact_sha`
   - `expected_state_version`
2. `execution_evidence`
   - exact project/task/effect lineage
   - exact resulting artifact SHA
   - successful prior isolated execution state
   - `terminal_authority == false`
   - `release_completion_authority == false`
   - deterministic evidence hash
3. `review_gate`
   - `state == CLEAR`
   - immutable/frozen `evidence_refs`
   - exact reviewed `artifact_sha`
   - exact reviewed `action`
4. `authority_record`
   - `authority_id`
   - `source_class` — `HUMAN` or `PLATFORM_POLICY`
   - `decision` — `APPROVE` or `DENY`
   - exact project/task/effect/action/artifact binding
   - exact `state_version`
   - `issued_at_epoch`
   - `expires_at_epoch`
   - immutable/frozen `evidence_refs`
   - deterministic `authority_record_hash`
5. `current_state`
   - exact `project_id`
   - exact current authoritative `state_version`
6. explicit `now_epoch`

No ambient conversation history, provider/model label, worker assertion, prior workflow status, or stale CI result is authority.

## 3. Frozen authority invariants

**S6-I01 Separate terminal authority** — prior isolated execution success never implies terminal authority.

**S6-I02 External source class** — `MODEL`, `WORKER`, `RESEARCHER`, `JUDGE`, or any unrecognized source class cannot authorize terminal action. Only structurally valid `HUMAN` or `PLATFORM_POLICY` authority records may proceed in this bounded reference mechanism.

**S6-I03 Exact action binding** — approval for one terminal action cannot authorize another action.

**S6-I04 Exact artifact binding** — approval/review for one artifact SHA cannot authorize a different artifact SHA or a changed branch head.

**S6-I05 Scoped exact lineage binding** — bindings are enforced according to each frozen input schema, without inferring absent fields: `terminal_request`, `execution_evidence`, and `authority_record` must share exact project/task/effect/artifact lineage; `review_gate` must bind the exact terminal action and artifact SHA with immutable evidence references; `current_state` must bind the exact project ID and authoritative state version. No task/effect/artifact fields are required in `current_state`, and no project/task/effect fields are required in `review_gate` unless a later separately approved contract explicitly changes those schemas.

**S6-I06 Current authoritative version** — request `expected_state_version` must equal current authoritative `state_version`; stale/future versions fail closed.

**S6-I07 Review required** — terminal authorization requires a well-formed `CLEAR` review gate bound to the exact action and artifact. `REVIEW_REQUIRED`, `HUMAN_REQUIRED`, malformed, missing, or stale review evidence cannot authorize.

**S6-I08 Explicit approval** — only `decision == APPROVE` can authorize. `DENY`, missing, malformed, or contradictory decisions fail closed.

**S6-I09 Time validity** — authority record must be issued no later than `now_epoch` and must not be expired.

**S6-I10 Deterministic authority-record integrity** — the supplied authority-record hash must match canonical deterministic content. Tampering fails closed.

**S6-I11 Evidence integrity** — execution evidence must be self-consistent, deterministically hashed, and explicitly non-terminal in its own authority fields.

**S6-I12 No success laundering** — green CI, model success, reviewer/model agreement, isolated execution success, or repository mutation success cannot substitute for the terminal authority record.

**S6-I13 Idempotent decision** — identical bound inputs produce the same terminal decision receipt and digest.

**S6-I14 Rebinding rejection** — reusing an authority identity/hash for a changed action, artifact, lineage, or state version cannot authorize.

**S6-I15 Receipt is not side effect** — `AUTHORIZED_FOR_TERMINAL_ACTION` means a separately controlled terminal executor may be invoked for the exact bound action; it is not proof that the action occurred.

**S6-I16 Source authentication nonclaim** — this reference validates structure, binding, freshness, and deterministic integrity only. It does not prove cryptographic human identity, production IAM, signature authenticity, KMS custody, or organizational authorization policy.

## 4. Frozen decision states

- `DENY_REQUEST`
- `DENY_EXECUTION_EVIDENCE`
- `DENY_REVIEW_GATE`
- `DENY_AUTHORITY_SOURCE`
- `DENY_AUTHORITY_RECORD`
- `DENY_STATE_VERSION`
- `DENY_EXPIRED_AUTHORITY`
- `TERMINAL_ACTION_DENIED`
- `AUTHORIZED_FOR_TERMINAL_ACTION`

Every decision must include:

- `authorized`
- `terminal_authority`
- `release_completion_authority`
- exact bound lineage
- deterministic `receipt_hash`
- reason

Only `AUTHORIZED_FOR_TERMINAL_ACTION` may set `authorized`, `terminal_authority`, and `release_completion_authority` true.

## 5. Frozen acceptance cases

- `S6-01` exact valid RELEASE approval reaches `AUTHORIZED_FOR_TERMINAL_ACTION`.
- `S6-02` valid MERGE approval reaches authorization only for MERGE.
- `S6-03` valid DEPLOY approval reaches authorization only for DEPLOY.
- `S6-04` valid COMPLETE approval reaches authorization only for COMPLETE.
- `S6-05` prior isolated execution success without authority record is denied.
- `S6-06` model/worker authority source is denied.
- `S6-07` action substitution is denied.
- `S6-08` artifact SHA substitution / moved head is denied.
- `S6-09` project/task/effect lineage mismatch is denied where those fields are present in the frozen input schema.
- `S6-10` stale expected authoritative state version is denied.
- `S6-11` future expected authoritative state version is denied.
- `S6-12` `REVIEW_REQUIRED` cannot authorize.
- `S6-13` `HUMAN_REQUIRED` cannot authorize.
- `S6-14` malformed review gate cannot authorize.
- `S6-15` explicit authority `DENY` returns `TERMINAL_ACTION_DENIED`.
- `S6-16` expired authority is denied.
- `S6-17` future-issued authority is denied.
- `S6-18` tampered authority record hash is denied.
- `S6-19` malformed/tampered execution evidence is denied.
- `S6-20` execution evidence attempting terminal authority is denied.
- `S6-21` identical replay returns identical decision body and receipt hash.
- `S6-22` green-CI/model-success fields in auxiliary evidence cannot authorize without valid authority record.
- `S6-23` authority identity/hash cannot be rebound to a changed artifact/action/state version and remain valid.
- `S6-24` authorized receipt contains no claim that merge/deploy/release/completion actually occurred.
- `S6-25` Option-A schema preservation: a valid authorization succeeds with `review_gate` containing only its frozen action/artifact/evidence fields and `current_state` containing only project/state-version fields; absent non-schema task/effect/artifact fields must not be invented or required.

## 6. Acceptance criteria

A bounded Slice 6 pass requires all `S6-01..S6-25` deterministic tests to pass on one exact candidate SHA and the accepted Slice 1→Slice 5 regression chain to remain green.

Independent integration review remains mandatory before promotion into `main`.

## 7. Forbidden shortcuts

- do not turn green CI into terminal authority;
- do not treat model/reviewer consensus as authority;
- do not accept moved artifact/head identity after review;
- do not widen approval from one terminal action to another;
- do not accept stale/future authoritative state versions;
- do not weaken review requirements to obtain a pass;
- do not infer human identity from a string label;
- do not claim the terminal action occurred merely because the gate authorized it;
- do not invent or require fields outside the frozen per-input schemas to satisfy an over-broad interpretation of lineage;
- do not modify accepted Slice 1→Slice 5 behavior to accommodate this slice.

## 8. Claim boundary

A bounded pass proves only a deterministic reference terminal-authorization gate with scoped per-input action/artifact/lineage/state-version binding, explicit external approval input, review-gate dependency, freshness checks, and model/worker non-authority. It does not prove production identity authentication, cryptographic signatures, IAM/KMS correctness, remote side-effect safety, deployment safety, or organizational release policy correctness.

## 9. Preserved contradiction and decision history

The original S6-I05 wording remains part of repository history and is not rewritten retroactively. `REV-MVP-SLICE6-TERMINAL-AUTHORITY-004` returned semantic PASS but deterministic adjudication classified the contract contradiction as `REQUIREMENT_UNRESOLVED_CONTRACT_INTERNAL_CONTRADICTION` with authority effect `NONE`. The authoritative requirement decision selected Option A: preserve the frozen input schemas and narrow S6-I05 to those per-object bindings. All earlier review outcomes, provider failures, defect exposure, and repair commits remain historical evidence and do not authorize promotion of this amended candidate.



---

## AUTHORITATIVE: experiments/governed-platform/INTEGRATED_GOVERNED_MVP_SLICE10_EXTERNAL_SIDE_EFFECT_GATEWAY_CONTRACT.md

Ref: 87f6e3df73c0c70c5d8ff4da38365ff92721aff7
Git blob SHA: 9903acf1dc1454bba2dec411100c2d39c8a8ca6c

# Integrated Governed MVP — Slice 10 External Side-Effect Gateway Contract

Status: **PRE-IMPLEMENTATION FROZEN BOUNDARY**

Current authoritative `main` parent: `ab3454a84a5afbfeeb9a15bcf87f0be8d4e8a137`.
Accepted prior boundary: Slice 9 external credential lease gate, exact accepted candidate `16ae65c9d4939efc05aeff76f0ae2e708428b3b1`.

## 1. Goal

Falsify whether an exact already-governed remote execution binding plus a valid current credential lease can invoke one bounded external side-effect adapter without allowing a model, worker, reviewer, retry path, stale authority record, stale lease, transport ambiguity, provider success label, or local crash to widen the target/action/payload, duplicate the external effect, launder ambiguous outcomes into success, or convert credential possession/provider response into completion authority.

Slice 10 introduces a deterministic **safe reference external side-effect gateway** with durable idempotency and ambiguous-outcome recovery. It does not call a real production GitHub/cloud/deployment/payment endpoint and does not perform a production consequence.

## 2. Included

- exact consumption of accepted Slice8 remote-execution lineage and accepted Slice9 credential lease evidence;
- platform-owned provider/endpoint/action/resource binding;
- deterministic external idempotency key derived from the frozen execution identity;
- one external idempotency key → one exact provider/endpoint/action/resource/payload binding;
- pre-call revalidation of terminal authority and credential lease validity;
- safe loopback/reference external endpoint that persists provider-side effect identity separately from the caller;
- durable caller-side intent, attempt, reconciliation, and completion records;
- explicit handling of timeout/connection loss/unknown response after the provider may already have committed the effect;
- reconciliation/query before retry when outcome is ambiguous;
- crash recovery when provider commit succeeds before caller completion persistence;
- rejection of provider/endpoint/action/resource/payload substitution;
- provider HTTP success or model/reviewer/CI claim retained only as evidence, never completion authority;
- secret-value non-persistence/non-disclosure;
- response/effect evidence bound to exact request, external effect identity, result digest, and current lineage;
- preserved accepted Slice1→Slice9 regression lineage.

## 3. Deferred / nonclaims

- real GitHub merge/release/deploy mutation;
- real cloud infrastructure mutation;
- real payment/message/production API;
- production secret manager/IAM correctness;
- external provider cryptographic identity attestation;
- TLS/PKI/DNS/proxy/service-mesh correctness;
- third-party provider bugs, eventual-consistency guarantees, or global exactly-once semantics;
- multi-region consensus;
- malicious host/root compromise resistance;
- autonomous release/deploy/merge authority;
- proof that a provider HTTP 2xx means the intended business effect occurred unless independently reconciled under this contract.

## 4. Frozen input contract

### External effect request

- `side_effect_request_id`
- `project_id`
- `task_id`
- `effect_id`
- `terminal_execution_id`
- `remote_idempotency_key`
- `credential_lease_id`
- `credential_profile_id`
- `provider_id`
- `endpoint_id`
- `action`
- `resource_id`
- `artifact_sha`
- `state_version`
- `payload_digest`
- `authority_snapshot_hash`
- `lease_evidence_hash`
- `now_epoch`

No raw secret/API key/token/password field is permitted.

### External provider/reference result

- `provider_id`
- `endpoint_id`
- `external_idempotency_key`
- `external_effect_id`
- `provider_status`
- `provider_result_digest`
- `provider_committed`
- `observed_at_epoch`

The result is evidence only. It is not terminal completion authority.

## 5. Frozen invariants

**S10-I01 Exact accepted upstream lineage** — no external attempt is permitted without valid exact Slice8 remote execution lineage and valid exact Slice9 credential lease evidence.

**S10-I02 Platform-owned target binding** — provider, endpoint, action, resource, and credential profile are platform-controlled; model/worker/reviewer input cannot replace them.

**S10-I03 Use-time authority and lease validity** — current terminal authority and credential lease/profile validity must be rechecked immediately before each external invocation/reconciliation step.

**S10-I04 Deterministic external idempotency** — the external idempotency key is platform-derived from the exact frozen effect binding and reused for retries of the same intent; transport attempts never mint new effect intent.

**S10-I05 One external key, one binding** — reuse of an external idempotency key with changed provider/endpoint/action/resource/artifact/state/payload/lease binding is denied.

**S10-I06 Ambiguous outcome is not failure or success** — timeout, connection loss, process death, missing body, malformed body, or unknown transport state after dispatch must enter `OUTCOME_UNKNOWN_RECONCILE_REQUIRED`; it must not be retried as a fresh effect or marked successful without reconciliation.

**S10-I07 Reconcile before retry** — after an ambiguous attempt, the gateway must query/recover provider-side state using the same external idempotency key before another mutating call.

**S10-I08 Crash-after-provider-commit recovery** — if the provider committed the effect before caller persistence/crash, restart must recover the same external effect identity and must not duplicate the effect.

**S10-I09 Provider success is not completion authority** — HTTP 2xx, provider `SUCCESS`, model/reviewer agreement, CI green, or credential possession cannot mint terminal completion/release/deploy/merge authority.

**S10-I10 Provider response integrity** — external effect evidence must bind exact provider/endpoint/idempotency/effect/result digest and must reject tampered or mismatched responses.

**S10-I11 Scope containment** — payload/resource/action may not exceed the intersection of terminal authority, remote execution binding, and credential lease/profile policy.

**S10-I12 Revocation dominates retry** — if authority/lease/profile is revoked/expired after an ambiguous attempt, reconciliation may inspect existing provider state but no new mutating retry may occur under stale authority.

**S10-I13 Secret-value non-persistence/disclosure** — no raw secret may appear in request/evidence/ledger/telemetry/diagnostics/provider error records.

**S10-I14 Durable intent before dispatch** — the exact effect intent/binding must be persisted before any mutating provider dispatch.

**S10-I15 Reference endpoint only** — a passing local/reference external target proves bounded transport/idempotency/reconciliation semantics only, not production external-provider safety.

## 6. Frozen result states

- `DENY_UPSTREAM_LINEAGE`
- `DENY_AUTHORITY_OR_LEASE`
- `DENY_TARGET_SUBSTITUTION`
- `DENY_SCOPE_WIDENING`
- `DENY_IDEMPOTENCY_REBIND`
- `DENY_RESPONSE_INTEGRITY`
- `OUTCOME_UNKNOWN_RECONCILE_REQUIRED`
- `RECONCILED_EXISTING_EFFECT`
- `REFERENCE_EFFECT_APPLIED`
- `REFERENCE_EFFECT_REPLAYED`
- `REFERENCE_EFFECT_FAILED`

Only `RECONCILED_EXISTING_EFFECT`, `REFERENCE_EFFECT_APPLIED`, and `REFERENCE_EFFECT_REPLAYED` may carry positive external-effect evidence. None constitutes merge/deploy/release/completion authority.

## 7. Frozen acceptance cases

- `S10-01` exact accepted Slice8+Slice9 lineage applies one bounded reference external effect.
- `S10-02` exact replay reuses the same external idempotency key/effect identity without duplicate provider mutation.
- `S10-03` missing/malformed/non-success Slice8 lineage denies before provider access.
- `S10-04` missing/malformed/non-success Slice9 lease evidence denies before provider access.
- `S10-05` provider substitution denies.
- `S10-06` endpoint substitution denies.
- `S10-07` action/resource/artifact/state/payload widening denies.
- `S10-08` caller-supplied replacement external idempotency key denies.
- `S10-09` same external key with changed binding denies.
- `S10-10` raw secret input denies before dispatch.
- `S10-11` expired/revoked authority denies dispatch.
- `S10-12` expired/revoked/stale credential lease/profile denies dispatch.
- `S10-13` timeout before provider commit yields safe failure/no provider effect.
- `S10-14` timeout after provider commit yields `OUTCOME_UNKNOWN_RECONCILE_REQUIRED`, not fresh retry/success.
- `S10-15` reconciliation after ambiguous provider commit recovers the same external effect identity.
- `S10-16` crash after provider commit but before caller completion persistence recovers after restart without duplicate effect.
- `S10-17` repeated recovery/replay after committed effect never increments provider effect count.
- `S10-18` ambiguous attempt followed by authority/lease revocation may reconcile existing state but cannot issue a new mutating retry.
- `S10-19` provider HTTP 200 with mismatched effect/idempotency/result digest is rejected.
- `S10-20` provider self-reported success without provider-side committed evidence cannot become positive completion evidence.
- `S10-21` provider 5xx before commit remains failure and does not mint completion evidence.
- `S10-22` governed evidence/telemetry/diagnostics contain no raw secret value.
- `S10-23` mutated provider/endpoint/action/resource/artifact/state/payload/lease/idempotency fields change or invalidate evidence hash.
- `S10-24` provider/model/reviewer/CI success claims cannot become terminal authority.
- `S10-25` synthetic future provider/endpoint identifiers work without provider-specific evidence/dashboard branching.
- `S10-26` no result claims a real production GitHub/cloud/deploy/payment action occurred.

## 8. Construction and freeze rules

1. Commit this contract before acceptance tests or mechanism implementation.
2. Add `S10-01..S10-26` falsification tests before mechanism implementation wherever scientifically feasible.
3. Preserve the first RED run; do not weaken tests to obtain green.
4. Include explicit provider-side effect counters/state so duplicate mutations are observable.
5. Include crash points before dispatch, after dispatch-before-response, after provider commit-before-local-completion, and after local completion.
6. Keep the reference endpoint deterministic and network-local/safe; no production credential or production API is permitted.
7. Provider/endpoint behavior must be registry/config driven; include a synthetic future provider/endpoint case.
8. Preserve accepted Slice1→Slice9 regressions.
9. Freeze an exact candidate only after all Slice10 cases and prior regressions are green.
10. Fresh independent review of the exact candidate is mandatory before promotion.
11. Deterministic review-of-review and exact closure-head validation are mandatory before merge.
12. Green CI, provider success, credential possession, model/reviewer PASS, or reconciliation success is evidence only and never merge/deploy/release authority by itself.

## 9. Claim boundary

A bounded pass supports only that the tested safe reference external side-effect gateway enforced exact target/lineage binding, durable idempotency, ambiguous-outcome reconciliation, crash recovery, replay non-duplication, current authority/lease checks, response integrity, and secret non-disclosure under the frozen cases. It does not establish production external-provider safety, production IAM/secret-manager correctness, global exactly-once semantics, real deployment/release safety, or autonomous terminal authority.



---

## PROPOSED_PR39: standards/conversation-continuity-and-resumption-control.md

Ref: 1029e8a7883abc30975a6bff908f43cf9192dab5
Git blob SHA: 0e5af4b42e39c3a751c13e1b5b162643b45effec

# Conversation Continuity and Resumption Control

Status: **PROPOSED — REVIEW REQUIRED — NON-AUTHORITATIVE**

Authority effect: **NONE_EVIDENCE_ONLY**

Purpose: prevent chat interruption, device switching, context truncation, conversation rollover, model/session changes, or stale conversational state from silently changing governed workflow state or skipping required gates.

## 1. Core invariant

A conversation is an interface, not the authoritative workflow state.

No chat/session/device boundary may itself create, advance, reset, approve, qualify, adjudicate, merge, release, or otherwise authorize a governed state transition.

## 2. Development-time continuity source

While the governed platform itself is still being built, durable project continuity must be recovered from repository-backed evidence and frozen artifacts rather than conversational inference alone.

Before consequential project work resumes after an interruption, the operator/assistant must recover enough durable state to determine:

- current governed phase;
- exact candidate/artifact identity and commit SHA or digest where applicable;
- completed required steps;
- pending required steps;
- reviewer/test/adjudication status;
- current authority effect;
- unresolved findings or stale conditions;
- exact next permitted action.

Repository evidence is a development-time continuity anchor. It is not automatically runtime governance authority.

## 3. Production-time continuity source

In the implemented platform, authoritative resumption state must come from the platform coordination backend plus append-only evidence/governance ledger, not from ChatGPT memory, a conversation transcript, or GitHub UI state.

GitHub may remain a development/reference/mirror adapter but must not become the sole runtime continuity authority.

## 4. Resume-from-checkpoint rule

After any interruption, governed work must resume from the latest valid durable checkpoint whose bindings can be verified.

A checkpoint must bind, as applicable:

- project/workflow identifier;
- phase;
- task/candidate identifier;
- exact commit SHA/artifact digest;
- policy/schema version;
- required reviewer/test set;
- completed evidence references;
- pending evidence requirements;
- authority state;
- next permitted transition/action;
- checkpoint timestamp/sequence;
- predecessor checkpoint/event digest when ledger-backed.

Conversational recollection may help locate the checkpoint but may not override contradictory durable evidence.

## 5. Timestamp recovery rule

If work stops abruptly, recover the latest valid durable event/checkpoint by authoritative sequence first and timestamp second.

Wall-clock recency alone must not override a linearly ordered ledger sequence. In development workflows without a platform ledger, Git commit/order plus explicitly recorded project checkpoint evidence should be preferred over conversational recency.

Incomplete assistant reasoning, proposed next steps, unsent edits, or interrupted tool plans do not become authoritative merely because they occurred later in a chat.

## 6. No stage skipping

Resumption must preserve all prerequisite barriers.

Examples:

- `REVIEW_1_COMPLETE / REVIEW_2_PENDING / REVIEW_3_PENDING` may not resume at adjudication.
- `ALL_REQUIRED_REVIEWS_FROZEN` may resume at adjudication only if the exact candidate binding still matches.
- a failed or stale validation may not resume as qualified.
- a pending adjudication may not resume at repair/merge/release.

For multi-review workflows, the default barrier is:

`ALL_REQUIRED_REVIEWS_FROZEN -> ADJUDICATION -> REPAIR/DECISION`

Receipt of any subset of required reviews must not trigger candidate modification unless the governing policy explicitly permits iterative review and invalidates/restarts the affected review set.

## 7. Exact-artifact binding

Reviews, tests, validations, adjudications, and approvals survive an interruption only for the exact artifact/revision to which they were bound.

Any material candidate change produces a new candidate identity and must trigger the policy-defined stale/revalidation/re-review behavior.

## 8. Approval scope preservation

A user/operator approval survives an interruption only for the exact scoped action it approved.

Examples:

- approval to run Reviewer 2 on candidate X does not authorize Reviewer 3;
- approval to execute tests does not authorize repair;
- approval to repair does not authorize adjudication or merge;
- approval to adjudicate does not grant terminal authority.

A device/chat/model change never broadens approval scope.

## 9. Interruption is non-authoritative

The following events have zero authority effect by themselves:

- switching laptop/phone/desktop;
- opening a new conversation;
- hitting a conversation/context limit;
- reconnecting after network loss;
- changing assistant model/session;
- restarting an application;
- receiving a new conversational summary;
- restoring from assistant memory.

Each is a transport/interface event, not a governance transition.

## 10. Preserve RED, stale, and incomplete history

Resumption must preserve prior failures, rejected evidence, stale records, interrupted attempts, incomplete review sets, and superseded checkpoints.

A new conversation must not reconstruct a cleaner state by omission.

## 11. Contradiction handling

If conversational state conflicts with durable repository/ledger evidence, governed progression must stop at `CONTINUITY_CONFLICT` until the conflict is resolved from authoritative evidence.

The system must not choose the version that is more convenient, more recent in chat, or more permissive.

Resolution itself must be recorded as evidence and must not erase the conflicting history.

## 12. Consequential-action continuity check

Before architecture mutation, implementation, validation, qualification, reviewer orchestration, adjudication, merge, release, deployment, or terminal action after interruption, perform a continuity check that answers:

1. What exact workflow and phase are active?
2. What exact candidate/artifact is bound?
3. What required gates are complete?
4. What required gates remain pending?
5. Has any bound evidence become stale?
6. What authority state currently exists?
7. What is the single next permitted governed action?

If any answer is unresolved, fail closed.

## 13. Reviewer isolation across interruption

Independent reviewer evidence must remain isolated even when the review workflow spans multiple chats/devices.

A resumed session must not expose one reviewer’s substantive findings to another reviewer unless the governing review protocol explicitly requires cross-review.

The continuity checkpoint may record reviewer status and artifact identity, but should not leak substantive reviewer conclusions into a still-pending independent review path.

## 14. API and remote-worker continuity

External API/worker execution is not inherently tied to a ChatGPT conversation.

Its continuity is valid only if the platform durably binds request identity, task/candidate identity, worker/reviewer identity, evidence digests, response/result identity, lifecycle state, and relevant policy/authority state outside the chat transcript.

An API request/response that exists only in conversational memory is not durable governance state.

## 15. Runtime checkpoint ownership

Production checkpoints must be emitted and validated by a trusted coordination/governance component under role/event authorization rules. A worker, candidate, reviewer, or conversational assistant must not be able to self-create an authoritative checkpoint that advances its own lifecycle state.

## 16. Required machine states

At minimum, implementations should support explicit continuity outcomes such as:

- `CONTINUITY_OK`
- `CONTINUITY_STALE`
- `CONTINUITY_CONFLICT`
- `CONTINUITY_INSUFFICIENT_EVIDENCE`
- `CONTINUITY_REVIEW_BARRIER_PENDING`
- `CONTINUITY_AUTHORITY_BARRIER_PENDING`

Exact enums/error codes must be frozen before implementation qualification.

## 17. Current manual operating rule

Until this standard is reviewed and qualified, use the following bounded operating practice for this repository:

- recover current project state from GitHub/frozen artifacts before consequential work after a chat interruption;
- do not treat memory or chat summaries as authoritative when they conflict with repository evidence;
- preserve pending manual-review barriers;
- do not use a partial reviewer set to trigger repair or adjudication;
- keep all reviewer artifacts evidence-only until the preregistered review set is complete and adjudicated.

This operating rule is a safety bound, not proof that the final platform mechanism is sufficient.

## 18. Freeze condition

This standard must not be frozen until its associated continuity/resumption falsification matrix is reviewed and executed to the required policy threshold.

This document grants no merge, release, production, qualification, adjudication, or terminal authority.



---

## PROPOSED_PR39: standards/external-manual-review-packet-control.md

Ref: 1029e8a7883abc30975a6bff908f43cf9192dab5
Git blob SHA: 0528a80309bfd573ab71b2d102dfe11e0a04b2cf

# External Manual Review Packet Control

Status: **PROPOSED — REVIEW REQUIRED — NON-AUTHORITATIVE**

Authority effect: **NONE_EVIDENCE_ONLY**

Purpose: ensure an external/manual reviewer can review the exact frozen candidate without requiring repository, GitHub, local filesystem, API, or prior-chat access.

## 1. Self-contained packet rule

When an external reviewer does not have verified access to the authoritative repository or source system, the review request must be delivered as a self-contained packet.

The packet must include:

- the exact frozen candidate artifact contents required for review;
- the frozen candidate identifier, commit SHA and/or artifact digest;
- the review scope;
- the complete external review prompt;
- explicit evidence-only / authority limitation;
- any preregistered falsification matrix or acceptance criteria required to evaluate the candidate.

A repository URL, PR number, branch name, file path, or SHA by itself is not sufficient evidence delivery when the reviewer cannot access the repository.

## 2. Prompt accompanies every external review

Every external/manual review request must include the review prompt together with the candidate packet. The prompt must not be supplied only by conversational reference such as “use the previous prompt.”

The prompt must state the reviewer posture, required output structure, scope, and authority effect.

## 3. Exact candidate binding

The packet must identify the exact candidate revision being reviewed. If the candidate changes after packet creation, the packet becomes stale and must not be reused as review evidence for the new candidate.

Any review returned against a stale packet remains evidence only for the exact candidate represented in that packet.

## 4. No hidden dependency on reviewer access

Packet construction must assume the external reviewer has no access to:

- GitHub or repository contents;
- prior ChatGPT conversations;
- local development files;
- connected applications;
- internal APIs;
- other reviewers’ findings.

If any external dependency is required, it must be explicitly included in the packet or the review must be marked `INSUFFICIENT_EVIDENCE` for that dependency.

## 5. Reviewer isolation

For independent reviews, a packet must not contain substantive findings, conclusions, scores, or dispositions from another reviewer unless the governing protocol explicitly defines a cross-review stage.

Status metadata may state that other reviews exist or are pending only when necessary for workflow coordination and without exposing their conclusions.

## 6. Delivery format

Use a directly readable, self-contained file format. Do not package the review packet as a ZIP archive unless the user explicitly requests ZIP.

A single Markdown, text, PDF, or other directly readable document is preferred when feasible.

## 7. Integrity check before delivery

Before presenting the packet, verify:

1. all required candidate files are included in full;
2. the frozen candidate identifier matches the source artifact;
3. the complete review prompt is present;
4. no required content depends on inaccessible links;
5. no prior reviewer findings have contaminated an independent-review packet;
6. authority remains `NONE_EVIDENCE_ONLY` unless a separate qualified governance rule explicitly says otherwise.

## 8. Operating rule

For this project, when the user asks for an external review packet, default to:

`EXACT FROZEN ARTIFACT(S) + COMPLETE REVIEW PROMPT + AUTHORITY LIMITATION`

and assume **NO GITHUB ACCESS** unless access has been explicitly established.

This document grants no merge, release, production, qualification, adjudication, or terminal authority.


---

## PROPOSED_PR40: standards/project-governance-policy-composition.md

Ref: 513bb3304a14f42e0c1a67bb6a408c339a0f4463
Git blob SHA: 1348d2ac63629531f50a0d827697ff648062c973

# Project Governance Policy Composition Standard

Status: PROPOSED_PENDING_INDEPENDENT_REVIEW

## 1. Purpose

This standard defines how user-, organization-, project-, and experiment-specific governance rules compose with mandatory platform governance.

The governing principle is:

> Users may strengthen or specialize governance for their project, but lower-level configuration must not silently weaken mandatory platform invariants.

## 2. Governance hierarchy

Effective governance is composed in this order:

1. Platform mandatory invariants
2. Organization governance
3. Project governance
4. Experiment / release governance

Lower levels inherit all applicable higher-level requirements.

Effective Governance = Platform Mandatory Rules + Organization Rules + Project Rules + Experiment/Release Rules

Project or experiment configuration does not replace the platform baseline.

## 3. Non-weakenable platform floor

A lower-level rule MUST NOT disable, bypass, contradict, redefine, or silently weaken a mandatory platform invariant.

Examples of platform invariants include, where applicable:

- no self-granted PASS or qualification;
- preservation of prior failures, retractions, and contrary evidence;
- exact evidence/source identity binding;
- mandatory independent review where policy requires it;
- no fabricated or candidate-self-authored evidence being treated as independent proof;
- fail closed when mandatory evidence, authority, identity, or review is missing or invalid;
- no unauthorized promotion, deployment, release, or live provider/API authority;
- deterministic or otherwise governed evidence requirements defined by the applicable platform policy.

If a lower-level rule conflicts with a mandatory invariant, the conflict MUST be rejected and the effective policy MUST remain non-promotable until resolved.

## 4. User/project rule capability

Authorized users MAY add project-specific governance requirements, including but not limited to:

- additional independent reviewers;
- stricter mutation or coverage thresholds;
- security/privacy requirements;
- logging restrictions;
- manual approval gates;
- approved-model or approved-provider constraints;
- retention periods;
- domain-specific evidence requirements;
- performance, accessibility, compliance, or release conditions.

Such rules may specialize or strengthen the platform baseline.

## 5. Explicit override policy

No implicit override is permitted.

A higher-level rule MAY be overridden only when all of the following are true:

1. the higher-level rule is explicitly marked overridable;
2. the lower-level actor has explicit authority for that override;
3. the override is recorded as a distinct policy change;
4. the resulting effective policy is recomputed and validated;
5. the override does not weaken any invariant marked mandatory/non-overridable;
6. any required independent review of the governance change is completed before promotion.

Absence of an override declaration means the higher-level rule remains authoritative.

## 6. Effective Governance Snapshot

Before governed execution, the platform MUST derive an immutable Effective Governance Snapshot containing at least:

- platform policy version/identity;
- organization policy version/identity, if any;
- project policy version/identity, if any;
- experiment/release policy version/identity, if any;
- composed effective requirements;
- conflict-resolution result;
- identities/hashes of all contributing policy inputs;
- actor/authority metadata for policy changes;
- creation timestamp or governed sequence identity.

The Effective Governance Snapshot MUST be content-addressed or otherwise immutably bound to the governed candidate and its evidence.

Changing governance after a candidate is frozen MUST produce a new governance snapshot and, where the changed rule is material, a fresh governed candidate/evidence cycle.

## 7. Conflict rules

Policy composition MUST be fail-closed.

For the same governed requirement:

- a stricter compatible constraint wins;
- additive requirements accumulate;
- a contradictory lower-level weakening is rejected;
- ambiguity is non-promotable until resolved;
- missing mandatory policy inputs are non-promotable.

Examples:

- Platform requires >=1 independent reviewer; project requires 2 -> effective requirement is 2.
- Platform requires independent review; project says none -> project rule is invalid.
- Platform requires failures preserved; project says delete old failures -> project rule is invalid.
- Platform allows retention >=1 year; project requires 7 years -> effective retention is 7 years.

## 8. Auditability

Every governance change MUST preserve:

- rule identifier;
- old value/state;
- new value/state;
- actor identity/authority;
- rationale;
- effective policy scope;
- governed sequence/version;
- review/adjudication evidence when required.

Policy history MUST NOT be silently rewritten.

## 9. Authority boundary

Policy definition is not qualification authority.

A user, organization, project owner, model, reviewer, or policy composer MUST NOT gain release/promotion authority merely by authoring or selecting governance rules.

The effective policy determines constraints; separate governed evidence and review determine whether those constraints are satisfied.

## 10. Required implementation architecture

The governed platform should expose these logical components:

- Governance Policy Registry
  - Platform Policy
  - Organization Policy
  - Project Policy
  - Experiment / Release Policy
- Policy Composition Engine
- Effective Governance Snapshot
- Policy Conflict Validator
- Policy Change Audit Log
- Governance Snapshot -> Candidate/Evidence Binding

The composition engine MUST be deterministic for the same ordered policy inputs.

## 11. Required falsification cases

At minimum, implementation tests must attempt to falsify:

1. project rule disables mandatory independent review;
2. project rule enables self-approval;
3. project rule lowers a mandatory evidence threshold;
4. project rule deletes/purges required historical failures;
5. project rule weakens a non-overridable authority boundary;
6. conflicting policies are silently accepted;
7. policy changes after source freeze do not trigger a new governance snapshot;
8. evidence produced under policy version A is presented under policy version B;
9. unauthorized actor changes project governance;
10. policy composer produces different effective policy for identical ordered inputs.

Any surviving case blocks promotion.

## 12. Promotion rule

This standard becomes authoritative only after the repository's applicable governance-change review and promotion process closes successfully.

Until then:

- Status = PROPOSED_PENDING_INDEPENDENT_REVIEW
- Authority effect = NONE

