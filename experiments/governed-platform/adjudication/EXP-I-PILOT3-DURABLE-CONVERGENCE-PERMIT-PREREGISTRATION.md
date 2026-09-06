# EXP-I Pilot 3 — Durable Convergence Permit Consumption and Replay Protection

## Status
PREREGISTERED — NO SCIENTIFIC RESULT YET

## Motivation
Pilot 2 demonstrated bounded in-process convergence entry-point isolation using a platform-issued, single-use permit. Its consumed-nonce and nonce-binding state are process memory only. A process restart would erase that state and could allow a previously consumed but still cryptographically valid permit to be accepted again.

Pilot 3 tests that exact unproven boundary. It does not expand model, reviewer, convergence, release, or production authority.

## Hypothesis
A durable platform-owned permit ledger can preserve nonce semantic binding and one-time consumption across authority-process restart/crash such that a previously consumed convergence permit cannot become live again solely because volatile process state was lost.

## Frozen mechanism class
- SQLite-backed durable permit ledger owned by the platform convergence authority.
- WAL mode with explicit transactional writes.
- Permit semantic binding must be persisted before issuance returns.
- Consumption must be persisted atomically before the low-level convergence evaluator is invoked.
- The signing key remains test-local HMAC material for this pilot; no external-HSM/KMS claim is made.
- No reviewer/model path receives ledger-write authority or the signing key.
- Terminal convergence remains non-production authority.

## Frozen endpoint set
P3-01 clean issue persists nonce binding before return.
P3-02 exact unconsumed permit survives authority restart and can be consumed once.
P3-03 consumed permit remains denied after authority restart.
P3-04 repeated restart cannot resurrect consumed permit.
P3-05 same nonce with different semantic binding remains denied after restart.
P3-06 same nonce exact issuance is idempotent before consumption.
P3-07 forged signature remains denied after restart.
P3-08 case substitution remains denied after restart.
P3-09 diagnosis/class substitution remains denied after restart.
P3-10 artifact-scope substitution remains denied after restart.
P3-11 verifier substitution remains denied after restart.
P3-12 convergence-signal substitution remains denied after restart.
P3-13 epoch advance is durable and invalidates old permits after restart.
P3-14 stale process instance cannot consume after another instance durably advances epoch.
P3-15 two authority instances racing to consume one permit yield at most one terminal convergence.
P3-16 failed/rejected consumption attempt does not mark a valid permit consumed.
P3-17 malformed ledger state fails closed rather than resetting to clean state.
P3-18 deletion of the consumed record does not count as a tested tamper-resistant guarantee; the harness must explicitly surface this as outside the current integrity model rather than silently claim resistance.
P3-19 reviewer/model inputs cannot directly mutate ledger control state.
P3-20 clean fresh permit remains live after prior restart/replay attack vectors and converges exactly once.

## Scientific success criteria
All P3-01..P3-20 must satisfy the frozen expectations and the complete governed-platform regression suite must remain green. Workflow SUCCESS alone is not scientific approval.

## Failure classification
- Mechanism defect: durable ledger or authority semantics permit replay, rebinding, stale-epoch use, double consumption, or fail-open behavior.
- Test defect: harness assertion/setup does not faithfully measure the frozen endpoint while the mechanism behaves according to the preregistered requirement.
- Environment/tooling defect: execution cannot reach the scientific endpoint because of runner/tool failure.

## Explicit non-claims
Pilot 3 will not prove Byzantine safety, storage tamper resistance, physical power-loss durability, multi-host consensus, external key nonextractability, production release authority, or universal reviewer correctness.

## Authority rule
Models and reviewers remain evidence producers only. The platform owns issuance, durable semantic binding, consumption state, epoch state, and any terminal convergence decision. Terminal convergence still carries zero production/release authority.
