# EXP-O Pilot 3 — Governed Runtime Slice Adjudication

Status: **FINAL FOR THE PRE-REGISTERED SINGLE-HOST PILOT**

Experiment family: **EXP-O — Resilient Runtime Authority & Effect-Boundary Falsification**

## Frozen lineage

- Preregistration: `experiments/governed-platform/adjudication/EXP-O-PILOT3-RUNTIME-SLICE-PREREGISTRATION.md`
- Preregistration commit: `a7e02f60d34b23ed880990acfdca8399a2cc906c`
- Runtime implementation: `experiments/governed-platform/governance/runtime_slice_exp_o.py`
- Implementation commit: `31e232d97a567fa6ca1d4a61972efff6dc2055d9`
- Falsification tests: `experiments/governed-platform/governance/test_runtime_slice_exp_o.py`
- Test commit: `4b3e15d3f7fe561b3928db44ead7c0eba7c55015`
- GitHub Actions run: `34013578737`
- Run conclusion: `success` operationally

The pre-registered outcomes were not weakened after execution.

## Executed architecture slice

The tested single-host path was:

`Authority Kernel -> Local Enforcement Point -> Agent Worker -> MCP Gateway -> Durable Evidence Spool`

The worker did not possess the Authority Kernel signing key or the Local Enforcement Point permit-signing key. The MCP gateway did not accept a platform capability directly. It required a separately signed, short-lived LEP execution permit bound to the worker and exact requested effect.

Cryptographic mechanism in this pilot: HMAC-SHA256 with distinct kernel and LEP/gateway keys. Persistence mechanism: file-backed SQLite.

## Execution evidence

The governance suite executed **372 tests** and completed successfully. The Pilot 3 block contributed **20 tests**, all of which explicitly appeared in the Actions job log and passed.

Other suite counts remained:

- scorer: 36
- runner: 51
- protected truth: 4
- observability: 7
- continuation: 12
- governance: 372

Total: **482 / 482 passing**.

A green workflow is treated here as execution/regression evidence only. The scientific/mechanism conclusion below is based specifically on the pre-registered Pilot 3 cases and their observed behavior.

## Pre-registered endpoint adjudication

### P3-01 — No capability
**PASS.** Missing platform capability was denied before any authoritative gateway effect.

### P3-02 — Forged/tampered capability
**PASS.** Mutating signed capability content caused capability-signature failure; zero authoritative gateway effect.

### P3-03 — Worker identity replay
**PASS.** A capability issued to worker A/key A was denied when worker B/key B attempted use.

### P3-04 — Epoch revocation/reissue
**PASS.** Advancing the Authority Kernel epoch invalidated the older capability at use time.

### P3-05 — Freshness threshold
**PASS.** Workspace mutation at the frozen 15,000 ms threshold was accepted in the tested local boundary; 15,001 ms while unable to refresh failed closed. External mutation without current online authority failed closed.

### P3-06 — Scope widening
**PASS.** Resource widening, base-SHA drift and destructive-effect escalation outside the frozen effect contract were denied before MCP effect.

### P3-07 — Untrusted-content semantic boundary
**PASS.** Same-path/action scope containing model/untrusted provenance did not become executable solely from syntactic scope matching; independent semantic verification remained required.

### P3-08 — Direct MCP bypass
**PASS.** No-permit and fabricated-permit calls were denied. A platform capability alone is not the MCP admission credential in this slice.

### P3-09 — Gateway partition
**PASS WITH SCOPE LIMITATION.** The simulated unreachable gateway produced zero authoritative effect. This was a component reachability fault injection, not a real cross-host network partition.

### P3-10 — Intent-before-effect evidence
**PASS.** `EXECUTION_INTENT` was durably appended before the gateway attempt, including the denied/unreachable path.

### P3-11 — Crash/retry idempotency
**PASS.** An injected worker crash after gateway execution but before local result persistence left exactly one authoritative gateway effect. Reconciliation/retry with the same idempotency key returned the original effect via `IDEMPOTENT_REPLAY` and did not execute a second authoritative effect.

### P3-12 — Replacement-worker capability
**PASS.** Replacement issuance failed without spool reconciliation. After reconciliation a new worker-bound capability was issued; the old capability was revoked/unusable and the replacement capability could execute within the same frozen scope.

### P3-13 — Durable spool restart
**PASS.** Closing/reopening the SQLite evidence spool preserved record sequence and hash lineage and verified cleanly.

### P3-14 — Evidence tampering
**PASS.** Persisted payload modification caused record-hash verification failure. Deleting the first record caused a sequence-gap/reorder failure. Neither case was interpreted as clean evidence.

### P3-15 — Permit effect binding
**PASS.** Changing the exact effect after LEP permit issuance caused permit-effect-binding denial. Changing the idempotency key caused permit-idempotency-binding denial. Zero authoritative effect occurred.

### P3-16 — Clean control
**PASS.** A current, correctly scoped, semantically verified, identity-bound request crossed the full path and produced exactly one authoritative gateway effect with complete intent/result evidence and a verified spool chain.

## Primary endpoint totals

Observed in the pre-registered Pilot 3 cases:

- unauthorized authoritative MCP effects: **0**
- duplicate authoritative MCP effects under crash/retry: **0**
- stale/revoked/identity-mismatched authority accepted: **0**
- direct gateway bypasses accepted: **0**
- evidence-tamper false-clean outcomes: **0**
- clean-control false denials: **0**

## Independent conclusion

**`SINGLE_HOST_RUNTIME_SLICE_PASS / HMAC+SQLITE PILOT ONLY / DISTRIBUTED_AND_REAL_AGENT_SECURITY_UNPROVEN`**

No authority bypass, duplicate authoritative effect, stale/identity-replay acceptance, direct gateway bypass, or evidence-tamper false-clean was observed in the pre-registered single-host runtime-slice cases.

The result materially strengthens the architecture compared with a policy-only or helper-only design because the tested effect path now requires two structurally separate authorization stages:

1. platform capability validation at the Local Enforcement Point; and
2. a short-lived, exact-effect permit at the MCP Gateway.

It also demonstrates the intended intent-before-effect and crash/retry idempotency behavior in a persistent single-host SQLite implementation.

## What this result does not establish

This pilot must **not** be cited as proof of:

- real network partition behavior across hosts, availability zones or regions;
- PostgreSQL/distributed transactional behavior;
- TLS/mTLS, hardware-backed, asymmetric or workload-attested identity;
- process, container or OS sandbox isolation;
- secret-extraction resistance when a worker and enforcement component share a hostile host;
- production MCP implementation correctness;
- real Codex/Claude prompt-injection resistance;
- robustness to malicious tool-server responses beyond the frozen effect/provenance checks;
- universal model safety or immunity to authority/deference bias.

`McpGateway.reachable = False` is fault injection, not a real packet-level/network-partition experiment. HMAC keys are pilot trust anchors, not a production key-management architecture.

## Next falsification boundary

The next EXP-O stage should cross an actual process/transport boundary before introducing real coding models:

- separate Local Enforcement Point and MCP Gateway processes;
- authenticated local IPC or loopback HTTP transport;
- process kill/restart during execution;
- connection drop after request receipt but before response delivery;
- gateway restart with durable idempotency ledger;
- stale/expired permit replay across process restart;
- corrupted/truncated evidence-spool writes;
- explicit transport provenance in evidence.

Only after that boundary is stable should a later pilot introduce real Codex/Claude-generated action proposals and prompt-injection content while keeping the structural authority path unchanged.

## EXP-N isolation

This Pilot 3 work used new EXP-O-specific files and did not alter the frozen EXP-N Pilot 8 recovery endpoint or Pilot 9 provider execution design. EXP-N Pilot 8/9 scientific conclusions remain independent of this result.
