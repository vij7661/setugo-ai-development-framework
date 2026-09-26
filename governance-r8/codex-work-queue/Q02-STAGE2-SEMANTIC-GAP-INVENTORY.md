# Q02 — Deterministic Stage2 semantic-gap inventory and next-gate scaffold

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

Determine the remaining Stage2 semantic work after SG-1 closure without inventing an SG-2 scope manually.

## Required coding

1. Build a deterministic scanner over the exact Stage1 candidate and current governed artifacts to enumerate semantic obligations not covered by the closed SG-1 objective.
2. Classify each discovered item as:
   - already covered;
   - excluded by SG-1 but still required for a later phase;
   - unresolved semantic dependency;
   - runtime-only;
   - release/deployment/production-only;
   - manual-policy decision.
3. Emit a machine-readable inventory with exact file/blob/source references and stable IDs.
4. Generate proposed next-gate preregistration skeletons only for evidence-backed semantic gaps.
5. Add false-positive tests proving lexical/name similarity alone cannot create a new gate.
6. Add omission tests so a known uncovered semantic obligation makes the inventory fail.
7. Never execute or activate a proposed next gate in this PR.

## Done when

- The repository can deterministically answer “what semantic coding remains after SG-1?”.
- Any proposed SG-2/SG-n scope is generated from bound evidence rather than assistant/model inference.
- The output clearly separates semantic work from runtime/release/deployment/production work.
- If a human decision is required to choose among valid next gates, record MANUAL_INTERVENTION_REQUIRED and finish all deterministic inventory work first.
