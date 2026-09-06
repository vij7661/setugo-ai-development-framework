# EXP-O Pilot 1 — Runtime Boundary Deterministic Adjudication

Date: 2026-09-06
Status: **DETERMINISTIC_MECHANISM_PASS / BEHAVIORAL & PRODUCTION CLAIMS NOT ESTABLISHED**

## Frozen lineage

- Architecture operational contract: `c11fe8a940a76c732a31f113144033a34f37b9e4`
- EXP-O pre-registration: `ff01b2515f11ef143359d1f1d7fa18196e29c254`
- Deterministic mechanism implementation: `f9e1e06b8772b1d639612fd9ab639d6ee295fe3f`
- Deterministic falsification tests: `d9cd0e45929015d90b0ca31ee35b3129d305db04`
- GitHub Actions run: `34012869602`
- Run conclusion: `SUCCESS` operationally

The implementation commit has the pre-registration commit as its direct parent. The hypotheses, candidate thresholds, protected cases and decision discipline therefore existed before the mechanism implementation used for this run.

## Execution evidence

The governed harness executed:

- scorer regressions: 36 / 36
- runner regressions: 51 / 51
- protected-truth regressions: 4 / 4
- observability regressions: 7 / 7
- continuation regressions: 12 / 12
- governance regressions: 345 / 345

Total: **455 / 455** deterministic tests passed.

The new EXP-O runtime block contains **33 / 33** passing cases:

| Pilot | Focus | Cases | Result |
|---|---|---:|---|
| O1 | Authority freshness, partition and fencing | 11 | PASS |
| O2 | Content/effect-level intent binding | 6 | PASS |
| O3 | Preventive change claims and integration revalidation | 5 | PASS |
| O4 | Worker restart / sender-constrained rebinding | 5 | PASS |
| O5 | Partitioned evidence checkpoint / independent anchor | 6 | PASS |

## Independent endpoint adjudication

### O1 — Authority freshness, partition and fencing

Protected stale/partition cases did not create an unauthorized external or release effect.

Observed deterministic boundary behavior:
- `READ_ONLY` at exactly 60,000 ms cached age remained locally usable under the test contract; at 60,001 ms during partition it failed closed.
- `WORKSPACE_MUTATION` at exactly 15,000 ms remained usable only for the isolated non-authoritative workspace; at 15,001 ms it failed closed.
- stale/mismatched authority epoch was denied;
- stale resource fence was denied;
- `EXTERNAL_MUTATION` required current online authority for the final effect;
- `RELEASE_OR_PRODUCTION` required current online authority plus a resource fence.

Primary deterministic endpoint: **0 protected stale/partition cases produced unauthorized external/release authorization.**

### O2 — Content/effect-level intent binding

The mechanism rejected injected effects that:
- touched an explicitly forbidden production resource;
- added a changed file outside the frozen effect contract;
- exceeded the changed-file bound.

For the harder same-path case, the mechanism did **not** pretend that category/path checks prove semantic correspondence. When untrusted content influenced a change inside an otherwise permitted path and semantic correspondence was required, the result was `INDEPENDENT_SEMANTIC_VERIFICATION_REQUIRED` rather than automatic authorization. Only a separately supplied semantic-verification result permitted the tested effect to continue.

Primary deterministic endpoint: **0 tested injected effects reached authorization solely because the broad action category was permitted.**

This does not establish real-agent prompt-injection resistance. A future behavioral O2B must be separately pre-registered.

### O3 — Preventive change claims

The claim registry behaved as a live pre-execution coordination control, independent of evidence-ledger reconstruction:
- non-overlapping exclusive claims were granted;
- a second overlapping exclusive writer was placed in `WAITING_CONFLICT` before execution;
- overlapping `PARALLEL_PROPOSAL` work could proceed only as non-authoritative proposals and required combined verification;
- a stale base required revalidation;
- even a current exclusive claim did not imply release authority.

Primary deterministic endpoint: **0 tested overlapping exclusive writers received simultaneous authoritative mutation disposition.**

### O4 — Worker restart / capability rebinding

The original sender-bound capability validated for its original worker identity. The same capability was denied when presented by a replacement worker identity.

Replacement continuation required:
- durable evidence spool reconciliation;
- a new capability ID;
- a new nonce;
- a new worker/key binding;
- a non-decreasing authority epoch (the tested reissue increments it);
- the old capability to be marked revoked.

Primary deterministic endpoint: **0 tested transferred/replayed old-worker capabilities authorized the replacement worker.**

### O5 — Partitioned evidence checkpoint and independent anchoring

The tested evidence mechanism:
- verified an intact fully checkpointed partition against a different trust-domain anchor;
- detected mutation inside an anchored range;
- detected an anchor root mismatch;
- rejected an anchor under the same administrative trust domain as `INDEPENDENT`;
- represented an uncheckpointed tail explicitly as `ANCHORED_WITH_UNCHECKPOINTED_TAIL` with release integrity not current;
- enforced the pre-registered candidate checkpoint thresholds by the earlier time/record boundary.

Primary deterministic endpoint: **0 tested tampered covered records were accepted as anchored-valid.**

## What this result establishes

Within this deterministic mechanism model, the pre-registered boundary rules behave consistently with the revised architecture for the tested cases:

**external authority + bounded local freshness + monotonic fencing + content/effect intent binding + preventive claims + sender-bound worker identity + anchored evidence.**

The result also confirms that the new EXP-O modules did not disturb the frozen EXP-N Pilot 8/9 guard regressions in this harness run.

## What this result does NOT establish

This is not evidence that:
- the candidate 60 s / 15 s freshness values are appropriate production SLOs;
- a real distributed deployment meets those revocation bounds under packet loss, clock skew, failover or regional partition;
- Codex, Claude Code or another real agent resists prompt injection;
- real cryptographic proof-of-possession, mTLS, key rotation or issuer compromise handling is correct;
- a real claim registry is race-free under database/process concurrency;
- a real WORM/transparency anchor is operationally independent;
- Merkle checkpointing meets production throughput/recovery objectives;
- the platform as a whole is scientifically or production-approved.

Those require fault-injection, integration, performance and behavioral pilots against real deployment components.

## Next EXP-O work

The next promoted tests should preserve this deterministic boundary and add real-system evidence in this order:

1. **O1B distributed fault injection** — actual LEP/kernel replicas, network partitions, clock skew, cache-expiry boundaries and revocation-latency measurement.
2. **O3B concurrent persistence test** — real transactional claim registry with simultaneous writers/processes and crash/retry behavior.
3. **O4B worker lifecycle integration** — real ephemeral worker crash/reschedule + workload identity + newly issued sender-bound capability.
4. **O5B evidence durability/anchor integration** — crash between spool/blob/ledger/checkpoint stages plus a separately administered anchor.
5. **O2B behavioral agent prompt-injection test** — only after the effect boundary is wired to a real agent/MCP path; separately pre-register agents, contexts, injections, sampling and protected outcomes.

Until those are completed, the appropriate claim is:

> **The pre-registered EXP-O deterministic runtime-boundary cases passed; production runtime resilience and real-agent behavioral robustness remain unproven.**
