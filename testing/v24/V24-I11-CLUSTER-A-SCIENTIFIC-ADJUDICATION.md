# V24 I11 Cluster A Scientific Adjudication

Status: **RED — WDPC-454 FAIL_CODE_DEFECT**

Execution run: `34748563045`
Execution SHA: `86f85ac17ea88e7cb95d7271e5e9cea6d3bc84c4`
Exact pre-scientific frontier: `e9a02e722edcd5e16b82abeeb37f7ab68c9295bf`
Frozen I10 subject: `9836dc3ff233cca582f485434fc1c6494cf7eb05`
V8 plan: reviewed and repository-bound.

## Results

PASS: WDPC-433, WDPC-446, WDPC-447, WDPC-453, WDPC-463 (mechanism-only positive), WDPC-481, WDPC-482, WDPC-490.

FAIL_CODE_DEFECT: WDPC-454.

NOT_EXECUTED_EXTERNAL_EVIDENCE_REQUIRED: WDPC-491.

BLOCKED_BY_I1_SEMANTIC_QUALIFICATION: WDPC-469, WDPC-495.

## WDPC-454 defect

The exact candidate `normative_control_catalog.py` accepts an authoritative artifact after an additional uncatalogued Level-2 normative-looking permission clause is inserted, provided the artifact blob binding on the already-declared descriptors is updated. The candidate returned:

- `state = NORMATIVE_CONTROL_CATALOG_QUALIFIED`
- `qualified = true`
- `problems = []`

The expected endpoint was `NORMATIVE_CONTROL_CATALOG_INCOMPLETE`.

Root cause exposed by the falsification fixture: `validate_normative_catalog()` verifies the caller-declared `required_clause_locators` but does not independently reject an additional normative-looking/Level-2 clause that is absent from that locator inventory. The manifest can therefore define away the omitted clause.

This RED is preserved and is not repaired during the falsification sweep. Same-mechanism positive authority claims remain non-authoritative; WDPC-469/495 were already blocked by I1 semantic qualification.

## Repository-operation note

Before scientific execution, accidental non-scientific commit `3671d085c80435841426972cb66b0f024a829a75` was created on the pre-execution harness branch. Scientific execution did **not** use that drifted head; the scientific branch was created directly from exact frontier `e9a02e722edcd5e16b82abeeb37f7ab68c9295bf`.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
