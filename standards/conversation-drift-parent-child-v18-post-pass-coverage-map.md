# V18 Post-Pass Coverage Map

Status: **PROPOSED V18 — REVIEW REQUIRED — NON-AUTHORITATIVE**

Authority effect: **NONE_EVIDENCE_ONLY**

Candidate order: `V5 -> V6 -> V7 -> V8 -> V9 -> V10 -> V11 -> V12 -> V13 -> V14 -> V15 -> V16 -> V17 -> V18`

Exact V17 base: `da39da9ea02af6915d4283f6a09c6d18212fa4ed`

V18 adds only the reviewer-identified post-pass hardening families below; all active V5–V17 rules remain in force.

| Mechanism ID | Purpose | New endpoint(s) | Falsification cases |
|---|---|---|---|
| `MECH-THRESHOLD-ATOMIC-CRASH-RECOVERY` | Prove all-or-nothing durable threshold commit and ambiguous-ack reconciliation | `REVIEW_THRESHOLD_COMMIT_OUTCOME_UNKNOWN` | WDPC-273, 278 |
| `MECH-ROOT-LEDGER-ANTI-SELF-GRANT` | Prevent sub-threshold/single-guardian mutation of threshold and packet ledgers | `ROOT_GOVERNED_LEDGER_MUTATION_REJECTED` | WDPC-274, 279 |
| `MECH-REUSE-POLICY-PROSPECTIVE-ONLY` | Prevent retroactive legalization of previously consumed review evidence | `REVIEW_THRESHOLD_REUSE_RETROACTIVE_REJECTED` | WDPC-275, 280 |
| `MECH-CANONICAL-CORPUS-DEPENDENCY-REVALIDATION` | Invalidate/revalidate dependent decisions after corpus/algorithm change | `CANONICAL_CORPUS_DEPENDENT_REVALIDATION_REQUIRED` | WDPC-276, 281 |
| `MECH-THRESHOLD-LEDGER-ANTI-ROLLBACK-FORK` | Detect privileged rollback, prefix replacement, fork or hidden lineage | `REVIEW_THRESHOLD_LEDGER_ROLLBACK_OR_FORK` | WDPC-277, 282 |

## Coverage accounting

- New negative cases: WDPC-273…277.
- New positive/non-overblocking cases: WDPC-278…282.
- Existing duplicate-supporting cases retain their prior accounting and do not inflate unique-mechanism confidence.
- V17 R3 `PASS_FOR_NEXT_DESIGN_STAGE` remains bound only to V17; it is not automatically inherited as a V18 pass.

## Authority boundary

This map is design/falsification evidence only. It does not qualify implementation, satisfy the manual-review gate, or authorize execution freeze, merge, release, deployment, adjudication, or terminal state.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
