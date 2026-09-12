# ECC-Derived V10 Path Primitive Integrity Ledger

Status: `V10_CLEAN_PRE_REPAIR_RED_PRESERVED`

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

The V10 assertion file and runner were frozen before mechanism repair.

## RED-001

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

## Current disposition

`V10_CLEAN_PRE_REPAIR_RED_PRESERVED`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
