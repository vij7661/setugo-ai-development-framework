# V24-I11-V6-R15 — Pre-Review Falsification Closure 001

Status: **FALSIFICATION BOUNDARY CLOSED FOR MANUAL SUCCESSOR REVIEW / NO AUTHORITY EFFECT**

Authority effect: `NONE_EVIDENCE_ONLY`

## Frozen candidate

- commit: `2e875bb29be48d39c9be6f3525d4f4610869848c`
- tree: `d2c9c0c85564808941fdb54cfbbd53f51f5397ee`
- predecessor R14: `REJECTED`
- scientific execution: `CLOSED_PENDING_SUCCESSOR_REVIEW`
- runtime qualification: `NOT_CLAIMED`

## Full construction boundary

Run `34776147253` completed `SUCCESS` and bound:

- 190-file external exact-file pinset;
- exact R15 native observer source and compiled binary;
- exact CPython program/interpreter/environment;
- historical R13/native-boundary attack rejection;
- seven mandatory R15 path/memory attacks;
- six external trusted-oracle records;
- candidate structural validation with `qualified = false`;
- native-binary substitution rejection;
- unchanged post-execution sandbox exactness.

Full construction evidence is recorded in `V24-I11-V6-R15-FULL-NATIVE-CONSTRUCTION-EVIDENCE.md`.

## Preserved falsification history

### R15 RED 001

Run `34775801974` — `PROBE_OBSERVABILITY_DEFECT_BEFORE_INTENDED_ENDPOINT_PROOF`.

No false green was established. Exact R15 native diagnostics were added without weakening enforcement.

### R15 RED 002

Run `34776044993` — `FULL_CONSTRUCTION_WORKFLOW_ARGUMENT_MISMATCH_BEFORE_ORACLE_ENDPOINT`.

No oracle scenario executed. Only unsupported workflow CLI options were removed; candidate/native enforcement was unchanged.

### R15 RED 003

Run `34776271310` — `SYMLINK_ATTACK_HARNESS_PATH_DEFECT_BEFORE_REALPATH_ENDPOINT` for three symlink cases.

Five other alternate-representation attacks conclusively reached and were rejected at the intended endpoint:

- double-slash `/proc` spelling;
- dot-dot `/proc` spelling;
- `pathlib.Path`;
- custom `os.PathLike` returning bytes;
- integer file-descriptor representation fail-closed.

The three original symlink probes used relative paths from the wrong process working directory and therefore did not reach the symlink/realpath endpoint. This is preserved rather than inferred PASS.

Raw artifact binding:
- artifact ID `10324245438`
- outer SHA-256 `5379104c453a61891c3419df777f7d548d7b3816dfafb96cec047c1520fcab9a`
- raw inner evidence SHA-256 `b0bc2504a190abab0d2b492ec229c229d9af5c527f63e09a6aca221563dfea6a`

### Corrected symlink falsification V2

Run `34776332464` — `SUCCESS`.

All three corrected attacks derived absolute alias paths from the executing candidate module's `__file__`, thereby reaching the actual symlink inside the attack sandbox:

1. Unicode file symlink -> `/proc/self/mem`;
2. bytes file symlink -> `/proc/self/mem`;
3. directory symlink -> `/proc`, then `/self/maps`.

For all three:
- native return code non-zero;
- `R15_AUDIT_FORBIDDEN_NORMALIZED_PATH` observed;
- authenticated native observation not emitted;
- `false_green_reproduced = false`.

Artifact:
- ID `10323866558`
- outer SHA-256 `2218f9ca487d285262c98864e4b555db182dc0047426b954e6d3093bd2fb544c`
- raw evidence SHA-256 `9b20518a57de68178efb1936b726b2d78d9f5822065f2c5bf26dff3f662489bf`
- independent post-download recomputation: `VERIFIED`.

## Falsification disposition

No currently executed R15 construction/falsification probe reproduces an authority-bearing false green for the frozen candidate.

This does **not** mean R15 is correct, complete, qualified, or ready for scientific execution. It means only that the current pre-review falsification set is closed enough to submit the exact frozen candidate/evidence to a fresh independent manual successor review.

The manual reviewer must actively search for bypasses outside the executed attack set and must not infer safety merely from green construction evidence.

## State transition

- `R15_CONSTRUCTION = PASS_EVIDENCE_ONLY`
- `R15_PRE_REVIEW_FALSIFICATION = CLOSED_NO_KNOWN_REPRODUCED_FALSE_GREEN`
- `MANUAL_SUCCESSOR_REVIEW = REQUIRED_NEXT`
- `SCIENTIFIC_EXECUTION = CLOSED_PENDING_SUCCESSOR_REVIEW`
- `RUNTIME_QUALIFICATION = NOT_CLAIMED`
- `AUTOMATED_EXTERNAL_REVIEWER_API_CALLS = PROHIBITED`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
