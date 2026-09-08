# GOV-FROZEN-CROSS-COMMIT-EVIDENCE-001

## Objective
Repair the R3 evidence-package defect identified in Slice5 R3 run 34247110619: a lossless R2-to-R3 handoff stored on the governance branch must be inspectable as actual materialized evidence without copying it into or mutating the reviewed product candidate.

## Frozen contract
1. Preserve existing candidate-bound `file`, `ci_run`, and `history` semantics unchanged.
2. Add evidence type `frozen_file` with required fields:
   - `ref`: repository path
   - `commit`: exact lowercase 40-character Git commit SHA
3. Materialize with exact `git show <commit>:<path>` only after verifying the commit resolves exactly.
4. Record source commit, path, UTF-8 byte count, and SHA-256 of bytes in the corpus.
5. Never fall back to branch HEAD, candidate SHA, working-tree content, or history text when the pinned commit/path is unavailable.
6. Malformed SHA, missing path, unavailable commit/path, or non-UTF8 content fails closed before provider invocation.
7. The new evidence type grants no authority by itself; it is evidence input only.
8. Candidate-bound `file` refs remain bound to the reviewed candidate and cannot specify an alternate commit.
9. Reviewer/provider semantics and exact provider/model binding remain unchanged.

## Required deterministic cases
- exact pinned governance file materializes with correct commit/path/hash;
- wrong/malformed SHA rejects;
- missing path rejects;
- absent file at valid commit rejects;
- candidate `file` behavior is unchanged;
- unknown ref type rejects;
- materialized count still equals declared refs;
- no provider/network call occurs in qualification tests.

## Slice5 use
After a fresh R2 for the repaired Slice5 candidate, R3 must include the actual lossless R2-to-R3 handoff via `frozen_file` pinned to the governance commit that freezes that handoff. History text alone is insufficient.
