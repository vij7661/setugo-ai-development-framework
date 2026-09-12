# Workflow Drift and Parent-Child Impact Control — V23 Endpoint-Precedence Addendum

Status: **PROPOSED V23 — REVIEW REQUIRED — NON-AUTHORITATIVE**

Authority effect: **NONE_EVIDENCE_ONLY**

This addendum is additive over `standards/conversation-drift-parent-child-impact-control-v23-completeness-hardening.md` and explicitly adopts:

- `standards/platform-authority-endpoint-precedence-v23.md`
- Table ID: `AUTHORITY-ENDPOINT-PRECEDENCE-V23`

The exact blob and candidate commit binding must be taken from the final frozen V23 composite candidate.

## V23-EP01 — Mandatory table consultation

Every WDPC authority decision, evidence qualification, kernel-decision application, reconciliation, and proof-view qualification with overlapping failure predicates must consult the exact active kernel-bound endpoint-precedence table.

Local implementation order, exception handling order, caller preference, UI preference, model reasoning order, or retry path cannot select an alternative endpoint.

## V23-EP02 — WDPC-357 prospective narrowing

For V23 prospective evaluation corresponding to historical WDPC-357:

1. a proven source-class-specific invalidity uses the exact source-specific endpoint mapped by the active table;
2. absent such a mapping, proven revoked/expired/compromised/superseded/wrong-generation/wrong-tuple/wrong-class/wrong-policy-bound source evidence returns `AUTHORITY_EVIDENCE_SOURCE_INVALID`;
3. missing/unavailable evidence needed to establish current qualification returns `INSUFFICIENT_EVIDENCE`.

Historical V22 case text/results are not rewritten.

## V23-EP03 — Kernel decision application precedence

For a qualifying exact decision-record identity:

- proven ledger rollback/fork/integrity failure → `AUTHORITY_KERNEL_DECISION_LEDGER_INTEGRITY_INVALID`;
- record matches the intended transition but bound preconditions/currentness changed after issuance → `ROOT_KERNEL_DECISION_STALE`;
- record is absent, unanchored, replayed to a different transition, malformed, wrong-generation, or otherwise non-qualifying → `ROOT_KERNEL_ENFORCEMENT_REQUIRED`, unless an earlier table phase already produced a stricter endpoint.

## V23-EP04 — Proof-view precedence

A proof-view failure cannot hide or replace an earlier underlying authority failure. The underlying authority endpoint remains authoritative; proof qualification additionally fails with `PROOF_VIEW_COMPLETENESS_INVALID` when the manifest-required field is suppressed or falsely classified.

## V23-EP05 — Freeze rule

This addendum is design-only and grants no implementation/falsification/execution freeze, merge, release, deployment, qualification, production authority, adjudication, or terminal authority.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
