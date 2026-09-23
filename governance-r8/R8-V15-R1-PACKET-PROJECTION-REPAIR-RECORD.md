# R8 v15-r1 Internal Packet-Projection Repair Record

Status: **INTERNAL_NORMALIZATION_REPAIR — NON_AUTHORITATIVE**
Authority effect: **NONE**

Preserved first packaging attempt:
- branch: `packaging/r8-v15-review-bundle-2026-09-23`
- packet-projection check commit: `e6c34e1a46c5b8655c9029ee690799c1f958116b`
- result: FAIL

The first check reported:
1. raw current-status marker count = 2 because the literal marker also appeared inside the fenced ProjectionManifest JSON; this was a validator false positive because structural markers are recognized only as exact standalone lines outside fenced code;
2. predecessor-status literal `R8 v12 = NOT_IMPLEMENTED` survived inside X14-033. This exposed a genuine BSP context gap: the cross-mechanism adversarial corpus was test data, but the initial BSP-5 grammar did not assign that whole corpus an explicit semantic-test parser state.

Repair:
- add `MARKED_SEMANTIC_TEST_SECTION`;
- define exact paired standalone begin/end markers with matching stable ID;
- forbid nesting and malformed pairing;
- require the cross-mechanism corpus to use stable ID `cross-mechanism-adversarial-corpus`;
- classify predecessor/status literals inside that marked section as `SEMANTIC_TEST_LITERAL`;
- preserve ordinary predecessor status removal outside semantic-test contexts;
- update normalized NORM-041 and traceability.

This is a narrow projection-grammar repair. It does not change SRTT, authority, trust-root, resolver, state-seal, rotation, or external-effect semantics.

The failed first projection attempt remains preserved and is not rewritten to PASS.
