# TESTING Qualification Ownership — Harness False Green 001

Phase: `TESTING`
Classification: `TEST DEFECT / GOVERNANCE-PROCESS DEFECT`
Material: `true`
Run: `34438769149`
Exact SHA: `726eaa695c78346e678e104360949ef96800301e`
Disposition: `BLOCK_TESTING`

## Observation

The workflow invoked:

`python -m unittest -v test_phase_policy.py test_qualification_boundary_policy.py test_manual_review_authority_spoofing_regression.py ...`

The workflow concluded SUCCESS and reported 66 tests.

However, the job log contains no executed tests from `test_qualification_boundary_policy.py` or `test_manual_review_authority_spoofing_regression.py`. Both files define pytest-style module-level `test_*` functions rather than `unittest.TestCase` methods. Python `unittest` does not collect those module-level functions.

Therefore the qualification ownership suite and the frozen manual authority-spoofing regressions were silently omitted while CI remained green.

## Why this is load-bearing

The green runs previously cited as construction evidence for QO-01 through QO-08 did not execute the module-level ownership tests. Their success cannot support the ownership-mechanism claims.

The new frozen spoofing attacks were specifically expected to fail against the current mechanism. Their silent non-execution converted an expected RED into a false GREEN.

## Required repair order

1. Repair the test harness first so every intended ownership test is actually collected and executed.
2. Re-run the unchanged vulnerable mechanism with the frozen spoofing tests and preserve the genuine RED.
3. Only after that RED is observed, repair MR-001 / MR-002.
4. Re-run all ownership, phase-policy, review-protocol, and terminal-authority regressions.
5. Perform a new manual exact-SHA re-falsification.

No earlier green run is deleted; it remains evidence of the harness defect.