# EXP-O Pilot 2 — Persistent Change-Claim Concurrency Pre-registration

Date: 2026-09-06
Status: **PRE-REGISTERED BEFORE IMPLEMENTATION**

Depends on deterministic Pilot 1 adjudication: `0040483931830b7790cb936a0e81af89312a5fed`

## Question

Does a transactional persistent Change Claim Registry prevent two concurrent overlapping exclusive Builders from both obtaining an authoritative execution disposition, including under retry and rollback conditions?

This is a persistence/concurrency pilot. It is stronger than the in-memory O3 mechanism test but is not a production distributed-database or multi-region claim.

## Frozen implementation boundary

Pilot 2 will use a file-backed SQLite database with separate connections per contender. SQLite is selected only to exercise real transaction serialization, uniqueness and rollback semantics inside CI without adding external infrastructure.

The target production database remains undecided/likely PostgreSQL. Passing this pilot does not transfer automatically to another database implementation.

## Claim identity

A claim intent is bound to:
- `task_id`;
- `base_sha`;
- normalized resource scope;
- mode (`EXCLUSIVE` or `PARALLEL_PROPOSAL`).

The registry persists an intent hash. A retry of the exact same intent must be idempotent. Reusing the same task identity with a different claim intent must fail closed.

## Frozen cases

1. **Concurrent overlapping exclusive writers**
   - Two threads/process-equivalent clients begin from the same base and request overlapping exclusive scopes.
   - Protected outcome: exactly one `EXCLUSIVE_GRANTED`; exactly one `WAITING_CONFLICT`.
   - Never two grants.

2. **Concurrent non-overlapping exclusive writers**
   - Both are permitted.
   - Protected outcome: two `EXCLUSIVE_GRANTED` rows with distinct monotonic claim epochs.

3. **Concurrent overlapping parallel proposals**
   - Both may receive `PARALLEL_PROPOSAL_GRANTED` because neither gains integration authority.
   - Final integration remains separately governed and is not tested as release authority here.

4. **Exact retry idempotency**
   - Repeating an already granted task/base/resources/mode returns the original claim identity/epoch.
   - Protected outcome: one durable active claim row, not two.

5. **Task identity reused with different claim intent**
   - Protected outcome: `CLAIM_INTENT_MISMATCH`; existing claim unchanged.

6. **Injected failure before commit**
   - Simulate an exception after overlap/epoch decision but before transaction commit.
   - Protected outcome: no partial claim row and no consumed claim epoch after rollback.

7. **Restart/reopen durability**
   - Close the store and reopen a new connection/process-equivalent instance.
   - Protected outcome: active claim and epoch remain readable and continue to block an overlapping exclusive request.

## Primary endpoint

Across concurrent overlapping-exclusive trials:

**simultaneous overlapping authoritative grants = 0**.

## Secondary endpoints

- exact-intent duplicate durable rows = 0;
- mismatched-intent reuse accepted = 0;
- partial rows after injected rollback = 0;
- claim epoch duplication = 0;
- active claim lost after reopen = 0.

## Decision rule

`DETERMINISTIC_PERSISTENCE_PASS` requires every frozen case to pass without weakening the protected outcomes.

A CI/workflow SUCCESS is operational completion only. The adjudication must inspect the actual concurrency test outputs.

## Non-claims

Passing Pilot 2 does not establish:
- PostgreSQL serializability correctness;
- distributed lock/lease safety under network partitions;
- multi-region linearizability;
- production throughput/latency;
- deadlock/starvation behavior at scale;
- correctness of semantic resource-overlap classification beyond the frozen scope representation.
