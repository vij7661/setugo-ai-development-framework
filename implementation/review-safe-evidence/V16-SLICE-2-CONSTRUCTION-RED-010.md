# V16 Slice 2 Construction RED 010

## Classification

`CODE_DEFECT / INHERITED_PROTOCOL_FD_LATE_OUTPUT_FALSE_GREEN`

This RED preserves a mechanically reproduced defect in External Supervisor V1. Later repairs or PASS results MUST NOT erase or overwrite it.

## V1 mechanism under falsification

- supervisor source blob: `62b66e386c6f1473a7051c7deef3f7fc7da0ea64`
- V1 construction commit: `7df80ebe2144cd6eefc7e4f9eb12dff0b471969b`
- V1 construction tree: `956ea7318ec433d6fd2f0cfe2f6c42df03b3f7e0`
- V1 construction run: `34998546821`
- V1 construction job: `104480879266`
- prior evidence: `V16-SLICE-2-CONSTRUCTION-EVIDENCE-007.md`

The V1 14-case construction matrix remains preserved. This RED narrows the unsupported property: V1 did not prove that its captured stdout represented the complete protocol stream after all inherited writers closed.

## Falsification run

- probe commit: `0d5199c92e5271478fa327027540809ef126c695`
- probe tree: `18b5c5f13df1128efb1aa1a86b0bdce92eff4171`
- workflow: `Review Safe Evidence V16 Slice 2 Supervisor V1 Descendant Falsification`
- workflow run: `34998713799`
- job: `104481440329`
- falsification workflow result: `success`

The falsification workflow is green because its intended endpoint was successful reproduction of the V1 false-green. It is not a PASS of V1.

## Reproduced mechanism defect

The worker:

1. forked a descendant that inherited stdout;
2. parent emitted one valid response matching the supervisor oracle;
3. parent exited 0;
4. descendant kept inherited stdout open, slept 750 ms, then attempted additional output.

Supervisor V1 observed the main process as exited and finalized when there was no immediately readable event, even though an inherited stdout writer remained open. It parsed only the valid prefix and returned:

`SUPERVISOR_ORACLE_PASS_NONAUTHORITATIVE`

The probe then emitted:

`SUPERVISOR_V1_DESCENDANT_FALSE_GREEN_REPRODUCED=YES`

`SUPERVISOR_V1_FINALIZED_BEFORE_ALL_INHERITED_OUTPUT_FDS_CLOSED=true`

`SUPERVISOR_V1_EXACTLY_ONE_COMPLETE_RESPONSE_STREAM_NOT_PROVEN=true`

Thus V1's exact-one-response rule was false-green: it validated a prefix rather than proving EOF on all inherited protocol writers.

## Required narrow repair

The supervisor must not finalize response parsing merely because the main worker PID exited.

It must:

- retain the stdout/stderr read ends until EOF on every protocol pipe or until the configured deadline;
- continue bounded reads after main-process exit while any inherited writer keeps a pipe open;
- include delayed descendant output in the same bounded response stream, causing exact-JSON parsing to fail if extra output exists;
- fail closed on protocol-pipe EOF timeout even when the main process exit status was 0;
- kill the worker process group on timeout/overflow where possible;
- add a regression for valid-prefix + delayed descendant extra output;
- add a regression for valid-prefix + descendant holding a pipe open past the deadline.

Separate OS-level descendant/process-replacement containment remains a broader unproven sandbox boundary even after this protocol repair.

## Authority boundary

`SUPERVISOR_V1_PROTOCOL_COMPLETENESS=FAILED`

`INTERNAL_ADVERSARIAL_REVIEW_EXHAUSTED=false`

`V16_SLICE2_FREEZE_ALLOWED=false`

`IMPLEMENTATION_QUALIFICATION=NOT_CLAIMED`

`RUNTIME_QUALIFICATION=NOT_CLAIMED`

`SCIENTIFIC_AUTHORITY=NOT_CLAIMED`

`AUTHORITY_EFFECT=NONE_EVIDENCE_ONLY`
