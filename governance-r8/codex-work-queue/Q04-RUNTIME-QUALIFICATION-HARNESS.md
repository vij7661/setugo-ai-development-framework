# Q04 — Runtime qualification harness and evidence emitter

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

Build the non-authoritative machinery needed to qualify the exact integrated candidate at runtime after all runtime blockers are resolved.

## Required coding

1. Define a machine-readable runtime threat model and qualification matrix.
2. Bind the harness to exact candidate commit/tree and exact implementation/machinery blobs.
3. Cover filesystem mutation/race behavior, permission/read-only/I/O failure, crash/restart boundaries, idempotency, durable state, external-effect denial, and candidate immutability where applicable.
4. Separate “mechanism test passed” from “runtime qualification granted”.
5. Emit immutable bounded evidence with run/job/toolchain/environment identities.
6. Require independent post-run review before any runtime-qualified state can be materialized.
7. Add negative tests for stale candidate, stale review, substituted environment evidence, missing fault proof, skipped arms, partial runs, and green-workflow laundering.
8. If real target infrastructure or credentials are needed, finish all local/deterministic harness code, record MANUAL_INTERVENTION_REQUIRED, and continue queue.

## Done when

- Harness and evidence format are complete and testable.
- No runtime qualification is self-granted.
- Any live execution remains separately authorized.
