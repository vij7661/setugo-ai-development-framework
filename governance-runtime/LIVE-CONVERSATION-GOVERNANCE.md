# Live Conversation Governance Runtime

## Purpose

This runtime applies the governed-platform rules to the human–LLM development conversation itself so that chat-window changes, context loss, model confidence, summaries, shared-memory drift, or reviewer availability cannot silently change authoritative project state.

This is an operational control for our collaboration, not a claim that the ChatGPT product itself enforces these rules internally. GitHub-governed state remains authoritative.

## Authority versus operational memory

Authority and continuity utility are separate concepts.

For authoritative project decisions, use this precedence deterministically:

1. Governed GitHub state and immutable evidence bound to exact revisions.
2. Governed registries/checkpoints explicitly referenced by GitHub state.
3. Governed shared project memory as an active coordination and continuity layer whose material pointers must resolve to authoritative evidence before promotion.
4. Current Project chats/files as working context.
5. Raw conversation summaries and ungoverned continuity caches as advisory navigation only.
6. Model recollection or confidence has no authority.

Shared project memory is **not ignored**. Agents are expected to read it, use it to locate current work, write useful continuity state back to it, and reconcile it with authoritative references. Shared memory may contain verified pointers, working claims, unresolved hypotheses, reviewer findings, pending review requests, task state, and coordination metadata. It does not independently confer authoritative status.

If shared memory and a higher-precedence governed source conflict, the higher-precedence source wins, the memory entry becomes stale/conflicted, and the discrepancy must be surfaced and repaired rather than silently merged.

## Memory classes

The platform model uses three distinct memory/state classes:

1. **Working memory** — short-lived agent/session context.
2. **Shared project memory** — cross-agent/project continuity and coordination.
3. **Authoritative state** — Git, evidence registries, frozen artifacts, experiment registries, accepted governed decisions.

Information may flow from working memory to shared memory with provenance. Information flowing from shared memory into authoritative state must satisfy the same evidence, review, and governor requirements as any other proposed authoritative input. Authoritative state may be synchronized downward into shared memory as verified pointers/cached continuity.

## Session bootstrap and chat-window handoff

Before resuming authoritative work in a fresh chat/session/context window:

1. Read `governance-runtime/shared-memory.json` to recover current project continuity and outstanding review/work items.
2. Read `governance-runtime/session-state.json` from the governed runtime branch.
3. Verify every authoritative branch, commit, evidence pointer, and frozen artifact referenced by the checkpoint/shared memory.
4. Read the current applicable standards and experiment/adjudication artifacts referenced by the checkpoint.
5. Reconcile shared memory and chat/project context with governed state.
6. If they conflict, use governed state, mark/surface the stale or conflicting memory, and repair shared memory when possible.
7. If governed state is missing, malformed, or cannot be verified, enter `GROUNDING_REQUIRED` and do not make an authoritative transition from memory or conversation alone.
8. Never require the user to restate authoritative experiment definitions when governed state is available.

A chat boundary must affect convenience only, not claim status, experiment status, revision identity, evidence validity, promotion eligibility, review status, or release outcome.

## Live state classes

Conversation/shared-memory content must be treated as one of these states when material:

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

Repetition, paraphrase, summary, model confidence, shared-memory replication, or multi-model agreement cannot upgrade a state.

## Authority boundary

A single LLM may generate proposals, code, tests, hypotheses, analysis, and candidate repairs. A single LLM may not by itself make a material authoritative transition when policy requires independent review.

The governor/policy decides whether review is required. The proposing LLM cannot waive review because it is confident, because another model is unavailable, or because the chosen review transport is manual.

### Mandatory independent-review triggers

Independent review is mandatory before any of the following becomes authoritative:

- experiment adjudication such as `PASS`, `BOUNDED_PASS`, `FAIL`, or `NOT_TESTED`;
- material classification of a scientific failure when the classification changes the repair path, fixture, frozen test, mechanism, or conclusion;
- modification of a frozen test, fixture, preregistration, acceptance criterion, or expected result after exposure;
- architecture/governance mechanism change with material authority consequences;
- promotion of material external evidence or a material external-research conclusion;
- retraction/supersession of previously authoritative claims where downstream artifacts may be affected;
- acceptance of a governed requirement derived from contested or model-generated evidence;
- release, deploy, merge, production mutation, completion authority, or equivalent terminal action;
- resolution of a material disagreement between evidence sources or reviewers;
- any transition explicitly marked by a governing standard as requiring independent judgment.

Review is normally not mandatory for routine non-authoritative drafting, deterministic replay of already-authorized actions, mechanical formatting, or narrow code construction that remains behind frozen acceptance gates.

If required review is unavailable, the state must remain `PENDING_INDEPENDENT_REVIEW` or `PENDING_EXTERNAL_REVIEW`. Unavailability cannot be treated as consent or success.

## Review protocol and transport abstraction

Every mandatory review is represented by a transport-neutral `ReviewRequest` with at least:

- review request identity;
- deterministic trigger;
- reviewed artifact type/reference/exact revision;
- proposer identity;
- required reviewer/provider class;
- blind-review requirement when applicable;
- review questions;
- evidence references;
- expected output contract;
- request integrity hash/state.

Returned review is represented as `ReviewEvidence` bound to the exact request and artifact revision.

Review transport is a separate concern from governance policy. Supported modes are:

- `AUTOMATIC_API` — the platform Review Orchestrator dispatches the exact governed `ReviewRequest` through a configured provider adapter (Claude, DeepSeek, Gemini, etc.) and records the returned `ReviewEvidence`.
- `MANUAL_RELAY` — used in this ChatGPT collaboration when no provider API is available. The assistant surfaces the exact governed review packet in chat, identifies the requested reviewer, and the user relays it manually. The transition remains pending until valid returned review evidence is recorded.

The same Review Policy, ReviewRequest schema, ReviewEvidence validation, independence rules, deterministic evidence gates, and promotion decision apply to both transports.

**Transport must never be an input to promotion eligibility.** Manual mode must not disable, weaken, reconfigure, or replace automatic API behavior. Automatic API failure must fail closed to pending review, just as a missing manual response does.

A manual relay cannot mark its own request completed. An API adapter cannot confer authority merely because a provider returned a response. Both must pass ReviewEvidence validation and the deterministic governor/evidence gate.

## Manual relay operating behavior for this collaboration

When policy requires review and no automatic reviewer integration is available, the assistant must say clearly in chat, for example:

`REVIEW NEEDED — CLAUDE — <review_request_id>`

or

`REVIEW NEEDED — DEEPSEEK — <review_request_id>`

and provide a self-contained review packet bound to an exact artifact commit/evidence set.

Where blind review is required, the packet must not lead the reviewer with the proposer conclusion. It should request an independent disposition and findings from the frozen evidence.

When the user returns the reviewer output, the assistant must validate that it matches the review request, exact artifact revision, required reviewer identity/class, output contract, and independence requirement before counting it as valid review evidence.

## Automatic API behavior for the platform

The production platform may configure one or more provider adapters under `AUTOMATIC_API`. The Review Orchestrator must:

1. receive the same logical ReviewRequest that manual relay would use;
2. select/dispatch through configured provider policy without modifying governance requirements;
3. preserve exact request/artifact binding;
4. record provider/model/run identity when material;
5. validate returned ReviewEvidence;
6. fail closed to pending review on provider error, timeout, malformed response, wrong artifact, independence failure, or unavailable provider;
7. preserve duplicate/retry idempotency and reject semantic rebinding of an existing review request identity.

No production policy may require changing governance rules merely to switch from manual relay to API automation.

## Reviewer independence

A review counts as independent only when the reviewer is not merely the same model rephrasing or reviewing its own prior hidden reasoning/context.

Where practical, bind review evidence to:

- reviewer/model/provider identity;
- reviewed artifact/commit/evidence identity;
- review input scope;
- review result;
- timestamp/run identity when material;
- whether the reviewer was blind to the proposer conclusion before producing its own analysis.

A second model's agreement is consensus metadata, not evidence. Mandatory deterministic evidence gates still apply.

If reviewer independence cannot be established, record `REVIEW_INDEPENDENCE_UNPROVEN` and do not count it as the required independent review.

## External evidence

Material external claims must follow `standards/external-evidence-semantic-validation.md`.

Names, snippets, secondary summaries, shared-memory repetition, model recollection, or reviewer consensus cannot substitute for the required evidence contract. Primary/authoritative evidence outranks lexical similarity and unsupported model interpretation for functional-capability claims.

## Conversational drift, shared memory, and continuity

All continuity behavior must follow `standards/conversational-drift-contamination-control.md`.

Conversation is not authority. Shared project memory is an active governed continuity subsystem but not an independent authority source.

When authoritative state is successfully changed:

1. authoritative persistence occurs first;
2. shared-memory synchronization is attempted afterward;
3. if shared-memory synchronization fails, the authoritative change remains valid if it was already durably persisted;
4. the memory failure is surfaced and recorded, and the memory state is treated as stale until repaired;
5. if the authoritative change itself was not durably persisted, authoritative completion/promotion is blocked instead of relying on memory.

If a continuity/shared-memory read or write fails:

- surface it truthfully;
- never say state was saved/remembered/synchronized/persisted if the write failed;
- continue only from verified governed state when authoritative state is already durable;
- block authoritative completion if the authoritative change itself was not durably persisted;
- preserve the failure in history when material.

## Frozen evidence and repair discipline

For falsification/acceptance work:

1. preregister/freeze the contract before scientific exposure where required;
2. preserve the first exposure result;
3. classify a failure before repair;
4. do not change a frozen test/fixture/expectation merely to obtain green;
5. if a frozen artifact must change after exposure, treat that as a material governance event requiring independent review and a new explicit scientific boundary;
6. preserve superseded/invalid attempts rather than silently rewriting history;
7. a green construction run is not automatically scientific acceptance if the preregistered method requires a later freeze/first-exposure acceptance run.

## Failure taxonomy for live conversation governance

At minimum record/surface these failures when they occur:

- `MEMORY_OVERRIDES_AUTHORITY`
- `SHARED_MEMORY_STALE_UNDETECTED`
- `SHARED_MEMORY_CONFLICT_SILENTLY_MERGED`
- `SHARED_MEMORY_UNVERIFIED_CLAIM_PROMOTED`
- `STALE_CONTEXT_REINTRODUCED`
- `SOURCE_CONFLICT_SILENTLY_MERGED`
- `USER_REPETITION_REQUIRED_FOR_AUTHORITATIVE_RECOVERY`
- `CONTINUITY_WRITE_FALSELY_ACKNOWLEDGED`
- `AUTHORITATIVE_REVISION_NOT_REESTABLISHED`
- `MODEL_CONFIDENCE_BYPASSED_REVIEW`
- `MANDATORY_REVIEW_SKIPPED`
- `REVIEW_INDEPENDENCE_UNPROVEN`
- `REVIEW_WRONG_REVISION_ACCEPTED`
- `REVIEW_TRANSPORT_CHANGED_POLICY`
- `MANUAL_RELAY_SELF_COMPLETED`
- `API_FAILURE_TREATED_AS_APPROVAL`
- `REVIEW_ID_SEMANTIC_REBIND`
- `CONSENSUS_AS_EVIDENCE`
- `FROZEN_ARTIFACT_CHANGED_AFTER_EXPOSURE_WITHOUT_REVIEW`
- `FAILURE_HISTORY_REWRITTEN`
- `UNVERIFIED_PARENT_PROMOTED`
- `TERMINAL_AUTHORITY_SELF_GRANTED`

## Live operating procedure for this collaboration

For every material work cycle:

1. **Recover continuity** — read shared project memory.
2. **Ground** — verify the shared-memory pointers against the current Git checkpoint and relevant authoritative artifacts.
3. **Reconcile** — surface/repair stale or conflicting shared memory.
4. **Classify** — identify whether the requested action is proposal, construction, scientific interpretation, promotion, retraction, or terminal authority.
5. **Pre-register/freeze when applicable** — before exposure.
6. **Execute** — perform the narrow requested work.
7. **Preserve** — record first failures and exact revision/run identities.
8. **Review boundary** — if policy requires review, create/bind a ReviewRequest and choose transport separately.
9. **Manual/API delivery** — use `MANUAL_RELAY` here unless a valid connected provider adapter exists; production may use `AUTOMATIC_API` without policy change.
10. **Validate review evidence** — reviewer agreement cannot bypass evidence requirements.
11. **Governor/evidence gate** — decide promotion deterministically.
12. **Checkpoint** — update authoritative session state after material milestones.
13. **Synchronize shared memory** — write continuity pointers/state after authoritative persistence; surface failures truthfully.
14. **Handoff** — a new chat starts from shared memory, verifies against Git, then resumes.

## User steering and approvals

The user may direct priorities, approve optional actions, select among valid reviewer providers when policy permits, or provide manual external reviewer output. User direction does not rewrite governed evidence or erase prior failures. Terminal/destructive operations retain their own explicit authority requirements.

## Known limitation

This runtime cannot force the underlying ChatGPT product to load Git/shared project memory automatically in every future conversation. Compliance is operational: the assistant must perform the bootstrap/reconciliation check before authoritative continuation. If authoritative Git/evidence access is unavailable in a future chat, authoritative project work remains `GROUNDING_REQUIRED` even if shared memory appears complete.
