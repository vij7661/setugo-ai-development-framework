# RELEASE R1 Bridge Shape RED 001

Status: PRESERVED_RED
Authority effect: NONE

Preregistered requirement: `REL-R1-01` in `governance-runtime/release-preregistrations/RELEASE-R1-HARDENING-001.md`.

Exact exposed candidate SHA: `a170dcbf3ed431eed3e8b0bf01bb1f7edbfa620c`.
GitHub Actions run: `34499863762`.
Observed conclusion: `failure`.

The frozen RELEASE regression required a bridge-owned `_execute_sync_test_function` guard capable of rejecting coroutine, generator, async-generator, awaitable-returning, and generator-returning top-level qualification tests. The pre-repair bridge did not contain that mechanism, so the regression failed as intended.

Classification: `GOVERNANCE_PROCESS_DEFECT / QUALIFICATION_HARNESS_FALSE_GREEN_RISK` exposed before repair.

This RED remains evidence after later repair. It must not be rewritten as a successful run or removed from the scientific history.
