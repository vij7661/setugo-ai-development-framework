# Workflow Drift and Parent-Child Impact Control

Status: **PROPOSED V4 — REVIEW REQUIRED — NON-AUTHORITATIVE**

Authority effect: **NONE_EVIDENCE_ONLY**

Purpose: prevent workflow drift, context loss, blocking dependencies, nested subtasks, operator redirection, or automated orchestration from silently replacing, mutating, invalidating, or bypassing a governed parent workflow. This revision makes R1 accountable for drift awareness and user disclosure while preventing R1 from becoming the authority that validates its own drift decisions.

> Status labels do not enforce any rule. A PASS, BLOCKED, REVIEWED, or similar label has no authority unless the named platform mechanism below commits the required state/event under the bound policy.

## 1. Platform scope

The production platform supports API-backed governed execution only.

Supported orchestration modes:

- `MANUAL_GOVERNED`: a human principal approves/selects governed transitions through platform UI/API.
- `AUTOMATIC_GOVERNED`: a qualified policy authorizes eligible transitions automatically.

Both modes MUST use the same authoritative workflow state, policy/role registry, drift validator, evidence/governance ledger, exact-artifact binding, idempotency controls, reviewer isolation, and authority gates. Manual copy/paste transport of reviewer/worker results is not a supported runtime execution mode.

The present development/testing review of this candidate is manual-only and MUST NOT use external reviewer/model API calls to qualify the draft.

## 2. Named enforcement components

The following logical components are normative. They may share deployment infrastructure, but their authority boundaries MUST remain independently enforceable.

### 2.1 Workflow State Authority (`WSA`)

The `WSA` owns authoritative workflow/task-graph state, checkpoint sequence, candidate binding, active children, pending gates, and current permitted-action set. R1 cannot directly write authoritative WSA state.

### 2.2 Drift Guard Validator (`DGV`)

The `DGV` is the deterministic enforcement boundary outside R1. It validates every consequential R1 proposal against the current WSA state and bound policy before state mutation or external side effect.

The DGV MUST NOT trust R1's classification as authority. It recomputes eligibility from WSA state plus the Policy & Role Registry.

### 2.3 Policy & Role Registry (`PRR`)

The `PRR` owns versioned policy identities, policy digests, role identities, permissions, downgrade authority, impact-decision authority, fallback authority, and transition mappings. A policy/role is qualified only when an exact active registry entry exists for the current workflow scope and revision.

### 2.4 Reviewer Context Builder (`RCB`)

The `RCB` constructs machine-facing context for R2/R3/other independent reviewers from WSA/ledger state. It does not accept R1 narrative as authoritative input.

### 2.5 Disclosure Recorder (`DR`)

The `DR` durably records required user-facing material-drift disclosures and their delivery state. Disclosure and approval are distinct objects.

### 2.6 Governance/Evidence Ledger (`GEL`)

The `GEL` is append-only for authoritative workflow events, R1 proposals, DGV decisions, disclosures, reviewer-context records, impact records, rejected attempts, and preserved RED history.

## 3. Deterministic definitions

For this standard:

- **Consequential action**: any action that can mutate authoritative workflow/task/candidate/policy/evidence/approval/authority state, issue or reconcile an external worker/reviewer/model request, create/cancel/supersede a child, mark evidence stale/valid, or cause an external side effect.
- **Material workflow drift**: a proposed change that would change root/parent/task identity, phase, candidate binding, policy binding, pending gate set, authority state, exact permitted-action set, or create a child with consequential scope. Pure explanation/read-only assistance that cannot affect those fields is not material drift.
- **Information-only child**: a child whose policy scope contains no consequential permission and whose completion cannot mutate parent state without a separate governed impact transition.
- **Qualified policy**: an active PRR entry bound by policy ID, version, digest, scope, effective sequence, and permitted transition set.
- **Authorized role**: a principal/service role present in the bound PRR version with an exact permission for the requested transition.
- **Exact next permitted action**: the set computed by DGV from WSA state machine + bound PRR policy; not prose supplied by R1.
- **Unaffected**: a result established by deterministic dependency comparison showing no changed parent candidate digest, policy dependency, gate dependency, evidence dependency, authority dependency, or acceptance/falsification dependency. Absence of a discovered change is not sufficient.
- **Stale evidence**: evidence whose bound candidate/policy/identity/gate/assumption dependency no longer matches current authoritative dependencies.

If a required term cannot be deterministically resolved from WSA/PRR/GEL state, DGV returns `DRIFT_CONFLICT_OR_INSUFFICIENT_STATE` and consequential progression is blocked.

## 4. Core invariant

Conversation, UI focus, device, chat/session, model memory, user-memory summaries, agent reasoning, or the most recently active task are continuity aids only. They do not change workflow authority.

A parent remains bound to its exact checkpoint, candidate, evidence, approvals, reviewer/test barriers, and permitted-action set until WSA commits an authorized transition.

## 5. Workflow Context Envelope (`WCE`)

Before R1 performs or proposes a consequential action, it MUST receive a WSA-issued `WorkflowContextEnvelope`.

Required fields:

- `envelope_id`
- `schema_version`
- `root_workflow_id`
- `parent_workflow_id`
- `current_task_id`
- `current_phase`
- `checkpoint_id`
- `checkpoint_sequence`
- `workflow_graph_digest`
- `candidate_manifest_digest`
- `policy_id`
- `policy_version`
- `policy_digest`
- `pending_gate_set_digest`
- `active_children_digest`
- `permitted_action_set_digest`
- `prohibited_action_set_digest` where applicable
- `issued_authority_sequence`
- `issued_at`
- `expires_at` or policy-defined maximum age
- `issuer_id = WSA`
- `key_id`
- integrity signature/MAC over the canonical envelope

The signing/MAC key MUST be inaccessible to R1. The envelope schema/version and key identity are validated by DGV.

### 5.1 WCE validation algorithm

Before a consequential action, DGV MUST verify:

1. schema version supported;
2. issuer is the authorized WSA identity;
3. signature/MAC valid;
4. envelope workflow/task IDs match the submitted action;
5. checkpoint sequence equals the current WSA checkpoint for that action scope;
6. candidate/policy/graph/gate/action-set digests match current WSA/PRR state;
7. envelope is not expired/stale/replayed beyond policy;
8. action idempotency/nonce is valid;
9. no newer conflicting WSA sequence supersedes the envelope.

Any failure emits `CONTEXT_ENVELOPE_REJECTED`, returns `DRIFT_CONFLICT_OR_INSUFFICIENT_STATE`, and blocks the consequential action.

Time alone is never sufficient freshness proof; authoritative sequence/digest comparison is mandatory.

## 6. R1 drift-sentinel responsibility

R1 is the designated user-facing drift sentinel. R1 owns:

- drift awareness;
- proposed drift classification;
- explicit material-drift disclosure content;
- explanation of parent checkpoint/resume point;
- proposal to open/classify a child;
- proposal to preserve/return to parent.

R1 does not own workflow truth, impact authority, downgrade authority, reviewer-isolation authority, or terminal authority.

R1 classifies intent as one of:

- `SAME_WORKFLOW`
- `INFORMATION_ONLY_CHILD`
- `NON_BLOCKING_CHILD`
- `BLOCKING_CHILD`
- `DEPENDENCY_CHILD`
- `INCIDENT_CHILD`
- `DRIFT_CONFLICT_OR_INSUFFICIENT_STATE`

This classification is always a proposal until DGV validates any consequential effect.

## 7. R1 Drift Decision Proposal

Every consequential R1 proposal MUST be durably preserved before execution with:

- `proposal_id`
- `r1_identity`
- `WCE.envelope_id`
- user/operator intent digest
- proposed action type
- proposed relationship classification
- proposed parent/child IDs
- proposed candidate/policy binding
- rationale digest or structured reason code
- request nonce/idempotency key
- creation sequence/time

The original proposal is immutable evidence even when DGV rejects it or R1 later corrects itself.

## 8. Independent R1 self-drift enforcement

DGV recomputes the allowed action from current WSA/PRR state.

If R1 proposes `SAME_WORKFLOW` or another classification but the action is outside the permitted action set, DGV MUST:

1. perform no consequential transition/side effect;
2. append `R1_SELF_DRIFT_BLOCKED` to GEL;
3. bind the rejected `proposal_id`, WCE, expected WSA scope, conflicting action, candidate/policy/checkpoint identities, and rejection reason;
4. preserve the parent/child graph and checkpoint unchanged;
5. expose the corrected authoritative state to R1/user;
6. preserve the RED event permanently even if a later retry succeeds.

`R1_SELF_DRIFT_BLOCKED` is an event schema, not a model label.

Minimum event fields:

- `event_id`
- `event_type = R1_SELF_DRIFT_BLOCKED`
- `proposal_id`
- `r1_identity`
- `root_workflow_id`
- `parent_workflow_id`
- `checkpoint_sequence`
- `candidate_manifest_digest`
- `policy_id/version/digest`
- `expected_permitted_action_set_digest`
- attempted action digest/type
- rejection reason code
- WSA sequence before and after (must prove no unauthorized transition)
- predecessor event digest
- authoritative event sequence

## 9. Task relationship model

Every material diversion is one of:

- `NON_BLOCKING_CHILD`
- `BLOCKING_CHILD`
- `DEPENDENCY_CHILD`
- `INCIDENT_CHILD`
- `INFORMATION_ONLY_CHILD`

Every child binds child/parent IDs, relationship type, reason, initiating principal/service, orchestration mode, parent checkpoint, candidate manifest, policy/schema, pending gates, parent authority state, return condition, authority scope, creation nonce/idempotency identity, and predecessor event digest.

A child cannot become root because it is newest, longest-running, or visible in the UI.

## 10. Classification authority and downgrade control

R1 may propose a relationship. DGV validates it against PRR policy.

A transition from `BLOCKING_CHILD`, `DEPENDENCY_CHILD`, or `INCIDENT_CHILD` to `NON_BLOCKING_CHILD`/`INFORMATION_ONLY_CHILD` that removes or weakens a gate is a **relationship downgrade**.

A relationship downgrade requires:

- a PRR permission explicitly named `RELATIONSHIP_DOWNGRADE` for that workflow/policy scope;
- a `RelationshipDowngradeDecision` bound to parent/child IDs, original class, proposed class, candidate/policy/checkpoint, reason code, nonce/idempotency key, predecessor digest, and policy version;
- confirmation by an authorized principal/policy component that is independent from the original proposer when the downgrade removes a mandatory gate;
- preservation of the original blocking classification/history.

R1 alone can never satisfy the independent confirmation requirement.

Unauthorized downgrade emits `RELATIONSHIP_DOWNGRADE_REJECTED`. Authorized downgrade emits `RELATIONSHIP_DOWNGRADE_ACCEPTED`.

## 11. Parent suspension and return

Opening a blocking/dependency child commits `PARENT_PAUSED_PENDING_CHILD_IMPACT` (or a more specific policy-defined paused state) and preserves the exact resume checkpoint.

A child may return control only after:

1. child stopping condition reached;
2. required child evidence preserved;
3. required `ChildImpactRecord` accepted;
4. candidate/checkpoint binding revalidated;
5. stale evidence explicitly marked;
6. sibling/blocking children evaluated;
7. DGV computes the exact next permitted parent action.

Accepted return emits `PARENT_RESUMED_FROM_CHILD` with immediate graph-edge IDs. Nested return MUST proceed one graph edge at a time.

## 12. ChildImpactRecord and impact authority

Allowed impact classes:

- `PARENT_UNAFFECTED`
- `PARENT_BLOCKED`
- `PARENT_CONSTRAINT_ADDED`
- `PARENT_EVIDENCE_STALE`
- `PARENT_REVIEW_RESTART_REQUIRED`
- `PARENT_POLICY_REBIND_REQUIRED`
- `PARENT_CANDIDATE_INVALIDATED`
- `PARENT_ABORT_REQUIRED`

Required fields:

- impact record ID;
- parent/child workflow IDs;
- parent checkpoint ID/sequence;
- parent candidate manifest digest;
- child result/candidate digest;
- child disposition;
- impact class;
- affected/unaffected/stale artifact/evidence/gate IDs;
- dependency comparison evidence;
- required re-review/re-test/rebind actions;
- exact next permitted parent action identifier;
- deciding authorized role/policy component;
- independent confirmer where policy requires one;
- orchestration mode;
- decision nonce/idempotency key;
- policy ID/version/digest;
- predecessor record/event digest;
- authoritative sequence/time.

PRR defines which roles/policies may issue each impact class. An impact record cannot grant terminal authority merely by containing a permissive class.

`PARENT_UNAFFECTED` requires deterministic dependency comparison; an empty affected set by itself is insufficient.

A stale/replayed impact record is rejected as `CHILD_IMPACT_RECORD_REJECTED`.

## 13. Evidence staleness

Evidence staleness is dependency-specific. DGV evaluates candidate digest, policy digest, reviewer independence, acceptance/falsification criteria, identity/credential binding, stage prerequisites, provider/model qualification, request/result binding, and authority-source dependencies.

A process-only change does not automatically invalidate candidate evidence. A candidate change does not automatically invalidate unrelated process evidence. The exact affected/unaffected/stale sets MUST be recorded.

## 14. User drift disclosure object

Material drift requires a durable `DriftDisclosureRecord` created by DR.

Fields:

- `disclosure_id`
- `user_principal_id`
- `root_workflow_id`
- `parent_workflow_id`
- `parent_checkpoint_id/sequence`
- `child_workflow_id` if created/proposed
- relationship classification
- parent paused/unaffected state
- impact-handling-required flag
- orchestration mode
- normalized disclosure content digest
- delivery target/channel identity
- `delivery_state` = `PENDING | DELIVERED | FAILED`
- record sequence/time
- delivery sequence/time when delivered
- related proposal/event IDs
- `approval_required` boolean
- separate `approval_object_id` when applicable

Disclosure is not approval. User acknowledgement of disclosure is not approval unless a separately valid approval object exists.

### 14.1 MANUAL_GOVERNED timing

For material drift that requires user approval, `DISCLOSURE_DELIVERED` MUST occur before approval capture and before the diverted consequential transition. Wrong recipient/workflow/checkpoint or late disclosure fails the disclosure gate.

### 14.2 AUTOMATIC_GOVERNED timing

If bound policy has `async_disclosure_allowed = false`, disclosure delivery precedes the transition.

If bound policy has `async_disclosure_allowed = true`, the authoritative transition and `DRIFT_DISCLOSURE_RECORDED` MUST be committed atomically, delivery enters `PENDING`, and the user-facing surface MUST deliver the disclosure at the next available interaction/notification cycle. The workflow transition may remain valid, but the disclosure/UX test remains failed until `DELIVERED`; it cannot be reported as a clean disclosure PASS while pending/failed.

## 15. R1 unavailability and fallback

PRR may define a role `R1_FALLBACK_ORCHESTRATOR` with an exact workflow scope and expiry/effective sequence.

If R1 is unavailable and no active qualified fallback exists, DGV emits `R1_UNAVAILABLE_BLOCKED` and blocks consequential orchestration that requires the R1 drift-sentinel function.

No model, reviewer, UI session, operator, or child inherits R1 authority implicitly.

A fallback is subject to the same WCE, DGV, disclosure, and self-drift rules and cannot validate its own authority.

## 16. R2/R3 reviewer context isolation

RCB constructs a `ReviewerWorkflowContext` directly from WSA/GEL/PRR.

Allowed fields by default:

- reviewer identity/role;
- review workflow/task ID;
- parent workflow ID;
- parent checkpoint ID/sequence;
- parent active/paused status;
- existence/type of blocking child when necessary;
- candidate manifest digest and policy identity;
- reviewer's own pending/completed status;
- unresolved impact status;
- explicitly authorized evidence/artifact scope.

Prohibited before cross-review/adjudication authorization:

- another reviewer's substantive findings/disposition;
- R1 persuasive narrative/rationale;
- expected agreement/majority;
- adjudication conclusion;
- hidden golden/test-oracle result.

RCB records `ReviewerContextRecord` with schema version, allowed-field policy, payload digest, source WSA sequence, reviewer identity, and delivery event.

A prohibited field or source mismatch emits `REVIEW_CONTEXT_REJECTED_LEAKAGE`; the contaminated payload cannot count as independent review evidence.

## 17. Cross-standard linkage with EXP-K

Workflow/task drift and claim/evidence contamination remain separate controls but share correlated ledger identities when one incident crosses both domains.

A cross-domain event MUST bind:

- `workflow_drift_event_id` where applicable;
- related EXP-K `claim_id`/continuity-failure ID(s);
- parent/child workflow IDs;
- candidate/policy/checkpoint identities;
- separate workflow disposition and claim/evidence status;
- rule that neither disposition authorizes the other.

Workflow recovery cannot validate a claim. Claim validation cannot authorize a workflow transition.

## 18. Concurrency, leases, and fencing

Consequential writes use a WSA-issued write lease or compare-and-swap token containing workflow/task ID, checkpoint sequence, candidate digest, and monotonic fencing token.

WSA accepts only the highest current fencing token for the exact scope. A stale writer emits `STALE_WORKFLOW_WRITER_REJECTED`; both writes cannot commit.

Manual/automatic races, parent/child races, cancellation/supersession races, and late external results use the same authoritative sequence/fencing rule.

## 19. External request/result binding

Every external worker/reviewer/model request in eventual runtime binds workflow/task/parent IDs, candidate manifest, policy/schema, provider/model identity, request ID, intent-level idempotency key, payload digest, lifecycle state, evidence-visibility scope, effect/reconciliation state, and authoritative sequence.

Timeout/retry/late success/device/UI restart must reconcile to one intent/effect. A result bound to an older candidate/policy/checkpoint cannot advance a newer state.

This runtime rule does not authorize reviewer/model API calls during the current manual testing phase.

## 20. Cancellation, supersession, policy migration, and graph returns

Cancellation and supersession are explicit mutually ordered transitions. The first accepted transition at the authoritative WSA sequence wins; later conflicting attempts are rejected and preserved.

Policy migration requires an explicit `POLICY_REBIND_DECISION` or bound-policy continuation decision before new-policy rules affect an in-flight workflow.

Nested child return emits one `CHILD_RETURN_EDGE_ACCEPTED` per immediate graph edge. Sibling completion cannot erase another sibling or its impact record.

## 21. Development/testing source precedence vs runtime authority

During the present development/testing stage, exact frozen GitHub/project artifacts and committed checkpoints are the durable recovery source. R1 memory/chat may help locate them but cannot override them.

If memory conflicts with the frozen project checkpoint, the conflict is surfaced and the durable checkpoint wins. If the exact durable state cannot be established, the development workflow fails closed rather than guessing.

In the eventual runtime platform, GitHub is not the workflow authority. WSA + PRR + GEL are the runtime authority under their qualified recovery rules.

## 22. Current project application

For the present governed-platform design work:

- Parent: MVP independent-review workflow.
- Parent state: `PARENT_PAUSED_PENDING_CHILD_IMPACT`.
- Child 1: continuity/resumption governance.
- Child 2: workflow-drift and parent-child impact governance.
- Parent reviewer barriers remain pending and unchanged unless a separately governed impact decision says otherwise.

DeepSeek review evidence against the prior candidate `fafbdc74bb54808095603994a687be55624f7215` remains immutable evidence for that prior candidate only. This V4 candidate is a new revision and requires a fresh independent review binding.

## 23. Freeze condition

This standard MUST NOT be frozen until its V4 falsification matrix is independently reviewed and executed to the required policy threshold.

No label, model statement, review, child impact record, disclosure record, or R1 proposal grants merge, release, production, qualification, adjudication, or terminal authority unless a separately qualified governing policy explicitly grants that exact transition.
