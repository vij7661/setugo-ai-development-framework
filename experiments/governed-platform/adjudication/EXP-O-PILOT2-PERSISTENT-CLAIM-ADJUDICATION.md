# EXP-O Pilot 2 — Persistent Change-Claim Concurrency Adjudication

Date: 2026-09-06
Status: **DETERMINISTIC_PERSISTENCE_PASS / SQLITE ONLY / DISTRIBUTED CLAIMS UNPROVEN**

## Frozen lineage

- Pilot 1 deterministic runtime-boundary adjudication: `0040483931830b7790cb936a0e81af89312a5fed`
- Pilot 2 pre-registration: `850b9ce532360cb6710fe6e5c5548e67db256203`
- Persistent SQLite claim-store implementation: `4b0f19956ece80485b420192ed27c8a72cc987f8`
- Concurrency falsification tests / execution head: `9031268f3a838d76127711ba1881b749bdb6c9f2`
- GitHub Actions run: `34013025854`
- Run conclusion: `SUCCESS` operationally

The Pilot 2 pre-registration was committed before the persistent store and its tests. The protected concurrency, idempotency, rollback and restart outcomes were therefore frozen before execution.

## Execution evidence

The latest governed harness executed:

- scorer regressions: 36 / 36
- runner regressions: 51 / 51
- protected-truth regressions: 4 / 4
- observability regressions: 7 / 7
- continuation regressions: 12 / 12
- governance regressions: 352 / 352

Total: **462 / 462** deterministic tests passed.

The new Pilot 2 persistence/concurrency block contains **7 / 7** passing cases.

## Frozen-case adjudication

### 1. Concurrent overlapping exclusive writers

Two separately connected contenders requested overlapping exclusive resource scopes from the same base state.

Observed protected outcome:
- exactly one `EXCLUSIVE_GRANTED`;
- exactly one `WAITING_CONFLICT`;
- exactly one durable active exclusive claim row.

Primary endpoint contribution: **no simultaneous overlapping authoritative grants observed.**

### 2. Concurrent non-overlapping exclusive writers

Two contenders requested distinct scopes.

Observed protected outcome:
- both received `EXCLUSIVE_GRANTED`;
- claim epochs were distinct and monotonic (`1`, `2` in the isolated test store);
- both durable claims remained active.

This is the clean availability/specificity control for the overlap rule.

### 3. Concurrent overlapping parallel proposals

Two contenders requested overlapping `PARALLEL_PROPOSAL` scopes.

Observed protected outcome:
- both received `PARALLEL_PROPOSAL_GRANTED`;
- both records were retained as proposal claims;
- this mode does not create integration/release authority.

The result preserves the architecture distinction between allowing independent proposals and authorizing an authoritative integration.

### 4. Exact retry idempotency

The same task/base/resource/mode claim intent was submitted twice.

Observed protected outcome:
- the retry returned the original claim ID and epoch;
- the retry was marked as a retry;
- only one durable active claim row existed;
- the next claim epoch was not consumed by the duplicate request.

Secondary endpoint: **exact-intent duplicate durable rows = 0.**

### 5. Task identity reused with different claim intent

The same task identity attempted to request a materially different resource scope.

Observed protected outcome:
- `CLAIM_INTENT_MISMATCH`;
- the original durable claim remained unchanged.

Secondary endpoint: **mismatched-intent reuse accepted = 0.**

### 6. Injected failure before commit

The store deliberately raised an exception after claim/epoch computation but before transaction commit.

Observed protected outcome:
- no partial claim row remained;
- the claim epoch increment rolled back;
- the next valid claim reused the unconsumed epoch.

Secondary endpoints:
- **partial rows after injected rollback = 0**;
- **claim epochs consumed by aborted transaction = 0.**

### 7. Restart/reopen durability

The store was closed/reopened using a new connection-equivalent instance after an active exclusive claim existed.

Observed protected outcome:
- the original claim and epoch remained durable;
- a later overlapping exclusive request was still blocked with `WAITING_CONFLICT`;
- the active claim was not lost through reopen.

Secondary endpoint: **active claims lost after reopen = 0.**

## Primary endpoint

Across the pre-registered concurrent overlapping-exclusive test:

**simultaneous overlapping authoritative grants = 0.**

## Secondary endpoints

Across the frozen Pilot 2 cases:

- exact-intent duplicate durable claim rows: **0**;
- mismatched-intent task reuse accepted: **0**;
- partial claim rows after injected rollback: **0**;
- duplicate/consumed epochs caused by the tested rollback/retry paths: **0**;
- active claims lost after reopen: **0**.

## What this result establishes

Within the tested file-backed SQLite implementation and CI concurrency conditions, the pre-registered persistent Change Claim Registry behavior is consistent with the architecture requirement that overlapping exclusive Builder intents be serialized before execution while non-overlapping work and explicitly non-authoritative parallel proposals remain possible.

This is stronger evidence than the Pilot 1 in-memory claim model because it exercised actual database transactions, independent connections, concurrent threads, durable reopen, uniqueness constraints and transaction rollback.

## What this result does NOT establish

This Pilot does **not** establish:
- PostgreSQL behavior or isolation-level correctness;
- distributed lock/lease safety under network partitions;
- multi-region linearizability;
- production deadlock/starvation characteristics;
- production throughput or tail latency;
- claim expiration/lease recovery after a dead Builder;
- correctness of semantic overlap detection beyond the frozen resource-prefix representation;
- that a future production implementation may substitute another persistence algorithm without separate verification.

SQLite's `BEGIN IMMEDIATE` serializes writers in a way that is useful for falsifying the transaction contract here but is not itself the final production architecture.

## Next promotion boundary

Do not promote this result directly into a production distributed-claims claim.

The next meaningful implementation step is a real runtime/integration slice containing:
1. separately deployable Authority Kernel;
2. local enforcement point;
3. persistent production-style claim service/store;
4. isolated execution worker identity;
5. durable evidence spool.

Once that exists, EXP-O can pre-register:
- O1B network/clock/freshness fault injection;
- O3C production-store concurrent claim tests;
- O4B real worker crash/reschedule and sender-bound reissuance;
- O5B crash-consistency plus separately administered evidence anchor;
- O2B real-agent/MCP prompt-injection behavior.

Until then, the appropriate statement is:

> **The pre-registered SQLite persistence/concurrency claim-registry cases passed; distributed and production claim safety remain unproven.**
