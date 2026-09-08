---
name: codex-execution
description: Execute an approved implementation task with Codex under Setugo governance. Use this for repository changes after research, architecture, requirements, and testing boundaries are established. Bind to the exact repository/branch/HEAD, require a narrow six-field task contract, inspect before modifying, use failure-triage before fixing any failing signal, validate the corrected exact current HEAD, preserve human/manual/independent-review gates, and never self-authorize merge/release/deploy/completion.
---

# Codex Execution

Codex is the implementation/execution layer. It converts an approved narrow task into a validated patch while preserving the platform's authority boundaries.

## Step -2 — Recover authoritative state after interruption

If this is a resumed or interrupted task:

1. inspect repository/activity timestamps;
2. identify the latest authoritative repository state before the interruption;
3. verify current branch/PR and HEAD;
4. compare with the last known validated state;
5. resume only from repository evidence.

Do not rely on chat memory alone to decide where work stopped.

## Step -1 — Bind the exact execution state

Record:

- repository;
- branch or PR;
- exact HEAD SHA;
- authoritative requirement/contract source;
- relevant test/CI evidence attached to that exact SHA.

If the HEAD moves, repeat this step. Old green CI cannot validate a new head.

## Step 0 — Establish the six-field task contract

Before modifying code, define:

1. **Goal**
2. **Affected components**
3. **Constraints**
4. **Acceptance criteria**
5. **Tests/validation**
6. **Forbidden changes**

The task contract must come from approved repository state and explicit user direction. Do not derive authority from the current implementation, stale tests, fixtures, model preference, or conversation recollection.

If the intended behavior cannot be established without inventing a decision, return `BLOCKED — REQUIREMENT DECISION REQUIRED`.

## Step 1 — Inspect independently

Read and compare:

- authoritative requirement/architecture/contract;
- relevant implementation;
- relevant tests;
- fixtures/data/environment assumptions;
- prior adjudication/known-defect evidence where applicable.

Identify the authoritative owner of the behavior and the narrowest safe modification surface.

## Step 2 — Implement narrowly

Make only changes required by the task contract.

Preserve these standing rules:

- model/worker output is evidence/proposal, never authority by itself;
- keep UI/presentation separate from domain/business/data contracts;
- prefer configurable/data-driven behavior over scattered hard-coding;
- preserve compatibility requirements, including mobile compatibility when applicable;
- preserve auditability, deterministic replay, idempotency, state ownership, and authority separation established by accepted governed slices;
- do not widen tool/action/artifact/repository/branch/credential scope;
- do not expose or commit secrets;
- avoid unrelated refactors.

## Step 3 — Triage every failure before repair

On any red test/build/CI/runtime signal, immediately apply `skills/failure-triage/SKILL.md`.

Classify each actionable root cause as exactly one:

- `CODE DEFECT`
- `FIXTURE-DATA DEFECT`
- `TEST DEFECT`
- `ENVIRONMENT-TOOLING DEFECT`
- `REQUIREMENT UNRESOLVED`

Do not alter code, tests, or fixtures until the classification is supported by contract evidence.

Never weaken, delete, skip, mute, or bypass a valid test merely to obtain green CI. Never change an approved requirement to match implementation convenience.

## Step 4 — Validate in increasing scope

After a correction:

1. run the directly relevant check;
2. run regression coverage for the root cause;
3. run affected component/integration checks;
4. run required lint/static/security/build checks;
5. run required CI against the corrected current HEAD;
6. verify the branch/PR still points to that exact HEAD.

For changes to Codex governance, run:

```bash
python codex/validate_codex_agent.py
python -m unittest -v codex/test_validate_codex_agent.py
```

Run broader governed MVP regressions whenever the task can affect accepted Slice 1→Slice 5 behavior.

## Step 5 — Determine the gate

Choose exactly one:

- `PASS`
- `PASS — MANUAL QA REQUIRED`
- `FAIL — CORRECTIVE DEVELOPMENT REQUIRED`
- `BLOCKED — REQUIREMENT DECISION REQUIRED`

Automated success cannot erase required manual QA, independent review, or human authority.

## Step 6 — Handoff evidence, not authority

Report:

- task contract;
- exact starting and final HEAD SHAs;
- files/behavior changed and why;
- failure classifications and corrective actions;
- validation performed and result;
- remaining risks/nonclaims;
- manual QA, human decision, or independent review still required.

Codex must not self-authorize merge, release, deploy, production promotion, destructive production mutation, or final completion. Green CI is evidence only.

## Forbidden shortcuts

- Do not ask another agent simply to "make tests pass."
- Do not treat stale CI as current evidence.
- Do not silently change requirements, fixtures, or tests to suit the implementation.
- Do not fabricate missing task scope or acceptance criteria.
- Do not continue through `REQUIREMENT UNRESOLVED`.
- Do not claim terminal authority from model consensus, reviewer wording, or CI success.
- Do not resume interrupted work from conversation memory without repository timestamp/state verification.
