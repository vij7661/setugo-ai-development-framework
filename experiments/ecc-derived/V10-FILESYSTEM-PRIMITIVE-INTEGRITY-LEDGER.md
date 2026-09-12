# ECC-Derived V10 Filesystem Primitive Integrity Ledger

Status: `V10_CLEAN_PRE_REPAIR_RED_PRESERVED`

Authority effect: `NONE_EVIDENCE_ONLY`

No requirement is adopted, promoted, released, frozen, or granted authority by this ledger.

## Parent

- V9 ledger head: `978853924bf7f9317eb664ba7c20e93643b92771`
- V9 ledger-head CI run: `34695526295`
- V9 ledger-head CI status: `PASS`
- V9 bounded result: `176/176 PASS`

V9 history remains unchanged. V10 addresses filesystem/path callable surfaces that V9 explicitly left unqualified.

## Frozen assertions

- V10 assertion commit: `c17b7ce60c11755e220d85bd46125a028375462c`
- V10 runner commit: `8df452a3958809101dd77d3817e3f0351ee476d5`
- workflow-enabled pre-repair SHA: `32e5b01a0b489b16da90a902d7bcdce22c165ff5`

The six V10 assertions were frozen before mechanism repair.

## RED-001

- exact candidate: `32e5b01a0b489b16da90a902d7bcdce22c165ff5`
- workflow run: `34695607521`
- workflow job: `103558444052`
- result: `182 tests; 5 failures; 0 errors`
- legitimate V10 candidate positive control: `PASS`
- retained V1-V9 non-superseded tests: `PASS`

Observed failures:

1. `PATH_READ_TEXT_SUBSTITUTION_PLUS_DEPENDENCY_TAMPER_CAN_MINT`
   - a forged manifest supplied through replaced `Path.read_text` plus malicious strict/reference functions yielded eligible authority.

2. `PATH_READ_BYTES_ALIAS_CONTROLS_LEGITIMATE_AUTHORITY`
   - replacing public `Path.read_bytes` caused legitimate candidate authority to fail.

3. `PATH_RESOLVE_ALIAS_CONTROLS_LEGITIMATE_AUTHORITY`
   - replacing public `Path.resolve` caused legitimate candidate authority to fail.

4. `PATH_IS_FILE_ALIAS_CONTROLS_LEGITIMATE_AUTHORITY`
   - replacing public `Path.is_file` caused legitimate candidate authority to fail.

5. `PATH_IS_SYMLINK_ALIAS_CONTROLS_LEGITIMATE_AUTHORITY`
   - replacing public `Path.is_symlink` caused legitimate candidate authority to fail.

## Root-cause classification

`GOVERNANCE_MECHANISM_DEFECT`

The closure-held verifier captured the `Path` class object but continued dynamic method lookup on that mutable class. Therefore ordinary monkeypatching of its methods remained authoritative.

## Current disposition

`V10_CLEAN_PRE_REPAIR_RED_PRESERVED`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
