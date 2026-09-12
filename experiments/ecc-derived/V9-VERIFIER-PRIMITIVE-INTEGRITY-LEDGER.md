# ECC-Derived V9 Verifier Primitive Integrity Ledger

Status: `V9_CLEAN_PRE_REPAIR_RED_PRESERVED`

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

The six V9 assertions were frozen before any V9 mechanism repair.

## RED-001

- exact candidate: `3b55870a949028118ff824fba5decc6e1b817ef2`
- workflow run: `34695305679`
- workflow job: `103557655012`
- result: `176 tests; 5 failures; 0 errors`
- legitimate V9 candidate-path positive control: `PASS`
- all retained V1-V8 non-superseded tests: `PASS`

Observed failures:

1. `JSON_DUMPS_SUBSTITUTION_MASKS_POST_ISSUANCE_MUTATION`
   - a genuine sealed result was mutated after issuance;
   - replacing the public `json.dumps` primitive with the original trusted serialization caused the mutated result to remain eligible.

2. `JSON_DUMPS_SUBSTITUTION_CONTROLS_NEW_SEAL_CONSTRUCTION`
   - replacing public `json.dumps` during issuance poisoned the candidate seal;
   - after the alias was restored, the otherwise legitimate result was no longer eligible.

3. `JSON_LOADS_SUBSTITUTION_PLUS_DEPENDENCY_TAMPER_CAN_MINT`
   - strict/reference runtime functions were replaced with favorable malicious functions;
   - public `json.loads` was replaced to return an in-memory forged manifest with hashes for those malicious functions;
   - the candidate path minted a result that remained eligible.

4. `MARSHAL_ALIAS_SUBSTITUTION_CONTROLS_LEGITIMATE_AUTHORITY`
   - replacing public `marshal.dumps` alone caused an otherwise legitimate candidate path to fail as `CANDIDATE_BOUNDARY_POLICY_INVALID`.

5. `MARSHAL_DUMPS_SUBSTITUTION_PLUS_DEPENDENCY_TAMPER_CAN_MINT`
   - strict/reference runtime functions were replaced with favorable malicious functions;
   - public `marshal.dumps` was replaced so the malicious code objects serialized to the trusted code bytes;
   - the verifier accepted the expected runtime hashes and the candidate path minted eligible authority.

## Root-cause classification

`GOVERNANCE_MECHANISM_DEFECT`

This is not a fixture/test-data defect, expectation defect, or block-all result. The legitimate positive control passes, and the attacks demonstrate that V8 captured mutable module objects rather than exact immutable-enough callable references for the verifier/seal primitives.

## Historical supersession preservation

The V9 runner continues to print the four prior supersession records from V6/V8. No earlier assertion file or RED evidence was deleted or rewritten.

## Current disposition

`V9_CLEAN_PRE_REPAIR_RED_PRESERVED`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
