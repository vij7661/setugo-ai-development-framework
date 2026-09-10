# TESTING Qualification Boundary — Strengthened R8 Independent Review

Status: `CHANGES_REQUIRED_PRESERVED`
Authority effect: `NONE_EVIDENCE_ONLY`
Reviewed candidate SHA: `61e98ba0ca8fc461b407e91e4f60ffc687fc784e`
Reviewed external checker SHA: `37df9c463d8db7bde4616e2f71f621b7188a40b6`
Reviewed external governance root SHA: `5f470774ec8c17f5519da8db2aaae59af114cef9`
Reviewer disposition: `CHANGES_REQUIRED`

## Reviewer adjudication preserved

The independent reviewer found R8-01, R8-02, R8-04, R8-05, and R8-07 addressed in the strengthened packet. R8-03 was assessed as bounded with residual use-time checker-revision risk. R8-06 remained blocking because the reviewed scientific subject was still the exposed SHA `61e98ba0...`; no distinct repaired successor SHA with fresh exact-SHA evidence existed yet.

The review also exposed a new HIGH false-green path: the external checker pins authority-critical production files, but then executes candidate-controlled unittest modules whose Git blobs are not independently pinned. A candidate could weaken/replace those tests and preserve an external PASS unless the checker either pins the exact invoked test corpus or replaces it with checker-owned adversarial tests.

A second residual finding was that GitHub required checks bind context plus App integration ID, not the check-run `external_id`; therefore the branch rule cannot itself require checker SHA `37df9c...`. This is not directly candidate-exploitable under the protected external-checker/credential boundary, but remains a bounded governance residual unless an additional use-time checker-revision mechanism is established.

## Exact blocking requirements carried forward

1. Produce a distinct repaired successor candidate SHA and run fresh candidate CI, external qualification, and independent review against that exact SHA. Evidence for `61e98ba0...` must not be replayed to the successor.
2. Close the candidate-controlled test-harness false-green path before relying on another external PASS.
3. Preserve the checker-revision residual explicitly; do not claim GitHub branch rules bind `external_id` when they do not.
4. Previous RED and PASS evidence remains history only and grants no authority.

No TESTING, RELEASE, PRODUCTION, merge, deployment, or terminal authority is granted by this record.