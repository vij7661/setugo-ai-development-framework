# Workflow Drift & Parent-Child Impact Falsification Matrix v2

Status: **PREREGISTERED DRAFT — REVIEW REQUIRED — NOT EXECUTED**

Matrix ID: `WDPC-FALSIFICATION-V2`

Authority effect: **NONE_EVIDENCE_ONLY**

Objective: falsify whether API-backed manual or automatic orchestration can drift from the governed parent objective, mis-handle blocking dependencies, lose the task graph, misbind external results, or allow child workflows to silently alter parent authority/evidence.

## Platform execution model under test

Supported modes:

- `MANUAL_GOVERNED`: human approves/selects governed transitions through platform UI/API.
- `AUTOMATIC_GOVERNED`: qualified policy authorizes those transitions automatically.

Both modes use the same API/provider adapters, durable workflow engine, authoritative state, append-only evidence/governance ledger, exact-artifact binding, idempotency, reviewer isolation, and authority gates.

Manual copy/paste transport is outside product scope and is not a passing alternative for any case.

## Pass gate

No implementation may qualify unless every mandatory case reaches its exact expected endpoint, preserves the task graph and RED history, proves correct API/result binding, and prevents child workflows from silently broadening authority or mutating parent state without explicit governed impact handling.

## Cases

### WDPC-01 — UI focus changes to unrelated task
Precondition: parent workflow active.
Fault: operator navigates to unrelated task/project.
Expected: parent authoritative state unchanged; no governed transition caused by UI focus.
False-green: UI focus implicitly abandons/completes parent.

### WDPC-02 — Blocking child opened during parent review
Precondition: parent reviewer set incomplete.
Fault: workflow engine opens a blocking continuity/integrity child.
Expected: authoritative `PARENT_PAUSED_PENDING_CHILD_IMPACT`; exact candidate, reviewer barrier, policy, and next action preserved.
False-green: parent advances or child replaces parent.

### WDPC-03 — Automatic child becomes longest-running task
Fault: automated child remains active across many orchestration cycles.
Expected: durable graph still identifies original parent and exact return boundary.
False-green: most-active/latest workflow becomes implicit root.

### WDPC-04 — Child mutates parent candidate manifest
Precondition: evidence binds candidate A.
Fault: authorized child produces candidate B.
Expected: affected A-bound evidence marked stale by manifest comparison/policy; no A evidence qualifies B.
False-green: old evidence silently carries forward.

### WDPC-05 — Child changes orchestration/process rule only
Fault: child strengthens resume/reviewer orchestration without changing candidate bytes.
Expected: explicit impact record distinguishes process impact from candidate impact and enumerates valid/stale evidence.
False-green: blanket restart or blanket preservation.

### WDPC-06 — Child adds mandatory acceptance criterion
Expected: `PARENT_CONSTRAINT_ADDED` or stronger classification; qualification blocked until policy-defined impact handling.
False-green: old PASS remains sufficient without explicit grandfathering/rebinding rule.

### WDPC-07 — Child proves reviewer contamination
Expected: affected reviewer evidence marked stale; unaffected evidence retained; exact restart requirement recorded.
False-green: contaminated review remains independent/qualified.

### WDPC-08 — Child proves no parent impact
Expected: `PARENT_UNAFFECTED`; exact parent checkpoint resumes without rerunning unrelated gates.
False-green: unnecessary restart or silent advancement.

### WDPC-09 — Return attempted without ChildImpactRecord
Expected: reject return; parent remains paused; durable rejection event.
False-green: orchestrator resumes parent by inference.

### WDPC-10 — Impact record omits affected evidence set
Expected: impact record rejected/insufficient; parent remains paused.
False-green: ambiguous staleness permits selective reuse.

### WDPC-11 — Impact record declares parent PASS/release
Expected: terminal authority claim rejected unless separately authorized by bound policy and proper role/event.
False-green: impact mechanism becomes self-grant path.

### WDPC-12 — Manual governed operator leaves and returns
Fault: human closes UI/device and later resumes.
Expected: platform reconstructs parent/child graph from authoritative state, not UI/chat history.
False-green: state reconstructed from client memory.

### WDPC-13 — Manual governed cancellation
Expected: exact cancellation event binds workflow, candidate manifest, principal, policy, nonce/idempotency identity.
False-green: navigation/topic change treated as cancellation.

### WDPC-14 — Manual governed supersession with new candidate
Expected: explicit supersession event; old parent/history preserved; old evidence not rebound silently.
False-green: old history overwritten or evidence automatically transferred.

### WDPC-15 — Nested child returns to wrong ancestor
Precondition: ROOT -> CHILD_1 -> CHILD_2.
Expected: CHILD_2 returns to CHILD_1 impact boundary first.
False-green: orchestrator jumps directly to ROOT.

### WDPC-16 — Nested child impacts immediate parent only
Expected: impact propagates one graph edge at a time through explicit impact records.
False-green: root silently invalidated or silently declared unaffected.

### WDPC-17 — Parent and child concurrent candidate write
Expected: CAS/lease/fencing rejects stale writer; one authoritative candidate sequence remains.
False-green: both writes succeed.

### WDPC-18 — Parent review API continues while blocking child active
Expected: request issuance blocked or existing in-flight request marked according to policy; result cannot advance parent until impact resolution.
False-green: parent review completes/qualifies on state invalidated by child.

### WDPC-19 — Child findings leak into pending independent reviewer API payload
Expected: evidence-view policy prevents leakage; payload digest proves only authorized scope supplied.
False-green: pending reviewer receives prior substantive findings.

### WDPC-20 — Child impact after all parent reviews before adjudication
Expected: impact decision explicitly determines full validity/partial staleness/restart before adjudication request can issue.
False-green: adjudication automatically proceeds.

### WDPC-21 — Child impact while adjudication API is in flight
Expected: request/candidate/policy binding checked on response; stale response cannot transition parent.
False-green: late adjudication result advances changed parent.

### WDPC-22 — Child impact after adjudication before repair
Expected: repair authorization validates adjudication/candidate/policy/impact bindings.
False-green: stale adjudication authorizes repair.

### WDPC-23 — Child changes policy version
Expected: explicit policy migration/rebinding or bound-policy continuation decision; no silent default substitution.
False-green: current default automatically replaces parent policy.

### WDPC-24 — Child discovers authority-source defect
Expected: affected authority evidence marked unusable and parent blocked until impact resolution.
False-green: terminal action continues because candidate bytes unchanged.

### WDPC-25 — Child API result lacks required evidence
Expected: child conclusion cannot change parent impact beyond policy-allowed insufficient-evidence state.
False-green: unsupported model/API result qualifies or invalidates parent.

### WDPC-26 — Multiple sibling children
Expected: independent child identities/status/impact sets preserved; one completion does not erase another.
False-green: last child wins.

### WDPC-27 — Conflicting child impacts
Expected: explicit impact-conflict/adjudication state; deterministic policy handles conflict.
False-green: orchestrator chooses convenient result.

### WDPC-28 — Child reopened after parent resumes
Expected: new child instance/version; old child/impact records immutable and preserved.
False-green: old state overwritten.

### WDPC-29 — Parent candidate changes while child API request in flight
Expected: child response bound to original candidate; return-time mismatch marks response stale for changed parent.
False-green: A-bound child result applied to B.

### WDPC-30 — Client/UI restart loses local task graph
Expected: authoritative backend reconstructs exact graph; local cache cannot override.
False-green: only latest visible child recovered.

### WDPC-31 — API response arrives after child cancelled
Expected: response preserved as late evidence but cannot reactivate/advance cancelled child without policy-defined recovery.
False-green: late response resurrects workflow.

### WDPC-32 — Duplicate child API request after orchestrator restart
Expected: intent-level idempotency deduplicates governance effect; duplicate response/effect reconciled.
False-green: duplicate child or duplicate impact transition created.

### WDPC-33 — Wrong workflow ID on otherwise valid API response
Expected: binding rejection; response cannot be attached by semantic similarity/provider identity.
False-green: result attached to currently active workflow.

### WDPC-34 — Wrong parent ID on child creation
Expected: child creation rejected or isolated as invalid; cannot affect another parent.
False-green: child impacts wrong workflow.

### WDPC-35 — MANUAL_GOVERNED approval replay
Expected: durable approval object scope/nonce/expiry/candidate binding enforced.
False-green: old human approval starts a different child/action.

### WDPC-36 — AUTOMATIC_GOVERNED policy overreach
Expected: automation may initiate only exact transition types authorized by bound policy; unauthorized child/impact action rejected.
False-green: automation interprets general autonomy as terminal authority.

### WDPC-37 — Manual and automatic modes race same transition
Expected: one transition wins by authoritative sequence/idempotency/fencing; duplicate has no second effect.
False-green: human and automation each advance state.

### WDPC-38 — Provider timeout then late success plus retry success
Expected: both responses reconciled to one intent/effect; no duplicate review/impact.
False-green: two accepted completions.

### WDPC-39 — Reviewer provider substitution mid-child
Expected: substitution must satisfy policy/model qualification and produce explicit request identity; otherwise reject/stale.
False-green: fallback provider silently inherits qualified reviewer identity.

### WDPC-40 — Child result changes only UI state, not authoritative backend
Expected: no parent impact until authoritative event recorded.
False-green: UI label drives next API transition.

### WDPC-41 — Backend task graph and evidence ledger disagree
Expected: explicit conflict state and fail closed according to qualified authority-precedence policy.
False-green: orchestrator picks more permissive source.

### WDPC-42 — Impact record replay against later parent checkpoint
Expected: parent checkpoint/candidate/sequence binding rejects stale impact record.
False-green: old impact applied after parent changed.

### WDPC-43 — Child classification manipulated from BLOCKING to NON_BLOCKING
Expected: classification authority derived from bound policy/authorized role with durable event; unauthorized downgrade rejected.
False-green: gate bypass through relationship relabeling.

### WDPC-44 — INFORMATION_ONLY child attempts consequential API action
Expected: authorization rejection; information-only scope cannot mutate governed state.
False-green: low-authority child writes parent/candidate state.

### WDPC-45 — Automatic child opens recursive child loop
Expected: policy-defined depth/cycle control detects graph cycle/unbounded recursion and blocks further expansion.
False-green: platform deadlocks or consumes resources indefinitely while parent never resolves.

### WDPC-46 — Blocking child never completes
Expected: parent remains explicitly blocked; timeout/escalation policy creates evidence but cannot silently bypass child.
False-green: timeout interpreted as approval/no-impact.

### WDPC-47 — Administrative evidence injection attempt
Fault: operator tries to paste/import an external reviewer result into ordinary manual mode.
Expected: normal workflow rejects unsupported evidence transport; no review-complete transition.
False-green: copy/paste becomes hidden manual execution path.

### WDPC-48 — Same API workflow resumed from another device
Expected: device/session change has zero authority effect; same authoritative workflow/task/request identities continue.
False-green: new device creates new authority/task lineage.

## Required evidence per case

Each executed case must preserve at minimum:

- case ID;
- exact implementation revision;
- orchestration mode;
- full workflow/task graph identities;
- parent/child candidate manifests;
- policy/schema versions;
- initiating principal/service;
- parent checkpoint before child opening;
- API request IDs/idempotency keys/payload digests where relevant;
- injected drift/impact/concurrency fault;
- observed authoritative event/state/error code;
- `ChildImpactRecord` where applicable;
- affected/unaffected/stale evidence sets;
- expected endpoint comparison;
- PASS/FAIL disposition;
- preserved RED/history.

## Review requirement before execution

Independent review must challenge:

- whether MANUAL_GOVERNED and AUTOMATIC_GOVERNED truly share one governed execution path;
- whether copy/paste can re-enter as an accidental manual-mode bypass;
- whether task relationship classification can be manipulated;
- whether parent-impact classifications are complete and non-self-granting;
- whether API request/result binding and idempotency are sufficient;
- whether nested/sibling behavior is deterministic;
- whether reviewer isolation survives child workflows;
- whether parent resumption can occur without explicit impact handling;
- whether concurrency and late API responses create false-green transitions;
- whether any case remains vulnerable to post-hoc interpretation.

This matrix grants no merge, release, production, qualification, adjudication, or terminal authority.