# ECC-Derived Program Result Ledger

Status: **OPEN — NO CHILD TERMINAL YET**

Authority effect: **NONE_EVIDENCE_ONLY**

Baseline: `290ac043959f30db12c9ae16826eda1dd5bcbdfb`

| Experiment | Current state | Terminal disposition | Evidence digest | Notes |
|---|---|---|---|---|
| EXP-ECC-1 | PREREGISTERED | — | — | Enforcement execution attestation |
| EXP-ECC-2 | PREREGISTERED | — | — | Declared-vs-executable equivalence |
| EXP-ECC-3 | PREREGISTERED | — | — | Qualified harness capability envelope |
| EXP-ECC-4 | PREREGISTERED | — | — | Capability activation consent |
| EXP-ECC-5 | PREREGISTERED | — | — | Tool/MCP config attestation and drift |
| EXP-ECC-6 | PREREGISTERED | — | — | Review egress/provider relationship |
| EXP-ECC-7 | PREREGISTERED | — | — | Learned-artifact promotion boundary |

## Allowed child states

`PREREGISTERED -> RED_EXPECTED -> MECHANISM_REPAIR_IN_PROGRESS -> REEXECUTION -> TERMINAL`

A child may also terminate `INSUFFICIENT_EVIDENCE` without repair if the required scientific boundary cannot be tested honestly.

## Terminal dispositions

Only:
- `BOUNDED_PASS`
- `BOUNDED_FAIL`
- `INSUFFICIENT_EVIDENCE`

Prior RED/failure states remain preserved after repair.

## Program completion gate

`ALL_CHILD_EXPERIMENTS_TERMINAL` is true only when all seven rows have a terminal disposition and exact evidence digest/baseline binding.

Before that state:
- no combined external-review packet;
- no aggregate PASS;
- no automatic requirement promotion;
- no V18 mutation;
- no merge/release/deploy/completion authority.

After that state, construct one self-contained external review packet for the complete experiment family. External review evaluates evidence and proposed impact; it does not rewrite child results.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
