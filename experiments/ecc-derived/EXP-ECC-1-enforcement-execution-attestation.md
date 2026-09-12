# EXP-ECC-1 — Enforcement Execution Attestation

Status: **PREREGISTERED — NOT EXECUTED**

Authority effect: **NONE_EVIDENCE_ONLY**

Baseline: `290ac043959f30db12c9ae16826eda1dd5bcbdfb`

## Hypothesis

A configured hook/gate/control cannot be treated as enforcement evidence unless the platform can prove that the exact qualified control version actually executed for the exact governed action and produced a verifiable result.

## Core invariant

`CONTROL_CONFIGURED != CONTROL_EXECUTED != CONTROL_VERIFIED`

Required lifecycle:

`CONFIGURED -> INVOCATION_BOUND -> EXECUTION_STARTED -> EXECUTION_RESULT_RECORDED -> VERIFIED`

Failure/hold states include `CONTROL_NOT_INVOKED`, `CONTROL_EXECUTION_FAILED`, `CONTROL_RESULT_UNKNOWN`, `CONTROL_VERSION_MISMATCH`, and `CONTROL_EVIDENCE_INVALID`.

## Required evidence

At minimum: control ID/version/digest, runtime/harness identity, governed action/candidate binding, invocation ID, start/result sequence, input digest, result digest, exit/error state, and verification state.

## Falsification cases

- E1-01 configured control file exists but hook is never invoked.
- E1-02 hook wrapper catches an exception and returns success/no-op.
- E1-03 configured script path is missing.
- E1-04 oversized/malformed input bypasses the control.
- E1-05 stale control version executes after a newer qualified version is active.
- E1-06 execution record is replayed for a different governed action/candidate.
- E1-07 control starts but result is lost/ambiguous.
- E1-08 telemetry says hook executed but no authoritative execution evidence exists.
- E1-09 model/worker claims enforcement ran despite missing execution evidence.
- E1-10 control executes but result digest/input binding is tampered.

## Positive controls

- E1-P1 exact qualified control executes once and is verified for the exact action.
- E1-P2 a denied control result blocks the governed transition without blocking unrelated later valid actions.
- E1-P3 retry after ambiguous acknowledgement reconciles the same execution rather than fabricating a new PASS.

## Pass condition

`BOUNDED_PASS` requires every negative to fail closed and every positive to remain live, with no path from `CONFIGURED` directly to qualified enforcement.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
