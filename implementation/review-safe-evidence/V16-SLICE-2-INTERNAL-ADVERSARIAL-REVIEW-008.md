# V16 Slice 2 Internal Adversarial Review 008

Review target: External Assertion Supervisor V1, source blob `62b66e386c6f1473a7051c7deef3f7fc7da0ea64`, construction run `34998546821`.

Review class: **INTERNAL_ADVERSARIAL_RECORD / NON-INDEPENDENT**

`AUTHORITY_EFFECT=NONE_EVIDENCE_ONLY`

## Disposition

`CHANGES_REQUIRED`

`INTERNAL_ADVERSARIAL_REVIEW_EXHAUSTED=false`

`V16_SLICE2_FREEZE_ALLOWED=false`

## High finding

### IAR8-H1 — Supervisor V1 can finalize a valid response prefix before inherited protocol writers reach EOF

Affected function:

`review_safe_evidence_v16_execution_supervisor._run_worker_bounded`

Concrete false-green path:

- evaluated worker forks a descendant that inherits stdout;
- parent writes one valid oracle-matching response and exits 0;
- descendant keeps stdout open but is temporarily silent;
- V1 observes `proc.poll() is not None` and no immediately readable selector event, then breaks from its read loop;
- V1 performs only a nonblocking residual drain and can therefore parse the already-received valid prefix before the descendant's delayed bytes arrive;
- the supervisor returns `SUPERVISOR_ORACLE_PASS_NONAUTHORITATIVE` even though the complete inherited stdout stream has not reached EOF.

This was mechanically reproduced by workflow run `34998713799`, job `104481440329`. The probe emitted:

`SUPERVISOR_V1_DESCENDANT_FALSE_GREEN_REPRODUCED=YES`

`SUPERVISOR_V1_FINALIZED_BEFORE_ALL_INHERITED_OUTPUT_FDS_CLOSED=true`

`SUPERVISOR_V1_EXACTLY_ONE_COMPLETE_RESPONSE_STREAM_NOT_PROVEN=true`

Why High:

The new supervisor's principal security improvement is that it, not the evaluated worker, determines whether a complete bounded response satisfies the oracle. Parsing a prefix while an inherited writer is still live breaks that completion boundary and permits late output to escape the exact-one-response check.

Required narrow repair:

- never use main-PID exit alone as response-stream completion;
- keep reading until every registered stdout/stderr pipe reaches EOF or the global deadline expires;
- treat an inherited open protocol pipe at deadline as failure even if the main process exited 0;
- preserve size limits across all inherited writers;
- kill the original process group on timeout/overflow where possible;
- regress valid-prefix + delayed extra output and valid-prefix + pipe-held-open-beyond-deadline.

## Medium observations retained as explicit migration obligations

### IAR8-M1 — Oracle provenance is configuration-supplied, not yet bound to an authenticated supervised-test manifest

`supervise(config)` accepts `expected_result` and `worker_command` from its caller. In the V1 construction workflow those values are created by the harness and the resulting state is explicitly non-authoritative, so this is not currently a promotion false-green. Before supervised Slice 2 cases become load-bearing, each oracle/request/worker/profile relation must be bound to a governed test-plan/manifest rather than accepted from an arbitrary caller.

### IAR8-M2 — OS-level process replacement and descendant escape remain unproven

V1 uses a process group and timeout but does not prove a complete arbitrary-code sandbox. A worker can attempt `fork`, `setsid`, `exec*`, file/network access, or other descendant escape. The current design explicitly discloses these as unproven; they remain blockers to any final arbitrary-code sandbox claim.

## Preserved positive evidence

The V1 14-case matrix remains useful construction evidence: abrupt zero exit without a response, nonzero exit, signal termination, timeout, malformed/duplicate/extra response material, wrong operation identity, self-declared PASS, oracle mismatch, stdout overflow, and valid-response-then-nonzero all failed closed as exercised.

IAR8-H1 does not erase those observations. It adds a missing inherited-writer completeness attack.

## Required next state

Repair H1 first. Do not migrate the 77-test universe or claim supervisor-core exhaustion until the inherited-pipe regressions pass and another adversarial pass is performed.

`IMPLEMENTATION_QUALIFICATION=NOT_CLAIMED`

`RUNTIME_QUALIFICATION=NOT_CLAIMED`

`SCIENTIFIC_AUTHORITY=NOT_CLAIMED`

`AUTHORITY_EFFECT=NONE_EVIDENCE_ONLY`
