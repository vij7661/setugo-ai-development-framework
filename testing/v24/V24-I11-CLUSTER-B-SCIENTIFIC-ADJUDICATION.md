# V24 I11 Cluster B Scientific Adjudication

Status: **RED — 10/10 EXECUTED CASES FAIL_CODE_DEFECT**

Execution run: `34749496950`
Execution SHA: `0c4857f35c8d6c3b3e3c96b857285284584ff5a0`
Exact pre-scientific frontier: `e9a02e722edcd5e16b82abeeb37f7ab68c9295bf`
Frozen I10 subject: `9836dc3ff233cca582f485434fc1c6494cf7eb05`
Frozen I10 tree: `d68cbccdceebad88715c8b37ddfcd524fc16ce8a`
Reviewed plan: `V8_REVIEWED`
Environment: Python `3.12.7`, `PYTHONHASHSEED=0`, UTC, frozen logical clock.

## Results

Executed: WDPC-444, WDPC-448, WDPC-450, WDPC-459, WDPC-487, WDPC-488, WDPC-492, WDPC-441, WDPC-478, WDPC-480.

`FAIL_CODE_DEFECT`: all 10 executed cases.

PASS: none.

Blocked positives:
- WDPC-493 — `BLOCKED_BY_PRIOR_LOAD_BEARING_FAILURE`
- WDPC-496 — `BLOCKED_BY_PRIOR_LOAD_BEARING_FAILURE`

Result ledger head:
`20d053368060db8885ed9cac3a2b650a02972865c0630b0019c1c250eefa4cf7`

Artifact ID: `10314918690`
Artifact zip SHA-256: `43a908e9bafef0ba68af75eedcb3a31dbb644ec8876e651775df8d962685693a`

## Root-cause relationship

Nine of the ten failures clearly exhibit the already-observed systemic family `GOVERNED_ENDPOINT_PROJECTION_INCOMPLETE_ACROSS_V24_VALIDATORS`: the frozen candidate returns coarse states such as `AUTHORITY_UNIVERSE_INCOMPLETE`, `AUTHORITY_UNIVERSE_CONSTRUCTION_VALID`, `COMPLETENESS_BOOTSTRAP_CONSTRUCTION_VALID`, or `V24_APPLY_BLOCKED` rather than the exact implementation-emitted V8 governed endpoint. Meaningful internal diagnostics cannot be normalized into the expected endpoint under the reviewed contract.

WDPC-478 is preserved separately for follow-up analysis because its fixture expected `AUTHORITY_ADMISSION_REQUIRED`, but the candidate returned `V24_APPLY_READY`, `allowed=true`, with no candidate problems. That could represent a stronger functional/fixture-boundary defect in addition to endpoint projection. It is not reclassified here without further evidence.

## Infrastructure history

Earlier Cluster B run `34748667569` ended `startup_failure` with zero jobs. Runs `34748809624` and `34749370756` remained queued with zero jobs. Those events are infrastructure evidence only and are not scientific results.

The alternate workflow identity was used solely to obtain a runner. It remained a descendant of the exact pre-scientific frontier and retained the frozen Python 3.12.7/runtime and V8/I10 bindings.

No implementation repair is made during the falsification sweep.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
