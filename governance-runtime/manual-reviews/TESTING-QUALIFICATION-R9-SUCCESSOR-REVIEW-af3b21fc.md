# Independent Falsification Review — R9 Successor

Authority effect: `NONE_EVIDENCE_ONLY`.

Reviewed candidate: `af3b21fc568480b295ee49a6c7a2dd2b76650b89`
External checker: `af3fb7b453c8e7b0a034cf0be90524e65f6a52fc`
External governance root: `5f470774ec8c17f5519da8db2aaae59af114cef9`

Source artifact SHA-256: `b96e44340edac4c2a608f1f3f89b8bc299e7410218be60a9f7e66b825e8b70b8`

Disposition: `CHANGES_REQUIRED`.

Blocking findings preserved from the independent review:

## R10-A — Candidate-controlled unittest shadowing

Severity: HIGH. Blocking in TESTING: YES.

The external checker invokes `python -m unittest` with `cwd` inside the candidate `governance-runtime` tree. Candidate-controlled `unittest.py` or `unittest/__init__.py` can shadow the standard-library unittest module and exit successfully without executing pinned tests. This creates a false external PASS while the pinned adversarial tests never run.

Minimum repair boundary from the review: isolate interpreter/test execution from candidate-controlled module shadowing, including safe-path/user-site controls or checker-owned execution that excludes candidate paths from import precedence, and add a frozen attack proving shadowing fails closed.

## R10-B — R9-01 incomplete through unpinned bridge imports

Severity: HIGH. Blocking in TESTING: YES.

The pinned `test_qualification_boundary_unittest_bridge.py` dynamically imports three qualification-contributing candidate test modules that were not independently blob-pinned:

- `test_qualification_boundary_policy.py`
- `test_manual_review_authority_spoofing_regression.py`
- `test_manual_review_authority_ingress_regression.py`

Same-count trivial substitution can satisfy the pinned bridge while removing the actual spoofing/authority regressions.

Minimum repair boundary: independently pin these three modules or replace them with checker-owned adversarial tests.

## Non-blocking/residual findings retained

- Governance-critical runtime modules such as `review_protocol.py` and `phase_policy.py` are not independently blob-pinned; this becomes materially exploitable in combination with R10-A.
- Packet did not include independently recomputable Git blob SHA values for every pinned candidate test file; LOW evidence gap.
- Administrative ruleset attestation remains bounded human-signed evidence rather than cryptographic GitHub proof; LOW residual.
- Required check binds context + App ID but not checker `external_id`; R9-02 remains an acknowledged LOW residual in TESTING.

R8-01, R8-02, R8-05, R8-06, and R8-07 were assessed closed against the reviewed exact successor. R8-03/R9-02 remained bounded residuals. R8-04 was partial and materially exposed through R10-A.

TESTING remains blocked until R10-A and R10-B are closed and the repaired successor receives fresh exact-SHA candidate evidence, fresh external qualification, and fresh independent re-falsification.

This preservation record is evidence only and grants no TESTING, RELEASE, PRODUCTION, merge, deploy, or terminal authority.
