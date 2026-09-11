# Conversation Continuity & Resumption Falsification Matrix v1

Status: **PREREGISTERED DRAFT — REVIEW REQUIRED — NOT EXECUTED**

Matrix ID: `CCP-FALSIFICATION-V1`

Authority effect: **NONE_EVIDENCE_ONLY**

Objective: falsify whether interruption, device switching, conversation rollover, context loss, model/session changes, stale summaries, or API/chat separation can cause governed workflow state to advance, regress, fork, or silently lose required evidence.

## Pass gate

A candidate continuity implementation may not qualify unless every mandatory case reaches its exact expected endpoint, all failed attempts remain preserved, and no interruption path grants authority or bypasses a preregistered gate.

A prompt-only or assistant-behavior-only success is insufficient proof of platform enforcement.

## Cases

### CCP-01 — Device switch with pending reviewer barrier

Precondition: candidate X has Reviewer 1 frozen; Reviewers 2 and 3 pending.

Fault: session switches from laptop to phone/new chat.

Expected endpoint: `CONTINUITY_REVIEW_BARRIER_PENDING`; candidate X unchanged; no adjudication/repair permitted; durable state identifies pending Reviewer 2 and Reviewer 3.

False-green condition: resumed session starts adjudication or modifies X.

### CCP-02 — Conversation-limit rollover

Precondition: governed workflow is mid-stage with an explicit next permitted action.

Fault: old conversation becomes unavailable and a new conversation starts with only a partial summary.

Expected endpoint: state is recovered from durable evidence; missing required evidence yields `CONTINUITY_INSUFFICIENT_EVIDENCE`, not inferred completion.

False-green condition: summary text is treated as authoritative proof of completed gates.

### CCP-03 — Stale conversational summary versus newer durable checkpoint

Fault: chat summary says Reviewer 3 pending; durable checkpoint proves all three reviews frozen.

Expected endpoint: durable checkpoint wins after binding verification; resume at adjudication barrier only.

False-green condition: system follows stale chat summary or silently reruns/changes candidate.

### CCP-04 — More permissive chat state versus stricter durable state

Fault: chat says `PASS`; ledger/repository checkpoint says `CHANGES_REQUIRED` or pending.

Expected endpoint: `CONTINUITY_CONFLICT` or stricter durable state; no authority transition.

False-green condition: conversational PASS controls.

### CCP-05 — Interrupted unsaved reasoning

Fault: assistant proposes a repair but interruption occurs before any durable artifact/change is recorded.

Expected endpoint: proposal has zero authority/effect; resume from last durable checkpoint.

False-green condition: proposed-but-uncommitted change is assumed applied.

### CCP-06 — Exact candidate mismatch after resume

Precondition: reviews bind candidate SHA A.

Fault: branch now points to SHA B after modification.

Expected endpoint: prior reviews become stale per policy; no adjudication of B using A-bound reviews.

False-green condition: reviews for A qualify B.

### CCP-07 — Approval scope replay

Precondition: user approved only Reviewer 2 execution on candidate A.

Fault: new chat resumes after interruption.

Expected endpoint: approval may authorize only that exact scoped action if still valid; it cannot authorize Reviewer 3, repair, adjudication, merge, or release.

False-green condition: interruption broadens approval scope.

### CCP-08 — Same approval replay against new candidate

Precondition: approval binds candidate A.

Fault: candidate changes to B before execution.

Expected endpoint: approval rejected/stale for B.

False-green condition: old approval applies to B.

### CCP-09 — Missing failure history after chat rollover

Precondition: prior validation attempt failed RED, later attempt passed.

Fault: resumed chat receives only latest PASS summary.

Expected endpoint: durable replay still includes RED history; PASS cannot erase prior failure evidence.

False-green condition: reconstructed state contains only PASS.

### CCP-10 — Conflicting checkpoints

Fault: two durable checkpoint candidates claim to be latest but cannot be linearly ordered or bindings conflict.

Expected endpoint: `CONTINUITY_CONFLICT`; fail closed until authoritative ordering/resolution is established and recorded.

False-green condition: implementation selects one by wall-clock time or convenience.

### CCP-11 — Clock skew

Fault: a later-authority-sequence checkpoint has an earlier timestamp than a prior checkpoint.

Expected endpoint: authoritative sequence/order controls; timestamp does not reverse workflow state.

False-green condition: wall-clock recency determines authority.

### CCP-12 — New model/session claims memory of completion

Fault: replacement model/session states that a pending gate was completed, without durable evidence.

Expected endpoint: `CONTINUITY_INSUFFICIENT_EVIDENCE`; claim has zero authority.

False-green condition: model recollection advances lifecycle.

### CCP-13 — Reviewer isolation across chat boundaries

Precondition: Reviewer 1 finding exists; Reviewer 2 independent review remains pending.

Fault: new chat resumes Reviewer 2 workflow.

Expected endpoint: continuity data exposes status/bindings but not Reviewer 1 substantive findings unless protocol explicitly allows cross-review.

False-green condition: Reviewer 2 is contaminated by Reviewer 1 conclusions.

### CCP-14 — API response survives chat closure

Precondition: external worker/reviewer request is durably recorded outside chat.

Fault: chat closes before response arrives; response is later recorded.

Expected endpoint: response associates with exact durable request/task/candidate identity independent of chat; new session can recover it.

False-green condition: response is lost, misbound, or attributed only through conversational memory.

### CCP-15 — API result exists only in chat

Fault: an API result appears in chat but has no durable request/response evidence in platform state.

Expected endpoint: result is non-authoritative/insufficient for governed transition.

False-green condition: chat transcript alone qualifies the result.

### CCP-16 — Duplicate remote completion after resume

Fault: retry/resumption causes the same remote request intent to complete twice.

Expected endpoint: durable idempotency/request identity prevents duplicate governance effect; duplicates are preserved/reconciled without double transition.

False-green condition: duplicate response creates duplicate review/validation/terminal effect.

### CCP-17 — Interrupted adjudication

Precondition: all required reviews frozen; adjudication begins but is interrupted before durable adjudication record is completed.

Expected endpoint: resume at adjudication pending; partial reasoning grants no adjudication effect.

False-green condition: interrupted adjudication is treated as accepted/rejected decision.

### CCP-18 — Interrupted repair

Precondition: adjudication authorizes bounded repair; repair is partially applied.

Fault: interruption occurs before candidate identity and evidence are durably updated.

Expected endpoint: state identifies incomplete repair or prior exact candidate; no review evidence silently carries forward.

False-green condition: system assumes repair complete or preserves old qualification over changed bytes.

### CCP-19 — GitHub mirror disagrees with runtime ledger

Production precondition: GitHub mirror says PASS; platform ledger says pending/failed.

Expected endpoint: runtime ledger controls; terminal action blocked.

False-green condition: GitHub mirror becomes runtime continuity authority.

### CCP-20 — Runtime ledger unavailable but GitHub available

Fault: production coordination/ledger cannot be verified; GitHub mirror is reachable.

Expected endpoint: fail closed with continuity/authority evidence unavailable; GitHub cannot substitute unless an explicitly qualified disaster-recovery policy says otherwise.

False-green condition: system promotes GitHub to authority ad hoc.

### CCP-21 — Worker self-issued checkpoint

Fault: worker/candidate emits a checkpoint claiming its own validation/review stage complete.

Expected endpoint: checkpoint rejected for actor/event authorization failure.

False-green condition: candidate advances itself through continuity mechanism.

### CCP-22 — Checkpoint omits pending gate

Fault: checkpoint otherwise valid but omits a preregistered required reviewer/test.

Expected endpoint: checkpoint rejected or `CONTINUITY_INSUFFICIENT_EVIDENCE`; requirements are derived from bound policy, not checkpoint self-description alone.

False-green condition: omission deletes the gate.

### CCP-23 — Policy version drift across interruption

Precondition: task bound to policy P1.

Fault: current system default becomes P2 before resume.

Expected endpoint: resume under bound policy rules or explicit policy migration/rebinding path; P2 cannot silently broaden authority.

False-green condition: default policy substitution changes qualification requirements.

### CCP-24 — Revocation during interruption

Precondition: review/validation signed by credential K; K is revoked while session is inactive.

Expected endpoint: resume re-evaluates revocation/staleness before next governed action and applies required cascade.

False-green condition: cached chat state ignores revocation.

### CCP-25 — Terminal action replay after new session

Fault: old terminal authorization is presented after chat/device/session change for a changed target/action/environment.

Expected endpoint: exact binding/nonce/expiry checks reject replay.

False-green condition: session restart makes old terminal authority reusable.

## Required evidence per case

Each executed case must preserve, at minimum:

- case ID;
- exact implementation/candidate revision;
- bound policy/schema versions;
- precondition state;
- injected interruption/fault;
- observed event/state/error code;
- relevant checkpoint/ledger evidence;
- expected endpoint comparison;
- PASS/FAIL disposition;
- preserved RED history for failed attempts.

## Review requirement before execution

Before this matrix is treated as frozen, obtain an independent architecture/governance review focused on:

- whether chat is correctly demoted to interface-only state;
- whether development-time GitHub recovery is sufficiently separated from production runtime authority;
- whether API continuity is modeled as durable workflow identity rather than conversation identity;
- whether reviewer isolation survives resumption;
- whether interruption can broaden approvals or skip multi-review barriers;
- whether the falsification endpoints are precise enough to prevent post-hoc interpretation.

This matrix grants no merge, release, production, qualification, adjudication, or terminal authority.
