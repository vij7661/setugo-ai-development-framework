# ECC-Derived V8 Verifier-Substitution Ledger

Status: `V8_BOUNDED_VERIFIER_SUBSTITUTION_GREEN_PENDING_EXTERNAL_REREVIEW`

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

The V8 bounded threat model is ordinary Python module attribute replacement and ordinary monkeypatching of dependency functions. It does not claim resistance to reflective closure-cell extraction, bytecode/interpreter compromise, native memory compromise, repository/code-replacement authority, an independent production trust root, or durable cross-process provenance.

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

The V8 assertion file and V8 runner were frozen before mechanism repair and were not changed to obtain GREEN.

## RED-001 — preserved pre-repair failure

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

Controls that already passed in the same RED run:

- actual reference-dependency mutation is detected when the real verifier executes;
- actual strict-core mutation is detected when the real verifier executes;
- dependency mutation after issuance invalidates eligibility consumption;
- legitimate candidate issuance remains positive;
- the public verifier reports the current policy as valid;
- no known internal-verifier capability handle is exported.

This isolates the defect to public-verifier authority and dependency alias/substitution coupling, not to the base candidate/evidence fixtures.

## Deterministic repair

- repair generator staged: `bdb3cdb0cd0a25d5371524d7133f2ff3544031ea`
- repair workflow-enabling commit: `ff4b551e3b59fa4d8394dcfa4564931f5c48892c`
- repair workflow run: `34694993098`
- repair workflow input: `ff4b551e3b59fa4d8394dcfa4564931f5c48892c`
- mechanism repair commit: `6d09bb16ca8c9c643df97bbb6681a1ccf51dfdb6`
- candidate boundary SHA-256: `ccfed9256263ccc9f3c37ff47391a9fa08d52f488af81c658fbfa92622668b30`
- trust manifest SHA-256: `ccba6b4d2add0a1e4dac1f9df939c6311ed3e8b6d0ae701a92a08e92f2986b4d`

The repair:

- moves candidate-authority runtime verification behind a closure-held verifier;
- captures the original strict-core and reference-evidence module objects for candidate authority;
- keeps the exported `verify_runtime_policy()` as a diagnostic wrapper only;
- removes the temporary internal-verifier/factory handles from ordinary module namespace after entrypoint construction;
- rechecks file hashes, module identity, runtime function-code hashes, manifest contract, and dependency integrity on issuance and eligibility consumption;
- preserves process-local opaque provenance sealing from V6/V7; and
- does not claim resistance beyond the stated V8 bounded threat model.

## GREEN-001 — repaired candidate falsification

A user-token evidence-only commit was used to trigger the frozen runner because the workflow-token repair commit does not reliably retrigger the falsification workflow.

- exact tested SHA: `256c66b4f7de25533e405e32e3d2eeb31fc0199d`
- mechanism under test: repair commit `6d09bb16ca8c9c643df97bbb6681a1ccf51dfdb6`
- evidence-only trigger file: `experiments/ecc-derived/V8-VERIFIER-SUBSTITUTION-REPAIR-CANDIDATE.json`
- workflow run: `34695023104`
- workflow job: `103556912189`
- result: `170/170 PASS`

The same frozen V8 suite now verifies:

- always-true public verifier + reference-function tamper cannot mint;
- always-true public verifier + strict/reference tamper cannot mint;
- module-alias substitution + public-verifier substitution cannot mint;
- replacing the public verifier no longer controls issuance;
- replacing the public verifier no longer controls consumption;
- actual strict/reference dependency mutation still fails closed;
- dependency mutation after issuance invalidates later consumption;
- legitimate candidate issuance remains positive;
- process-local seal/copy/serialization/mutation protections from V6/V7 remain green; and
- review/learning paths remain non-candidate-authoritative.

The runner continues to print all superseded-test records explicitly. No historical RED was removed or rewritten.

## Bounded conclusion

V8 closes the demonstrated ordinary-module verifier-substitution false-green path within its declared threat model.

This is not production qualification. Remaining boundaries include at least:

- reflective closure-cell or interpreter-level extraction/rewriting;
- native process-memory compromise;
- repository/code-replacement authority;
- live platform attestation and an independent production trust root;
- durable signed provenance for cross-process use; and
- independent external engineering review of the exact current candidate/evidence corpus.

## Current disposition

`V8_BOUNDED_VERIFIER_SUBSTITUTION_GREEN_PENDING_EXTERNAL_REREVIEW`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
