# Q07 — Deployment qualification, environment binding and rollback gate

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

Build deployment qualification machinery without granting deployment or production authority.

## Required coding

1. Bind deployment candidate to exact release artifact digest and environment identity.
2. Define environment configuration/provenance contract without storing secrets.
3. Add dry-run/preflight checks, migration compatibility checks where applicable, health/readiness checks, rollback plan verification, and post-deploy evidence schema.
4. Fail closed on environment drift, artifact substitution, missing rollback evidence, partial health checks, stale qualification, or unknown target.
5. Separate DEPLOYMENT_QUALIFIED evidence from DEPLOY_AUTHORIZED action.
6. Add deterministic tests and negative/fault cases.
7. If a real cloud/environment is needed, complete local code/tests, record MANUAL_INTERVENTION_REQUIRED with exact credentials/infrastructure need, and continue queue.

## Done when

- Deployment readiness can be evaluated without deploying.
- No production authority is granted.
