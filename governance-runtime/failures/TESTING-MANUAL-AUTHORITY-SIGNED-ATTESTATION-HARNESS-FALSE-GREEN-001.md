# TESTING Manual Authority Signed-Attestation Harness False Green 001

Status: `PRESERVED_FALSE_GREEN`
Phase: `TESTING`
Authority effect: `NONE_EVIDENCE_ONLY`

## Exact run

- candidate SHA: `2585c7e20674cbc56c97f6342ecde6ba426badc1`
- workflow run: `34441874259`
- workflow conclusion: `SUCCESS`

## Defect

The workflow explicitly invoked `python -m unittest -v test_manual_authority_signed_attestation.py`, but that file contained only module-level `test_*` functions. Python `unittest` did not collect those functions. The CI log reported the same 69 governance tests as before and did not list any of the new real signed-attestation cases.

Therefore run `34441874259` is not evidence that the real human-signed fixture or its replay/tamper cases executed, even though other governance tests were green.

## Repair discipline

The test expectations and signed fixture MUST NOT be weakened. Correct only collection by converting the test module to a `unittest.TestCase` (or equivalent explicit bridge), then rerun the exact resulting candidate.

## Nonclaim

This false green does not imply the Ed25519 verifier is defective. It proves only that the newly added signed-fixture regressions were not executed by that run.
