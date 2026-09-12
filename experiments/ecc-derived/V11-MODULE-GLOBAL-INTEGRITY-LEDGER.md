# ECC-Derived V11 Module-Global Integrity Ledger

Status: `V11_BOUNDED_MODULE_GLOBAL_GREEN_PENDING_EXTERNAL_REREVIEW`

Authority effect: `NONE_EVIDENCE_ONLY`

No requirement is adopted, promoted, released, frozen, or granted authority by this ledger.

## Parent

- V10 authoritative candidate: `63617dd1f01f0063b5534de128d5afce17f169be`
- V10 ledger-head CI: `183/183 PASS`
- external clean engineering re-review evidence commit: `76d8006f912683e332338f8f04a5aa456d320171`
- external review class: `AI_GENERATED_ENGINEERING_FEEDBACK_ONLY`
- external review disposition: `CHANGES_REQUIRED_BEFORE_IMPACT_ADJUDICATION`
- manual-review threshold contribution: `0`

The V10 history remains immutable. V11 addresses the externally identified ordinary-module monkeypatch false-green boundary.

## V11 hypothesis

The candidate-authority verifier must not treat unchanged top-level `__code__` as sufficient integrity when the checked functions still consult mutable module-global helper functions or data.

V11 requires candidate authority to fail closed when ordinary module access mutates:

1. the strict helper path used beneath a checked top-level function;
2. the reference evidence store used beneath the unchanged lookup function;
3. capability classification globals used by the strict role evaluator;
4. checked dependency function objects that reuse the original `__code__` while changing globals/default environment; or
5. public module-global coverage metadata that should not itself control legitimate authority.

Legitimate EXP-ECC-1 through EXP-ECC-5 candidate paths must remain positive, and the public diagnostic verifier must remain positive when the runtime is untampered.

This remains a bounded ordinary-module monkeypatch experiment. It does not claim resistance to concurrent mutation between verification and evaluation, reflective closure extraction, mutation of closure-held/captured objects themselves, interpreter/native-memory compromise, repository/code-replacement authority, live platform attestation, an independent production trust root, or durable signed cross-process provenance.

## Frozen assertions

- V11 assertion commit: `d79df1078cdaae6048e1ca636406935c26316616`
- V11 runner commit: `fe9d29372b3454870a0fac94140f9af079dc7764`
- V11 workflow-enabled pre-repair SHA: `9febf942842bd089a0d2c68c3d670d135b2377f0`

The V11 assertion file was frozen before mechanism repair and was not modified to obtain GREEN.

## RED-001 — clean pre-repair RED

- exact candidate: `9febf942842bd089a0d2c68c3d670d135b2377f0`
- workflow run: `34697338898`
- workflow job: `103562973730`
- result: `190 tests; 5 failures; 0 errors`
- retained V1-V10 non-superseded tests: `PASS`
- V11 positive controls: `PASS`

Observed failures:

1. `STRICT_HELPER_PLUS_REFERENCE_STORE_MUTATION_CAN_MINT`
2. `REFERENCE_STORE_MUTATION_ALONE_CAN_MINT`
3. `ALLOWED_CAPABILITY_GLOBAL_MUTATION_CAN_PROMOTE_UNKNOWN_CAPABILITY`
4. `PUBLIC_COVERS_GLOBAL_CONTROLS_LEGITIMATE_CANDIDATE_AUTHORITY`
5. `SAME_CODE_NEW_FUNCTION_GLOBALS_CAN_MINT`

## Root-cause classification

`GOVERNANCE_MECHANISM_DEFECT_MODULE_GLOBAL_INTEGRITY_INCOMPLETE`

V10 verified file identity, module identity, selected top-level `__code__` hashes, JSON/marshal/path primitives, and process-local result provenance, but candidate-authoritative strict/reference functions still resolved mutable module-global helpers/data at runtime. The verifier did not bind those subordinate globals, and `_COVERS` remained a replaceable public module-global input to the verifier itself.

## Deterministic repair

- repair generator commit: `c98e233ac3650f4990e23a93610fa8d6321bbb9b`
- repair workflow-enabling commit: `af3405eb55d9f1aaf5bb219dc8d954ad60f0e81c`
- repair workflow run: `34697622479`
- mechanism repair commit: `a85a85e471b99b2800dd958896f1ab620ab6792f`
- candidate boundary SHA-256: `fbbcdb89b0e7e547c749a226f0f7fd359dd513137b2480007c8b69bafa00b77d`
- V11 assertion modification during repair: `NONE`

The repair:

- captures the exact checked strict/reference entrypoint function objects at verifier initialization;
- requires those exact objects to remain installed, so a new function object reusing the original `__code__` cannot become candidate-authoritative;
- recursively snapshots module-global dependencies actually referenced by the checked entrypoints and helper functions;
- compares mutable dictionaries, sets, lists, tuples and scalar values structurally at each runtime verification;
- binds helper-function identity, code, defaults and keyword defaults;
- therefore detects mutation of `_strict`, `_REFERENCE`, `_ALLOWED_CAP_CLASSES`, `_CAPABILITY_RANK`, and equivalent recursively referenced globals before positive candidate sealing;
- captures the expected experiment coverage set inside the verifier closure so later mutation of public `_COVERS` cannot disable legitimate authority or redefine the manifest coverage contract; and
- retains all V6-V10 provenance, verifier-substitution, primitive-integrity, and path-integrity controls.

Manifest posture now includes:

- `record_type = ECC_GOVERNANCE_V11_MODULE_GLOBAL_INTEGRITY_MANIFEST`
- `module_global_dependency_policy = RECURSIVE_REFERENCED_GLOBALS_BOUND_AT_INITIALIZATION`
- `checked_entrypoint_identity_policy = EXACT_FUNCTION_OBJECT_IDENTITY_REQUIRED`
- `module_global_mutation_fail_closed = true`
- `same_code_new_function_object_fail_closed = true`
- `public_covers_global_controls_candidate_authority = false`

## GREEN-002 — repaired candidate falsification

- exact tested SHA: `5884af027191231c4625f8c913b2a4b1ea2e00ab`
- mechanism parent: `a85a85e471b99b2800dd958896f1ab620ab6792f`
- workflow run: `34697656020`
- workflow job: `103563800594`
- result: `190/190 PASS`
- retained V1-V10 non-superseded tests: `PASS`
- V11 positive controls: `PASS`
- all five V11 pre-repair failure classes: `PASS`
- historical supersession records: still explicit

The same frozen V11 assertions that produced RED-001 now pass without modification.

## Bounded interpretation

V11 supports only this bounded claim: under the current reference process and ordinary-module monkeypatch threat model exercised by the frozen V11 suite, candidate authority fails closed when checked entrypoint objects, recursively referenced module-global helpers/data, capability-classification globals, or the reference evidence store are replaced or mutated before verification; public `_COVERS` mutation does not control candidate authority.

V11 does **not** establish resistance to:

- concurrent/TOCTOU mutation between a successful verification and subsequent strict/reference execution;
- reflective extraction or mutation of closure-held captured objects;
- mutation of lower-level interpreter/runtime primitives not already captured by V9/V10;
- interpreter/native-memory compromise;
- repository/code-replacement authority;
- live platform attestation;
- independent production trust-root separation; or
- durable signed cross-process provenance.

Those remain explicit nonclaims pending separate design or integration evidence.

## Current disposition

- V11 reference mechanism: `BOUNDED_GREEN_PENDING_CLEAN_EXTERNAL_ENGINEERING_REREVIEW`
- EXP-ECC-1..5: `REFERENCE_MECHANISM_HARDENED_BUT_LIVE_INTEGRATION_EVIDENCE_STILL_REQUIRED`
- EXP-ECC-6..7: `DEFER_PENDING_INTEGRATION_EVIDENCE`
- freeze: `NOT_FROZEN`
- manual-review threshold contribution from AI reviews: `0`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
