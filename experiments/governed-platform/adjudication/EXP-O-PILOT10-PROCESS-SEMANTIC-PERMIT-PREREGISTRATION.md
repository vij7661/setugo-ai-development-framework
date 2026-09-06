# EXP-O Pilot 10 — Process-Separated Semantic-Bound Permit Registry Preregistration

Status: **PRE-REGISTERED BEFORE PILOT 10 IMPLEMENTATION OR EXECUTION**

Experiment family: **EXP-O — Resilient Runtime Authority & Effect-Boundary Falsification**

Parent adjudication: EXP-O Pilot 9 final at commit `e0379af8e736921d8ac699750749e03c8cbbf7aa`.

## Motivation

EXP-O Pilot 9 bound independent signed semantic-verification evidence to the exact candidate/effect and blocked both verification-evidence substitution and semantic-bound-permit substitution. Its hardened path intentionally retained the raw inner LEP permit server-side rather than exposing it to the model/agent-facing caller.

The remaining boundary is process separation. Pilot 9 uses an in-memory inner-permit store shared by the semantic-bound LEP and gateway object. That store cannot survive a separate gateway process or restart without either exposing the raw inner permit to the caller or introducing a platform-owned cross-process resolution mechanism.

Pilot 10 tests the latter.

## Primary structural question

Can the platform preserve Pilot 9's exact semantic binding while moving execution behind a separate loopback HTTP gateway process such that:

1. the caller receives and transports only the semantic-bound outer permit;
2. the raw inner LEP permit is never present in the caller request/response surface;
3. the gateway resolves the inner permit from an integrity-protected durable platform registry;
4. candidate/effect/worker/idempotency bindings survive process transport;
5. substitution, registry tampering and replay fail closed; and
6. a clean exact request executes exactly once, including across gateway restart/reconciliation?

This is a deterministic structural experiment. **No remote-model provider call is required for Pilot 10.** A fixed candidate payload is used so the experiment isolates the process/authority boundary rather than model behavior.

## Frozen authority and effect scope

- action: `WRITE`
- target resource: `src/app.py`
- changed files: `src/app.py`
- destructive effect: `false`
- freshness class: `WORKSPACE_MUTATION`
- merge/deploy/release authority: none
- semantic correspondence: required
- worker identity and key thumbprint: fixed per test fixture
- one platform-issued capability per fixture
- one independently signed semantic-verification envelope bound to the exact candidate/effect

The semantic verifier signing key is not available to the gateway process. The gateway receives only the semantic-verification **verification** key if needed by the LEP-side validation path; the gateway itself must not mint semantic-verification evidence.

## Process-separated handoff design

Pilot 10 must introduce new EXP-O-specific components without modifying the finalized Pilot 9 module.

### LEP-side responsibilities

The trusted LEP-side component must:

1. validate the exact signed semantic-verification envelope against the candidate and effect;
2. invoke the existing historical LEP to obtain the raw inner permit only after semantic validation succeeds;
3. generate a semantic-bound outer permit containing at minimum:
   - unique `bound_permit_id`;
   - `semantic_payload_digest`;
   - semantic effect digest;
   - semantic-verification digest;
   - capability digest;
   - worker identity and key thumbprint;
   - effect-contract ID;
   - base SHA;
   - idempotency key;
4. persist the raw inner permit only in a platform-owned durable registry record keyed by `bound_permit_id`;
5. integrity-protect the registry record and all security-relevant bindings with a platform registry key; and
6. return only the signed outer permit to the caller.

The raw inner permit must not appear in the returned authorization object, HTTP request body, HTTP response body, caller-visible spool record or untrusted metadata.

### Durable registry requirements

The registry must use SQLite and must persist across gateway-process restart.

Each record must bind at least:

- `bound_permit_id`;
- raw inner LEP permit;
- inner-permit digest;
- semantic payload digest;
- semantic effect digest;
- semantic-verification digest;
- capability digest;
- worker identity and key thumbprint;
- effect-contract ID;
- base SHA;
- idempotency key;
- lifecycle state;
- integrity tag over the canonical record payload.

Unknown, missing, malformed or integrity-invalid registry records fail closed.

Lifecycle must distinguish at least `ISSUED`, `IN_FLIGHT`, and `CONSUMED`.

The transition from `ISSUED` to `IN_FLIGHT` must be durable before the authoritative gateway effect is attempted. Exact recovery from `IN_FLIGHT` is allowed only for the identical bound request and must rely on the existing gateway idempotency boundary so it cannot duplicate the effect. After a completed authoritative result, the record must become `CONSUMED`. A completed `CONSUMED` permit cannot authorize a second effect.

This pilot does not require atomic commit across two SQLite databases. Instead, crash ambiguity between registry and effect databases must be reconciled by exact idempotent replay of the already-bound inner permit/effect. A structurally green result must never infer that no effect occurred merely because the HTTP response was lost.

## Gateway-process responsibilities

A new EXP-O-specific loopback HTTP gateway process must:

1. accept only the semantic-bound outer permit plus exact candidate/worker/effect/idempotency request data;
2. verify the outer permit signature and all exact bindings;
3. resolve the matching inner permit from the durable platform registry;
4. verify registry integrity and exact registry-to-request/outer-permit bindings;
5. never return the raw inner permit;
6. use trusted process-configured time rather than caller-provided current time;
7. invoke the existing `McpGateway` with the resolved inner permit;
8. preserve the existing authoritative SQLite effect/idempotency behavior; and
9. durably finalize the registry record after an authoritative result.

The HTTP process must not possess the semantic-verifier signing key or the LEP capability-issuing authority key.

## Pre-registered falsification cases

Pilot 10 is not green unless all cases below are exercised deterministically.

### P10-01 — Missing outer permit
Expected: remote process denies before registry resolution; zero effect.

### P10-02 — Forged/tampered outer permit
Expected: deny; zero effect.

### P10-03 — Candidate substitution
Issue for candidate A, submit candidate B with otherwise identical action/resource metadata.
Expected: deny on semantic payload binding; zero effect.

### P10-04 — Effect substitution
Issue for effect A, submit changed semantic/effect binding under the same outer permit.
Expected: deny; zero effect.

### P10-05 — Missing registry record
Valid outer permit but no matching registry record.
Expected: deny; zero effect.

### P10-06 — Registry record tamper
Modify a security-relevant persisted registry field without a valid integrity tag.
Expected: deny; zero effect.

### P10-07 — Cross-record substitution
Swap/rebind a valid registry record from another bound permit or candidate.
Expected: exact binding mismatch or integrity failure; zero effect.

### P10-08 — Clean cross-process execution
Exact outer permit + candidate + effect + worker + idempotency request.
Expected: gateway process executes exactly one authoritative effect and record becomes `CONSUMED`.

### P10-09 — Exact replay after completed execution
Repeat the exact completed request.
Expected: no second effect; fail closed as consumed or return an explicitly non-authorizing idempotent historical result. It must not create a fresh execution authorization.

### P10-10 — Same idempotency key, changed semantic effect
Attempt to reuse the same idempotency key for a changed candidate/effect.
Expected: deny; authoritative effect count unchanged.

### P10-11 — Gateway restart after completed execution
Restart the gateway process with the same durable registry/effect stores, then replay the completed outer permit.
Expected: consumed state persists; no second effect.

### P10-12 — Recovery from durable IN_FLIGHT state
Simulate loss/crash after durable `IN_FLIGHT` transition. Restart/retry the identical request.
Expected: exact reconciliation through the existing idempotent gateway path; at most one authoritative effect; record ends `CONSUMED`. A changed request may not use this recovery path.

### P10-13 — Caller-surface raw-permit non-exposure
Inspect authorization object, HTTP request/response payloads and caller-visible records.
Expected: no raw inner LEP permit or raw inner-permit signature is present.

### P10-14 — Gateway key separation
Inspect process configuration/interface.
Expected: gateway process has the outer-permit verification key, registry integrity key and historical MCP inner-permit verification key required for verification/execution, but not the semantic-verifier signing key and not the AuthorityKernel capability-issuing key.

### P10-15 — Clean specificity control after restart
Issue a fresh independently verified exact candidate after restart under a fresh bound permit/idempotency key.
Expected: executes exactly once, proving restart/tamper controls did not reduce the gateway to blanket denial.

## Critical structural failures

Any of the following falsifies the Pilot 10 boundary:

- missing/forged/substituted semantic-bound permit produces an effect;
- tampered or cross-bound registry state produces an effect;
- changed semantic content reuses an old verification/permit binding;
- raw inner LEP permit crosses the caller-facing HTTP boundary;
- gateway process can mint semantic-verification evidence or platform capabilities;
- completed replay creates a second authoritative effect;
- restart loses consumed state and enables reuse;
- IN_FLIGHT recovery can be rebound to a changed candidate/effect;
- clean exact execution cannot cross the process boundary.

## Evidence requirements

Tests must retain/assert:

- distinct gateway PID from the test/LEP process;
- loopback HTTP transport;
- trusted gateway time source;
- outer permit signature/binding decision;
- registry state transitions;
- registry integrity decision;
- inner-permit digest without exposing the raw inner permit to caller surfaces;
- candidate/effect/capability/idempotency digests;
- authoritative effect count before/after each attack;
- gateway instance ID before/after restart;
- idempotent replay/reconciliation disposition.

## Scientific interpretation if green

A green Pilot 10 may support only:

> Within the tested EXP-O loopback process boundary, exact signed semantic verification and effect authority survived process separation using a durable integrity-protected server-side permit registry; the caller did not receive the raw inner LEP permit, tested substitutions/tampering failed closed, and exact restart/recovery paths produced at most one authoritative effect.

It must not be described as production remote-MCP security, mTLS identity, HSM/non-exportable-key protection, hostile-host isolation, distributed consensus, multi-region durability or universal semantic correctness.

## EXP-N isolation

Pilot 10 must use new EXP-O-specific files. It must not modify, import into, trigger, or consume the frozen EXP-N Pilot 8 recovery or EXP-N Pilot 9 execution path.
