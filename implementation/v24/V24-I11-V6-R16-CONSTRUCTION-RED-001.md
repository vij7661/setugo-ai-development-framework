# V24-I11-V6-R16 — Construction RED 001

Status: **PRESERVED RED / TEST-FIXTURE DEFECT BEFORE INTENDED VALIDATOR ENDPOINT**

Authority effect: `NONE_EVIDENCE_ONLY`

## Bound run

- workflow: `V24 V6 R16 Contract Construction`
- run: `34777200425`
- candidate head: `0bf998a5b5e649c6cf39cee259b968f533defa15`
- candidate tree: `96f58824da760eb8bf1d7ff3e354359e8c26bdf0`
- Python: `3.12.14`

## Result

- R16 module/test compilation: PASS
- R16 contract tests reached: 13
- 12 PASS
- 1 ERROR
- broader V24 regression: skipped because the R16 test step failed

## Failure endpoint

`test_name_only_probe_record_cannot_satisfy_execution` deliberately replaced one probe record with a name-only object containing only `probe_id`. Before invoking `validate_r16_external_evidence`, the test helper `reseal_probe_set()` attempted to read `record_digest` from every record. The deliberately malformed name-only record therefore caused `KeyError: 'record_digest'` inside the test fixture.

The validator under test was not reached for this adversarial case.

## Classification

`TEST_FIXTURE_DEFECT_BEFORE_INTENDED_VALIDATOR_ENDPOINT`

This RED is not evidence that the R16 validator accepts name-only probe records. It also is not a PASS for that behavior because the intended endpoint was not exercised.

## Narrow repair

Change only the adversarial test fixture so its top-level `probe_set_digest` can be recomputed without requiring a missing `record_digest`, then rerun the exact gate. Do not weaken production validation.

- scientific execution: `CLOSED_PENDING_SUCCESSOR_REVIEW`
- runtime qualification: `NOT_CLAIMED`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
