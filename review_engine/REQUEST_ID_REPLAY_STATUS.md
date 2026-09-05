# Governed Request ID Replay Protection — Status

## Verified implementation baseline

- Implementation/test SHA: `3b4ec2875408c872bb9c8d9a321239f2ef2425a4`
- Exact-head GitHub Actions run: `33988532011`
- Workflow: `Governed Platform + Review Engine Harness`
- Result: **SUCCESS**

The successful exact-head run covered the Review Engine system regressions plus the existing scorer, runner, protected-truth, observability, continuation-authority and governor falsification gates.

## Control verified

A `request_id`/session ID is a single-use governed review execution identifier.

`SQLiteSessionStore.append` atomically reserves the identifier when the orchestrator emits `REQUEST_RECEIVED`. A second `REQUEST_RECEIVED` for an existing session is rejected while holding a SQLite `BEGIN IMMEDIATE` transaction. A terminal `FINAL_DECISION` also seals the session against later evidence appends.

Because `REQUEST_RECEIVED` is emitted before R1/provider invocation, a losing duplicate is rejected before it can invoke a reviewer. This applies both to a retry after process/application restart and to a duplicate that arrives while the winning review is still executing.

The current contract deliberately rejects even an exact duplicate rather than silently replaying/caching a previous result. Any future idempotent-result cache must be explicit and cryptographically/artifact bound; it must not merge a new execution into an existing evidence chain.

## Falsification coverage

The session/application regressions verify:

1. duplicate `REQUEST_RECEIVED` is atomically rejected;
2. a terminal session rejects late evidence events;
3. concurrent evidence writers preserve one hash-linked sequence;
4. same-process duplicate review IDs do not merge evidence;
5. a duplicate after application restart invokes no provider and leaves exactly one request/final sequence;
6. a concurrent duplicate arriving while the winning R1 call is still blocked is rejected before a second provider invocation;
7. the winning session remains one valid hash-linked lifecycle with one `REQUEST_RECEIVED` and one `FINAL_DECISION`.

## What this does not prove

This milestone is limited to **single-node durable request-ID admission and replay rejection**. It does not claim:

- distributed/multi-node exactly-once execution;
- cross-database atomicity with external systems;
- idempotent external actions (action execution remains disabled);
- automatic recovery of an admitted session if the process crashes before a terminal event;
- WORM/external immutability of the SQLite ledger.

The interrupted-session/terminal-failure evidence path remains a separate control to address next.
