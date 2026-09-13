# V24 I11 V6 R11 — Manual Review Adjudication 003 / R12 Scope Freeze

Status: **R11 REJECTED / R12 REQUIRED / R12 SCOPE FROZEN**

Authority effect: `NONE_EVIDENCE_ONLY`

## 1. Basis

This adjudication follows the earlier R11 manual-review adjudication and incorporates the later independently supplied clean review artifact preserved verbatim in the repository.

The later review reports:
- `CONTENT_BINDING = CONSISTENT`
- `CRYPTOGRAPHIC_RECOMPUTATION = NOT_PERFORMED`
- overall `NEEDS_REVISION`
- R11-A `NOT SATISFIED`
- R11-B `SATISFIED` with respect to exact-file pinning
- H/I/J/K/L/M/N/O/P assessed satisfied within the reviewed package scope
- Q not satisfied because the trusted runner executes candidate-controlled tests in the same mutable Python process as trusted result accounting.

The lack of cryptographic recomputation in the later review does not invalidate the prior independently verified package/hash evidence. It also does not grant any new authority. This adjudication uses the later review only as independent technical/systemic review evidence.

## 2. R11 disposition

R11 remains rejected.

Scientific WDPC execution remains closed. Runtime qualification is not claimed. Construction/static-verification PASS results remain evidence only.

## 3. Frozen R12 required repairs

### R12-A — actual interpreter startup state must be verified by trusted authority

The trusted execution path must fail closed from the *actual running interpreter state*, not from pinset-declared booleans alone.

Minimum required properties:
- verify actual isolation/no-site/environment-ignore posture before candidate-controlled bytes execute;
- do not accept a declared `interpreter_contract` as proof of runtime state;
- reject missing or incorrect isolation before any qualification-contributing result can be accepted;
- bind the observed interpreter/runtime identity into the external execution evidence.

### R12-B — candidate execution must be outside trusted result-accounting process state

Candidate-controlled modules/tests must not execute in the same mutable Python process that determines qualification contribution.

Minimum required properties:
- trusted parent/orchestrator must never import candidate modules;
- candidate execution occurs in a separate isolated child process boundary;
- trusted parent derives accounting from independently validated child-process evidence;
- candidate output, exit code, JSON, unittest objects, stdout/stderr, or self-reported PASS must never directly self-authorize qualification;
- malicious child behavior including monkeypatching `unittest`, replacing result classes/runners, mutating `sys.stdout`, abnormal exit, truncation, malformed output, duplicate output, replayed output, or forged success must fail closed unless independently corroborated by the trusted protocol.

A same-process repair that merely snapshots/restores selected `unittest` attributes is insufficient.

### R12-C — mandatory adversarial checks require executed evidence binding

Mandatory adversarial-check completeness must not be satisfiable by check-name strings.

Each required check must bind to an executed evidence record containing, at minimum:
- canonical check identity;
- exact candidate commit/tree;
- exact execution environment/interpreter contract identity;
- terminal execution status and result;
- evidence-record digest;
- trusted runner/orchestrator identity;
- independent witness/authority identity where required;
- freshness/current-round binding where required.

Missing, stale, mismatched, unexecuted, duplicate, replayed, or name-only evidence fails closed.

## 4. Explicit R12 adversarial targets

The following are mandatory construction/falsification targets for the successor and cannot be silently omitted:

1. runner invoked without required isolation flags;
2. candidate test monkeypatches `unittest.TextTestRunner`;
3. candidate test monkeypatches `unittest.TestResult.wasSuccessful`;
4. candidate code mutates stdout/stderr/result serialization;
5. child exits 0 without valid evidence;
6. child emits forged PASS payload;
7. child emits duplicate/replayed evidence record;
8. child terminates abruptly before evidence finalization;
9. name-only mandatory adversarial-check manifest;
10. stale/mismatched check evidence bound to another candidate/tree/environment;
11. host/target Python stdlib-name-set mismatch;
12. anti-false-green AST scanner evasion by casing, Unicode confusable, or runtime string construction.

The last two are preserved open risks until demonstrated closed; they are not assumed defects merely from assertion.

## 5. Seven-file prior-review gap

The earlier reviewer explicitly reported not fully reading seven support/runtime files. The later independent full-package review supplied H–Q conclusions and found no additional blocker beyond runner/process-boundary and interpreter-isolation concerns.

This is sufficient to remove the **implementation hold**, but not to erase the earlier scope caveat. Therefore R12 construction must include regression/adversarial coverage ensuring these seven files cannot weaken R12-A/B/C or create caller-label/boolean/name/count/digest/status false-green paths:

- `v24_admission_application_witness.py`
- `v24_completeness_bootstrap.py`
- `v24_aggregate_budget.py`
- `v24_generation_migration.py`
- `v24_review_proof_audit.py`
- `v24_authority_surface_inventory.py`
- `validate_runtime.py`

Any newly demonstrated blocker in those files becomes part of R12 before freeze; no mid-sweep weakening is permitted.

## 6. Non-blocking observations carried forward

- real-world currentness/independence remains externally sourced and necessary-but-not-sufficient;
- branch isolation is an external repository/authority property and must be proven by repository evidence, not inferred from package prose;
- exact-file pinning remains a valid R11 contribution but does not solve trusted-process isolation;
- cryptographic recomputation not performed by the later reviewer is recorded as such and must not be upgraded to `VERIFIED` for that review artifact.

## 7. State transition

- `R11_ACCEPTED = false`
- `R12_REQUIRED = true`
- `R12_SCOPE_FROZEN = true`
- `R12_IMPLEMENTATION_MAY_BEGIN = true`
- `SCIENTIFIC_EXECUTION_OPEN = false`
- `RUNTIME_QUALIFICATION_CLAIMED = false`

R12 must be implemented as a successor. Do not patch the frozen R11 candidate in place.

Historical RED, package, review, and adjudication evidence remains append-only.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
