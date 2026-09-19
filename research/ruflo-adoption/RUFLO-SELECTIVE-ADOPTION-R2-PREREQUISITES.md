# Ruflo Selective Adoption R2 — Prerequisite Matrix

Presence is not sufficient. A prerequisite marked `QUALIFIED` must have completed its own governed implementation, falsification and independent review.

| Target | Mandatory prerequisites |
|---|---|
| Gate 0 R2 design closure | independent R2 manual design review; zero unresolved Critical/High |
| Gate 1 EXP-M deterministic implementation | frozen EXP-M R5 only; independent of RA adoption |
| FP-01 CanonicalRecordIdentity | Gate 0 bounded pass |
| RA-01 diagnostic projection | Gate 0 bounded pass; named authoritative source map |
| RA-05 generated inventory | Gate 0 bounded pass; diagnostic-only status |
| RA-06 source/execution receipts | Gate 0 bounded pass; FP-01 qualified |
| RA-07 advisory negative archive | FP-01 qualified; rollback/tamper primitive qualified; no deny-list authority |
| RA-11 diagnostics | Gate 0 bounded pass; provenance-safe representation |
| FP-02 AuthorityGenerationCAS | Gate 0 bounded pass; protected-state store defined |
| RA-02 evidence assurance | FP-01 qualified; governing composition rules reviewed |
| RA-03 evaluation/promotion transaction | FP-01 + FP-02 qualified; evaluator write isolation; external-auth policy derived from authority snapshot |
| RA-04 capability envelope | FP-02 qualified; canonical scope comparator; atomic consumable reservation ledger |
| RA-08 authority-bearing memory supersession | FP-01 + FP-02 + RA-02 + RA-07 mechanism qualified; namespace authority defined; active-projection CAS defined |
| RA-09 tool permission contract | RA-04 qualified; platform tool-risk registry qualified |
| RA-11 enforcement | RA-02 + RA-04 + RA-09 qualified; signature/publisher/dependency/load/sandbox mechanisms qualified |
| RA-10 multi-writer worktrees/leases/fencing | RA-03 + RA-04 + RA-06 + RA-09 + RA-11 enforcement + FP-02 qualified |
| RA-12 swarm-capable routing | RA-01 capability projection correctness + RA-03 + RA-04 + RA-09 + RA-10 + RA-11 enforcement qualified |
| RA-13 bounded research/dream cycle | RA-01 + RA-03 + RA-04 + RA-06 + RA-07 + RA-08 provenance/supersession + RA-09 + RA-10 + RA-11 enforcement + RA-12 qualified; authoritative policy/gold/evaluation write isolation |

## Rules

1. "Implemented" does not satisfy a `QUALIFIED` prerequisite.
2. Diagnostic RA-11 does not satisfy RA-11 enforcement.
3. A route that is single-executor-only may be tested before RA-10, but it must be structurally unable to spawn concurrent writers.
4. Any target that uses memory as authority also requires RA-08; advisory retrieval does not.
5. Any target that changes promotion/release authority requires RA-03.
6. Any target that delegates consumable resources requires RA-04 hierarchical conservation semantics and atomic parent-ledger reservation.
7. Any target ingesting external/untrusted content into an executable/reviewer context requires RA-11 enforcement before authority-bearing use.
8. Unknown prerequisite state fails closed.
