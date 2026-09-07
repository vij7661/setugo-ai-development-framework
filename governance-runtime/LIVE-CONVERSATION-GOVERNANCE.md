# Live Conversation Governance Runtime

## Purpose

This runtime applies governed-platform rules to the human–LLM development conversation so chat-window changes, context loss, model confidence, shared-memory drift, reviewer availability, or review-delivery mode cannot silently change authoritative project state.

This is an operational control for our collaboration, not a claim that the ChatGPT product itself enforces these rules internally. Governed Git/evidence remains authoritative.

## Authority versus operational memory

Authority and continuity utility are separate.

Authority precedence:

1. Governed GitHub state and immutable evidence bound to exact revisions.
2. Governed registries/checkpoints referenced by GitHub state.
3. Governed shared project memory as an active continuity/coordination layer whose material pointers must resolve to authority before promotion.
4. Current Project chats/files as working context.
5. Ungoverned summaries/caches as advisory navigation.
6. Model recollection/confidence has no authority.

Shared project memory is actively read and written. It may contain verified pointers, working claims, hypotheses, reviewer findings, pending review requests, task state, and coordination metadata. It never independently confers authoritative status.

If shared memory conflicts with a higher-precedence governed source, authority wins; memory becomes stale/conflicted and must be surfaced/repaired rather than silently merged.

## Memory classes

1. **Working memory** — short-lived agent/session context.
2. **Shared project memory** — cross-agent/project continuity and coordination.
3. **Authoritative state** — Git, evidence registries, frozen artifacts, experiment registries, accepted governed decisions.

Working → shared memory is allowed with provenance. Shared memory → authority must pass the same evidence/review/governor requirements as any other proposed authoritative input. Authority may synchronize down into shared memory as verified pointers.

## Session bootstrap and chat-window handoff

Before authoritative work resumes in a fresh chat/session/context window:

1. Read `governance-runtime/shared-memory.json`.
2. Read `governance-runtime/session-state.json`.
3. Verify referenced branches, commits, evidence, review requests, and frozen artifacts.
4. Read applicable governed standards/artifacts.
5. Reconcile memory/chat context against governed state.
6. If they conflict, authority wins and stale/conflicting memory is surfaced/repaired.
7. If authority is unavailable/malformed/unverifiable, enter `GROUNDING_REQUIRED` and do not make an authoritative transition from memory/chat alone.
8. Do not require the user to restate authoritative definitions when governed state exists.

A chat boundary may affect convenience only, not claim status, experiment status, revision identity, review status, evidence validity, promotion eligibility, or release outcome.

## Live state classes

Material content may be typed as:

- `WORKING_PROPOSAL`
- `UNVERIFIED_CLAIM`
- `SOURCE_VERIFIED`
- `INDEPENDENTLY_REVIEWED`
- `PROMOTABLE`
- `ACCEPTED_DECISION`
- `GOVERNED_REQUIREMENT`
- `AMBIGUOUS`
- `INSUFFICIENT_EVIDENCE`
- `CONTRADICTED`
- `RETRACTED`
- `NEEDS_REASSESSMENT`
- `PENDING_INDEPENDENT_REVIEW`
- `PENDING_EXTERNAL_REVIEW`
- `MEMORY_STALE`
- `MEMORY_CONFLICT`
- `GROUNDING_REQUIRED`

Repetition, paraphrase, summary, model confidence, shared-memory replication, or multi-model agreement cannot upgrade status.

## Review policy versus platform mode

Review **requirement** and platform **mode** are separate dimensions.

### Review levels

- `NONE` — no review requested.
- `RECOMMENDED` — primary R1 may recommend independent review for additional confidence; skipping it has no authority consequence because the result is not crossing a mandatory authority boundary.
- `REQUIRED` — deterministic governance policy requires independent review before a material authoritative transition. In manual mode the user may decline the call, but the protected transition remains pending/non-authoritative.

R1 may raise a non-mandatory result from `NONE` to `RECOMMENDED`. R1 may not lower a deterministic `REQUIRED` review because it is confident.

### Platform modes

#### `AUTO_MODE`

R1/platform produces the result, review policy evaluates the level, and any `RECOMMENDED` or `REQUIRED` review is automatically dispatched through configured provider APIs. `REQUIRED` transitions remain blocked until valid review evidence and deterministic gates pass.

#### `MANUAL_MODE`

R1/platform shows its answer first. When review level is `RECOMMENDED` or `REQUIRED`, the UI shows review controls such as `Ask Claude` and `Ask DeepSeek`. No provider API is called until the user selects a reviewer.

For `RECOMMENDED`, the user may ignore the buttons. For `REQUIRED`, the user may decline the call, but the protected authoritative transition stays `PENDING_INDEPENDENT_REVIEW`; the answer remains only a proposal/non-authoritative result.

Changing `AUTO_MODE` ↔ `MANUAL_MODE` changes who initiates a review call, never evidence requirements, reviewer-independence rules, review validity, deterministic governor, or authority semantics.

## Mandatory independent-review triggers

Independent review is mandatory before any of these becomes authoritative:

- experiment adjudication (`PASS`, `BOUNDED_PASS`, `FAIL`, `NOT_TESTED`);
- material scientific-failure classification that changes repair path, fixture, frozen test, mechanism, or conclusion;
- modification of frozen tests/fixtures/preregistration/acceptance criteria/expected results after exposure;
- material architecture/governance mechanism change;
- promotion of material external evidence/research conclusion;
- authoritative retraction/supersession with downstream impact;
- governed requirement acceptance derived from contested/model-generated evidence;
- release/deploy/merge/production mutation/completion or equivalent terminal action;
- material reviewer/evidence disagreement resolution;
- anything a governing standard marks as requiring independent judgment.

Routine drafting, formatting, deterministic replay of already-authorized actions, and narrow construction behind frozen gates normally do not require review unless R1 recommends it.

## ReviewRequest, ReviewEvidence, and transport

Every mandatory review uses a transport-neutral `ReviewRequest` containing at least request identity, trigger, exact reviewed artifact revision, proposer identity, required reviewer/provider class, blind-review requirement, questions, evidence references, expected output, and integrity hash.

Returned `ReviewEvidence` is bound to the exact request and reviewed artifact revision.

Supported review transports/initiations:

- `AUTOMATIC_API` — `AUTO_MODE`; platform automatically calls the configured provider API.
- `USER_INITIATED_API` — production `MANUAL_MODE`; user presses `Ask Claude`/`Ask DeepSeek`, which calls the same provider adapter/API semantics used by auto mode.
- `MANUAL_RELAY` — fallback used in this ChatGPT collaboration when direct provider API access is unavailable; the user manually relays a portable review packet.

`AUTOMATIC_API` and `USER_INITIATED_API` differ only in initiation. They must deliver the same governed ReviewRequest semantics through the same provider-adapter contract.

`MANUAL_RELAY` is not the production manual-mode architecture. It is a fallback for environments where direct reviewer APIs are unavailable.

Platform mode and review transport must never be inputs to promotion eligibility.

## Self-contained manual review bundle

A reviewer used through `MANUAL_RELAY` must be assumed to have **zero repository/tool access** unless explicitly proven otherwise.

Therefore manual relay requires a self-contained portable bundle containing:

- exact ReviewRequest;
- exact reviewed commit identity;
- embedded UTF-8 contents of every artifact necessary for review;
- per-artifact SHA-256 content hashes;
- relevant CI/evidence summary;
- bundle integrity hash;
- `repository_access_required: false`.

The reviewer must be able to perform the requested review from the bundle alone. Repository links may be optional metadata but cannot be required.

When the current execution environment cannot persist the generated external packet back into Git, governed Git must retain a compact portable-bundle manifest containing at least the review request ID, exact reviewed candidate revision, exported filename, whole-packet SHA-256, per-artifact hashes/lengths, CI identity, and `repository_access_required: false`. The manifest is evidence of what packet was exported; it is **not** a substitute for the full self-contained packet. Before returned review evidence is accepted, the actual packet used for manual relay must be available and its hash/bindings must match the governed manifest. A missing or mismatched external packet therefore fails closed even if its manifest exists.

If the bundle is missing, malformed, corrupted, targets the wrong revision, or rebinds ReviewRequest semantics, manual review remains pending/fails closed.

## Reviewer independence

A review is independent only when the reviewer is not merely the proposer reviewing its own prior hidden reasoning/context.

Where practical bind reviewer provider/model identity, exact artifact/evidence identity, review input scope, result, run/timestamp when material, and blind-review status where required.

Second-model agreement is consensus metadata, not evidence. Independent review cannot bypass deterministic evidence gates.

If independence cannot be established, record `REVIEW_INDEPENDENCE_UNPROVEN` and do not count it as required review.

## Automatic API behavior

Provider adapters used by both `AUTOMATIC_API` and `USER_INITIATED_API` must:

1. receive the same logical ReviewRequest;
2. preserve request/artifact identity;
3. record provider/model/run identity when material;
4. validate returned ReviewEvidence;
5. fail closed on timeout, provider error, malformed response, wrong artifact, independence failure, or unavailable provider;
6. preserve duplicate/retry idempotency and reject semantic rebinding.

Switching between auto and manual product modes must not require changing governance policy or provider-adapter semantics.

## Manual relay behavior for this collaboration

When this collaboration reaches a review boundary and no connected reviewer API exists, the assistant states clearly `REVIEW NEEDED — <REVIEWER> — <review_request_id>` and provides/uploads the self-contained portable bundle. The user relays it manually. Returned output is validated against the exact request, artifact revision, reviewer identity, output contract, independence requirement, and governed portable-bundle manifest before it counts as review evidence.

## Shared-memory continuity

When authoritative state changes:

1. persist authoritative state first;
2. synchronize shared memory afterward;
3. if memory synchronization fails after authoritative persistence, authority remains valid and memory becomes stale;
4. surface/preserve the memory failure;
5. if authoritative persistence itself failed, block authoritative completion instead of relying on memory.

## Frozen evidence and repair discipline

For falsification/acceptance work:

1. preregister/freeze before scientific exposure where required;
2. preserve first exposure;
3. classify before repair;
4. never change frozen test/fixture/expectation merely to obtain green;
5. changing frozen artifacts after exposure requires explicit new boundary and independent review;
6. preserve superseded/invalid attempts;
7. construction green is not scientific acceptance when the method requires a later freeze/first-exposure acceptance run.

## Failure taxonomy

At minimum surface/record:

- `MEMORY_OVERRIDES_AUTHORITY`
- `SHARED_MEMORY_STALE_UNDETECTED`
- `SHARED_MEMORY_CONFLICT_SILENTLY_MERGED`
- `SHARED_MEMORY_UNVERIFIED_CLAIM_PROMOTED`
- `MODEL_CONFIDENCE_BYPASSED_REVIEW`
- `MANDATORY_REVIEW_SKIPPED`
- `REVIEW_INDEPENDENCE_UNPROVEN`
- `REVIEW_WRONG_REVISION_ACCEPTED`
- `REVIEW_TRANSPORT_CHANGED_POLICY`
- `PLATFORM_MODE_CHANGED_AUTHORITY`
- `MANUAL_MODE_REQUIRED_REVIEW_TREATED_AS_OPTIONAL_AUTHORITY`
- `MANUAL_RELAY_SELF_COMPLETED`
- `MANUAL_RELAY_REQUIRED_REPOSITORY_ACCESS`
- `PORTABLE_REVIEW_BUNDLE_TAMPERED`
- `PORTABLE_REVIEW_MANIFEST_MISMATCH`
- `API_FAILURE_TREATED_AS_APPROVAL`
- `REVIEW_ID_SEMANTIC_REBIND`
- `CONSENSUS_AS_EVIDENCE`
- `FROZEN_ARTIFACT_CHANGED_AFTER_EXPOSURE_WITHOUT_REVIEW`
- `FAILURE_HISTORY_REWRITTEN`
- `UNVERIFIED_PARENT_PROMOTED`
- `TERMINAL_AUTHORITY_SELF_GRANTED`

## Live operating procedure

For every material cycle:

1. Recover continuity from shared project memory.
2. Verify pointers against authoritative Git/evidence.
3. Reconcile stale/conflicting memory.
4. Classify work and review level.
5. Preregister/freeze when applicable.
6. Execute narrow work.
7. Preserve first failures/exact revisions.
8. Apply review policy.
9. Use platform mode to choose automatic dispatch vs user review controls.
10. Use the selected transport without changing policy.
11. Validate ReviewEvidence and, for manual relay, the actual packet against its governed manifest.
12. Apply deterministic governor/evidence gate.
13. Persist authoritative checkpoint.
14. Synchronize shared memory.
15. New chat resumes from shared memory then verifies Git.

## Known limitation

This runtime cannot force the underlying ChatGPT product to bootstrap Git/shared memory or directly call Claude/DeepSeek in every conversation. Compliance here is operational. If authoritative evidence cannot be verified, state remains `GROUNDING_REQUIRED`; if required external review cannot be obtained, the protected transition remains pending.
