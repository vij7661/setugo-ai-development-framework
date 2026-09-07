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
