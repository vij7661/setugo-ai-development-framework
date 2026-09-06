# EXP-O Pilot 11 — IN_FLIGHT Ownership and Recovery Fencing Preregistration

Status: **PRE-REGISTERED BEFORE PILOT 11 IMPLEMENTATION OR EXECUTION**

Experiment family: **EXP-O — Resilient Runtime Authority & Effect-Boundary Falsification**

Parent Pilot 10 adjudication commit: `1d7c68ca265fb9ab501c38ff27b6aa75ade72f89`.

## Motivation

EXP-O Pilot 10 proved the tested process-separated semantic-bound permit path could keep raw inner LEP permits server-side, preserve semantic/effect/idempotency bindings, survive restart, and reconcile a post-effect crash without duplicating the authoritative effect.

A narrower concurrency ambiguity remains in the Pilot 10 registry lifecycle. `IN_FLIGHT` currently means only that some gateway use has begun. An exact second request can observe `IN_FLIGHT` and enter the same recovery path even when the original gateway instance is still alive. Historical MCP idempotency prevents duplicate committed effects, but that alone does not prove **exclusive live ownership of execution authority** at the semantic-bound gateway layer.

Pilot 11 separates:

- a legitimate restart takeover of abandoned `IN_FLIGHT` work; from
- a concurrent duplicate arriving while the current gateway instance still owns the in-flight permit.

The target property is not merely "at most one effect." It is:

> At most one live gateway instance owns active use-time authority for a semantic-bound permit at a given fencing epoch; same-owner concurrent duplicates cannot acquire a second active authorization, while a new gateway instance may take over an abandoned exact request under a strictly higher durable lease epoch.

## Experiment type

Deterministic structural/process-concurrency falsification. **No remote-model provider call is required.**

Pilot 11 must be implemented in new EXP-O-specific files or a versioned Pilot 11 wrapper/subclass. Finalized Pilot 10 evidence remains historically frozen at its adjudicated commit.

## Frozen authority/effect fixture

Unless a case explicitly mutates one field for a falsifier:

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
- transport: separate child gateway process over loopback HTTP
- authoritative effect store: existing MCP SQLite idempotency boundary

## Required Pilot 11 registry ownership fields

The Pilot 11 registry record must durably bind at least:

- `lease_owner_gateway_instance_id`;
- monotonically increasing `lease_epoch`;
- `state` in `ISSUED`, `IN_FLIGHT`, `CONSUMED`;
- the complete Pilot 10 candidate/effect/capability/worker/base/contract/idempotency bindings;
- registry integrity tag over the ownership/fencing fields as well as the semantic bindings.

Ownership/fencing fields are platform state. They are never accepted from the model/caller as authority.

## Required ownership semantics

### First use

For an `ISSUED` exact permit:

- current gateway instance atomically becomes owner;
- state becomes `IN_FLIGHT`;
- `lease_epoch` advances from 0 to 1;
- gateway receives a trusted resolution token containing/binding the current owner and epoch;
- only that owner+epoch may subsequently finalize that attempt.

### Same live owner duplicate

If state is `IN_FLIGHT` and `lease_owner_gateway_instance_id == current_gateway_instance_id`:

- a second request must **not** obtain a second active inner-permit resolution;
- it must fail closed or return an explicitly non-authorizing `IN_FLIGHT_ALREADY_OWNED`/equivalent status;
- authoritative effect count must not increase because of the rejected duplicate.

### Restart takeover

If state is `IN_FLIGHT` and the requesting gateway has a **different platform-generated gateway instance ID**:

- exact unchanged request may take over only through the explicit recovery path;
- `lease_epoch` must atomically increase;
- owner changes to new gateway instance;
- historical inner permit/effect/idempotency binding remains unchanged;
- changed candidate/effect/worker/idempotency cannot use takeover;
- new owner may reconcile via existing MCP idempotency.

Pilot 11 does not claim that differing instance ID alone is sufficient in production to prove prior owner death. This is a controlled crash/restart pilot where the harness owns process lifecycle. The bounded claim is fencing behavior under that controlled lifecycle.

### Stale owner fencing

After a new instance takes over at a higher `lease_epoch`, any completion/finalization attempt from the old owner/old epoch must fail closed and must not change `CONSUMED`, result digest, or effect count.

## Pre-registered falsification cases

Pilot 11 is not structurally green unless every case below is deterministically exercised.

### P11-01 — First use acquires owner epoch 1
Expected: exact request transitions `ISSUED -> IN_FLIGHT`, owner=current gateway instance, epoch=1 before MCP effect; clean completion finalizes `CONSUMED` under owner/epoch 1.

### P11-02 — Same-instance duplicate while first request is held IN_FLIGHT
Hold the first request after durable ownership acquisition but before MCP execution. Submit the exact same request concurrently to the same gateway instance.
Expected: second request does not resolve raw inner permit, does not execute, and reports non-authorizing already-owned/in-flight status.

### P11-03 — Same-instance duplicate cannot manufacture two authorization-success responses
Expected: for the controlled concurrent pair, at most one request may receive a fresh execution-authorizing path. The loser may report busy/already-owned but not `authorized=true` as a second live execution authorization.

### P11-04 — Concurrent duplicate authoritative effects remain exactly one
Release the held winner and complete it.
Expected: total authoritative effect count=1.

### P11-05 — Changed candidate cannot bypass live-owner fence
While candidate A is `IN_FLIGHT` under current owner, send candidate B under A's permit.
Expected: semantic/outer binding denial before ownership takeover/resolution; zero new effect.

### P11-06 — Changed effect cannot bypass live-owner fence
Expected: exact binding denial; zero new effect.

### P11-07 — Same external idempotency key with changed semantic effect remains denied
Expected: Pilot 10 semantic-idempotency protection remains intact under lease/fencing changes.

### P11-08 — Crash leaves durable owner+epoch with IN_FLIGHT state
Crash the owning gateway after ownership acquisition and before effect.
Expected: registry remains `IN_FLIGHT`, old owner ID retained, epoch=1, no effect.

### P11-09 — New gateway instance exact takeover advances epoch
Restart gateway, submit exact unchanged request.
Expected: takeover succeeds only for new instance, owner changes, epoch=2, and request may execute/reconcile exactly once.

### P11-10 — Old owner epoch cannot finalize after takeover
Use a deterministic trusted-harness stale-finalization probe representing the old owner/epoch after new-owner takeover.
Expected: denied as stale/fenced; no registry/effect mutation.

### P11-11 — Takeover with changed candidate denied
Expected: no owner/epoch change and no effect.

### P11-12 — Takeover with changed idempotency key denied
Expected: no owner/epoch change and no effect.

### P11-13 — Post-effect/pre-finalize crash takeover reconciles without duplicate
Winner commits authoritative MCP effect, crashes before semantic-registry finalization, then a new gateway instance takes over exact request at higher epoch.
Expected: MCP returns idempotent historical result; registry finalizes `CONSUMED`; effect count remains one.

### P11-14 — Stale owner cannot overwrite new owner's authoritative result digest
After takeover/finalization, old owner+epoch attempts finalize with either the same or a different result digest.
Expected: stale owner is denied in both cases; committed result digest remains unchanged.

### P11-15 — Consumed permit cannot be taken over by any later instance
Expected: restart after `CONSUMED` does not advance lease epoch or owner and cannot authorize another effect.

### P11-16 — Fresh clean permit after concurrency/restart remains live
Issue a new independently verified permit after the race/restart cases.
Expected: fresh exact request executes exactly once, proving ownership fencing is not blanket denial.

## Critical failures

Any of the following falsifies the Pilot 11 boundary:

- same live gateway instance obtains two active inner-permit resolutions for one bound permit;
- same-instance concurrent duplicate returns a second fresh `authorized=true` execution path;
- takeover does not advance a durable monotonically increasing lease epoch;
- stale owner/epoch can finalize after takeover;
- changed candidate/effect/idempotency can use restart takeover;
- consumed permit can be revived by a later gateway instance;
- concurrency or recovery produces more than one authoritative effect;
- clean fresh requests can no longer execute.

## Evidence requirements

Retain/assert:

- gateway instance IDs;
- lease owner and lease epoch before/after each transition;
- durable registry state;
- whether inner permit resolution occurred;
- whether gateway invocation occurred;
- HTTP response classification for winner/loser;
- effect count before/after;
- authoritative result digest;
- idempotent replay disposition;
- stale-finalization denial reason.

## Allowed interpretation if green

> Within the tested EXP-O loopback process lifecycle, semantic-bound permit use was fenced to one live gateway owner per lease epoch; same-instance concurrent duplicates could not acquire a second active execution authorization, controlled restart takeover required an exact unchanged request and advanced a durable epoch, stale owners could not finalize after takeover, and authoritative effects remained at most once.

Do not generalize this to distributed consensus, split-brain prevention across hostile hosts, lease-expiry correctness, Byzantine gateways, production liveness detection, TLS identity, or multi-region failover.

## EXP-N isolation

Pilot 11 must not modify, execute, import into, or consume the frozen EXP-N Pilot 8 recovery or EXP-N Pilot 9 execution paths.