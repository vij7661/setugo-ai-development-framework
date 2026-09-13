# V24-I11-V6-R13 — Falsification Adjudication 001

Status: **R13 REJECTED / R14 REQUIRED**

Authority effect: `NONE_EVIDENCE_ONLY`

## 1. Bound R13 candidate and falsification

R13 candidate:
- commit `94728f0bbf0564e5d9c2e4f8b11e600dffabee99`
- tree `d15efec0a63e53866592e0961504495331d89025`

R13 was created after the R12 same-process frame-introspection false green and attempted to move PASS/FAIL derivation into an external trusted oracle while treating candidate execution as untrusted observation only.

The corrected tailored-frame falsification is preserved in:
- `review/v24/V24-I11-V6-R13-TAILORED-FRAME-FALSIFICATION-RESULT.json`
- `review/v24/V24-I11-V6-R13-TAILORED-FRAME-ORACLE-EVIDENCE.json`

Observed terminal result:
- `classification = FAIL_CODE_DEFECT`
- `false_green_reproduced = true`
- `oracle_exit_code = 0`
- `oracle_record_count = 6`
- `all_oracle_records_pass = true`
- scientific execution remained closed
- runtime qualification remained unclaimed.

## 2. Accepted Critical defect — candidate can forge the observation protocol before intended function execution

**Accepted / Critical / `FAIL_CODE_DEFECT`.**

The R13 trusted oracle did not import candidate code itself, but it launched a Python observation process that imported candidate modules and trusted a JSON observation envelope emitted by that same candidate-compromised process.

The syntactically valid attack inserted candidate code after the module's `from __future__ import annotations` line. At import time the malicious code walked Python frames using `sys._getframe()`, located the observer's request object, derived the expected observation for each requested check, wrote a syntactically valid `R13_OBSERVATION=...` payload, and terminated with exit code 0 before the intended production function executed.

The external oracle then evaluated those forged observations and produced six PASS evidence records. This proves that randomized oracle challenges do not establish function execution when the challenge/request and trusted observation protocol are visible inside the candidate-controlled Python interpreter.

## 3. Why R13 cannot be patched in place

The defect is structural, not a missing canary or string check:

- any Python observation shim that imports candidate Python shares Python frames/modules/protocol state with candidate code;
- candidate code can inspect or mutate that shim and forge its observation envelope;
- adding another Python frame/canary check repeats the rejected R12/R13 trust shape.

R13 therefore cannot be repaired by another same-process Python observer patch.

## 4. Required R14 property

For qualification-contributing execution, R14 must establish a stronger observation boundary:

1. trusted PASS/FAIL oracle logic remains in a process/address space that never imports candidate Python;
2. the component that imports/calls candidate Python must not implement the authoritative assertion logic;
3. the observation channel itself must be produced by trusted code that candidate Python cannot replace through Python frame/module/global mutation;
4. direct candidate stdout/stderr, exit-zero, unittest result, Python JSON envelope, or candidate-generated PASS label is never authoritative;
5. early `os._exit(0)`, protocol injection, `sys._getframe()`/`inspect` mutation, `__main__` mutation, trace/profile hooks, and output-FD attacks must fail closed;
6. runtime-generated challenge material remains useful but cannot be the sole protection;
7. exact-file pinning and actual interpreter/runtime identity remain externally bound;
8. the R13 tailored-frame exploit becomes a mandatory regression attack.

A native or otherwise non-Python trusted observation primitive is acceptable if it captures the actual function return/exception outside candidate-mutable Python protocol logic and fails closed on abnormal termination or observation-channel tampering.

## 5. Supplemental internal hardening discovered after the historical R13 branch

A later manual R11 supplemental review exposed additional independent false-green paths in runtime validation, completeness/admission/migration/accounting, authority-surface derivation, and review-protocol promotion semantics.

Those repairs were constructed on branch:
`implementation/v24-i11-v6-r12-manual-review-remediation`

Construction boundary before continuity correction:
- commit `db6320550b71285325ba8dbfca9722e0b0812558`
- tree `eccda344a86e0e2325421cb1ac8f7ed2f03fbde5`
- run `34773655157`
- `30/30` review-protocol tests PASS
- `261/261` V24 tests PASS
- total `291/291` PASS

A later evidence-only commit recorded the run history:
`ed6cab142a360bb998b0cd4e21afd32429175c0f`

Because R12 and R13 had already been historically rejected, that branch **does not resurrect R12 and is not a new accepted successor generation**. Its code changes are classified:

`POST_REJECTION_SUPPLEMENTAL_CONSTRUCTION_INPUT_ONLY`

R14 must carry those accepted internal remediations forward while also replacing the rejected R13 observation boundary.

## 6. State transition

- `R12 = HISTORICALLY_REJECTED`
- `R13 = REJECTED`
- `R14_REQUIRED = true`
- `R14_MUST_INHERIT_SUPPLEMENTAL_INTERNAL_REMEDIATION = true`
- `R14_MUST_REPLACE_R13_PYTHON_OBSERVER_TRUST_BOUNDARY = true`
- `SCIENTIFIC_EXECUTION = CLOSED`
- `RUNTIME_QUALIFICATION = NOT_CLAIMED`
- automated external reviewer/provider API calls during TESTING/FALSIFICATION remain prohibited.

No earlier RED/PASS evidence is deleted or rewritten.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
