# ECC-Derived V10 Filesystem Primitive Integrity Ledger

Status: `V10_BOUNDED_FILESYSTEM_PRIMITIVE_GREEN_PENDING_NEXT_BOUNDARY_REVIEW`

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

The six V10 assertions were frozen before mechanism repair and were not modified to obtain GREEN.

## RED-001 — preserved pre-repair failure

- exact candidate: `32e5b01a0b489b16da90a902d7bcdce22c165ff5`
- workflow run: `34695607521`
- workflow job: `103558444052`
- result: `182 tests; 5 failures; 0 errors`
- legitimate V10 candidate positive control: `PASS`
- retained V1-V9 non-superseded tests: `PASS`

Observed failures:

1. `PATH_READ_TEXT_SUBSTITUTION_PLUS_DEPENDENCY_TAMPER_CAN_MINT`
2. `PATH_READ_BYTES_ALIAS_CONTROLS_LEGITIMATE_AUTHORITY`
3. `PATH_RESOLVE_ALIAS_CONTROLS_LEGITIMATE_AUTHORITY`
4. `PATH_IS_FILE_ALIAS_CONTROLS_LEGITIMATE_AUTHORITY`
5. `PATH_IS_SYMLINK_ALIAS_CONTROLS_LEGITIMATE_AUTHORITY`

## Root-cause classification

`GOVERNANCE_MECHANISM_DEFECT`

The closure-held verifier captured the `Path` class object but continued dynamic method lookup on that mutable class. Therefore ordinary monkeypatching of its methods remained authoritative.

## Deterministic repair

- RED preservation commit: `01392ab7bfe6946c7fc78dacc4800d6ae6a17eb4`
- repair generator commit: `8f8747eab85e9ebe185c6c1e5d777bc154f30013`
- repair workflow input: `864c4d8774050dbd251087a605eb9bdf5cbd9c06`
- repair workflow run: `34695665825`
- repair workflow job: `103558600201`
- mechanism repair commit: `5cf1ccaf87cca20326f5838e27aac27ab75de423`
- candidate boundary SHA-256: `e4268982dd2d2f27d45370d8eb9fb29e7d461d17762c4a87924a7651ef33bd51`
- trust manifest SHA-256: `f81dc7c0bbfd71f4c2bbd9313ae185c2d825befeef12fa225465700b386fdf81`

The repair:

- captures exact `Path.resolve`, `Path.is_symlink`, `Path.is_file`, `Path.read_text`, and `Path.read_bytes` callables at initialization;
- uses the captured callables directly for module identity, filesystem presence, manifest loading, and source hashing;
- versions the trust manifest to `ECC_GOVERNANCE_V10_FILESYSTEM_PRIMITIVE_INTEGRITY_MANIFEST`;
- declares `filesystem_primitive_policy = EXACT_PATH_METHODS_CAPTURED_AT_INITIALIZATION`;
- preserves V9 exact-callable capture for JSON/marshal/hash primitives, V8 closure-held verifier/dependency binding, and V6/V7 process-local provenance/seal controls; and
- makes no claim against mutation of the captured callable objects themselves, interpreter/native-memory compromise, or other not-yet-falsified authority surfaces.

## GREEN-001 — repaired candidate falsification

- exact tested SHA: `281f3fafa9639dda6568706e54f9196db07f5ff3`
- exact mechanism parent: `5cf1ccaf87cca20326f5838e27aac27ab75de423`
- evidence-only trigger file: `experiments/ecc-derived/V10-FILESYSTEM-PRIMITIVE-REPAIR-CANDIDATE.json`
- workflow run: `34695736752`
- workflow job: `103558784033`
- result: `182/182 PASS`

The same frozen V10 suite now verifies:

- `Path.read_text` substitution plus strict/reference dependency tamper cannot mint;
- public `Path.read_bytes` substitution does not control legitimate candidate authority;
- public `Path.resolve` substitution does not control legitimate candidate authority;
- public `Path.is_file` substitution does not control legitimate candidate authority;
- public `Path.is_symlink` substitution does not control legitimate candidate authority;
- the legitimate V10 candidate path remains positive;
- all retained V1-V9 non-superseded cases remain green; and
- all four historical supersession records remain explicit.

## Remaining boundary

V10 proves only the frozen filesystem-method attacks above. It does not establish resistance to mutation of the captured callable objects themselves, mutation/replacement of captured mutable state such as the `sys.modules` mapping or module metadata, concurrent/TOCTOU mutation between verification and strict/reference execution, reflective closure extraction, interpreter or native-memory compromise, repository/code-replacement authority, live platform attestation, independent production trust roots, or durable signed cross-process provenance.

These must remain non-claims until separately falsified or explicitly placed outside the bounded threat model.

## Current disposition

`V10_BOUNDED_FILESYSTEM_PRIMITIVE_GREEN_PENDING_NEXT_BOUNDARY_REVIEW`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
