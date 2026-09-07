# Live Conversation Governance Runtime

## Purpose

This runtime applies the governed-platform rules to the human–LLM development conversation itself so that chat-window changes, context loss, model confidence, summaries, memory, or reviewer availability cannot silently change authoritative project state.

This is an operational control for our collaboration, not a claim that the ChatGPT product itself enforces these rules internally. GitHub-governed state remains authoritative.

## Source precedence

For authoritative project decisions, use this precedence deterministically:

1. Governed GitHub state and immutable evidence bound to exact revisions.
2. Governed registries/checkpoints explicitly referenced by GitHub state.
3. Current Project chats/files as working context only.
4. Chat summaries, continuity caches, and model memory as advisory continuity only.
5. Model recollection or confidence has no authority.

If sources conflict, the higher-precedence source wins and the conflict must be surfaced. Do not silently merge conflicting state.

## Session bootstrap and chat-window handoff

Before resuming authoritative work in a fresh chat/session/context window:

1. Read `governance-runtime/session-state.json` from the governed runtime branch.
2. Verify every referenced active branch and commit still exists.
3. Read the current applicable standards and experiment/adjudication artifacts referenced by the checkpoint.
4. Compare chat/project context with governed state.
5. If they conflict, use governed state and record/surface the discrepancy.
6. If governed state is missing, stale, malformed, or cannot be verified, enter `GROUNDING_REQUIRED` and do not make an authoritative transition from memory or conversation alone.
7. Never require the user to restate authoritative experiment definitions when governed state is available.

A chat boundary must affect convenience only, not claim status, experiment status, revision identity, evidence validity, promotion eligibility, or release outcome.

## Live state classes

Conversation content must be treated as one of these states when material:

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
- `GROUNDING_REQUIRED`

Repetition, paraphrase, summary, model confidence, or multi-model agreement cannot upgrade a state.

## Authority boundary

A single LLM may generate proposals, code, tests, hypotheses, analysis, and candidate repairs. A single LLM may not by itself make a material authoritative transition when the review matrix below requires independent review.

The governor/policy decides whether review is required. The proposing LLM cannot waive review because it is confident.

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

If required review is unavailable, the state must remain `PENDING_INDEPENDENT_REVIEW`. Unavailability cannot be treated as consent or success.

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

Names, snippets, secondary summaries, model recollection, or reviewer consensus cannot substitute for the required evidence contract. Primary/authoritative evidence outranks lexical similarity and unsupported model interpretation for functional-capability claims.

## Conversational drift and continuity

All continuity behavior must follow `standards/conversational-drift-contamination-control.md`.

Conversation is not authority. Raw chat, summaries, memory, and continuity caches may aid navigation but cannot restore, upgrade, retract, or replace governed state.

If a continuity read/write fails:

- surface it truthfully;
- never say the state was saved/remembered/persisted if the write failed;
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
- `STALE_CONTEXT_REINTRODUCED`
- `SOURCE_CONFLICT_SILENTLY_MERGED`
- `USER_REPETITION_REQUIRED_FOR_AUTHORITATIVE_RECOVERY`
- `CONTINUITY_WRITE_FALSELY_ACKNOWLEDGED`
- `AUTHORITATIVE_REVISION_NOT_REESTABLISHED`
- `MODEL_CONFIDENCE_BYPASSED_REVIEW`
- `MANDATORY_REVIEW_SKIPPED`
- `REVIEW_INDEPENDENCE_UNPROVEN`
- `CONSENSUS_AS_EVIDENCE`
- `FROZEN_ARTIFACT_CHANGED_AFTER_EXPOSURE_WITHOUT_REVIEW`
- `FAILURE_HISTORY_REWRITTEN`
- `UNVERIFIED_PARENT_PROMOTED`
- `TERMINAL_AUTHORITY_SELF_GRANTED`

## Live operating procedure for this collaboration

For every material work cycle:

1. **Ground** — read/verify the current Git checkpoint and relevant authoritative artifacts.
2. **Classify** — identify whether the requested action is proposal, construction, scientific interpretation, promotion, retraction, or terminal authority.
3. **Pre-register/freeze when applicable** — before exposure.
4. **Execute** — perform the narrow requested work.
5. **Preserve** — record first failures and exact revision/run identities.
6. **Review boundary** — if the result crosses a mandatory-review trigger, do not call it authoritative until independent review is present and valid.
7. **Governor/evidence gate** — independent-review agreement cannot bypass deterministic evidence requirements.
8. **Checkpoint** — update `governance-runtime/session-state.json` after every material authoritative milestone or change of active workstream.
9. **Handoff** — a new chat resumes by reading the checkpoint first, not by trusting the previous chat summary.

## User steering and approvals

The user may direct priorities, approve optional actions, or provide external reviewer output. User direction does not rewrite governed evidence or erase prior failures. If the user explicitly chooses to override a recommended process for a non-authoritative action, record the deviation when material. Terminal/destructive operations retain their own explicit authority requirements.

## Known limitation

This runtime cannot force the underlying ChatGPT product to load Git automatically in every future conversation. Therefore compliance is operational: the assistant must perform the bootstrap check before authoritative continuation. If Git/tool access is unavailable in a future chat, authoritative project work must remain `GROUNDING_REQUIRED` rather than being reconstructed from memory alone.
