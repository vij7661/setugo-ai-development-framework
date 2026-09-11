# Conversation Drift and Parent-Child Impact Control

Status: **PROPOSED — REVIEW REQUIRED — NON-AUTHORITATIVE**

Authority effect: **NONE_EVIDENCE_ONLY**

Purpose: prevent conversational topic drift, side investigations, blocking dependencies, or nested subtasks from silently replacing, mutating, invalidating, or bypassing the governed parent workflow.

## 1. Core invariant

A change in conversational focus does not change workflow authority.

A parent workflow remains bound to its exact checkpoint, candidate, evidence, approvals, reviewer/test barriers, and next permitted action unless an explicit governed impact decision says otherwise.

## 2. Task relationship model

Every material diversion from the current governed objective must be classified as one of:

- `NON_BLOCKING_CHILD`
- `BLOCKING_CHILD`
- `DEPENDENCY_CHILD`
- `INCIDENT_CHILD`
- `INFORMATION_ONLY_CHILD`

Every child task must bind:

- `child_workflow_id`
- `parent_workflow_id`
- relationship type
- reason opened
- parent checkpoint at suspension
- parent candidate/artifact identity
- parent policy/schema version
- parent pending gates
- parent authority state
- exact return condition
- child authority scope

A child may not silently become the parent merely because the conversation spends more turns on it.

## 3. Parent suspension rule

When a blocking or dependency child is opened, the parent must transition to an explicit suspended state such as:

- `PARENT_PAUSED_CHILD_ACTIVE`
- `PARENT_PAUSED_PENDING_CHILD_IMPACT`

Suspension must preserve the exact parent resume point.

A suspended parent is not completed, abandoned, failed, passed, adjudicated, repaired, merged, released, or otherwise advanced merely because focus moved elsewhere.

## 4. Child authority boundary

A child task has authority only within its declared scope.

A child may discover facts or controls that affect the parent, but it may not directly:

- rewrite parent evidence;
- mark parent reviews/tests complete;
- broaden parent approvals;
- alter parent candidate identity without explicit parent-impact handling;
- adjudicate the parent;
- grant parent qualification, merge, release, deployment, or terminal authority.

## 5. Parent-impact classification

Before a child can affect parent progression, an explicit `ChildImpactRecord` must classify the effect as exactly one of:

- `PARENT_UNAFFECTED`
- `PARENT_BLOCKED`
- `PARENT_CONSTRAINT_ADDED`
- `PARENT_EVIDENCE_STALE`
- `PARENT_REVIEW_RESTART_REQUIRED`
- `PARENT_POLICY_REBIND_REQUIRED`
- `PARENT_CANDIDATE_INVALIDATED`
- `PARENT_ABORT_REQUIRED`

No implicit impact classification is allowed.

## 6. ChildImpactRecord requirements

A `ChildImpactRecord` must bind, at minimum:

- parent workflow ID;
- child workflow ID;
- parent checkpoint ID/sequence;
- parent candidate digest/SHA;
- child candidate/result digest;
- child disposition;
- exact impact classification;
- affected parent artifacts/evidence/gates;
- unaffected parent artifacts/evidence/gates;
- stale evidence set, if any;
- required re-review/re-test/rebinding actions, if any;
- exact next permitted parent action;
- deciding principal/role;
- decision timestamp/sequence;
- policy/schema version;
- predecessor record digest where ledger-backed.

The record is evidence of impact handling; it does not itself grant terminal authority unless a separately qualified policy says so.

## 7. Evidence staleness rule

If a child changes any parent assumption that existing evidence relied upon, the affected evidence must be evaluated for staleness.

Examples include changes to:

- candidate bytes/artifact manifest;
- policy or schema version;
- reviewer independence requirements;
- acceptance/falsification criteria;
- authority source or ordering rule;
- identity or credential requirements;
- workflow stage prerequisites.

Staleness must be evidence-specific. A child must not force a blanket restart unless the governing policy requires it.

## 8. Review-process integrity impacts

If a child discovers a flaw in the review/test process rather than the parent candidate itself, the impact decision must distinguish between:

- candidate evidence remains valid but future resume mechanics change;
- only some reviewer/test evidence becomes stale;
- the entire review/test set must restart;
- parent candidate itself becomes invalid.

This distinction must be recorded, not inferred conversationally.

## 9. Return-to-parent rule

A child may return control to the parent only when:

1. the child reaches its declared stopping condition;
2. required child evidence is durably preserved;
3. a `ChildImpactRecord` exists if the child can affect the parent;
4. the parent candidate/checkpoint binding is revalidated;
5. any stale evidence is explicitly marked;
6. the exact next permitted parent action is derived from the parent policy plus the impact record.

If any of these are unresolved, return must fail closed.

## 10. Nested child tasks

Nested children must preserve the complete task stack.

At minimum the durable stack must support:

`ROOT_PARENT -> CHILD_1 -> CHILD_2 -> ... -> CURRENT`

Each child must retain its own parent pointer, opening reason, status, blocking relationship, return condition, and impact state.

Completion of a nested child returns to its immediate parent, not automatically to the root workflow.

## 11. Drift detection

A consequential action must be checked against the current task stack.

If the proposed action does not belong to the active workflow or an explicitly opened child scope, the system must produce `CONVERSATION_DRIFT_DETECTED` and fail closed for consequential progression until the task relationship is classified.

Ordinary informational conversation may continue, but it must not mutate governed state without classification.

## 12. User topic changes

A user changing topic does not erase or complete the prior governed workflow.

Unless the user explicitly cancels or supersedes the parent, the prior workflow becomes suspended or remains active according to the relationship classification.

Explicit cancellation/supersession must itself be recorded against the exact workflow/candidate scope.

## 13. Concurrent parent/child mutation

A child that may mutate the same candidate/artifacts as its parent must block parent review, adjudication, or qualification until impact handling is complete.

The parent and child must not concurrently write to the same governed candidate without qualified concurrency/fencing controls.

## 14. Reviewer isolation under drift

Opening a child investigation during a multi-review parent workflow must not leak substantive findings between still-independent reviewers.

A child may record reviewer status and process state, but substantive reviewer findings remain isolated unless the review protocol explicitly enters cross-review/adjudication.

## 15. Current bounded operating rule

Until this standard is reviewed and qualified:

- when a material diversion occurs, record it as parent/child rather than silently replacing the active goal;
- if the child directly affects the parent, pause the parent and require explicit impact classification before resuming;
- do not repair or modify a frozen parent candidate merely because a child discovered a possible issue unless the parent review/adjudication policy permits it;
- preserve parent resume point and all pending barriers;
- preserve all raw external reviews unchanged as evidence-only.

## 16. Current project application

For the present governed-platform work:

- Parent: MVP independent-review workflow.
- Parent state: `PARENT_PAUSED_PENDING_CHILD_IMPACT`.
- Child 1: conversation continuity/resumption governance.
- Child 2: conversation drift and parent-child impact governance.
- Parent reviewer barriers remain pending and unchanged.
- No child result may silently complete, invalidate, or repair the MVP parent before an explicit impact decision.

## 17. Freeze condition

This standard must not be frozen until the associated parent-child/drift falsification matrix is independently reviewed and executed to the required policy threshold.

This document grants no merge, release, production, qualification, adjudication, or terminal authority.