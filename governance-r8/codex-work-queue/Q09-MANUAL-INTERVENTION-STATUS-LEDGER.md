# Q09 — Manual-intervention ledger and uninterrupted work-queue tooling

## Global execution rules

- Base truth is the SG-1 bounded closure at commit `7cd2787d85b189a4161f271ee131e42bd961140a`.
- Do not weaken existing tests, governance oracles, authority boundaries, failure preservation, exact-SHA binding, or independent-review requirements.
- Do not grant runtime/release/deployment/production/policy/constitutional/root/terminal authority.
- Do not restore six-slice cadence automatically; fallback-to-3 remains ACTIVE unless a separately authorized human action changes it.
- Preserve all RED/failure history.
- Add deterministic tests for every new mechanism and negative/bypass tests for every load-bearing guard.
- Keep changes scoped to this PR. If a prerequisite requires human approval/review/credentials/external infrastructure, implement everything possible up to that boundary, record `MANUAL_INTERVENTION_REQUIRED` with exact reason/evidence, and do not wait.
- Never stop the overall work queue because this PR is blocked; the master Codex queue must continue to the next PR.
- Do not merge the PR. Leave it ready for later human review.


## Objective

Support the requested workflow: a blocked PR must not halt coding on the remaining PRs.

## Required coding

1. Add a machine-readable work-queue manifest listing all coding PR/task IDs, dependencies, and states.
2. Add tooling that records per-task:
   - CODE_COMPLETE;
   - TESTS_PASS;
   - MANUAL_INTERVENTION_REQUIRED;
   - BLOCKED_BY_CODE_DEPENDENCY;
   - REVIEW_REQUIRED;
   - READY_FOR_HUMAN_CHECK.
3. A manual-intervention item must contain exact reason, command/run/PR/file evidence, and requested human action.
4. Add a queue command that selects the next runnable coding task and skips tasks waiting on humans.
5. Never auto-approve reviews, restore cadence, merge PRs, activate governed gates, release, deploy, or enable production.
6. Generate a final consolidated manual-intervention report after the queue has no runnable coding tasks.
7. Add tests proving one blocked task does not prevent selection of the next independent task.

## Done when

- Codex can work through the entire coding queue without stopping for human-only boundaries.
- At the end, one deterministic report tells us exactly what manual interventions remain.
