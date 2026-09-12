# ECC-Derived V10 Path Primitive Integrity Ledger

Status: `V10_BOUNDED_PATH_PRIMITIVE_GREEN_PENDING_EXTERNAL_REREVIEW`

Authority effect: `NONE_EVIDENCE_ONLY`

No requirement is adopted, promoted, released, frozen, or granted authority by this ledger.

## Parent

- V9 ledger head: `978853924bf7f9317eb664ba7c20e93643b92771`
- V9 ledger-head CI run: `34695526295`
- V9 ledger-head CI status: `PASS`
- V9 bounded result: exact JSON/marshal callables are captured at initialization for candidate-authority verification/sealing.

## V10 hypothesis

Ordinary replacement of public `pathlib.Path` methods after module initialization must not control candidate-authority verification.

The V10 verifier must capture exact callable references for:

- `Path.read_text`
- `Path.read_bytes`
- `Path.resolve`
- `Path.is_file`
- `Path.is_symlink`

and use those captured callables for all candidate-authority filesystem/path checks.

A legitimate candidate path must remain positive when the public aliases are later monkeypatched, while forged manifest/dependency substitution must still fail closed.

## Frozen assertions

- V10 assertion commit: `d4227c32be1344f769ff9e5bda00ac954669ad13`
- V10 runner commit: `ee3b0473758e7037e495cacae4f2f792cb86856e`
- V10 workflow-enabled pre-repair SHA: `c3d0773cc2259ae3f8bb5d1775e8d8b686843591`

The V10 assertion file and runner were frozen before mechanism repair and were not modified to obtain GREEN.

## RED-001 — preserved pre-repair failure

- exact candidate: `c3d0773cc2259ae3f8bb5d1775e8d8b686843591`
- workflow run: `34695969414`
- workflow job: `103559389165`
- result: `183 tests; 6 failures; 0 errors`
- legitimate V10 positive control: `PASS`
- retained V1-V9 non-superseded tests: `PASS`

Failure classes:

1. `PATH_READ_TEXT_SUBSTITUTION_PLUS_DEPENDENCY_TAMPER_CAN_MINT`
2. `PATH_READ_TEXT_ALIAS_CONTROLS_LEGITIMATE_AUTHORITY`
3. `PATH_READ_BYTES_ALIAS_CONTROLS_LEGITIMATE_AUTHORITY`
4. `PATH_RESOLVE_ALIAS_CONTROLS_LEGITIMATE_AUTHORITY`
5. `PATH_IS_FILE_ALIAS_CONTROLS_LEGITIMATE_AUTHORITY`
6. `PATH_IS_SYMLINK_ALIAS_CONTROLS_LEGITIMATE_AUTHORITY`

Root cause: `GOVERNANCE_MECHANISM_DEFECT` — V9 captured the `Path` class object but continued dynamic method lookup on that mutable class.

## Deterministic repair

- RED preservation commit: `1141cfcbd31be13747ffa549faba061294240a9e`
- ledger-open commit: `6ecb29fb66b104a5743335a538e4d0c02adb8223`
- repair generator commit: `29acf883ae4995f119ef03873d8b4ffdd50801c0`
- repair workflow-enabling commit: `d1afbf0855a1fc93f4c7584dbb970fa1a170b343`
- repair workflow run: `34696046594`
- repair workflow job: `103559590557`
- mechanism repair commit: `70fcb4c`
- candidate-boundary SHA-256: `7705eb56bb03c28c12db78f64c30d6c43972643bdfbce15167849d64e140a8b9`
- trust-manifest SHA-256: `a6abf9341eb28b04a07d3d0314e8fcbd97fa2db17f5b77ee8c09e21585f5df4d`

The repair:

- captures exact `Path.read_text`, `Path.read_bytes`, `Path.resolve`, `Path.is_file`, and `Path.is_symlink` callable references at verifier initialization;
- uses those captured callables for manifest reading, module hashing, path resolution, symlink checks, and file-presence checks;
- makes later monkeypatching of the public `Path` methods diagnostic/non-authoritative to candidate issuance/consumption;
- preserves the V8/V9 closure-held verifier, strict/reference module identity binding, exact JSON/marshal callable capture, and process-local seal provenance; and
- does not claim resistance to mutation of the captured callable objects themselves, deeper OS/filesystem primitives used inside those callables, reflective closure extraction, interpreter/native-memory compromise, repository/code-replacement authority, live platform attestation, or durable cross-process provenance.

## GREEN-002 — repaired candidate falsification

A user-token evidence-only commit retriggered the frozen runner because the workflow-token repair push does not reliably trigger the falsification workflow.

- exact tested SHA: `3fcf51f993a26e6c8f921cc78c67f7765f856d63`
- mechanism parent: repair commit `70fcb4c`
- evidence-only trigger file: `experiments/ecc-derived/evidence/V10-PATH-REPAIR-APPLIED-001.json`
- workflow run: `34696073501`
- workflow job: `103559662284`
- result: `183/183 PASS`

The same frozen V10 suite now verifies:

- forged manifest text via public `Path.read_text` plus strict/reference tamper cannot mint candidate authority;
- public `Path.read_text` replacement cannot disable a legitimate candidate path;
- public `Path.read_bytes` replacement cannot disable a legitimate candidate path;
- public `Path.resolve` replacement cannot disable a legitimate candidate path;
- public `Path.is_file` replacement cannot disable a legitimate candidate path;
- public `Path.is_symlink` replacement cannot disable a legitimate candidate path;
- the legitimate V10 path remains positive;
- all retained V1-V9 non-superseded tests remain green; and
- all historical supersession records remain explicit.

## Bounded conclusion

V10 closes the demonstrated ordinary-module `Path` method substitution boundary within its frozen threat model.

This is not production qualification. Remaining boundaries include at least:

- mutation or replacement of the captured callable objects themselves;
- deeper OS/filesystem primitives invoked from the captured `Path` methods;
- reflective closure-cell extraction or rewriting;
- interpreter/native-memory compromise;
- repository/code-replacement authority;
- live platform attestation and an independent production trust root;
- durable signed provenance for cross-process use; and
- independent external engineering review of the exact current candidate/evidence corpus.

These remaining lower-level Python/runtime surfaces are not automatically expanded into another experiment generation. They are explicit bounded nonclaims for the next external engineering review to assess.

## Current disposition

- V10 reference mechanism: `BOUNDED_GREEN_PENDING_EXTERNAL_ENGINEERING_REREVIEW`
- EXP-ECC-1..5: `REFERENCE_MECHANISM_HARDENED_BUT_LIVE_INTEGRATION_EVIDENCE_STILL_REQUIRED`
- EXP-ECC-6..7: `DEFER_PENDING_INTEGRATION_EVIDENCE`
- freeze: `NOT_FROZEN`
- manual-review threshold contribution from AI reviews: `0`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
