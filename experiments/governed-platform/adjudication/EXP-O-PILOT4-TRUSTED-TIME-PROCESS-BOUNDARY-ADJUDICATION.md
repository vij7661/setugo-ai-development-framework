# EXP-O Pilot 4 — Trusted Time + Process/Transport Boundary Adjudication

Status: **FINAL FOR THE PRE-REGISTERED PILOT 4 BOUNDARY**

Experiment family: **EXP-O — Resilient Runtime Authority & Effect-Boundary Falsification**

## Frozen lineage

- Pilot 3 post-hoc defect record: `experiments/governed-platform/adjudication/EXP-O-PILOT3-POSTHOC-TRUSTED-TIME-FINDING.md`
- Defect record commit: `c7b1c520ad31d61c4f56c39b460cb8cda521ef29`
- Pilot 4 preregistration: `experiments/governed-platform/adjudication/EXP-O-PILOT4-TRUSTED-TIME-PROCESS-BOUNDARY-PREREGISTRATION.md`
- Preregistration commit: `cf216cfa8acd1de62a932a1981908d42d4ae01ba`
- Trusted-time/process helper implementation: `experiments/governed-platform/governance/runtime_process_exp_o.py`
- Helper implementation commit: `5bae5bc804da69758a9d7f50a5a27ca9d0bf4c7f`
- Separate gateway process: `experiments/governed-platform/governance/mcp_gateway_process_exp_o.py`
- Gateway implementation commit: `4c23d421eed48ca9a5b7b301f804eb7dd3b0b246`
- Falsification tests: `experiments/governed-platform/governance/test_runtime_process_exp_o.py`
- Test commit: `e62756dbccd2f5111099c78a42995f23ff238deb`
- GitHub Actions run: `34013807960`
- Operational run conclusion: `success`

The preregistered expected outcomes were not weakened after execution.

## Architecture boundary tested

Corrected path:

`Authority Kernel -> trusted-clock LEP -> Agent/Client -> loopback HTTP -> separate MCP Gateway process -> durable gateway ledger`

Client-side evidence remained in a durable SQLite spool.

Security-sensitive current time for the corrected path was obtained from trusted component configuration rather than from an action request. The LEP held a trusted clock object. The gateway process read a process-configured trusted clock file and ignored request-body time claims.

Cryptographic mechanism remained HMAC-SHA256 with test keys. Transport was loopback HTTP. Gateway and client persistence were SQLite.

## Execution evidence

The Actions job log explicitly executed and passed all **18 Pilot 4 tests**.

The governance suite executed **390 tests** and completed successfully.

Other suite counts remained:

- scorer: 36
- runner: 51
- protected truth: 4
- observability: 7
- continuation: 12
- governance: 390

Total: **500 / 500 passing**.

Workflow success is treated as operational/regression evidence only. The mechanism conclusion below is based on the preregistered Pilot 4 outcomes and the observed test behavior.

## Preregistered case adjudication

### P4-01 — Legacy Pilot 3 defect reproduction
**PASS AS EXPECTED HISTORICAL FALSIFICATION.**

The frozen Pilot 3 caller-controlled-time design accepted an expired capability/permit path when the caller supplied a backdated `now_ms`. This reproduces the post-hoc trusted-time defect rather than treating it as hypothetical.

P4-01 is not counted as a failure of the corrected Pilot 4 path.

### P4-02 — Trusted LEP clock ignores worker time claims
**PASS.**

A capability expired according to the LEP trusted clock was denied even when untrusted request metadata claimed an earlier time.

### P4-03 — Trusted gateway clock ignores worker time claims
**PASS.**

A permit expired according to the gateway-process trusted clock was denied even when untrusted request metadata claimed a backdated time.

### P4-04 — Exact freshness threshold
**PASS.**

Workspace mutation at the frozen 15,000 ms freshness boundary passed under the trusted LEP test clock; advancing the trusted clock to 15,001 ms caused fail-closed behavior when refresh was unavailable. Request time metadata did not change the outcome.

### P4-05 — Separate process boundary
**PASS.**

The authoritative MCP gateway ran in a different Python process from the test client/worker and was invoked over loopback HTTP rather than direct in-process gateway method execution.

### P4-06 — No permit over transport
**PASS.**

An HTTP request without a LEP permit was denied and produced zero authoritative gateway effects.

### P4-07 — Fabricated/tampered permit over transport
**PASS.**

Fabricated and post-signature-mutated permits were rejected by the gateway process.

### P4-08 — Exact effect binding over transport
**PASS.**

Changing effect content or the idempotency key after permit issuance caused gateway denial. The signed permit remained bound to the exact effect request.

### P4-09 — Response loss after authoritative commit
**PASS.**

The gateway durably committed one authoritative effect and then intentionally dropped the HTTP response. The client recorded `TRANSPORT_OUTCOME_UNKNOWN` with authoritative outcome `UNKNOWN`; it did not misreport the action as authoritative success or failure.

### P4-10 — Retry after response loss
**PASS.**

Retry/reconciliation with the same logical intent and idempotency key recovered the original committed result through `IDEMPOTENT_REPLAY`. The durable gateway ledger still contained exactly one authoritative effect.

### P4-11 — Gateway process restart
**PASS.**

After killing and restarting the gateway process against the same SQLite ledger, replay of the same idempotency key returned the existing authoritative result and did not create a duplicate effect.

### P4-12 — Expired permit after process restart
**PASS.**

Restarting the gateway did not reset permit validity. A permit expired under the restarted process clock remained denied.

### P4-13 — Idempotency key rebound to a different effect
**PASS.**

An idempotency key already bound to an authoritative effect could not be reused to replace that effect with different content.

### P4-14 — Gateway process unavailable before request
**PASS.**

When the gateway process was unavailable, the client recorded transport-incomplete/authoritative-unknown state and zero new authoritative effect. Transport failure was not laundered into an authoritative action outcome.

### P4-15 — Intent before network
**PASS.**

The client durable spool persisted `EXECUTION_INTENT` before the HTTP attempt and stored transport uncertainty separately when no complete response was obtained.

### P4-16 — Reconciliation after client restart
**PASS.**

A newly constructed client over the same durable spool reconciled the previously unknown result using the same idempotency key. The spool retained one original logical `EXECUTION_INTENT` plus a distinct `EXECUTION_RETRY`; the gateway effect count remained one.

### P4-17 — Transport provenance
**PASS.**

Evidence captured loopback-HTTP transport, gateway process instance identity and whether the gateway disposition was fresh execution or replay.

### P4-18 — Clean control
**PASS.**

A current, correctly scoped, semantically verified request crossed the two-process HTTP boundary and executed exactly once. Deliberately false request time claims did not alter the gateway trusted time or the authorization result.

## Corrected-path primary endpoints

P4-02 through P4-18 observed:

- expired/stale authority accepted because of worker time claim: **0**
- expired permit accepted because of worker time claim: **0**
- direct/fabricated permit bypass accepted: **0**
- duplicate authoritative effects after response loss/retry/restart: **0**
- idempotency replacement of an existing different effect: **0**
- transport uncertainty misreported as authoritative action success/failure: **0**
- clean-control false denials: **0**

Historical defect reproduction P4-01: **1 / 1 reproduced as preregistered**.

## Independent conclusion

**`TRUSTED_TIME_AND_TWO_PROCESS_LOOPBACK_PASS / HISTORICAL_PILOT3_TIME_DEFECT_REPRODUCED / REMOTE_HOST_AND_REAL_AGENT_SECURITY_UNPROVEN`**

Pilot 4 materially strengthens the runtime architecture in two ways.

First, it falsified an over-broad interpretation of Pilot 3 by reproducing the caller-controlled-time defect. The repository therefore retains evidence that a green preregistered suite can still leave an untested authority boundary.

Second, the corrected path moved security-sensitive time inside the enforcement components and moved the MCP authoritative effect boundary into a separate process. Within the preregistered same-host loopback tests, no worker-time expiry bypass, permit bypass, duplicate authoritative effect, idempotency replacement, or transport-outcome false claim was observed.

## What this result does not establish

This Pilot 4 result must **not** be cited as proof of:

- remote-host or multi-region network-partition correctness;
- TLS/mTLS, workload identity, hardware-backed keys or asymmetric sender identity;
- protection if the worker can read the LEP/gateway process secrets or trusted-clock configuration on the same hostile host;
- OS/container sandbox escape resistance;
- packet-level adversarial network behavior beyond the tested loopback response-drop/process-unavailable faults;
- PostgreSQL/distributed transaction semantics;
- production MCP-server correctness;
- real Codex/Claude prompt-injection resistance;
- universal model safety or immunity to authority/deference bias.

The separate process is a stronger boundary than Pilot 3's direct in-process call, but both processes still share one host and administrative trust domain in the CI environment.

## Next falsification boundary

Before introducing real coding models, the next EXP-O stage should attack the **tool-response and provenance boundary** while preserving this corrected authority path:

1. malicious/compromised MCP responses containing instructions to widen authority or mutate additional resources;
2. mismatch between requested effect and returned tool result;
3. forged success, partial success and malformed result envelopes;
4. replayed result from another worker/task/effect;
5. response content attempting to influence later plan/authority state;
6. result evidence bound to gateway instance, idempotency key, effect digest and capability/permit lineage;
7. independent semantic/result verification before any release/completion gate.

After that boundary is stable, a later isolated pilot can introduce real model-generated action proposals and prompt-injection content while keeping capability issuance, trusted time, LEP permits and MCP admission external to the model.

## EXP-N isolation

Pilot 4 used new EXP-O-specific files. It did not modify the frozen EXP-N Pilot 8 recovery endpoint or Pilot 9 provider execution design. EXP-N conclusions remain independent.
