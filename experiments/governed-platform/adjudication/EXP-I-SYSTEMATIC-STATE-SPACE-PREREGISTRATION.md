# EXP-I — Systematic State-Space / Fault Analysis Preregistration

## Status

PREREGISTERED — EXPLORER NOT YET EXPOSED

## Scientific lineage

This analysis begins only after EXP-I Pilot 19 received `BOUNDED_PASS` on evaluated SHA `6514f9f8530c97a3d10d4027857bfdb1b8656a8a`, with P19-01..P19-16 explicitly passing and the complete governed-platform regression suite passing 1106/1106 on the same frozen SHA.

Pilot 19 remains the terminal hand-authored same-host pilot for the current EXP-I chain. This work is **not Pilot 20**. It implements Transition Track A from `EXP-I-PROTOTYPE-STOP-CRITERIA-REVIEW.md` and attacks the methodological gap left by manually selected crash vectors: unknown operation/fault interleavings.

## Falsification question

Within the frozen bounded abstraction below, does any reachable sequence of issue, commit, anchor update, receipt persistence, response loss, crash/restart, replay, reconciliation, stale-state substitution, same-generation conflict, or concurrent reconciliation violate the Pilot 19 safety/liveness contract?

A counterexample is evidence against the mechanism/model correspondence and must be preserved before repair. Absence of a counterexample is only a bounded systematic result, never a universal proof.

## Frozen model correspondence

The explorer models the durable protocol implemented by `exp_i_issuance_anchor_crash_consistency.py`:

- an issuance ledger with unique recovery identities and monotonic committed generations;
- a separately authenticated current anchor;
- a ledger-local reconciliation receipt recording the last anchor state observed as durably installed;
- transient issue/reconcile work that disappears on crash;
- durable anchor temporary material that is not itself current authority;
- atomic anchor replacement;
- minimum-side authority only when ledger, anchor, and receipt correspond exactly;
- exact repair of the uniquely derivable `ledger = receipt + 1, anchor = receipt` divergence;
- exact receipt completion of the uniquely derivable post-anchor-replace state;
- fail-closed behavior for stale, conflicting, non-contiguous, or ambiguous state.

Cryptography is abstracted as perfect authentication for valid states. Forgery resistance is outside this analysis because prior EXP-I pilots separately tested signature/key boundaries. Fault operators may substitute previously valid stale states or authenticated conflicting same-generation material; they may not forge arbitrary valid authentication.

## Frozen initial state

Genesis is:

- ledger generation 0;
- anchor generation 0 bound exactly to the ledger genesis prefix;
- reconciliation receipt generation 0 bound exactly to that anchor;
- trusted minimum at generation 0 for this abstract issuance protocol;
- no active issue transaction;
- no active reconciler work;
- no anchor temporary material;
- no delivered issuance response.

## Frozen bounded domains

The first systematic run is frozen to:

- committed issuance generations: `0..2`;
- recovery identities: `REC-A`, `REC-B`;
- semantic targets: `TARGET-X`, `TARGET-Y`;
- reconciler workers: `W1`, `W2`;
- maximum transition depth: `14`;
- maximum crash/restart transitions in one trace: `2`;
- maximum stale-ledger substitutions in one trace: `1`;
- maximum stale-anchor substitutions in one trace: `1`;
- maximum same-generation conflicting-anchor injections in one trace: `1`;
- response-loss events are bounded by the transition-depth limit;
- state canonicalization/deduplication is mandatory.

These bounds must not be increased, decreased, or otherwise tuned after seeing a scientific counterexample without preserving the first result. A later larger bound is a separate analysis run with explicit lineage.

## Frozen transition operators

The explorer must represent at least these transitions where their preconditions hold:

1. `ISSUE_BEGIN(recovery_id, target)`
2. `ISSUE_INSERT_UNCOMMITTED`
3. `ISSUE_LEDGER_COMMIT`
4. `RECONCILE_BEGIN(worker)`
5. `ANCHOR_TEMP_WRITE(worker)`
6. `ANCHOR_ATOMIC_REPLACE(worker)`
7. `RECEIPT_PERSIST(worker)`
8. `RESPONSE_DELIVER`
9. `RESPONSE_LOSS`
10. `CRASH_RESTART`
11. `DUPLICATE_REPLAY(recovery_id, target)`
12. `REBIND_ATTEMPT(recovery_id, different_target)`
13. `STALE_LEDGER_SUBSTITUTE`
14. `STALE_ANCHOR_SUBSTITUTE`
15. `CONFLICTING_SAME_GENERATION_ANCHOR`
16. a second concurrent `RECONCILE_BEGIN` where the first reconciliation has not completed.

A crash discards volatile transactions/work but does not erase already committed ledger rows, atomically replaced anchor state, persisted receipts, or retained stale-snapshot history.

## Frozen authority predicate

`AUTHORITATIVE_USE_ALLOWED` is true only when all of the following are true:

- current ledger generation equals current anchor generation equals receipt generation;
- anchor content equals the exact committed ledger prefix state for that generation;
- receipt content/hash corresponds to that exact current anchor state;
- no semantic binding conflict exists for any accepted recovery identity.

No model, reviewer, caller, worker choice, response-delivery flag, temporary anchor, ledger row alone, or anchor alone contributes authority.

## Frozen invariants

These are copied from the prototype stop-criteria review and may not be weakened after exposure:

1. **No authority from ambiguity:** unresolved or conflicting state never authorizes trusted-minimum mutation.
2. **No ledger-only authority:** a committed ledger row without required reconciled anchor correspondence cannot authorize use.
3. **No anchor-only authority:** anchor state without exact committed ledger correspondence cannot authorize use.
4. **Monotonic trust:** accepted generation/issuance state never moves backward.
5. **No semantic rebinding:** one recovery identity never maps to two target semantics.
6. **At-most-once consequential advancement:** retries/crashes do not create two authoritative advancements for one intent.
7. **Deterministic reconciliation:** uniquely derivable divergence converges to one exact state independent of caller preference.
8. **Fail-closed conflict:** non-uniquely derivable divergence does not auto-reconcile.
9. **Liveness from safe states:** after a uniquely recoverable crash, a clean next generation can eventually advance exactly once.
10. **External authority:** model/reviewer/caller data cannot choose trusted reconciliation state.

## Additional model sanity obligations

The explorer must also fail if:

- a crash transforms uncommitted issue work into a committed issuance;
- temporary anchor material is treated as current authority;
- a response-delivery/loss event changes durable authority;
- a replay creates a second ledger row for the same recovery identity;
- an attempted semantic rebind modifies the original binding;
- reconciliation advances more than one generation at a time;
- an ambiguous state is classified as uniquely recoverable.

## State classification frozen before run

The abstract classifier must distinguish at least:

- `RECONCILED`
- `LEDGER_AHEAD_EXACT`
- `ANCHOR_REPLACED_RECEIPT_PENDING`
- `FAIL_CLOSED`

`LEDGER_AHEAD_EXACT` is permitted only for exactly one committed generation above the receipt while anchor and receipt still exactly agree on the prior ledger prefix.

`ANCHOR_REPLACED_RECEIPT_PENDING` is permitted only when the anchor exactly equals the current ledger state one generation above the receipt and the receipt still exactly corresponds to the prior ledger prefix.

All other divergence is `FAIL_CLOSED`.

## Exploration algorithm

- deterministic breadth-first search from genesis;
- canonical immutable state representation;
- deduplicate already visited states at equal or shallower depth;
- enumerate all enabled frozen transitions in deterministic lexical order;
- check invariants on every reachable state and every consequential transition;
- retain predecessor plus transition for exact shortest counterexample reconstruction;
- do not prune a state merely because it is fail-closed; safe recovery/restart transitions must still be explored when enabled;
- report total states, transitions, maximum reached depth, terminal classifications, and invariant check counts.

## Liveness check

For every reachable state classified as uniquely recoverable (`RECONCILED`, `LEDGER_AHEAD_EXACT`, or `ANCHOR_REPLACED_RECEIPT_PENDING`) with capacity for another generation, run a bounded continuation search inside the same frozen state bound. The check passes only if at least one protocol-controlled path—without stale/conflict fault injection—can reach a reconciled state at the next generation exactly once.

This is bounded existential recovery liveness, not fairness or distributed liveness proof.

## Counterexample preservation

On first failure, emit a deterministic record containing:

- invariant identifier;
- shortest transition trace from genesis;
- state before the violating transition;
- violating transition;
- resulting state;
- classifier result;
- authority predicate result;
- bound/configuration identity;
- explorer implementation commit SHA when run in CI.

The first counterexample must be committed or attached to adjudication evidence before any mechanism or explorer repair.

## Scientific acceptance

A `BOUNDED_SYSTEMATIC_PASS` requires:

- the explorer implementation matches this preregistration;
- every state reachable within the frozen bounds is checked;
- all ten frozen invariants and sanity obligations hold;
- all uniquely recoverable states satisfy the bounded liveness check;
- the full governed-platform regression suite passes on the exact evaluated SHA;
- the exact CI run/job and state/transition totals are retained.

If any invariant fails, status is `COUNTEREXAMPLE_FOUND`, regardless of aggregate pass percentage.

If the explorer cannot complete the frozen search because of an implementation/resource defect, status is `NOT_TESTED` or `HARNESS_FAILURE`, not PASS.

## Interpretation rule

No result from this bounded abstract exploration may be described as formal proof, exhaustive proof of all real executions, distributed consensus proof, power-loss proof, KMS/HSM proof, Byzantine safety, production readiness, release authority, or third-party certification.

A clean result means only: **no counterexample was reachable in this frozen abstraction and bound.**

## Parallel integrated MVP work

Transition Track C is not part of the state-explorer pass/fail result. In parallel, define the integrated governed-platform MVP slice around:

`request -> diagnosis -> permissible-action decision -> task-specific model qualification -> scoped capability issuance -> Builder execution -> independent evidence collection -> Judge/reviewer verification -> governed approval gate -> retained audit/continuation state`

The MVP definition must preserve explicit release/deploy authority outside models and must reuse proven governance mechanisms rather than granting new authority through orchestration glue.