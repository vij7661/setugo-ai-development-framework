# Workflow Drift and Parent-Child Impact Control

Status: **PROPOSED — REVIEW REQUIRED — NON-AUTHORITATIVE**

Authority effect: **NONE_EVIDENCE_ONLY**

Purpose: prevent workflow drift, blocking dependencies, nested subtasks, operator redirection, automated sub-workflows, or R1 context loss from silently replacing, mutating, invalidating, or bypassing the governed parent workflow.

## 1. Platform scope

The platform supports only API-backed governed execution.

Supported orchestration modes are:

- `MANUAL_GOVERNED`: a human operator initiates, approves, rejects, or selects governed transitions through the platform UI/API.
- `AUTOMATIC_GOVERNED`: policy-authorized orchestration initiates eligible transitions automatically.

Both modes MUST use the same durable workflow engine, API/provider adapters, authoritative state store, append-only evidence/governance ledger, identity model, idempotency controls, reviewer isolation, exact-artifact binding, and authority gates.

Manual copy/paste transport of reviewer or worker results is **not a supported platform execution mode**.

The difference between manual and automatic mode is who initiates or approves a transition, not how work or evidence is transported.

## 2. Core invariant

A change in UI focus, operator intent, active task, agent plan, model output, conversation/session, device, or orchestration focus does not itself change workflow authority.

A parent workflow remains bound to its exact checkpoint, candidate, evidence, approvals, reviewer/test barriers, and next permitted action unless an explicit governed impact decision says otherwise.

Conversation, model memory, user-memory summaries, and client-local state are advisory continuity aids only. They may help locate authoritative state but may not override it.

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

Every consequential action must be checked against the active workflow/task graph and policy binding before it is allowed to change authoritative state.

If the proposed action does not belong to the active workflow or an explicitly opened child scope, the platform must emit `WORKFLOW_DRIFT_DETECTED` and reject consequential progression until the task relationship is classified.

UI focus, chat text, operator navigation, agent reasoning, model output, remembered context, or a newly opened conversation may suggest a task change, but none may mutate governed workflow state without an authoritative transition.

## 13. R1 drift-sentinel responsibility

R1 is the designated user-facing drift sentinel for governed orchestration.

R1 owns **drift awareness, drift declaration, user disclosure, and workflow-preservation proposals**. R1 does **not** own terminal impact authority and must not become the sole source of truth about whether drift occurred.

Before R1 performs or proposes any consequential action, R1 must receive or recover an authoritative workflow-context envelope containing at minimum:

- root workflow ID;
- current parent workflow ID;
- current task/child ID;
- current phase;
- authoritative checkpoint ID/sequence;
- exact candidate/artifact manifest digest;
- bound policy/schema version;
- pending reviewer/test/approval/authority gates;
- active blocking and non-blocking children;
- exact next permitted actions;
- explicitly prohibited actions where policy defines them;
- source/version of the authoritative workflow state.

R1 must compare the new user/operator intent and its own proposed action against that envelope and classify the intent as one of:

- `SAME_WORKFLOW`
- `INFORMATION_ONLY_CHILD`
- `NON_BLOCKING_CHILD`
- `BLOCKING_CHILD`
- `DEPENDENCY_CHILD`
- `INCIDENT_CHILD`
- `DRIFT_CONFLICT_OR_INSUFFICIENT_STATE`

The classification is a proposal until the platform/policy validates any consequential transition that depends on it.

R1 may not unilaterally downgrade a relationship from blocking/dependency/incident to non-blocking/information-only when that downgrade would remove or weaken a gate. Such a downgrade requires the authorized policy/role and a durable event.

## 14. R1 user-disclosure rule

If R1 detects **material workflow drift**, R1 must explicitly tell the user.

The disclosure must identify, at minimum:

- the current parent workflow;
- the current parent checkpoint/resume point;
- the proposed diversion/child;
- the proposed relationship classification;
- whether parent progression is paused or unaffected;
- whether parent-impact handling will be required before return.

In `MANUAL_GOVERNED`, material drift disclosure must occur before a diverted consequential workflow proceeds, and any user approval required by policy must be captured as a separately bound approval object.

In `AUTOMATIC_GOVERNED`, a qualified policy may permit the transition without synchronous user approval, but R1 must still surface the material drift and resulting parent/child state to the user. Automatic mode removes an approval wait only where policy permits; it does not remove the disclosure obligation.

Routine information-only branching that has no authority, candidate, evidence, gate, or parent-progression effect may be recorded without interruptive disclosure unless policy requires otherwise.

## 15. R1 self-drift and independent enforcement

R1 itself is an untrusted participant with respect to authoritative workflow state. A new chat, context truncation, stale memory, faulty summary, model substitution, or confident reasoning error may cause R1 to drift.

Therefore, the platform must independently validate every consequential R1-proposed action against authoritative workflow/task state.

If R1 says `SAME_WORKFLOW` or otherwise fails to detect drift, but the proposed action is outside authorized scope, the platform must reject the action and durably record a self-drift event such as:

`R1_SELF_DRIFT_BLOCKED`

The rejection must preserve:

- R1's proposed action;
- authoritative expected scope;
- conflicting workflow/task/candidate/policy bindings;
- rejection reason;
- authoritative sequence/checkpoint;
- resulting parent/child state;
- prior failure history.

R1 may then correct its behavior, but the original self-drift failure must not be rewritten as though it never occurred.

If R1 is unavailable or cannot establish authoritative state, consequential progression must fail closed or transfer only through a separately qualified fallback role/policy. R1 unavailability must never create an unguarded execution path.

## 16. Source precedence across development/testing and runtime

During the present development/testing stage, GitHub/frozen project artifacts and exact committed checkpoints are the durable project source of truth for workflow recovery. R1 may use conversational memory to locate those artifacts, but memory must not override them.

If memory/chat context conflicts with the exact GitHub/frozen checkpoint, R1 must surface the conflict and use the durable state. If the required durable state cannot be established, R1 must return an insufficient/conflict state rather than guess.

In the eventual runtime platform, GitHub is not the runtime workflow authority. The authoritative source becomes the platform workflow engine plus governance/evidence ledger and their qualified recovery rules.

## 17. R2/R3 drift awareness and reviewer isolation

R2, R3, and other independent reviewers/workers must not depend on R1's natural-language narrative to know workflow drift state.

When drift metadata is relevant to their task, the platform must construct a policy-scoped context from authoritative workflow state. It may include the minimum necessary facts such as:

- parent workflow and checkpoint;
- parent paused/active status;
- existence and type of a blocking child;
- exact candidate/policy binding;
- the reviewer's own pending/completed status;
- whether impact adjudication is unresolved.

It must not disclose another reviewer's substantive findings, R1's persuasive interpretation, expected agreement, or adjudication conclusions unless the governing protocol has explicitly entered a stage where that information is authorized.

Thus, R1 owns user-facing disclosure while the platform owns machine-facing workflow truth.

## 18. Operator redirection, cancellation, and supersession

An operator changing focus does not erase or complete a prior governed workflow.

Unless an authorized cancellation or supersession transition is submitted and accepted, the prior workflow remains active or suspended according to its relationship state.

Cancellation/supersession must bind the exact workflow, candidate manifest, principal, action scope, nonce/idempotency identity, and policy version.

## 19. Concurrent parent/child mutation

A child that may mutate the same candidate/artifacts as its parent must block parent review, adjudication, or qualification until impact handling is complete.

The workflow engine must enforce qualified concurrency controls such as single-writer leases/CAS plus fencing tokens for consequential writes.

A UI/device/session is not the concurrency authority; the workflow engine is.

## 20. Reviewer isolation under drift

Opening a child investigation during a multi-review parent workflow must not leak substantive findings between still-independent reviewers.

Reviewer/provider requests must be generated from policy-scoped evidence views. Pending reviewers receive only the artifact/evidence scope authorized for that independent review.

A child may record reviewer status and process state, but substantive reviewer findings remain access-controlled until the protocol explicitly enters cross-review/adjudication.

## 21. API execution requirements

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

A retry, timeout, device change, UI reload, conversation restart, or orchestration restart must not create a duplicate governance effect.

## 22. Manual versus automatic governed mode

`MANUAL_GOVERNED` and `AUTOMATIC_GOVERNED` share the same execution path after authorization.

In `MANUAL_GOVERNED`, a human may be required to approve an eligible transition before the workflow engine sends the API request or applies the next governed action.

In `AUTOMATIC_GOVERNED`, a qualified policy may authorize the workflow engine to initiate that same transition without a synchronous human approval.

Neither mode permits external copy/paste evidence injection as a normal execution path.

Any administrative evidence import capability, if ever added, must be a separately governed exceptional recovery mechanism and must not masquerade as ordinary manual mode.

## 23. Relationship to EXP-K conversational drift control

This standard does not replace `standards/conversational-drift-contamination-control.md` or EXP-K.

EXP-K governs **claim/evidence contamination**: unsupported claims, status laundering, repetition, memory conflicts, retractions, and authoritative grounding of factual/evidentiary state.

This standard governs **workflow/task drift**: losing the active parent, changing stages, skipping barriers, opening children, returning to the wrong checkpoint, misclassifying parent impact, or allowing R1/context loss to move the workflow outside authorized scope.

Where a workflow-drift event also introduces or propagates unsupported claims, both controls apply. Workflow recovery does not validate claims, and claim validation does not authorize a workflow transition.

## 24. Current bounded operating rule for development/testing work

Until this standard is reviewed and qualified:

- testing/review of this candidate is manual; do not use external reviewer/model API calls;
- use exact frozen GitHub/project state to recover the current development workflow;
- model the production platform as API-backed only;
- do not add copy/paste reviewer transport as a product feature;
- treat human involvement as governed approval/selection through platform state;
- preserve parent resume points and pending barriers;
- require explicit impact classification before a blocking child permits parent resumption;
- R1 must disclose material drift to the user and must not treat its own memory as authoritative.

## 25. Current project application

For the present governed-platform design work:

- Parent: MVP independent-review workflow.
- Parent state: `PARENT_PAUSED_PENDING_CHILD_IMPACT`.
- Child 1: continuity/resumption governance.
- Child 2: workflow-drift and parent-child impact governance.
- Parent reviewer barriers remain pending and unchanged.
- R1 must recover this project state from the exact durable project checkpoint before consequential continuation after a chat/session/device boundary.
- These development-time manual review activities do not imply that copy/paste is a supported runtime platform mode.

## 26. Freeze condition

This standard must not be frozen until its associated workflow-drift/parent-child falsification matrix, including R1 self-drift and disclosure cases, is independently reviewed and executed to the required policy threshold.

This document grants no merge, release, production, qualification, adjudication, or terminal authority.