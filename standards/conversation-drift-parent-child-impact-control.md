# Workflow Drift and Parent-Child Impact Control

Status: **PROPOSED — REVIEW REQUIRED — NON-AUTHORITATIVE**

Authority effect: **NONE_EVIDENCE_ONLY**

Purpose: prevent workflow drift, blocking dependencies, nested subtasks, operator redirection, or automated sub-workflows from silently replacing, mutating, invalidating, or bypassing the governed parent workflow.

## 1. Platform scope

The platform supports only API-backed governed execution.

Supported orchestration modes are:

- `MANUAL_GOVERNED`: a human operator initiates, approves, rejects, or selects governed transitions through the platform UI/API.
- `AUTOMATIC_GOVERNED`: policy-authorized orchestration initiates eligible transitions automatically.

Both modes MUST use the same durable workflow engine, API/provider adapters, authoritative state store, append-only evidence/governance ledger, identity model, idempotency controls, reviewer isolation, exact-artifact binding, and authority gates.

Manual copy/paste transport of reviewer or worker results is **not a supported platform execution mode**.

The difference between manual and automatic mode is who initiates or approves a transition, not how work or evidence is transported.

## 2. Core invariant

A change in UI focus, operator intent, active task, agent plan, or automated orchestration focus does not itself change workflow authority.

A parent workflow remains bound to its exact checkpoint, candidate, evidence, approvals, reviewer/test barriers, and next permitted action unless an explicit governed impact decision says otherwise.

## 3. Task relationship model

Every material diversion from the current governed objective must be classified as one of:

- `NON_BLOCKING_CHILD`
- `BLOCKING_CHILD`
- `DEPENDENCY_CHILD`
- `INCIDENT_CHILD`
- `INFORMATION_ONLY_CHILD`

Every child task must durably bind:

- `child_workflow_id`
- `parent_workflow_id`
- relationship type
- reason opened
- initiating principal/service
- orchestration mode
- parent checkpoint at suspension
- parent candidate/artifact manifest identity
- parent policy/schema version
- parent pending gates
- parent authority state
- exact return condition
- child authority scope
- API request/effect identities needed for child execution

A child may not silently become the parent because it becomes the currently displayed, most recently active, or longest-running task.

## 4. Parent suspension rule

When a blocking or dependency child is opened, the parent must transition through an authoritative workflow event to an explicit suspended state such as:

- `PARENT_PAUSED_CHILD_ACTIVE`
- `PARENT_PAUSED_PENDING_CHILD_IMPACT`

Suspension must preserve the exact parent resume point.

A suspended parent is not completed, abandoned, failed, passed, adjudicated, repaired, merged, released, deployed, or otherwise advanced merely because execution focus moved elsewhere.

## 5. Child authority boundary

A child task has authority only within its declared scope.

A child may discover facts, evidence, or controls that affect the parent, but it may not directly:

- rewrite parent evidence;
- mark parent reviews/tests complete;
- broaden parent approvals;
- alter parent candidate identity without explicit parent-impact handling;
- adjudicate the parent;
- grant parent qualification, merge, release, deployment, or terminal authority.

Child-produced API responses and model judgments remain evidence subject to the parent policy; they do not become authority merely because they were produced by an automated workflow.

## 6. Parent-impact classification

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

## 7. ChildImpactRecord requirements

A `ChildImpactRecord` must bind, at minimum:

- parent workflow ID;
- child workflow ID;
- parent checkpoint ID/sequence;
- parent candidate manifest digest;
- child candidate/result digest;
- child disposition;
- exact impact classification;
- affected parent artifacts/evidence/gates;
- unaffected parent artifacts/evidence/gates;
- stale evidence set, if any;
- required re-review/re-test/rebinding actions, if any;
- exact next permitted parent action;
- deciding principal/role or authorized policy component;
- orchestration mode;
- decision timestamp/authoritative sequence;
- policy/schema version;
- predecessor record digest;
- idempotency/effect identity for the impact decision.

The record is evidence of impact handling; it does not itself grant terminal authority unless a separately qualified policy explicitly grants that transition.

## 8. Evidence staleness rule

If a child changes any parent assumption that existing evidence relied upon, the affected evidence must be evaluated for staleness.

Examples include changes to:

- candidate artifact manifest/digests;
- policy or schema version;
- reviewer independence requirements;
- acceptance/falsification criteria;
- authority source or ordering rule;
- identity or credential requirements;
- workflow stage prerequisites;
- provider/model qualification requirements;
- API request/result binding rules.

Staleness must be evidence-specific. A child must not force a blanket restart unless the governing policy requires it.

## 9. Review-process integrity impacts

If a child discovers a flaw in the review/test process rather than the parent candidate itself, the impact decision must distinguish between:

- candidate evidence remains valid but future orchestration mechanics change;
- only some reviewer/test evidence becomes stale;
- the entire review/test set must restart;
- parent candidate itself becomes invalid.

This distinction must be recorded in platform state and must not be inferred from UI/conversation context.

## 10. Return-to-parent rule

A child may return control to the parent only when:

1. the child reaches its declared stopping condition;
2. required child evidence is durably preserved;
3. a `ChildImpactRecord` exists if the child can affect the parent;
4. the parent candidate/checkpoint binding is revalidated;
5. any stale evidence is explicitly marked;
6. pending sibling/blocking children are evaluated;
7. the exact next permitted parent action is derived from the bound parent policy plus impact records.

If any condition is unresolved, return must fail closed.

## 11. Nested child tasks

Nested children must preserve the complete durable task graph.

At minimum:

`ROOT_PARENT -> CHILD_1 -> CHILD_2 -> ... -> CURRENT`

Each child must retain its own parent pointer, opening reason, status, blocking relationship, return condition, orchestration mode, and impact state.

Completion of a nested child returns to its immediate parent impact boundary, not automatically to the root workflow.

## 12. Workflow drift detection

Every consequential API action must be checked against the active workflow/task graph and policy binding.

If the proposed action does not belong to the active workflow or an explicitly opened child scope, the platform must emit `WORKFLOW_DRIFT_DETECTED` and reject consequential progression until the task relationship is classified.

UI focus, chat text, operator navigation, agent reasoning, or model output may suggest a task change, but none may mutate governed workflow state without an authoritative transition.

## 13. Operator redirection, cancellation, and supersession

An operator changing focus does not erase or complete a prior governed workflow.

Unless an authorized cancellation or supersession transition is submitted and accepted, the prior workflow remains active or suspended according to its relationship state.

Cancellation/supersession must bind the exact workflow, candidate manifest, principal, action scope, nonce/idempotency identity, and policy version.

## 14. Concurrent parent/child mutation

A child that may mutate the same candidate/artifacts as its parent must block parent review, adjudication, or qualification until impact handling is complete.

The workflow engine must enforce qualified concurrency controls such as single-writer leases/CAS plus fencing tokens for consequential writes.

A UI/device/session is not the concurrency authority; the workflow engine is.

## 15. Reviewer isolation under drift

Opening a child investigation during a multi-review parent workflow must not leak substantive findings between still-independent reviewers.

Reviewer/provider requests must be generated from policy-scoped evidence views. Pending reviewers receive only the artifact/evidence scope authorized for that independent review.

A child may record reviewer status and process state, but substantive reviewer findings remain access-controlled until the protocol explicitly enters cross-review/adjudication.

## 16. API execution requirements

Every external worker/reviewer/model invocation must durably bind at minimum:

- workflow ID;
- task/child ID;
- parent workflow ID where applicable;
- candidate/artifact manifest digest;
- policy/schema version;
- provider/model/worker identity;
- request ID;
- intent-level idempotency key;
- request payload digest;
- response digest;
- lifecycle state;
- evidence visibility scope;
- effect/reconciliation state;
- authoritative sequence/event reference.

A retry, timeout, device change, UI reload, or orchestration restart must not create a duplicate governance effect.

## 17. Manual versus automatic governed mode

`MANUAL_GOVERNED` and `AUTOMATIC_GOVERNED` share the same execution path after authorization.

In `MANUAL_GOVERNED`, a human may be required to approve an eligible transition before the workflow engine sends the API request or applies the next governed action.

In `AUTOMATIC_GOVERNED`, a qualified policy may authorize the workflow engine to initiate that same transition without a synchronous human approval.

Neither mode permits external copy/paste evidence injection as a normal execution path.

Any administrative evidence import capability, if ever added, must be a separately governed exceptional recovery mechanism and must not masquerade as ordinary manual mode.

## 18. Current bounded operating rule for design work

Until this standard is reviewed and qualified:

- model the production platform as API-backed only;
- do not add copy/paste reviewer transport as a product feature;
- treat human involvement as governed approval/selection through platform state;
- preserve parent resume points and pending barriers;
- require explicit impact classification before a blocking child permits parent resumption.

## 19. Current project application

For the present governed-platform design work:

- Parent: MVP independent-review workflow.
- Parent state: `PARENT_PAUSED_PENDING_CHILD_IMPACT`.
- Child 1: continuity/resumption governance.
- Child 2: workflow-drift and parent-child impact governance.
- Parent reviewer barriers remain pending and unchanged.
- These development-time review activities do not imply that copy/paste is a supported runtime platform mode.

## 20. Freeze condition

This standard must not be frozen until its associated API-backed workflow-drift/parent-child falsification matrix is independently reviewed and executed to the required policy threshold.

This document grants no merge, release, production, qualification, adjudication, or terminal authority.