# ECC-Derived V12 Transitive Primitive Integrity Ledger

Status: `V12_CLEAN_PRE_REPAIR_RED_PRESERVED`

Authority effect: `NONE_EVIDENCE_ONLY`

No requirement is adopted, promoted, released, frozen, or granted authority by this ledger.

## Parent

- V11 exact candidate: `39d19dbf4d62b2861128f00e62a7325ff1039fa6`
- V11 exact ledger-head CI: `190/190 PASS`
- V11 AI clean re-review: `CHANGES_REQUIRED_BEFORE_IMPACT_ADJUDICATION`
- review evidence class: `AI_GENERATED_ENGINEERING_FEEDBACK_ONLY`
- manual-review threshold contribution: `0`
- EXP-ECC-1..4 reviewer disposition: `ADOPT_REQUIREMENT_CANDIDATE`
- EXP-ECC-5 reviewer disposition: `NARROW_REQUIREMENT_CANDIDATE`
- EXP-ECC-6..7 reviewer disposition: `DEFER_PENDING_INTEGRATION_EVIDENCE`
- freeze recommendation: `DO_NOT_FREEZE`

## V12 hypothesis

V12 tests whether candidate-authoritative EXP-ECC-5 config equivalence remains fail-closed when ordinary module access mutates transitive primitive attributes used beneath the strict digest helper, while preserving legitimate config positives.

The corrected V12 target requires:

1. mutation of `ecc_governance_strict.hashlib.sha256` must be detected before candidate authority can be sealed;
2. mutation of `ecc_governance_strict.json.dumps` must be detected before candidate authority can be sealed;
3. candidate-authoritative dependency integrity must bind those exact transitive callables, not merely the `hashlib`/`json` module-object identities;
4. the independent EXP-ECC-5 reference record must bind raw `permission_profile` and actual `argv` as semantic evidence in addition to digest fields;
5. the boundary config cross-check must compare those raw semantic fields; and
6. legitimate untampered EXP-ECC-5 config evidence must remain positive.

## Review-path narrowing

The external review's concrete sequence changed both `permission_profile` and `argv`. The first V12 run showed that the strict config evaluator already compares `permission_profile` directly, so broader permission drift is rejected independently of digest recomputation. The remaining false-green is narrower but real: keep permission unchanged, change actual `argv`, retain genuine digest fields, and mutate `hashlib.sha256` or `json.dumps` so strict digest recomputation falsely accepts the stale digests.

This narrowing is preserved as a fixture/review-path correction, not a rewrite of the external review.

## Assertions and RED history

- initial V12 assertion commit: `ead455cf0996076e0c838be29405282be4cd7311`
- runner commit: `9de842999393d948f9199c1b493a849efd358644`
- workflow-enabled SHA: `c80cdb4ff94229baea5836440a3efba7176c2417`

### RED-001

- exact SHA: `c80cdb4ff94229baea5836440a3efba7176c2417`
- run: `34699078195`
- job: `103567521590`
- result: `199 tests; 3 failures; 0 errors`
- classification: `RED_WITH_ATTACK_FIXTURE_NARROWING_REQUIRED`

The two initial mint-attempt tests passed for the wrong reason because they also changed `permission_profile`, which the V11 strict evaluator already compares directly. No mechanism repair had begun.

### Corrected fixture

- fixture-only correction SHA: `2f76dd3a56dc12d7700badaee1ede15ac03504df`
- mechanism changes before corrected rerun: `NONE`
- correction: keep permission profile identical and mutate only actual `argv` while retaining genuine digest fields.

### RED-002 — clean pre-repair RED

- exact SHA: `2f76dd3a56dc12d7700badaee1ede15ac03504df`
- run: `34699141793`
- job: `103567689956`
- result: `199 tests; 5 failures; 0 errors`

Failure classes:

1. `HASHLIB_SHA256_TRANSITIVE_ATTRIBUTE_MUTATION_CAN_MINT_FORGED_ARGV`
2. `JSON_DUMPS_TRANSITIVE_ATTRIBUTE_MUTATION_CAN_MINT_FORGED_ARGV`
3. `STRICT_HASHLIB_SHA256_ATTRIBUTE_NOT_RUNTIME_BOUND`
4. `STRICT_JSON_DUMPS_ATTRIBUTE_NOT_RUNTIME_BOUND`
5. `REFERENCE_CONFIG_RECORD_MISSING_RAW_PERMISSION_PROFILE_AND_ARGV`

Positive controls remained green, including legitimate EXP-ECC-5 and ordinary permission/argv drift rejection without primitive tamper.

## Current disposition

`V12_CLEAN_PRE_REPAIR_RED_PRESERVED`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
