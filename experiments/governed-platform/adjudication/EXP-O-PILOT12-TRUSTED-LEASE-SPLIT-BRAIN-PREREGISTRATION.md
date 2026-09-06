# EXP-O Pilot 12 — Trusted Lease Expiry and Live Cross-Instance Split-Brain Fencing Preregistration

Status: **PRE-REGISTERED BEFORE PILOT 12 IMPLEMENTATION OR TEST EXECUTION**

Experiment family: **EXP-O — Resilient Runtime Authority & Effect-Boundary Falsification**

Parent Pilot 11 adjudication commit: `8429e7fff058c99757e0c70c475a10e5e84ed114`.

## Motivation

EXP-O Pilot 11 established, within a controlled same-host crash/restart lifecycle, one active gateway owner per lease epoch and exact restart takeover under a higher epoch. Its bounded recovery rule deliberately allowed a different platform-generated gateway instance ID to take over an `IN_FLIGHT` exact request because the harness itself proved that the previous gateway had crashed.

That rule is not sufficient when two different gateway processes may both still be alive. A second live gateway could otherwise present the exact same permit and acquire a higher epoch merely because its instance ID differs, displacing a still-authorized owner. Historical MCP idempotency can prevent duplicate committed effects but cannot by itself prove that two live gateways did not simultaneously obtain active execution authority.

Pilot 12 therefore tests a stronger platform boundary:

> A different gateway instance cannot displace a still-live, unexpired owner merely by presenting an exact request. Cross-instance takeover is authorized only after platform-trusted lease expiry (or a separately authoritative revocation/death decision, if explicitly implemented), and takeover atomically advances the fencing epoch. Caller/model time claims never determine lease expiry.

## Experiment type

Deterministic structural/process-concurrency falsification. **No remote-model provider call is required.**

Pilot 12 must use new versioned EXP-O-specific files or wrappers. Finalized Pilot 11 implementation/evidence remains historically frozen.

## Frozen authority/effect fixture

Unless a case explicitly changes one field for a falsifier:

- action: `WRITE`
- target resource: `src/app.py`
- changed files: `src/app.py`
- destructive effect: false
- freshness class: `WORKSPACE_MUTATION`
- effect contract: `contract-v1`
- base SHA: `base-v1`
- semantic verification: independently signed and exact
- model authority effect: none
- merge/deploy/release authority: none
- transport: separate child gateway processes over loopback HTTP
- authoritative effect store: existing MCP SQLite idempotency boundary
- ownership/fencing store: integrity-protected SQLite platform state
- lease duration: **1000 ms**
- lease-time authority: **platform-trusted clock only**

## Trusted-time semantics

Pilot 12 must not accept worker/model/caller-supplied time as authority for lease acquisition, renewal, expiry, or takeover.

The authoritative lease clock must be platform-controlled and read inside the trusted lease/fencing boundary. The test harness may advance that clock deterministically, but gateway request payloads cannot set or override it.

Frozen expiry boundary:

- lease is active while `trusted_now_ms < lease_expires_at_ms`;
- takeover may become eligible when `trusted_now_ms >= lease_expires_at_ms`;
- exact `lease_expires_at_ms - 1` must deny cross-instance takeover;
- exact `lease_expires_at_ms` may permit exact takeover;
- this boundary must be explicitly tested.

## Required lease state

The Pilot 12 durable ownership record must bind at least:

- `lease_owner_gateway_instance_id`;
- monotonically increasing `lease_epoch`;
- `lease_expires_at_ms`;
- `state` in `ISSUED`, `IN_FLIGHT`, `CONSUMED`;
- complete Pilot 10/Pilot 11 candidate/effect/capability/worker/base/contract/idempotency bindings;
- integrity protection covering lease owner, epoch, expiry and semantic/effect bindings.

Lease owner/epoch/expiry are platform state, never model or caller authority.

## Required ownership semantics

### First use

For an exact `ISSUED` permit, the trusted boundary atomically:

- sets owner to the current gateway instance;
- advances epoch 0 -> 1;
- sets `lease_expires_at_ms = trusted_now_ms + 1000`;
- transitions to `IN_FLIGHT`;
- resolves exactly one active execution path for owner+epoch.

### Same current owner before expiry

A duplicate execution attempt must remain non-authorizing as in Pilot 11. A separate explicit renewal operation may extend the lease only if:

- caller is the exact current owner gateway instance;
- caller presents the exact current epoch;
- state is `IN_FLIGHT`;
- lease has not already been displaced or consumed;
- trusted clock is used.

Successful renewal extends expiry and **does not change lease epoch**.

### Different live gateway before expiry

Even for an exact unchanged request, if `trusted_now_ms < lease_expires_at_ms`, a different gateway instance must fail closed with a non-authorizing live-owner/unexpired-lease classification. It must not:

- resolve the raw inner permit;
- change owner;
- change epoch;
- change expiry;
- invoke MCP;
- increase effect count.

### Cross-instance takeover at/after trusted expiry

At `trusted_now_ms >= lease_expires_at_ms`, a different gateway may take over only if the request is otherwise exact and unchanged. The takeover must atomically:

- verify trusted expiry;
- verify exact semantic/effect/capability/worker/base/contract/idempotency bindings;
- change owner to the new gateway;
- advance epoch by exactly one;
- assign a fresh platform lease expiry;
- preserve the underlying semantic permit/effect/idempotency identity.

### Stale owner after takeover

The old owner and old epoch must be unable to renew, finalize, or execute after the new owner has taken over.

## Pre-registered falsification cases

Pilot 12 is not structurally green unless every case below is deterministically exercised.

### P12-01 — First owner receives trusted lease deadline
Expected: first exact use becomes owner at epoch 1, with expiry exactly trusted acquisition time + 1000 ms.

### P12-02 — Different live gateway before expiry cannot take over
Hold owner A `IN_FLIGHT` before effect. Start gateway B while A remains alive. Submit exact same request through B at `expiry - 1` or earlier.
Expected: B non-authorizing; owner/epoch/expiry unchanged; no B inner-permit resolution/effect.

### P12-03 — Failed pre-expiry takeover cannot mutate fencing state
Expected: after P12-02 denial, durable owner remains A, epoch remains 1, expiry unchanged and effect count unchanged.

### P12-04 — Current owner can renew before expiry without epoch change
Expected: explicit renewal by A at current epoch extends expiry from trusted clock and keeps epoch 1.

### P12-05 — Non-owner cannot renew current lease
Expected: B renewal attempt denied; owner, epoch and expiry unchanged.

### P12-06 — Caller/model time claim cannot force early expiry
Send a request carrying a fabricated future/backdated time field if the transport accepts opaque metadata, or directly exercise the trusted registry API with an untrusted time argument if such a legacy surface exists.
Expected: the claim is ignored/rejected as authority; trusted clock controls decision; no early takeover.

### P12-07 — Exact expiry boundary is deterministic
Expected: B takeover at `expiry - 1` is denied; B takeover at exactly `expiry` may succeed if otherwise exact. No ambiguous off-by-one behavior.

### P12-08 — Exact post-expiry takeover advances epoch
Expected: exact B takeover at/after trusted expiry succeeds, owner becomes B, epoch advances 1 -> 2, fresh expiry is assigned from trusted clock.

### P12-09 — Old owner cannot finalize after expiry takeover
Expected: A/epoch1 stale finalization denied; no result/effect mutation.

### P12-10 — Old owner cannot renew after takeover
Expected: A/epoch1 renewal denied and cannot extend B's lease.

### P12-11 — Changed candidate cannot use expired-lease takeover
Expected: semantic binding denial; no owner/epoch/effect change.

### P12-12 — Changed effect or idempotency binding cannot use takeover
Expected: exact binding denial; no owner/epoch/effect change.

### P12-13 — Two different live gateways racing at expiry yield one next owner
With old lease expired, race exact takeover attempts from gateway B and gateway C.
Expected: exactly one becomes epoch-2 owner. The loser is non-authorizing and cannot obtain a second fresh execution path. Epoch must not jump twice merely because two takeover requests race.

### P12-14 — Post-effect/pre-finalize ambiguity remains exactly once
After a valid expiry takeover commits the MCP effect but crashes before joint finalization, subsequent exact recovery reconciles the historical effect without duplicate authoritative effect.

### P12-15 — Consumed permit cannot be revived after lease expiry
Expected: later trusted time advancement and new gateway instances cannot take over or authorize another effect after `CONSUMED`.

### P12-16 — Fresh clean permit remains live
Issue a new independently verified permit after expiry/race/recovery cases.
Expected: normal first-owner execution succeeds exactly once, proving trusted lease fencing is not blanket denial.

## Critical failures

Any of the following falsifies the Pilot 12 boundary:

- different live gateway acquires active authority before trusted lease expiry;
- failed pre-expiry takeover changes owner, epoch or expiry;
- caller/model time claim can force lease expiry/takeover;
- non-owner can renew a lease;
- renewal changes fencing epoch without ownership transfer;
- takeover at/after expiry fails to advance epoch exactly once;
- two racing takeover gateways both obtain fresh active execution authorization;
- stale owner can renew/finalize after takeover;
- changed semantic/effect/idempotency binding can use expiry takeover;
- consumed permit can be revived;
- concurrency/recovery produces more than one authoritative effect;
- fresh clean requests cannot execute.

## Evidence requirements

Retain/assert at minimum:

- gateway instance IDs for incumbent and contenders;
- trusted clock value at every acquire/renew/takeover decision;
- lease expiry before/after;
- owner and epoch before/after;
- registry state before/after;
- takeover/renewal decision and denial reason;
- whether inner permit resolution occurred;
- whether MCP gateway invocation occurred;
- effect count before/after;
- authoritative result digest/replay disposition;
- stale renewal/finalization denial reasons.

## Allowed interpretation if green

> Within the tested EXP-O same-host process boundary using a platform-trusted lease clock, an unexpired live semantic-permit owner could not be displaced by another gateway instance; cross-instance takeover of the exact request became eligible only at/after trusted lease expiry, atomically advanced the fencing epoch, stale owners could not renew or finalize afterward, and authoritative effects remained at most once.

Do **not** generalize this result to distributed consensus, production-grade failure detection, hostile multi-host split-brain prevention, clock synchronization across machines, Byzantine gateways, network partitions, quorum safety, TLS workload identity, or multi-region failover.

## EXP-N isolation

Pilot 12 must not modify, execute, import into, or consume the frozen EXP-N Pilot 8 recovery or EXP-N Pilot 9 execution paths.