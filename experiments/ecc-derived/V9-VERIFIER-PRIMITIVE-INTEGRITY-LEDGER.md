# ECC-Derived V9 Verifier Primitive Integrity Ledger

Status: `V9_BOUNDED_VERIFIER_PRIMITIVE_GREEN_PENDING_NEXT_BOUNDARY_REVIEW`

Authority effect: `NONE_EVIDENCE_ONLY`

No requirement is adopted, promoted, released, frozen, or granted authority by this ledger.

## Parent

- V8 bounded-green ledger head: `be28b37333156dfa5b86eec8322d4e7f1c3e4afc`
- V8 ledger-head CI run: `34695062011`
- V8 ledger-head CI status: `PASS`
- V8 next-risk handoff base: `f6d3d29c012477030ff2a6b1be5f650cdc921c90`

V8's `170/170 PASS` remains valid only for the exact frozen V8 assertions. V9 addresses newly exposed mutable verifier/seal primitives that were not covered by V8.

## V9 hypothesis

Ordinary replacement of public module aliases such as `json.loads`, `json.dumps`, or `marshal.dumps` must not control candidate-authority verification or process-local seal integrity after module initialization.

Candidate-authority code must use exact captured callable primitives rather than later attribute lookup on mutable module objects.

## Frozen assertions

- V9 assertion commit: `9e440459b3955ff278a0e1806b1f565984d1e12b`
- V9 runner commit: `8c7fbb73b66fb5dd77faa2a47624d77f3f47abf7`
- V9 workflow-enabled pre-repair SHA: `3b55870a949028118ff824fba5decc6e1b817ef2`

The six V9 assertions were frozen before any V9 mechanism repair and were not modified to obtain GREEN.

## RED-001 — preserved pre-repair failure

- exact candidate: `3b55870a949028118ff824fba5decc6e1b817ef2`
- workflow run: `34695305679`
- workflow job: `103557655012`
- result: `176 tests; 5 failures; 0 errors`
- legitimate V9 candidate-path positive control: `PASS`
- all retained V1-V8 non-superseded tests: `PASS`

Observed failures:

1. `JSON_DUMPS_SUBSTITUTION_MASKS_POST_ISSUANCE_MUTATION`
2. `JSON_DUMPS_SUBSTITUTION_CONTROLS_NEW_SEAL_CONSTRUCTION`
3. `JSON_LOADS_SUBSTITUTION_PLUS_DEPENDENCY_TAMPER_CAN_MINT`
4. `MARSHAL_ALIAS_SUBSTITUTION_CONTROLS_LEGITIMATE_AUTHORITY`
5. `MARSHAL_DUMPS_SUBSTITUTION_PLUS_DEPENDENCY_TAMPER_CAN_MINT`

## Root-cause classification

`GOVERNANCE_MECHANISM_DEFECT`

This is not a fixture/test-data defect, expectation defect, or block-all result. The legitimate positive control passes, and the attacks demonstrated that V8 captured mutable module objects rather than exact callable references for the verifier/seal primitives.

## Deterministic repair

- V9 RED preservation commit: `6c357d63a23785f42c0d467b9b1bfea618102938`
- repair generator commit: `fb60513208cd49849ff62a6356171d2d59fcb233`
- repair workflow input: `c681c7fa034f466c1d41a82f4ef5208fb98c4ef6`
- repair workflow run: `34695433100`
- repair workflow job: `103557996070`
- mechanism repair commit: `2d9c4e3cca3fedd3dac9a3e74de71e66ac270cc8`
- candidate boundary SHA-256: `d2c4a16eb46505b9e3e097c8e85896043bcf053b1e9dae90fdf88b2cd084a4c3`
- trust manifest SHA-256: `2f51c600b32b8eab6fc6172861db4df7de932c096c1b54cac0c5df704e888015`

The repair:

- captures exact `hashlib.sha256`, `json.loads`, and `marshal.dumps` callable references for runtime verification;
- captures exact `hashlib.sha256` and `json.dumps` callable references for candidate seal construction/revalidation;
- removes candidate-authority dependence on later mutation of the public `json` and `marshal` module attributes;
- uses the already-captured favorable-status map during eligibility consumption instead of returning to mutable module-global `_FAVORABLE`;
- preserves V8 closure-held runtime verifier and strict/reference module-object binding; and
- makes no claim against reflective mutation of captured callable objects, interpreter/native-memory compromise, repository-authority compromise, or other primitives not yet falsified.

## GREEN-001 — repaired candidate falsification

- exact tested SHA: `bf7dd882d66c5074f3be7eda651f50e4abc9532f`
- exact mechanism parent: `2d9c4e3cca3fedd3dac9a3e74de71e66ac270cc8`
- evidence-only trigger file: `experiments/ecc-derived/V9-VERIFIER-PRIMITIVE-REPAIR-CANDIDATE.json`
- workflow run: `34695461414`
- workflow job: `103558066098`
- result: `176/176 PASS`

The same frozen V9 suite now verifies:

- JSON-load substitution plus strict/reference tamper cannot mint;
- marshal-code-serialization substitution plus strict/reference tamper cannot mint;
- JSON serialization substitution cannot mask post-issuance result mutation;
- JSON serialization substitution cannot poison new candidate seals;
- public marshal alias substitution no longer controls legitimate candidate authority;
- the legitimate V9 candidate path remains positive;
- all retained V1-V8 non-superseded cases remain green; and
- all historical supersession records remain explicit.

## Remaining boundary

V9 proves only the frozen primitive-substitution attacks above. The runtime verifier still uses filesystem/path and module-registry mechanisms whose own mutable-callable surfaces have not yet been independently falsified. In particular, `Path.read_text`, `Path.read_bytes`, `Path.resolve`, `Path.is_file`, and `Path.is_symlink` are not covered by the V9 assertions. No claim is made yet that ordinary mutation of those primitives cannot affect candidate authority.

Additional remaining boundaries include reflective closure/callable mutation, interpreter or native-memory compromise, repository/code-replacement authority, live platform attestation, independent production trust roots, and durable signed cross-process provenance.

## Historical supersession preservation

The V9 runner continues to print the four prior supersession records from V6/V8. No earlier assertion file or RED evidence was deleted or rewritten.

## Current disposition

`V9_BOUNDED_VERIFIER_PRIMITIVE_GREEN_PENDING_NEXT_BOUNDARY_REVIEW`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
