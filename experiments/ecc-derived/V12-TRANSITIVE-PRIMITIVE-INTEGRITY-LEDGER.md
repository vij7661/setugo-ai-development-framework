# ECC-Derived V12 Transitive Primitive Integrity Ledger

Status: `V12_BOUNDED_TRANSITIVE_PRIMITIVE_GREEN_PENDING_CLEAN_EXTERNAL_REREVIEW`

Authority effect: `NONE_EVIDENCE_ONLY`

No requirement is adopted, promoted, released, frozen, or granted authority by this ledger.

## Parent and external review

- V11 exact candidate: `39d19dbf4d62b2861128f00e62a7325ff1039fa6`
- V11 exact ledger-head CI: `190/190 PASS`
- V11 AI clean re-review: `CHANGES_REQUIRED_BEFORE_IMPACT_ADJUDICATION`
- review evidence class: `AI_GENERATED_ENGINEERING_FEEDBACK_ONLY`
- manual-review threshold contribution: `0`
- EXP-ECC-1..4 reviewer disposition: `ADOPT_REQUIREMENT_CANDIDATE`
- EXP-ECC-5 reviewer disposition: `NARROW_REQUIREMENT_CANDIDATE`
- EXP-ECC-6..7 reviewer disposition: `DEFER_PENDING_INTEGRATION_EVIDENCE`
- freeze recommendation: `DO_NOT_FREEZE`

The reviewer disposition is preserved as engineering feedback only. This V12 ledger does not itself adopt EXP-ECC-1..4 or promote EXP-ECC-5.

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

## Frozen assertions and runner lineage

- initial V12 assertion commit: `ead455cf0996076e0c838be29405282be4cd7311`
- initial V12 runner commit: `9de842999393d948f9199c1b493a849efd358644`
- workflow-enabled pre-repair SHA: `c80cdb4ff94229baea5836440a3efba7176c2417`
- corrected attack-fixture SHA: `2f76dd3a56dc12d7700badaee1ede15ac03504df`
- final supersession-aware runner SHA: `210ad4fa3b8629141e6f7ee3531c2f5cc8d450a0`

The V12 mechanism assertions were frozen before mechanism repair. The only pre-repair assertion change narrowed an attack fixture after the first run proved that changing `permission_profile` short-circuited the intended digest-only attack. No mechanism code was changed before the clean RED-002.

## RED-001 — attack-fixture narrowing required

- exact SHA: `c80cdb4ff94229baea5836440a3efba7176c2417`
- run: `34699078195`
- job: `103567521590`
- result: `199 tests; 3 failures; 0 errors`
- classification: `RED_WITH_ATTACK_FIXTURE_NARROWING_REQUIRED`

The two initial mint-attempt tests passed for the wrong reason because they also changed `permission_profile`, which the V11 strict evaluator already compares directly. No mechanism repair had begun.

## RED-002 — clean pre-repair RED

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

## Deterministic V12 repair

- repair generator commit: `9da64c95a780604488b553259ad251950e9520ee`
- repair workflow-enabling commit: `4fec5bbcaf9058f3c15bab726e83016f873429d0`
- repair workflow run: `34699239535`
- repair job: `103567942600`
- generated mechanism commit: `c650d169c0581e60f21d2d54ee61344dc38528cb`
- V12 mechanism assertions modified during repair: `NONE`

The repair:

- captures exact `strict_core.hashlib.sha256` and `strict_core.json.dumps` callables at verifier initialization;
- fails runtime policy if either exact callable changes;
- adds raw `argv` and `permission_profile` to the independent `ECC-V5-E5-POS` reference record;
- compares those raw semantic fields in the candidate-boundary config cross-check in addition to digest fields; and
- updates the V12 manifest to declare the transitive primitive integrity policy and remaining bounded nonclaims.

Generated module hashes before the later manifest runtime-code correction:

- candidate boundary SHA-256: `81eebdd4e42a10940809f42647a391d7d3a63dc8613744e8b775aefe723f694e`
- reference evidence SHA-256: `bcf513496e2f7d17456ad7ee6feea7762828d331c91018ef70b3df1ad777b22d`

## RED-003 — first repair baseline lockout

- exact tested SHA: `88fe4ab45903a3b9ba729e0906cac160fb653b30`
- run: `34699308868`
- job: `103568129139`
- result: `199 tests; 40 failures; 0 errors`
- classification: `GOVERNANCE_MECHANISM_REPAIR_DEFECT_RUNTIME_POLICY_BASELINE_MISMATCH`

The new V12 attacks failed closed, but the untampered runtime verifier also returned false, causing broad historical positive-control failures. This block-all state was explicitly rejected as a false green and preserved as RED.

## Diagnostic and manifest-only runtime-code correction

Diagnostic checkout: `eb48bd270bc9443e705e6090be2a3145b4b6c106`

- diagnostic run: `34699433392`
- diagnostic job: `103568458454`
- entrypoint identity: `PASS`
- recursive dependency globals: `PASS`
- exact `strict_core.hashlib.sha256` identity: `PASS`
- exact `strict_core.json.dumps` identity: `PASS`
- file/module hashes: `PASS`
- printed V12 manifest policy checks: `PASS`
- baseline runtime verifier: `FAIL`

Root cause: adding raw config fields to `ecc_reference_evidence.py` shifted code-object line metadata for `lookup_reference_evidence`. The logic remained unchanged, but the manifest still contained the V11 hash of `marshal.dumps(lookup_reference_evidence.__code__)`.

Manifest-only correction:

- correction workflow run: `34699495930`
- correction job: `103568617987`
- generated correction commit: `bd15d1dba0d3ebc068f048aa7622be388314650e`
- old reference runtime code hash: `3ff864bbc1c50cac3600e483607557352de0220a1928216d8ded81cb43d318ce`
- corrected reference runtime code hash: `b49cd197dd367ccb7811a87c954e24fa0d003862c172dad228ef451682e823d9`
- corrected manifest SHA-256: `d89016612c39c9dc7b198f2ad6502854ade9e3e3b15f4d6565eaa4c8fadb0193`
- logic change: `NONE`

## RED-004 — historical semantic conflict after baseline recovery

- exact tested SHA: `605fba752ea0de4b4956baedd544f58fa4b14109`
- run: `34699541584`
- job: `103568741013`
- result: `199 tests; 1 failure; 0 errors`

The only remaining failure was the historical V9 test:

`test_ecc_governance_v9_verifier_primitive_integrity.ECCV9VerifierPrimitiveIntegrity.test_json_dumps_substitution_cannot_poison_new_candidate_seal`

V9 assumed that replacing `boundary.json.dumps` was merely a public/seal serialization alias change and should not block legitimate candidate issuance. V12 establishes a stronger and more precise fact: `boundary.json` and `strict_core.json` are the same imported module object, so changing `boundary.json.dumps` also changes the exact `strict_core.json.dumps` callable used by candidate-authoritative EXP-ECC-5 digest validation. Under V12, that mutation must fail closed.

The V9 source file remains immutable historical evidence. V12 supersedes only this exact positive expectation in the active runner and prints the reason. Replacement coverage is provided by:

- `test_json_dumps_attribute_mutation_cannot_mint_forged_argv`
- `test_json_dumps_transitive_dependency_is_runtime_bound`
- `test_legitimate_exp_ecc_5_config_path_remains_positive`

## GREEN-005 — bounded V12 pass

- exact tested SHA: `210ad4fa3b8629141e6f7ee3531c2f5cc8d450a0`
- workflow run: `34699645817`
- workflow job: `103569016271`
- result: `198/198 PASS`
- retained V1-V11 non-superseded suite: `PASS`
- V12 transitive primitive negative cases: `PASS`
- V12 raw config semantic binding: `PASS`
- legitimate EXP-ECC-5 positive control: `PASS`
- untampered public diagnostic verifier: `PASS`
- all five active supersession records: printed explicitly by the runner

## Bounded interpretation

V12 supports only this bounded claim: within the current reference process and ordinary-module monkeypatch threat model exercised by the active V12 suite, candidate-authoritative EXP-ECC-5 config evidence fails closed when the exact `strict_core.hashlib.sha256` or `strict_core.json.dumps` callable is replaced, and the independent reference cross-check now directly binds raw `argv` and `permission_profile` in addition to digest fields.

V12 does **not** establish resistance to:

- mutation of already captured callable objects themselves;
- concurrent/TOCTOU mutation between a successful verification and strict/reference execution;
- reflective extraction or mutation of closure-held captured objects;
- deeper interpreter/native-memory compromise;
- repository/code-replacement authority;
- live platform attestation;
- independent production trust-root separation; or
- durable signed cross-process provenance.

These remain explicit bounded nonclaims, not implicit passes.

## Current disposition

- V12 reference mechanism: `BOUNDED_GREEN_PENDING_CLEAN_EXTERNAL_ENGINEERING_REREVIEW`
- EXP-ECC-1..4: `REVIEWER_RECOMMENDED_ADOPT_REQUIREMENT_CANDIDATE_BUT_NOT_PROMOTED`
- EXP-ECC-5: `NARROWED_REFERENCE_MECHANISM_GREEN_PENDING_CLEAN_REREVIEW`
- EXP-ECC-6..7: `DEFER_PENDING_INTEGRATION_EVIDENCE`
- freeze: `NOT_FROZEN`
- manual-review threshold contribution from AI reviews: `0`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
