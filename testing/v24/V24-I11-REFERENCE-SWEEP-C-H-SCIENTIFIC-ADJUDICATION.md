# V24 I11 Reference Sweep C–H Scientific Adjudication

Status: **RED — SYSTEMIC GOVERNED-ENDPOINT INTEGRATION DEFECT FAMILY**

Execution run: `34749374558`
Execution SHA: `3f925c2ad69f4be722de00ddd544aea07c4a08e4`
Exact pre-scientific frontier: `e9a02e722edcd5e16b82abeeb37f7ab68c9295bf`
Frozen I10 subject: `9836dc3ff233cca582f485434fc1c6494cf7eb05`
Frozen I10 tree: `d68cbccdceebad88715c8b37ddfcd524fc16ce8a`
Reviewed plan: `V8_REVIEWED`
Environment: Python `3.12.7`, `PYTHONHASHSEED=0`, UTC, frozen logical clock.

## Scientific result

Executed reference-negative cases: **25**

`FAIL_CODE_DEFECT`: WDPC-431, 432, 434, 435, 436, 437, 438, 439, 440, 442, 445, 451, 452, 455, 456, 457, 471, 473, 475, 476, 479, 483, 499, 501, 502.

PASS: **none**.

Result ledger head:
`98d964b7984edb5fa763e547a6ec180acc5cda3adb4ebfac93928d3e15e405fb`

## Preserved non-executions

External/manual evidence required and not executed: WDPC-443, 449, 458, 460, 466, 467, 468, 472, 474, 477, 484, 485, 486, 489, 494, 497, 498, 500, 503, 504, 505, 506.

Positive/reference controls blocked by failed or unresolved same-mechanism negatives: WDPC-461, 462, 464, 465, 470.

WDPC-469 and WDPC-495 remain blocked by I1 semantic qualification outside this sweep.

## Root-cause family

V8 requires an exact implementation-emitted governed endpoint and forbids translation/normalization of internal diagnostics into the expected endpoint.

The frozen candidate instead returned coarse construction/apply states such as `EFFECTIVE_CONTROL_INCOMPLETE`, `EFFECTIVE_CONTROL_CONSTRUCTION_VALID`, `I6_CONSTRUCTION_INCOMPLETE`, `AGGREGATE_BUDGET_INCOMPLETE`, `AGGREGATE_BUDGET_CONSTRUCTION_VALID`, `GENERATION_MIGRATION_INCOMPLETE`, `COMPLETENESS_BOOTSTRAP_INCOMPLETE`, `COMPLETENESS_BOOTSTRAP_CONSTRUCTION_VALID`, and `V24_APPLY_BLOCKED`.

The diagnostics often identify the injected fault, but the governed result surface does not emit the exact V8 endpoint. These 25 REDs are therefore one systemic defect family:

`GOVERNED_ENDPOINT_PROJECTION_INCOMPLETE_ACROSS_V24_VALIDATORS`

with module-specific manifestations in effective-control, completeness/bootstrap, admission/application/witness, aggregate-budget, generation/migration, and apply-time validation.

This adjudication does not weaken V8 by accepting coarse construction states as endpoint substitutes. It preserves the RED history.

## Relationship to Cluster A RED

WDPC-454 remains a separate substantive normative-catalog completeness defect: an uncatalogued normative-looking clause can be defined away by the caller-declared locator inventory.

No repair is made during this falsification sweep.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
