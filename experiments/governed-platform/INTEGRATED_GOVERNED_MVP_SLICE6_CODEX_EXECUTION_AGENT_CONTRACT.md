# Integrated Governed MVP — Slice 6 Codex Execution Agent Contract

Status: **PRE-IMPLEMENTATION FROZEN BOUNDARY**

Parent authoritative integration commit: `f67e0dfb4fe9b4bb67c76dbd43f1485861c96fc0` (accepted Slice 5 authoritative state ledger).

## 1. Goal

Falsify whether Codex can be introduced as a governed implementation/execution agent without gaining authority to redefine requirements, weaken tests, widen task scope, bypass review, trust stale CI, or mint merge/release/completion authority.

Codex is an execution mechanism. It is not a source of product truth or terminal authority.

## 2. Included

- root-level Codex operating contract through `AGENTS.md`;
- a reusable `codex-execution` skill defining task intake, implementation, failure triage, validation, and handoff rules;
- exact repository/branch/HEAD binding before and after work;
- narrow task scoping with explicit goal, affected components, constraints, acceptance criteria, tests, and forbidden changes;
- mandatory use of the existing failure-triage protocol before fixing any failing signal;
- exact-current-HEAD CI validation before reporting success;
- preservation of manual-QA and human-decision gates;
- prohibition on self-issued merge/release/deploy/completion authority;
- deterministic static validation that the Codex agent package contains the mandatory governance clauses.

## 3. Deferred / nonclaims

- production remote sandbox security;
- provider/model attestation;
- autonomous merge, deploy, release, or production authority;
- autonomous requirement resolution;
- distributed multi-host execution guarantees;
- secrets/KMS production integration;
- physical durability guarantees beyond already accepted Slice 5 scope.

## 4. Frozen authority invariants

**S6-I01 Contract authority** — Codex must derive intended behavior from the latest approved authoritative requirement/architecture state, never from implementation convenience, stale tests, chat recollection, or model preference.

**S6-I02 Exact state binding** — before changing code, Codex records repository, branch, and exact HEAD; before claiming success, it re-reads and validates the exact current HEAD.

**S6-I03 Narrow execution scope** — every implementation task must define goal, affected components, constraints, acceptance criteria, tests, and forbidden changes before modification begins.

**S6-I04 No test laundering** — Codex may not weaken/delete/skip valid tests, alter fixtures, hard-code behavior, or redefine requirements merely to make CI green.

**S6-I05 Failure triage first** — any failing test/build/CI signal must be classified using the repository `failure-triage` skill before corrective implementation.

**S6-I06 Root-cause ownership** — repairs are made at the authoritative owner of the defect and must avoid unrelated changes.

**S6-I07 Fresh validation** — success requires validation against the corrected current HEAD; CI or test evidence from an older SHA is non-authoritative for the new head.

**S6-I08 Human gate preservation** — `REQUIREMENT UNRESOLVED`, manual QA, security-sensitive approval, and terminal authority decisions remain external human/platform gates.

**S6-I09 No terminal authority** — Codex cannot merge, release, deploy, mark production-ready, or declare completion solely from its own output or green CI.

**S6-I10 Evidence handoff** — Codex must report what changed, why, exact validation executed, exact HEAD, remaining risks, and any required manual/human gate.

**S6-I11 Abrupt-stop recovery** — after an interrupted session, Codex must recover from repository/activity timestamps and authoritative repo state before resuming; chat memory alone is insufficient.

**S6-I12 Deterministic guardability** — mandatory governance clauses must be machine-checkable so accidental weakening of the Codex operating contract fails CI.

## 5. Frozen acceptance cases

- `S6-01` root `AGENTS.md` exists and establishes Codex as execution-only, not requirement or terminal authority.
- `S6-02` task protocol requires goal, affected components, constraints, acceptance criteria, tests, and forbidden changes.
- `S6-03` exact repo/branch/HEAD capture is required before implementation.
- `S6-04` exact current HEAD revalidation is required before PASS/completion reporting.
- `S6-05` failure-triage is mandatory before changing code after a failing signal.
- `S6-06` valid tests/fixtures/requirements cannot be weakened merely to reach green CI.
- `S6-07` unresolved requirements stop execution behind a human decision gate.
- `S6-08` manual QA remains explicit when automated validation is insufficient.
- `S6-09` Codex cannot self-authorize merge/release/deploy/production/completion.
- `S6-10` abrupt-stop recovery requires latest authoritative repo/activity timestamp inspection.
- `S6-11` reusable `skills/codex-execution/SKILL.md` exists and mirrors the root authority invariants.
- `S6-12` a deterministic validator rejects removal of any mandatory governance clause.
- `S6-13` a deterministic validator rejects an agent configuration that grants Codex terminal authority.
- `S6-14` validation tooling itself runs without network access or model self-report.
- `S6-15` the existing failure-triage skill remains unchanged and referenced rather than duplicated inconsistently.
- `S6-16` Slice 1→Slice 5 accepted behavior remains untouched by the Codex integration package.

## 6. Construction and freeze rules

1. Commit this contract before implementation files.
2. Implement on `feature/integrated-governed-mvp-slice6-codex-execution-agent` only.
3. Do not weaken Slice 1→Slice 5 contracts or adjudications.
4. Preserve the first failing construction/validation result before repair.
5. Freeze one exact candidate SHA only after S6-01..S6-16 pass.
6. Independent review remains required before promotion into `main`.
7. Green CI alone is insufficient for promotion.

## 7. Claim boundary

A bounded Slice 6 pass proves only that the repository contains a machine-checkable governed Codex execution-agent contract that preserves existing authority boundaries, exact-head validation, failure triage, narrow task scope, human gates, and interruption recovery. It does not prove production sandbox security or grant Codex autonomous terminal authority.
