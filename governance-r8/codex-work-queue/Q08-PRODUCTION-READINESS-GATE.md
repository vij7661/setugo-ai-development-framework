# Q08 — Production readiness, observability and recovery qualification

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

Implement production-readiness evidence checks while keeping production enablement a separate human/governed authority.

## Required coding

1. Define production-readiness contract for:
   - observability/telemetry;
   - durable audit/failure history;
   - backup/recovery where applicable;
   - incident/rollback readiness;
   - capacity/error-budget or equivalent bounded health signals;
   - secret/config handling checks;
   - dependency/provider failure behavior.
2. Add deterministic readiness checks and falsification cases.
3. Prove success labels/healthy dashboards cannot mint production authority.
4. Require exact release/deployment evidence lineage.
5. Emit bounded readiness evidence and reviewer packet.
6. Do not enable production traffic or mutate live infrastructure.

## Done when

- Production readiness can be tested and evidenced.
- PRODUCTION_AUTHORIZED remains false until a separately governed action.
