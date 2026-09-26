# Q03 — Runtime filesystem TOCTOU hardening

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


## Source blocker

`governance-r8/R8-V15-R1-RUNTIME-QUALIFICATION-OPEN-001.json`
records `R8V15R1-RTQ-OPEN-001`: filesystem path-check/read TOCTOU under adversarial concurrent namespace mutation.

## Objective

Implement the narrow runtime-safe file-read primitive required to resolve this coding blocker, without claiming runtime qualification.

## Required coding

1. Define the supported filesystem/adversary model in code-facing documentation/tests.
2. Replace check-then-`Path.read_bytes()` patterns on the affected governed path with a single-open descriptor-based read.
3. Use no-follow semantics where supported.
4. Verify opened object identity/type with `fstat` or equivalent before consuming bytes.
5. Preserve confinement, symlink rejection, exact digest checks, and existing error taxonomy.
6. Add adversarial tests for:
   - symlink swap;
   - rename/replace race;
   - non-regular file;
   - inode/object substitution;
   - read failure;
   - platform capability fallback/fail-closed behavior.
7. Add regression tests proving no weakening of repository-local construction behavior.

## Done when

- The code no longer has the known check/read namespace gap for the in-scope path.
- Race/fault tests are deterministic and fail closed.
- Runtime qualification remains explicitly false pending the separate qualification PR/review.
