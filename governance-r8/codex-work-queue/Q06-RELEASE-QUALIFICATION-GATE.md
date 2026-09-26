# Q06 — Non-authoritative release qualification gate

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

Implement release-qualification machinery that cannot convert test/reviewer/workflow success into release authority by itself.

## Required coding

1. Define release-candidate identity and exact dependency on bounded Stage2/runtime qualification evidence.
2. Implement fail-closed release prerequisites and state transitions.
3. Require exact source commit/tree, build artifact digest/SBOM or equivalent inventory, test/qualification evidence, unresolved-finding check, and independent release review.
4. Separate RELEASE_QUALIFIED evidence from RELEASE_AUTHORIZED action.
5. Add stale/substituted build, partial evidence, skipped review, green-CI laundering, and self-approval negative tests.
6. Add deterministic evidence/packet generation.
7. Do not perform or authorize an actual release.

## Done when

- Release qualification can be evaluated deterministically.
- Release action remains a separately authorized boundary.
