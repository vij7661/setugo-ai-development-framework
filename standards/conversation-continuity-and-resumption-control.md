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
