# EXP-O Pilot 14 — Independent-Process Network Quorum Authority Preregistration

Status: **PRE-REGISTERED BEFORE PILOT 14 IMPLEMENTATION OR TEST EXECUTION**

Experiment family: **EXP-O — Resilient Runtime Authority & Effect-Boundary Falsification**

Parent Pilot 13 adjudication commit: `806e5d3868298cc962f447b28305ac5788c89386`.

## Motivation

Pilot 13 established the frozen quorum/term/lease invariants only inside one deterministic Python process. It did not test independent replica lifecycles, per-node durable state, authenticated inter-node messages, transport failures, delayed/stale acknowledgements, duplicated messages, or process crashes.

Pilot 14 moves the same authority boundary across a real process/network boundary without claiming production consensus correctness.

> A consequential authority decision is valid only when an independent leader process obtains fresh authenticated acknowledgements from a majority of distinct replica processes for the exact current authority revision. Lost, delayed, duplicated, stale, unauthenticated, or replayed peer messages cannot manufacture quorum or revive stale authority.

## Experiment type

Deterministic structural/process/network falsification using three independent Python replica server processes over loopback HTTP, one separate SQLite authority store per replica, authenticated inter-node envelopes, a platform-controlled trusted clock, and deterministic transport fault injection.

**No remote-model provider call is required.**

This is a prototype falsification harness, not a production Raft/Paxos implementation.

## Frozen topology and authority fixture

- replica processes: exactly `r1`, `r2`, `r3`;
- one OS process and one SQLite authority database per replica;
- quorum: exactly 2 distinct authenticated replica identities;
- loopback HTTP transport;
- inter-node authentication: HMAC-SHA256 pilot key over canonical message envelope;
- each authenticated envelope binds: cluster id, sender replica id, receiver replica id, message type, term, message id, payload digest;
- replay cache/message ledger is durable per receiving replica;
- initial term: 0;
- leader terms strictly monotonic;
- trusted lease duration: 1000 ms;
- platform-controlled clock is read inside replica process authority decisions; caller-supplied time is non-authoritative;
- action: `WRITE`;
- target/changed resource: `src/app.py`;
- destructive effect: false;
- freshness class: `WORKSPACE_MUTATION`;
- effect contract: `contract-v1`;
- base SHA: `base-v1`;
- exact semantic/effect/worker/idempotency bindings inherited from Pilot 13;
- model authority effect: none;
- merge/deploy/release authority: none;
- effect sink: durable idempotent SQLite effect boundary;
- every consequential effect requires a fresh majority confirmation from live replica processes in the current term.

## Required process/network properties

1. Replica identity comes from process configuration and authenticated message keying, never from caller-provided display labels.
2. A quorum counts distinct authenticated member identities only.
3. Each receiver durably rejects a repeated `message_id` with conflicting payload.
4. Exact duplicate delivery is idempotent and cannot count a voter twice.
5. A stale-term acknowledgement cannot satisfy a current-term quorum.
6. An acknowledgement for a different record digest, commit index, owner, epoch or expiry cannot satisfy the exact authority decision.
7. A leader that cannot obtain a majority response before the bounded operation deadline fails closed.
8. Delayed responses arriving after the operation has failed/term has advanced cannot retroactively create authority.
9. Replica restart reloads durable term/index/authority/message-ledger state before serving authoritative traffic.
10. Current majority failover preserves an unexpired lease; exact takeover is eligible only at/after trusted expiry.

## Deterministic fault vocabulary

The test harness may inject only predeclared transport faults:

- `DROP`: message not delivered;
- `DUPLICATE`: exact authenticated envelope delivered twice;
- `DELAY_UNTIL_RELEASE`: delivery/response held until harness release;
- `CORRUPT_AUTH`: signature/tag altered before receiver verification;
- `STALE_TERM_REPLAY`: previously valid authenticated response replayed after a higher term exists;
- `STALE_REVISION_REPLAY`: previously valid acknowledgement replayed for a newer authority revision;
- `REORDER`: a delayed older message is released after a newer message has already committed.

Fault injection changes transport scheduling only; it cannot directly mutate replica authority databases.

## Pre-registered falsification cases

### P14-01 — Replica processes are physically independent and durably identified
Expected: three distinct PIDs, three distinct database paths, fixed replica IDs, and no shared in-memory authority object.

### P14-02 — Two authenticated distinct process votes elect term-1 leader
Expected: `r1` elected with `r1+r2`; one vote or duplicate `r1` acknowledgement cannot elect.

### P14-03 — Forged/unauthenticated peer acknowledgement cannot satisfy quorum
Corrupt the peer authentication tag.
Expected: receiver/leader rejects it; no term/index/authority advance.

### P14-04 — Duplicate delivery cannot manufacture a second voter
Deliver the same valid `r2` acknowledgement twice.
Expected: it counts once; durable message identity prevents conflicting replay; no synthetic quorum from one peer identity.

### P14-05 — Exact authority acquisition commits to two independent durable stores
Expected: leader and one follower persist identical current record digest, term and commit index before a quorum certificate is returned.

### P14-06 — Lost peer messages make isolated former leader fail closed at use time
Partition/drop both outgoing peer confirmations from `r1`.
Expected: stale/local state and cached certificate cannot authorize effect; effect count stays zero.

### P14-07 — Delayed acknowledgement cannot retroactively authorize after timeout
Hold the only peer acknowledgement until the leader operation fails closed, then release it.
Expected: the completed failed operation remains failed; delayed response cannot create an effect or authority certificate later.

### P14-08 — Higher-term majority failover preserves unexpired old lease
Allow `r2+r3` to elect term 2 while `r1` is isolated, before lease expiry.
Expected: majority leader exists but exact owner/epoch remain unchanged and takeover is denied until expiry.

### P14-09 — Stale-term authenticated response cannot satisfy term-2 quorum
Replay a valid term-1 response after term 2 election.
Expected: rejected as stale; cannot count toward current majority confirmation.

### P14-10 — Exact trusted expiry permits term-2 takeover and epoch advance once
At exact expiry, current majority performs exact takeover.
Expected: owner changes, epoch 1 -> 2, commit index advances, two durable stores converge, certificate binds term 2/current revision.

### P14-11 — Reordered old authority message cannot roll back committed takeover
Delay an older term-1/epoch-1 replication message, commit term-2/epoch-2 takeover, then release old message.
Expected: receivers reject/ignore the reordered stale update; no term/index/owner/epoch rollback.

### P14-12 — Replica restart preserves stale fencing and replay ledger
Restart a stale/previous replica process after term-2 takeover.
Expected: it reloads durable old state, does not self-promote, rejects conflicting message-id replay, and cannot serve authoritative state until current-majority catch-up.

### P14-13 — Total process-level quorum loss denies all new consequential authority
Drop all inter-node traffic while processes remain alive.
Expected: acquire/renew/takeover/finalize/effect paths fail closed; local HTTP availability does not equal authority availability.

### P14-14 — Network heal/catch-up converges without rollback
Restore connectivity and synchronize stale replica from current majority.
Expected: highest committed term/index/revision wins; stale state cannot overwrite current state.

### P14-15 — Post-effect leader crash plus higher-term recovery remains exactly once
After current quorum authorization reaches the idempotent effect sink, terminate leader before replicated consumption acknowledgement completes. Elect a higher-term leader and retry exact logical effect.
Expected: replay reconciles; effect count stays one; consumed/current state converges monotonically.

### P14-16 — Fresh clean authority remains live after faults, restart and repair
Issue a fresh independently bound permit after the fault matrix.
Expected: current leader obtains fresh authenticated quorum, executes exactly once, and persists consumed state to a quorum.

## Critical failures

Pilot 14 is falsified if any tested path shows:

- one process/one identity/duplicate response satisfies quorum;
- unauthenticated or corrupted peer message influences authority state;
- exact duplicate transport delivery counts twice;
- conflicting replay with reused message ID is accepted;
- cached/local authority permits effect after live quorum loss;
- delayed response retroactively changes a completed deny into effective authority;
- stale-term or stale-revision response satisfies current quorum;
- higher-term leader steals an unexpired lease;
- exact expiry takeover fails to advance epoch exactly once;
- reordered stale message rolls term/index/owner/epoch backward;
- restarted stale replica self-promotes or serves stale state as authoritative;
- total inter-node partition still permits new consequential authority;
- repair overwrites newer committed state with stale state;
- failover/recovery causes more than one authoritative effect;
- fresh clean liveness is lost.

## Evidence requirements

Retain/assert at minimum:

- replica PID, replica ID and DB path;
- process start/restart identity;
- per-node term, leader, commit index, authority digest, owner, lease epoch/expiry/state;
- message sender/receiver/type/id/term/payload digest/authentication result;
- replay-ledger disposition;
- injected fault and release ordering;
- quorum voter identities used by each authority decision;
- operation start/finish disposition and timeout/failure classification;
- trusted clock value for lease decisions;
- effect count and idempotent replay disposition;
- final converged state after repair.

## Allowed interpretation if green

> Within the tested three-process loopback-HTTP EXP-O prototype, consequential authority required fresh authenticated majority confirmation from distinct replica processes; duplicate, forged, delayed, stale and reordered peer messages did not manufacture effective authority; unexpired lease ownership survived majority failover; exact-expiry takeover advanced the fence; process restart and partition recovery did not roll authority state backward; and the tested crash/recovery path retained at-most-once effects.

Do **not** generalize this result to production consensus correctness, arbitrary asynchronous networks, unbounded delay, Byzantine nodes, compromised keys/hosts, real TLS/mTLS, disk corruption, fsync/power-loss semantics, dynamic membership, joint consensus, clock synchronization across machines, WAN/multi-region operation, or formal linearizability.

## EXP-N isolation

Pilot 14 must use new EXP-O-only paths and must not modify, import into, execute, or consume the frozen EXP-N Pilot 8 recovery or EXP-N Pilot 9 execution paths.