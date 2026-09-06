# EXP-O Pilot 13 — Replicated Quorum Authority Under Partition Preregistration

Status: **PRE-REGISTERED BEFORE PILOT 13 IMPLEMENTATION OR TEST EXECUTION**

Experiment family: **EXP-O — Resilient Runtime Authority & Effect-Boundary Falsification**

Parent Pilot 12 adjudication commit: `c7c5d9dc05a6483e2def5e9abefe3bc1352f2fff`.

## Motivation

EXP-O Pilot 12 closed the same-host live cross-instance lease-steal boundary using a platform-trusted clock, owner+epoch fencing, and one SQLite serialization point. That result explicitly did **not** establish distributed consensus or multi-host partition safety.

The next unresolved boundary is authority-state replication. With multiple authority replicas, a stale or isolated replica/leader must not continue issuing, renewing, transferring, or revalidating consequential authority after it loses quorum. A majority partition must not overwrite an unexpired lease merely because the old owner is unreachable, and after a legitimate higher-term takeover the stale side must never roll authority state backward.

Pilot 13 therefore tests the stronger boundary:

> Consequential use-time authority exists only when the exact semantic/effect request is confirmed against a quorum-committed authority record in the current leadership term. Minority partitions and stale replicas are non-authoritative. A new majority leader may transfer ownership only under the frozen lease rules, and committed term/epoch/commit-index state is monotonic across partition, failover, and repair.

## Experiment type

Deterministic structural distributed-systems falsification using a **three-replica quorum simulation** with explicit partition topology, terms, commit indexes, trusted time, and replicated authority records. **No remote-model provider call is required.**

This is not a claim of production Raft/Paxos correctness. The simulation exists to falsify quorum/term/lease invariants before selecting or implementing a production consensus substrate.

Pilot 13 must use new versioned EXP-O-specific files. Finalized Pilot 12 implementation/evidence remains historically frozen.

## Frozen cluster and authority fixture

- authority replicas: exactly `r1`, `r2`, `r3`;
- quorum size: exactly 2 distinct replicas;
- initial term: 0, no leader;
- elected leader terms must increase monotonically;
- one platform-trusted deterministic clock for the simulation;
- lease duration: 1000 ms;
- action: `WRITE`;
- target resource: `src/app.py`;
- changed files: `src/app.py`;
- destructive effect: false;
- freshness class: `WORKSPACE_MUTATION`;
- effect contract: `contract-v1`;
- base SHA: `base-v1`;
- semantic verification: independently signed and exact as inherited from Pilots 9–12;
- model authority effect: none;
- merge/deploy/release authority: none;
- authoritative effect sink: durable idempotent MCP-style SQLite effect boundary;
- all execution decisions require current quorum authority revalidation at use time.

## Replicated state requirements

Each authority replica must retain at least:

- `current_term`;
- `leader_id` or explicit no-leader state;
- `commit_index`;
- exact authority record revision/digest;
- semantic permit identity and complete candidate/effect/worker/base/contract/idempotency bindings;
- `lease_owner_gateway_instance_id`;
- monotonically increasing `lease_epoch`;
- `lease_expires_at_ms`;
- state in `ISSUED`, `IN_FLIGHT`, `CONSUMED`;
- authoritative result digest when consumed.

A quorum commit certificate must bind at least:

- cluster identity;
- current term;
- commit index;
- authority record digest;
- owner gateway instance;
- lease epoch;
- lease expiry;
- exact semantic/effect/idempotency bindings;
- **two distinct voter replica IDs** from the frozen membership.

Duplicate voter identities, unknown replicas, stale terms, stale commit indexes, or mismatched record digests cannot create a quorum certificate.

## Frozen quorum semantics

### Leader authority

A replica may act as authoritative leader only when it can contact a quorum including itself and has been elected in the highest committed term known to that quorum.

A self-declared or stale leader in a minority partition has zero authority to:

- acquire a lease;
- renew a lease;
- transfer/take over a lease;
- finalize consumed state;
- mint a quorum certificate;
- authorize a consequential effect.

### Use-time revalidation

Every consequential execution must obtain a fresh quorum confirmation/certificate for the current exact authority record. Cached local state or an old certificate is insufficient after loss of quorum, term advance, owner/epoch change, expiry, or consumption.

### Unexpired lease under majority failover

Loss of the old leader/owner is **not** by itself authority to steal an unexpired lease. Unless an explicit separately authoritative revocation mechanism is implemented and preregistered, the new majority leader must preserve the old owner until trusted lease expiry.

### Takeover at expiry

At `trusted_now_ms >= lease_expires_at_ms`, an exact majority-authorized takeover may:

- change owner;
- advance lease epoch by exactly one;
- retain exact semantic/effect/idempotency identity;
- commit under the current leader term;
- assign a fresh trusted expiry;
- return a quorum certificate only after quorum commit.

### Monotonic repair

After partitions heal, stale replicas must catch up to the highest quorum-committed `(term, commit_index)` and may not overwrite or roll back newer owner/epoch/consumed state.

## Pre-registered falsification cases

Pilot 13 is not structurally green unless every case below is deterministically exercised.

### P13-01 — Three-member election requires two distinct voters
Elect `r1` in term 1 with `r1+r2` reachable.
Expected: leader `r1`, term 1. A duplicated `r1,r1` or one-node vote set cannot satisfy quorum.

### P13-02 — Initial exact authority acquisition is quorum committed
Acquire the exact semantic permit through term-1 leader `r1`.
Expected: owner A, lease epoch 1, commit index advances, at least `r1+r2` contain the identical committed record, and the returned certificate contains two distinct frozen voter IDs.

### P13-03 — Isolated former leader cannot revalidate consequential use
Partition `r1` alone while `r2+r3` remain connected, before lease expiry.
Expected: `r1` cannot obtain fresh quorum confirmation and cannot authorize or invoke the effect boundary even though its local record still says it is leader/owner.

### P13-04 — Minority former leader cannot renew
Expected: renewal through isolated `r1` denied; no authoritative expiry/epoch/commit-index change.

### P13-05 — Minority partition cannot advance term/epoch or mint authority
Expected: one-node side cannot elect a valid leader, cannot take over, cannot advance lease epoch, and cannot mint a valid quorum certificate.

### P13-06 — Majority partition elects a higher-term leader
Elect `r2` with `r2+r3` in term 2.
Expected: term monotonically advances 1 -> 2 on the majority; `r1` remains stale/non-authoritative.

### P13-07 — New majority leader cannot steal an unexpired old lease
Before trusted expiry, submit the exact request through `r2`.
Expected: takeover denied solely because lease remains unexpired; owner A and lease epoch 1 remain unchanged in quorum-committed state.

### P13-08 — Exact expiry allows majority takeover under higher term
At exactly `lease_expires_at_ms`, submit the exact request through `r2` for owner B.
Expected: quorum commit succeeds in term 2; owner becomes B; lease epoch advances 1 -> 2 exactly once; fresh trusted expiry and new commit index assigned.

### P13-09 — Stale term-1 leader cannot use, renew, finalize, or overwrite after takeover
While `r1` remains stale, exercise all four paths.
Expected: every path denied; no effect or authority-state mutation.

### P13-10 — Stale replica read cannot be promoted to authoritative use
Read the old owner/epoch from stale `r1` and attempt consequential execution using that local view or an old term-1 certificate.
Expected: use-time quorum revalidation rejects it; no effect.

### P13-11 — Competing leadership claims cannot both commit authority
Create a topology in which `r2+r3` form the only majority while stale `r1` claims leadership separately.
Expected: only the majority leader can produce a new committed authority revision/certificate; minority claim remains non-authoritative.

### P13-12 — Total quorum loss fails closed
Partition all three replicas from each other.
Expected: no acquire, renew, takeover, finalize, or consequential execution can be newly authorized from any replica.

### P13-13 — Quorum restoration preserves highest committed term/index
Heal a quorum containing one stale and one current replica.
Expected: stale state catches up to the highest quorum-committed term/commit index before authoritative service; no rollback to the older owner/epoch/expiry.

### P13-14 — Stale replica cannot serve authoritative read until caught up
Before catch-up, explicitly request an authoritative read/use through the stale node.
Expected: fail closed or redirect/non-authoritative response. After catch-up and quorum confirmation, the node may expose the current state but never the stale state as authority.

### P13-15 — Effect remains exactly once across leader crash after commit ambiguity
After a valid quorum-authorized execution reaches the idempotent effect boundary, crash/replace the current leader before final replicated consumption acknowledgement completes.
Expected: subsequent higher-term recovery reconciles the same logical effect/idempotency identity; authoritative effect count remains exactly one and consumed state converges monotonically.

### P13-16 — Fresh clean authority remains live after partition and repair
After partition, higher-term election, stale-node repair, and recovery, issue a fresh independently verified permit.
Expected: current quorum leader acquires/executes exactly once with a current certificate, demonstrating quorum safety is not blanket denial.

## Critical failures

Any of the following falsifies the Pilot 13 boundary:

- one replica or duplicate voter IDs satisfy quorum;
- minority/stale leader can mint or reuse effective consequential authority after losing quorum;
- cached/stale replica state is accepted as use-time authority without current quorum confirmation;
- majority leader steals an unexpired lease without a separately preregistered revocation decision;
- term, lease epoch, or commit index rolls backward;
- two competing leadership sides both commit effective authority for the same permit revision;
- takeover at expiry does not advance lease epoch exactly once;
- old-term owner can renew/finalize/use after higher-term takeover;
- total quorum loss still allows new consequential authority;
- stale state overwrites newer state during repair;
- changed semantic/effect/idempotency binding survives takeover/revalidation;
- failover/recovery produces more than one authoritative effect;
- consumed state revives;
- fresh clean authority cannot execute after repair.

## Evidence requirements

Retain/assert at minimum:

- topology/connectivity before each decision;
- replica IDs participating in election and each quorum commit;
- current term and leader view per replica;
- commit index per replica;
- authority record digest per replica;
- owner/lease epoch/expiry/state per replica;
- trusted clock at lease decisions;
- certificate term/index/voters/digest;
- authoritative vs non-authoritative read classification;
- denial reason for minority/stale/quorum-loss paths;
- effect count before/after;
- recovery/reconciliation disposition;
- final converged state after partition heal.

## Allowed interpretation if green

> Within the tested deterministic three-replica EXP-O quorum simulation, consequential authority required current majority confirmation, minority and stale leaders could not mint or revalidate effective authority, unexpired leases were not stolen during failover, higher-term expiry takeover advanced the fence monotonically, stale replicas could not roll state backward, and authoritative effects remained at most once across the tested partition/recovery paths.

Do **not** generalize this result to a production consensus algorithm, real multi-host networking, asynchronous timing, packet duplication/reordering, clock synchronization across machines, disk corruption, Byzantine replicas, membership changes, joint consensus, TLS/workload identity, geographically distributed quorum latency, or multi-region disaster recovery.

## EXP-N isolation

Pilot 13 must not modify, execute, import into, or consume the frozen EXP-N Pilot 8 recovery or EXP-N Pilot 9 execution paths.