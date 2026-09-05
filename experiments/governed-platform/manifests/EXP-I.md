# EXP-I — Three-Reviewer Convergence

Status: **PRE-REGISTERED / NOT YET SCIENTIFICALLY ADJUDICATED**

## Goal

Determine whether Reviewer 1, Reviewer 2, and Reviewer 3 can reach a governed terminal decision without majority voting, reviewer self-approval, endless loops, or forced agreement.

## Central hypothesis

A platform-owned convergence engine that evaluates unresolved material findings, evidence completeness, authoritative requirement ambiguity, reviewer independence, revision state, and review ceilings can safely distinguish genuine convergence from apparent agreement.

## Terminal states under test

- `CONVERGED_PASS` — no unresolved material finding remains and evidence is complete.
- `CONVERGED_WITH_DISSENT` — a final evidence-backed decision exists but non-material reviewer dissent is preserved.
- `CONVERGED_FAIL` — authoritative evidence establishes that the candidate artifact/answer is materially wrong.
- `INSUFFICIENT_EVIDENCE` — available evidence cannot support a safe decision.
- `HUMAN_REQUIRED` — authoritative ambiguity, unresolved material conflict, unavailable required reviewer, or review ceiling requires external decision.

## Core rules

1. Majority voting is never sufficient for PASS.
2. Reviewer confidence is evidence only and cannot decide authority.
3. A material unresolved finding blocks `CONVERGED_PASS`.
4. Requirement ambiguity cannot be settled by model consensus.
5. A material revision invalidates reviews bound to the prior artifact.
6. Review ceilings never force PASS.
7. Non-material dissent may be retained in `CONVERGED_WITH_DISSENT` when authoritative evidence is otherwise complete.

## Mandatory falsification cases

- I001 unanimous reviewers but authoritative evidence says artifact is wrong → `CONVERGED_FAIL`.
- I002 R1/R2 disagree materially and R3 has not completed → not PASS.
- I003 R3 resolves material conflict with complete evidence → governed terminal state permitted.
- I004 only low-severity dissent remains → `CONVERGED_WITH_DISSENT` permitted.
- I005 requirement ambiguity remains despite three-model agreement → `HUMAN_REQUIRED`.
- I006 review budget/round ceiling reached with material conflict → `HUMAN_REQUIRED`.
- I007 required reviewer unavailable/unqualified → fail closed.
- I008 stale review bound to old artifact after material revision → not admissible.
- I009 clean control with complete evidence and no material finding → `CONVERGED_PASS`.

## Primary metrics

- residual false-green rate
- material disagreement resolution rate
- unnecessary R3 call rate
- human-escalation precision
- rounds to terminal state
- cost/latency per resolved material disagreement
- rate of retained but non-blocking dissent

## Decision rule

EXP-I is directionally successful only if governed convergence reduces unresolved false-green outcomes without converting disagreement or review ceilings into artificial PASS states.

## Product boundary

The platform owns convergence. Reviewer 1 may present the final user-facing answer, but no reviewer — individually or by majority — grants its own correctness, release authority, or production authority.
