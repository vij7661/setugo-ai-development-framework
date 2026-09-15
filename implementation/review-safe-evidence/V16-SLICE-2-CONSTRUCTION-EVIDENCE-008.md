# V16 Slice 2 Construction Evidence 008

## Bound construction run

- candidate commit: `c1f5853fb8c520c926df6216fa4d5c8b4a970a08`
- candidate tree: `af29bfba24919bccf66c56c558be52f0f3f8e2c1`
- repaired supervisor source blob: `a0f2c573eca92ade798550cd7fa0515bd0e56e0c`
- workflow: `Review Safe Evidence V16 Slice 2 External Supervisor V2`
- workflow run: `34999060722`
- job: `104482599483`
- result: `success`

This is construction evidence only. RED 009 and RED 010 remain preserved historical failures.

## V2 matrix result

The repaired supervisor executed 17 bounded cases:

- expected construction PASS: 2;
- expected fail-closed: 15.

The original V1 matrix remained stable and the IAR8 inherited-writer regressions were added.

Observed regression results:

`V16_SLICE2_RED009_ABRUPT_ZERO_EXIT_REGRESSION=PASS`

`V16_SLICE2_RED010_DELAYED_DESCENDANT_OUTPUT_REGRESSION=PASS`

`V16_SLICE2_RED010_HELD_OPEN_PIPE_TIMEOUT_REGRESSION=PASS`

`V16_SLICE2_DESCENDANT_AGGREGATE_OUTPUT_LIMIT_REGRESSION=PASS`

For the exact RED-010 shape, the main worker emitted a valid result and exited 0 while a descendant retained stdout and later emitted extra bytes. V2 waited for inherited-pipe EOF, captured the delayed bytes, and rejected the combined stream as invalid JSON rather than accepting the valid prefix.

For a descendant that held stdout open beyond the deadline, V2 returned `SUPERVISOR_FAIL_CLOSED` with both `WORKER_PROTOCOL_STREAMS_NOT_EOF` and `WORKER_TIMEOUT`, despite main-worker return code 0.

For descendant aggregate stdout overflow, V2 failed closed with `WORKER_STDOUT_OVERSIZE`.

The repaired source blob matched before and after execution, and the checkout remained clean.

## Scope boundary

This result closes only the construction-level inherited-protocol-stream defect exercised by IAR8-H1. It does not establish a complete arbitrary-code sandbox or an authenticated supervised-test-plan authority.

Still open:

`WORKER_PROCESS_REPLACEMENT_OS_ENFORCEMENT=NOT_YET_PROVEN`

`WORKER_DESCENDANT_PROCESS_ESCAPE_ENFORCEMENT=NOT_YET_PROVEN`

`SUPERVISED_TEST_PLAN_AUTHENTICATED_BINDING=NOT_YET_IMPLEMENTED`

`EXISTING_77_TESTS_EXTERNAL_SUPERVISOR_MIGRATION=NOT_COMPLETE`

## Authority boundary

`INTERNAL_ADVERSARIAL_REVIEW_EXHAUSTED=false`

`V16_SLICE2_FREEZE_ALLOWED=false`

`IMPLEMENTATION_QUALIFICATION=NOT_CLAIMED`

`RUNTIME_QUALIFICATION=NOT_CLAIMED`

`SCIENTIFIC_AUTHORITY=NOT_CLAIMED`

`AUTHORITY_EFFECT=NONE_EVIDENCE_ONLY`
