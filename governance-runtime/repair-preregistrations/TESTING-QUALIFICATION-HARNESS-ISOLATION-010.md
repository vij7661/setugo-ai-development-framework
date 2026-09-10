# TESTING Qualification Harness Isolation — Repair Preregistration 010

Status: FROZEN_BEFORE_REPAIR
Authority effect: NONE_EVIDENCE_ONLY

## Scientific subject

Exact exposed candidate SHA: `af3b21fc568480b295ee49a6c7a2dd2b76650b89`.

The independent R9 successor review returned `CHANGES_REQUIRED` and exposed two blocking false-green paths:

- `R10-A`: candidate-controlled Python module shadowing can prevent the externally invoked unittest suite from executing while returning success.
- `R10-B`: three candidate qualification test modules imported through the pinned bridge are not independently blob-pinned and can be replaced with same-count trivial tests.

The eventual repaired successor SHA is intentionally unknown at preregistration time and MUST be recorded only after repair and merge. No PASS from the exposed subject may be replayed to that successor.

## Frozen attacks

### R10-A — unittest shadowing

Construct a candidate attack revision that adds a candidate-controlled `governance-runtime/unittest.py` or equivalent import-precedence shadow which exits successfully without executing the intended qualification tests. The repaired external checker MUST fail closed before publishing a successful qualification result.

Acceptance requires the checker-owned execution path to prevent candidate-controlled stdlib/test-runner shadowing. The mechanism must not simply grep for one filename; it must remove candidate-controlled import precedence from the interpreter/test-runner boundary or provide equivalently strong isolation. User-site contamination must also be disabled.

### R10-B — bridge dependency substitution

Construct a candidate attack revision that modifies at least one of:

- `governance-runtime/test_qualification_boundary_policy.py`
- `governance-runtime/test_manual_review_authority_spoofing_regression.py`
- `governance-runtime/test_manual_review_authority_ingress_regression.py`

without changing the already pinned bridge file, preserving the bridge's expected count/prefix shape. The repaired external checker MUST fail closed on blob identity before accepting the test result.

## Repair boundary

1. Independently pin all three bridge-imported qualification test modules by exact candidate Git blob SHA, or replace them with checker-owned adversarial tests outside candidate control.
2. Execute candidate qualification tests from a checker-owned location/interpreter configuration that cannot import a candidate-provided `unittest`, `json`, `hashlib`, or equivalent stdlib shadow from the candidate working directory. Prefer an isolated Python invocation and explicit controlled module search path.
3. Disable user-site import influence for qualification execution.
4. Preserve prior RED/CHANGES_REQUIRED evidence append-only.
5. Do not weaken exact-SHA, App-source, external-root, policy/verifier/facade, ruleset, or signed-attestation checks.
6. R9-02 checker-revision binding remains a separately acknowledged bounded TESTING residual unless new evidence shows candidate exploitability.
7. Any new material finding discovered during repair must be preserved and preregistered before its mechanism is changed.

## Required evidence for closure

- A genuine RED/fail-closed execution for the frozen R10-A attack.
- A genuine RED/fail-closed execution for the frozen R10-B attack.
- Green external qualification for a distinct repaired candidate successor SHA.
- Successful execution of all intended qualification tests under the isolated runner.
- Fresh independent manual re-falsification of the distinct repaired successor exact SHA.
- All results remain evidence only; no automated PASS grants terminal authority.

## Completion rule

R10-A and R10-B are not closed by construction or by local green tests alone. TESTING remains blocked until the frozen attacks are demonstrated fail-closed and a distinct successor passes fresh exact-SHA external qualification plus independent manual re-falsification.
