---
name: failure-triage
description: Diagnose and classify the root cause of a failing test, broken build, or red CI run before writing any fix. Use this immediately whenever a test fails, an assertion doesn't match, a build breaks, or CI goes red — before patching code, editing a fixture, or touching a test. Also use before deleting or skipping any test, before "just" updating a snapshot/fixture to make CI pass, and before reporting a failure as resolved. Do not let a failure get fixed, silenced, or explained away without going through this triage first.
---

# Failure Triage

A failing signal (test, build, CI run) is not itself the problem — it's evidence.
The job here is to find out what it's evidence *of* before anyone touches code.

## Step -1 — Verify the execution state

For repository, build, or CI failures, first verify that the evidence being diagnosed belongs to the exact execution state under review: repository, branch or PR, head SHA, failing run, failing job/check, and relevant environment. Do not diagnose an old CI failure against newer source code without explicitly accounting for the difference. A previously green commit does not validate a different head.

## Step 0 — Establish the contract, not the artifact

Before judging anything, write down in one sentence what the *intended* behavior
is supposed to be — from the requirement or spec, not from what the code or test
currently does. Never assume the current implementation, current test, current
fixture, or current documentation is correct just because it exists.

If there is no clear intended contract for this behavior, stop here — this is a
**REQUIREMENT UNRESOLVED** case (see below). Do not guess one and proceed.

### Contract authority check

When requirement/specification sources disagree, do not choose whichever source supports the current implementation. Determine the most recently approved authoritative product or architecture decision and record the evidence used to establish the contract. Tests, fixtures, implementation, generated documentation, and current behavior are evidence of implementation state; they are not automatically sources of product truth.

## Step 1 — Gather four things independently

Do not skip straight to "the code is probably wrong" or "the test is probably
flaky." Look at all four before deciding:

1. **The product requirement** — what should happen, per the contract from Step 0.
2. **The implementation** — what the code actually does.
3. **The test expectation** — what the test asserts should happen.
4. **The fixture/data/environment** — what data, mocks, or environment the test
   runs against, and whether the CI/build tooling itself is healthy.

## Step 2 — Classify into exactly one category

Classify each independently actionable failure/root cause as exactly one category. Do not split one root cause across categories. If investigation reveals multiple independent defects, split them into separate failure records and classify each independently before moving on.

| Category | Meaning | Signal |
|---|---|---|
| **CODE DEFECT** | The implementation violates the intended contract. | Requirement and test agree; code diverges. |
| **FIXTURE-DATA DEFECT** | Test data or fixtures violate the intended contract. | Code is right; the data used to test it is wrong or stale. |
| **TEST DEFECT** | The test expectation itself is obsolete or incorrect. | Code correctly follows a contract the test wasn't updated for. |
| **ENVIRONMENT-TOOLING DEFECT** | A build/CI/environment issue unrelated to product behavior. | Failure disappears with a clean environment / different runner; product logic isn't involved. |
| **REQUIREMENT UNRESOLVED** | The intended contract itself is undefined or ambiguous. | You can't complete Step 0 without inventing an answer. |

## Step 3 — Apply the matching corrective action

- **CODE DEFECT** — explain which requirement is violated and identify the authoritative architectural owner of the behavior (for example UI/state, domain, backend, persistence, integration, or configuration). Fix the defect at that owner rather than patching a downstream consumer, keep or add a regression test, and re-run validation.
- **FIXTURE-DATA DEFECT** — explain why the fixture violates the contract, fix the
  fixture, confirm production behavior is untouched.
- **TEST DEFECT** — explain why the expectation is obsolete/incorrect, correct the
  test to enforce the actual contract, make no unnecessary implementation changes.
- **ENVIRONMENT-TOOLING DEFECT** — fix build/CI/tooling/environment without
  touching product behavior.
- **REQUIREMENT UNRESOLVED** — stop. Do not invent a decision. Surface the exact
  open question to a human and wait.

## Standing prohibitions (apply regardless of category)

- Do not assume a failing test means the code is wrong.
- Do not assume the code is correct just because tests pass.
- Never weaken a valid test, alter fixtures, or hard-code behavior merely to get
  a green build.
- Never delete a failing test because it's inconvenient — only because Step 3
  determined it's a genuine TEST DEFECT, and even then replace it, don't just
  remove it.
- Never restore obsolete behavior solely because an outdated test expects it.
- Never silently change the product requirement to match what the code happens
  to do.
- Do not modify unrelated production behavior, requirements, fixtures, tests, APIs, schemas, or architecture while correcting the classified failure unless the additional change is demonstrably required by the same root cause.
- Fix the root cause. Not the symptom.

## Step 4 — Validate the correction and determine the gate

After a corrective change, validate the corrected current head rather than relying on evidence from an older commit. Run the narrowest useful validation first, then broaden as appropriate:

1. Re-run the originally failing test/check.
2. Run the regression test added or updated for the root cause, where applicable.
3. Run related/affected component tests.
4. Run relevant formatting, lint/static analysis, integration, contract/API, security, or build checks affected by the change.
5. Run required CI against the corrected current head.

Do not claim the failure is resolved merely because one targeted test passes if broader affected validation is still required. A successful CI run proves only the checks that actually ran.

After validation, explicitly choose one gate result:

- **PASS** — correction is validated and no manual QA remains.
- **PASS — MANUAL QA REQUIRED** — automated validation is healthy, but human/device/visual/integration behavior still requires manual verification. Provide exact build/version/commit, environment setup, test identity/data, actions, expected results, and failure evidence to capture.
- **FAIL — CORRECTIVE DEVELOPMENT REQUIRED** — validation still exposes a defect; triage the new or remaining failure again from Step 0.
- **BLOCKED — REQUIREMENT DECISION REQUIRED** — the contract cannot be established without a human decision.

## Output format

For every failure, report:

- **Test/check name**
- **Expected behavior** (from the contract, not the test source)
- **Actual behavior**
- **Root-cause classification** (exactly one category from Step 2)
- **Evidence** for that classification
- **Corrective action taken** (or the open question, if REQUIREMENT UNRESOLVED)
- **Regression test** added or updated, if applicable
- **Validation performed** against the corrected current head
- **Gate result** (PASS; PASS — MANUAL QA REQUIRED; FAIL — CORRECTIVE DEVELOPMENT REQUIRED; or BLOCKED — REQUIREMENT DECISION REQUIRED)

For a batch of failures, triage each one independently — a batch failing for the
same visible reason can still have different root causes underneath.
