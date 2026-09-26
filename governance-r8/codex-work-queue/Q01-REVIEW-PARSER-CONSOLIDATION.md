# Q01 — Shared review-contract parser and exact-artifact preflight

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

Remove the duplicated review-parser logic that caused the two failed-closed SG-1 activation attempts, while preserving fail-closed semantics.

## Required coding

1. Extract the review A-H parser into one importable production module used by:
   - activation-gate validation;
   - offline parser validation;
   - exact-review dry-run/preflight tooling.
2. Preserve the accepted contract:
   - exactly one ordered A-H document;
   - A = BOUNDED_PASS when required;
   - clean C/D sections;
   - H activation YES / YES. with optional single list marker;
   - H broader authority NO / NO. with optional single list marker;
   - reject contradictory YES/NO declarations;
   - reject duplicated/reordered sections;
   - reject hidden Critical/High findings outside C/D, including list-marker forms and FINDING forms.
3. Add table-driven adversarial tests covering punctuation, whitespace, case, bullets, duplicates, hidden findings, contradictory declarations, malformed headings, and copied/stale review scenarios.
4. Add an exact-artifact preflight command that validates the exact review file against the exact gate contract before an activation artifact may be created.
5. Refactor workflows to call the shared module rather than embed separate regex logic.
6. Preserve exact authority boundaries and historical activation failures.

## Done when

- Shared parser has one authoritative code path.
- Existing Review 002, Review 003, and Review 004 all produce the expected bounded parse result.
- Known malformed variants fail closed.
- CI proves workflow and offline validator use the same parser implementation.
- No activation or semantic execution occurs in this PR.
