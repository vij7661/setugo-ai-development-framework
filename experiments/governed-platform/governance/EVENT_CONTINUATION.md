# Event-Driven Continuation Governance

Status: **V4.2 experimental implementation requirement**

## Principle

The platform must not depend on an LLM remaining active, a chat remaining open, or periodic prompting to continue a workflow.

**Event-driven continuation is primary. Polling and schedules are fallbacks only when a source cannot emit a trustworthy completion/change event.**

The authoritative workflow state belongs to the platform, not to any model conversation.

## Continuation path

```text
Event Source
  -> Event Gateway
  -> Authenticity / Replay Guard
  -> Project + Task Resolver
  -> Exact-State Validator
  -> Continuation Policy Engine
  -> Authority Gate
  -> Agent / Tool / Human action
  -> Evidence Ledger + Project State
  -> Next event
```

An event never means "tell an LLM to continue" by itself. It is evidence that may permit a governed state transition.

## Typical event sources

- CI/workflow completion;
- agent/job completion callback;
- pull request/review state change;
- deployment result;
- test-platform result;
- environment provisioning result;
- human decision/approval;
- timeout/deadline event where a real event source is unavailable.

## Required validation before continuation

For every consequential event, validate as applicable:

- event source and authenticity;
- event ID / deduplication key;
- project ID and workflow/task ID;
- expected current project state;
- repository, branch and exact commit SHA;
- run/job/deployment identity;
- whether the event is stale, duplicated or out of order;
- evidence/provenance references;
- current authority and permission scope;
- whether a mandatory human/manual gate is active;
- whether budget/resource policy permits the next action.

A stale successful CI event for an old SHA must not advance a newer implementation.

## Continuation decisions

The policy engine returns one of:

- `CONTINUE` — current gate satisfied; dispatch the next authorized task.
- `RETRY` — retry the same authorized operation under retry/idempotency policy.
- `DIAGNOSE` — evidence indicates failure; enter evidence-based failure diagnosis.
- `BLOCK` — required evidence/authority/resource is missing or unsafe.
- `REQUEST_HUMAN` — a genuine business/security/legal/manual decision or validation is required.
- `COMPLETE` — terminal evidence requirements are satisfied.
- `IGNORE` — duplicate, stale, irrelevant or superseded event.

No event may directly produce `COMPLETE` without satisfying the evidence-state transition policy.

## Idempotency and ordering

Events must have stable identities. Processing the same event more than once must not duplicate side effects. The platform records processed event IDs and the state transition they caused.

When ordering matters, continuation must compare event/run/SHA/state lineage rather than arrival time alone. Out-of-order events are either ignored or retained as evidence without rolling authoritative state backward.

## Failure handling

A failed CI/test/agent event enters the five-category diagnostic process:

`CODE DEFECT / FIXTURE-DATA DEFECT / TEST DEFECT / ENVIRONMENT-TOOLING DEFECT / REQUIREMENT UNRESOLVED`.

Corrective authority is granted only after diagnosis. The event source cannot grant corrective authority merely by reporting failure.

## Scheduling and polling

Schedules are appropriate for genuinely time-based work such as daily reports or deadlines. Polling is permitted only when a useful source event/webhook/callback is unavailable or unreliable.

Fallback polling must be bounded, back off appropriately, deduplicate observed state, and stop when the terminal/continuation event is established. Polling frequency is an operational policy, not a substitute for event-driven orchestration.

## User notification policy

The system should not require the user to ask whether work finished. It should surface a notification when:

- human action/decision/manual QA is required;
- a terminal requested workflow completes;
- execution becomes blocked and cannot safely self-recover;
- an explicitly requested milestone/status notification is reached.

Routine successful internal transitions may continue without interrupting the user, while remaining visible in the evidence/project history.

## EXP-F falsification additions

Attack the continuation layer with at least:

1. duplicate completion event;
2. stale PASS for an older SHA;
3. out-of-order FAIL arriving after a superseding successful run;
4. forged/unauthenticated event;
5. valid event referencing the wrong project/task;
6. replayed event attempting duplicate side effect;
7. PASS event while mandatory manual gate is active;
8. event attempting `UNPROVEN -> COMPLETE` without required evidence;
9. budget/resource exhaustion event incorrectly interpreted as PASS;
10. two simultaneous valid completion events racing to advance the same state.

Success means the platform reaches the same authoritative state under retries/reordering and never advances a gate from stale, forged or insufficient evidence.
