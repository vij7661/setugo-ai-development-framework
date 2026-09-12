# ECC-Derived V8 Verifier-Substitution Ledger

Status: `V8_CLEAN_PRE_REPAIR_RED_PRESERVED`

Authority effect: `NONE_EVIDENCE_ONLY`

No requirement is adopted, promoted, released, frozen, or granted authority by this ledger.

## Parent

- V7 ledger head: `58592c578e9176b49a508273c7239fcfb11ca48b`
- V7 ledger-head CI run: `34694603530`
- V7 ledger-head CI status: `PASS`
- V7 bounded result: ordinary module access no longer exposes the known seal constructor/helper shortcuts.

V7 history remains unchanged. V8 addresses the next exposed boundary: substitution of the public runtime verifier together with strict/reference dependencies.

## V8 hypothesis

The public `verify_runtime_policy()` function must be diagnostic, not a capability whose replacement changes candidate authority.

Candidate issuance and candidate-result consumption must instead depend on:

1. a closure-held internal runtime verifier not reachable by ordinary module attribute access;
2. closure-held exact strict-core and reference-evidence module objects;
3. fresh internal policy verification on every candidate issuance and eligibility consumption;
4. fail-closed detection when the captured dependency objects themselves are mutated; and
5. continued positive operation for the legitimate untampered candidate path.

The V8 bounded threat model is ordinary Python module attribute replacement and ordinary monkeypatching of dependency functions. It does not claim resistance to reflective closure-cell extraction, bytecode/interpreter compromise, native memory compromise, or repository/code-replacement authority.

## Historical assertion supersession

V8 preserves prior test files unchanged but explicitly supersedes three older assertions whose mechanism was itself found unsafe:

- V5: replacing the public verifier to simulate policy change before candidate eligibility;
- V6: replacing the public verifier to simulate candidate-boundary failure;
- V6: replacing the public verifier to simulate policy failure at eligibility consumption.

Those assertions are replaced by V8 tests that mutate the actual strict/reference dependencies and require the internal verifier to detect the mutation. Thus the recheck requirement is strengthened rather than removed.

The earlier V5 raw-dictionary positive assertion remains separately superseded by V6 provenance sealing.

## Frozen assertions

- V8 assertion commit: `9b58cdb427c1ec80dfed27a3c1982cd7fdba63bd`
- V8 runner commit: `920297e487b3071cffc3f7094d064c819ad153c3`
- V8 workflow-enabled pre-repair SHA: `28ece812654f544dd27848e89ddf47508963dbab`

The V8 assertion file was frozen before mechanism repair.

## RED-001

- exact candidate: `28ece812654f544dd27848e89ddf47508963dbab`
- workflow run: `34694716021`
- workflow job: `103556106608`
- result: `170 tests; 5 failures; 0 errors`

Failure classes:

- `ALWAYS_TRUE_PUBLIC_VERIFIER_PLUS_REFERENCE_FUNCTION_TAMPER_CAN_MINT`
- `ALWAYS_TRUE_PUBLIC_VERIFIER_PLUS_STRICT_AND_REFERENCE_TAMPER_CAN_MINT`
- `MODULE_ALIAS_SUBSTITUTION_PLUS_PUBLIC_VERIFIER_SUBSTITUTION_CAN_MINT`
- `PUBLIC_VERIFIER_REPLACEMENT_CONTROLS_CANDIDATE_CONSUMPTION`
- `PUBLIC_VERIFIER_REPLACEMENT_CONTROLS_CANDIDATE_ISSUANCE`

Controls that already passed in the same run:

- actual reference-dependency mutation is detected when the real verifier executes;
- actual strict-core mutation is detected when the real verifier executes;
- dependency mutation after issuance invalidates eligibility consumption;
- legitimate candidate issuance remains positive;
- the public verifier reports the current policy as valid;
- no known internal-verifier capability handle is currently exported.

This isolates the defect to public-verifier authority and dependency alias/substitution coupling, not to the base candidate/evidence fixtures.

## Current disposition

`V8_CLEAN_PRE_REPAIR_RED_PRESERVED`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
