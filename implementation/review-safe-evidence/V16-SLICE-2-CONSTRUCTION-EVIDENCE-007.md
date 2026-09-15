# V16 Slice 2 Construction Evidence 007

## Bound construction run

- candidate commit: `7df80ebe2144cd6eefc7e4f9eb12dff0b471969b`
- candidate tree: `956ea7318ec433d6fd2f0cfe2f6c42df03b3f7e0`
- supervisor source blob: `62b66e386c6f1473a7051c7deef3f7fc7da0ea64`
- workflow: `Review Safe Evidence V16 Slice 2 External Supervisor V1`
- workflow run: `34998546821`
- job: `104480879266`
- result: `success`

This is **construction evidence only**. It does not erase RED 009, does not complete migration of the historical 77-test universe, and does not establish implementation/runtime/scientific/effect authority.

## Mechanism matrix

The workflow exercised 14 supervisor/worker cases. Two expected-valid cases passed only after the supervisor parsed the bounded worker result and independently applied the supervisor-owned oracle. Twelve adversarial cases failed closed.

Expected-valid:

- normal bounded response;
- normal bounded response with worker stderr diagnostics.

Expected fail-closed:

- abrupt `os._exit(0)` with no response;
- nonzero exit;
- signal termination;
- timeout;
- malformed JSON;
- duplicate JSON keys;
- extra console text/multiple response material;
- wrong operation identity;
- worker self-declared `PASS` top-level field;
- oracle-mismatching result;
- oversized stdout;
- valid-looking response followed by nonzero exit.

The load-bearing IAR7 regression was explicitly demonstrated repaired at this boundary:

`abrupt_zero` produced worker return code `0` but supervisor state `SUPERVISOR_FAIL_CLOSED`, `response_valid=false`, and `oracle_pass=false`.

The workflow emitted:

`V16_SLICE2_SUPERVISOR_MATRIX_CASES=14`

`V16_SLICE2_SUPERVISOR_EXPECTED_PASS_CASES=2`

`V16_SLICE2_SUPERVISOR_EXPECTED_FAIL_CLOSED_CASES=12`

`V16_SLICE2_IAR7_ABRUPT_ZERO_EXIT_FAILS_CLOSED=PASS`

`V16_SLICE2_SUPERVISOR_ORACLE_EXECUTES_AFTER_WORKER=PASS`

Pre/post source blob and checkout re-attestation also passed.

## Deliberately open boundaries

This construction result does **not** prove an arbitrary-code worker sandbox. The current design explicitly leaves these open:

`WORKER_PROCESS_REPLACEMENT_OS_ENFORCEMENT=NOT_YET_PROVEN`

`WORKER_DESCENDANT_PROCESS_ESCAPE_ENFORCEMENT=NOT_YET_PROVEN`

It also does not migrate the existing 77 mandatory Slice 2 behavioral tests to supervisor-owned external oracles:

`EXISTING_77_TESTS_EXTERNAL_SUPERVISOR_MIGRATION=NOT_COMPLETE`

Therefore RED 009 is not retroactively converted into a PASS. The new supervisor core demonstrates a narrower repaired completion rule for its own bounded result protocol.

## Authority boundary

`INTERNAL_ADVERSARIAL_REVIEW_EXHAUSTED=false`

`V16_SLICE2_FREEZE_ALLOWED=false`

`IMPLEMENTATION_QUALIFICATION=NOT_CLAIMED`

`RUNTIME_QUALIFICATION=NOT_CLAIMED`

`SCIENTIFIC_AUTHORITY=NOT_CLAIMED`

`AUTHORITY_EFFECT=NONE_EVIDENCE_ONLY`
