# V16 Slice 2 Internal Adversarial Review 009

Review target: External Assertion Supervisor V2, source blob `a0f2c573eca92ade798550cd7fa0515bd0e56e0c`, construction run `34999060722`.

Review class: **INTERNAL_ADVERSARIAL_RECORD / NON-INDEPENDENT**

`AUTHORITY_EFFECT=NONE_EVIDENCE_ONLY`

## Disposition

`CHANGES_REQUIRED`

`INTERNAL_ADVERSARIAL_REVIEW_EXHAUSTED=false`

`V16_SLICE2_FREEZE_ALLOWED=false`

## Repaired predecessor finding

### IAR8-H1 — inherited protocol writer completion

Status: **REPAIRED FOR THE EXERCISED V2 PROTOCOL BOUNDARY**.

V2 no longer treats exit of the original worker PID as protocol completion. It waits for EOF on inherited stdout/stderr writers or the global deadline, enforces aggregate stream limits, and fails closed if a descendant holds a protocol pipe open. Run `34999060722` demonstrated the RED-010 delayed-extra-output and held-open-pipe regressions fail closed.

This closure is construction-level only and does not imply a complete arbitrary-code sandbox.

## New High finding

### IAR9-H1 — detached descendant can survive a supervisor PASS and act after the receipt

Affected boundary: `review_safe_evidence_v16_execution_supervisor._run_worker_bounded` and the V2 worker isolation model.

V2 protects the protocol stream, but its process-containment mechanism is only `start_new_session=True` plus process-group kill on timeout/overflow. A worker-controlled descendant can potentially detach into a different session/process group, close inherited protocol descriptors, allow the original worker to return a valid oracle-matching response and exit 0, and then continue executing after the supervisor has observed EOF and issued `SUPERVISOR_ORACLE_PASS_NONAUTHORITATIVE`.

Concrete suspected false-green path:

1. worker forks a descendant;
2. descendant calls `setsid()` (or an equivalent detach path) and closes inherited stdout/stderr so V2 can observe protocol EOF;
3. original worker emits the correct bounded result and exits 0;
4. supervisor sees complete protocol EOF, correct operation ID, correct result, and main-worker rc=0, then writes PASS;
5. detached descendant remains alive and performs a delayed side effect after the receipt.

Why High:

For a harness evaluating arbitrary or candidate-controlled code, a trusted completion receipt cannot mean the evaluated execution boundary is complete if an evaluated descendant remains active and able to mutate state after receipt issuance. This is distinct from result correctness: the result may be correct while execution containment is false-green.

### Required falsification

Before choosing a repair, mechanically test the exact shape with a bounded fixture:

- worker forks;
- descendant detaches, closes protocol FDs, waits;
- main worker emits a valid oracle-matching result and exits 0;
- supervisor V2 is allowed to finish;
- probe checks whether the detached descendant can create a delayed marker after supervisor PASS.

If reproduced, preserve as the next CODE_DEFECT RED. If not reproduced, preserve the negative result and identify the mechanism that prevented escape.

### Required repair if reproduced

Do not rely only on process groups. The supervisor must own an OS-enforced or kernel-supported descendant-accounting boundary that remains authoritative across fork/clone, `setsid`, and `exec*`.

A Linux subreaper-based construction repair is admissible only if it is mechanically shown to:

- make orphaned worker descendants observable/reparented to the trusted supervisor;
- detect any live descendant before PASS;
- kill/reap escaped descendants before final receipt;
- fail closed if descendant cleanup cannot be proven complete;
- handle repeated/double-fork descendants and process replacement;
- preserve the V2 protocol EOF/size/timeout guarantees.

If subreaper semantics cannot provide a race-resistant bound for the tested threat model, move to a stronger PID-namespace/cgroup/sandbox mechanism rather than weakening the claim.

## Medium/open governance finding

### IAR9-M1 — supervisor oracle and worker provenance are caller-configured, not yet governed-plan bound

`supervise(config)` accepts `expected_result`, `worker_command`, `worker_cwd`, limits, and request data from its caller. The current receipt is explicitly `NONAUTHORITATIVE`, so this is not presently a promotion bypass. Before supervised cases become load-bearing, those fields must be derived from an exact governed supervised-test-plan object rather than accepted as arbitrary caller truth.

Required future binding includes at minimum plan ID/digest, requirement ID, operation ID, request digest, oracle digest or independently defined predicate/version, worker artifact digest, supervisor profile/source digest, limits, candidate/generation context, and currentness.

## Migration finding

### IAR9-M2 — historical 77-test suite has not been migrated to the external-supervisor oracle boundary

The historical 77 in-process tests remain behavioral construction evidence. They cannot be relabeled as externally supervised simply because the supervisor core exists. Every load-bearing Slice 2 requirement must eventually map to a supervised case or a governed explicit exception with preserved rationale.

## Receipt authenticity boundary

The V2 `receipt_digest` is a SHA-256 integrity/content digest only. It does not by itself authenticate issuer provenance or confer authority. Any later authority-bearing receipt use must bind to the V16 authenticated trust/role/generation machinery rather than treating the self-contained digest as a signature.

## Required next state

Run the detached-descendant falsification before advancing to test-plan binding or migration. Keep overall exhaustion and freeze blocked regardless of the probe result.

`IMPLEMENTATION_QUALIFICATION=NOT_CLAIMED`

`RUNTIME_QUALIFICATION=NOT_CLAIMED`

`SCIENTIFIC_AUTHORITY=NOT_CLAIMED`

`AUTHORITY_EFFECT=NONE_EVIDENCE_ONLY`
