# EXP-O Pilot 4 — Trusted Time + Process/Transport Boundary Preregistration

Status: **PRE-REGISTERED BEFORE PILOT 4 IMPLEMENTATION**

Experiment family: **EXP-O — Resilient Runtime Authority & Effect-Boundary Falsification**

Parent/head before this preregistration: `c7b1c520ad31d61c4f56c39b460cb8cda521ef29`

Predecessor finding: `EXP-O-PILOT3-POSTHOC-TRUSTED-TIME-FINDING.md`

## Purpose

Correct the Pilot 3 worker-controlled-time defect and move the MCP admission boundary into a separate OS process reached through an actual loopback HTTP transport.

Target path:

`Authority Kernel -> trusted-clock LEP -> Agent/Client -> loopback HTTP -> separate MCP Gateway process -> durable gateway ledger`

The durable evidence spool remains on the client side for this pilot and records transport provenance and reconciliation evidence.

This pilot remains isolated from EXP-N Pilot 8/9 provider execution paths.

## Frozen security rules

1. A worker/request may not provide the current time used for security decisions.
2. Current time is obtained inside the trusted LEP and inside the gateway process.
3. Deterministic tests may control time only through a trusted clock configured at component/process construction/startup, not in the action request payload.
4. A capability may be used only if the trusted LEP clock says it is unexpired/current.
5. A permit may be used only if the trusted gateway clock says it is unexpired/current.
6. A request field named `now_ms`, `current_time`, `timestamp`, or equivalent is ordinary untrusted payload and must not alter authority freshness/expiry.
7. The gateway process accepts only a valid LEP-signed exact-effect permit.
8. Gateway idempotency state is durable across process restart.
9. Connection/response loss after commit must not create a second authoritative effect on retry.
10. A clean control must remain executable; fail-closed behavior may not be achieved by blocking everything.

Cryptography remains HMAC-SHA256 for pilot scope only. Transport is loopback HTTP only; this is not TLS/mTLS evidence.

## Pre-registered cases

### P4-01 Legacy defect reproduction
The historical Pilot 3 path must demonstrate that caller-supplied backdated `now_ms` can influence expiry/freshness. This is retained as evidence of the discovered defect, not as acceptable behavior.

### P4-02 Trusted LEP clock ignores worker time claims
A capability expired according to the LEP clock must be denied even if the worker request contains a forged/backdated time field.

### P4-03 Trusted gateway clock ignores worker time claims
A permit expired according to the gateway-process clock must be denied even if the request body contains a forged/backdated time field.

### P4-04 Exact freshness threshold
With a trusted test clock, workspace mutation exactly at the registered freshness limit may pass; advancing the trusted clock by one millisecond must fail closed regardless of request payload.

### P4-05 Separate process required
The MCP authoritative ledger mutation must occur in a separately launched Python process. The test client/worker must interact through HTTP rather than direct `McpGateway.execute(...)` invocation.

### P4-06 No permit over transport
HTTP request without an LEP permit must be denied and create zero authoritative effects.

### P4-07 Fabricated/tampered permit over transport
A fabricated signature or permit whose signed content was mutated must be denied by the gateway process.

### P4-08 Exact effect binding over transport
Changing action/resource/base SHA/idempotency binding after permit issuance must be denied by the gateway process.

### P4-09 Response loss after authoritative commit
Inject response loss after the gateway durably commits a valid effect but before the HTTP response reaches the client. The first client call must be transport-incomplete/unknown, not reported as clean failure or success.

### P4-10 Retry after response loss
Retrying the same exact effect and idempotency key after P4-09 must recover the original committed result and must not create a second authoritative effect.

### P4-11 Gateway process restart
After one authoritative effect, kill the gateway process, restart a new process against the same durable ledger, and retry the same idempotency key. It must return idempotent replay with effect count still one.

### P4-12 Expired permit after process restart
A permit that has expired according to the restarted gateway process clock must remain denied after restart; restart may not reset permit validity.

### P4-13 Idempotency key rebound to different effect
Reusing an existing idempotency key with a different effect/permit binding must not execute or replace the original authoritative effect.

### P4-14 Process unavailable before request
If no gateway process is reachable, the client must return transport-ineligible/unknown and zero new authoritative effect. This is not evidence that the underlying action failed.

### P4-15 Intent-before-network evidence
The client durable spool must append intent before the HTTP request attempt and record transport outcome separately from authoritative gateway result.

### P4-16 Reconciliation after client restart
After response loss, a newly constructed client using the same durable spool and idempotency key must reconcile by retrying rather than minting a new logical intent/effect.

### P4-17 Transport provenance
Evidence must identify loopback HTTP transport, gateway process instance identity, and whether the result was fresh execution or idempotent replay.

### P4-18 Clean control
A current, correctly scoped, semantically verified request with valid worker binding and LEP permit must cross the separate-process HTTP boundary exactly once and persist complete evidence.

## Primary endpoints

Targets for the corrected path:

- expired/stale authority accepted because of worker time claim: `0`
- expired permit accepted because of worker time claim: `0`
- direct/fabricated permit bypass: `0`
- duplicate authoritative effects after response loss/retry/restart: `0`
- idempotency replacement of an existing different effect: `0`
- transport failure misreported as authoritative action failure/success: `0`
- clean-control false denial: `0`

P4-01 is expected to reproduce the historical legacy defect and is not counted as a failure of the corrected Pilot 4 path.

## Evidence requirements

The test log must show every P4 case explicitly. For P4-09/P4-10/P4-11, authoritative effect count must be read from the durable gateway ledger, not inferred from client response.

## Pass interpretation

A pass establishes only the tested single-host, two-process, loopback-HTTP behavior with HMAC test keys and SQLite persistence.

It does not establish:

- TLS/mTLS or remote-host identity;
- hostile-host/process isolation;
- kernel/container sandboxing;
- packet-level multi-host partition semantics;
- production MCP server correctness;
- distributed databases;
- real Codex/Claude prompt-injection behavior.

## Failure handling

Any corrected-path acceptance of worker-controlled time, expired authority, bypassed permit, duplicate effect, or false authoritative interpretation of transport uncertainty is a mechanism defect. Expected outcomes must not be weakened post hoc to obtain green CI.
