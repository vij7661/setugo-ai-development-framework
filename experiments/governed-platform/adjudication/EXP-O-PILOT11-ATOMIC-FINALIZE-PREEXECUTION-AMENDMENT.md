# EXP-O Pilot 11 — Atomic Owner-Fenced Finalization Pre-Execution Amendment

Status: **PRE-REGISTERED BEFORE PILOT 11 TEST EXECUTION**

Parent preregistration: `EXP-O-PILOT11-INFLIGHT-OWNERSHIP-FENCING-PREREGISTRATION.md`

## Reason for amendment

During implementation review, before any Pilot 11 falsification test execution, the initial draft separated:

1. a lease owner/epoch check; and
2. finalization of the underlying Pilot 10 semantic permit registry

into different SQLite transactions.

That creates a TOCTOU window: a new gateway instance could take over the lease after the old owner passes its check but before the old owner finalizes the underlying semantic permit. A green test suite that did not close that window could therefore overstate stale-owner fencing.

## Amendment

Pilot 11 must place the ownership/fencing record in the **same SQLite database** as the Pilot 10 semantic-permit registry and perform the authoritative finalization transition in one `BEGIN IMMEDIATE` transaction that:

- verifies lease-record integrity;
- verifies state `IN_FLIGHT`;
- verifies exact current `lease_owner_gateway_instance_id`;
- verifies exact current `lease_epoch`;
- verifies the underlying Pilot 10 semantic-permit record and its integrity;
- requires the underlying Pilot 10 record to be `IN_FLIGHT`;
- writes the authoritative result digest and transitions the Pilot 10 record to `CONSUMED`;
- writes the same authoritative result digest and transitions the Pilot 11 lease record to `CONSUMED`; and
- commits both state transitions atomically.

If ownership/epoch changes first, the stale finalizer fails without changing either record. If the finalizer commits first, later takeover sees `CONSUMED` and fails.

The ownership acquisition/takeover transition and the underlying P10 `ISSUED/IN_FLIGHT` state remain durably checked. Exact crash/recovery behavior continues to rely on MCP idempotency for ambiguity after an effect commit but before the joint semantic/lease finalization transaction.

## Scientific endpoint impact

- Pilot 11 hypothesis changed: **false**
- preregistered cases changed: **false**
- success/failure criteria changed: **false**
- authority scope changed: **false**
- effect scope changed: **false**
- provider/model sampling changed: **not applicable; no provider call**
- implementation strength increased before test execution: **true**

This amendment closes a pre-test false-green opportunity and does not relax any preregistered requirement.