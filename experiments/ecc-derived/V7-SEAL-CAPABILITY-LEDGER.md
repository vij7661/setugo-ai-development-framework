# ECC-Derived V7 Seal-Capability Ledger

Status: `V7_BOUNDED_ORDINARY_MODULE_ACCESS_GREEN_NEXT_FALSIFICATION_REQUIRED`

Authority effect: `NONE_EVIDENCE_ONLY`

No requirement is adopted, promoted, released, frozen, or granted authority by this ledger.

## Parent

- V6 ledger head: `a9a28a7d25ea97d79237fd9706659023314af507`
- V6 status: `V6_BOUNDED_PROCESS_LOCAL_PROVENANCE_GREEN_PENDING_EXTERNAL_REREVIEW`
- V6 final ledger-head falsification: `155/155 PASS`

V6 remains valid only for the exact frozen V6 attacks. V7 addresses a newly exposed omission and does not rewrite V6 history.

## V7 hypothesis

V7 tests whether ordinary module attribute access exposes the positive provenance-minting capability without executing the governed candidate entrypoints.

A V7-safe reference boundary must satisfy all of the following:

1. no module-global raw seal function;
2. no module-global candidate-result constructor holding the issuer capability;
3. no generic formatting helper that can mint `candidate_eligible=true` provenance from arbitrary payloads;
4. no generic finish helper that can seal an arbitrary favorable payload after only runtime-policy checking;
5. legitimate candidate entrypoints still issue eligible results after their required core/evidence checks; and
6. plain caller-forged dictionaries remain ineligible.

The bounded threat model is ordinary Python module access. V7 does not claim resistance to arbitrary reflective closure-cell extraction, bytecode rewriting, native-process memory access, interpreter compromise, or a malicious actor with repository/code-replacement authority. Those require separate trust boundaries.

## Frozen assertions

- V7 assertion commit: `c7eeb35623ebe643106f56b2dd4486a37131cc95`
- V7 runner commit: `f3ad428cb76c73be766c8edc7e31bc5516f2880f`
- V7 workflow-enabled pre-repair SHA: `062ffeb869310afcedbdde228855bb72451171c4`

The V7 assertion file was frozen before mechanism repair and remained unchanged through both repair attempts.

## RED-001 — pre-repair

- exact candidate: `062ffeb869310afcedbdde228855bb72451171c4`
- workflow run: `34694186737`
- workflow job: `103554703960`
- result: `162 tests; 5 failures; 0 errors`
- legitimate candidate-entrypoint positive control: `PASS`
- plain forged-dictionary negative control: `PASS`

Observed failure classes:

- `MODULE_EXPORTS_RAW_SEAL_CAPABILITY`
- `MODULE_EXPORTS_CANDIDATE_RESULT_CONSTRUCTOR`
- `GENERIC_TYPED_HELPER_CAN_MINT_POSITIVE_AUTHORITY`
- `FINISH_POSITIVE_HELPER_CAN_MINT_FROM_ARBITRARY_PAYLOAD`
- `BOUNDARY_NAMESPACE_EXPOSES_CAPABILITY_BEARING_SHORTCUTS`

The RED proved that V6 process-local provenance was non-forgeable by serialization/copying but still forgeable through ordinary access to exported capability-bearing helpers.

## First V7 repair

- repair input SHA: `27c6c8cf957423b50332f527d7a61ef3e423cde1`
- repair workflow run: `34694307644`
- repair workflow job: `103555029498`
- first repair mechanism commit: `1f8d04830837cfe2b38990bf81457370918b4aa1`
- boundary SHA-256: `3f003e889c3dd8926148f37de0e98738bee5f3ea3369cb0187d7a483841f4ae6`
- manifest SHA-256: `14f6e6e4c5113b0c04757e91ab273b7c4c8731641124cd29bdd5936fe620ffba`

The first repair moved positive-seal capability into a closure-local API factory and removed ordinary module-global handles for the issuer token, candidate-result constructor, generic positive formatter, and generic finish helper.

Manifest posture explicitly bounded the claim:

- `seal_capability_policy = POSITIVE_SEAL_CAPABILITY_CLOSURE_LOCAL_ONLY`
- `ordinary_module_access_can_mint_provenance = false`
- `reflective_closure_extraction_resistance_claimed = false`
- `interpreter_compromise_resistance_claimed = false`

## RED-002 — first-repair mechanism defect

- exact tested candidate: `6bd9d8ddfd3292e830ba29730b9f4643a4b056e8`
- workflow run: `34694344292`
- workflow job: `103555122380`
- result: `162 tests; 16 failures; 0 errors`
- classification: `RED_MECHANISM_REPAIR_DEFECT`

The original five V7 seal-capability failures all turned green, but two new repair defects caused retained V5/V6 regressions:

1. `V7-REPAIR-DEFECT-001 — CODE_DEFECT`: `verify_runtime_policy()` still expected the V6 manifest record type after the manifest had moved to V7, so legitimate candidate routes failed closed.
2. `V7-REPAIR-DEFECT-002 — SEMANTIC_REGRESSION`: candidate entrypoints captured the verifier function at factory creation, violating retained V5/V6 semantics requiring the current runtime-policy verifier to be rechecked at issuance and consumption.

This failed repair remains part of the evidence history and was not squashed or reclassified as green.

## Repair correction

- correction input SHA: `35c60aef335d69e574327e53200c4d9677309fda`
- correction workflow run: `34694435708`
- correction workflow job: `103555362145`
- correction mechanism commit: `40a095032d430bce5bd578d981e264047f74bc8d`
- corrected boundary SHA-256: `d70aaa0dea897a41a5689f00297ae6d795723d9f05738b7f2a631a02a83e645a`
- corrected manifest SHA-256: `9d128821d9fbc073e9aeee05f2270f649f28b35f43568027ca6b303116e15ac7`

The correction changed only the classified repair defects:

- runtime verification now validates the V7 manifest contract;
- dynamic `verify_runtime_policy()` lookup is restored at issuance and consumption;
- closure-local positive-seal capability remains in place;
- V7 assertions remain unchanged.

## GREEN-003

- exact tested candidate: `350fe3c174d563e45db726fd6f40e71d95635c92`
- workflow run: `34694477250`
- workflow job: `103555472942`
- result: `162/162 PASS`
- retained V1/V2 suites: `PASS`
- retained non-superseded V5 assertions: `PASS`
- retained V6 provenance assertions: `PASS`
- V7 seal-capability assertions: `PASS`

The sequence is therefore preserved as:

`RED-001 -> FIRST REPAIR -> RED-002 (repair defect) -> CORRECTION -> GREEN-003`

No test was modified to obtain GREEN-003.

## Bounded interpretation

V7 supports only this claim: under ordinary Python module attribute access, the exact V7 reference boundary does not expose the known raw positive-seal constructor/helper shortcuts, while legitimate candidate entrypoints still produce eligible process-local results and the V6 copy/serialization/mutation protections remain intact.

V7 does **not** establish:

- resistance to reflective closure-cell extraction;
- resistance to bytecode, interpreter, or native-process memory compromise;
- durable cross-process provenance/signatures;
- live platform attestation;
- independent production trust-root separation;
- production readiness;
- EXP-ECC-6/7 readiness; or
- requirement adoption.

## Newly exposed higher-order boundary

V7 restored dynamic runtime-policy lookup to preserve the V5/V6 recheck contract. That leaves a distinct ordinary-module-access combination to falsify:

1. replace module-global `verify_runtime_policy` with an always-true function;
2. replace or monkeypatch strict-core candidate functions and/or reference-evidence lookup;
3. invoke a legitimate candidate entrypoint;
4. determine whether the entrypoint can then mint a closure-sealed eligible result from substituted dependencies.

Existing tests prove that strict/reference monkeypatches are detected **when the real verifier executes**, and that the current verifier is rechecked dynamically. They do not prove that simultaneous verifier substitution plus dependency substitution cannot bypass both controls.

Open risk:
`V7-OPEN-RUNTIME-VERIFIER-SUBSTITUTION-001 — DYNAMIC_POLICY_VERIFIER_AND_DEPENDENCY_SUBSTITUTION`

Required next step: open a separate falsification generation for verifier/dependency substitution before external engineering re-review or any freeze decision.

## Current disposition

- V7 seal-capability boundary: `BOUNDED_GREEN`
- next falsification: `REQUIRED`
- EXP-ECC-1..5: `REFERENCE_MECHANISM_HARDENED_BUT_LIVE_INTEGRATION_EVIDENCE_STILL_REQUIRED`
- EXP-ECC-6..7: `DEFER_PENDING_INTEGRATION_EVIDENCE`
- freeze: `NOT_FROZEN`
- manual-review threshold contribution: `0`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
