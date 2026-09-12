# ECC-Derived V7 Seal-Capability Ledger

Status: `V7_CLEAN_PRE_REPAIR_RED_PRESERVED`

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

The V7 assertion file was frozen before mechanism repair.

## RED-001

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

The RED proves that V6 process-local provenance was non-forgeable by serialization/copying but still forgeable through ordinary access to exported capability-bearing helpers.

## Current disposition

`V7_CLEAN_PRE_REPAIR_RED_PRESERVED`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
