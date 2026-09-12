# ECC-Derived V11 Module-Global Integrity Ledger

Status: `V11_CLEAN_PRE_REPAIR_RED_PRESERVED`

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

The V11 assertion file was frozen before mechanism repair.

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

V10 verifies file identity, module identity, selected top-level `__code__` hashes, JSON/marshal/path primitives, and process-local result provenance, but candidate-authoritative strict/reference functions still resolve mutable module-global helpers/data at runtime. The verifier does not bind those subordinate globals, and `_COVERS` remains a replaceable public module-global input to the verifier itself.

## Current disposition

`V11_CLEAN_PRE_REPAIR_RED_PRESERVED`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
